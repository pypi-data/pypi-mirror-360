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
    Optional,
    Sequence,
    TypeVar,
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
from boulderopal.ions._drives import (
    Drive,
    OptimizableDrive,
)
from boulderopal.optimization import run_optimization


def _validate_system_parameters(
    lamb_dicke_parameters: np.ndarray,
    relative_detunings: np.ndarray,
    target_phases: Optional[np.ndarray],
) -> int:
    """
    Validate the arrays describing an ion system
    and return the number of ions.
    """

    ion_count = lamb_dicke_parameters.shape[-1]

    Checker.VALUE(
        lamb_dicke_parameters.shape == (3, ion_count, ion_count)
        and relative_detunings.shape == (3, ion_count),
        "The shape of the Lamb–Dicke parameters array must be (3, N, N), "
        "and the shape of the relative detunings array must be (3, N), "
        "where N is the number of ions.",
        {
            "lamb_dicke_parameters.shape": lamb_dicke_parameters.shape,
            "relative_detunings.shape": relative_detunings.shape,
        },
    )

    if target_phases is not None:
        Checker.VALUE(
            target_phases.shape == (ion_count, ion_count),
            "The shape of the target phases array must be (N, N), "
            "where N is the number of ions.",
            {"target_phases.shape": target_phases.shape, "ion count": ion_count},
        )

    return ion_count


_T = TypeVar("_T", Drive, OptimizableDrive)


def _check_drives_addressing(drives: Sequence[_T], ion_count: int) -> None:
    """
    Check the input drives are a list and that the ions they address are valid.
    """

    Checker.TYPE(isinstance(drives, list), "You must provide a list of drives.")

    all_addressing: list[int] = []
    for idx, drive in enumerate(drives):
        Checker.VALUE(
            all(0 <= ion < ion_count for ion in drive.addressing),
            "The addressed ions must be between 0 (inclusive) "
            "and the number of ions (exclusive).",
            {f"drives[{idx}].addressing": drive.addressing, "ion count": ion_count},
        )
        all_addressing.extend(drive.addressing)

    Checker.VALUE(
        len(all_addressing) == len(set(all_addressing)),
        "Each ion can only be addressed by a single drive.",
    )


def _get_ion_drives(
    pwc_addressing_pairs: list[tuple[Pwc, tuple[int, ...]]], ion_count: int
) -> tuple[Sequence[Optional[Pwc]], list[int]]:
    """
    From a list of (Pwc, list(int)) tuples (drives and ions addressed by them),
    return (1) a list of length ion_count containing the drive addressing each ion
    or None if the ion is not addressed by any drive and (2) a list with the indices
    of the addressed ions.
    """
    ion_drives = [None] * ion_count
    addressed_ions = []
    for pwc, addressing in pwc_addressing_pairs:
        for ion in addressing:
            ion_drives[ion] = pwc  # type: ignore
            addressed_ions.append(ion)

    return ion_drives, addressed_ions


_MS_NODE_NAMES = ["sample_times", "phases", "displacements", "infidelities"]


