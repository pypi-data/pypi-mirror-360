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
"""Implementation of sums of continuous operators."""

from typing import Iterable, no_type_check
from collections.abc import Callable, Hashable

import jax.numpy as jnp
from netket.jax import canonicalize_dtypes
from netket.utils import HashableArray, struct
from netket.utils.numbers import is_scalar
from netket.utils.types import Array, DType, PyTree

from ._continuous_operator import ContinuousOperator


@struct.dataclass
class SumOperatorPyTree:
    """Data container used by :class:`SumOperator` JAX kernels."""

    ops: tuple[ContinuousOperator, ...] = struct.field(pytree_node=False)
    coeffs: Array
    op_data: tuple[PyTree, ...]


def _flatten_sumoperators(
    operators: Iterable[ContinuousOperator], coefficients: Array
) -> tuple[list[ContinuousOperator], list[complex]]:
    """Flatten nested :class:`SumOperator` objects."""
    new_operators: list[ContinuousOperator] = []
    new_coeffs: list[complex] = []
    for op, c in zip(operators, coefficients):
        if isinstance(op, SumOperator):
            new_operators.extend(op.operators)
            new_coeffs.extend(c * op.coefficients)
        else:
            new_operators.append(op)
            new_coeffs.append(c)
    return new_operators, new_coeffs


class SumOperator(ContinuousOperator):
    r"""Sum of multiple continuous operators."""

    _operators: tuple[ContinuousOperator, ...]
    _coefficients: Array
    _is_hermitian: bool
    __attrs: tuple[Hashable, ...] | None

    @no_type_check
    def __init__(
        self,
        *operators: ContinuousOperator,
        coefficients: float | Iterable[float] = 1.0,
        dtype: DType | None = None,
    ) -> None:
        """Constructs a sum of ``ContinuousOperator`` instances."""
        hi_spaces = [op.hilbert for op in operators]
        if not all(hi == hi_spaces[0] for hi in hi_spaces):
            raise NotImplementedError(
                "Cannot add operators on different hilbert spaces"
            )

        if is_scalar(coefficients):
            coefficients = [coefficients for _ in operators]  # type: ignore

        if len(operators) != len(coefficients):  # type: ignore
            raise AssertionError("Each operator needs a coefficient")

        operators, coefficients = _flatten_sumoperators(operators, coefficients)

        dtype = canonicalize_dtypes(float, *operators, *coefficients, dtype=dtype)

        self._operators = tuple(operators)
        self._coefficients = jnp.asarray(coefficients, dtype=dtype)

        super().__init__(hi_spaces[0], self._coefficients.dtype)

        self._is_hermitian = all(op.is_hermitian for op in operators)
        self.__attrs = None

    @property
    def is_hermitian(self) -> bool:
        return self._is_hermitian

    @property
    def operators(self) -> tuple[ContinuousOperator, ...]:
        """Operators appearing in this sum."""
        return self._operators

    @property
    def coefficients(self) -> Array:
        return self._coefficients

    @staticmethod
    def _expect_kernel(
        logpsi: Callable, params: PyTree, x: Array, data: SumOperatorPyTree
    ) -> Array:
        result = [
            data.coeffs[i] * op._expect_kernel(logpsi, params, x, op_data)
            for i, (op, op_data) in enumerate(zip(data.ops, data.op_data))
        ]
        return sum(result)

    def _pack_arguments(self) -> SumOperatorPyTree:
        return SumOperatorPyTree(
            self.operators,
            self.coefficients,
            tuple(op._pack_arguments() for op in self.operators),
        )

    @property
    def _attrs(self) -> tuple[Hashable, ...]:
        if self.__attrs is None:
            self.__attrs = (
                self.hilbert,
                self.operators,
                HashableArray(self.coefficients),
                self.dtype,
            )
        return self.__attrs

    def __repr__(self) -> str:
        return (
            f"SumOperator(operators={self.operators}, coefficients={self.coefficients})"
        )
