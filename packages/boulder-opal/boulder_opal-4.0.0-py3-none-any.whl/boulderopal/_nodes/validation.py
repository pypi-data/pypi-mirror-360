# Copyright 2025 Q-CTRL. All rights reserved.
#
# Licensed under the Q-CTRL Terms of service (the "License"). Unauthorized
# copying or use of this file, via any medium, is strictly prohibited.
# Proprietary and confidential. You may not use this file except in compliance
# with the License. You may obtain a copy of the License at
#
#    https://q-ctrl.com/terms
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS. See the
# License for the specific language.

from __future__ import annotations

from enum import Enum
from functools import partial
from typing import (
    Any,
    Callable,
    Tuple,
    TypeVar,
)

import numpy as np
from scipy.sparse import spmatrix

from boulderopal._nodes.node_data import (
    Pwc,
    SparsePwc,
    Stf,
    Target,
    Tensor,
)
from boulderopal._typing import Self
from boulderopal._validation import (
    ArrayT,
    Checker,
    ScalarT,
    type_pipe,
)

_S = TypeVar("_S", Pwc, SparsePwc, Stf, Target, Tensor, np.ndarray, spmatrix)


def shapeable(value: _S, *, name: str) -> _S:
    """
    Perform preliminary validation for the input:
        - ensure a spmatrix or Tensor input is not empty.
        - do nothing if it's a Boulder Opal type that contains shape information.
        - try to convert the input to NumPy array.
    Note that this function doesn't know the argument type, which is left for Pydantic to check.
    """
    if isinstance(value, (Tensor, spmatrix)):
        Checker.VALUE(np.prod(value.shape) != 0, f"The {name} can't have empty value.")
        return value
    if isinstance(value, (Pwc, SparsePwc, Stf, Target)):
        return value
    return ArrayT.NUMERIC(name)(value)


BatchValueShapes = Tuple[Tuple[int, ...], Tuple[int, ...]]


def _get_matrix_shape(value: Any, name: str) -> BatchValueShapes:
    def _validate_shape(x: tuple[int, ...], strict: bool = False) -> tuple[int, ...]:
        if strict:
            Checker.VALUE(len(x) == 2, f"The value of {name} must be 2D.")
        else:
            Checker.VALUE(len(x) >= 2, f"The {name} must be at least 2D.")
        return x

    if isinstance(value, (np.ndarray, Tensor, spmatrix)):
        shape = _validate_shape(value.shape)
        return shape[:-2], shape[-2:]
    if isinstance(value, (Pwc, Stf)):
        value_shape = _validate_shape(value.value_shape, strict=True)
        return value.batch_shape, value_shape
    if isinstance(value, (SparsePwc, Target)):
        value_shape = _validate_shape(value.value_shape, strict=True)
        return (), value_shape
    raise TypeError(f"Unknown type for a matrix, got {type(value)}.")


def _get_operator_shape(value: Any, name: str) -> BatchValueShapes:
    def _validate_shape(x: tuple[int, ...], strict: bool = False) -> tuple[int, ...]:
        if strict:
            Checker.VALUE(len(x) == 2, f"The value of {name} must be 2D.")
        else:
            Checker.VALUE(len(x) >= 2, f"The {name} must be at least 2D.")
        Checker.VALUE(
            x[-1] == x[-2], f"The {name} must be a square in the last two dimensions."
        )
        return x

    if isinstance(value, (np.ndarray, Tensor, spmatrix)):
        shape = _validate_shape(value.shape)
        return shape[:-2], shape[-2:]
    if isinstance(value, (Pwc, Stf)):
        value_shape = _validate_shape(value.value_shape, strict=True)
        return value.batch_shape, value_shape
    if isinstance(value, (SparsePwc, Target)):
        value_shape = _validate_shape(value.value_shape, strict=True)
        return (), value_shape
    raise TypeError(f"Unknown type for an operator, got {type(value)}.")


def _get_vector_shape(value: Any, name: str) -> BatchValueShapes:
    def _validate_shape(
        shape_: tuple[int, ...], strict: bool = False
    ) -> tuple[int, ...]:
        Checker.VALUE(len(shape_) >= 1, f"The {name} must be at least 1D.")
        if strict:
            Checker.VALUE(len(shape_) == 1, f"The value of {name} must be 1D.")
        return shape_

    if isinstance(value, (np.ndarray, Tensor, spmatrix)):
        shape = _validate_shape(value.shape)
        return shape[:-1], shape[-1:]
    if isinstance(value, (Pwc, Stf)):
        value_shape = _validate_shape(value.value_shape, strict=True)
        return value.batch_shape, value_shape
    if isinstance(value, SparsePwc):
        value_shape = _validate_shape(value.value_shape, strict=True)
        return (), value_shape
    raise TypeError(f"Unknown type for a vector, got {type(value)}.")


