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

from typing import (
    List,
    Optional,
    Union,
)

import numpy as np
from pydantic import Field

from boulderopal._nodes.base import create_operation
from boulderopal._nodes.node_data import (
    ConvolutionKernel,
    Pwc,
    Stf,
    Tensor,
)
from boulderopal._nodes.validation import (
    ArrayT,
    ShapeT,
    non_negative_scalar,
    positive_scalar,
    scalar_or_shapeable,
    shapeable,
    starts_with_zero,
)
from boulderopal._typing import Annotated
from boulderopal._validation import (
    Checker,
    ScalarT,
    pipe,
    validated,
)


class StfGraph:  # pylint: disable=unused-argument
    """
    Base class implementing Stf graph methods.
    """

    @validated
    def stf_operator(
        self,
        signal: Annotated[Stf, pipe(after=ShapeT.SIGNAL())],
        operator: Annotated[
            Union[np.ndarray, Tensor],
            pipe(shapeable, after=ShapeT.OPERATOR().no_batch()),
        ],
    ) -> Stf:
        r"""
        Create a constant operator multiplied by a sampleable signal.

        Parameters
        ----------
        signal : Stf
            A sampleable function representing the signal :math:`a(t)`
            or a batch of sampleable functions.
        operator : np.ndarray or Tensor
            The operator :math:`A`. It must have two equal dimensions.

        Returns
        -------
        Stf
            The sampleable operator :math:`a(t)A` (or batch of sampleable operators, if
            you provide a batch of signals).

        See Also
        --------
        Graph.constant_stf_operator : Create a constant `Stf` operator.
        Graph.pwc_operator : Corresponding operation for `Pwc`\s.
        Graph.stf_sum : Sum multiple `Stf`\s.

        Notes
        -----
        For more information on `Stf` nodes see the `Working with time-dependent functions in
        Boulder Opal <https://docs.q-ctrl.com/boulder-opal/topics/working-with-time-dependent-
        functions-in-boulder-opal>`_ topic.
        """

        operation = create_operation(self.stf_operator, locals())
        return Stf(
            operation, value_shape=operator.shape, batch_shape=signal.batch_shape
        )

    @validated
    def constant_stf_operator(
        self,
        operator: Annotated[
            Union[np.ndarray, Tensor], pipe(shapeable, after=ShapeT.OPERATOR())
        ],
    ) -> Stf:
        r"""
        Create a constant operator.

        Parameters
        ----------
        operator : np.ndarray or Tensor
            The operator :math:`A`, or a batch of operators. It must have at
            least two dimensions, and its last two dimensions must be equal.

        Returns
        -------
        Stf
            The operator :math:`t\mapsto A` (or batch of
            operators, if you provide a batch of operators).

        See Also
        --------
        Graph.constant_pwc_operator : Corresponding operation for `Pwc`\s.
        Graph.constant_stf : Create a batch of constant `Stf`\s.
        Graph.stf_operator : Create an `Stf` operator.

        Notes
        -----
        For more information on `Stf` nodes see the `Working with time-dependent functions in
        Boulder Opal <https://docs.q-ctrl.com/boulder-opal/topics/working-with-time-dependent-
        functions-in-boulder-opal>`_ topic.
        """
        operation = create_operation(self.constant_stf_operator, locals())
        return Stf(
            operation, value_shape=operator.shape[-2:], batch_shape=operator.shape[:-2]
        )

    @validated
    def constant_stf(
        self,
        constant: Annotated[
            Union[float, complex, np.ndarray, Tensor], pipe(scalar_or_shapeable)
        ],
        batch_dimension_count: Annotated[int, pipe(ScalarT.INT().ge(0))] = 0,
    ) -> Stf:
        r"""
        Create a constant sampleable tensor-valued function of time.

        Parameters
        ----------
        constant : number or np.ndarray or Tensor
            The constant value :math:`c` of the function.
            To create a batch of :math:`B_1 \times \ldots \times B_n` constant
            functions of shape :math:`D_1 \times \ldots \times D_m`, provide this `constant`
            parameter as an object of shape
            :math:`B_1\times\ldots\times B_n\times D_1\times\ldots\times D_m`.
        batch_dimension_count : int, optional
            The number of batch dimensions, :math:`n`, in `constant`.
            If provided, the first :math:`n` dimensions of `constant` are considered
            batch dimensions. Defaults to 0, which corresponds to no batch.

        Returns
        -------
        Stf
           An Stf representing the constant function :math:`f(t) = c` for all time
           :math:`t` (or a batch of functions, if you provide `batch_dimension_count`).

        See Also
        --------
        Graph.constant_pwc : Corresponding operation for `Pwc`\s.
        Graph.constant_stf_operator : Create a constant sampleable function from operators.
        Graph.identity_stf : Create an `Stf` representing the identity function.

        Notes
        -----
        For more information on `Stf` nodes see the `Working with time-dependent functions in
        Boulder Opal <https://docs.q-ctrl.com/boulder-opal/topics/working-with-time-dependent-
        functions-in-boulder-opal>`_ topic.
        """

        shape = getattr(constant, "shape", ())
        Checker.VALUE(
            len(shape) >= batch_dimension_count,
            "The number of batch dimensions must not be larger than the number "
            "of dimensions of the input constant.",
            {"constant shape": shape, "batch_dimension_count": batch_dimension_count},
        )
        return Stf(
            operation=create_operation(self.constant_stf, locals()),
            value_shape=shape[batch_dimension_count:],
            batch_shape=shape[:batch_dimension_count],
        )

    @validated
    def stf_sum(self, terms: Annotated[List[Stf], Field(min_length=1)]) -> Stf:
        r"""
        Create the sum of multiple sampleable functions.

        Parameters
        ----------
        terms : list[Stf]
            The individual sampleable function :math:`\{v_j(t)\}` to sum.

        Returns
        -------
        Stf
            The sampleable function of time :math:`\sum_j v_j(t)`. It has the same
            shape as each of the `terms` that you provide.

        See Also
        --------
        Graph.hermitian_part : Hermitian part of an `Stf` operator.
        Graph.pwc_sum : Corresponding operation for `Pwc`\s.
        Graph.stf_operator : Create an `Stf` operator.

        Notes
        -----
        For more information on `Stf` nodes see the `Working with time-dependent functions in
        Boulder Opal <https://docs.q-ctrl.com/boulder-opal/topics/working-with-time-dependent-
        functions-in-boulder-opal>`_ topic.
        """

        for attr in ["value_shape", "batch_shape"]:
            Checker.VALUE(
                len(set(getattr(term, attr) for term in terms)) == 1,
                f"All the terms must have the same {attr}.",
            )
        operation = create_operation(self.stf_sum, locals())
        return Stf(
            operation,
            value_shape=terms[0].value_shape,
            batch_shape=terms[0].batch_shape,
        )

    @validated
    def discretize_stf(
        self,
        stf: Stf,
        duration: Annotated[float, pipe(ScalarT.REAL().gt(0))],
        segment_count: Annotated[int, pipe(ScalarT.INT().gt(0))],
        sample_count_per_segment: Annotated[int, pipe(ScalarT.INT().gt(0))] = 1,
        *,
        name: Optional[str] = None,
    ) -> Pwc:
        r"""
        Create a piecewise-constant function by discretizing a sampleable function.

        Use this function to create a piecewise-constant approximation to a sampleable
        function (obtained, for example, by filtering an initial
        piecewise-constant function).

        Parameters
        ----------
        stf : Stf
            The sampleable function :math:`v(t)` to discretize. The values of the
            function can have any shape. You can also provide a batch of
            functions, in which case the discretization is applied to each
            element of the batch.
        duration : float
            The duration :math:`\tau` over which discretization should be
            performed. The resulting piecewise-constant function has this
            duration.
        segment_count : int
            The number of segments :math:`N` in the resulting piecewise-constant
            function.
        sample_count_per_segment : int, optional
            The number of samples :math:`M` of the sampleable function to take when
            calculating the value of each segment in the discretization. Defaults
            to 1.
        name : str or None, optional
            The name of the node.

        Returns
        -------
        Pwc
            The piecewise-constant function :math:`w(t)` obtained by discretizing
            the sampleable function (or batch of piecewise-constant functions, if
            you provided a batch of sampleable functions).

        See Also
        --------
        Graph.convolve_pwc : Create an `Stf` by convolving a `Pwc` with a kernel.
        Graph.filter_and_resample_pwc : Filter a `Pwc` with a sinc filter and resample it.
        Graph.identity_stf : Create an `Stf` representing the identity function.
        Graph.sample_stf : Sample an `Stf` at given times.

        Notes
        -----
        The resulting function :math:`w(t)` is piecewise-constant with :math:`N`
        segments, meaning it has segment values :math:`\{w_n\}` such that
        :math:`w(t)=w_n` for :math:`t_{n-1}\leq t\leq t_n`, where :math:`t_n= n \tau/N`.

        Each segment value :math:`w_n` is the average of samples of :math:`v(t)`
        at the midpoints of :math:`M` equally sized subsegments between
        :math:`t_{n-1}` and :math:`t_n`:

        .. math::
            w_n = \frac{1}{M}
            \sum_{m=1}^M v\left(t_{n-1} + \left(m-\tfrac{1}{2}\right) \frac{\tau}{MN} \right).

        For more information on `Stf` nodes see the `Working with time-dependent functions in
        Boulder Opal <https://docs.q-ctrl.com/boulder-opal/topics/working-with-time-dependent-
        functions-in-boulder-opal>`_ topic.

        Examples
        --------
        Create discretized Gaussian signal.

        >>> times = graph.identity_stf()
        >>> gaussian_signal = graph.exp(- (times - 5e-6) ** 2 / 2e-6 ** 2) / 2e-6
        >>> discretized_gamma_signal = graph.discretize_stf(
        ...     stf=gaussian_signal, duration=10e-6, segment_count=256, name="gamma"
        ... )
        >>> discretized_gamma_signal
        <Pwc: name="gamma", operation_name="discretize_stf", value_shape=(), batch_shape=()>

        Refer to the `How to create dephasing and amplitude robust single-qubit gates
        <https://docs.q-ctrl.com/boulder-opal/user-guides/how-to-create-dephasing-and-amplitude-
        robust-single-qubit-gates>`_ user guide to find the example in context.
        """

        durations = duration / segment_count * np.ones(segment_count)
        return Pwc(
            operation=create_operation(self.discretize_stf, locals()),
            durations=durations,
            value_shape=stf.value_shape,
            batch_shape=stf.batch_shape,
        )

    @validated
    def time_evolution_operators_stf(
        self,
        hamiltonian: Annotated[Stf, pipe(after=ShapeT.OPERATOR())],
        sample_times: Annotated[np.ndarray, pipe(ArrayT.REAL().ndim(1).ge(0).ascend())],
        evolution_times: Optional[
            Annotated[
                np.ndarray,
                pipe(ArrayT.REAL().ndim(1).ge(0).ascend(), after=starts_with_zero),
            ]
        ] = None,
        *,
        name: Optional[str] = None,
    ) -> Tensor:
        """
        Calculate the time-evolution operators for a system defined by an STF Hamiltonian by using a
        4th order Runge–Kutta method.

        Parameters
        ----------
        hamiltonian : Stf
            The control Hamiltonian, or batch of control Hamiltonians.
        sample_times : np.ndarray
            The N times at which you want to sample the unitaries. Must be ordered and contain
            at least one element. If you don't provide `evolution_times`, `sample_times` must
            start with 0.
        evolution_times : np.ndarray or None, optional
            The times at which the Hamiltonian should be sampled for the Runge–Kutta integration.
            If you provide it, must start with 0 and be ordered.
            If you don't provide it, the `sample_times` are used for the integration.
        name : str or None, optional
            The name of the node.

        Returns
        -------
        Tensor
            Tensor of shape ``(..., N, D, D)``, representing the unitary time evolution.
            The n-th element (along the -3 dimension) represents the unitary (or batch of unitaries)
            from t = 0 to ``sample_times[n]``.

        See Also
        --------
        Graph.time_evolution_operators_pwc : Corresponding operation for `Pwc` Hamiltonians.

        Notes
        -----
        For more information on `Stf` nodes see the `Working with time-dependent functions in
        Boulder Opal <https://docs.q-ctrl.com/boulder-opal/topics/working-with-time-dependent-
        functions-in-boulder-opal>`_ topic.

        Examples
        --------
        Simulate the dynamics of a qubit, where a simple Gaussian drive rotate the qubit
        along the x-axis.

        >>> duration = np.pi
        >>> initial_state = np.array([1, 0])
        >>> sigma_x = np.array([[0, 1], [1, 0]])
        >>> time = graph.identity_stf()
        >>> gaussian_drive = graph.exp(-(time ** 2))
        >>> hamiltonian = gaussian_drive * sigma_x * np.sqrt(np.pi) / 2
        >>> graph.time_evolution_operators_stf(
        ...     hamiltonian=hamiltonian,
        ...     sample_times=[duration],
        ...     evolution_times=np.linspace(0, duration, 200),
        ...     name="unitaries",
        ... )
        <Tensor: name="unitaries", operation_name="time_evolution_operators_stf", shape=(1, 2, 2)>
        >>> result = bo.execute_graph(graph=graph, output_node_names="unitaries")
        >>> result["output"]["unitaries"]["value"].dot(initial_state)
        array([[0.70711169 + 0.0j, 0.0 - 0.70710187j]])
        """
        if evolution_times is None:
            Checker.VALUE(
                sample_times[0] == 0,
                "If you don't provide evolution times, the first of the sample times must be zero.",
            )
        shape = hamiltonian.batch_shape + (len(sample_times),) + hamiltonian.value_shape
        operation = create_operation(self.time_evolution_operators_stf, locals())
        return Tensor(operation, shape=shape)

    @validated
    def convolve_pwc(self, pwc: Pwc, kernel: ConvolutionKernel) -> Stf:
        r"""
        Create the convolution of a piecewise-constant function with a kernel.

        Parameters
        ----------
        pwc : Pwc
            The piecewise-constant function :math:`\alpha(t)` to convolve. You
            can provide a batch of functions, in which case the convolution is
            applied to each element of the batch.
        kernel : ConvolutionKernel
            The node representing the kernel :math:`K(t)`.

        Returns
        -------
        Stf
            The sampleable function representing the signal :math:`(\alpha * K)(t)`
            (or batch of signals, if you provide a batch of functions).

        See Also
        --------
        Graph.discretize_stf : Discretize an `Stf` into a `Pwc`.
        Graph.filter_and_resample_pwc : Filter a `Pwc` with a sinc filter and resample it.
        Graph.gaussian_convolution_kernel :
            Create a convolution kernel representing a normalized Gaussian.
        Graph.pwc : Create piecewise-constant functions.
        Graph.sample_stf : Sample an `Stf` at given times.
        Graph.sinc_convolution_kernel : Create a convolution kernel representing the sinc function.

        Notes
        -----
        The convolution is

        .. math::
            (\alpha * K)(t) \equiv
            \int_{-\infty}^\infty \alpha(\tau) K(t-\tau) d\tau.

        Convolution in the time domain is equivalent to multiplication in the
        frequency domain, so this function can be viewed as applying a linear
        time-invariant filter (specified via its time domain kernel :math:`K(t)`)
        to :math:`\alpha(t)`.

        For more information on `Stf` nodes see the `Working with time-dependent functions in
        Boulder Opal <https://docs.q-ctrl.com/boulder-opal/topics/working-with-time-dependent-
        functions-in-boulder-opal>`_ topic.

        Examples
        --------
        Filter a piecewise-constant signal using a Gaussian convolution kernel.

        >>> gaussian_kernel = graph.gaussian_convolution_kernel(std=1.0, offset=3.0)
        >>> gaussian_kernel
        <ConvolutionKernel: operation_name="gaussian_convolution_kernel">
        >>> pwc_signal
        <Pwc: name="alpha", operation_name="pwc_signal", value_shape=(), batch_shape=()>
        >>> filtered_signal = graph.convolve_pwc(pwc=pwc_signal, kernel=gaussian_kernel)
        >>> filtered_signal
        <Stf: operation_name="convolve_pwc", value_shape=(), batch_shape=()>

        Refer to the `How to add smoothing and band-limits to optimized controls
        <https://docs.q-ctrl.com/boulder-opal/user-guides/how-to-add-smoothing-and-band-limits-to-optimized-controls>`_
        user guide to find the example in context.
        """
        operation = create_operation(self.convolve_pwc, locals())
        return Stf(operation, value_shape=pwc.value_shape, batch_shape=pwc.batch_shape)

    @validated
    def sinc_convolution_kernel(
        self, cutoff_frequency: Annotated[Union[float, Tensor], pipe(positive_scalar)]
    ) -> ConvolutionKernel:
        r"""
        Create a convolution kernel representing the sinc function.

        Use this kernel to eliminate angular frequencies above a certain cutoff.

        Parameters
        ----------
        cutoff_frequency : float or Tensor
            Upper limit :math:`\omega_c` of the range of angular frequencies that you want
            to preserve. The filter eliminates components of the signal that have
            higher angular frequencies.

        Returns
        -------
        ConvolutionKernel
            A node representing the sinc function to use in a convolution.

        See Also
        --------
        Graph.convolve_pwc : Create an `Stf` by convolving a `Pwc` with a kernel.
        Graph.filter_and_resample_pwc : Filter a `Pwc` with a sinc filter and resample it.
        Graph.gaussian_convolution_kernel :
            Create a convolution kernel representing a normalized Gaussian.

        Notes
        -----
        The sinc kernel that this node represents is defined as

        .. math::
            K(t) = \frac{\sin(\omega_c t)}{\pi t}.

        In the frequency domain, the sinc function is constant in the range
        :math:`[-\omega_c, \omega_c]` and zero elsewhere. The filter it represents therefore
        passes angular frequencies only in that range.

        For more information on `Stf` nodes see the `Working with time-dependent functions in
        Boulder Opal <https://docs.q-ctrl.com/boulder-opal/topics/working-with-time-dependent-
        functions-in-boulder-opal>`_ topic.

        Examples
        --------
        Filter a signal by convolving it with a sinc kernel.

        >>> sinc_kernel = graph.sinc_convolution_kernel(cutoff_frequency=300e6)
        >>> sinc_kernel
        <ConvolutionKernel: operation_name="sinc_convolution_kernel">
        >>> pwc_signal
        <Pwc: name="pwc_signal_#1", operation_name="pwc_signal", value_shape=(), batch_shape=()>
        >>> filtered_signal = graph.convolve_pwc(pwc=pwc_signal, kernel=sinc_kernel)
        >>> filtered_signal
        <Stf: operation_name="convolve_pwc", value_shape=(), batch_shape=()>

        Refer to the `How to create leakage-robust single-qubit gates
        <https://docs.q-ctrl.com/boulder-opal/user-guides/how-to-create-leakage-robust-single-qubit-gates>`_
        user guide to find the example in context.
        """
        return ConvolutionKernel(
            create_operation(self.sinc_convolution_kernel, locals())
        )

    @validated
    def gaussian_convolution_kernel(
        self,
        std: Annotated[Union[float, Tensor], pipe(positive_scalar)],
        offset: Annotated[Union[float, Tensor], pipe(non_negative_scalar)] = 0,
    ) -> ConvolutionKernel:
        r"""
        Create a convolution kernel representing a normalized Gaussian.

        Use this kernel to allow angular frequencies in the range roughly determined by
        its width, and progressively suppress components outside that range.

        Parameters
        ----------
        std : float or Tensor
            Standard deviation :math:`\sigma` of the Gaussian in the time domain.
            The standard deviation in the frequency domain is its inverse, so that
            a high value of this parameter lets fewer angular frequencies pass.
        offset : float or Tensor, optional
            Center :math:`\mu` of the Gaussian distribution in the time domain.
            Use this to offset the signal in time. Defaults to 0.

        Returns
        -------
        ConvolutionKernel
            A node representing a Gaussian function to use in a convolution.

        See Also
        --------
        Graph.convolve_pwc : Create an `Stf` by convolving a `Pwc` with a kernel.
        Graph.sinc_convolution_kernel : Create a convolution kernel representing the sinc function.

        Notes
        -----
        The Gaussian kernel that this node represents is defined as:

        .. math::
            K(t) = \frac{e^{-(t-\mu)^2/(2\sigma^2)}}{\sqrt{2\pi\sigma^2}}.

        In the frequency domain, this Gaussian has standard deviation
        :math:`\omega_c= \sigma^{-1}`. The filter it represents therefore
        passes angular frequencies roughly in the range :math:`[-\omega_c, \omega_c]`.

        For more information on `Stf` nodes see the `Working with time-dependent functions in
        Boulder Opal <https://docs.q-ctrl.com/boulder-opal/topics/working-with-time-dependent-
        functions-in-boulder-opal>`_ topic.

        Examples
        --------
        Filter a signal by convolving it with a Gaussian kernel.

        >>> gaussian_kernel = graph.gaussian_convolution_kernel(std=1.0, offset=3.0)
        >>> gaussian_kernel
        <ConvolutionKernel: operation_name="gaussian_convolution_kernel">
        >>> signal
        <Pwc: name="alpha", operation_name="pwc_signal", value_shape=(), batch_shape=()>
        >>> filtered_signal = graph.convolve_pwc(pwc=signal, kernel=gaussian_kernel)
        >>> filtered_signal
        <Stf: operation_name="convolve_pwc", value_shape=(), batch_shape=()>

        Refer to the `How to characterize a transmission line using a qubit as a probe
        <https://docs.q-ctrl.com/boulder-opal/user-guides/how-to-characterize-a-transmission-
        line-using-a-qubit-as-a-probe>`_ user guide to find the example in context.
        """
        return ConvolutionKernel(
            create_operation(self.gaussian_convolution_kernel, locals())
        )

    @validated
    def sample_stf(
        self,
        stf: Stf,
        sample_times: Annotated[np.ndarray, pipe(ArrayT.REAL().ndim(1).ge(0).ascend())],
        *,
        name: Optional[str] = None,
    ) -> Tensor:
        """
        Sample an Stf at the given times.

        Parameters
        ----------
        stf : Stf
            The Stf to sample.
        sample_times : np.ndarray
            The times at which you want to sample the Stf. Must be ordered and contain
            at least one element.
        name : str or None, optional
            The name of the node.

        Returns
        -------
        Tensor
            The values of the Stf at the given times.

        See Also
        --------
        Graph.constant_stf_operator : Create a constant `Stf` operator.
        Graph.discretize_stf : Discretize an `Stf` into a `Pwc`.
        Graph.identity_stf : Create an `Stf` representing the identity function.
        Graph.sample_pwc : Sample a `Pwc` at given times.

        Notes
        -----
        For more information on `Stf` nodes see the `Working with time-dependent functions in
        Boulder Opal <https://docs.q-ctrl.com/boulder-opal/topics/working-with-time-dependent-
        functions-in-boulder-opal>`_ topic.
        """
        shape = stf.batch_shape + (len(sample_times),) + stf.value_shape
        return Tensor(create_operation(self.sample_stf, locals()), shape=shape)

    def identity_stf(self) -> Stf:
        r"""
        Create an Stf representing the identity function, f(t) = t.

        Returns
        -------
        Stf
            An Stf representing the identity function.

        See Also
        --------
        Graph.constant_stf: Create a batch of constant `Stf`\s.
        Graph.discretize_stf : Discretize an `Stf` into a `Pwc`.
        Graph.sample_stf : Sample an `Stf` at given times.

        Notes
        -----
        For more information on `Stf` nodes see the `Working with time-dependent functions in
        Boulder Opal <https://docs.q-ctrl.com/boulder-opal/topics/working-with-time-dependent-
        functions-in-boulder-opal>`_ topic.

        Examples
        --------
        Create Gaussian pulse.

        >>> time = graph.identity_stf()
        >>> time
        <Stf: operation_name="identity_stf", value_shape=(), batch_shape=()>
        >>> gaussian = graph.exp(- time ** 2)
        >>> gaussian
        <Stf: operation_name="exp", value_shape=(), batch_shape=()>

        See more examples in the `How to define continuous analytical Hamiltonians
        <https://docs.q-ctrl.com/boulder-opal/user-guides/how-to-define-continuous-analytical-
        hamiltonians>`_ user guide.
        """
        operation = create_operation(self.identity_stf, locals())
        return Stf(operation, value_shape=(), batch_shape=())
