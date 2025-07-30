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

# pylint: disable=missing-function-docstring
from __future__ import annotations

from typing import (
    TYPE_CHECKING,
    Any,
    Optional,
)

import numpy as np

from .base import boulder_opal_workflow

if TYPE_CHECKING:
    from boulderopal.graph import Graph


@boulder_opal_workflow("closed_loop_step_workflow")
def closed_loop_step_workflow(
    optimizer: dict, results: Optional[dict], test_point_count: Optional[int]
) -> dict[str, Any]:
    return {
        "optimizer": optimizer,
        "results": results,
        "test_point_count": test_point_count,
    }


@boulder_opal_workflow("execute_graph_workflow")
def execute_graph_workflow(
    graph: "Graph",
    output_node_names: list[str],
    execution_mode: str,
    *,
    run_async: bool,  # pylint: disable=unused-argument
) -> dict[str, Any]:
    return {
        "graph": graph,
        "output_node_names": output_node_names,
        "execution_mode": execution_mode,
    }


@boulder_opal_workflow("obtain_ion_chain_properties_workflow")
def obtain_ion_chain_properties_workflow(
    atomic_mass: float,
    ion_count: int,
    center_of_mass_frequencies: np.ndarray,
    wavevector: np.ndarray,
    laser_detuning: Optional[float],
) -> dict[str, Any]:
    return {
        "atomic_mass": atomic_mass,
        "ion_count": ion_count,
        "center_of_mass_frequencies": center_of_mass_frequencies,
        "wavevector": wavevector,
        "laser_detuning": laser_detuning,
    }


@boulder_opal_workflow("reconstruct_noise_workflow")
def reconstruct_noise_workflow(
    method: dict[str, dict[str, Any]],
    noises_frequencies: list[np.ndarray],
    filter_functions: list[np.ndarray],
    infidelities: np.ndarray,
    infidelity_uncertainties: Optional[np.ndarray],
) -> dict[str, Any]:
    return {
        "method": method,
        "noises_frequencies": noises_frequencies,
        "filter_functions": filter_functions,
        "infidelities": infidelities,
        "infidelity_uncertainties": infidelity_uncertainties,
    }


@boulder_opal_workflow("run_gradient_free_optimization_workflow")
def run_gradient_free_optimization_workflow(
    graph: "Graph",
    cost_node_name: str,
    output_node_names: list[str],
    iteration_count: int,
    target_cost: Optional[float],
    optimization_count: int,
    cost_history_scope: str,
    seed: Optional[int],
) -> dict[str, Any]:
    return {
        "graph": graph,
        "cost_node_name": cost_node_name,
        "output_node_names": output_node_names,
        "iteration_count": iteration_count,
        "target_cost": target_cost,
        "optimization_count": optimization_count,
        "cost_history_scope": cost_history_scope,
        "seed": seed,
    }


@boulder_opal_workflow("run_optimization_workflow")
def run_optimization_workflow(
    graph: "Graph",
    optimization_count: int,
    cost_node_name: str,
    output_node_names: list[str],
    target_cost: Optional[float],
    max_iteration_count: Optional[int],
    cost_tolerance: Optional[float],
    cost_history_scope: str,
    seed: Optional[int],
    *,
    run_async: bool,  # pylint: disable=unused-argument
) -> dict[str, Any]:
    return {
        "graph": graph,
        "optimization_count": optimization_count,
        "cost_node_name": cost_node_name,
        "output_node_names": output_node_names,
        "target_cost": target_cost,
        "max_iteration_count": max_iteration_count,
        "cost_tolerance": cost_tolerance,
        "cost_history_scope": cost_history_scope,
        "seed": seed,
    }


@boulder_opal_workflow("run_stochastic_optimization_workflow")
def run_stochastic_optimization_workflow(
    graph: "Graph",
    optimizer: dict,
    cost_node_name: str,
    output_node_names: list[str],
    iteration_count: int,
    cost_history_scope: str,
    target_cost: Optional[float],
    seed: Optional[int],
    *,
    run_async: bool,  # pylint: disable=unused-argument
) -> dict[str, Any]:
    return {
        "graph": graph,
        "optimizer": optimizer,
        "cost_node_name": cost_node_name,
        "output_node_names": output_node_names,
        "iteration_count": iteration_count,
        "cost_history_scope": cost_history_scope,
        "target_cost": target_cost,
        "seed": seed,
    }
