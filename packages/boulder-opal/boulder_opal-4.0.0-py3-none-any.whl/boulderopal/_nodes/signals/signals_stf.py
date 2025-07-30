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
STF signal library nodes.
"""

from __future__ import annotations

from typing import (
    TYPE_CHECKING,
    Optional,
    Union,
)

import numpy as np

from boulderopal._nodes.node_data import (
    Stf,
    Tensor,
)
from boulderopal._nodes.validation import (
    ShapeT,
    positive_scalar,
    scalar,
    shapeable,
)
from boulderopal._typing import Annotated
from boulderopal._validation import (
    Checker,
    ScalarT,
    pipe,
    validated,
)

if TYPE_CHECKING:
    from boulderopal.graph._graph import Graph


class StfSignals:
    """
    Base class implementing Stf signal graph methods.
    """

    def __init__(self, graph: "Graph") -> None:
        self._graph = graph

    @validated
    def sech_pulse_stf(
        self,
        amplitude: Annotated[Union[float, complex, Tensor], pipe(scalar)],
        width: Annotated[Union[float, Tensor], pipe(positive_scalar)],
        center_time: Annotated[Union[float, Tensor], pipe(scalar)],
    ) -> Stf:
        r"""
        Create an `Stf` representing a hyperbolic secant pulse.

        Parameters
        ----------
        amplitude : float or complex or Tensor
            The amplitude of the pulse, :math:`A`.
            It must either be a scalar or contain a single element.
        width : float or Tensor
            The characteristic time for the hyperbolic secant pulse, :math:`t_\mathrm{pulse}`.
            It must either be a scalar or contain a single element.
        center_time : float or Tensor
            The time at which the pulse peaks, :math:`t_\mathrm{peak}`.
            It must either be a scalar or contain a single element.

        Returns
        -------
        Stf
            The sampleable hyperbolic secant pulse.

        See Also
        --------
        :func:`Graph.signals.gaussian_pulse_stf <signals.gaussian_pulse_stf>`
            Create an `Stf` representing a Gaussian pulse.
        :func:`boulderopal.signals.sech_pulse`
            Create a `Signal` object representing a hyperbolic secant pulse.
        :func:`Graph.signals.sech_pulse_pwc <signals.sech_pulse_pwc>`
            Corresponding operation with `Pwc` output.

        Notes
        -----
        The hyperbolic secant pulse is defined as

            .. math:: \mathop{\mathrm{Sech}}(t)
                = \frac{A}{\cosh\left((t - t_\mathrm{peak}) / t_\mathrm{pulse} \right)} .

        The full width at half maximum of the pulse is about :math:`2.634 t_\mathrm{pulse}`.

        Examples
        --------
        Define a sampleable sech pulse.

        >>> sech = graph.signals.sech_pulse_stf(
        ...     amplitude=1.0, width=0.1, center_time=0.5
        ... )
        >>> graph.discretize_stf(stf=sech, duration=1.2, segment_count=5, name="sech")
        <Pwc: name="sech", operation_name="discretize_stf", value_shape=(), batch_shape=()>
        >>> result = bo.execute_graph(graph=graph, output_node_names="sech")
        >>> result["output"]["sech"]
        {'durations': array([0.24, 0.24, 0.24, 0.24, 0.24]),
        'values': array([0.04471916, 0.46492199, 0.64805427, 0.06667228, 0.00605505]),
        'time_dimension': 0}

        Define a sampleable sech pulse with optimizable parameters.

        >>> amplitude = graph.optimizable_scalar(
        ...     lower_bound=0, upper_bound=2.*np.pi, name="amplitude"
        ... )
        >>> width = graph.optimizable_scalar(
        ...     lower_bound=0.1, upper_bound=0.5, name="width"
        ... )
        >>> center_time = graph.optimizable_scalar(
        ...     lower_bound=0.2, upper_bound=0.8, name="center_time"
        ... )
        >>> graph.signals.sech_pulse_stf(
        ...     amplitude=amplitude, width=width, center_time=center_time
        ... )
        <Stf: operation_name="truediv", value_shape=(), batch_shape=()>
        """

        return amplitude / self._graph.cosh(  # type:ignore
            (self._graph.identity_stf() - center_time) / width
        )

    @validated
    def gaussian_pulse_stf(
        self,
        amplitude: Annotated[Union[float, complex, Tensor], pipe(scalar)],
        width: Annotated[Union[float, Tensor], pipe(positive_scalar)],
        center_time: Annotated[Union[float, Tensor], pipe(scalar)],
        drag: Optional[Annotated[Union[float, Tensor], pipe(scalar)]] = None,
    ) -> Stf:
        r"""
        Create an `Stf` representing a Gaussian pulse.

        Parameters
        ----------
        amplitude : float or complex or Tensor
            The amplitude of the Gaussian pulse, :math:`A`.
            It must either be a scalar or contain a single element.
        width : float or Tensor
            The standard deviation of the Gaussian pulse, :math:`\sigma`.
            It must either be a scalar or contain a single element.
        center_time : float or Tensor
            The center of the Gaussian pulse, :math:`t_0`.
            It must either be a scalar or contain a single element.
        drag : float or Tensor or None, optional
            The DRAG parameter, :math:`\beta`.
            If passed, it must either be a scalar or contain a single element.
            Defaults to no DRAG correction.

        Returns
        -------
        Stf
            The sampleable Gaussian pulse.

        See Also
        --------
        :func:`Graph.signals.gaussian_pulse_pwc <signals.gaussian_pulse_pwc>`
            Corresponding operation with `Pwc` output.
        :func:`Graph.signals.sech_pulse_stf <signals.sech_pulse_stf>`
            Create an `Stf` representing a hyperbolic secant pulse.

        Notes
        -----
        The Gaussian pulse is defined as

        .. math:: \mathop{\mathrm{Gaussian}}(t) =
            A \left(1-\frac{i\beta (t-t_0)}{\sigma^2}\right)
            \exp \left(- \frac{(t-t_0)^2}{2\sigma^2} \right) .

        Examples
        --------
        Define a sampleable Gaussian pulse.

        >>> gaussian = graph.signals.gaussian_pulse_stf(
        ...     amplitude=1.0, width=0.1, center_time=0.5
        ... )
        >>> graph.discretize_stf(
        ...     gaussian, duration=1, segment_count=5, name="gaussian"
        ... )
        <Pwc: name="gaussian", operation_name="discretize_stf", value_shape=(), batch_shape=()>
        >>> result = bo.execute_graph(graph=graph, output_node_names="gaussian")
        >>> result["output"]["gaussian"]
        {'durations': array([0.2, 0.2, 0.2, 0.2, 0.2]),
        'values': array([3.35462628e-04, 1.35335283e-01, 1.00000000e+00, 1.35335283e-01,
                3.35462628e-04]),
        'time_dimension': 0}

        Define a sampleable Gaussian with a DRAG correction.

        >>> drag_gaussian = graph.signals.gaussian_pulse_stf(
        ...     amplitude=1.0, width=0.1, center_time=0.5, drag=0.2
        ... )
        >>> graph.discretize_stf(
        ...     drag_gaussian, duration=1, segment_count=5, name="drag_gaussian"
        ... )
        <Pwc: name="drag_gaussian", operation_name="discretize_stf", value_shape=(), batch_shape=()>
        >>> result = bo.execute_graph(graph=graph, output_node_names="drag_gaussian")
        >>> result["output"]["drag_gaussian"]
        {'durations': array([0.2, 0.2, 0.2, 0.2, 0.2]),
        'values': array([3.35462628e-04+0.0026837j , 1.35335283e-01+0.54134113j,
                1.00000000e+00+0.j        , 1.35335283e-01-0.54134113j,
                3.35462628e-04-0.0026837j ]),
        'time_dimension': 0}

        Define a sampleable Gaussian pulse with optimizable parameters.

        >>> amplitude = graph.optimizable_scalar(
        ...     lower_bound=0, upper_bound=2.*np.pi, name="amplitude"
        ... )
        >>> width = graph.optimizable_scalar(
        ...     lower_bound=0.1, upper_bound=0.5, name="width"
        ... )
        >>> center_time = graph.optimizable_scalar(
        ...     lower_bound=0.2, upper_bound=0.8, name="center_time"
        ... )
        >>> drag = graph.optimizable_scalar(
        ...     lower_bound=0, upper_bound=0.5, name="drag"
        ... )
        >>> graph.signals.gaussian_pulse_stf(
        ...     amplitude=amplitude, width=width, center_time=center_time, drag=drag
        ... )
        <Stf: operation_name="multiply", value_shape=(), batch_shape=()>
        """
        if drag is not None:
            correction = -(1j * drag / (width**2)) * (
                self._graph.identity_stf() - center_time
            )
            amplitude *= 1.0 + correction

        return amplitude * self._graph.exp(  # type: ignore
            -((self._graph.identity_stf() - center_time) ** 2) / (2 * width**2)
        )

    @validated
    def sinusoid_stf(
        self,
        amplitude: Annotated[Union[float, complex, Tensor], pipe(scalar)],
        angular_frequency: Annotated[Union[float, Tensor], pipe(positive_scalar)],
        phase: Annotated[Union[float, Tensor], pipe(scalar)] = 0.0,
    ) -> Stf:
        r"""
        Create an `Stf` representing a sinusoidal oscillation.

        Parameters
        ----------
        amplitude : float or complex or Tensor
            The amplitude of the oscillation, :math:`A`.
            It must either be a scalar or contain a single element.
        angular_frequency : float or Tensor
            The angular frequency of the oscillation, :math:`\omega`.
            It must either be a scalar or contain a single element.
        phase : float or Tensor, optional
            The phase of the oscillation, :math:`\phi`.
            If passed, it must either be a scalar or contain a single element.
            Defaults to 0.

        Returns
        -------
        Stf
            The sampleable sinusoid.

        See Also
        --------
        :func:`Graph.signals.hann_series_stf <signals.hann_series_stf>`
            Create an `Stf` representing a sum of Hann window functions.
        :func:`boulderopal.signals.sinusoid`
            Create a `Signal` object representing a sinusoidal oscillation.
        :func:`Graph.signals.sinusoid_pwc <signals.sinusoid_pwc>`
            Corresponding operation with `Pwc` output.
        :func:`Graph.sin`
            Calculate the element-wise sine of an object.

        Notes
        -----
        The sinusoid is defined as

        .. math:: \mathop{\mathrm{Sinusoid}}(t) = A \sin \left( \omega t + \phi \right) .

        Examples
        --------
        Define an STF oscillation.

        >>> oscillation = graph.signals.sinusoid_stf(
        ...     amplitude=2.0, angular_frequency=3.0, phase=np.pi/4
        ... )
        >>> graph.discretize_stf(
        ...     oscillation, duration=10, segment_count=5, name="oscillation"
        ... )
        <Pwc: name="oscillation", operation_name="discretize_stf", value_shape=(), batch_shape=()>
        >>> result = bo.execute_graph(graph=graph, output_node_names="oscillation")
        >>> result["output"]["oscillation"]
        {'durations': array([2., 2., 2., 2., 2.]),
        'values': array([-1.20048699, -0.70570922, -0.15471507,  0.4086036 ,  0.93937314]),
        'time_dimension': 0}

        Define a sinusoid with optimizable parameters.

        >>> amplitude = graph.optimizable_scalar(
        ...     lower_bound=0, upper_bound=4e3, name="amplitude"
        ... )
        >>> angular_frequency = graph.optimizable_scalar(
        ...     lower_bound=5e6, upper_bound=20e6, name="angular_frequency"
        ... )
        >>> phase = graph.optimization_variable(
        ...     count=1,
        ...     lower_bound=0,
        ...     upper_bound=2*np.pi,
        ...     is_lower_unbounded=True,
        ...     is_upper_unbounded=True,
        ...     name="phase",
        ... )
        >>> graph.signals.sinusoid_stf(
        ...     amplitude=amplitude, angular_frequency=angular_frequency, phase=phase
        ... )
        <Stf: operation_name="multiply", value_shape=(), batch_shape=()>
        """
        return amplitude * self._graph.sin(  # type: ignore
            angular_frequency * self._graph.identity_stf() + phase
        )

    @validated
    def hann_series_stf(
        self,
        coefficients: Annotated[
            Union[np.ndarray, Tensor], pipe(shapeable, after=ShapeT.VECTOR().no_batch())
        ],
        end_time: Annotated[float, pipe(ScalarT.REAL())],
        start_time: Annotated[float, pipe(ScalarT.REAL())] = 0.0,
    ) -> Stf:
        r"""
        Create an `Stf` representing a sum of Hann window functions.

        Parameters
        ----------
        coefficients : np.ndarray or Tensor
            The coefficients for the different Hann window functions, :math:`c_n`.
            It must be a 1D array or Tensor.
        end_time : float
            The time at which the Hann series ends, :math:`t_\mathrm{end}`.
        start_time : float, optional
            The time at which the Hann series starts, :math:`t_\mathrm{start}`.
            Defaults to 0.

        Returns
        -------
        Stf
            The sampleable Hann window functions series.

        See Also
        --------
        :func:`boulderopal.signals.hann_series`
            Create a `Signal` object representing a sum of Hann window functions.
        :func:`Graph.signals.hann_series_pwc <signals.hann_series_pwc>`
            Corresponding operation with `Pwc` output.
        :func:`Graph.signals.sinusoid_stf <signals.sinusoid_stf>`
            Create an `Stf` representing a sinusoidal oscillation.

        Notes
        -----
        The series is defined as

        .. math:: \mathop{\mathrm{Hann}}(t)
            = \sum_{n=1}^N c_n \sin^2 \left(
                \frac{\pi n (t - t_\mathrm{start})}{t_\mathrm{end} - t_\mathrm{start}}
            \right) ,

        where :math:`N` is the number of coefficients.

        Note that the function values outside the :math:`(t_\mathrm{start}, t_\mathrm{end})` range
        will not be zero.

        Examples
        --------
        Define a simple sampleable Hann series.

        >>> hann = graph.signals.hann_series_stf(
        ...     coefficients=np.array([0.5, 1, 0.25]), end_time=1.0
        ... )
        >>> graph.discretize_stf(hann, duration=1, segment_count=5, name="hann")
        <Pwc: name="hann", operation_name="discretize_stf", value_shape=(), batch_shape=()>
        >>> result = bo.execute_graph(graph=graph, output_node_names="hann")
        >>> result["output"]["hann"]
        {'durations': array([0.2, 0.2, 0.2, 0.2, 0.2]),
        'values': array([0.5568644 , 1.25563559, 0.75      , 1.25563569, 0.55686415]),
        'time_dimension': 0}

        Define a sampleable Hann series with optimizable coefficients.

        >>> coefficients = graph.optimization_variable(
        ...     count=8, lower_bound=-3.5e6, upper_bound=3.5e6, name="coefficients"
        ... )
        >>> graph.signals.hann_series_stf(coefficients=coefficients, end_time=2.0e-6)
        <Stf: operation_name="stf_sum", value_shape=(), batch_shape=()>
        """

        Checker.VALUE(
            end_time > start_time,
            "The end time must be greater than the start time.",
            {"start_time": start_time, "end_time": end_time},
        )

        # Define scaled times π (t - t_start) / (t_end - t_start).
        scaled_time = (self._graph.identity_stf() - start_time) * (
            np.pi / (end_time - start_time)
        )

        # Calculate function values.
        stfs = [
            coefficients[idx] * self._graph.sin((idx + 1) * scaled_time) ** 2
            for idx in range(coefficients.shape[0])
        ]
        return self._graph.stf_sum(stfs)

    @validated
    def linear_ramp_stf(
        self,
        slope: Annotated[Union[float, complex, Tensor], pipe(scalar)],
        shift: Annotated[Union[float, complex, Tensor], pipe(scalar)] = 0.0,
    ) -> Stf:
        r"""
        Create an `Stf` representing a linear ramp.

        Parameters
        ----------
        slope : float or complex or Tensor
            The slope of the ramp, :math:`a`.
            It must either be a scalar or contain a single element.
        shift : float or complex or Tensor, optional
            The value of the ramp at :math:`t = 0`, :math:`b`.
            It must either be a scalar or contain a single element.
            Defaults to 0.

        Returns
        -------
        Stf
            The sampleable linear ramp.

        See Also
        --------
        :func:`boulderopal.signals.linear_ramp`
            Create a `Signal` object representing a linear ramp.
        :func:`Graph.signals.linear_ramp_pwc <signals.linear_ramp_pwc>`
            Corresponding operation with `Pwc` output.
        :func:`Graph.signals.tanh_ramp_stf <signals.tanh_ramp_stf>`
            Create an `Stf` representing a hyperbolic tangent ramp.

        Notes
        -----
        The linear ramp is defined as

        .. math:: \mathop{\mathrm{Linear}}(t) = a t + b .

        Examples
        --------
        Define a linear STF ramp.

        >>> linear = graph.signals.linear_ramp_stf(slope=4.0, shift=-2.0)
        >>> graph.discretize_stf(linear, duration=1, segment_count=5, name="linear")
        <Pwc: name="linear", operation_name="discretize_stf", value_shape=(), batch_shape=()>
        >>> result = bo.execute_graph(graph=graph, output_node_names="linear")
        >>> result["output"]["linear"]
        {'durations': array([0.2, 0.2, 0.2, 0.2, 0.2]),
        'values': array([-1.6, -0.8,  0. ,  0.8,  1.6]),
        'time_dimension': 0}

        Define a linear STF ramp with an optimizable slope and root.

        >>> slope = graph.optimizable_scalar(
        ...     lower_bound=-4, upper_bound=4, name="slope"
        ... )
        >>> root = graph.optimizable_scalar(
        ...     lower_bound=-4, upper_bound=4, name="slope"
        ... )
        >>> shift = - slope * root
        >>> graph.signals.linear_ramp_stf(slope=slope, shift=shift)
        <Stf: operation_name="add", value_shape=(), batch_shape=()>
        """
        return slope * self._graph.identity_stf() + shift

    @validated
    def tanh_ramp_stf(
        self,
        center_time: Annotated[Union[float, Tensor], pipe(scalar)],
        ramp_duration: Annotated[Union[float, Tensor], pipe(positive_scalar)],
        end_value: Annotated[Union[float, complex, Tensor], pipe(scalar)],
        start_value: Optional[
            Annotated[Union[float, complex, Tensor], pipe(scalar)]
        ] = None,
    ) -> Stf:
        r"""
        Create an `Stf` representing a hyperbolic tangent ramp.

        Parameters
        ----------
        center_time : float or Tensor
            The time at which the ramp has its greatest slope, :math:`t_0`.
            It must either be a scalar or contain a single element.
        ramp_duration : float or Tensor
            The characteristic time for the hyperbolic tangent ramp, :math:`t_\mathrm{ramp}`.
            It must either be a scalar or contain a single element.
        end_value : float or complex or Tensor
            The asymptotic value of the ramp towards :math:`t \to +\infty`, :math:`a_+`.
            It must either be a scalar or contain a single element.
        start_value : float or complex or Tensor, optional
            The asymptotic value of the ramp towards :math:`t \to -\infty`, :math:`a_-`.
            If passed, it must either be a scalar or contain a single element.
            Defaults to minus `end_value`.

        Returns
        -------
        Stf
            The sampleable hyperbolic tangent ramp.

        See Also
        --------
        :func:`Graph.signals.linear_ramp_stf <signals.linear_ramp_stf>`
            Create an `Stf` representing a linear ramp.
        :func:`boulderopal.signals.tanh_ramp`
            Create a `Signal` object representing a hyperbolic tangent ramp.
        :func:`Graph.signals.tanh_ramp_pwc <signals.tanh_ramp_pwc>`
            Corresponding operation with `Pwc` output.
        :func:`Graph.tanh`
            Calculate the element-wise hyperbolic tangent of an object.

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

        With the default value of `start_value` (:math:`a_-`),
        the ramp expression simplifies to

        .. math:: \mathop{\mathrm{Tanh}}(t)
            = A \tanh\left( \frac{t - t_0}{t_\mathrm{ramp}} \right) ,

        where :math:`A = a_+` is the end value (the start value is then :math:`-A`).

        Examples
        --------
        Define a simple sampleable hyperbolic tangent ramp.

        >>> tanh = graph.signals.tanh_ramp_stf(
        ...     center_time=0.4, ramp_duration=0.2, end_value=2, start_value=-1
        ... )
        >>> graph.discretize_stf(tanh, duration=1, segment_count=5, name="tanh")
        <Pwc: name="tanh", operation_name="discretize_stf", value_shape=(), batch_shape=()>
        >>> result = bo.execute_graph(graph=graph, output_node_names="tanh")
        >>> result["output"]["tanh"]
        {'durations': array([0.2, 0.2, 0.2, 0.2, 0.2]),
        'values': array([-0.85772238, -0.19317574,  1.19317574,  1.85772238,  1.97992145]),
        'time_dimension': 0}

        Define a hyperbolic tangent ramp with optimizable parameters.

        >>> center_time = graph.optimizable_scalar(
        ...     lower_bound=0.25e-6, upper_bound=0.75e-6, name="center_time"
        ... )
        >>> ramp_duration = graph.optimizable_scalar(
        ...     lower_bound=0.1e-6, upper_bound=0.3e-6, name="ramp_duration"
        ... )
        >>> end_value = graph.optimizable_scalar(
        ...     lower_bound=0, upper_bound=3e6, name="end_value"
        ... )
        >>> graph.signals.tanh_ramp_stf(
        ...     center_time=center_time, ramp_duration=ramp_duration, end_value=end_value
        ... )
        <Stf: operation_name="add", value_shape=(), batch_shape=()>
        """

        if start_value is None:
            start_value = -end_value

        return start_value + 0.5 * (end_value - start_value) * (  # type: ignore
            1
            + self._graph.tanh(
                (self._graph.identity_stf() - center_time) / ramp_duration
            )
        )
