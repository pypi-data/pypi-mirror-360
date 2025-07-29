from numpy.random import default_rng

from exoml.ete6.ete6_generator import Ete6ModelGenerator
from exoml.ml.encoding.time_position import value_encode_times
from sklearn.utils import shuffle
import numpy as np
import pandas as pd


class TranspotModelGenerator(Ete6ModelGenerator):
    def __init__(self, injected_objects_df, lcs_dir, batch_size, input_sizes, zero_epsilon=1e-7,
                 measurements_per_point=13):
        super().__init__()
        self.injected_objects_df = injected_objects_df
        self.lcs_dir = lcs_dir
        self.batch_size = batch_size
        self.input_sizes = input_sizes
        self.zero_epsilon = zero_epsilon
        self.random_number_generator = default_rng()
        self.measurements_per_point = measurements_per_point

    def __len__(self):
        return (np.ceil(len(self.injected_objects_df) / float(self.batch_size))).astype(int)

    def class_weights(self):
        return {0: 1, 1: 1}

    def __getitem__(self, idx):
        max_index = (idx + 1) * self.batch_size
        max_index = len(self.injected_objects_df) if max_index > len(self.injected_objects_df) else max_index
        target_indexes = np.arange(idx * self.batch_size, max_index, 1)
        target_indexes = shuffle(target_indexes)
        injected_objects_df = self.injected_objects_df.iloc[target_indexes]
        star_array = np.empty((len(target_indexes), 11, 1))
        global_flux_array = np.empty((len(target_indexes), self.input_sizes[0], self.measurements_per_point))
        batch_data_values = np.empty((len(target_indexes), 1))
        i = 0
        for df_index, target_row in injected_objects_df.iterrows():
            target_id = int(target_row['TIC ID'])
            leading_zeros_object_id = '{:09}'.format(target_id)
            lc_filename = str(leading_zeros_object_id) + '_lc.csv'
            star_filename = str(leading_zeros_object_id) + '_star.csv'
            star_df = pd.read_csv(self.lcs_dir + '/' + star_filename, index_col=False)
            star_df = self._prepare_input_star(star_df)
            lc_df = pd.read_csv(self.lcs_dir + '/' + lc_filename, usecols=['#time', 'flux', 'flux_0', 'flux_1',
                                                                           'flux_2', 'flux_3', 'flux_4',
                                                                           'flux_err', 'centroid_x',
                                                                           'centroid_y', 'motion_x', 'motion_y',
                                                                           'bck_flux'], low_memory=True)
            lc_df = self._prepare_input_lc(lc_df)
            type = target_row['type']
            batch_data_values[i] = 0 if type == 'none' else 1
            # not_null_times_args = np.argwhere(lc_df['#time'].to_numpy() > 0).flatten()
            # lc_df = lc_df.iloc[not_null_times_args]
            star_array[i] = np.transpose([star_df.to_numpy()])
            global_flux_array[i] = lc_df.to_numpy()
            assert not np.isnan(star_array[i]).any() and not np.isinf(star_array[i]).any()
            assert not np.isnan(global_flux_array[i]).any() and not np.isinf(global_flux_array[i]).any()
            if np.max(global_flux_array[i]) >= 2:
                print("MAX FLUX VALUE OVERCAME BY " + str(target_id))
            assert np.max(global_flux_array[i]) < 2
            i = i + 1
        return [star_array, global_flux_array], batch_data_values

    def _prepare_input_lc(self, input_df):
        result_df = super()._prepare_input_lc(input_df)
        args_zero = np.argwhere(result_df["#time"].to_numpy() <= self.zero_epsilon).flatten()
        first_non_zero_arg = np.argwhere(result_df["#time"].to_numpy() > self.zero_epsilon).flatten()[0]
        time = result_df["#time"].to_numpy()
        result_df["#time"] = value_encode_times(time - time[first_non_zero_arg], max_time=100)
        result_df["#time"].iloc[args_zero] = self.zero_epsilon
        return result_df

# df = pd.read_csv("/mnt/DATA-2/ete6/injected_objects.csv", index_col=False)
# df = shuffle(df)
# df.reset_index(inplace=True, drop=True)
# img = IatsonModelGenerator(df, "/mnt/DATA-2/ete6/lcs", 20, [11, 2500, 500, 500, 500, 500, 500, 500])
# img.__getitem__(20)
