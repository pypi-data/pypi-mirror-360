import abc
import importlib
import warnings

#from keras import backend
#from keras_core.src.utils import tf_utils
from keras.src import backend
from keras.src.utils import tf_utils

from keras.callbacks import Callback
import tensorflow as tf
#from tensorflow_addons.optimizers import MultiOptimizer
from typeguard import typechecked
from typing import Union, List


if (
    hasattr(tf.keras.optimizers, "experimental")
    and tf.keras.optimizers.Optimizer.__module__
    == tf.keras.optimizers.experimental.Optimizer.__module__
):
    # If the default optimizer points to new Keras optimizer, addon optimizers
    # should use the legacy path.
    KerasLegacyOptimizer = tf.keras.optimizers.legacy.Optimizer
else:
    KerasLegacyOptimizer = tf.keras.optimizers.Optimizer


if importlib.util.find_spec("tensorflow.keras.optimizers.legacy") is not None:
    Optimizer = Union[
        tf.keras.optimizers.Optimizer, tf.keras.optimizers.legacy.Optimizer, str
    ]
else:
    Optimizer = Union[tf.keras.optimizers.Optimizer, str]


class AveragedOptimizerWrapper(KerasLegacyOptimizer, metaclass=abc.ABCMeta):
    @typechecked
    def __init__(
        self,
        optimizer: Optimizer,
        name: str = "AverageOptimizer",
        **kwargs,
    ):
        super().__init__(name, **kwargs)

        if isinstance(optimizer, str):
            if (
                hasattr(tf.keras.optimizers, "legacy")
                and KerasLegacyOptimizer == tf.keras.optimizers.legacy.Optimizer
            ):
                optimizer = tf.keras.optimizers.get(
                    optimizer, use_legacy_optimizer=True
                )
            else:
                optimizer = tf.keras.optimizers.get(optimizer)

        if not isinstance(optimizer, KerasLegacyOptimizer):
            raise TypeError(
                "optimizer is not an object of tf.keras.optimizers.legacy.Optimizer "
            )

        self._optimizer = optimizer
        self._track_trackable(self._optimizer, "awg_optimizer")

    def _create_slots(self, var_list):
        self._optimizer._create_slots(var_list=var_list)
        for var in var_list:
            self.add_slot(var, "average")

    def _create_hypers(self):
        self._optimizer._create_hypers()

    def _prepare_local(self, var_device, var_dtype, apply_state):
        return self._optimizer._prepare_local(var_device, var_dtype, apply_state)

    def apply_gradients(self, grads_and_vars, name=None, **kwargs):
        self._optimizer._iterations = self.iterations
        return super().apply_gradients(grads_and_vars, name, **kwargs)

    @abc.abstractmethod
    def average_op(self, var, average_var, local_apply_state):
        raise NotImplementedError

    def _apply_average_op(self, train_op, var, apply_state):
        apply_state = apply_state or {}
        local_apply_state = apply_state.get((var.device, var.dtype.base_dtype))
        if local_apply_state is None:
            local_apply_state = self._fallback_apply_state(
                var.device, var.dtype.base_dtype
            )
        average_var = self.get_slot(var, "average")
        return self.average_op(var, average_var, local_apply_state)

    def _resource_apply_dense(self, grad, var, apply_state=None):
        if "apply_state" in self._optimizer._dense_apply_args:
            train_op = self._optimizer._resource_apply_dense(
                grad, var, apply_state=apply_state
            )
        else:
            train_op = self._optimizer._resource_apply_dense(grad, var)
        average_op = self._apply_average_op(train_op, var, apply_state)
        return tf.group(train_op, average_op)

    def _resource_apply_sparse(self, grad, var, indices, apply_state=None):
        if "apply_state" in self._optimizer._sparse_apply_args:
            train_op = self._optimizer._resource_apply_sparse(
                grad, var, indices, apply_state=apply_state
            )
        else:
            train_op = self._optimizer._resource_apply_sparse(grad, var, indices)
        average_op = self._apply_average_op(train_op, var, apply_state)
        return tf.group(train_op, average_op)

    def _resource_apply_sparse_duplicate_indices(
        self, grad, var, indices, apply_state=None
    ):
        if "apply_state" in self._optimizer._sparse_apply_args:
            train_op = self._optimizer._resource_apply_sparse_duplicate_indices(
                grad, var, indices, apply_state=apply_state
            )
        else:
            train_op = self._optimizer._resource_apply_sparse_duplicate_indices(
                grad, var, indices
            )
        average_op = self._apply_average_op(train_op, var, apply_state)
        return tf.group(train_op, average_op)

    def assign_average_vars(self, var_list):
        """Assign variables in var_list with their respective averages.

        Args:
            var_list: List of model variables to be assigned to their average.

        Returns:
            assign_op: The op corresponding to the assignment operation of
            variables to their average.

        Example:
        ```python
        model = tf.Sequential([...])
        opt = tfa.optimizers.SWA(
                tf.keras.optimizers.SGD(lr=2.0), 100, 10)
        model.compile(opt, ...)
        model.fit(x, y, ...)

        # Update the weights to their mean before saving
        opt.assign_average_vars(model.variables)

        model.save('model.h5')
        ```
        """
        assign_ops = []
        for var in var_list:
            try:
                assign_ops.append(
                    var.assign(
                        self.get_slot(var, "average"),
                        use_locking=self._use_locking,
                    )
                )
            except Exception as e:
                warnings.warn("Unable to assign average slot to {} : {}".format(var, e))
        return tf.group(assign_ops)

    def get_config(self):
        config = {
            "optimizer": tf.keras.optimizers.serialize(self._optimizer),
        }
        base_config = super().get_config()
        return {**base_config, **config}

    @classmethod
    def from_config(cls, config, custom_objects=None):
        optimizer = tf.keras.optimizers.deserialize(
            config.pop("optimizer"), custom_objects=custom_objects
        )
        return cls(optimizer, **config)

    @property
    def weights(self):
        return self._weights + self._optimizer.weights

    @property
    def lr(self):
        return self._optimizer._get_hyper("learning_rate")

    @lr.setter
    def lr(self, lr):
        self._optimizer._set_hyper("learning_rate", lr)  #

    @property
    def learning_rate(self):
        return self._optimizer._get_hyper("learning_rate")

    @learning_rate.setter
    def learning_rate(self, learning_rate):
        self._optimizer._set_hyper("learning_rate", learning_rate)


