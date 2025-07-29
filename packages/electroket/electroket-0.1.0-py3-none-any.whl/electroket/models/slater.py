from __future__ import annotations

from typing import Callable

import jax
import jax.numpy as jnp
from flax import linen as nn
from flax.linen.initializers import orthogonal
from netket.utils.types import Array, DType, NNInitFunc

from ..molecule import Molecule, gaussian_orbitals
from ..molecule.orbitals import BOHR_ANG


class Slater(nn.Module):
    """Slater determinant wavefunction for molecules."""

    mol: Molecule
    basis: str = "STO-3G"
    param_dtype: DType = jnp.float64
    coeff_init: NNInitFunc = orthogonal()

    def setup(self) -> None:
        orbitals = gaussian_orbitals(self.mol, basis=self.basis)
        self._orbitals: tuple[Callable[[Array], Array], ...] = orbitals
        self._orbital_units = getattr(orbitals[0], "units", "angstrom")
        self._n_basis = len(orbitals)
        self._up_idx = tuple(
            i for i, e in enumerate(self.mol.electrons) if e.m_z is None or e.m_z > 0
        )
        self._down_idx = tuple(
            i
            for i, e in enumerate(self.mol.electrons)
            if e.m_z is not None and e.m_z < 0
        )
        self._n_up = len(self._up_idx)
        self._n_down = len(self._down_idx)

    def _eval_basis(self, coords: Array) -> Array:
        """Return basis orbitals evaluated at ``coords``.

        Parameters
        ----------
        coords
            Electronic coordinates in Bohr.

        Returns
        -------
        Array
            Values of all basis orbitals at ``coords``.

        Notes
        -----
        If the orbitals are defined in Angstrom, ``coords`` are converted
        before evaluation. Otherwise, they are used as-is.
        """

        if self._orbital_units == "angstrom":
            coords_use = coords * BOHR_ANG
        else:
            coords_use = coords
        coords_flat = coords_use.reshape((-1, coords.shape[-1]))
        vals = [jax.vmap(orb)(coords_flat) for orb in self._orbitals]
        phi = jnp.stack(vals, axis=-1)
        phi = phi.reshape(coords.shape[:-1] + (self._n_basis,))
        return phi

    @nn.compact
    def __call__(self, x: Array) -> Array:
        dim = self.mol.cell.dimension
        coords = x.reshape(x.shape[:-1] + (self._n_up + self._n_down, dim))
        phi = self._eval_basis(coords)  # (..., n_elec, n_basis)

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


class MolecularSlater(nn.Module):
    """Slater model acting on the full molecular Hilbert space."""

    mol: Molecule
    basis: str = "STO-3G"
    param_dtype: DType = jnp.float64
    coeff_init: NNInitFunc = orthogonal()

    def setup(self) -> None:
        self.slater = Slater(
            self.mol,
            basis=self.basis,
            param_dtype=self.param_dtype,
            coeff_init=self.coeff_init,
        )
        self.pos_idx = self.mol.position_indices

    def __call__(self, x: Array) -> Array:
        return self.slater(x[..., self.pos_idx])


__all__ = ["Slater", "MolecularSlater"]
