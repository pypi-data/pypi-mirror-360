import jax
import jax.numpy as jnp
import electroket


def test_displacement_jit():
    cell = electroket.Cell(extent=(1.0,))
    r1 = jnp.array([0.1])
    r2 = jnp.array([0.9])
    disp = cell.displacement(r1, r2)
    assert jnp.allclose(disp, jnp.array([-0.2]))
    disp_jit = jax.jit(cell.displacement)(r1, r2)
    assert jnp.allclose(disp_jit, jnp.array([-0.2]))

    cell_open = electroket.Cell(extent=(1.0,), pbc=False)
    disp_open = cell_open.displacement(r1, r2)
    assert jnp.allclose(disp_open, jnp.array([0.8]))


def test_wrap_and_symmetry():
    cell = electroket.Cell(extent=(2.0, 3.0), pbc=(True, False))
    r = jnp.array([2.5, -1.0])
    wrapped = cell.wrap(r)
    assert jnp.allclose(wrapped, jnp.array([0.5, -1.0]))

    r2 = jnp.array([0.4, 1.0])
    d12 = cell.displacement(r, r2)
    d21 = cell.displacement(r2, r)
    assert jnp.allclose(d12, -d21)


def test_nd_displacement():
    l = jnp.array([4.0, 4.0, 4.0, 4.0])
    cell = electroket.Cell(extent=tuple(l))
    zero = jnp.zeros(4)
    disp = cell.displacement(zero, l * 0.75)
    assert jnp.allclose(disp, -l * 0.25)


def test_reciprocal_vectors():
    cell = electroket.Cell(extent=(8.0, 10.0))
    gvecs = cell.reciprocal_vectors(g_max=9.0)
    assert jnp.max(jnp.linalg.norm(gvecs, axis=1)) <= 9.0 + 1e-12

    cell_open = electroket.Cell(extent=(8.0, 10.0), pbc=(True, False))
    gvecs2 = cell_open.reciprocal_vectors(5.0)
    assert gvecs2.shape == (0, 2)


def test_freespace_distance():
    fs = electroket.FreeSpace(2)
    r1 = jnp.array([1.0, 0.0])
    r2 = jnp.array([0.0, 1.0])
    assert jnp.isclose(fs.distance(r1, r2), jnp.sqrt(2.0))


def test_has_pbc_property():
    cell = electroket.Cell(extent=(1.0, 2.0), pbc=(True, False))
    assert cell.has_pbc

    fs = electroket.FreeSpace(3)
    assert not fs.has_pbc
