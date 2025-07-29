from __future__ import annotations

from functools import partial, reduce
from dataclasses import dataclass
from typing import Optional, Sequence

import netket as nk
import numpy as np
from netket.hilbert import TensorHilbert, Spin
from netket.hilbert.constraint import DiscreteHilbertConstraint

from ..geometry.cell import Cell
from .continuous_hilbert import ContinuousHilbert


class Particle(ContinuousHilbert):
    """Hilbert space of a single particle in continuous space.

    Parameters
    ----------
    geometry
        Simulation cell describing the domain.
    mass, charge, S, label
        Optional physical properties attached to the particle. They are not
        used by the Hilbert space implementation but are carried around for
        convenience.
    """

    def __init__(
        self,
        *,
        geometry: Cell,
        mass: Optional[float] = None,
        charge: Optional[float] = None,
        S: Optional[float] = None,
        label: Optional[str] = None,
    ) -> None:
        """Construct a single particle confined to ``geometry``.

        Args:
            geometry: Instance of :class:`~electroket.geometry.cell.Cell` defining
                the simulation box.
        """

        if not isinstance(geometry, Cell):
            raise TypeError("`geometry` must be an instance of `geometry.Cell`.")

        self._geometry = geometry
        self.mass = mass
        self.charge = charge
        self.S = S
        self.label = label

        super().__init__(geometry.extent)

    @property
    def size(self) -> int:
        return len(self.domain)

    @property
    def geometry(self) -> Cell:
        """Geometry of the continuous space."""
        return self._geometry

    # ------------------------------------------------------------------
    # convenience utilities used by samplers

    @property
    def position_indices(self) -> tuple[int, ...]:
        """Indices corresponding to the particle coordinates."""

        return tuple(range(self.size))

    @property
    def positions_hilbert(self) -> "Particle":
        """Hilbert space describing only the particle coordinates."""

        return self

    @property
    def _attrs(self):
        return (self.geometry, self.mass, self.charge, self.S, self.label)

    def __repr__(self) -> str:
        return f"Particle(d={len(self.domain)})"

    def __pow__(self, n: int) -> Particle | TensorHilbert:
        """Return the tensor product of ``n`` identical particles."""
        return reduce(lambda a, b: a * b, [self] * n)


_ContParticle = Particle


@dataclass(frozen=True, slots=True)
class SpinfulParticle:
    """Particle with an additional spin degree of freedom."""

    mass: float
    charge: float
    S: float
    label: str
    position: Sequence[float] | None = None
    m_z: float | None = None

    def _spin_block(self) -> nk.hilbert.AbstractHilbert:
        if self.S <= 0:
            raise ValueError("SpinfulParticle requires S > 0.")
        if self.m_z is None:
            return Spin(s=self.S)
        if self.m_z not in np.arange(-self.S, self.S + 1, 1.0):
            raise ValueError(f"Invalid m_z={self.m_z} for S={self.S}")
        from netket.utils import StaticRange

        return nk.hilbert.HomogeneousHilbert(
            local_states=StaticRange(self.m_z, step=1, length=1),
            N=1,
        )

    def _pos_block(self, cell: Cell) -> nk.hilbert.AbstractHilbert:
        if self.position is None:
            return _ContParticle(geometry=cell)
        if len(self.position) != cell.dimension:
            raise ValueError("position has wrong dimensionality for this Cell.")
        from netket.utils import StaticRange

        blocks = [
            nk.hilbert.HomogeneousHilbert(StaticRange(p, step=1, length=1))
            for p in self.position
        ]
        res = blocks[0]
        for b in blocks[1:]:
            res = res * b
        return res


Electron = partial(SpinfulParticle, mass=1.0, charge=-1.0, S=0.5, label="e⁻")
Proton = partial(
    SpinfulParticle,
    mass=1836.15267389,
    charge=+1.0,
    S=0.5,
    label="p⁺",
)


class ParticleSet(ContinuousHilbert):
    """Hilbert space of several particles inside a :class:`Cell`."""

    def __init__(
        self,
        particles: Sequence[SpinfulParticle],
        cell: Cell,
        *,
        total_sz: float | None = None,
        constraint: DiscreteHilbertConstraint | None = None,
    ) -> None:
        self.particles = tuple(particles)
        self.cell = cell

        super().__init__(cell.extent)

        blocks = []
        dyn_spin_sites = []
        pos_blocks = []
        pos_indices: list[int] = []
        current = 0
        for p in self.particles:
            if isinstance(p, _ContParticle):
                pb = p
                spin_block = None
            else:
                pb = p._pos_block(cell)
                spin_block = p._spin_block() if isinstance(p, SpinfulParticle) else None

            blocks.append(pb)
            if isinstance(pb, ContinuousHilbert):
                pos_blocks.append(pb)
                pos_indices.extend(range(current, current + pb.size))
            current += pb.size
            if spin_block is not None:
                blocks.append(spin_block)
                if p.m_z is None:
                    dyn_spin_sites.append(len(blocks) - 1)
                current += spin_block.size

        hilb = blocks[0]
        for blk in blocks[1:]:
            hilb = hilb * blk

        pos_hilb = None
        if pos_blocks:
            pos_hilb = pos_blocks[0]
            for pb in pos_blocks[1:]:
                pos_hilb = pos_hilb * pb

        if total_sz is not None:
            dyn_N = len(dyn_spin_sites)
            if dyn_N == 0 and total_sz != 0:
                raise ValueError("All spins are fixed; total_sz must be 0.")
            fixed_sz = sum(
                p.m_z
                for p in self.particles
                if isinstance(p, SpinfulParticle) and p.m_z is not None
            )
            needed = total_sz - fixed_sz
            if not np.isclose(needed, int(2 * needed) / 2):
                raise ValueError("total_sz must be integer/half-integer.")
            aux = Spin(s=0.5, N=dyn_N, total_sz=needed)
            constraint = (
                aux._constraint if constraint is None else constraint & aux._constraint
            )

        if constraint is not None:
            hilb = nk.hilbert.HomogeneousHilbert(
                local_states=hilb.local_states,
                N=hilb.size,
                constraint=constraint,
            )

        self._impl = hilb
        self._positions_impl = pos_hilb
        self._pos_indices = tuple(pos_indices)

    @property
    def geometry(self) -> Cell:
        return self.cell

    @property
    def domain(self) -> tuple[float, ...]:
        return self.cell.extent

    @property
    def n_particles(self) -> int:
        return len(self.particles)

    @property
    def size(self) -> int:
        return self._impl.size

    def states_spins(self, *args, **kwargs):
        return self._impl.states_spins(*args, **kwargs)

    @property
    def position_indices(self) -> tuple[int, ...]:
        """Indices of the continuous coordinates within the Hilbert state."""

        return self._pos_indices

    @property
    def positions_hilbert(self) -> ContinuousHilbert | None:
        """Hilbert space containing only the mobile particles' coordinates."""

        return self._positions_impl

    @property
    def _attrs(self):
        return (self.particles, self.cell, self.size, self._pos_indices)
