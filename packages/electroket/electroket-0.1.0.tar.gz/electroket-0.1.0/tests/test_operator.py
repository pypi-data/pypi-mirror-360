import jax.numpy as jnp
import numpy as np
import pytest

import electroket


def test_kinetic_particle_init():
    geo = electroket.Cell(extent=(1.0,))
    p = electroket.Particle(geometry=geo, mass=2.0)
    kin = electroket.KineticEnergy(p)
    assert kin.hilbert is p
    np.testing.assert_allclose(np.asarray(kin.mass), [2.0])
    assert kin.is_hermitian


def test_kinetic_particleset_init():
    cell = electroket.Cell(extent=(1.0,))
    hi = electroket.ParticleSet([electroket.Electron(), electroket.Proton()], cell)
    kin = electroket.KineticEnergy(hi)
    masses = np.asarray([1.0, 1836.15267389])
    np.testing.assert_allclose(np.asarray(kin.mass), masses)


def test_kinetic_requires_mass():
    geo = electroket.Cell(extent=(1.0,))
    p = electroket.Particle(geometry=geo)
    with pytest.raises(ValueError):
        electroket.KineticEnergy(p)


def test_constant_wavefunction_zero_energy():
    geo = electroket.Cell(extent=(1.0,), pbc=False)
    p = electroket.Particle(geometry=geo, mass=1.0)
    kin = electroket.KineticEnergy(p)

    def logpsi(params, x):
        return jnp.zeros(())

    x = jnp.zeros((3, p.size))
    coeff = kin._pack_arguments()
    res = kin._expect_kernel(logpsi, None, x, coeff)
    np.testing.assert_allclose(np.asarray(res), 0.0)


def test_harmonic_oscillator_local_energy():
    cell = electroket.Cell(extent=(5.0,), pbc=False)
    m = 2.0
    hbar = 0.5
    p = electroket.Particle(geometry=cell, mass=m)
    kin = electroket.KineticEnergy(p, hbar=hbar)
    alpha = 0.4

    def logpsi(params, x):
        return -alpha * jnp.sum(x**2, axis=-1)

    x = jnp.linspace(-1.0, 1.0, 5).reshape(-1, 1)
    coeff = kin._pack_arguments()
    res = kin._expect_kernel(logpsi, None, x, coeff)
    expected = (hbar**2 * alpha) / m - (2 * hbar**2 * alpha**2 / m) * x[:, 0] ** 2
    np.testing.assert_allclose(np.asarray(res), np.asarray(expected))


def test_potential_energy_expectation():
    cell = electroket.Cell(extent=(2.0,), pbc=False)
    p = electroket.Particle(geometry=cell)

    def pot(x):
        return 0.5 * x[0] ** 2

    pot_op = electroket.PotentialEnergy(p, pot, coefficient=2.0)

    def logpsi(params, x):
        return jnp.zeros(())

    x = jnp.linspace(-1.0, 1.0, 3).reshape(-1, 1)
    args = pot_op._pack_arguments()
    res = pot_op._expect_kernel(logpsi, None, x, args)
    expected = 2.0 * 0.5 * x[:, 0] ** 2
    np.testing.assert_allclose(np.asarray(res), np.asarray(expected))


def test_sum_operator_combines_terms():
    cell = electroket.Cell(extent=(1.0,), pbc=False)
    p = electroket.Particle(geometry=cell, mass=1.0)

    kin = electroket.KineticEnergy(p)

    def pot(x):
        return x[0] ** 2

    pot_op = electroket.PotentialEnergy(p, pot)
    ham = kin + pot_op
    assert isinstance(ham, electroket.SumOperator)

    def logpsi(params, x):
        return jnp.zeros(())

    x = jnp.array([[0.3], [-0.3]])
    args = ham._pack_arguments()
    res = ham._expect_kernel(logpsi, None, x, args)
    expected = jnp.sum(x**2, axis=-1)
    np.testing.assert_allclose(np.asarray(res), np.asarray(expected))


def test_harmonic_oscillator_ground_state_local_energy():
    cell = electroket.Cell(extent=(5.0,), pbc=False)
    p = electroket.Particle(geometry=cell, mass=1.0)
    kin = electroket.KineticEnergy(p)

    def pot(x):
        return 0.5 * x[0] ** 2

    pot_op = electroket.PotentialEnergy(p, pot)
    ham = kin + pot_op
    alpha = 0.5

    def logpsi(params, x):
        return -alpha * jnp.sum(x**2, axis=-1)

    x = jnp.linspace(-2.0, 2.0, 7).reshape(-1, 1)
    args = ham._pack_arguments()
    res = ham._expect_kernel(logpsi, None, x, args)
    expected = jnp.full(x.shape[0], 0.5)
    np.testing.assert_allclose(np.asarray(res), np.asarray(expected))


def test_pair_interaction_expectation():
    cell = electroket.Cell(extent=(2.0,), pbc=False)
    hi = electroket.ParticleSet([electroket.Electron(), electroket.Electron()], cell)

    pair = electroket.PairInteraction(hi, lambda r: r**2, coefficient=2.0)

    def logpsi(params, x):
        return jnp.zeros(())

    x = jnp.array(
        [
            [0.1, -0.5, 0.3, 0.5],
            [0.0, 0.5, 0.5, -0.5],
        ]
    )
    args = pair._pack_arguments()
    res = pair._expect_kernel(logpsi, None, x, args)
    r = jnp.abs(x[:, 0] - x[:, 2])
    expected = 2.0 * r**2
    np.testing.assert_allclose(np.asarray(res), np.asarray(expected))
