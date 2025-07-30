'''
Tracy NN 

A lightweight tracer for understanding & debugging PyTorch neural networks.

Author: [Billy Pu$h3r]
License: MIT
'''

__version__ = '0.1.0'
import torch
import functools
import torch.nn as nn
import torch.nn.functional as F
from typing import Callable, Any, Optional, Dict, List, Tuple
import inspect
import re
import sys
from contextlib import contextmanager

class Color:
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    DARKCYAN = '\033[36m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ORANGE = '\033[33m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'
    GREY = '\033[90m'

    @classmethod
    def disable(cls):
        for attr in dir(cls):
            if not attr.startswith('_') and attr != 'disable':
                setattr(cls, attr, '')


class Tracer:
    '''
    A PyTorch neural network tracer for observing what's happening inside the
    model during forward passes by giving a detailed trace of every operation!
    
    Usage example:
        ```python
        tracer = Tracer('My Model Debug')
        tracer.start(model)
        
        # Run your model
        output = model(input_tensor)
        
        tracer.stop()
        ```
    '''
    
    def __init__(self, name: str = 'Neural Network'):
        '''
        Initialize the tracer with a custom name.
        
        Args:
            name[str]: Custom name for your tracing session (shows up in output)
        '''
        self.name = name
        self.hooks: List[torch.utils.hooks.RemovableHandle] = []
        self.original_methods: Dict[str, Callable] = {}
        self.original_tensor_methods: Dict[str, Callable] = {}
        self.tensor_ops_tracer = TensorOpsTracer(Color)
        self._is_active = False

    def _get_calling_module_fn(self) -> Optional[str]:
        '''
        Walk up the call stack to find which nn.Module method triggered this operation.
        
        This tells you WHERE in your model an operation happened!
        '''
        for frame_info in inspect.stack():
            locals_ = frame_info.frame.f_locals
            if 'self' in locals_ and isinstance(locals_['self'], nn.Module):
                return f'{locals_['self'].__class__.__name__}.{frame_info.function}'
        return None

    def _format_tensor(self, tensor: Any) -> str:
        '''Format tensor information in a human-readable way.'''
        if isinstance(tensor, torch.Tensor):
            shape_str = f'{Color.BLUE}{list(tensor.shape)}{Color.END}'
            device_str = f'{Color.GREEN}{tensor.device}{Color.END}'
            dtype_str = f'{Color.GREY}{tensor.dtype}{Color.END}'
            return f'Tensor {shape_str} {dtype_str} @ {device_str}'
        elif tensor is None:
            return f'{Color.GREY}None{Color.END}'
        else:
            return f'{Color.GREY}{type(tensor).__name__}{Color.END}'

    def _format_tensors(self, tensors: Any) -> str:
        '''Handle multiple tensors (tuples, lists, dicts) gracefully.'''
        if isinstance(tensors, (tuple, list)):
            if len(tensors) == 1:
                return self._format_tensor(tensors[0])
            return f'[{', '.join(self._format_tensor(t) for t in tensors)}]'
        elif isinstance(tensors, dict):
            items = [f'{k}: {self._format_tensor(v)}' for k, v in tensors.items()]
            return '{' + ', '.join(items) + '}'
        else:
            return self._format_tensor(tensors)

    def _get_module_params(self, module: nn.Module) -> str:
        '''Extract key parameters from common module types for display.'''
        params = []
        
        # Common layer types and their important parameters
        if isinstance(module, nn.Linear):
            params.extend([
                f'in_features={Color.ORANGE}{module.in_features}{Color.END}',
                f'out_features={Color.ORANGE}{module.out_features}{Color.END}'
            ])
        elif isinstance(module, (nn.Conv1d, nn.Conv2d, nn.Conv3d)):
            params.extend([
                f'in_channels={Color.ORANGE}{module.in_channels}{Color.END}',
                f'out_channels={Color.ORANGE}{module.out_channels}{Color.END}',
                f'kernel_size={Color.ORANGE}{module.kernel_size}{Color.END}'
            ])
        elif isinstance(module, nn.BatchNorm2d):
            params.append(f'num_features={Color.ORANGE}{module.num_features}{Color.END}')
        elif isinstance(module, nn.Dropout):
            params.append(f'p={Color.ORANGE}{module.p}{Color.END}')
        
        return f' ({', '.join(params)})' if params else ''

    def _module_hook(self, module: nn.Module, inputs: Any, outputs: Any, name: str = ''):
        '''Hook function that gets called for every module forward pass.'''
        # Skip container modules (they don't do actual computation)
        if len(list(module.children())) > 0:
            return
            
        name_str = f'{name} ' if name else ''
        class_name = module.__class__.__name__
        params_str = self._get_module_params(module)
        
        module_name = f'{Color.PURPLE}{name_str}({class_name}){params_str}{Color.END}'
        print(f'  {Color.PURPLE}●{Color.END} {module_name}')
        print(f'{Color.GREY}  ├─{Color.END} Input: {self._format_tensors(inputs)}')
        print(f'{Color.GREY}  └─{Color.END} Output: {self._format_tensors(outputs)}')
        print(f'{Color.GREY}  │{Color.END}')

    def _functional_wrapper(self, original_func: Callable, func_name: str) -> Callable:
        '''Wrap F.* functions to trace their usage.'''
        @functools.wraps(original_func)
        def wrapper(*args, **kwargs):
            result = original_func(*args, **kwargs)
            caller = self._get_calling_module_fn()
            caller_str = f'{Color.GREY}@ [{caller}]{Color.END}' if caller else ''
            func_str = f'{Color.CYAN}F.{func_name}{Color.END}'
            
            # Show non-tensor arguments if they exist
            args_str = ''
            if len(args) > 1:
                non_tensor_args = [str(a) for a in args[1:] if not isinstance(a, torch.Tensor)]
                if non_tensor_args:
                    args_str = f'({', '.join(non_tensor_args)})'
            
            print(f'  {Color.CYAN}●{Color.END} {func_str}{args_str} {caller_str}')
            print(f'{Color.GREY}  ├─{Color.END} Input: {self._format_tensors(args[0]) if args else 'N/A'}')
            print(f'{Color.GREY}  └─{Color.END} Output: {self._format_tensors(result)}')
            print(f'{Color.GREY}  │{Color.END}')
            return result
        return wrapper

    def _tensor_method_wrapper(self, original_func: Callable, func_name: str) -> Callable:
        '''Wrap tensor methods to trace their usage.'''
        @functools.wraps(original_func)
        def wrapper(tensor, *args, **kwargs):
            result = original_func(tensor, *args, **kwargs)
            caller = self._get_calling_module_fn()
            caller_str = f'{Color.GREY}@ [{caller}]{Color.END}' if caller else ''
            func_str = f'{Color.RED}Tensor.{func_name}{Color.END}'
            
            # Format arguments nicely
            all_args = []
            all_args.extend(str(a) for a in args)
            all_args.extend(f'{k}={v}' for k, v in kwargs.items())
            args_str = f'({', '.join(all_args)})' if all_args else ''
            
            print(f'  {Color.RED}●{Color.END} {func_str}{args_str} {caller_str}')
            print(f'{Color.GREY}  ├─{Color.END} Input: {self._format_tensor(tensor)}')
            print(f'{Color.GREY}  └─{Color.END} Output: {self._format_tensor(result)}')
            print(f'{Color.GREY}  │{Color.END}')
            return result
        return wrapper

    def start(self, model: nn.Module):
        '''
        Start tracing the model.
        
        Args:
            model: The PyTorch model to trace
            
        Note:
            Don't forget to call stop() when you're done, or use the context manager.
        '''
        if self._is_active:
            print(f'{Color.YELLOW}Tracer {self.name} is already active!{Color.END}')
            return
            
        self._is_active = True
        print('─' * 80)
        print(f'  {Color.GREEN}●{Color.END} {Color.BOLD}TRACING {self.name} STARTED{Color.END}')
        print(f'{Color.GREY}  │{Color.END}')
        
        # Register hooks for all modules
        for name, module in model.named_modules():
            hook_fn = functools.partial(self._module_hook, name=name)
            self.hooks.append(module.register_forward_hook(hook_fn))

        # Patch common F.* functions
        funcs_to_patch = [
            'relu', 'leaky_relu', 'gelu', 'sigmoid', 'tanh', 'softmax', 'log_softmax',
            'dropout', 'interpolate', 'max_pool2d', 'avg_pool2d', 'adaptive_avg_pool2d'
        ]
        for func_name in funcs_to_patch:
            if hasattr(F, func_name) and func_name not in self.original_methods:
                self.original_methods[func_name] = getattr(F, func_name)
                setattr(F, func_name, self._functional_wrapper(self.original_methods[func_name], func_name))

        # Patch tensor methods that change shape/data
        tensor_methods_to_patch = ['view', 'reshape', 'transpose', 'permute', 'flatten']
        for func_name in tensor_methods_to_patch:
            if hasattr(torch.Tensor, func_name) and func_name not in self.original_tensor_methods:
                self.original_tensor_methods[func_name] = getattr(torch.Tensor, func_name)
                setattr(torch.Tensor, func_name, self._tensor_method_wrapper(self.original_tensor_methods[func_name], func_name))

        # Start tensor operations tracing
        self.tensor_ops_tracer._start_tensor_ops_tracing()

    def stop(self):
        '''
        Stop tracing and clean up all patches. 
        
        Always call this when you're done, or your PyTorch functions will stay patched!
        '''
        if not self._is_active:
            return
            
        self._is_active = False
        
        # Clean up tensor ops tracing first
        self.tensor_ops_tracer._stop_tensor_ops_tracing()
        
        # Remove all hooks
        for handle in self.hooks:
            handle.remove()
        self.hooks.clear()
        
        # Restore original F.* functions
        for func_name, original_func in self.original_methods.items():
            setattr(F, func_name, original_func)
        self.original_methods.clear()
        
        # Restore original tensor methods
        for func_name, original_func in self.original_tensor_methods.items():
            setattr(torch.Tensor, func_name, original_func)
        self.original_tensor_methods.clear()
        
        print(f'{Color.GREY}  │{Color.END}')
        print(f'  {Color.GREEN}●{Color.END} {Color.BOLD}TRACING {self.name} COMPLETE{Color.END}')
        print('─' * 80)

    @contextmanager
    def trace(self, model: nn.Module):
        '''
        Context manager for safe tracing. Automatically cleans up! 
        
        Usage:
            with tracer.trace(model):
                output = model(input_tensor)
        '''
        try:
            self.start(model)
            yield self
        finally:
            self.stop()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()


class TensorOpsTracer:
    '''
    The specialized tracer for tensor-to-tensor operations.
    
    This handles the nitty-gritty of matrix multiplications, additions, and other
    tensor operations that happen during forward passes. It even tries to extract
    variable names from your code! 
    '''
    
    def __init__(self, color_class):
        self.Color = color_class
        self.original_tensor_methods: Dict[str, Callable] = {}
        self.original_tensor_ops: Dict[str, Callable] = {}

    def _format_tensor(self, tensor: Any) -> str:
        '''Format tensor info consistently with the main tracer.'''
        if isinstance(tensor, torch.Tensor):
            shape_str = f'{self.Color.BLUE}{list(tensor.shape)}{self.Color.END}'
            device_str = f'{self.Color.GREEN}{tensor.device}{self.Color.END}'
            return f'Tensor {shape_str} @ {device_str}'
        elif tensor is None:
            return f'{self.Color.GREY}None{self.Color.END}'
        else:
            return f'{self.Color.GREY}{type(tensor).__name__}{self.Color.END}'

    def _get_calling_module_fn(self) -> Optional[str]:
        '''Find the calling module method.'''
        for frame_info in inspect.stack():
            locals_ = frame_info.frame.f_locals
            if 'self' in locals_ and isinstance(locals_['self'], nn.Module):
                return f'{locals_['self'].__class__.__name__}.{frame_info.function}'
        return None

    def _get_operand_names(self, frame_info: inspect.FrameInfo, op_name: str) -> Tuple[str, str, str]:
        '''
        Try to extract variable names from the source code.
        
        This is a bit of code archaeology - we look at the actual source line
        to figure out what variables were used in the operation.
        '''
        try:
            code_context = frame_info.code_context[0].strip()
            # Look for patterns like: result = a @ b, output = x * y, etc.
            patterns = [
                r'(\w+)\s*=\s*(\w+)\s*@\s*(\w+)',  # Matrix multiplication
                r'(\w+)\s*=\s*(\w+)\s*\*\s*(\w+)',  # Element-wise multiplication
                r'(\w+)\s*=\s*(\w+)\s*\+\s*(\w+)',  # Addition
                r'(\w+)\s*=\s*(\w+)\s*-\s*(\w+)',  # Subtraction
            ]
            
            for pattern in patterns:
                match = re.search(pattern, code_context)
                if match:
                    return match.groups()
                    
        except (IndexError, AttributeError):
            pass
            
        # Fallback to generic names
        return 'output', 'left', 'right'

    def _tensor_binary_op_wrapper(self, original_func: Callable, op_name: str) -> Callable:
        '''Wrap binary tensor operations (a @ b, a + b, etc.).'''
        @functools.wraps(original_func)
        def wrapper(self_tensor, other, *args, **kwargs):
            result = original_func(self_tensor, other, *args, **kwargs)
            caller = self._get_calling_module_fn()
            caller_str = f'{self.Color.GREY}@ [{caller}]{self.Color.END}' if caller else ''
            
            # Try to find the frame where the operation was called
            op_frame = None
            for frame_info in inspect.stack():
                if 'self' in frame_info.frame.f_locals and isinstance(frame_info.frame.f_locals['self'], nn.Module):
                    op_frame = frame_info
                    break
            
            # Extract variable names if possible
            output_name, left_name, right_name = 'output', 'left', 'right'
            if op_frame:
                output_name, left_name, right_name = self._get_operand_names(op_frame, op_name)

            # Make the operation symbol pretty
            op_display = '@' if op_name == '__matmul__' else op_name.strip('_')
            func_str = f'{self.Color.YELLOW}Tensor.{op_display}{self.Color.END}'
            
            print(f'  {self.Color.YELLOW}●{self.Color.END} {func_str} {caller_str}')
            print(f'{self.Color.GREY}  ├─{self.Color.END} {left_name.capitalize()}: {self._format_tensor(self_tensor)}')
            print(f'{self.Color.GREY}  ├─{self.Color.END} {right_name.capitalize()}: {self._format_tensor(other)}')
            print(f'{self.Color.GREY}  └─{self.Color.END} {output_name.capitalize()}: {self._format_tensor(result)}')
            print(f'{self.Color.GREY}  │{self.Color.END}')
            return result
        return wrapper

    def _tensor_unary_op_wrapper(self, original_func: Callable, op_name: str) -> Callable:
        '''Wrap unary tensor operations (sum, mean, etc.).'''
        @functools.wraps(original_func)
        def wrapper(self_tensor, *args, **kwargs):
            result = original_func(self_tensor, *args, **kwargs)
            caller = self._get_calling_module_fn()
            caller_str = f'{self.Color.GREY}@ [{caller}]{self.Color.END}' if caller else ''
            func_str = f'{self.Color.DARKCYAN}Tensor.{op_name}{self.Color.END}'
            
            print(f'  {self.Color.DARKCYAN}●{self.Color.END} {func_str} {caller_str}')
            print(f'{self.Color.GREY}  ├─{self.Color.END} Input: {self._format_tensor(self_tensor)}')
            print(f'{self.Color.GREY}  └─{self.Color.END} Output: {self._format_tensor(result)}')
            print(f'{self.Color.GREY}  │{self.Color.END}')
            return result
        return wrapper

    def _start_tensor_ops_tracing(self):
        '''Start tracing tensor operations.'''
        # Binary operations (tensor op tensor)
        binary_ops = [
            '__matmul__', 'matmul', '__add__', '__sub__', '__mul__', '__truediv__',
            '__floordiv__', '__mod__', '__pow__', 'mm', 'bmm', 'addmm'
        ]
        
        # Unary operations (tensor.operation())
        unary_ops = [
            'sum', 'mean', 'std', 'var', 'min', 'max', 'argmin', 'argmax',
            'norm', 'abs', 'sqrt', 'exp', 'log', 'squeeze', 'unsqueeze',
            'contiguous', 'clone', 'detach'
        ]
        
        for op_name in binary_ops:
            if hasattr(torch.Tensor, op_name) and op_name not in self.original_tensor_ops:
                self.original_tensor_ops[op_name] = getattr(torch.Tensor, op_name)
                setattr(torch.Tensor, op_name, self._tensor_binary_op_wrapper(self.original_tensor_ops[op_name], op_name))
        
        for op_name in unary_ops:
            if hasattr(torch.Tensor, op_name) and op_name not in self.original_tensor_methods:
                self.original_tensor_methods[op_name] = getattr(torch.Tensor, op_name)
                setattr(torch.Tensor, op_name, self._tensor_unary_op_wrapper(self.original_tensor_methods[op_name], op_name))

    def _stop_tensor_ops_tracing(self):
        '''Stop tracing and restore original tensor methods.'''
        for op_name, original in self.original_tensor_ops.items():
            setattr(torch.Tensor, op_name, original)
        self.original_tensor_ops.clear()
        
        for op_name, original in self.original_tensor_methods.items():
            setattr(torch.Tensor, op_name, original)
        self.original_tensor_methods.clear()


# Convenience function for quick usage
def trace_model(model: nn.Module, name: str = 'Quick Trace'):
    '''
    Quick function to create and return a tracer for a model.
    
    Usage:
        tracer = trace_model(model, 'My Model')
        with tracer.trace(model):
            output = model(input)
    '''
    return Tracer(name)


# Auto-disable colors in non-interactive environments
if not sys.stdout.isatty():
    Color.disable()

