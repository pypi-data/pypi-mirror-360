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
    TYPE_CHECKING,
    Any,
    Callable,
    Iterator,
    Optional,
    SupportsIndex,
    no_type_check,
)

import numpy as np
from qctrlcommons.node.wrapper import (
    NamedNodeData,
    NodeData,
    Operation,
)

if TYPE_CHECKING:
    from boulderopal.graph import Graph


def _get_item(
    graph: "Graph", value: Any, key: SupportsIndex | slice, name: Optional[str] = None
) -> Any:
    """
    Get an item (or items) from a node value.

    Typically you would use slicing syntax ``value[key]`` instead of using this function directly.

    Parameters
    ----------
    graph : Graph
        The graph that the node belongs to.
    value : Any
        The value from which to get the item.
    key : SupportsIndex or slice
        The key for the item or items.
    name : str or None, optional
        The name of the node.

    Returns
    -------
    Any
        The item or items obtained from ``value[key]``.
    """

    return NamedNodeData(
        Operation(graph, "getitem", False, value=value, key=key, name=name)
    )


def _get_attribute(
    graph: "Graph", value: Any, attr: str, name: Optional[str] = None
) -> Any:
    """
    Get an attribute from a node value.

    Typically you would use the syntax ``value.attr`` instead of using this function directly.

    Parameters
    ----------
    graph : Graph
        The graph that the node belongs to.
    value : Any
        The value from which to get the item.
    attr : str
        The name of the attribute.
    name : str or None, optional
        The name of the node.

    Returns
    -------
    Any
        The item or items obtained from ``value.attr``, or to be more precise,
        ``getattr(value, attr)``.

    Notes
    -----
    Only certain combinations of `value` and `attr` are supported.
    """

    valid = {"FilterFunction": ("inverse_powers", "uncertainties"), "Pwc": ("values")}
    if attr in valid.get(value.__class__.__name__, ()):
        return NamedNodeData(
            Operation(graph, "getattr", False, value=value, attr=attr, name=name)
        )

    # Invalid combination of value type and attr, so show an error message.
    raise ValueError(
        f"Not allowed to fetch attribute. Valid combinations are {valid}, "
        f"but got {value.__class__.__name__} with {attr}."
    )


class ArithmeticMixin:
    """
    Mixin to be used by NodeData that support binary arithmetic operations with
    number/array/Tensor/Pwc/Stf objects.

    By default ``arr + graph.op()`` throws an error, since NumPy doesn't know how to add
    `graph.op()` objects to arrays. Even the fact that the func ops override `__radd__` doesn't
    help, since the NumPy addition takes precedence. We can instead tell NumPy to delegate all
    binary operations to the other operand, by explicitly clearing the `__array_ufunc__`
    attribute.
    """

    __array_ufunc__ = None

    @no_type_check
    def __add__(self, other):
        return self.operation.graph.add(self, other)

    @no_type_check
    def __radd__(self, other):
        return self.operation.graph.add(other, self)

    @no_type_check
    def __sub__(self, other):
        return self.operation.graph.subtract(self, other)

    @no_type_check
    def __rsub__(self, other):
        return self.operation.graph.subtract(other, self)

    @no_type_check
    def __matmul__(self, other):
        return self.operation.graph.matmul(self, other)

    @no_type_check
    def __rmatmul__(self, other):
        return self.operation.graph.matmul(other, self)

    @no_type_check
    def __mul__(self, other):
        return self.operation.graph.multiply(self, other)

    @no_type_check
    def __rmul__(self, other):
        return self.operation.graph.multiply(other, self)

    @no_type_check
    def __floordiv__(self, other):
        return self.operation.graph.floordiv(self, other)

    @no_type_check
    def __rfloordiv__(self, other):
        return self.operation.graph.floordiv(other, self)

    @no_type_check
    def __pow__(self, power):
        return self.operation.graph.pow(self, power)

    @no_type_check
    def __rpow__(self, other):
        return self.operation.graph.pow(other, self)

    @no_type_check
    def __truediv__(self, other):
        return self.operation.graph.truediv(self, other)

    @no_type_check
    def __rtruediv__(self, other):
        return self.operation.graph.truediv(other, self)

    @no_type_check
    def __abs__(self):
        return self.operation.graph.abs(self)

    @no_type_check
    def __neg__(self):
        return self.operation.graph.negative(self)


