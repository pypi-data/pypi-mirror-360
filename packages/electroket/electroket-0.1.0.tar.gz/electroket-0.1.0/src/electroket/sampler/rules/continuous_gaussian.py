import jax
import jax.numpy as jnp
import numpy as np

from netket.sampler.rules.base import MetropolisRule


class GaussianRule(MetropolisRule):
    r"""A Gaussian transition rule for continuous systems."""

    sigma: float
    """Variance of the Gaussian distribution used to propose new configurations."""

    def __init__(self, sigma: float = 1.0) -> None:
        """Construct the rule.

        Parameters
        ----------
        sigma
            Standard deviation of the Gaussian distribution used to propose
            new configurations.
        """
        self.sigma = sigma

    def transition(
        rule,
        sampler,
        machine,
        parameters,
        state,
        key,
        r,
    ):
        if jnp.issubdtype(r.dtype, jnp.complexfloating):
            raise TypeError("Gaussian Rule does not work with complex basis elements.")

        n_chains = r.shape[0]
        hilb = sampler.hilbert

        try:
            cell = hilb.geometry
        except AttributeError as err:
            raise TypeError("Hilbert space must define a `geometry` attribute") from err

        pos_idx = getattr(hilb, "position_indices", tuple(range(hilb.size)))
        n_particles = getattr(hilb, "n_particles", 1)

        base_pbc = jnp.tile(cell._pbc, n_particles).astype(bool)
        base_extent = jnp.tile(cell.lengths, n_particles).astype(r.dtype)

        pos_idx_arr = jnp.asarray(pos_idx)
        boundary = base_pbc.take(pos_idx_arr)

        prop = jax.random.normal(
            key, shape=(n_chains, len(pos_idx)), dtype=r.dtype
        ) * jnp.asarray(rule.sigma, dtype=r.dtype)

        new_pos = r[:, pos_idx] + prop
        if cell.has_pbc:
            modulus = base_extent.take(pos_idx_arr)
            new_pos = jnp.where(boundary, new_pos % modulus, new_pos)

        rp = r.at[:, pos_idx].set(new_pos)

        return rp, None

    def __repr__(self) -> str:
        return f"GaussianRule(sigma={self.sigma})"
