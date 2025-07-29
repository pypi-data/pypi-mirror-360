import jax.numpy as jnp
import numpy as np
import netket as nk
import electroket


def _simple_particleset():
    cell = electroket.Cell(extent=(1.0,))
    return electroket.ParticleSet(
        [electroket.Electron(), electroket.Electron(m_z=0.5)], cell
    )


def test_particleset_size():
    hi = _simple_particleset()
    assert hi.size == 4


def test_positions_indices_and_random_state():
    cell = electroket.Cell(extent=(1.0,))
    hi = electroket.ParticleSet(
        [electroket.Electron(position=(0.2,)), electroket.Electron()], cell
    )

    assert hi.position_indices == (2,)
    assert hi.positions_hilbert.size == 1

    rs = hi.random_state(nk.jax.PRNGKey(0), 3)
    np.testing.assert_allclose(rs[:, 0], 0.2)


def test_fixed_spin_not_sampled():
    cell = electroket.Cell(extent=(1.0,))
    hi = electroket.ParticleSet(
        [electroket.Electron(m_z=0.5), electroket.Electron()], cell
    )

    rs = hi.random_state(nk.jax.PRNGKey(0), 4)
    np.testing.assert_allclose(rs[:, 1], 0.5)
