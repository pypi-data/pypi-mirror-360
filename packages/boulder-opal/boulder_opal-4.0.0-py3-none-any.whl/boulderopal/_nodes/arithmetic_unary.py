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
    Union,
)

import numpy as np
from qctrlcommons.node.wrapper import Operation

from boulderopal._nodes.base import create_operation
from boulderopal._nodes.node_data import (
    Pwc,
    Stf,
    Tensor,
)
from boulderopal._nodes.utils import get_arraylike_shape
from boulderopal._nodes.validation import (
    Checker,
    ShapeT,
    number_or_shapeable,
    real_array,
    real_shapeable,
    shapeable,
)
from boulderopal._typing import Annotated
from boulderopal._validation import (
    pipe,
    validated,
)


def _create_flexible_unary_node_data(
    _operation: Operation,
    x: int | float | complex | np.ndarray | Tensor | Pwc | Stf,
    name: Optional[str],
    value_shape_changer: Optional[Callable] = None,
) -> Tensor | Pwc | Stf:
    """
    Create the corresponding dataclass for nodes acting on Tensors, Pwcs, and Stfs
    implementing unary functions.

    Parameters
    ----------
    _operation : Operation
        The operation to implement.
    x : number or np.ndarray or Tensor or Pwc or Stf
        The object on which the operation acts.
    name : str or None
        The name of the node.
    value_shape_changer : Callable[[tuple], tuple], optional
        Callable that transforms the original shape of the object into the shape after the operation
        is applied. Defaults to an identity operation, that is to say, to not change the shape.

    Returns
    -------
    Tensor or Pwc or Stf
        The operation acting on the object.
    """

    # By default don't change shapes.
    def get_value_shape(shape: tuple[int, ...]) -> tuple[int, ...]:
        if value_shape_changer is None:
            return shape
        return value_shape_changer(shape)

    if isinstance(x, Stf):
        Checker.VALUE(
            name is None, "You can't assign a name to an Stf node.", {"name": name}
        )
        return Stf(
            _operation,
            value_shape=get_value_shape(x.value_shape),
            batch_shape=x.batch_shape,
        )

    if isinstance(x, Pwc):
        return Pwc(
            _operation,
            value_shape=get_value_shape(x.value_shape),
            durations=x.durations,
            batch_shape=x.batch_shape,
        )
    shape = get_arraylike_shape(x)
    return Tensor(_operation, shape=get_value_shape(shape))


