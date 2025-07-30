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

from boulderopal._nodes.base import create_operation
from boulderopal._nodes.validation import (
    ShapeT,
    shapeable,
    starts_with_zero,
)
from boulderopal._typing import Annotated
from boulderopal._validation import (
    ArrayT,
    Checker,
    pipe,
    validated,
)

from .node_data import (
    Pwc,
    Stf,
    Target,
    Tensor,
)
from .utils import get_broadcasted_shape


def _validate_infidelity_input(
    hamiltonian: Pwc | Stf,
    target: Target,
    noise_operators: Optional[list[np.ndarray | Tensor | Pwc | Stf]],
) -> tuple[int, ...]:
    batch_shape = hamiltonian.batch_shape
    value_shape = hamiltonian.value_shape

    Checker.VALUE(
        value_shape == target.value_shape,
        "The Hamiltonian and the target must have the same value shape.",
        {
            "hamiltonian.value_shape": value_shape,
            "target.value_shape": target.value_shape,
        },
    )
    for idx, noise_operator in enumerate(noise_operators or []):
        if isinstance(noise_operator, (Pwc, Stf)):
            noise_operator_batch_shape = noise_operator.batch_shape
            noise_operator_value_shape = noise_operator.value_shape
        else:
            noise_operator_batch_shape = noise_operator.shape[:-2]
            noise_operator_value_shape = noise_operator.shape[-2:]

        Checker.VALUE(
            noise_operator_value_shape == value_shape,
            "The Hamiltonian and the noise operators must have the same value shape.",
            {
                "hamiltonian.value_shape": value_shape,
                f"noise_operators[{idx}] value shape": noise_operator_value_shape,
            },
        )

        batch_shape = get_broadcasted_shape(
            batch_shape,
            noise_operator_batch_shape,
            message="The batch shapes of the Hamiltonian and all noise operators must be "
            "broadcastable.",
        )

    return batch_shape


