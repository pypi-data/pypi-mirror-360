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

from collections import namedtuple
from typing import (
    Any,
    Callable,
    Optional,
    Union,
)

import numpy as np

from boulderopal._nodes.node_data import Pwc
from boulderopal._validation import (
    ArrayT,
    Checker,
    ScalarT,
    nullable,
)
from boulderopal.graph import (
    Graph,
    execute_graph,
)
from boulderopal.optimization import run_optimization
from boulderopal.superconducting._components import (
    Cavity,
    CavityCavityInteraction,
    Coefficient,
    Transmon,
    TransmonCavityInteraction,
    TransmonTransmonInteraction,
    validate_real_coefficient,
)
from boulderopal.superconducting._drives import (
    ComplexOptimizableConstant,
    ComplexOptimizableSignal,
    RealOptimizableConstant,
    RealOptimizableSignal,
)

Interaction = Union[
    TransmonTransmonInteraction, TransmonCavityInteraction, CavityCavityInteraction
]

_QHOOps = namedtuple("_QHOOps", ["a", "adag", "n"])


def _create_qho_operators(
    graph: Graph, transmons: list[Transmon], cavities: list[Cavity]
) -> dict[str, _QHOOps]:
    """
    Create the creation, annihilation, and number operators for transmons and cavities.

    This function returns a dictionary whose keys are the subsystem names and whose values are
    _QHOOps named tuples (with field names a, adag, and n) with the operators of each subsystem.
    """
    systems = transmons + cavities
    dimensions = [system.dimension for system in systems]
    return {
        system.name: _QHOOps(
            graph.embed_operators(
                (graph.annihilation_operator(system.dimension), idx), dimensions
            ),
            graph.embed_operators(
                (graph.creation_operator(system.dimension), idx), dimensions
            ),
            graph.embed_operators(
                (graph.number_operator(system.dimension), idx), dimensions
            ),
        )
        for idx, system in enumerate(systems)
    }


