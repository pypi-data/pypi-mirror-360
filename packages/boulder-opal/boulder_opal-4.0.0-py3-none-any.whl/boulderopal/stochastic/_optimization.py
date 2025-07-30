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
    Literal,
    Optional,
    Union,
    overload,
)

from boulderopal._core import run_stochastic_optimization_workflow
from boulderopal._validation import (
    Checker,
    ScalarT,
    nullable,
    validate_enum,
)
from boulderopal._validation.graph import (
    check_cost_node,
    check_cost_node_for_optimization_graph,
    check_initial_value_for_optimization_node,
    check_optimization_node_in_graph,
    validate_output_node_names,
)
from boulderopal.cloud._async import BoulderOpalJob
from boulderopal.graph import Graph
from boulderopal.optimization._optimization import HistoryScope
from boulderopal.stochastic._optimizer import Adam


@overload
def run_stochastic_optimization(
    graph: Graph,
    cost_node_name: str,
    output_node_names: str | list[str],
    optimizer: Optional[Adam | str] = None,
    iteration_count: int = 1000,
    target_cost: Optional[float] = None,
    cost_history_scope: HistoryScope = HistoryScope.NONE,
    seed: Optional[int] = None,
    *,
    run_async: Literal[False] = False,
) -> dict: ...


@overload
def run_stochastic_optimization(
    graph: Graph,
    cost_node_name: str,
    output_node_names: str | list[str],
    optimizer: Optional[Adam | str] = None,
    iteration_count: int = 1000,
    target_cost: Optional[float] = None,
    cost_history_scope: HistoryScope = HistoryScope.NONE,
    seed: Optional[int] = None,
    *,
    run_async: Literal[True],
) -> BoulderOpalJob: ...


