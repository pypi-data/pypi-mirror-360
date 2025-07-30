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
from typing import (
    Any,
    Generic,
    Optional,
    TypeVar,
)

import numpy as np

from boulderopal._validation import (
    ArrayT,
    Checker,
    ScalarT,
    nullable,
)
from boulderopal.superconducting._drives import (
    ComplexOptimizableConstant,
    ComplexOptimizableSignal,
    OptimizableCoefficient,
    RealOptimizableConstant,
    RealOptimizableSignal,
)

RealAtype = TypeVar(
    "RealAtype", int, float, np.ndarray, RealOptimizableConstant, RealOptimizableSignal
)
RealBtype = TypeVar(
    "RealBtype", int, float, np.ndarray, RealOptimizableConstant, RealOptimizableSignal
)
Coefficient = TypeVar(
    "Coefficient",
    int,
    float,
    complex,
    np.ndarray,
    RealOptimizableSignal,
    RealOptimizableConstant,
    ComplexOptimizableConstant,
    ComplexOptimizableSignal,
)


def validate_real_coefficient(value: Any, name: str) -> Any:
    """
    Ensure coefficient is real-valued.
    """
    if isinstance(value, (RealOptimizableSignal, RealOptimizableConstant)):
        return value
    try:
        try:
            return ScalarT.REAL(name)(value)
        except TypeError:
            return ArrayT.REAL(name)(value)
    except TypeError as err:
        # re-raise to throw a better error message.
        raise TypeError(
            f"The {name} must be real-valued. The supported types are scalar, array, "
            f"RealOptimizableConstant, and RealOptimizableSignal. type(name)={type(value)}"
        ) from err


def _validate_coefficient(value: Any, name: str) -> Any:
    if isinstance(value, OptimizableCoefficient):
        return value
    try:
        try:
            return ScalarT.NUMERIC(name)(value)
        except TypeError:
            try:
                return ArrayT.REAL(name)(value)
            except TypeError:
                return ArrayT.COMPLEX(name)(value)
    except TypeError as err:
        # re-raise to throw a better error message.
        raise TypeError(
            f"The {name} must be a number or OptimizableCoefficient. type(name)={type(value)}"
        ) from err


@dataclass
class Transmon(Generic[RealAtype, RealBtype, Coefficient]):
    """
    Class that stores all the physical system data for a transmon.

    Parameters
    ----------
    dimension : int
        Number of dimensions of the Hilbert space of the transmon.
        Must be at least 2.
    frequency : real or np.ndarray or RealOptimizableSignal or RealOptimizableConstant or None, \
                optional
        The frequency of the transmon, :math:`\\omega_t`.
        If not provided, it defaults to no frequency term.
    anharmonicity : real or np.ndarray or RealOptimizableSignal or RealOptimizableConstant \
                or None, optional
        The nonlinearity of the transmon, :math:`\\alpha`.
        If not provided, it defaults to no anharmonicity term.
    drive : real or complex or np.ndarray or RealOptimizableSignal or \
            RealOptimizableConstant or ComplexOptimizableSignal or \
            ComplexOptimizableConstant or None, optional
        The complex drive of the transmon, :math:`\\gamma_t`.
        If not provided, it defaults to no drive term.
    name : str, optional
        The identifier of the transmon that is used to link interaction terms to this transmon.
        Defaults to "transmon".

    See Also
    --------
    boulderopal.superconducting.Cavity :
        Class describing cavities in superconducting systems.
    boulderopal.superconducting.TransmonCavityInteraction :
        Class describing interactions between a transmon and a cavity.
    boulderopal.superconducting.TransmonTransmonInteraction :
        Class describing interactions between two transmons.

    Notes
    -----
    The Hamiltonian for the transmon is defined as

    .. math::
        H_\\mathrm{transmon} =
            \\omega_t b^\\dagger b
            + \\frac{\\alpha}{2} (b^\\dagger)^2 b^2
            + \\frac{1}{2} \\left(\\gamma_t b^\\dagger + H.c. \\right) ,

    where :math:`H.c.` indicates the Hermitian conjugate.
    All coefficients in the Hamiltonian are optional,
    and you should only pass those relevant to your system.
    """

    dimension: int
    frequency: Optional[RealAtype] = None
    anharmonicity: Optional[RealBtype] = None
    drive: Optional[Coefficient] = None
    name: str = "transmon"

    def __post_init__(self) -> None:
        self.dimension = ScalarT.INT("dimension").ge(2)(self.dimension)
        self.frequency = nullable(
            validate_real_coefficient, self.frequency, "frequency"
        )
        self.anharmonicity = nullable(
            validate_real_coefficient, self.anharmonicity, "anharmonicity"
        )
        self.drive = nullable(_validate_coefficient, self.drive, "drive")


