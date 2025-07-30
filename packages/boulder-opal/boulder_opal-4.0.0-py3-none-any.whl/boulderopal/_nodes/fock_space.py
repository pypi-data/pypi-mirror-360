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
    Any,
    List,
    Optional,
    Union,
)

import numpy as np

from boulderopal._nodes.base import create_operation
from boulderopal._nodes.validation import (
    ShapeT,
    shapeable,
)
from boulderopal._typing import Annotated
from boulderopal._validation import (
    ArrayT,
    Checker,
    ScalarT,
    pipe,
    sequence_like,
    validated,
)

from .node_data import Tensor


def _validate_fock_state_input(
    dimension: int | list[int],
    level: int | list[int] | list[list[int]],
    offset: Optional[int | list[int]],
) -> tuple[int, ...]:
    """
    Validate the inputs of the Fock state node and, if they're valid,
    return the shape of the Fock state.
    """
    if isinstance(dimension, list):
        # dimension is a list, so offset must be a list of non-negative integers of the same length.
        if offset is not None:
            Checker.VALUE(
                isinstance(offset, list) and len(offset) == len(dimension),
                "When constructed from subsystems, a non-default offset must be a list of integers "
                "and have the same size as dimension.",
                {"dimension": dimension, "offset": offset},
            )

        # level must be int or list[int] or list[list[int]].
        if isinstance(level, list):
            if isinstance(level[0], list):
                # level is list[list[int]].
                Checker.VALUE(
                    all(len(item) == len(dimension) for item in level),  # type: ignore
                    "Each batch of level must be a list of integers with the same "
                    "length as dimension.",
                    {"level": level, "dimension": dimension},
                )
            else:
                # level is list[int].
                Checker.VALUE(
                    len(level) == len(dimension),
                    "Level must be a list of integers with the same length as dimension.",
                    {"level": level, "dimension": dimension},
                )
            _level_arr = np.asarray(level)
        else:
            # level is int.
            _level_arr = np.repeat(level, len(dimension))

        # level must be in [offset, dim+offset).
        _dimension_arr = np.asarray(dimension)
        _offset_arr = (
            np.zeros_like(_dimension_arr) if offset is None else np.asarray(offset)
        )
        Checker.VALUE(
            np.all(_level_arr >= _offset_arr),
            "Level must be larger than or equal to offset.",
            {"level": level, "offset": offset},
        )
        Checker.VALUE(
            np.all(_level_arr < (_dimension_arr + _offset_arr)),
            "Level must be smaller than dimension + offset.",
            {"level": level, "dimension": dimension, "offset": offset},
        )

        return _level_arr.shape[:-1] + (int(np.prod(dimension)),)

    # dimension is an int, so offset must be a non-negative integer (if set).
    if offset is not None:
        if not isinstance(offset, int):
            raise TypeError(
                "Dimension and offset must be the same type. They should either be "
                "integers or lists of integers. "
                f"dimension={dimension}, offset={offset}."
            )
        _offset: int = offset
    else:
        _offset = 0

    # level must be an int or list[int] in [offset, dim+offset).
    Checker.VALUE(
        isinstance(level, int) or isinstance(level[0], int),
        "If the Fock state is not constructed from subsystems, "
        "level must either be an integer or a list of integers.",
        {"dimension": dimension, "level": level},
    )
    level_arr = np.asarray(level)
    Checker.VALUE(
        np.all(level_arr >= _offset),
        "Level must be larger than or equal to the offset.",
        {"offset": _offset, "level": level},
    )
    Checker.VALUE(
        np.all(level_arr < dimension + _offset),
        "Level must be smaller than dimension + offset.",
        {"dimension": dimension, "offset": _offset, "level": level},
    )

    return level_arr.shape + (dimension,)


def _validate_alpha(value: Any, *, name: str) -> Union[int, float, complex, np.ndarray]:
    try:
        return ScalarT.NUMERIC(name)(value)
    except TypeError:
        try:
            return ArrayT.NUMERIC().ndim(1)(value, name=name)
        except TypeError as exc:
            raise TypeError(f"{name} must be a number or a 1D array.") from exc


