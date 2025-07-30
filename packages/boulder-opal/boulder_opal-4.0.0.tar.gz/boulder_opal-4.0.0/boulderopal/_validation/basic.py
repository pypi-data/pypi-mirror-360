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

from collections import namedtuple
from enum import Enum
from functools import partial
from operator import (
    ge,
    gt,
    le,
    lt,
    ne,
)
from typing import (
    Any,
    Callable,
    Optional,
    Type,
    TypeVar,
    Union,
)

import numpy as np

from boulderopal._typing import (
    Concatenate,
    ParamSpec,
    Self,
)
from boulderopal._validation.exceptions import Checker

T = TypeVar("T", bound=Enum)


def validate_enum(enum_: Type[T], item: T | str) -> str:
    """
    Check whether the item is a valid option in enum_. If so, return the name of that option.
    Otherwise, raise an error.

    Parameters
    ----------
    enum_ : T
        An Enum where we expect the option value to be a str.
    item : T or str
        The item to be checked with enum_.

    Returns
    -------
    str
        The name of a valid enum option.
    """
    if isinstance(item, enum_):
        return item.name
    try:
        return getattr(enum_, item).name  # type: ignore
    except (TypeError, AttributeError) as err:
        raise ValueError(
            f"Only the following options are allowed: {list(enum_.__members__)}, got {item}."
        ) from err


def _filter_0d_array(val: Any) -> Any:
    if isinstance(val, np.ndarray) and val.ndim == 0:
        return val.item()
    return val


def _is_integer(val: Any) -> bool:
    return isinstance(_filter_0d_array(val), ScalarT.INT.value.types)


def _is_real(val: Any) -> bool:
    return _is_integer(val) or isinstance(
        _filter_0d_array(val), ScalarT.REAL.value.types
    )


def _is_complex(val: Any) -> bool:
    return _is_real(val) or _is_strict_complex(val)


def _is_strict_complex(val: Any) -> bool:
    return isinstance(_filter_0d_array(val), ScalarT.COMPLEX.value.types)


def _is_numeric(val: Any) -> bool:
    return _is_real(val) or _is_complex(val)


def _number_converter(val: Any) -> int | float | complex:
    if _is_integer(val):
        return int(val)
    if _is_real(val):
        return float(val)
    return complex(val)


# types: supported types defined by Python and Numpy for a given dtype
# checker: a callable to check the input scalar
# converter: a callable to convert the scalar to the corresponding Python primitive type
_ScalarTValidator = namedtuple("_ScalarTValidator", ["types", "checker", "converter"])

_Number = Union[int, float, complex, np.integer, np.float64, np.complex128]
_SCALAR = TypeVar("_SCALAR", bound=_Number)

_CompareOp = namedtuple("_CompareOp", ["op", "message"])


class _Compare(Enum):
    LESS = _CompareOp(lt, "smaller than")
    LESS_EQUAL = _CompareOp(le, "smaller than or equal to")
    GREATER = _CompareOp(gt, "greater than")
    GREATER_EQUAL = _CompareOp(ge, "greater than or equal to")
    NOT_EQUAL = _CompareOp(ne, "not equal to")


class _ScalarValidator:
    def __init__(self, type_: "ScalarT", name: str):
        self._type = type_
        self._name = name
        self._validator_pipe: list[Callable[[_Number], None]] = []

    def _compare(
        self, operator: _Compare, rhs: float | int, name: str, value: _Number
    ) -> None:
        Checker.VALUE(
            not _is_strict_complex(value),
            f"Complex number {self._name} doesn't support comparison.",
        )
        _name_val = str(rhs) if len(name) == 0 else f"{name} {rhs}"
        Checker.VALUE(
            operator.value.op(value, rhs),
            f"The {self._name} must be {operator.value.message} {_name_val}.",
            {self._name: value},
        )

    def lt(self, bound: float | int, rhs_name: str = "") -> Self:
        """
        Scalar < bound.
        """
        self._validator_pipe.append(
            partial(self._compare, _Compare.LESS, bound, rhs_name)
        )
        return self

    def le(self, bound: float | int, rhs_name: str = "") -> Self:
        """
        Scalar <= bound.
        """
        self._validator_pipe.append(
            partial(self._compare, _Compare.LESS_EQUAL, bound, rhs_name)
        )
        return self

    def gt(self, bound: float | int, rhs_name: str = "") -> Self:
        """
        Scalar > bound.
        """
        self._validator_pipe.append(
            partial(self._compare, _Compare.GREATER, bound, rhs_name)
        )
        return self

    def ge(self, bound: float | int, rhs_name: str = "") -> Self:
        """
        Scalar >= bound.
        """
        self._validator_pipe.append(
            partial(self._compare, _Compare.GREATER_EQUAL, bound, rhs_name)
        )
        return self

    def ne(self, value: float | int, rhs_name: str = "") -> Self:
        """
        Scalar != value.
        """
        self._validator_pipe.append(
            partial(self._compare, _Compare.NOT_EQUAL, value, rhs_name)
        )
        return self

    def __call__(self, value: _SCALAR, *, name: Optional[str] = None) -> _SCALAR:
        if name is not None:
            self._name = name
        Checker.TYPE(
            self._type.value.checker(value),
            f"The {self._name} must be a {self._type.name.lower()}.",
            {self._name: value},
        )
        _converted = self._type.value.converter(value)
        for _func in self._validator_pipe:
            _func(_converted)
        return _converted


