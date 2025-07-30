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
    Literal,
    Optional,
    Sequence,
    Tuple,
    Union,
)

import numpy as np
from scipy.sparse import (
    coo_matrix,
    issparse,
    spmatrix,
)

from boulderopal._nodes.base import create_operation
from boulderopal._nodes.validation import (
    ShapeT,
    bounded_by,
    shapeable,
)
from boulderopal._typing import Annotated
from boulderopal._validation import (
    ArrayT,
    Checker,
    ScalarT,
    pipe,
    validated,
)

from .node_data import (
    Pwc,
    SparsePwc,
    Tensor,
)

_LindbladTerms = Sequence[Tuple[float, Union[coo_matrix, Tensor, np.ndarray]]]


def _normalize_lindblad_terms(terms: Any, *, name: str) -> _LindbladTerms:
    """
    Validate types of lindblad_terms and normalize the type for each term.
    """
    Checker.TYPE(
        isinstance(terms, list) and len(terms) >= 0, f"The {name} must not be empty."
    )
    normalized = []
    for index, term in enumerate(terms):
        Checker.VALUE(
            isinstance(term, tuple) and len(term) == 2,
            f"The {name} must be a list of tuples with a decay rate and an operator each.",
            {f"Item {index} of {name}": term},
        )
        rate, op = term
        rate = ScalarT.REAL(f"decay rate in item {index} of {name}").gt(0)(rate)

        op_name = f"operator in item {index} of {name}"
        if isinstance(op, spmatrix):
            op = op.tocoo()
        elif not isinstance(op, Tensor):
            try:
                op = ArrayT.NUMERIC(op_name)(op)
            except TypeError as e:
                raise TypeError(
                    f"The {op_name} must be a NumPy array, or Tensor, or spmatrix."
                ) from e
        op = ShapeT.OPERATOR()(op, name=op_name)

        normalized.append((rate, op))

    return normalized


def _check_hamiltonian_shape(
    hamiltonian: Pwc | SparsePwc, dimension: int, name: str
) -> None:
    """
    Check if Hamiltonian has a compatible `dimension`.
    """
    Checker.VALUE(
        hamiltonian.value_shape == (dimension, dimension),
        f"The dimension of the Hamiltonian must be compatible with the dimension of {name}.",
        {
            "hamiltonian dimension": hamiltonian.value_shape,
            f"dimension of {name}": dimension,
        },
    )


def _check_lindblad_shape(
    lindblad_terms: _LindbladTerms, dimension: int, name: str
) -> None:
    """
    Check if each Lindblad operator has the same `dimension`.
    """
    for index, (_, op) in enumerate(lindblad_terms):
        Checker.VALUE(
            op.shape[0] == dimension,
            f"The dimension of Lindblad operator of item {index} must be compatible "
            f"with the dimension of {name}.",
            {"Lindblad operator shape": op.shape, f"dimension of {name}": dimension},
        )


