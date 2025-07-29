import tensorflow as tf
from keras import backend as K


def intransit_weighted_mean_squared_error(y_true, y_pred):
    y_pred = tf.convert_to_tensor(y_pred)
    y_true = tf.cast(y_true, y_pred.dtype)
    squared_diff = tf.math.squared_difference(y_pred, y_true)
    it_mask = tf.where(tf.less(y_true, 1))
    oot_mask = tf.where(tf.equal(y_true, 1))
    oot_squared_diff = K.mean(tf.boolean_mask(squared_diff, oot_mask), axis=-1)
    it_squared_diff = K.mean(tf.boolean_mask(squared_diff, it_mask), axis=-1)
    return K.sum(oot_squared_diff, it_squared_diff)
