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
Library of signals for Boulder Opal.
"""
from __future__ import annotations

import inspect
from functools import wraps
from typing import (
    Any,
    Callable,
    Optional,
)

import numpy as np

from boulderopal._nodes.node_data import NodeData
from boulderopal._validation import Checker


def _no_graph_parameters(alternatives: Optional[str]) -> Callable:
    """
    Check that none of the parameters passed to the function are graph objects.

    Use this as a decorator for non-graph functions, to make sure that no
    graph object types are being passed as parameters by accident.

    Parameters
    ----------
    alternatives : str or None
        Text listing alternative functions that do accept graphs and that the
        user might be intending to use instead. If it's None, nothing is
        suggested to the user.

    Returns
    -------
    Callable
        A decorator that adds checks to the beginning of the function to see
        if none of the inputs are graph types, and raises an exception that
        suggests the `alternatives`.

    Examples
    --------
    Create a addition function that only accepts non-Graph objects as input,
    and that suggests `graph.add` as an alternative.

    >>> @_no_graph_parameters(alternatives="`graph.add`")
    ... def numpy_add(x, y):
    ...     return x + y
    >>> numpy_add(1, graph.tensor(2))
    TypeError: The parameters of `numpy_add` cannot be graph objects.
    Perhaps you intended to use `graph.add`? type(y)='Tensor'
    """
    advice = ""
    if alternatives is not None:
        advice = f" Perhaps you intended to use {alternatives}?"

    def _no_graph_parameters(function: Callable) -> Callable:
        arg_names = list(inspect.signature(function).parameters)

        error_message = (
            f"The parameters of `{function.__name__}` cannot be graph objects." + advice
        )

        @wraps(function)
        def _function(*args, **kwargs) -> Any:  # type: ignore
            for arg_name, arg in zip(arg_names, args):
                Checker.TYPE(
                    not isinstance(arg, NodeData),
                    error_message,
                    {f"type({arg_name})": type(arg).__name__},
                )

            for key, kwarg in kwargs.items():
                Checker.TYPE(
                    not isinstance(kwarg, NodeData),
                    error_message,
                    {f"type({key})": type(kwarg).__name__},
                )
            return function(*args, **kwargs)

        return _function

    return _no_graph_parameters


class Signal:
    """
    A class that contains information about a signal that can be discretized.

    You can use this class to create and store signals that will be sent to
    third-party devices. The signals created in this way are independent of
    Boulder Opal graphs and have a fixed time step between their segments.

    Parameters
    ----------
    function : Callable
        A function that returns the value of the signal at each instant of time.
        It must be capable of accepting a NumPy array of times as an input
        parameters, in which case it should return the values of the function
        for all the times passed.
    duration : float
        The duration of the signal.
    """

    def __init__(self, function: Callable, duration: float):
        Checker.VALUE(
            duration > 0, "The duration must be positive.", {"duration": duration}
        )

        self.duration = duration
        self._function = function

    def export_with_time_step(self, time_step: float) -> np.ndarray:
        """
        Return the values of the signal sampled at a constant rate given by the
        time step provided.

        Parameters
        ----------
        time_step : float
            The interval when the signal is to be sampled (that is, the duration
            of each segment of the discretized signal). It must be positive and
            shorter than the total duration of the signal.

        Returns
        -------
        np.ndarray
            An array with the values of the signal sampled at equal intervals.
            The value of the signal in each segment corresponds to the value of
            the function at the center of that segment.

        Warnings
        --------
        If the time step passed doesn't exactly divide the total duration of
        the signal, this function will round the number of segments of the
        discretized output to the nearest number that is an integer multiple of
        the time step.
        """
        Checker.VALUE(
            time_step > 0, "The time step must be positive.", {"time_step": time_step}
        )
        Checker.VALUE(
            self.duration >= time_step,
            "The time step must not be longer than the duration of the signal.",
            {"duration": self.duration, "time_step": time_step},
        )

        segment_count = int(np.round(self.duration / time_step))
        times = (np.arange(segment_count) + 0.5) * time_step

        return self._function(times)

    def export_with_sampling_rate(self, sampling_rate: float) -> np.ndarray:
        """
        Return the values of the signal sampled at a constant rate given by the
        sampling rate provided.

        Parameters
        ----------
        sampling_rate : float
            The rate at which the signal is sampled (that is, the inverse of the
            duration of each segment of the discretized signal). It must be
            positive and larger than the inverse of the duration.

        Returns
        -------
        np.ndarray
            An array with the values of the signal sampled at equal intervals.
            The value of the signal in each segment corresponds to the value of
            the function at the center of that segment.

        Warnings
        --------
        If the inverse of the sampling rate passed doesn't exactly divide the
        total duration of the signal, this function will round the number of
        segments of the discretized output to the nearest number that is an
        integer multiple of the inverse of the sampling rate.
        """
        Checker.VALUE(
            sampling_rate > 0,
            "The sampling rate must be positive.",
            {"sampling_rate": sampling_rate},
        )
        time_step = 1 / sampling_rate
        Checker.VALUE(
            self.duration >= time_step,
            "The inverse of the sampling rate must not be longer than the"
            " duration of the signal.",
            {"duration": self.duration, "1/sampling_rate": time_step},
        )

        segment_count = int(np.round(self.duration / time_step))
        times = (np.arange(segment_count) + 0.5) * time_step

        return self._function(times)


@_no_graph_parameters(alternatives="`graph.signals.square_pulse_pwc`")
def square_pulse(
    duration: float,
    amplitude: float | complex,
    start_time: float = 0.0,
    end_time: Optional[float] = None,
) -> Signal:
    r"""
    Create a `Signal` object representing a square pulse.

    Parameters
    ----------
    duration : float
         The duration of the pulse.
    amplitude : float or complex
        The amplitude of the square pulse, :math:`A`.
    start_time : float, optional
        The start time of the square pulse, :math:`t_0`.
        Defaults to 0.
    end_time : float or None, optional
        The end time of the square pulse, :math:`t_1`.
        Must be greater than the start time.
        Defaults to the `duration`.

    Returns
    -------
    Signal
        The square pulse.

    See Also
    --------
    :func:`boulderopal.signals.cosine_pulse`
        Create a `Signal` object representing a cosine pulse.
    :func:`boulderopal.signals.gaussian_pulse`
        Create a `Signal` object representing a Gaussian pulse.
    :func:`boulderopal.signals.sech_pulse`
        Create a `Signal` object representing a hyperbolic secant pulse.
    :func:`Graph.signals.square_pulse_pwc <boulderopal.graph.signals.square_pulse_pwc>`
        Graph operation to create a `Pwc` representing a square pulse.

    Notes
    -----
    The square pulse is defined as

    .. math:: \mathop{\mathrm{Square}}(t) = A \theta(t-t_0) \theta(t_1-t) ,

    where :math:`\theta(t)` is the
    `Heaviside step function <https://en.wikipedia.org/wiki/Heaviside_step_function>`_.

    Examples
    --------
    Define a square pulse and discretize it.

    >>> pulse = bo.signals.square_pulse(duration=4.0, amplitude=2.5, start_time=1.0, end_time=3.0)
    >>> pulse.export_with_time_step(time_step=1.0)
    array([0. , 2.5, 2.5, 0. ])
    """
    if end_time is None:
        end_time = duration

    Checker.VALUE(
        end_time > start_time,
        "The end time must be greater than the start time.",
        {"start_time": start_time, "end_time": end_time},
    )

    return Signal(
        function=lambda times: np.where(
            np.logical_and(times >= start_time, times <= end_time), amplitude, 0.0
        ),
        duration=duration,
    )


@_no_graph_parameters(alternatives="`graph.signals.cosine_pwc`")
def cosine_pulse(
    duration: float,
    amplitude: float | complex,
    drag: float = 0.0,
    start_time: float = 0.0,
    end_time: Optional[float] = None,
    flat_duration: float = 0.0,
) -> Signal:
    r"""
    Create a `Signal` object representing a cosine pulse.

    Parameters
    ----------
    duration : float
         The duration of the pulse.
    amplitude : float or complex
        The amplitude of the pulse, :math:`A`.
    drag : float, optional
        The DRAG parameter, :math:`\beta`.
        Defaults to 0, in which case there is no DRAG correction.
    start_time : float, optional
        The time at which the cosine pulse starts, :math:`t_\mathrm{start}`.
        Defaults to 0.
    end_time : float or None, optional
        The time at which the cosine pulse ends, :math:`t_\mathrm{end}`.
        Defaults to the `duration`.
    flat_duration : float, optional
        The amount of time that the pulse remains constant after the peak of
        the cosine, :math:`t_\mathrm{flat}`.
        If passed, it must be nonnegative and less than the difference between
        `end_time` and `start_time`.
        Defaults to 0, in which case no constant part is added to the cosine pulse.

    Returns
    -------
    Signal
        The cosine pulse.

    See Also
    --------
    :func:`boulderopal.signals.gaussian_pulse`
        Create a `Signal` object representing a Gaussian pulse.
    :func:`boulderopal.signals.hann_series`
        Create a `Signal` object representing a sum of Hann window functions.
    :func:`boulderopal.signals.sech_pulse`
        Create a `Signal` object representing a hyperbolic secant pulse.
    :func:`boulderopal.signals.sinusoid`
        Create a `Signal` object representing a sinusoidal oscillation.
    :func:`boulderopal.signals.square_pulse`
        Create a `Signal` object representing a square pulse.
    :func:`Graph.signals.cosine_pulse_pwc <boulderopal.graph.signals.cosine_pulse_pwc>`
        Graph operation to create a `Pwc` representing a cosine pulse.

    Notes
    -----
    The cosine pulse is defined as

    .. math:: \mathop{\mathrm{Cos}}(t) =
        \begin{cases}
        0
        &\mathrm{if} \quad t < t_\mathrm{start} \\
        \frac{A}{2} \left[1+\cos \left(\omega \{t-\tau_-\} \right)
        + i\omega\beta \sin \left(\omega \{t-\tau_-\}\right)\right]
        &\mathrm{if} \quad t_\mathrm{start} \le t < \tau_- \\
        A
        &\mathrm{if} \quad \tau_- \le t \le \tau_+ \\
        \frac{A}{2} \left[1+\cos \left(\omega\{t-\tau_+\}\right)
        + i\omega \beta\sin \left(\omega \{t-\tau_+\}\right)\right]
        &\mathrm{if} \quad \tau_+ < t \le t_\mathrm{end} \\
        0
        &\mathrm{if} \quad t > t_\mathrm{end} \\
        \end{cases},

    where :math:`\omega=2\pi /(t_\mathrm{end}-t_\mathrm{start} - t_\mathrm{flat})`,
    :math:`\tau_\mp` are the start/end times of the flat segment,
    with :math:`\tau_\mp=(t_\mathrm{start}+t_\mathrm{end} \mp t_\mathrm{flat})/2`.

    If the flat duration is zero (the default setting), this reduces to

    .. math:: \mathop{\mathrm{Cos}}(t) =
        \frac{A}{2} \left[1+\cos \left(\omega \{t-\tau\} \right)
        + i\omega\beta \sin \left(\omega \{t-\tau\}\right)\right]
        \theta(t-t_\mathrm{start}) \theta(t_\mathrm{end}-t),

    where now :math:`\omega=2\pi /(t_\mathrm{end}-t_\mathrm{start})`,
    :math:`\tau=(t_\mathrm{start}+t_\mathrm{end})/2`
    and :math:`\theta(t)` is the
    `Heaviside step function <https://en.wikipedia.org/wiki/Heaviside_step_function>`_.

    Examples
    --------
    Define a cosine pulse.

    >>> pulse = bo.signals.cosine_pulse(duration=3.0, amplitude=1.0)
    >>> pulse.export_with_time_step(time_step=0.5)
    array([0.0669873+0.j, 0.5      +0.j, 0.9330127+0.j, 0.9330127+0.j,
           0.5      +0.j, 0.0669873+0.j])

    Define a flat-top cosine pulse with a DRAG correction.

    >>> pulse = bo.signals.cosine_pulse(
    ...     duration=3.0, amplitude=1.0, drag=0.1, flat_duration=0.6
    ... )
    >>> pulse.export_with_sampling_rate(sampling_rate=2.0)
    array([0.10332333-0.07968668j, 0.69134172-0.12093555j,
           1.        +0.j        , 1.        +0.j        ,
           0.69134172+0.12093555j, 0.10332333+0.07968668j])
    """
    if end_time is None:
        end_time = duration

    Checker.VALUE(
        end_time > start_time,
        "The end time must be greater than the start time.",
        {"start_time": start_time, "end_time": end_time},
    )
    Checker.VALUE(
        0 <= flat_duration <= (end_time - start_time),
        "The duration of the flat part of the pulse has to be nonnegative and"
        "smaller than or equal to the total duration of the pulse.",
        {
            "flat_duration": flat_duration,
            "start_time": start_time,
            "end_time": end_time,
        },
    )

    pulse_period = end_time - start_time - flat_duration

    flat_segment_start = start_time + 0.5 * pulse_period
    flat_segment_end = end_time - 0.5 * pulse_period

    angular_frequency = 2.0 * np.pi / pulse_period

    def _cosine_pulse(times: np.ndarray) -> np.ndarray:
        shifted_times = np.where(
            times <= flat_segment_start,
            times - flat_segment_start,
            times - flat_segment_end,
        )
        values = (0.5 * amplitude) * (
            1
            + np.cos(angular_frequency * shifted_times)
            + (angular_frequency * drag * 1j)
            * np.sin(angular_frequency * shifted_times)
        )

        # Make pulse flat for the duration of the "flat segment".
        flat_values = np.where(
            np.logical_and(times > flat_segment_start, times < flat_segment_end),
            amplitude,
            values,
        )

        # Make the pulse zero before its start and after its end.
        limited_values = np.where(
            np.logical_and(times > start_time, times < end_time), flat_values, 0
        )
        return limited_values

    return Signal(function=_cosine_pulse, duration=duration)


@_no_graph_parameters(
    alternatives="`graph.signals.sinusoid_pwc` or `graph.signals.sinusoid_stf`"
)
def sinusoid(
    duration: float,
    amplitude: float | complex,
    angular_frequency: float,
    phase: float = 0.0,
) -> Signal:
    r"""
    Create a `Signal` object representing a sinusoidal oscillation.

    Parameters
    ----------
    duration : float
        The duration of the oscillation.
    amplitude : float or complex
        The amplitude of the oscillation, :math:`A`.
    angular_frequency : float
        The angular frequency of the oscillation, :math:`\omega`.
    phase : float, optional
        The phase of the oscillation, :math:`\phi`.
        Defaults to 0.

    Returns
    -------
    Signal
        The sinusoidal oscillation.

    See Also
    --------
    :func:`boulderopal.signals.cosine_pulse`
        Create a `Signal` object representing a cosine pulse.
    :func:`boulderopal.signals.hann_series`
        Create a `Signal` object representing a sum of Hann window functions.
    :func:`Graph.signals.sinusoid_pwc <boulderopal.graph.signals.sinusoid_pwc>`
        Graph operation to create a `Pwc` representing a sinusoidal oscillation.
    :func:`Graph.signals.sinusoid_stf <boulderopal.graph.signals.sinusoid_stf>`
        Graph operation to create a `Stf` representing a sinusoidal oscillation.

    Notes
    -----
    The sinusoid is defined as

    .. math:: \mathop{\mathrm{Sinusoid}}(t) = A \sin \left( \omega t + \phi \right) .

    Examples
    --------
    Define a sinusoidal oscillation.

    >>> signal = bo.signals.sinusoid(
    ...     duration=2.0,
    ...     amplitude=1.0,
    ...     angular_frequency=np.pi,
    ...     phase=np.pi/2.0,
    ... )
    >>> signal.export_with_sampling_rate(sampling_rate=0.25)
    array([ 0.92387953,  0.38268343, -0.38268343, -0.92387953, -0.92387953,
       -0.38268343,  0.38268343,  0.92387953])
    """

    return Signal(
        function=lambda times: amplitude * np.sin(angular_frequency * times + phase),
        duration=duration,
    )


@_no_graph_parameters(
    alternatives="`graph.signals.hann_series_pwc` or `graph.signals.hann_series_stf`"
)
def hann_series(duration: float, coefficients: np.ndarray) -> Signal:
    r"""
    Create a `Signal` object representing a sum of Hann window functions.

    Parameters
    ----------
    duration : float
        The duration of the signal, :math:`T`.
    coefficients : np.ndarray
        The coefficients for the different Hann window functions, :math:`c_n`.
        It must be a 1D array.

    Returns
    -------
    Signal
        The Hann window functions series.

    See Also
    --------
    :func:`boulderopal.signals.cosine_pulse`
        Create a `Signal` object representing a cosine pulse.
    :func:`boulderopal.signals.sinusoid`
        Create a `Signal` object representing a sinusoidal oscillation.
    :func:`Graph.signals.hann_series_pwc <boulderopal.graph.signals.hann_series_pwc>`
        Graph operation to create a `Pwc` representing a sum of Hann window functions.
    :func:`Graph.signals.hann_series_stf <boulderopal.graph.signals.hann_series_stf>`
        Graph operation to create an `Stf` representing a sum of Hann window functions.

    Notes
    -----
    The series is defined as

    .. math:: \mathop{\mathrm{Hann}}(t)
        = \sum_{n=1}^N c_n \sin^2 \left( \frac{\pi n t}{T} \right) ,

    where :math:`N` is the number of coefficients.

    Examples
    --------
    Define a simple Hann series.

    >>> signal = bo.signals.hann_series(
    ...     duration=5.0,
    ...     coefficients=np.array([0.5, 1, 0.25]),
    ... )
    >>> signal.export_with_time_step(time_step=0.5)
    array([0.15925422, 1.00144425, 1.375     , 1.05757275, 0.78172879,
       0.78172879, 1.05757275, 1.375     , 1.00144425, 0.15925422])
    """

    Checker.VALUE(
        len(coefficients.shape) == 1,
        "The coefficients must be in a 1D array.",
        {"coefficients.shape": coefficients.shape},
    )

    nss = np.arange(1, coefficients.shape[0] + 1)

    return Signal(
        function=lambda times: np.sum(
            coefficients * np.sin(np.pi * nss * times[:, None] / duration) ** 2, axis=1
        ),
        duration=duration,
    )


@_no_graph_parameters(
    alternatives="`graph.signals.linear_ramp_pwc` or `graph.signals.linear_ramp_stf`"
)
def linear_ramp(
    duration: float,
    end_value: float | complex,
    start_value: Optional[float | complex] = None,
    start_time: float = 0.0,
    end_time: Optional[float] = None,
) -> Signal:
    r"""
    Create a `Signal` object representing a linear ramp.

    Parameters
    ----------
    duration : float
        The duration of the signal, :math:`T`.
    end_value : float or complex
        The value of the ramp at :math:`t = t_\mathrm{end}`, :math:`a_\mathrm{end}`.
    start_value : float or complex or None, optional
        The value of the ramp at :math:`t = t_\mathrm{start}`, :math:`a_\mathrm{start}`.
        Defaults to :math:`-a_\mathrm{end}`.
    start_time : float, optional
        The time at which the linear ramp starts, :math:`t_\mathrm{start}`.
        Defaults to 0.
    end_time : float or None, optional
        The time at which the linear ramp ends, :math:`t_\mathrm{end}`.
        Defaults to the given duration :math:`T`.

    Returns
    -------
    Signal
        The linear ramp.

    See Also
    --------
    :func:`Graph.signals.linear_ramp_pwc <boulderopal.graph.signals.linear_ramp_pwc>`
        Graph operation to create a `Pwc` representing a linear ramp.
    :func:`Graph.signals.linear_ramp_stf <boulderopal.graph.signals.linear_ramp_stf>`
        Graph operation to create a `Stf` representing a linear ramp.
    :func:`boulderopal.signals.tanh_ramp`
        Create a `Signal` object representing a hyperbolic tangent ramp.

    Notes
    -----
    The linear ramp is defined as

    .. math:: \mathop{\mathrm{Linear}}(t) =
        \begin{cases}
            a_\mathrm{start} &\mathrm{if} \quad t < t_\mathrm{start}\\
            a_\mathrm{start} + (a_\mathrm{end} - a_\mathrm{start})
                \frac{t - t_\mathrm{start}}{t_\mathrm{end} - t_\mathrm{start}}
                &\mathrm{if} \quad t_\mathrm{start} \le t \le t_\mathrm{end} \\
            a_\mathrm{end} &\mathrm{if} \quad t > t_\mathrm{end}
        \end{cases} .

    Examples
    --------
    Define a linear ramp with start and end times.

    >>> signal = bo.signals.linear_ramp(
    ...     duration=4, end_value=2, start_time=1, end_time=3
    ... )
    >>> signal.export_with_time_step(time_step=0.25)
    array([-2.  , -2.  , -2.  , -2.  , -1.75, -1.25, -0.75, -0.25,  0.25,
        0.75,  1.25,  1.75,  2.  ,  2.  ,  2.  ,  2.  ])
    """
    if start_value is None:
        start_value = -end_value

    if end_time is None:
        end_time = duration

    Checker.VALUE(
        start_time < end_time,
        "The end time of the pulse must be greater than the start time.",
        {"end_time": end_time, "start_time": start_time},
    )

    slope = (end_value - start_value) / (end_time - start_time)

    def _linear_ramp(times: np.ndarray) -> np.ndarray:
        assert start_value is not None  # make mypy happy
        result = np.where(times > end_time, end_value - start_value, 0.0)
        result += start_value + np.where(
            np.logical_and(times >= start_time, times <= end_time),
            slope * (times - start_time),
            0,
        )
        return result

    return Signal(function=_linear_ramp, duration=duration)


@_no_graph_parameters(
    alternatives="`graph.signals.tanh_ramp_pwc` or `graph.signals.tanh_ramp_stf`"
)
def tanh_ramp(
    duration: float,
    end_value: float | complex,
    start_value: Optional[float | complex] = None,
    ramp_duration: Optional[float] = None,
    center_time: Optional[float] = None,
) -> Signal:
    r"""
    Create a `Signal` object representing a hyperbolic tangent ramp.

    Parameters
    ----------
    duration : float
        The duration of the signal, :math:`T`.
    end_value : float or complex
        The asymptotic value of the ramp towards :math:`t \to +\infty`, :math:`a_+`.
    start_value : float or complex or None, optional
        The asymptotic value of the ramp towards :math:`t \to -\infty`, :math:`a_-`.
        Defaults to minus `end_value`.
    ramp_duration : float or None, optional
        The characteristic time for the hyperbolic tangent ramp, :math:`t_\mathrm{ramp}`.
        Defaults to :math:`T/6`.
    center_time : float or None, optional
        The time at which the ramp has its greatest slope, :math:`t_0`.
        Defaults to :math:`T/2`.

    Returns
    -------
    Signal
        The hyperbolic tangent ramp.

    See Also
    --------
    :func:`boulderopal.signals.linear_ramp`
        Create a `Signal` object representing a linear ramp.
    :func:`Graph.signals.tanh_ramp_pwc <boulderopal.graph.signals.tanh_ramp_pwc>`
        Graph operation to create a `Pwc` representing a hyperbolic tangent ramp.
    :func:`Graph.signals.tanh_ramp_stf <boulderopal.graph.signals.tanh_ramp_stf>`
        Graph operation to create a `Stf` representing a hyperbolic tangent ramp.

    Notes
    -----
    The hyperbolic tangent ramp is defined as

    .. math:: \mathop{\mathrm{Tanh}}(t)
        = \frac{a_+ + a_-}{2}
            + \frac{a_+ - a_-}{2} \tanh\left( \frac{t - t_0}{t_\mathrm{ramp}} \right) ,

    where the function's asymptotic values :math:`a_\pm` are defined by:

    .. math::  a_\pm := \lim_{t\to\pm\infty} \mathop{\mathrm{Tanh}}(t) ,

    and :math:`t_0` is related to :math:`t_\mathrm{ramp}` by:

    .. math::
        \left.\frac{{\mathrm d}\mathop{\mathrm{Tanh}}(t)}{{\mathrm d}t}\right|_{t=t_0}
            = \frac{ (a_+ - a_-)}{2 t_\mathrm{ramp}} .

    Note that if :math:`t_0` is close to the edges of the ramp,
    for example :math:`t_0 \lesssim 2 t_\mathrm{ramp}`,
    then the first and last values of the outputted array will differ from the
    expected asymptotic values.

    With the default values of `start_value` (:math:`a_-`),
    `ramp_duration` (:math:`t_\mathrm{ramp}`), and `center_time` (:math:`t_0`),
    the ramp expression simplifies to

    .. math:: \mathop{\mathrm{Tanh}}(t) = A \tanh\left( \frac{t - T/2}{T/6} \right),

    where :math:`A = a_+` is the end value (the start value is then :math:`-A`).
    This defines a symmetric ramp (around :math:`(T/2, 0)`)
    between :math:`-0.995 A` (at :math:`t=0`) and :math:`0.995 A` (at :math:`t=T`).

    Examples
    --------
    Define a tanh ramp.

    >>> signal = bo.signals.tanh_ramp(
    ...     duration=4, end_value=2, start_value=1, ramp_duration=0.4, center_time=2.
    ... )
    >>> signal.export_with_time_step(time_step=0.4)
    array([1.00012339, 1.00091105, 1.00669285, 1.04742587, 1.26894142,
       1.73105858, 1.95257413, 1.99330715, 1.99908895, 1.99987661])
    """
    if start_value is None:
        start_value = -end_value

    if ramp_duration is None:
        ramp_duration = duration / 6

    if center_time is None:
        center_time = duration / 2

    assert start_value is not None  # make mypy happy

    def _tanh_ramp(times: np.ndarray) -> np.ndarray:
        return start_value + 0.5 * (end_value - start_value) * (
            1 + np.tanh((times - center_time) / ramp_duration)
        )

    return Signal(function=_tanh_ramp, duration=duration)


@_no_graph_parameters(
    alternatives="`graph.signals.sech_pulse_pwc` or `graph.signals.sech_pulse_stf`"
)
def sech_pulse(
    duration: float,
    amplitude: float | complex,
    width: Optional[float] = None,
    center_time: Optional[float] = None,
) -> Signal:
    r"""
    Create a `Signal` object representing a hyperbolic secant pulse.

    Parameters
    ----------
    duration : float
        The duration of the signal, :math:`T`.
    amplitude : float or complex
        The amplitude of the pulse, :math:`A`.
    width : float or None, optional
        The characteristic time for the hyperbolic secant pulse, :math:`t_\mathrm{pulse}`.
        Defaults to :math:`T/12`,
        giving the pulse a full width at half maximum (FWHM) of :math:`0.22 T`.
    center_time : float or None, optional
        The time at which the pulse peaks, :math:`t_\mathrm{peak}`.
        Defaults to :math:`T/2`.

    Returns
    -------
    Signal
        The hyperbolic secant pulse.

    See Also
    --------
    :func:`boulderopal.signals.cosine_pulse`
        Create a `Signal` object representing a cosine pulse.
    :func:`boulderopal.signals.gaussian_pulse`
        Create a `Signal` object representing a Gaussian pulse.
    :func:`Graph.signals.sech_pulse_pwc <boulderopal.graph.signals.sech_pulse_pwc>`
        Graph operation to create a `Pwc` representing a hyperbolic secant pulse.
    :func:`Graph.signals.sech_pulse_stf <boulderopal.graph.signals.sech_pulse_stf>`
        Graph operation to create a `Stf` representing a hyperbolic secant pulse.
    :func:`boulderopal.signals.square_pulse`
        Create a `Signal` object representing a square pulse.

    Notes
    -----
    The hyperbolic secant pulse is defined as

    .. math:: \mathop{\mathrm{Sech}}(t)
        = \frac{A}{\cosh\left((t - t_\mathrm{peak}) / t_\mathrm{pulse} \right)} .

    The FWHM of the pulse is about :math:`2.634 t_\mathrm{pulse}`.

    Examples
    --------
    Define a displaced sech pulse.

    >>> pulse = bo.signals.sech_pulse(duration=1, amplitude=1, center_time=0.4)
    >>> pulse.export_with_time_step(time_step=0.1)
    array([0.02998441, 0.09932793, 0.32180487, 0.84355069, 0.84355069,
       0.32180487, 0.09932793, 0.02998441, 0.00903298, 0.00272073])
    """
    if width is None:
        width = duration / 12

    if center_time is None:
        center_time = duration / 2

    return Signal(
        function=lambda times: amplitude / np.cosh((times - center_time) / width),
        duration=duration,
    )


@_no_graph_parameters(
    alternatives="`graph.signals.gaussian_pulse_pwc` or `graph.signals.gaussian_pulse_stf`"
)
def gaussian_pulse(
    duration: float,
    amplitude: float | complex,
    width: Optional[float] = None,
    center_time: Optional[float] = None,
    drag: float = 0.0,
    flat_duration: float = 0.0,
) -> Signal:
    r"""
    Create a `Signal` object representing a Gaussian pulse.

    Parameters
    ----------
    duration : float
        The duration of the signal, :math:`T`.
    amplitude : float or complex
        The amplitude of the Gaussian pulse, :math:`A`.
    width : float or None, optional
        The standard deviation of the Gaussian pulse, :math:`\sigma`.
        Defaults to :math:`T/10` or :math:`(T-t_\mathrm{flat})/10` if `flat_duration` is passed.
    center_time : float or None, optional
        The center of the Gaussian pulse, :math:`t_0`.
        Defaults to half of the given value of the duration, :math:`T/2`.
    drag : float, optional
        The DRAG parameter, :math:`\beta`.
        Defaults to 0, in which case there is no DRAG correction.
    flat_duration : float, optional
        The amount of time to remain constant after the peak of the Gaussian,
        :math:`t_\mathrm{flat}`.
        If passed, it must be nonnegative and less than the duration.
        Defaults to 0, in which case no constant part is added to the Gaussian pulse.

    Returns
    -------
    Signal
        The Gaussian pulse.

    See Also
    --------
    :func:`boulderopal.signals.cosine_pulse`
        Create a `Signal` object representing a cosine pulse.
    :func:`Graph.signals.gaussian_pulse_pwc <boulderopal.graph.signals.gaussian_pulse_pwc>`
        Graph operation to create a `Pwc` representing a Gaussian pulse.
    :func:`Graph.signals.gaussian_pulse_stf <boulderopal.graph.signals.gaussian_pulse_stf>`
        Graph operation to create a `Stf` representing a Gaussian pulse.
    :func:`boulderopal.signals.sech_pulse`
        Create a `Signal` object representing a hyperbolic secant pulse.
    :func:`boulderopal.signals.square_pulse`
        Create a `Signal` object representing a square pulse.

    Notes
    -----
    The Gaussian pulse is defined as

    .. math:: \mathop{\mathrm{Gaussian}}(t) =
        \begin{cases}
            A \left(1-\frac{i\beta (t-t_1)}{\sigma^2}\right)
            \exp \left(- \frac{(t-t_1)^2}{2\sigma^2} \right)
                &\mathrm{if} \quad t < t_1=t_0- t_\mathrm{flat}/2\\
            A
                &\mathrm{if} \quad t_0-t_\mathrm{flat}/2 \le t < t_0+t_\mathrm{flat}/2 \\
            A \left(1-\frac{i\beta (t-t_2)}{\sigma^2}\right)
            \exp \left(- \frac{(t-t_2)^2}{2\sigma^2} \right)
                &\mathrm{if} \quad t > t_2=t_0+t_\mathrm{flat}/2
        \end{cases} .

    If the flat duration is zero (the default setting), this reduces to

    .. math:: \mathop{\mathrm{Gaussian}}(t) =
        A \left(1-\frac{i\beta (t-t_0)}{\sigma^2}\right)
        \exp \left(- \frac{(t-t_0)^2}{2\sigma^2} \right) .

    Examples
    --------
    Define a Gaussian pulse.

    >>> pulse = bo.signals.gaussian_pulse(duration=2.0, amplitude=1.0)
    >>> pulse.export_with_time_step(time_step=0.2)
    array([4.00652974e-05+0.j, 2.18749112e-03+0.j, 4.39369336e-02+0.j,
       3.24652467e-01+0.j, 8.82496903e-01+0.j, 8.82496903e-01+0.j,
       3.24652467e-01+0.j, 4.39369336e-02+0.j, 2.18749112e-03+0.j,
       4.00652974e-05+0.j])

    Define a flat-top Gaussian pulse with a DRAG correction.

    >>> pulse = bo.signals.gaussian_pulse(
    ...     duration=1.0,
    ...     amplitude=1.0,
    ...     width=0.2,
    ...     center_time=0.6,
    ...     drag=0.1,
    ...     flat_duration=0.2,
    ... )
    >>> pulse.export_with_sampling_rate(sampling_rate=10.)
    array([0.07955951+0.08950445j, 0.21626517+0.18923202j,
       0.45783336+0.28614585j, 0.7548396 +0.28306485j,
       0.96923323+0.12115415j, 1.        +0.j        ,
       1.        +0.j        , 0.96923323-0.12115415j,
       0.7548396 -0.28306485j, 0.45783336-0.28614585j])
    """

    Checker.VALUE(
        0.0 <= flat_duration < duration,
        "The flat duration must be nonnegative and less than the duration.",
        {"flat_duration": flat_duration, "duration": duration},
    )

    if center_time is None:
        center_time = 0.5 * duration

    if width is None:
        if flat_duration is None:
            width = duration / 10
        else:
            width = (duration - flat_duration) / 10

    # Time at which first Gaussian ends.
    flat_segment_start = center_time - 0.5 * flat_duration
    # Time at which second Gaussian starts.
    flat_segment_end = center_time + 0.5 * flat_duration

    def _gaussian_pulse(times: np.ndarray) -> np.ndarray:
        assert width is not None  # make mypy happy

        shifted_times = np.where(
            times <= flat_segment_start,
            times - flat_segment_start,
            times - flat_segment_end,
        )

        values = amplitude * (1.0 - 1j * drag * shifted_times / (width**2))
        values *= np.exp(-(shifted_times**2) / (2 * width**2))

        # Make pulse flat for the duration of the "flat segment".
        flat_values = np.where(
            np.logical_and(times > flat_segment_start, times < flat_segment_end),
            amplitude,
            values,
        )

        return flat_values

    return Signal(function=_gaussian_pulse, duration=duration)
