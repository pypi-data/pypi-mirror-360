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
Functionality related to the computational-flow graph object.
"""
from __future__ import annotations

from typing import Optional

import numpy as np
from qctrlcommons.graph import Graph as BaseGraph

from boulderopal._nodes.arithmetic_binary import ArithmeticBinaryGraph
from boulderopal._nodes.arithmetic_unary import ArithmeticUnaryGraph
from boulderopal._nodes.differentiation import DifferentiationGraph
from boulderopal._nodes.filter_function import FilterFunctionGraph
from boulderopal._nodes.fock_space import FockSpaceGraph
from boulderopal._nodes.infidelity import InfidelityGraph
from boulderopal._nodes.ions import IonsGraph
from boulderopal._nodes.node_data import (
    ConvolutionKernel,
    Pwc,
)
from boulderopal._nodes.optimization import OptimizationGraph
from boulderopal._nodes.oqs import OqsGraph
from boulderopal._nodes.pwc import PwcGraph
from boulderopal._nodes.random import RandomGraph
from boulderopal._nodes.signals import Signals
from boulderopal._nodes.sparse import SparseGraph
from boulderopal._nodes.stf import StfGraph
from boulderopal._nodes.tensor import TensorGraph
from boulderopal._validation import Checker


class Graph(  # pylint: disable=too-many-ancestors
    ArithmeticBinaryGraph,
    ArithmeticUnaryGraph,
    BaseGraph,
    DifferentiationGraph,
    FilterFunctionGraph,
    FockSpaceGraph,
    InfidelityGraph,
    OptimizationGraph,
    OqsGraph,
    PwcGraph,
    SparseGraph,
    StfGraph,
    TensorGraph,
):
    """
    A class for representing and building a Boulder Opal data flow graph.

    The graph object is the main entry point to the Boulder Opal graph ecosystem.
    You can call methods to add nodes to the graph, and use the `operations` attribute to get a
    dictionary representation of the graph.
    """

    def __init__(self) -> None:
        self.random = RandomGraph(self)
        self.signals = Signals(self)
        self.ions = IonsGraph(self)
        super().__init__()

    def filter_and_resample_pwc(
        self,
        pwc: Pwc,
        kernel: ConvolutionKernel,
        segment_count: int,
        duration: Optional[float] = None,
        *,
        name: Optional[str] = None,
    ) -> Pwc:
        r"""
        Filter a piecewise-constant function by convolving it with a kernel and resample it again.

        Parameters
        ----------
        pwc : Pwc
            The piecewise-constant function :math:`\alpha(t)` to be filtered.
        kernel : ConvolutionKernel
            The node representing the kernel :math:`K(t)`.
        segment_count : int
            The number of segments of the resampled filtered function.
        duration : float or None, optional
            Force the resulting piecewise-constant function to have a certain duration.
            This option is mainly to avoid floating point errors when the total duration is
            too small. Defaults to the sum of segment durations of `pwc`.
        name : str or None, optional
            The name of the node.

        Returns
        -------
        Pwc
            The filtered and resampled piecewise-constant function.

        See Also
        --------
        :func:`Graph.convolve_pwc` :
            Create the convolution of a piecewise-constant function with a kernel.
        :func:`Graph.discretize_stf` :
            Create a piecewise-constant function by discretizing a sampleable function.
        :func:`Graph.sinc_convolution_kernel` :
            Create a convolution kernel representing the sinc function.

        Notes
        -----
        The convolution is

        .. math::
            (\alpha * K)(t) \equiv
            \int_{-\infty}^\infty \alpha(\tau) K(t-\tau) \mathrm{d}\tau.

        Convolution in the time domain is equivalent to multiplication in the
        frequency domain, so this function can be viewed as applying a linear
        time-invariant filter (specified via its time domain kernel :math:`K(t)`)
        to :math:`\alpha(t)`.
        """
        return self.discretize_stf(
            stf=self.convolve_pwc(pwc=pwc, kernel=kernel),
            duration=duration or np.sum(pwc.durations),
            segment_count=segment_count,
            name=name,
        )

    def real_optimizable_pwc_signal(
        self,
        segment_count: int,
        duration: float,
        maximum: float,
        minimum: float = 0.0,
        initial_values: Optional[np.ndarray | list[np.ndarray]] = None,
        *,
        name: Optional[str] = None,
    ) -> Pwc:
        """
        Create a real optimizable piecewise-constant signal.

        Parameters
        ----------
        segment_count : int
            The number of piecewise-constant segments in the signal.
        duration : float
            The duration of the signal.
        maximum : float
            The upper bound for the signal values.
        minimum : float, optional
            The lower bound for the signal values. Defaults to 0.
        initial_values : np.ndarray or list[np.ndarray] or None, optional
            Initial values for the signal. You can either provide a single array,
            or a list of them. If a list of arrays is used, they must have the same length.
            Defaults to None, meaning the optimizer initializes the variables with random values.
        name : str or None, optional
            The name of the node.

        Returns
        -------
        Pwc
            The optimizable piecewise-constant signal.

        See Also
        --------
        :func:`Graph.complex_optimizable_pwc_signal` :
            Create a complex optimizable `Pwc` signal.
        :func:`Graph.optimization_variable` :
            Create optimization variables, which can be bounded, semi-bounded, or unbounded.
        :func:`Graph.pwc_signal` : Create a piecewise-constant signal.
        """
        Checker.VALUE(maximum > minimum, "maximum must be greater than minimum.")

        values = self.optimization_variable(
            count=segment_count,
            lower_bound=minimum,
            upper_bound=maximum,
            initial_values=initial_values,
        )
        return self.pwc_signal(values=values, duration=duration, name=name)

    def complex_optimizable_pwc_signal(
        self,
        segment_count: int,
        duration: float,
        maximum: float,
        initial_values: Optional[np.ndarray | list[np.ndarray]] = None,
        *,
        name: Optional[str] = None,
    ) -> Pwc:
        """
        Create a complex optimizable piecewise-constant signal.

        Parameters
        ----------
        segment_count : int
            The number of segments of the signal.
        duration : float
            The duration of the signal.
        maximum : float
            The upper bound for the modulus of the signal values.
        initial_values : np.ndarray or list[np.ndarray] or None, optional
            Initial values for the signal. You can either provide a single array,
            or a list of them. If a list of arrays is used, they must have the same length.
            Defaults to None, meaning the optimizer initializes the variables with random values.
        name : str or None, optional
            The name of the node.

        Returns
        -------
        Pwc
            The optimizable piecewise-constant signal.

        See Also
        --------
        :func:`Graph.real_optimizable_pwc_signal` :
            Create a real optimizable `Pwc` signal.
        :func:`Graph.complex_pwc_signal` :
            Create a complex piecewise-constant signal from moduli and phases.
        :func:`Graph.optimization_variable` :
            Create optimization variables, which can be bounded, semi-bounded, or unbounded.
        :func:`Graph.pwc_signal` : Create a piecewise-constant signal.

        Notes
        -----
        Note that this function sets limits to the modulus of the signal.

        If you want to set (different) limits to the real and imaginary parts instead,
        consider using `graph.real_optimizable_signal` to create signals for the
        real and imaginary parts, which you can pass to `graph.complex_value`.
        """

        Checker.VALUE(maximum > 0, "maximum must be greater than 0.")
        initial_moduli: Optional[list[np.ndarray] | np.ndarray] = None
        initial_phases: Optional[list[np.ndarray] | np.ndarray] = None

        if initial_values is not None:
            if isinstance(initial_values, list):
                initial_moduli = list(np.absolute(initial_values))
                initial_phases = list(np.angle(initial_values))
            else:
                initial_moduli = np.absolute(initial_values)
                initial_phases = np.angle(initial_values)

        moduli = self.optimization_variable(
            count=segment_count,
            lower_bound=0.0,
            upper_bound=maximum,
            initial_values=initial_moduli,
        )
        phases = self.optimization_variable(
            count=segment_count,
            lower_bound=-np.pi,
            upper_bound=np.pi,
            is_lower_unbounded=True,
            is_upper_unbounded=True,
            initial_values=initial_phases,
        )
        return self.complex_pwc_signal(
            moduli=moduli, phases=phases, duration=duration, name=name
        )
