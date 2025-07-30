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
    Pwc,
    Tensor,
)
from boulderopal._nodes.utils import (
    get_broadcasted_shape,
    mesh_pwc_durations,
)
from boulderopal._nodes.validation import (
    ShapeT,
    bounded_by,
    no_scalar,
    scalar_or_shapeable,
    shapeable,
    strict_real_array,
)
from boulderopal._typing import Annotated
from boulderopal._validation import (
    ArrayT,
    Checker,
    ScalarT,
    pipe,
    validated,
)


class PwcGraph:  # pylint: disable=unused-argument
    """
    Base class implementing Pwc graph methods.
    """

    @validated
    def pwc(
        self,
        durations: Annotated[np.ndarray, pipe(ArrayT.REAL().ndim(1).gt(0))],
        values: Annotated[Union[np.ndarray, Tensor], pipe(shapeable, after=no_scalar)],
        time_dimension: Annotated[int, pipe(ScalarT.INT())] = 0,
        *,
        name: Optional[str] = None,
    ) -> Pwc:
        r"""
        Create a piecewise-constant function of time.

        Parameters
        ----------
        durations : np.ndarray (1D, real)
            The durations :math:`\{\delta t_n\}` of the :math:`N` constant
            segments.
        values : np.ndarray or Tensor
            The values :math:`\{v_n\}` of the function on the constant segments.
            The dimension corresponding to `time_dimension` must be the same
            length as `durations`. To create a batch of
            :math:`B_1 \times \ldots \times B_n` piecewise-constant tensors of
            shape :math:`D_1 \times \ldots \times D_m`, provide this `values`
            parameter as an object of shape
            :math:`B_1\times\ldots\times B_n\times N\times D_1\times\ldots\times D_m`.
        time_dimension : int, optional
            The axis along `values` corresponding to time. All dimensions that
            come before the `time_dimension` are batch dimensions: if there are
            :math:`n` batch dimensions, then `time_dimension` is also :math:`n`.
            Defaults to 0, which corresponds to no batch. Note that you can
            pass a negative value to refer to the time dimension.
        name : str or None, optional
            The name of the node.

        Returns
        -------
        Pwc
            The piecewise-constant function of time :math:`v(t)`, satisfying
            :math:`v(t)=v_n` for :math:`t_{n-1}\leq t\leq t_n`, where
            :math:`t_0=0` and :math:`t_n=t_{n-1}+\delta t_n`. If you provide a
            batch of values, the returned `Pwc` represents a
            corresponding batch of :math:`B_1 \times \ldots \times B_n`
            functions :math:`v(t)`, each of shape
            :math:`D_1 \times \ldots \times D_m`.

        See Also
        --------
        Graph.pwc_operator : Create `Pwc` operators.
        Graph.pwc_signal : Create `Pwc` signals from (possibly complex) values.
        Graph.pwc_sum : Sum multiple `Pwc`\s.

        Notes
        -----
        For more information on `Pwc` nodes see the `Working with time-dependent functions in
        Boulder Opal <https://docs.q-ctrl.com/boulder-opal/topics/working-with-time-dependent-
        functions-in-boulder-opal>`_ topic.

        Examples
        --------
        Create a Hamiltonian from a piecewise-constant signal with non-uniform segment durations.

        >>> omega = graph.pwc(
        ...     values=np.array([1, 2, 3]), durations=np.array([0.1, 0.2, 0.3]), name="omega"
        ... )
        >>> omega
        <Pwc: name="omega", operation_name="pwc", value_shape=(), batch_shape=()>
        >>> sigma_z = np.array([[1, 0], [0, -1]])
        >>> hamiltonian = omega * sigma_z
        >>> hamiltonian.name = "hamiltonian"
        >>> result = bo.execute_graph(graph=graph, output_node_names="hamiltonian")
        >>> result["output"]["hamiltonian"]
        {
            'durations': array([0.1, 0.2, 0.3]),
            'values': array([
                [[ 1.,  0.], [ 0., -1.]],
                [[ 2.,  0.], [ 0., -2.]],
                [[ 3.,  0.], [ 0., -3.]]
            ]),
            'time_dimension': 0
        }

        See more examples in the `How to simulate quantum dynamics subject to noise with graphs
        <https://docs.q-ctrl.com/boulder-opal/user-guides/how-to-simulate-
        quantum-dynamics-subject-to-noise-with-graphs>`_ user guide.
        """
        Checker.VALUE(
            -len(values.shape) <= time_dimension < len(values.shape),
            "The time_dimension must be a valid dimension of values.",
            {"time_dimension": time_dimension, "value_shape": values.shape},
        )
        Checker.VALUE(
            values.shape[time_dimension] == len(durations),
            "The size of the time dimension of values must be equal to the length"
            " of the durations.",
            {"time_dimension": time_dimension, "len(durations)": len(durations)},
        )

        operation = create_operation(self.pwc, locals())

        _dim = (
            time_dimension
            if time_dimension >= 0
            else time_dimension + len(values.shape)
        )
        return Pwc(
            operation,
            value_shape=values.shape[_dim + 1 :],
            durations=durations,
            batch_shape=values.shape[:_dim],
        )

    @validated
    def pwc_signal(
        self,
        values: Annotated[Union[np.ndarray, Tensor], pipe(shapeable, after=no_scalar)],
        duration: Annotated[float, pipe(ScalarT.REAL().gt(0))],
        *,
        name: Optional[str] = None,
    ) -> Pwc:
        r"""
        Create a piecewise-constant signal (scalar-valued function of time).

        Use this function to create a piecewise-constant signal in which the
        constant segments all have the same duration.

        Parameters
        ----------
        values : np.ndarray or Tensor
            The values :math:`\{\alpha_n\}` of the :math:`N` constant segments.
            These can represent either a single sequence of segment values or a
            batch of them. To create a batch of
            :math:`B_1 \times \ldots \times B_n` signals, represent these
            `values` as a tensor of shape
            :math:`B_1 \times \ldots \times B_n \times N`.
        duration : float
            The total duration :math:`\tau` of the signal.
        name : str or None, optional
            The name of the node.

        Returns
        -------
        Pwc
            The piecewise-constant function of time :math:`\alpha(t)`, satisfying
            :math:`\alpha(t)=\alpha_n` for :math:`t_{n-1}\leq t\leq t_n`, where
            :math:`t_n=n\tau/N` (where :math:`N` is the number of values
            in :math:`\{\alpha_n\}`). If you provide a batch of values, the
            returned `Pwc` represents a corresponding batch of
            :math:`B_1 \times \ldots \times B_n` functions :math:`\alpha(t)`.

        See Also
        --------
        Graph.complex_pwc_signal : Create complex `Pwc` signals from their moduli and phases.
        Graph.pwc : Corresponding operation with support for segments of different durations.
        Graph.pwc_operator : Create `Pwc` operators.
        Graph.pwc_sum : Sum multiple `Pwc`\s.
        Graph.symmetrize_pwc : Symmetrize `Pwc`\s.

        Notes
        -----
        For more information on `Pwc` nodes see the `Working with time-dependent functions in
        Boulder Opal <https://docs.q-ctrl.com/boulder-opal/topics/working-with-time-dependent-
        functions-in-boulder-opal>`_ topic.

        Examples
        --------
        Create a piecewise-constant signal with uniform segment duration.

        >>> graph.pwc_signal(duration=0.1, values=np.array([2, 3]), name="signal")
        <Pwc: name="signal", operation_name="pwc_signal", value_shape=(), batch_shape=()>
        >>> result = bo.execute_graph(graph=graph, output_node_names="signal")
        >>> result["output"]["signal"]
        {
            'durations': array([0.05, 0.05]),
            'values': array([2., 3.]),
            'time_dimension': 0
        }

        See more examples in the `Get familiar with graphs <https://docs.q-ctrl.com/
        boulder-opal/tutorials/get-familiar-with-graphs>`_ tutorial.
        """

        shape = values.shape
        durations = duration / shape[-1] * np.ones(shape[-1])
        operation = create_operation(self.pwc_signal, locals())
        return Pwc(
            operation, value_shape=(), durations=durations, batch_shape=shape[:-1]
        )

    @validated
    def complex_pwc_signal(
        self,
        moduli: Annotated[
            Union[np.ndarray, Tensor],
            pipe(shapeable, after=[no_scalar, strict_real_array]),
        ],
        phases: Annotated[
            Union[np.ndarray, Tensor],
            pipe(shapeable, after=[no_scalar, strict_real_array]),
        ],
        duration: Annotated[float, pipe(ScalarT.REAL().gt(0))],
        *,
        name: Optional[str] = None,
    ) -> Pwc:
        r"""
        Create a complex piecewise-constant signal from moduli and phases.

        Use this function to create a complex piecewise-constant signal from
        moduli and phases defined for each segment, in which the constant segments
        all have the same duration.

        Parameters
        ----------
        moduli : np.ndarray(real) or Tensor(real)
            The moduli :math:`\{\Omega_n\}` of the values of :math:`N` constant
            segments. These can represent either the moduli of a single
            sequence of segment values or of a batch of them. To provide a
            batch of sequences of segment values of shape
            :math:`B_1 \times \ldots \times B_n`, represent these moduli as a
            tensor of shape :math:`B_1 \times \ldots \times B_n \times N`.
        phases : np.ndarray(real) or Tensor(real)
            The phases :math:`\{\phi_n\}` of the complex segment values. Must
            have the same length as `moduli` (or same shape, if you're
            providing a batch).
        duration : float
            The total duration :math:`\tau` of the signal.
        name : str or None, optional
            The name of the node.

        Returns
        -------
        Pwc
            The piecewise-constant function of time :math:`v(t)`, satisfying
            :math:`v(t)=\Omega_n e^{i\phi_n}` for :math:`t_{n-1}\leq t\leq t_n`,
            where :math:`t_n=n\tau/N` (where :math:`N` is the number of
            values in :math:`\{\Omega_n\}` and :math:`\{\phi_n\}`). If you
            provide a batch of `moduli` and `phases`, the returned `Pwc`
            represents a corresponding batch of
            :math:`B_1 \times \ldots \times B_n` functions :math:`v(t)`.

        See Also
        --------
        Graph.pwc_signal : Create `Pwc` signals from (possibly complex) values.

        Notes
        -----
        For more information on `Pwc` nodes see the `Working with time-dependent functions in
        Boulder Opal <https://docs.q-ctrl.com/boulder-opal/topics/working-with-time-dependent-
        functions-in-boulder-opal>`_ topic.

        Examples
        --------
        Create a complex piecewise-constant signal with batched moduli and phases.

        >>> moduli = np.array([[1, 2], [3, 4]])
        >>> phases = np.array([[0.1, 0.2], [0.5, 0.7]])
        >>> graph.complex_pwc_signal(moduli=moduli, phases=phases, duration=0.2, name="signal")
        <Pwc: name="signal", operation_name="complex_pwc_signal", value_shape=(), batch_shape=(2,)>
        >>> result = bo.execute_graph(graph=graph, output_node_names="signal")
        >>> result["output"]["signal"]
        {
            'durations': array([0.1, 0.1]),
            'values': array([
                [0.99500417+0.09983342j, 1.96013316+0.39733866j],
                [2.63274769+1.43827662j, 3.05936875+2.57687075j]
            ]),
            'time_dimension': 1
        }

        See more examples in the `Design robust single-qubit gates using computational graphs
        <https://docs.q-ctrl.com/boulder-opal/tutorials/design-robust-single-qubit-gates-
        using-computational-graphs>`_ tutorial.
        """

        Checker.VALUE(
            moduli.shape == phases.shape,
            "The shape of moduli and phases must be equal.",
            {"moduli.shape": moduli.shape, "phases.shape": phases.shape},
        )
        durations = duration / moduli.shape[-1] * np.ones(moduli.shape[-1])
        operation = create_operation(self.complex_pwc_signal, locals())
        return Pwc(
            operation,
            value_shape=(),
            durations=durations,
            batch_shape=moduli.shape[:-1],
        )

    @validated
    def pwc_operator(
        self,
        signal: Annotated[Pwc, pipe(after=ShapeT.SIGNAL())],
        operator: Annotated[
            Union[np.ndarray, Tensor],
            pipe(shapeable, after=ShapeT.OPERATOR().no_batch()),
        ],
        *,
        name: Optional[str] = None,
    ) -> Pwc:
        r"""
        Create a constant operator multiplied by a piecewise-constant signal.

        Parameters
        ----------
        signal : Pwc
            The piecewise-constant signal :math:`a(t)`, or a batch of
            piecewise-constant signals.
        operator : np.ndarray or Tensor
            The operator :math:`A`. It must have two equal dimensions.
        name : str or None, optional
            The name of the node.

        Returns
        -------
        Pwc
            The piecewise-constant operator :math:`a(t)A` (or a batch of
            piecewise-constant operators, if you provide a batch of
            piecewise-constant signals).

        See Also
        --------
        Graph.complex_pwc_signal : Create complex `Pwc` signals from their moduli and phases.
        Graph.constant_pwc_operator : Create constant `Pwc`\s.
        Graph.hermitian_part : Hermitian part of an operator.
        Graph.pwc : Create piecewise-constant functions.
        Graph.pwc_signal : Create `Pwc` signals from (possibly complex) values.
        Graph.pwc_sum : Sum multiple `Pwc`\s.
        Graph.stf_operator : Corresponding operation for `Stf`\s.

        Notes
        -----
        For more information on `Pwc` nodes see the `Working with time-dependent functions in
        Boulder Opal <https://docs.q-ctrl.com/boulder-opal/topics/working-with-time-dependent-
        functions-in-boulder-opal>`_ topic.

        Examples
        --------
        Create a piecewise-constant operator with non-uniform segment durations.

        >>> sigma_z = np.array([[1.0, 0.0],[0.0, -1.0]])
        >>> graph.pwc_operator(
        ...     signal=graph.pwc(durations=np.array([0.1, 0.2]), values=np.array([1, 2])),
        ...     operator=sigma_z,
        ...     name="operator",
        ... )
        <Pwc: name="operator", operation_name="pwc_operator", value_shape=(2, 2), batch_shape=()>
        >>> result = bo.execute_graph(graph=graph, output_node_names="operator")
        >>> result["output"]["operator"]
        {
            'durations': array([0.1, 0.2]),
            'values': array([
                [[ 1.,  0.], [ 0., -1.]],
                [[ 2.,  0.], [ 0., -2.]]
            ]),
            'time_dimension': 0
        }

        See more examples in the `How to represent quantum systems using graphs
        <https://docs.q-ctrl.com/boulder-opal/user-guides/how-to-represent-quantum-
        systems-using-graphs>`_ user guide.
        """

        operation = create_operation(self.pwc_operator, locals())
        return Pwc(
            operation,
            value_shape=operator.shape,
            durations=signal.durations,
            batch_shape=signal.batch_shape,
        )

    @validated
    def constant_pwc_operator(
        self,
        duration: Annotated[float, pipe(ScalarT.REAL().gt(0))],
        operator: Annotated[
            Union[np.ndarray, Tensor], pipe(shapeable, after=ShapeT.OPERATOR())
        ],
        *,
        name: Optional[str] = None,
    ) -> Pwc:
        # pylint: disable=line-too-long
        r"""
        Create a constant piecewise-constant operator over a specified duration.

        Parameters
        ----------
        duration : float
            The duration :math:`\tau` for the resulting piecewise-constant
            operator.
        operator : np.ndarray or Tensor
            The operator :math:`A`, or a batch of operators. It must have at
            least two dimensions, and its last two dimensions must be equal.
        name : str or None, optional
            The name of the node.

        Returns
        -------
        Pwc
            The constant operator :math:`t\mapsto A` (for :math:`0\leq t\leq\tau`)
            (or a batch of constant operators, if you provide a batch of operators).

        See Also
        --------
        Graph.constant_stf_operator : Corresponding operation for `Stf`\s.
        Graph.hermitian_part : Hermitian part of an operator.
        Graph.pwc_operator : Create `Pwc` operators.

        Notes
        -----
        For more information on `Pwc` nodes see the `Working with time-dependent functions in
        Boulder Opal <https://docs.q-ctrl.com/boulder-opal/topics/working-with-time-dependent-
        functions-in-boulder-opal>`_ topic.

        Examples
        --------
        Create a Hamiltonian from a batched constant operator.

        >>> sigma_x = np.array([[0.0, 1.0], [1.0, 0.0]])
        >>> sigma_z = np.array([[1.0, 0.0], [0.0, -1.0]])
        >>> batched_operators = np.asarray([sigma_x, sigma_z])
        >>> graph.constant_pwc_operator(duration=0.1, operator=batched_operators,  name="op")
        <Pwc: name="op", operation_name="constant_pwc_operator", value_shape=(2, 2), batch_shape=(2,)>
        >>> result = bo.execute_graph(graph=graph, output_node_names="op")
        >>> result["output"]["op"]
        {
            'durations': array([0.1]),
            'values': array([
                [[[ 0.,  1.], [ 1.,  0.]]],
                [[[ 1.,  0.], [ 0., -1.]]]
            ]),
            'time_dimension': 1
        }

        See more examples in the `How to represent quantum systems using graphs
        <https://docs.q-ctrl.com/boulder-opal/user-guides/how-to-represent-quantum-
        systems-using-graphs>`_ user guide.
        """
        # pylint: enable:line-too-long

        operation = create_operation(self.constant_pwc_operator, locals())
        return Pwc(
            operation,
            durations=np.array([duration]),
            value_shape=operator.shape[-2:],
            batch_shape=operator.shape[:-2],
        )

    @validated
    def constant_pwc(
        self,
        constant: Annotated[
            Union[float, complex, np.ndarray, Tensor], pipe(scalar_or_shapeable)
        ],
        duration: Annotated[float, pipe(ScalarT.REAL().gt(0))],
        batch_dimension_count: Annotated[int, pipe(ScalarT.INT().ge(0))] = 0,
        *,
        name: Optional[str] = None,
    ) -> Pwc:
        r"""
        Create a piecewise-constant function of time that is constant over a specified duration.

        Parameters
        ----------
        constant : number or np.ndarray or Tensor
            The value :math:`c` of the function on the constant segment.
            To create a batch of :math:`B_1 \times \ldots \times B_n` piecewise-constant
            functions of shape :math:`D_1 \times \ldots \times D_m`, provide this `constant`
            parameter as an object of shape
            :math:`B_1\times\ldots\times B_n\times D_1\times\ldots\times D_m`.
        duration : float
            The duration :math:`\tau` for the resulting piecewise-constant function.
        batch_dimension_count : int, optional
            The number of batch dimensions, :math:`n` in `constant`.
            If provided, the first :math:`n` dimensions of `constant` are considered batch
            dimensions. Defaults to 0, which corresponds to no batch.
        name : str or None, optional
            The name of the node.

        Returns
        -------
        Pwc
            The constant function :math:`f(t) = c` (for :math:`0\leq t\leq\tau`)
            (or a batch of constant functions, if you provide `batch_dimension_count`).

        See Also
        --------
        Graph.constant_pwc_operator : Create constant `Pwc` operators.
        Graph.constant_stf : Corresponding operation for `Stf`\s.
        Graph.pwc : Create piecewise-constant functions.

        Notes
        -----
        For more information on `Pwc` nodes see the `Working with time-dependent functions in
        Boulder Opal <https://docs.q-ctrl.com/boulder-opal/topics/working-with-time-dependent-
        functions-in-boulder-opal>`_ topic.

        Examples
        --------
        Create a batched piecewise-constant function.

        >>> constant = np.arange(12).reshape((2, 2, 3))
        >>> graph.constant_pwc(
        ...     constant=constant, duration=0.1, batch_dimension_count=1, name="constant"
        ... )
        <Pwc: name="constant", operation_name="constant_pwc", value_shape=(2, 3), batch_shape=(2,)>
        >>> result = bo.execute_graph(graph=graph, output_node_names="constant")
        >>> result["output"]["constant"]
        {
            'durations': array([0.1]),
            'values': array([
                [[[ 0.,  1.,  2.], [ 3.,  4.,  5.]]],
                [[[ 6.,  7.,  8.], [ 9., 10., 11.]]]
            ]),
            'time_dimension': 1
        }

        See more examples in the `Simulate the dynamics of a single qubit using computational graphs
        <https://docs.q-ctrl.com/boulder-opal/tutorials/simulate-the-dynamics-of-a-single-qubit-
        using-computational-graphs>`_ tutorial.
        """

        shape = getattr(constant, "shape", ())
        Checker.VALUE(
            len(shape) >= batch_dimension_count,
            "The number of batch dimensions must not be larger than the number "
            "of dimensions of the input constant.",
            {
                "constant": constant,
                "batch_dimension_count": batch_dimension_count,
                "Number of value dimensions": len(shape),
            },
        )

        operation = create_operation(self.constant_pwc, locals())
        return Pwc(
            operation,
            value_shape=shape[batch_dimension_count:],
            durations=np.array([duration]),
            batch_shape=shape[:batch_dimension_count],
        )

    @validated
    def pwc_sum(
        self,
        terms: Annotated[List[Pwc], Field(min_length=1)],
        *,
        name: Optional[str] = None,
    ) -> Pwc:
        r"""
        Create the sum of multiple piecewise-constant terms.

        Parameters
        ----------
        terms : list[Pwc]
            The individual piecewise-constant terms :math:`\{v_j(t)\}` to sum. All
            terms must have the same duration, values of the same shape, and the
            same batch shape, but may have different segmentations (different
            numbers of segments of different durations) and different dtypes of
            segment values.
        name : str or None, optional
            The name of the node.

        Returns
        -------
        Pwc
            The piecewise-constant function (or batch of functions) of time
            :math:`\sum_j v_j(t)`. Its values have the same shape as the values of
            each of the `terms` that you provided. If each of the `terms` represents
            a batch of functions, this result represents a batch of functions with
            the same batch shape. If any `term` has complex-valued segments, the
            value of the returned Pwc is complex, otherwise is float.

        See Also
        --------
        Graph.discretize_stf : Discretize an `Stf` into a `Pwc`.
        Graph.pwc : Create piecewise-constant functions.
        Graph.pwc_operator : Create `Pwc` operators.
        Graph.pwc_signal : Create `Pwc` signals from (possibly complex) values.
        Graph.stf_sum : Corresponding operation for `Stf`\s.

        Notes
        -----
        For more information on `Pwc` nodes see the `Working with time-dependent functions in
        Boulder Opal <https://docs.q-ctrl.com/boulder-opal/topics/working-with-time-dependent-
        functions-in-boulder-opal>`_ topic.

        Examples
        --------
        Sum a list of piecewise-constant terms of different durations.

        >>> x = graph.pwc(durations=np.array([0.1, 0.3]), values=np.array([1, 2]))
        >>> y = graph.pwc(durations=np.array([0.2, 0.2]), values=np.array([3, 1]))
        >>> graph.pwc_sum([x, y], name="sum")
        <Pwc: name="sum", operation_name="pwc_sum", value_shape=(), batch_shape=()>
        >>> result = bo.execute_graph(graph=graph, output_node_names="sum")
        >>> result["output"]["sum"]
        {
            'durations': array([0.1, 0.1, 0.2]),
            'values': array([4., 5., 3.]),
            'time_dimension': 0
        }

        See more examples in the `How to optimize controls robust to strong noise sources
        <https://docs.q-ctrl.com/boulder-opal/user-guides/how-to-optimize-controls-robust-to-
        strong-noise-sources>`_ user guide.
        """

        for attr in ["value_shape", "batch_shape"]:
            Checker.VALUE(
                len(set(getattr(term, attr) for term in terms)) == 1,
                f"All the terms must have the same {attr}.",
            )

        return Pwc(
            operation=create_operation(self.pwc_sum, locals()),
            durations=mesh_pwc_durations(terms),
            value_shape=terms[0].value_shape,
            batch_shape=terms[0].batch_shape,
        )

    @validated
    def time_reverse_pwc(self, pwc: Pwc, *, name: Optional[str] = None) -> Pwc:
        r"""
        Reverse in time a piecewise-constant function.

        Parameters
        ----------
        pwc : Pwc
            The piecewise-constant function :math:`v(t)` to reverse.
        name : str or None, optional
            The name of the node.

        Returns
        -------
        Pwc
            The piecewise-constant function :math:`w(t)` defined by
            :math:`w(t)=v(\tau-t)` for :math:`0\leq t\leq \tau`, where
            :math:`\tau` is the duration of :math:`v(t)`.

        See Also
        --------
        Graph.symmetrize_pwc : Symmetrize `Pwc`\s.
        Graph.time_concatenate_pwc : Concatenate `Pwc`\s in time.

        Notes
        -----
        For more information on `Pwc` nodes see the `Working with time-dependent functions in
        Boulder Opal <https://docs.q-ctrl.com/boulder-opal/topics/working-with-time-dependent-
        functions-in-boulder-opal>`_ topic.

        Examples
        --------
        Reverse a piecewise constant function.

        >>> x = graph.pwc(durations=np.array([0.1, 0.5, 0.3]), values=np.array([1, 2, 3]))
        >>> graph.time_reverse_pwc(x, name="reverse")
        <Pwc: name="reverse", operation_name="time_reverse_pwc", value_shape=(), batch_shape=()>
        >>> result = bo.execute_graph(graph=graph, output_node_names="reverse")
        >>> result["output"]["reverse"]
        {
            'durations': array([0.3, 0.5, 0.1]),
            'values': array([3., 2., 1.]),
            'time_dimension': 0
        }
        """
        return Pwc(
            operation=create_operation(self.time_reverse_pwc, locals()),
            value_shape=pwc.value_shape,
            durations=pwc.durations[::-1],
            batch_shape=pwc.batch_shape,
        )

    @validated
    def symmetrize_pwc(self, pwc: Pwc, *, name: Optional[str] = None) -> Pwc:
        r"""
        Create the symmetrization of a piecewise-constant function.

        Parameters
        ----------
        pwc : Pwc
            The piecewise-constant function :math:`v(t)` to symmetrize.
        name : str or None, optional
            The name of the node.

        Returns
        -------
        Pwc
            The piecewise-constant function :math:`w(t)` defined by
            :math:`w(t)=v(t)` for :math:`0\leq t\leq \tau` and
            :math:`w(t)=v(2\tau-t)` for :math:`\tau\leq t\leq 2\tau`, where
            :math:`\tau` is the duration of :math:`v(t)`.

        See Also
        --------
        Graph.pwc_signal : Create `Pwc` signals from (possibly complex) values.
        Graph.time_reverse_pwc : Reverse `Pwc`\s in time.

        Notes
        -----
        For more information on `Pwc` nodes see the `Working with time-dependent functions in
        Boulder Opal <https://docs.q-ctrl.com/boulder-opal/topics/working-with-time-dependent-
        functions-in-boulder-opal>`_ topic.

        Examples
        --------
        Create a symmetric piecewise-constant function.

        >>> x = graph.pwc(durations=np.array([0.1, 0.3]), values=np.array([1, 2]))
        >>> graph.symmetrize_pwc(x, name="symmetrize")
        <Pwc: name="symmetrize", operation_name="symmetrize_pwc", value_shape=(), batch_shape=()>
        >>> result = bo.execute_graph(graph=graph, output_node_names="symmetrize")
        >>> result["output"]["symmetrize"]
        {
            'durations': array([0.1, 0.3, 0.3, 0.1]),
            'values': array([1., 2., 2., 1.]),
            'time_dimension': 0
        }

        See more examples in the `How to optimize controls with time symmetrization
        <https://docs.q-ctrl.com/boulder-opal/user-guides/how-to-optimize-controls-with-
        time-symmetrization>`_ user guide.
        """
        symmetrized_durations = np.concatenate((pwc.durations, pwc.durations[::-1]))
        return Pwc(
            operation=create_operation(self.symmetrize_pwc, locals()),
            value_shape=pwc.value_shape,
            durations=symmetrized_durations,
            batch_shape=pwc.batch_shape,
        )

    @validated
    def time_concatenate_pwc(
        self,
        pwc_list: Annotated[List[Pwc], Field(min_length=1)],
        *,
        name: Optional[str] = None,
    ) -> Pwc:
        r"""
        Concatenate multiple piecewise-constant functions in the time dimension.

        Parameters
        ----------
        pwc_list : list[Pwc]
            The individual piecewise-constant functions :math:`\{A_i(t)\}` to concatenate.
            All the functions must have the same value shape, and can have broadcastable
            batch shapes.
        name : str or None, optional
            The name of the node.

        Returns
        -------
        Pwc
            The concatenated piecewise-constant function (or batch of functions).

        See Also
        --------
        Graph.pwc : Create piecewise-constant functions.
        Graph.pwc_sum : Sum multiple `Pwc`\s.
        Graph.symmetrize_pwc : Symmetrize `Pwc`\s.
        Graph.time_reverse_pwc : Reverse `Pwc`\s in time.

        Notes
        -----
        The function resulting from the concatenation is

        .. math::
            C(t) = \begin{cases}
            A_0(t) & \mathrm{for} & 0 < t < \tau_0
            \\
            A_1(t - \tau_0) & \mathrm{for} & \tau_0 < t < \tau_0 + \tau_1
            \\
            A_2(t - \tau_0 - \tau_1) & \mathrm{for} & \tau_0 + \tau_1 < t < \tau_0 + \tau_1 + \tau_2
            \\
            & \vdots &
            \end{cases}

        where :math:`\tau_i` is the duration of the i-th function.

        For more information on `Pwc` nodes see the `Working with time-dependent functions in
        Boulder Opal <https://docs.q-ctrl.com/boulder-opal/topics/working-with-time-dependent-
        functions-in-boulder-opal>`_ topic.

        Examples
        --------
        Concatenate two piecewise-constant functions.

        >>> pwc1 = graph.pwc(durations=np.array([0.2, 0.5]), values=np.array([1, 2]))
        >>> pwc2 = graph.pwc(durations=np.array([0.7, 0.9]), values=np.array([3, 4]))
        >>> graph.time_concatenate_pwc([pwc1, pwc2], name="concat")
        <Pwc: name="concat", operation_name="time_concatenate_pwc", value_shape=(), batch_shape=()>
        >>> result = bo.execute_graph(graph=graph, output_node_names="concat")
        >>> result["output"]["concat"]
        {
            'durations': array([0.2, 0.5, 0.7, 0.9]),
            'values': array([1., 2., 3., 4.]),
            'time_dimension': 0
        """
        Checker.VALUE(
            len(set(pwc.value_shape for pwc in pwc_list)) == 1,
            "All the Pwcs must have the same value shape.",
        )
        batch_shape = get_broadcasted_shape(
            *[pwc.batch_shape for pwc in pwc_list],
            message="All the Pwcs must have broadcastable batch shapes.",
        )
        return Pwc(
            operation=create_operation(self.time_concatenate_pwc, locals()),
            durations=np.concatenate([pwc.durations for pwc in pwc_list]),
            value_shape=pwc_list[0].value_shape,
            batch_shape=batch_shape,
        )

    @validated
    def time_evolution_operators_pwc(
        self,
        hamiltonian: Annotated[Pwc, pipe(after=ShapeT.OPERATOR())],
        sample_times: Annotated[np.ndarray, pipe(ArrayT.REAL().ndim(1).ge(0).ascend())],
        *,
        name: Optional[str] = None,
    ) -> Tensor:
        """
        Calculate the unitary time-evolution operators for a system defined by a piecewise-constant
        Hamiltonian.

        Parameters
        ----------
        hamiltonian : Pwc
            The control Hamiltonian, or batch of control Hamiltonians.
        sample_times : np.ndarray
            The N times at which you want to sample the unitaries. Must be ordered and contain
            at least one element, and lie between 0 and the duration of the Hamiltonian.
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
        Graph.state_evolution_pwc : Evolve a quantum state.
        Graph.time_evolution_operators_stf : Corresponding operation for `Stf` Hamiltonians.

        Notes
        -----
        For more information on `Pwc` nodes see the `Working with time-dependent functions in
        Boulder Opal <https://docs.q-ctrl.com/boulder-opal/topics/working-with-time-dependent-
        functions-in-boulder-opal>`_ topic.

        Examples
        --------
        Simulate the dynamics of a single qubit, where a constant drive rotates the
        qubit along the x-axis.

        >>> initial_state = np.array([1, 0])
        >>> sigma_x = np.array([[0, 1], [1, 0]])
        >>> duration = np.pi
        >>> hamiltonian = graph.constant_pwc_operator(duration=duration, operator=sigma_x / 2)
        >>> graph.time_evolution_operators_pwc(
        ...     hamiltonian=hamiltonian, sample_times=[duration], name="unitaries"
        ... )
        <Tensor: name="unitaries", operation_name="time_evolution_operators_pwc", shape=(1, 2, 2)>
        >>> result = bo.execute_graph(graph=graph, output_node_names="unitaries")
        >>> result["output"]["unitaries"]["value"].dot(initial_state)
        array([[5.0532155e-16+0.j, 0.0000000e+00-1.j]])

        See more examples in the `How to simulate quantum dynamics for noiseless systems
        using graphs <https://docs.q-ctrl.com/boulder-opal/user-guides/how-to-simulate-
        quantum-dynamics-for-noiseless-systems-using-graphs>`_ user guide.
        """

        duration = np.sum(hamiltonian.durations)
        sample_times = bounded_by(
            sample_times, "sample_times", duration, "the duration of Hamiltonian"
        )
        shape = hamiltonian.batch_shape + (len(sample_times),) + hamiltonian.value_shape
        operation = create_operation(self.time_evolution_operators_pwc, locals())
        return Tensor(operation, shape=shape)

    @validated
    def sample_pwc(
        self,
        pwc: Pwc,
        sample_times: Annotated[np.ndarray, pipe(ArrayT.REAL().ndim(1).ge(0).ascend())],
        *,
        name: Optional[str] = None,
    ) -> Tensor:
        r"""
        Sample a Pwc at the given times.

        Parameters
        ----------
        pwc : Pwc
            The Pwc to sample.
        sample_times : list or tuple or np.ndarray(1D, real)
            The times at which you want to sample the Pwc. Must be ordered, contain
            at least one element, and lie between 0 and the duration of the Pwc.
            For a sample time :math:`t` the returned value
            lies in the half open interval :math:`t_{j-1} < t \leq t_j`, where
            :math:`t_j` indicates the boundary of a segment.
        name : str or None, optional
            The name of the node.

        Returns
        -------
        Tensor
            The values of the Pwc at the given times.

        See Also
        --------
        Graph.sample_stf : Sample an `Stf` at given times.

        Notes
        -----
        For more information on `Pwc` nodes see the `Working with time-dependent functions in
        Boulder Opal <https://docs.q-ctrl.com/boulder-opal/topics/working-with-time-dependent-
        functions-in-boulder-opal>`_ topic.
        """

        duration = np.sum(pwc.durations)
        sample_times = bounded_by(
            sample_times, "sample_times", duration, "the duration of pwc"
        )
        shape = pwc.batch_shape + (len(sample_times),) + pwc.value_shape
        operation = create_operation(self.sample_pwc, locals())
        return Tensor(operation, shape=shape)
