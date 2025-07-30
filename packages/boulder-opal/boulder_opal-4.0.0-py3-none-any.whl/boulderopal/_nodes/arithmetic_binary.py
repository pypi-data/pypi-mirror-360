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
from boulderopal._nodes.validation import (
    Checker,
    ShapeT,
    number_or_shapeable,
    real_array,
    real_shapeable,
)
from boulderopal._typing import Annotated
from boulderopal._validation import (
    pipe,
    validated,
)

from .node_data import (
    Pwc,
    Stf,
    Tensor,
)
from .utils import (
    get_arraylike_shape,
    get_broadcasted_shape,
    mesh_pwc_durations,
    validate_function_output_shapes,
    validate_tensor_and_function_output_shapes,
)


def _default_broadcast_validator(
    shape_x: tuple[int, ...], shape_y: tuple[int, ...], x: str, y: str
) -> tuple[int, ...]:
    return get_broadcasted_shape(
        shape_x, shape_y, message=f"The shapes of {x} and {y} are not broadcastable."
    )


def _create_flexible_binary_node_data(
    _operation: Operation,
    op_name: str,
    x: int | float | complex | np.ndarray | Tensor | Pwc | Stf,
    y: int | float | complex | np.ndarray | Tensor | Pwc | Stf,
    name: Optional[str],
    validate_value_shape: Callable = _default_broadcast_validator,
) -> Tensor | Pwc | Stf:
    """
    Create the corresponding dataclass for nodes acting on Tensors, Pwcs, and Stfs
    implementing binary functions.

    Parameters
    ----------
    _operation : Operation
        The operation to implement.
    op_name : str
        The name of the operation.
    x : number or np.ndarray or Tensor or Pwc or Stf
        The left operand.
    y : number or np.ndarray or Tensor or Pwc or Stf
        The right operand.
    name : str or None
        The name of the node.
    validate_value_shape : Callable[[tuple, tuple, str, str], tuple], optional
        Function that takes the value shapes of two Tensors, Pwcs,
        or Stfs (as well as their names), and returns the expected values
        shape of the output Tensor, Pwc, or Stf. The function
        shouldn't assume that the shapes are compatible, and raise an
        exception if they aren't. The names provided should be used to
        generate the error message.

    Returns
    -------
    Tensor or Pwc or Stf
        The operation acting on the object.
    """
    # operation(Pwc, Stf) or operation(Stf, Pwc)
    Checker.TYPE(
        not (isinstance(x, Pwc) and isinstance(y, Stf))
        and not (isinstance(x, Stf) and isinstance(y, Pwc)),
        f"You can't apply the {op_name} operation between a Pwc and an Stf.",
        {"x": x, "y": y},
    )

    # operation(Stf, Stf)
    if isinstance(x, Stf) and isinstance(y, Stf):
        Checker.VALUE(
            name is None, "You can't assign a name to an Stf node.", {"name": name}
        )

        batch_shape, value_shape = validate_function_output_shapes(
            x.batch_shape,
            x.value_shape,
            y.batch_shape,
            y.value_shape,
            validate_value_shape=validate_value_shape,
        )
        return Stf(_operation, value_shape=value_shape, batch_shape=batch_shape)

    # operation(Pwc, Pwc)
    if isinstance(x, Pwc) and isinstance(y, Pwc):
        Checker.VALUE(
            np.isclose(np.sum(x.durations), np.sum(y.durations)),
            "Both Pwc terms must have the same total duration.",
            {"x": x, "y": y},
        )

        batch_shape, value_shape = validate_function_output_shapes(
            x.batch_shape,
            x.value_shape,
            y.batch_shape,
            y.value_shape,
            validate_value_shape=validate_value_shape,
        )

        durations = mesh_pwc_durations([x, y])
        return Pwc(
            _operation,
            value_shape=value_shape,
            durations=durations,
            batch_shape=batch_shape,
        )

    # operation(Stf, ArrayLike) or operation(ArrayLike, Stf)
    if isinstance(x, Stf) or isinstance(y, Stf):
        Checker.VALUE(
            name is None, "You can't assign a name to an Stf node.", {"name": name}
        )

        if isinstance(x, Stf):
            f_batch_shape, f_value_shape = x.batch_shape, x.value_shape
            f_name = "x"
            t_shape = get_arraylike_shape(y)
            t_name = "y"
            tensor_first = False
        else:
            assert isinstance(y, Stf)
            t_shape = get_arraylike_shape(x)
            t_name = "x"
            f_batch_shape, f_value_shape = y.batch_shape, y.value_shape
            f_name = "y"
            tensor_first = True

        batch_shape, value_shape = validate_tensor_and_function_output_shapes(
            t_shape,
            f_batch_shape,
            f_value_shape,
            t_name,
            f_name,
            validate_value_shape=validate_value_shape,
            tensor_first=tensor_first,
        )

        return Stf(_operation, value_shape=value_shape, batch_shape=batch_shape)

    # operation(Pwc, ArrayLike) or operation(ArrayLike, Pwc)
    if isinstance(x, Pwc) or isinstance(y, Pwc):
        if isinstance(x, Pwc):
            f_batch_shape, f_value_shape = x.batch_shape, x.value_shape
            f_name = "x"
            durations = x.durations
            t_shape = get_arraylike_shape(y)
            t_name = "y"
            tensor_first = False
        else:
            assert isinstance(y, Pwc)
            t_shape = get_arraylike_shape(x)
            t_name = "x"
            f_batch_shape, f_value_shape = y.batch_shape, y.value_shape
            f_name = "y"
            durations = y.durations
            tensor_first = True

        batch_shape, value_shape = validate_tensor_and_function_output_shapes(
            t_shape,
            f_batch_shape,
            f_value_shape,
            t_name,
            f_name,
            validate_value_shape=validate_value_shape,
            tensor_first=tensor_first,
        )

        return Pwc(
            _operation,
            value_shape=value_shape,
            durations=durations,
            batch_shape=batch_shape,
        )

    # operation(ArrayLike, ArrayLike)
    shape = validate_value_shape(
        get_arraylike_shape(x), get_arraylike_shape(y), "x", "y"
    )
    return Tensor(_operation, shape=shape)


