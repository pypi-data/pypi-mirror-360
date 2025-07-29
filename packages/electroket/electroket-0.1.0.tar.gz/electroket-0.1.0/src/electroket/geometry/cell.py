from __future__ import annotations

import itertools
import math
from typing import Iterable, Tuple

import jax.numpy as jnp


class Cell:
    """Geometry-only simulation cell supporting PBC and OBC in any dimension.

    Parameters
    ----------
    extent:
        Array specifying the unit cell. If ``extent.ndim == 1`` it is treated
        as a diagonal box with edge lengths given by ``extent``. If
        ``extent.ndim == 2`` it must be a square matrix whose rows are the
        lattice vectors.
    pbc:
        Boundary condition flags. Either a single ``bool`` applied to all axes
        or a boolean array of length equal to the spatial dimension.
    """

    __slots__ = (
        "dim",
        "box",
        "invbox",
        "lengths",
        "volume",
        "metric",
        "_pbc",
        "_has_pbc",
    )

    def __init__(self, extent: Iterable[float] | jnp.ndarray, pbc=True) -> None:
        box = jnp.asarray(extent, dtype=jnp.float32)
        if box.ndim == 1:
            d = int(box.shape[0])
            box = jnp.diag(box)
        elif box.ndim == 2 and box.shape[0] == box.shape[1]:
            d = int(box.shape[0])
        else:
            raise ValueError("extent must have shape (d,) or square (d,d)")

        pbc_arr = jnp.asarray(pbc)
        if pbc_arr.ndim == 0:
            pbc_arr = jnp.full(d, bool(pbc), dtype=bool)
        elif pbc_arr.shape != (d,):
            raise ValueError("pbc must be bool or array with shape (d,)")
        pbc_arr = pbc_arr.astype(bool)

        invbox = jnp.linalg.inv(box)
        lengths = jnp.linalg.norm(box, axis=1)
        vol = jnp.abs(jnp.linalg.det(box))
        if not bool(jnp.all(pbc_arr)):
            vol = jnp.inf
        metric = box @ box.T

        object.__setattr__(self, "dim", d)
        object.__setattr__(self, "box", box)
        object.__setattr__(self, "invbox", invbox)
        object.__setattr__(self, "lengths", lengths)
        object.__setattr__(self, "volume", vol)
        object.__setattr__(self, "metric", metric)
        object.__setattr__(self, "_pbc", pbc_arr)
        object.__setattr__(self, "_has_pbc", bool(jnp.any(pbc_arr)))

    # ------------------------------------------------------------------
    # Compatibility helpers
    @property
    def extent(self) -> Tuple[float, ...]:
        """Edge lengths of the simulation box."""

        return tuple(float(x) for x in self.lengths)

    @property
    def dimension(self) -> int:
        """Number of spatial dimensions."""

        return self.dim

    @property
    def pbc(self) -> jnp.ndarray:
        """Periodic boundary conditions."""

        return self._pbc

    @property
    def has_pbc(self) -> bool:
        """Return ``True`` if any axis has periodic boundaries."""

        return self._has_pbc

    # ------------------------------------------------------------------
    def cart_to_frac(self, r_cart: jnp.ndarray) -> jnp.ndarray:
        """Convert Cartesian coordinates to fractional coordinates."""

        return jnp.matmul(r_cart, self.invbox)

    def frac_to_cart(self, s_frac: jnp.ndarray) -> jnp.ndarray:
        """Convert fractional coordinates to Cartesian coordinates."""

        return jnp.matmul(s_frac, self.box)

    def wrap(self, r_cart: jnp.ndarray) -> jnp.ndarray:
        """Map Cartesian coordinates into the primary cell."""

        s = self.cart_to_frac(r_cart)
        s = jnp.where(self._pbc, jnp.mod(s, 1.0), s)
        return self.frac_to_cart(s)

    def displacement(self, r_i: jnp.ndarray, r_j: jnp.ndarray) -> jnp.ndarray:
        """Return the minimum-image displacement vector ``r_i - r_j``."""

        ds = self.cart_to_frac(r_j) - self.cart_to_frac(r_i)
        ds = jnp.where(self._pbc, ds - jnp.round(ds), ds)
        return self.frac_to_cart(ds)

    def pairwise_displacements(self, r: jnp.ndarray) -> jnp.ndarray:
        """Return pairwise minimum-image displacements for a set of points."""

        s = self.cart_to_frac(r)
        ds = s[None, :, :] - s[:, None, :]
        ds = jnp.where(self._pbc, ds - jnp.round(ds), ds)
        return self.frac_to_cart(ds)

    def distance(self, r_i: jnp.ndarray, r_j: jnp.ndarray) -> jnp.ndarray:
        """Minimum-image distance between two points."""

        dr = self.displacement(r_i, r_j)
        return jnp.linalg.norm(dr, axis=-1)

    def reciprocal_vectors(self, g_max: float) -> jnp.ndarray:
        """Generate reciprocal lattice vectors with magnitude up to ``g_max``."""
        if not bool(jnp.all(self._pbc)):
            return jnp.zeros((0, self.dim), dtype=jnp.float32)

        g_basis = 2.0 * math.pi * self.invbox
        lengths = jnp.linalg.norm(g_basis, axis=1)
        max_n = int(math.ceil(g_max / float(jnp.min(lengths)))) + 1

        vecs = []
        for n in itertools.product(range(-max_n, max_n + 1), repeat=self.dim):
            if all(k == 0 for k in n):
                continue
            g = jnp.matmul(jnp.array(n, dtype=jnp.float32), g_basis)
            if jnp.linalg.norm(g) <= g_max + 1e-12:
                vecs.append(g)
        if not vecs:
            return jnp.zeros((0, self.dim), dtype=jnp.float32)
        return jnp.stack(vecs)


