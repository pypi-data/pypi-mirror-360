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
"""
Module to host some utils functions, which are exposed at the top-level.
"""
from __future__ import annotations

from qctrlworkflowclient.utils import package_versions_table


def print_package_versions() -> None:
    """
    Print a Markdown-formatted table showing the Python version being used,
    as well as the versions of some loaded packages that are relevant to Boulder Opal.
    """

    package_names = [
        # External packages.
        "jsonpickle",
        "matplotlib",
        "mloop",
        "numpy",
        "qiskit",
        "qutip",
        "scipy",
        # Q-CTRL packages.
        "boulderopal",
        "qctrlcommons",
        "qctrlexperimentscheduler",
        "qctrlmloop",
        "qctrlopencontrols",
        "qctrlqua",
        "qctrlvisualizer",
        "qctrlworkflowclient",
    ]

    print(package_versions_table(package_names))


__all__ = ["print_package_versions"]
