
import jax
import jax.numpy as jnp

def jax_crps(observation, forecast, ensemble_axis: int = -1):
    """
    Compute the CRPS between an observation and a forecast ensemble.

    Parameters:
    -----------
    observation : array-like, shape (..., D)
        Observation without ensemble dimension.
    forecast : array-like, shape (..., D, E)
        Ensemble forecast with E ensemble members along the last axis (by default).
    ensemble_axis : int, optional
        Axis of the ensemble in the forecast array (default: -1)

    Returns:
    --------
    crps : jnp.ndarray, shape (..., D)
        CRPS at each observation location (or spatial/temporal index).
    """
    forecast = jnp.asarray(forecast)
    observation = jnp.asarray(observation)

    # Move ensemble axis to the last position for consistency
    if ensemble_axis != -1:
        forecast = jnp.moveaxis(forecast, ensemble_axis, -1)

    # Squeeze the last axis if it's a singleton (i.e., shape (..., D, 1))
    if observation.ndim == forecast.ndim and observation.shape[-1] == 1:
        observation = jnp.squeeze(observation, axis=-1)


    @jax.jit
    def _crps(obs, fcst):
        obs_expanded = obs[..., jnp.newaxis]  # shape (..., D, 1)
        term1 = jnp.mean(jnp.abs(fcst - obs_expanded), axis=-1)

        fcst1 = fcst[..., :, jnp.newaxis]
        fcst2 = fcst[..., jnp.newaxis, :]
        term2 = 0.5 * jnp.mean(jnp.abs(fcst1 - fcst2), axis=(-2, -1))

        return term1 - term2

    return _crps(observation, forecast)


def jax_crps_mean(observation, forecast, ensemble_axis: int = -1):
    """Compute the mean CRPS across all observations."""
    crps = jax_crps(observation, forecast, ensemble_axis)
    return jnp.mean(crps)