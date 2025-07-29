import jax
import netket as nk
import electroket


def test_h2_vmc_runs():
    mol = electroket.Molecule(
        atoms=[("H", [0.0, 0.0, -0.35]), ("H", [0.0, 0.0, 0.35])],
        units="angstrom",
    )
    hilb = mol
    kin = electroket.operator.KineticEnergy(mol)
    coul = electroket.operator.CoulombInteraction(mol)
    ham = kin + coul
    model = electroket.models.MolecularSlater(mol)
    sampler = electroket.sampler.MetropolisSampler(
        hilb, electroket.sampler.GaussianRule(sigma=0.1), n_chains_per_rank=1
    )
    vstate = nk.vqs.MCState(
        sampler,
        model,
        n_samples=4,
        n_discard_per_chain=2,
        seed=0,
        sampler_seed=1,
    )
    sr = nk.optimizer.SR(diag_shift=0.05)
    opt = nk.optimizer.Sgd(learning_rate=0.1)
    driver = nk.driver.VMC(
        hamiltonian=ham,
        optimizer=opt,
        variational_state=vstate,
        preconditioner=sr,
    )
    driver.run(n_iter=1)


def test_harmonic_oscillator_vmc_runs():
    cell = electroket.Cell(extent=(5.0,), pbc=False)
    hilb = electroket.Particle(geometry=cell, mass=1.0)
    kin = nk.operator.KineticEnergy(hilb, mass=1.0)
    pot = nk.operator.PotentialEnergy(hilb, lambda x: 0.5 * x[0] ** 2)
    ham = kin + pot
    model = electroket.models.Gaussian()
    sampler = electroket.sampler.MetropolisSampler(
        hilb, electroket.sampler.GaussianRule(sigma=0.5), n_chains_per_rank=1
    )
    vstate = nk.vqs.MCState(
        sampler,
        model,
        n_samples=4,
        n_discard_per_chain=2,
        seed=0,
        sampler_seed=1,
    )
    sr = nk.optimizer.SR(diag_shift=0.05)
    opt = nk.optimizer.Sgd(learning_rate=0.1)
    driver = nk.driver.VMC(
        hamiltonian=ham,
        optimizer=opt,
        variational_state=vstate,
        preconditioner=sr,
    )
    driver.run(n_iter=1)
