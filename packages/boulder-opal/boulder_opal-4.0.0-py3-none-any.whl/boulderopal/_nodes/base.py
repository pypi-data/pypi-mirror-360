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

from typing import (
    Callable,
    Optional,
)

from qctrlcommons.graph import Graph
from qctrlcommons.node.wrapper import Operation


def create_operation(
    obj: Callable,
    kwargs: dict,
    graph: Optional[Graph] = None,
    name: Optional[str] = None,
) -> Operation:
    """
    Return a graph operation.

    This is a helper function for easily creating an Operation inside a graph method. `obj` is
    expected to be the graph method itself and kwargs is expected to be `locals()`. For example,
    inside a sub-graph method `node_func`, one might call
    `create_operation(self.node_func, locals())` to create an operator instead of repeating all
    the arguments that node_func takes.

    The optional graph and name parameter allows one to pass the graph object and an operation name
    explicitly when necessary.

    Parameters
    ----------
    obj : Callable
        A graph method.
    kwargs : dict
        The keyword arguments for the operation.
        These are usually the local variable inside the graph method.
    graph : Graph or None, optional
        The graph object can be derived from the `__self__` attribute of the method.
        But in the case where `__self__` might not be the actual graph object,
        one can pass it explicitly.
    name : str or None, optional
        Often the operation name is the same as the method name. If not, one can overwrite it using
        this parameter. For example, nodes in the random namespace.

    Returns
    -------
    Operation
        The newly created operation.
    """
    # obj should be MethodType, but mypy has trouble handling MethodType and Callable.
    graph = graph or obj.__self__  # type: ignore
    expected_kwargs = {
        key: kwargs[key] for key in obj.__annotations__.keys() if key != "return"
    }
    operation_name = name or obj.__name__
    return Operation(graph, operation_name, **expected_kwargs)
