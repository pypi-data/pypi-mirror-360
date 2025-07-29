from __future__ import annotations

from netket.utils.dispatch import dispatch

import math
import jax
import jax.numpy as jnp
import numpy as np
import netket as nk
import netket.jax as nkjax

from ..hilbert.continuous_hilbert import ContinuousHilbert
from ..hilbert.particle import ParticleSet, Particle


def take_sub(key, x, n):
    key, subkey = jax.random.split(key)
    ind = jax.random.choice(
        subkey, jnp.arange(0, x.shape[0], 1), replace=False, shape=(n,)
    )
    return x[ind, :]


@dispatch
def random_state(hilb: Particle, key, batches: int, *, dtype):
    """Return random particle states.

    If periodic boundary conditions are present, particles are
    uniformly distributed with a small Gaussian noise added.
    Otherwise positions are sampled from a normal distribution.
    """

    sdim = hilb.spatial_dimension
    n_particles = 1

    pbc_vec = jnp.tile(hilb.geometry._pbc, n_particles)
    boundary = jnp.tile(pbc_vec, (batches, 1))

    Ls = jnp.tile(jnp.asarray(hilb.domain), n_particles)

    modulus = jnp.where(pbc_vec, Ls, 1.0)
    min_modulus = jnp.min(modulus)

    gaussian = jax.random.normal(
        key, shape=(batches, hilb.size), dtype=nkjax.dtype_real(dtype)
    )

    width = min_modulus / (4.0 * n_particles)
    noise = gaussian * width

    key = jax.random.split(key, num=batches)
    n = int(math.ceil(n_particles ** (1 / sdim)))
    xs = jnp.linspace(0, min(hilb.domain), n)
    uniform = jnp.array(jnp.meshgrid(*(sdim * [xs]))).reshape(-1, sdim)
    uniform = jnp.tile(uniform, (batches, 1, 1))

    uniform = jax.vmap(take_sub, in_axes=(0, 0, None))(
        key, uniform, n_particles
    ).reshape(batches, -1)
    rs = jnp.where(boundary, (uniform + noise) % modulus, gaussian)

    return jnp.asarray(rs, dtype=dtype)


@dispatch
def random_state(hilb: ParticleSet, key, batches: int, *, dtype):  # noqa: F811
    return random_state(hilb._impl, key, batches, dtype=dtype)


@dispatch
def flip_state_scalar(hilb: ContinuousHilbert, key, x, i):
    raise TypeError(
        "Flipping state is undefined for continuous Hilbert spaces. "
        "(Maybe you tried using `MetropolisLocal` on a continuous Hilbert space? "
        "This won't work because 'flipping' a continuous variable is not defined. "
        "You should try a different sampler.)"
    )