def _validate_physical_system_inputs(
    transmons: list[Transmon], cavities: list[Cavity], interactions: list[Interaction]
) -> tuple[
    list[TransmonTransmonInteraction],
    list[TransmonCavityInteraction],
    list[CavityCavityInteraction],
]:
    """
    Validate the type of the subsystems and interactions,
    and the subsystem names in the interactions.

    This function returns three lists containing
    (1) all the transmon-transmon interactions,
    (2) all the transmon-cavity interactions, and
    (3) all the cavity-cavity interactions.
    """

    Checker.VALUE(
        len(transmons) + len(cavities) > 0,
        "At least one transmon or cavity must be provided.",
        {"transmons": transmons, "cavities": cavities},
    )

    Checker.TYPE(
        all(isinstance(transmon, Transmon) for transmon in transmons),
        "Each element in transmons must be a Transmon object.",
        {"transmons": transmons},
    )
    transmon_names = [transmon.name for transmon in transmons]
    Checker.VALUE(
        len(transmon_names) == len(set(transmon_names)),
        "Transmon names must be unique.",
        {"transmon names": transmon_names},
    )

    Checker.TYPE(
        all(isinstance(cavity, Cavity) for cavity in cavities),
        "Each element in cavities must be a Cavity object.",
        {"cavities": cavities},
    )
    cavity_names = [cavity.name for cavity in cavities]
    Checker.VALUE(
        len(cavity_names) == len(set(cavity_names)),
        "Cavity names must be unique.",
        {"cavity names": cavity_names},
    )

    Checker.VALUE(
        len(transmon_names + cavity_names) == len(set(transmon_names + cavity_names)),
        "Transmon and cavity names must be unique.",
        {"transmon names": transmon_names, "cavity names": cavity_names},
    )

    transmon_transmon_interactions = [
        intx for intx in interactions if isinstance(intx, TransmonTransmonInteraction)
    ]
    transmon_cavity_interactions = [
        intx for intx in interactions if isinstance(intx, TransmonCavityInteraction)
    ]
    cavity_cavity_interactions = [
        intx for intx in interactions if isinstance(intx, CavityCavityInteraction)
    ]
    Checker.VALUE(
        len(transmon_transmon_interactions)
        + len(transmon_cavity_interactions)
        + len(cavity_cavity_interactions)
        == len(interactions),
        "Each element in interactions must be a TransmonTransmonInteraction, "
        "a TransmonCavityInteraction, or a CavityCavityInteraction object.",
        {"interactions": interactions},
    )

    tt_interaction_name_pairs = set(
        frozenset(tt_interaction.transmon_names)
        for tt_interaction in transmon_transmon_interactions
    )
    Checker.VALUE(
        len(tt_interaction_name_pairs) == len(transmon_transmon_interactions),
        "There are duplicate names in the transmon-transmon interaction terms.",
        {"interactions": interactions},
    )

    for tt_interaction in transmon_transmon_interactions:
        name_1, name_2 = tt_interaction.transmon_names
        Checker.VALUE(
            name_1 in transmon_names and name_2 in transmon_names,
            "Names in transmon-transmon interaction terms must refer to transmons in the system.",
            {"transmon names": transmon_names},
        )

    tc_interaction_name_pairs = set(
        (tc_interaction.transmon_name, tc_interaction.cavity_name)
        for tc_interaction in transmon_cavity_interactions
    )
    Checker.VALUE(
        len(tc_interaction_name_pairs) == len(transmon_cavity_interactions),
        "There are duplicate names in the transmon-cavity interaction terms.",
        {"interactions": interactions},
    )

    for tc_interaction in transmon_cavity_interactions:
        Checker.VALUE(
            tc_interaction.transmon_name in transmon_names,
            "Transmon names in transmon-cavity interaction terms "
            "must refer to transmons in the system.",
            {"transmon names": transmon_names},
        )
        Checker.VALUE(
            tc_interaction.cavity_name in cavity_names,
            "Cavity names in transmon-cavity interaction terms "
            "must refer to cavities in the system.",
            {"cavity names": cavity_names},
        )

    cc_interaction_name_pairs = set(
        frozenset(cc_interaction.cavity_names)
        for cc_interaction in cavity_cavity_interactions
    )
    Checker.VALUE(
        len(cc_interaction_name_pairs) == len(cavity_cavity_interactions),
        "There are duplicate names in the cavity-cavity interaction terms.",
        {"interactions": interactions},
    )

    for cc_interaction in cavity_cavity_interactions:
        name_1, name_2 = cc_interaction.cavity_names
        Checker.VALUE(
            name_1 in cavity_names and name_2 in cavity_names,
            "Names in cavity-cavity interaction terms must refer to cavities in the system.",
            {"cavity names": cavity_names},
        )

    return (
        transmon_transmon_interactions,
        transmon_cavity_interactions,
        cavity_cavity_interactions,
    )


def _convert_to_pwc(
    graph: Graph,
    coefficient: Coefficient,
    real_valued: bool,
    name: str,
    filter_signal: Optional[Callable],
    gate_duration: float,
    optimizable_node_names: list,
) -> Pwc:
    """
    Return the Pwc representation of a coefficient.

    This function has a side effect to mutate `optimizable_node_names` list as
    it iterates over the coefficient parameter.
    """

    # This is to double check we pass the real coefficient when needed.
    # Also note this is done by checking whether the corresponding Hamiltonian part
    # is Hermitian or not, which is due to the format of the Hamiltonian and the process of how
    # we build the Hamiltonian from user input.
    if real_valued:
        coefficient = validate_real_coefficient(coefficient, name)

    # Convert array into Pwc.
    if isinstance(coefficient, np.ndarray):
        return graph.pwc_signal(coefficient, gate_duration, name=name)

    # Convert Real/ComplexOptimizableConstant into optimizable constant Pwc.
    if isinstance(coefficient, (RealOptimizableConstant, ComplexOptimizableConstant)):
        optimizable_node_names.append(name)
        return coefficient.get_pwc(graph, gate_duration, name)

    # Convert Real/ComplexOptimizableSignal into optimizable Pwc.
    if isinstance(coefficient, (RealOptimizableSignal, ComplexOptimizableSignal)):
        optimizable_node_names.append(name)
        signal = coefficient.get_pwc(graph, gate_duration, name)
        if filter_signal is None:
            return signal
        optimizable_node_names.append(f"{name}_filtered")
        return filter_signal(signal, name)

    return graph.constant_pwc(
        constant=graph.tensor(coefficient, name=name), duration=gate_duration
    )


