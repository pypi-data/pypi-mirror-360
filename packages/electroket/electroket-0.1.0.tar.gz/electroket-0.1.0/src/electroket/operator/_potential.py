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
"""Implementation of potential energy operators."""

from collections.abc import Callable, Hashable

import jax
import jax.numpy as jnp
from netket.utils import HashableArray, struct
from netket.utils.types import Array, DType, PyTree

from ..hilbert.continuous_hilbert import ContinuousHilbert
from ._continuous_operator import ContinuousOperator


@struct.dataclass
class PotentialOperatorPyTree:
    """Data container for JAX kernels of :class:`PotentialEnergy`."""

    potential_fun: Callable = struct.field(pytree_node=False)
    coefficient: Array


class PotentialEnergy(ContinuousOperator):
    r"""Local potential energy operator."""

    _afun: Callable
    _coefficient: Array
    __attrs: tuple[Hashable, ...] | None

    def __init__(
        self,
        hilbert: ContinuousHilbert,
        afun: Callable,
        coefficient: float = 1.0,
        dtype: DType | None = None,
    ) -> None:
        """Construct a potential energy operator.

        Parameters
        ----------
        hilbert
            Continuous Hilbert space on which the operator acts.
        afun
            Potential energy function ``V(x)`` receiving a single configuration.
        coefficient
            Scalar coefficient multiplying the potential energy.
        dtype
            Optional dtype of ``coefficient``.
        """
        self._afun = afun
        self._coefficient = jnp.asarray(coefficient, dtype=dtype)
        self.__attrs = None
        super().__init__(hilbert, self._coefficient.dtype)

    @property
    def coefficient(self) -> Array:
        return self._coefficient

    @property
    def is_hermitian(self) -> bool:
        return True

    @staticmethod
    def _expect_kernel(
        logpsi: Callable, params: PyTree, x: Array, data: PotentialOperatorPyTree
    ) -> Array:
        return data.coefficient * jax.vmap(data.potential_fun, in_axes=(0,))(x)

    def _pack_arguments(self) -> PotentialOperatorPyTree:
        return PotentialOperatorPyTree(self._afun, self.coefficient)

    @property
    def _attrs(self) -> tuple[Hashable, ...]:
        if self.__attrs is None:
            self.__attrs = (
                self.hilbert,
                self._afun,
                self.dtype,
                HashableArray(self.coefficient),
            )
        return self.__attrs

    def __repr__(self) -> str:
        return f"Potential(coefficient={self.coefficient}, function={self._afun})"