# pylint: disable=missing-function-docstring
class Tensor(NamedNodeData, ArithmeticMixin):
    """
    A multi-dimensional array of data.

    Most functions accepting a :obj:`.Tensor` object can alternatively accept a NumPy array.

    You can use the arithmetic operators ``+``, ``-``, ``*``, ``**``, ``/``, ``//``, and ``@``
    to perform operations between two `Tensor` objects.

    Attributes
    ----------
    shape : tuple
        The shape of the tensor.
    name : str
        The name assigned to the node.

    See Also
    --------
    Graph.tensor : Create a real or complex Tensor with the data provided.

    Notes
    -----
    The value of a `Tensor` node can be fetched in a graph calculation
    by adding its `name` in the `output_node_names` parameter for the function call.
    This will add an item to the output dictionary in the calculation result object,
    whose key is `name`. The item's value will be a dictionary
    with the "value" of the Tensor as a NumPy array.
    """

    def __init__(self, operation: Operation, shape: tuple[int, ...]) -> None:
        self.shape = shape
        super().__init__(operation=operation)
        self.operation.is_scalar_tensor = np.prod(self.shape) == 1

    def __getitem__(self, item: SupportsIndex | slice) -> "Tensor":
        """
        Refer to item in operation.
        """
        node_data = _get_item(self.operation.graph, self, item)
        shape = np.empty(self.shape)[item].shape
        return Tensor(node_data.operation, shape=shape)

    def __iter__(self) -> None:
        # Disable iteration for now. Even though this should work fine in theory (since all client
        # tensors have fully-defined shapes), allowing iterability on the client causes tensors to
        # pass checks that will fail in the backend (for example, if tensors are iterable on the
        # client, a multi-dimensional tensor can be passed to a function that expects a list of
        # tensors; such an input will fail in the backend though). This could be revisited in the
        # future if we're more strict about client-side validation of iterable inputs, or if we
        # update the backend to be able to iterate over tensors.
        raise TypeError(
            "You cannot iterate over Tensors directly. Instead you can iterate over the indices "
            "and extract elements of the tensor using `tensor[index]`."
        )

    def __repr__(self) -> str:
        return (
            f'<Tensor: name="{self.name}", '
            f'operation_name="{self.operation.operation_name}", '
            f"shape={self.shape}>"
        )


class Pwc(NamedNodeData, ArithmeticMixin):
    """
    A piecewise-constant tensor-valued function of time (or batch of such functions).

    You can use the arithmetic operators ``+``, ``-``, ``*``, ``**``, ``/``, ``//``, and ``@``
    to perform operations between two `Pwc` objects or between a `Pwc` and a `Tensor`.

    Attributes
    ----------
    values : Tensor
        The values of the function on the piecewise-constant segments.
    durations : np.ndarray
        The durations of the constant segments.
    value_shape : tuple
        The shape of the function value.
    batch_shape : tuple
        The shape of the batch in the function.
    name : str
        The name assigned to the node.

    See Also
    --------
    Graph.pwc : Operation to create piecewise-constant functions.

    Notes
    -----
    The value of a `Pwc` node can be fetched in a graph calculation
    by adding its `name` in the `output_node_names` parameter for the function call.
    This will add an item to the output dictionary in the calculation result object,
    whose key is `name`. The item's value will be a dictionary with the "durations"
    of the piecewise-constant segments, the "values" of the function at each segment,
    and its "time_dimension" (the axis of the values array that corresponds to time).
    Dimensions of the values trailing the time dimension represent the dimensions of
    the object represented by the `Pwc`.
    Dimensions preceding the time dimension represent batch dimensions.

    For more information on `Pwc` nodes see the `Working with time-dependent functions in
    Boulder Opal <https://docs.q-ctrl.com/boulder-opal/topics/working-with-time-dependent-
    functions-in-boulder-opal>`_ topic.
    """

    def __init__(
        self,
        operation: Operation,
        value_shape: tuple[int, ...],
        durations: np.ndarray,
        batch_shape: tuple[int, ...],
    ) -> None:
        self.value_shape = value_shape
        self.batch_shape = batch_shape
        self.durations = durations
        super().__init__(operation=operation)

    @property
    def values(self) -> Tensor:
        """
        Access to the values in Pwc.
        """
        node_data = _get_attribute(self.operation.graph, self, "values")
        shape = (
            tuple(self.batch_shape) + (len(self.durations),) + tuple(self.value_shape)
        )
        return Tensor(node_data.operation, shape=shape)

    def __repr__(self) -> str:
        return (
            f'<Pwc: name="{self.name}", '
            f'operation_name="{self.operation.operation_name}", '
            f"value_shape={self.value_shape}, batch_shape={self.batch_shape}>"
        )


