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
    Callable,
    List,
    Optional,
    Union,
)

import numpy as np
from pydantic import SkipValidation

from boulderopal._nodes.base import create_operation
from boulderopal._nodes.node_data import (
    Pwc,
    Stf,
    Tensor,
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


def _validate_initial_values(
    values: Any, count: int, lower: float, upper: float
) -> Optional[np.ndarray | list[np.ndarray]]:
    Checker.VALUE(
        upper > lower,
        "The lower bound must be less than the upper bound.",
        {"lower_bound": lower, "upper_bound": upper},
    )
    if values is None:
        return None

    def _validate_value(value: Any, *, name: str) -> np.ndarray:
        return ArrayT.REAL(name).ndim(1).shape((count,)).ge(lower).le(upper)(value)

    try:
        return sequence_like(_validate_value)(values, name="initial_values")
    except TypeError as exc:
        raise TypeError(
            "The initial values must be a NumPy array or a list of NumPy arrays."
        ) from exc


def _check_inputs_real_fourier_signal(
    lower: float,
    upper: float,
    fixed_frequencies: Optional[np.ndarray],
    optimizable_frequency_count: Optional[int],
    randomized_frequency_count: Optional[int],
) -> None:
    """
    Check if the inputs of real_fourier_pwc/stf_signal function are valid.
    """
    Checker.VALUE(
        upper > lower,
        "The initial coefficient lower bound must be less than the upper bound.",
        {
            "initial_coefficient_lower_bound": lower,
            "initial_coefficient_upper_bound": upper,
        },
    )
    Checker.VALUE(
        (fixed_frequencies is not None)
        + (optimizable_frequency_count is not None)
        + (randomized_frequency_count is not None)
        == 1,
        "Exactly one of `fixed_frequencies`, `optimizable_frequency_count`, and "
        "`randomized_frequency_count` must be provided.",
        {
            "fixed_frequencies": fixed_frequencies,
            "optimizable_frequency_count": optimizable_frequency_count,
            "randomized_frequency_count": randomized_frequency_count,
        },
    )


class OptimizationGraph:  # pylint: disable=unused-argument
    """
    Base class implementing optimization graph methods.
    """

    @validated
    def optimization_variable(
        self,
        count: Annotated[int, pipe(ScalarT.INT().gt(0))],
        lower_bound: Annotated[float, pipe(ScalarT.REAL())],
        upper_bound: Annotated[float, pipe(ScalarT.REAL())],
        is_lower_unbounded: bool = False,
        is_upper_unbounded: bool = False,
        initial_values: Annotated[
            Optional[Union[np.ndarray, List[np.ndarray]]], SkipValidation
        ] = None,
        *,
        name: Optional[str] = None,
    ) -> Tensor:
        r"""
        Create a 1D Tensor of optimization variables, which can be bounded,
        semi-bounded, or unbounded.

        Use this function to create a sequence of variables that can be tuned by
        the optimizer (within specified bounds) in order to minimize the cost
        function.

        Parameters
        ----------
        count : int
            The number :math:`N` of individual real-valued variables to create.
        lower_bound : float
            The lower bound :math:`v_\mathrm{min}` for generating an initial value for the
            variables. This will also be used as lower bound if the variables are lower bounded.
            The same lower bound applies to all `count` individual variables.
        upper_bound : float
            The upper bound :math:`v_\mathrm{max}` for generating an initial value for the
            variables. This will also be used as upper bound if the variables are upper bounded.
            The same upper bound applies to all `count` individual variables.
        is_lower_unbounded : bool, optional
            Defaults to False. Set this flag to True to define a semi-bounded variable with
            lower bound :math:`-\infty`; in this case, the `lower_bound` parameter is used only for
            generating an initial value.
        is_upper_unbounded : bool, optional
            Defaults to False. Set this flag to True to define a semi-bounded variable with
            upper bound :math:`+\infty`; in this case, the `upper_bound` parameter is used only for
            generating an initial value.
        initial_values : np.ndarray or List[np.ndarray] or None, optional
            Initial values for the optimization variable. You can either provide a single initial
            value, or a list of them. Note that all optimization variables in a graph with
            non-default initial values must have the same length. That is, you must set them either
            as a single array or a list of arrays of the same length. Defaults to None, meaning
            the optimizer initializes the variables with random values.
        name : str or None, optional
            The name of the node.

        Returns
        -------
        Tensor
            The sequence :math:`\{v_n\}` of :math:`N` optimization variables. If both
            `is_lower_unbounded` and `is_upper_unbounded` are False, these variables are
            bounded such that :math:`v_\mathrm{min}\leq v_n\leq v_\mathrm{max}`. If one of the
            flags is True (for example `is_lower_unbounded=True`), these variables are
            semi-bounded (for example :math:`-\infty \leq v_n \leq v_\mathrm{max}`).
            If both of them are True, then these variables are unbounded and satisfy that
            :math:`-\infty \leq v_n \leq +\infty`.

        See Also
        --------
        Graph.anchored_difference_bounded_variables :
            Create anchored optimization variables with a difference bound.
        Graph.complex_optimizable_pwc_signal :
            Create a complex optimizable `Pwc` signal.
        Graph.optimizable_scalar : Create an optimization scalar.
        Graph.real_optimizable_pwc_signal :
            Create a real optimizable `Pwc` signal.
        boulderopal.run_optimization :
            Function to find the minimum of a generic function.

        Examples
        --------
        Perform a simple optimization task.

        >>> variables = graph.optimization_variable(
        ...     2, lower_bound=0, upper_bound=1, name="variables"
        ... )
        >>> x = variables[0]
        >>> y = variables[1]
        >>> cost = (x - 0.1) ** 2 + graph.sin(y) ** 2
        >>> cost.name = "cost"
        >>> result = bo.run_optimization(
        ...     graph=graph, cost_node_name="cost", output_node_names="variables"
        ... )
        >>> result["cost"]
        0.0
        >>> result["output"]["variables"]["value"]
        array([0.1, 0.])

        See examples about optimal control of quantum systems in the
        `How to optimize controls in arbitrary quantum systems using graphs
        <https://docs.q-ctrl.com/boulder-opal/user-guides/how-to-optimize-controls-
        in-arbitrary-quantum-systems-using-graphs>`_ user guide.
        """

        initial_values = _validate_initial_values(
            initial_values, count, lower_bound, upper_bound
        )
        operation = create_operation(self.optimization_variable, locals())
        return Tensor(operation, shape=(count,))

    @validated
    def anchored_difference_bounded_variables(
        self,
        count: Annotated[int, pipe(ScalarT.INT().gt(0))],
        lower_bound: Annotated[float, pipe(ScalarT.REAL())],
        upper_bound: Annotated[float, pipe(ScalarT.REAL())],
        difference_bound: Annotated[float, pipe(ScalarT.REAL().ge(0))],
        initial_values: Annotated[
            Optional[Union[np.ndarray, List[np.ndarray]]], SkipValidation
        ] = None,
        *,
        name: Optional[str] = None,
    ) -> Tensor:
        r"""
        Create a sequence of optimizable variables with an anchored difference bound.

        Use this function to create a sequence of optimization variables that have
        a difference bound (each variable is constrained to be within a given
        distance of the adjacent variables) and are anchored to zero at the start
        and end (the initial and final variables are within a given distance of
        zero).

        Parameters
        ----------
        count : int
            The number :math:`N` of individual real-valued variables to create.
        lower_bound : float
            The lower bound :math:`v_\mathrm{min}` on the variables.
            The same lower bound applies to all `count` individual variables.
        upper_bound : float
            The upper bound :math:`v_\mathrm{max}` on the variables.
            The same upper bound applies to all `count` individual variables.
        difference_bound : float
            The difference bound :math:`\delta` to enforce between adjacent
            variables.
        initial_values : np.ndarray or List[np.ndarray] or None, optional
            Initial values for optimization variable. You can either provide a single initial
            value, or a list of them. Note that all optimization variables in a graph with
            non-default initial values must have the same length. That is, you must set them either
            as a single array or a list of arrays of the same length. Defaults to None, meaning
            the optimizer initializes the variables with random values.
        name : str or None, optional
            The name of the node.

        Returns
        -------
        Tensor
            The sequence :math:`\{v_n\}` of :math:`N` anchored difference-bounded
            optimization variables, satisfying
            :math:`v_\mathrm{min}\leq v_n\leq v_\mathrm{max}`,
            :math:`|v_{n-1}-v_n|\leq\delta` for :math:`2\leq n\leq N`,
            :math:`|v_1|\leq\delta`, and :math:`|v_N|\leq\delta`.

        See Also
        --------
        Graph.optimization_variable : Create 1D Tensor of optimization variables.
        boulderopal.run_optimization :
            Function to find the minimum of generic deterministic functions.
        boulderopal.run_stochastic_optimization :
            Function to find the minimum of generic stochastic functions.

        Examples
        --------
        Create optimizable PWC signal with anchored difference bound.

        >>> values = graph.anchored_difference_bounded_variables(
        ...     count=10, lower_bound=-1, upper_bound=1, difference_bound=0.1
        ... )
        >>> graph.pwc_signal(values=values, duration=1)
        <Pwc: name="pwc_signal_#1", operation_name="pwc_signal", value_shape=(), batch_shape=()>

        See the "Band-limited pulses with bounded slew rates" example in the
        `How to add smoothing and band-limits to optimized controls
        <https://docs.q-ctrl.com/boulder-opal/user-guides/how-to-add-smoothing-and-band-limits-to-
        optimized-controls#example-band-limited-pulses-with-bounded-slew-rates>`_ user guide.
        """

        initial_values = _validate_initial_values(
            initial_values, count, lower_bound, upper_bound
        )
        operation = create_operation(
            self.anchored_difference_bounded_variables, locals()
        )
        return Tensor(operation, shape=(count,))

    @validated
    def real_fourier_stf_signal(
        self,
        duration: Annotated[float, pipe(ScalarT.REAL().gt(0))],
        initial_coefficient_lower_bound: Annotated[float, pipe(ScalarT.REAL())] = -1,
        initial_coefficient_upper_bound: Annotated[float, pipe(ScalarT.REAL())] = 1,
        fixed_frequencies: Optional[
            Annotated[np.ndarray, pipe(ArrayT.REAL().ndim(1).gt(0))]
        ] = None,
        optimizable_frequency_count: Optional[
            Annotated[int, pipe(ScalarT.INT().gt(0))]
        ] = None,
        randomized_frequency_count: Optional[
            Annotated[int, pipe(ScalarT.INT().gt(0))]
        ] = None,
    ) -> Stf:
        r"""
        Create a real sampleable signal constructed from Fourier components.

        Use this function to create a signal defined in terms of Fourier (sine/cosine)
        basis signals that can be optimized by varying their coefficients and, optionally,
        their frequencies.

        Parameters
        ----------
        duration : float
            The total duration :math:`\tau` of the signal.
        initial_coefficient_lower_bound : float, optional
            The lower bound :math:`c_\mathrm{min}` on the initial coefficient
            values. Defaults to -1.
        initial_coefficient_upper_bound : float, optional
            The upper bound :math:`c_\mathrm{max}` on the initial coefficient
            values. Defaults to 1.
        fixed_frequencies : np.ndarray or None, optional
            A 1D array containing the fixed non-zero frequencies :math:`\{f_m\}`
            to use for the Fourier basis. If provided, must be non-empty and specified in
            the inverse units of `duration` (for example if `duration` is in seconds, these
            values must be given in Hertz).
        optimizable_frequency_count : int or None, optional
            The number of non-zero frequencies :math:`M` to use, if the
            frequencies can be optimized. Defaults to 0.
        randomized_frequency_count : int or None, optional
            The number of non-zero frequencies :math:`M` to use, if the
            frequencies are to be randomized but fixed. Defaults to 0.

        Returns
        -------
        Stf
            The optimizable, real-valued, sampleable signal built from the
            appropriate Fourier components.

        Warnings
        --------
        You must provide exactly one of `fixed_frequencies`, `optimizable_frequency_count`,
        or `randomized_frequency_count`.

        See Also
        --------
        Graph.real_fourier_pwc_signal : Corresponding operation for `Pwc`.

        Notes
        -----
        This function sets the basis signal frequencies :math:`\{f_m\}`
        depending on the chosen mode:

        * For fixed frequencies, you provide the frequencies directly.
        * For optimizable frequencies, you provide the number of frequencies
          :math:`M`, and this function creates :math:`M` unbounded optimizable
          variables :math:`\{f_m\}`, with initial values in the ranges
          :math:`\{[(m-1)/\tau, m/\tau]\}`.
        * For randomized frequencies, you provide the number of frequencies
          :math:`M`, and this function creates :math:`M` randomized constants
          :math:`\{f_m\}` in the ranges :math:`\{[(m-1)/\tau, m/\tau]\}`.

        After this function creates the :math:`M` frequencies :math:`\{f_m\}`, it
        produces the signal

        .. math::
            \alpha^\prime(t) = v_0 +
            \sum_{m=1}^M [ v_m \cos(2\pi t f_m) + w_m \sin(2\pi t f_m) ],

        where :math:`\{v_m,w_m\}` are (unbounded) optimizable variables, with
        initial values bounded by :math:`c_\mathrm{min}` and
        :math:`c_\mathrm{max}`. This function produces the final signal :math:`\alpha(t)`.

        You can use the signals created by this function for chopped random basis
        (CRAB) optimization [1]_.

        References
        ----------
        .. [1] `P. Doria, T. Calarco, and S. Montangero,
                Phys. Rev. Lett. 106, 190501 (2011).
                <https://doi.org/10.1103/PhysRevLett.106.190501>`_
        """

        _check_inputs_real_fourier_signal(
            initial_coefficient_lower_bound,
            initial_coefficient_upper_bound,
            fixed_frequencies,
            optimizable_frequency_count,
            randomized_frequency_count,
        )
        operation = create_operation(self.real_fourier_stf_signal, locals())
        return Stf(operation, value_shape=(), batch_shape=())

    @validated
    def real_fourier_pwc_signal(
        self,
        duration: Annotated[float, pipe(ScalarT.REAL().gt(0))],
        segment_count: Annotated[int, pipe(ScalarT.INT().gt(0))],
        initial_coefficient_lower_bound: Annotated[float, pipe(ScalarT.REAL())] = -1,
        initial_coefficient_upper_bound: Annotated[float, pipe(ScalarT.REAL())] = 1,
        fixed_frequencies: Optional[
            Annotated[np.ndarray, pipe(ArrayT.REAL().ndim(1).gt(0))]
        ] = None,
        optimizable_frequency_count: Optional[
            Annotated[int, pipe(ScalarT.INT().gt(0))]
        ] = None,
        randomized_frequency_count: Optional[
            Annotated[int, pipe(ScalarT.INT().gt(0))]
        ] = None,
        *,
        name: Optional[str] = None,
    ) -> Pwc:
        r"""
        Create a piecewise-constant signal constructed from Fourier components.

        Use this function to create a signal defined in terms of Fourier
        (sine/cosine) basis signals that can be optimized by varying their
        coefficients and, optionally, their frequencies.

        Parameters
        ----------
        duration : float
            The total duration :math:`\tau` of the signal.
        segment_count : int
            The number of segments :math:`N` to use for the piecewise-constant
            approximation.
        initial_coefficient_lower_bound : float, optional
            The lower bound :math:`c_\mathrm{min}` on the initial coefficient
            values. Defaults to -1.
        initial_coefficient_upper_bound : float, optional
            The upper bound :math:`c_\mathrm{max}` on the initial coefficient
            values. Defaults to 1.
        fixed_frequencies : np.ndarray or None, optional
            A 1D array object containing the fixed non-zero frequencies :math:`\{f_m\}`
            to use for the Fourier basis. If provided, must be non-empty and specified in
            the inverse units of `duration` (for example if `duration` is in seconds, these
            values must be given in Hertz).
        optimizable_frequency_count : int or None, optional
            The number of non-zero frequencies :math:`M` to use, if the
            frequencies can be optimized. Defaults to 0.
        randomized_frequency_count : int or None, optional
            The number of non-zero frequencies :math:`M` to use, if the
            frequencies are to be randomized but fixed. Defaults to 0.
        name : str or None, optional
            The name of the node.

        Returns
        -------
        Pwc
            The optimizable, real-valued, piecewise-constant signal built from the
            appropriate Fourier components.

        Warnings
        --------
        You must provide exactly one of `fixed_frequencies`, `optimizable_frequency_count`,
        or `randomized_frequency_count`.

        See Also
        --------
        Graph.real_fourier_stf_signal : Corresponding operation for `Stf`.

        Notes
        -----
        This function sets the basis signal frequencies :math:`\{f_m\}`
        depending on the chosen mode:

        * For fixed frequencies, you provide the frequencies directly.
        * For optimizable frequencies, you provide the number of frequencies
          :math:`M`, and this function creates :math:`M` unbounded optimizable
          variables :math:`\{f_m\}`, with initial values in the ranges
          :math:`\{[(m-1)/\tau, m/\tau]\}`.
        * For randomized frequencies, you provide the number of frequencies
          :math:`M`, and this function creates :math:`M` randomized constants
          :math:`\{f_m\}` in the ranges :math:`\{[(m-1)/\tau, m/\tau]\}`.

        After this function creates the :math:`M` frequencies :math:`\{f_m\}`, it
        produces the signal

        .. math::
            \alpha^\prime(t) = v_0 +
            \sum_{m=1}^M [ v_m \cos(2\pi t f_m) + w_m \sin(2\pi t f_m) ],

        where :math:`\{v_m,w_m\}` are (unbounded) optimizable variables, with
        initial values bounded by :math:`c_\mathrm{min}` and
        :math:`c_\mathrm{max}`. This function produces the final
        piecewise-constant signal :math:`\alpha(t)` by sampling
        :math:`\alpha^\prime(t)` at :math:`N` equally spaced points along the
        duration :math:`\tau`, and using those sampled values as the constant
        segment values.

        You can use the signals created by this function for chopped random basis
        (CRAB) optimization [1]_.

        References
        ----------
        .. [1] `P. Doria, T. Calarco, and S. Montangero,
                Phys. Rev. Lett. 106, 190501 (2011).
                <https://doi.org/10.1103/PhysRevLett.106.190501>`_

        Examples
        --------
        See the "Fourier-basis optimization on a qutrit" example in the
        `How to optimize controls using arbitrary basis functions
        <https://docs.q-ctrl.com/boulder-opal/user-guides/how-to-optimize-controls-using-arbitrary-
        basis-functions#example-fourier-basis-optimization-on-a-qutrit>`_ user guide.
        """

        _check_inputs_real_fourier_signal(
            initial_coefficient_lower_bound,
            initial_coefficient_upper_bound,
            fixed_frequencies,
            optimizable_frequency_count,
            randomized_frequency_count,
        )

        durations = duration / segment_count * np.ones(segment_count)
        operation = create_operation(self.real_fourier_pwc_signal, locals())
        return Pwc(operation, value_shape=(), durations=durations, batch_shape=())

    @validated
    def optimizable_scalar(
        self,
        lower_bound: Annotated[float, pipe(ScalarT.REAL())],
        upper_bound: Annotated[float, pipe(ScalarT.REAL())],
        is_lower_unbounded: bool = False,
        is_upper_unbounded: bool = False,
        initial_values: Annotated[
            Optional[Union[float, List[float]]], SkipValidation
        ] = None,
        *,
        name: Optional[str] = None,
    ) -> Tensor:
        r"""
        Create an optimizable scalar Tensor, which can be bounded, semi-bounded, or unbounded.

        Use this function to create a single variable that can be tuned by
        the optimizer to minimize the cost function.

        Parameters
        ----------
        lower_bound : float
            The lower bound :math:`v_\mathrm{min}` for generating an initial value for the variable.
            This will also be used as lower bound if the variable is lower bounded.
        upper_bound : float
            The upper bound :math:`v_\mathrm{max}` for generating an initial value for the variable.
            This will also be used as upper bound if the variable is upper bounded.
        is_lower_unbounded : bool, optional
            Defaults to False. Set this flag to True to define a semi-bounded variable with
            lower bound :math:`-\infty`; in this case, the `lower_bound` parameter is used only for
            generating an initial value.
        is_upper_unbounded : bool, optional
            Defaults to False. Set this flag to True to define a semi-bounded variable with
            upper bound :math:`+\infty`; in this case, the `upper_bound` parameter is used only for
            generating an initial value.
        initial_values : float or List[float] or None, optional
            Initial values for the optimization variable. You can either provide a single initial
            value, or a list of them. Note that all optimization variables in a graph with
            non-default initial values must have the same length. That is, you must set them all
            either as a single value or a list of values of the same length. Defaults to None,
            meaning the optimizer initializes the variable with a random value.
        name : str or None, optional
            The name of the node.

        Returns
        -------
        Tensor
            The :math:`v` optimizable scalar. If both `is_lower_unbounded` and `is_upper_unbounded`
            are False, the variables is bounded such that
            :math:`v_\mathrm{min}\leq v \leq v_\mathrm{max}`. If one of the flags is True
            (for example `is_lower_unbounded=True`), the variable is semi-bounded
            (for example :math:`-\infty \leq v \leq v_\mathrm{max}`). If both of them are True,
            then the variable is unbounded and satisfies that :math:`-\infty \leq v \leq +\infty`.

        See Also
        --------
        Graph.optimization_variable : Create 1D Tensor of optimization variables.
        boulderopal.run_optimization :
            Function to find the minimum of a generic function.
        """

        initial_array: Optional[np.ndarray | list[np.ndarray]] = None
        if initial_values is not None:

            def _validator(name: str) -> Callable:
                return ScalarT.REAL(name).ge(lower_bound).le(upper_bound)

            if isinstance(initial_values, list):
                initial_array = [
                    np.array([_validator(f"initial_values[{idx}]")(value)])
                    for idx, value in enumerate(initial_values)
                ]
            else:
                initial_array = np.array([_validator("initial_values")(initial_values)])

        scalar = self.optimization_variable(
            count=1,
            lower_bound=lower_bound,
            upper_bound=upper_bound,
            is_lower_unbounded=is_lower_unbounded,
            is_upper_unbounded=is_upper_unbounded,
            initial_values=initial_array,
        )[0]

        if name is not None:
            scalar.name = name

        return scalar
