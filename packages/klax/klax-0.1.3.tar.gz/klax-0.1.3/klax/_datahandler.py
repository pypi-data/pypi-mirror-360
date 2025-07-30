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

"""Implements methods for handling data, such as batching and splitting."""

import typing
import warnings
from collections.abc import Generator, Sequence
from typing import Any, Protocol

import equinox as eqx
import jax
import jax.numpy as jnp
import jax.random as jr
import numpy as np
from jaxtyping import PRNGKeyArray, PyTree


def broadcast_and_get_size(
    data: PyTree[Any], batch_axis: PyTree[int | None]
) -> tuple[PyTree[int | None], int]:
    """Broadcast `batch_axis` to the same structure as `data` and get size.

    Args:
        data: PyTree of data.
        batch_axis: PyTree of the batch axis indices. `None` is used to
            indicate that the corresponding leaf or subtree in data does not
            have a batch axis. `batch_axis` must have the same structure as
            `data` or have `data` as a prefix.

    Raises:
        ValueError: If `batch_axis` is not a prefix of `data`.
        ValueError: If not all batch axes have the same size.

    Returns:
        Tuple of the broadcasted `batch_axis` and the `dataset_size`.

    """
    try:
        batch_axis = jax.tree.map(
            lambda a, d: jax.tree.map(eqx.if_array(a), d),
            batch_axis,
            data,
            is_leaf=lambda x: x is None,
        )
    except ValueError as e:
        raise ValueError(
            f"batch_axis must be a prefix of data. Original message: {e}"
        )

    dataset_sizes = jax.tree.map(
        lambda a, d: None if a is None else d.shape[a],
        batch_axis,
        data,
        is_leaf=lambda x: x is None,
    )
    dataset_sizes = jax.tree.leaves(dataset_sizes)
    if len(dataset_sizes) == 0:
        # No leaf in data has a batch dimension -> singelton data set
        dataset_size = 1
    else:
        if not all(b == dataset_sizes[0] for b in dataset_sizes[1:]):
            raise ValueError("All batched arrays must have equal batch sizes.")
        dataset_size = dataset_sizes[0]

    return batch_axis, dataset_size


@typing.runtime_checkable
class BatchGenerator(Protocol):
    def __call__(
        self,
        data: PyTree[Any],
        batch_size: int,
        batch_axis: PyTree[int | None],
        *,
        key: PRNGKeyArray,
    ) -> Generator[PyTree[Any], None, None]:
        raise NotImplementedError


def batch_data(
    data: PyTree[Any],
    batch_size: int = 32,
    batch_axis: PyTree[int | None] = 0,
    convert_to_numpy: bool = True,
    *,
    key: PRNGKeyArray,
) -> Generator[PyTree[Any], None, None]:
    """Create a `Generator` that draws subsets of data without replacement.

    The data can be any `PyTree` with `ArrayLike` leaves. If `batch_mask` is
    passed, batch axes (including `None` for no batching) can be specified for
    every leaf individualy.
    A generator is returned that indefinetly yields batches of data with size
    `batch_size`. Examples are drawn without replacement until the remaining
    dataset is smaller than `batch_size`, at which point the dataset will be
    reshuffeld and the process starts over.

    Example:
        This is an example for a nested `PyTree`, where the elements x and y
        have batch dimension along the first axis.

        ```python
        >>> import klax
        >>> import jax
        >>> import jax.numpy as jnp
        >>>
        >>> x = jnp.array([1., 2.])
        >>> y = jnp.array([[1.], [2.]])
        >>> data = (x, {"a": 1.0, "b": y})
        >>> batch_mask = (0, {"a": None, "b": 0})
        >>> iter_data = klax.batch_data(
        ...     data,
        ...     32,
        ...     batch_mask,
        ...     key=jax.random.key(0)
        ... )
        >>>
        ```

    Args:
        data: The data that shall be batched. It can be any `PyTree` with
            `ArrayLike` leaves.
        batch_size: The number of examples in a batch.
        batch_axis: PyTree of the batch axis indices. `None` is used to
            indicate that the corresponding leaf or subtree in data does not
            have a batch axis. `batch_axis` must have the same structure as
            `data` or have `data` as a prefix.
            (Defaults to 0, meaning all leaves in `data` are
            batched along their first dimension.)
        convert_to_numpy: If `True`, batched data leafs will be converted to
            Numpy arrays before batching. This is useful for performance
            reasons, as Numpy's slicing is much faster than JAX's.
        key: A `jax.random.PRNGKey` used to provide randomness for batch
            generation. (Keyword only argument.)

    Returns:
        A `Generator` that yields a random batch of data every time is is
        called.

    Yields:
        A `PyTree[ArrayLike]` with the same structure as `data`. Where all
        batched leaves have `batch_size`.

    Note:
        Note that if the size of the dataset is smaller than `batch_size`, the
        obtained batches will have dataset size.

    """
    batch_axis, dataset_size = broadcast_and_get_size(data, batch_axis)

    # Convert to Numpy arrays. Numpy's slicing is much faster than JAX's, so
    # for fast model training steps this actually makes a huge difference!
    # However, be aware that this is likely only true if JAX runs on CPU.
    if convert_to_numpy:
        data = jax.tree.map(
            lambda x, a: x if a is None else np.array(x),
            data,
            batch_axis,
            is_leaf=lambda x: x is None,
        )

    # Reduce batch size if the dataset has less examples than batch size
    batch_size = min(batch_size, dataset_size)

    indices = jnp.arange(dataset_size)
    while True:
        perm = jr.permutation(key, indices)
        (key,) = jr.split(key, 1)  # Update key
        start, end = 0, batch_size
        while end <= dataset_size:
            batch_perm = perm[start:end]
            yield jax.tree.map(
                lambda a, x: x if a is None else x[batch_perm],
                batch_axis,
                data,
                is_leaf=lambda x: x is None,
            )
            start = end
            end = start + batch_size


