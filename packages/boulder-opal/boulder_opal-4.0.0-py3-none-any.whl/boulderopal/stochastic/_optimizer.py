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

from dataclasses import dataclass

from boulderopal._validation import ScalarT


@dataclass
class Adam:
    """
    Adaptive moment estimation (Adam) optimizer for stochastic optimization.

    For more detail on Adam see
    `Adam <https://en.wikipedia.org/wiki/Stochastic_gradient_descent#Adam>`_ on Wikipedia.

    Parameters
    ----------
    learning_rate : float, optional
        The learning rate for the Adam optimizer.
        If set, must be positive. Defaults to 0.01.

    See Also
    --------
    boulderopal.run_stochastic_optimization :
        Perform gradient-based stochastic optimization of generic real-valued functions.
    """

    learning_rate: float = 0.01

    def __post_init__(self) -> None:
        self.learning_rate = ScalarT.REAL("learning_rate").gt(0)(self.learning_rate)
