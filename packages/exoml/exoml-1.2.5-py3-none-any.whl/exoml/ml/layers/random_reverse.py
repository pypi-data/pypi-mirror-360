import tensorflow as tf


class RandomReverseLayer(tf.keras.layers.Layer):
    def __init__(self, threshold, axis=-1, **kwargs):
        super(RandomReverseLayer, self).__init__(**kwargs)
        self.axis = axis
        self.threshold = threshold  # The maximum integer threshold

    def call(self, inputs, training=None):
        # Generate a random integer between 0 and threshold
        if training:
            rand_int = tf.random.uniform(shape=(), minval=0, maxval=1)
            return tf.cond(tf.math.less_equal(rand_int, self.threshold),
                           lambda: RandomReverseLayer.reverse_tensor(inputs, [self.axis]),
                           lambda: RandomReverseLayer.return_tensor(inputs))
        else:
            return inputs

    @staticmethod
    def return_tensor(inputs):
        return inputs

    @staticmethod
    def reverse_tensor(inputs, axis):
        return tf.reverse(inputs, axis=axis)

    def get_config(self):
        config = super(RandomReverseLayer, self).get_config()
        config.update({"threshold": self.threshold})
        return config