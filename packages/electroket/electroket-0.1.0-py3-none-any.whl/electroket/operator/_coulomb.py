from __future__ import annotations

from functools import partial
from typing import Callable

import jax
import jax.numpy as jnp
from netket.utils import HashableArray
from netket.utils.types import Array, DType, PyTree

from ._ewald import build_ewald_energy
from ..geometry.cell import Cell
from ..hilbert.particle import Particle, ParticleSet, SpinfulParticle
from ._continuous_operator import ContinuousOperator


class CoulombInteraction(ContinuousOperator):
    """Coulomb interaction energy for a :class:`ParticleSet`.

    This operator computes the pairwise Coulomb interaction among the
    particles contained in ``hilbert``. Charges are automatically inferred
    from the :class:`~electroket.hilbert.particle.Particle` or
    :class:`~electroket.hilbert.particle.SpinfulParticle` instances used to build
    the :class:`ParticleSet`.

    Parameters
    ----------
    hilbert:
        The particle set describing the system.
    ewald:
        If ``True`` and the simulation cell has fully periodic boundary
        conditions, the energy is computed using Ewald summation.
        Mixed boundary conditions are not supported.
    dtype:
        Optional data type of the charges.
    target_force_rms:
        Desired RMS force error when using Ewald summation.  Ignored if
        ``ewald=False``.
    safety:
        Safety factor applied to the automatically determined reciprocal
        cutoff when using Ewald summation.

    Notes
    -----
    The Coulomb potential is set to :math:`1/r` in the units of the
    underlying geometry.  Fixed particle positions, if provided when
    constructing ``hilbert``, are treated as immutable and contribute to the
    total energy accordingly.
    """

    def __init__(
        self,
        hilbert: ParticleSet,
        *,
        ewald: bool = False,
        dtype: DType | None = None,
        target_force_rms: float = 1e-4,
        safety: float = 2.0,
    ) -> None:
        if not isinstance(hilbert, ParticleSet):
            raise TypeError("hilbert must be an instance of ParticleSet")

        cell = hilbert.cell
        if any(cell.pbc):
            raise ValueError(
                "CoulombInteraction currently supports only open boundary" " conditions"
            )
        if ewald:
            raise ValueError("Ewald summation is temporarily disabled")

        self._cell: Cell = cell
        self._ewald = False

        charges = []
        gather_indices = []
        dynamic_mask = []
        fixed_positions = []
        pos_indices = list(hilbert.position_indices)
        dim = cell.dimension

        for p in hilbert.particles:
            if isinstance(p, Particle) or (
                isinstance(p, SpinfulParticle) and p.position is None
            ):
                idxs = jnp.asarray([pos_indices.pop(0) for _ in range(dim)], dtype=int)
                gather_indices.append(idxs)
                dynamic_mask.append(True)
                fixed_positions.append(jnp.zeros(dim))
                q = p.charge if isinstance(p, Particle) else p.charge
            else:
                gather_indices.append(jnp.zeros(dim, dtype=int))
                dynamic_mask.append(False)
                fixed_positions.append(jnp.asarray(p.position))
                q = p.charge
            if q is None:
                raise ValueError("All particles must have a defined charge")
            charges.append(q)

        self._charges = jnp.asarray(charges, dtype=dtype)
        self._gather_indices = jnp.stack(gather_indices)
        self._dynamic_mask = jnp.asarray(dynamic_mask)
        self._fixed_positions = jnp.stack(fixed_positions)
        self._dtype = self._charges.dtype

        pair_list = [
            (i, j) for i in range(len(charges)) for j in range(i + 1, len(charges))
        ]
        if pair_list:
            pair_indices = jnp.asarray(pair_list, dtype=int)
            self._pair_i = pair_indices[:, 0]
            self._pair_j = pair_indices[:, 1]
        else:
            self._pair_i = jnp.asarray([], dtype=int)
            self._pair_j = jnp.asarray([], dtype=int)

        if self._ewald:
            self._ewald_energy = build_ewald_energy(
                self._charges,
                self._cell,
                target_force_rms=target_force_rms,
                safety=safety,
            )
        else:
            self._ewald_energy = None

        self.__attrs: tuple | None = None
        super().__init__(hilbert, self._dtype)

    @property
    def charges(self) -> Array:
        """Charges of the particles."""

        return self._charges

    @property
    def is_hermitian(self) -> bool:
        """Whether the operator is Hermitian."""

        return True

    def _energy_direct(self, positions: Array) -> Array:
        pos_i = positions[self._pair_i]
        pos_j = positions[self._pair_j]
        distances = jax.vmap(self._cell.distance)(pos_i, pos_j)
        q_i = self._charges[self._pair_i]
        q_j = self._charges[self._pair_j]
        return jnp.sum(q_i * q_j / distances)

    def _expect_kernel_single(
        self, logpsi: Callable, params: PyTree, x: Array, _: PyTree | None
    ) -> Array:
        del logpsi, params
        gathered = jnp.take(x, self._gather_indices)
        positions = jnp.where(
            self._dynamic_mask[:, None], gathered, self._fixed_positions
        )
        if self._ewald:
            assert self._ewald_energy is not None
            return self._ewald_energy(positions)
        return self._energy_direct(positions)

    @partial(jax.vmap, in_axes=(None, None, None, 0, None))
    def _expect_kernel(
        self, logpsi: Callable, params: PyTree, x: Array, data: PyTree | None
    ) -> Array:
        return self._expect_kernel_single(logpsi, params, x, data)

    def _pack_arguments(self) -> None:
        return None

    @property
    def _attrs(self) -> tuple:
        if self.__attrs is None:
            self.__attrs = (
                self.hilbert,
                HashableArray(self._charges),
                self._ewald,
            )
        return self.__attrs

    def __repr__(self) -> str:
        return "CoulombInteraction(ewald={})".format(self._ewald)
