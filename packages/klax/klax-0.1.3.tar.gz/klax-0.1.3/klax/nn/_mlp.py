# This file includes code from Equinox
#
#     https://github.com/patrick-kidger/equinox
#
# licensed under Apache 2.0. Changes were made to class `MLP`.
#
# Modifications copyright 2025 The Klax Authors.
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

from collections.abc import Callable, Sequence
from typing import Literal

import equinox as eqx
import jax
import jax.random as jrandom
from jax.nn.initializers import Initializer, he_normal, zeros
from jaxtyping import Array, PRNGKeyArray

from .._misc import default_floating_dtype
from .._wrappers import Constraint, Unwrappable
from ._linear import Linear


class MLP(eqx.Module, strict=True):
    """Standard Multi-Layer Perceptron; also known as a feed-forward network.

    This class is modified form [`equinox.nn.MLP`](https://docs.kidger.site/equinox/api/nn/mlp/#equinox.nn.MLP)
    to allow for custom initialization and different node numbers in the hidden
    layers. Hence, it may also be used for ecoder/decoder tasks.

    """

    layers: tuple[Linear, ...]
    activations: tuple[Callable, ...]
    final_activation: Callable
    use_bias: bool = eqx.field(static=True)
    use_final_bias: bool = eqx.field(static=True)
    in_size: int | Literal["scalar"] = eqx.field(static=True)
    out_size: int | Literal["scalar"] = eqx.field(static=True)
    width_sizes: tuple[int, ...] = eqx.field(static=True)

    def __init__(
        self,
        in_size: int | Literal["scalar"],
        out_size: int | Literal["scalar"],
        width_sizes: Sequence[int],
        weight_init: Initializer = he_normal(),
        bias_init: Initializer = zeros,
        activation: Callable = jax.nn.softplus,
        final_activation: Callable = lambda x: x,
        use_bias: bool = True,
        use_final_bias: bool = True,
        weight_wrap: type[Constraint] | type[Unwrappable[Array]] | None = None,
        bias_wrap: type[Constraint] | type[Unwrappable[Array]] | None = None,
        dtype: type | None = None,
        *,
        key: PRNGKeyArray,
    ):
        """Initialize MLP.

        Args:
            in_size: The input size. The input to the module should be a vector
                of shape `(in_features,)`.
            out_size: The output size. The output from the module will be a
                vector of shape `(out_features,)`.
            width_sizes: The sizes of each hidden layer in a list.
            weight_init: The weight initializer of type
                `jax.nn.initializers.Initializer`. (Defaults to he_normal().)
            bias_init: The bias initializer of type
                `jax.nn.initializers.Initializer`. (Defaults to zeros.)
            activation: The activation function after each hidden layer.
                (Defaults to `jax.nn.softplus`).
            final_activation: The activation function after the output layer.
                (Defaults to the identity.)
            use_bias: Whether to add on a bias to internal layers.
                (Defaults to `True`.)
            use_final_bias: Whether to add on a bias to the final layer.
                (Defaults to `True`.)
            weight_wrap: An optional wrapper that is passed to all weights.
            bias_wrap: An optional wrapper that is passed to all biases.
            dtype: The dtype to use for all the weights and biases in this MLP.
                Defaults to either `jax.numpy.float32` or `jax.numpy.float64`
                depending on whether JAX is in 64-bit mode.
            key: A `jax.random.PRNGKey` used to provide randomness for
                parameter initialisation. (Keyword only argument.)

        Note:
            Note that `in_size` also supports the string `"scalar"` as a
            special value. In this case the input to the module should be of
            shape `()`.

            Likewise `out_size` can also be a string `"scalar"`, in which case
            the output from the module will have shape `()`.

        """
        dtype = default_floating_dtype() if dtype is None else dtype
        width_sizes = tuple(width_sizes)

        self.in_size = in_size
        self.out_size = out_size
        self.width_sizes = width_sizes
        self.use_bias = use_bias
        self.use_final_bias = use_final_bias

        in_sizes = (in_size,) + width_sizes
        out_sizes = width_sizes + (out_size,)
        use_biases = len(width_sizes) * (use_bias,) + (use_final_bias,)
        keys = jrandom.split(key, len(out_sizes))
        self.layers = tuple(
            Linear(
                sin,
                sout,
                weight_init,
                bias_init,
                ub,
                weight_wrap,
                bias_wrap,
                dtype=dtype,
                key=key,
            )
            for sin, sout, ub, key in zip(
                in_sizes, out_sizes, use_biases, keys
            )
        )

        # In case `activation` or `final_activation` are learnt, then make a
        # separate copy of their weights for every neuron.
        activations = []
        for width in width_sizes:
            activations.append(
                eqx.filter_vmap(lambda: activation, axis_size=width)()
            )
        self.activations = tuple(activations)
        if out_size == "scalar":
            self.final_activation = final_activation
        else:
            self.final_activation = eqx.filter_vmap(
                lambda: final_activation, axis_size=out_size
            )()

    def __call__(self, x: Array, *, key: PRNGKeyArray | None = None) -> Array:
        """Forward pass through MLP.

        Args:
            x: A JAX array with shape `(in_size,)`. (Or shape `()` if
                `in_size="scalar"`.)
            key: Ignored; provided for compatibility with the rest of the
                Equinox API. (Keyword only argument.)

        Returns:
            A JAX array with shape `(out_size,)`. (Or shape `()` if
            `out_size="scalar"`.)

        """
        for i, (layer, activation) in enumerate(
            zip(self.layers[:-1], self.activations)
        ):
            x = layer(x)
            layer_activation = jax.tree.map(
                lambda x: x[i] if eqx.is_array(x) else x, activation
            )
            x = eqx.filter_vmap(lambda a, b: a(b))(layer_activation, x)
        x = self.layers[-1](x)
        if self.out_size == "scalar":
            x = self.final_activation(x)
        else:
            x = eqx.filter_vmap(lambda a, b: a(b))(self.final_activation, x)
        return x