def _create_superconducting_hamiltonian(
    graph: Graph,
    transmons: list[Transmon],
    cavities: list[Cavity],
    interactions: list[Interaction],
    gate_duration: float,
    cutoff_frequency: Optional[float],
    sample_count: int,
) -> tuple[Pwc, list[str]]:
    """
    Create the Hamiltonian of a system composed of transmons and cavities.

    This function returns the Hamiltonian as a Pwc node and a list with the names of
    the optimizable nodes that have been added to the graph. If some of these are PWC functions
    and `cutoff_frequency` is not None, then the names of the filtered PWC nodes are also included.
    """

    (
        transmon_transmon_interactions,
        transmon_cavity_interactions,
        cavity_cavity_interactions,
    ) = _validate_physical_system_inputs(transmons, cavities, interactions)

    # Define annihilation and creation operators for the transmon and the cavity.
    operators = _create_qho_operators(graph, transmons, cavities)

    # Create nested dictionary structure containing information for the different Hamiltonian terms.
    hamiltonian_info: dict[str, Any] = {}

    # Add transmon terms.
    for transmon in transmons:
        transmon_ops = operators[transmon.name]
        hamiltonian_info[f"{transmon.name}.frequency"] = {
            "coefficient": transmon.frequency,
            "operator": transmon_ops.n,
            "is_hermitian": True,
        }
        hamiltonian_info[f"{transmon.name}.anharmonicity"] = {
            "coefficient": transmon.anharmonicity,
            "operator": 0.5 * (transmon_ops.n @ transmon_ops.n - transmon_ops.n),
            "is_hermitian": True,
        }
        hamiltonian_info[f"{transmon.name}.drive"] = {
            "coefficient": transmon.drive,
            "operator": transmon_ops.adag,
            "is_hermitian": False,
        }

    # Add cavity terms.
    for cavity in cavities:
        cavity_ops = operators[cavity.name]
        hamiltonian_info[f"{cavity.name}.frequency"] = {
            "coefficient": cavity.frequency,
            "operator": cavity_ops.n,
            "is_hermitian": True,
        }
        hamiltonian_info[f"{cavity.name}.kerr_coefficient"] = {
            "coefficient": cavity.kerr_coefficient,
            "operator": 0.5 * (cavity_ops.n @ cavity_ops.n - cavity_ops.n),
            "is_hermitian": True,
        }
        hamiltonian_info[f"{cavity.name}.drive"] = {
            "coefficient": cavity.drive,
            "operator": cavity_ops.adag,
            "is_hermitian": False,
        }

    # Add transmon-transmon interaction terms.
    for tt_interaction in transmon_transmon_interactions:
        name_1, name_2 = tt_interaction.transmon_names
        transmon_1_ops = operators[name_1]
        transmon_2_ops = operators[name_2]
        key = f"{name_1}_{name_2}_interaction"
        hamiltonian_info[f"{key}.effective_coupling"] = {
            "coefficient": tt_interaction.effective_coupling,
            "operator": 2 * transmon_1_ops.a @ transmon_2_ops.adag,
            "is_hermitian": False,
        }

    # Add transmon-cavity interaction terms.
    for tc_interaction in transmon_cavity_interactions:
        transmon_ops = operators[tc_interaction.transmon_name]
        cavity_ops = operators[tc_interaction.cavity_name]
        key = f"{tc_interaction.transmon_name}_{tc_interaction.cavity_name}_interaction"
        hamiltonian_info[f"{key}.dispersive_shift"] = {
            "coefficient": tc_interaction.dispersive_shift,
            "operator": transmon_ops.n @ cavity_ops.n,
            "is_hermitian": True,
        }
        hamiltonian_info[f"{key}.rabi_coupling"] = {
            "coefficient": tc_interaction.rabi_coupling,
            "operator": 2 * transmon_ops.adag @ cavity_ops.a,
            "is_hermitian": False,
        }

    # Add cavity-cavity interaction terms.
    for cc_interaction in cavity_cavity_interactions:
        name_1, name_2 = cc_interaction.cavity_names
        cavity_1_ops = operators[name_1]
        cavity_2_ops = operators[name_2]
        key = f"{name_1}_{name_2}_interaction"
        hamiltonian_info[f"{key}.cross_kerr_coefficient"] = {
            "coefficient": cc_interaction.cross_kerr_coefficient,
            "operator": cavity_1_ops.n @ cavity_2_ops.n,
            "is_hermitian": True,
        }

    Checker.VALUE(
        any(np.any(info["coefficient"]) for info in hamiltonian_info.values()),
        "The system must contain at least one Hamiltonian coefficient.",
        {"transmons": transmons, "cavities": cavities, "interactions": interactions},
    )

    # Create kernel to filter signals (used in convert_to_pwc).
    if cutoff_frequency is not None:
        kernel = graph.sinc_convolution_kernel(cutoff_frequency)
        _filter = lambda x, y: graph.discretize_stf(  # pylint: disable=unnecessary-lambda-assignment
            stf=graph.convolve_pwc(pwc=x, kernel=kernel),
            duration=gate_duration,
            segment_count=sample_count,
            name=f"{y}_filtered",
        )
    else:
        _filter = None

    # Build the Hamiltonian from the different terms.
    hamiltonian_terms = []
    optimizable_node_names: list[str] = []  # filled up by convert_to_pwc

    for name, info in hamiltonian_info.items():
        if info["coefficient"] is not None:
            coefficient = _convert_to_pwc(
                graph=graph,
                coefficient=info["coefficient"],
                real_valued=info["is_hermitian"],
                name=name,
                filter_signal=_filter,
                gate_duration=gate_duration,
                optimizable_node_names=optimizable_node_names,
            )
            if info["is_hermitian"]:
                hamiltonian_terms.append(coefficient * info["operator"])
            else:
                hamiltonian_terms.append(0.5 * coefficient * info["operator"])
                hamiltonian_terms.append(
                    0.5 * graph.conjugate(coefficient) * graph.adjoint(info["operator"])
                )

    return graph.pwc_sum(hamiltonian_terms), optimizable_node_names