@tf.keras.utils.register_keras_serializable(package="Addons")
class SWA(AveragedOptimizerWrapper):
     """This class extends optimizers with Stochastic Weight Averaging (SWA).

     The Stochastic Weight Averaging mechanism was proposed by Pavel Izmailov
     et. al in the paper [Averaging Weights Leads to Wider Optima and
     Better Generalization](https://arxiv.org/abs/1803.05407). The optimizer
     implements averaging of multiple points along the trajectory of SGD. The
    optimizer expects an inner optimizer which will be used to apply the
     gradients to the variables and itself computes a running average of the
     variables every `k` steps (which generally corresponds to the end
     of a cycle when a cyclic learning rate is employed).

     We also allow the specification of the number of steps averaging
     should first happen after. Let's say, we want averaging to happen every `k`
     steps after the first `m` steps. After step `m` we'd take a snapshot of the
     variables and then average the weights appropriately at step `m + k`,
     `m + 2k` and so on. The assign_average_vars function can be called at the
     end of training to obtain the averaged_weights from the optimizer.

     Note: If your model has batch-normalization layers you would need to run
     the final weights through the data to compute the running mean and
     variance corresponding to the activations for each layer of the network.
     From the paper: If the DNN uses batch normalization we run one
     additional pass over the data, to compute the running mean and standard
     deviation of the activations for each layer of the network with SWA
     weights after the training is finished, since these statistics are not
     collected during training. For most deep learning libraries, such as
     PyTorch or Tensorflow, one can typically collect these statistics by
     making a forward pass over the data in training mode
     ([Averaging Weights Leads to Wider Optima and Better
     Generalization](https://arxiv.org/abs/1803.05407))

     Example of usage:

     ```python
     opt = tf.keras.optimizers.SGD(learning_rate)
     opt = tfa.optimizers.SWA(opt, start_averaging=m, average_period=k)
     ```
     """

     @typechecked
     def __init__(
         self,
         optimizer: Optimizer,
         start_averaging: int = 0,
         average_period: int = 10,
         name: str = "SWA",
         **kwargs,
     ):
         r"""Wrap optimizer with the Stochastic Weight Averaging mechanism.

         Args:
             optimizer: The original optimizer that will be used to compute and
                 apply the gradients.
             start_averaging: An integer. Threshold to start averaging using
                 SWA. Averaging only occurs at `start_averaging` iters, must
                 be >= 0. If start_averaging = m, the first snapshot will be
                 taken after the mth application of gradients (where the first
                 iteration is iteration 0).
             average_period: An integer. The synchronization period of SWA. The
                 averaging occurs every average_period steps. Averaging period
                 needs to be >= 1.
             name: Optional name for the operations created when applying
                 gradients. Defaults to 'SWA'.
             **kwargs: keyword arguments. Allowed to be {`clipnorm`,
                 `clipvalue`, `lr`, `decay`}. `clipnorm` is clip gradients by
                 norm; `clipvalue` is clip gradients by value, `decay` is
                 included for backward compatibility to allow time inverse
                 decay of learning rate. `lr` is included for backward
                 compatibility, recommended to use `learning_rate` instead.
         """
         super().__init__(optimizer, name, **kwargs)

         if average_period < 1:
             raise ValueError("average_period must be >= 1")
         if start_averaging < 0:
             raise ValueError("start_averaging must be >= 0")

         self._set_hyper("average_period", average_period)
         self._set_hyper("start_averaging", start_averaging)

     @tf.function
     def average_op(self, var, average_var, local_apply_state):
         average_period = self._get_hyper("average_period", tf.dtypes.int64)
         start_averaging = self._get_hyper("start_averaging", tf.dtypes.int64)
         # number of times snapshots of weights have been taken (using max to
         # avoid negative values of num_snapshots).
         num_snapshots = tf.math.maximum(
             tf.cast(0, tf.int64),
             tf.math.floordiv(self.iterations - start_averaging, average_period),
         )

         # The average update should happen iff two conditions are met:
         # 1. A min number of iterations (start_averaging) have taken place.
         # 2. Iteration is one in which snapshot should be taken.
         checkpoint = start_averaging + num_snapshots * average_period
         if self.iterations >= start_averaging and self.iterations == checkpoint:
             num_snapshots = tf.cast(num_snapshots, tf.float32)
             average_value = (average_var * num_snapshots + var) / (num_snapshots + 1.0)
             return average_var.assign(average_value, use_locking=self._use_locking)

         return average_var

     def get_config(self):
         config = {
             "average_period": self._serialize_hyperparameter("average_period"),
             "start_averaging": self._serialize_hyperparameter("start_averaging"),
         }
         base_config = super().get_config()
         return {**base_config, **config}

