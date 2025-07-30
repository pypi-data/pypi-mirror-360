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

from qctrlworkflowclient.router.api import (
    Action,
    ActionStatus,
)

from boulderopal._core.formatter import metadata_formatter
from boulderopal._validation import Checker
from boulderopal.cloud._utils import get_cloud_router


class BoulderOpalJob:
    """
    An object tracking a Boulder Opal calculation submitted to the cloud.

    Parameters
    ----------
    action : Action
        The unique identifier object for the cloud job.

    Attributes
    ----------
    action_id : str
        The ID associated with the calculation.
    """

    def __init__(self, action: Action) -> None:
        self._action = action
        self._router = get_cloud_router("Manipulating a BoulderOpalJob")

    def __repr__(self) -> str:
        return f'<BoulderOpalJob: action_id="{self.action_id}">'

    @property
    def action_id(self) -> str:
        """
        The job action ID.
        """
        return self._action.action_id

    def get_status(self) -> str:
        """
        Get the job status.

        Returns
        -------
        str
            The status of the job.
        """
        self._action = self._router.update_action_status(action=self._action)
        assert self._action.status is not None, "Unknown action status."
        return self._action.status

    def get_result(self) -> dict:
        """
        Get the job result.
        Note that this is a blocking operation.

        Returns
        -------
        dict
            A dictionary containing the calculation result.
        """
        return metadata_formatter(
            self._router.get_result(self._action, revoke_on_interrupt=False)
        ).decoded

    def cancel(self) -> None:
        """
        Cancel the remote job.
        """
        status = self.get_status()
        if status == ActionStatus.REVOKED.value:
            message = "was already cancelled"
        elif status == ActionStatus.SUCCESS.value:
            message = "has already completed"
        elif status == ActionStatus.FAILURE.value:
            message = "failed"
        else:
            message = ""

        if message != "":
            print(
                f'Your task (action_id="{self.action_id}") {message}, '
                "and cannot be cancelled."
            )
        else:
            self._router._revoke_action(  # pylint: disable=protected-access
                self._action
            )
            print(f'Your task (action_id="{self.action_id}") has been cancelled.')


def get_job(action_id: int | str) -> BoulderOpalJob:
    """
    Create an object to track a remote job from its action ID.

    Parameters
    ----------
    action_id : int or str
        The ID associated with the calculation.
        You can get the ID of your calculations from the activity monitor.

    Returns
    -------
    BoulderOpalJob
        The object tracking the remote job.
    """
    Checker.TYPE(
        str(action_id).isnumeric(),
        "The calculation ID must be an integer.",
        {"action_id": action_id},
    )
    return BoulderOpalJob(Action(action_id=str(action_id)))
