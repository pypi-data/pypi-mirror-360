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

from dataclasses import asdict
from typing import Optional

import numpy as np

from boulderopal._core import reconstruct_noise_workflow
from boulderopal._validation import (
    ArrayT,
    Checker,
    nullable,
)
from boulderopal.noise_reconstruction._classes import (
    ALLOWED_NOISE_RECONSTRUCTION_METHODS,
    FilterFunction,
    NoiseReconstructionMethod,
    SVDEntropyTruncation,
    SVDFixedLengthTruncation,
)


def _check_filter_function_list(
    filter_functions_list: list[FilterFunction],
    filter_functions_name: str,
    control_count: int,
) -> None:
    """
    Check that all the filter functions for a given noise channel are valid.
    """
    Checker.TYPE(
        isinstance(filter_functions_list, list)
        and all(
            isinstance(filter_function, FilterFunction)
            for filter_function in filter_functions_list
        ),
        f"The {filter_functions_name} must be a list of FilterFunction.",
    )
    Checker.VALUE(
        len(filter_functions_list) == control_count,
        "The list of filter functions for a noise channel must have the"
        " same length as the infidelities.",
        {
            "len(infidelities)": control_count,
            f"len({filter_functions_name})": len(filter_functions_list),
        },
    )
    Checker.VALUE(
        all(
            filter_functions_list[0].sample_count == filter_function.sample_count
            for filter_function in filter_functions_list[1:]
        ),
        "All the filter functions associated with a noise channel must"
        " have the same number of samples.",
    )
    Checker.VALUE(
        all(
            np.allclose(
                filter_functions_list[0].frequencies, filter_function.frequencies
            )
            for filter_function in filter_functions_list[1:]
        ),
        "The sample frequencies of all the filter functions associated with"
        " a noise channel must be the same.",
    )


def _check_svd_fixed_length_truncation(
    method: SVDFixedLengthTruncation, control_count: int, total_sampled_frequencies: int
) -> None:
    """
    Perform additional validation for SVDFixedLengthTruncation.
    """
    if method.singular_value_count is not None:
        Checker.VALUE(
            method.singular_value_count <= control_count,
            "The singular value count for the SVD method with fixed length"
            " must be less than or equal to the number of infidelities.",
            {
                "singular_value_count": method.singular_value_count,
                "len(infidelities)": control_count,
            },
        )
        Checker.VALUE(
            method.singular_value_count <= total_sampled_frequencies,
            "The singular value count for the SVD method with fixed length"
            " must be less than or equal to the total number of frequencies sampled"
            " for the filter functions of each control.",
            {
                "singular_value_count": method.singular_value_count,
                "total sampled frequencies": total_sampled_frequencies,
            },
        )