def simulate(
    transmons: list[Transmon],
    cavities: list[Cavity],
    interactions: list[Interaction],
    gate_duration: float,
    sample_count: int = 128,
    cutoff_frequency: Optional[float] = None,
    initial_state: Optional[np.ndarray] = None,
) -> dict:
    """
    Simulate a system composed of transmons and cavities.

    This function builds a graph describing the Hamiltonian (see the note part for details) of a
    superconducting system, and calls :func:`~boulderopal.execute_graph` to simulate its dynamics.

    Parameters
    ----------
    transmons : list[Transmon]
        List of objects containing the physical information about the transmons.
        It must not contain any optimizable coefficients.
        It can be an empty list, but at least one transmon or cavity must be provided.
    cavities : list[Cavity]
        List of objects containing the physical information about the cavities.
        They must not contain any optimizable coefficients.
        It can be an empty list, but at least one transmon or cavity must be provided.
    interactions : list[TransmonTransmonInteraction or TransmonCavityInteraction or \
            CavityCavityInteraction]
        List of objects containing the physical information about the interactions in the system.
        They must not contain any optimizable coefficients.
        It can be an empty list.
    gate_duration : float
        The duration of the gate to be simulated, :math:`t_\\mathrm{gate}`.
        It must be greater than zero.
    sample_count : int, optional
        The number of times between 0 and `gate_duration` (included)
        at which the evolution is sampled.
        Defaults to 128.
    cutoff_frequency : float or None, optional
        The cutoff frequency of a linear sinc filter to be applied to the piecewise-constant
        signals you provide for the coefficients. If not provided, the signals are not filtered.
        If the signals are filtered, a larger sample count leads to a more accurate numerical
        integration. If the signals are not filtered, the sample count has no effect on the
        numerical precision of the integration.
    initial_state : np.ndarray or None, optional
        The initial state of the system, :math:`|\\Psi_\\mathrm{initial}\\rangle`, as a 1D array of
        length ``D = np.prod([system.dimension for system in transmons + cavities])``.
        If not provided, the function only returns the system's unitary time-evolution operators.

    Returns
    -------
    dict
        The result of the `execute_graph` call.
        Its ``output`` item is a dictionary containing information about
        the evolution of the system, with the following keys:

            ``sample_times``
                The times at which the system's evolution is sampled,
                as an array of shape ``(T,)``.
            ``unitaries``
                The system's unitary time-evolution operators at each sample time,
                as an array of shape ``(T, D, D)``.
            ``state_evolution``
                The time evolution of the initial state at each sample time,
                as an array of shape ``(T, D)``.
                This is only returned if you provide an initial state.

    See Also
    --------
    :func:`boulderopal.superconducting.optimize` :
        Find optimal pulses or parameters for a system composed of transmons and cavities.

    Notes
    -----
    The Hamiltonian of the system is of the form

    .. math::
        H = \\sum_i H_{\\mathrm{transmon}_i}
            + \\sum_i H_{\\mathrm{cavity}_i}
            + \\sum_{i,j} H_{\\mathrm{transmon}_i-\\mathrm{transmon}_j}
            + \\sum_{i,j} H_{\\mathrm{transmon}_i-\\mathrm{cavity}_j}
            + \\sum_{i,j} H_{\\mathrm{cavity}_i-\\mathrm{cavity}_j}

    where i and j mark the i-th and j-th transmon or cavity.
    For their definition of each Hamiltonian term, see its respective class.

    The Hilbert space of the system is defined as the outer product of all the
    transmon Hilbert spaces (in the order they're provided in `transmons`) with
    the cavity Hilbert spaces (in the order they're provided in `cavities`), that is:

    .. math::
        \\mathcal{H} =
            \\mathcal{H}_{\\mathrm{transmon}_1} \\otimes \\mathcal{H}_{\\mathrm{transmon}_2}
            \\otimes \\ldots
            \\otimes \\mathcal{H}_{\\mathrm{cavity}_1} \\otimes \\mathcal{H}_{\\mathrm{cavity}_2}
            \\otimes \\ldots

    The system dimension `D` is then the product of all transmon and cavity dimensions.
    """
    gate_duration = ScalarT.REAL("gate_duration").gt(0)(gate_duration)
    sample_count = ScalarT.INT("sample_count").gt(0)(sample_count)
    cutoff_frequency = nullable(ScalarT.REAL("cutoff_frequency"), cutoff_frequency)

    system_dimension = np.prod(
        [system.dimension for system in transmons + cavities], dtype=int
    )
    initial_state = nullable(
        ArrayT.COMPLEX("initial_state").ndim(1).shape((system_dimension,)),
        initial_state,
    )

    graph = Graph()

    # Create PWC Hamiltonian.
    hamiltonian, optimizable_node_names = _create_superconducting_hamiltonian(
        graph=graph,
        transmons=transmons,
        cavities=cavities,
        interactions=interactions,
        gate_duration=gate_duration,
        cutoff_frequency=cutoff_frequency,
        sample_count=sample_count,
    )

    # Check whether there are any optimizable coefficients.
    Checker.VALUE(
        len(optimizable_node_names) == 0,
        "None of the Hamiltonian terms can be optimizable.",
        {"transmons": transmons, "cavities": cavities, "interactions": interactions},
    )

    # Calculate the evolution.
    sample_times = np.linspace(0.0, gate_duration, sample_count)
    graph.tensor(sample_times, name="sample_times")
    unitaries = graph.time_evolution_operators_pwc(
        hamiltonian=hamiltonian, sample_times=sample_times, name="unitaries"
    )

    output_node_names = ["unitaries", "sample_times"]

    if initial_state is not None:
        states = unitaries @ initial_state[:, None]
        states = states[..., 0]
        states.name = "state_evolution"
        output_node_names.append("state_evolution")

    return execute_graph(graph=graph, output_node_names=output_node_names)


