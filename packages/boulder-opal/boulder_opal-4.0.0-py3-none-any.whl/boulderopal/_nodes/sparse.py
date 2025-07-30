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
    List,
    Optional,
    Union,
)

import numpy as np
from pydantic import Field
from scipy.sparse import (
    issparse,
    spmatrix,
)

from boulderopal._nodes.base import create_operation
from boulderopal._nodes.validation import (
    ArrayT,
    ShapeT,
    _to_scalar_tensor,
    bounded_by,
    shapeable,
)
from boulderopal._typing import Annotated
from boulderopal._validation import (
    Checker,
    ScalarT,
    pipe,
    type_pipe,
    validated,
)

from .node_data import (
    Pwc,
    SparsePwc,
    Tensor,
)
from .utils import mesh_pwc_durations


def _int_messenger(name: str) -> str:
    return f"The {name} must be a positive int or a scalar Tensor."


def _float_messenger(name: str) -> str:
    return f"The {name} must be a positive float or a scalar Tensor."


_scalar_int = type_pipe([ScalarT.INT().gt(0), _to_scalar_tensor], _int_messenger)
_scalar_float = type_pipe([ScalarT.REAL().gt(0), _to_scalar_tensor], _float_messenger)


def _validate_terms(value: list[SparsePwc], *, name: str) -> list[SparsePwc]:
    """
    Validate a list of SparsePwc terms.
    """
    shape_0 = value[0].value_shape
    for i, term in enumerate(value):
        shape = term.value_shape
        Checker.VALUE(
            shape == shape_0,
            f"All the elements in {name} must have the same shape.",
            {"terms[0].value_shape": shape_0, f"terms[{i}].value_shape": shape},
        )
    return value


