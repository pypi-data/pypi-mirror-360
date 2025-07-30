# Tracy NN

**Tracy NN** is a lightweight debugging and inspection tool for PyTorch models. It helps you trace and log tensor shapes and operations as data flows through your model — especially useful for understanding complex architectures like transformers.

---

## Features

-  Trace any PyTorch `nn.Module` and log all tensor shapes and operations
-  Supports custom modules and `nn.Sequential` models
-  Detects common operations like `@`, `.view`, `.permute`, `.transpose`, and more
-  Lightweight: only requires a single forward pass to log everything
-  Supports nested modules and submodules with readable indentation
-  Hooks into PyTorch without modifying your model
-  Context manager support: use it inline with minimal code
-  Clean readable terminal logs

---

## Installation

```bash
pip install tracy_nn
```

---

## Usage

### Basic usage

```python
import torch
import torch.nn as nn
from tracy_nn import Tracer

x = torch.rand(batch_size, seq_len, d_in)
mha = MHA(d_in, d_out, seq_len, num_heads, context_window, dropout)

tracer = Tracer('MHA')
tracer.start(mha)

output = mha(x)

tracer.stop()
```

### Using the context manager

```python
from tracy_nn import Tracer

tracer = Tracer('MyModel')
with tracer.trace(model):
    output = model(input_tensor)
```

### Even shorter with `trace_model`

```python
from tracy_nn import trace_model

tracer = trace_model(model, 'MyModel')
with tracer.trace(model):
    output = model(input_tensor)
```

---

## Note!

- **Do not** use `tracy_nn` during training — it will log every operation and slow things down.
- Only one forward pass is needed to trace everything.
- Some functional calls like `torch.cat()` may not get traced. Use `Tensor.cat()` or their method equivalents for better compatibility.
- Standard Python operations like `@`, `+`, `/`, etc., are translated internally to their traced PyTorch equivalents.

---

## Why did i make it?

I built Tracy NN while struggling to understand matrix transformations in transformers. By using PyTorch’s hook system, I was able to introspect every tensor flowing through my model — and I hope this helps other **curious** people build a better mental model of how neural networks work.

---

## License

MIT License