def optimize(
    transmons: list[Transmon],
    cavities: list[Cavity],
    interactions: list[Interaction],
    gate_duration: float,
    initial_state: Optional[np.ndarray] = None,
    target_state: Optional[np.ndarray] = None,
    target_operation: Optional[np.ndarray] = None,
    sample_count: int = 128,
    cutoff_frequency: Optional[float] = None,
    **optimization_kwargs: Any,
) -> dict[str, Any]:
    """
    Find optimal pulses or parameters for a system composed of transmons and cavities,
    in order to achieve a target state or implement a target operation.

    At least one of the terms in the `transmons`, `cavities`, or `interactions` arguments
    must be optimizable.

    To optimize a state transfer, you need to provide an initial and a target state.
    To optimize a target gate/unitary, you need to provide a target operation.

    This function builds a graph describing the Hamiltonian (see the note part for details) of a
    superconducting system, and calls :func:`~boulderopal.run_optimization` to
    to perform the optimization task.

    Parameters
    ----------
    transmons : list[Transmon]
        List of objects containing the physical information about the transmons.
        It can be an empty list, but at least one transmon or cavity must be provided.
    cavities : list[Cavity]
        List of objects containing the physical information about the cavities.
        It can be an empty list, but at least one transmon or cavity must be provided.
    interactions : list[TransmonTransmonInteraction or TransmonCavityInteraction or \
            CavityCavityInteraction]
        List of objects containing the physical information about the interactions in the system.
        It can be an empty list.
    gate_duration : float
        The duration of the gate to be optimized, :math:`t_\\mathrm{gate}`.
        It must be greater than zero.
    initial_state : np.ndarray or None, optional
        The initial state of the system, :math:`|\\Psi_\\mathrm{initial}\\rangle`, as a 1D array of
        length ``D = np.prod([system.dimension for system in transmon + cavities])``.
        If provided, the function also returns its time evolution.
        This is a required parameter if you pass a `target_state`.
    target_state : np.ndarray or None, optional
        The target state of the optimization, :math:`|\\Psi_\\mathrm{target}\\rangle`,
        as a 1D array of length `D`.
        You must provide exactly one of `target_state` or `target_operation`.
    target_operation : np.ndarray or None, optional
        The target operation of the optimization, :math:`U_\\mathrm{target}`,
        as a 2D array of shape ``(D, D)``.
        You must provide exactly one of `target_state` or `target_operation`.
    sample_count : int, optional
        The number of times between 0 and `gate_duration` (included)
        at which the evolution is sampled.
        Defaults to 128.
    cutoff_frequency : float or None, optional
        The cutoff frequency of a linear sinc filter to be applied to the piecewise-constant
        signals you provide for the coefficients. If not provided, the signals are not filtered.
        If the signals are filtered, a larger sample count leads to a more accurate numerical
        integration. If the signals are not filtered, the sample count has no effect on the
        numerical precision of the integration.
    **optimization_kwargs : dict
        Additional parameters to pass to boulderopal.run_optimization.

    Returns
    -------
    dict
        The result of the `run_optimization` call.
        Its ``output`` item is a dictionary containing the optimized coefficients and information
        about the time evolution of the system, with the following keys:

            optimized coefficients
                These are the names of the requested optimized Hamiltonian coefficients, under
                keys such as ``[transmon_1_name].drive``, ``[cavity_2_name].frequency``,
                ``[transmon_2_name]_[cavity_1_name]_interaction.dispersive_shift``, and
                ``[cavity_1_name]_[cavity_2_name]_interaction.cross_kerr_coefficient`` (where
                ``[transmon_n_name]`` and  ``[cavity_n_name]`` are the names assigned to the
                respective transmons or cavities).
                If you pass a `cutoff_frequency`, the filtered versions of the
                piecewise-constant coefficients are also included with keys such as
                ``[transmon_2_name].drive_filtered``.
            ``infidelity``
                The state/operational infidelity of the optimized evolution.
            ``sample_times``
                The times at which the system's evolution is sampled,
                as an array of shape ``(T,)``.
            ``unitaries``
                The system's unitary time-evolution operators at each sample time,
                as an array of shape ``(T, D, D)``.
            ``state_evolution``
                The time evolution of the initial state at each sample time,
                as an array of shape ``(T, D)``.
                This is only returned if you provide an initial state.

    See Also
    --------
    :func:`boulderopal.superconducting.simulate` :
        Simulate a system composed of transmons and cavities.

    Notes
    -----
    The Hamiltonian of the system is of the form

    .. math::
        H = \\sum_i H_{\\mathrm{transmon}_i}
            + \\sum_i H_{\\mathrm{cavity}_i}
            + \\sum_{i,j} H_{\\mathrm{transmon}_i-\\mathrm{transmon}_j}
            + \\sum_{i,j} H_{\\mathrm{transmon}_i-\\mathrm{cavity}_j}
            + \\sum_{i,j} H_{\\mathrm{cavity}_i-\\mathrm{cavity}_j}

    where i and j mark the i-th and j-th transmon or cavity.
    For their definition of each Hamiltonian term, see its respective class.

    The Hilbert space of the system is defined as the outer product of all the
    transmon Hilbert spaces (in the order they're provided in `transmons`) with
    the cavity Hilbert spaces (in the order they're provided in `cavities`), that is:

    .. math::
        \\mathcal{H} =
            \\mathcal{H}_{\\mathrm{transmon}_1} \\otimes \\mathcal{H}_{\\mathrm{transmon}_2}
            \\otimes \\ldots
            \\otimes \\mathcal{H}_{\\mathrm{cavity}_1} \\otimes \\mathcal{H}_{\\mathrm{cavity}_2}
            \\otimes \\ldots

    The system dimension `D` is then the product of all transmon and cavity dimensions.

    If you provide an `initial_state` and a `target_state`, the optimization cost is defined as the
    infidelity of the state transfer process,

    .. math::
        \\mathcal{I}
            = 1 - \\left|
                \\langle
                    \\Psi_\\mathrm{target} | U(t_\\mathrm{gate}) | \\Psi_\\mathrm{initial}
                \\rangle
            \\right|^2 ,

    where :math:`U(t)` is the unitary time-evolution operator generated by the Hamiltonian.

    If you provide a `target_operation`, the optimization cost is defined as the operational
    infidelity,

    .. math::
        \\mathcal{I}
            = 1 - \\left| \\frac
                {\\mathrm{Tr} (U_\\mathrm{target}^\\dagger U(t_\\mathrm{gate}))}
                {\\mathrm{Tr} (U_\\mathrm{target}^\\dagger U_\\mathrm{target})}
            \\right|^2 .

    See the `superconducting systems namespace classes
    <https://docs.q-ctrl.com/boulder-opal/references/boulder-opal/
    boulderopal/superconducting.html>`_
    for a list of the relevant objects to describe subsystems and optimizable coefficients.
    """

    Checker.VALUE(
        (target_state is None) ^ (target_operation is None),
        "You have to provide exactly one of `target_state` or `target_operation`.",
        {"target_state": target_state, "target_operation": target_operation},
    )
    if target_state is not None:
        Checker.VALUE(
            initial_state is not None,
            "If you provide a `target_state`, you must provide an `initial_state`.",
            {"target_state": target_state, "initial_state": initial_state},
        )

    gate_duration = ScalarT.REAL("gate_duration").gt(0)(gate_duration)
    sample_count = ScalarT.INT("sample_count").gt(0)(sample_count)
    cutoff_frequency = nullable(ScalarT.REAL("cutoff_frequency"), cutoff_frequency)

    dim = np.prod([system.dimension for system in transmons + cavities], dtype=int)
    initial_state = nullable(
        ArrayT.COMPLEX("initial_state").ndim(1).shape((dim,)), initial_state
    )
    target_state = nullable(
        ArrayT.COMPLEX("target_state").ndim(1).shape((dim,)), target_state
    )
    target_operation = nullable(
        ArrayT.COMPLEX("target_operation").ndim(2).shape((dim, dim)), target_operation
    )

    graph = Graph()

    # Create PWC Hamiltonian.
    hamiltonian, optimizable_node_names = _create_superconducting_hamiltonian(
        graph=graph,
        transmons=transmons,
        cavities=cavities,
        interactions=interactions,
        gate_duration=gate_duration,
        cutoff_frequency=cutoff_frequency,
        sample_count=sample_count,
    )

    # Check whether there are any optimizable coefficients.
    Checker.VALUE(
        len(optimizable_node_names) > 0,
        "At least one of the Hamiltonian terms must be optimizable.",
        {"transmons": transmons, "cavities": cavities, "interactions": interactions},
    )

    sample_times = np.linspace(0.0, gate_duration, sample_count)
    graph.tensor(sample_times, name="sample_times")
    unitaries = graph.time_evolution_operators_pwc(
        hamiltonian=hamiltonian, sample_times=sample_times, name="unitaries"
    )
    other_output_node_names = ["sample_times", "unitaries", "infidelity"]

    if initial_state is not None:
        states = unitaries @ initial_state[:, None]
        states = states[..., 0]
        states.name = "state_evolution"
        other_output_node_names.append("state_evolution")

    if target_state is not None:
        graph.state_infidelity(target_state, states[-1], name="infidelity")
    else:
        # The assert is to pass static type checking. As per the beginning of this
        # function, target_operation and target_state cannot be None simultaneously.
        assert target_operation is not None
        graph.unitary_infidelity(unitaries[-1], target_operation, name="infidelity")

    return run_optimization(
        graph=graph,
        cost_node_name="infidelity",
        output_node_names=optimizable_node_names + other_output_node_names,
        **optimization_kwargs,
    )
