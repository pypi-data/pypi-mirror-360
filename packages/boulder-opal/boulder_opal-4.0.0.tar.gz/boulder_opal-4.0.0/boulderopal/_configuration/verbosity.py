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

from dataclasses import dataclass
from enum import Enum
from typing import Any

from boulderopal._validation import validate_enum


class _VerbosityEnum(Enum):
    """
    Verbosity modes for Boulder Opal cloud calculations.
    """

    VERBOSE = "VERBOSE"
    QUIET = "QUIET"


def _format_message(action_id: str, status: str) -> str:
    _message = {
        "PENDING": "is queued",
        "RECEIVED": "has been received",
        "STARTED": "has started",
        "SUCCESS": "has completed",
        "FAILURE": "has failed",
        "RETRY": "is retrying",
        "REVOKED": "has been cancelled",
    }.get(status, f"has an unknown status ({status})")

    return f'Your task (action_id="{action_id}") {_message}.'


@dataclass
class StatusMessagePrinter:
    """
    Class to manage printing messages during task execution.

    Parameters
    ----------
    last_message : str
        The last message printed.
    verbosity : str
        The level of verbosity for messages.
    """

    last_message: str = ""
    verbosity: str = "VERBOSE"

    def __call__(self, event: str, data: Any) -> None:
        """
        Prints a message if the action was updated.
        """
        if self.verbosity == "QUIET":
            return

        if event == "action.updated":
            action = data["action"]
            message = _format_message(action.action_id, action.status)
            if message != self.last_message:
                self.last_message = message
                print(message)


MESSAGE_PRINTER = StatusMessagePrinter()


def set_verbosity(verbosity: str) -> None:
    """
    Set the verbosity mode when running calculations on the cloud.

    Parameters
    ----------
    verbosity : str
        The verbosity of messages. Possible values are:
        "VERBOSE" (showing task status messages) and
        "QUIET" (not showing them).
    """
    MESSAGE_PRINTER.verbosity = validate_enum(_VerbosityEnum, verbosity)
