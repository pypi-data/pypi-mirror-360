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

from dataclasses import (
    asdict,
    dataclass,
)
from typing import (
    Any,
    Callable,
    Optional,
)

import numpy as np

from boulderopal._configuration.configuration import in_local_mode
from boulderopal._core import closed_loop_step_workflow
from boulderopal._validation import (
    ArrayT,
    Checker,
    ScalarT,
    nullable,
)
from boulderopal.closed_loop._optimizers import (
    ALLOWED_OPTIMIZERS,
    ClosedLoopOptimizer,
    Cmaes,
    GaussianProcess,
    NeuralNetwork,
    SimulatedAnnealing,
)
from boulderopal.cloud._utils import shut_down_machines


@dataclass
class Results:
    """
    Results from evaluating the closed-loop optimization cost function.

    Parameters
    ----------
    parameters : np.ndarray
        The parameters at which the cost function was evaluated
        as a 2D array of shape ``(test_point_count, parameter_count)``.
    costs : np.ndarray
        The evaluated costs from the cost function
        as a 1D array of shape ``(test_point_count,)``.
    cost_uncertainties : np.ndarray or None, optional
        The uncertainties associated with the costs.
        If provided, must have the same shape as costs.
        Defaults to None, in which case there is no uncertainty associated to the costs.

    See Also
    --------
    boulderopal.closed_loop.step : Perform a single step in a closed-loop optimization.
    """

    parameters: np.ndarray
    costs: np.ndarray
    cost_uncertainties: Optional[np.ndarray] = None

    def __post_init__(self) -> None:
        self.parameters = ArrayT.REAL("parameters").ndim(2)(self.parameters)
        self.costs = (
            ArrayT.REAL("costs")
            .ndim(1)
            .shape((self.parameters.shape[0],), "one item per measurement")(self.costs)
        )
        self.cost_uncertainties = nullable(
            ArrayT.REAL("cost_uncertainties")
            .ndim(1)
            .shape(self.costs.shape, "same as the costs"),
            self.cost_uncertainties,
        )


def step(
    optimizer: ClosedLoopOptimizer | str,
    results: Optional[Results] = None,
    test_point_count: Optional[int] = None,
) -> dict:
    """
    Perform a single step in a closed-loop optimization.

    Parameters
    ----------
    optimizer : ClosedLoopOptimizer or str
        The optimizer to be used in the minimization of the cost function, or an optimizer state.
        If this is the first optimization step pass an instance of a closed-loop optimizer class.
        In subsequent steps, pass the optimizer state as returned by the previous step.
    results : Results or None, optional
        Results from evaluating the cost function. You can omit this parameter if you want to
        generate more test points but have not yet evaluated the cost function.
        Defaults to None.
        Note that some optimizers might have extra requirements of results needed for the first
        optimization step. You can check the documentation of the individual optimizers for details.
    test_point_count : int or None, optional
        Requested number of test points to be generated from the optimizer at this step.
        This is a hint to the optimizer, the number of returned test points might be different.
        You should set this value based on the number of test points you can efficiently calculate
        as a batch or in parallel. Typically, optimizers will return at least this many points,
        but they might return more (for example if a certain number of points is required in order
        to move the algorithm to the next state) or, occasionally, fewer (for example if moving the
        algorithm to the next state requires the evaluation of a specific point and nothing more).

    Returns
    -------
    dict
        A dictionary containing the optimization step result, with the following keys:

        ``test_points``
            New test points at which the cost function should be evaluated
            for the next optimization step.
        ``state``
            The optimizer state, to be provided in the next step.
        ``metadata``
            Metadata associated with the calculation.
            No guarantees are made about the contents of this metadata dictionary;
            the contained information is intended purely to help interpret the results of the
            calculation on a one-off basis.

    See Also
    --------
    boulderopal.closed_loop.optimize :
        Run a closed-loop optimization to find a minimum of the given cost function.
    boulderopal.execute_graph : Evaluate generic functions.
    boulderopal.run_gradient_free_optimization :
        Perform model-based optimization without using gradient values.
    boulderopal.run_optimization :
        Perform gradient-based deterministic optimization of generic real-valued functions.
    boulderopal.run_stochastic_optimization :
        Perform gradient-based stochastic optimization of generic real-valued functions.
    """
    Checker.TYPE(
        isinstance(optimizer, (*ALLOWED_OPTIMIZERS, str)),
        "You must provide either an optimizer or an optimizer state.",
        {"type(optimizer)": type(optimizer)},
    )

    if isinstance(optimizer, ClosedLoopOptimizer):
        closed_loop_optimizer: dict[str, Any] | str = asdict(optimizer)
    else:
        closed_loop_optimizer = optimizer

    test_point_count = nullable(ScalarT.INT("test_point_count").gt(0), test_point_count)

    return closed_loop_step_workflow(
        optimizer=closed_loop_optimizer,
        results=None if results is None else asdict(results),
        test_point_count=test_point_count,
    )


