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

import sys
import time

import jax
import jax.numpy as jnp
import jax.random as jrandom
import pytest

import klax


def test_callbackargs(getkey, getmodel, getloss):
    # Test lazy evaluation of loss function
    count = 0

    def get_loss(model, data):
        nonlocal count
        count += 1
        x, y = data
        y_pred = jax.vmap(model)(x)
        return jnp.mean(jnp.square(y - y_pred))

    x = jrandom.uniform(getkey(), (10,))
    x_val = jrandom.uniform(getkey(), (10,))

    model = getmodel()
    flat_model, treedef_model = jax.tree.flatten(model)

    opt_state = (None, (1, 3.14))  # Dummy opt state for testing
    flat_opt_state, treedef_opt_state = jax.tree.flatten(opt_state)

    cbargs = klax.CallbackArgs(
        get_loss, treedef_model, treedef_opt_state, (x, x), (x_val, x_val)
    )
    cbargs.update(flat_model, flat_opt_state, 1)

    assert count == 0
    loss_1 = cbargs.loss
    loss_2 = cbargs.loss
    assert loss_1 == 0
    assert loss_1 == loss_2
    assert count == 1
    _ = cbargs.val_loss
    assert count == 2
    cbargs.update(flat_model, flat_opt_state, 2)
    _ = cbargs.loss
    assert count == 3

    # Test data reference count
    x = jrandom.uniform(getkey(), (10,))
    data = (x, x)
    model = getmodel()
    flat_model, treedef_model = jax.tree.flatten(model)

    assert sys.getrefcount(data) == 2
    cbargs = klax.CallbackArgs(getloss, treedef_model, treedef_opt_state, data)
    assert sys.getrefcount(data) == 3

    # Test update time
    x = jrandom.uniform(getkey(), (10,))
    data = (x, x)
    model = getmodel()
    flat_model, treedef_model = jax.tree.flatten(model)
    cbargs = klax.CallbackArgs(getloss, treedef_model, treedef_opt_state, data)
    cbargs.update(flat_model, flat_opt_state, 0)
    time_on_last_update = cbargs.time_on_last_update
    cbargs.update(flat_model, flat_opt_state, 0)
    assert cbargs.time_on_last_update >= time_on_last_update


def test_history_callback(getkey, getmodel, getloss, tmp_path):
    x = jrandom.uniform(getkey(), (10,))
    model = getmodel()
    flat_model, treedef_model = jax.tree.flatten(model)

    opt_state = (None, (1, 3.14))  # Dummy opt state for testing
    flat_opt_state, treedef_opt_state = jax.tree.flatten(opt_state)

    cbargs = klax.CallbackArgs(
        getloss, treedef_model, treedef_opt_state, (x, x), None
    )
    history = klax.HistoryCallback(2)

    # On training start update
    cbargs.update(flat_model, flat_opt_state, 0)
    history.on_training_start(cbargs)
    time.sleep(1e-6)  # Sleep to ensure that training time is greater than 0

    # First update
    cbargs.update(flat_model, flat_opt_state, 1)
    history(cbargs)
    assert len(history.loss) == 1
    assert len(history.val_loss) == 1

    # Second update
    cbargs.update(flat_model, flat_opt_state, 2)
    history(cbargs)
    assert len(history.loss) == 2
    assert len(history.val_loss) == 2

    # On training end update
    cbargs.update(flat_model, flat_opt_state, -1)
    history.on_training_end(cbargs)

    assert history.training_time > 0.0

    # Test save and load
    filepath = tmp_path / "some_dir/test_history.pkl"
    with pytest.raises(FileNotFoundError):
        history.save(filepath, create_dir=False)
    history.save(filepath, create_dir=True)
    with pytest.raises(FileExistsError):
        history.save(filepath, overwrite=False)
    history.save(filepath, overwrite=True)
    history2 = klax.HistoryCallback.load(filepath)

    # This is not a complete equality test!
    assert len(history2.loss) == len(history.loss)
