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
"""
Classes associated to the closed-loop optimizers.
"""

from __future__ import annotations

from abc import ABC
from dataclasses import (
    dataclass,
    field,
)
from enum import Enum
from typing import (
    Any,
    Optional,
)

import numpy as np

from boulderopal._validation import (
    ArrayT,
    Checker,
    ScalarT,
    nullable,
    validate_enum,
)


class BoundType(Enum):
    """
    Boundary type for parameter bounds.

    Attributes
    ----------
    NON_PERIODIC
        Non-periodic boundaries. This means the optimizer will clip the parameter values
        to remain within the bounds any time it takes a step outside of the bounds.

    PERIODIC
        Periodic boundaries. This means the optimizer will modulo parameter values
        back within the bounds any time it takes a step outside of the bounds.

    See also
    --------
    boulderopal.closed_loop.Bounds :
        A box constraint with which you can define the (inclusive) bounds and their type
        for each optimizable parameter in your optimization.
    """

    NON_PERIODIC = "NON_PERIODIC"
    PERIODIC = "PERIODIC"


@dataclass
class Bounds:
    """
    A box constraint with which you can define the (inclusive) bounds and their type
    for each optimizable parameter in your optimization.

    Parameters
    ----------
    values : np.ndarray
        The per-parameter bounds on the test points.
        The bounds must be a NumPy array of shape ``(parameter_count, 2)`` where the trailing
        axis are the bounds for each parameter (with the lower bound first, followed by the upper
        bound).
    bound_type : BoundType or list[BoundType], optional
        The boundary type for the bounds. You can provide a single BoundType to be used
        for all parameters, or a list with a BoundType for each parameter.
        Defaults to non-periodic bounds.
    """

    values: np.ndarray
    bound_type: BoundType | list[BoundType] | list[str] = BoundType.NON_PERIODIC

    def __post_init__(self) -> None:
        self.values = _validate_bounds(self.values)
        if isinstance(self.bound_type, list):
            Checker.VALUE(
                len(self.bound_type) == self.values.shape[0],
                "If you provide a list of bound types, it must have as many items as parameters.",
                {
                    "parameter count": self.values.shape[0],
                    "len(bound_type)": len(self.bound_type),
                },
            )
            self.bound_type = [
                validate_enum(BoundType, bound_type) for bound_type in self.bound_type
            ]
        else:
            bound_type = validate_enum(BoundType, self.bound_type)
            self.bound_type = [bound_type] * self.values.shape[0]


@dataclass
class ClosedLoopOptimizer(ABC):  # pylint: disable=too-few-public-methods
    """
    Abstract class for optimizers used in closed-loop optimization.

    To create an optimizer, use one of the concrete classes.

    See Also
    --------
    boulderopal.closed_loop.Cmaes :
        Class describing the covariance matrix adaptation evolution strategy (CMA-ES) optimizer.
    boulderopal.closed_loop.GaussianProcess :
        Class describing the Gaussian-process-based optimizer.
    boulderopal.closed_loop.NeuralNetwork :
        Class describing the neural-network-based optimizer.
    boulderopal.closed_loop.SimulatedAnnealing :
        Class describing the simulated annealing optimizer.
    """

    bounds: Bounds
    method_name: str

    def __setattr__(self, name: str, value: Any) -> None:
        if name == "method_name":
            raise RuntimeError(
                "Mutating the `method_name` of the optimizer is not allowed."
            )
        super().__setattr__(name, value)


