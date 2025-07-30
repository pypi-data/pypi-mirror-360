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
from typing import (
    Literal,
    Union,
    overload,
)

from boulderopal._core import execute_graph_workflow
from boulderopal._validation import (
    Checker,
    validate_enum,
)
from boulderopal._validation.graph import (
    is_optimization_variable,
    validate_output_node_names,
)
from boulderopal.cloud._async import BoulderOpalJob
from boulderopal.graph._graph import Graph


class ExecutionMode(Enum):
    """
    Configuration for the execution mode used in `execute_graph`.

    Attributes
    ----------
    COMPILED
        Compiled execution, where the graph you provide is compiled into an executable that can
        run operations in parallel and with low overhead (at the expense of compilation time).
        This mode can be faster for simulations of open system dynamics, large systems, or systems
        described by sampleable tensor function (Stf) objects.

    EAGER
        Eager execution, where the graph nodes you provide are executed sequentially
        immediately as they are encountered. This mode can be faster for simulations of systems
        described by piecewise-constant Hamiltonians with a large number (more than roughly 1000)
        of segments.

    See Also
    --------
    boulderopal.execute_graph : Evaluate a graph corresponding to a set of generic functions.
    """

    COMPILED = "COMPILED"
    EAGER = "EAGER"


@overload
def execute_graph(
    graph: Graph,
    output_node_names: str | list[str],
    execution_mode: ExecutionMode = ExecutionMode.COMPILED,
    *,
    run_async: Literal[False] = False,
) -> dict: ...


@overload
def execute_graph(
    graph: Graph,
    output_node_names: str | list[str],
    execution_mode: ExecutionMode = ExecutionMode.COMPILED,
    *,
    run_async: Literal[True],
) -> BoulderOpalJob: ...


def execute_graph(
    graph: Graph,
    output_node_names: str | list[str],
    execution_mode: ExecutionMode = ExecutionMode.COMPILED,
    *,
    run_async: bool = False,
) -> Union[dict, BoulderOpalJob]:
    r"""
    Evaluate a graph corresponding to a set of generic functions.

    Use this function to carry out computations expressed as a graph
    representing a collection of arbitrary functions.

    Parameters
    ----------
    graph : Graph
        The graph describing the outputs. It must contain nodes with names
        (giving the output functions).
    output_node_names : str or list[str]
        The names of the graph nodes that define the output functions.
        The function evaluates these and returns them in the output.
        You can pass a string for a single node or a list of node names.
    execution_mode : ExecutionMode, optional
        The execution mode to use for the calculation. Choosing a custom execution mode can lead to
        faster computations in certain cases. Defaults to compiled execution mode.
    run_async : bool, optional
        Whether to execute the cloud calculation job asynchronously.
        If set to True, the function is a non-blocking operation and returns
        a BoulderOpalJob object.
        If set to False (the default), the function is blocking and on completion returns
        the calculation result as a dictionary.

    Returns
    -------
    dict or BoulderOpalJob
        When `run_async` is True, the function returns a BoulderOpalJob to manage the remote job.
        When `run_async` is False, the function returns a dictionary
        containing the graph execution result, with the following keys:

        ``output``
            The dictionary giving the value of each requested output node.
            The keys of the dictionary are the names of the output nodes.
        ``metadata``
            Metadata associated with the calculation.
            No guarantees are made about the contents of this metadata dictionary;
            the contained information is intended purely to help interpret the results of the
            calculation on a one-off basis.

    See Also
    --------
    boulderopal.closed_loop.optimize :
        Run a closed-loop optimization to find a minimum of the given cost function.
    boulderopal.closed_loop.step : Perform a single step in a closed-loop optimization.
    boulderopal.run_gradient_free_optimization :
        Perform model-based optimization without using gradient values.
    boulderopal.run_optimization :
        Perform gradient-based deterministic optimization of generic real-valued functions.
    boulderopal.run_stochastic_optimization :
        Perform gradient-based stochastic optimization of generic real-valued functions.
    boulderopal.cloud.BoulderOpalJob :
        An async Boulder Opal job submitted to the cloud.

    Notes
    -----
    This function computes arbitrary functions represented by a graph.

    The graph is made up of primitive nodes, where each node represents
    a function of the output of the nodes (or constant values) it depends on.
    You can assign a name to any node and request a list of named nodes :math:`\{s_j\}`
    as the outputs to be evaluated.

    Examples
    --------
    See the `How to represent quantum systems using graphs
    <https://docs.q-ctrl.com/boulder-opal/user-guides/
    how-to-represent-quantum-systems-using-graphs>`_ user guide.
    """

    for operation in graph.operations.values():
        Checker.VALUE(
            not is_optimization_variable(operation),
            f"The operation '{operation.operation_name}' is not available to use"
            " as part of the execute_graph function.",
        )

    output_node_names = validate_output_node_names(output_node_names, graph)
    return execute_graph_workflow(
        graph=graph,
        output_node_names=output_node_names,
        execution_mode=validate_enum(ExecutionMode, execution_mode),
        run_async=run_async,
    )
