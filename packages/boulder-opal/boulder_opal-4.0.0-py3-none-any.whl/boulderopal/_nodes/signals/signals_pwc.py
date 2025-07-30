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
    TYPE_CHECKING,
    Any,
    Optional,
    Union,
)

import numpy as np

from boulderopal._nodes.node_data import (
    Pwc,
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
    validate_enum,
    validated,
)

if TYPE_CHECKING:
    from boulderopal._nodes.node_data import Stf
    from boulderopal.graph._graph import Graph


class SegmentationType(str, Enum):
    """
    An enumeration of segmentation types for piecewise-constant signals.

    You can use this Enum to specify the segmentation type for graph nodes that
    define a PWC signal containing a constant part.

    Attributes
    ----------
    UNIFORM
        A uniform segmentation distributes the piecewise-constant segments
        uniformly along the signal's duration.
        This segmentation type is more efficient when combining different signals,
        as their segmentations will match.

    MINIMAL
        A minimal segmentation represents constant parts of the piecewise-constant
        function with a minimal number of segments (typically one or two),
        reserving most of the segments for the non-constant parts.
        This segmentation type might be preferred when only a single signal is present
        in the system, as it leads to a more efficient sampling of the non-constant parts.
        However, combining signals with different segmentations can lead to uneven sampling
        and increased computation time due to the increase in number of segments.
    """

    UNIFORM = "UNIFORM"
    MINIMAL = "MINIMAL"


def _get_sample_times(duration: float, segment_count: int) -> np.ndarray:
    """
    Returns an array of `segment_count` equally spaced times between 0 and `duration`.
    Each time is taken at the center of a segment with duration ``dt = duration / segment_count``,
    that is, ``[dt/2, dt + dt/2, 2dt + dt/2, ..., duration - dt/2]``.
    """
    times, time_step = np.linspace(
        0, duration, segment_count, endpoint=False, retstep=True
    )
    times += time_step / 2
    return times


