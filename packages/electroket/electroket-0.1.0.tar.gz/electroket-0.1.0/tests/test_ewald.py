import pytest
import jax.numpy as jnp

from electroket.operator._ewald import build_ewald_energy
from electroket.geometry.cell import Cell

pytest.skip("Ewald summation is temporarily disabled", allow_module_level=True)

_M_NaCl = -1.74756
_M_CsCl = -1.76267


def test_translation():
    cell = Cell(jnp.array([9.0, 9.0]), pbc=True)
    q = jnp.array([+1.0, -1.0])
    R = jnp.array([[0.1, 0.2], [4.0, 4.0]])
    E_fn = build_ewald_energy(q, cell)
    assert abs(float(E_fn(R)) - float(E_fn(cell.wrap(R + 0.37)))) < 1e-8


def test_nacl_madelung():
    # conventional NaCl cell: 4 Na⁺ + 4 Cl⁻
    a = 5.64
    cell = Cell(jnp.array([a, a, a]), pbc=True)
    charges = jnp.array([+1.0, -1.0, +1.0, -1.0])
    pos_frac = jnp.array([[0, 0, 0], [0, 0.5, 0.5], [0.5, 0, 0.5], [0.5, 0.5, 0]])
    R = cell.frac_to_cart(pos_frac)
    E_fn = build_ewald_energy(charges, cell, target_force_rms=1e-6)
    madelung = float(E_fn(R)) * a / 1.0
    assert abs(madelung - _M_NaCl) < 5e-4


def test_cscl_madelung():
    # primitive CsCl cell:  Cs⁺ at (0,0,0), Cl⁻ at (.5,.5,.5)
    a = 4.12
    cell = Cell(jnp.array([a, a, a]), pbc=True)
    charges = jnp.array([+1.0, -1.0])
    R = jnp.array([[0, 0, 0], [0.5 * a, 0.5 * a, 0.5 * a]])
    E_fn = build_ewald_energy(charges, cell, target_force_rms=1e-6)
    madelung = float(E_fn(R)) * a / 1.0
    assert abs(madelung - _M_CsCl) < 5e-4


def test_large_box_pair():
    # +1 and -1 separated by L/2 in a huge box → energy ≈ -2/L
    L = 60.0
    cell = Cell(jnp.array([L, L, L]), pbc=True)
    charges = jnp.array([+1.0, -1.0])
    R = jnp.array([[0, 0, 0], [L / 2, 0, 0]])
    E_fn = build_ewald_energy(charges, cell, target_force_rms=1e-5)
    E_ref = -2.0 / L
    assert abs(float(E_fn(R)) - E_ref) < 2e-4
