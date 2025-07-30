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

from typing import (
    Callable,
    Optional,
)

import numpy as np

from boulderopal._nodes.node_data import (
    Pwc,
    SparsePwc,
    Tensor,
)
from boulderopal._validation import Checker


def get_broadcasted_shape(*shapes: tuple[int, ...], message: str) -> tuple[int, ...]:
    """
    Return the shape resulting of broadcasting multiple shapes,
    or None if they're not broadcastable.

    The shapes are broadcastable if, for each dimension starting from the end,
    they all have either the same size or a size 1.

    Parameters
    ----------
    *shapes : tuple[int]
        Shapes of the objects.
    message : str
        The error message.

    Returns
    -------
    tuple[int]
        The resulting broadcasted shape.
    """
    try:
        return np.broadcast_shapes(*shapes)
    except ValueError as e:
        raise ValueError(message) from e


def validate_function_output_shapes(
    x_batch_shape: tuple[int, ...],
    x_value_shape: tuple[int, ...],
    y_batch_shape: tuple[int, ...],
    y_value_shape: tuple[int, ...],
    validate_value_shape: Callable,
) -> tuple[tuple[int, ...], tuple[int, ...]]:
    """
    Get the output batch and value shape for two input shapes of Pwcs/Stfs.
    The names of the variables are assumed to be x and y when reporting errors.

    Parameters
    ----------
    x_batch_shape : tuple[int]
        The batch shape of the first object.
    x_value_shape : tuple[int]
        The value shape of the first object.
    y_batch_shape : tuple[int]
        The batch shape of the second object.
    y_value_shape : tuple[int]
        The value shape of the second object.
    validate_value_shape : Callable[[tuple, tuple, str, str], tuple]
        Function that takes the value shapes of two Tensors, Pwcs,
        or Stfs (as well as their names), and returns the expected values
        shape of the output Tensor, Pwc, or Stf. The function
        shouldn't assume that the shapes are compatible, and raise an
        exception if they aren't. The names provided should be used to
        generate the error message.

    Returns
    -------
    tuple[int], tuple[int]
        The batch and value shapes of the output Pwc/Stf.
    """
    batch_shape = get_broadcasted_shape(
        x_batch_shape,
        y_batch_shape,
        message="The batch shapes of x and y must be broadcastable.",
    )
    value_shape = validate_value_shape(x_value_shape, y_value_shape, "x", "y")

    return batch_shape, value_shape


def validate_tensor_and_function_output_shapes(
    t_shape: tuple[int, ...],
    f_batch_shape: tuple[int, ...],
    f_value_shape: tuple[int, ...],
    t_name: str,
    f_name: str,
    validate_value_shape: Callable,
    tensor_first: bool = True,
) -> tuple[tuple[int, ...], tuple[int, ...]]:
    """
    Get the output batch and value shape for an input tensor and an input Pwc/Stf.

    Parameters
    ----------
    t_shape : tuple[int, ...]
        The shape of the tensor.
    f_batch_shape : tuple[int, ...]
        The batch shape of the Pwc/Stf.
    f_value_shape : tuple[int, ...]
        The value shape of the Pwc/Stf.
    t_name : str
        The name of the tensor variable, used for the error message in case the shapes aren't
        compatible.
    f_name : str
        The name of the function variable, used for the error message in case the shapes aren't
        compatible.
    validate_value_shape : Callable[[tuple, tuple, str, str], tuple]
        Function that takes the value shapes of two Tensors, Pwcs,
        or Stfs (as well as their names), and returns the expected values
        shape of the output Tensor, Pwc, or Stf. The function
        shouldn't assume that the shapes are compatible, and raise an
        exception if they aren't. The names provided should be used to
        generate the error message.
    tensor_first : bool, optional
        Whether the Tensor is the leftmost parameter. Defaults to True.

    Returns
    -------
    tuple[int, ...], tuple[int, ...]
        The batch and value shapes of the output Pwc/Stf.
    """
    if tensor_first:
        value_shape = validate_value_shape(t_shape, f_value_shape, t_name, f_name)
    else:
        value_shape = validate_value_shape(f_value_shape, t_shape, f_name, t_name)

    return f_batch_shape, value_shape


def check_operation_axis(
    axis: Optional[list[int] | int], shape: tuple[int, ...], tensor_name: str
) -> list[int]:
    """
    Certain Tensor operations are applied along the axis of the Tensor.
    The function checks
    1. whether the axis is consistent with the shape of the tensor.
    2. whether there are any repeated items in axis.
    """

    if axis is None:
        return list(range(len(shape)))

    if not isinstance(axis, list):
        axis = [axis]

    for i, dimension in enumerate(axis):
        Checker.VALUE(
            -len(shape) <= dimension < len(shape),
            f"Elements of axis must be valid axes of {tensor_name} (between {-len(shape)} "
            f"and {len(shape)-1}, inclusive).",
            {f"axis[{i}]": dimension, f"len({tensor_name}.shape)": len(shape)},
        )
        if dimension < 0:
            axis[i] = dimension + len(shape)

    Checker.VALUE(
        len(set(axis)) == len(axis), "Elements of axis must be unique.", {"axis": axis}
    )

    return axis


def get_keepdims_operation_shape(
    shape: tuple[int, ...], axis: list[int], keepdims: bool
) -> tuple[int, ...]:
    """
    Return the shape of the operations that can keep the dimension of the input tensor.
    """
    output_shape = []
    for i, size in enumerate(shape):
        if i not in axis:
            output_shape.append(size)
        elif keepdims:
            output_shape.append(1)
    return tuple(output_shape)


def mesh_pwc_durations(pwcs: list[Pwc] | list[SparsePwc]) -> np.ndarray:
    """
    Return an array with the durations resulting of meshing the durations
    of the input PWC functions.

    Parameters
    ----------
    pwcs : list[Pwc] or list[SparsePwc]
        The Pwc functions whose durations should be meshed.

    Returns
    -------
    np.array
        The array with meshed durations.
    """
    _durations = [sum(pwc.durations) for pwc in pwcs]
    Checker.VALUE(
        np.allclose(_durations[0], _durations, atol=0.0),
        "All Pwc must have the same duration.",
    )

    times = np.unique(np.concatenate([np.cumsum(pwc.durations) for pwc in pwcs]))
    return np.diff(np.insert(times, 0, 0))


def get_arraylike_shape(
    x: Tensor | float | int | complex | np.ndarray,
) -> tuple[int, ...]:
    """
    Return the shape of an array-like object.
    """
    return getattr(x, "shape", ())