class ScalarT(Enum):
    """
    Store dtypes to validate both Python and NumPy types.
    """

    INT = _ScalarTValidator((int, np.integer), _is_integer, int)
    REAL = _ScalarTValidator((float, np.float64), _is_real, float)
    COMPLEX = _ScalarTValidator((complex, np.complex128), _is_complex, complex)
    NUMERIC = _ScalarTValidator(None, _is_numeric, _number_converter)

    def __call__(self, name: str = "") -> _ScalarValidator:
        """
        Return a `_ScalarValidator` to validate a scalar by the dtype with optional constraints.

        Note that you can ignore the `name` argument and set it later when invoking the validator.
        """
        return _ScalarValidator(self, name)


# valid_dtype_kinds: valid values for the array's dtype.kind.
# dtype: data type of the returned validated NumPy array
_ArrayTValidator = namedtuple("_ArrayTValidator", ["valid_dtype_kinds", "dtype"])


def _no_comparison(value: np.ndarray, name: str) -> None:
    Checker.VALUE(
        value.dtype.kind != "c", f"Complex array {name} doesn't support comparison."
    )


class _ArrayValidator:
    def __init__(self, type_: "ArrayT", name: str):
        self._type = type_
        self._name = name
        self._validator_pipe: list[
            Callable[[np.ndarray], tuple[bool | np.bool_, str]]
        ] = []

    def ndim(self, dim_: int) -> Self:
        """
        The number of dimensions of the array must be dim_.
        """
        self._validator_pipe.append(
            lambda x: (x.ndim == dim_, f"The {self._name} must be a {dim_}D array.")
        )
        return self

    def shape(self, shape_: tuple, extra: str = "") -> Self:
        """
        The shape of the array must be shape_.
        """

        _shape_message = f"{shape_}" if len(extra) == 0 else f"{extra}, {shape_}"
        message = f"The shape of {self._name} must be {_shape_message}."
        self._validator_pipe.append(lambda x: (x.shape == shape_, message))
        return self

    def no_scalar(self) -> Self:
        """
        Do not allow scalar array.
        """
        self._validator_pipe.append(
            lambda x: (
                len(x.shape) > 0,
                f"The {self._name} must not be a scalar array.",
            )
        )
        return self

    def _compare(
        self, operator: _Compare, rhs: float | int, name: str, value: np.ndarray
    ) -> tuple[np.bool_, str]:
        _no_comparison(value, name)
        _name_val = str(rhs) if len(name) == 0 else f"{name} {rhs}"
        return (
            np.all(operator.value.op(value, rhs)),
            f"The value in {self._name} must be {operator.value.message} {_name_val}.",
        )

    def lt(self, bound: float | int, rhs_name: str = "") -> Self:
        """
        np.all(array < bound).
        """
        self._validator_pipe.append(
            partial(self._compare, _Compare.LESS, bound, rhs_name)
        )
        return self

    def le(self, bound: float | int, rhs_name: str = "") -> Self:
        """
        np.all(array <= bound).
        """
        self._validator_pipe.append(
            partial(self._compare, _Compare.LESS_EQUAL, bound, rhs_name)
        )
        return self

    def gt(self, bound: float | int, rhs_name: str = "") -> Self:
        """
        np.all(array > bound).
        """
        self._validator_pipe.append(
            partial(self._compare, _Compare.GREATER, bound, rhs_name)
        )
        return self

    def ge(self, bound: float | int, rhs_name: str = "") -> Self:
        """
        np.all(array >= bound).
        """
        self._validator_pipe.append(
            partial(self._compare, _Compare.GREATER_EQUAL, bound, rhs_name)
        )
        return self

    def ascend(self) -> Self:
        """
        In ascending order.
        """

        def _check(x: np.ndarray) -> tuple[np.bool_, str]:
            _no_comparison(x, self._name)
            return (
                np.all(np.diff(x) > 0),
                f"The {self._name} must be in ascending order and not have duplicate values.",
            )

        self._validator_pipe.append(_check)
        return self

    def descend(self) -> Self:
        """
        In descending order.
        """

        def _check(x: np.ndarray) -> tuple[np.bool_, str]:
            _no_comparison(x, self._name)
            return (
                np.all(np.diff(x) < 0),
                f"The {self._name} must be in descending order and not have duplicate values.",
            )

        self._validator_pipe.append(_check)
        return self

    def square(self) -> Self:
        """
        Last two dimensions are equal.
        """
        self._validator_pipe.append(
            lambda x: (
                x.shape[-1] == x.shape[-2],
                f"The {self._name} must be square in the last two dimensions.",
            )
        )
        return self

    def hermitian(self) -> Self:
        """
        Equals its adjoint.
        """
        self._validator_pipe.append(
            lambda x: (
                np.allclose(x, np.moveaxis(x, -1, -2).conj()),
                f"The {self._name} must be Hermitian.",
            )
        )
        return self

    def idempotent(self) -> Self:
        """
        Equals its square.
        """
        self._validator_pipe.append(
            lambda x: (
                np.allclose(x, x @ x),
                f"The {self._name} must be idempotent, but does not equal its square.",
            )
        )
        return self

    def __call__(self, value: Any, *, name: Optional[str] = None) -> np.ndarray:
        if name is not None:
            self._name = name
        try:
            _converted = np.asarray(value)
        except ValueError as exc:
            raise TypeError(
                f"Can't convert {self._name} to an array, {self._name}={value}."
            ) from exc
        Checker.VALUE(
            _converted.size > 0, f"The {self._name} must not be an empty array."
        )
        Checker.TYPE(
            _converted.dtype.kind in self._type.value.valid_dtype_kinds,
            f"The {self._name} must be a {self._type.name.lower()} array.",
        )

        # Special handler for cases:
        # - int typed array to address the signed and unsigned cases.
        # - a generic numeric array
        # That is, we preserve the dtype from users in these cases.
        if self._type not in (ArrayT.INT, ArrayT.NUMERIC):
            try:
                _converted = _converted.astype(self._type.value.dtype, casting="safe")
            except TypeError as err:
                raise TypeError(
                    f"Expected {self._name} as an array of {self._type.name.lower()} dtype, "
                    f"but got {_converted.dtype}."
                ) from err

        for func in self._validator_pipe:
            Checker.VALUE(*func(_converted))

        return _converted


