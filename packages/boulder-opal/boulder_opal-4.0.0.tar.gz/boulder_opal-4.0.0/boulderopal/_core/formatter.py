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

from qctrlworkflowclient.router.api import DecodedResult


def metadata_formatter(input_: DecodedResult) -> DecodedResult:
    """
    Insert `action_id` to the `metadata` key of the result.

    Parameters
    ----------
    input_ : DecodedResult
        The result from the workflow functions.

    Returns
    -------
    DecodedResult
        The reformatted result.
    """
    result = input_.decoded
    assert isinstance(result, dict)
    if result.get("metadata") is None:
        result["metadata"] = {}
    result["metadata"].update({"action_id": input_.action_id})
    return input_


def async_result_formatter(input_: DecodedResult) -> dict:
    """
    Format the response result before updating it in the async result dictionary.

    Parameters
    ----------
    input_ : DecodedResult
        The result from the workflow functions.

    Returns
    -------
    dict
        The reformatted result.
    """
    result = metadata_formatter(input_)
    return result.decoded


def metadata_local_formatter(input_: dict) -> dict:
    """
    Fill action_id key as None in local mode.

    Parameters
    ----------
    input_ : dict
        Result from running workflow functions locally.

    Returns
    -------
    dict
        Formatted result.
    """
    if input_.get("metadata") is None:
        input_["metadata"] = {}
    input_["metadata"]["action_id"] = None
    return input_