def run_stochastic_optimization(
    graph: Graph,
    cost_node_name: str,
    output_node_names: str | list[str],
    optimizer: Optional[Adam | str] = None,
    iteration_count: int = 1000,
    target_cost: Optional[float] = None,
    cost_history_scope: HistoryScope = HistoryScope.NONE,
    seed: Optional[int] = None,
    *,
    run_async: bool = False,
) -> Union[dict, BoulderOpalJob]:
    r"""
    Perform gradient-based stochastic optimization of generic real-valued functions.

    Use this function to determine a choice of variables that minimizes the
    value of a stochastic scalar real-valued cost function of those variables. You
    express that cost function as a graph describing how the input variables
    and stochastic variables are transformed into the cost value.

    Parameters
    ----------
    graph : Graph
        The graph describing the cost :math:`C(\mathbf v, \boldsymbol \beta)` and outputs
        :math:`\{F_j(\mathbf v)\}` as functions of the optimizable input variables
        :math:`\mathbf v`. The graph must contain nodes with names :math:`s` (giving the
        cost function) and :math:`\{s_j\}` (giving the output functions).
    cost_node_name : str
        The name :math:`s` of the real-valued scalar graph node that defines the cost
        function :math:`C(\mathbf v, \boldsymbol \beta)` to be minimized.
    output_node_names : str or list[str]
        The names :math:`\{s_j\}` of the graph nodes that define the output functions
        :math:`\{F_j(\mathbf v)\}`. The function evaluates these using the optimized
        variables and returns them in the output. If any of the output nodes depend
        on random nodes, the random values used to calculate the output might not
        correspond to the values used to calculate the final cost.
    optimizer : Adam or str or None, optional
        The optimizer used for the stochastic optimization. You can either create an Adam optimizer
        for this parameter, or pass the string from a previous optimization result that represents
        state of the optimizer (the value with the key `state` in the returned dictionary from
        this function) to restart the optimization.
        Note that you can only resume a previous optimization if you pass the same graph.
        Defaults to a new Adam optimizer.
    iteration_count : int, optional
        The number :math:`N` of iterations the optimizer performs until it halts.
        The function returns the results from the best iteration (the one with
        the lowest cost). Defaults to 1000.
    target_cost : float or None, optional
        A target value of the cost that you can set as an early stop condition for the
        optimizer. If the cost becomes equal or smaller than this value, the
        optimization halts. Defaults to None, which means that this function runs
        until the `iteration_count` is reached.
    cost_history_scope : HistoryScope, optional
        Configuration for the scope of the returned cost history data.
        Use this to select how you want the history data to be returned.
        Defaults to no cost history data returned.
    seed : int or None, optional
        Seed for the random number generator used in the optimizer.
        If set, must be a non-negative integer.
        Use this option to generate deterministic results from the optimizer.
        Note that if your graph contains nodes generating random samples,
        you need to also set seeds for those nodes to ensure a reproducible result.
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
        containing the optimization result, with the following keys:

        ``cost``
            The minimum cost function value :math:`C(\mathbf v_\mathrm{optimized})`
            achieved across all optimization iterations.
        ``output``
            The dictionary giving the value of each requested output node, evaluated
            at the optimized variables, namely :math:`\{s_j: F_j(\mathbf v_\mathrm{optimized})\}`.
            The keys of the dictionary are the names :math:`\{s_j\}` of the output nodes.
            If any of the output nodes depend on random nodes, the random values used to
            calculate the output might not correspond to the values used to calculate the best cost.
        ``state``
            The encoded optimizer state. You can use this parameter to resume the optimization from
            the current step.
        ``cost_history``
            The evolution of the cost function across all optimization iterations.
        ``metadata``
            Metadata associated with the calculation.
            No guarantees are made about the contents of this metadata dictionary;
            the contained information is intended purely to help interpret the results of the
            calculation on a one-off basis.

    See Also
    --------
    :func:`boulderopal.stochastic.Adam`
        Create an Adam optimizer for stochastic optimization.
    :func:`boulderopal.closed_loop.optimize`
        Run a closed-loop optimization to find a minimum of the given cost function.
    :func:`boulderopal.closed_loop.step`
        Perform a single step in a closed-loop optimization.
    :func:`boulderopal.execute_graph`
        Evaluate generic functions.
    :func:`boulderopal.run_gradient_free_optimization`
        Perform model-based optimization without using gradient values.
    :func:`boulderopal.run_optimization`
        Perform gradient-based deterministic optimization of generic real-valued functions.
    boulderopal.cloud.BoulderOpalJob :
        An async Boulder Opal job submitted to the cloud.

    Notes
    -----

    Given a cost function :math:`C(\mathbf v, \boldsymbol \beta)` of optimization
    variables :math:`\mathbf v` and stochastic variables :math:`\boldsymbol \beta`,
    this function computes an estimate :math:`\mathbf v_\mathrm{optimized}` of
    :math:`\mathrm{argmin}_{\mathbf v} C(\mathbf v, \boldsymbol \beta)`, namely the
    choice of variables :math:`\mathbf v` that minimizes :math:`C(\mathbf v, \boldsymbol \beta)`
    with noise through the stochastic variables :math:`\boldsymbol \beta`.
    The function then calculates the values of arbitrary output functions
    :math:`\{F_j(\mathbf v_\mathrm{optimized})\}` with that choice of variables.

    This function represents the cost and output functions as nodes of a graph.
    This graph defines the input variables :math:`\mathbf v` and stochastic variables
    :math:`\boldsymbol \beta`, and how these variables are transformed into the corresponding
    cost and output quantities. You build the graph from primitive nodes defined in the
    Graph object. Each such node, which can be identified by a name, represents a function
    of the previous nodes in the graph (and thus, transitively, a function of the input variables).
    You can use any named scalar real-valued node :math:`s` as the cost function, and any named
    nodes :math:`\{s_j\}` as outputs.

    After you provide a cost function :math:`C(\mathbf v, \boldsymbol \beta)` (via a graph),
    this function runs the optimization process for :math:`N` iterations, each with random
    stochastic variables, to identify local minima of the stochastic cost function, and then takes
    the variables corresponding to the best such minimum as :math:`\mathbf v_\mathrm{optimized}`.

    Note that this function only performs a single optimization run. That means, if you provide
    lists of initial values for optimization variables in the graph, only the first one for
    each variable will be used.

    A common use-case for this function is to determine controls for a quantum system that yield
    an optimal gate subject to noise: the variables :math:`\mathbf v` parameterize the controls to
    be optimized, and the cost function :math:`C(\mathbf v, \boldsymbol \beta)` is the operational
    infidelity describing the quality of the resulting gate relative to a target gate with noise
    through the stochastic variables :math:`\boldsymbol \beta`. When combined with the node
    definitions in the Boulder Opal package, which make it convenient to define such cost functions,
    this function provides a highly configurable framework for quantum control that encapsulates
    other common tools such as batch gradient ascent pulse engineering [1]_.

    References
    ----------
    .. [1] `R. Wu, H. Ding, D. Dong, and X. Wang, Physical Review A 99, 042327 (2019).
            <https://doi.org/10.1103/PhysRevA.99.042327>`_

    Examples
    --------
    Perform a simple stochastic optimization.

    >>> graph = bo.Graph()
    >>> x = graph.optimization_variable(1, -1, 1, name="x")
    >>> cost = (x - 0.5) ** 2
    >>> cost.name = "cost"
    >>> result = bo.run_stochastic_optimization(
    ...     graph=graph, cost_node_name="cost", output_node_names="x"
    ... )
    >>> result["cost"], result["output"]
        (0.0, {'x': {'value': array([0.5])}})

    To have a better understanding of the optimization landscape, you can use the
    `cost_history_scope` parameter to retrieve the cost history information from the optimizer.
    See the reference for the available options.
    For example, to retrieve all available history information:

    >>> history_result = bo.run_stochastic_optimization(
    ...     graph=graph,
    ...     cost_node_name="cost",
    ...     output_node_names="x",
    ...     cost_history_scope="ALL",
    ... )

    You can then access the history information from the `cost_history` key.
    We only show here the last two records to avoid a lengthy output.

    >>> history_result["cost_history"]["iteration_values"][-2:]
        [1.9721522630525295e-31, 1.9721522630525295e-31]
    >>> history_result["cost_history"]["historical_best"][-2:]
        [0.0, 0.0]

    See also the `How to optimize controls robust to strong noise sources
    <https://docs.q-ctrl.com/boulder-opal/user-guides/how-to-optimize-
    controls-robust-to-strong-noise-sources>`_ user guide.
    """

    check_optimization_node_in_graph(graph)
    check_initial_value_for_optimization_node(graph)
    check_cost_node(cost_node_name, graph)

    output_node_names = validate_output_node_names(output_node_names, graph)
    check_cost_node_for_optimization_graph(graph, cost_node_name, output_node_names)

    if optimizer is None:
        optimizer = Adam()
    else:
        Checker.TYPE(
            isinstance(optimizer, (Adam, str)),
            "The optimizer must either be an Adam optimizer or"
            "a string to represent the state of the optimizer.",
            {"type(optimizer)": type(optimizer)},
        )
    assert optimizer is not None
    if isinstance(optimizer, Adam):
        optimizer_configuration: dict[str, Any] = {
            "adam": {"learning_rate": optimizer.learning_rate}
        }
    else:
        optimizer_configuration = {"state": optimizer}

    return run_stochastic_optimization_workflow(
        graph=graph,
        optimizer=optimizer_configuration,
        cost_node_name=cost_node_name,
        output_node_names=output_node_names,
        iteration_count=ScalarT.INT("iteration_count").gt(0)(iteration_count),
        target_cost=nullable(ScalarT.REAL("target_cost"), target_cost),
        cost_history_scope=validate_enum(HistoryScope, cost_history_scope),
        seed=nullable(ScalarT.INT("seed").ge(0), seed),
        run_async=run_async,
    )
