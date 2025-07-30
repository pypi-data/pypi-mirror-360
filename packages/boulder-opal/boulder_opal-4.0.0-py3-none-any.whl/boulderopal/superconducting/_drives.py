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

from abc import (
    ABC,
    abstractmethod,
)
from dataclasses import dataclass
from typing import TYPE_CHECKING

import numpy as np

from boulderopal._nodes.node_data import Pwc
from boulderopal._validation import ScalarT

if TYPE_CHECKING:
    from boulderopal.graph.graph import Graph


class OptimizableCoefficient(ABC):
    """
    Abstract class for optimizable Hamiltonian coefficients.
    """

    @abstractmethod
    def get_pwc(self, graph: Graph, gate_duration: float, name: str) -> Pwc:
        """
        Return a Pwc representation of the optimizable coefficient.
        """
        raise NotImplementedError


@dataclass
class RealOptimizableConstant(OptimizableCoefficient):
    """
    A real-valued optimizable constant coefficient for a Hamiltonian term.
    The main function will try to find the optimal value for this constant.

    Parameters
    ----------
    min : float
        The minimum value that the coefficient can take.
    max : float
        The maximum value that the coefficient can take.

    See Also
    --------
    boulderopal.superconducting.ComplexOptimizableConstant :
        Class describing complex optimizable constant coefficients.
    boulderopal.superconducting.ComplexOptimizableSignal :
        Class describing complex optimizable piecewise-constant coefficients.
    boulderopal.superconducting.RealOptimizableSignal :
        Class describing real optimizable piecewise-constant coefficients.
    """

    min: float
    max: float

    def __post_init__(self) -> None:
        self.min = ScalarT.REAL("min")(self.min)
        self.max = ScalarT.REAL("max").gt(self.min, "min")(self.max)

    def get_pwc(self, graph: Graph, gate_duration: float, name: str) -> Pwc:
        value = graph.optimizable_scalar(self.min, self.max)
        value.name = name
        return graph.constant_pwc(constant=value, duration=gate_duration)


@dataclass
class ComplexOptimizableConstant(OptimizableCoefficient):
    """
    A complex-valued optimizable constant coefficient for a Hamiltonian term.
    The main function will try to find the optimal value for this constant.

    Parameters
    ----------
    max_modulus : float
        The maximum value that the modulus of the coefficient can take.

    See Also
    --------
    boulderopal.superconducting.ComplexOptimizableSignal :
        Class describing complex optimizable piecewise-constant coefficients.
    boulderopal.superconducting.RealOptimizableConstant :
        Class describing real optimizable constant coefficients.
    boulderopal.superconducting.RealOptimizableSignal :
        Class describing real optimizable piecewise-constant coefficients.
    """

    max_modulus: float

    def __post_init__(self) -> None:
        self.max_modulus = ScalarT.REAL("max_modulus").gt(0)(self.max_modulus)

    def get_pwc(self, graph: Graph, gate_duration: float, name: str) -> Pwc:
        mod = graph.optimizable_scalar(0, self.max_modulus)
        phase = graph.optimizable_scalar(0, 2 * np.pi, True, True)
        value = graph.multiply(mod, graph.exp(1j * phase), name=name)
        return graph.constant_pwc(constant=value, duration=gate_duration)


@dataclass
class RealOptimizableSignal(OptimizableCoefficient):
    """
    A real-valued optimizable time-dependent piecewise-constant coefficient for
    a Hamiltonian term. The main function will try to find the optimal value for
    this signal at each segment.

    Parameters
    ----------
    count : int
        The number of segments in the piecewise-constant signal.
    min : float
        The minimum value that the signal can take at each segment.
    max : float
        The maximum value that the signal can take at each segment.

    See Also
    --------
    boulderopal.superconducting.ComplexOptimizableConstant :
        Class describing complex optimizable constant coefficient.
    boulderopal.superconducting.ComplexOptimizableSignal :
        Class describing complex optimizable piecewise-constant coefficients.
    boulderopal.superconducting.RealOptimizableConstant :
        Class describing real optimizable constant coefficients.
    """

    count: int
    min: float
    max: float

    def __post_init__(self) -> None:
        self.count = ScalarT.INT("count").gt(0)(self.count)
        self.min = ScalarT.REAL("min")(self.min)
        self.max = ScalarT.REAL("max").gt(self.min, "min")(self.max)

    def get_pwc(self, graph: Graph, gate_duration: float, name: str) -> Pwc:
        values = graph.optimization_variable(self.count, self.min, self.max)
        return graph.pwc_signal(values=values, duration=gate_duration, name=name)


@dataclass
class ComplexOptimizableSignal(OptimizableCoefficient):
    """
    A complex-valued optimizable time-dependent piecewise-constant coefficient
    for a Hamiltonian term. The main function will try to find the optimal value
    for this signal at each segment.

    Parameters
    ----------
    count : int
        The number of segments in the piecewise-constant signal.
    max_modulus : float
        The maximum value that the modulus of the signal can take at each segment.

    See Also
    --------
    boulderopal.superconducting.ComplexOptimizableConstant :
        Class describing complex optimizable constant coefficients.
    boulderopal.superconducting.RealOptimizableConstant :
        Class describing real optimizable constant coefficients.
    boulderopal.superconducting.RealOptimizableSignal :
        Class describing real optimizable piecewise-constant coefficients.
    """

    count: int
    max_modulus: float

    def __post_init__(self) -> None:
        self.count = ScalarT.INT("count").gt(0)(self.count)
        self.max_modulus = ScalarT.REAL("max_modulus").gt(0)(self.max_modulus)

    def get_pwc(self, graph: Graph, gate_duration: float, name: str) -> Pwc:
        return graph.complex_optimizable_pwc_signal(
            segment_count=self.count,
            duration=gate_duration,
            maximum=self.max_modulus,
            name=name,
        )
