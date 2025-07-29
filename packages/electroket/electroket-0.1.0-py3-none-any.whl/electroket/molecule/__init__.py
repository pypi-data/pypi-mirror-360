from __future__ import annotations

from functools import partial
from typing import Iterable, Sequence, Tuple

from ..geometry.cell import FreeSpace
from dataclasses import dataclass

from ..hilbert.particle import Electron, ParticleSet, SpinfulParticle


@dataclass(frozen=True, slots=True)
class FixedParticle(SpinfulParticle):
    """Spinless particle fixed at a given position."""

    def _spin_block(self):
        return None


ANGSTROM_TO_BOHR = 1.8897259886


# Atomic number and atomic mass (in unified atomic mass units) for the first
# 20 elements. The values are approximate averages of the naturally occurring
# isotopic compositions.
_ELEMENT_DATA: dict[str, Tuple[int, float]] = {
    "H": (1, 1.0080),
    "He": (2, 4.00260),
    "Li": (3, 7.0),
    "Be": (4, 9.012183),
    "B": (5, 10.81),
    "C": (6, 12.011),
    "N": (7, 14.007),
    "O": (8, 15.999),
    "F": (9, 18.99840316),
    "Ne": (10, 20.180),
    "Na": (11, 22.9897693),
    "Mg": (12, 24.305),
    "Al": (13, 26.981538),
    "Si": (14, 28.085),
    "P": (15, 30.97376200),
    "S": (16, 32.07),
    "Cl": (17, 35.45),
    "Ar": (18, 39.9),
    "K": (19, 39.0983),
    "Ca": (20, 40.08),
}


# Conversion factor from atomic mass units to electron masses.
_AMU_TO_ME = 1822.888486209


def _make_nucleus(symbol: str) -> partial:
    Z, mass_u = _ELEMENT_DATA[symbol]
    mass = mass_u * _AMU_TO_ME
    return partial(
        FixedParticle,
        mass=mass,
        charge=float(Z),
        S=0.0,
        label=symbol,
    )


# Create nucleus factories
NUCLEI = {sym: _make_nucleus(sym) for sym in _ELEMENT_DATA}

from .orbitals import gaussian_orbitals

# Export individual nuclei
globals().update(NUCLEI)
__all__ = ["Molecule", "gaussian_orbitals"] + list(NUCLEI.keys())


class Molecule(ParticleSet):
    """Simple molecular system composed of nuclei and electrons."""

    def __init__(
        self,
        atoms: Sequence[Tuple[str, Iterable[float]]],
        *,
        units: str = "bohr",
    ) -> None:
        """Construct a molecule.

        Parameters
        ----------
        atoms
            Iterable of ``(symbol, position)`` pairs. ``symbol`` must be one of
            the first 20 elements. ``position`` is an iterable of length three
            giving the coordinates of the nucleus.
        units
            Either ``"bohr"`` or ``"angstrom"``.
        """
        if units not in {"bohr", "angstrom"}:
            raise ValueError("units must be 'bohr' or 'angstrom'")

        scale = 1.0 if units == "bohr" else ANGSTROM_TO_BOHR

        nuclei = []
        n_electrons = 0
        for sym, pos in atoms:
            if sym not in NUCLEI:
                raise ValueError(f"Unknown element symbol: {sym}")
            coords = tuple(float(x) * scale for x in pos)
            nucleus = NUCLEI[sym](position=coords)
            nuclei.append(nucleus)
            Z, _ = _ELEMENT_DATA[sym]
            n_electrons += Z

        if n_electrons % 2 != 0:
            raise ValueError("Number of electrons must be even.")

        electrons = []
        half = n_electrons // 2
        for i in range(n_electrons):
            m_z = 0.5 if i < half else -0.5
            electrons.append(Electron(m_z=m_z))

        particles = nuclei + electrons
        cell = FreeSpace(3)
        super().__init__(particles, cell)

        self.nuclei = tuple(nuclei)
        self.electrons = tuple(electrons)
        self.atoms = tuple((s, tuple(float(x) * scale for x in p)) for s, p in atoms)
        self.units = "bohr"
