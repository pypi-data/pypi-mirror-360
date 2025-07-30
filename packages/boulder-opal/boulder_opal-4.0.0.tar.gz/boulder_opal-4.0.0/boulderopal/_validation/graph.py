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

from collections import deque
from itertools import chain
from typing import (
    TYPE_CHECKING,
    Iterable,
)

from qctrlcommons.node.wrapper import (
    NodeData,
    Operation,
)

from boulderopal._validation import Checker

if TYPE_CHECKING:
    from boulderopal.graph import Graph

_OPTIMIZATION_NODES = {
    "anchored_difference_bounded_variables",
    "optimization_variable",
    "real_fourier_pwc_signal",
    "real_fourier_stf_signal",
}

_NO_GRADIENT_SUPPORT_NODES = {"steady_state", "wigner_transform"}


def is_optimization_variable(operation: Operation) -> bool:
    """
    Check if an Operation represents an optimization variable.
    """
    return operation.operation_name in _OPTIMIZATION_NODES


def supports_gradient(operation: Operation) -> bool:
    """
    Check if an Operation supports gradient.
    """
    return operation.operation_name not in _NO_GRADIENT_SUPPORT_NODES


def validate_output_node_names(
    node_names: str | list[str], graph: "Graph"
) -> list[str]:
    """
    Validate the names of the output nodes for fetching from a graph.

    If any node is not in the graph, raise an error. Otherwise, normalize the names to a list of
    strings.

    Parameters
    ---------
    node_names : str or list[str]
        Name of the nodes to be fetched.
    graph : Graph
        The graph where the nodes are supposed to be fetched from.

    Returns
    -------
    list[str]
        A list of valid node names.
    """

    if isinstance(node_names, str):
        node_names = [node_names]

    Checker.TYPE(
        isinstance(node_names, list)
        and all(isinstance(name, str) for name in node_names),
        "The output node names must be a string or a list of strings.",
    )

    Checker.VALUE(
        len(node_names) >= 1, "The output node names must have at least one element."
    )

    for name in node_names:
        check_node_in_graph(
            name,
            graph,
            f"The requested output node name '{name}' is not present in the graph.",
        )

    return node_names


def check_node_in_graph(node: str, graph: "Graph", message: str) -> None:
    """
    Check if a node is in the Graph.

    Parameters
    ----------
    node : str
        The name of the node.
    graph : Graph
        The Graph to be validated.
    message : str
        The error message.
    """
    Checker.VALUE(node in graph.operations, message, {"node name": node})


def check_optimization_node_in_graph(graph: "Graph") -> None:
    """
    Check optimization graph at least has one optimization node.
    """
    for operation in graph.operations.values():
        if is_optimization_variable(operation):
            return
    raise ValueError(
        "At least one optimization variable is required in the optimization graph."
    )


def check_cost_node(node: str, graph: Graph) -> None:
    """
    Check cost node:
        - if the node is in the graph.
        - if the node is a scalar Tensor.
    """
    Checker.TYPE(
        isinstance(node, str),
        "The cost node name must be a string.",
        {"type(cost_node_name)": type(node)},
    )
    check_node_in_graph(node, graph, "A cost node must be present in the graph.")
    Checker.VALUE(
        graph.operations[node].is_scalar_tensor,
        "The cost node must be a scalar Tensor.",
        {"cost_node_name": node},
    )


def check_cost_node_for_optimization_graph(
    graph: Graph,
    cost_node_name: str,
    output_node_names: list[str],
    check_gradient_nodes: bool = True,
) -> None:
    """
    Traverse the graph from the cost node, and check:
        1. All connected the nodes should support gradient if `check_gradient_nodes` is True.
        2. Any optimizable node to be fetched should connect to the cost node.
    """

    connected_optimization_node_names = set()

    def _validate_node_from_operation(operation: Operation) -> None:
        if check_gradient_nodes:
            Checker.VALUE(
                supports_gradient(operation),
                f"The {operation.operation_name} node does not support gradient.",
            )
        if is_optimization_variable(operation):
            connected_optimization_node_names.add(operation.name)

    def _get_parent_operations(node: str) -> Iterable[Operation]:
        """
        Go through inputs of the nodes, which might include Python primitive iterables.
        Find all NodeData and flat them as a single iterable.
        """

        def _get_input_items(input_: Iterable) -> Iterable:
            if isinstance(input_, NodeData):
                return [input_.operation]
            if isinstance(input_, (list, tuple)):
                return chain.from_iterable(_get_input_items(item) for item in input_)
            if isinstance(input_, dict):
                return chain.from_iterable(
                    _get_input_items(item) for item in input_.values()
                )
            return []

        return chain.from_iterable(
            _get_input_items(input_)
            for input_ in graph.operations[node].kwargs.values()
        )

    visited_nodes: set[str] = set()
    nodes_to_check: deque = deque()

    # cost node is where we start with.
    _validate_node_from_operation(graph.operations[cost_node_name])
    visited_nodes.add(cost_node_name)
    nodes_to_check.appendleft(cost_node_name)

    while nodes_to_check:
        node = nodes_to_check.pop()

        for operation in _get_parent_operations(node):
            if operation.name not in visited_nodes:
                _validate_node_from_operation(operation)
                visited_nodes.add(operation.name)
                nodes_to_check.appendleft(operation.name)

    # Graph traverse is done and all connected optimization nodes are recorded.
    # Now check output nodes.
    for name in output_node_names:
        if is_optimization_variable(graph.operations[name]):
            Checker.VALUE(
                name in connected_optimization_node_names,
                "The requested optimization node in `output_node_names` is not connected "
                "to the cost node.",
                {"disconnected output node name": name},
            )


def check_initial_value_for_optimization_node(graph: Graph) -> None:
    """
    Check optimization node has valid non-default initial values.
    """

    initial_value_info = {}

    for name, operation in graph.operations.items():
        if (
            is_optimization_variable(operation)
            and operation.kwargs.get("initial_values") is not None
        ):
            initial_value_info[name] = operation.kwargs["initial_values"]

    initial_values = list(initial_value_info.values())
    if len(initial_values) != 0:
        for val in initial_values[1:]:
            Checker.TYPE(
                isinstance(val, type(initial_values[0])),
                "Non-default initial values of optimization variables in the graph"
                " must either all be an array or all be a list of arrays.",
                initial_value_info,
            )

        if isinstance(initial_values[0], list):
            for val in initial_values[1:]:
                Checker.VALUE(
                    len(val) == len(initial_values[0]),
                    "Lists of initial values of optimization variables must have the same length.",
                    initial_value_info,
                )
