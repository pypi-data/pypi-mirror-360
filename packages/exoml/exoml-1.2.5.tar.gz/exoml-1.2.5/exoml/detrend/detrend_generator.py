import logging

from exoml.ete6.ete6_generator import Ete6ModelGenerator
from exoml.ml.encoding.time_position import value_encode_times
from sklearn.utils import shuffle
import tensorflow as tf
import numpy as np
import pandas as pd


class DetrendModelGenerator(Ete6ModelGenerator):
    """
    Sequence generator for DETREND model batches
    """
    def __init__(self, lc_filenames, batch_size, input_size, zero_epsilon):
        super().__init__(zero_epsilon)
        self.lc_filenames = lc_filenames
        self.batch_size = batch_size
        self.input_size = input_size

    def __len__(self):
        return (np.ceil(len(self.lc_filenames) / float(self.batch_size))).astype(int)

    def __getitem__(self, idx):
        batch_filenames = self.lc_filenames[idx * self.batch_size: (idx + 1) * self.batch_size]
        filenames_shuffled = shuffle(batch_filenames)
        batch_data_array = np.empty((len(filenames_shuffled), self.input_size[0], self.input_size[1]))
        batch_data_values = np.empty((len(filenames_shuffled), self.input_size[0]))
        i = 0
        for file in filenames_shuffled:
            input_df = pd.read_csv(file, usecols=['#time', 'flux', 'flux_err', 'centroid_x', 'centroid_y',
                                                  'motion_x', 'motion_y', 'bck_flux'], low_memory=True)
            values_df = pd.read_csv(file, usecols=['eb_model', 'bckeb_model', 'planet_model'],
                                    low_memory=True)
            input_df = self.__prepare_input_data(input_df)
            batch_data_array[i] = input_df.to_numpy()
            assert not np.isnan(batch_data_array[i]).any() and not np.isinf(batch_data_array[i]).any()
            values_df['model'] = 1 - ((1 - values_df['eb_model']) + (1 - values_df['bckeb_model']) +
                                      (1 - values_df['planet_model']))
            batch_data_values[i] = values_df['model'].to_numpy()
            batch_data_values[i] = np.nan_to_num(batch_data_values[i], nan=self.zero_epsilon)
            negative_values_args = np.argwhere(batch_data_values[i] <= 0).flatten()
            batch_data_values[i][negative_values_args] = self.zero_epsilon
            assert not np.isnan(batch_data_values[i]).any() and not np.isinf(batch_data_values[i]).any()
            logging.info("GENERATOR Inputs max " + str(np.max(batch_data_array[i])) + " and min " +
                         str(np.min(batch_data_array[i])))
            logging.info("GENERATOR Values max " + str(np.max(batch_data_values[i])) + " and min " +
                         str(np.min(batch_data_values[i])))
            i = i + 1
        return batch_data_array, batch_data_values

    def __prepare_input_data(self, input_df):
        time = input_df["#time"].to_numpy()
        input_df["#time"] = value_encode_times(time - time[0])
        dif = time[1:] - time[:-1]
        jumps = np.where(np.abs(dif) > 0.25)[0]
        jumps = np.append(jumps, len(input_df))
        previous_jump_index = 0
        for jumpIndex in jumps:
            token = input_df["centroid_x"][previous_jump_index:jumpIndex].to_numpy()
            input_df["centroid_x"][previous_jump_index:jumpIndex] = (np.tanh(token - np.nanmedian(token)) + 1) / 2
            token = input_df["centroid_y"][previous_jump_index:jumpIndex].to_numpy()
            input_df["centroid_y"][previous_jump_index:jumpIndex] = (np.tanh(token - np.nanmedian(token)) + 1) / 2
            token = input_df["motion_x"][previous_jump_index:jumpIndex].to_numpy()
            input_df["motion_x"][previous_jump_index:jumpIndex] = (np.tanh(token - np.nanmedian(token)) + 1) / 2
            token = input_df["motion_y"][previous_jump_index:jumpIndex].to_numpy()
            input_df["motion_y"][previous_jump_index:jumpIndex] = (np.tanh(token - np.nanmedian(token)) + 1) / 2
            token = input_df["bck_flux"][previous_jump_index:jumpIndex].to_numpy()
            input_df["bck_flux"][previous_jump_index:jumpIndex] = (np.tanh(token - np.nanmedian(token)) + 1) / 3
            previous_jump_index = jumpIndex
        input_df = input_df.fillna(self.zero_epsilon)
        input_df = input_df.replace(0.0, self.zero_epsilon)
        input_df = input_df.replace(0, self.zero_epsilon)
        return input_df

    def class_weights(self):
        return None