def ms_simulate(
    drives: list[Drive],
    duration: float,
    lamb_dicke_parameters: np.ndarray,
    relative_detunings: np.ndarray,
    target_phases: Optional[np.ndarray] = None,
    sample_count: int = 128,
) -> dict:
    r"""
    Simulate a Mølmer–Sørensen-type operation on a system composed of ions.

    This function builds a graph describing the Mølmer–Sørensen operation
    and calls `boulderopal.execute_graph` to simulate the ion dynamics.

    Parameters
    ----------
    drives : list[~ions.Drive]
        A list of drives addressing the ions.
        Each ion can only be addressed by a single drive,
        but there may be ions not addressed by any drive.
    duration : float
        The duration, in seconds, of the dynamics to be simulated, :math:`T`.
        It must be greater than zero.
    lamb_dicke_parameters : np.ndarray
        The laser-ion coupling strength, :math:`\{\eta_{jkl}\}`.
        Its shape must be ``(3, N, N)``, where the dimensions indicate,
        respectively, axis, collective mode, and ion.
    relative_detunings : np.ndarray
        The difference :math:`\{\delta_{jk} = \nu_{jk} - \delta\}` (in Hz) between each motional
        mode frequency and the laser detuning from the qubit transition frequency :math:`\omega_0`.
        Its shape must be ``(3, N)``, where the dimensions indicate, respectively,
        axis and collective mode.
    target_phases : np.ndarray or None, optional
        The target total relative phases between ion pairs, :math:`\{\Psi_{ln}\}`,
        as a strictly lower triangular matrix of shape ``(N, N)``.
        :math:`\Psi_{ln}` with :math:`l > n` indicates the relative phase between ions
        :math:`l` and :math:`n`, while :math:`\Psi_{ln} = 0` for :math:`l \leq n`.
        If not provided, the function does not return the operational infidelities.
    sample_count : int, optional
        The number of times :math:`T` between 0 and `duration` (included)
        at which the evolution is sampled.
        Defaults to 128.

    Returns
    -------
    dict
        The result of the `execute_graph` call.
        Its ``output`` item is a dictionary containing information about
        the evolution of the system, with the following keys:

            ``sample_times``
                The times at which the evolution is sampled, as an array of shape ``(T,)``.
            ``phases``
                Acquired phases :math:`\{\Phi_{ln}(t_i) = \phi_{ln}(t_i) + \phi_{nl}(t_i)\}`
                for each sample time and for all ion pairs, as a strictly lower triangular
                matrix of shape ``(T, N, N)``.
                :math:`\Phi_{ln}(t_i)` with :math:`l > n` indicates the relative phase between ions
                :math:`l` and :math:`n`, while :math:`\Phi_{ln}(t_i) = 0` for :math:`l \leq n`.
            ``displacements``
                Displacements :math:`\{\eta_{jkl}\alpha_{jkl}(t_i)\}` for all mode-ion combinations,
                as an array of shape ``(T, 3, N, N)``, where the dimensions indicate, respectively,
                time, axis, collective mode, and ion.
            ``infidelities``
                A 1D array of length ``T`` with the operational infidelities of
                the Mølmer–Sørensen gate at each sample time, :math:`\mathcal{I}(t_i)`.
                Only returned if target relative phases are provided.

    See Also
    --------
    boulderopal.ions.Drive :
        Class describing non-optimizable drives.
    boulderopal.ions.ms_optimize :
        Find optimal pulses to perform Mølmer–Sørensen-type operations on trapped ions systems.
    boulderopal.ions.obtain_ion_chain_properties :
        Calculate the properties of an ion chain.

    Notes
    -----
    The internal and motional Hamiltonian of :math:`N` ions is

    .. math::
        H_0 = \sum_{j=1}^{3} \sum_{k=1}^{N} \hbar\nu_{jk} \left(a_{jk}^\dagger a_{jk}
            + \frac{1}{2}\right) + \sum_{l=1}^N \frac{\hbar \omega_0}{2} \sigma_{z,l} ,

    where :math:`j` indicates axis dimension (:math:`x`, :math:`y`, or :math:`z`),
    :math:`k` indicates collective mode, :math:`a_{jk}` is the annihilation operator,
    and :math:`\sigma_{z,l}` is the Pauli :math:`Z` operator for ion :math:`l`.

    The interaction Hamiltonian for Mølmer–Sørensen-type
    operations in the rotating frame with respect to :math:`H_0` is

    .. math::
        H_I(t) = i\hbar \sum_{j=1}^{3} \sum_{k=1}^{N} \sum_{l=1}^N
            \sigma_{x,l} \left(-\beta_{jkl}^*(t)a_{jk} + \beta_{jkl}(t) a_{jk}^\dagger\right) ,

    where :math:`\sigma_{x,l}` is the Pauli :math:`X` operator for ion :math:`l` and

    .. math::
        \beta_{jkl}(t) = \eta_{jkl} \frac{\gamma_l(t)}{2} \exp(i 2 \pi \delta_{jk} t)

    indicates the coupling between ion :math:`l` and motional mode :math:`(j,k)`.

    The corresponding unitary operation is given by [1]_

    .. math::
        U(t) = \exp\left[ \sum_{l=1}^N \sigma_{x,l} B_l(t)
            + i\sum_{l=1}^N\sum_{n=1}^{l-1} (\phi_{ln}(t) + \phi_{nl}(t))
            \sigma_{x,l} \sigma_{x,n} \right] ,

    where

    .. math::
        B_l(t) &\equiv \sum_{j=1}^{3} \sum_{k=1}^{N}
            \left(\eta_{jkl}\alpha_{jkl}(t)a_{jk}^\dagger
            - \eta_{jkl}^{\ast}\alpha_{jkl}^\ast(t)a_{jk} \right) ,

        \phi_{ln}(t) &\equiv \mathrm{Im} \left[ \sum_{j=1}^{3} \sum_{k=1}^{N}
            \int_{0}^{t} d \tau_1 \int_{0}^{\tau_1} d \tau_2
            \beta_{jkl}(\tau_1)\beta_{jkn}^{\ast}(\tau_2) \right] ,

        \alpha_{jkl}(t) &\equiv \int_0^t d\tau \frac{\gamma_l(\tau)}{2}
            \exp(i 2 \pi \delta_{jk} \tau) .

    The operational infidelity of the Mølmer–Sørensen gate is defined as [1]_:

    .. math::
        \mathcal{I} = 1 - \left| \left( \prod_{n=1}^N \prod_{l=n+1}^N
            \cos ( \Phi_{ln} - \Psi_{ln}) \right)
            \left( 1 - \sum_{j=1}^3 \sum_{k=1}^N \sum_{l=1}^N \left[ |\eta_{jkl} \alpha_{jkl}|^2
            \left(\bar{n}_{jk}+\frac{1}{2} \right) \right] \right) \right|^2 ,

    References
    ----------
    .. [1] `C. D. B. Bentley, H. Ball, M. J. Biercuk, A. R. R. Carvalho,
            M. R. Hush, and H. J. Slatyer, Advanced Quantum Technologies 3, 2000044 (2020).
            <https://doi.org/10.1002/qute.202000044>`_
    """

    duration = ScalarT.REAL("duration").gt(0)(duration)

    lamb_dicke_parameters = ArrayT.REAL("lamb_dicke_parameters").ndim(3)(
        lamb_dicke_parameters
    )
    relative_detunings = ArrayT.REAL("relative_detunings").ndim(2)(relative_detunings)
    target_phases = nullable(ArrayT.REAL("target_phases").ndim(2), target_phases)
    ion_count = _validate_system_parameters(
        lamb_dicke_parameters, relative_detunings, target_phases
    )

    Checker.VALUE(
        all(isinstance(drive, Drive) for drive in drives),
        "All drives must be non-optimizable.",
        {"drives": drives},
    )

    _check_drives_addressing(drives, ion_count)

    graph = Graph()

    drive_pwcs = [
        (drive.get_pwc(graph, duration), drive.addressing) for drive in drives
    ]
    ion_drives, addressed_ions = _get_ion_drives(drive_pwcs, ion_count)

    sample_times = np.linspace(0.0, duration, sample_count)
    graph.tensor(sample_times, name="sample_times")

    phases = graph.ions.ms_phases(
        drives=ion_drives,
        lamb_dicke_parameters=lamb_dicke_parameters,
        relative_detunings=relative_detunings,
        sample_times=sample_times,
        name=_MS_NODE_NAMES[1],
    )

    displacements = graph.ions.ms_displacements(
        drives=ion_drives,
        lamb_dicke_parameters=lamb_dicke_parameters,
        relative_detunings=relative_detunings,
        sample_times=sample_times,
    )

    # If there are unaddressed ions add zeros for their displacements.
    ion_count = lamb_dicke_parameters.shape[-1]
    if len(addressed_ions) < ion_count:
        graph.matmul(
            displacements, np.eye(ion_count)[addressed_ions], name=_MS_NODE_NAMES[2]
        )
    else:
        displacements.name = _MS_NODE_NAMES[2]

    if target_phases is not None:
        graph.ions.ms_infidelity(
            phases=phases,
            displacements=displacements,
            target_phases=target_phases,
            name=_MS_NODE_NAMES[3],
        )
        output_node_names = _MS_NODE_NAMES
    else:
        output_node_names = _MS_NODE_NAMES[:3]

    return execute_graph(graph=graph, output_node_names=output_node_names)