def reconstruct(
    filter_functions: list[list[FilterFunction]],
    infidelities: np.ndarray,
    infidelity_uncertainties: Optional[np.ndarray] = None,
    method: Optional[NoiseReconstructionMethod] = None,
) -> dict:
    r"""
    Estimate the power spectral density (PSD) of noise processes affecting a quantum system.

    Use this function to obtain noise PSDs from measurements performed on
    your quantum system. You must provide the measurements as filter functions,
    which describe the controls applied to the system, and operational
    infidelities.

    Parameters
    ----------
    filter_functions : list[list[FilterFunction]]
        The filter functions associated with each control and noise. Each filter
        function represents the sensitivity of a set of controls to a certain
        noise. The placement in the outer list corresponds to the noise,
        while the inner list is organized by control. Note that at least one filter
        function must be present, and that the filter functions for each noise
        channel have to be sampled at the same frequencies.
    infidelities : np.ndarray
        The infidelities associated with the application of each control.
        It must contain at least one element, and all its values must be
        greater than or equal to 0, and less than or equal to 1.
    infidelity_uncertainties : np.ndarray or None, optional
        The uncertainty associated with each infidelity. The array must have the same
        length as the `infidelities`, and all values must be greater than or equal to
        0, and less than or equal to 1. Defaults to None, in which case no
        uncertainty is associated to the infidelities.
    method : NoiseReconstructionMethod or None, optional
        The method to be used in the noise reconstruction. Defaults to the
        singular value decomposition (SVD) method with entropy truncation at 0.5.

    Returns
    -------
    dict
        A dictionary containing the noise reconstruction result, with the following keys:

        ``output``
            A list with the spectral distributions of the reconstructed noises.
            Each list entry is a dictionary containing the power spectral densities of a noise
            (and the frequencies at which they are defined),
            presented in the same sequence as provided in the `filter_functions` argument.
            It might contain the estimated uncertainties for the spectral densities,
            if you provide infidelity uncertainties.

        ``metadata``
            Metadata associated with the calculation.
            No guarantees are made about the contents of this metadata dictionary;
            the contained information is intended purely to help interpret the results of the
            calculation on a one-off basis.

    Notes
    -----
    From the filter function theory [1]_, the operational infidelity for a given control
    sequence applied on a weak-noise-perturbed quantum system is the overlap between the
    noise power spectral density (PSD) and the corresponding filter functions:

    .. math::
        {\mathcal I}_j = \sum_{k = 1}^{N_{\mathrm{noise}}} \int {\mathrm d}f \,
        F_{jk}(f) S_k(f) ,

    where :math:`S_k(f)` is the PSD for the noise channel :math:`k`, :math:`F_{jk}(f)` is
    the filter function corresponding to the control sequence :math:`j` and the noise
    channel :math:`k`, and :math:`{\mathcal I}_j` is the measured infidelity after the
    control :math:`j` is applied to the system. Discretizing the integrals for all
    :math:`M` measurements gives the following linear equation:

    .. math::
        F'{\mathbf S} = {\mathbf I} ,

    where :math:`F' = [F'_1, \dots, F'_j, \dots, F'_{N_{\mathrm{noise}}}]`
    is a :math:`M \times K` matrix and each element :math:`F'_j` is a
    :math:`M \times K_j` matrix representing the sampled filter functions weighted by
    discretized frequency step for the noise channel :math:`j` and
    :math:`K \equiv \sum_{j=1}^{N_\mathrm{noise}} K_j`; noise PSD
    :math:`{\mathbf S} = [{\mathbf S}_1, \dots, {\mathbf S}_j \dots, {\mathbf S}_K]^\top`
    is a :math:`K \times 1` vector and each element :math:`{\mathbf S}_j` is a
    :math:`K_j \times 1` vector for noise channel :math:`j`; infidelity vector
    :math:`{\mathbf I} = [{\mathcal I}_1, {\mathcal I}_2, \dots, {\mathcal I}_M]^\top`
    is a :math:`M \times 1` vector. Given sampled filter functions and infidelities,
    this function gives an estimation of the noise PSD :math:`{\mathbf S}_{\mathrm{est}}`.
    If uncertainties are provided with infidelities, this function also returns the
    uncertainties in estimation.

    References
    ----------
    .. [1] `T. J. Green, J. Sastrawan, H. Uys, and M. J. Biercuk,
            New Journal of Physics 15, 095004 (2013).
            <https://doi.org/10.1088/1367-2630/15/9/095004>`_

    Examples
    --------
    Perform a simple noise reconstruction of one noise affecting frequency 2,
    using two pulses perfectly sensitive to frequencies 1 and 2:

    >>> filter_functions = [
    ...    [
    ...        bo.noise_reconstruction.FilterFunction(
    ...            frequencies=np.array([1, 2]), inverse_powers=np.array([1, 0])
    ...        ),
    ...        bo.noise_reconstruction.FilterFunction(
    ...            frequencies=np.array([1, 2]), inverse_powers=np.array([0, 1])
    ...        )
    ...    ]
    ... ]
    >>> result = bo.noise_reconstruction.reconstruct(
    ...    filter_functions=filter_functions, infidelities=np.array([0, 1])
    ... )
    >>> result["output"]
        [{'frequencies': array([1., 2.]), 'psd': array([0., 1.])}]

    See also the `How to perform noise spectroscopy on arbitrary noise channels
    <https://docs.q-ctrl.com/boulder-opal/user-guides/how-to-
    perform-noise-spectroscopy-on-arbitrary-noise-channels>`_ user guide.
    """
    infidelities = ArrayT.REAL("infidelities").ndim(1).ge(0).le(1)(infidelities)
    control_count = len(infidelities)
    Checker.VALUE(
        len(infidelities) > 1,
        "You must provide at least one infidelity.",
        {"infidelities": infidelities},
    )

    infidelity_uncertainties = nullable(
        ArrayT.REAL("infidelity_uncertainties")
        .ndim(1)
        .shape((control_count,))
        .ge(0)
        .le(1),
        infidelity_uncertainties,
    )

    Checker.TYPE(
        isinstance(filter_functions, list),
        "The filter functions must be passed as a list.",
        {"type(filter_functions)": type(filter_functions)},
    )
    Checker.VALUE(
        len(filter_functions) > 0,
        "The list of filter functions must have at least one element.",
    )

    # Generate two lists with noise_count elements each. One contains frequencies
    # as (noise_sample_count,) arrays; the other contains filter functions values,
    # as (sample_count, noise_sample_count) arrays.
    # Note that noise_sample_count can be different for different noises.
    noises_frequencies = []
    sampled_filter_functions = []
    for index, filter_functions_list in enumerate(filter_functions):
        _check_filter_function_list(
            filter_functions_list, f"filter_functions[{index}]", control_count
        )
        noises_frequencies.append(filter_functions_list[0].frequencies)
        sampled_filter_functions.append(
            np.array(
                [
                    filter_function.inverse_powers
                    for filter_function in filter_functions_list
                ]
            )
        )

    if method is None:
        method = SVDEntropyTruncation(rounding_threshold=0.5)

    Checker.TYPE(
        isinstance(method, ALLOWED_NOISE_RECONSTRUCTION_METHODS),
        f"Unrecognized method: {method}.",
    )

    # Additional validation for the Fixed-Length Truncation SVD.
    if isinstance(method, SVDFixedLengthTruncation):
        total_sampled_frequencies = sum(
            filter_function.sample_count for filter_function in filter_functions[:][0]
        )
        _check_svd_fixed_length_truncation(
            method=method,
            control_count=control_count,
            total_sampled_frequencies=total_sampled_frequencies,
        )

    return reconstruct_noise_workflow(
        method=asdict(method),
        noises_frequencies=noises_frequencies,
        filter_functions=sampled_filter_functions,
        infidelities=infidelities,
        infidelity_uncertainties=infidelity_uncertainties,
    )