class InfidelityGraph:  # pylint: disable=unused-argument
    """
    Base class implementing infidelity graph methods.
    """

    @validated
    def target(
        self,
        operator: Annotated[
            Union[np.ndarray, Tensor],
            pipe(shapeable, after=ShapeT.OPERATOR().no_batch()),
        ],
        filter_function_projector: Optional[
            Annotated[
                np.ndarray,
                pipe(ArrayT.NUMERIC().ndim(2).square().hermitian().idempotent()),
            ]
        ] = None,
    ) -> Target:
        r"""
        Create information about the target for system time evolution.

        Nodes created with this function contain two types of information: the
        target gate for the system time evolution, and the projection operator
        that defines the subspace of interest for robustness.

        Parameters
        ----------
        operator : np.ndarray or Tensor
            The target gate :math:`U_\mathrm{target}`. Must be a non-zero partial
            isometry.
        filter_function_projector : np.ndarray or None, optional
            The orthogonal projection matrix :math:`P` onto the subspace used for
            filter function calculations. If you provide a value then it must be
            Hermitian and idempotent. Defaults to the identity matrix.

        Returns
        -------
        Target
            The node containing the specified target information.

        See Also
        --------
        Graph.infidelity_pwc : Total infidelity of a system with a piecewise-constant Hamiltonian.
        Graph.infidelity_stf : Total infidelity of a system with a sampleable Hamiltonian.

        Notes
        -----
        The target gate :math:`U_\mathrm{target}` is a non-zero partial isometry,
        which means that it can be expressed in the form
        :math:`\sum_j \left|\psi_j\right>\left<\phi_j\right|`, where
        :math:`\left\{\left|\psi_j\right>\right\}` and
        :math:`\left\{\left|\phi_j\right>\right\}` both form (non-empty)
        orthonormal, but not necessarily complete, sets. Such a target represents
        a target state :math:`\left|\psi_j\right>` for each initial state
        :math:`\left|\phi_j\right>`. The resulting operational infidelity is 0
        if and only if, up to global phase, each initial state
        :math:`\left|\phi_j\right>` maps exactly to the corresponding final state
        :math:`\left|\psi_j\right>`.

        The filter function projector :math:`P` is an orthogonal projection
        matrix, which means that it satisfies :math:`P=P^\dagger=P^2`. The image
        of :math:`P` defines the set of initial states from which the calculated
        filter function measures robustness.

        Examples
        --------
        Define a target operation for the Pauli :math:`X` gate.

        >>> target_operation = graph.target(operator=np.array([[0, 1], [1, 0]]))
        >>> target_operation
        <Target: operation_name="target", value_shape=(2, 2)>

        See more examples in the `How to optimize controls robust to strong noise sources
        <https://docs.q-ctrl.com/boulder-opal/user-guides/how-to-optimize-controls-robust-
        to-strong-noise-sources>`_ user guide.
        """

        shape = operator.shape

        if isinstance(operator, np.ndarray):
            Checker.VALUE(np.any(operator), "The operator must be non-zero.")
            Checker.VALUE(
                np.allclose(operator @ operator.T.conj() @ operator, operator),
                "The operator must be a partial isometry, but does not yield itself "
                "when multiplied by its adjoint and then itself.",
            )

        if filter_function_projector is not None:
            Checker.VALUE(
                filter_function_projector.shape == shape,
                "The projection operator must have the same dimension as the target operator.",
                {
                    "operator.shape": shape,
                    "filter_function_projector.shape": filter_function_projector.shape,
                },
            )

        operation = create_operation(self.target, locals())
        return Target(operation, value_shape=shape)

    @validated
    def infidelity_pwc(
        self,
        hamiltonian: Annotated[Pwc, pipe(after=ShapeT.OPERATOR())],
        target: Annotated[Target, pipe(after=ShapeT.OPERATOR())],
        noise_operators: Optional[
            List[
                Annotated[
                    Union[np.ndarray, Tensor, Pwc],
                    pipe(shapeable, after=ShapeT.OPERATOR()),
                ]
            ]
        ] = None,
        *,
        name: Optional[str] = None,
    ) -> Tensor:
        r"""
        Create the total infidelity of the given piecewise-constant system.

        Use this function to compute the sum of the operational infidelity (which
        measures how effectively the system achieves a target gate) and filter
        function values (which measure how robust the system evolution is to
        various perturbative noise processes). This total infidelity value
        provides a cost that measures how effectively and robustly a set of
        controls achieves a target operation.

        Note that the total infidelity returned by this function is at least zero,
        but might be larger than one (for example if the system is highly
        sensitive to one of the noise processes).

        Parameters
        ----------
        hamiltonian : Pwc
            The control Hamiltonian :math:`H_{\mathrm c}(t)`. You can provide
            either a single Hamiltonian or a batch of them.
        target : Target
            The object describing the target gate :math:`U_\mathrm{target}` and
            (optionally) the filter function projector :math:`P`. If you
            provide a batch of Hamiltonians, the function uses the same target
            for all the elements in the batch.
        noise_operators : list[np.ndarray or Tensor or Pwc] or None, optional
            The perturbative noise operators :math:`\{N_j(t)\}`. The operators
            in the list can either be single operators or batches of them. If
            any of the noise operators or the Hamiltonian are batches, the batch
            shapes must all be broadcastable. You can omit this list if there are
            no noises.
        name : str or None, optional
            The name of the node.

        Returns
        -------
        Tensor
            The total infidelity (operational infidelity plus filter function
            values) of the given system, with respect to the given target gate.
            If you provide a batch of Hamiltonians or noise operators, the
            function returns a batch of infidelities containing one infidelity
            for each Hamiltonian and list of noise operators in the input batches.

        Warnings
        --------
        The Hessian matrix cannot currently be calculated for a graph which includes
        an `infidelity_pwc` node if the `hamiltonian` has degenerate eigenvalues at
        any segment.

        See Also
        --------
        Graph.infidelity_stf : Corresponding operation for `Stf` Hamiltonians.
        Graph.target : Define the target operation of the time evolution.
        Graph.time_evolution_operators_pwc : Unitary time evolution operators
            for quantum systems with `Pwc` Hamiltonians.

        Notes
        -----
        The total system Hamiltonian is

        .. math:: H_{\mathrm c}(t) + \sum_j \beta_j(t) N_j(t),

        where :math:`\{\beta_j(t)\}` are small, dimensionless, stochastic
        variables.

        The total infidelity, as represented by this node, is the sum of the
        operational infidelity :math:`\mathcal{I}` and the filter functions
        :math:`\{F_j(0)\}` of each noise operator evaluated at zero frequency.

        The operational infidelity is

        .. math::
          \mathcal{I} = 1-\left|
            \frac{\mathrm{Tr} \left(U_\mathrm{target}^\dagger U(t)\right)}
            {\mathrm{Tr} \left(U_\mathrm{target}^\dagger U_\mathrm{target}\right)}
            \right|^2,

        where :math:`U(t)` is the unitary time evolution operator due to
        :math:`H_{\mathrm c}(t)`.

        The filter function for the noise operator :math:`N_j(t)` is a measure of
        robustness, defined at frequency :math:`f` as

        .. math::
          F_j(f) = \frac{1}{\mathrm{Tr}(P)} \mathrm{Tr} \left( P
            \mathcal{F} \left\{ \tilde N_j^\prime(t) \right\} \left[ \mathcal{F}
            \left\{ \tilde N^\prime (t) \right\} \right]^\dagger P \right),

        where :math:`\mathcal{F}` is the Fourier transform,
        :math:`\tilde N_j(t) \equiv U_c^\dagger(t) N_j(t) U_c(t)` is the
        toggling-frame noise operator, and
        :math:`\tilde N_j^\prime(t)\equiv
        \tilde N_j(t)-
        \frac{\mathrm{Tr}(P\tilde N_j(t)P)}{\mathrm{Tr}(P)} \mathbb{I}`
        differs from :math:`\tilde N_j(t)` only by a multiple of the identity but
        is trace-free on the subspace of interest. The filter function value at
        zero frequency quantifies the sensitivity of the controls to quasi-static
        noise applied via the corresponding noise operator.

        Examples
        --------
        Calculate infidelity of the identity gate for a noiseless single qubit.

        >>> sigma_z = np.array([[1, 0], [0, -1]])
        >>> hamiltonian = graph.pwc(
        ...     durations=np.array([0.1, 0.1]), values=np.array([sigma_z, -sigma_z])
        ... )
        >>> target = graph.target(np.eye(2))
        >>> infidelity = graph.infidelity_pwc(
        ...     hamiltonian=hamiltonian, target=target, name="infidelity"
        ... )
        >>> result = bo.execute_graph(graph=graph, output_node_names="infidelity")
        >>> result["output"]["infidelity"]["value"]
        0.0

        See more examples in the `How to optimize controls with non-linear dependencies
        <https://docs.q-ctrl.com/boulder-opal/user-guides/how-to-optimize-controls-
        with-nonlinear-dependences>`_ user guide.
        """

        shape = _validate_infidelity_input(hamiltonian, target, noise_operators)

        operation = create_operation(self.infidelity_pwc, locals())
        return Tensor(operation, shape=shape)

    @validated
    def infidelity_stf(
        self,
        sample_times: Annotated[
            np.ndarray,
            pipe(ArrayT.REAL().ndim(1).ge(0).ascend(), after=starts_with_zero),
        ],
        hamiltonian: Annotated[Stf, pipe(after=ShapeT.OPERATOR())],
        target: Annotated[Target, pipe(after=ShapeT.OPERATOR())],
        noise_operators: Optional[
            List[
                Annotated[
                    Union[np.ndarray, Tensor, Stf],
                    pipe(shapeable, after=ShapeT.OPERATOR()),
                ]
            ]
        ] = None,
        *,
        name: Optional[str] = None,
    ) -> Tensor:
        r"""
        Create the total infidelity of a given system with a sampleable Hamiltonian.

        See :obj:`infidelity_pwc` for information about the total infidelity
        created by this function.

        Parameters
        ----------
        sample_times : np.ndarray(1D, real)
            The times at which the Hamiltonian and noise operators (if present) should be sampled
            for the integration. Must start with 0, be ordered, and contain at least one element.
        hamiltonian : Stf
            The control Hamiltonian :math:`H_{\mathrm c}(t)`. You can provide
            either a single Hamiltonian or a batch of them.
        target : Target
            The object describing the target gate :math:`U_\mathrm{target}` and
            (optionally) the filter function projector :math:`P`. If you
            provide a batch of Hamiltonians, the function uses the same target
            for all the elements in the batch.
        noise_operators : list[np.ndarray or Tensor or Stf] or None, optional
            The perturbative noise operators :math:`\{N_j(t)\}`. The operators
            in the list can either be single operators or batches of them. If
            any of the noise operators or the Hamiltonian are batches, the batch
            shapes must all be broadcastable. You can omit this list if there are
            no noises.
        name : str or None, optional
            The name of the node.

        Returns
        -------
        Tensor
            The total infidelity (operational infidelity plus filter function
            values) of the given system, with respect to the given target gate,
            at the last time in `sample_times`.
            If you provide a batch of Hamiltonians or noise operators, the
            function returns a batch of infidelities containing one infidelity
            for each Hamiltonian and list of noise operators in the input batches.

        See Also
        --------
        Graph.infidelity_pwc : Corresponding operation for `Pwc` Hamiltonians.
        Graph.target : Define the target operation of the time evolution.
        Graph.time_evolution_operators_stf : Unitary time evolution operators
            for quantum systems with `Stf` Hamiltonians.

        Examples
        --------
        Calculate the infidelity of the Pauli :math:`X` gate for a noiseless qubit.

        >>> sigma_x = np.array([[0, 1], [1, 0]])
        >>> hamiltonian = graph.constant_stf_operator(np.pi * sigma_x / 2)
        >>> target = graph.target(sigma_x)
        >>> infidelity = graph.infidelity_stf(
        ...     sample_times=np.linspace(0, 0.5, 100),
        ...     hamiltonian=hamiltonian,
        ...     target=target,
        ...     name="infidelity",
        ... )
        >>> result = bo.execute_graph(graph=graph, output_node_names="infidelity")
        >>> result["output"]["infidelity"]["value"]
        0.5000000000260991
        """
        shape = _validate_infidelity_input(hamiltonian, target, noise_operators)

        operation = create_operation(self.infidelity_stf, locals())
        return Tensor(operation, shape=shape)
