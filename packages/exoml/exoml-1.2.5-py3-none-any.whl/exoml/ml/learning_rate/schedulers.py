import dataclasses

import tensorflow as tf

#from keras_core.src.optimizers.schedules.learning_rate_schedule import LearningRateSchedule
from keras.optimizers.schedules import LearningRateSchedule


@dataclasses.dataclass(init=False)
class ExponentialRescaleDecay(LearningRateSchedule):
    def __init__(
            self,
            initial_learning_rate,
            decay_steps,
            decay_rate,
            restore_steps,
            restore_rate=1.5,
            staircase=False,
            name=None):
        """Applies exponential decay to the learning rate and a value recovery of the learning rate to prevent gradient
    vanishing.

    Args:
      initial_learning_rate: A scalar `float32` or `float64` `Tensor` or a
        Python number.  The initial learning rate.
      decay_steps: A scalar `int32` or `int64` `Tensor` or a Python number.
        Must be positive.  See the decay computation above.
      decay_rate: A scalar `float32` or `float64` `Tensor` or a
        Python number.  The decay rate.
      restore_steps: A scalar `float32` or `float64` `Tensor` or a
        Python number.  The number of steps to wait for a learning rate rescale
      restore_rate: A scalar `float32` or `float64` `Tensor` or a
        Python number.  The restore rate.
      staircase: Boolean.  If `True` decay the learning rate at discrete
        intervals
      name: String.  Optional name of the operation.  Defaults to
        'ExponentialDecay'.
    """
        super(ExponentialRescaleDecay, self).__init__()
        assert restore_steps > decay_steps
        self.initial_learning_rate = initial_learning_rate
        self.decay_steps = decay_steps
        self.decay_rate = decay_rate
        self.restore_steps = restore_steps
        self.restore_rate = restore_rate
        self.staircase = staircase
        self.name = name

    def __call__(self, step):
        with tf.name_scope(self.name or "ExponentialRescaleDecay") as name:
            initial_learning_rate = tf.convert_to_tensor(
                self.initial_learning_rate, dtype=tf.float64, name="initial_learning_rate")
            dtype = initial_learning_rate.dtype
            decay_steps = tf.cast(self.decay_steps, dtype)
            decay_rate = tf.cast(self.decay_rate, dtype)
            restore_rate = tf.cast(self.restore_rate, dtype)
            restore_steps = tf.cast(self.restore_steps, dtype)
            step_double = tf.cast(step, dtype)
            # Mod is enforcing float64
            steps_since_last_rescale = tf.math.mod(step_double, restore_steps)
            restores_done = tf.math.floordiv(step_double, restore_steps)
            one_tensor = tf.cast(tf.constant(1), dtype)
            restores_done = tf.cond(tf.math.equal(restores_done, 0),
                                    lambda: one_tensor,
                                    lambda: restores_done + one_tensor)
            restores_done_by_rate = tf.cond(tf.math.equal(restores_done, 1),
                                            lambda: restores_done,
                                            lambda: tf.divide(restores_done, restore_rate))
            p = steps_since_last_rescale / decay_steps
            if self.staircase:
                p = tf.floor(p)
            new_learning_rate = tf.divide(initial_learning_rate, restores_done_by_rate)
            new_learning_rate = tf.multiply(new_learning_rate, tf.pow(decay_rate, p), name=name)
            return new_learning_rate

    def get_config(self):
        return {
            "initial_learning_rate": self.initial_learning_rate,
            "decay_steps": self.decay_steps,
            "decay_rate": self.decay_rate,
            "restore_steps": self.restore_steps,
            "restore_rate": self.restore_rate,
            "staircase": self.staircase,
            "name": self.name
        }
