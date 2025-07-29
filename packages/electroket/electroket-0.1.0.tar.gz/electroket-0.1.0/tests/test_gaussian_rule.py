import jax
import jax.numpy as jnp
import numpy as np
import pytest
import electroket


class DummySampler:
    def __init__(self, hilbert):
        self.hilbert = hilbert


def test_gaussian_rule_no_pbc():
    cell = electroket.Cell(extent=(1.0,), pbc=False)
    hi = electroket.Particle(geometry=cell)
    sampler = DummySampler(hi)
    rule = electroket.sampler.rules.GaussianRule(sigma=0.5)

    r = jnp.zeros((2, hi.size))
    key = jax.random.PRNGKey(0)

    rp, _ = rule.transition(sampler, None, None, None, key, r)

    noise = jax.random.normal(key, shape=r.shape) * 0.5
    expected = r + noise
    np.testing.assert_allclose(np.asarray(rp), np.asarray(expected))


def test_gaussian_rule_pbc_wrap():
    cell = electroket.Cell(extent=(1.0,))
    hi = electroket.Particle(geometry=cell)
    sampler = DummySampler(hi)
    rule = electroket.sampler.rules.GaussianRule(sigma=0.2)

    r = jnp.array([[0.9]])
    key = jax.random.PRNGKey(1)

    rp, _ = rule.transition(sampler, None, None, None, key, r)
    noise = jax.random.normal(key, shape=r.shape) * 0.2
    expected = (r + noise) % 1.0
    np.testing.assert_allclose(np.asarray(rp), np.asarray(expected))


def test_gaussian_rule_complex_raises():
    cell = electroket.Cell(extent=(1.0,))
    hi = electroket.Particle(geometry=cell)
    sampler = DummySampler(hi)
    rule = electroket.sampler.rules.GaussianRule()

    r = jnp.zeros((1, hi.size), dtype=jnp.complex64)
    key = jax.random.PRNGKey(0)
    with pytest.raises(TypeError):
        rule.transition(sampler, None, None, None, key, r)


def test_gaussian_rule_free_space():
    fs = electroket.FreeSpace(3)
    hi = electroket.Particle(geometry=fs)
    sampler = DummySampler(hi)
    rule = electroket.sampler.rules.GaussianRule(sigma=0.1)

    r = jnp.zeros((2, hi.size))
    key = jax.random.PRNGKey(2)

    rp, _ = rule.transition(sampler, None, None, None, key, r)

    noise = jax.random.normal(key, shape=r.shape) * 0.1
    expected = r + noise
    np.testing.assert_allclose(np.asarray(rp), np.asarray(expected))