class Stf(NodeData, ArithmeticMixin):
    """
    A sampleable tensor-valued function of time (or batch of such functions).

    You can use the arithmetic operators ``+``, ``-``, ``*``, ``**``, ``/``, ``//``, and ``@``
    to perform operations between two `Stf` objects or between an `Stf` and a `Tensor`.

    Attributes
    ----------
    value_shape : tuple
        The shape of the function value.
    batch_shape : tuple
        The shape of the batch in the function.

    See Also
    --------
    Graph.identity_stf : Operation to create an `Stf` representing the identity function.

    Notes
    -----
    Stf nodes represent arbitrary functions of time. Piecewise-constant (PWC) or constant functions
    are special cases of Stfs and the Q-CTRL Python package provides specific APIs to support them.
    Note that as the PWC property can simplify the calculation, you should always consider using
    PWC-related APIs if your system parameters or controls are described by PWC functions.

    The value of `Stf` nodes is not fetchable from graphs.
    Therefore, they do not have a `name` attribute.

    For more information on `Stf` nodes see the `Working with time-dependent functions in
    Boulder Opal <https://docs.q-ctrl.com/boulder-opal/topics/working-with-time-dependent-
    functions-in-boulder-opal>`_ topic.
    """

    def __init__(
        self,
        operation: Operation,
        value_shape: tuple[int, ...],
        batch_shape: tuple[int, ...],
    ):
        self.value_shape = value_shape
        self.batch_shape = batch_shape
        super().__init__(operation=operation)

    def __repr__(self) -> str:
        return (
            f'<Stf: operation_name="{self.operation.operation_name}", '
            f"value_shape={self.value_shape}, batch_shape={self.batch_shape}>"
        )


class SparsePwc(NodeData):
    """
    A piecewise-constant sparse-matrix-valued function of time.

    Attributes
    ----------
    value_shape : tuple[int, ...]
        The shape of the function value.
    durations : np.ndarray
        The durations of the constant segments.

    See Also
    --------
    Graph.sparse_pwc_operator : Operation to create `SparsePwc` operators.

    Notes
    -----
    The value of `SparsePwc` nodes is not fetchable from graphs.
    Therefore, they do not have a `name` attribute.
    """

    def __init__(
        self, operation: Operation, value_shape: tuple[int, ...], durations: np.ndarray
    ) -> None:
        self.value_shape = value_shape
        self.durations = durations
        super().__init__(operation=operation)

    def __repr__(self) -> str:
        return (
            f'<SparsePwc: operation_name="{self.operation.operation_name}", '
            f"value_shape={self.value_shape}>"
        )


class Target(NodeData):
    """
    A target gate for an infidelity calculation.

    Attributes
    ----------
    value_shape : tuple[int, ...]
        The shape of the target gate operation.

    See Also
    --------
    Graph.target : Operation to define the target operation of a time evolution.

    Notes
    -----
    The value of `Target` nodes is not fetchable from graphs.
    Therefore, they do not have a `name` attribute.
    """

    def __init__(self, operation: Operation, value_shape: tuple[int, ...]) -> None:
        self.value_shape = value_shape
        super().__init__(operation=operation)

    def __repr__(self) -> str:
        return (
            f'<Target: operation_name="{self.operation.operation_name}", '
            f"value_shape={self.value_shape}>"
        )


