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

from typing import (
    List,
    Optional,
)

import numpy as np

from boulderopal._nodes.base import create_operation
from boulderopal._nodes.node_data import Tensor
from boulderopal._validation import (
    Checker,
    validated,
)


class DifferentiationGraph:  # pylint: disable=unused-argument
    """
    Base class implementing differentiation graph methods.
    """

    @validated
    def hessian(
        self, tensor: Tensor, variables: List[Tensor], *, name: Optional[str] = None
    ) -> Tensor:
        r"""
        Calculate a single Hessian matrix for all the variables.

        The Hessian is a matrix containing all the second partial derivatives
        of the `tensor` with respect to the `variables`.

        Parameters
        ----------
        tensor : Tensor
            The real scalar tensor :math:`T` whose Hessian matrix you want to
            calculate.
        variables : list[Tensor]
            The list of real variables :math:`\{\theta_i\}` with respect to
            which you want to take the second partial derivatives of the
            tensor. If any of the tensors of the list is not scalar, this
            function treats each of the elements of the tensor as a different
            variable. It does this by flattening all tensors and concatenating
            them in the same sequence that you provided in this list.
        name : str or None, optional
            The name of the node.

        Returns
        -------
        Tensor
            A 2D real Hessian matrix :math:`H` containing the second partial
            derivatives of the `tensor` :math:`T` with respect to the
            `variables` :math:`\{\theta_i\}`.

        Warnings
        --------
        This function currently doesn't support calculating a Hessian matrix for
        a graph which includes an `infidelity_pwc` node if it involves a Hamiltonian
        with degenerate eigenvalues at any segment. In that case, the function
        returns a `nan` Hessian matrix.

        Notes
        -----
        The :math:`(i,j)` element of the Hessian contains the partial
        derivative of the `tensor` with respect to the ith and the jth
        `variables`:

        .. math::
            H_{i,j} = \frac{\partial^2 T}{\partial \theta_i \partial \theta_j}.

        The variables :math:`\{\theta_i\}` follow the same sequence as the
        input list of `variables`. If some of the `variables` are not scalars,
        this function flattens them and concatenates them in the same order of
        the list of `variables` that you provided to create the sequence of
        scalar variables :math:`\{\theta_i\}`.

        If you choose a negative log-likelihood as the tensor :math:`T`, you
        can use this Hessian as an estimate of the Fisher information matrix.
        """
        Checker.VALUE(
            tensor.operation.is_scalar_tensor, "The tensor must be a scalar tensor."
        )
        variable_count = int(
            np.sum([np.prod(variable.shape) for variable in variables])
        )
        shape = (variable_count, variable_count)
        operation = create_operation(self.hessian, locals())
        return Tensor(operation, shape=shape)
