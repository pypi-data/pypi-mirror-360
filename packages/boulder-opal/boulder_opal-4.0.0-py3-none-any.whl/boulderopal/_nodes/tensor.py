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

from typing import (
    Any,
    List,
    Literal,
    Optional,
    Tuple,
    Union,
)

import numpy as np
from pydantic import Field

from boulderopal._typing import Annotated
from boulderopal._validation import (
    Checker,
    ScalarT,
    pipe,
    sequence_like,
    type_pipe,
    validated,
)

from .base import create_operation
from .node_data import Tensor
from .utils import (
    check_operation_axis,
    get_broadcasted_shape,
    get_keepdims_operation_shape,
)
from .validation import (
    ShapeT,
    no_scalar,
    scalar_or_shapeable,
    shapeable,
)


def _embed_messenger(name: str) -> str:
    return f"The {name} must be a list of tuples with an operator and an integer position each."


def _embed_tuple(value: Any, *, name: str) -> Tuple[Union[np.ndarray, Tensor], int]:
    Checker.TYPE(
        isinstance(value, (list, tuple)) and len(value) == 2, _embed_messenger(name)
    )

    operator, position = value
    return (
        ShapeT.OPERATOR()(shapeable(operator, name=f"{name}[0]"), name=name),
        ScalarT.INT().ge(0)(position, name=f"{name}[1]"),
    )


_embed_validator = type_pipe(
    [_embed_tuple, sequence_like(_embed_tuple)], _embed_messenger
)


