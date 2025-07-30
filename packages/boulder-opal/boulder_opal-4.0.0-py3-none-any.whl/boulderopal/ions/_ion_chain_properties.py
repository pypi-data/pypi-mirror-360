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

from typing import Optional

import numpy as np

from boulderopal._core import obtain_ion_chain_properties_workflow
from boulderopal._validation import (
    ArrayT,
    Checker,
    ScalarT,
)


def obtain_ion_chain_properties(
    atomic_mass: float,
    ion_count: int,
    center_of_mass_frequencies: np.ndarray,
    wavevector: np.ndarray,
    laser_detuning: Optional[float] = None,
) -> dict:
    """
    Calculate the Lamb–Dicke parameters, frequencies (or relative detunings
    if a laser detuning is provided), and eigenvectors
    of the collective motional modes of an ion chain.

    Parameters
    ----------
    atomic_mass : float
        The atomic mass of the ions of the chain in atomic units.
        All ions in the chain are assumed to be of the same species.
    ion_count : int
        The number of ions in the chain, :math:`N`.
    center_of_mass_frequencies : np.ndarray
        The center-of-mass trapping frequencies in each direction.
        Must contain three positive elements.
    wavevector : np.ndarray
        The laser difference angular wave vector (in rad/m) in each direction.
        Must contain three elements.
    laser_detuning : float or None, optional
        The detuning of the control laser.
        If not provided, the returned relative detunings represent the mode frequencies.

    Returns
    -------
    dict
        A dictionary containing the ion chain properties, with the following keys:

        ``lamb_dicke_parameters``
            A 3D array of shape ``(3, N, N)`` representing the Lamb–Dicke parameters of the ions.
            Its dimensions indicate, respectively, direction, mode, and ion.
        ``relative_detunings``
            A 2D array of shape ``(3, N)`` representing the mode frequencies
            (or relative detunings if a laser detuning is provided).
            Its dimensions indicate, respectively, direction and mode.
        ``eigenvectors``
            A 3D array of shape ``(3, N, N)`` representing the eigenvectors of each mode.
            Its dimensions indicate, respectively, direction, mode, and ion.
        ``metadata``
            Metadata associated with the calculation.
            No guarantees are made about the contents of this metadata dictionary;
            the contained information is intended purely to help interpret the results of the
            calculation on a one-off basis.

    See Also
    --------
    boulderopal.ions.ms_optimize :
        Find optimal pulses to perform Mølmer–Sørensen-type operations on trapped ions systems.
    boulderopal.ions.ms_simulate :
        Simulate a Mølmer–Sørensen-type operation on a trapped ions system.

    Notes
    -----
    The directions of input parameters and returned arrays are ordered as
    radial x-direction, radial y-direction, and axial z-direction, corresponding, respectively,
    to the unit vectors :math:`(1, 0, 0)`, :math:`(0, 1, 0)`, and :math:`(0, 0, 1)`.

    Examples
    --------
    Refer to the `How to optimize error-robust Mølmer–Sørensen gates for trapped ions
    <https://docs.q-ctrl.com/boulder-opal/user-guides/how-to-optimize-error-robust
    -molmer-sorensen-gates-for-trapped-ions>`_ user guide to find how to use this function.
    """

    center_of_mass_frequencies = (
        ArrayT.REAL("center_of_mass_frequencies")
        .ndim(1)
        .shape((3,))
        .gt(0)(center_of_mass_frequencies)
    )
    wavevector = ArrayT.REAL("wavevector").ndim(1).shape((3,))(wavevector)
    Checker.VALUE(
        not np.allclose(wavevector, 0),
        "At least one of the wavevector components must be non-zero.",
        {"wavevector": wavevector},
    )
    if laser_detuning is not None:
        laser_detuning = ScalarT.REAL("laser_detuning")(laser_detuning)

    return obtain_ion_chain_properties_workflow(
        atomic_mass=ScalarT.REAL("atomic_mass").gt(0)(atomic_mass),
        ion_count=ScalarT.INT("ion_count").gt(0)(ion_count),
        center_of_mass_frequencies=center_of_mass_frequencies,
        wavevector=wavevector,
        laser_detuning=laser_detuning,
    )
