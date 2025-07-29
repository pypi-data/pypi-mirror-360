import warnings

from keras.callbacks import ModelCheckpoint
import tensorflow as tf
import numpy as np
from keras.src import backend


def sync_to_numpy_or_python_type(tensors):
    """Took this method from abandonned tensorflow_addons

    Syncs and converts a structure of `Tensor`s to `NumPy` arrays or Python
    scalar types.

    For each tensor, it calls `tensor.numpy()`. If the result is a scalar value,
    it converts it to a Python type, such as a float or int, by calling
    `result.item()`.

    Numpy scalars are converted, as Python types are often more convenient to
    deal with. This is especially useful for bfloat16 Numpy scalars, which don't
    support as many operations as other Numpy values.

    Async strategies (such as `TPUStrategy` and `ParameterServerStrategy`) are
    forced to
    sync during this process.

    Args:
      tensors: A structure of tensors.

    Returns:
      `tensors`, but scalar tensors are converted to Python types and non-scalar
      tensors are converted to Numpy arrays.
    """
    if isinstance(tensors, tf.distribute.experimental.coordinator.RemoteValue):
        tensors = tensors.fetch()

    def _to_single_numpy_or_python_type(t):
        # Don't turn ragged or sparse tensors to NumPy.
        if isinstance(t, tf.Tensor):
            t = t.numpy()
        # Strings, ragged and sparse tensors don't have .item(). Return them
        # as-is.
        if not isinstance(t, (np.ndarray, np.generic)):
            return t
        return t.item() if np.ndim(t) == 0 else t

    return tf.nest.map_structure(_to_single_numpy_or_python_type, tensors)


class ModelCheckpointCallback(ModelCheckpoint):
    def __init__(self, filepath, original_path, monitor: str = "val_loss", verbose: int = 0,
                 save_best_only: bool = False,
                 save_weights_only: bool = False, mode: str = "auto", save_freq="epoch",
                 initial_value_threshold=None, filter_metrics: list[str] = []):
        super().__init__(filepath=filepath,
                         monitor=monitor, verbose=verbose, save_best_only=save_best_only,
                         save_weights_only=save_weights_only, mode=mode, save_freq=save_freq,
                         initial_value_threshold=initial_value_threshold)
        self.original_path = original_path
        self.filter_metrics = filter_metrics
        self.epochs_since_last_save = 0

    def on_epoch_end(self, epoch, logs=None):
        self.epochs_since_last_save += 1
        if self.save_freq == "epoch":
            self._save_model(epoch=epoch, batch=None, logs=logs)

    def _should_save_model(self, epoch, batch, logs, filepath):
        """Determines whether the model should be saved.

        The model should be saved in the following cases:

        - self.save_best_only is False
        - self.save_best_only is True and `monitor` is a numpy array or
          backend tensor (falls back to `save_best_only=False`)
        - self.save_best_only is True and `self.monitor_op(current, self.best)`
          evaluates to True.

        Args:
            epoch: the epoch this iteration is in.
            batch: the batch this iteration is in. `None` if the `save_freq`
                is set to `"epoch"`.
            logs: the `logs` dict passed in to `on_batch_end` or
                `on_epoch_end`.
            filepath: the path where the model would be saved
        """
        logs = logs or {}
        if self.save_best_only:
            current = logs.get(self.monitor)
            if current is None:
                warnings.warn(
                    f"Can save best model only with {self.monitor} available.",
                    stacklevel=2,
                )
                return True
            elif (
                isinstance(current, np.ndarray) or backend.is_tensor(current)
            ) and len(current.shape) > 0:
                warnings.warn(
                    "Can save best model only when `monitor` is "
                    f"a scalar value. Received: {current}. "
                    "Falling back to `save_best_only=False`."
                )
                return True
            else:
                if self.monitor_op(current, self.best) and np.all(np.array(self.filter_metrics) > 0):
                    self.best = current
                    return True
                else:
                    return False
        else:
            return True


