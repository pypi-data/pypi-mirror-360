import logging
from abc import abstractmethod

import matplotlib.pyplot as plt
import foldedleastsquares
import scipy
import timesynth
import wotan
from lcbuilder.helper import LcbuilderHelper
from numpy.random import default_rng
from scipy import stats
from sklearn.preprocessing import StandardScaler, MinMaxScaler

from exoml.ml.encoding.time_position import value_encode_times
from sklearn.utils import shuffle
import tensorflow as tf
import numpy as np
import pandas as pd

from exoml.ml.functions.functions import sigmoid


class CurvePrioritizerGenerator(tf.keras.utils.Sequence):
    def __init__(self, injected_objects_df, batch_size, zero_epsilon=1e-6, shuffle_batch=True):
        self.injected_objects_df = injected_objects_df
        self.batch_size = batch_size
        self.zero_epsilon = zero_epsilon
        self.minmax_scaler = MinMaxScaler(feature_range=(self.zero_epsilon, 1 - self.zero_epsilon))
        self.shuffle_batch = shuffle_batch

    def __getitem__(self, idx):
        max_index = (idx + 1) * self.batch_size
        max_index = len(self.injected_objects_df) if max_index > len(self.injected_objects_df) else max_index
        target_indexes = np.arange(idx * self.batch_size, max_index, 1)
        injected_objects_df = self.injected_objects_df.iloc[target_indexes]
        if self.shuffle_batch:
            injected_objects_df = shuffle(injected_objects_df)
        curves_array = np.empty((len(target_indexes), 20000))
        #TODO prepare data
        return curves_array

    def class_weights(self):
        return {0: 1, 1: 1}

    def __len__(self):
        return (np.ceil(len(self.injected_objects_df) / float(self.batch_size))).astype(int)

    def on_epoch_end(self):
        if self.shuffle_batch:
            self.injected_objects_df = shuffle(self.injected_objects_df)

    def assert_in_range(self, object_id, array, array_err, values_range=(0, 1)):
        if np.isnan(array).any() or (array_err is not None and np.isnan(array_err).any()):
            raise ValueError("Target " + str(object_id) + " contains NaN values")
        elif np.max(array) > values_range[1] or (array_err is not None and np.max(array_err) > values_range[1]):
            raise ValueError("Target " + str(object_id) + " contains values > 1")
        elif np.min(array) < values_range[0] or (array_err is not None and np.max(array_err) < values_range[0]):
            raise ValueError("Target " + str(object_id) + " contains values < 0")
        elif np.all(array == values_range[0]) or (array_err is not None and np.all(array_err == values_range[0])):
            raise ValueError("Target " + str(object_id) + " contains all values == 0")

# df = pd.read_csv("/mnt/DATA-2/ete6/injected_objects.csv", index_col=False)
# df = shuffle(df)
# df.reset_index(inplace=True, drop=True)
# img = IatsonModelGenerator(df, "/mnt/DATA-2/ete6/lcs", 20, [11, 2500, 500, 500, 500, 500, 500, 500])
# img.__getitem__(20)