class TensorGraph:  # pylint: disable=too-many-public-methods,unused-argument
    """
    Base class implementing Tensor methods.
    """

    @validated
    def tensor(
        self,
        data: Annotated[
            Union[int, float, complex, np.ndarray, Tensor], pipe(scalar_or_shapeable)
        ],
        *,
        name: Optional[str] = None,
    ) -> Tensor:
        """
        Create a real or complex Tensor with the data provided.

        Parameters
        ----------
        data : number or np.ndarray or Tensor
            The data to convert to an appropriate tensor.
        name : str or None, optional
            The name of the node.

        Returns
        -------
        Tensor
            Real or complex Tensor representation of the input data.

        Notes
        -----
        Use this node to create a Tensor from some numeric `data`. Note that you
        can pass numbers or NumPy arrays to operations that accept Tensors.
        """
        operation = create_operation(self.tensor, locals())
        shape = getattr(data, "shape", ())
        return Tensor(operation, shape=shape)

    @validated
    def concatenate(
        self,
        tensors: Annotated[
            List[
                Annotated[Union[np.ndarray, Tensor], pipe(shapeable, after=no_scalar)]
            ],
            Field(min_length=2),
        ],
        axis: Annotated[int, pipe(ScalarT.INT())],
        *,
        name: Optional[str] = None,
    ) -> Tensor:
        """
        Concatenate a list of tensors along a specified dimension.

        Parameters
        ----------
        tensors : list[np.ndarray or Tensor]
            The list of tensors that you want to concatenate. All of them must have the
            same shape in all dimensions except `axis`. You must pass at least two
            elements in this list.
        axis : int
            The dimension along which you want to concatenate the tensors.
        name : str or None, optional
            The name of the node.

        Returns
        -------
        Tensor
            The concatenated tensor.

        Notes
        -----
        This node only concatenates on an existing axis, it does not create new
        axes. If you want to stack along a new axis or concatenate scalars, add
        a new axis to the tensors with ``[None]``.

        Examples
        --------
        >>> x = np.array([[1, 2, 3], [4, 5, 6]])
        >>> y = np.array([[7, 8, 9]])

        Concatenate `x` and `y` along their first dimension.

        >>> graph.concatenate(tensors=[x, y], axis=0, name="node_0")
        <Tensor: name="node_0", operation_name="concatenate", shape=(3, 3)>
        >>> result = bo.execute_graph(graph=graph, output_node_names="node_0")
        >>> result["output"]["node_0"]["value"]
        array([[1., 2., 3.],
               [4., 5., 6.],
               [7., 8., 9.]])

        Concatenate two `x` arrays along their second dimension.

        >>> graph.concatenate(tensors=[x, x], axis=1, name="node_1")
        <Tensor: name="node_1", operation_name="concatenate", shape=(2, 6)>
        >>> result = bo.execute_graph(graph=graph, output_node_names="node_1")
        >>> result["output"]["node_1"]["value"]
        array([[1., 2., 3., 1., 2., 3.],
               [4., 5., 6., 4., 5., 6.]])
        """

        Checker.VALUE(
            all(-len(tensor.shape) <= axis < len(tensor.shape) for tensor in tensors),
            "The axis must be a valid dimension of all the tensors.",
            {"axis": axis},
        )

        _axis = axis if axis >= 0 else axis + len(tensors[0].shape)

        lead_shape = tensors[0].shape[:_axis]
        trail_shape = tensors[0].shape[_axis + 1 :]

        Checker.VALUE(
            all(
                tensor.shape[:_axis] == lead_shape
                and tensor.shape[_axis + 1 :] == trail_shape
                for tensor in tensors
            ),
            "All tensors must have the same size in every dimension, except for the"
            " dimension that corresponds to the value of axis.",
            {"axis": axis},
        )

        shape = (
            lead_shape + (sum(tensor.shape[_axis] for tensor in tensors),) + trail_shape
        )

        operation = create_operation(self.concatenate, locals())
        return Tensor(operation, shape=shape)

    @validated
    def sum(
        self,
        input_tensor: Union[
            List[Tensor], Annotated[Union[np.ndarray, Tensor], pipe(shapeable)]
        ],
        axis: Optional[
            Annotated[
                Union[int, List[int]], pipe(sequence_like(ScalarT.INT(), min_length=0))
            ]
        ] = None,
        keepdims: bool = False,
        *,
        name: Optional[str] = None,
    ) -> Tensor:
        """
        Sum the elements in a tensor (or a list of tensors with the same shape) along
        one or multiple of its axes.

        Parameters
        ----------
        input_tensor : np.ndarray or Tensor or list[Tensor]
            The tensor whose elements you want to sum. If you pass a list of tensors, they must
            all have the same shape, and are interpreted as being stacked along a new first
            dimension (for example, if you pass two 2D tensors of shape ``(3, 4)``, the result
            is equivalent to passing the stacked 3D tensor of shape ``(2, 3, 4)``).
        axis : int or list[int] or None, optional
            The dimension or dimensions along which you want to sum the tensor. Defaults to None, in
            which case this node sums along all axes of the tensor.
        keepdims : bool, optional
            Whether or not to retain summed axes in the output tensor. If True, each dimension in
            `axis` has size 1 in the result; otherwise, the dimensions in `axis` are removed
            from the result. Defaults to False.
        name : str or None, optional
            The name of the node.

        Returns
        -------
        Tensor
            The tensor obtained by summing the input tensor along the specified axes (or, if
            `axis` was None, the tensor obtained by summing the input tensor along all of
            the specified axes).

        See Also
        --------
        Graph.einsum : Tensor contraction via Einstein summation convention.

        Examples
        --------
        Sum elements of an array.

        >>> a = np.array([1, 2, 3])
        >>> graph.sum(a, 0, name="sum_a")
        <Tensor: name="sum_a", operation_name="sum", shape=()>
        >>> result = bo.execute_graph(graph=graph, output_node_names="sum_a")
        >>> result["output"]["sum_a"]["value"]
        6

        Sum elements of a 2D array along its first dimension.

        >>> b = np.array([[1, 2, 3], [4, 5, 6]])
        >>> graph.sum(b, 0, name="sum_b")
        <Tensor: name="sum_b", operation_name="sum", shape=(3,)>
        >>> result = bo.execute_graph(graph=graph, output_node_names="sum_b")
        >>> result["output"]["sum_b"]["value"]
        array([5, 7, 9])
        """
        if isinstance(input_tensor, list):
            if len(input_tensor) > 0:
                Checker.VALUE(
                    all(
                        tensor.shape == input_tensor[0].shape
                        for tensor in input_tensor[1:]  # type: ignore
                    ),
                    "The tensors must have the same shape.",
                )
                shape = (len(input_tensor),) + input_tensor[0].shape
            else:
                # Note that if the input is an empty list then the shape is somewhat ambiguous (it
                # could be an empty list of tensors of any shape), but for consistency with
                # TF and NP we interpret it as 1D.
                shape = ()
        else:
            shape = input_tensor.shape

        axes = check_operation_axis(axis, shape, "input_tensor")

        output_shape = get_keepdims_operation_shape(shape, axes, keepdims)
        operation = create_operation(self.sum, locals())
        return Tensor(operation, shape=output_shape)

    @validated
    def reverse(
        self,
        tensor: Annotated[Union[np.ndarray, Tensor], pipe(shapeable, after=no_scalar)],
        axis: Annotated[Union[int, List[int]], pipe(sequence_like(ScalarT.INT()))],
        *,
        name: Optional[str] = None,
    ) -> Tensor:
        """
        Reverse a tensor along some specified dimensions.

        Parameters
        ----------
        tensor : np.ndarray or Tensor
            The tensor that you want to reverse. It must have at least
            one dimension.
        axis : int or list[int]
            The dimension or dimensions along which you want to reverse the tensor.
        name : str or None, optional
            The name of the node.

        Returns
        -------
        Tensor
            The reversed tensor.

        Examples
        --------
        >>> x = np.array([[1, 2, 3], [4, 5, 6]])

        Reverse an array along its first dimension.

        >>> graph.reverse(x, 0, name="a")
        <Tensor: name="a", operation_name="reverse", shape=(2, 3)>
        >>> result = bo.execute_graph(graph=graph, output_node_names="a")
        >>> result["output"]["a"]["value"]
        array([[4, 5, 6],
               [1, 2, 3]])

        Reverse an array along its first and second dimension.

        >>> graph.reverse(x, [0, 1], name="b")
        <Tensor: name="b", operation_name="reverse", shape=(2, 3)>
        >>> result = bo.execute_graph(graph=graph, output_node_names="b")
        >>> result["output"]["b"]["value"]
        array([[6, 5, 4],
               [3, 2, 1]])
        """
        shape = tensor.shape
        _ = check_operation_axis(axis, shape, "tensor")

        operation = create_operation(self.reverse, locals())
        return Tensor(operation, shape=shape)

    # pylint: disable=redefined-builtin
    @validated
    def repeat(
        self,
        input: Annotated[Union[np.ndarray, Tensor], pipe(shapeable, after=no_scalar)],
        repeats: Annotated[
            Union[int, List[int]],
            pipe(sequence_like(ScalarT.INT().ge(0), normalizer=list)),
        ],
        axis: Optional[Annotated[int, pipe(ScalarT.INT())]] = None,
        *,
        name: Optional[str] = None,
    ) -> Tensor:
        """
        Repeat elements of a tensor.

        Parameters
        ----------
        input : np.ndarray or Tensor
            The tensor whose elements you want to repeat.
        repeats : int or list[int]
            The number of times to repeat each element. If you pass a single int or singleton list,
            that number of repetitions is applied to each element. Otherwise, you must pass a list
            with the same length as `input` along the specified `axis` (or the same total length as
            `input` if you omit `axis`).
        axis : int or None, optional
            The axis along which you want to repeat elements. If you omit this value then the input
            is first flattened, and the repetitions applied to the flattened tensor.
        name : str or None, optional
            The name of the node.

        Returns
        -------
        Tensor
            The repeated tensor. The result has the same shape as `input` except along `axis`,
            where its size is either the sum of `repeats` (if `repeats` is a list with at least
            two elements) or the product of the original size along `axis` with `repeats` (if
            `repeats` is a single int or singleton list). If `axis` is None then the output is
            1D, with the sizes as described above applied to the flattened input tensor.

        Examples
        --------
        >>> x = np.array([1, 2, 3])
        >>> y = np.array([[1, 2, 3], [4, 5, 6]])

        Duplicate each entry in an array once.

        >>> graph.repeat(x, 2, axis=0, name="a")
        <Tensor: name="a", operation_name="repeat", shape=(6,)>
        >>> result = bo.execute_graph(graph=graph, output_node_names="a")
        >>> result["output"]["a"]["value"]
        array([1, 1, 2, 2, 3, 3])

        Create a new array with different repetitions for each element in the original array
        along its second dimension.

        >>> graph.repeat(x, [2, 3, 4], axis=0, name="b")
        <Tensor: name="b", operation_name="repeat", shape=(9,)>
        >>> result = bo.execute_graph(graph=graph, output_node_names="b")
        >>> result["output"]["b"]["value"]
        array([1, 1, 2, 2, 2, 3, 3, 3, 3])

        Duplicate each entry in an array along its second dimension.

        >>> graph.repeat(y, 2, axis=1, name="c")
        <Tensor: name="c", operation_name="repeat", shape=(2, 6)>
        >>> result = bo.execute_graph(graph=graph, output_node_names="c")
        >>> result["output"]["c"]["value"]
        array([[1, 1, 2, 2, 3, 3],
               [4, 4, 5, 5, 6, 6]])

        Create a new array with different repetitions for each element in the original array
        along its first dimension.

        >>> graph.repeat(y, [2, 3], axis=0, name="d")
        <Tensor: name="d", operation_name="repeat", shape=(5, 3)>
        >>> result = bo.execute_graph(graph=graph, output_node_names="d")
        >>> result["output"]["d"]["value"]
        array([[1, 2, 3],
               [1, 2, 3],
               [4, 5, 6],
               [4, 5, 6],
               [4, 5, 6]])
        """
        assert isinstance(repeats, list)
        # Prevent the creation of empty tensors.
        Checker.VALUE(
            sum(repeats) > 0,
            "At least one of the repeats must be different from zero.",
            {"repeats": repeats},
        )

        if axis is None:
            # The input is flattened if axis is None.
            shape: Tuple[int, ...] = (np.prod(input.shape, dtype=int),)
            _axis = 0
            _error_variable = "number of elements in input"
        else:
            shape = input.shape
            _axis = check_operation_axis(axis, shape, "input")[0]
            _error_variable = "length of the input along the axis"

        Checker.VALUE(
            len(repeats) == 1 or len(repeats) == shape[_axis],
            f"Number of repeats must either be one or equal to the {_error_variable}.",
            {"len(repeats)": len(repeats), _error_variable: shape[_axis]},
        )

        _repeats = repeats if len(repeats) > 1 else repeats * shape[_axis]

        output_shape = shape[:_axis] + (sum(_repeats),) + shape[_axis + 1 :]
        operation = create_operation(self.repeat, locals())
        return Tensor(operation, shape=output_shape)

    # pylint: enable=redefined-builtin

    @validated
    def cumulative_sum(
        self,
        x: Annotated[Union[np.ndarray, Tensor], pipe(shapeable, after=no_scalar)],
        axis: Annotated[int, pipe(ScalarT.INT())] = 0,
        *,
        name: Optional[str] = None,
    ) -> Tensor:
        """
        Calculate the cumulative sum of a tensor along a specified dimension.

        Parameters
        ----------
        x : np.ndarray or Tensor
            The tensor whose elements you want to sum. It must have at least
            one dimension.
        axis : int, optional
            The dimension along which you want to sum the tensor. Defaults to 0.
        name : str or None, optional
            The name of the node.

        Returns
        -------
        Tensor
            The cumulative sum of `x` along dimension `axis`.

        Examples
        --------
        >>> x = np.array([1, 2, 3])
        >>> y = np.array([[1, 2, 3], [4, 5, 6]])

        Calculate the cumulative sum of an array.

        >>> graph.cumulative_sum(x, axis=0, name="a")
        <Tensor: name="a", operation_name="cumulative_sum", shape=(3,)>
        >>> result = bo.execute_graph(graph=graph, output_node_names="a")
        >>> result["output"]["a"]["value"]
        array([1, 3, 6])

        Calculate the cumulative sum of a 2D array along its first dimension.

        >>> graph.cumulative_sum(y, axis=0, name="b")
        <Tensor: name="b", operation_name="cumulative_sum", shape=(2, 3)>
        >>> result = bo.execute_graph(graph=graph, output_node_names="b")
        >>> result["output"]["b"]["value"]
        array([[1, 2, 3],
               [5, 7, 9]])

        Calculate the cumulative sum of a 2D array along its second dimension.

        >>> graph.cumulative_sum(y, axis=1, name="c")
        <Tensor: name="c", operation_name="cumulative_sum", shape=(2, 3)>
        >>> result = bo.execute_graph(graph=graph, output_node_names="c")
        >>> result["output"]["c"]["value"]
        array([[ 1,  3,  6],
               [ 4,  9, 15]])
        """
        shape = x.shape
        _ = check_operation_axis(axis, shape, "x")

        operation = create_operation(self.cumulative_sum, locals())
        return Tensor(operation, shape=shape)

    @validated
    def transpose(
        self,
        a: Annotated[Union[np.ndarray, Tensor], pipe(shapeable)],
        perm: Optional[List[Annotated[int, pipe(ScalarT.INT())]]] = None,
        *,
        name: Optional[str] = None,
    ) -> Tensor:
        """
        Reorder the dimensions of a tensor.

        Parameters
        ----------
        a : np.ndarray or Tensor
            The tensor whose dimensions you want to permute, :math:`x`.
        perm : list[int] or None, optional
            The order of the input dimensions for the returned tensor. If you provide it, it must
            be a permutation of all integers between 0 and ``N-1``, where `N` is the rank of `a`.
            If you don't provide it, the order of the dimensions is inverted, that is to say,
            it defaults to ``[N-1, …, 1, 0]``.
        name : str or None, optional
            The name of the node.

        Returns
        -------
        Tensor
            The input tensor with its dimensions permuted. The `i`-th dimension of the
            returned tensor corresponds to the `perm[i]`-th input dimension.

        See Also
        --------
        Graph.adjoint : Hermitian adjoint of an operator.
        Graph.einsum : Tensor contraction via Einstein summation convention.
        """

        if perm is None:
            shape = a.shape[::-1]
        else:
            # This check converts negative axes into the range [0, len(a.shape)]:
            axes = check_operation_axis(perm, a.shape, "a")

            # This check makes sure all axes in the range [0, len(a.shape)] were used:
            Checker.VALUE(
                set(axes) == set(range(len(a.shape))),
                "The value of perm must be a valid permutation of the indices of a.",
                {"perm": perm, "missing indices": set(range(len(a.shape))) - set(axes)},
            )

            shape = tuple(a.shape[dimension] for dimension in axes)

        operation = create_operation(self.transpose, locals())
        return Tensor(operation, shape=shape)

    @validated
    def pauli_matrix(
        self,
        label: Literal["I", "X", "Y", "Z", "M", "P"],
        *,
        name: Optional[str] = None,
    ) -> Tensor:
        r"""
        Create a Pauli matrix from a label.

        Parameters
        ----------
        label : str
            The string that indicates which Pauli matrix to create.
            Must be ``'I'``, ``'X'``, ``'Y'``, ``'Z'``, ``'M'``, or ``'P'``. ``'M'`` creates
            the lowering matrix :math:`\sigma_- = \frac{1}{2}(\sigma_x + i\sigma_y)`. ``'P'``
            creates the raising matrix :math:`\sigma_+ = \frac{1}{2}(\sigma_x - i\sigma_y)`.
            We use the convention :math:`|\downarrow\rangle = \begin{bmatrix}1\\0\end{bmatrix}`
            and :math:`|\uparrow\rangle = \begin{bmatrix}0\\1\end{bmatrix}`.
        name : str or None, optional
            The name of the node.

        Returns
        -------
        Tensor
            The Pauli matrix.

        See Also
        --------
        Graph.pauli_kronecker_product : Embed Pauli matrices into a larger Hilbert space.

        Examples
        --------
        Create the Pauli X matrix.

        >>> graph.pauli_matrix("X", name="sigma_x")
        <Tensor: name="sigma_x", operation_name="pauli_matrix", shape=(2, 2)>
        >>> result = bo.execute_graph(graph=graph, output_node_names="sigma_x")
        >>> result["output"]["sigma_x"]["value"]
        array([[0.+0.j, 1.+0.j],
               [1.+0.j, 0.+0.j]])
        """
        operation = create_operation(self.pauli_matrix, locals())
        return Tensor(operation, shape=(2, 2))

    @validated
    def pauli_kronecker_product(
        self,
        labels: Annotated[
            List[
                Tuple[
                    Literal["I", "X", "Y", "Z", "M", "P"],
                    Annotated[int, pipe(ScalarT.INT().ge(0))],
                ]
            ],
            Field(min_length=1),
        ],
        subsystem_count: Annotated[int, pipe(ScalarT.INT().gt(0))],
        *,
        name: Optional[str] = None,
    ) -> Tensor:
        r"""
        Place Pauli matrices into their two-dimensional subsystems of a system and
        returns the Kronecker product.

        Parameters
        ----------
        labels : list[tuple[str, int]]
            A list of tuples, each containing a pair of labels for the Pauli matrix and its
            position.  The Pauli matrix label is a string ``'I'``, ``'X'``, ``'Y'``, ``'Z'``,
            ``'M'``, or ``'P'`` and the position label is a non-negative integer and smaller
            than `system_count` indicating the position of the Pauli matrix in the system. At
            least one tuple must be provided.  ``'M'`` creates the lowering matrix
            :math:`\sigma_- = \frac{1}{2}(\sigma_x + i\sigma_y)`.  ``'P'`` creates the raising
            matrix :math:`\sigma_+ = \frac{1}{2}(\sigma_x - i\sigma_y)`.
            We use the convention :math:`|\downarrow\rangle = \begin{bmatrix}1\\0\end{bmatrix}`
            and :math:`|\uparrow\rangle = \begin{bmatrix}0\\1\end{bmatrix}`.
        subsystem_count : int
            The number of two-level subsystems that constitute the system. Must be a positive
            number.
        name : str or None, optional
            The name of the node.

        Returns
        -------
        Tensor
            The Kronecker product of Pauli matrices.

        See Also
        --------
        Graph.embed_operators : Embed operators into a larger Hilbert space.
        Graph.kron : Kronecker product between two objects.
        Graph.kronecker_product_list : Kronecker product of a list of operators.

        Examples
        --------
        Place a single Pauli :math:`X` matrix in the second of two subsystems to create :math:`IX`.

        >>> graph.pauli_kronecker_product([("X", 1)], subsystem_count=2, name="IX")
        <Tensor: name="IX", operation_name="pauli_kronecker_product", shape=(4, 4)>
        >>> result = bo.execute_graph(graph=graph, output_node_names="IX")
        >>> result["output"]["IX"]["value"]
        array([[0.+0.j, 1.+0.j, 0.+0.j, 0.+0.j],
               [1.+0.j, 0.+0.j, 0.+0.j, 0.+0.j],
               [0.+0.j, 0.+0.j, 0.+0.j, 1.+0.j],
               [0.+0.j, 0.+0.j, 1.+0.j, 0.+0.j]])

        Place a single Pauli :math:`X` matrix in the second of three subsystems to create
        :math:`IXI`.

        >>> graph.pauli_kronecker_product([("X", 1)], subsystem_count=3, name="IXI")
        <Tensor: name="IXI", operation_name="pauli_kronecker_product", shape=(8, 8)>
        >>> result = bo.execute_graph(graph=graph, output_node_names="IXI")
        >>> result["output"]["IXI"]["value"]
        array([[0.+0.j, 0.+0.j, 1.+0.j, 0.+0.j, 0.+0.j, 0.+0.j, 0.+0.j, 0.+0.j],
               [0.+0.j, 0.+0.j, 0.+0.j, 1.+0.j, 0.+0.j, 0.+0.j, 0.+0.j, 0.+0.j],
               ...
               [0.+0.j, 0.+0.j, 0.+0.j, 0.+0.j, 0.+0.j, 1.+0.j, 0.+0.j, 0.+0.j]])

        Place two Pauli :math:`X` matrices in the second and third of three subsystems
        to create :math:`IXX`.

        >>> graph.pauli_kronecker_product([("X", 1), ("X", 2)], subsystem_count=3, name="IXX")
        <Tensor: name="IXX", operation_name="pauli_kronecker_product", shape=(8, 8)>
        >>> result = bo.execute_graph(graph=graph, output_node_names="IXX")
        >>> result["output"]["IXX"]["value"]
        array([[0.+0.j, 0.+0.j, 0.+0.j, 1.+0.j, 0.+0.j, 0.+0.j, 0.+0.j, 0.+0.j],
               [0.+0.j, 0.+0.j, 1.+0.j, 0.+0.j, 0.+0.j, 0.+0.j, 0.+0.j, 0.+0.j],
               ...
               [0.+0.j, 0.+0.j, 0.+0.j, 0.+0.j, 1.+0.j, 0.+0.j, 0.+0.j, 0.+0.j]])
        """
        positions = [label[1] for label in labels]

        Checker.VALUE(
            np.all(np.array(positions) < subsystem_count),
            "All positions must be smaller than `subsystem_count`.",
            {"positions": positions, "subsystem_count": subsystem_count},
        )
        Checker.VALUE(
            len(set(positions)) == len(positions), "All positions must be unique."
        )

        dimension = 2**subsystem_count
        operation = create_operation(self.pauli_kronecker_product, locals())
        return Tensor(operation, shape=(dimension, dimension))

    @validated
    def einsum(
        self,
        equation: str,
        tensors: List[Annotated[Union[np.ndarray, Tensor], pipe(shapeable)]],
        *,
        name: Optional[str] = None,
    ) -> Tensor:
        r"""
        Perform tensor contraction via Einstein summation convention.

        Use this node to perform multi-dimensional, linear algebraic array operations between
        tensors.

        Parameters
        ----------
        equation : str
            The equation describing the tensor contraction.
            The format is the same as in NumPy's einsum.
        tensors : list[np.ndarray or Tensor]
            The tensors to be contracted. Their rank must be not greater than six.
        name : str or None, optional
            The name of the node.

        Returns
        -------
        Tensor
            The contracted Tensor.

        See Also
        --------
        Graph.matmul : Matrix multiplication between objects.
        Graph.sum : Sum elements in a tensor along one or multiple axes.
        Graph.trace : Trace of an object.
        Graph.transpose : Reorder the dimensions of a tensor.

        Notes
        -----
        You can use tensor contraction with Einstein summation convention to create a new
        tensor from its element-wise computation from other tensors. This applies to any
        tensor operation that you can write as an equation relating the elements of the
        result as sums over products of elements of the inputs.

        The element-wise equation of the operation is summarized by a string describing
        the Einstein summation to be performed on the inputs. For example, the matrix
        multiplication between two matrices can be written as

        .. math::
            R_{ik} = \sum_j P_{ij} Q_{jk} .

        To convert this element-wise equation to the appropriate string, you can:
        remove summations and variable names (`ik = ij * jk`),
        move the output to the right (`ij * jk = ik`), and
        replace "`*`" with "`,`" and "`=`" with "`->`" (`ij,jk->ik`).
        You can also use an ellipsis (...) to broadcast over unchanged dimensions.

        For more information about Einstein summation, see `Einstein notation`_ on Wikipedia.

        .. _Einstein notation:
            https://en.wikipedia.org/wiki/Einstein_notation

        Examples
        --------
        >>> x = np.arange(16, dtype=float)

        Diagonal of a matrix.

        >>> graph.einsum("ii->i", [x.reshape(4, 4)], name="diagonal")
        <Tensor: name="diagonal", operation_name="einsum", shape=(4,)>
        >>> result = bo.execute_graph(graph=graph, output_node_names="diagonal")
        >>> result["output"]["diagonal"]["value"]
        array([0., 5., 10., 15.])

        Trace of a matrix.

        >>> graph.einsum('ii->', [x.reshape(4, 4)], name="trace")
        <Tensor: name="trace", operation_name="einsum", shape=()>
        >>> result = bo.execute_graph(graph=graph, output_node_names="trace")
        >>> result["output"]["trace"]["value"]
        30.0

        Sum over matrix axis.

        >>> graph.einsum('ij->i', [x.reshape((4, 4))], name="sum_1")
        <Tensor: name="sum_1", operation_name="einsum", shape=(4,)>
        >>> result = bo.execute_graph(graph=graph, output_node_names="sum_1")
        >>> result["output"]["sum_1"]["value"]
        array([ 6., 22., 38., 54.])

        Sum over tensor axis ignoring leading dimensions.

        >>> graph.einsum('...ji->...i', [x.reshape((2, 2, 4))], name='sum_2')
        <Tensor: name="sum_2", operation_name="einsum", shape=(2, 4)>
        >>> result = bo.execute_graph(graph=graph, output_node_names="sum_2")
        >>> result["output"]["sum_2"]["value"]
        array([[ 4.,  6.,  8., 10.],
               [20., 22., 24., 26.]])

        Reorder tensor axes.

        >>> graph.einsum('ijk->jki', [x.reshape((8, 1, 2))], name="reorder")
        <Tensor: name="reorder", operation_name="einsum", shape=(1, 2, 8)>
        >>> result = bo.execute_graph(graph=graph, output_node_names="reorder")
        >>> result["output"]["reorder"]["value"]
        array([[[ 0.,  2.,  4.,  6.,  8., 10., 12., 14.],
                [ 1.,  3.,  5.,  7.,  9., 11., 13., 15.]]])

        Vector inner product.

        >>> graph.einsum('i,i->', [x, np.ones(16)], name="inner")
        <Tensor: name="inner", operation_name="einsum", shape=()>
        >>> result = bo.execute_graph(graph=graph, output_node_names="inner")
        >>> result["output"]["inner"]["value"]
        120.0

        Matrix-vector multiplication.

        >>> graph.einsum('ij,j->i', [x.reshape((4, 4)), np.ones(4)], name="multiplication")
        <Tensor: name="multiplication", operation_name="einsum", shape=(4,)>
        >>> result = bo.execute_graph(graph=graph, output_node_names="multiplication")
        >>> result["output"]["multiplication"]["value"]
        array([ 6., 22., 38., 54.])

        Vector outer product.

        >>> graph.einsum("i,j->ij", [x[:2], x[:3]], name="outer")
        <Tensor: name="outer", operation_name="einsum", shape=(2, 3)>
        >>> result = bo.execute_graph(graph=graph, output_node_names="outer")
        >>> result["output"]["outer"]["value"]
        array([[0., 0., 0.],
               [0., 1., 2.]])

        Tensor contraction.

        >>> graph.einsum(
        ...     "ijk,jil->kl", [x.reshape((4, 2, 2)), x.reshape((2, 4, 2))], name="contraction"
        ... )
        <Tensor: name="contraction", operation_name="einsum", shape=(2, 2)>
        >>> result = bo.execute_graph(graph=graph, output_node_names="contraction")
        >>> result["output"]["contraction"]["value"]
        array([[504., 560.],
               [560., 624.]])

        Trace along first two axes.

        >>> graph.einsum("ii...->i...", [x.reshape((2, 2, 4))], name="trace_2")
        <Tensor: name="trace_2", operation_name="einsum", shape=(2, 4)>
        >>> result = bo.execute_graph(graph=graph, output_node_names="trace_2")
        >>> result["output"]["trace_2"]["value"]
        array([[ 0.,  1.,  2.,  3.],
               [12., 13., 14., 15.]])

        Matrix multiplication using the left-most indices.

        >>> graph.einsum(
        ...     "ij...,jk...->ik...", [x.reshape((1, 4, 4)), x.reshape((4, 1, 4))], name="left_most"
        ... )
        <Tensor: name="left_most", operation_name="einsum", shape=(1, 1, 4)>
        >>> result = bo.execute_graph(graph=graph, output_node_names="left_most")
        >>> result["output"]["left_most"]["value"]
        array([[[224., 276., 336., 404.]]])
        """

        try:
            shape = np.einsum(
                equation, *[np.zeros(tensor.shape) for tensor in tensors]
            ).shape
        except ValueError as exc:
            raise ValueError(
                "The equation is not valid or is incompatible with the inputs."
            ) from exc

        Checker.VALUE(
            all(len(tensor.shape) <= 6 for tensor in tensors),
            "Tensors with rank greater than six are not supported.",
        )
        operation = create_operation(self.einsum, locals())
        return Tensor(operation, shape=shape)

    @validated
    def expectation_value(
        self,
        state: Annotated[
            Union[np.ndarray, Tensor], pipe(shapeable, after=ShapeT.VECTOR())
        ],
        operator: Annotated[
            Union[np.ndarray, Tensor], pipe(shapeable, after=ShapeT.OPERATOR())
        ],
        *,
        name: Optional[str] = None,
    ) -> Tensor:
        r"""
        Calculate the expectation value of an operator with respect to a state.

        The last dimension of the state must be equal to the last two dimensions
        of the operator and their batch shapes must be broadcastable.

        Parameters
        ----------
        state : np.ndarray or Tensor
            The state. It must be a vector of shape ``(..., D)``.
        operator : np.ndarray or Tensor
            The operator. It must be of shape ``(..., D, D)``.
        name : str or None, optional
            The name of the node.

        Returns
        -------
        Tensor
            The expectation value with shape ``(...)``.

        See Also
        --------
        Graph.density_matrix_expectation_value :
            Expectation value of an operator with respect to a density matrix.
        Graph.inner_product : Inner product of two vectors.
        Graph.outer_product : Outer product of two vectors.
        Graph.trace : Trace of an object.

        Notes
        -----
        The expectation value of an operator :math:`\mathbf{A}` with respect to
        a vector :math:`\mathbf{x}` is defined as

        .. math::
            \mathbf{x}^\dagger \mathbf{A} \mathbf{x} = \langle x \vert \mathbf{A} \vert x \rangle
            = \sum_{ij} x^\ast_{i} A_{ij} x_{j} .

        For more information about the expectation value, see `expectation value`_ on Wikipedia.

        .. _expectation value:
            https://en.wikipedia.org/wiki/Expectation_value_(quantum_mechanics)

        Examples
        --------
        >>> graph.expectation_value(np.array([1j, 1j]), np.eye(2), name="expectation")
        <Tensor: name="expectation", operation_name="expectation_value", shape=()>
        >>> result = bo.execute_graph(graph=graph, output_node_names="expectation")
        >>> result["output"]["expectation"]["value"]
        2.+0.j
        >>> graph.expectation_value(np.ones([3,1,4]), np.ones([2,4,4]), name="expectation)
        <Tensor: name="expectation", operation_name="expectation_value", shape=(3, 2)>
        >>> result = bo.execute_graph(graph=graph, output_node_names="expectation")
        >>> result["output"]["expectation"]["value"]
        array([[16, 16], [16, 16], [16, 16]])
        """

        Checker.VALUE(
            state.shape[-1] == operator.shape[-1],
            "State and operator shapes must have the same size in their last axis.",
            {
                "value shape of state": state.shape[-1:],
                "value shape of operator": operator.shape[-2:],
            },
        )

        shape = get_broadcasted_shape(
            state.shape[:-1],
            operator.shape[:-2],
            message="The batch shapes of state and operator must be broadcastable.",
        )

        operation = create_operation(self.expectation_value, locals())
        return Tensor(operation, shape=shape)

    @validated
    def density_matrix_expectation_value(
        self,
        density_matrix: Annotated[
            Union[np.ndarray, Tensor], pipe(shapeable, after=ShapeT.OPERATOR())
        ],
        operator: Annotated[
            Union[np.ndarray, Tensor], pipe(shapeable, after=ShapeT.OPERATOR())
        ],
        *,
        name: Optional[str] = None,
    ) -> Tensor:
        r"""
        Calculate the expectation value of an operator with respect to a density matrix.

        The last two dimensions of the density matrix must be equal to the last two dimensions
        of the operator and their batch shapes must be broadcastable.

        Parameters
        ----------
        density_matrix : np.ndarray or Tensor
            The density matrix. It must be of shape ``(..., D, D)``.
        operator : np.ndarray or Tensor
            The operator. It must be of shape ``(..., D, D)``.
        name : str or None, optional
            The name of the node.

        Returns
        -------
        Tensor
            The expectation value with shape ``(...)``.

        See Also
        --------
        Graph.expectation_value : Expectation value of an operator with respect to a pure state.
        Graph.inner_product : Inner product of two vectors.
        Graph.outer_product : Outer product of two vectors.
        Graph.trace : Trace of an object.

        Notes
        -----
        The expectation value of an operator :math:`\mathbf{A}` with respect to
        a density matrix :math:`\rho=\sum_i p_i |\psi_i\rangle\langle\psi_i|` is defined as

        .. math::
            {\mathrm{Tr}}(A\rho) = {\mathrm{Tr}}(A\sum_i p_i |\psi_i\rangle\langle\psi_i|)
            = \sum_i p_i \langle\psi_i|A|\psi_i\rangle .

        For more information about the density matrix expectation value, see
        `density matrix`_ on Wikipedia.

        .. _density matrix:
            https://en.wikipedia.org/wiki/Density_matrix

        Examples
        --------
        >>> graph.density_matrix_expectation_value(
        ...     np.array([[0.9, 0.], [0., 0.1]]), np.array([[1., 0.], [0., -1.]]),
        ...     name="expectation",
        ... )
        <Tensor: name="expectation", operation_name="density_matrix_expectation_value", shape=()>
        >>> result = bo.execute_graph(graph=graph, output_node_names="expectation")
        >>> result["output"]["expectation"]["value"]
        0.8
        >>> graph.density_matrix_expectation_value(
        ...     np.array([[0.9, 0.], [0., 0.1]]),
        ...     np.array([[[0., 1.], [1., 0.]], [[0., -1.j], [1.j, 0.]], [[1., 0.], [0., -1.]]]),
        ...     name="expectation2"
        ... )
        <Tensor: name="expectation2", operation_name="expectation_value", shape=(3,)>
        >>> result = bo.execute_graph(graph=graph, output_node_names="expectation2")
        >>> result["output"]["expectation2"]["value"]
        array([0. +0.j, 0. +0.j, 0.8+0.j])
        """

        Checker.VALUE(
            density_matrix.shape[-1] == operator.shape[-1],
            "Density matrix and operator shapes must have the same size in their last axis.",
            {
                "value shape of density matrix": density_matrix.shape[-2:],
                "value shape of operator": operator.shape[-2:],
            },
        )

        shape = get_broadcasted_shape(
            density_matrix.shape[:-2],
            operator.shape[:-2],
            message="The batch shapes of density matrix and operator must be broadcastable.",
        )

        operation = create_operation(self.density_matrix_expectation_value, locals())
        return Tensor(operation, shape=shape)

    @validated
    def inner_product(
        self,
        x: Annotated[Union[np.ndarray, Tensor], pipe(shapeable, after=ShapeT.VECTOR())],
        y: Annotated[Union[np.ndarray, Tensor], pipe(shapeable, after=ShapeT.VECTOR())],
        *,
        name: Optional[str] = None,
    ) -> Tensor:
        r"""
        Calculate the inner product of two vectors.

        The vectors must have the same last dimension and broadcastable shapes.

        Parameters
        ----------
        x : np.ndarray or Tensor
            The left multiplicand. It must be a vector of shape ``(..., D)``.
        y : np.ndarray or Tensor
            The right multiplicand. It must be a vector of shape ``(..., D)``.
        name : str or None, optional
            The name of the node.

        Returns
        -------
        Tensor
            The inner product of two vectors of shape ``(...)``.

        See Also
        --------
        Graph.density_matrix_expectation_value :
            Expectation value of an operator with respect to a density matrix.
        Graph.einsum : Tensor contraction via Einstein summation convention.
        Graph.expectation_value : Expectation value of an operator with respect to a pure state.
        Graph.outer_product : Outer product of two vectors.
        Graph.trace : Trace of an object.

        Notes
        -----
        The inner product or dot product of two complex vectors :math:`\mathbf{x}`
        and :math:`\mathbf{y}` is defined as

        .. math::
            \langle \mathbf{x} \vert \mathbf{y} \rangle = \sum_i x^\ast_{i} y_{i} .

        For more information about the inner product, see `dot product`_ on Wikipedia.

        .. _dot product:
            https://en.wikipedia.org/wiki/Dot_product

        Examples
        --------
        >>> graph.inner_product(np.array([1j, 1j]), np.array([1j, 1j]), name="inner")
        <Tensor: name="inner", operation_name="inner_product", shape=()>
        >>> result = bo.execute_graph(graph=graph, output_node_names="inner")
        >>> result["output"]["inner"]["value"]
        2.+0.j

        >>> graph.inner_product(np.ones((3,1,4), np.ones(2,4), name="inner2")
        <Tensor: name="inner2", operation_name="inner_product", shape=(3, 2)>
        >>> result = bo.execute_graph(graph=graph, output_node_names="inner2")
        >>> result["output"]["inner2"]["value"]
        array([[4, 4], [4, 4], [4, 4]])
        """

        Checker.VALUE(
            x.shape[-1] == y.shape[-1],
            "The vectors must be of same length in their last dimension.",
            {"x.shape": y.shape, "y.shape": x.shape},
        )

        shape = get_broadcasted_shape(
            x.shape[:-1],
            y.shape[:-1],
            message="The batch shapes of x and y must be broadcastable.",
        )

        operation = create_operation(self.inner_product, locals())
        return Tensor(operation, shape=shape)

    @validated
    def outer_product(
        self,
        x: Annotated[Union[np.ndarray, Tensor], pipe(shapeable, after=ShapeT.VECTOR())],
        y: Annotated[Union[np.ndarray, Tensor], pipe(shapeable, after=ShapeT.VECTOR())],
        *,
        name: Optional[str] = None,
    ) -> Tensor:
        r"""
        Calculate the outer product of two vectors.

        The vectors can have different last dimensions but must have broadcastable batch dimensions.

        Parameters
        ----------
        x : np.ndarray or Tensor
            The left multiplicand. It must be a vector of shape ``(..., M)``.
        y : np.ndarray or Tensor
            The right multiplicand. It must be a vector of shape ``(..., N)``.
        name : str or None, optional
            The name of the node.

        Returns
        -------
        Tensor
            The outer product of two vectors of shape ``(..., M, N)``.

        See Also
        --------
        Graph.density_matrix_expectation_value :
            Expectation value of an operator with respect to a density matrix.
        Graph.expectation_value : Expectation value of an operator with respect to a pure state.
        Graph.inner_product : Inner product of two vectors.
        Graph.trace : Trace of an object.

        Notes
        -----
        The outer product of two complex vectors :math:`\mathbf{x}`
        and :math:`\mathbf{y}` is defined as

        .. math::
            (\mathbf{x} \otimes \mathbf{y})_{ij} = x_{i} y^\ast_{j}.

        For more information about the outer product, see `outer product`_ on Wikipedia.

        .. _outer product:
            https://en.wikipedia.org/wiki/Outer_product

        Examples
        --------
        >>> graph.outer_product(np.array([1j, 1j]), np.array([1j, -1j]), name="outer")
        <Tensor: name="outer", operation_name="outer_product", shape=(2, 2)>
        >>> result = bo.execute_graph(graph=graph, output_node_names="outer")
        >>> result["output"]["outer"]["value"]
        array([[1.+0.j, -1.+0.j], [1.+0.j, -1.+0.j]])

        >>> graph.outer_product(np.ones((3,1,2), np.ones(2,2), name="outer2")
        <Tensor: name="outer2", operation_name="outer_product", shape=(3, 2, 2, 2)>
        >>> result = bo.execute_graph(graph=graph, output_node_names="outer2")
        >>> result["output"]["outer2"]["value"]
        array([[[[1, 1], [1, 1]], [[1, 1], [1, 1]]],
            [[[1, 1], [1, 1]], [[1, 1], [1, 1]]],
            [[[1, 1], [1, 1]], [[1, 1], [1, 1]]])
        """

        batch_shape = get_broadcasted_shape(
            x.shape[:-1],
            y.shape[:-1],
            message="The batch shapes of x and y must be broadcastable.",
        )
        shape = batch_shape + (x.shape[-1], y.shape[-1])

        operation = create_operation(self.outer_product, locals())
        return Tensor(operation, shape=shape)

    @validated
    def partial_trace(
        self,
        density_matrix: Annotated[
            Union[np.ndarray, Tensor], pipe(shapeable, after=ShapeT.OPERATOR())
        ],
        subsystem_dimensions: Annotated[
            List[Annotated[int, pipe(ScalarT.INT().gt(0))]], Field(min_length=1)
        ],
        traced_subsystems: Union[
            Annotated[
                List[Annotated[int, pipe(ScalarT.INT().ge(0))]], Field(min_length=1)
            ],
            Annotated[int, pipe(ScalarT.INT().ge(0))],
        ],
        *,
        name: Optional[str] = None,
    ) -> Tensor:
        r"""
        Calculate the partial trace of a density matrix.

        Parameters
        ----------
        density_matrix : np.ndarray or Tensor
            The density matrix :math:`\rho` of the system to be reduced.
            Can be a single square matrix or a batch of matrices
            with dimension ``(..., D, D)``.
        subsystem_dimensions : list[int]
            The dimension of each subsystem. The product of the subsystem
            dimensions is the dimension of the system ``D``.
        traced_subsystems : int or list[int]
            The indices (starting from zero) of the subsystems to be traced out.
            Each index refers to a different subsystem.
        name : str or None, optional
            The name of the node.

        Returns
        -------
        Tensor
            The reduced density matrix of shape ``(..., d, d)``. The reduced
            dimension ``d`` is equal to the system dimension ``D`` divided by the
            product of the traced out subsystem dimensions.

        Notes
        -----
        Given a density matrix :math:`\rho` of two subsystems :math:`A`
        and :math:`B`, the partial trace over subsystem :math:`B` is defined as

        .. math::
            ({\mathrm{Tr}_{B}} \rho)_{ij} = \sum_k \rho_{ik,jk}.

        For more information about the partial trace, see `partial trace`_ on Wikipedia.

        .. _partial trace:
            https://en.wikipedia.org/wiki/Partial_trace

        Examples
        --------
        >>> graph.partial_trace(np.diag([1, 0, 0, 0]), [2, 2], 1, name="partial")
        <Tensor: name="partial", operation_name="partial_trace", shape=(2, 2)>
        >>> result = bo.execute_graph(graph=graph, output_node_names="partial")
        >>> result["output"]["partial"]["value"]
        array([[[1, 0], [0, 0]])

        >>> graph.partial_trace(np.eye(10)/10, [2, 5], 1, name="partial2")
        <Tensor: name="partial2", operation_name="partial_trace", shape=(2, 2)>
        >>> result = bo.execute_graph(graph=graph, output_node_names="partial2")
        >>> result["output"]["partial2"]["value"]
        array([[[0.5, 0], [0, 0.5]])

        See more examples in the `How to simulate large open system dynamics
        <https://docs.q-ctrl.com/boulder-opal/user-guides/how-to-simulate-large-open-
        system-dynamics>`_ user guide.
        """

        Checker.VALUE(
            np.prod(subsystem_dimensions) == density_matrix.shape[-1],
            "The product of the subsystem_dimensions must be equal to the last "
            "density_matrix dimension.",
        )

        if not isinstance(traced_subsystems, list):
            traced_subsystems = [traced_subsystems]

        Checker.VALUE(
            np.all(np.array(traced_subsystems) < len(subsystem_dimensions)),
            "The traced_subsystems must be indices within the range "
            "of the number of subsystems.",
        )
        Checker.VALUE(
            len(set(traced_subsystems)) == len(traced_subsystems),
            "The traced_subsystems must not have duplicate values.",
        )

        reduced_matrix_dimension = density_matrix.shape[-1] // np.prod(
            [subsystem_dimensions[i] for i in traced_subsystems], dtype=int
        )
        shape = density_matrix.shape[:-2] + (
            reduced_matrix_dimension,
            reduced_matrix_dimension,
        )

        operation = create_operation(self.partial_trace, locals())
        return Tensor(operation, shape=shape)

    @validated
    def reshape(
        self,
        tensor: Annotated[Union[np.ndarray, Tensor], pipe(shapeable)],
        shape: Tuple[Annotated[int, pipe(ScalarT.INT().ge(-1).ne(0))], ...],
        *,
        name: Optional[str] = None,
    ) -> Tensor:
        """
        Reshape a tensor into a new shape, keeping the order of its elements.

        Parameters
        ----------
        tensor : np.ndarray or Tensor
            The tensor you want to reshape.
        shape : tuple[int, ...]
            The new shape of the tensor.
            One and only one of the dimensions can be set to -1.
            In that case, the method will automatically calculate that dimension's size by
            keeping the total size constant.
        name : str or None, optional
            The name of the node.

        Returns
        -------
        Tensor
            The reshaped tensor.

        Examples
        --------
        >>> graph.reshape(tensor=np.ones((4, 4)), shape=(2, 8), name='reshape')
        <Tensor: name="reshape", operation_name="reshape", shape=(2, 8)>

        >>> graph.reshape(tensor=np.ones((4, 4)), shape=(2, -1), name='reshape_1')
        <Tensor: name="reshape_1", operation_name="reshape", shape=(2, 8)>

        >>> graph.reshape(tensor=np.ones((4, 4)), shape=(2, -1, 2), name='reshape_2')
        <Tensor: name="reshape_2", operation_name="reshape", shape=(2, 4, 2)>

        >>> graph.reshape(tensor=np.ones((2, 2)), shape=(-1,), name='reshape_3')
        <Tensor: name="reshape_3", operation_name="reshape", shape=(4,)>
        """
        tensor_element_count = np.prod(tensor.shape)
        shape_element_count = np.prod(shape)

        missing_dimensions = np.nonzero(np.asarray(shape) == -1)[0]
        if len(missing_dimensions) > 0:
            Checker.VALUE(
                len(missing_dimensions) == 1,
                "You can only specify one axis with -1 in the new shape.",
                {"shape": shape},
            )

            _dim = missing_dimensions[0]
            missing_value = (-1) * tensor_element_count / shape_element_count

            Checker.VALUE(
                int(missing_value) == missing_value,
                "Unable to allocate a whole number of elements for the unspecified axis (-1).",
                {"tensor.shape": tensor.shape, "shape": shape},
            )
            shape_new = shape[:_dim] + (int(missing_value),) + shape[_dim + 1 :]
        else:
            Checker.VALUE(
                tensor_element_count == shape_element_count,
                "New shape must have the same number of elements as the input tensor.",
                {"tensor.shape": tensor.shape, "shape": shape},
            )
            shape_new = shape

        operation = create_operation(self.reshape, locals())
        return Tensor(operation, shape=shape_new)

    @validated
    def density_matrix_infidelity(
        self,
        x: Annotated[
            Union[np.ndarray, Tensor], pipe(shapeable, after=ShapeT.OPERATOR())
        ],
        y: Annotated[
            Union[np.ndarray, Tensor], pipe(shapeable, after=ShapeT.OPERATOR())
        ],
        *,
        name: Optional[str] = None,
    ) -> Tensor:
        r"""
        Calculate the infidelity between two states represented by density matrices.

        Parameters
        ----------
        x : np.ndarray or Tensor
            The density matrix :math:`x` with shape ``(..., D, D)``.
            The last two dimensions must have the same size for both
            matrices, and its batch dimensions must be broadcastable.
        y : np.ndarray or Tensor
            The density matrix :math:`y` with shape ``(..., D, D)``.
            The last two dimensions must have the same size for both
            matrices, and its batch dimensions must be broadcastable.
        name : str or None, optional
            The name of the node.

        Returns
        -------
        Tensor
            The state infidelity of the density matrices with respect to each
            other. Its shape is the broadcasted value of the batch shapes of
            the two input parameters.

        Warnings
        --------
        This function assumes that the parameters are density matrices and
        therefore are positive definite. Passing matrices that have negative
        or complex eigenvalues will result in wrong values for the infidelity.

        See Also
        --------
        Graph.infidelity_pwc : Total infidelity of a system with a piecewise-constant Hamiltonian.
        Graph.infidelity_stf : Total infidelity of a system with a sampleable Hamiltonian.
        Graph.state_infidelity : Infidelity between two quantum states.
        Graph.unitary_infidelity : Infidelity between a unitary and target operators.

        Notes
        -----
        The general formula for the infidelity of two density matrices is

        .. math::
            I = 1 - \left[ \mathrm{Tr}\left( \sqrt{\sqrt{x} y \sqrt{x}} \right) \right]^2

        Examples
        --------
        >>> infidelity = graph.density_matrix_infidelity(
        ...     np.array([[0.5, 0], [0, 0.5]]),
        ...     np.array([[1, 0], [0, 0]]),
        ...     name="infidelity",
        ... )
        >>> result = bo.execute_graph(graph=graph, output_node_names="infidelity")
        >>> result["output"]["infidelity"]["value"]
        0.5
        """

        Checker.VALUE(
            x.shape[-2:] == y.shape[-2:],
            "The last two dimensions of the x and y must be the same.",
            {"x.shape": x.shape, "y.shape": y.shape},
        )

        broadcasted_shape = get_broadcasted_shape(
            x.shape[:-2],
            y.shape[:-2],
            message="The batch shapes of x and y must be broadcastable.",
        )

        operation = create_operation(self.density_matrix_infidelity, locals())
        return Tensor(operation, shape=broadcasted_shape)

    @validated
    def unitary_infidelity(
        self,
        unitary_operator: Annotated[
            Union[np.ndarray, Tensor], pipe(shapeable, after=ShapeT.OPERATOR())
        ],
        target: Annotated[
            Union[np.ndarray, Tensor], pipe(shapeable, after=ShapeT.OPERATOR())
        ],
        *,
        name: Optional[str] = None,
    ) -> Tensor:
        r"""
        Calculate the infidelity between a target operation and the actual implemented unitary.

        Both operators must be square and have shapes broadcastable to each other.

        Parameters
        ----------
        unitary_operator : np.ndarray or Tensor
            The actual unitary operator, :math:`U`, with shape ``(..., D, D)``.
            Its last two dimensions must be equal and the same as `target`, and its batch
            dimensions, if any, must be broadcastable with `target`.
        target : np.ndarray or Tensor
            The target operation with respect to which the infidelity will be calculated,
            :math:`V`, with shape ``(..., D, D)``.
            Its last two dimensions must be equal and the same as `unitary_operator`,
            and its batch dimensions, if any, must be broadcastable with `unitary_operator`.
        name : str or None, optional
            The name of the node.

        Returns
        -------
        Tensor
            The infidelity between the two operators, with shape ``(...)``.

        See Also
        --------
        Graph.density_matrix_infidelity : Infidelity between two density matrices.
        Graph.infidelity_pwc : Total infidelity of a system with a piecewise-constant Hamiltonian.
        Graph.infidelity_stf : Total infidelity of a system with a sampleable Hamiltonian.
        Graph.state_infidelity : Infidelity between two quantum states.

        Notes
        -----
        The operational infidelity between the actual unitary and target operators is defined as

        .. math::
          \mathcal{I} = 1 - \left|
              \frac{\mathrm{Tr} (V^\dagger U)}{\mathrm{Tr} (V^\dagger V)}
          \right|^2 .

        Examples
        --------
        Calculate the infidelity of a unitary with respect to a :math:`\sigma_x` gate.

        >>> theta = 0.5
        >>> sigma_x = np.array([[0, 1], [1, 0]])
        >>> unitary = np.array([[np.cos(theta), np.sin(theta)], [np.sin(theta), -np.cos(theta)]])
        >>> graph.unitary_infidelity(unitary_operator=unitary, target=sigma_x, name="infidelity")
        <Tensor: name="infidelity", operation_name="unitary_infidelity", shape=()>
        >>> result = bo.execute_graph(graph=graph, output_node_names="infidelity")
        >>> result["output"]["infidelity"]["value"]
        0.7701511529340699

        Calculate the time-dependent infidelity of the identity gate for a noiseless single qubit.

        >>> sigma_x = np.array([[0, 1], [1, 0]])
        >>> hamiltonian = sigma_x * graph.pwc_signal(
        ...     duration=1, values=np.pi * np.array([0.25, 1, 0.25])
        ... )
        >>> unitaries = graph.time_evolution_operators_pwc(
        ...     hamiltonian=hamiltonian, sample_times=np.linspace(0, 1, 10)
        ... )
        >>> graph.unitary_infidelity(
        ...     unitary_operator=unitaries, target=np.eye(2), name="infidelities"
        ... )
        <Tensor: name="infidelities", operation_name="unitary_infidelity", shape=(10,)>
        >>> result = bo.execute_graph(graph=graph, output_node_names="infidelities")
        >>> result["output"]["infidelities"]["value"]
        array([0.        , 0.00759612, 0.03015369, 0.0669873 , 0.32898993,
               0.67101007, 0.9330127 , 0.96984631, 0.99240388, 1.        ])
        """
        Checker.VALUE(
            unitary_operator.shape[-2:] == target.shape[-2:],
            "The last two dimensions of the unitary and target operators must be the same.",
            {
                "unitary_operator.shape": unitary_operator.shape,
                "target.shape": target.shape,
            },
        )

        shape = get_broadcasted_shape(
            unitary_operator.shape[:-2],
            target.shape[:-2],
            message="The batch shapes of unitary operator and target must be broadcastable.",
        )

        operation = create_operation(self.unitary_infidelity, locals())
        return Tensor(operation, shape=shape)

    @validated
    def state_infidelity(
        self,
        x: Annotated[Union[np.ndarray, Tensor], pipe(shapeable, after=ShapeT.VECTOR())],
        y: Annotated[Union[np.ndarray, Tensor], pipe(shapeable, after=ShapeT.VECTOR())],
        *,
        name: Optional[str] = None,
    ) -> Tensor:
        r"""
        Calculate the infidelity of two pure states.

        Parameters
        ----------
        x : np.ndarray or Tensor
            A pure state, :math:`|\psi\rangle`, with shape ``(..., D)``.
            Note that the last dimension must be the same as `y`, and the batch dimension,
            if any, must be broadcastable with `y`.
        y : np.ndarray or Tensor
            A pure state, :math:`|\phi\rangle`, with shape ``(..., D)``.
            Note that the last dimension must be the same as `x`, and the batch dimension,
            if any, must be broadcastable with `x`.
        name : str or None, optional
            The name of the node.

        Returns
        -------
        Tensor
            The infidelity of two pure states, with shape ``(...)``.

        See Also
        --------
        Graph.density_matrix_infidelity : Infidelity between two density matrices.
        Graph.inner_product : Inner product of two vectors.
        Graph.unitary_infidelity : Infidelity between a unitary and target operators.

        Notes
        -----
        The infidelity of two pure states :math:`|\psi\rangle` and :math:`|\phi\rangle`
        is defined as :math:`1 - \| \langle \psi | \phi \rangle \|^2`.

        For more information about the state fidelity, see `fidelity of quantum states`_
        on Wikipedia.

        .. _fidelity of quantum states:
            https://en.wikipedia.org/wiki/Fidelity_of_quantum_states

        Examples
        --------
        >>> graph.state_infidelity(
        ...     np.array([0, 1]), np.array([[1, 0], [0, 1]]), name="infidelity"
        ... )
        <Tensor: name="infidelity", operation_name="state_infidelity", shape=(2,)>
        >>> result = bo.execute_graph(graph=graph, output_node_names="infidelity")
        >>> result["output"]["infidelity"]["value"]
        array([1., 0.])
        """

        Checker.VALUE(
            x.shape[-1] == y.shape[-1],
            "The last dimension of x and y must be the same.",
            {"x.shape": x.shape, "y.shape": y.shape},
        )
        shape = get_broadcasted_shape(
            x.shape[:-1],
            y.shape[:-1],
            message="The batch shapes of x and y must be broadcastable.",
        )

        operation = create_operation(self.state_infidelity, locals())
        return Tensor(operation, shape=shape)

    @validated
    def embed_operators(
        self,
        operators: Annotated[
            Union[
                List[Tuple[Union[np.ndarray, Tensor], int]],
                Tuple[Union[np.ndarray, Tensor], int],
            ],
            pipe(_embed_validator),
        ],
        dimensions: List[Annotated[int, pipe(ScalarT.INT().gt(0))]],
        *,
        name: Optional[str] = None,
    ) -> Tensor:
        r"""
        Embed an operator or set of operators into a larger Hilbert space.

        Parameters
        ----------
        operators : list[tuple[np.ndarray or Tensor, int]] or tuple[np.ndarray or Tensor, int]
            A tuple or a list of tuples that contain pairs of the operators to be embedded and their
            corresponding positions in the full space.
            The positions must be non-negative integers less than the length of the dimensions list.
            The operators must be at least 2D and can contain leading batch dimensions.
            The dimension of the operators must match the value of the dimensions list
            at the given position.
        dimensions : list[int]
            The dimensions of each subspace.
        name : str or none, optional
            The name of the node.

        Returns
        -------
        Tensor
            The operators embedded into the full Hilbert space. The dimension of the Hilbert
            space of the output is equal to the product of the elements of the dimensions list.

        See Also
        --------
        Graph.kron : Kronecker product between two objects.
        Graph.kronecker_product_list : Kronecker product of a list of operators.
        Graph.pauli_kronecker_product : Embed Pauli matrices into a larger Hilbert space.

        Notes
        -----
        This function computes :math:`A_1 \otimes A_2 \otimes ...` where :math:`A_i`
        is either the operator passed for position :math:`i` (if given) or an identity matrix.
        The dimension of :math:`A_i` corresponds to the :math:`i`-th entry in the dimensions list.

        Examples
        --------
        Embed a single operator.

        >>> sigma_z = graph.pauli_matrix("Z")
        >>> graph.embed_operators((sigma_z, 0), [2, 3], name="Z0")
        <Tensor: name="Z0", operation_name="embed_operators", shape=(6, 6)>
        >>> result = bo.execute_graph(graph=graph, output_node_names="Z0")
        >>> result["output"]["Z0"]["value"]
        array([[ 1.+0.j,  0.+0.j,  0.+0.j,  0.+0.j,  0.+0.j,  0.+0.j],
               [ 0.+0.j,  1.+0.j,  0.+0.j,  0.+0.j,  0.+0.j,  0.+0.j],
               [ 0.+0.j,  0.+0.j,  1.+0.j,  0.+0.j,  0.+0.j,  0.+0.j],
               [ 0.+0.j,  0.+0.j,  0.+0.j, -1.+0.j,  0.+0.j,  0.+0.j],
               [ 0.+0.j,  0.+0.j,  0.+0.j,  0.+0.j, -1.+0.j,  0.+0.j],
               [ 0.+0.j,  0.+0.j,  0.+0.j,  0.+0.j,  0.+0.j, -1.+0.j]])

        Embed multiple operators.

        >>> number_op = graph.number_operator(2)
        >>> sigma_x = graph.pauli_matrix("X")
        >>> graph.embed_operators([(number_op, 0), (sigma_x, 2)], [2, 2, 2], name="N0X2")
        <Tensor: name="N0X2", operation_name="embed_operators", shape=(8, 8)>
        >>> result = bo.execute_graph(graph=graph, output_node_names="N0X2")
        >>> result["output"]["N0X2"]["value"]
        array([[0.+0.j, 0.+0.j, 0.+0.j, 0.+0.j, 0.+0.j, 0.+0.j, 0.+0.j, 0.+0.j],
               [0.+0.j, 0.+0.j, 0.+0.j, 0.+0.j, 0.+0.j, 0.+0.j, 0.+0.j, 0.+0.j],
               [0.+0.j, 0.+0.j, 0.+0.j, 0.+0.j, 0.+0.j, 0.+0.j, 0.+0.j, 0.+0.j],
               [0.+0.j, 0.+0.j, 0.+0.j, 0.+0.j, 0.+0.j, 0.+0.j, 0.+0.j, 0.+0.j],
               [0.+0.j, 0.+0.j, 0.+0.j, 0.+0.j, 0.+0.j, 1.+0.j, 0.+0.j, 0.+0.j],
               [0.+0.j, 0.+0.j, 0.+0.j, 0.+0.j, 1.+0.j, 0.+0.j, 0.+0.j, 0.+0.j],
               [0.+0.j, 0.+0.j, 0.+0.j, 0.+0.j, 0.+0.j, 0.+0.j, 0.+0.j, 1.+0.j],
               [0.+0.j, 0.+0.j, 0.+0.j, 0.+0.j, 0.+0.j, 0.+0.j, 1.+0.j, 0.+0.j]])
        """

        _operators = [operators] if isinstance(operators, tuple) else operators
        for index, (operator, position) in enumerate(_operators):
            Checker.VALUE(
                position < len(dimensions),
                "The position must be less than the length of the dimensions list.",
                {
                    f"operators[{index}][1]": position,
                    "len(dimensions)": len(dimensions),
                },
            )
            Checker.VALUE(
                operator.shape[-2:] == (dimensions[position], dimensions[position]),
                "The last two dimensions of the operator must match the value of the"
                " dimensions list at the given position.",
                {
                    f"shape of {index}-th operator": operator.shape,
                    "position for this operator": position,
                    f"dimensions[{position}]": dimensions[position],
                },
            )

        batch_shape = get_broadcasted_shape(
            *[i[0].shape[:-2] for i in _operators],
            message="The batch shapes of all the operators must be broadcastable.",
        )

        full_dimension = np.prod(dimensions, dtype=int)
        full_shape = batch_shape + (full_dimension, full_dimension)

        operation = create_operation(self.embed_operators, locals())
        return Tensor(operation, shape=full_shape)

    @validated
    def kronecker_product_list(
        self,
        operators: Annotated[
            List[
                Annotated[
                    Union[np.ndarray, Tensor], pipe(shapeable, after=ShapeT.MATRIX())
                ]
            ],
            Field(min_length=1),
        ],
        *,
        name: Optional[str] = None,
    ) -> Tensor:
        r"""
        Calculate the Kronecker product between a list of operators.

        Parameters
        ----------
        operators : list[Tensor or np.ndarray]
            The list of operators. It must contain at least one operator.
            The operators must be at least 2D and can contain leading batch dimensions.
        name : str or None, optional
            The name of the node.

        Returns
        -------
        Tensor
            The Kronecker product of the list of operators. The Hilbert space of the output is equal
            to the tensor product of the Hilbert spaces of all the given operators.

        See Also
        --------
        Graph.embed_operators : Embed operators into a larger Hilbert space.
        Graph.kron : Kronecker product between two objects.
        Graph.pauli_kronecker_product : Embed Pauli matrices into a larger Hilbert space.

        Examples
        --------
        >>> number_op = graph.number_operator(3)
        >>> sigma_x = graph.pauli_matrix("X")
        >>> graph.kronecker_product_list([number_op, sigma_x], name="N0X1")
        <Tensor: name="N0X1", operation_name="kronecker_product_list", shape=(6, 6)>
        >>> result = bo.execute_graph(graph=graph, output_node_names="N0X1")
        >>> result["output"]["N0X1"]["value"]
        array([[0.+0.j, 0.+0.j, 0.+0.j, 0.+0.j, 0.+0.j, 0.+0.j],
               [0.+0.j, 0.+0.j, 0.+0.j, 0.+0.j, 0.+0.j, 0.+0.j],
               [0.+0.j, 0.+0.j, 0.+0.j, 1.+0.j, 0.+0.j, 0.+0.j],
               [0.+0.j, 0.+0.j, 1.+0.j, 0.+0.j, 0.+0.j, 0.+0.j],
               [0.+0.j, 0.+0.j, 0.+0.j, 0.+0.j, 0.+0.j, 2.+0.j],
               [0.+0.j, 0.+0.j, 0.+0.j, 0.+0.j, 2.+0.j, 0.+0.j]])
        """
        batch_shape = get_broadcasted_shape(
            *[op.shape[:-2] for op in operators],
            message="The batch shapes of the operators must be broadcastable.",
        )
        value_shape = (
            np.prod([op.shape[-2] for op in operators], dtype=int),
            np.prod([op.shape[-1] for op in operators], dtype=int),
        )

        shape = batch_shape + value_shape
        operation = create_operation(self.kronecker_product_list, locals())
        return Tensor(operation, shape=shape)

    @validated
    def min(
        self,
        x: Annotated[Union[np.ndarray, Tensor], pipe(shapeable)],
        axis: Optional[
            Annotated[Union[int, List[int]], pipe(sequence_like(ScalarT.INT()))]
        ] = None,
        keepdims: bool = False,
        *,
        name: Optional[str] = None,
    ) -> Tensor:
        """
        Find the minimum value in a tensor along one or multiple of its axes.

        Parameters
        ----------
        x : np.ndarray or Tensor
            The tensor of which you want to find the minimum value.
        axis : int or list[int] or None, optional
            The dimension or dimensions along which you want to search the tensor.
            Defaults to None, in which case this node returns the minimum value
            along all axes of the tensor.
        keepdims : bool, optional
            Whether or not to retain summed axes in the output tensor. If True, each dimension
            in `axis` has size 1 in the result; otherwise, the dimensions in `axis` are
            removed from the result. Defaults to False.
        name : str or None, optional
            The name of the node.

        Returns
        -------
        Tensor
            The minimum tensor obtained by searching the input tensor along the specified axes.

        See Also
        --------
        Graph.max : Find the maximum value in a tensor along one or multiple of its axes.
        """
        axes = check_operation_axis(axis, x.shape, "x")
        shape = get_keepdims_operation_shape(x.shape, axes, keepdims)

        operation = create_operation(self.min, locals())
        return Tensor(operation, shape=shape)

    @validated
    def max(
        self,
        x: Annotated[Union[np.ndarray, Tensor], pipe(shapeable)],
        axis: Optional[
            Annotated[Union[int, List[int]], pipe(sequence_like(ScalarT.INT()))]
        ] = None,
        keepdims: bool = False,
        *,
        name: Optional[str] = None,
    ) -> Tensor:
        """
        Find the maximum value in a tensor along one or multiple of its axes.

        Parameters
        ----------
        x : np.ndarray or Tensor
            The tensor of which you want to find the maximum value.
        axis : int or list[int] or None, optional
            The dimension or dimensions along which you want to search the tensor.
            Defaults to None, in which case this node returns the maximum value
            along all axes of the tensor.
        keepdims : bool, optional
            Whether or not to retain summed axes in the output tensor. If True, each dimension
            in `axis` has size 1 in the result; otherwise, the dimensions in `axis` are
            removed from the result. Defaults to False.
        name : str or None, optional
            The name of the node.

        Returns
        -------
        Tensor
            The maximum tensor obtained by searching the input tensor along the specified axes.

        See Also
        --------
        Graph.min : Find the minimum value in a tensor along one or multiple of its axes.
        """
        axes = check_operation_axis(axis, x.shape, "x")
        shape = get_keepdims_operation_shape(x.shape, axes, keepdims)

        operation = create_operation(self.max, locals())
        return Tensor(operation, shape=shape)