@dataclass
class Cmaes(ClosedLoopOptimizer):
    r"""
    The covariance matrix adaptation evolution strategy (CMA-ES) optimizer.

    Parameters
    ----------
    bounds : Bounds
        The bounds on the test points.
    initial_mean : np.ndarray or None, optional
        The per-parameter initial mean for the multivariate normal distribution.
        Defaults to None, in which case a random value inside the bounds is used for each parameter.
        If set, each parameter's mean must be within its corresponding bounds.
    initial_step_size : float or None, optional
        The initial step size for the multivariate normal distribution from which new test
        points are sampled.
        Defaults to one.
    population_size : int or None, optional
        The population size of the test candidates. It is recommended to use a population size of
        at least :math:`P = 4 + \lfloor 3 \times \log N \rfloor`, where :math:`N` is the number of
        optimizable parameters, :math:`\log` is the natural logarithm, and :math:`\lfloor x \rfloor`
        is the floor function.
        Defaults to :math:`P`.
    seed : int or None, optional
        Seed for the random number generator used in the optimizer.
        If set, must be a non-negative integer.
        Use this option to generate deterministic results from the optimizer.

    Notes
    -----
    The CMA-ES optimizer uses a multivariate normal distribution to generate new test points.
    From an `initial_mean` and `initial_step_size`, this distribution is continually
    updated using an evolutionary strategy, with each update depending on the previous values and
    the current set of results.
    New test points are sampled from the distribution until convergence is reached.

    For more detail on CMA-ES see `CMA-ES <https://en.wikipedia.org/wiki/CMA-ES>`_ on Wikipedia.
    """

    bounds: Bounds
    initial_mean: Optional[np.ndarray] = None
    initial_step_size: Optional[float] = None
    population_size: Optional[int] = None
    seed: Optional[int] = None
    method_name: str = field(default="CMA-ES", init=False)

    def __post_init__(self) -> None:
        self.initial_mean = nullable(
            ArrayT.REAL("initial_mean").ndim(1), self.initial_mean
        )
        self.initial_step_size = nullable(
            ScalarT.REAL("initial_step_size").gt(0), self.initial_step_size
        )
        self.population_size = nullable(
            ScalarT.INT("population_size").gt(0), self.population_size
        )
        self.seed = nullable(ScalarT.INT("seed").ge(0), self.seed)

        if self.initial_mean is not None:
            Checker.VALUE(
                len(self.initial_mean) == len(self.bounds.values),
                "The initial mean and the bounds must have the same length.",
                {
                    "len(initial_mean)": len(self.initial_mean),
                    "len(bounds.values)": len(self.bounds.values),
                },
            )
            for mean, bound in zip(self.initial_mean, self.bounds.values):
                Checker.VALUE(
                    bound[0] <= mean <= bound[1],
                    "The initial mean must be within the bounds.",
                    {
                        "initial_mean": self.initial_mean,
                        "bounds.values": self.bounds.values,
                    },
                )


@dataclass
class GaussianProcess(ClosedLoopOptimizer):
    r"""
    The Gaussian process optimizer.

    Parameters
    ----------
    bounds : Bounds
        The bounds on the test points.
    length_scale_bounds : np.ndarray or None, optional
        The per-parameter length scale bounds on the test points.
        The bounds must be a NumPy array of shape ``(parameter_count, 2)`` where the trailing
        axis are the bounds for each parameter (with the lower bound first, followed by the upper
        bound).
        If not specified,  :py:obj:`~closed_loop.optimize` will pick a value derived from the
        `bounds` by picking orders of magnitudes below/above the sidelength for each box axis.
    seed : int or None, optional
        Seed for the random number generator used in the optimizer.
        If set, must be a non-negative integer.
        Use this option to generate deterministic results from the optimizer.

    Notes
    -----
    The Gaussian process is defined by the kernel

    .. math::
        k({\mathbf x}_j, {\mathbf x}_k)
            = \exp \left(-\frac{1}{2} ( {\mathbf x}_j - {\mathbf x}_k )^\top
                \Sigma^{-2} ( {\mathbf x}_j - {\mathbf x}_k )\right) ,

    where :math:`{\mathbf x}_j` is an :math:`n`-dimensional vector representing the
    :math:`j`-th test point, :math:`\Sigma= {\mathrm diag}(l_1, \cdots, l_n)`
    is an :math:`n \times n` diagonal matrix, and :math:`\{ l_j \}` are the length scales.
    The length scales are tuned while training the model, within the bounds set by the
    `length_scale_bounds` parameter. Roughly speaking, the amount a parameter needs to change
    to impact the optimization cost should lie within the length scale bounds.

    It's recommended to provide non-zero `cost_uncertainty` to :py:obj:`~closed_loop.optimize`
    when using this optimizer, otherwise you might encounter a numerical error when the optimizer
    tries to fit the kernel with your input data. If the error persists, try increasing the
    `cost_uncertainty` value or decreasing the minimum length scale bound. However, such numerical
    error is also an indication that your data might not be suitable to be modelled by a
    Gaussian process, and in that case, consider using a different closed-loop optimizer.

    For more detail on Gaussian processes see
    `Gaussian process <https://en.wikipedia.org/wiki/Gaussian_process>`_ on Wikipedia.
    """

    bounds: Bounds
    length_scale_bounds: Optional[np.ndarray] = None
    seed: Optional[int] = None
    method_name: str = field(default="Gaussian process", init=False)

    def __post_init__(self) -> None:
        if self.length_scale_bounds is not None:
            self.length_scale_bounds = _validate_bounds(
                self.length_scale_bounds, "length scale bounds"
            )

        self.seed = nullable(ScalarT.INT("seed").ge(0), self.seed)

        if self.length_scale_bounds is not None:
            Checker.VALUE(
                len(self.length_scale_bounds) == len(self.bounds.values),
                "The length scale bounds and the bounds must have the same length.",
                {
                    "len(length_scale_bounds)": len(self.length_scale_bounds),
                    "len(bounds.values)": len(self.bounds.values),
                },
            )


