import jax.numpy as jnp
import numpy as np

import electroket


def test_particle_basic():
    geo = electroket.Cell(extent=(jnp.inf, 10.0), pbc=(False, True))
    part = electroket.Particle(geometry=geo)
    assert part.size == 2
    assert part.domain == geo.extent
    assert part.geometry == geo


def test_particle_pow():
    geo = electroket.Cell(extent=(jnp.inf, 10.0), pbc=(False, True))
    part = electroket.Particle(geometry=geo)
    multi = part**3
    assert multi.size == part.size * 3
    assert len(multi.subspaces) == 3