class ArrayT(Enum):
    """
    Store dtypes to validate array-likes.
    """

    INT = _ArrayTValidator("iu", np.integer)
    REAL = _ArrayTValidator("iuf", np.float64)
    COMPLEX = _ArrayTValidator("iufc", np.complex128)
    NUMERIC = _ArrayTValidator("iufc", None)

    def __call__(self, name: str = "") -> _ArrayValidator:
        """
        Return an `_ArrayValidator` to validate an array-like by the dtype
        with optional constraints.

        Note that you can ignore the `name` argument and set it later when invoking the validator.
        """
        return _ArrayValidator(self, name)


_VAL = TypeVar("_VAL")
P = ParamSpec("P")


def nullable(
    validator: Callable[Concatenate[_VAL, P], _VAL],
    value: Optional[_VAL],
    *args: P.args,
    **kwargs: P.kwargs,
) -> Optional[_VAL]:
    """
    Validate a parameter that can be None.

    When the parameter holds a non-null value, the validator callable is used to check the value.
    The validator takes the value as the first argument and some other options as defined by P, it
    returns the same type as the input value (strictly speaking, the returned type is something
    that can be converted from the input one. But in reality, we expect them to be
    interchangeable). The P annotation here allows mypy to also check the types for the
    resting arguments of the validator.
    """
    if value is None:
        return value
    return validator(value, *args, **kwargs)