class ArithmeticUnaryGraph:  # pylint: disable=unused-argument, too-many-public-methods
    """
    Base class implementing unary arithmetic graph methods.
    """

    @validated
    def sqrt(
        self,
        x: Annotated[
            Union[float, complex, np.ndarray, Tensor, Pwc, Stf],
            pipe(number_or_shapeable),
        ],
        *,
        name: Optional[str] = None,
    ) -> Union[Tensor, Pwc, Stf]:
        r"""
        Calculate the element-wise square root of an object. This can be a number, an array,
        a tensor, or a time-dependent function in the form of a Pwc or an Stf.

        Parameters
        ----------
        x : number or np.ndarray or Tensor or Pwc or Stf
            The object whose square root you want to calculate, :math:`x`. For numbers, arrays, and
            tensors, the object is converted to a tensor and then the operation is applied. For
            functions of time (Pwcs and Stfs), the composition of the operation with the function
            is computed (that is, the operation is applied to the function values).
        name : str or None, optional
            The name of the node. You can only provide a name if the object is not an Stf.

        Returns
        -------
        Tensor or Pwc or Stf
            The element-wise square root, :math:`\sqrt{x}`, of the values or function you provided.
            The returned object is of the same kind as the one you provided, except if you provide a
            number or an np.ndarray in which case it's a Tensor.
        """
        operation = create_operation(self.sqrt, locals())
        return _create_flexible_unary_node_data(operation, x, name)

    @validated
    def sin(
        self,
        x: Annotated[
            Union[float, complex, np.ndarray, Tensor, Pwc, Stf],
            pipe(number_or_shapeable),
        ],
        *,
        name: Optional[str] = None,
    ) -> Union[Tensor, Pwc, Stf]:
        r"""
        Calculate the element-wise sine of an object. This can be a number, an array, a tensor,
        or a time-dependent function in the form of a Pwc or an Stf.

        Parameters
        ----------
        x : number or np.ndarray or Tensor or Pwc or Stf
            The object whose sine you want to calculate, :math:`x`. For numbers, arrays, and
            tensors, the object is converted to a tensor and then the operation is applied. For
            functions of time (Pwcs and Stfs), the composition of the operation with the function
            is computed (that is, the operation is applied to the function values).
        name : str or None, optional
            The name of the node. You can only provide a name if the object is not an Stf.

        Returns
        -------
        Tensor or Pwc or Stf
            The element-wise sine, :math:`\sin{x}`, of the values or function you provided.
            The returned object is of the same kind as the one you provided, except if you provide a
            number or an np.ndarray in which case it's a Tensor.
        """
        operation = create_operation(self.sin, locals())
        return _create_flexible_unary_node_data(operation, x, name)

    @validated
    def cos(
        self,
        x: Annotated[
            Union[float, complex, np.ndarray, Tensor, Pwc, Stf],
            pipe(number_or_shapeable),
        ],
        *,
        name: Optional[str] = None,
    ) -> Union[Tensor, Pwc, Stf]:
        r"""
        Calculate the element-wise cosine of an object. This can be a number, an array, a tensor,
        or a time-dependent function in the form of a Pwc or an Stf.

        Parameters
        ----------
        x : number or np.ndarray or Tensor or Pwc or Stf
            The object whose cosine you want to calculate, :math:`x`. For numbers, arrays, and
            tensors, the object is converted to a tensor and then the operation is applied. For
            functions of time (Pwcs and Stfs), the composition of the operation with the function
            is computed (that is, the operation is applied to the function values).
        name : str or None, optional
            The name of the node. You can only provide a name if the object is not an Stf.

        Returns
        -------
        Tensor or Pwc or Stf
            The element-wise cosine, :math:`\cos{x}`, of the values or function you provided.
            The returned object is of the same kind as the one you provided, except if you provide a
            number or an np.ndarray in which case it's a Tensor.
        """
        operation = create_operation(self.cos, locals())
        return _create_flexible_unary_node_data(operation, x, name)

    @validated
    def tan(
        self,
        x: Annotated[
            Union[float, complex, np.ndarray, Tensor, Pwc, Stf],
            pipe(number_or_shapeable),
        ],
        *,
        name: Optional[str] = None,
    ) -> Union[Tensor, Pwc, Stf]:
        r"""
        Calculate the element-wise tangent of an object. This can be a number, an array, a tensor,
        or a time-dependent function in the form of a Pwc or an Stf.

        Parameters
        ----------
        x : number or np.ndarray or Tensor or Pwc or Stf
            The object whose tangent you want to calculate, :math:`x`. For numbers, arrays, and
            tensors, the object is converted to a tensor and then the operation is applied. For
            functions of time (Pwcs and Stfs), the composition of the operation with the function
            is computed (that is, the operation is applied to the function values).
        name : str or None, optional
            The name of the node. You can only provide a name if the object is not an Stf.

        Returns
        -------
        Tensor or Pwc or Stf
            The element-wise tangent, :math:`\tan{x}`, of the values or function you provided.
            The returned object is of the same kind as the one you provided, except if you provide a
            number or an np.ndarray in which case it's a Tensor.
        """
        operation = create_operation(self.tan, locals())
        return _create_flexible_unary_node_data(operation, x, name)

    @validated
    def sinh(
        self,
        x: Annotated[
            Union[float, complex, np.ndarray, Tensor, Pwc, Stf],
            pipe(number_or_shapeable),
        ],
        *,
        name: Optional[str] = None,
    ) -> Union[Tensor, Pwc, Stf]:
        r"""
        Calculate the element-wise hyperbolic sine of an object. This can be a number, an array,
        a tensor, or a time-dependent function in the form of a Pwc or an Stf.

        Parameters
        ----------
        x : number or np.ndarray or Tensor or Pwc or Stf
            The object whose hyperbolic sine you want to calculate, :math:`x`.
            For numbers, arrays, and tensors, the object is converted to a tensor and
            then the operation is applied.
            For functions of time (Pwcs and Stfs), the composition of the operation with the
            function is computed (that is, the operation is applied to the function values).
        name : str or None, optional
            The name of the node. You can only provide a name if the object is not an Stf.

        Returns
        -------
        Tensor or Pwc or Stf
            The element-wise hyperbolic sine, :math:`\sinh{x}`, of the values or function you
            provided.
            The returned object is of the same kind as the one you provided, except if you provide a
            number or an np.ndarray in which case it's a Tensor.
        """
        operation = create_operation(self.sinh, locals())
        return _create_flexible_unary_node_data(operation, x, name)

    @validated
    def cosh(
        self,
        x: Annotated[
            Union[float, complex, np.ndarray, Tensor, Pwc, Stf],
            pipe(number_or_shapeable),
        ],
        *,
        name: Optional[str] = None,
    ) -> Union[Tensor, Pwc, Stf]:
        r"""
        Calculate the element-wise hyperbolic cosine of an object. This can be a number, an array,
        a tensor, or a time-dependent function in the form of a Pwc or an Stf.

        Parameters
        ----------
        x : number or np.ndarray or Tensor or Pwc or Stf
            The object whose hyperbolic cosine you want to calculate, :math:`x`.
            For numbers, arrays, and tensors, the object is converted to a tensor and
            then the operation is applied.
            For functions of time (Pwcs and Stfs), the composition of the operation with the
            function is computed (that is, the operation is applied to the function values).
        name : str or None, optional
            The name of the node. You can only provide a name if the object is not an Stf.

        Returns
        -------
        Tensor or Pwc or Stf
            The element-wise hyperbolic cosine, :math:`\cosh{x}`, of the values or function you
            provided. The returned object is of the same kind as the one you provided, except if you
            provide a number or an np.ndarray in which case it's a Tensor.
        """
        operation = create_operation(self.cosh, locals())
        return _create_flexible_unary_node_data(operation, x, name)

    @validated
    def tanh(
        self,
        x: Annotated[
            Union[float, complex, np.ndarray, Tensor, Pwc, Stf],
            pipe(number_or_shapeable),
        ],
        *,
        name: Optional[str] = None,
    ) -> Union[Tensor, Pwc, Stf]:
        r"""
        Calculate the element-wise hyperbolic tangent of an object. This can be a number, an array,
        a tensor, or a time-dependent function in the form of a Pwc or an Stf.

        Parameters
        ----------
        x : number or np.ndarray or Tensor or Pwc or Stf
            The object whose hyperbolic tangent you want to calculate, :math:`x`.
            For numbers, arrays, and tensors, the object is converted to a tensor and
            then the operation is applied.
            For functions of time (Pwcs and Stfs), the composition of the operation with the
            function is computed (that is, the operation is applied to the function values).
        name : str or None, optional
            The name of the node. You can only provide a name if the object is not an Stf.

        Returns
        -------
        Tensor or Pwc or Stf
            The element-wise hyperbolic tangent, :math:`\tanh{x}`, of the values or function you
            provided. The returned object is of the same kind as the one you provided, except if you
            provide a number or an np.ndarray in which case it's a Tensor.
        """
        operation = create_operation(self.tanh, locals())
        return _create_flexible_unary_node_data(operation, x, name)

    @validated
    def log(
        self,
        x: Annotated[
            Union[float, complex, np.ndarray, Tensor, Pwc, Stf],
            pipe(number_or_shapeable),
        ],
        *,
        name: Optional[str] = None,
    ) -> Union[Tensor, Pwc, Stf]:
        r"""
        Calculate the element-wise natural logarithm of an object. This can be a number, an array,
        a tensor, or a time-dependent function in the form of a Pwc or an Stf.

        Parameters
        ----------
        x : number or np.ndarray or Tensor or Pwc or Stf
            The object whose natural logarithm you want to calculate, :math:`x`.
            For numbers, arrays, and tensors, the object is converted to a tensor and then the
            operation is applied.
            For functions of time (Pwcs and Stfs), the composition of the operation with the
            function is computed (that is, the operation is applied to the function values).
        name : str or None, optional
            The name of the node. You can only provide a name if the object is not an Stf.

        Returns
        -------
        Tensor or Pwc or Stf
            The element-wise natural logarithm, :math:`\log{x}`, of the values or function you
            provided. The returned object is of the same kind as the one you provided, except if you
            provide a number or an np.ndarray in which case it's a Tensor.
        """
        operation = create_operation(self.log, locals())
        return _create_flexible_unary_node_data(operation, x, name)

    @validated
    def exp(
        self,
        x: Annotated[
            Union[float, complex, np.ndarray, Tensor, Pwc, Stf],
            pipe(number_or_shapeable),
        ],
        *,
        name: Optional[str] = None,
    ) -> Union[Tensor, Pwc, Stf]:
        r"""
        Calculate the element-wise exponential of an object. This can be a number, an array,
        a tensor, or a time-dependent function in the form of a Pwc or an Stf.

        Parameters
        ----------
        x : number or np.ndarray or Tensor or Pwc or Stf
            The object whose exponential you want to calculate, :math:`x`. For numbers, arrays,
            and tensors, the object is converted to a tensor and then the operation is applied. For
            functions of time (Pwcs and Stfs), the composition of the operation with the function
            is computed (that is, the operation is applied to the function values).
        name : str or None, optional
            The name of the node. You can only provide a name if the object is not an Stf.

        Returns
        -------
        Tensor or Pwc or Stf
            The element-wise exponential, :math:`e^{x}`, of the values or function you
            provided. The returned object is of the same kind as the one you provided, except if you
            provide a number or an np.ndarray in which case it's a Tensor.
        """
        operation = create_operation(self.exp, locals())
        return _create_flexible_unary_node_data(operation, x, name)

    @validated
    def negative(
        self,
        x: Annotated[
            Union[float, complex, np.ndarray, Tensor, Pwc, Stf],
            pipe(number_or_shapeable),
        ],
        *,
        name: Optional[str] = None,
    ) -> Union[Tensor, Pwc, Stf]:
        r"""
        Calculate the element-wise numerical negative value of an object. This can be a number,
        an array, a tensor, or a time-dependent function in the form of a Pwc or an Stf.

        Parameters
        ----------
        x : number or np.ndarray or Tensor or Pwc or Stf
            The object whose numerical negative value you want to calculate, :math:`x`. For numbers,
            arrays, and tensors, the object is converted to a tensor and then the operation is
            applied. For functions of time (Pwcs and Stfs), the composition of the operation with
            the function is computed (that is, the operation is applied to the function values).
        name : str or None, optional
            The name of the node. You can only provide a name if the object is not an Stf.

        Returns
        -------
        Tensor or Pwc or Stf
            The element-wise negation, :math:`-x`, of the values or function you
            provided. The returned object is of the same kind as the one you provided, except if you
            provide a number or an np.ndarray in which case it's a Tensor.
        """
        operation = create_operation(self.negative, locals())
        return _create_flexible_unary_node_data(operation, x, name)

    @validated
    def real(
        self,
        x: Annotated[
            Union[float, complex, np.ndarray, Tensor, Pwc, Stf],
            pipe(number_or_shapeable),
        ],
        *,
        name: Optional[str] = None,
    ) -> Union[Tensor, Pwc, Stf]:
        r"""
        Calculate the element-wise real part of an object. This can be a number, an array,
        a tensor, or a time-dependent function in the form of a Pwc or an Stf.

        Parameters
        ----------
        x : number or np.ndarray or Tensor or Pwc or Stf
            The object whose real part you want to calculate, :math:`x`. For numbers,
            arrays, and tensors, the object is converted to a tensor and then the operation is
            applied. For functions of time (Pwcs and Stfs), the composition of the operation with
            the function is computed (that is, the operation is applied to the function values).
        name : str or None, optional
            The name of the node. You can only provide a name if the object is not an Stf.

        Returns
        -------
        Tensor or Pwc or Stf
            The element-wise real part, :math:`\Re(x)`, of the values or function you provided. The
            returned object is a real object of the same kind as the one you provided, except if you
            provide a number or an np.ndarray in which case it's a Tensor.

        See Also
        --------
        Graph.complex_value : Create a complex object from its real and imaginary parts.
        Graph.imag : Imaginary part of a complex object.
        """
        operation = create_operation(self.real, locals())
        return _create_flexible_unary_node_data(operation, x, name)

    @validated
    def imag(
        self,
        x: Annotated[
            Union[float, complex, np.ndarray, Tensor, Pwc, Stf],
            pipe(number_or_shapeable),
        ],
        *,
        name: Optional[str] = None,
    ) -> Union[Tensor, Pwc, Stf]:
        r"""
        Calculate the element-wise imaginary part of an object. This can be a number, an array,
        a tensor, or a time-dependent function in the form of a Pwc or an Stf.

        Parameters
        ----------
        x : number or np.ndarray or Tensor or Pwc or Stf
            The object whose imaginary part you want to calculate, :math:`x`. For numbers,
            arrays, and tensors, the object is converted to a tensor and then the operation is
            applied. For functions of time (Pwcs and Stfs), the composition of the operation with
            the function is computed (that is, the operation is applied to the function values).
        name : str or None, optional
            The name of the node. You can only provide a name if the object is not an Stf.

        Returns
        -------
        Tensor or Pwc or Stf
            The element-wise imaginary part, :math:`\Im(x)`, of the values or function you provided.
            The returned object is a real object of the same kind as the one you provided, except if
            you provide a number or an np.ndarray in which case it's a Tensor.

        See Also
        --------
        Graph.complex_value : Create a complex object from its real and imaginary parts.
        Graph.real : Real part of a complex object.
        """
        operation = create_operation(self.imag, locals())
        return _create_flexible_unary_node_data(operation, x, name)

    @validated
    def abs(
        self,
        x: Annotated[
            Union[float, complex, np.ndarray, Tensor, Pwc, Stf],
            pipe(number_or_shapeable),
        ],
        *,
        name: Optional[str] = None,
    ) -> Union[Tensor, Pwc, Stf]:
        r"""
        Calculate the element-wise absolute value of an object. This can be a number, an array,
        a tensor, or a time-dependent function in the form of a Pwc or an Stf.

        Parameters
        ----------
        x : number or np.ndarray or Tensor or Pwc or Stf
            The object whose absolute value you want to calculate, :math:`x`. For numbers,
            arrays, and tensors, the object is converted to a tensor and then the operation is
            applied. For functions of time (Pwcs and Stfs), the composition of the operation with
            the function is computed (that is, the operation is applied to the function values).
        name : str or None, optional
            The name of the node. You can only provide a name if the object is not an Stf.

        Returns
        -------
        Tensor or Pwc or Stf
            The element-wise absolute value, :math:`\left|x\right|`, of the values or function you
            provided. The returned object is a real object of the same kind as the one you provided,
            except if you provide a number or an np.ndarray in which case it's a Tensor.

        See Also
        --------
        Graph.angle : Argument of a complex object.
        Graph.complex_value : Create a complex object from its real and imaginary parts.
        """
        operation = create_operation(self.abs, locals())
        return _create_flexible_unary_node_data(operation, x, name)

    @validated
    def angle(
        self,
        x: Annotated[
            Union[float, complex, np.ndarray, Tensor, Pwc, Stf],
            pipe(number_or_shapeable),
        ],
        *,
        name: Optional[str] = None,
    ) -> Union[Tensor, Pwc, Stf]:
        r"""
        Calculate the element-wise argument of an object. This can be a number, an array,
        a tensor, or a time-dependent function in the form of a Pwc or an Stf.

        Parameters
        ----------
        x : number or np.ndarray or Tensor or Pwc or Stf
            The object whose argument you want to calculate, :math:`x`. For numbers,
            arrays, and tensors, the object is converted to a tensor and then the operation is
            applied. For functions of time (Pwcs and Stfs), the composition of the operation with
            the function is computed (that is, the operation is applied to the function values).
        name : str or None, optional
            The name of the node. You can only provide a name if the object is not an Stf.

        Returns
        -------
        Tensor or Pwc or Stf
            The element-wise argument, :math:`\arg(x)`, of the values or function you provided. The
            returned object is a real object of the same kind as the one you provided, except if you
            provide a number or an np.ndarray in which case it's a Tensor.

        See Also
        --------
        Graph.abs : Absolute value of a complex object.
        Graph.complex_value : Create a complex object from its real and imaginary parts.
        """
        operation = create_operation(self.angle, locals())
        return _create_flexible_unary_node_data(operation, x, name)

    @validated
    def conjugate(
        self,
        x: Annotated[
            Union[float, complex, np.ndarray, Tensor, Pwc, Stf],
            pipe(number_or_shapeable),
        ],
        *,
        name: Optional[str] = None,
    ) -> Union[Tensor, Pwc, Stf]:
        r"""
        Calculate the element-wise complex conjugate of an object. This can be a number, an array,
        a tensor, or a time-dependent function in the form of a Pwc or an Stf.

        Parameters
        ----------
        x : number or np.ndarray or Tensor or Pwc or Stf
            The object whose complex conjugate you want to calculate, :math:`x`. For numbers,
            arrays, and tensors, the object is converted to a tensor and then the operation is
            applied. For functions of time (Pwcs and Stfs), the composition of the operation with
            the function is computed (that is, the operation is applied to the function values).
        name : str or None, optional
            The name of the node. You can only provide a name if the object is not an Stf.

        Returns
        -------
        Tensor or Pwc or Stf
            The element-wise complex conjugate, :math:`x^\ast`, of the values or function you
            provided. The returned object is of the same kind as the one you provided, except if you
            provide a number or an np.ndarray in which case it's a Tensor.

        See Also
        --------
        Graph.adjoint : Hermitian adjoint of an operator.
        """
        operation = create_operation(self.conjugate, locals())
        return _create_flexible_unary_node_data(operation, x, name)

    @validated
    def arcsin(
        self,
        x: Annotated[
            Union[float, np.ndarray, Tensor, Pwc, Stf],
            pipe(real_shapeable, after=real_array),
        ],
        *,
        name: Optional[str] = None,
    ) -> Union[Tensor, Pwc, Stf]:
        r"""
        Calculate the element-wise arcsine of an object. This can be a number, an array,
        a tensor, or a time-dependent function in the form of a Pwc or an Stf.

        Parameters
        ----------
        x : float or np.ndarray or Tensor or Pwc or Stf
            The object whose arcsine you want to calculate, :math:`x`. Must be real.
            For numbers, arrays, and tensors, the object is converted to a tensor and then
            the operation is applied.
            For functions of time (Pwcs and Stfs), the composition of the operation with the
            function is computed (that is, the operation is applied to the function values).
        name : str or None, optional
            The name of the node. You can only provide a name if the object is not an Stf.

        Returns
        -------
        Tensor or Pwc or Stf
            The element-wise arcsine, :math:`\arcsin{x}`, of the values or function you
            provided. Outputs will be in the range of :math:`[-\pi/2, \pi/2]`.
            The returned object is of the same kind as the one you provided, except if you
            provide a number or an np.ndarray in which case it's a Tensor.
        """
        operation = create_operation(self.arcsin, locals())
        return _create_flexible_unary_node_data(operation, x, name)

    @validated
    def arccos(
        self,
        x: Annotated[
            Union[float, np.ndarray, Tensor, Pwc, Stf],
            pipe(real_shapeable, after=real_array),
        ],
        *,
        name: Optional[str] = None,
    ) -> Union[Tensor, Pwc, Stf]:
        r"""
        Calculate the element-wise arccosine of an object. This can be a number, an array,
        a tensor, or a time-dependent function in the form of a Pwc or an Stf.

        Parameters
        ----------
        x : float or np.ndarray or Tensor or Pwc or Stf
            The object whose arccosine you want to calculate, :math:`x`. Must be real.
            For numbers, arrays, and tensors, the object is converted to a tensor and then
            the operation is applied.
            For functions of time (Pwcs and Stfs), the composition of the operation with the
            function is computed (that is, the operation is applied to the function values).
        name : str or None, optional
            The name of the node. You can only provide a name if the object is not an Stf.

        Returns
        -------
        Tensor or Pwc or Stf
            The element-wise arccosine, :math:`\arccos{x}`, of the values or function you
            provided. Outputs will be in the range of :math:`[0, \pi]`.
            The returned object is of the same kind as the one you provided, except if you
            provide a number or an np.ndarray in which case it's a Tensor.
        """
        operation = create_operation(self.arccos, locals())
        return _create_flexible_unary_node_data(operation, x, name)

    @validated
    def arctan(
        self,
        x: Annotated[
            Union[float, np.ndarray, Tensor, Pwc, Stf],
            pipe(real_shapeable, after=real_array),
        ],
        *,
        name: Optional[str] = None,
    ) -> Union[Tensor, Pwc, Stf]:
        r"""
        Calculate the element-wise arctangent of an object. This can be a number, an array,
        a tensor, or a time-dependent function in the form of a Pwc or an Stf.

        Parameters
        ----------
        x : float or np.ndarray or Tensor or Pwc or Stf
            The object whose arctangent you want to calculate, :math:`x`. Must be real.
            For numbers, arrays, and tensors, the object is converted to a tensor and then
            the operation is applied.
            For functions of time (Pwcs and Stfs), the composition of the operation with the
            function is computed (that is, the operation is applied to the function values).
        name : str or None, optional
            The name of the node. You can only provide a name if the object is not an Stf.

        Returns
        -------
        Tensor or Pwc or Stf
            The element-wise arctangent, :math:`\arctan{x}`, of the values or function you
            provided. Outputs will be in the range of :math:`[-\pi/2, \pi/2]`.
            The returned object is of the same kind as the one you provided, except if you
            provide a number or an np.ndarray in which case it's a Tensor.
        """
        operation = create_operation(self.arctan, locals())
        return _create_flexible_unary_node_data(operation, x, name)

    @validated
    def adjoint(
        self,
        x: Annotated[
            Union[np.ndarray, Tensor, Pwc, Stf], pipe(shapeable, after=ShapeT.MATRIX())
        ],
        *,
        name: Optional[str] = None,
    ) -> Union[Tensor, Pwc, Stf]:
        r"""
        Calculate the element-wise adjoint of the last two dimensions of an object.
        This can be a an array, a tensor, or a time-dependent function in the form of a
        Pwc or an Stf where values have at least two dimensions.

        Parameters
        ----------
        x : np.ndarray or Tensor or Pwc or Stf
            The object whose adjoint you want to calculate, :math:`X^\dagger`.
            Must be a matrix or a matrix-valued function.
            For arrays and tensors, the object is converted to a tensor and then
            the operation is applied. For functions of time (Pwcs and Stfs), the composition
            of the operation with the function is computed
            (that is, the operation is applied to the function values).
        name : str or None, optional
            The name of the node. You can only provide a name if the object is not an Stf.

        Returns
        -------
        Tensor or Pwc or Stf
            The element-wise adjoint, of the last two dimension of the given matrix or matrix-valued
            function.

        See Also
        --------
        Graph.conjugate : Conjugate of a complex object.
        Graph.transpose : Reorder the dimensions of a tensor.
        """

        def value_shape_changer(value_shape: tuple[int, ...]) -> tuple[int, ...]:
            *batch, x, y = value_shape  # Unpacking syntax is awesome.
            return (*batch, y, x)

        operation = create_operation(self.adjoint, locals())
        return _create_flexible_unary_node_data(operation, x, name, value_shape_changer)

    @validated
    def trace(
        self,
        x: Annotated[
            Union[np.ndarray, Tensor, Pwc, Stf], pipe(shapeable, after=ShapeT.MATRIX())
        ],
        *,
        name: Optional[str] = None,
    ) -> Union[Tensor, Pwc, Stf]:
        r"""
        Calculate the trace of an object. This can be a an array,
        a tensor, or a time-dependent function in the form of a Pwc or an Stf
        where values have at least two dimensions.
        The trace is calculated on the last two dimensions.

        Parameters
        ----------
        x : np.ndarray or Tensor or Pwc or Stf
            The object whose trace you want to calculate, :math:`\mathop{\mathrm{Tr}}(x)`.
            Must be a matrix or a matrix-valued function.
            For arrays and tensors, the object is converted to a tensor and then
            the operation is applied. For functions of time (Pwcs and Stfs), the composition
            of the operation with the function is computed
            (that is, the operation is applied to the function values).
        name : str or None, optional
            The name of the node. You can only provide a name if the object is not an Stf.

        Returns
        -------
        Tensor or Pwc or Stf
            The trace of the last two dimension of the given matrix or matrix-valued
            function. Outputs will have two fewer dimensions.

        See Also
        --------
        Graph.einsum : Tensor contraction via Einstein summation convention.
        """
        operation = create_operation(self.trace, locals())
        return _create_flexible_unary_node_data(
            operation, x, name, lambda value_shape: value_shape[:-2]
        )

    @validated
    def hermitian_part(
        self,
        x: Annotated[
            Union[np.ndarray, Tensor, Pwc, Stf],
            pipe(shapeable, after=ShapeT.OPERATOR()),
        ],
        *,
        name: Optional[str] = None,
    ) -> Union[Tensor, Pwc, Stf]:
        # pylint: disable=line-too-long
        r"""
        Calculate the Hermitian part of an object. This can be an array,
        a tensor, or a time-dependent function in the form of a Pwc or an Stf
        where values have at least two dimensions.
        The operation is applied on the last two dimensions, which must be equal to each other.

        Parameters
        ----------
        x : np.ndarray or Tensor or Pwc or Stf
            The object whose Hermitian part you want to calculate, :math:`\mathop{x}`.
            Must be a matrix or a matrix-valued function.
            For arrays and tensors, the object is converted to a tensor and then
            the operation is applied. For functions of time (Pwcs and Stfs), the composition
            of the operation with the function is computed
            (that is, the operation is applied to the function values).
        name : str or None, optional
            The name of the node. You can only provide a name if the object is not an Stf.

        Returns
        -------
        Tensor or Pwc or Stf
            The Hermitian part of the matrix or matrix-valued function,
            :math:`\frac{1}{2}(\mathop{x}+\mathop{x}^\dagger)`.
            Outputs will have the same dimension as the inputs.

        See Also
        --------
        Graph.adjoint : Hermitian adjoint of an operator.

        Examples
        --------
        Create a Hamiltonian from a non-Hermitian Pwc operator.

        >>> omega = graph.pwc(durations=np.array([0.5, 0.7]), values=np.array([0.2, 0.4]))
        >>> sigma_m = np.array([[0, 1], [0, 0]])
        >>> operator = omega * sigma_m
        >>> graph.hermitian_part(operator, name="hamiltonian")
        <Pwc: name="hamiltonian", operation_name="hermitian_part", value_shape=(2, 2), batch_shape=()>
        >>> result = bo.execute_graph(graph=graph, output_node_names="hamiltonian")
        >>> result["output"]["hamiltonian"]
        {
            'durations': array([0.5, 0.7]),
            'values': array([
                [[0. , 0.1], [0.1, 0. ]],
                [[0. , 0.2], [0.2, 0. ]]
                ]),
            'time_dimension': 0
        }

        See more examples in the `Simulate the dynamics of a single qubit using computational graphs
        <https://docs.q-ctrl.com/boulder-opal/tutorials/simulate-the-dynamics-of-a-single-qubit-
        using-computational-graphs>`_ tutorial.

        Create a Hamiltonian from a non-Hermitian Stf operator.

        >>> operator = stf_signal * np.array([[0, 1, 0], [0, 0, np.sqrt(2)], [0, 0, 0]])
        >>> hamiltonian = graph.hermitian_part(operator)
        >>> hamiltonian
        <Stf: operation_name="hermitian_part", value_shape=(3, 3), batch_shape=()>

        Create a Hermitian matrix from a non-Hermitian np.ndarray.

        >>> sigma_m = np.array([[0, 1], [0, 0]])
        >>> graph.hermitian_part(sigma_m, name="hamiltonian")
        <Tensor: name="hamiltonian", operation_name="hermitian_part", shape=(2, 2)>
        >>> result = bo.execute_graph(graph=graph, output_node_names="hamiltonian")
        >>> result["output"]["hamiltonian"]
        {'value': array([[0. , 0.5], [0.5, 0. ]])}
        """
        # pylint: enable=line-too-long
        operation = create_operation(self.hermitian_part, locals())
        return _create_flexible_unary_node_data(operation, x, name)
