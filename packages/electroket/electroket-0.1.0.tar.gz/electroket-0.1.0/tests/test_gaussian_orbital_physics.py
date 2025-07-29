import numpy as np
import jax.numpy as jnp
import pytest

import electroket

pyscf = pytest.importorskip("pyscf")
from pyscf import gto
from electroket.molecule.orbitals import BOHR_ANG


def _build_pyscf_h():
    mol = gto.M(
        atom="H 0 0 0",
        basis="sto3g",
        unit="Angstrom",
        cart=True,
        spin=1,
    )
    return mol


def _ao_index(mol, substr: str) -> int:
    substr = substr.lower().replace("_", "")
    for i, lbl in enumerate(mol.ao_labels()):
        if substr in lbl.lower().replace(" ", ""):
            return i
    raise ValueError(substr)


def _pyscf_ao(mol, idx, coords):
    vals = mol.eval_gto("GTOval_cart", coords)
    return vals[:, idx]


def test_h1s_normalized():
    mol = electroket.Molecule(
        [("H", [0.0, 0.0, 0.0]), ("H", [1000.0, 0.0, 0.0])], units="angstrom"
    )
    orb = electroket.gaussian_orbitals(mol)[0]

    r_bohr = np.linspace(0.0, 15.0, 2001)
    r_ang = r_bohr * BOHR_ANG
    coords = np.column_stack([r_ang, np.zeros_like(r_ang), np.zeros_like(r_ang)])
    vals = np.asarray(orb(coords))
    prob = 4 * np.pi * r_bohr**2 * np.abs(vals) ** 2
    integral = np.trapz(prob, r_bohr)
    assert integral == pytest.approx(1.0, abs=1e-6)


def test_h1s_matches_pyscf():
    mol_ck = electroket.Molecule(
        [("H", [0.0, 0.0, 0.0]), ("H", [1000.0, 0.0, 0.0])], units="angstrom"
    )
    orb = electroket.gaussian_orbitals(mol_ck)[0]

    r_ang = np.linspace(0.0, 3.0, 50)
    coords_ang = np.column_stack([r_ang, np.zeros_like(r_ang), np.zeros_like(r_ang)])
    vals_ck = np.asarray(orb(coords_ang))

    mol_py = _build_pyscf_h()
    idx = _ao_index(mol_py, "1s")
    coords_bohr = coords_ang / BOHR_ANG
    vals_py = _pyscf_ao(mol_py, idx, coords_bohr)

    np.testing.assert_allclose(vals_ck, vals_py, rtol=1e-6, atol=1e-8)


def test_vectorized_matches_loop():
    mol = electroket.Molecule(
        [("H", [0.0, 0.0, 0.0]), ("H", [1000.0, 0.0, 0.0])], units="angstrom"
    )
    orb = electroket.gaussian_orbitals(mol)[0]

    coords_ang = np.random.default_rng(0).uniform(-1.0, 1.0, size=(10, 3))
    vec = orb(coords_ang)
    loop = jnp.array([orb(c) for c in coords_ang])

    np.testing.assert_allclose(np.asarray(vec), np.asarray(loop))