@tf.keras.utils.register_keras_serializable(package="Addons")
class MultiOptimizer(KerasLegacyOptimizer):
     """Multi Optimizer Wrapper for Discriminative Layer Training.

     Creates a wrapper around a set of instantiated optimizer layer pairs.
     Generally useful for transfer learning of deep networks.

     Each optimizer will optimize only the weights associated with its paired layer.
     This can be used to implement discriminative layer training by assigning
     different learning rates to each optimizer layer pair.
     `(tf.keras.optimizers.legacy.Optimizer, List[tf.keras.layers.Layer])` pairs are also supported.
     Please note that the layers must be instantiated before instantiating the optimizer.

     Args:
         optimizers_and_layers: a list of tuples of an optimizer and a layer or model.
             Each tuple should contain exactly 1 instantiated optimizer and 1 object that
             subclasses `tf.keras.Model`, `tf.keras.Sequential` or `tf.keras.layers.Layer`.
             Nested layers and models will be automatically discovered.
             Alternatively, in place of a single layer, you can pass a list of layers.
         optimizer_specs: specialized list for serialization.
             Should be left as None for almost all cases.
             If you are loading a serialized version of this optimizer,
             please use `tf.keras.models.load_model` after saving a model compiled with this optimizer.

     Usage:

     >>> model = tf.keras.Sequential([
     ...     tf.keras.Input(shape=(4,)),
     ...     tf.keras.layers.Dense(8),
     ...     tf.keras.layers.Dense(16),
     ...     tf.keras.layers.Dense(32),
     ... ])
     >>> optimizers = [
     ...     tf.keras.optimizers.Adam(learning_rate=1e-4),
     ...     tf.keras.optimizers.Adam(learning_rate=1e-2)
     ... ]
     >>> optimizers_and_layers = [(optimizers[0], model.layers[0]), (optimizers[1], model.layers[1:])]
     >>> optimizer = tfa.optimizers.MultiOptimizer(optimizers_and_layers)
     >>> model.compile(optimizer=optimizer, loss="mse")

     Reference:
         - [Universal Language Model Fine-tuning for Text Classification](https://arxiv.org/abs/1801.06146)
         - [Collaborative Layer-wise Discriminative Learning in Deep Neural Networks](https://arxiv.org/abs/1607.05440)

     Note: Currently, `tfa.optimizers.MultiOptimizer` does not support callbacks that modify optimizers.
         However, you can instantiate optimizer layer pairs with
         `tf.keras.optimizers.schedules.LearningRateSchedule`
         instead of a static learning rate.

     This code should function on CPU, GPU, and TPU. Apply with `tf.distribute.Strategy().scope()` context as you
     would with any other optimizer.
     """

     @typechecked
     def __init__(
          self,
         optimizers_and_layers: Union[list, None] = None,
         optimizer_specs: Union[list, None] = None,
         name: str = "MultiOptimizer",
         **kwargs,
     ):

         super(MultiOptimizer, self).__init__(name, **kwargs)

         if optimizer_specs is None and optimizers_and_layers is not None:
             self.optimizer_specs = [
                 self.create_optimizer_spec(optimizer, layers_or_model)
                 for optimizer, layers_or_model in optimizers_and_layers
             ]

         elif optimizer_specs is not None and optimizers_and_layers is None:
             self.optimizer_specs = [
                 self.maybe_initialize_optimizer_spec(spec) for spec in optimizer_specs
             ]

         else:
             raise RuntimeError(
                 "Must specify one of `optimizers_and_layers` or `optimizer_specs`."
             )

     def apply_gradients(self, grads_and_vars, **kwargs):
         """Wrapped apply_gradient method.

         Returns an operation to be executed.
         """

         for spec in self.optimizer_specs:
             spec["gv"] = []

         for grad, var in tuple(grads_and_vars):
             for spec in self.optimizer_specs:
                 for name in spec["weights"]:
                     if var.name == name:
                         spec["gv"].append((grad, var))

         update_ops = [
             spec["optimizer"].apply_gradients(spec["gv"], **kwargs)
             for spec in self.optimizer_specs
         ]
         update_group = tf.group(update_ops)

         any_symbolic = any(
             isinstance(i, tf.Operation) or tf_utils.is_symbolic_tensor(i)
             for i in update_ops
         )

         if not tf.executing_eagerly() or any_symbolic:
             # If the current context is graph mode or any of the update ops are
             # symbolic then the step update should be carried out under a graph
             # context. (eager updates execute immediately)
             with backend._current_graph(  # pylint: disable=protected-access
                 update_ops
             ).as_default():
                 with tf.control_dependencies([update_group]):
                     return self.iterations.assign_add(1, read_value=False)

         return self.iterations.assign_add(1)

     def get_config(self):
         config = super(MultiOptimizer, self).get_config()
         optimizer_specs_without_gv = []
         for optimizer_spec in self.optimizer_specs:
             optimizer_specs_without_gv.append(
                 {
                     "optimizer": optimizer_spec["optimizer"],
                     "weights": optimizer_spec["weights"],
                 }
             )
         config.update({"optimizer_specs": optimizer_specs_without_gv})
         return config

     @classmethod
     def create_optimizer_spec(
         cls,
         optimizer: KerasLegacyOptimizer,
         layers_or_model: Union[
             tf.keras.Model,
             tf.keras.Sequential,
             tf.keras.layers.Layer,
             List[tf.keras.layers.Layer],
         ],
     ):
         """Creates a serializable optimizer spec.

         The name of each variable is used rather than `var.ref()` to enable serialization and deserialization.
         """
         if isinstance(layers_or_model, list):
             weights = [
                 var.name for sublayer in layers_or_model for var in sublayer.weights
             ]
         else:
             weights = [var.name for var in layers_or_model.weights]

         return {
             "optimizer": optimizer,
             "weights": weights,
         }

     @classmethod
     def maybe_initialize_optimizer_spec(cls, optimizer_spec):
         if isinstance(optimizer_spec["optimizer"], dict):
             optimizer_spec["optimizer"] = tf.keras.optimizers.deserialize(
                 optimizer_spec["optimizer"]
             )

         return optimizer_spec

     def __repr__(self):
         return "Multi Optimizer with %i optimizer layer pairs" % len(
             self.optimizer_specs
         )

