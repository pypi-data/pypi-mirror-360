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
from abc import ABC
from dataclasses import (
    dataclass,
    field,
)
from typing import (
    Any,
    Optional,
)

import numpy as np

from boulderopal._validation import (
    ArrayT,
    Checker,
    ScalarT,
    nullable,
)


@dataclass
class FilterFunction:
    """
    A class to store information about the controls applied in the noise
    reconstruction process, in the form of filter functions.

    The filter function specifies how sensitive a set of controls is to a specific
    noise, at a certain frequency. Filter functions can be calculated using
    the ``execute_graph`` function together with the ``graph.filter_function``
    operator. The output of that operation can then be passed directly to this
    function.

    Parameters
    ----------
    frequencies : np.ndarray
        A 1D array of the frequencies where the filter function is sampled.
        The frequencies must be provided in ascending order.
    inverse_powers : np.ndarray
        A 1D arrays of the values of the filter function at the frequencies
        where it is sampled. Must have the same length as `frequencies`,
        and all its values must be greater or equal to zero.
    uncertainties : np.ndarray or None, optional
        The uncertainties associated with each sampled point of the filter
        function. These values are not used for noise reconstruction.
    """

    frequencies: np.ndarray
    inverse_powers: np.ndarray
    uncertainties: Optional[np.ndarray] = None

    def __post_init__(self) -> None:
        self.frequencies = ArrayT.REAL("frequencies").ndim(1)(self.frequencies)
        self.inverse_powers = (
            ArrayT.REAL("inverse_powers")
            .ndim(1)
            .ge(0)
            .shape(self.frequencies.shape, "same as the frequencies")(
                self.inverse_powers
            )
        )
        self.uncertainties = nullable(
            ArrayT.REAL("uncertainties")
            .ndim(1)
            .ge(0)
            .shape(self.inverse_powers.shape, "same as inverse_powers"),
            self.uncertainties,
        )
        Checker.VALUE(
            all(np.diff(self.frequencies) > 0),
            "The frequencies must be provided in ascending order.",
            {"frequencies": self.frequencies},
        )
        self._sample_count = len(self.frequencies)

    @property
    def sample_count(self) -> int:
        """
        The number of samples in the filter function.
        """
        return self._sample_count


@dataclass
class NoiseReconstructionMethod(ABC):
    """
    Base class for the noise reconstruction methods.
    """

    method_name: str

    def __setattr__(self, name: str, value: Any) -> None:
        if name == "method_name":
            raise RuntimeError(
                "Mutating the `method_name` of the optimizer is not allowed."
            )
        super().__setattr__(name, value)


@dataclass
class ConvexOptimization(NoiseReconstructionMethod):
    r"""
    Configuration for noise reconstruction with the convex optimization (CVX) method.

    Parameters
    ----------
    power_density_lower_bound : float
        The lower bound for the reconstructed power spectral densities.
        It must be greater than or equal to 0.
    power_density_upper_bound : float
        The upper bound for the reconstructed power spectral densities.
        It must be greater than the `power_density_lower_bound`.
    regularization_hyperparameter : float
        The regularization hyperparameter :math:`\lambda`.

    Notes
    -----
    The CVX method finds the estimation of the power spectral density (PSD) matrix
    :math:`{\mathbf S}` by solving the optimization problem:

    .. math::
        {\mathbf S}_{\mathrm{est}} = \mathrm{argmin}_{\textbf S} (\| F'{\mathbf S} -
        {\mathbf I} \|_2^2 + \lambda \| L_1 {\mathbf S} \|_2^2) ,

    where :math:`F^\prime` is the matrix of weighted filter functions and
    :math:`\| \bullet \|_2` denotes the Euclidean norm and :math:`L_1` is the
    first-order derivative operator defined as

    .. math::
        \begin{align}
            L_1 =
              \begin{bmatrix}
                -1 &      1 &         &    \\
                   & \ddots &  \ddots &     \\
                   &        &      -1 & 1    \\
              \end{bmatrix}_{(K - 1) \times K} .
        \end{align}

    :math:`\lambda` is a positive regularization hyperparameter which determines the
    smoothness of :math:`{\mathbf S}_{\mathrm{est}}`. If you provide uncertainties in
    measurements, this method calculates the uncertainties in estimation using a Monte
    Carlo method.
    """

    power_density_lower_bound: float
    power_density_upper_bound: float
    regularization_hyperparameter: float
    method_name: str = field(default="convex optimization", init=False)

    def __post_init__(self) -> None:
        self.power_density_lower_bound = ScalarT.REAL("power_density_lower_bound").ge(
            0
        )(self.power_density_lower_bound)

        self.power_density_upper_bound = ScalarT.REAL("power_density_upper_bound").gt(
            self.power_density_lower_bound, "power_density_lower_bound"
        )(self.power_density_upper_bound)

        self.regularization_hyperparameter = ScalarT.REAL(
            "regularization_hyperparameter"
        ).ge(0)(self.regularization_hyperparameter)


