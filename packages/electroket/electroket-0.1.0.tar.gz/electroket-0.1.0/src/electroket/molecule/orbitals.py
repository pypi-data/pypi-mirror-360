from __future__ import annotations

from collections.abc import Callable

import jax.numpy as jnp
from netket.utils.types import Array

from typing import TYPE_CHECKING

BOHR_ANG = 0.529177210903


def _factorial2(n: int) -> jnp.ndarray:
    """Return ``n!!`` computed with JAX arrays."""

    if n <= 0:
        return jnp.array(1.0)
    return jnp.prod(jnp.arange(n, 0, -2))


if TYPE_CHECKING:  # pragma: no cover
    from . import Molecule

from .basis_sto3g import STO3G


def _make_orbital(
    center: Array, exps: Array, coefs: Array, axis: int | None
) -> Callable[[Array], Array]:
    """Create a single Gaussian orbital.

    Args:
        center: Position of the orbital center.
        exps: Primitive exponents :math:`\alpha_i`.
        coefs: Contraction coefficients :math:`c_i`.
        axis: Angular component or ``None`` for ``s`` orbitals.

    Returns:
        Callable evaluating the orbital at a position ``r``.
    """

    alpha = jnp.asarray(exps)
    c_raw = jnp.asarray(coefs)

    l = 0 if axis is None else 1
    num = (4.0 * alpha) ** l
    den = _factorial2(2 * l - 1) * _factorial2(2 * l)
    norm = (2.0 * alpha / jnp.pi) ** 0.75 * jnp.sqrt(num / den)
    c = c_raw * norm

    def orbital(r: Array) -> Array:
        diff = r - center
        diff_bohr = diff / BOHR_ANG
        r2 = jnp.sum(diff_bohr**2, axis=-1)
        val = jnp.sum(c * jnp.exp(-alpha * r2[..., None]), axis=-1)
        if axis is None:
            return val
        return diff_bohr[..., axis] * val

    orbital.units = "angstrom"
    return orbital


def gaussian_orbitals(
    mol: Molecule, *, basis: str = "STO-3G"
) -> tuple[Callable[[Array], Array], ...]:
    """Return Gaussian orbital functions for a molecule.

    Args:
        mol: Molecule for which to build the orbitals.
        basis: Basis set name. Only ``"STO-3G"`` is supported.

    Returns:
        Tuple of callables evaluating the orbitals.
    """
    if basis != "STO-3G":
        raise NotImplementedError("Only STO-3G basis is implemented.")

    orbitals: list[Callable[[Array], Array]] = []
    for sym, pos in mol.atoms:
        if sym not in STO3G:
            raise ValueError(f"No STO-3G data for element {sym}")
        center = jnp.asarray(pos) * BOHR_ANG
        for shell in STO3G[sym]:
            if shell["angular"] == "s":
                orbitals.append(
                    _make_orbital(
                        center, shell["exponents"], shell["coefficients"], None
                    )
                )
            elif shell["angular"] == "p":
                for ax in range(3):
                    orbitals.append(
                        _make_orbital(
                            center, shell["exponents"], shell["coefficients"], ax
                        )
                    )
            else:
                raise NotImplementedError(
                    f"Angular momentum '{shell['angular']}' not supported."
                )
    return tuple(orbitals)


__all__ = ["gaussian_orbitals"]
