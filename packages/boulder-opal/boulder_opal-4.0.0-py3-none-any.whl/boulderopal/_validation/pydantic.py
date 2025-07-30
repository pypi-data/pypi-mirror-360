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

from functools import (
    partial,
    wraps,
)
from itertools import chain
from typing import (
    Any,
    Callable,
    Iterator,
    List,
    Optional,
    Protocol,
    TypeVar,
    Union,
)

from pydantic import (
    ConfigDict,
    ValidationInfo,
    ValidatorFunctionWrapHandler,
    WrapValidator,
    validate_call,
)

from boulderopal._typing import ParamSpec
from boulderopal._validation.exceptions import Checker

T = TypeVar("T")


class _ValidatorT(Protocol):
    """
    All validator function should satisfy this protocol.
    """

    def __call__(self, value: Any, *, name: str) -> Any: ...


_ValidatorPipe = Optional[Union[List[_ValidatorT], _ValidatorT]]


def pipe(
    before: _ValidatorPipe = None, *, after: _ValidatorPipe = None
) -> WrapValidator:
    """
    This function is to mimic the behavior of the `Before/AfterValidator` with the `WrapValidator`
    such that one doesn't need to pass the name of the variable to be checked, and provide
    a simpler interface to define execution order.

    `before` and `after` are either a single validator or a list of them.
    All validators must be a callable with a signature like `func(value, *, name)`.

    The execution order is to run validators in the before list in the order as they are
    inserted, then invoke the Pydantic handler, and finally run all validators in the after list
    in the order they are inserted.
    """

    def inner_validator(
        value: T, handler: ValidatorFunctionWrapHandler, info: ValidationInfo
    ) -> T:

        def _normalize(validator: _ValidatorPipe) -> Iterator[Callable[[T], T]]:
            assert isinstance(info.field_name, str)
            if validator is None:
                return iter(())
            if callable(validator):
                return iter([partial(validator, name=info.field_name)])
            return (partial(func, name=info.field_name) for func in validator)

        for _func in chain(_normalize(before), [handler], _normalize(after)):  # type: ignore
            value = _func(value)  # type: ignore
        return value

    return WrapValidator(inner_validator)


P = ParamSpec("P")
R = TypeVar("R")


def validated(func: Callable[P, R]) -> Callable[P, R]:
    """
    Decorator to mark a callable as validated by Pydantic (V2) and in-house validators.

    The function wraps `validate_call` and `func` so that we can use Pydantic
    to validate inputs for the callable and also maintain its signature
    and docstring.

    Note that we enable the `arbitrary_types_allowed` flag to support the
    customized/flexible types in Boulder Opal.
    """

    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        return validate_call(func, config=ConfigDict(arbitrary_types_allowed=True))(  # type: ignore
            *args, **kwargs
        )

    return wrapper


def type_pipe(
    validators: list[_ValidatorT], messenger: Callable[[str], str]
) -> _ValidatorT:
    """
    Run the validators in the `validators` list sequentially until the value is resolved.
    Otherwise, throw a TypeError with the message customized by the `messenger` callable.

    This could be useful when resolving union types like scalar | Tensor.
    Similarly, all validators must have a signature like `func(value, * , name)`.
    """

    def _inner(value: T, *, name: str) -> T:
        for _validator in validators:
            try:
                return _validator(value, name=name)
            except TypeError:
                pass
        raise TypeError(messenger(name))

    return _inner


def sequence_like(
    validator: _ValidatorT, normalizer: Optional[type] = None, min_length: int = 1
) -> _ValidatorT:
    """
    Validate a single element or a list/tuple of elements with the same type.
    The element validator must have a signature like `func(value, * , name)`.

    This is useful in the case we want to perform validation for input type like `T | list[T]`,
    where we need to apply the same validator either to `T` or `list[T]`.

    Type like `T | list[T]` is often introduced for UX. If we want to normalize internally
    (i.e., to only handle `list[T]`), we can pass the optional `normalizer`. This parameter
    is expected to either be `list` or `tuple`.

    Note that similar to other utility Pydantic functions, this helper assumes that input
    can only be 1D sequence and doesn't support types other than list and tuple. Such
    type-checking is done by Pydantic.
    """

    def _inner(value: T, *, name: str) -> list[T] | tuple[T, ...] | T:
        if isinstance(value, (list, tuple)):
            Checker.VALUE(
                len(value) >= min_length,
                f"The {name} must have at least length {min_length}.",
            )
            return type(value)(
                validator(item, name=f"{name}[{idx}]") for idx, item in enumerate(value)
            )
        if normalizer is not None:
            return normalizer([validator(value, name=name)])
        return validator(value, name=name)

    return _inner
