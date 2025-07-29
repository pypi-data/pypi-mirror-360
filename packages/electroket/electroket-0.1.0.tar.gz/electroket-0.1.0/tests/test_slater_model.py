import jax
import jax.numpy as jnp
import numpy as np
from flax import linen as nn
import electroket


def test_slater_model_evaluates():
    mol = electroket.Molecule(
        atoms=[("H", [0.0, 0.0, -0.35]), ("H", [0.0, 0.0, 0.35])],
        units="angstrom",
    )
    model = electroket.models.Slater(mol)
    x = jnp.zeros((2, mol.positions_hilbert.size))
    params = model.init(jax.random.PRNGKey(0), x)
    out = model.apply(params, x)
    assert out.shape == (2,)
    assert jnp.iscomplexobj(out)


def test_molecular_slater_full_state():
    mol = electroket.Molecule(
        atoms=[("H", [0.0, 0.0, -0.35]), ("H", [0.0, 0.0, 0.35])],
        units="angstrom",
    )
    model = electroket.models.MolecularSlater(mol)
    x = jnp.zeros((2, mol.size))
    params = model.init(jax.random.PRNGKey(1), x)
    out = model.apply(params, x)
    assert out.shape == (2,)
    assert jnp.iscomplexobj(out)


def test_eval_basis_converts_units():
    mol = electroket.Molecule(
        atoms=[("H", [0.0, 0.0, -0.35]), ("H", [0.0, 0.0, 0.35])],
        units="bohr",
    )
    model = electroket.models.Slater(mol)
    params = model.init(
        jax.random.PRNGKey(2), jnp.zeros((1, mol.positions_hilbert.size))
    )
    coords_bohr = jnp.array([[[0.1, 0.0, 0.0], [0.0, 0.1, 0.0]]])
    phi_model = model.apply(params, coords_bohr, method=model._eval_basis)

    orbitals = electroket.gaussian_orbitals(mol)
    coords_ang = coords_bohr * electroket.molecule.orbitals.BOHR_ANG
    coords_flat = coords_ang.reshape((-1, coords_ang.shape[-1]))
    vals = [jax.vmap(o)(coords_flat) for o in orbitals]
    expected = jnp.stack(vals, axis=-1).reshape(
        coords_bohr.shape[:-1] + (len(orbitals),)
    )

    np.testing.assert_allclose(np.asarray(phi_model), np.asarray(expected))


def test_eval_basis_respects_orbital_units():
    mol = electroket.Molecule(
        atoms=[("H", [0.0, 0.0, 0.0]), ("H", [0.0, 0.0, 1.0])],
        units="bohr",
    )

    def lin_orb(r):
        return r[..., 0] + 2 * r[..., 1] + 3 * r[..., 2]

    lin_orb.units = "bohr"

    class DummySlater(electroket.models.Slater):
        def setup(self):
            self._orbitals = (lin_orb,)
            self._orbital_units = "bohr"
            self._n_basis = 1
            self._up_idx = tuple(
                i
                for i, e in enumerate(self.mol.electrons)
                if e.m_z is None or e.m_z > 0
            )
            self._down_idx = tuple(
                i
                for i, e in enumerate(self.mol.electrons)
                if e.m_z is not None and e.m_z < 0
            )
            self._n_up = len(self._up_idx)
            self._n_down = len(self._down_idx)

        @nn.compact
        def __call__(self, x):
            dim = self.mol.cell.dimension
            coords = x.reshape(x.shape[:-1] + (self._n_up + self._n_down, dim))
            phi = self._eval_basis(coords)
            coeff_up = self.param(
                "coeff_up",
                self.coeff_init,
                (self._n_up, self._n_basis),
                self.param_dtype,
            )
            coeff_down = self.param(
                "coeff_down",
                self.coeff_init,
                (self._n_down, self._n_basis),
                self.param_dtype,
            )
            up_vals = jnp.einsum("...ib,ab->...ia", phi[..., self._up_idx, :], coeff_up)
            down_vals = jnp.einsum(
                "...ib,ab->...ia", phi[..., self._down_idx, :], coeff_down
            )
            sign_u, logdet_u = jnp.linalg.slogdet(up_vals)
            sign_d, logdet_d = jnp.linalg.slogdet(down_vals)
            return logdet_u + logdet_d + jnp.log(sign_u * sign_d + 0j)

    model = DummySlater(mol)
    params = model.init(
        jax.random.PRNGKey(3), jnp.zeros((1, mol.positions_hilbert.size))
    )

    coords = jnp.array([[[0.1, 0.2, 0.3], [0.3, 0.2, 0.1]]])
    phi_model = model.apply(params, coords, method=model._eval_basis)
    expected = jax.vmap(lin_orb)(coords.reshape((-1, 3))).reshape(
        coords.shape[:-1] + (1,)
    )

    np.testing.assert_allclose(np.asarray(phi_model), np.asarray(expected))
