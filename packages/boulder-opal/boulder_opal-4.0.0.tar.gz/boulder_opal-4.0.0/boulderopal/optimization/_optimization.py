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
    Optional,
    Union,
    overload,
)

from boulderopal._core import run_optimization_workflow
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
from boulderopal.cloud._async import BoulderOpalJob
from boulderopal.graph._graph import Graph


class HistoryScope(Enum):
    """
    Configuration for the history data returned from a graph-based optimizer.

    Attributes
    ----------
    NONE
        Do not return any history information.

    ITERATION_VALUES
        Return the value obtained at each iteration and optimization.

    HISTORICAL_BEST
        Return the best values reached up to each iteration for each optimization.

    ALL
        Return both the values obtained at each iteration and the historical best values.

    See also
    --------
    boulderopal.run_gradient_free_optimization :
        Perform model-based optimization without using gradient values.
    boulderopal.run_optimization :
        Perform gradient-based deterministic optimization of generic real-valued functions.
    boulderopal.run_stochastic_optimization :
        Perform gradient-based stochastic optimization of generic real-valued functions.
    """

    NONE = "NONE"
    ITERATION_VALUES = "ITERATION_VALUES"
    HISTORICAL_BEST = "HISTORICAL_BEST"
    ALL = "ALL"


@overload
def run_optimization(
    graph: Graph,
    cost_node_name: str,
    output_node_names: str | list[str],
    max_iteration_count: Optional[int] = None,
    target_cost: Optional[float] = None,
    cost_tolerance: Optional[float] = None,
    optimization_count: int = 4,
    cost_history_scope: HistoryScope = HistoryScope.NONE,
    seed: Optional[int] = None,
    *,
    run_async: Literal[False] = False,
) -> dict: ...


@overload
def run_optimization(
    graph: Graph,
    cost_node_name: str,
    output_node_names: str | list[str],
    max_iteration_count: Optional[int] = None,
    target_cost: Optional[float] = None,
    cost_tolerance: Optional[float] = None,
    optimization_count: int = 4,
    cost_history_scope: HistoryScope = HistoryScope.NONE,
    seed: Optional[int] = None,
    *,
    run_async: Literal[True],
) -> BoulderOpalJob: ...


def run_optimization(
    graph: Graph,
    cost_node_name: str,
    output_node_names: str | list[str],
    max_iteration_count: Optional[int] = None,
    target_cost: Optional[float] = None,
    cost_tolerance: Optional[float] = None,
    optimization_count: int = 4,
    cost_history_scope: HistoryScope = HistoryScope.NONE,
    seed: Optional[int] = None,
    *,
    run_async: bool = False,
) -> Union[dict, BoulderOpalJob]:
    r"""
    Perform gradient-based deterministic optimization of generic real-valued functions.

    Use this function to determine a choice of variables that minimizes the value of a scalar
    real-valued cost function of those variables. You express that cost function as a graph
    describing how the input variables are transformed into the cost value.

    Note that this function will pick a different initial guess for each optimization run.
    You can provide initial values (or a list of them of the same length) for the optimization
    variables in the graph, and the optimizer will start with those values.
    If the `optimization_count` is larger than the number of provided initial values,
    the optimizer will use random values after consuming all available initial values.

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
    max_iteration_count : int or None, optional
        The maximum number of cost evaluations to perform. You can set this as an early stop
        condition for the optimizer. Defaults to None, which means that the optimizer runs
        until it converges.
    target_cost : float or None, optional
        A target value of the cost that you can set as an early stop condition for the optimizer.
        If the cost becomes equal or smaller than this value, the optimization halts.
        Defaults to None, meaning that the optimizer runs until it converges.
    cost_tolerance : float or None, optional
        The tolerance :math:`\mathrm{tol}` to check whether the cost function has converged.
        You can set this as an early stop condition for the optimizer.
        The optimizer stops when the improvement of the cost function over the iterations is below
        the tolerance. That is, it stops when
        :math:`(C_j - C_{j+1}) / \max(|C_j|, |C_{j+1}|, 1) \le \mathrm{tol}`.
        Defaults to None, meaning the optimizer handles the tolerance automatically.
        You can try different values depending on your optimization problem.
        A recommended starting value is about 1e-9.
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
    boulderopal.closed_loop.step :
        Perform a single step in a closed-loop optimization.
    boulderopal.execute_graph :
        Evaluate generic functions.
    boulderopal.run_gradient_free_optimization :
        Perform model-based optimization without using gradient values.
    boulderopal.run_stochastic_optimization :
        Perform gradient-based stochastic optimization of generic real-valued functions.
    boulderopal.cloud.BoulderOpalJob :
        An async Boulder Opal job submitted to the cloud.

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

    A common use-case for this function is to determine controls for a quantum system that yield
    an optimal gate: the variables :math:`\mathbf v` parameterize the controls to be optimized,
    and the cost function :math:`C(\mathbf v)` is the operational infidelity describing the quality
    of the resulting gate relative to a target gate. When combined with the node definitions in the
    Boulder Opal package, which make it convenient to define such cost functions, this function
    provides a highly configurable framework for quantum control that encapsulates other common
    tools such as gradient ascent pulse engineering [1]_ and chopped random basis (CRAB)
    optimization [2]_.

    The optimizer will carry out the gradient-based optimization until it converges to a minimum.
    You can set up early stop conditions such as a target cost or a maximum number of cost
    evaluations via the `target_cost` and `max_iteration_count` parameters. If both are provided,
    the optimizer will terminate when either of the two conditions is satisfied.

    References
    ----------
    .. [1] `N. Khaneja, T. Reiss, C. Kehlet, T. Schulte-Herbrüggen, and S. J. Glaser,
            Journal of Magnetic Resonance 172, 2 (2005).
            <https://doi.org/10.1016/j.jmr.2004.11.004>`_

    .. [2] `P. Doria, T. Calarco, and S. Montangero,
            Physical Review Letters 106, 190501 (2011).
            <https://doi.org/10.1103/PhysRevLett.106.190501>`_

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
    >>> result = bo.run_optimization(
    ...     graph=graph, cost_node_name="cost", output_node_names="variables"
    ... )
    >>> result["cost"], result["output"]
        (0.0, {'variables': {'value': array([0.5, 0.1])}})

    See also the `How to optimize controls in arbitrary quantum systems using graphs
    <https://docs.q-ctrl.com/boulder-opal/user-guides/how-to-
    optimize-controls-in-arbitrary-quantum-systems-using-graphs>`_ user guide.
    """

    check_optimization_node_in_graph(graph)
    check_initial_value_for_optimization_node(graph)
    check_cost_node(cost_node_name, graph)

    output_node_names = validate_output_node_names(output_node_names, graph)
    check_cost_node_for_optimization_graph(graph, cost_node_name, output_node_names)

    result = run_optimization_workflow(
        graph=graph,
        optimization_count=ScalarT.INT("optimization_count").gt(0)(optimization_count),
        cost_node_name=cost_node_name,
        output_node_names=output_node_names,
        target_cost=nullable(ScalarT.REAL("target_cost"), target_cost),
        max_iteration_count=nullable(
            ScalarT.INT("max_iteration_count").gt(0), max_iteration_count
        ),
        cost_tolerance=nullable(ScalarT.REAL("cost_tolerance").gt(0), cost_tolerance),
        cost_history_scope=validate_enum(HistoryScope, cost_history_scope),
        seed=nullable(ScalarT.INT("seed").ge(0), seed),
        run_async=run_async,
    )
    return result
