import electroket


def test_molecule_water():
    water = electroket.Molecule(
        atoms=[
            ("O", [0.0, 0.0, 0.0]),
            ("H", [0.0, -0.757, 0.587]),
            ("H", [0.0, 0.757, 0.587]),
        ],
        units="angstrom",
    )

    assert isinstance(water, electroket.ParticleSet)
    assert water.n_particles == 13
    assert water.positions_hilbert.size == 30

    spins = [p.m_z for p in water.electrons]
    assert spins.count(0.5) == 5
    assert spins.count(-0.5) == 5
