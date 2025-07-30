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

from typing import Optional

import numpy as np

from boulderopal._nodes.base import create_operation
from boulderopal._nodes.validation import ShapeT
from boulderopal._typing import Annotated
from boulderopal._validation import (
    ArrayT,
    Checker,
    ScalarT,
    pipe,
    validated,
)

from .node_data import (
    FilterFunction,
    Pwc,
    Tensor,
)


def _check_filter_function_input_shapes(
    control_hamiltonian: Pwc,
    noise_operator: Pwc,
    projection_operator: Optional[np.ndarray],
) -> None:
    Checker.VALUE(
        noise_operator.value_shape == control_hamiltonian.value_shape,
        "The noise operator must have same dimension as the control Hamiltonian.",
        {
            "control_hamiltonian.value_shape": control_hamiltonian.value_shape,
            "noise_operator.value_shape": noise_operator.value_shape,
        },
    )

    if projection_operator is not None:
        Checker.VALUE(
            projection_operator.shape == control_hamiltonian.value_shape,
            "The projection operator must have the same dimension as the control Hamiltonian.",
            {
                "control_hamiltonian.value_shape": control_hamiltonian.value_shape,
                "projection_operator.shape": projection_operator.shape,
            },
        )


class FilterFunctionGraph:  # pylint: disable=unused-argument
    """
    Base class implementing filter function graph methods.
    """

    @validated
    def filter_function(
        self,
        control_hamiltonian: Annotated[Pwc, pipe(after=ShapeT.OPERATOR().no_batch())],
        noise_operator: Annotated[Pwc, pipe(after=ShapeT.OPERATOR().no_batch())],
        frequencies: Annotated[np.ndarray, pipe(ArrayT.REAL().ndim(1))],
        sample_count: Optional[Annotated[int, pipe(ScalarT.INT().gt(1))]] = 100,
        projection_operator: Optional[
            Annotated[
                np.ndarray,
                pipe(ArrayT.NUMERIC().ndim(2).square().hermitian().idempotent()),
            ]
        ] = None,
        *,
        name: Optional[str] = None,
    ) -> FilterFunction:
        r"""
        Evaluate the filter function for a control Hamiltonian and a noise operator
        at the given frequency elements.

        Parameters
        ----------
        control_hamiltonian : Pwc
            The control Hamiltonian :math:`H_\mathrm{c}(t)`.
        noise_operator : Pwc
            The noise operator :math:`N(t)`.
        frequencies : list or tuple or np.ndarray
            The elements in the frequency domain at which to return
            the values of the filter function.
        sample_count : int or None, optional
            The number of points in time, :math:`M`, to sample the control-frame noise operator.
            These samples are used to calculate the approximate Fourier integral efficiently.
            If None the piecewise Fourier integral is calculated exactly.
            Defaults to 100.
        projection_operator : np.ndarray or None, optional
            The projection operator :math:`P`. Defaults to the identity matrix.
        name : str or None, optional
            The name of the node.

        Returns
        -------
        ~graphs.FilterFunction
            The filter function.

        See Also
        --------
        Graph.frequency_domain_noise_operator :
            Control-frame noise operator in the frequency domain.

        Notes
        -----
        The filter function is defined as [1]_:

        .. math::
            F(f) = \frac{1}{\mathrm{Tr}(P)} \mathrm{Tr} \left(
            P \mathcal{F} \left\{ \tilde N^\prime(t) \right\}(f)
            \mathcal{F} \left\{ \tilde N^\prime(t) \right\}(f)^\dagger P \right),

        with the control-frame noise operator in the frequency domain

        .. math::
            \mathcal{F} \left\{ \tilde N^\prime(t) \right\}(f) = \int_0^\tau
            e^{-i 2\pi f t} \tilde N^\prime(t) \mathrm{d}t,

        where

        .. math::
            \tilde N^\prime(t) = \tilde N(t) - \frac{\mathrm{Tr}\left( P \tilde N(t)
            P \right)}{\mathrm{Tr}(P)} \mathbb{I}

        is the traceless control-frame noise operator in the time domain,

        .. math::
            \tilde N(t) = U_c^\dagger(t) N(t) U_c(t)

        is the control-frame noise operator in the time domain, and :math:`U_c(t)` is
        the time evolution induced by the control Hamiltonian.

        References
        ----------
        .. [1] `H. Ball, M. J. Biercuk, A. R. R. Carvalho, J. Chen, M. Hush,
                L. A. De Castro, L. Li, P. J. Liebermann, H. J. Slatyer, and C. Edmunds,
                Quantum Sci. Technol. 6, 044011 (2021).
                <https://doi.org/10.1088/2058-9565/abdca6>`_
        """

        _check_filter_function_input_shapes(
            control_hamiltonian, noise_operator, projection_operator
        )

        operation = create_operation(self.filter_function, locals())
        return FilterFunction(
            operation, frequencies=frequencies, exact=sample_count is None
        )

    @validated
    def frequency_domain_noise_operator(
        self,
        control_hamiltonian: Annotated[Pwc, pipe(after=ShapeT.OPERATOR().no_batch())],
        noise_operator: Annotated[Pwc, pipe(after=ShapeT.OPERATOR().no_batch())],
        frequencies: Annotated[np.ndarray, pipe(ArrayT.REAL().ndim(1))],
        sample_count: Optional[Annotated[int, pipe(ScalarT.INT().gt(1))]] = 100,
        projection_operator: Optional[
            Annotated[
                np.ndarray,
                pipe(ArrayT.NUMERIC().ndim(2).square().hermitian().idempotent()),
            ]
        ] = None,
        *,
        name: Optional[str] = None,
    ) -> Tensor:
        r"""
        Create a control-frame noise operator in the frequency domain for a control Hamiltonian
        and a noise operator at the given frequencies.

        Parameters
        ----------
        control_hamiltonian : Pwc
            The control Hamiltonian :math:`H_\mathrm{c}(t)`.
        noise_operator : Pwc
            The noise operator :math:`N(t)`.
        frequencies : list or tuple or np.ndarray
            The elements in the frequency domain at which to return
            the values of the filter function.
        sample_count : int or None, optional
            The number of points in time, :math:`M`, to sample the control-frame noise operator.
            These samples are used to calculate the approximate Fourier integral efficiently.
            If None the piecewise Fourier integral is calculated exactly.
            Defaults to 100.
        projection_operator : np.ndarray or None, optional
            The projection operator :math:`P`. Defaults to the identity matrix.
        name : str or None, optional
            The name of the node.

        Returns
        -------
        Tensor
            The noise operator in the frequency domain.

        See Also
        --------
        Graph.filter_function :
            The filter function.

        Notes
        -----
        The control-frame noise operator in the frequency domain
        is defined as the Fourier transform of the operator in the time domain [1]_:

        .. math::
            \mathcal{F} \left\{ \tilde N^\prime(t) \right\}(f) = \int_0^\tau
            e^{-i 2\pi f t} \tilde N^\prime(t) \mathrm{d}t,

        where

        .. math::
            \tilde N^\prime(t) = \tilde N(t) - \frac{\mathrm{Tr}\left( P \tilde N(t)
            P \right)}{\mathrm{Tr}(P)} \mathbb{I}

        is the traceless control-frame noise operator in the time domain,

        .. math::
            \tilde N(t) = U_c^\dagger(t) N(t) U_c(t)

        is the control-frame noise operator in the time domain, and :math:`U_c(t)` is
        the time evolution induced by the control Hamiltonian. If `sample_count` is
        set, the Fourier integral is approximated as

        .. math::
            \mathcal{F} \left\{ \tilde N^\prime(t) \right\}(f) \approx \sum_{n=0}^{M-1}
            \frac{\tau}{M} e^{-i 2\pi f n \tau/M}
            \langle \tilde N^\prime (n\tau/M) \rangle,

        where :math:`\tau` is the duration of the control Hamiltonian.

        References
        ----------
        .. [1] `H. Ball, M. J. Biercuk, A. R. R. Carvalho, J. Chen, M. Hush,
                L. A. De Castro, L. Li, P. J. Liebermann, H. J. Slatyer, and C. Edmunds,
                Quantum Sci. Technol. 6, 044011 (2021).
                <https://doi.org/10.1088/2058-9565/abdca6>`_
        """

        count = len(frequencies)
        _check_filter_function_input_shapes(
            control_hamiltonian, noise_operator, projection_operator
        )

        operation = create_operation(self.frequency_domain_noise_operator, locals())
        return Tensor(operation, shape=(count,) + control_hamiltonian.value_shape)