class FreeSpace(Cell):
    """Cell representing free space (no periodic boundaries)."""

    __slots__ = ()

    def __init__(self, dimension: int) -> None:
        object.__setattr__(self, "dim", int(dimension))
        box = jnp.eye(dimension, dtype=jnp.float32)
        object.__setattr__(self, "box", box)
        object.__setattr__(self, "invbox", box)
        lengths = jnp.full(dimension, jnp.inf, dtype=jnp.float32)
        object.__setattr__(self, "lengths", lengths)
        object.__setattr__(self, "volume", jnp.inf)
        object.__setattr__(self, "metric", box)
        object.__setattr__(self, "_pbc", jnp.zeros(dimension, dtype=bool))

    # ------------------------------------------------------------------
    # In free space, fractional coordinates coincide with Cartesian ones
    @property
    def pbc(self) -> Tuple[bool, ...]:  # type: ignore[override]
        return (False,) * self.dim

    def cart_to_frac(self, r_cart: jnp.ndarray) -> jnp.ndarray:  # type: ignore[override]
        return jnp.asarray(r_cart)

    def frac_to_cart(self, s_frac: jnp.ndarray) -> jnp.ndarray:  # type: ignore[override]
        return jnp.asarray(s_frac)

    def wrap(self, r_cart: jnp.ndarray) -> jnp.ndarray:  # type: ignore[override]
        return jnp.asarray(r_cart)

    def displacement(self, r_i: jnp.ndarray, r_j: jnp.ndarray) -> jnp.ndarray:  # type: ignore[override]
        return jnp.asarray(r_j) - jnp.asarray(r_i)

    def pairwise_displacements(self, r: jnp.ndarray) -> jnp.ndarray:  # type: ignore[override]
        r = jnp.asarray(r)
        return r[None, :, :] - r[:, None, :]

    def distance(self, r_i: jnp.ndarray, r_j: jnp.ndarray) -> jnp.ndarray:  # type: ignore[override]
        return jnp.linalg.norm(jnp.asarray(r_i) - jnp.asarray(r_j), axis=-1)

    def reciprocal_vectors(self, g_max: float) -> jnp.ndarray:  # type: ignore[override]
        return jnp.zeros((0, self.dim), dtype=jnp.float32)

    @property
    def has_pbc(self) -> bool:  # type: ignore[override]
        """Return ``False`` as free space has no PBCs."""

        return False