class SparseGraph:  # pylint: disable=unused-argument
    """
    Base class implementing sparse graph methods.
    """

    @validated
    def sparse_pwc_operator(
        self,
        signal: Annotated[Pwc, pipe(shapeable, after=ShapeT.SIGNAL().no_batch())],
        operator: Annotated[
            Union[np.ndarray, spmatrix, Tensor],
            pipe(shapeable, after=ShapeT.OPERATOR().no_batch()),
        ],
    ) -> SparsePwc:
        r"""
        Create a sparse piecewise-constant operator (sparse-matrix-valued function of time).

        Each of the piecewise-constant segments (time periods) is a scalar multiple
        of the operator.

        Parameters
        ----------
        signal : Pwc
            The scalar-valued piecewise-constant function of time :math:`a(t)`.
        operator : numpy.ndarray or scipy.sparse.spmatrix or Tensor
            The sparse operator :math:`A` to be scaled over time.
            If you pass a Tensor or NumPy array, it will be internally
            converted into a sparse representation.

        Returns
        -------
        SparsePwc
            The piecewise-constant sparse operator :math:`a(t)A`.

        See Also
        --------
        Graph.constant_sparse_pwc_operator : Create constant `SparsePwc`\s.
        Graph.density_matrix_evolution_pwc : Evolve a quantum state in an open system.
        Graph.pwc_operator : Corresponding operation for `Pwc`\s.
        Graph.sparse_pwc_hermitian_part : Hermitian part of a `SparsePwc` operator.
        Graph.sparse_pwc_sum : Sum multiple `SparsePwc`\s.
        Graph.state_evolution_pwc : Evolve a quantum state.

        Examples
        --------
        Create a sparse PWC operator.

        >>> from scipy.sparse import coo_matrix
        >>> sigma_x = np.array([[0, 1], [1, 0]])
        >>> signal = graph.pwc_signal(values=np.array([1, 2, 3]), duration=0.1)
        >>> graph.sparse_pwc_operator(signal=signal, operator=coo_matrix(sigma_x))
        <SparsePwc: operation_name="sparse_pwc_operator", value_shape=(2, 2)>

        See more examples in the `How to simulate large open system dynamics
        <https://docs.q-ctrl.com/boulder-opal/user-guides/how-to-simulate-large-open-system-dynamics>`_
        user guide.
        """
        operation = create_operation(self.sparse_pwc_operator, locals())
        return SparsePwc(
            operation, value_shape=operator.shape, durations=signal.durations
        )

    @validated
    def constant_sparse_pwc_operator(
        self,
        duration: Annotated[float, pipe(ScalarT.REAL().gt(0))],
        operator: Annotated[
            Union[np.ndarray, spmatrix, Tensor],
            pipe(shapeable, after=ShapeT.OPERATOR().no_batch()),
        ],
    ) -> SparsePwc:
        r"""
        Create a constant sparse piecewise-constant operator over a specified duration.

        Parameters
        ----------
        duration : float
            The duration :math:`\tau` for the resulting piecewise-constant operator.
        operator : numpy.ndarray or scipy.sparse.spmatrix or Tensor
            The sparse operator :math:`A`. If you pass a Tensor or NumPy array,
            it will be internally converted into a sparse representation.

        Returns
        -------
        SparsePwc
            The constant operator :math:`t\mapsto A` (for :math:`0\leq t\leq\tau`).

        See Also
        --------
        Graph.constant_pwc_operator : Corresponding operation for `Pwc`\s.
        Graph.sparse_pwc_hermitian_part : Hermitian part of a `SparsePwc` operator.
        Graph.sparse_pwc_operator : Create `SparsePwc` operators.
        Graph.sparse_pwc_sum : Sum multiple `SparsePwc`\s.

        Examples
        --------
        Create a constant sparse PWC operator.

        >>> from scipy.sparse import coo_matrix
        >>> sigma_x = np.array([[0, 1], [1, 0]])
        >>> graph.constant_sparse_pwc_operator(duration=0.1, operator=coo_matrix(sigma_x))
        <SparsePwc: operation_name="constant_sparse_pwc_operator", value_shape=(2, 2)>

        See more examples in the `How to simulate large open system dynamics
        <https://docs.q-ctrl.com/boulder-opal/user-guides/how-to-simulate-large-open-system-dynamics>`_
        user guide.
        """
        operation = create_operation(self.constant_sparse_pwc_operator, locals())
        return SparsePwc(
            operation, value_shape=operator.shape, durations=np.array([duration])
        )

    @validated
    def sparse_pwc_sum(
        self,
        terms: Annotated[
            List[
                Annotated[
                    SparsePwc, pipe(shapeable, after=ShapeT.OPERATOR().no_batch())
                ]
            ],
            Field(min_length=1),
            pipe(after=_validate_terms),
        ],
    ) -> SparsePwc:
        r"""
        Create the sum of multiple sparse-matrix-valued piecewise-constant functions.

        Parameters
        ----------
        terms : list[SparsePwc]
            The individual piecewise-constant terms :math:`\{v_j(t)\}` to sum.
            All terms must be sparse, have values of the same shape,
            and have the same total duration
            but may have different numbers of segments of different durations.

        Returns
        -------
        SparsePwc
            The piecewise-constant function of time :math:`\sum_j v_j(t)`. It
            has the same shape as each of the `terms` that you provided.

        See Also
        --------
        Graph.constant_sparse_pwc_operator : Create constant `SparsePwc`\s.
        Graph.pwc_sum : Corresponding operation for `Pwc`\s.
        Graph.sparse_pwc_operator : Create `SparsePwc` operators.

        Examples
        --------
        Sum two sparse PWC operators.

        >>> from scipy.sparse import coo_matrix
        >>> sigma_x = np.array([[0, 1], [1, 0]])
        >>> sigma_y = np.array([[0, -1j], [1j, 0]])
        >>> sp_x = graph.constant_sparse_pwc_operator(duration=0.1, operator=coo_matrix(sigma_x))
        >>> sp_y = graph.constant_sparse_pwc_operator(duration=0.1, operator=coo_matrix(sigma_y))
        >>> graph.sparse_pwc_sum([sp_x, sp_y])
        <SparsePwc: operation_name="sparse_pwc_sum", value_shape=(2, 2)>

        See more examples in the `How to simulate large open system dynamics
        <https://docs.q-ctrl.com/boulder-opal/user-guides/how-to-simulate-large-open-system-dynamics>`_
        user guide.
        """
        value_shape = terms[0].value_shape
        operation = create_operation(self.sparse_pwc_sum, locals())
        return SparsePwc(
            operation, value_shape=value_shape, durations=mesh_pwc_durations(terms)
        )

    @validated
    def sparse_pwc_hermitian_part(
        self,
        operator: Annotated[
            SparsePwc, pipe(shapeable, after=ShapeT.OPERATOR().no_batch())
        ],
    ) -> SparsePwc:
        r"""
        Create the Hermitian part of a piecewise-constant operator.

        Parameters
        ----------
        operator : SparsePwc
            The operator :math:`A(t)`.

        Returns
        -------
        SparsePwc
            The Hermitian part :math:`\frac{1}{2}(A(t)+A^\dagger(t))`.

        See Also
        --------
        Graph.hermitian_part : Hermitian part of an operator.
        Graph.sparse_pwc_operator : Create `SparsePwc`\s.

        Examples
        --------
        Create a Hermitian sparse PWC operator.

        >>> from scipy.sparse import coo_matrix
        >>> sigma_m = np.array([[0, 1], [0, 0]])
        >>> sp_m = graph.constant_sparse_pwc_operator(duration=0.1, operator=coo_matrix(sigma_m))
        >>> graph.sparse_pwc_hermitian_part(sp_m)
        <SparsePwc: operation_name="sparse_pwc_hermitian_part", value_shape=(2, 2)>
        """
        operation = create_operation(self.sparse_pwc_hermitian_part, locals())
        return SparsePwc(
            operation, value_shape=operator.value_shape, durations=operator.durations
        )

    @validated
    def state_evolution_pwc(
        self,
        initial_state: Annotated[
            Union[np.ndarray, Tensor], pipe(shapeable, after=ShapeT.VECTOR().no_batch())
        ],
        hamiltonian: Annotated[
            Union[Pwc, SparsePwc], pipe(shapeable, after=ShapeT.OPERATOR().no_batch())
        ],
        krylov_subspace_dimension: Annotated[Union[int, Tensor], pipe(_scalar_int)],
        sample_times: Optional[
            Annotated[np.ndarray, pipe(ArrayT.REAL().ndim(1).ge(0).ascend())]
        ] = None,
        *,
        name: Optional[str] = None,
    ) -> Tensor:
        r"""
        Calculate the time evolution of a state generated by a piecewise-constant
        Hamiltonian by using the Lanczos method.

        Parameters
        ----------
        initial_state : Tensor or np.ndarray
            The initial state as a Tensor or np.ndarray of shape ``(D,)``.
        hamiltonian : Pwc or SparsePwc
            The control Hamiltonian. Uses sparse matrix multiplication if of type
            `SparsePwc`, which can be more efficient for large operators that are
            relatively sparse (contain mostly zeros).
        krylov_subspace_dimension : Tensor or int
            The dimension of the Krylov subspace `k` for the Lanczos method.
        sample_times : np.ndarray(1D, real) or None, optional
            The N times at which you want to sample the state. Must be ordered and
            contain at least one element. If omitted only the evolved state at the
            final time of the control Hamiltonian is returned.
        name : str or None, optional
            The name of the node.

        Returns
        -------
        Tensor
            Tensor of shape ``(N, D)`` or ``(D,)`` if `sample_times` is omitted
            representing the state evolution. The n-th element (along the first
            dimension) represents the state at ``sample_times[n]`` evolved from
            the initial state.

        Warnings
        --------
        This calculation can be relatively inefficient for small systems (very roughly
        speaking, when the dimension of your Hilbert space is less than around 100; the
        exact cutoff depends on the specifics of your problem though). You should generally
        first try using `time_evolution_operators_pwc` to get the full time evolution
        operators (and evolve your state using those), and only switch to this method
        if that approach proves too slow or memory intensive. See the
        `How to simulate quantum dynamics for noiseless systems using graphs`_ user guide
        for an example of calculating state evolution with `time_evolution_operators_pwc`.

        .. _How to simulate quantum dynamics for noiseless systems using graphs:
            https://docs.q-ctrl.com/boulder-opal/user-guides/how-to-simulate-quantum-
            dynamics-for-noiseless-systems-using-graphs

        See Also
        --------
        Graph.density_matrix_evolution_pwc : Corresponding operation for open systems.
        Graph.discretize_stf : Discretize an `Stf` into a `Pwc`.
        Graph.estimated_krylov_subspace_dimension_lanczos :
            Obtain a Krylov subspace dimension to use with this integrator.
        Graph.sparse_pwc_operator : Create `SparsePwc` operators.
        Graph.time_evolution_operators_pwc :
            Unitary time evolution operators for quantum systems with `Pwc` Hamiltonians.

        Notes
        -----
        The Lanczos algorithm calculates the unitary evolution of a state in the Krylov
        subspace. This subspace is spanned by the states resulting from applying the first
        `k` powers of the Hamiltonian on the input state, with `k` being the subspace dimension,
        much smaller that the full Hilbert space dimension. This allows for an efficient
        state propagation in high-dimensional systems compared to calculating the full
        unitary operator.

        Moreover, this function uses sparse matrix multiplication when the Hamiltonian is passed as
        a `SparsePwc`. This can lead to more efficient calculations when they involve large
        operators that are relatively sparse (contain mostly zeros). In this case, the initial state
        is still a densely represented array or tensor.

        Note that increasing the density of `sample_times` does not affect the accuracy of the
        integration. However, increasing the Krylov subspace dimension or subdividing the
        Hamiltonian into shorter piecewise-constant segments can reduce the integration error,
        at the expense of longer computation times.

        Examples
        --------
        See example in the `How to optimize controls on large sparse Hamiltonians
        <https://docs.q-ctrl.com/boulder-opal/user-guides/how-to-optimize-controls-on-
        large-sparse-hamiltonians>`_ user guide.
        """

        dimension = initial_state.shape[-1]
        Checker.VALUE(
            hamiltonian.value_shape == (dimension, dimension),
            "The initial state and the Hamiltonian must have compatible shapes.",
            {
                "hamiltonian dimension": hamiltonian.value_shape,
                "initial_state.shape": initial_state.shape,
            },
        )

        if sample_times is None:
            shape = initial_state.shape
        else:
            duration = np.sum(hamiltonian.durations)
            sample_times = bounded_by(
                sample_times, "sample_times", duration, "the duration of Hamiltonian"
            )
            shape = (len(sample_times),) + initial_state.shape

        operation = create_operation(self.state_evolution_pwc, locals())
        return Tensor(operation, shape=shape)

    @validated
    def estimated_krylov_subspace_dimension_lanczos(
        self,
        spectral_range: Annotated[Union[float, Tensor], pipe(_scalar_float)],
        duration: Annotated[float, pipe(ScalarT.REAL().gt(0))],
        maximum_segment_duration: Annotated[float, pipe(ScalarT.REAL().gt(0))],
        error_tolerance: Annotated[float, pipe(ScalarT.REAL().gt(0))] = 1e-6,
        *,
        name: Optional[str] = None,
    ) -> Tensor:
        r"""
        Calculate an appropriate Krylov subspace dimension (:math:`k`) to use in the Lanczos
        integrator while keeping the total error in the evolution below a given error tolerance.

        Note that you can provide your own estimation of the Hamiltonian spectral range or use the
        `spectral_range` operation to perform that calculation.

        Parameters
        ----------
        spectral_range : float or Tensor
            Estimated order of magnitude of Hamiltonian spectral range (difference
            between largest and smallest eigenvalues).
        duration : float
            The total evolution time.
        maximum_segment_duration : float
            The maximum duration of the piecewise-constant Hamiltonian segments.
        error_tolerance : float, optional
            Tolerance for the error in the integration, defined as the Frobenius norm of
            the vectorial difference between the exact state and the estimated state.
            Defaults to 1e-6.
        name : str or None, optional
            The name of the node.

        Returns
        -------
        Tensor
            Recommended value of :math:`k` to use in a Lanczos integration with a Hamiltonian with a
            similar spectral range to the one passed.

        See Also
        --------
        Graph.spectral_range : Range of the eigenvalues of a Hermitian operator.
        Graph.state_evolution_pwc : Evolve a quantum state.

        Notes
        -----
        To provide the recommended :math:`k` parameter, this function uses the bound
        in the error for the Lanczos algorithm [1]_ [2]_ as an estimate for the error.
        For a single time step this gives

        .. math::
            \mathrm{error} \leq 12 \exp \left( - \frac{(w\tau)^2}{16 k} \right)
            \left (\frac{e w \tau}{ 4 k}  \right )^{k}

        where :math:`\tau` is the time step and :math:`w` is the spectral range of the Hamiltonian.

        As this bound overestimates the error, the actual resulting errors
        with the recommended parameter are expected to be (a few orders of magnitude)
        smaller than the requested tolerance.

        References
        ----------
        .. [1] `N. Del Buono and L. Lopez,
            Lect. Notes Comput. Sci. 2658, 111 (2003).
            <https://doi.org/10.1007/3-540-44862-4_13>`_

        .. [2] `M. Hochbruck and C. Lubich,
            SIAM J. Numer. Anal. 34, 1911 (1997).
            <https://doi.org/10.1137/S0036142995280572>`_

        Examples
        --------
        >>> graph.estimated_krylov_subspace_dimension_lanczos(
        ...     spectral_range=30.0,
        ...     duration=5e-7,
        ...     maximum_segment_duration=2.5e-8,
        ...     error_tolerance=1e-5,
        ...     name="dim",
        ... )
        <Tensor: name="dim", operation_name="estimated_krylov_subspace_dimension_lanczos", shape=()>
        >>> result = bo.execute_graph(graph=graph, output_node_names="dim")
        >>> result["output"]["dim"]["value"]
        2

        See more examples in the `How to optimize controls on large sparse Hamiltonians
        <https://docs.q-ctrl.com/boulder-opal/user-guides/how-to-optimize-controls-on-
        large-sparse-hamiltonians>`_ user guide.
        """

        Checker.VALUE(
            maximum_segment_duration <= duration,
            "The maximum segment duration must be less than or equal to duration.",
            {
                "maximum_segment_duration": maximum_segment_duration,
                "duration": duration,
            },
        )
        operation = create_operation(
            self.estimated_krylov_subspace_dimension_lanczos, locals()
        )
        return Tensor(operation, shape=())

    @validated
    def spectral_range(
        self,
        operator: Annotated[
            Union[Tensor, np.ndarray, spmatrix],
            pipe(shapeable, after=ShapeT.OPERATOR().no_batch()),
        ],
        iteration_count: Annotated[int, pipe(ScalarT.INT().gt(0))] = 3000,
        seed: Optional[Annotated[int, pipe(ScalarT.INT())]] = None,
        *,
        name: Optional[str] = None,
    ) -> Tensor:
        r"""
        Obtain the range of the eigenvalues of a Hermitian operator.

        This function provides an estimate of the difference between the
        highest and the lowest eigenvalues of the operator. You can adjust its
        precision by modifying its default parameters.

        Parameters
        ----------
        operator : np.ndarray or scipy.sparse.spmatrix or Tensor
            The Hermitian operator :math:`M` whose range of eigenvalues you
            want to determine.
        iteration_count : int, optional
            The number of iterations :math:`N` in the calculation. Defaults to
            3000. Choose a higher number to improve the precision, or a smaller
            number to make the estimation run faster.
        seed : int or None, optional
            The random seed that the function uses to choose the initial random
            vector :math:`\left| r \right\rangle`. Defaults to None, which
            means that the function uses a different seed in each run.
        name : str or None, optional
            The name of the node.

        Returns
        -------
        Tensor (scalar, real)
            The difference between the largest and the smallest eigenvalues of
            the operator.

        Warnings
        --------
        This calculation can be expensive, so we recommend that you run it
        before the optimization, if possible. You can do this by using a
        representative or a worst-case operator.

        Notes
        -----
        This function repeatedly multiplies the operator :math:`M` with a
        random vector :math:`\left| r \right\rangle`. In terms of the operator's
        eigenvalues :math:`\{ v_i \}` and eigenvectors
        :math:`\{\left|v_i \right\rangle\}`, the result of :math:`N` matrix
        multiplications is:

        .. math::
            M^N \left|r\right\rangle = \sum_i v_i^N \left|v_i\right\rangle
            \left\langle v_i \right. \left| r \right\rangle.

        For large :math:`N`, the term corresponding to the eigenvalue with
        largest absolute value :math:`V` will dominate the sum, as long as
        :math:`\left|r\right\rangle` has a non-zero overlap with its
        eigenvector. The function then retrieves the eigenvalue :math:`V` via:

        .. math::
            V \approx \frac{\left\langle r \right| M^{2N+1} \left| r
            \right\rangle}{\left\| M^N \left| r \right\rangle \right\|^2}.

        The same procedure applied to the matrix :math:`M-V` allows the function
        to find the eigenvalue at the opposite end of the spectral range.

        Examples
        --------
        >>> operator = np.diag([10, 40])
        >>> graph.spectral_range(operator, name="spectral_range")
        <Tensor: name="spectral_range", operation_name="spectral_range", shape=()>
        >>> result = bo.execute_graph(graph=graph, output_node_names="spectral_range")
        >>> result["output"]["spectral_range"]["value"]
        30.0

        See more examples in the `How to optimize controls on large sparse Hamiltonians
        <https://docs.q-ctrl.com/boulder-opal/user-guides/how-to-optimize-controls-on
        -large-sparse-hamiltonians>`_ user guide.
        """
        is_hermitian = True
        if issparse(operator):
            is_hermitian = np.allclose((operator - operator.getH()).data, 0)  # type: ignore
        elif isinstance(operator, np.ndarray):
            is_hermitian = np.allclose(operator, operator.T.conj())
        Checker.VALUE(is_hermitian, "The Hamiltonian must be Hermitian.")

        operation = create_operation(self.spectral_range, locals())
        return Tensor(operation, shape=())
