from __future__ import annotations

from typing import Callable

import jax
import jax.numpy as jnp
from flax import linen as nn
from netket.utils.types import Array, DType

from ..molecule import Molecule, gaussian_orbitals
from ..molecule.orbitals import BOHR_ANG


@jax.custom_jvp
def _safe_norm(x: Array) -> Array:
    """Return ``jnp.linalg.norm`` with finite gradient at ``x=0``."""

    return jnp.linalg.norm(x, axis=-1)


@_safe_norm.defjvp
def _safe_norm_jvp(primals, tangents):
    (x,), (t,) = primals, tangents
    norm = jnp.linalg.norm(x, axis=-1)
    zero = norm == 0
    norm_safe = jnp.where(zero, 1.0, norm)
    dnorm_dt = jnp.sum(x * t, axis=-1) / norm_safe
    dnorm_dt = jnp.where(zero, 0.0, dnorm_dt)
    return norm, dnorm_dt


class OneBodyJastrow(nn.Module):
    """One-body Jastrow factor for molecules."""

    mol: Molecule
    basis: str = "STO-3G"
    param_dtype: DType = jnp.float64

    def setup(self) -> None:
        self._dim = self.mol.cell.dimension
        self._Z = jnp.asarray(
            [p.charge for p in self.mol.nuclei], dtype=self.param_dtype
        )
        self._R = jnp.asarray(
            [p.position for p in self.mol.nuclei], dtype=self.param_dtype
        )

        orbitals = gaussian_orbitals(self.mol, basis=self.basis)
        self._orbitals: tuple[Callable[[Array], Array], ...] = orbitals
        self._orbital_units = getattr(orbitals[0], "units", "angstrom")
        self._n_basis = len(orbitals)

        self._n_elec = len(self.mol.electrons)

    def _eval_basis(self, coords: Array) -> Array:
        """Return AO basis values at ``coords``.

        Parameters
        ----------
        coords
            Electronic coordinates in Bohr.

        Returns
        -------
        Array
            Values of each basis orbital at ``coords``.
        """

        if self._orbital_units == "angstrom":
            coords_use = coords * BOHR_ANG
        else:
            coords_use = coords
        coords_flat = coords_use.reshape((-1, coords_use.shape[-1]))
        vals = [jax.vmap(o)(coords_flat) for o in self._orbitals]
        phi = jnp.stack(vals, axis=-1)
        phi = phi.reshape(coords_use.shape[:-1] + (self._n_basis,))
        return phi

    @nn.compact
    def u(self, x: Array) -> Array:
        """Evaluate the one-body Jastrow term.

        Parameters
        ----------
        x
            Flattened electronic coordinates in Bohr.

        Returns
        -------
        Array
            Value of the one-body Jastrow factor for each configuration.
        """

        b = self.param(
            "b", nn.initializers.zeros, (self._Z.shape[0],), self.param_dtype
        )
        coeff = self.param(
            "coeff", nn.initializers.zeros, (self._n_basis,), self.param_dtype
        )

        coords = x.reshape(x.shape[:-1] + (self._n_elec, self._dim))

        diff = coords[..., :, None, :] - self._R
        r = _safe_norm(diff)
        cusp = -self._Z * r / (1.0 + b * r)
        cusp = jnp.sum(cusp, axis=-1)

        phi = self._eval_basis(coords)
        ao = jnp.einsum("...ib,b->...i", phi, coeff)

        return jnp.sum(cusp + ao, axis=-1)

    __call__ = u


class TwoBodyJastrow(nn.Module):
    """Electron–electron Jastrow factor with spin-dependent cusps."""

    mol: Molecule
    param_dtype: DType = jnp.float64

    def setup(self) -> None:
        self._dim = self.mol.cell.dimension
        self._n_elec = len(self.mol.electrons)
        self._cell = self.mol.cell

        spins = [1 if e.m_z is None or e.m_z > 0 else -1 for e in self.mol.electrons]

        same = []
        opp = []
        for i in range(self._n_elec):
            for j in range(i + 1, self._n_elec):
                if spins[i] == spins[j]:
                    same.append((i, j))
                else:
                    opp.append((i, j))

        if same:
            self._same_i = jnp.asarray([p[0] for p in same], dtype=int)
            self._same_j = jnp.asarray([p[1] for p in same], dtype=int)
        else:
            self._same_i = jnp.asarray([], dtype=int)
            self._same_j = jnp.asarray([], dtype=int)

        if opp:
            self._opp_i = jnp.asarray([p[0] for p in opp], dtype=int)
            self._opp_j = jnp.asarray([p[1] for p in opp], dtype=int)
        else:
            self._opp_i = jnp.asarray([], dtype=int)
            self._opp_j = jnp.asarray([], dtype=int)

    @nn.compact
    def u(self, x: Array) -> Array:
        """Evaluate the two-body Jastrow term.

        Parameters
        ----------
        x
            Flattened electronic coordinates in Bohr.

        Returns
        -------
        Array
            Value of the two-body Jastrow factor for each configuration.
        """

        beta_same_raw = self.param(
            "beta_same", nn.initializers.zeros, (), self.param_dtype
        )
        beta_opp_raw = self.param(
            "beta_opposite", nn.initializers.zeros, (), self.param_dtype
        )

        beta_same = jnp.exp(beta_same_raw)
        beta_opp = jnp.exp(beta_opp_raw)

        coords = x.reshape(x.shape[:-1] + (self._n_elec, self._dim))
        if self._same_i.size + self._opp_i.size == 0:
            return jnp.zeros(x.shape[:-1], dtype=self.param_dtype)

        if coords.ndim == 2:
            # ``pairwise_displacements`` expects an ``(n_elec, dim)`` array. When
            # a batch dimension is absent, calling ``vmap`` would incorrectly
            # split the electron coordinates along the first axis and lead to
            # shape errors.  Avoid ``vmap`` in this case.
            disp = self._cell.pairwise_displacements(coords)
        else:
            disp = jax.vmap(self._cell.pairwise_displacements)(coords)
        dist = _safe_norm(disp)

        val = jnp.zeros(x.shape[:-1], dtype=self.param_dtype)
        if self._opp_i.size > 0:
            r_opp = dist[..., self._opp_i, self._opp_j]
            term_opp = 0.5 * r_opp / (1.0 + beta_opp * r_opp)
            val = val + jnp.sum(term_opp, axis=-1)

        if self._same_i.size > 0:
            r_same = dist[..., self._same_i, self._same_j]
            term_same = 0.25 * r_same / (1.0 + beta_same * r_same)
            val = val + jnp.sum(term_same, axis=-1)

        return val

    __call__ = u


class TotalJastrow(nn.Module):
    """Convenience wrapper combining one- and two-body Jastrow factors."""

    one_body: OneBodyJastrow | None = None
    two_body: TwoBodyJastrow | None = None

    def log_jastrow(self, x: Array) -> Array:
        """Return the total Jastrow factor.

        Parameters
        ----------
        x
            Flattened electronic coordinates in Bohr.

        Returns
        -------
        Array
            Combined value of all contained Jastrow factors.
        """

        val = 0.0
        if self.one_body is not None:
            val = val + self.one_body.u(x)
        if self.two_body is not None:
            val = val + self.two_body.u(x)
        return val

    __call__ = log_jastrow


__all__ = ["OneBodyJastrow", "TwoBodyJastrow", "TotalJastrow"]