@dataclass
class Cavity(Generic[RealAtype, RealBtype, Coefficient]):
    """
    Class that stores all the physical system data for a cavity.

    Parameters
    ----------
    dimension : int
        Number of dimensions of the Hilbert space of the cavity.
        Must be at least 2.
    frequency : real or np.ndarray or RealOptimizableSignal or RealOptimizableConstant, optional
        The frequency of the cavity or None, :math:`\\omega_c`.
        If not provided, it defaults to no frequency term.
    kerr_coefficient : real or np.ndarray or RealOptimizableSignal or \
            RealOptimizableConstant or None, optional
        The nonlinearity of the cavity, :math:`K`.
        If not provided, it defaults to no nonlinear term.
    drive : real or complex or np.ndarray or RealOptimizableSignal or \
            RealOptimizableConstant or ComplexOptimizableSignal or \
            ComplexOptimizableConstant or None, optional
        The complex drive of the cavity, :math:`\\gamma_c`.
        If not provided, it defaults to no drive term.
    name : str, optional
        The identifier of the cavity that is used to link interaction terms to this cavity.
        Defaults to "cavity".

    See Also
    --------
    boulderopal.superconducting.CavityCavityInteraction :
        Class describing interactions between two cavities.
    boulderopal.superconducting.Transmon :
        Class describing transmons in superconducting systems.
    boulderopal.superconducting.TransmonCavityInteraction :
        Class describing interactions between a transmon and a cavity.

    Notes
    -----
    The Hamiltonian for the cavity is defined as

    .. math::
        H_\\mathrm{cavity} =
            \\omega_c a^\\dagger a
            + \\frac{K}{2} (a^\\dagger)^2 a^2
            + \\frac{1}{2} \\left(\\gamma_c a^\\dagger + H.c. \\right) ,

    where :math:`H.c.` indicates the Hermitian conjugate.
    All coefficients in the Hamiltonian are optional,
    and you should only pass those relevant to your system.
    """

    dimension: int
    frequency: Optional[RealAtype] = None
    kerr_coefficient: Optional[RealBtype] = None
    drive: Optional[Coefficient] = None
    name: str = "cavity"

    def __post_init__(self) -> None:
        self.dimension = ScalarT.INT("dimension").ge(2)(self.dimension)
        self.frequency = nullable(
            validate_real_coefficient, self.frequency, "frequency"
        )
        self.kerr_coefficient = nullable(
            validate_real_coefficient, self.kerr_coefficient, "kerr_coefficient"
        )
        self.drive = nullable(_validate_coefficient, self.drive, "drive")


@dataclass
class TransmonTransmonInteraction(Generic[Coefficient]):
    """
    Class that stores all the physical system data for the interaction
    between two transmons.

    Parameters
    ----------
    transmon_names : tuple[str, str]
        The two names identifying the transmons in the interaction.
    effective_coupling : real or complex or np.ndarray or RealOptimizableSignal or \
            RealOptimizableConstant or ComplexOptimizableSignal or \
            ComplexOptimizableConstant or None, optional
        The effective coupling between the two transmons, :math:`g`.
        If not provided, it defaults to no effective coupling term.

    See Also
    --------
    boulderopal.superconducting.Transmon :
        Class describing transmons in superconducting systems.

    Notes
    -----
    The Hamiltonian for the interaction is defined as

    .. math::
        H_\\mathrm{transmon-transmon} = g b_1 b_2^\\dagger + H.c. .
    """

    transmon_names: tuple[str, str]
    effective_coupling: Optional[Coefficient]

    def __post_init__(self) -> None:
        Checker.VALUE(
            self.transmon_names[0] != self.transmon_names[1],
            "The names of the two transmons must be different.",
            {"transmon_names": self.transmon_names},
        )
        self.effective_coupling = nullable(
            _validate_coefficient, self.effective_coupling, "effective_coupling"
        )


