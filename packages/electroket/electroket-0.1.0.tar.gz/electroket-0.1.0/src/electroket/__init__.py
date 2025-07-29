"""electroket initialization module."""

from __future__ import annotations

import netket as nk
from .hilbert.continuous_hilbert import ContinuousHilbert
from .hilbert.particle import (
    Particle,
    ParticleSet,
    SpinfulParticle,
    Electron,
    Proton,
)
from .geometry.cell import Cell, FreeSpace
from . import molecule
from .molecule import Molecule, gaussian_orbitals

from .operator import (
    ContinuousOperator,
    KineticEnergy,
    PotentialEnergy,
    PairInteraction,
    CoulombInteraction,
    SumOperator,
)
from . import sampler
from . import models
from .pyscf_utils import scf_orbitals, make_scf_initializer

from . import random as _random  # noqa: F401

__all__ = [
    "nk",
    "show_version",
    "ContinuousHilbert",
    "Particle",
    "ParticleSet",
    "SpinfulParticle",
    "Electron",
    "Proton",
    "Molecule",
    "Cell",
    "FreeSpace",
    "ContinuousOperator",
    "KineticEnergy",
    "PotentialEnergy",
    "PairInteraction",
    "CoulombInteraction",
    "SumOperator",
    "sampler",
    "models",
    "scf_orbitals",
    "make_scf_initializer",
]

__all__ += [name for name in molecule.__all__ if name not in __all__]


def show_version() -> str:
    """Return the installed electroket version."""

    from importlib import metadata

    return metadata.version("electroket")