class OqsGraph:  # pylint: disable=unused-argument
    """
    Base class implementing OQS graph methods.
    """

    @validated
    def density_matrix_evolution_pwc(
        self,
        initial_density_matrix: Annotated[
            Union[np.ndarray, Tensor], pipe(shapeable, after=ShapeT.OPERATOR().batch(1))
        ],
        hamiltonian: Annotated[
            Union[Pwc, SparsePwc], pipe(shapeable, after=ShapeT.OPERATOR().no_batch())
        ],
        lindblad_terms: Annotated[
            Sequence[Tuple[float, Union[np.ndarray, spmatrix, Tensor]]],
            pipe(_normalize_lindblad_terms),
        ],
        sample_times: Optional[
            Annotated[np.ndarray, pipe(ArrayT.REAL().ndim(1).ge(0).ascend())]
        ] = None,
        error_tolerance: Optional[
            Annotated[float, pipe(ScalarT.REAL().le(1e-2))]
        ] = 1e-6,
        *,
        name: Optional[str] = None,
    ) -> Tensor:
        r"""
        Calculate the state evolution of an open system described by the GKS–Lindblad master
        equation.

        The controls that you provide to this function have to be in piecewise-constant
        format. If your controls are smooth sampleable tensor-valued functions (STFs), you
        have to discretize them with `discretize_stf` before passing them to this function.
        You may need to increase the number of segments that you choose for the
        discretization depending on the sizes of oscillations in the smooth controls.

        By default, this function computes an approximate piecewise-constant solution for
        the consideration of efficiency, with the accuracy controlled by the
        parameter `error_tolerance`. If your system is small, you can set the
        `error_tolerance` to None to obtain an exact solution.

        Note that when using the exact method, both `hamiltonian` and `lindblad_terms`
        are converted to the dense representation, regardless of their original formats.
        This means that the computation can be slow and memory intensive when applied to
        large systems.

        When using the approximate method, the sparse representation is used internally if
        `hamiltonian` is a `SparsePwc`, otherwise the dense representation is used.

        Parameters
        ----------
        initial_density_matrix : np.ndarray or Tensor
            A 2D array of the shape ``(D, D)`` representing the initial density matrix of
            the system, :math:`\rho_{\mathrm s}`. You can also pass a batch of density matrices
            and the input data shape must be ``(B, D, D)`` where ``B`` is the batch dimension.
        hamiltonian : Pwc or SparsePwc
            A piecewise-constant function representing the effective system Hamiltonian,
            :math:`H_{\mathrm s}(t)`, for the entire evolution duration.
        lindblad_terms : list[tuple[float, np.ndarray or Tensor or scipy.sparse.spmatrix]]
            A list of pairs, :math:`(\gamma_j, L_j)`, representing the positive decay rate
            :math:`\gamma_j` and the Lindblad operator :math:`L_j` for each coupling
            channel :math:`j`. You must provide at least one Lindblad term.
        sample_times : np.ndarray or None, optional
            A 1D array like object of length :math:`T` specifying the times :math:`\{t_i\}` at
            which this function calculates system states. Must be ordered and contain at least
            one element. Note that increasing the density of sample times does not affect the
            computation precision of this function. If omitted only the evolved density matrix
            at the final time of the system Hamiltonian is returned.
        error_tolerance : float or None, optional
            Defaults to 1e-6. This option enables an approximate method to solve the master
            equation, meaning the 2-norm of the difference between the propagated state and the
            exact solution at the final time (and at each sample time if passed) is within the error
            tolerance. Note that, if set, this value must be smaller than 1e-2 (inclusive).
            However, setting it to a too small value (for example below 1e-12) might result in
            slower computation, but would not further improve the precision, since the dominating
            error in that case is due to floating point error. You can also explicitly set this
            option to None to find the exact piecewise-constant solution. Note that using the
            exact solution can be very computationally demanding in calculations involving a large
            Hilbert space or a large number of segments.
        name : str or None, optional
            The name of the node.

        Returns
        -------
        Tensor
            The time-evolved density matrix, with shape ``(D, D)`` or ``(T, D, D)``,
            depending on whether you provided sample times.
            If you provide a batch of initial states, the shape is
            ``(B, T, D, D)`` or ``(B, D, D)``.

        See Also
        --------
        Graph.jump_trajectory_evolution_pwc :
            Trajectory-based state evolution of an open quantum system.
        Graph.steady_state : Compute the steady state of open quantum system.

        Notes
        -----
        Under the Markovian approximation, the dynamics of an open quantum system can be
        described by the GKS–Lindblad master equation [1]_ [2]_

        .. math::
            \frac{{\mathrm d}\rho_{\mathrm s}(t)}{{\mathrm d}t} =
            -i [H_{\mathrm s}(t), \rho_{\mathrm s}(t)]
            + \sum_j \gamma_j {\mathcal D}[L_j] \rho_{\mathrm s}(t) ,

        where :math:`{\mathcal D}` is a superoperator describing the decoherent process in the
        system evolution and defined as

        .. math::
            {\mathcal D}[X]\rho := X \rho X^\dagger
                - \frac{1}{2}\left( X^\dagger X \rho + \rho X^\dagger X \right)

        for any system operator :math:`X`.

        This function uses sparse matrix multiplication when the Hamiltonian is passed as a
        `SparsePwc` and the Lindblad operators as sparse matrices. This leads to more efficient
        calculations when they involve large operators that are relatively sparse (contain mostly
        zeros). In this case, the initial density matrix is still a densely represented array
        or tensor.

        References
        ----------
        .. [1] `V. Gorini, A. Kossakowski, and E. C. G. Sudarshan,
                J. Math. Phys. 17, 821 (1976).
                <https://doi.org/10.1063/1.522979>`_
        .. [2] `G. Lindblad,
                Commun. Math. Phys. 48, 119 (1976).
                <https://doi.org/10.1007/BF01608499>`_

        Examples
        --------
        Simulate a trivial decay process for a single qubit described by the following
        master equation
        :math:`\dot{\rho} = -i[\sigma_z / 2, \, \rho] + \mathcal{D}[\sigma_-]\rho`.

        >>> duration = 20
        >>> initial_density_matrix = np.array([[0, 0], [0, 1]])
        >>> hamiltonian = graph.constant_pwc_operator(
        ...     duration=duration, operator=graph.pauli_matrix("Z") / 2
        ... )
        >>> lindblad_terms = [(1, graph.pauli_matrix("M"))]
        >>> graph.density_matrix_evolution_pwc(
        ...     initial_density_matrix, hamiltonian, lindblad_terms, name="decay"
        ... )
        <Tensor: name="decay", operation_name="density_matrix_evolution_pwc", shape=(2, 2)>
        >>> result = bo.execute_graph(graph=graph, output_node_names="decay")
        >>> result["output"]["decay"]["value"]
        array([[9.99999998e-01+0.j, 0.00000000e+00+0.j],
               [0.00000000e+00+0.j, 2.06115362e-09+0.j]])

        See more examples in the `How to simulate open system dynamics
        <https://docs.q-ctrl.com/boulder-opal/user-guides/how-to-simulate-open-system-dynamics>`_
        and `How to simulate large open system dynamics
        <https://docs.q-ctrl.com/boulder-opal/user-guides/how-to-simulate-
        large-open-system-dynamics>`_ user guides.
        """

        _shape = initial_density_matrix.shape
        _check_hamiltonian_shape(hamiltonian, _shape[-1], "initial_density_matrix")
        _check_lindblad_shape(lindblad_terms, _shape[-1], "initial_density_matrix")

        if sample_times is None:
            shape = _shape
        else:
            duration = np.sum(hamiltonian.durations)
            sample_times = bounded_by(
                sample_times, "sample_times", duration, "the duration of Hamiltonian"
            )
            shape = _shape[:-2] + (len(sample_times),) + _shape[-2:]
        operation = create_operation(self.density_matrix_evolution_pwc, locals())
        return Tensor(operation, shape=shape)

    @validated
    def jump_trajectory_evolution_pwc(
        self,
        initial_state_vector: Annotated[
            Union[np.ndarray, Tensor], pipe(shapeable, after=ShapeT.VECTOR().batch(1))
        ],
        hamiltonian: Annotated[
            Union[Pwc, SparsePwc], pipe(shapeable, after=ShapeT.OPERATOR().no_batch())
        ],
        lindblad_terms: Annotated[
            Sequence[Tuple[float, Union[np.ndarray, spmatrix, Tensor]]],
            pipe(_normalize_lindblad_terms),
        ],
        max_time_step: Annotated[float, pipe(ScalarT.REAL().gt(0))],
        trajectory_count: Annotated[int, pipe(ScalarT.INT().gt(0))],
        sample_times: Optional[
            Annotated[np.ndarray, pipe(ArrayT.REAL().ndim(1).ge(0).ascend())]
        ] = None,
        seed: Optional[Annotated[int, pipe(ScalarT.INT().ge(0))]] = None,
        *,
        name: Optional[str] = None,
    ) -> Tensor:
        r"""
        Calculate the state evolution of an open system described by the GKS–Lindblad master
        equation using a jump-based trajectory method.

        This function calculates multiple pure-state trajectories starting from an initial pure
        state and returns the average density matrix over all trajectories.

        Note that regardless of their original formats, both `hamiltonian` and `lindblad_terms`
        are internally converted to a dense representation, so there is no computational advantage
        in using a sparse representation with this method.

        Parameters
        ----------
        initial_state_vector : np.ndarray or Tensor
            The initial state vector :math:`|\psi\rangle` as a ``(D,)`` array or Tensor,
            or batch of initial state vectors as a ``(B, D)`` array or Tensor.
        hamiltonian : Pwc or SparsePwc
            A piecewise-constant function representing the system Hamiltonian,
            :math:`H_{\mathrm s}(t)`, for the entire evolution duration,
            with Hilbert space dimension D.
        lindblad_terms : list[tuple[float, np.ndarray or Tensor or scipy.sparse.spmatrix]]
            A list of pairs, :math:`(\gamma_j, L_j)`, representing the positive decay rate
            :math:`\gamma_j` and the Lindblad operator :math:`L_j` for each coupling
            channel :math:`j`. You must provide at least one Lindblad term.
        max_time_step : float
            The maximum time step to use in the integration.
            Each PWC segment will be subdivided into steps that are, at most, this value.
            A smaller value for the maximum time step will more accurately sample the jump
            processes, but also lead to a slower computation.
        trajectory_count : int
            The number of quantum trajectories to run.
        sample_times : np.ndarray or None, optional
            A 1D array like object of length :math:`T` specifying the times :math:`\{t_i\}` at
            which this function calculates system states. Must be ordered and contain at least
            one element. If omitted only the evolved density matrix at the final time of the
            system Hamiltonian is returned. Note that increasing the density of sample times
            does not affect the computation precision of this function, but might slow down
            the calculation.
        seed : int or None, optional
            A seed for the random number generator.
            Defaults to None, in which case a random value for the seed is used.
        name : str, optional
            The name of the node.

        Returns
        -------
        Tensor
            The time-evolved density matrix, with shape ``(D, D)`` or ``(T, D, D)``,
            depending on whether you provided sample times.
            If you provide a batch of initial states, the shape is ``(B, T, D, D)``
            or ``(B, D, D)``.

        See Also
        --------
        Graph.density_matrix_evolution_pwc : State evolution of an open quantum system.
        Graph.steady_state : Compute the steady state of open quantum system.

        Notes
        -----
        Under the Markovian approximation, the dynamics of an open quantum system can be described
        by the GKS–Lindblad master equation [1]_ [2]_

        .. math::
            \frac{{\mathrm d}\rho_{\mathrm s}(t)}{{\mathrm d}t} =
            -i [H_{\mathrm s}(t), \rho_{\mathrm s}(t)]
            + \sum_j \gamma_j {\mathcal D}[L_j] \rho_{\mathrm s}(t) ,

        where :math:`{\mathcal D}` is a superoperator describing the decoherent process in the
        system evolution and defined as

        .. math::
            {\mathcal D}[X]\rho := X \rho X^\dagger
                - \frac{1}{2}\left( X^\dagger X \rho + \rho X^\dagger X \right)

        for any system operator :math:`X`.

        This function solves the GKS–Lindblad master equation with an initial pure state
        :math:`\rho_{\mathrm s}(0) = |\psi\rangle\langle\psi|`, by calculating
        multiple quantum trajectories performing quantum jumps,
        :math:`|\tilde\psi_k(t)\rangle`, and averaging the result:

        .. math::
            \rho(t) = \frac{1}{M} \sum_{k=1}^M |\tilde\psi_k(t) \rangle\langle \tilde\psi_k(t) | .

        References
        ----------
        .. [1] `V. Gorini, A. Kossakowski, and E. C. G. Sudarshan,
                J. Math. Phys. 17, 821 (1976).
                <https://doi.org/10.1063/1.522979>`_
        .. [2] `G. Lindblad,
                Commun. Math. Phys. 48, 119 (1976).
                <https://doi.org/10.1007/BF01608499>`_
        """

        dim = initial_state_vector.shape[-1]
        _check_hamiltonian_shape(hamiltonian, dim, "initial_density_matrix")
        _check_lindblad_shape(lindblad_terms, dim, "initial_density_matrix")

        shape: tuple[int, ...] = (dim, dim)
        if sample_times is not None:
            duration = np.sum(hamiltonian.durations)
            sample_times = bounded_by(
                sample_times, "sample_times", duration, "the duration of Hamiltonian"
            )
            shape = (len(sample_times),) + shape
        if len(initial_state_vector.shape) != 1:
            shape = (initial_state_vector.shape[0],) + shape

        operation = create_operation(self.jump_trajectory_evolution_pwc, locals())
        return Tensor(operation, shape=shape)

    @validated
    def steady_state(
        self,
        hamiltonian: Annotated[
            Union[Tensor, np.ndarray, spmatrix],
            pipe(shapeable, after=ShapeT.OPERATOR().no_batch()),
        ],
        lindblad_terms: Annotated[
            Sequence[Tuple[float, Union[np.ndarray, spmatrix, Tensor]]],
            pipe(_normalize_lindblad_terms),
        ],
        method: Literal["QR", "EIGEN_DENSE", "EIGEN_SPARSE"] = "QR",
        *,
        name: Optional[str] = None,
    ) -> Tensor:
        r"""
        Find the steady state of a time-independent open quantum system.

        The Hamiltonian and Lindblad operators that you provide have to give
        rise to a unique steady state.

        Parameters
        ----------
        hamiltonian : Tensor or spmatrix
            A 2D array of shape ``(D, D)`` representing the time-independent
            Hamiltonian of the system, :math:`H_{\mathrm s}`.
        lindblad_terms : list[tuple[float, np.ndarray or Tensor or scipy.sparse.spmatrix]]
            A list of pairs, :math:`(\gamma_j, L_j)`, representing the positive decay rate
            :math:`\gamma_j` and the Lindblad operator :math:`L_j` for each coupling
            channel :math:`j`. You must provide at least one Lindblad term.
        method : str, optional
            The method used to find the steady state.
            Must be one of "QR", "EIGEN_SPARSE", or "EIGEN_DENSE".
            The "QR" method obtains the steady state through a QR decomposition and is suitable
            for small quantum systems with dense representation.
            The "EIGEN_SPARSE" and "EIGEN_DENSE" methods find the steady state as the eigenvector
            whose eigenvalue is closest to zero, using either a sparse or a dense representation
            of the generator.
            Defaults to "QR".
        name : str or None, optional
            The name of the node.

        Returns
        -------
        Tensor
            The density matrix representing the steady state of the system.

        Warnings
        --------
        This function currently does not support calculating the gradient with respect to its
        inputs. Therefore, it cannot be used in a graph for a `run_optimization` or
        `run_stochastic_optimization` call, which will raise a `RuntimeError`.
        Please use gradient-free optimization if you want to perform an optimization task with this
        function. You can learn more about it in the
        `How to optimize controls using gradient-free optimization
        <https://docs.q-ctrl.com/boulder-opal/user-guides/how-to-optimize-controls-using-
        gradient-free-optimization>`_ user guide.

        See Also
        --------
        Graph.density_matrix_evolution_pwc : State evolution of an open quantum system.
        Graph.jump_trajectory_evolution_pwc :
            Trajectory-based state evolution of an open quantum system.

        Notes
        -----
        Under the Markovian approximation, the dynamics of an open quantum system can be described
        by the GKS–Lindblad master equation [1]_ [2]_,

        .. math::
            \frac{{\mathrm d}\rho_{\mathrm s}(t)}{{\mathrm d}t} =
            {\mathcal L} (\rho_{\mathrm s}(t)) ,

        where the Lindblad superoperator :math:`{\mathcal L}` is defined as

        .. math::
            {\mathcal L} (\rho_{\mathrm s}(t)) = -i [H_{\mathrm s}(t), \rho_{\mathrm s}(t)]
            + \sum_j \gamma_j {\mathcal D}[L_j] \rho_{\mathrm s}(t) ,

        where :math:`{\mathcal D}` is a superoperator describing the decoherent process in the
        system evolution and defined as

        .. math::
            {\mathcal D}[X]\rho := X \rho X^\dagger
                - \frac{1}{2}\left( X^\dagger X \rho + \rho X^\dagger X \right)

        for any system operator :math:`X`.

        This function computes the steady state of :math:`{\mathcal L}` by solving

        .. math:: \frac{{\mathrm d}\rho_{\mathrm s}(t)}{{\mathrm d}t} = 0 .

        The function assumes that :math:`H_{\mathrm s}` is time independent
        and that the dynamics generated by :math:`{\mathcal L}`
        give rise to a unique steady state. That is, the generated quantum dynamical map
        has to be ergodic [3]_.

        References
        ----------
        .. [1] `V. Gorini, A. Kossakowski, and E. C. G. Sudarshan,
                J. Math. Phys. 17, 821 (1976).
                <https://doi.org/10.1063/1.522979>`_
        .. [2] `G. Lindblad,
                Commun. Math. Phys. 48, 119 (1976).
                <https://doi.org/10.1007/BF01608499>`_
        .. [3] `D. Burgarth, G. Chiribella, V. Giovannetti, P. Perinotti, and K. Yuasa,
                New J. Phys. 15 073045 (2013).
                <https://doi.org/10.1088/1367-2630/15/7/073045>`_

        Examples
        --------
        Compute the steady state of the single qubit open system dynamics according to the
        Hamiltonian :math:`H=\omega\sigma_z` and the single Lindblad operator :math:`L=\sigma_-`.

        >>> omega = 0.8
        >>> gamma = 0.5
        >>> hamiltonian = omega * graph.pauli_matrix("Z")
        >>> lindblad_terms = [(gamma, graph.pauli_matrix("M"))]
        >>> graph.steady_state(hamiltonian, lindblad_terms, name="steady_state")
        <Tensor: name="steady_state", operation_name="steady_state", shape=(2, 2)>
        >>> result = bo.execute_graph(graph=graph, output_node_names="steady_state")
        >>> result["output"]["steady_state"]["value"]
        array([[1.+0.j 0.-0.j]
               [0.-0.j 0.-0.j]])
        """

        is_hermitian = True
        if issparse(hamiltonian):
            is_hermitian = np.allclose((hamiltonian - hamiltonian.getH()).data, 0)  # type: ignore
        elif isinstance(hamiltonian, np.ndarray):
            is_hermitian = np.allclose(hamiltonian, hamiltonian.T.conj())
        Checker.VALUE(is_hermitian, "The Hamiltonian must be Hermitian.")
        _check_lindblad_shape(lindblad_terms, hamiltonian.shape[-1], "hamiltonian")
        operation = create_operation(self.steady_state, locals())
        return Tensor(operation, shape=hamiltonian.shape)
