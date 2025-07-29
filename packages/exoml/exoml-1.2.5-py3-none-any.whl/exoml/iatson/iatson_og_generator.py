import logging
import os
import sys

import matplotlib.pyplot as plt
import foldedleastsquares
from lcbuilder.helper import LcbuilderHelper
from numpy.random import default_rng
from exoml.ete6.ete6_generator import Ete6ModelGenerator
from exoml.ml.encoding.time_position import value_encode_times
from sklearn.utils import shuffle
import numpy as np
import pandas as pd


class IatsonOgModelGenerator(Ete6ModelGenerator):
    def __init__(self, injected_objects_df, lcs_dir, batch_size, input_sizes, type_to_label, zero_epsilon=1e-7,
                 measurements_per_point=2, plot_inputs=False, fixed_target_id=None, store_arrays=False,
                 from_arrays=True, shuffle_batch=True):
        super().__init__(zero_epsilon, shuffle_batch=shuffle_batch)
        self.injected_objects_df = injected_objects_df
        self.kics_lcs_dir = lcs_dir + '/q1_q17/lcs/'
        self.tics_lcs_dir = lcs_dir + '/ete6/lcs/'
        self.batch_size = batch_size
        self.input_sizes = input_sizes
        self.random_number_generator = default_rng()
        self.measurements_per_point = measurements_per_point
        self.type_to_label = type_to_label
        self.plot_inputs = plot_inputs
        self.fixed_target_id = fixed_target_id
        self.store_arrays = store_arrays
        self.from_arrays = from_arrays

    def __len__(self):
        return (np.ceil(len(self.injected_objects_df) / float(self.batch_size))).astype(int)

    def class_weights(self):
        return {0: 1, 1: 1}

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

    def _plot_input(self, input_array, input_err_array, type, scenario):
        if self.plot_inputs:
            transposed_err_array = []
            transposed_array = np.transpose(input_array)
            fig, axs = plt.subplots(2, 2, figsize=(24, 12), constrained_layout=True)
            current_array = transposed_array[0]
            current_array_mask = np.argwhere((~np.isnan(current_array)) & (current_array > self.zero_epsilon)).flatten()
            current_array = current_array[current_array_mask]
            time_array = current_array
            axs[0][0].scatter(np.arange(0, len(current_array)), current_array)
            # axs[0][0].set_ylim(np.mean(current_array) - 6 * np.std(current_array), np.mean(current_array) + 6 * np.std(current_array))
            axs[0][0].set_title("Time")
            current_array = transposed_array[1]
            current_array_mask = np.argwhere((~np.isnan(current_array)) & (current_array > self.zero_epsilon)).flatten()
            current_array = current_array[current_array_mask]
            if input_err_array is not None:
                transposed_err_array = np.transpose(input_err_array)
                axs[0][1].errorbar(time_array[current_array_mask], current_array, ls='none',
                                   yerr=transposed_err_array[1][current_array_mask], color="orange", alpha=0.5)
            axs[0][1].scatter(time_array[current_array_mask], current_array)
            if len(transposed_array) > 2:
                current_array = transposed_array[2]
                current_array_mask = np.argwhere(
                    (~np.isnan(current_array)) & (current_array > self.zero_epsilon)).flatten()
                current_array = current_array[current_array_mask]
                if input_err_array is not None:
                    axs[1][0].errorbar(time_array[current_array_mask], transposed_array[2], ls='none',
                                       yerr=transposed_err_array[2][current_array_mask], color="orange", alpha=0.5)
                axs[1][0].scatter(time_array[current_array_mask], current_array)
            #axs[0][1].set_ylim(np.mean(current_array) - 6 * np.std(current_array), np.mean(current_array) + 6 * np.std(current_array))
            axs[0][1].set_title("Flux")
            axs[1][0].set_title("Flux 1")
            # current_array = transposed_array[8]
            # current_array_mask = np.argwhere((~np.isnan(current_array)) & (current_array > self.zero_epsilon)).flatten()
            # current_array = current_array[current_array_mask]
            # axs[1][1].errorbar(time_array[current_array_mask], current_array,
            #                    yerr=transposed_err_array[8][current_array_mask], color="orange", alpha=0.5)
            # axs[1][1].scatter(time_array[current_array_mask], current_array)
            # # axs[1][1].set_ylim(np.mean(current_array) - 6 * np.std(current_array),
            # #                    np.mean(current_array) + 6 * np.std(current_array))
            # axs[1][1].set_title("Flux 2")
            # current_array = transposed_array[9]
            # current_array_mask = np.argwhere((~np.isnan(current_array)) & (current_array > self.zero_epsilon)).flatten()
            # current_array = current_array[current_array_mask]
            # axs[2][0].errorbar(time_array[current_array_mask], current_array,
            #                    yerr=transposed_err_array[9][current_array_mask], color="orange", alpha=0.5)
            # axs[2][0].scatter(time_array[current_array_mask], current_array)
            # # axs[2][0].set_ylim(np.mean(current_array) - 6 * np.std(current_array),
            # #                    np.mean(current_array) + 6 * np.std(current_array))
            # axs[2][0].set_title("Flux 3")
            # current_array = transposed_array[10]
            # current_array_mask = np.argwhere((~np.isnan(current_array)) & (current_array > self.zero_epsilon)).flatten()
            # current_array = current_array[current_array_mask]
            # axs[2][1].errorbar(time_array[current_array_mask], current_array,
            #                    yerr=transposed_err_array[10][current_array_mask], color="orange", alpha=0.5)
            # axs[2][1].scatter(time_array[current_array_mask], current_array)
            # # axs[2][1].set_ylim(np.mean(current_array) - 6 * np.std(current_array),
            # #                    np.mean(current_array) + 6 * np.std(current_array))
            # axs[2][1].set_title("Flux 4")
            # current_array = transposed_array[11]
            # current_array_mask = np.argwhere((~np.isnan(current_array)) & (current_array > self.zero_epsilon)).flatten()
            # current_array = current_array[current_array_mask]
            # axs[3][0].errorbar(time_array[current_array_mask], current_array,
            #                    yerr=transposed_err_array[11][current_array_mask], color="orange", alpha=0.5)
            # axs[3][0].scatter(time_array[current_array_mask], current_array)
            # # axs[3][0].set_ylim(np.mean(current_array) - 6 * np.std(current_array),
            # #                    np.mean(current_array) + 6 * np.std(current_array))
            # axs[3][0].set_title("Flux 5")
            # current_array = transposed_array[6]
            # current_array_mask = np.argwhere((~np.isnan(current_array)) & (current_array > self.zero_epsilon)).flatten()
            # current_array = current_array[current_array_mask]
            # axs[3][1].errorbar(time_array[current_array_mask], current_array,
            #                    yerr=transposed_err_array[6][current_array_mask], color="orange", alpha=0.5)
            # axs[3][1].scatter(time_array[current_array_mask], current_array)
            # # axs[3][1].set_ylim(np.mean(current_array) - 6 * np.std(current_array), np.mean(current_array) + 6 * np.std(current_array))
            # axs[3][1].set_title("Bck Flux")
            # current_array = transposed_array[2]
            # current_array_mask = np.argwhere((~np.isnan(current_array)) & (current_array > self.zero_epsilon)).flatten()
            # current_array = current_array[current_array_mask]
            # axs[4][0].errorbar(time_array[current_array_mask], current_array,
            #                    yerr=transposed_err_array[2][current_array_mask], color="orange", alpha=0.5)
            # axs[4][0].scatter(time_array[current_array_mask], current_array)
            # # axs[4][0].set_ylim(np.mean(current_array) - 6 * np.std(current_array), np.mean(current_array) + 6 * np.std(current_array))
            # axs[4][0].set_title("Centroid X")
            # current_array = transposed_array[3]
            # current_array_mask = np.argwhere((~np.isnan(current_array)) & (current_array > self.zero_epsilon)).flatten()
            # current_array = current_array[current_array_mask]
            # axs[4][1].errorbar(time_array[current_array_mask], current_array,
            #                    yerr=transposed_err_array[3][current_array_mask], color="orange", alpha=0.5)
            # axs[4][1].scatter(time_array[current_array_mask], current_array)
            # # axs[4][1].set_ylim(np.mean(current_array) - 6 * np.std(current_array), np.mean(current_array) + 6 * np.std(current_array))
            # axs[4][1].set_title("Centroid Y")
            # current_array = transposed_array[4]
            # current_array_mask = np.argwhere((~np.isnan(current_array)) & (current_array > self.zero_epsilon)).flatten()
            # current_array = current_array[current_array_mask]
            # axs[5][0].errorbar(time_array[current_array_mask], current_array,
            #                    yerr=transposed_err_array[4][current_array_mask], color="orange", alpha=0.5)
            # axs[5][0].scatter(time_array[current_array_mask], current_array)
            # # axs[5][0].set_ylim(np.mean(current_array) - 6 * np.std(current_array), np.mean(current_array) + 6 * np.std(current_array))
            # axs[5][0].set_title("Motion Y")
            # current_array = transposed_array[5]
            # current_array_mask = np.argwhere((~np.isnan(current_array)) & (current_array > self.zero_epsilon)).flatten()
            # current_array = current_array[current_array_mask]
            # axs[5][1].errorbar(time_array[current_array_mask], current_array,
            #                    yerr=transposed_err_array[5][current_array_mask], color="orange", alpha=0.5)
            # axs[5][1].scatter(time_array[current_array_mask], current_array)
            # # axs[5][1].set_ylim(np.mean(current_array) - 6 * np.std(current_array), np.mean(current_array) + 6 * np.std(current_array))
            # axs[5][1].set_title("Motion Y")
            fig.suptitle(type + " " + scenario)
            plt.show()
            plt.clf()
            plt.close()

    def plot_single_data(self, lc_df, target_row):
        fig, axs = plt.subplots(1, 1, figsize=(8, 4), constrained_layout=True)
        axs.scatter(lc_df['#time'], lc_df['flux_0'])
        axs.set_ylim(0.5 - target_row['tce_depth'] / 0.5e6, 0.505)
        plt.show()
        plt.clf()
        plt.close()

    def __getitem__(self, idx):
        max_index = (idx + 1) * self.batch_size
        max_index = len(self.injected_objects_df) if max_index > len(self.injected_objects_df) else max_index
        target_indexes = np.arange(idx * self.batch_size, max_index, 1)
        injected_objects_df = self.injected_objects_df.iloc[target_indexes]
        if self.shuffle_batch:
            injected_objects_df = shuffle(injected_objects_df)
        folded_og_array = np.empty((len(target_indexes), self.input_sizes[3], 2))
        folded_og_array_err = np.empty((len(target_indexes), self.input_sizes[3], 2))
        batch_data_values = np.empty((len(target_indexes), 1))
        i = 0
        for df_index, target_row in injected_objects_df.iterrows():
            if self.fixed_target_id is not None:
                target_row = self.injected_objects_df[self.injected_objects_df['object_id'] == self.fixed_target_id[0]]
                target_row = target_row[target_row['period'] == self.fixed_target_id[1]]
            #TODO refactor to use mission for object_id
            object_id = target_row['object_id'].split(' ')
            mission_id = object_id[0]
            target_id = int(object_id[1])
            period = target_row['period']
            epoch = target_row['epoch']
            duration = target_row['duration(h)'] / 24
            duration_to_period = duration / period
            type = target_row['type']
            multitype = target_row['multitype']
            batch_data_values[i] = [0.0 if isinstance(multitype, str) and 'tce_og' in multitype else 1.0]
            lcs_dir = self.kics_lcs_dir if mission_id == 'KIC' else self.tics_lcs_dir
            file_prefix = lcs_dir + '/' + mission_id + '_' + str(target_id) + '_' + str(round(period, 2)) \
                if mission_id == 'KIC' else lcs_dir + '/' + mission_id + ' ' + str(target_id) + '_' + str(round(period, 2))
            if self.from_arrays:
                folded_og_array[i] = np.loadtxt(file_prefix + '_input_og.csv', delimiter=',')
                folded_og_array_err[i] = np.loadtxt(file_prefix + '_input_og_err.csv', delimiter=',')
            else:
                #TODO refactor to use mission for _lc files
                og_short_filename = file_prefix + '_og_short.csv'
                og_long_filename = file_prefix + '_og_long.csv'
                og_df = None
                if os.path.exists(og_long_filename):
                    read_og_df = pd.read_csv(og_long_filename, usecols=['time', 'og_flux', 'halo_flux', 'core_flux'],
                                             low_memory=True)
                    read_og_df = self.compute_og_df(read_og_df, object_id, duration)
                    og_df = read_og_df if og_df is None else og_df.append(read_og_df, ignore_index=True)
                if os.path.exists(og_short_filename):
                    read_og_df = pd.read_csv(og_short_filename, usecols=['time', 'og_flux', 'halo_flux', 'core_flux'],
                                             low_memory=True)
                    read_og_df = self.compute_og_df(read_og_df, object_id, duration)
                    og_df = read_og_df if og_df is None else og_df.append(read_og_df, ignore_index=True)
                og_df['time'] = self.fold(og_df['time'].to_numpy(), period, epoch + period / 2)
                og_df = og_df.sort_values(by=['time'])
                og_df = self._prepare_input_og(og_df)
                og_df = og_df[(og_df['time'] > 0.5 - duration_to_period * 3) & (
                        og_df['time'] < 0.5 + duration_to_period * 3)]
                folded_og_array[i], folded_og_array_err[i] = self.bin_by_time(og_df.to_numpy(), self.input_sizes[3], target_row['object_id'])
            self.assert_in_range(object_id, folded_og_array[i], folded_og_array_err[i])
            self._plot_input(folded_og_array[i], folded_og_array_err[i], target_row['object_id'] + "_" + type, "OG")
            if self.store_arrays:
                logging.info("Storing arrays into prefix " + file_prefix)
                np.savetxt(file_prefix + '_input_og.csv', folded_og_array[i], delimiter=',')
                np.savetxt(file_prefix + '_input_og_err.csv', folded_og_array_err[i], delimiter=',')
            i = i + 1
        return folded_og_array, batch_data_values
