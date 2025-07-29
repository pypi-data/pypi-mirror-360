from __future__ import annotations

from collections.abc import Callable
from functools import partial

import jax
import jax.numpy as jnp
from netket.utils import HashableArray
from netket.utils.types import Array, DType, PyTree

from ..hilbert.particle import Particle, ParticleSet, SpinfulParticle
from ..geometry.cell import Cell
from ._continuous_operator import ContinuousOperator


class PairInteraction(ContinuousOperator):
    """Two-body interaction potential for a :class:`ParticleSet`.

    Parameters
    ----------
    hilbert
        Hilbert space of the particles.
    vfun
        Potential energy function ``V(r)`` depending only on the distance ``r``
        between two particles.
    coefficient
        Scalar coefficient multiplying the interaction potential.
    dtype
        Optional dtype of ``coefficient``.
    """

    def __init__(
        self,
        hilbert: ParticleSet,
        vfun: Callable[[Array], Array],
        coefficient: float = 1.0,
        dtype: DType | None = None,
    ) -> None:
        if not isinstance(hilbert, ParticleSet):
            raise TypeError("hilbert must be an instance of ParticleSet")

        self._vfun = vfun
        self._coefficient = jnp.asarray(coefficient, dtype=dtype)

        self._cell: Cell = hilbert.cell
        dim = self._cell.dimension

        pos_indices = list(hilbert.position_indices)

        gather_indices = []
        dynamic_mask = []
        fixed_positions = []

        for p in hilbert.particles:
            if isinstance(p, Particle) or (
                isinstance(p, SpinfulParticle) and p.position is None
            ):
                idxs = jnp.asarray([pos_indices.pop(0) for _ in range(dim)], dtype=int)
                gather_indices.append(idxs)
                dynamic_mask.append(True)
                fixed_positions.append(jnp.zeros(dim))
            elif isinstance(p, SpinfulParticle) and p.position is not None:
                gather_indices.append(jnp.zeros(dim, dtype=int))
                dynamic_mask.append(False)
                fixed_positions.append(jnp.asarray(p.position))
            else:  # pragma: no cover - safeguard
                raise TypeError("Unsupported particle type")

        self._gather_indices = jnp.stack(gather_indices)
        self._dynamic_mask = jnp.asarray(dynamic_mask)
        self._fixed_positions = jnp.stack(fixed_positions)

        pair_list = [
            (i, j)
            for i in range(len(hilbert.particles))
            for j in range(i + 1, len(hilbert.particles))
        ]

        if pair_list:
            pair_indices = jnp.asarray(pair_list, dtype=int)
            self._pair_i = pair_indices[:, 0]
            self._pair_j = pair_indices[:, 1]
        else:  # pragma: no cover - no pairs
            self._pair_i = jnp.asarray([], dtype=int)
            self._pair_j = jnp.asarray([], dtype=int)

        self.__attrs: tuple | None = None
        super().__init__(hilbert, self._coefficient.dtype)

    @property
    def coefficient(self) -> Array:
        return self._coefficient

    def _expect_kernel_single(
        self, logpsi: Callable, params: PyTree, x: Array, coefficient: Array
    ) -> Array:
        del logpsi, params

        gathered = jnp.take(x, self._gather_indices)
        positions = jnp.where(
            self._dynamic_mask[:, None], gathered, self._fixed_positions
        )

        pos_i = positions[self._pair_i]
        pos_j = positions[self._pair_j]

        distances = jax.vmap(self._cell.distance)(pos_i, pos_j)
        energy = jnp.sum(jax.vmap(self._vfun)(distances))

        return coefficient * energy

    @partial(jax.vmap, in_axes=(None, None, None, 0, None))
    def _expect_kernel(
        self, logpsi: Callable, params: PyTree, x: Array, coefficient: Array
    ) -> Array:
        return self._expect_kernel_single(logpsi, params, x, coefficient)

    def _pack_arguments(self) -> Array:
        return self.coefficient

    @property
    def _attrs(self) -> tuple:
        if self.__attrs is None:
            self.__attrs = (
                self.hilbert,
                self._vfun,
                self.dtype,
                HashableArray(self.coefficient),
            )
        return self.__attrs

    def __repr__(self) -> str:
        return f"PairInteraction(coefficient={self.coefficient}, function={self._vfun})"
