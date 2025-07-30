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

from functools import (
    partial,
    wraps,
)
from typing import (
    Any,
    Callable,
)

from qctrlworkflowclient import core_workflow
from qctrlworkflowclient.functions import async_core_workflow
from qctrlworkflowclient.router.api import (
    Action,
    DecodedResult,
)

from boulderopal._configuration.configuration import (
    get_configuration,
    in_local_mode,
    is_async,
)
from boulderopal._core.formatter import (
    metadata_formatter,
    metadata_local_formatter,
)
from boulderopal._validation import Checker
from boulderopal.cloud._async import BoulderOpalJob


def _formatter(
    result: DecodedResult | dict,
    formatters: tuple[Callable[[DecodedResult], DecodedResult], ...] = (
        metadata_formatter,
    ),
) -> dict:
    if result is None or (isinstance(result, DecodedResult) and result.decoded is None):
        raise RuntimeError("All workflow function should return a non-nullable result.")
    if in_local_mode():
        return metadata_local_formatter(result)
    if is_async(result):
        return result
    for _func in formatters:
        result = _func(result)
    assert isinstance(result, DecodedResult)
    return result.decoded


def _async_formatter(input_: dict[str, Action]) -> BoulderOpalJob:
    action = input_["async_result"]
    return BoulderOpalJob(action=action)


def boulder_opal_workflow(workflow_name: str) -> Callable:
    """
    Decorator to wrap a workflow function.

    Parameters
    ----------
    workflow_name : str
        The name of the workflow.

    Returns
    -------
    Callable
        The wrapped function.
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def customized_decorator(*args: Any, **kwargs: Any) -> dict:
            run_async = kwargs.get("run_async")
            Checker.VALUE(
                not (run_async and in_local_mode()),
                "Async submission is not supported in local mode.",
            )

            if run_async:
                return partial(
                    async_core_workflow, get_configuration, formatter=_async_formatter
                )(workflow_name)(func)(*args, **kwargs)
            return partial(core_workflow, get_configuration, formatter=_formatter)(
                workflow_name
            )(func)(*args, **kwargs)

        return customized_decorator

    return decorator