class PwcSignals:
    """
    Base class implementing Pwc signal graph methods.
    """

    def __init__(self, graph: "Graph") -> None:
        self._graph = graph

    @validated
    def square_pulse_pwc(
        self,
        duration: Annotated[float, pipe(ScalarT.REAL().gt(0))],
        segment_count: Annotated[int, pipe(ScalarT.INT().ge(1))],
        amplitude: Annotated[Union[float, complex, Tensor], pipe(scalar)],
        start_time: float = 0,
        end_time: Optional[Annotated[float, pipe(ScalarT.REAL())]] = None,
        segmentation: SegmentationType = SegmentationType.UNIFORM,
        *,
        name: Optional[str] = None,
    ) -> Pwc:
        r"""
        Create a `Pwc` representing a square pulse.

        The entire signal lasts from time 0 to the given duration with the
        square pulse being applied from the start time to the end time.

        Parameters
        ----------
        duration : float
            The duration of the signal.
        segment_count : int
            The number of segments in the PWC.
            Only used if the segmentation type is "UNIFORM" .
        amplitude : float or complex or Tensor
            The amplitude of the square pulse, :math:`A`.
            It must either be a scalar or contain a single element.
        start_time : float, optional
            The start time of the square pulse, :math:`t_\mathrm{start}`.
            Defaults to 0.
        end_time : float or None, optional
            The end time of the square pulse, :math:`t_\mathrm{end}`.
            Must be greater than the start time.
            Defaults to the value of the given duration.
        segmentation : :class:`~signals.SegmentationType`
            The type of segmentation for the pulse.
            With a "MINIMAL" segmentation, the returned Pwc has
            between one and three segments, depending on the start time,
            end time, and duration of the signal.
            Defaults to "UNIFORM", in which case the segments are uniformly
            distributed along the signal's duration.
        name : str or None, optional
            The name of the node.

        Returns
        -------
        Pwc
            The square pulse.

        See Also
        --------
        :func:`Graph.signals.cosine_pulse_pwc <signals.cosine_pulse_pwc>`
            Create a `Pwc` representing a cosine pulse.
        :func:`Graph.signals.gaussian_pulse_pwc <signals.gaussian_pulse_pwc>`
            Create a `Pwc` representing a Gaussian pulse.
        :func:`Graph.signals.sech_pulse_pwc <signals.sech_pulse_pwc>`
            Create a `Pwc` representing a hyperbolic secant pulse.
        :func:`boulderopal.signals.square_pulse`
            Create a `Signal` object representing a square pulse.

        Notes
        -----
        The square pulse is defined as

        .. math:: \mathop{\mathrm{Square}}(t)
            = A \theta(t-t_\mathrm{start}) \theta(t_\mathrm{end}-t) ,

        where :math:`\theta(t)` is the
        `Heaviside step function <https://en.wikipedia.org/wiki/Heaviside_step_function>`_.

        Examples
        --------
        Define a square pulse with an optimizable amplitude.

        >>> amplitude = graph.optimizable_scalar(
        ...     lower_bound=0, upper_bound=2.*np.pi, name="amplitude"
        ... )
        >>> graph.signals.square_pulse_pwc(
        ...     duration=4.0, amplitude=amplitude, segment_count=100, name="square"
        ... )
        <Pwc: name="square", operation_name="pwc_signal", value_shape=(), batch_shape=()>

        Define a square PWC pulse.

        >>> graph.signals.square_pulse_pwc(
        ...     duration=4.0,
        ...     segment_count=5,
        ...     amplitude=2.5,
        ...     start_time=1.0,
        ...     end_time=3.0,
        ...     name="square",
        ... )
        <Pwc: name="square", operation_name="pwc_signal", value_shape=(), batch_shape=()>
        >>> result = bo.execute_graph(graph=graph, output_node_names="square")
        >>> result["output"]["square"]
        {
            'durations': array([0.8, 0.8, 0.8, 0.8, 0.8]),
            'values': array([0. , 2.5, 2.5, 2.5, 0. ]),
            'time_dimension': 0
        }

        Define a square PWC pulse with a minimal segmentation.

        >>> graph.signals.square_pulse_pwc(
        ...     duration=4.0,
        ...     segment_count=None,
        ...     amplitude=2.5,
        ...     start_time=1.0,
        ...     end_time=3.0,
        ...     segmentation="MINIMAL",
        ...     name="square",
        ... )
        <Pwc: name="square", operation_name="time_concatenate_pwc", value_shape=(), batch_shape=()>
        >>> result = bo.execute_graph(graph=graph, output_node_names="square")
        >>> result["output"]["square"]
        {
            'durations': array([1., 2., 1.]),
            'values': array([0. , 2.5, 0. ]),
            'time_dimension': 0
        }
        """

        if end_time is None:
            end_time = duration
        else:
            Checker.VALUE(
                end_time > start_time,
                "The end time must be greater than the start time.",
                {"start_time": start_time, "end_time": end_time},
            )

        if validate_enum(SegmentationType, segmentation) == SegmentationType.UNIFORM:
            times = _get_sample_times(duration, segment_count)
            values = amplitude * np.where(
                np.logical_and(times > start_time, times < end_time), 1, 0
            )
            return self._graph.pwc_signal(values=values, duration=duration, name=name)

        if start_time >= duration or end_time <= 0:
            # In both of these cases the signal is always zero.
            return self._graph.constant_pwc(constant=0.0, duration=duration, name=name)

        pwcs = []

        if start_time > 0:
            # Add preceding step function.
            pwcs.append(self._graph.constant_pwc(constant=0.0, duration=start_time))

        pwcs.append(
            self._graph.constant_pwc(
                constant=amplitude,
                duration=min(end_time, duration) - max(start_time, 0),
            )
        )

        if end_time < duration:
            # Add trailing step function.
            pwcs.append(
                self._graph.constant_pwc(constant=0.0, duration=duration - end_time)
            )

        return self._graph.time_concatenate_pwc(pwcs, name=name)

    @validated
    def sech_pulse_pwc(
        self,
        duration: Annotated[float, pipe(ScalarT.REAL().gt(0))],
        segment_count: Annotated[int, pipe(ScalarT.INT().ge(1))],
        amplitude: Annotated[Union[float, complex, Tensor], pipe(scalar)],
        width: Optional[Annotated[Union[float, Tensor], pipe(positive_scalar)]] = None,
        center_time: Optional[Annotated[Union[float, Tensor], pipe(scalar)]] = None,
        *,
        name: Optional[str] = None,
    ) -> Pwc:
        r"""
        Create a `Pwc` representing a hyperbolic secant pulse.

        Parameters
        ----------
        duration : float
            The duration of the signal, :math:`T`.
        segment_count : int
            The number of segments in the PWC.
        amplitude : float or complex or Tensor
            The amplitude of the pulse, :math:`A`.
            It must either be a scalar or contain a single element.
        width : float or Tensor or None, optional
            The characteristic time for the hyperbolic secant pulse, :math:`t_\mathrm{pulse}`.
            If passed, it must either be a scalar or contain a single element.
            Defaults to :math:`T/12`,
            giving the pulse a full width at half maximum (FWHM) of :math:`0.22 T`.
        center_time : float or Tensor or None, optional
            The time at which the pulse peaks, :math:`t_\mathrm{peak}`.
            If passed, it must either be a scalar or contain a single element.
            Defaults to :math:`T/2`.
        name : str or None, optional
            The name of the node.

        Returns
        -------
        Pwc
            The sampled hyperbolic secant pulse.

        See Also
        --------
        :func:`Graph.signals.cosine_pulse_pwc <signals.cosine_pulse_pwc>`
            Create a `Pwc` representing a cosine pulse.
        :func:`Graph.signals.gaussian_pulse_pwc <signals.gaussian_pulse_pwc>`
            Create a `Pwc` representing a Gaussian pulse.
        :func:`boulderopal.signals.sech_pulse`
            Create a `Signal` object representing a hyperbolic secant pulse.
        :func:`Graph.signals.sech_pulse_stf <signals.sech_pulse_stf>`
            Corresponding operation with `Stf` output.
        :func:`Graph.signals.square_pulse_pwc <signals.square_pulse_pwc>`
            Create a `Pwc` representing a square pulse.

        Notes
        -----
        The hyperbolic secant pulse is defined as

        .. math:: \mathop{\mathrm{Sech}}(t)
            = \frac{A}{\cosh\left((t - t_\mathrm{peak}) / t_\mathrm{pulse} \right)} .

        The FWHM of the pulse is about :math:`2.634 t_\mathrm{pulse}`.

        Examples
        --------
        Define a simple sech PWC pulse.

        >>> graph.signals.sech_pulse_pwc(
        ...     duration=5, segment_count=50, amplitude=1, name="sech"
        ... )
        <Pwc: name="sech", operation_name="discretize_stf", value_shape=(), batch_shape=()>
        >>> result = bo.execute_graph(graph=graph, output_node_names="sech")
        >>> result["output"]["sech"]
        {
            'durations': array([0.1, 0.1, ..., 0.1, 0.1]),
            'values': array([0.00558953, 0.00710565, ..., 0.00710565, 0.00558953]),
            'time_dimension': 0
        }

        Define a displaced sech PWC pulse.

        >>> graph.signals.sech_pulse_pwc(
        ...     duration=3e-6,
        ...     segment_count=60,
        ...     amplitude=20e6,
        ...     width=0.15e-6,
        ...     center_time=1e-6,
        ...     name="displaced",
        ... )
        <Pwc: name="displaced", operation_name="discretize_stf", value_shape=(), batch_shape=()>
        >>> result = bo.execute_graph(graph=graph, output_node_names="sech_displaced")
        >>> result["output"]["sech_displaced"]
        {
            'durations': array([5.e-08, 5.e-08, ..., 5.e-08, 5.e-08]),
            'values': array([6.01374318e+04, 8.39283672e+04, ..., 1.06810547e+02, 7.65331014e+01]),
            'time_dimension': 0
        }

        Define a sech pulse with optimizable parameters.

        >>> amplitude = graph.optimizable_scalar(
        ...     lower_bound=0, upper_bound=10e6, name="amplitude"
        ... )
        >>> width = graph.optimizable_scalar(
        ...     lower_bound=0.1e-6, upper_bound=0.5e-6, name="width"
        ... )
        >>> center_time = graph.optimizable_scalar(
        ...     lower_bound=1e-6, upper_bound=2e-6, name="center_time"
        ... )
        >>> graph.signals.sech_pulse_pwc(
        ...     duration=3e-6,
        ...     segment_count=32,
        ...     amplitude=amplitude,
        ...     width=width,
        ...     center_time=center_time,
        ...     name="sech_pulse",
        ... )
        <Pwc: name="sech_pulse", operation_name="discretize_stf", value_shape=(), batch_shape=()>
        """
        if width is None:
            width = duration / 12

        if center_time is None:
            center_time = duration / 2

        stf = amplitude / self._graph.cosh(
            (self._graph.identity_stf() - center_time) / width
        )
        return self._graph.discretize_stf(stf, duration, segment_count, name=name)  # type: ignore

    @validated
    def linear_ramp_pwc(
        self,
        duration: Annotated[float, pipe(ScalarT.REAL().gt(0))],
        segment_count: Annotated[int, pipe(ScalarT.INT().ge(1))],
        end_value: Annotated[Union[float, complex, Tensor], pipe(scalar)],
        start_value: Optional[
            Annotated[Union[float, complex, Tensor], pipe(scalar)]
        ] = None,
        start_time: float = 0,
        end_time: Optional[float] = None,
        segmentation: SegmentationType = SegmentationType.UNIFORM,
        *,
        name: Optional[str] = None,
    ) -> Pwc:
        r"""
        Create a `Pwc` representing a linear ramp.

        Parameters
        ----------
        duration : float
            The duration of the signal, :math:`T`.
        segment_count : int
            The number of segments in the PWC.
        end_value : float or complex or Tensor
            The value of the ramp at :math:`t = t_\mathrm{end}`, :math:`a_\mathrm{end}`.
            It must either be a scalar or contain a single element.
        start_value : float or complex or Tensor or None, optional
            The value of the ramp at :math:`t = t_\mathrm{start}`, :math:`a_\mathrm{start}`.
            If passed, it must either be a scalar or contain a single element.
            Defaults to :math:`-a_\mathrm{end}`.
        start_time : float, optional
            The time at which the linear ramp starts, :math:`t_\mathrm{start}`.
            Defaults to 0.
        end_time : float or None, optional
            The time at which the linear ramp ends, :math:`t_\mathrm{end}`.
            Defaults to the given duration :math:`T`.
        segmentation : :class:`~signals.SegmentationType`
            The type of segmentation for the signal.
            With a "MINIMAL" segmentation, most of the segments are placed in the
            non-constant parts of the signal.
            Defaults to "UNIFORM", in which case the segments are uniformly
            distributed along the signal's duration.
        name : str or None, optional
            The name of the node.

        Returns
        -------
        Pwc
            The sampled linear ramp.

        See Also
        --------
        :func:`boulderopal.signals.linear_ramp`
            Create a `Signal` object representing a linear ramp.
        :func:`Graph.signals.linear_ramp_stf <signals.linear_ramp_stf>`
            Corresponding operation with `Stf` output.
        :func:`Graph.signals.tanh_ramp_pwc <signals.tanh_ramp_pwc>`
            Create a `Pwc` representing a hyperbolic tangent ramp.

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
        Define a linear PWC ramp.

        >>> graph.signals.linear_ramp_pwc(
        ...     duration=2.0, segment_count=5, end_value=1.5, start_value=0.5, name="linear_ramp"
        ... )
        <Pwc: name="linear_ramp", operation_name="pwc_signal", value_shape=(), batch_shape=()>
        >>> result = bo.execute_graph(graph=graph, output_node_names="linear_ramp")
        >>> result["output"]["linear_ramp"]
        {
            'durations': array([0.4, 0.4, 0.4, 0.4, 0.4]),
            'values': array([0.6, 0.8, 1. , 1.2, 1.4]),
            'time_dimension': 0
        }

        Define a linear ramp with start and end times.

        >>> graph.signals.linear_ramp_pwc(
        ...     duration=4,
        ...     segment_count=8,
        ...     end_value=2,
        ...     start_time=1,
        ...     end_time=3,
        ...     name="linear",
        ... )
        <Pwc: name="linear", operation_name="pwc_signal", value_shape=(), batch_shape=()>
        >>> result = bo.execute_graph(graph=graph, output_node_names="linear")
        >>> result["output"]["linear"]
        {
            'durations': array([0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5]),
            'values': array([-2. , -2. , -1.5, -0.5,  0.5,  1.5,  2. ,  2. ]),
            'time_dimension': 0
        }

        Define a linear ramp with minimal segmentation.

        >>> graph.signals.linear_ramp_pwc(
        ...     duration=4,
        ...     segment_count=6,
        ...     end_value=2,
        ...     start_time=1,
        ...     end_time=3,
        ...     segmentation="MINIMAL",
        ...     name="linear",
        ... )
        <Pwc: name="linear", operation_name="time_concatenate_pwc", value_shape=(), batch_shape=()>
        >>> result = bo.execute_graph(graph=graph, output_node_names="linear")
        >>> result["output"]["linear"]
        {
            'durations': array([1. , 0.5, 0.5, 0.5, 0.5, 1. ]),
            'values': array([-2. , -1.5, -0.5,  0.5,  1.5,  2. ]),
            'time_dimension': 0
        }

        Define a linear ramp with an optimizable slope around 0.

        >>> duration = 4.0
        >>> slope = graph.optimizable_scalar(
        ...     lower_bound=-30, upper_bound=30, name="slope"
        ... )
        >>> end_value = slope * duration / 2
        >>> graph.signals.linear_ramp_pwc(
        ...     duration=duration, segment_count=64, end_value=end_value, name="linear_ramp"
        ... )
        <Pwc: name="linear_ramp", operation_name="pwc_signal", value_shape=(), batch_shape=()>
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

        if validate_enum(SegmentationType, segmentation) == SegmentationType.UNIFORM:
            times = _get_sample_times(duration, segment_count)
            values = np.clip((times - start_time) / (end_time - start_time), 0, 1)
            values = (end_value - start_value) * values + start_value
            return self._graph.pwc_signal(values=values, duration=duration, name=name)

        slope = (end_value - start_value) / (end_time - start_time)

        if start_time <= 0.0 and end_time >= duration:
            # No flat parts inside of the PWC.
            stf = start_value + slope * (self._graph.identity_stf() - start_time)
            return self._graph.discretize_stf(stf, duration, segment_count, name=name)

        if end_time <= 0.0 or start_time >= duration:
            # The whole ramp falls outside of the PWC.
            return self._graph.discretize_stf(
                self._graph.constant_stf(0.0), duration, segment_count, name=name
            )

        pre_step_pwc = None
        post_step_pwc = None

        if start_time > 0.0:
            # Preceding step function.
            pre_step_pwc = self._graph.constant_pwc(
                constant=start_value, duration=start_time
            )
            segment_count -= 1

        if end_time < duration:
            # Trailing step function.
            post_step_pwc = self._graph.constant_pwc(
                constant=end_value, duration=duration - end_time
            )
            segment_count -= 1

        # Ramp part.
        stf = start_value + slope * (self._graph.identity_stf() - min(start_time, 0.0))
        ramp_duration = min(end_time, duration) - max(start_time, 0.0)
        ramp_pwc = self._graph.discretize_stf(stf, ramp_duration, segment_count)

        pwcs = [ramp_pwc]
        if pre_step_pwc is not None:
            pwcs.insert(0, pre_step_pwc)
        if post_step_pwc is not None:
            pwcs.append(post_step_pwc)

        return self._graph.time_concatenate_pwc(pwcs, name=name)

    @validated
    def tanh_ramp_pwc(
        self,
        duration: Annotated[float, pipe(ScalarT.REAL().gt(0))],
        segment_count: Annotated[int, pipe(ScalarT.INT().ge(1))],
        end_value: Annotated[Union[float, complex, Tensor], pipe(scalar)],
        start_value: Optional[
            Annotated[Union[float, complex, Tensor], pipe(scalar)]
        ] = None,
        ramp_duration: Optional[
            Annotated[Union[float, Tensor], pipe(positive_scalar)]
        ] = None,
        center_time: Optional[Annotated[Union[float, Tensor], pipe(scalar)]] = None,
        *,
        name: Optional[str] = None,
    ) -> Pwc:
        r"""
        Create a `Pwc` representing a hyperbolic tangent ramp.

        Parameters
        ----------
        duration : float
            The duration of the signal, :math:`T`.
        segment_count : int
            The number of segments in the PWC.
        end_value : float or complex or Tensor
            The asymptotic value of the ramp towards :math:`t \to +\infty`, :math:`a_+`.
            It must either be a scalar or contain a single element.
        start_value : float or complex or Tensor or None, optional
            The asymptotic value of the ramp towards :math:`t \to -\infty`, :math:`a_-`.
            If passed, it must either be a scalar or contain a single element.
            Defaults to minus `end_value`.
        ramp_duration : float or Tensor or None, optional
            The characteristic time for the hyperbolic tangent ramp, :math:`t_\mathrm{ramp}`.
            If passed, it must either be a scalar or contain a single element.
            Defaults to :math:`T/6`.
        center_time : float or Tensor or None, optional
            The time at which the ramp has its greatest slope, :math:`t_0`.
            If passed, it must either be a scalar or contain a single element.
            Defaults to :math:`T/2`.
        name : str or None, optional
            The name of the node.

        Returns
        -------
        Pwc
            The sampled hyperbolic tangent ramp.

        See Also
        --------
        :func:`Graph.signals.linear_ramp_pwc <signals.linear_ramp_pwc>`
            Create a `Pwc` representing a linear ramp.
        :func:`boulderopal.signals.tanh_ramp`
            Create a `Signal` object representing a hyperbolic tangent ramp.
        :func:`Graph.signals.tanh_ramp_stf <signals.tanh_ramp_stf>`
            Corresponding operation with `Stf` output.
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

        Note that if :math:`t_0` is close to the edges of the PWC,
        for example :math:`t_0 \lesssim 2 t_\mathrm{ramp}`,
        then the first and last values of the PWC will differ from the expected asymptotic values.

        With the default values of `start_value` (:math:`a_-`),
        `ramp_duration` (:math:`t_\mathrm{ramp}`), and `center_time` (:math:`t_0`),
        the ramp expression simplifies to

        .. math:: \mathop{\mathrm{Tanh}}(t) = A \tanh\left( \frac{t - T/2}{T/6} \right),

        where :math:`A = a_+` is the end value (the start value is then :math:`-A`).
        This defines a symmetric ramp (around :math:`(T/2, 0)`)
        between :math:`-0.995 A` (at :math:`t=0`) and :math:`0.995 A` (at :math:`t=T`).

        Examples
        --------
        Define a simple tanh PWC ramp.

        >>> graph.signals.tanh_ramp_pwc(
        ...     duration=5.0, segment_count=50, end_value=1, name="tanh_ramp"
        ... )
        <Pwc: name="tanh_ramp", operation_name="discretize_stf", value_shape=(), batch_shape=()>
        >>> result = bo.execute_graph(graph=graph, output_node_names="tanh_ramp")
        >>> result["output"]["tanh_ramp"]
        {
            'durations': array([0.1, 0.1, ..., 0.1, 0.1]),
            'values': array([-0.99442601, -0.99291942, ..., 0.99291942,  0.99442601]),
            'time_dimension': 0
        }

        Define a flat-top pulse from two hyperbolic tangent ramps.

        >>> ramp = graph.signals.tanh_ramp_pwc(
        ...     duration=3,
        ...     segment_count=60,
        ...     end_value=1,
        ...     ramp_duration=0.25,
        ...     center_time=0.5,
        ... )
        >>> flat_top_pulse = 0.5 * (ramp + graph.time_reverse_pwc(ramp))
        >>> flat_top_pulse.name="flat_top_pulse"
        >>> result = bo.execute_graph(graph=graph, output_node_names="flat_top_pulse")
        >>> result["output"]["flat_top_pulse"]
        {
            'durations': array([0.05, 0.05, ..., 0.05, 0.05]),
            'values': array([0.02188127, 0.03229546, ..., 0.03229546, 0.02188127]),
            'time_dimension': 0
        }

        Define a hyperbolic tangent ramp with optimizable parameters.

        >>> end_value = graph.optimizable_scalar(
        ...     lower_bound=0, upper_bound=3e6, name="end_value"
        ... )
        >>> ramp_duration = graph.optimizable_scalar(
        ...     lower_bound=0.1e-6, upper_bound=0.3e-6, name="ramp_duration"
        ... )
        >>> center_time = graph.optimizable_scalar(
        ...     lower_bound=0.25e-6, upper_bound=0.75e-6, name="center_time"
        ... )
        >>> graph.signals.tanh_ramp_pwc(
        ...     duration=1e-6,
        ...     segment_count=32,
        ...     end_value=end_value,
        ...     start_value=0.0,
        ...     ramp_duration=ramp_duration,
        ...     center_time=center_time,
        ...     name="tanh_ramp",
        ... )
        <Pwc: name="tanh_ramp", operation_name="discretize_stf", value_shape=(), batch_shape=()>
        """

        if start_value is None:
            start_value = -end_value

        if ramp_duration is None:
            ramp_duration = duration / 6

        if center_time is None:
            center_time = duration / 2

        stf = start_value + 0.5 * (end_value - start_value) * (
            1
            + self._graph.tanh(
                (self._graph.identity_stf() - center_time) / ramp_duration
            )
        )
        return self._graph.discretize_stf(stf, duration, segment_count, name=name)  # type: ignore

    @validated
    def gaussian_pulse_pwc(
        self,
        duration: Annotated[float, pipe(ScalarT.REAL().gt(0))],
        segment_count: Annotated[int, pipe(ScalarT.INT().ge(4))],
        amplitude: Annotated[Union[float, complex, Tensor], pipe(scalar)],
        width: Optional[Annotated[Union[float, Tensor], pipe(positive_scalar)]] = None,
        center_time: Optional[float] = None,
        drag: Optional[Annotated[Union[float, Tensor], pipe(scalar)]] = None,
        flat_duration: Optional[Annotated[float, pipe(ScalarT.REAL().gt(0))]] = None,
        segmentation: SegmentationType = SegmentationType.UNIFORM,
        *,
        name: Optional[str] = None,
    ) -> Pwc:
        r"""
        Create a `Pwc` representing a Gaussian pulse.

        Parameters
        ----------
        duration : float
            The duration of the signal, :math:`T`.
        segment_count : int
            The number of segments in the PWC.
            Must be at least four.
        amplitude : float or complex or Tensor
            The amplitude of the Gaussian pulse, :math:`A`.
            It must either be a scalar or contain a single element.
        width : float or Tensor or None, optional
            The standard deviation of the Gaussian pulse, :math:`\sigma`.
            It must either be a scalar or contain a single element.
            Defaults to :math:`T/10` or :math:`(T-t_\mathrm{flat})/10` if `flat_duration` is passed.
        center_time : float or None, optional
            The center of the Gaussian pulse, :math:`t_0`.
            Defaults to half of the given value of the duration, :math:`T/2`.
        drag : float or Tensor or None, optional
            The DRAG parameter, :math:`\beta`.
            If passed, it must either be a scalar or contain a single element.
            Defaults to no DRAG correction.
        flat_duration : float or None, optional
            The amount of time to remain constant after the peak of the Gaussian,
            :math:`t_\mathrm{flat}`.
            If passed, it must be positive and less than the duration.
            Defaults to None, in which case no constant part is added to the Gaussian pulse.
        segmentation : :class:`~signals.SegmentationType`
            The type of segmentation for the signal.
            With a "MINIMAL" segmentation, most of the segments are placed in the
            non-constant parts of the signal.
            Defaults to "UNIFORM", in which case the segments are uniformly
            distributed along the signal's duration.
        name : str or None, optional
            The name of the node.

        Returns
        -------
        Pwc
            The sampled Gaussian pulse.
            If no flat duration is passed then the pulse is evenly sampled between :math:`0` and
            :math:`T`. If one is passed, the flat part of the pulse is described by one or two
            segments (depending on the values of `center_time` and `segment_count`), and the
            rest of the pulse is sampled with the remaining segments.

        See Also
        --------
        :func:`Graph.signals.cosine_pulse_pwc <signals.cosine_pulse_pwc>`
            Create a `Pwc` representing a cosine pulse.
        :func:`Graph.signals.gaussian_pulse_stf <signals.gaussian_pulse_stf>`
            Corresponding operation with `Stf` output.
        :func:`Graph.signals.sech_pulse_pwc <signals.sech_pulse_pwc>`
            Create a `Pwc` representing a hyperbolic secant pulse.
        :func:`Graph.signals.square_pulse_pwc <signals.square_pulse_pwc>`
            Create a `Pwc` representing a square pulse.

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
        Define a Gaussian PWC pulse.

        >>> graph.signals.gaussian_pulse_pwc(
        ...     duration=3.0,
        ...     segment_count=100,
        ...     amplitude=1.0,
        ...     name="gaussian",
        ... )
        <Pwc: name="gaussian", operation_name="discretize_stf", value_shape=(), batch_shape=()>
        >>> result = bo.execute_graph(graph=graph, output_node_names="gaussian")
        >>> result["output"]["gaussian"]
        {
            'durations': array([0.03, 0.03, ..., 0.03, 0.03]),
            'values': array([4.77913973e-06, 7.80106730e-06, ..., 7.80106730e-06, 4.77913973e-06]),
            'time_dimension': 0
        }

        Define a flat-top Gaussian PWC pulse with a DRAG correction with minimal segmentation.

        >>> graph.signals.gaussian_pulse_pwc(
        ...     duration=3.0,
        ...     segment_count=100,
        ...     amplitude=1.0,
        ...     width=0.2,
        ...     center_time=1.5,
        ...     drag=0.1,
        ...     flat_duration=0.2,
        ...     segmentation="MINIMAL",
        ...     name="drag",
        ... )
        <Pwc: name="drag", operation_name="time_concatenate_pwc", value_shape=(), batch_shape=()>
        >>> result = bo.execute_graph(graph=graph, output_node_names="gaussian_drag")
        >>> result["output"]["gaussian_drag"]
        {
            'durations': array([0.02857143, 0.02857143, ..., 0.02857143, 0.02857143]),
            'values': array([3.76551948e-11+1.30448351e-10j, 1.00289674e-10+3.40268532e-10j, ...,
                             1.00289593e-10-3.40268262e-10j, 3.76551637e-11-1.30448246e-10j]),
            'time_dimension': 0
        }

        Define a Gaussian pulse with optimizable parameters.

        >>> amplitude = graph.optimizable_scalar(
        ...     lower_bound=0, upper_bound=2.*np.pi, name="amplitude"
        ... )
        >>> width = graph.optimizable_scalar(
        ...     lower_bound=0.1, upper_bound=2., name="width"
        ... )
        >>> drag = graph.optimizable_scalar(
        ...     lower_bound=0, upper_bound=1., name="drag"
        ... )
        >>> graph.signals.gaussian_pulse_pwc(
        ...     duration=3.0,
        ...     segment_count=100,
        ...     amplitude=amplitude,
        ...     width=width,
        ...     drag=drag,
        ...     name="gaussian",
        ... )
        <Pwc: name="gaussian", operation_name="discretize_stf", value_shape=(), batch_shape=()>
        """

        if center_time is None:
            center_time = 0.5 * duration

        if width is None:
            if flat_duration is None:
                width = duration / 10
            else:
                width = (duration - flat_duration) / 10

        def create_gaussian(center_parameter: float) -> Stf:
            assert width is not None
            shifted_time = self._graph.identity_stf() - center_parameter
            gaussian = amplitude * self._graph.exp(-(shifted_time**2) / (2 * width**2))
            if drag is None:
                return gaussian  # type: ignore
            return gaussian * (1.0 - 1j * drag * shifted_time / (width**2))

        if flat_duration is None:
            return self._graph.discretize_stf(
                create_gaussian(center_time), duration, segment_count, name=name
            )

        Checker.VALUE(
            flat_duration < duration,
            "The flat duration must be less than the duration.",
            {"flat_duration": flat_duration, "duration": duration},
        )

        # Time at which first Gaussian ends.
        flat_segment_start = center_time - 0.5 * flat_duration
        # Time at which second Gaussian starts.
        flat_segment_end = center_time + 0.5 * flat_duration

        if validate_enum(SegmentationType, segmentation) == SegmentationType.UNIFORM:
            times = _get_sample_times(duration, segment_count)

            left_ramp_times = times[np.where(times < flat_segment_start)]
            values: list[Any] = []
            if len(left_ramp_times) > 0:
                values.append(
                    self._graph.sample_stf(
                        create_gaussian(flat_segment_start), left_ramp_times
                    )
                )

            flat_times_count = np.sum(
                np.logical_and(times >= flat_segment_start, times <= flat_segment_end)
            )
            if flat_times_count > 0:
                values.append(amplitude * np.ones(flat_times_count))

            right_ramp_times = times[np.where(times > flat_segment_end)]
            if len(right_ramp_times) > 0:
                values.append(
                    self._graph.sample_stf(
                        create_gaussian(flat_segment_end), right_ramp_times
                    )
                )

            return self._graph.pwc_signal(
                values=self._graph.concatenate(values, axis=0),
                duration=duration,
                name=name,
            )

        if flat_segment_start >= duration:
            # In this case since the flat segment starts after the duration, it is not part of
            # the signal.
            return self._graph.discretize_stf(
                create_gaussian(flat_segment_end), duration, segment_count, name=name
            )

        if flat_segment_end <= 0:
            # In this case since the flat segment finishes before time zero, it is not part of
            # the signal.
            return self._graph.discretize_stf(
                create_gaussian(flat_segment_end), duration, segment_count, name=name
            )

        if flat_segment_end >= duration:
            # In this case since the flat segment finishes after the duration, the second Gaussian
            # is not part of the signal.
            durations = [flat_segment_start, duration - flat_segment_start]
            segment_counts = [segment_count - 1, 1]
            stfs = [
                create_gaussian(flat_segment_start),
                self._graph.constant_stf(amplitude),
            ]

        elif flat_segment_start <= 0:
            # In this case since the flat segment begins before time zero, the first Gaussian
            # is not part of the signal.
            durations = [flat_segment_end, duration - flat_segment_end]
            segment_counts = [1, segment_count - 1]
            stfs = [self._graph.constant_stf(amplitude), create_gaussian(0.0)]

        else:
            durations = [flat_segment_start, flat_duration, duration - flat_segment_end]
            segment_counts = _allocate_segment_counts(durations, segment_count)
            stfs = [
                create_gaussian(flat_segment_start),
                self._graph.constant_stf(amplitude),
                create_gaussian(0.0),
            ]

        pwcs = [
            self._graph.discretize_stf(*args)
            for args in zip(stfs, durations, segment_counts)
        ]
        return self._graph.time_concatenate_pwc(pwcs, name=name)

    @validated
    def cosine_pulse_pwc(
        self,
        duration: Annotated[float, pipe(ScalarT.REAL().gt(0))],
        segment_count: Annotated[int, pipe(ScalarT.INT().gt(0))],
        amplitude: Annotated[Union[float, complex, Tensor], pipe(scalar)],
        drag: Optional[Annotated[Union[float, Tensor], pipe(scalar)]] = None,
        start_time: float = 0.0,
        end_time: Optional[float] = None,
        flat_duration: Optional[Annotated[float, pipe(ScalarT.REAL().gt(0))]] = None,
        segmentation: SegmentationType = SegmentationType.UNIFORM,
        *,
        name: Optional[str] = None,
    ) -> Pwc:
        r"""
        Create a `Pwc` representing a cosine pulse.

        Parameters
        ----------
        duration : float
            The duration of the signal, :math:`T`.
        segment_count : int
            The number of segments in the PWC.
            Must be at least six.
        amplitude : float or complex or Tensor
            The amplitude of the pulse, :math:`A`.
            It must either be a scalar or contain a single element.
        drag : float or Tensor or None, optional
            The DRAG parameter, :math:`\beta`.
            If passed, it must either be a scalar or contain a single element.
            Defaults to no DRAG correction.
        start_time : float, optional
            The time at which the cosine pulse starts, :math:`t_\mathrm{start}`.
            Defaults to 0.
        end_time : float or None, optional
            The time at which the cosine pulse ends, :math:`t_\mathrm{end}`.
            Defaults to the given duration :math:`T`.
        flat_duration : float or None, optional
            The amount of time to remain constant after the peak of the cosine,
            :math:`t_\mathrm{flat}`.
            If passed, it must be positive and less than the difference between `end_time` and
            `start_time`.
            Defaults to None, in which case no constant part is added to the cosine pulse.
        segmentation : :class:`~signals.SegmentationType`
            The type of segmentation for the signal.
            With a "MINIMAL" segmentation, most of the segments are placed in the
            non-constant parts of the signal.
            Defaults to "UNIFORM", in which case the segments are uniformly
            distributed along the signal's duration.
        name : str or None, optional
            The name of the node.

        Returns
        -------
        Pwc
            The sampled cosine pulse.
            If no flat duration is passed then the pulse is evenly sampled between :math:`0` and
            :math:`T`. If one is passed, the flat part of the pulse is described by one or two
            segments (depending on the value of `segment_count`), and the rest of the pulse is
            sampled with the remaining segments.

        See Also
        --------
        :func:`boulderopal.signals.cosine_pulse`
            Create a `Signal` object representing a cosine pulse.
        :func:`Graph.signals.gaussian_pulse_pwc <signals.gaussian_pulse_pwc>`
            Create a `Pwc` representing a Gaussian pulse.
        :func:`Graph.signals.hann_series_pwc <signals.hann_series_pwc>`
            Create a `Pwc` representing a sum of Hann window functions.
        :func:`Graph.signals.sech_pulse_pwc <signals.sech_pulse_pwc>`
            Create a `Pwc` representing a hyperbolic secant pulse.
        :func:`Graph.signals.sinusoid_pwc <signals.sinusoid_pwc>`
            Create a `Pwc` representing a sinusoidal oscillation.
        :func:`Graph.signals.square_pulse_pwc <signals.square_pulse_pwc>`
            Create a `Pwc` representing a square pulse.
        :func:`Graph.cos`
            Calculate the element-wise cosine of an object.

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
        Define a cosine PWC pulse.

        >>> graph.signals.cosine_pulse_pwc(
        ...     duration=3.0, segment_count=100, amplitude=1.0, name="cos_pulse"
        ... )
        <Pwc: name="cos_pulse", operation_name="pwc_signal", value_shape=(), batch_shape=()>
        >>> result = bo.execute_graph(graph=graph, output_node_names="cos_pulse")
        >>> result["output"]["cos_pulse"]
        {
            'durations': array([0.03, 0.03, ..., 0.03, 0.03]),
            'values': array([2.46719817e-04, 2.21901770e-03, ..., 2.21901770e-03, 2.46719817e-04]),
            'time_dimension': 0
        }

        Define a flat-top cosine PWC pulse with a DRAG correction.

        >>> graph.signals.cosine_pulse_pwc(
        ...     duration=3.0,
        ...     segment_count=100,
        ...     amplitude=1.0,
        ...     drag=0.1,
        ...     start_time=1.0,
        ...     end_time=2.0,
        ...     flat_duration=0.3,
        ...     segmentation="MINIMAL",
        ...     name="cos_flat",
        ... )
        <Pwc: name="cos_flat", operation_name="pwc_signal", value_shape=(), batch_shape=()>
        >>> result = bo.execute_graph(graph=graph, output_node_names="cos_flat")
        >>> result["output"]["cos_flat"]
        {
            'durations': array([1.        , 0.00729167, ..., 0.00729167, 1.        ]),
            'values': array([0.00000000e+00+0.j        , 2.67706262e-04-0.01468429j, ...,
                             2.67706262e-04+0.01468429j, 0.00000000e+00+0.j        ]),
            'time_dimension': 0
        }

        Define a cosine pulse with optimizable parameters.

        >>> amplitude = graph.optimizable_scalar(
        ...     lower_bound=0, upper_bound=2.*np.pi, name="amplitude"
        ... )
        >>> drag = graph.optimizable_scalar(
        ...     lower_bound=0, upper_bound=1., name="drag"
        ... )
        >>> graph.signals.cosine_pulse_pwc(
        ...     duration=3.0,
        ...     segment_count=100,
        ...     amplitude=amplitude,
        ...     drag=drag,
        ...     name="cos_pulse",
        ... )
        <Pwc: name="cos_pulse", operation_name="pwc_signal", value_shape=(), batch_shape=()>
        """

        if end_time is None:
            end_time = duration

        Checker.VALUE(
            start_time < end_time,
            "The end time must be greater than the start time.",
            {"end_time": end_time, "start_time": start_time},
        )

        if flat_duration is not None:
            Checker.VALUE(
                flat_duration < end_time - start_time,
                "The flat duration must be less than the end time minus the start time.",
                {
                    "flat_duration": flat_duration,
                    "end_time - start_time": end_time - start_time,
                },
            )

        if start_time >= duration or end_time <= 0:
            # In both of these cases the signal is always zero.
            return self._graph.pwc_signal(
                duration=duration, values=np.zeros(segment_count), name=name
            )

        if validate_enum(SegmentationType, segmentation) == SegmentationType.UNIFORM:
            if flat_duration is None:
                flat_duration = 0
            pulse_period = end_time - start_time - flat_duration
            angular_freq = 2 * np.pi / pulse_period
            pulse_center = 0.5 * (start_time + end_time)
            flat_part_start = pulse_center - flat_duration * 0.5
            flat_part_end = pulse_center + flat_duration * 0.5

            times = _get_sample_times(duration, segment_count)

            # Create array with the values of the argument of cos/sin in the pulse definition.
            phases = np.where(
                np.logical_and(times > flat_part_start, times < flat_part_end), 0, np.pi
            )
            left_ramp_mask = np.where(
                np.logical_and(times >= start_time, times <= flat_part_start)
            )
            phases[left_ramp_mask] = angular_freq * (
                times[left_ramp_mask] - flat_part_start
            )
            right_ramp_mask = np.where(
                np.logical_and(times >= flat_part_end, times <= end_time)
            )
            phases[right_ramp_mask] = angular_freq * (
                times[right_ramp_mask] - flat_part_end
            )

            # Calculate pulse values.
            pulse = 1 + np.cos(phases)
            if drag is not None:
                pulse = pulse + angular_freq * drag * 1j * np.sin(phases)

            return self._graph.pwc_signal(
                duration=duration, values=0.5 * amplitude * pulse, name=name
            )

        def create_pulse(
            peak_time: float, omega: float, duration_: float, segment_count_: int
        ) -> Pwc:
            # Creates a PWC with segment_count_ segments representing
            #   A/2 [ 1 + cos(ω (t-tp)) + i ω β sin(ω (t - tp)) ]
            # between 0 and duration_,
            # where A is the amplitude, ω is omega, tp is peak_time,
            # and β is the DRAG parameter.

            shifted_times = _get_sample_times(duration_, segment_count_) - peak_time
            pulse = 1 + np.cos(omega * shifted_times)
            if drag is not None:
                pulse = pulse + omega * drag * 1j * np.sin(omega * shifted_times)

            return self._graph.pwc_signal(
                duration=duration_, values=0.5 * amplitude * pulse
            )

        pwcs = []

        pulse_segment_count = (
            segment_count - (start_time > 0.0) - (end_time < duration)
        )  # The number of segments for the cosine pulse.

        if start_time > 0.0:
            # Add preceding step function.
            pwcs.append(
                self._graph.pwc_signal(duration=start_time, values=np.array([0.0]))
            )

        if flat_duration is None:
            pulse_period = end_time - start_time  # The period of the cosine pulse.
            angular_freq = 2 * np.pi / pulse_period
            # The peak is 0.5 * pulse_period after the
            # start of the pulse plus start_time if start_time < 0.
            pwcs.append(
                create_pulse(
                    0.5 * pulse_period + min(start_time, 0),
                    angular_freq,
                    min(duration, end_time) - max(start_time, 0),
                    pulse_segment_count,
                )
            )
        else:
            Checker.VALUE(
                segment_count > 5,
                "The number of segments must be at least 6.",
                {"segment_count": segment_count},
            )

            # The period of the cosine pulse.
            pulse_period = end_time - start_time - flat_duration
            angular_freq = 2 * np.pi / pulse_period
            pulse_center = 0.5 * (start_time + end_time)
            flat_segment_start = pulse_center - flat_duration * 0.5
            flat_segment_end = pulse_center + flat_duration * 0.5

            durations = np.array(
                [
                    min(flat_segment_start, duration) - max(start_time, 0),
                    min(flat_segment_end, duration) - max(flat_segment_start, 0),
                    min(end_time, duration) - max(flat_segment_end, 0),
                ]
            )
            durations = durations * (durations > 0.0)

            if flat_segment_start <= 0.0 and flat_segment_end >= duration:
                # In this case the flat segment is the entire signal.
                segment_counts = [0, pulse_segment_count, 0]
            else:
                segment_counts = _allocate_segment_counts(
                    durations, pulse_segment_count
                )

            if flat_segment_start > 0.0:
                pwcs.append(
                    create_pulse(
                        0.5 * pulse_period + min(start_time, 0),
                        angular_freq,
                        durations[0],
                        segment_counts[0],
                    )
                )

            if flat_segment_start < duration and flat_segment_end > 0.0:
                pwcs.append(
                    self._graph.discretize_stf(
                        self._graph.constant_stf(amplitude),
                        durations[1],
                        segment_counts[1],
                    )
                )

            if flat_segment_end < duration:
                # The peak is at the start of the pulse, unless flat_segment_end < 0 in
                # which case it's flat_segment_end.
                pwcs.append(
                    create_pulse(
                        min(flat_segment_end, 0),
                        angular_freq,
                        durations[2],
                        segment_counts[2],
                    )
                )

        if end_time < duration:
            # Add trailing step function.
            pwcs.append(
                self._graph.pwc_signal(
                    duration=duration - end_time, values=np.array([0.0])
                )
            )

        return self._graph.time_concatenate_pwc(pwcs, name=name)

    @validated
    def sinusoid_pwc(
        self,
        duration: Annotated[float, pipe(ScalarT.REAL().gt(0))],
        segment_count: Annotated[int, pipe(ScalarT.INT().gt(0))],
        amplitude: Annotated[Union[float, complex, Tensor], pipe(scalar)],
        angular_frequency: Annotated[Union[float, Tensor], pipe(scalar)],
        phase: Annotated[Union[float, Tensor], pipe(scalar)] = 0.0,
        *,
        name: Optional[str] = None,
    ) -> Pwc:
        r"""
        Create a `Pwc` representing a sinusoidal oscillation.

        Parameters
        ----------
        duration : float
            The duration of the signal, :math:`T`.
        segment_count : int
            The number of segments in the PWC.
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
        name : str or None, optional
            The name of the node.

        Returns
        -------
        Pwc
            The sampled sinusoid.

        See Also
        --------
        :func:`Graph.signals.cosine_pulse_pwc <signals.cosine_pulse_pwc>`
            Create a `Pwc` representing a cosine pulse.
        :func:`Graph.signals.hann_series_pwc <signals.hann_series_pwc>`
            Create a `Pwc` representing a sum of Hann window functions.
        :func:`boulderopal.signals.sinusoid`
            Create a `Signal` object representing a sinusoidal oscillation.
        :func:`Graph.signals.sinusoid_stf <signals.sinusoid_stf>`
            Corresponding operation with `Stf` output.
        :func:`Graph.sin`
            Calculate the element-wise sine of an object.

        Notes
        -----
        The sinusoid is defined as

        .. math:: \mathop{\mathrm{Sinusoid}}(t) = A \sin \left( \omega t + \phi \right) .

        Examples
        --------
        Define a PWC oscillation.

        >>> graph.signals.sinusoid_pwc(
        ...     duration=5.0,
        ...     segment_count=100,
        ...     amplitude=1.0,
        ...     angular_frequency=np.pi,
        ...     phase=np.pi/2.0,
        ...     name="oscillation"
        ... )
        <Pwc: name="oscillation", operation_name="discretize_stf", value_shape=(), batch_shape=()>
        >>> result = bo.execute_graph(graph=graph, output_node_names="oscillation")
        >>> result["output"]["oscillation"]
        {
            'durations': array([0.05, 0.05, ..., 0.05, 0.05]),
            'values': array([ 0.99691733,  0.97236992,  ..., -0.97236992, -0.99691733]),
            'time_dimension': 0
        }

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
        >>> graph.signals.sinusoid_pwc(
        ...     duration=3e-6,
        ...     segment_count=100,
        ...     amplitude=amplitude,
        ...     angular_frequency=angular_frequency,
        ...     phase=phase,
        ...     name="oscillation"
        ... )
        <Pwc: name="oscillation", operation_name="discretize_stf", value_shape=(), batch_shape=()>
        """

        stf = amplitude * self._graph.sin(
            angular_frequency * self._graph.identity_stf() + phase
        )
        return self._graph.discretize_stf(stf, duration, segment_count, name=name)  # type: ignore

    @validated
    def hann_series_pwc(
        self,
        duration: Annotated[float, pipe(ScalarT.REAL().gt(0))],
        segment_count: Annotated[int, pipe(ScalarT.INT().gt(0))],
        coefficients: Annotated[
            Union[np.ndarray, Tensor], pipe(shapeable, after=ShapeT.VECTOR().no_batch())
        ],
        *,
        name: Optional[str] = None,
    ) -> Pwc:
        r"""
        Create a `Pwc` representing a sum of Hann window functions.

        The piecewise-constant function is sampled from Hann functions that start and end at zero.

        Parameters
        ----------
        duration : float
            The duration of the signal, :math:`T`.
        segment_count : int
            The number of segments in the PWC.
        coefficients : np.ndarray or Tensor
            The coefficients for the different Hann window functions, :math:`c_n`.
            It must be a 1D array or Tensor and it can't contain more than `segment_count` elements.
        name : str or None, optional
            The name of the node.

        Returns
        -------
        Pwc
            The sampled Hann window functions series.

        See Also
        --------
        :func:`Graph.signals.cosine_pulse_pwc <signals.cosine_pulse_pwc>`
            Create a `Pwc` representing a cosine pulse.
        :func:`Graph.signals.sinusoid_pwc <signals.sinusoid_pwc>`
            Create a `Pwc` representing a sinusoidal oscillation.
        :func:`boulderopal.signals.hann_series`
            Create a `Signal` object representing a sum of Hann window functions.
        :func:`Graph.signals.hann_series_stf <signals.hann_series_stf>`
            Corresponding operation with `Stf` output.

        Notes
        -----
        The series is defined as

        .. math:: \mathop{\mathrm{Hann}}(t)
            = \sum_{n=1}^N c_n \sin^2 \left( \frac{\pi n t}{T} \right) ,

        where :math:`N` is the number of coefficients.

        Examples
        --------
        Define a simple Hann series.

        >>> graph.signals.hann_series_pwc(
        ...     duration=5.0,
        ...     segment_count=50,
        ...     coefficients=np.array([0.5, 1, 0.25]),
        ...     name="hann_series",
        ... )
        <Pwc: name="hann_series", operation_name="pwc_signal", value_shape=(), batch_shape=()>
        >>> result = bo.execute_graph(graph=graph, output_node_names="hann_series")
        >>> result["output"]["hann_series"]
        {
            'durations': array([0.1, 0.1, ..., 0.1, 0.1]),
            'values': array([0.00665006, 0.05899895, ..., 0.05899895, 0.00665006]),
            'time_dimension': 0
        }

        Define a Hann series with optimizable coefficients.

        >>> coefficients = graph.optimization_variable(
        ...     count=8, lower_bound=-3.5e6, upper_bound=3.5e6, name="coefficients"
        ... )
        >>> graph.signals.hann_series_pwc(
        ...     duration=2.0e-6,
        ...     segment_count=128,
        ...     coefficients=coefficients,
        ...     name="hann_series",
        ... )
        <Pwc: name="hann_series", operation_name="pwc_signal", value_shape=(), batch_shape=()>
        """

        Checker.VALUE(
            coefficients.shape[0] <= segment_count,
            "There can't be more coefficients than segments.",
            {"coefficients.shape": coefficients.shape, "segment_count": segment_count},
        )

        # Define scaled times π t / T to sample the function.
        scaled_times = _get_sample_times(duration, segment_count) * np.pi / duration

        # Calculate function values.
        nss = np.arange(1, coefficients.shape[0] + 1)
        values = self._graph.sum(
            coefficients * np.sin(nss * scaled_times[:, None]) ** 2, axis=1
        )

        return self._graph.pwc_signal(duration=duration, values=values, name=name)


def _allocate_segment_counts(durations: list | np.ndarray, segment_count: int) -> list:
    """
    Allocate the number of segments between two non-flat segments and one flat segment.
    The flat segment is assumed to lie in the middle of the other two.
    The number of segments each non-flat part has is in proportion to their duration of time.
    The non-flat durations are at indexes 0 and 2 of durations, durations[0] and durations[2].
    durations[1] can only be zero if one of durations[0] or durations[2] are also zero
    (e.g. [2,0,3] and [0,0,0] are not valid inputs).
    """
    # In the symmetric case (durations[0] = durations[2]), the flat part gets two segments
    # if segment_count is even and one otherwise.
    if np.isclose(durations[0], durations[2]):
        pulse_counts = [(segment_count - 1) // 2] * 2
        pulse_counts.insert(1, segment_count - 2 * pulse_counts[0])
        return pulse_counts

    flat_segments = int(durations[1] > 0.0)  # Number of flat segments.
    # Note that if flat_segments is 0, either durations[0] or durations[2] must be 0.
    if np.isclose(durations[0], 0.0):
        return [0, flat_segments, segment_count - flat_segments]
    if np.isclose(durations[2], 0.0):
        return [segment_count - flat_segments, flat_segments, 0]

    # In this case we know flat_segments=1 and all pulse_counts should be at least 1.
    non_flat_duration = durations[0] + durations[2]
    pulse_counts = [
        int((segment_count - 1) * durations[index] / non_flat_duration)
        for index in [0, 2]
    ]
    # Make sure the pulses each get at least one segment even if the duration is very small.
    pulse_counts = [max(pulse_count, 1) for pulse_count in pulse_counts]
    pulse_counts.insert(1, 1)

    # If there are too many or few segments, we update the largest segment count.
    pulse_counts[np.argmax(pulse_counts)] += segment_count - sum(pulse_counts)

    return pulse_counts