@dataclass
class SVDEntropyTruncation(NoiseReconstructionMethod):
    r"""
    Configuration for noise reconstruction with the singular value decomposition
    (SVD) method using entropy truncation.

    Parameters
    ----------
    rounding_threshold : float, optional
        The rounding threshold of the entropy, between 0 and 1 (inclusive).
        Defaults to 0.5.

    Notes
    -----
    The singular value decomposition (SVD) method first finds a low rank approximation
    of the matrix of weighted filter functions :math:`F^\prime`:

    .. math::
        F^\prime \approx U \Sigma V ,

    where matrices :math:`U` and :math:`V` satisfy that
    :math:`U^\dagger U = VV^\dagger = \mathbb{I}_{n_{\mathrm{sv}} \times n_{\mathrm{sv}}}`,
    and :math:`\Sigma` is a diagonal matrix of :math:`n_{\mathrm{sv}}` truncated
    singular values, which in the entropy truncation method are determined by
    the entropy of the singular values :math:`E`.

    The entropy truncation method calculates the value :math:`2^E` and rounds the
    value to an integer :math:`n_{\mathrm{sv}}`. When rounding the value
    :math:`2^E`, the floor of :math:`2^E` plus the rounding threshold that you
    chose is taken. Therefore a small value leads to rounding down, while a
    large value leads to rounding up. The :math:`n_{\mathrm{sv}}` is then used
    as the truncation value.

    The SVD method then estimates the noise power spectral density (PSD) :math:`\mathbf S` as:

    .. math::
        {\mathbf S}_{\mathrm{est}} = V^\dagger\Sigma^{-1}U^\dagger{\mathbf I} .

    This method calculates the uncertainties in estimation using error propagation if
    you provide measurement uncertainties.
    """

    rounding_threshold: float = 0.5
    method_name: str = field(default="SVD entropy truncation", init=False)

    def __post_init__(self) -> None:
        self.rounding_threshold = (
            ScalarT.REAL("rounding_threshold").ge(0).le(1)(self.rounding_threshold)
        )


@dataclass
class SVDFixedLengthTruncation(NoiseReconstructionMethod):
    r"""
    Configuration for noise reconstruction with the singular value decomposition
    (SVD) method using fixed-length truncation.

    Parameters
    ----------
    singular_value_count : int or None, optional
        The number of singular values to retain. It must be greater or equal to 1.
        Defaults to None, in which case no truncation is performed.

    Notes
    -----
    The singular value decomposition (SVD) method first finds a low rank approximation
    of the matrix of weighted filter functions :math:`F^\prime`:

    .. math::
        F^\prime \approx U \Sigma V ,

    where matrices :math:`U` and :math:`V` satisfy that
    :math:`U^\dagger U = VV^\dagger = \mathbb{I}_{n_{\mathrm{sv}} \times n_{\mathrm{sv}}}`,
    and :math:`\Sigma` is a diagonal matrix of :math:`n_{\mathrm{sv}}` truncated
    singular values, which are determined by the `singular_value_count` that you
    provided.

    The SVD method then estimates the noise power spectral density (PSD) :math:`\mathbf S` as:

    .. math::
        {\mathbf S}_{\mathrm{est}} = V^\dagger\Sigma^{-1}U^\dagger{\mathbf I} .

    This method calculates the uncertainties in estimation using error propagation if
    you provide measurement uncertainties.
    """

    singular_value_count: Optional[int] = None
    method_name: str = field(default="SVD fixed-length truncation", init=False)

    def __post_init__(self) -> None:
        self.singular_value_count = nullable(
            ScalarT.INT("singular_value_count").ge(1), self.singular_value_count
        )


ALLOWED_NOISE_RECONSTRUCTION_METHODS = (
    ConvexOptimization,
    SVDEntropyTruncation,
    SVDFixedLengthTruncation,
)