@dataclass
class TransmonCavityInteraction(Generic[RealAtype, Coefficient]):
    """
    Class that stores all the physical system data for the interaction
    between a transmon and a cavity.

    Parameters
    ----------
    dispersive_shift : real or np.ndarray or RealOptimizableSignal or \
            RealOptimizableConstant or None, optional
        The dispersive shift between the transmon and the cavity, :math:`\\chi`.
        You must provide either a dispersive shift or a Rabi coupling.
    rabi_coupling : real or complex or np.ndarray or RealOptimizableSignal or \
            RealOptimizableConstant or ComplexOptimizableSignal or \
            ComplexOptimizableConstant or None, optional
        The strength of the Rabi coupling between the transmon and the cavity, :math:`\\Omega`.
        You must provide either a dispersive shift or a Rabi coupling.
    transmon_name : str, optional
        The name identifying the transmon in the interaction.
        Defaults to "transmon".
    cavity_name : str, optional
        The name identifying the cavity in the interaction.
        Defaults to "cavity".

    See Also
    --------
    boulderopal.superconducting.Cavity :
        Class describing cavities in superconducting systems.
    boulderopal.superconducting.Transmon :
        Class describing transmons in superconducting systems.

    Notes
    -----
    The Hamiltonian for the interaction is defined as

    .. math:: H_\\mathrm{transmon-cavity} = \\chi a^\\dagger a b^\\dagger b ,

    or as

    .. math:: H_\\mathrm{transmon-cavity} = \\Omega a b^\\dagger + H.c. ,

    where :math:`H.c.` indicates the Hermitian conjugate.
    """

    dispersive_shift: Optional[RealAtype] = None
    rabi_coupling: Optional[Coefficient] = None
    transmon_name: str = "transmon"
    cavity_name: str = "cavity"

    def __post_init__(self) -> None:
        Checker.VALUE(
            (self.dispersive_shift is None) ^ (self.rabi_coupling is None),  # xor
            "You must provide either a dispersive shift or a Rabi coupling.",
            {
                "dispersive_shift": self.dispersive_shift,
                "rabi_coupling": self.rabi_coupling,
            },
        )
        self.dispersive_shift = nullable(
            validate_real_coefficient, self.dispersive_shift, "dispersive_shift"
        )
        self.rabi_coupling = nullable(
            _validate_coefficient, self.rabi_coupling, "rabi_coupling"
        )


@dataclass
class CavityCavityInteraction(Generic[RealAtype]):
    r"""
    Class that stores all the physical system data for the interaction
    between two cavities.

    Parameters
    ----------
    cavity_names : tuple[str, str]
        The two names identifying the cavities in the interaction.
    cross_kerr_coefficient : real or np.ndarray or RealOptimizableSignal or RealOptimizableConstant
        The cross-Kerr coefficient between the two cavities, :math:`K_{12}`.
        If not provided, it defaults to no cross-Kerr term.

    See Also
    --------
    boulderopal.superconducting.Cavity :
        Class describing cavities in superconducting systems.

    Notes
    -----
    The Hamiltonian for the interaction is defined as

    .. math::
        H_\mathrm{cavity-cavity} = K_{12} a_1^\dagger a_1 a_2^\dagger a_2 .
    """

    cavity_names: tuple[str, str]
    cross_kerr_coefficient: RealAtype

    def __post_init__(self) -> None:
        Checker.VALUE(
            self.cavity_names[0] != self.cavity_names[1],
            "The names of the two cavities must be different.",
            {"cavity_names": self.cavity_names},
        )
        self.cross_kerr_coefficient = validate_real_coefficient(
            self.cross_kerr_coefficient, "cross_kerr_coefficient"
        )
