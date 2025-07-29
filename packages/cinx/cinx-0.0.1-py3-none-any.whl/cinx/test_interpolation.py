import jax.numpy as jnp
from jax.test_util import check_grads

from cinx import interp


def test_interp_1d_basic():
    """Test basic 1D interpolation with known points."""
    xp = jnp.array([0.0, 1.0, 2.0, 3.0])
    fp = jnp.array([0.0, 1.0, 0.0, -1.0]) # A simple curve
    x = jnp.array([0.5, 1.5, 2.5])
    f_interp = interp(x, xp, fp)
    f_at_xp = interp(xp, xp, fp)
    assert jnp.allclose(f_at_xp, fp, atol=1e-6)
    assert jnp.all(f_interp >= -1.01) and jnp.all(f_interp <= 1.01) # Small tolerance

def test_interp_1d_edge_points():
    """Test interpolation exactly at the data points."""
    xp = jnp.array([0.0, 1.0, 2.0, 3.0])
    fp = jnp.array([0.0, 1.0, 0.0, -1.0])
    x_query = xp # Query at the original data points

    f_interp = interp(x_query, xp, fp)
    assert jnp.allclose(f_interp, fp, atol=1e-6)

def test_interp_1d_constant_function():
    """Test interpolation of a constant function."""
    xp = jnp.array([0.0, 1.0, 2.0, 3.0])
    fp = jnp.array([5.0, 5.0, 5.0, 5.0])
    x = jnp.array([0.5, 1.5, 2.5])

    f_interp = interp(x, xp, fp)
    assert jnp.allclose(f_interp, jnp.array([5.0, 5.0, 5.0]), atol=1e-6)

def test_interp_2d_basic():
    """Test 2D interpolation (fp has multiple variables)."""
    xp = jnp.array([0.0, 1.0, 2.0, 3.0])
    # Two variables: sin(x) and cos(x)
    fp = jnp.stack([jnp.sin(xp), jnp.cos(xp)], axis=-1) # shape (4, 2)
    x = jnp.array([0.5, 1.5, 2.5])

    f_interp = interp(x, xp, fp) # Should return shape (3, 2)

    assert f_interp.shape == (x.shape[0], fp.shape[-1])

    # Test that interpolation at original points is accurate for 2D case
    f_at_xp = interp(xp, xp, fp)
    assert jnp.allclose(f_at_xp, fp, atol=1e-6)

    # Basic range check
    assert jnp.all(f_interp >= -1.01) and jnp.all(f_interp <= 1.01)

def test_interp_2d_constant_variables():
    """Test 2D interpolation where variables are constant."""
    xp = jnp.array([0.0, 1.0, 2.0, 3.0])
    fp = jnp.array([[1.0, 5.0], [1.0, 5.0], [1.0, 5.0], [1.0, 5.0]]) # Two constant variables
    x = jnp.array([0.5, 1.5, 2.5])

    f_interp = interp(x, xp, fp)
    expected_f = jnp.array([[1.0, 5.0], [1.0, 5.0], [1.0, 5.0]])
    assert jnp.allclose(f_interp, expected_f, atol=1e-6)


def test_interp_differentiability_1d():
    """Test differentiability of interp for 1D case."""
    xp = jnp.array([0.0, 1.0, 2.0, 3.0], dtype=jnp.float32)
    fp = jnp.array([0.0, 1.0, 0.0, -1.0], dtype=jnp.float32)
    x_query = jnp.array([0.5, 1.5, 2.5], dtype=jnp.float32)

    # Define a wrapper function for grad that takes only one argument to differentiate
    def interp_wrapper_fp(fp_val):
        return interp(x_query, xp, fp_val).sum() # Sum for scalar output

    def interp_wrapper_x(x_val):
        return interp(x_val, xp, fp).sum()

    # Check gradients with respect to fp
    check_grads(interp_wrapper_fp, (fp,), order=1, modes=['rev'])

    # Check gradients with respect to x_query
    check_grads(interp_wrapper_x, (x_query,), order=1, modes=['rev'])


def test_interp_differentiability_2d():
    """Test differentiability of interp for 2D case."""
    xp = jnp.array([0.0, 1.0, 2.0, 3.0], dtype=jnp.float32)
    fp = jnp.stack([jnp.sin(xp), jnp.cos(xp)], axis=-1).astype(jnp.float32) # shape (4, 2)
    x_query = jnp.array([0.5, 1.5, 2.5], dtype=jnp.float32)

    def interp_wrapper_fp_2d(fp_val):
        return interp(x_query, xp, fp_val).sum()

    def interp_wrapper_x_2d(x_val):
        return interp(x_val, xp, fp).sum()

    # Check gradients with respect to fp (2D)
    check_grads(interp_wrapper_fp_2d, (fp,), order=1, modes=['rev'])

    # Check gradients with respect to x_query (for 2D fp)
    check_grads(interp_wrapper_x_2d, (x_query,), order=1, modes=['rev'])

def test_interp_x_single_value():
    """Test interpolation when x is a single value, ensuring it's treated as 1D."""
    xp = jnp.array([0.0, 1.0, 2.0, 3.0])
    fp = jnp.array([0.0, 1.0, 0.0, -1.0])
    x = jnp.array([1.5]) # Changed to a 1D array to satisfy ndim > 0 assertion

    f_interp = interp(x, xp, fp)
    assert f_interp.shape == (1,) # Should return a 1D array with one element

    # Test with 2D fp and single x
    fp_2d = jnp.stack([jnp.sin(xp), jnp.cos(xp)], axis=-1)
    f_interp_2d = interp(x, xp, fp_2d)
    assert f_interp_2d.shape == (1, fp_2d.shape[-1]) # Should return a 2D array (1, num_variables)