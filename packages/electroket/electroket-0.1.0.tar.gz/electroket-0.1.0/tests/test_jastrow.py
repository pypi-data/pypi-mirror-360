import numpy as np
import jax
import jax.numpy as jnp
import pytest

import electroket


def test_onebody_nuclear_cusp():
    mol = electroket.Molecule([("He", [0.0, 0.0, 0.0])])
    jast = electroket.models.OneBodyJastrow(mol)
    x = jnp.zeros((1, mol.positions_hilbert.size))
    params = jast.init(jax.random.PRNGKey(0), x, method=jast.u)

    def f(r):
        pos1 = jnp.array([r, 0.0, 0.0])
        pos2 = jnp.array([1.0, 0.0, 0.0])
        coords = jnp.stack([pos1, pos2]).reshape(-1)
        return jast.apply(params, coords[None, :], method=jast.u)[0].real

    eps = 1e-4
    deriv = (f(eps) - f(0.0)) / eps
    np.testing.assert_allclose(np.asarray(deriv), -2.0, rtol=1e-2, atol=1e-2)


def test_twobody_electron_cusp():
    mol = electroket.Molecule([("He", [0.0, 0.0, 0.0])])
    jast = electroket.models.TwoBodyJastrow(mol)
    x = jnp.zeros((1, mol.positions_hilbert.size))
    params = jast.init(jax.random.PRNGKey(1), x, method=jast.u)

    def f(r):
        pos1 = jnp.array([-0.5 * r, 0.0, 0.0])
        pos2 = jnp.array([0.5 * r, 0.0, 0.0])
        coords = jnp.stack([pos1, pos2]).reshape(-1)
        return jast.apply(params, coords[None, :], method=jast.u)[0].real

    eps = 1e-4
    deriv = (f(eps) - f(0.0)) / eps
    np.testing.assert_allclose(np.asarray(deriv), 0.5, rtol=1e-2, atol=1e-2)


def test_twobody_same_spin_cusp():
    mol = electroket.Molecule([("He", [0.0, 0.0, 0.0]), ("He", [3.0, 0.0, 0.0])])
    jast = electroket.models.TwoBodyJastrow(mol)
    x = jnp.zeros((1, mol.positions_hilbert.size))
    params = jast.init(jax.random.PRNGKey(2), x, method=jast.u)

    def f(r):
        pos1 = jnp.array([-0.5 * r, 0.0, 0.0])
        pos2 = jnp.array([0.5 * r, 0.0, 0.0])
        others = jnp.array([[1.0, 0.0, 0.0], [-1.0, 0.0, 0.0]])
        coords = jnp.concatenate([pos1[None, :], pos2[None, :], others]).reshape(-1)
        return jast.apply(params, coords[None, :], method=jast.u)[0].real

    eps = 1e-4
    deriv = (f(eps) - f(0.0)) / eps
    np.testing.assert_allclose(np.asarray(deriv), 0.25, rtol=1e-2, atol=1e-2)
