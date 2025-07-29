import jax
import jax.numpy as jnp

CUBIC_COEFFS = jnp.array(
    [
        [2.0, -2.0, 1.0, 1.0],
        [-3.0, 3.0, -2.0, -1.0],
        [0.0, 0.0, 1.0, 0.0],
        [1.0, 0.0, 0.0, 0.0],
    ]
)


def _catmull_slopes(xp, fp):
    xp = jnp.pad(xp, (1, 1), mode="edge")
    fp = jnp.pad(fp, (1, 1), mode="edge")
    return (fp[2:] - fp[:-2]) / (xp[2:] - xp[:-2])


def _hermite_segment(xq, xp, fp, sp):
    i = jnp.clip(jnp.searchsorted(xp, xq, side="right") - 1, 0, xp.size - 2)
    x0, x1 = xp[i], xp[i + 1]
    p0, p1 = fp[i], fp[i + 1]
    m0, m1 = sp[i], sp[i + 1]
    h = x1 - x0
    t = (xq - x0) / h
    F = jnp.array([p0, p1, h * m0, h * m1])
    coef = CUBIC_COEFFS @ F
    return ((coef[0]*t + coef[1])*t + coef[2])*t + coef[3]


@jax.jit
def interp(x, xp, fp):
    """
    Interpolate the values of `fp` at the points `xp` to the points `x`.

    Args:
        - x: The points at which to evaluate the interpolated values.
        - xp: The points at which the values `fp` are defined.
        - fp: The values to interpolate.

    Returns:
        - The interpolated values at the points `x`.
    """
    ndim = x.ndim

    assert ndim > 0, "x must have at least one dimension but got 0 dimensions"
    assert ndim < 3, f"x must have at most two dimensions but got {ndim}"

    if fp.ndim == 2:
        slopes = jax.vmap(_catmull_slopes, in_axes=(None, 1))(xp, fp)
        h_func = jax.vmap(_hermite_segment, in_axes=(None, None, 1, 0))
        f = jax.vmap(lambda z: h_func(z, xp, fp, slopes))(x.ravel())
        return f.reshape((*x.shape, fp.shape[-1]))
    else:
        xp, fp = jnp.broadcast_arrays(xp, fp)
        slopes = _catmull_slopes(xp, fp)
        f = jax.vmap(lambda z: _hermite_segment(z, xp, fp, slopes))(x.ravel())
        return f.reshape(x.shape)