class WarmUpAndLinDecreaseCallback(Callback):
    def __init__(
            self,
            initial_lr,
            top_lr,
            baseline_lr,
            warmup_epochs,
            baseline_epochs,
            name=None):
        """Applies linear decrease with a first stage of warmup
    """
        super(WarmUpAndLinDecreaseCallback, self).__init__()
        assert initial_lr > 0
        self.initial_lr = initial_lr
        self.top_lr = top_lr
        self.baseline_lr = baseline_lr
        self.warmup_epochs = warmup_epochs
        self.baseline_epochs = baseline_epochs
        self.name = name
        super().__init__()

    def on_epoch_end(self, epoch, logs=None):
        if self.model.optimizer.__class__.__name__ == MultiOptimizer.__name__:
            for index, optimizer_spec in enumerate(self.model.optimizer.optimizer_specs):
                optimizer = optimizer_spec['optimizer']
                warmup_slope = (self.top_lr - self.initial_lr) / self.warmup_epochs
                decreasing_slope = (self.baseline_lr - self.top_lr) / self.baseline_epochs
                new_lr_decreasing = epoch * decreasing_slope + self.top_lr
                new_lr_warmup = epoch * warmup_slope + self.initial_lr
                new_learning_rate = new_lr_warmup if epoch <= self.warmup_epochs else new_lr_decreasing
                new_learning_rate = new_learning_rate if new_learning_rate < self.baseline_lr else new_learning_rate
                new_learning_rate = new_learning_rate * optimizer.progressive_lr_factor
                backend.set_value(optimizer.lr, new_learning_rate)
        else:
            optimizer = self.model.optimizer
            if self.warmup_epochs <= 0:
                warmup_slope = 1
            else:
                warmup_slope = (self.top_lr - self.initial_lr) / self.warmup_epochs
            decreasing_slope = (self.baseline_lr - self.top_lr) / self.baseline_epochs
            new_lr_decreasing = epoch * decreasing_slope + self.top_lr
            new_lr_warmup = epoch * warmup_slope + self.initial_lr
            new_learning_rate = new_lr_warmup if epoch <= self.warmup_epochs else new_lr_decreasing
            new_learning_rate = new_learning_rate if new_learning_rate < self.baseline_lr else new_learning_rate
            backend.set_value(optimizer.lr, new_learning_rate)
