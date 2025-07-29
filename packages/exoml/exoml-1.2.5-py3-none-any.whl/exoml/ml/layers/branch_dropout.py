import tensorflow as tf


class BranchDropoutLayer(tf.keras.layers.Layer):
    def __init__(self, dropout_rate=0.5, **kwargs):
        super(BranchDropoutLayer, self).__init__(**kwargs)
        self.dropout_rate = dropout_rate  # Probability to drop a branch

    def call(self, inputs, training=None):
        if training:
            mask = tf.random.uniform(shape=(), minval=0, maxval=1) > self.dropout_rate
            mask = tf.cast(mask, dtype=inputs.dtype)  # Convert mask to same dtype as inputs
            # Multiply the input by the mask (0 drops the input, 1 keeps it)
            return inputs * mask
        else:
            return inputs

    def get_config(self):
        config = super(BranchDropoutLayer, self).get_config()
        config.update({"dropout_rate": self.dropout_rate})
        return config