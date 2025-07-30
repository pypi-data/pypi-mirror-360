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

from typing import Optional

from boulderopal._core import run_gradient_free_optimization_workflow
from boulderopal._validation import (
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
from boulderopal.graph._graph import Graph
from boulderopal.optimization._optimization import HistoryScope


def run_gradient_free_optimization(
    graph: Graph,
    cost_node_name: str,
    output_node_names: str | list[str],
    iteration_count: int = 100,
    target_cost: Optional[float] = None,
    optimization_count: int = 4,
    cost_history_scope: HistoryScope = HistoryScope.NONE,
    seed: Optional[int] = None,
) -> dict:
    r"""
    Perform model-based optimization without using gradient values.

    Use this function to determine a choice of variables that minimizes the
    value of a scalar real-valued cost function of those variables. You
    express that cost function as a graph describing how the input variables
    are transformed into the cost value.

    This function provides an alternative to the gradient based optimizer, and
    is useful when the gradient is either very costly to compute or inaccessible
    (for example if the graph includes a node that does not allow gradients).

    Parameters
    ----------
    graph : Graph
        The graph describing the cost :math:`C(\mathbf v)` and outputs :math:`\{F_j(\mathbf v)\}`
        as functions of the optimizable input variables :math:`\mathbf v`.
        The graph must contain nodes with names :math:`s` (giving the cost function)
        and :math:`\{s_j\}` (giving the output functions).
    cost_node_name : str
        The name :math:`s` of the real-valued scalar graph node that defines the cost
        function :math:`C(\mathbf v)` to be minimized.
    output_node_names : str or list[str]
        The names :math:`\{s_j\}` of the graph nodes that define the output functions
        :math:`\{F_j(\mathbf v)\}`. The function evaluates these using the optimized
        variables and returns them in the output.
    iteration_count : int, optional
        The number of iterations the optimizer performs until it halts.
        Defaults to 100.
    target_cost : float or None, optional
        A target value of the cost that you can set as an early stop condition for the optimizer.
        If the cost becomes equal or smaller than this value, the optimization halts.
        Defaults to None, meaning that the optimizer runs until it converges.
    optimization_count : int, optional
        The number :math:`N` of independent randomly seeded optimizations to perform.
        The function returns the results from the best optimization (the one with
        the lowest cost). Defaults to 4. Depending on the landscape of the optimization problem,
        a larger value will help in finding lower costs, at the expense of prolonging computation
        time.
    cost_history_scope : HistoryScope, optional
        Configuration for the scope of the returned cost history data.
        Use this to select if you want the history data to be returned.
        Defaults to no cost history data returned.
    seed : int or None, optional
        Seed for the random number generator used in the optimizer.
        If set, must be a non-negative integer.
        Use this option to generate deterministic results from the optimizer.
        Note that if your graph contains nodes generating random samples,
        you need to also set seeds for those nodes to ensure a reproducible result.

    Returns
    -------
    dict
        A dictionary containing the optimization result, with the following keys:

        ``cost``
            The minimum cost function value :math:`C(\mathbf v_\mathrm{optimized})`
            achieved across all optimizations.
        ``output``
            The dictionary giving the value of each requested output node, evaluated
            at the optimized variables, namely
            :math:`\{s_j: F_j(\mathbf v_\mathrm{optimized})\}`.
            The keys of the dictionary are the names :math:`\{s_j\}` of the output nodes.
        ``cost_history``
            The evolution of the cost function across all optimizations and iterations.
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
    boulderopal.execute_graph : Evaluate generic functions.
    boulderopal.run_optimization :
        Perform gradient-based deterministic optimization of generic real-valued functions.
    boulderopal.run_stochastic_optimization :
        Perform gradient-based stochastic optimization of generic real-valued functions.

    Notes
    -----
    Given a cost function :math:`C(\mathbf v)` of variables :math:`\mathbf v`, this function
    computes an estimate :math:`\mathbf v_\mathrm{optimized}` of
    :math:`\mathrm{argmin}_{\mathbf v} C(\mathbf v)`, namely the choice of variables
    :math:`\mathbf v` that minimizes :math:`C(\mathbf v)`. The function then calculates the values
    of arbitrary output functions :math:`\{F_j(\mathbf v_\mathrm{optimized})\}` with that choice
    of variables.

    This function represents the cost and output functions as nodes of a graph.
    This graph defines the input optimization variables :math:`\mathbf v`, and how these variables
    are transformed into the corresponding cost and output quantities. You build the graph from
    primitive nodes defined in the graph of the Boulder Opal package.
    Each such node, which can be identified by a name, represents a function of the previous nodes
    in the graph (and thus, transitively, a function of the input variables).
    You can use any named scalar real-valued node :math:`s` as the cost function, and any named
    nodes :math:`\{s_j\}` as outputs.

    After you provide a cost function :math:`C(\mathbf v)` (via a graph), this function runs an
    optimization process :math:`N` times, each with random initial variables, to identify :math:`N`
    local minima of the cost function, and then takes the variables corresponding to the best
    such minimum as :math:`\mathbf v_\mathrm{optimized}`.

    The optimizer will carry out the gradient-free optimization for a number of iterations
    set by `iteration_count`. If a `target_cost` is passed and the cost becomes less
    than or equal to this value then the optimizer will terminate early.

    The gradient-free optimizer used here is the covariance matrix adaptation evolution strategy
    (CMA-ES) based optimizer. For more detail on CMA-ES see
    `CMA-ES <https://en.wikipedia.org/wiki/CMA-ES>`_ on Wikipedia.

    Examples
    --------
    Perform a simple optimization with variables that are initialized to given values.

    >>> graph = bo.Graph()
    >>> variables = graph.optimization_variable(
    ...     2, -1, 1, initial_values=np.array([0.6, 0.]), name="variables"
    ... )
    >>> x, y = variables[0], variables[1]
    >>> cost = (x - 0.5) ** 2 + (y - 0.1) ** 2
    >>> cost.name = "cost"
    >>> result = bo.run_gradient_free_optimization(
    ...     graph=graph, cost_node_name="cost", output_node_names="variables", seed=0
    ... )
    >>> result["cost"], result["output"]
        (5.166836148557636e-22, {'variables': {'value': array([0.5, 0.1])}})

    See also the `How to optimize controls using gradient-free optimization user guide
    <https://docs.q-ctrl.com/boulder-opal/user-guides/how-to-
    optimize-controls-using-gradient-free-optimization>`_.
    """
    check_optimization_node_in_graph(graph)
    check_initial_value_for_optimization_node(graph)
    check_cost_node(cost_node_name, graph)

    output_node_names = validate_output_node_names(output_node_names, graph)
    check_cost_node_for_optimization_graph(
        graph, cost_node_name, output_node_names, check_gradient_nodes=False
    )

    result = run_gradient_free_optimization_workflow(
        graph=graph,
        cost_node_name=cost_node_name,
        output_node_names=output_node_names,
        iteration_count=nullable(ScalarT.INT("iteration_count").gt(0), iteration_count),
        target_cost=nullable(ScalarT.REAL("target_cost"), target_cost),
        optimization_count=ScalarT.INT("optimization_count").gt(0)(optimization_count),
        cost_history_scope=validate_enum(HistoryScope, cost_history_scope),
        seed=nullable(ScalarT.INT("seed").ge(0), seed),
    )
    return result