def _generate_random_initial_points(optimizer: ClosedLoopOptimizer) -> np.ndarray:
    """
    Generate a random array of initial points depending on the chosen optimizer.
    """
    parameter_count = optimizer.bounds.values.shape[0]

    if isinstance(optimizer, Cmaes):
        if optimizer.population_size is not None:
            point_count = optimizer.population_size
        else:
            point_count = int(4 + np.floor(3 * np.log(parameter_count)))

    elif isinstance(optimizer, (GaussianProcess, NeuralNetwork, SimulatedAnnealing)):
        point_count = 2 * parameter_count

    else:
        # This should never be raised as we validate the optimizer in the main function.
        raise TypeError(
            "The type of the optimizer is not valid.",
            {"type(optimizer)": type(optimizer)},
        )

    assert hasattr(optimizer, "seed")  # Make mypy happy.
    rng = np.random.default_rng(seed=optimizer.seed)
    bounds_ = optimizer.bounds.values
    return rng.uniform(
        low=bounds_[:, 0], high=bounds_[:, 1], size=(point_count, len(bounds_))
    )


def optimize(
    cost_function: Callable,
    optimizer: ClosedLoopOptimizer | str,
    initial_parameters: Optional[np.ndarray] = None,
    target_cost: Optional[float] = None,
    max_iteration_count: int = 100,
    callback: Optional[Callable] = None,
    verbose: bool = True,
    auto_machine_management: bool = False,
) -> dict:
    """
    Run a closed-loop optimization to find a minimum of the given cost function.

    This is an iterative process, where the optimizer generates and tests a set of points.
    After several iterations the distribution of generated test points should converge
    to low values of the cost function. You can use this approach when your system is too
    complicated to model.

    The provided cost function must take a 2D array of shape ``(test_point_count, parameter_count)``
    as input and return a 1D array of costs of length `test_point_count`.
    Alternatively, it can return a 2D array of shape ``(2, test_point_count)``, where the first
    row represents the costs and the second row represents their associated uncertainties.

    For best results, you should provide a set of `initial_parameters` to start the optimization.
    The performance and convergence of the optimizer might change depending on these values.
    If you don't pass `initial_parameters`, randomly sampled values inside the bounds are used.
    The number of initial values is set to the population size for CMA-ES and to
    ``2 * parameter_count`` for other optimizers.

    Parameters
    ----------
    cost_function : Callable
        The cost function to minimize, as a callable that takes a 2D NumPy array of parameters and
        returns either a 1D NumPy array of costs, or a 2D NumPy arrays of costs and uncertainties.
        The cost function should always return the same type of output
        (either always return uncertainties or never return them).
    optimizer : ClosedLoopOptimizer or str
        The optimizer to be used in the minimization of the cost function, or an optimizer state.
        If this is the first optimization step, pass an instance of a closed-loop optimizer class.
        If you want to resume an optimization, pass the optimizer state as of the last step.
    initial_parameters : np.ndarray or None, optional
        The initial values of the parameters to use in the optimization,
        as a 2D NumPy array of shape ``(test_point_count, parameter_count)``.
        If not passed, random values uniformly sampled inside the optimizer bounds are used.
        If you provide an optimizer state, you must provide an array of initial parameters.
    target_cost : float or None, optional
        The target cost.
        If passed, the optimization will halt if the best cost is below the given value.
    max_iteration_count : int, optional
        The maximum number of iterations.
        Defaults to 100.
    callback : Callable or None, optional
        A function that takes in the current set of parameters, a 2D NumPy array of shape
        ``(test_point_count, parameter_count)``, and returns a bool.
        The function is evaluated once during each iteration with the
        current parameters. If it returns True, the optimization is halted.
    verbose : bool, optional
        Whether to print out information about the optimization cycle.
        Defaults to True.
    auto_machine_management : bool, optional
        Whether to shut down the cloud machines after the step function is finished to
        save resources.
        Defaults to False.

    Returns
    -------
    dict
        A dictionary containing the optimization result, with the following keys:

        ``cost``
            The lowest cost found during the optimization.
        ``parameters``
            The optimal parameters associated to the lowest cost.
        ``cost_history``
            The history of best cost values up to each optimization step.
        ``step``
            A dictionary containing the information about the last optimization step,
            to be used to resume the optimization.
            It contains the optimizer ``state`` and the ``test_points`` at which
            the cost function should be evaluated next.

    See Also
    --------
    boulderopal.closed_loop.step :
        Perform a single step in a closed-loop optimization.
    boulderopal.execute_graph : Evaluate generic functions.
    boulderopal.run_gradient_free_optimization :
        Perform model-based optimization without using gradient values.
    boulderopal.run_optimization :
        Perform gradient-based deterministic optimization of generic real-valued functions.
    boulderopal.run_stochastic_optimization :
        Perform gradient-based stochastic optimization of generic real-valued functions.

    Notes
    -----
    At each iteration, the cost function will be called with the same number of data points as
    initially provided in `initial_parameters`. However, in some situations the optimizer might
    request more points (for example, if a certain number of points is required in order to move
    the algorithm to the next state) or, occasionally, fewer (for example, if moving the algorithm
    to the next state requires the evaluation of a specific point and nothing more).

    If the optimization loop is halted via a `KeyboardInterrupt` then the function returns
    the best results obtained in the optimization thus far.

    This function will make a server call at each iteration.
    Each call will be associated with a different `action_id`.
    The `action_id` of the final iteration can be found in
    `result["step"]["metadata"]["action_id"]` where
    `result` is the dictionary returned by the function.

    Additionally, the `auto_machine_management` flag can help you preserve your Boulder Opal
    cloud computing resources by automatically shutting down machines in your environment
    after each step, provided there are no tasks queued or running.
    This feature is particularly useful if your cost function takes a long time to run.
    However, keep in mind that shutting down machines may result in some delay
    when they are brought back online for the next iteration.
    Note that you shouldn't set the flag if the cost function calls the Boulder Opal API.
    """

    def verbose_print(message: str) -> None:
        if verbose:
            print(message)

    initial_parameters = nullable(
        ArrayT.REAL("initial_parameters").ndim(2), initial_parameters
    )

    Checker.TYPE(
        isinstance(optimizer, (*ALLOWED_OPTIMIZERS, str)),
        "You must provide either an optimizer or an optimizer state.",
        {"type(optimizer)": type(optimizer)},
    )

    if isinstance(optimizer, ClosedLoopOptimizer):
        if initial_parameters is not None:
            Checker.VALUE(
                np.all(
                    (initial_parameters >= optimizer.bounds.values[:, 0])
                    & (initial_parameters <= optimizer.bounds.values[:, 1])
                ),
                "The initial parameters must be within the optimizer bounds.",
                {
                    "initial_parameters": initial_parameters,
                    "optimizer.bounds.values": optimizer.bounds.values,
                },
            )
        else:
            initial_parameters = _generate_random_initial_points(optimizer)
        closed_loop_optimizer: dict | str = asdict(optimizer)
        verbose_print(
            "Running closed loop optimization\n"
            "-----------------------------------------------\n"
            f"  Optimizer             : {optimizer.method_name}\n"
            f"  Number of test points : {initial_parameters.shape[0]}\n"
            f"  Number of parameters  : {initial_parameters.shape[1]}\n"
            "-----------------------------------------------\n"
        )
    else:
        Checker.VALUE(
            initial_parameters is not None,
            "If you provide an optimizer state, you must provide initial parameters.",
            {"initial_parameters": initial_parameters, "optimizer": optimizer},
        )
        assert isinstance(initial_parameters, np.ndarray)  # Make mypy happy.

        closed_loop_optimizer = optimizer
        verbose_print(
            "Resuming closed loop optimization\n"
            "-----------------------------------------------\n"
            f"  Number of test points : {initial_parameters.shape[0]}\n"
            f"  Number of parameters  : {initial_parameters.shape[1]}\n"
            "-----------------------------------------------\n"
        )

    max_iteration_count = ScalarT.INT("max_iteration_count").gt(0)(max_iteration_count)

    test_parameters = initial_parameters
    test_point_count = initial_parameters.shape[0]

    # Obtain initial costs.
    verbose_print("Calling cost function…")
    cost_return = cost_function(test_parameters)

    Checker.VALUE(
        isinstance(cost_return, np.ndarray) and cost_return.ndim in (1, 2),
        "The cost function must return a 1D or 2D array.",
        {"cost_function(test_parameters)": cost_return},
    )

    if cost_return.ndim == 2:
        Checker.VALUE(
            cost_return.shape == (2, len(initial_parameters)),
            "If the cost function returns a 2D array, it must be of shape "
            "``(2, test_point_count)``.",
            {"cost_function(test_parameters)": cost_return},
        )
        uncertainties_returned = True
        costs, cost_uncertainties = cost_return

    else:
        Checker.VALUE(
            cost_return.shape == (len(initial_parameters),),
            "If the cost function returns a 1D array, it must be of length `test_point_count`.",
            {"cost_function(test_parameters)": cost_return},
        )

        uncertainties_returned = False
        costs = cost_return
        cost_uncertainties = None

    best_cost_overall, best_parameters_overall = min(
        zip(costs, test_parameters), key=lambda params: params[0]
    )
    verbose_print(f"  Initial best cost: {best_cost_overall:.3e}")

    # Store the cost history.
    best_cost_history = [best_cost_overall]

    # Empty step result in case the loop is broken on the first iteration.
    step_result = {}

    if in_local_mode():
        verbose_print("\nAuto machine management will have no effect in local mode.")
        auto_machine_management = False

    # Run the optimization loop until a halting condition is met.
    try:
        for iteration_count in range(max_iteration_count):
            results = Results(
                parameters=test_parameters,
                costs=costs,
                cost_uncertainties=cost_uncertainties,
            )

            # Call the automated closed-loop optimizer and obtain the next set of test points.
            verbose_print("\nRunning optimizer…")
            step_result = closed_loop_step_workflow(
                optimizer=closed_loop_optimizer,
                results=asdict(results),
                test_point_count=test_point_count,
            )

            # Shut down machines to save resources.
            if auto_machine_management:
                verbose_print("\nShutting down machines to save resources…")
                shut_down_machines()

            # Retrieve the data returned by the closed-loop optimizer.
            closed_loop_optimizer = step_result["state"]
            test_parameters = step_result["test_points"]

            # Obtain costs.
            verbose_print("Calling cost function…")
            if uncertainties_returned:
                costs, cost_uncertainties = cost_function(test_parameters)
            else:
                costs = cost_function(test_parameters)

            # Record the best results after this iteration.
            best_cost, best_parameters = min(
                zip(costs, test_parameters), key=lambda params: params[0]
            )

            # Compare last best results with best result overall.
            if best_cost < best_cost_overall:
                best_cost_overall = best_cost
                best_parameters_overall = best_parameters

            # Print the current best cost.
            verbose_print(
                f"  Best cost after {iteration_count+1} iterations: {best_cost_overall:.3e}"
            )

            # Store the current best cost.
            best_cost_history.append(best_cost_overall)

            if callback is not None:
                if callback(test_parameters):
                    verbose_print(
                        "\nCallback condition satisfied. Stopping the optimization."
                    )
                    break

            # Check if desired threshold has been achieved.
            if target_cost is not None:
                if best_cost_overall < target_cost:
                    verbose_print("\nTarget cost reached. Stopping the optimization.")
                    break
        else:
            verbose_print(
                "\nMaximum iteration count reached. Stopping the optimization."
            )

    # Exit loop (and return latest results)
    # if a KeyboardInterrupt or an Exception is caught.
    except KeyboardInterrupt:
        print("\nCalculation interrupted. Stopping the optimization.")

    except Exception as exc:  # pylint: disable=broad-exception-caught
        print(
            f"\nSomething went wrong after {iteration_count} iterations. "
            "Stopping the optimization and returning latest results. "
            "See the following for more details:"
        )
        print(", ".join([str(arg) for arg in exc.args]))

    return {
        "cost": best_cost_overall,
        "parameters": best_parameters_overall,
        "cost_history": best_cost_history,
        "step": step_result,
    }
