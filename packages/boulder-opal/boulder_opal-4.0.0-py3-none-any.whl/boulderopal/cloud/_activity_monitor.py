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

from datetime import datetime
from typing import (
    Any,
    Optional,
)

from rich.console import Console
from rich.table import Table

from boulderopal._validation import ScalarT
from boulderopal.cloud._utils import get_cloud_router

_ACTION_NAME_MAP = {
    "closed_loop_step_workflow": "closed_loop.step",
    "execute_graph_workflow": "execute_graph",
    "obtain_ion_chain_properties_workflow": "ions.obtain_ion_chain_properties",
    "reconstruct_noise_workflow": "noise_reconstruction.reconstruct",
    "run_gradient_free_optimization_workflow": "run_gradient_free_optimization",
    "run_optimization_workflow": "run_optimization",
    "run_stochastic_optimization_workflow": "run_stochastic_optimization",
}


def show_activity_monitor(
    limit: int = 5, offset: int = 0, status: Optional[str] = None
) -> None:
    """
    Print information from previously submitted actions.

    Parameters
    ----------
    limit : int, optional
        The number of actions to print. Cannot exceed 50. Defaults to 5.
    offset : int, optional
        The number of recent actions to ignore before starting to print.
        Defaults to 0.
    status : str or None, optional
        The filter for action status. Defaults to None, meaning actions with all status are
        printed. Available options are SUCCESS, FAILURE, REVOKED, PENDING,
        RECEIVED, RETRY, and STARTED.
    """

    limit = ScalarT.INT("limit").ge(1).le(50)(limit)
    router = get_cloud_router("Activity monitor")
    action_records: list[dict[str, Any]] = router.activity_monitor(
        limit, offset, status
    )

    if len(action_records) == 0:
        print("No actions found for the specified arguments.")
        return

    table = Table(title="Activity monitor", show_lines=True)
    console = Console()

    for header in ["Action name", "Created UTC", "Updated UTC", "Run time", "Status"]:
        table.add_column(header, justify="center")

    for row in action_records:
        table.add_row(*_format_action_record(row))

    console.print(table)


def _format_action_record(record: dict[str, str]) -> list[str]:
    created_at = datetime.fromisoformat(record["createdAt"])
    updated_at = datetime.fromisoformat(record["updatedAt"])
    run_time = int((updated_at - created_at).total_seconds())

    _state_map = {
        "SUCCESS": "Completed",
        "FAILURE": "Failed",
        "REVOKED": "Cancelled",
        "PENDING": "Queued",
        "RECEIVED": "Received",
        "RETRY": "Retried",
        "STARTED": "Started",
    }

    _name = _ACTION_NAME_MAP.get(record["name"], record["name"])

    return [
        f'{_name}\nID {record["modelId"]}',
        created_at.strftime("%Y-%m-%d\n%H:%M:%S"),
        updated_at.strftime("%Y-%m-%d\n%H:%M:%S"),
        f"{run_time//3600:02d}:{(run_time % 3600)//60:02d}:{run_time % 60:02d}",
        _state_map.get(record["status"], record["status"]),
    ]
