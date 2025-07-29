from __future__ import annotations

from netket.hilbert.abstract_hilbert import AbstractHilbert


class ContinuousHilbert(AbstractHilbert):
    """Abstract class for the Hilbert space of particles in continuous space."""

    def __init__(self, domain: tuple[float, ...]):
        """Construct an Hilbert space with continuous degrees of freedom.

        Args:
            domain: Tuple indicating the maximum of the continuous quantum
                number(s) in the configurations. Each entry corresponds to a
                different physical dimension. A particle in a 3D box of size
                ``L`` would take ``(L, L, L)``. A rotor model would take, for
                example, ``(2 * np.pi,)``.
        """
        self._extent = tuple(domain)
        super().__init__()

    @property
    def domain(self) -> tuple[float, ...]:
        """Domain of the continuous variable for each dimension."""
        return self._extent

    @property
    def spatial_dimension(self) -> int:
        """Number of spatial dimensions."""
        return len(self._extent)
