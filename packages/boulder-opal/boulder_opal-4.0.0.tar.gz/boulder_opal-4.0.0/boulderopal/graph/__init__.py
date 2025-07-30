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

# Make private alias for all imports to clean up the autocomplete for the graph module.
import sys as _sys

import boulderopal._nodes.node_data as _nd
from boulderopal._nodes.ions import IonsGraph as _IonsGraph
from boulderopal._nodes.random import RandomGraph as _RandomGraph
from boulderopal._nodes.signals import Signals as _Signals
from boulderopal.graph._execute_graph import (
    ExecutionMode,
    execute_graph,
)
from boulderopal.graph._graph import Graph

_TYPE_REGISTRY = [
    _nd.ConvolutionKernel,
    _nd.FilterFunction,
    _nd.Pwc,
    _nd.SparsePwc,
    _nd.Stf,
    _nd.Target,
    _nd.Tensor,
]

# Binding the Graph related types to the current module, this is useful
# for building docs for the Graph class.
_module = _sys.modules[__name__]
for _type_cls in _TYPE_REGISTRY:
    setattr(_module, _type_cls.__name__, _type_cls)


# To build doc for namespace nodes. These are added as if they are part of the `Graph` module.
setattr(_module, "random", _RandomGraph)
setattr(_module, "ions", _IonsGraph)
setattr(_module, "signals", _Signals)


__all__ = ["ExecutionMode", "Graph", "execute_graph"]
