from __future__ import annotations

import math
from typing import Callable

import jax.numpy as jnp
from jax import jit
from jax.scipy.special import erfc

from ..geometry.cell import Cell


def _rms_force_real(alpha: float, r_c: float, q2: float) -> float:
    """Kolafa-Perram RMS-force error bound for the real-space sum."""

    return (
        2.0 * q2 * jnp.sqrt(alpha / math.pi) * jnp.exp(-((alpha * r_c) ** 2)) / (r_c**2)
    )


def _rms_force_recip(
    alpha: float, g_max: float, L_min: float, V: float, q2: float
) -> float:
    """Kolafa-Perram RMS-force error bound for the reciprocal-space sum."""

    pref = 2.0 * math.pi * q2 / (V * jnp.sqrt(math.pi * alpha))
    return pref * jnp.exp(-(g_max**2) / (4.0 * alpha**2)) / (L_min**2)


def build_ewald_energy(
    charges: jnp.ndarray,
    cell: Cell,
    *,
    target_force_rms: float = 1e-4,
    safety: float = 2.0,
) -> Callable[[jnp.ndarray], jnp.ndarray]:
    """Return a JAX energy function implementing the Ewald summation.

    Parameters
    ----------
    charges
        Array of particle charges with shape ``(N,)``.
    cell
        Simulation cell describing the geometry.
    target_force_rms
        Desired RMS force error used to auto-tune the Ewald parameters.
    safety
        Safety factor applied to the reciprocal cutoff.

    Returns
    -------
    Callable
        Function taking an array ``R`` of positions with shape ``(N, d)`` and
        returning the electrostatic energy.
    """

    charges = jnp.asarray(charges, dtype=jnp.float64)
    if jnp.abs(jnp.sum(charges)) > 1e-6:
        raise ValueError("Ewald summation requires a charge-neutral system.")

    q2 = jnp.sum(charges**2)
    periodic_axes = jnp.asarray(cell.pbc, dtype=bool)
    fully_periodic = bool(jnp.all(periodic_axes))
    L_periodic = cell.lengths[periodic_axes] if fully_periodic else jnp.inf
    L_min = jnp.min(L_periodic) if fully_periodic else jnp.inf
    V = cell.volume if fully_periodic else jnp.inf
    d = cell.dim

    r_c_grid = (
        jnp.linspace(0.25 * L_min, 0.5 * L_min, 16)
        if fully_periodic
        else jnp.array([jnp.max(cell.lengths)])
    )
    alpha_grid = (
        jnp.linspace(0.1 / L_min, 7.0 / r_c_grid.min(), 64)
        if fully_periodic
        else jnp.linspace(0.05 / cell.lengths.max(), 3.0 / cell.lengths.max(), 32)
    )

    @jit
    def _tune(
        alpha_vec: jnp.ndarray, rc_vec: jnp.ndarray
    ) -> tuple[float, float, float]:
        """Evaluate RMS-force error on a grid and return optimal parameters."""

        alpha, rc = jnp.meshgrid(alpha_vec, rc_vec, indexing="ij")
        err_real = _rms_force_real(alpha, rc, q2)

        if fully_periodic:
            g_star = (
                2.0
                * alpha
                * L_min
                * jnp.sqrt(jnp.maximum(-jnp.log(target_force_rms), 1.0))
                / math.pi
            )
            err_recip = _rms_force_recip(alpha, g_star, L_min, V, q2)
            err = jnp.sqrt(err_real**2 + err_recip**2)
        else:
            err = err_real

        idx = jnp.argmin(err)
        alpha_opt = alpha.ravel()[idx]
        rc_opt = rc.ravel()[idx]
        best_err = err.ravel()[idx]
        return alpha_opt, rc_opt, best_err

    alpha_opt, r_c_opt, best_err = _tune(alpha_grid, r_c_grid)
    alpha_opt, r_c_opt = float(alpha_opt), float(r_c_opt)
    g_max_opt = 0.0
    if fully_periodic:
        g_star = (
            2.0
            * alpha_opt
            * L_min
            * jnp.sqrt(jnp.maximum(-jnp.log(target_force_rms), 1.0))
            / math.pi
        )
        g_max_opt = float(g_star * safety)

    g_vecs = cell.reciprocal_vectors(g_max_opt) if fully_periodic else jnp.zeros((0, d))

    @jit
    def _energy_real(R: jnp.ndarray, q: jnp.ndarray) -> jnp.ndarray:
        disp = cell.pairwise_displacements(R)
        dist = jnp.linalg.norm(disp, axis=-1)
        mask = (dist > 0) & (dist < r_c_opt)
        phi = jnp.where(mask, erfc(alpha_opt * dist) / dist, 0.0)
        return 0.5 * jnp.sum(q[:, None] * q[None, :] * phi)

    @jit
    def _energy_recip(R: jnp.ndarray, q: jnp.ndarray) -> jnp.ndarray:
        M = g_vecs.shape[0]
        if M == 0:
            return jnp.array(0.0, dtype=R.dtype)
        g2 = jnp.sum(g_vecs**2, axis=1)
        phase = R @ g_vecs.T
        S = jnp.sum(q[:, None] * jnp.exp(1j * phase), axis=0)
        coeff = (2.0 * math.pi / V) * jnp.exp(-g2 / (4.0 * alpha_opt**2)) / g2
        return 0.5 * jnp.sum(coeff * jnp.abs(S) ** 2).real

    @jit
    def _energy_self(q: jnp.ndarray) -> jnp.ndarray:
        return -alpha_opt / math.sqrt(math.pi) * jnp.sum(q**2)

    @jit
    def energy_fn(R: jnp.ndarray, *, charges: jnp.ndarray = charges) -> jnp.ndarray:
        energy = _energy_real(R, charges) + _energy_self(charges)
        if fully_periodic:
            energy = energy + _energy_recip(R, charges)
        return energy

    return energy_fn
