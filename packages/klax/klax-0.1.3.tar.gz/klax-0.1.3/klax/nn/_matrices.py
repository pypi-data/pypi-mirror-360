# Copyright 2025 The Klax Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Implementations of (constrained) matrix-valued functions.

The functions have the form:
    A: R^n |-> R^(..., N, M)
"""

from collections.abc import Callable, Sequence
from typing import Any, Literal, cast

import equinox as eqx
import jax
import jax.numpy as jnp
from jax.nn.initializers import Initializer, he_normal, variance_scaling, zeros
from jaxtyping import Array, PRNGKeyArray

from .._misc import default_floating_dtype
from .._wrappers import (
    ContainsUnwrappablesError,
    SkewSymmetric,
    contains_unwrappables,
)
from ._mlp import MLP

type AtLeast2DTuple[T] = tuple[T, T, *tuple[T, ...]]


class Matrix(eqx.Module):
    """An unconstrained matrix-valued function based on an MLP.

    The MLP maps to a vector of elements which is transformed into a matrix.
    """

    mlp: MLP
    shape: AtLeast2DTuple[int] = eqx.field(static=True)

    def __init__(
        self,
        in_size: int | Literal["scalar"],
        shape: int | AtLeast2DTuple[int],
        width_sizes: Sequence[int],
        weight_init: Initializer = he_normal(),
        bias_init: Initializer = zeros,  # type: ignore
        activation: Callable = jax.nn.softplus,
        final_activation: Callable = lambda x: x,
        use_bias: bool = True,
        use_final_bias: bool = True,
        dtype: Any | None = None,
        *,
        key: PRNGKeyArray,
    ):
        """Initialize the `Matrix`.

        Args:
            in_size: The input size. The input to the module should be a vector
                of shape `(in_size,)`
            shape: The matrix shape. The output from the module will be an
                array with the specified `shape`. For square matrices a single
                integer N can be used as a shorthand for (N, N).
            width_sizes: The sizes of each hidden layer of the underlying MLP
                in a list.
            weight_init: The weight initializer of type
                `jax.nn.initializers.Initializer`. (Defaults to `he_normal()`)
            bias_init: The bias initializer of type
                `jax.nn.initializers.Initializer`. (Defaults to `zeros`)
            activation: The activation function after each hidden layer.
                (Defaults to ReLU).
            final_activation: The activation function after the output layer.
                (Defaults to the identity.)
            use_bias: Whether to add on a bias to internal layers.
                (Defaults to `True`.)
            use_final_bias: Whether to add on a bias to the final layer.
                (Defaults to `True`.)
            dtype: The dtype to use for all the weights and biases in this MLP.
                (Defaults to either `jax.numpy.float32` or `jax.numpy.float64`
                depending on whether JAX is in 64-bit mode.)
            key: A `jax.random.PRNGKey` used to provide randomness for
                parameter initialisation. (Keyword only argument.)

        Note:
            Note that `in_size` also supports the string `"scalar"` as a
            special value. In this case the input to the module should be of
            shape `()`.

        """
        shape = shape if isinstance(shape, tuple) else (shape, shape)

        out_size = int(jnp.prod(jnp.array(shape)))
        self.shape = shape
        self.mlp = MLP(
            in_size,
            out_size,
            width_sizes,
            weight_init,
            bias_init,
            activation,
            final_activation,
            use_bias,
            use_final_bias,
            dtype,
            key=key,
        )

    def __call__(self, x: Array) -> Array:
        """Forward pass through `Matrix`.

        Args:
            x: The input. Should be a JAX array of shape ``(in_size,)``. (Or
                shape ``()`` if ``in_size="scalar"``.)

        Returns:
            A JAX array of shape ``shape``.

        """
        return self.mlp(x).reshape(self.shape)


class ConstantMatrix(eqx.Module):
    """A constant, unconstrained matrix.

    It is a wrapper around a constant array that implements the matrix-valued
    function interface.
    """

    array: Array
    shape: AtLeast2DTuple[int] = eqx.field(static=True)

    def __init__(
        self,
        shape: int | AtLeast2DTuple[int],
        init: Initializer = variance_scaling(
            scale=1, mode="fan_avg", distribution="normal"
        ),
        dtype: Any | None = None,
        *,
        key: PRNGKeyArray,
    ):
        """Initialize the `ConstantMatrix`.

        Args:
            shape: The matrix shape. The output from the module will be a Array
                with sthe specified `shape`. For square matrices a single
                integer N can be used as a shorthand for (N, N).
            init: The array initializer of type
                `jax.nn.initializers.Initializer`. (Defaults to
                `variance_scaling(scale=1, mode="fan_avg", distribution="normal")`.)
            dtype: The dtype to use for all the weights and biases in this MLP.
                (Defaults to either `jax.numpy.float32` or `jax.numpy.float64`
                depending on whether JAX is in 64-bit mode.)
            key: A `jax.random.PRNGKey` used to provide randomness for
                parameter initialisation. (Keyword only argument.)

        """
        dtype = default_floating_dtype() if dtype is None else dtype
        self.shape = shape if isinstance(shape, tuple) else (shape, shape)
        self.array = init(key, self.shape, dtype)

    def __call__(self, x: Array) -> Array:
        """Forward pass through `ConstantMatrix`.

        Args:
            x: Ignored; provided for compatibility with the rest of the
                Matrix-valued function API.

        Returns:
            A JAX array of shape ``shape``.

        """
        return self.array


class SkewSymmetricMatrix(eqx.Module):
    """A kkew-symmetric matrix-valued function based on an MLP.

    The MLP maps the input to a vector of elements that are transformed into a
    skew-symmetric matrix.
    """

    mlp: MLP
    shape: AtLeast2DTuple[int] = eqx.field(static=True)

    def __init__(
        self,
        in_size: int | Literal["scalar"],
        shape: int | AtLeast2DTuple[int],
        width_sizes: Sequence[int],
        weight_init: Initializer = he_normal(),
        bias_init: Initializer = zeros,  # type: ignore
        activation: Callable = jax.nn.softplus,
        final_activation: Callable = lambda x: x,
        use_bias: bool = True,
        use_final_bias: bool = True,
        dtype: Any | None = None,
        *,
        key: PRNGKeyArray,
    ):
        """Initialize the `SkewSymmetricMatrix`.

        Args:
            in_size: The input size. The input to the module should be a vector
                of shape `(in_size,)`
            shape: The matrix shape. The output from the module will be a Array
                with sthe specified `shape`. For square matrices a single
                integer N can be used as a shorthand for (N, N).
            width_sizes: The sizes of each hidden layer of the underlying MLP
                in a list.
            weight_init: The weight initializer of type
                `jax.nn.initializers.Initializer`. (Defaults to `he_normal()`)
            bias_init: The bias initializer of type
                `jax.nn.initializers.Initializer`. (Defaults to `zeros`)
            activation: The activation function after each hidden layer.
                (Defaults to `softplus`).
            final_activation: The activation function after the output layer.
                (Defaults to the identity.)
            use_bias: Whether to add on a bias to internal layers.
                (Defaults to `True`.)
            use_final_bias: Whether to add on a bias to the final layer.
                (Defaults to `True`.)
            dtype: The dtype to use for all the weights and biases in this MLP.
                (Defaults to either `jax.numpy.float32` or `jax.numpy.float64`
                depending on whether JAX is in 64-bit mode.)
            key: A `jax.random.PRNGKey` used to provide randomness for
                parameter initialisation. (Keyword only argument.)

        Note:
            Note that `in_size` also supports the string `"scalar"` as a
            special value. In this case the input to the module should be of
            shape `()`.

        """
        shape = shape if isinstance(shape, tuple) else (shape, shape)
        if shape[-1] != shape[-2]:
            raise ValueError(
                "The last two dimensions in shape must be equal for "
                "skew-symmetric matrices."
            )

        out_size = int(jnp.prod(jnp.array(shape)))
        self.shape = shape
        self.mlp = MLP(
            in_size,
            out_size,
            width_sizes,
            weight_init,
            bias_init,
            activation,
            final_activation,
            use_bias,
            use_final_bias,
            dtype,
            key=key,
        )

    def __call__(self, x: Array) -> Array:
        """Forward pass through `SkewSymmetricMatrix`.

        Args:
            x: The input. Should be a JAX array of shape ``(in_size,)``. (Or
                shape ``()`` if ``in_size="scalar"``.)

        Returns:
            A JAX array of shape ``shape``.

        """
        matrix = self.mlp(x).reshape(self.shape)
        return matrix - matrix.mT


class ConstantSkewSymmetricMatrix(eqx.Module):
    """A constant skew-symmetric matrix.

    It is a wrapper around a constant skew-symmetry-constraind array that
    implements the matrix-valued function interface.
    """

    array: SkewSymmetric
    shape: AtLeast2DTuple[int] = eqx.field(static=True)

    def __init__(
        self,
        shape: int | AtLeast2DTuple[int],
        init: Initializer = variance_scaling(
            scale=1, mode="fan_avg", distribution="normal"
        ),
        dtype: Any | None = None,
        *,
        key: PRNGKeyArray,
    ):
        """Initialize the `ConstantSkewSymmetricMatrix`.

        Args:
            shape: The matrix shape. The output from the module will be a Array
                with sthe specified `shape`. For square matrices a single
                integer N can be used as a shorthand for (N, N).
            init: The array initializer of type
                `jax.nn.initializers.Initializer`. (Defaults to
                `variance_scaling(scale=1, mode="fan_avg", distribution="normal")`.)
            dtype: The dtype to use for all the weights and biases in this MLP.
                (Defaults to either `jax.numpy.float32` or `jax.numpy.float64`
                depending on whether JAX is in 64-bit mode.)
            key: A `jax.random.PRNGKey` used to provide randomness for
                parameter initialisation. (Keyword only argument.)

        """
        dtype = default_floating_dtype() if dtype is None else dtype
        self.shape = shape if isinstance(shape, tuple) else (shape, shape)
        array = init(key, self.shape, dtype)
        self.array = SkewSymmetric(array)

    def __call__(self, x: Array) -> Array:
        """Forward pass through `ConstantSkewSymmetricMatrix`.

        Args:
            x: Ignored; provided for compatibility with the rest of the
                Matrix-valued function API.

        Returns:
            A JAX array of shape ``shape``.

        """
        if contains_unwrappables(self):
            raise ContainsUnwrappablesError(
                "Model must be finalized before calling, see `klax.finalize`."
            )
        array = cast(Array, self.array)
        return array


class SPDMatrix(eqx.Module):
    """A symmetric positive definite matrix-valued function based on an MLP.

    The output vector `v` of the MLP is mapped to a matrix `B`. The module's
    output is then computed via `A=B@B*`.
    """

    mlp: MLP
    shape: AtLeast2DTuple[int] = eqx.field(static=True)
    epsilon: float = eqx.field(static=True)

    def __init__(
        self,
        in_size: int | Literal["scalar"],
        shape: int | AtLeast2DTuple[int],
        width_sizes: Sequence[int],
        epsilon: float = 1e-6,
        weight_init: Initializer = he_normal(),
        bias_init: Initializer = zeros,  # type: ignore
        activation: Callable = jax.nn.softplus,
        final_activation: Callable = lambda x: x,
        use_bias: bool = True,
        use_final_bias: bool = True,
        dtype: Any | None = None,
        *,
        key: PRNGKeyArray,
    ):
        """Initialize the `SPDMatrix`.

        Args:
            in_size: The input size. The input to the module should be a vector
                of shape `(in_size,)`
            shape: The matrix shape. The output from the module will be a Array
                with sthe specified `shape`. For square matrices a single
                integer N can be used as a shorthand for (N, N).
            width_sizes: The sizes of each hidden layer of the underlying MLP
                in a list.
            epsilon: Small value that is added to the diagonal of the output
                matrix to ensure positive definiteness. If only positive
                semi-definiteness is required set `epsilon = 0.`
                (Defaults to `1e-6`)
            weight_init: The weight initializer of type
                `jax.nn.initializers.Initializer`. (Defaults to `he_normal()`)
            bias_init: The bias initializer of type
                `jax.nn.initializers.Initializer`. (Defaults to `zeros`)
            activation: The activation function after each hidden layer.
                (Defaults to `softplus`)
            final_activation: The activation function after the output layer.
                (Defaults to the identity.)
            use_bias: Whether to add on a bias to internal layers.
                (Defaults to `True`.)
            use_final_bias: Whether to add on a bias to the final layer.
                (Defaults to `True`.)
            dtype: The dtype to use for all the weights and biases in this MLP.
                (Defaults to either `jax.numpy.float32` or `jax.numpy.float64`
                depending on whether JAX is in 64-bit mode.)
            key: A `jax.random.PRNGKey` used to provide randomness for
                parameter initialisation. (Keyword only argument.)

        Note:
            Note that `in_size` also supports the string `"scalar"` as a
            special value. In this case the input to the module should be of
            shape `()`.

        """
        shape = shape if isinstance(shape, tuple) else (shape, shape)
        if shape[-1] != shape[-2]:
            raise ValueError(
                "The last two dimensions in shape must be equal for "
                "symmetric matrices."
            )

        out_size = int(jnp.prod(jnp.array(shape)))
        self.shape = shape
        self.epsilon = epsilon
        self.mlp = MLP(
            in_size,
            out_size,
            width_sizes,
            weight_init,
            bias_init,
            activation,
            final_activation,
            use_bias,
            use_final_bias,
            dtype,
            key=key,
        )

    def __call__(self, x: Array) -> Array:
        """Forward pass through `SPDMatrix`.

        Args:
            x: The input. Should be a JAX array of shape ``(in_size,)``. (Or
                shape ``()`` if ``in_size="scalar"``.)

        Returns:
            A JAX array of shape ``shape``.

        """
        y = self.mlp(x).reshape(self.shape)
        a_matrix = y @ jnp.conjugate(y.mT)
        identity = jnp.broadcast_to(jnp.eye(self.shape[-1]), a_matrix.shape)
        return a_matrix + self.epsilon * identity


class ConstantSPDMatrix(eqx.Module):
    """A constant symmetric positive definite matrix-valued function.

    It is a wrapper around a constant symmetric postive semi-definite matrix
    with the matrix-valued function interface.
    """

    b_matrix: Array
    shape: AtLeast2DTuple[int] = eqx.field(static=True)
    epsilon: float = eqx.field(static=True)

    def __init__(
        self,
        shape: int | AtLeast2DTuple[int],
        epsilon: float = 1e-6,
        init: Initializer = variance_scaling(
            scale=1, mode="fan_avg", distribution="normal"
        ),
        dtype: Any | None = None,
        *,
        key: PRNGKeyArray,
    ):
        """Initialize the `ConstantSPDMatrix`.

        Args:
            shape: The matrix shape. The output from the module will be a
                Array with sthe specified `shape`. For square matrices a single
                integer N can be used as a shorthand for (N, N).
            epsilon: Small value that is added to the diagonal of the output
                matrix to ensure positive definiteness. If only positive
                semi-definiteness is required set `epsilon = 0.`
                (Defaults to `1e-6`)
            init: The initializer of type `jax.nn.initializers.Initializer` for
                the constant matrix `B` that produces the module's output via
                `A = B@B*`. (Defaults to `variance_scaling(scale=1,
                mode="fan_avg", distribution="normal")`.)
            dtype: The dtype to use for all the weights and biases in this MLP.
                (Defaults to either `jax.numpy.float32` or `jax.numpy.float64`
                depending on whether JAX is in 64-bit mode.)
            key: A `jax.random.PRNGKey` used to provide randomness for
                parameter initialisation. (Keyword only argument.)

        """
        shape = shape if isinstance(shape, tuple) else (shape, shape)
        if shape[-1] != shape[-2]:
            raise ValueError(
                "The last two dimensions in shape must be equal for "
                "symmetric matrices."
            )

        self.shape = shape
        self.epsilon = epsilon
        self.b_matrix = init(key, shape, dtype)

    def __call__(self, x: Array) -> Array:
        """Forward pass through `ConstantSPDMatrix`.

        Args:
            x: Ignored; provided for compatibility with the rest of the
                matrix-valued function API.

        Returns:
            A JAX array of shape `shape`.

        """
        a_matrix = self.b_matrix @ jnp.conjugate(self.b_matrix.mT)
        identity = jnp.broadcast_to(jnp.eye(self.shape[-1]), a_matrix.shape)
        return a_matrix + self.epsilon * identity
