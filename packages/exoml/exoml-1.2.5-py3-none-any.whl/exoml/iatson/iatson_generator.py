import matplotlib.pyplot as plt
import foldedleastsquares
from numpy.random import default_rng
from exoml.ete6.ete6_generator import Ete6ModelGenerator
from exoml.ml.encoding.time_position import value_encode_times
from sklearn.utils import shuffle
import numpy as np
import pandas as pd


class IatsonModelGenerator(Ete6ModelGenerator):
    TYPE_TO_LABEL = {'bckEB': [1, 0, 0, 0], 'EB': [0, 1, 0, 0], 'planet': [0, 0, 1, 0], 'none': [0, 0, 0, 1]}

    def __init__(self, injected_objects_df, lcs_dir, batch_size, input_sizes, zero_epsilon=1e-7,
                 measurements_per_point=13):
        super().__init__(zero_epsilon)
        self.injected_objects_df = injected_objects_df
        self.lcs_dir = lcs_dir
        self.batch_size = batch_size
        self.input_sizes = input_sizes
        self.random_number_generator = default_rng()
        self.measurements_per_point = measurements_per_point

    def __len__(self):
        return (np.ceil(len(self.injected_objects_df) / float(self.batch_size))).astype(int)

    def class_weights(self):
        return {0: 1, 1: 1, 2: 1, 3: 1}

    def _plot_df(self, df, type, scenario):
        fig, axs = plt.subplots(2, 3, figsize=(12, 6), constrained_layout=True)
        axs[0][0].scatter(df['#time'], df['flux'])
        axs[0][1].scatter(df['#time'], df['centroid_x'])
        axs[0][2].scatter(df['#time'], df['centroid_y'])
        axs[1][0].scatter(df['#time'], df['bck_flux'])
        axs[1][1].scatter(df['#time'], df['motion_x'])
        axs[1][2].scatter(df['#time'], df['motion_y'])
        plt.title(type + " " + scenario)
        plt.show()
        plt.clf()
        plt.close()

    def _plot_input(self, input_array, type, scenario):
        fig, axs = plt.subplots(4, 3, figsize=(12, 6), constrained_layout=True)
        current_array = np.transpose(input_array)[1]
        axs[0][0].scatter(np.transpose(input_array)[0], current_array)
        axs[0][0].set_ylim(np.mean(current_array) - 6 * np.std(current_array), np.mean(current_array) + 6 * np.std(current_array))
        current_array = np.transpose(input_array)[3]
        axs[0][1].scatter(np.transpose(input_array)[0], current_array)
        axs[0][1].set_ylim(np.mean(current_array) - 6 * np.std(current_array), np.mean(current_array) + 6 * np.std(current_array))
        current_array = np.transpose(input_array)[4]
        axs[0][2].scatter(np.transpose(input_array)[0], current_array)
        axs[0][2].set_ylim(np.mean(current_array) - 6 * np.std(current_array), np.mean(current_array) + 6 * np.std(current_array))
        current_array = np.transpose(input_array)[5]
        axs[1][0].scatter(np.transpose(input_array)[0], current_array)
        axs[1][0].set_ylim(np.mean(current_array) - 6 * np.std(current_array), np.mean(current_array) + 6 * np.std(current_array))
        current_array = np.transpose(input_array)[6]
        axs[1][1].scatter(np.transpose(input_array)[0], current_array)
        axs[1][1].set_ylim(np.mean(current_array) - 6 * np.std(current_array), np.mean(current_array) + 6 * np.std(current_array))
        current_array = np.transpose(input_array)[7]
        axs[1][2].scatter(np.transpose(input_array)[0], current_array)
        axs[1][2].set_ylim(np.mean(current_array) - 6 * np.std(current_array), np.mean(current_array) + 6 * np.std(current_array))
        current_array = np.transpose(input_array)[8]
        axs[2][0].scatter(np.transpose(input_array)[0], current_array)
        axs[2][0].set_ylim(np.mean(current_array) - 6 * np.std(current_array), np.mean(current_array) + 6 * np.std(current_array))
        current_array = np.transpose(input_array)[9]
        axs[2][1].scatter(np.transpose(input_array)[0], current_array)
        axs[2][1].set_ylim(np.mean(current_array) - 6 * np.std(current_array), np.mean(current_array) + 6 * np.std(current_array))
        current_array = np.transpose(input_array)[10]
        axs[2][2].scatter(np.transpose(input_array)[0], current_array)
        axs[2][2].set_ylim(np.mean(current_array) - 6 * np.std(current_array), np.mean(current_array) + 6 * np.std(current_array))
        current_array = np.transpose(input_array)[11]
        axs[3][0].scatter(np.transpose(input_array)[0], current_array)
        axs[3][0].set_ylim(np.mean(current_array) - 6 * np.std(current_array), np.mean(current_array) + 6 * np.std(current_array))
        current_array = np.transpose(input_array)[12]
        axs[3][1].scatter(np.transpose(input_array)[0], current_array)
        axs[3][1].set_ylim(np.mean(current_array) - 6 * np.std(current_array), np.mean(current_array) + 6 * np.std(current_array))
        plt.title(type + " " + scenario)
        plt.show()
        plt.clf()
        plt.close()

    def __getitem__(self, idx):
        max_index = (idx + 1) * self.batch_size
        max_index = len(self.injected_objects_df) if max_index > len(self.injected_objects_df) else max_index
        target_indexes = np.arange(idx * self.batch_size, max_index, 1)
        target_indexes = shuffle(target_indexes)
        injected_objects_df = self.injected_objects_df.iloc[target_indexes]
        star_array = np.empty((len(target_indexes), 11, 1))
        star_neighbours_array = np.empty((len(target_indexes), 9 * 15, 1))
        global_flux_array = np.empty((len(target_indexes), 2500, self.measurements_per_point))
        folded_flux_even_array = np.empty((len(target_indexes), 500, self.measurements_per_point))
        folded_flux_odd_array = np.empty((len(target_indexes), 500, self.measurements_per_point))
        folded_flux_even_subhar_array = np.empty((len(target_indexes), 500, self.measurements_per_point))
        folded_flux_odd_subhar_array = np.empty((len(target_indexes), 500, self.measurements_per_point))
        folded_flux_even_har_array = np.empty((len(target_indexes), 500, self.measurements_per_point))
        folded_flux_odd_har_array = np.empty((len(target_indexes), 500, self.measurements_per_point))
        batch_data_values = np.empty((len(target_indexes), len(self.TYPE_TO_LABEL)))
        i = 0
        for df_index, target_row in injected_objects_df.iterrows():
            target_id = int(target_row['TIC ID'])
            #target_id = 281734251
            # target_row = self.injected_objects_df[self.injected_objects_df['TIC ID'] == 356110099].iloc[0]
            leading_zeros_object_id = '{:09}'.format(target_id)
            lc_filename = str(leading_zeros_object_id) + '_lc.csv'
            star_filename = str(leading_zeros_object_id) + '_star.csv'
            star_neighbours_df = pd.read_csv(self.lcs_dir + '/' + star_filename,
                                             usecols=['Teff', 'lum', 'v', 'j', 'k', 'h', 'radius', 'mass',
                                                      'dist_arcsec'], index_col=False)
            star_neighbours_df = self._prepare_input_neighbour_stars(star_neighbours_df)
            star_df = pd.read_csv(self.lcs_dir + '/' + star_filename, index_col=False)
            star_df = self._prepare_input_star(star_df)
            lc_df = pd.read_csv(self.lcs_dir + '/' + lc_filename, usecols=['#time', 'flux', 'flux_0', 'flux_1',
                                                                           'flux_2', 'flux_3', 'flux_4',
                                                                           'flux_err', 'centroid_x',
                                                                           'centroid_y', 'motion_x', 'motion_y',
                                                                           'bck_flux'], low_memory=True)
            lc_df = self._prepare_input_lc(lc_df)
            type = target_row['type']
            batch_data_values[i] = self.TYPE_TO_LABEL[type]
            not_null_times_args = np.argwhere(lc_df['#time'].to_numpy() > 0).flatten()
            lc_df = lc_df.iloc[not_null_times_args]
            period = target_row['period']
            epoch = target_row['epoch']
            duration = target_row['duration(h)'] / 24
            duration_to_period = duration / period
            #['ld_a', 'ld_b', 'Teff', 'lum', 'logg', 'radius', 'mass', 'v', 'j', 'h', 'k'])
            neighbours_array = star_neighbours_df.to_numpy().flatten()
            star_neighbours_array[i] = np.transpose([neighbours_array if len(neighbours_array) == 9 * 15 \
                else neighbours_array + np.zeros(9 * 15 - len(neighbours_array))])
            star_array[i] = np.transpose([star_df.to_numpy()])
            time = lc_df['#time'].to_numpy()
            # Global flux
            # Shifting data 1/4 so that main transit and possible occultation don't get cut by the borders
            lc_df_sorted_fold = lc_df.copy()
            lc_df_sorted_fold['#time'] = foldedleastsquares.fold(time, period, epoch + period / 4)
            lc_df_sorted_fold = lc_df_sorted_fold.sort_values(by=['#time'])
            lc_df_sorted_fold = lc_df_sorted_fold.sort_values(by=['#time'])
            global_flux_array[i] = self.bin_by_time(lc_df_sorted_fold.to_numpy(), self.input_sizes[2])
            #self._plot_input(global_flux_array[i], type, "even")
            # Focus flux even
            lc_df_focus = lc_df.copy()
            lc_df_focus['#time'] = foldedleastsquares.fold(time, period, epoch)
            lc_df_focus = lc_df_focus.sort_values(by=['#time'])
            lc_df_focus = lc_df_focus[(lc_df_focus['#time'] > 0.5 - duration_to_period * 2) &
                                      (lc_df_focus['#time'] < 0.5 + duration_to_period * 2)]
            folded_flux_even_array[i] = self.bin_by_time(lc_df_focus.to_numpy(), self.input_sizes[3])
            # self._plot_df(lc_df_focus, type, "even")
            # self._plot_input(folded_flux_even_array[i], type, "even")
            # Focus flux odd
            lc_df_focus = lc_df.copy()
            lc_df_focus['#time'] = foldedleastsquares.fold(time, period, epoch + period / 2)
            lc_df_focus = lc_df_focus.sort_values(by=['#time'])
            lc_df_focus = lc_df_focus[(lc_df_focus['#time'] > 0.5 - duration_to_period * 3) &
                                      (lc_df_focus['#time'] < 0.5 + duration_to_period * 3)]
            folded_flux_odd_array[i] = self.bin_by_time(lc_df_focus.to_numpy(), self.input_sizes[4])
            # self._plot_df(lc_df_focus, type, "odd")
            # self._plot_input(folded_flux_odd_array[i], type, "odd")
            # Focus flux sub-harmonic even
            lc_df_focus = lc_df.copy()
            lc_df_focus['#time'] = foldedleastsquares.fold(time, period / 2, epoch)
            lc_df_focus = lc_df_focus.sort_values(by=['#time'])
            lc_df_focus = lc_df_focus[(lc_df_focus['#time'] > 0.5 - duration_to_period * 3) &
                                      (lc_df_focus['#time'] < 0.5 + duration_to_period * 3)]
            folded_flux_even_subhar_array[i] = self.bin_by_time(lc_df_focus.to_numpy(), self.input_sizes[5])
            # Focus flux sub-harmonic odd
            lc_df_focus = lc_df.copy()
            lc_df_focus['#time'] = foldedleastsquares.fold(time, period / 2, epoch + period / 4)
            lc_df_focus = lc_df_focus.sort_values(by=['#time'])
            lc_df_focus = lc_df_focus[(lc_df_focus['#time'] > 0.5 - duration_to_period * 3) &
                                      (lc_df_focus['#time'] < 0.5 + duration_to_period * 3)]
            folded_flux_odd_subhar_array[i] = self.bin_by_time(lc_df_focus.to_numpy(), self.input_sizes[6])
            # Focus flux harmonic even
            lc_df_focus = lc_df.copy()
            lc_df_focus['#time'] = foldedleastsquares.fold(time, period * 2, epoch)
            lc_df_focus = lc_df_focus.sort_values(by=['#time'])
            lc_df_focus = lc_df_focus[(lc_df_focus['#time'] > 0.5 - duration_to_period * 3) &
                                      (lc_df_focus['#time'] < 0.5 + duration_to_period * 3)]
            folded_flux_even_har_array[i] = self.bin_by_time(lc_df_focus.to_numpy(), self.input_sizes[7])
            # Focus flux harmonic odd
            lc_df_focus = lc_df.copy()
            lc_df_focus['#time'] = foldedleastsquares.fold(time, period * 2, epoch + period * 3 / 2)
            lc_df_focus = lc_df_focus.sort_values(by=['#time'])
            lc_df_focus = lc_df_focus[(lc_df_focus['#time'] > 0.5 - duration_to_period * 3) &
                                      (lc_df_focus['#time'] < 0.5 + duration_to_period * 3)]
            folded_flux_odd_har_array[i] = self.bin_by_time(lc_df_focus.to_numpy(), self.input_sizes[8])
            assert np.max(global_flux_array[i]) < 2
            assert not np.isnan(star_array[i]).any() and not np.isinf(star_array[i]).any()
            assert not np.isnan(global_flux_array[i]).any() and not np.isinf(global_flux_array[i]).any()
            assert not np.isnan(folded_flux_even_array[i]).any() and not np.isinf(folded_flux_even_array[i]).any()
            assert not np.isnan(folded_flux_odd_array[i]).any() and not np.isinf(folded_flux_odd_array[i]).any()
            assert not np.isnan(folded_flux_even_subhar_array[i]).any() and not np.isinf(folded_flux_even_subhar_array[i]).any()
            assert not np.isnan(folded_flux_odd_subhar_array[i]).any() and not np.isinf(folded_flux_odd_subhar_array[i]).any()
            assert not np.isnan(folded_flux_even_har_array[i]).any() and not np.isinf(folded_flux_even_har_array[i]).any()
            assert not np.isnan(folded_flux_odd_har_array[i]).any() and not np.isinf(folded_flux_odd_har_array[i]).any()
            # logging.info("GENERATOR Star Inputs max " + str(np.max(star_array[i])) + " and min " +
            #              str(np.min(star_array[i])))
            # logging.info("GENERATOR Global Flux Inputs max " + str(np.max(global_flux_array[i])) + " and min " +
            #              str(np.min(global_flux_array[i])))
            # logging.info("GENERATOR Folded Even Inputs max " + str(np.max(folded_flux_even_array[i])) + " and min " +
            #              str(np.min(folded_flux_even_array[i])))
            # logging.info("GENERATOR Folded Odd Inputs max " + str(np.max(folded_flux_odd_array[i])) + " and min " +
            #              str(np.min(folded_flux_odd_array[i])))
            # logging.info("GENERATOR Folded Even Subhar Inputs max " + str(np.max(folded_flux_even_subhar_array[i])) +
            #              " and min " + str(np.min(folded_flux_even_subhar_array[i])))
            # logging.info("GENERATOR Folded Odd Subhar Inputs max " + str(np.max(folded_flux_odd_subhar_array[i])) +
            #              " and min " + str(np.min(folded_flux_odd_subhar_array[i])))
            # logging.info("GENERATOR Folded Even Har Inputs max " + str(np.max(folded_flux_even_har_array[i])) +
            #              " and min " + str(np.min(folded_flux_even_har_array[i])))
            # logging.info("GENERATOR Folded Odd Har Inputs max " + str(np.max(folded_flux_odd_har_array[i])) +
            #              " and min " + str(np.min(folded_flux_odd_har_array[i])))
            i = i + 1
        return [star_array, star_neighbours_array, global_flux_array, folded_flux_even_array, folded_flux_odd_array,
                folded_flux_even_subhar_array, folded_flux_odd_subhar_array, folded_flux_even_har_array,
                folded_flux_odd_har_array], batch_data_values
#
# df = pd.read_csv("~/Downloads/injected_objects.csv", index_col=False)
# df = shuffle(df)
# df.reset_index(inplace=True, drop=True)
# img = IatsonModelGenerator(df, "~/Downloads/", 1, [11, 9 * 15, 2500, 500, 500, 500, 500, 500, 500])
# img.__getitem__(1)
