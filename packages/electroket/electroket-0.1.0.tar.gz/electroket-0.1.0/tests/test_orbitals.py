import jax.numpy as jnp
import electroket


def test_gaussian_orbitals_water():
    water = electroket.Molecule(
        atoms=[
            ("O", [0.0, 0.0, 0.0]),
            ("H", [0.0, -0.757, 0.587]),
            ("H", [0.0, 0.757, 0.587]),
        ],
        units="angstrom",
    )

    orbitals = electroket.gaussian_orbitals(water)
    assert len(orbitals) == 7
    values = jnp.array([orb(jnp.zeros(3)) for orb in orbitals])
    assert values.shape == (7,)