def _get_signal_shape(value: Any, name: str) -> BatchValueShapes:
    def _validate_shape(shape_: tuple[int, ...]) -> tuple[int, ...]:
        Checker.VALUE(shape_ == (), f"The {name} must have scalar value.")
        return shape_

    if isinstance(value, (Pwc, Stf)):
        return value.batch_shape, _validate_shape(value.value_shape)
    raise TypeError(f"Unknown type for a signal, got {type(value)}.")


class ShapeT(Enum):
    """
    Validator to check the shape of types that can represent matrix, operator, vector, or signal.
    """

    MATRIX = partial(_get_matrix_shape)
    OPERATOR = partial(_get_operator_shape)
    VECTOR = partial(_get_vector_shape)
    SIGNAL = partial(_get_signal_shape)

    def __call__(self) -> "_ShapeT":
        return _ShapeT(self)


class _ShapeT:
    """
    A validator class to check shapes for ShapeT.
    """

    def __init__(self, type_: ShapeT) -> None:
        self._type = type_
        self._name = ""
        self._func_pipe: list[Callable] = []
        self._value_dim = 0

    def batch(self, count: int) -> Self:
        """
        len(batch_dimension) <= count.
        """

        def _check(x: tuple[int, ...], _: Any) -> None:
            Checker.VALUE(
                len(x) <= count,
                f"{self._name} can have at most {count} batch dimensions.",
            )

        self._func_pipe.append(_check)
        return self

    def no_batch(self) -> Self:
        """
        Value can't have batch.
        """

        def _check(x: tuple[int, ...], _: Any) -> None:
            Checker.VALUE(
                x == (),
                f"The {self._name} doesn't support batched input, "
                f"its whole shape must be {self._value_dim}D.",
            )

        self._func_pipe.append(_check)
        return self

    def __call__(self, value: _S, *, name: str) -> _S:
        self._name = name
        batch_shape, value_shape = self._type.value(value, name=self._name)
        self._value_dim = len(value_shape)
        for f in self._func_pipe:
            f(batch_shape, value_shape)
        return value


def bounded_by(
    value: np.ndarray, name: str, bound: float, bound_name: str
) -> np.ndarray:
    """
    value[-1] <= bound.
    """
    Checker.VALUE(
        value[-1] <= bound or np.isclose(value[-1], bound, atol=0.0),
        f"The {name} must be smaller than or equal to {bound_name}.",
    )
    return value


def starts_with_zero(value: np.ndarray, *, name: str) -> np.ndarray:
    """
    1D array should start with 0.
    """
    Checker.VALUE(np.isclose(value[0], 0), f"The {name} must start with zero.")
    return value


_T = TypeVar("_T", np.ndarray, Tensor)


def no_scalar(value: _T, *, name: str) -> _T:
    """
    Do not allow scalar array.
    """
    Checker.TYPE(len(value.shape) > 0, f"The {name} must not be scalar.")
    return value


def strict_real_array(value: _T, *, name: str) -> _T:
    """
    Ensure NumPy array is real.
    """
    if isinstance(value, np.ndarray):
        Checker.TYPE(value.dtype.kind in "iuf", f"The {name} must be a real array.")
    return value


def _to_scalar_tensor(value: Tensor, *, name: str) -> Tensor:
    """
    Check if a Tensor value contains a single element and return a scalar Tensor.
    """

    if isinstance(value, Tensor):
        if value.shape == (1,):
            return value[0]
        if value.shape == ():
            return value
    raise TypeError(f"The {name} must be a scalar Tensor.")


scalar_or_shapeable = type_pipe(
    [ScalarT.NUMERIC(), shapeable],
    messenger=lambda x: (
        f"The {x} must be either a non-empty NumPy array or Tensor, or a numeric scalar."
    ),
)


def _qutip_obj(value: Any, *, name: str) -> np.ndarray:
    if hasattr(value, "full"):
        return value.full()
    raise TypeError(f"{name} is not a QuTiP object.")


number_or_shapeable = type_pipe(
    [_qutip_obj, ScalarT.NUMERIC(), shapeable],
    messenger=lambda name: f"The variable {name} must be "
    "a number, a NumPy array, a Pwc, an Stf, or a Tensor.",
)


def _real_messenger(name: str) -> str:
    return (
        f"The variable {name} must be "
        "a real number, a real NumPy array, a Pwc, an Stf, or a real Tensor."
    )


real_shapeable = type_pipe([_qutip_obj, ScalarT.REAL(), shapeable], _real_messenger)
real_array = type_pipe([strict_real_array], messenger=_real_messenger)


def _scalar_messenger(name: str) -> str:
    return f"The {name} must be a scalar or a scalar-like Tensor."


scalar = type_pipe([ScalarT.NUMERIC(), _to_scalar_tensor], _scalar_messenger)
positive_scalar = type_pipe(
    [ScalarT.REAL().gt(0), _to_scalar_tensor], _scalar_messenger
)
non_negative_scalar = type_pipe(
    [ScalarT.REAL().ge(0), _to_scalar_tensor], _scalar_messenger
)
