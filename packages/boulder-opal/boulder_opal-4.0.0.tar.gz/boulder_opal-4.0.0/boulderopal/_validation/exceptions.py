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

from enum import Enum
from functools import partial
from typing import (
    Any,
    Optional,
    Type,
)

import numpy as np


def _simple_check(
    condition: bool | np.bool_,
    message: str,
    extras: Optional[dict[str, Any]] = None,
    *,
    exc: Type[Exception],
) -> None:
    if condition:
        return
    if extras is not None:
        _extra = ", ".join([f"{key}={repr(val)}" for key, val in extras.items()])
        message = f"{message} {_extra}"
    raise exc(message)


class Checker(Enum):
    """
    Host validation functions to check input for Boulder Opal APIs.
    """

    TYPE = partial(_simple_check, exc=TypeError)
    VALUE = partial(_simple_check, exc=ValueError)

    def __call__(self, *args: Any, **kwargs: Any) -> None:
        return self.value(*args, **kwargs)