class ConvolutionKernel(NodeData):
    """
    A kernel to be used in a convolution.

    See Also
    --------
    Graph.convolve_pwc : Operation to create an `Stf` by convolving a `Pwc` with a kernel.
    Graph.gaussian_convolution_kernel : Operation to create a convolution kernel representing a
        normalized Gaussian.
    Graph.sinc_convolution_kernel : Operation to create a convolution kernel representing the sinc
        function.

    Notes
    -----
    The value of `ConvolutionKernel` nodes is not fetchable from graphs.
    Therefore, they do not have a `name` attribute.
    """

    def __init__(self, operation: Operation) -> None:
        super().__init__(operation=operation)

    def __repr__(self) -> str:
        return f'<ConvolutionKernel: operation_name="{self.operation.operation_name}">'


class Sequence(NamedNodeData):
    """
    Wrapper class for creating a sequence of Nodes.
    """

    def __init__(self, operation: Operation) -> None:
        self.items: list[Any] = []
        super().__init__(operation=operation)

    def create_sequence(self, node_constructor: Callable, size: int) -> "Sequence":
        """
        Populate the `items` of the sequence from the operation.

        Parameters
        ----------
        node_constructor : Callable
            A callable to generate the node data for the sequence.
        size : int
            Size of the sequence.

        Returns
        -------
        Sequence
            The sequence itself.
        """

        def get_item_op(item: SupportsIndex) -> "Operation":
            return _get_item(self.operation.graph, self, item).operation

        self.items = [
            node_constructor(get_item_op(index), index) for index in range(size)
        ]

        return self

    def __getitem__(self, index: int) -> "Operation":
        return self.items[index]

    def __iter__(self) -> Iterator:
        return iter(self.items)

    def __len__(self) -> int:
        return len(self.items)

    def __repr__(self) -> str:
        return (
            f'<Sequence: operation_name="{self.operation.operation_name}", '
            f"items={self.items}>"
        )


class FilterFunction(NamedNodeData):
    """
    A tensor-valued filter function result.

    Attributes
    ----------
    inverse_powers : Tensor
        The values of the filter function at the given frequencies.
    uncertainties : Tensor, optional
        The uncertainties of the filter function values.
        This field is None when the exact method is used for computing the filter function.
    frequencies : np.ndarray
        The frequencies at which the filter function has been evaluated.
    value_shape : tuple[int]
        The shape of the function value.
    exact : bool
        Indicates whether filter function is exact.
    name : str
        The name assigned to the node.

    See Also
    --------
    Graph.filter_function :
        Evaluate the filter function for a control Hamiltonian and a noise operator at the given
        frequency elements.

    Notes
    -----
    The value of a `FilterFunction` node can be fetched in a graph calculation
    by adding its `name` in the `output_node_names` parameter for the function call.
    This will add an item to the output dictionary in the calculation result object,
    whose key is `name`. The item's value will be a dictionary
    with NumPy arrays with the "frequencies" and "inverse_powers" values.
    If the filter function calculation is not exact, the dictionary also
    contains an array with the filter function "uncertainties".
    """

    def __init__(
        self, operation: Operation, frequencies: np.ndarray, exact: bool
    ) -> None:
        self.frequencies = frequencies
        self.exact = exact
        super().__init__(operation=operation)

    @property
    def value_shape(self) -> tuple[int, ...]:
        """
        Access the value shape.
        """
        return (len(self.frequencies),)

    @property
    def inverse_powers(self) -> Tensor:
        """
        Access to the inverse powers in FilterFunction.
        """
        node_data = _get_attribute(self.operation.graph, self, "inverse_powers")
        return Tensor(node_data.operation, shape=self.value_shape)

    @property
    def uncertainties(self) -> Optional[Tensor]:
        """
        Access to the uncertainties in FilterFunction.
        """
        if self.exact is False:
            node_data = _get_attribute(self.operation.graph, self, "uncertainties")
            return Tensor(node_data.operation, shape=self.value_shape)
        return None

    def __repr__(self) -> str:
        return (
            f'<FilterFunction: name="{self.name}", '
            f'operation_name="{self.operation.operation_name}", '
            f"value_shape={self.value_shape}>"
        )