class ArithmeticBinaryGraph:  # pylint: disable=unused-argument
    """
    Base class implementing binary arithmetic graph methods.
    """

    @validated
    def add(
        self,
        x: Annotated[
            Union[float, complex, np.ndarray, Tensor, Pwc, Stf],
            pipe(number_or_shapeable),
        ],
        y: Annotated[
            Union[float, complex, np.ndarray, Tensor, Pwc, Stf],
            pipe(number_or_shapeable),
        ],
        *,
        name: Optional[str] = None,
    ) -> Union[Tensor, Pwc, Stf]:
        """
        Calculate the element-wise sum between numbers, np.ndarrays, Tensors, Pwcs,
        or Stfs. You can also use the arithmetic operator ``+`` to calculate their sum.

        Considering numbers and np.ndarrays as Tensors, if the two objects are of the same type,
        so is the returned object. If the objects have different types, Pwcs and Stfs can operate
        with a tensor (returning a Pwc or Stf, respectively).

        This operation supports broadcasting between the different objects.
        When operating a tensor-like object with an Stf or a Pwc, the time dimension of the
        latter is ignored.

        Parameters
        ----------
        x : number or np.ndarray or Tensor or Pwc or Stf
            The left summand, :math:`x`.
        y : number or np.ndarray or Tensor or Pwc or Stf
            The right summand, :math:`y`.
        name : str or None, optional
            The name of the node. You can only provide a name if neither `x` nor `y` are Stfs.

        Returns
        -------
        Tensor or Pwc or Stf
            The element-wise sum :math:`x+y`.
        """
        operation = create_operation(self.add, locals())
        return _create_flexible_binary_node_data(operation, "add", x, y, name)

    @validated
    def subtract(
        self,
        x: Annotated[
            Union[float, complex, np.ndarray, Tensor, Pwc, Stf],
            pipe(number_or_shapeable),
        ],
        y: Annotated[
            Union[float, complex, np.ndarray, Tensor, Pwc, Stf],
            pipe(number_or_shapeable),
        ],
        *,
        name: Optional[str] = None,
    ) -> Union[Tensor, Pwc, Stf]:
        """
        Calculate the element-wise difference between numbers, np.ndarrays, Tensors, Pwcs,
        or Stfs. You can also use the arithmetic operator ``-`` to calculate their difference.

        Considering numbers and np.ndarrays as Tensors, if the two objects are of the same type,
        so is the returned object. If the objects have different types, Pwcs and Stfs can operate
        with a tensor (returning a Pwc or Stf, respectively).

        This operation supports broadcasting between the different objects.
        When operating a tensor-like object with an Stf or a Pwc, the time dimension of the
        latter is ignored.

        Parameters
        ----------
        x : number or np.ndarray or Tensor or Pwc or Stf
            The minuend, :math:`x`.
        y : number or np.ndarray or Tensor or Pwc or Stf
            The subtrahend, :math:`y`.
        name : str or None, optional
            The name of the node. You can only provide a name if neither `x` nor `y` are Stfs.

        Returns
        -------
        Tensor or Pwc or Stf
            The element-wise difference :math:`x-y`.
        """
        operation = create_operation(self.subtract, locals())
        return _create_flexible_binary_node_data(operation, "subtract", x, y, name)

    @validated
    def multiply(
        self,
        x: Annotated[
            Union[float, complex, np.ndarray, Tensor, Pwc, Stf],
            pipe(number_or_shapeable),
        ],
        y: Annotated[
            Union[float, complex, np.ndarray, Tensor, Pwc, Stf],
            pipe(number_or_shapeable),
        ],
        *,
        name: Optional[str] = None,
    ) -> Union[Tensor, Pwc, Stf]:
        r"""
        Calculate the element-wise product between numbers, np.ndarrays, Tensors,
        Pwcs, or Stfs. You can also use the arithmetic operator ``*`` to calculate their product.

        Considering numbers and np.ndarrays as Tensors, if the two objects are of the same type,
        so is the returned object. If the objects have different types, Pwcs and Stfs can operate
        with a tensor (returning a Pwc or Stf, respectively).

        This operation supports broadcasting between the different objects.
        When operating a tensor-like object with an Stf or a Pwc, the time dimension of the
        latter is ignored.

        Parameters
        ----------
        x : number or np.ndarray or Tensor or Pwc or Stf
            The left factor, :math:`x`.
        y : number or np.ndarray or Tensor or Pwc or Stf
            The right factor, :math:`y`.
        name : str or None, optional
            The name of the node. You can only provide a name if neither `x` nor `y` are Stfs.

        Returns
        -------
        Tensor or Pwc or Stf
            The element-wise product :math:`x \times y`.
        """
        operation = create_operation(self.multiply, locals())
        return _create_flexible_binary_node_data(operation, "multiply", x, y, name)

    @validated
    def truediv(
        self,
        x: Annotated[
            Union[float, complex, np.ndarray, Tensor, Pwc, Stf],
            pipe(number_or_shapeable),
        ],
        y: Annotated[
            Union[float, complex, np.ndarray, Tensor, Pwc, Stf],
            pipe(number_or_shapeable),
        ],
        *,
        name: Optional[str] = None,
    ) -> Union[Tensor, Pwc, Stf]:
        """
        Calculate the element-wise division between numbers, np.ndarrays, Tensors, Pwcs,
        or Stfs. You can also use the arithmetic operator ``/`` to calculate their division.

        Considering numbers and np.ndarrays as Tensors, if the two objects are of the same type,
        so is the returned object. If the objects have different types, Pwcs and Stfs can operate
        with a tensor (returning a Pwc or Stf, respectively).

        This operation supports broadcasting between the different objects.
        When operating a tensor-like object with an Stf or a Pwc, the time dimension of the
        latter is ignored.

        Parameters
        ----------
        x : number or np.ndarray or Tensor or Pwc or Stf
            The numerator, :math:`x`.
        y : number or np.ndarray or Tensor or Pwc or Stf
            The denominator, :math:`y`.
        name : str or None, optional
            The name of the node. You can only provide a name if neither `x` nor `y` are Stfs.

        Returns
        -------
        Tensor or Pwc or Stf
            The element-wise division :math:`x/y`.

        See Also
        --------
        Graph.floordiv : Divide two values and take the floor of the result.
        """
        operation = create_operation(self.truediv, locals())
        return _create_flexible_binary_node_data(operation, "truediv", x, y, name)

    @validated
    def floordiv(
        self,
        x: Annotated[
            Union[float, np.ndarray, Tensor, Pwc, Stf],
            pipe(real_shapeable, after=real_array),
        ],
        y: Annotated[
            Union[float, np.ndarray, Tensor, Pwc, Stf],
            pipe(real_shapeable, after=real_array),
        ],
        *,
        name: Optional[str] = None,
    ) -> Union[Tensor, Pwc, Stf]:
        r"""
        Calculate the element-wise rounded-down division between real numbers, np.ndarrays, Tensors,
        Pwcs, or Stfs. You can also use the arithmetic operator ``//`` to calculate their floor
        division.

        Considering numbers and np.ndarrays as Tensors, if the two objects are of the same type,
        so is the returned object. If the objects have different types, Pwcs and Stfs can operate
        with a tensor (returning a Pwc or Stf, respectively).

        This operation supports broadcasting between the different objects.
        When operating a tensor-like object with an Stf or a Pwc, the time dimension of the
        latter is ignored.

        Parameters
        ----------
        x : number or np.ndarray or Tensor or Pwc or Stf
            The numerator, :math:`x`. Must be real-valued.
        y : number or np.ndarray or Tensor or Pwc or Stf
            The denominator, :math:`y`. Must be real-valued.
        name : str or None, optional
            The name of the node. You can only provide a name if neither `x` nor `y` are Stfs.

        Returns
        -------
        Tensor or Pwc or Stf
            The element-wise rounded-down division :math:`\lfloor x/y \rfloor`.

        See Also
        --------
        Graph.truediv : Divide two values.
        """
        operation = create_operation(self.floordiv, locals())
        return _create_flexible_binary_node_data(operation, "floordiv", x, y, name)

    @validated
    def pow(
        self,
        x: Annotated[
            Union[float, complex, np.ndarray, Tensor, Pwc, Stf],
            pipe(number_or_shapeable),
        ],
        y: Annotated[
            Union[float, complex, np.ndarray, Tensor, Pwc, Stf],
            pipe(number_or_shapeable),
        ],
        *,
        name: Optional[str] = None,
    ) -> Union[Tensor, Pwc, Stf]:
        """
        Calculate the element-wise power between numbers, np.ndarrays, Tensors, Pwcs,
        or Stfs. You can also use the arithmetic operator ``**`` to calculate their power.

        Considering numbers and np.ndarrays as Tensors, if the two objects are of the same type,
        so is the returned object. If the objects have different types, Pwcs and Stfs can operate
        with a tensor (returning a Pwc or Stf, respectively).

        This operation supports broadcasting between the different objects.
        When operating a tensor-like object with an Stf or a Pwc, the time dimension of the
        latter is ignored.

        Parameters
        ----------
        x : number or np.ndarray or Tensor or Pwc or Stf
            The base, :math:`x`.
        y : number or np.ndarray or Tensor or Pwc or Stf
            The exponent, :math:`y`.
        name : str or None, optional
            The name of the node. You can only provide a name if neither `x` nor `y` are Stfs.

        Returns
        -------
        Tensor or Pwc or Stf
            The element-wise power :math:`x^y`.

        Warnings
        --------
        This function considers that the zeroth power of zero (:math:`0^0`) is
        undefined. This means that you might see an error if you attempt to
        fetch an object that contains :math:`0^0`.
        """
        operation = create_operation(self.pow, locals())
        return _create_flexible_binary_node_data(operation, "pow", x, y, name)

    @validated
    def complex_value(
        self,
        x: Annotated[
            Union[float, np.ndarray, Tensor, Pwc, Stf],
            pipe(real_shapeable, after=real_array),
        ],
        y: Annotated[
            Union[float, np.ndarray, Tensor, Pwc, Stf],
            pipe(real_shapeable, after=real_array),
        ],
        *,
        name: Optional[str] = None,
    ) -> Union[Tensor, Pwc, Stf]:
        """
        Create element-wise complex values from real numbers, np.ndarrays, Tensors,
        Pwcs, or Stfs, that is, the real and imaginary parts.

        Considering numbers and np.ndarrays as Tensors, if the two objects are of the same type,
        so is the returned object. If the objects have different types, Pwcs and Stfs can operate
        with a tensor (returning a Pwc or Stf, respectively).

        This operation supports broadcasting between the different objects.
        When operating a tensor-like object with an Stf or a Pwc, the time dimension of the
        latter is ignored.

        Parameters
        ----------
        x : number or np.ndarray or Tensor or Pwc or Stf
            The real part, :math:`x`.
        y : number or np.ndarray or Tensor or Pwc or Stf
            The imaginary part, :math:`y`.
        name : str or None, optional
            The name of the node. You can only provide a name if neither `x` nor `y` are Stfs.

        Returns
        -------
        Tensor or Pwc or Stf
            The element-wise complex number :math:`x+iy`.

        See Also
        --------
        Graph.abs : Absolute value of a complex object.
        Graph.angle : Argument of a complex object.
        Graph.conjugate : Conjugate of a complex object.
        Graph.imag : Imaginary part of a complex object.
        Graph.real : Real part of a complex object.
        """
        operation = create_operation(self.complex_value, locals())
        return _create_flexible_binary_node_data(operation, "complex_value", x, y, name)

    @validated
    def matmul(
        self,
        x: Annotated[
            Union[np.ndarray, Tensor, Pwc, Stf],
            pipe(number_or_shapeable, after=ShapeT.MATRIX()),
        ],
        y: Annotated[
            Union[np.ndarray, Tensor, Pwc, Stf],
            pipe(number_or_shapeable, after=ShapeT.MATRIX()),
        ],
        *,
        name: Optional[str] = None,
    ) -> Union[Tensor, Pwc, Stf]:
        """
        Calculate the matrix multiplication between np.ndarrays, Tensors,
        Pwcs, or Stfs. You can also use the arithmetic operator ``@``
        to calculate their matrix multiplication.

        If any of the inputs is a Pwc or Stf, the output is also a
        Pwc or Stf (mixing Pwcs and Stfs is not supported).
        Otherwise, the output is a Tensor.

        This operation supports broadcasting between the batch dimensions of
        the two input objects. All the dimensions with the exception of the two
        innermost ones (where the matrix multiplication is performed) are
        considered batch dimensions.

        When operating a tensor-like object with an Stf or a Pwc, the time
        dimension of the latter is ignored.

        Parameters
        ----------
        x : np.ndarray or Tensor or Pwc or Stf
            The left multiplicand. It must be a matrix (or batch of matrices)
            and its last dimension must be the same as the second-to-last
            dimension of `y`.
        y : np.ndarray or Tensor or Pwc or Stf
            The right multiplicand. It must be a matrix (or batch of matrices)
            and its second-to-last dimension must be the same as the last
            dimension of `x`.
        name : str or None, optional
            The name of the node. You can only provide a name if neither `x`
            nor `y` are Stfs.

        Returns
        -------
        Tensor or Pwc or Stf
            The matrix product of the input objects. If any of the input
            objects is a Pwc or Stf, the returned objects has the same
            type. Otherwise, it is a Tensor.

        See Also
        --------
        Graph.einsum : Tensor contraction via Einstein summation convention.
        """

        def validate_value_shape(
            x_shape: tuple[int, ...], y_shape: tuple[int, ...], x_name: str, y_name: str
        ) -> tuple[int, ...]:
            trailing_shape = _default_broadcast_validator(
                x_shape[:-2], y_shape[:-2], x_name, y_name
            )
            Checker.VALUE(
                x_shape[-1] == y_shape[-2],
                "The last dimension of x must be equal to the second-to-last dimension of y.",
                {"x shape": x_shape, "y shape": y_shape},
            )

            return trailing_shape + (x_shape[-2], y_shape[-1])

        operation = create_operation(self.matmul, locals())
        return _create_flexible_binary_node_data(
            operation, "matmul", x, y, name, validate_value_shape
        )

    @validated
    def kron(
        self,
        x: Annotated[
            Union[np.ndarray, Tensor, Pwc, Stf],
            pipe(number_or_shapeable, after=ShapeT.MATRIX()),
        ],
        y: Annotated[
            Union[np.ndarray, Tensor, Pwc, Stf],
            pipe(number_or_shapeable, after=ShapeT.MATRIX()),
        ],
        *,
        name: Optional[str] = None,
    ) -> Union[Tensor, Pwc, Stf]:
        """
        Calculate the Kronecker product between np.ndarrays, Tensors,
        Pwcs, or Stfs.

        If any of the inputs is a Pwc or Stf, the output is also a
        Pwc or Stf (mixing Pwcs and Stfs is not supported).
        Otherwise, the output is a Tensor.

        This operation supports broadcasting between the batch dimensions of
        the two input objects. All the dimensions with the exception of the two
        innermost ones (where the Kronecker product is performed) are
        considered batch dimensions.

        When operating a tensor-like object with an Stf or a Pwc, the time
        dimension of the latter is ignored.

        Parameters
        ----------
        x : np.ndarray or Tensor or Pwc or Stf
            The left multiplicand. It must be a have at least two dimensions.
        y : np.ndarray or Tensor or Pwc or Stf
            The right multiplicand. It must be a have at least two dimensions.
        name : str or None, optional
            The name of the node. You can only provide a name if neither `x`
            nor `y` are Stfs.

        Returns
        -------
        Tensor or Pwc or Stf
            The Kronecker product of the input objects. If any of the input
            objects is a Pwc or Stf, the returned objects has the same
            type. Otherwise, it is a Tensor.

        See Also
        --------
        Graph.embed_operators : Embed operators into a larger Hilbert space.
        Graph.kronecker_product_list : Kronecker product of a list of operators.
        Graph.pauli_kronecker_product : Embed Pauli matrices into a larger Hilbert space.
        """

        def validate_value_shape(
            x_shape: tuple[int, ...], y_shape: tuple[int, ...], x_name: str, y_name: str
        ) -> tuple[int, ...]:
            trailing_shape = _default_broadcast_validator(
                x_shape[:-2], y_shape[:-2], x_name, y_name
            )
            return trailing_shape + (
                x_shape[-2] * y_shape[-2],
                x_shape[-1] * y_shape[-1],
            )

        operation = create_operation(self.kron, locals())
        return _create_flexible_binary_node_data(
            operation, "kron", x, y, name, validate_value_shape
        )
