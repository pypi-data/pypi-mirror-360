import jax.numpy as jnp
import electroket


class DummyHilbert(electroket.ContinuousHilbert):
    @property
    def size(self) -> int:
        return self.spatial_dimension

    @property
    def _attrs(self):
        return (self.domain,)


def test_continuous_hilbert_basic():
    hilb = DummyHilbert((1.0, 2.0, 3.0))
    assert hilb.domain == (1.0, 2.0, 3.0)
    assert hilb.spatial_dimension == 3


def test_cell_geometry():
    cell = electroket.Cell(extent=(1.0, 2.0))
    assert cell.dim == 2
    assert cell.extent == (1.0, 2.0)


def test_cell_and_free_space():
    cell = electroket.Cell(extent=(1.0, 2.0))
    assert cell.dimension == 2
    fs = electroket.FreeSpace(3)
    assert fs.dimension == 3
    assert fs.extent == (float("inf"),) * 3
    assert fs.pbc == (False,) * 3
