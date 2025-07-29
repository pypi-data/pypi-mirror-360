"""STO-3G Gaussian basis parameters.

This module contains the STO-3G exponents and contraction coefficients
for elements hydrogen through oxygen. The data are stored in a dictionary
mapping element symbols to lists of shells. Each shell is represented by a
dictionary with the angular momentum type as ``"angular"``, a NumPy array of
``"exponents"`` and the corresponding ``"coefficients"``.
"""

from __future__ import annotations

import jax.numpy as jnp

__all__ = ["STO3G"]

STO3G: dict[str, list[dict[str, jnp.ndarray]]] = {
    "H": [
        {
            "angular": "s",
            "exponents": jnp.array([3.42525091, 0.62391373, 0.16885540]),
            "coefficients": jnp.array([0.15432897, 0.53532814, 0.44463454]),
        }
    ],
    "He": [
        {
            "angular": "s",
            "exponents": jnp.array([6.36242139, 1.15892300, 0.31364979]),
            "coefficients": jnp.array([0.15432897, 0.53532814, 0.44463454]),
        }
    ],
    "Li": [
        {
            "angular": "s",
            "exponents": jnp.array([16.119575, 2.9362007, 0.7946505]),
            "coefficients": jnp.array([0.15432897, 0.53532814, 0.44463454]),
        },
        {
            "angular": "s",
            "exponents": jnp.array([0.6362897, 0.1478601, 0.0480887]),
            "coefficients": jnp.array([-0.09996723, 0.39951283, 0.70011547]),
        },
        {
            "angular": "p",
            "exponents": jnp.array([0.6362897, 0.1478601, 0.0480887]),
            "coefficients": jnp.array([0.15591627, 0.60768372, 0.39195739]),
        },
    ],
    "Be": [
        {
            "angular": "s",
            "exponents": jnp.array([30.167871, 5.4951153, 1.4871927]),
            "coefficients": jnp.array([0.15432897, 0.53532814, 0.44463454]),
        },
        {
            "angular": "s",
            "exponents": jnp.array([1.3148331, 0.3055389, 0.0993707]),
            "coefficients": jnp.array([-0.09996723, 0.39951283, 0.70011547]),
        },
        {
            "angular": "p",
            "exponents": jnp.array([1.3148331, 0.3055389, 0.0993707]),
            "coefficients": jnp.array([0.15591627, 0.60768372, 0.39195739]),
        },
    ],
    "B": [
        {
            "angular": "s",
            "exponents": jnp.array([48.791113, 8.8873622, 2.4052670]),
            "coefficients": jnp.array([0.15432897, 0.53532814, 0.44463454]),
        },
        {
            "angular": "s",
            "exponents": jnp.array([2.2369561, 0.5198205, 0.1690618]),
            "coefficients": jnp.array([-0.09996723, 0.39951283, 0.70011547]),
        },
        {
            "angular": "p",
            "exponents": jnp.array([2.2369561, 0.5198205, 0.1690618]),
            "coefficients": jnp.array([0.15591627, 0.60768372, 0.39195739]),
        },
    ],
    "C": [
        {
            "angular": "s",
            "exponents": jnp.array([71.616837, 13.045096, 3.5305122]),
            "coefficients": jnp.array([0.15432897, 0.53532814, 0.44463454]),
        },
        {
            "angular": "s",
            "exponents": jnp.array([2.9412494, 0.6834831, 0.2222899]),
            "coefficients": jnp.array([-0.09996723, 0.39951283, 0.70011547]),
        },
        {
            "angular": "p",
            "exponents": jnp.array([2.9412494, 0.6834831, 0.2222899]),
            "coefficients": jnp.array([0.15591627, 0.60768372, 0.39195739]),
        },
    ],
    "N": [
        {
            "angular": "s",
            "exponents": jnp.array([99.106169, 18.052312, 4.8856602]),
            "coefficients": jnp.array([0.15432897, 0.53532814, 0.44463454]),
        },
        {
            "angular": "s",
            "exponents": jnp.array([3.7804559, 0.8784966, 0.2857144]),
            "coefficients": jnp.array([-0.09996723, 0.39951283, 0.70011547]),
        },
        {
            "angular": "p",
            "exponents": jnp.array([3.7804559, 0.8784966, 0.2857144]),
            "coefficients": jnp.array([0.15591627, 0.60768372, 0.39195739]),
        },
    ],
    "O": [
        {
            "angular": "s",
            "exponents": jnp.array([130.70932, 23.808861, 6.4436083]),
            "coefficients": jnp.array([0.15432897, 0.53532814, 0.44463454]),
        },
        {
            "angular": "s",
            "exponents": jnp.array([5.0331513, 1.1695961, 0.3803890]),
            "coefficients": jnp.array([-0.09996723, 0.39951283, 0.70011547]),
        },
        {
            "angular": "p",
            "exponents": jnp.array([5.0331513, 1.1695961, 0.3803890]),
            "coefficients": jnp.array([0.15591627, 0.60768372, 0.39195739]),
        },
    ],
}
