import jax
import jax.numpy as jnp
import numpy as np

import electroket


def test_gaussian_model_evaluates_quadratic_form():
    model = electroket.models.Gaussian()
    x = jnp.array([[0.0, 1.0], [1.0, 2.0]])
    params = model.init(jax.random.PRNGKey(0), x)
    kernel = params["params"]["kernel"]
    sigma = jnp.dot(kernel.T, kernel)
    expected = -0.5 * jnp.einsum("...i,ij,...j", x, sigma, x)
    out = model.apply(params, x)
    np.testing.assert_allclose(np.asarray(out), np.asarray(expected))
