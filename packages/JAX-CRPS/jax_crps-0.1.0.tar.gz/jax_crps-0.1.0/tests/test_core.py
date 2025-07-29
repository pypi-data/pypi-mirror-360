import jax.numpy as jnp
import jax.random as random
from JAX_CRPS.core import jax_crps 

def test_crps_simple_case():
    """Test CRPS for a simple known input-output."""
    obs = jnp.array([0.0])
    forecast = jnp.array([[1.0, -1.0]])  # shape (1, 2)
    expected = jnp.mean(jnp.abs(forecast - obs[..., None])) - 0.5 * jnp.mean(jnp.abs(forecast - forecast.T))
    result = jax_crps(obs, forecast)
    assert jnp.allclose(result, expected, atol=1e-6), f"Expected {expected}, got {result}"

def test_crps_accepts_singleton_observation():
    """Test that CRPS accepts (..., D, 1)-shaped observation arrays."""
    obs = jnp.array([[1.0], [2.0]])  # shape (2, 1)
    forecast = jnp.array([[0.5, 1.5], [1.5, 2.5]])  # shape (2, 2)

    result1 = jax_crps(obs, forecast)
    result2 = jax_crps(jnp.squeeze(obs, -1), forecast)

    assert jnp.allclose(result1, result2), "CRPS should match with or without singleton dimension."


def test_crps_high_dimensional():
    """Test that CRPS works with high-dimensional inputs."""
    key = random.PRNGKey(0)
    obs = random.normal(key, (4, 8, 8))  # shape (B, H, W)
    forecast = obs[..., None] + 0.1 * random.normal(key, (4, 8, 8, 20))  # shape (B, H, W, E)

    result = jax_crps(obs, forecast)
    assert result.shape == obs.shape, "CRPS output should match observation shape."

def test_crps_high_dimensional_equal_input():
    """Test that CRPS works with high-dimensional inputs."""
    key = random.PRNGKey(0)
    obs = random.normal(key, (4, 8, 8, 1))  # shape (B, H, W)
    forecast = obs[...] + 0.1 * random.normal(key, (4, 8, 8, 20))  # shape (B, H, W, E)

    result = jax_crps(obs, forecast)
    assert result.shape == (4, 8, 8), f"Expected {(4, 8, 8)}, got {result.shape}"


def test_crps_does_not_crash_on_vector_batch():
    """Test a vector-valued batch input."""
    obs = jnp.array([[1.0, 2.0], [3.0, 4.0]])  # shape (2, 2)
    forecast = jnp.array([
        [[0.9, 1.1], [2.1, 1.9]],
        [[2.9, 3.1], [4.1, 3.9]]
    ])  # shape (2, 2, 2)

    result = jax_crps(obs, forecast)
    assert result.shape == (2, 2), "CRPS shape mismatch on vector batch."

def test_perfect_forecast():
    """Test CRPS with a perfect forecast."""
    """In this case, CRPS should be zero."""
    obs = jnp.array([1.0, 2.0])
    fcst = jnp.array([[1.0, 1.0], [2.0, 2.0]])
    crps = jax_crps(obs, fcst)
    assert jnp.allclose(crps, jnp.zeros_like(obs), atol=1e-6), f"Expected {jnp.zeros_like(obs)}, got {crps}"

def test_notperfect_forecast():
    """Test CRPS with a not perfect forecast."""
    """In this case, CRPS should not be perfectly zero."""
    obs = jnp.array([1.0, 2.0, 3.0])
    fcst = jnp.array([[1.0, 1.0, 1.0], [2.0, 2.0, 2.0], [3.0, 42.0, 3.0]])
    crps = jax_crps(obs, fcst)
    assert jnp.not_equal(crps, jnp.zeros_like(obs)).any(), f"Expected {jnp.zeros_like(obs)}, got {crps}"

def test_constant_forecast_error():
    """Test CRPS with a constant forecast error."""
    """In this case, CRPS should be the mean absolute error."""
    obs = jnp.array([0.0])
    fcst = jnp.array([[1.0, 1.0, 1.0]])
    crps = jax_crps(obs, fcst)
    expected = jnp.mean(jnp.abs(fcst - obs[..., None]), axis=-1)
    assert jnp.allclose(crps, expected, atol=1e-6), f"Expected {expected}, got {crps}"


def test_jax_crps_autodiff():
    import jax
    obs = jnp.array([0.5, 1.0])
    # Forecast shape: (D=2, E=3)
    fcst = jnp.array([
        [0.4, 0.6, 0.5],
        [0.9, 1.1, 1.0],
    ])

    # Function to compute scalar summary of CRPS for grad
    def crps_sum(fcst_input):
        # Note: keep ensemble axis -1 by default
        crps = jax_crps(obs, fcst_input)
        return jnp.sum(crps)  # scalar output for grad

    grad_fn = jax.grad(crps_sum)
    grad = grad_fn(fcst)

    # Check gradient shape matches forecast shape
    assert grad.shape == fcst.shape

    # Check no NaNs or Infs in gradient
    assert jnp.all(jnp.isfinite(grad))

    # Optionally check that gradients are not all zero
    assert jnp.any(grad != 0)

def main():
    print(1+1)
    print("Running CRPS unit tests...")
    test_crps_simple_case()
    print("✔ test_crps_simple_case passed")

    test_crps_accepts_singleton_observation()
    print("✔ test_crps_accepts_singleton_observation passed")

    test_crps_high_dimensional()
    print("✔ test_crps_high_dimensional passed")

    test_crps_high_dimensional_equal_input()
    print("✔ test_crps_high_dimensional_equal_input passed")

    test_crps_does_not_crash_on_vector_batch()
    print("✔ test_crps_does_not_crash_on_vector_batch passed")

    test_perfect_forecast()
    print("✔ test_perfect_forecast passed")

    test_notperfect_forecast()
    print("✔ test_notperfect_forecast passed")

    test_constant_forecast_error()
    print("✔ test_constant_forecast_error passed")

    test_jax_crps_autodiff()
    print("✔ test_jax_crps_autodiff passed")

    print("✅ All CRPS tests passed!")


if __name__ == "__main__":
    main()