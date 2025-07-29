# cinx

[![tests](https://github.com/alonfnt/cinx/actions/workflows/tests.yml/badge.svg)](https://github.com/alonfnt/cinx/actions/workflows/tests.yml)
[![PyPI](https://img.shields.io/pypi/v/cinx.svg)](https://pypi.org/project/cinx/)

`cinx` is a minimal, non-nonsense library for differentiable and fast **cubic spline interpolation** in [JAX](https://docs.jax.dev/en/latest/quickstart.html).

 It's designed to be fully JAX-native, supporting GPU/TPU/CPU execution, and allowing you to backpropagate through your interpolation steps for seamless integration into your machine learning workflows.

## Usage
`cinx` provides a straightforward interp function that handles both single-variable and multi-variable interpolation.
Its pure JAX design means you can trivially use JAX transformations like `jax.vmap` for batch processing and `jax.grad` for gradient calculations.

### Basic 1D Interpolation
```python
import cinx
import jax.numpy as jnp

xp = jnp.linspace(0, 1, 5)
fp = jnp.sin(xp * jnp.pi)
x = jnp.linspace(0, 1, 100)

f = cinx.interp(x, xp, fp)
```

### Multi-variate Interpolation
```python
import jax.numpy as jnp
from cinx import interp

theta = jnp.linspace(0, 2 * jnp.pi, 5)
X_data = jnp.stack((theta, jnp.sin(theta)), axis=-1)
fp = jnp.dot(X_data, rot_matrix(jnp.pi / 4).T)

xp = jnp.linspace(0, 1, len(fp))
x = jnp.linspace(0, 1, 100)

f = interp(x, xp, fp)
```

### Batch Interpolation
```python
import jax
import jax.numpy as jnp
from cinx import interp

theta = jnp.linspace(0, 2 * jnp.pi, 5)
rot_matrix = lambda a: jnp.array([[jnp.cos(a), -jnp.sin(a)], 
                                  [jnp.sin(a), jnp.cos(a)]])
X_data = jnp.stack((theta, jnp.sin(theta)), axis=-1)

angles_batch = jnp.linspace(0, 2 * jnp.pi, 10)
fp = jnp.stack([jnp.dot(X_data, rot_matrix(a).T) for a in angles_batch], axis=0)

xp = jnp.linspace(0, 1, len(fp[0]))
x = jnp.linspace(0, 1, 100)

interp_vmap = jax.vmap(interp, in_axes=(None, None, 0))
f = interp_vmap(x, xp, fp)
```

## Installation
`cinx` can be installed from [PyPI]( https://pypi.org/project/cinx) via `pip`:

```bash
pip install cinx
```

## Citation
You don't have to, but if you use `cinx` in your research and need to reference it, please cite it as follows:

```
@software{alonso_zdyb_cinx,
  author = {Alonso, Albert and Zdyb, Frans},
  title = {cinx: Minimal Cubic Spline Interpolation in JAX},
  url = {https://github.com/alonfnt/cinx},
  version = {0.0.1},
  year = {2025}
}
```
