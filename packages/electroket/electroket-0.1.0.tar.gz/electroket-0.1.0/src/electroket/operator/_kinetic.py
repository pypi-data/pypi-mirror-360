# Copyright 2021 The NetKet Authors - All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from collections.abc import Callable
from functools import partial

import numpy as np

import jax
import jax.numpy as jnp

from netket.utils.types import DType, PyTree, Array
import netket.jax as nkjax
from ..hilbert.particle import Particle, ParticleSet
from ._continuous_operator import ContinuousOperator
from netket.utils import HashableArray


def jacrev(f):
    def jacfun(x):
        y, vjp_fun = nkjax.vjp(f, x)
        if y.size == 1:
            eye = jnp.eye(y.size, dtype=x.dtype)[0]
            J = jax.vmap(vjp_fun, in_axes=0)(eye)
        else:
            eye = jnp.eye(y.size, dtype=x.dtype)
            J = jax.vmap(vjp_fun, in_axes=0)(eye)
        return J

    return jacfun


def jacfwd(f):
    def jacfun(x):
        jvp_fun = lambda s: jax.jvp(f, (x,), (s,))[1]
        eye = jnp.eye(len(x), dtype=x.dtype)
        J = jax.vmap(jvp_fun, in_axes=0)(eye)
        return J

    return jacfun


class KineticEnergy(ContinuousOperator):
    r"""Kinetic energy operator.

    The local kinetic energy is

    .. math::

       T_{loc}(x) = -\frac{\hbar^2}{2} \sum_i \frac{1}{m_i}
       \Bigl( \partial_i^2 \log\psi(x) + [\partial_i \log\psi(x)]^2 \Bigr).

    """

    def __init__(
        self,
        hilbert: Particle | ParticleSet,
        dtype: DType | None = None,
        hbar: float = 1.0,
    ) -> None:
        """Construct the kinetic energy operator for ``hilbert``.

        Args:
            hilbert: Continuous Hilbert space describing one or more particles.
            dtype: Optional data type for the underlying masses.
            hbar: Value of hbar. Defaults to ``1.0``.
        """

        masses = []
        coeffs = []
        dim = hilbert.geometry.dimension
        if isinstance(hilbert, Particle):
            if hilbert.mass is None:
                raise ValueError("Particle mass must be defined.")
            masses.append(hilbert.mass)
            coeffs.extend([(hbar**2) / hilbert.mass] * dim)
        elif isinstance(hilbert, ParticleSet):
            for p in hilbert.particles:
                m = p.mass
                if m is None:
                    raise ValueError("All particles must have a defined mass.")
                masses.append(m)
                if getattr(p, "position", None) is None:
                    coeffs.extend([(hbar**2) / m] * dim)
        else:
            raise TypeError("hilbert must be `Particle` or `ParticleSet`.")

        self._mass = jnp.asarray(masses, dtype=dtype)
        self._coeff = jnp.asarray(coeffs, dtype=dtype)
        self._hbar = float(hbar)

        self._is_hermitian = np.allclose(self._mass.imag, 0.0)
        self.__attrs = None

        super().__init__(hilbert, self._mass.dtype)

    @property
    def mass(self):
        return self._mass

    @property
    def hbar(self):
        return self._hbar

    @property
    def is_hermitian(self):
        return self._is_hermitian

    def _expect_kernel_single(
        self, logpsi: Callable, params: PyTree, x: Array, coefficient: PyTree | None
    ):
        def logpsi_x(x):
            return logpsi(params, x)

        dlogpsi_x = jacrev(logpsi_x)

        hess = jacfwd(dlogpsi_x)(x)[0].reshape(x.shape[0], x.shape[0])
        grad = dlogpsi_x(x)[0]
        pos_idx = jnp.asarray(self.hilbert.position_indices)
        dp_dx2 = jnp.diag(hess).take(pos_idx)
        dp_dx = grad.take(pos_idx) ** 2

        return -0.5 * jnp.sum(coefficient * (dp_dx2 + dp_dx), axis=-1)

    @partial(jax.vmap, in_axes=(None, None, None, 0, None))
    def _expect_kernel(
        self, logpsi: Callable, params: PyTree, x: Array, coefficient: PyTree | None
    ):
        return self._expect_kernel_single(logpsi, params, x, coefficient)

    def _pack_arguments(self) -> PyTree:
        return self._coeff

    @property
    def _attrs(self):
        if self.__attrs is None:
            self.__attrs = (
                self.hilbert,
                self.dtype,
                HashableArray(self.mass),
                self._hbar,
            )
        return self.__attrs

    def __repr__(self):
        return f"KineticEnergy(m={self._mass}, hbar={self._hbar})"