@dataclass
class NeuralNetwork(ClosedLoopOptimizer):
    """
    The neural network optimizer.

    Parameters
    ----------
    bounds : Bounds
        The bounds on the test points.
    seed : int or None, optional
        Seed for the random number generator used in the optimizer.
        If set, must be a non-negative integer.
        Use this option to generate deterministic results from the optimizer.

    Notes
    -----
    The neural network optimizer builds and trains a neural network to fit the cost landscape with
    the data it receives. Then a set of test points are returned, which minimize the neural
    network's fitted cost landscape. A gradient based optimizer is used to minimize this landscape,
    with the points starting from different random initial values.

    This method is recommended when you can provide a large amount of data about your system.

    The network architecture used by this optimizer is chosen for its good performance on a variety
    of quantum control tasks.

    For best results, you should pass an array of `initial_parameters` evenly sampled
    over the whole parameter space.
    """

    bounds: Bounds
    seed: Optional[int] = None
    method_name: str = field(default="neural network", init=False)

    def __post_init__(self) -> None:
        self.seed = nullable(ScalarT.INT("seed").ge(0), self.seed)


@dataclass
class SimulatedAnnealing(ClosedLoopOptimizer):
    r"""
    The simulated annealing optimizer.

    Parameters
    ----------
    bounds : Bounds
        The bounds on the test points.
    temperatures : np.ndarray
        The array of initial per-parameter annealing temperatures :math:`T_0` used to generate
        new test points.
        Higher temperatures correspond to higher exploration.
        The per-parameter adjustments from the current test point are sampled from Cauchy
        distributions with scales given by temperatures.
        The temperatures are currently implemented to decay such that each temperature
        at the k-th step is set according to :math:`T_k=\frac{T_0}{1+k}`.
        All temperatures must be positive.
    temperature_cost : float
        The parameter for controlling the optimizer’s greediness.
        A high cost temperature allows the optimizer to explore test points which may not
        immediately improve the cost. A higher level of exploration can be helpful for
        more difficult optimization problems. The cost temperature is set to decay
        according to the same schedule as the temperatures.
        Must be positive.
    seed : int or None, optional
        Seed for the random number generator used in the optimizer.
        If set, must be a non-negative integer.
        Use this option to generate deterministic results from the optimizer.

    Notes
    -----
    This simulated annealing performs a temperature based random walk within the parameter `bounds`.
    The new test points are sampled from a distribution whose variance is given by the current
    `temperatures`. Higher `temperatures` translate to high levels of exploration, which can be
    useful for non-convex optimization. The `temperature_cost` parameter can be set independently of
    the `temperatures`, and controls the overall greediness of each update. A high
    `temperature_cost` allows the optimizer to accept updates which do not immediately improve the
    cost. Both `temperatures` and the `temperature_cost` automatically decay between iterations.

    For more information on this method see
    `simulated annealing <https://en.wikipedia.org/wiki/Simulated_annealing>`_ on Wikipedia.
    """

    bounds: Bounds
    temperatures: np.ndarray
    temperature_cost: float
    seed: Optional[int] = None
    method_name: str = field(default="simulated annealing", init=False)

    def __post_init__(self) -> None:
        self.temperatures = ArrayT.REAL("temperatures").ndim(1).gt(0)(self.temperatures)
        self.temperature_cost = ScalarT.REAL("temperature_cost").gt(0)(
            self.temperature_cost
        )
        self.seed = nullable(ScalarT.INT("seed").ge(0), self.seed)

        Checker.VALUE(
            len(self.temperatures) == len(self.bounds.values),
            "The temperatures and the bounds must have the same length.",
            {
                "len(temperatures)": len(self.temperatures),
                "len(bounds.values)": len(self.bounds.values),
            },
        )


def _validate_bounds(bounds: np.ndarray, name: str = "bounds") -> np.ndarray:
    """
    Validate input bounds.
    """
    bounds = ArrayT.REAL(name).ndim(2)(bounds)
    Checker.VALUE(
        bounds.shape[1] == 2,
        f"The {name} must be a 2D array with two components in the second axis.",
        {f"{name}.shape": bounds.shape},
    )
    Checker.VALUE(
        all(bounds[:, 1] > bounds[:, 0]),
        "The upper bound (second component) must be greater than the lower bound "
        f"(first component) for each element in the {name} array.",
        {"upper bounds": bounds[:, 1], "lower bounds": bounds[:, 0]},
    )
    return bounds


ALLOWED_OPTIMIZERS = (Cmaes, NeuralNetwork, GaussianProcess, SimulatedAnnealing)
