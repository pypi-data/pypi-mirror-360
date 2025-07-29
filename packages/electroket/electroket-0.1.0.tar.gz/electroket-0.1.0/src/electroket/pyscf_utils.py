from __future__ import annotations

from typing import Tuple

import numpy as np
import jax.numpy as jnp
from netket.utils.types import NNInitFunc

from .molecule import Molecule


def scf_orbitals(mol: Molecule, *, basis: str = "sto3g") -> Tuple[float, np.ndarray]:
    """Run a PySCF RHF calculation and return optimized orbitals.

    Parameters
    ----------
    mol
        Molecule for which to run the SCF.
    basis
        Basis set name to use with PySCF.

    Returns
    -------
    tuple
        Total SCF energy and the matrix of molecular orbital coefficients with
        shape ``(n_basis, n_basis)``.
    """
    import pyscf
    from pyscf import gto, scf

    atom = "; ".join(f"{sym} {x} {y} {z}" for sym, (x, y, z) in mol.atoms)
    spin = int(sum(e.m_z for e in mol.electrons) * 2)
    mol_p = gto.M(
        atom=atom,
        basis=basis.lower(),
        unit="Bohr",
        cart=True,
        spin=spin,
    )
    mf = scf.RHF(mol_p)
    energy = mf.kernel()
    return float(energy), np.asarray(mf.mo_coeff)


def make_scf_initializer(mo_coeff: np.ndarray) -> NNInitFunc:
    """Return a coefficient initializer using SCF orbitals.

    Parameters
    ----------
    mo_coeff
        Molecular orbital coefficients with shape ``(n_basis, n_orbital)``.

    Returns
    -------
    callable
        Initializer to pass as ``coeff_init`` to :class:`~electroket.models.Slater`.
    """

    def init(rng, shape, dtype=jnp.float64):
        n_orb, n_basis = shape
        assert n_basis == mo_coeff.shape[0]
        return jnp.asarray(mo_coeff[:, :n_orb].T, dtype=dtype)

    return init


__all__ = ["scf_orbitals", "make_scf_initializer"]