def ms_optimize(
    drives: Sequence[OptimizableDrive],
    duration: float,
    lamb_dicke_parameters: np.ndarray,
    relative_detunings: np.ndarray,
    target_phases: np.ndarray,
    sample_count: int = 128,
    robust: bool = False,
    **optimization_kwargs: Any,
) -> dict:
    r"""
    Find optimal pulses to perform a target Mølmer–Sørensen-type operation
    on a system composed of ions.

    This function builds a graph describing the Mølmer–Sørensen operation
    and calls `boulderopal.run_optimization` to minimize the target cost.

    Parameters
    ----------
    drives : list[OptimizableDrive]
        A list of optimizable drives addressing the ions.
        Each ion can only be addressed by a single drive,
        but there may be ions not addressed by any drive.
    duration : float
        The duration, in seconds, of the dynamics to be optimized, :math:`T`.
        It must be greater than zero.
    lamb_dicke_parameters : np.ndarray
        The laser-ion coupling strength, :math:`\{\eta_{jkl}\}`.
        Its shape must be ``(3, N, N)``, where the dimensions indicate,
        respectively, axis, collective mode, and ion.
    relative_detunings : np.ndarray
        The difference :math:`\{\delta_{jk} = \nu_{jk} - \delta\}` (in Hz) between each motional
        mode frequency and the laser detuning from the qubit transition frequency :math:`\omega_0`.
        Its shape must be ``(3, N)``, where the dimensions indicate, respectively,
        axis and collective mode.
    target_phases : np.ndarray or None, optional
        The target total relative phases between ion pairs, :math:`\{\Psi_{ln}\}`,
        as a strictly lower triangular matrix of shape ``(N, N)``.
        :math:`\Psi_{ln}` with :math:`l > n` indicates the relative phase between ions
        :math:`l` and :math:`n`, while :math:`\Psi_{ln} = 0` for :math:`l \leq n`.
    sample_count : int, optional
        The number of times :math:`T` between 0 and `duration` (both included)
        at which the evolution is sampled.
        Defaults to 128.
    robust : bool, optional
        If set to False, the cost corresponds to the infidelity at the end of the gate.
        If set to True, the cost is the final infidelity plus a dephasing-robust cost term.
        Defaults to False.
    **optimization_kwargs
        Additional parameters to pass to boulderopal.run_optimization.

    Returns
    -------
    dict
        The result of the `run_optimization` call.
        Its ``output`` item is a dictionary containing information about
        the optimized drive and the evolution of the system, with the following keys:

            optimized drives
                The piecewise-constant optimized drives implementing the gate.
                The keys are the names of the `drives` provided to the function.
            ``sample_times``
                The times at which the evolution is sampled, as an array of shape ``(T,)``.
            ``phases``
                Acquired phases :math:`\{\Phi_{ln}(t_i) = \phi_{ln}(t_i) + \phi_{nl}(t_i)\}`
                for each sample time and for all ion pairs, as a strictly lower triangular
                matrix of shape ``(T, N, N)``.
                :math:`\Phi_{ln}(t_i)` with :math:`l > n` indicates the relative phase between ions
                :math:`l` and :math:`n`, while :math:`\Phi_{ln}(t_i) = 0` for :math:`l \leq n`.
            ``displacements``
                Displacements :math:`\{\eta_{jkl}\alpha_{jkl}(t_i)\}` for all mode-ion combinations,
                as an array of shape ``(T, 3, N, N)``, where the dimensions indicate, respectively,
                time, axis, collective mode, and ion.
            ``infidelities``
                A 1D array of length ``T`` with the operational infidelities of
                the Mølmer–Sørensen gate at each sample time, :math:`\mathcal{I}(t_i)`.

    See Also
    --------
    boulderopal.ions.ComplexOptimizableDrive :
        Class describing a piecewise-constant complex-valued optimizable drive.
    boulderopal.ions.RealOptimizableDrive :
        Class describing a piecewise-constant real-valued optimizable drive.
    boulderopal.ions.ms_simulate :
        Simulate a Mølmer–Sørensen-type operation on a trapped ions system.
    boulderopal.ions.obtain_ion_chain_properties :
        Calculate the properties of an ion chain.

    Notes
    -----
    See the notes of :func:`boulderopal.ions.ms_simulate` for the main equations and definitions.

    You can use the `robust` flag to construct a Mølmer–Sørensen gate that is
    robust against dephasing noise. This imposes a symmetry [1]_ in the optimizable
    ion drives and aims to minimize the time-averaged positions of the phase-space
    trajectories,

    .. math::
        \langle \alpha_{jkl} \rangle
            = \frac{1}{t_\text{gate}} \int_0^{t_\text{gate}}
                \alpha_{jkl}(t) \mathrm{d} t .

    This is achieved by adding an additional term to the cost function,
    consisting of the sum of the square moduli of the time-averaged positions
    multiplied by the corresponding Lamb–Dicke parameters. That is to say,

    .. math::
        C_\text{robust} = \mathcal{I} + \sum_{j=1}^{3} \sum_{k=1}^{N} \sum_{l=1}^{N}
                \left| \eta_{jkl} \langle \alpha_{jkl} \rangle \right|^2 .

    References
    ----------
    .. [1] `C. D. B. Bentley, H. Ball, M. J. Biercuk, A. R. R. Carvalho,
            M. R. Hush, and H. J. Slatyer, Advanced Quantum Technologies 3, 2000044 (2020).
            <https://doi.org/10.1002/qute.202000044>`_
    """

    duration = ScalarT.REAL("duration").gt(0)(duration)

    lamb_dicke_parameters = ArrayT.REAL("lamb_dicke_parameters").ndim(3)(
        lamb_dicke_parameters
    )
    relative_detunings = ArrayT.REAL("relative_detunings").ndim(2)(relative_detunings)
    target_phases = ArrayT.REAL("target_phases").ndim(2)(target_phases)
    ion_count = _validate_system_parameters(
        lamb_dicke_parameters, relative_detunings, target_phases
    )

    Checker.TYPE(
        all(isinstance(drive, OptimizableDrive) for drive in drives),
        "All drives must be optimizable.",
    )

    _check_drives_addressing(drives, ion_count)

    drive_names = [drive.name for drive in drives]

    Checker.VALUE(
        len(drive_names) == len(set(drive_names)),
        "The drive names must be unique.",
        {"drive names": drive_names},
    )

    graph = Graph()

    drive_pwcs = [
        (drive.get_pwc(graph, duration, robust), drive.addressing) for drive in drives
    ]
    ion_drives, addressed_ions = _get_ion_drives(drive_pwcs, ion_count)

    sample_times = np.linspace(0.0, duration, sample_count)
    graph.tensor(sample_times, name="sample_times")

    phases = graph.ions.ms_phases(
        drives=ion_drives,
        lamb_dicke_parameters=lamb_dicke_parameters,
        relative_detunings=relative_detunings,
        sample_times=sample_times,
        name=_MS_NODE_NAMES[1],
    )

    displacements = graph.ions.ms_displacements(
        drives=ion_drives,
        lamb_dicke_parameters=lamb_dicke_parameters,
        relative_detunings=relative_detunings,
        sample_times=sample_times,
    )

    # If there are unaddressed ions add zeros for their displacements.
    ion_count = lamb_dicke_parameters.shape[-1]
    if len(addressed_ions) < ion_count:
        graph.matmul(
            displacements, np.eye(ion_count)[addressed_ions], name=_MS_NODE_NAMES[2]
        )
    else:
        displacements.name = _MS_NODE_NAMES[2]

    infidelities = graph.ions.ms_infidelity(
        phases=phases,
        displacements=displacements,
        target_phases=target_phases,
        name=_MS_NODE_NAMES[3],
    )

    cost = infidelities[-1]
    if robust:
        cost += graph.ions.ms_dephasing_robust_cost(
            drives=ion_drives,
            lamb_dicke_parameters=lamb_dicke_parameters,
            relative_detunings=relative_detunings,
        )

    return run_optimization(
        graph=graph,
        cost_node_name=cost.name,
        output_node_names=drive_names + _MS_NODE_NAMES,
        **optimization_kwargs,
    )