def split_data(
    data: PyTree[Any],
    proportions: Sequence[int | float],
    batch_axis: PyTree[int | None] = 0,
    *,
    key: PRNGKeyArray,
) -> tuple[PyTree[Any], ...]:
    """Split a `PyTree` of data into multiply randomly drawn subsets.

    This function is useful for splitting into training and test datasets. The
    axis of the split if controlled by the `batch_axis` argument, which
    specifies the batch axis for each leaf in `data`.

    Example:
        This is an example for a nested PyTree` of data.

        ```python
        >>> import klax
        >>> import jax
        >>>
        >>> x = jax.numpy.array([1., 2., 3.])
        >>> data = (x, {"a": 1.0, "b": x})
        >>> s1, s2 = klax.split_data(
        ...     data,
        ...     (2, 1),
        ...     key=jax.random.key(0)
        ... )
        >>> s1
        (Array([1., 2.], dtype=float32), {'a': 1.0, 'b': Array([1., 2.], dtype=float32)})
        >>> s2
        (Array([3.], dtype=float32), {'a': 1.0, 'b': Array([3.], dtype=float32)})
        ```

    Args:
        data: Data that shall be split. It can be any `PyTree`.
        proportions: Proportions of the split that will be applied to the data,
            e.g., `(80, 20)` for a 80% to 20% split. The proportions must be
            non-negative.
        batch_axis: PyTree of the batch axis indices. `None` is used to
            indicate that the corresponding leaf or subtree in data does not
            have a batch axis. `batch_axis` must have the same structure as
            `data` or have `data` as a prefix. (Defaults to 0)
        key: A `jax.random.PRNGKey` used to provide randomness to the split.
            (Keyword only argument.)

    Returns:
        Tuple of `PyTrees`.

    """
    props = jnp.array(proportions, dtype=float)
    if props.ndim != 1:
        raise ValueError("Proportions must be a 1D Sequence.")
    if jnp.any(props < 0.0):
        raise ValueError("Proportions must be non-negative.")
    props = props / jnp.sum(props)

    batch_axis, dataset_size = broadcast_and_get_size(data, batch_axis)

    indices = jnp.arange(dataset_size)
    perm = jr.permutation(key, indices)

    split_indices = jnp.round(
        jnp.cumsum(jnp.array(props[:-1]) * dataset_size)
    ).astype(int)
    sections = jnp.split(perm, split_indices)

    if not all(s.size for s in sections):
        warnings.warn("Proportions result in one or more empty subsets.")

    def get_subset(section):
        return jax.tree.map(
            lambda a, d: d
            if a is None
            else jnp.take(d, section, axis=a, unique_indices=True),
            batch_axis,
            data,
            is_leaf=lambda x: x is None,
        )

    return tuple(get_subset(section) for section in sections)