class FockSpaceGraph:  # pylint: disable=unused-argument
    """
    Base class implementing Fock space graph methods.
    """

    @validated
    def fock_state(
        self,
        dimension: Annotated[
            Union[int, List[int]], pipe(sequence_like(ScalarT.INT().ge(1)))
        ],
        level: Annotated[
            Union[int, List[int], List[List[int]]],
            pipe(sequence_like(sequence_like(ScalarT.INT().ge(0)))),
        ],
        offset: Optional[
            Annotated[Union[int, List[int]], pipe(sequence_like(ScalarT.INT().ge(0)))]
        ] = None,
        *,
        name: Optional[str] = None,
    ) -> Tensor:
        r"""
        Create a Fock state (or a batch of them).

        You can create a Fock state for a single system by providing the `dimension` of the
        truncated Fock space, the occupied energy `level`, and the lowest represented level
        `offset` (optional) as integer parameters. You can create a batch of Fock states
        by passing a list of integers to `level`.

        Alternatively, you can create a Fock state for a composite system. In this case, the
        `dimension` (and the optional `offset`) must be a list of integers, representing
        the size of the truncated space for each subsystem (and the respective offset).
        You can then set the occupied level for each subsystem as follows:

        - `level` is an integer, meaning all subsystems have the same occupied level.
        - `level` is a list of integers, meaning each element represents the occupied level
          for the corresponding subsystem.
        - `level` is a list of lists. The outer list defines a batch of states.
          Each inner list element is treated as in the above case.

        Parameters
        ----------
        dimension : int or list[int]
            The size of the state representation in the truncated Fock space. A list of integers
            is interpreted as the sizes of subsystems, meaning the final Fock space has the same
            size as the product of these integers. By default, the Fock space is truncated as
            [0, dimension). If non-zero offset is passed, the space is then truncated at
            [offset, dimension + offset).
        level : int or list[int] or list[list[int]]
            The level at which the Fock basis is occupied. If a list of integers
            (or a list of integers when constructed from subsystems) is passed,
            this function returns a batch of Fock states, where each element is a Fock state
            with the energy level specified in the list.
        offset : int or list[int] or None, optional
            The lowest level of Fock state in the representation. Defaults to None, meaning
            the lowest level is 0. If set, this parameter must have the same type as `dimension`.
        name : str or None, optional
            The name of the node.

        Returns
        -------
        Tensor
            Fock states with energy level specified by `level`. 1D vector if there is no batch
            in `level`, otherwise a 2D tensor where the first axis is the batch dimension.

        See Also
        --------
        Graph.annihilation_operator : Create an annihilation operator in the truncated Fock space.
        Graph.coherent_state : Create a coherent state (or a batch of them).
        Graph.creation_operator : Create a creation operator in the truncated Fock space.
        Graph.number_operator : Create a number operator in the truncated Fock space.

        Examples
        --------
        Create a Fock state for a single system.

        >>> graph.fock_state(2, 0, name="direct")
        <Tensor: name="direct", operation_name="fock_state", shape=(2,)>
        >>> result = bo.execute_graph(graph=graph, output_node_names="direct")
        >>> result["output"]["direct"]["value"]
        array([1.+0.j, 0.+0.j])

        Create a batch of Fock states for a single system.

        >>> graph.fock_state(2, [0, 1], name="direct_batch")
        <Tensor: name="direct_batch", operation_name="fock_state", shape=(2, 2)>
        >>> result = bo.execute_graph(graph=graph, output_node_names="direct_batch")
        >>> result["output"]["direct_batch"]["value"]
        array([[1.+0.j, 0.+0.j],
            [0.+0.j, 1.+0.j]])

        Create a batch of Fock states for a single system with an offset.

        >>> graph.fock_state(3, [1, 2], offset=1,  name="direct_offset")
        <Tensor: name="direct_offset", operation_name="fock_state", shape=(2, 3)>
        >>> result = bo.execute_graph(graph=graph, output_node_names="direct_offset")
        >>> result["output"]["direct_offset"]["value"]
        array([[1.+0.j, 0.+0.j, 0.+0.j],
            [0.+0.j, 1.+0.j, 0.+0.j]])

        Create a Fock state from subsystems.

        >>> graph.fock_state([2, 3], [1, 2], name="subsystems")
        <Tensor: name="subsystems", operation_name="fock_state", shape=(6,)>
        >>> result = bo.execute_graph(graph=graph, output_node_names="subsystems")
        >>> result["output"]["subsystems"]["value"]
        array([0.+0.j, 0.+0.j, 0.+0.j, 0.+0.j, 0.+0.j, 1.+0.j])

        Create a batch of Fock states from subsystems.

        >>> graph.fock_state([2, 3], [[0, 1], [1, 2]], name="batch")
        <Tensor: name="batch", operation_name="fock_state", shape=(2, 6)>
        >>> result = bo.execute_graph(graph=graph, output_node_names="batch")
        >>> result["output"]["batch"]["value"]
        array([[0.+0.j, 1.+0.j, 0.+0.j, 0.+0.j, 0.+0.j, 0.+0.j],
            [0.+0.j, 0.+0.j, 0.+0.j, 0.+0.j, 0.+0.j, 1.+0.j]])

        Create a batch of Fock states with offset from subsystems.

        >>> graph.fock_state([2, 3], [[1, 4], [1, 3]], offset=[1, 2], name="offset")
        <Tensor: name="offset", operation_name="fock_state", shape=(2, 6)>
        >>> result = bo.execute_graph(graph=graph, output_node_names="offset")
        >>> result["output"]["offset"]["value"]
        array([[0.+0.j, 0.+0.j, 1.+0.j, 0.+0.j, 0.+0.j, 0.+0.j],
            [0.+0.j, 1.+0.j, 0.+0.j, 0.+0.j, 0.+0.j, 0.+0.j]])
        """
        shape = _validate_fock_state_input(dimension, level, offset)
        operation = create_operation(self.fock_state, locals())
        return Tensor(operation, shape=shape)

    @validated
    def creation_operator(
        self,
        dimension: Annotated[int, pipe(ScalarT.INT().ge(1))],
        offset: Annotated[int, pipe(ScalarT.INT().ge(0))] = 0,
        *,
        name: Optional[str] = None,
    ) -> Tensor:
        r"""
        Create a creation operator in the truncated Fock space.

        Parameters
        ----------
        dimension : int
            The size of the state representation in the truncated Fock space.
            By default, the Fock space is truncated at [0, dimension).
            If non-zero offset is passed, the space is then
            truncated at [offset, dimension + offset).
        offset : int, optional
            The lowest level of Fock state in the representation. Defaults to 0.
        name : str or None, optional
            The name of the node.

        Returns
        -------
        Tensor
            A 2D tensor representing the creation operator.

        See Also
        --------
        Graph.annihilation_operator : Create an annihilation operator in the truncated Fock space.
        Graph.coherent_state : Create a coherent state (or a batch of them).
        Graph.fock_state : Create a Fock state (or a batch of them).
        Graph.number_operator : Create a number operator in the truncated Fock space.

        Examples
        --------
        Generate a creation operator for a two-level system.

        >>> graph.creation_operator(2, name="adagger")
        <Tensor: name="adagger", operation_name="creation_operator", shape=(2, 2)>
        >>> result = bo.execute_graph(graph=graph, output_node_names="adagger")
        >>> result["output"]["adagger"]["value"]
        array([[0.+0.j, 0.+0.j],
            [1.+0.j, 0.+0.j]])

        Apply a creation operator on the ground state such that
        :math:`a^\dagger|0\rangle = |1\rangle`.

        >>> adagger = graph.creation_operator(2)
        >>> state = adagger @ graph.fock_state(2, 0)[:, None]
        >>> state.name = "state"
        >>> result = bo.execute_graph(graph=graph, output_node_names="state")
        >>> result["output"]["state"]["value"]
        array([[0.+0.j],
            [1.+0.j]])

        Generate a creation operator for a three-level system with an offset.

        >>> graph.creation_operator(3, 1, name="adagger_offset")
        <Tensor: name="adagger_offset", operation_name="creation_operator", shape=(3, 3)>
        >>> result = bo.execute_graph(graph=graph, output_node_names="adagger_offset")
        >>> result["output"]["adagger_offset"]["value"]
        array([[0.+0.j, 0.+0.j, 0.+0.j],
            [1.41421356+0.j, 0.+0.j, 0.+0.j],
            [0.+0.j, 1.73205081+0.j, 0.+0.j]])

        Apply a creation operator with an offset such that
        :math:`a^\dagger|1\rangle = \sqrt{2}|2\rangle`.

        >>> adagger_offset = graph.creation_operator(3, 1)
        >>> state_offset = adagger_offset @ graph.fock_state(3, 1, 1)[:, None]
        >>> state.name = "offset"
        >>> result = bo.execute_graph(graph=graph, output_node_names="offset")
        >>> result["output"]["offset"]["value"]
        array([[0.        +0.j],
            [1.41421356+0.j],
            [0.        +0.j]])
        """
        operation = create_operation(self.creation_operator, locals())
        return Tensor(operation, shape=(dimension, dimension))

    @validated
    def annihilation_operator(
        self,
        dimension: Annotated[int, pipe(ScalarT.INT().ge(1))],
        offset: Annotated[int, pipe(ScalarT.INT().ge(0))] = 0,
        *,
        name: Optional[str] = None,
    ) -> Tensor:
        r"""
        Create an annihilation operator in the truncated Fock space.

        Parameters
        ----------
        dimension : int
            The size of the state representation in the truncated Fock space.
            By default, the Fock space is truncated at [0, dimension).
            If non-zero offset is passed, the space is then
            truncated at [offset, dimension + offset).
        offset : int, optional
            The lowest level of Fock state in the representation. Defaults to 0.
        name : str or None, optional
            The name of the node.

        Returns
        -------
        Tensor
            A 2D tensor representing the annihilation operator.

        See Also
        --------
        Graph.coherent_state : Create a coherent state (or a batch of them).
        Graph.creation_operator : Create a creation operator in the truncated Fock space.
        Graph.fock_state : Create a Fock state (or a batch of them).
        Graph.number_operator : Create a number operator in the truncated Fock space.

        Examples
        --------
        Generate an annihilation operator for a two-level system.

        >>> graph.annihilation_operator(2, name="a")
        <Tensor: name="a", operation_name="annihilation_operator", shape=(2, 2)>
        >>> result = bo.execute_graph(graph=graph, output_node_names="a")
        >>> result["output"]["a"]["value"]
        array([[0.+0.j, 1.+0.j],
            [0.+0.j, 0.+0.j]])

        Apply an annihilation operator on the excited state such that
        :math:`a|1\rangle = |0\rangle`.

        >>> a = graph.annihilation_operator(2)
        >>> state = a @ graph.fock_state(2, 1)[:, None]
        >>> state.name = "state"
        >>> result = bo.execute_graph(graph=graph, output_node_names="state")
        >>> result["output"]["state"]["value"]
        array([[1.+0.j],
            [0.+0.j]])

        Generate an annihilation operator for a three-level system with an offset.

        >>> graph.annihilation_operator(3, 1, name="a_offset")
        <Tensor: name="a_offset", operation_name="annihilation_operator", shape=(3, 3)>
        >>> result = bo.execute_graph(graph=graph, output_node_names="a_offset")
        >>> result["output"]["a_offset"]["value"]
        array([[0.+0.j, 1.41421356+0.j, 0.+0.j],
            [0.+0.j, 0.+0.j, 1.73205081+0.j],
            [0.+0.j, 0.+0.j, 0.+0.j]])

        Apply an annihilation operator with an offset such that
        :math:`a|2\rangle = \sqrt{2}|1\rangle`.

        >>> a_offset = graph.creation_operator(3, 1)
        >>> state_offset = a_offset @ graph.fock_state(3, 2, 1)[:, None]
        >>> state.name = "offset"
        >>> result = bo.execute_graph(graph=graph, output_node_names="offset")
        >>> result["output"]["offset"]["value"]
        array([[1.41421356+0.j],
            [0.        +0.j],
            [0.        +0.j]])
        """
        operation = create_operation(self.annihilation_operator, locals())
        return Tensor(operation, shape=(dimension, dimension))

    @validated
    def number_operator(
        self,
        dimension: Annotated[int, pipe(ScalarT.INT().ge(1))],
        offset: Annotated[int, pipe(ScalarT.INT().ge(0))] = 0,
        *,
        name: Optional[str] = None,
    ) -> Tensor:
        r"""
        Create a number operator in the truncated Fock space.

        Parameters
        ----------
        dimension : int
            The size of the state representation in the truncated Fock space.
            By default, the Fock space is truncated at [0, dimension).
            If non-zero offset is passed, the space is then
            truncated at [offset, dimension + offset).
        offset : int, optional
            The lowest level of Fock state in the representation. Defaults to 0.
        name : str or None, optional
            The name of the node.

        Returns
        -------
        Tensor
            A 2D tensor representing the number operator.

        See Also
        --------
        Graph.annihilation_operator : Create an annihilation operator in the truncated Fock space.
        Graph.coherent_state : Create a coherent state (or a batch of them).
        Graph.creation_operator : Create a creation operator in the truncated Fock space.
        Graph.fock_state : Create a Fock state (or a batch of them).

        Examples
        --------
        Generate a number operator for a three-level system.

        >>> graph.number_operator(3, name="n")
        <Tensor: name="n", operation_name="number_operator", shape=(3, 3)>
        >>> result = bo.execute_graph(graph=graph, output_node_names="n")
        >>> result["output"]["n"]["value"]
        array([[0.+0.j, 0.+0.j, 0.+0.j],
            [0.+0.j, 1.+0.j, 0.+0.j],
            [0.+0.j, 0.+0.j, 2.+0.j]])

        Apply a number operator on the second excited state such that
        :math:`N|2\rangle = 2|2\rangle`.

        >>> n = graph.number_operator(3)
        >>> state = n @ graph.fock_state(3, 2)[:, None]
        >>> state.name = "state"
        >>> result = bo.execute_graph(graph=graph, output_node_names="state")
        >>> result["output"]["state"]["value"]
        array([[0.+0.j],
            [0.+0.j],
            [2.+0.j]])

        Generate a number operator for a three-level system with an offset.

        >>> graph.number_operator(3, 1, name="n_offset")
        <Tensor: name="n_offset", operation_name="number_operator", shape=(3, 3)>
        >>> result = bo.execute_graph(graph=graph, output_node_names="n_offset")
        >>> result["output"]["n_offset"]["value"]
        array([[1.+0.j, 0.+0.j, 0.+0.j],
            [0.+0.j, 2.+0.j, 0.+0.j],
            [0.+0.j, 0.+0.j, 3.+0.j]])

        Apply a number operator with an offset such that
        :math:`N|3\rangle = 3|3\rangle`.

        >>> n_offset = graph.number_operator(3, 1)
        >>> state_offset = n_offset @ graph.fock_state(3, 3, 1)[:, None]
        >>> state_offset.name = "state_offset"
        >>> result = bo.execute_graph(graph=graph, output_node_names="state_offset")
        >>> result["output"]["state_offset"]["value"]
        array([[0.+0.j],
            [0.+0.j],
            [3.+0.j]])
        """
        operation = create_operation(self.number_operator, locals())
        return Tensor(operation, shape=(dimension, dimension))

    @validated
    def coherent_state(
        self,
        alpha: Annotated[Union[int, float, complex, np.ndarray], pipe(_validate_alpha)],
        dimension: Annotated[int, pipe(ScalarT.INT().ge(1))],
        offset: Annotated[int, pipe(ScalarT.INT().ge(0))] = 0,
        from_displacement: bool = True,
        *,
        name: Optional[str] = None,
    ) -> Tensor:
        r"""
        Create a coherent state (or a batch of them).

        By default, this function generates the coherent state by applying the displacement operator
        on the vacuum state in the truncated Fock space. Alternatively, you can also generate the
        coherent state from its analytical formula in the Fock basis (see the note part for details)
        by setting the flag `from_displacement` to False. Note that as the second approach is
        effectively truncating an infinite series, therefore the returned coherent state is not
        necessarily normalized.

        Parameters
        ----------
        alpha : number or np.ndarray
            A number :math:`\alpha` that characterizes the coherent state.
            You can also pass a 1D array to generate a batch of coherent states.
        dimension : int
            The size of the state representation in the truncated Fock space.
            By default, the Fock space is truncated at [0, dimension).
            If non-zero offset is passed, the space is then
            truncated at [offset, dimension + offset).
        offset : int, optional
            The lowest level of Fock state in the representation. Defaults to 0.
        from_displacement :  bool, optional
            Defaults to True, meaning the coherent state is computed from the displacement
            operation. You can set this flag to False to get the coherent state from its
            analytical formula in the Fock basis.
        name : str or None, optional
            The name of the node.

        Returns
        -------
        Tensor
            A tensor representing the coherent state. The shape is 1D if there is
            no batch in `alpha`, otherwise 2D where the first axis is the batch dimension.

        See Also
        --------
        Graph.annihilation_operator : Create an annihilation operator in the truncated Fock space.
        Graph.creation_operator : Create a creation operator in the truncated Fock space.
        Graph.displacement_operator :
            Create a displacement operator (or a batch of them) in the truncated Fock space.
        Graph.fock_state : Create a Fock state (or a batch of them).
        Graph.number_operator : Create a number operator in the truncated Fock space.

        Notes
        -----
        A coherent state :math:`|\alpha\rangle` can be generated by applying a displacement
        operator :math:`D(\alpha)` on the vacuum state :math:`|0\rangle`:

        .. math::
            |\alpha\rangle = D(\alpha)|0\rangle
                        = \exp(\alpha \hat{a}^\dagger  - \alpha^\ast \hat{a}) | 0 \rangle

        where :math:`\hat{a}` and :math:`\hat{a}^\dagger` are the annihilation
        and creation operators respectively.

        The coherent state can also be represented in the basis of Fock states:

        .. math::
            |\alpha\rangle = e^{-\frac{|\alpha|^2}{2}}
                            \sum_{n=0}^{\infty} \frac{\alpha^n}{\sqrt{n!}}|n\rangle .

        For more information about coherent states, see `coherent state`_ on Wikipedia.

        .. _coherent state:
            https://en.wikipedia.org/wiki/Coherent_state

        Examples
        --------
        Create a coherent state from displacement.

        >>> graph.coherent_state(1j, 2, name="state")
        <Tensor: name="state", operation_name="coherent_state", shape=(2,)>
        >>> result = bo.execute_graph(graph=graph, output_node_names="state")
        >>> result["output"]["state"]["value"]
        array([5.40302306e-01+0.j        , 5.55111512e-17+0.84147098j])

        Create a batch of coherent states from displacement.

        >>> graph.coherent_state([1j, 3], 2, name="batch")
        <Tensor: name="batch", operation_name="coherent_state", shape=(2, 2)>
        >>> result = bo.execute_graph(graph=graph, output_node_names="batch")
        >>> result["output"]["batch"]["value"]
        array([[ 5.40302306e-01+0.j        ,  5.55111512e-17+0.84147098j],
            [-9.89992497e-01+0.j        ,  1.41120008e-01+0.j        ]])

        Create a batch of coherent states from the analytical formula.

        >>> graph.coherent_state([1j, 3], 2, from_displacement=False, name="analytical")
        <Tensor: name="analytical", operation_name="coherent_state", shape=(2, 2)>
        >>> result = bo.execute_graph(graph=graph, output_node_names="analytical")
        >>> result["output"]["analytical"]["value"]
        array([[6.06530660e-01+0.j        , 3.71392916e-17+0.60653066j],
            [1.11089965e-02+0.j        , 3.33269896e-02+0.j        ]])
        """
        batch_shape = getattr(alpha, "shape", ())
        operation = create_operation(self.coherent_state, locals())
        return Tensor(operation, shape=batch_shape + (dimension,))

    @validated
    def displacement_operator(
        self,
        alpha: Annotated[Union[int, float, complex, np.ndarray], pipe(_validate_alpha)],
        dimension: Annotated[int, pipe(ScalarT.INT().ge(1))],
        offset: Annotated[int, pipe(ScalarT.INT().ge(0))] = 0,
        *,
        name: Optional[str] = None,
    ) -> Tensor:
        r"""
        Create a displacement operator (or a batch of them).

        Parameters
        ----------
        alpha : number or np.ndarray
            A number :math:`\alpha` that characterizes the displacement operator.
            You can also pass a 1D array to generate a batch of displacement operators.
        dimension : int
            The size of the truncated Fock space.
            By default, the Fock space is truncated at [0, dimension).
            If non-zero offset is passed, the space is then
            truncated at [offset, dimension + offset).
        offset : int, optional
            The lowest Fock state.
            Defaults to 0.
        name : str or None, optional
            The name of the node.

        Returns
        -------
        Tensor
            A tensor representing the displacement operator. The shape is 2D if there is no batch in
            `alpha`, otherwise 3D where the first axis is the batch dimension.

        See Also
        --------
        Graph.annihilation_operator : Create an annihilation operator in the truncated Fock space.
        Graph.coherent_state : Create a coherent state (or a batch of them).
        Graph.creation_operator : Create a creation operator in the truncated Fock space.
        Graph.fock_state : Create a Fock state (or a batch of them).
        Graph.number_operator : Create a number operator in the truncated Fock space.
        Graph.squeeze_operator :
            Create a squeeze operator (or a batch of them) in the truncated Fock space.

        Notes
        -----
        The displacement operator is defined as:

        .. math::
            D(\alpha) = \exp(\alpha \hat{a}^\dagger  - \alpha^\ast \hat{a})

        where :math:`\hat{a}` and :math:`\hat{a}^\dagger` are the annihilation
        and creation operators respectively.

        This operation uses truncated annihilation/creation operators to calculate the displacement
        operator. As such, for nonzero offset, generating a coherent state by applying the
        displacement operator to a Fock state will not generate the same result as using
        `coherent_state`, which uses a full operator and then truncates the resulting state.
        As the energy levels increase, however, the two coherent states will increasingly agree.

        For more information about the displacement operator, see `Displacement operator`_
        on Wikipedia.

        .. _Displacement operator:
            https://en.wikipedia.org/wiki/Displacement_operator

        Examples
        --------
        Create a displacement operator.

        >>> graph.displacement_operator(1j, 2, name="displacement")
        <Tensor: name="displacement", operation_name="displacement_operator", shape=(2, 2)>
        >>> result = bo.execute_graph(graph=graph, output_node_names="displacement")
        >>> result["output"]output["displacement"]["value"]
        array([[ 5.40302306e-01+0.00000000e+00j, -1.03050475e-16+8.41470985e-01j],
            [ 5.55111512e-17+8.41470985e-01j,  5.40302306e-01+6.61679489e-17j]])

        Create a batch of displacement operators.

        >>> graph.displacement_operator([1j, 3], 2, name="displacement_batch")
        <Tensor: name="displacement_batch", operation_name="displacement_operator", shape=(2, 2, 2)>
        >>> result = bo.execute_graph(graph=graph, output_node_names="displacement_batch")
        >>> result["output"]["displacement_batch"]["value"]
        array([[[ 5.40302306e-01+0.00000000e+00j, -1.11022302e-16+8.41470985e-01j],
                [ 5.55111512e-17+8.41470985e-01j, 5.40302306e-01+1.11022302e-16j]],
            [[-9.89992497e-01+0.00000000e+00j, -1.41120008e-01+0.00000000e+00j],
                [ 1.41120008e-01+0.00000000e+00j, -9.89992497e-01+0.00000000e+00j]]])
        """
        batch_shape = getattr(alpha, "shape", ())
        operation = create_operation(self.displacement_operator, locals())
        return Tensor(operation, shape=batch_shape + (dimension, dimension))

    @validated
    def squeeze_operator(
        self,
        zeta: Annotated[Union[int, float, complex, np.ndarray], pipe(_validate_alpha)],
        dimension: Annotated[int, pipe(ScalarT.INT().ge(1))],
        offset: Annotated[int, pipe(ScalarT.INT().ge(0))] = 0,
        *,
        name: Optional[str] = None,
    ) -> Tensor:
        r"""
        Create a squeeze operator (or a batch of them).

        Parameters
        ----------
        zeta : number or np.ndarray
            A number :math:`\zeta` that characterizes the squeeze operator.
            You can also pass a 1D array to generate a batch of squeeze operators.
        dimension : int
            The size of the truncated Fock space.
            By default, the Fock space is truncated at [0, dimension).
            If non-zero offset is passed, the space is then
            truncated at [offset, dimension + offset).
        offset : int, optional
            The lowest Fock state.
            Defaults to 0.
        name : str or None, optional
            The name of the node.

        Returns
        -------
        Tensor
            A tensor representing the squeeze operator. The shape is 2D if there is no batch in
            `zeta`, otherwise 3D where the first axis is the batch dimension.

        See Also
        --------
        Graph.annihilation_operator : Create an annihilation operator in the truncated Fock space.
        Graph.coherent_state : Create a coherent state (or a batch of them).
        Graph.creation_operator : Create a creation operator in the truncated Fock space.
        Graph.displacement_operator :
            Create a displacement operator (or a batch of them) in the truncated Fock space.
        Graph.fock_state : Create a Fock state (or a batch of them).
        Graph.number_operator : Create a number operator in the truncated Fock space.

        Notes
        -----
        The squeeze operator is defined as:

        .. math::
            S(\zeta) = \exp\left( \frac{\zeta^\ast \hat{a}^2 - \zeta \hat{a}^{\dagger2}}{2} \right)

        where :math:`\hat{a}` and :math:`\hat{a}^\dagger` are the annihilation
        and creation operators respectively.

        For more information about the squeeze operator, see `Squeeze operator`_ on Wikipedia.

        .. _Squeeze operator:
            https://en.wikipedia.org/wiki/Squeeze_operator

        Examples
        --------
        Create a squeeze operator.

        >>> graph.squeeze_operator(1j, 3, name="squeeze")
        <Tensor: name="squeeze", operation_name="squeeze_operator", shape=(3, 3)>
        >>> result = bo.execute_graph(graph=graph, output_node_names="squeeze")
        >>> result["output"]["squeeze"]["value"]
        array([[0.7602446+0.j        , 0.       +0.j        ,0.       -0.64963694j],
            [0.       +0.j        , 1.       +0.j        ,0.       +0.j        ],
            [0.       -0.64963694j, 0.       +0.j        ,0.7602446+0.j        ]])

        Create a batch of squeeze operators.

        >>> graph.squeeze_operator([1j, 3], 3, name="squeeze_batch")
        <Tensor: name="squeeze_batch", operation_name="squeeze_operator", shape=(2, 3, 3)>
        >>> result = bo.execute_graph(graph=graph, output_node_names="squeeze_batch")
        >>> result["output"]["squeeze_batch"]["value"]
        array([[[ 0.7602446 +0.j        ,  0.        +0.j        ,0.        -0.64963694j],
                [ 0.        +0.j        ,  1.        +0.j        ,0.        +0.j        ],
                [ 0.        -0.64963694j,  0.        +0.j        ,0.7602446 +0.j        ]],
            [[-0.19569944+0.j        ,  0.        +0.j        ,0.98066392+0.j        ],
                [ 0.        +0.j        ,  1.        +0.j        ,0.        +0.j        ],
                [-0.98066392-0.j        ,  0.        -0.j        ,-0.19569944-0.j        ]]])
        """
        batch_shape = getattr(zeta, "shape", ())
        operation = create_operation(self.squeeze_operator, locals())
        return Tensor(operation, shape=batch_shape + (dimension, dimension))

    @validated
    def wigner_transform(
        self,
        density_matrix: Annotated[
            Union[Tensor, np.ndarray], pipe(shapeable, after=ShapeT.OPERATOR())
        ],
        position: Annotated[np.ndarray, pipe(ArrayT.NUMERIC().ndim(1))],
        momentum: Annotated[np.ndarray, pipe(ArrayT.NUMERIC().ndim(1))],
        offset: Annotated[int, pipe(ScalarT.INT().ge(0))] = 0,
        *,
        name: Optional[str] = None,
    ) -> Tensor:
        r"""
        Transform a density matrix into a Wigner function (or a batch of them).

        Parameters
        ----------
        density_matrix : Tensor or np.ndarray
            The density matrix :math:`\rho` in the Fock basis.
            Must be of shape ``(..., D, D)``.
        position : np.ndarray
            The dimensionless position vector :math:`q`. Must be a 1D array of shape ``(L,)``.
        momentum : np.ndarray
            The dimensionless momentum vector :math:`p`. Must be a 1D array of shape ``(K,)``.
        offset : int, optional
            The lowest Fock state. Defaults to 0.
        name : str or None, optional
            The name of the node.

        Returns
        -------
        Tensor
            The Wigner function with shape ``(..., L, K)``.

        Warnings
        --------
        This function currently does not support calculating a gradient with respect to its inputs.
        Therefore, it cannot be used in a graph for a `run_optimization` or
        `run_stochastic_optimization` call, which will raise a `RuntimeError`.
        Please use gradient-free optimization if you want to perform an optimization task with this
        function. You can learn more about it in the
        `How to optimize controls using gradient-free optimization
        <https://docs.q-ctrl.com/boulder-opal/user-guides/how-to-optimize-controls-using-gradient-free-optimization>`_
        user guide.

        See Also
        --------
        Graph.coherent_state : Create a coherent state (or a batch of them).
        Graph.fock_state : Create a Fock state (or a batch of them).

        Notes
        -----
        The Wigner transform is defined as:

        .. math::
            W(q,p) = \frac{1}{2\pi} \int_{-\infty}^{\infty} \mathrm{e}^{\mathrm{i}sp}
            \langle q - s/2| \rho | q + s/2 \rangle \mathrm{d}s .

        For more information about the Wigner transform, see `Wigner function`_ on Wikipedia.

        .. _Wigner function:
            https://en.wikipedia.org/wiki/Wigner_quasiprobability_distribution

        Examples
        --------
        Create a Wigner function.

        >>> graph.wigner_transform(np.array([[1]]), [-1, 0, 1], np.zeros(1), name="wigner")
        <Tensor: name="wigner", operation_name="wigner_transform", shape=(3, 1)>
        >>> result = bo.execute_graph(graph=graph, output_node_names="wigner")
        >>> result["output"]["wigner"]["value"]
        array([[ 0.11709966+0.j],
            [ 0.31830989+0.j],
            [ 0.11709966+0.j]])

        Create a batch of Wigner function.

        >>> graph.wigner_transform(
                np.array([[[1, 0], [0, 0]], [[0, 0], [0, 1]]]),
                np.array([-1, 0, 1]),
                np.zeros(1),
                name="wigner_batch",
            )
        <Tensor: name="wigner_batch", operation_name="wigner_transform", shape=(2, 3, 1)>
        >>> result = bo.execute_graph(graph=graph, output_node_names="wigner_batch")
        >>> result["output"]["wigner_batch"]["value"]
        array([[[ 0.11709966+0.j],
                [ 0.31830989+0.j],
                [ 0.11709966+0.j]],
            [[ 0.11709966+0.j],
                [-0.31830989+0.j],
                [ 0.11709966+0.j]]])
        """
        batch_shape = density_matrix.shape[:-2]
        operation = create_operation(self.wigner_transform, locals())
        return Tensor(operation, shape=batch_shape + (len(position), len(momentum)))
