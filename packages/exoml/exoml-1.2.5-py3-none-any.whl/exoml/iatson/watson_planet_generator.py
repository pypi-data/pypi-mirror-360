import logging
import os

import matplotlib.pyplot as plt
import foldedleastsquares
import wotan
from lcbuilder.helper import LcbuilderHelper
from numpy.random import default_rng
from exoml.ete6.ete6_generator import Ete6ModelGenerator
from sklearn.utils import shuffle
import numpy as np
import pandas as pd
import tensorflow as tf


class WatsonPlanetModelGenerator(Ete6ModelGenerator):
    def __init__(self, injected_objects_df, lcs_dir, star_filename, lc_filename,
                 batch_size, input_sizes, transits_mask=None, zero_epsilon=1e-7,
                 measurements_per_point=1, plot_inputs=False, use_csvs=False, explain=False):
        super().__init__(zero_epsilon, shuffle_batch=False)
        self.injected_objects_df = injected_objects_df
        self.arrays_cache: dict = {}
        self.EXPLAIN_PERIOD_VALUE = [self.zero_epsilon, 0.5, 1 - self.zero_epsilon]
        self.EXPLAIN_DURATION_VALUE = [self.zero_epsilon, 0.5, 1 - self.zero_epsilon]
        self.EXPLAIN_RADIUS_VALUE = [self.zero_epsilon, 0.5, 1 - self.zero_epsilon]
        self.EXPLAIN_GTCN_VALUE = [self.zero_epsilon, 0.5, 1 - self.zero_epsilon]
        self.EXPLAIN_GTR_VALUE = [self.zero_epsilon, 0.5, 1 - self.zero_epsilon]
        self.EXPLAIN_OFFSET_VALUE = [self.zero_epsilon, 0.5, 1 - self.zero_epsilon]
        self.EXPLAIN_BFAP_VALUE = [self.zero_epsilon, 0.5, 1 - self.zero_epsilon]
        self.EXPLAIN_ODDEVEN_VALUE = [self.zero_epsilon, 0.5, 1 - self.zero_epsilon]
        self.EXPLAIN_TEMP_ALBEDO_VALUE = [f"{self.zero_epsilon},{1 - self.zero_epsilon}",
                                          "0.5,0.5",
                                          f"{1 - self.zero_epsilon},{self.zero_epsilon}"]
        self.EXPLAIN_ALBEDO_VALUE = [self.zero_epsilon, 0.5, 1 - self.zero_epsilon]
        self.EXPLAIN_STARTEFF_VALUE = [self.zero_epsilon, 0.5, 1 - self.zero_epsilon]
        self.EXPLAIN_STARRAD_VALUE = [self.zero_epsilon, 0.5, 1 - self.zero_epsilon]
        self.lcs_dir = lcs_dir
        self.star_filename = star_filename
        self.lc_filename = lc_filename
        self.batch_size = batch_size
        self.input_sizes = input_sizes
        self.transit_masks = transits_mask
        self.random_number_generator = default_rng()
        self.measurements_per_point = measurements_per_point
        self.plot_inputs = plot_inputs
        self.use_csvs = use_csvs
        self.explain = explain
        if self.explain:
            final_df = pd.DataFrame(
                columns=['object_id', 'period', 'duration(h)', 'depth_primary', 'radius(earth)', 'type',
                         'EXPLAIN_PERIOD_VALUE', 'EXPLAIN_DURATION_VALUE', 'EXPLAIN_RADIUS_VALUE', 'EXPLAIN_GTCN_VALUE',
                         'EXPLAIN_GTR_VALUE', 'EXPLAIN_OFFSET_VALUE', 'EXPLAIN_BFAP_VALUE',
                         'EXPLAIN_ODDEVEN_VALUE', 'EXPLAIN_TEMP_ALBEDO_VALUE',
                         'EXPLAIN_STARTEFF_VALUE', 'EXPLAIN_STARRAD_VALUE',
                         'EXPLAIN_GLOBAL_VIEW', 'EXPLAIN_MAIN_VIEW', 'EXPLAIN_SECONDARY_VIEW',
                         'EXPLAIN_ODD_VIEW', 'EXPLAIN_EVEN_VIEW', 'EXPLAIN_CENTROIDS_RA_VIEW',
                         'EXPLAIN_CENTROIDS_DEC_VIEW', 'EXPLAIN_OG_VIEW'])
            for index, row in self.injected_objects_df.iterrows():
                row_copy_df = row.copy().to_frame().T
                final_df = pd.concat([final_df, row_copy_df], ignore_index=True)
                row_copy_df = row.copy().to_frame().T
                row_copy_df['EXPLAIN_GLOBAL_VIEW'] = 'hide'
                row_copy_df['object_id'] = row_copy_df['object_id'] + ' global hide branch'
                final_df = pd.concat([final_df, row_copy_df], ignore_index=True)
                row_copy_df = row.copy().to_frame().T
                row_copy_df['EXPLAIN_MAIN_VIEW'] = 'hide'
                row_copy_df['object_id'] = row_copy_df['object_id'] + ' main hide branch'
                final_df = pd.concat([final_df, row_copy_df], ignore_index=True)
                row_copy_df = row.copy().to_frame().T
                row_copy_df['EXPLAIN_SECONDARY_VIEW'] = 'hide'
                row_copy_df['object_id'] = row_copy_df['object_id'] + ' secondary hide branch'
                final_df = pd.concat([final_df, row_copy_df], ignore_index=True)
                row_copy_df = row.copy().to_frame().T
                row_copy_df['EXPLAIN_SECONDARY_VIEW'] = 'strong'
                row_copy_df['object_id'] = row_copy_df['object_id'] + ' secondary strong branch'
                final_df = pd.concat([final_df, row_copy_df], ignore_index=True)
                row_copy_df = row.copy().to_frame().T
                row_copy_df['EXPLAIN_SECONDARY_VIEW'] = 'plain'
                row_copy_df['object_id'] = row_copy_df['object_id'] + ' secondary plain branch'
                final_df = pd.concat([final_df, row_copy_df], ignore_index=True)
                row_copy_df = row.copy().to_frame().T
                row_copy_df['EXPLAIN_ODD_VIEW'] = 'hide'
                row_copy_df['object_id'] = row_copy_df['object_id'] + ' odd hide branch'
                final_df = pd.concat([final_df, row_copy_df], ignore_index=True)
                row_copy_df = row.copy().to_frame().T
                row_copy_df['EXPLAIN_ODD_VIEW'] = 'strong'
                row_copy_df['object_id'] = row_copy_df['object_id'] + ' odd strong branch'
                final_df = pd.concat([final_df, row_copy_df], ignore_index=True)
                row_copy_df = row.copy().to_frame().T
                row_copy_df['EXPLAIN_ODD_VIEW'] = 'plain'
                row_copy_df['object_id'] = row_copy_df['object_id'] + ' odd plain branch'
                final_df = pd.concat([final_df, row_copy_df], ignore_index=True)
                row_copy_df = row.copy().to_frame().T
                row_copy_df['EXPLAIN_EVEN_VIEW'] = True
                row_copy_df['object_id'] = row_copy_df['object_id'] + ' even hide branch'
                final_df = pd.concat([final_df, row_copy_df], ignore_index=True)
                row_copy_df = row.copy().to_frame().T
                row_copy_df['EXPLAIN_EVEN_VIEW'] = 'strong'
                row_copy_df['object_id'] = row_copy_df['object_id'] + ' even strong branch'
                final_df = pd.concat([final_df, row_copy_df], ignore_index=True)
                row_copy_df = row.copy().to_frame().T
                row_copy_df['EXPLAIN_EVEN_VIEW'] = 'plain'
                row_copy_df['object_id'] = row_copy_df['object_id'] + ' even plain branch'
                final_df = pd.concat([final_df, row_copy_df], ignore_index=True)
                row_copy_df = row.copy().to_frame().T
                row_copy_df['EXPLAIN_CENTROIDS_RA_VIEW'] = 'hide'
                row_copy_df['object_id'] = row_copy_df['object_id'] + ' centroids ra hide branch'
                final_df = pd.concat([final_df, row_copy_df], ignore_index=True)
                row_copy_df = row.copy().to_frame().T
                row_copy_df['EXPLAIN_CENTROIDS_RA_VIEW'] = 'strong'
                row_copy_df['object_id'] = row_copy_df['object_id'] + ' centroids ra strong branch'
                final_df = pd.concat([final_df, row_copy_df], ignore_index=True)
                row_copy_df = row.copy().to_frame().T
                row_copy_df['EXPLAIN_CENTROIDS_RA_VIEW'] = 'plain'
                row_copy_df['object_id'] = row_copy_df['object_id'] + ' centroids ra plain branch'
                final_df = pd.concat([final_df, row_copy_df], ignore_index=True)
                row_copy_df = row.copy().to_frame().T
                row_copy_df['EXPLAIN_CENTROIDS_DEC_VIEW'] = 'hide'
                row_copy_df['object_id'] = row_copy_df['object_id'] + ' centroids dec hide branch'
                final_df = pd.concat([final_df, row_copy_df], ignore_index=True)
                row_copy_df = row.copy().to_frame().T
                row_copy_df['EXPLAIN_CENTROIDS_DEC_VIEW'] = 'strong'
                row_copy_df['object_id'] = row_copy_df['object_id'] + ' centroids dec strong branch'
                final_df = pd.concat([final_df, row_copy_df], ignore_index=True)
                row_copy_df = row.copy().to_frame().T
                row_copy_df['EXPLAIN_CENTROIDS_DEC_VIEW'] = 'plain'
                row_copy_df['object_id'] = row_copy_df['object_id'] + ' centroids dec plain branch'
                final_df = pd.concat([final_df, row_copy_df], ignore_index=True)
                row_copy_df = row.copy().to_frame().T
                row_copy_df['EXPLAIN_OG_VIEW'] = 'hide'
                row_copy_df['object_id'] = row_copy_df['object_id'] + ' og hide branch'
                final_df = pd.concat([final_df, row_copy_df], ignore_index=True)
                row_copy_df = row.copy().to_frame().T
                row_copy_df['EXPLAIN_OG_VIEW'] = 'halo'
                row_copy_df['object_id'] = row_copy_df['object_id'] + ' og halo branch'
                final_df = pd.concat([final_df, row_copy_df], ignore_index=True)
                row_copy_df = row.copy().to_frame().T
                row_copy_df['EXPLAIN_OG_VIEW'] = 'core'
                row_copy_df['object_id'] = row_copy_df['object_id'] + ' og core branch'
                final_df = pd.concat([final_df, row_copy_df], ignore_index=True)
                row_copy_df = row.copy().to_frame().T
                row_copy_df['EXPLAIN_OG_VIEW'] = 'plain'
                row_copy_df['object_id'] = row_copy_df['object_id'] + ' og plain branch'
                final_df = pd.concat([final_df, row_copy_df], ignore_index=True)
                for value in self.EXPLAIN_PERIOD_VALUE:
                    row_copy_df = row.copy().to_frame().T
                    row_copy_df['EXPLAIN_PERIOD_VALUE'] = value
                    row_copy_df['object_id'] = row_copy_df['object_id'] + f' transit period value={value}'
                    final_df = pd.concat([final_df, row_copy_df], ignore_index=True)
                for value in self.EXPLAIN_DURATION_VALUE:
                    row_copy_df = row.copy().to_frame().T
                    row_copy_df['EXPLAIN_DURATION_VALUE'] = value
                    row_copy_df['object_id'] = row_copy_df['object_id'] + f' transit duration value={value}'
                    final_df = pd.concat([final_df, row_copy_df], ignore_index=True)
                for value in self.EXPLAIN_RADIUS_VALUE:
                    row_copy_df = row.copy().to_frame().T
                    row_copy_df['EXPLAIN_RADIUS_VALUE'] = value
                    row_copy_df['object_id'] = row_copy_df['object_id'] + f' planet radius value={value}'
                    final_df = pd.concat([final_df, row_copy_df], ignore_index=True)
                for value in self.EXPLAIN_GTCN_VALUE:
                    row_copy_df = row.copy().to_frame().T
                    row_copy_df['EXPLAIN_GTCN_VALUE'] = value
                    row_copy_df['object_id'] = row_copy_df['object_id'] + f' good transit count value={value}'
                    final_df = pd.concat([final_df, row_copy_df], ignore_index=True)
                for value in self.EXPLAIN_GTR_VALUE:
                    row_copy_df = row.copy().to_frame().T
                    row_copy_df['EXPLAIN_GTR_VALUE'] = value
                    row_copy_df['object_id'] = row_copy_df['object_id'] + f' good transit ratio value={value}'
                    final_df = pd.concat([final_df, row_copy_df], ignore_index=True)
                for value in self.EXPLAIN_OFFSET_VALUE:
                    row_copy_df = row.copy().to_frame().T
                    row_copy_df['EXPLAIN_OFFSET_VALUE'] = value
                    row_copy_df['object_id'] = row_copy_df['object_id'] + f' source offset value={value}'
                    final_df = pd.concat([final_df, row_copy_df], ignore_index=True)
                for value in self.EXPLAIN_BFAP_VALUE:
                    row_copy_df = row.copy().to_frame().T
                    row_copy_df['EXPLAIN_BFAP_VALUE'] = value
                    row_copy_df['object_id'] = row_copy_df['object_id'] + f' bootstrap fap value={value}'
                    final_df = pd.concat([final_df, row_copy_df], ignore_index=True)
                for value in self.EXPLAIN_ODDEVEN_VALUE:
                    row_copy_df = row.copy().to_frame().T
                    row_copy_df['EXPLAIN_ODDEVEN_VALUE'] = value
                    row_copy_df['object_id'] = row_copy_df['object_id'] + f' odd-even factor value={value}'
                    final_df = pd.concat([final_df, row_copy_df], ignore_index=True)
                for value in self.EXPLAIN_TEMP_ALBEDO_VALUE:
                    row_copy_df = row.copy().to_frame().T
                    row_copy_df['EXPLAIN_TEMP_ALBEDO_VALUE'] = value
                    row_copy_df['object_id'] = row_copy_df['object_id'] + f' temp-albedo stat values={value}'
                    final_df = pd.concat([final_df, row_copy_df], ignore_index=True)
                for value in self.EXPLAIN_STARTEFF_VALUE:
                    row_copy_df = row.copy().to_frame().T
                    row_copy_df['EXPLAIN_STARTEFF_VALUE'] = value
                    row_copy_df['object_id'] = row_copy_df['object_id'] + f' star teff value={value}'
                    final_df = pd.concat([final_df, row_copy_df], ignore_index=True)
                for value in self.EXPLAIN_STARRAD_VALUE:
                    row_copy_df = row.copy().to_frame().T
                    row_copy_df['EXPLAIN_STARRAD_VALUE'] = value
                    row_copy_df['object_id'] = row_copy_df['object_id'] + f' star radius value={value}'
                    final_df = pd.concat([final_df, row_copy_df], ignore_index=True)
            self.injected_objects_df = final_df

    def __len__(self):
        return (np.ceil(len(self.injected_objects_df) / float(self.batch_size))).astype(int)

    def class_weights(self):
        return {0: 1, 1: 1}

    def _plot_df(self, df, type, scenario):
        fig, axs = plt.subplots(2, 3, figsize=(12, 6), constrained_layout=True)
        axs[0][0].scatter(df['time'], df['flux'])
        axs[0][1].scatter(df['time'], df['centroid_x'])
        axs[0][2].scatter(df['time'], df['centroid_y'])
        axs[1][0].scatter(df['time'], df['bck_flux'])
        axs[1][1].scatter(df['time'], df['motion_x'])
        axs[1][2].scatter(df['time'], df['motion_y'])
        plt.title(type + " " + scenario)
        plt.show()
        plt.clf()
        plt.close()

    def _plot_input(self, input_array, input_err_array, type, scenario, save_dir=None):
        if self.plot_inputs:
            transposed_array = np.transpose(input_array)
            if transposed_array.shape[0] <= 1:
                fig, axs = plt.subplots(1, 1, figsize=(24, 12), constrained_layout=True)
                current_array = transposed_array[0]
                current_array_mask = np.argwhere(
                    (~np.isnan(current_array)) & (current_array > self.zero_epsilon)).flatten()
                current_array = current_array[current_array_mask]
                axs.scatter(np.arange(0, len(current_array)), current_array)
                axs.set_title("Flux")
            else:
                fig, axs = plt.subplots(2, 1, figsize=(24, 24), constrained_layout=True)
                current_array = transposed_array[0]
                current_array_mask = np.argwhere(
                    (~np.isnan(current_array)) & (current_array > self.zero_epsilon)).flatten()
                current_array = current_array[current_array_mask]
                axs[0].scatter(np.arange(0, len(current_array)), current_array)
                axs[0].set_title("Flux 1")
                current_array = transposed_array[1]
                current_array_mask = np.argwhere(
                    (~np.isnan(current_array)) & (current_array > self.zero_epsilon)).flatten()
                current_array = current_array[current_array_mask]
                axs[1].scatter(np.arange(0, len(current_array)), current_array)
                axs[1].set_title("Flux 2")
            fig.suptitle(type + " " + scenario)
            if save_dir:
                if not os.path.exists(save_dir):
                    os.mkdir(save_dir)
                plt.savefig(f'{save_dir}/{type}_{scenario}.png')
            else:
                plt.show()
            plt.clf()
            plt.close()

    def plot_single_data(self, lc_df, target_row):
        fig, axs = plt.subplots(1, 1, figsize=(8, 4), constrained_layout=True)
        axs.scatter(lc_df['time'], lc_df['flux_0'])
        axs.set_ylim(0.5 - target_row['tce_depth'] / 0.5e6, 0.505)
        plt.show()
        plt.clf()
        plt.close()

    def mask_other_signals(self, data_df, transits_mask, time_key='time'):
        if transits_mask is not None:
            for item_mask in transits_mask:
                mask = foldedleastsquares.transit_mask(data_df[time_key].to_numpy(), item_mask['P'],
                                                       2 * item_mask['D'] / 60 / 24, item_mask['T0'])
                data_df = data_df[~mask]
        return data_df

    def __getitem__(self, idx):
        max_index = (idx + 1) * self.batch_size
        max_index = len(self.injected_objects_df) if max_index > len(self.injected_objects_df) else max_index
        target_indexes = np.arange(idx * self.batch_size, max_index, 1)
        injected_objects_df = self.injected_objects_df.iloc[target_indexes]
        if self.shuffle_batch:
            injected_objects_df = shuffle(injected_objects_df)
        star_array = np.empty((len(target_indexes), 2, 1))
        star_neighbours_array = np.empty((len(target_indexes), self.input_sizes[1], 1))
        #[period, planet radius, number of transits, ratio of good transits, transit depth, transit_offset_pos - transit_offset_err]
        scalar_values = np.empty((len(target_indexes), 12, 1))
        global_flux_array = np.empty((len(target_indexes), self.input_sizes[2], self.measurements_per_point))
        folded_flux_even_array = np.empty((len(target_indexes), self.input_sizes[3], self.measurements_per_point))
        folded_flux_odd_array = np.empty((len(target_indexes), self.input_sizes[3], self.measurements_per_point))
        folded_flux_even_subhar_array = np.empty((len(target_indexes), self.input_sizes[3], self.measurements_per_point))
        folded_flux_odd_subhar_array = np.empty((len(target_indexes), self.input_sizes[3], self.measurements_per_point))
        folded_flux_even_har_array = np.empty((len(target_indexes), self.input_sizes[3], self.measurements_per_point))
        folded_flux_odd_har_array = np.empty((len(target_indexes), self.input_sizes[3], self.measurements_per_point))
        global_flux_array_err = np.empty((len(target_indexes), self.input_sizes[2], self.measurements_per_point))
        folded_flux_even_array_err = np.empty((len(target_indexes), self.input_sizes[3], self.measurements_per_point))
        folded_flux_odd_array_err = np.empty((len(target_indexes), self.input_sizes[3], self.measurements_per_point))
        folded_flux_even_subhar_array_err = np.empty((len(target_indexes), self.input_sizes[3], self.measurements_per_point))
        folded_flux_odd_subhar_array_err = np.empty((len(target_indexes), self.input_sizes[3], self.measurements_per_point))
        folded_flux_even_har_array_err = np.empty((len(target_indexes), self.input_sizes[3], self.measurements_per_point))
        folded_flux_odd_har_array_err = np.empty((len(target_indexes), self.input_sizes[3], self.measurements_per_point))
        folded_centroids_array = np.empty((len(target_indexes), self.input_sizes[3], 2))
        folded_centroids_array_err = np.empty((len(target_indexes), self.input_sizes[3], 2))
        folded_og_array = np.empty((len(target_indexes), self.input_sizes[3], 1))
        folded_og_array_err = np.empty((len(target_indexes), self.input_sizes[3], 1))
        batch_data_values = np.empty((len(target_indexes), 1))
        i = 0
        for df_index, target_row in injected_objects_df.iterrows():
            #TODO refactor to use mission for object_id
            object_id = target_row['object_id'].split(' ')
            mission_id = object_id[0]
            target_id = int(object_id[1].split('_')[0])
            period = target_row['period']
            epoch = target_row['epoch']
            duration = target_row['duration(h)'] / 24
            duration_to_period = duration / period
            batch_data_values[i] = [0]
            file_prefix = self.lcs_dir + '/' #+ mission_id + '_' + str(target_id)
            inputs_save_dir = f'{self.lcs_dir}/iatson/'
            if (not self.use_csvs and not self.explain) or (self.explain and df_index == 0):
                if target_row['object_id'] in self.arrays_cache and 'folded_og_array' in self.arrays_cache[target_row['object_id']]:
                    folded_og_array[i] = self.arrays_cache[target_row['object_id']]['folded_og_array']
                else:
                    og_filename = file_prefix + 'og_dg.csv'
                    og_df = pd.read_csv(og_filename, usecols=['time', 'og_flux', 'halo_flux', 'core_flux'], low_memory=True)
                    og_df = self.mask_other_signals(og_df, transits_mask=self.transit_masks, time_key='time')
                    og_df = self.compute_og_df(og_df, object_id, duration)
                    og_df = og_df.sort_values(by=['time'])
                    og_df['time'] = self.fold(og_df['time'].to_numpy(), period, epoch + period / 2)
                    og_df = og_df.sort_values(by=['time'])
                    og_df = self._prepare_input_og(og_df)
                    og_df = og_df[(og_df['time'] > 0.5 - duration_to_period * 3) & (
                            og_df['time'] < 0.5 + duration_to_period * 3)]
                    folded_og_array[i], folded_og_array_err[i] = self.bin_by_time(og_df.to_numpy(), self.input_sizes[3],
                                                                                  target_row['object_id'])
                    self.arrays_cache[target_row['object_id']] = {}
                    self.arrays_cache[target_row['object_id']]['folded_og_array'] = folded_og_array[i]
                if target_id in self.arrays_cache and 'folded_centroids_array' in self.arrays_cache[target_row['object_id']]:
                    folded_centroids_array[i] = self.arrays_cache[target_row['object_id']]['folded_centroids_array']
                else:
                    centroids_filename = file_prefix + 'centroids.csv'
                    centroids_df = pd.read_csv(centroids_filename, usecols=['time', 'centroids_ra', 'centroids_dec'],
                                                        low_memory=True)
                    centroids_df = self.mask_other_signals(centroids_df, transits_mask=self.transit_masks, time_key='time')
                    centroids_df = centroids_df.sort_values(by=['time'])
                    centroids_df['centroids_ra'], _ = LcbuilderHelper.detrend(centroids_df['time'].to_numpy(),
                                                                                   centroids_df['centroids_ra'].to_numpy(),
                                                                                   duration * 4,
                                                                                   check_cadence=True)
                    centroids_df['centroids_dec'], _ = LcbuilderHelper.detrend(
                        centroids_df['time'].to_numpy(),
                        centroids_df['centroids_dec'].to_numpy(), duration * 4,
                        check_cadence=True)
                    centroids_df['time'] = self.fold(centroids_df['time'].to_numpy(), period, epoch + period / 2)
                    centroids_df = centroids_df.sort_values(by=['time'])
                    centroids_df = self._prepare_input_centroids(centroids_df)
                    centroids_df = centroids_df[(centroids_df['time'] > 0.5 - duration_to_period * 3) & (
                            centroids_df['time'] < 0.5 + duration_to_period * 3)]
                    folded_centroids_array[i], folded_centroids_array_err[i] = self.bin_by_time(centroids_df.to_numpy(), self.input_sizes[3], target_row['object_id'])
                    self.arrays_cache[target_row['object_id']]['folded_centroids_array'] = folded_centroids_array[i]
                if (target_row['object_id'] in self.arrays_cache and 'star_teff' in self.arrays_cache[target_row['object_id']]) and \
                        (target_row['object_id'] in self.arrays_cache and 'star_radius' in self.arrays_cache[target_row['object_id']]):
                    star_array[i] = [[self.arrays_cache[target_row['object_id']]['star_teff']],
                                     [self.arrays_cache[target_row['object_id']]['star_radius']]]
                    ra = self.arrays_cache[target_row['object_id']]['ra']
                    dec = self.arrays_cache[target_row['object_id']]['dec']
                else:
                    star_df = pd.read_csv(self.star_filename, usecols=['Teff', 'radius', 'ra', 'dec'],
                                          index_col=False)
                    star_df, ra, dec = self._prepare_input_star(target_row, star_df)
                    star_df['Teff'] = star_df['Teff'] if star_df['Teff'] <= 1 else 1
                    star_df['radius'] = star_df['radius'] if star_df['radius'] <= 1 else 1
                    star_array[i] = np.transpose([star_df.to_numpy()])
                    self.arrays_cache[target_row['object_id']]['ra'] = ra
                    self.arrays_cache[target_row['object_id']]['dec'] = dec
                    self.arrays_cache[target_row['object_id']]['star_teff'] = star_df['Teff']
                    self.arrays_cache[target_row['object_id']]['star_radius'] = star_df['radius']
                if target_row['object_id'] in self.arrays_cache and 'scalar_values' in self.arrays_cache[target_row['object_id']]:
                    scalar_values[i] = self.arrays_cache[target_row['object_id']]['scalar_values']
                    global_flux_array[i] = self.arrays_cache[target_row['object_id']]['global_flux_array']
                    folded_flux_odd_array[i] = self.arrays_cache[target_row['object_id']]['folded_flux_odd_array']
                    folded_flux_even_array[i] = self.arrays_cache[target_row['object_id']]['folded_flux_even_array']
                    folded_flux_even_har_array[i] = self.arrays_cache[target_row['object_id']]['folded_flux_even_har_array']
                    folded_flux_odd_har_array[i] = self.arrays_cache[target_row['object_id']]['folded_flux_odd_har_array']
                    folded_flux_even_subhar_array[i] = self.arrays_cache[target_row['object_id']]['folded_flux_even_subhar_array']
                    folded_flux_odd_subhar_array[i] = self.arrays_cache[target_row['object_id']]['folded_flux_odd_subhar_array']
                else:
                    lc_filename = self.lc_filename
                    lc_df = pd.read_csv(lc_filename, usecols=['time', 'flux'], low_memory=True)
                    if lc_df is None:
                        logging.warning("No curve for target " + file_prefix)
                        raise ValueError("No curve for target " + file_prefix)
                    lc_df = lc_df.sort_values(by=['time'])
                    lc_df = self.mask_other_signals(lc_df, transits_mask=self.transit_masks, time_key='time')
                    lc_df['flux'] = wotan.flatten(lc_df['time'].to_numpy(), lc_df['flux'].to_numpy(), duration * 4,
                                                  method='biweight')
                    lc_df, good_transits_count, transits_count = self._prepare_input_lc(lc_df, period, epoch, duration,
                                                                                        time_key='time', flux_key='flux')
                    not_null_times_args = np.argwhere(lc_df['time'].to_numpy() > 0).flatten()
                    lc_df = lc_df.iloc[not_null_times_args]
                    time = lc_df['time'].to_numpy()
                    # Global flux
                    # Shifting data 1/4 so that main transit and possible occultation don't get cut by the borders
                    lc_df_sorted_fold = lc_df.copy()
                    lc_df_sorted_fold['time'] = self.fold(time, period, epoch + period / 4)
                    lc_df_sorted_fold = lc_df_sorted_fold.sort_values(by=['time'])
                    global_flux_array[i], global_flux_array_err[i] = \
                        self.bin_by_time(lc_df_sorted_fold.to_numpy(), self.input_sizes[2], target_row['object_id'])
                    # Focus flux even
                    lc_df_focus = lc_df.copy()
                    lc_df_focus['time'] = self.fold(time, period, epoch)
                    lc_df_focus = lc_df_focus.sort_values(by=['time'])
                    lc_df_focus = lc_df_focus[(lc_df_focus['time'] > 0.5 - duration_to_period * 3) &
                                              (lc_df_focus['time'] < 0.5 + duration_to_period * 3)]
                    folded_flux_even_array[i], folded_flux_even_array_err[i] = \
                        self.bin_by_time(lc_df_focus.to_numpy(), self.input_sizes[3], target_row['object_id'])
                    # Focus flux odd
                    lc_df_focus = lc_df.copy()
                    lc_df_focus['time'] = self.fold(time, period, epoch + period / 2)
                    lc_df_focus = lc_df_focus.sort_values(by=['time'])
                    lc_df_focus = lc_df_focus[(lc_df_focus['time'] > 0.5 - duration_to_period * 3) &
                                              (lc_df_focus['time'] < 0.5 + duration_to_period * 3)]
                    folded_flux_odd_array[i], folded_flux_odd_array_err[i] = \
                        self.bin_by_time(lc_df_focus.to_numpy(), self.input_sizes[4], target_row['object_id'])
                    # Focus flux harmonic even
                    lc_df_focus = lc_df.copy()
                    lc_df_focus['time'] = self.fold(time, period * 2, epoch)
                    lc_df_focus = lc_df_focus.sort_values(by=['time'])
                    lc_df_focus = lc_df_focus[(lc_df_focus['time'] > 0.5 - duration_to_period * 1.5) &
                                              (lc_df_focus['time'] < 0.5 + duration_to_period * 1.5)]
                    oot_lc_df_focus = lc_df_focus[((lc_df_focus['time'] <= 0.5 - duration_to_period / 4) |
                                                   (lc_df_focus['time'] >= 0.5 + duration_to_period / 4))]
                    it_lc_df_focus = lc_df_focus[((lc_df_focus['time'] > 0.5 - duration_to_period / 4) &
                                                  (lc_df_focus['time'] < 0.5 + duration_to_period / 4))]
                    depth_even = (oot_lc_df_focus['flux'].mean() - it_lc_df_focus['flux'].mean()) * np.sqrt(
                        len(it_lc_df_focus)) / oot_lc_df_focus['flux'].std()
                    folded_flux_even_har_array[i], folded_flux_even_har_array_err[i] = \
                        self.bin_by_time(lc_df_focus.to_numpy(), self.input_sizes[7], target_row['object_id'])
                    # Focus flux harmonic odd
                    lc_df_focus = lc_df.copy()
                    lc_df_focus['time'] = self.fold(time, period * 2, epoch + period)
                    lc_df_focus = lc_df_focus.sort_values(by=['time'])
                    lc_df_focus = lc_df_focus[(lc_df_focus['time'] > 0.5 - duration_to_period * 1.5) &
                                              (lc_df_focus['time'] < 0.5 + duration_to_period * 1.5)]
                    oot_lc_df_focus = lc_df_focus[((lc_df_focus['time'] <= 0.5 - duration_to_period / 4) |
                                                   (lc_df_focus['time'] >= 0.5 + duration_to_period / 4))]
                    it_lc_df_focus = lc_df_focus[((lc_df_focus['time'] > 0.5 - duration_to_period / 4) &
                                                  (lc_df_focus['time'] < 0.5 + duration_to_period / 4))]
                    depth_odd = (oot_lc_df_focus['flux'].mean() - it_lc_df_focus['flux'].mean()) * np.sqrt(
                        len(it_lc_df_focus)) / oot_lc_df_focus['flux'].std()
                    folded_flux_odd_har_array[i], folded_flux_odd_har_array_err[i] = \
                        self.bin_by_time(lc_df_focus.to_numpy(), self.input_sizes[8], target_row['object_id'])
                    # Focus flux sub-harmonic even
                    lc_df_focus = pd.DataFrame(columns=['time', 'flux'])
                    time, flux0, _ = LcbuilderHelper.mask_transits(time,
                                                                   lc_df.copy()['flux'].to_numpy(), period,
                                                                   duration * 2,
                                                                   epoch)
                    lc_df_focus['time'] = time
                    lc_df_focus['flux'] = flux0
                    lc_df_focus['time'] = self.fold(time, period / 2, epoch)
                    lc_df_focus = lc_df_focus.sort_values(by=['time'])
                    lc_df_focus = lc_df_focus[(lc_df_focus['time'] > 0.5 - duration_to_period * 3) &
                                              (lc_df_focus['time'] < 0.5 + duration_to_period * 3)]
                    folded_flux_even_subhar_array[i], folded_flux_even_subhar_array_err[i] = \
                        self.bin_by_time(lc_df_focus.to_numpy(), self.input_sizes[5], target_row['object_id'])
                    # Focus flux sub-harmonic odd
                    lc_df_focus = pd.DataFrame(columns=['time', 'flux'])
                    lc_df_focus['time'] = time
                    lc_df_focus['flux'] = flux0
                    lc_df_focus['time'] = self.fold(time, period / 2, epoch + period / 4)
                    lc_df_focus = lc_df_focus.sort_values(by=['time'])
                    lc_df_focus = lc_df_focus[(lc_df_focus['time'] > 0.5 - duration_to_period * 3) &
                                              (lc_df_focus['time'] < 0.5 + duration_to_period * 3)]
                    folded_flux_odd_subhar_array[i], folded_flux_odd_subhar_array_err[i] = \
                        self.bin_by_time(lc_df_focus.to_numpy(), self.input_sizes[6], target_row['object_id'])
                    oe_factor = np.abs(depth_even - depth_odd)
                    oe_factor = oe_factor / 5 if oe_factor < 5 else 1 - self.zero_epsilon
                    oe_factor = oe_factor if not np.isnan(oe_factor) and oe_factor > 0 else self.zero_epsilon
                    offset_filename = file_prefix + 'source_offsets.csv'
                    offset_df = pd.read_csv(offset_filename, low_memory=True)
                    row = offset_df[offset_df['name'] == 'mean'].iloc[0]
                    offset_ra = row['ra']
                    offset_dec = row['dec']
                    offset_ra_err = row['ra_err']
                    offset_dec_err = row['dec_err']
                    target_dist = np.sqrt((offset_ra - ra) ** 2 + (offset_dec - dec) ** 2)
                    target_dist = target_dist if not np.isnan(target_dist) else self.zero_epsilon
                    offset_err = offset_ra_err if offset_ra_err > offset_dec_err else offset_dec_err
                    offset_err = offset_err if offset_err > 0 else target_dist * 2
                    offset_err = offset_err / (target_dist * 2)
                    target_dist = target_dist if target_dist < 1 else 1 - self.zero_epsilon
                    offset_err = 1 - self.zero_epsilon if offset_err >= 1 else offset_err
                    offset_err = offset_err if offset_err > 0 else self.zero_epsilon
                    metrics_df = pd.read_csv(file_prefix + 'metrics.csv')
                    temperature_stat = metrics_df.loc[metrics_df['metric'] == 'temp_stat'].iloc[0]['score']
                    albedo_stat = metrics_df.loc[metrics_df['metric'] == 'albedo_stat'].iloc[0]['score']
                    bootstrap_fap = metrics_df.loc[metrics_df['metric'] == 'bootstrap_fap'].iloc[0]['score']
                    oe_factor = np.abs(depth_even - depth_odd)
                    oe_factor = oe_factor / 5 if oe_factor < 5 else 1 - self.zero_epsilon
                    oe_factor = oe_factor if not np.isnan(oe_factor) and oe_factor > 0 else self.zero_epsilon
                    if np.isnan(temperature_stat):
                        temperature_stat = 0
                    elif temperature_stat < -10:
                        temperature_stat = -10
                    elif temperature_stat > 10:
                        temperature_stat = 10
                    temperature_stat = (temperature_stat + 10) / 20
                    temperature_stat = temperature_stat if temperature_stat > 0 else self.zero_epsilon
                    temperature_stat = temperature_stat if temperature_stat < 1 else 1 - self.zero_epsilon
                    if np.isnan(albedo_stat):
                        albedo_stat = 0
                    elif albedo_stat < -10:
                        albedo_stat = -10
                    elif albedo_stat > 10:
                        albedo_stat = 10
                    albedo_stat = (albedo_stat + 10) / 20
                    albedo_stat = albedo_stat if albedo_stat > 0 else self.zero_epsilon
                    albedo_stat = albedo_stat if albedo_stat < 1 else 1 - self.zero_epsilon
                    good_transits_count_norm = good_transits_count / 20
                    good_transits_count_norm = good_transits_count_norm if good_transits_count_norm < 1 else 1 - self.zero_epsilon
                    good_transits_ratio = good_transits_count / transits_count if transits_count > 0 else self.zero_epsilon
                    good_transits_ratio = good_transits_ratio if good_transits_ratio < 1 else 1 - self.zero_epsilon
                    planet_radius = target_row['radius(earth)'] / 300
                    planet_radius = planet_radius if planet_radius < 1 else 1 - self.zero_epsilon
                    depth = target_row['depth_primary'] / 1e3
                    depth = depth if depth < 1 else 1 - self.zero_epsilon
                    duration = duration / 15
                    duration = duration if duration < 1 else 1 - self.zero_epsilon
                    scalar_values[i] = np.array([[period / 1200 if period < 1200 else 1],
                                                      [duration],
                                                      [depth],
                                                      [planet_radius],
                                                      [good_transits_count_norm],
                                                      [good_transits_ratio],
                                                      [target_dist if not np.isnan(target_dist) else self.zero_epsilon],
                                                      [offset_err],
                                                      [bootstrap_fap],
                                                      [oe_factor],
                                                      [temperature_stat],
                                                      [albedo_stat]])
                    self.arrays_cache[target_row['object_id']]['global_flux_array'] = global_flux_array[i]
                    self.arrays_cache[target_row['object_id']]['folded_flux_even_array'] = folded_flux_even_array[i]
                    self.arrays_cache[target_row['object_id']]['folded_flux_odd_array'] = folded_flux_odd_array[i]
                    self.arrays_cache[target_row['object_id']]['folded_flux_even_subhar_array'] = folded_flux_even_subhar_array[i]
                    self.arrays_cache[target_row['object_id']]['folded_flux_odd_subhar_array'] = folded_flux_odd_subhar_array[i]
                    self.arrays_cache[target_row['object_id']]['folded_flux_even_har_array'] = folded_flux_even_har_array[i]
                    self.arrays_cache[target_row['object_id']]['folded_flux_odd_har_array'] = folded_flux_odd_har_array[i]
                    self.arrays_cache[target_row['object_id']]['scalar_values'] = scalar_values[i]
            else:
                scalar_values[i] = [[e] for e in np.loadtxt(inputs_save_dir + 'input_scalar_values.csv', delimiter=',')]
                star_array[i] = [[e] for e in np.loadtxt(inputs_save_dir + 'input_star.csv', delimiter=',')]
                star_neighbours_array[i] = [[e] for e in np.loadtxt(inputs_save_dir + 'input_nb.csv', delimiter=',')]
                global_flux_array[i] = np.loadtxt(inputs_save_dir + 'input_global.csv', delimiter=',').reshape(-1, 1)
                global_flux_array_err[i] = np.loadtxt(inputs_save_dir + 'input_global_err.csv', delimiter=',').reshape(-1, 1)
                folded_flux_even_array[i] = np.loadtxt(inputs_save_dir + 'input_even.csv', delimiter=',').reshape(-1, 1)
                folded_flux_even_array_err[i] = np.loadtxt(inputs_save_dir + 'input_even_err.csv', delimiter=',').reshape(-1, 1)
                folded_flux_odd_array[i] = np.loadtxt(inputs_save_dir + 'input_odd.csv', delimiter=',').reshape(-1, 1)
                folded_flux_odd_array_err[i] = np.loadtxt(inputs_save_dir + 'input_odd_err.csv', delimiter=',').reshape(-1, 1)
                folded_flux_even_subhar_array[i] = np.loadtxt(inputs_save_dir + 'input_even_sh.csv', delimiter=',').reshape(-1, 1)
                folded_flux_even_subhar_array_err[i] = np.loadtxt(inputs_save_dir + 'input_even_sh_err.csv', delimiter=',').reshape(-1, 1)
                folded_flux_odd_subhar_array[i] = np.loadtxt(inputs_save_dir + 'input_odd_sh.csv', delimiter=',').reshape(-1, 1)
                folded_flux_odd_subhar_array_err[i] = np.loadtxt(inputs_save_dir + 'input_odd_sh_err.csv', delimiter=',').reshape(-1, 1)
                folded_flux_even_har_array[i] = np.loadtxt(inputs_save_dir + 'input_even_h.csv', delimiter=',').reshape(-1, 1)
                folded_flux_even_har_array_err[i] = np.loadtxt(inputs_save_dir + 'input_even_h_err.csv', delimiter=',').reshape(-1, 1)
                folded_flux_odd_har_array[i] = np.loadtxt(inputs_save_dir + 'input_odd_h.csv', delimiter=',').reshape(-1, 1)
                folded_flux_odd_har_array_err[i] = np.loadtxt(inputs_save_dir + 'input_odd_h_err.csv', delimiter=',').reshape(-1, 1)
                folded_centroids_array[i] = np.loadtxt(inputs_save_dir + 'input_centroids.csv', delimiter=',')
                folded_centroids_array_err[i] = np.loadtxt(inputs_save_dir + 'input_centroids_err.csv', delimiter=',')
                folded_og_array[i] = np.loadtxt(inputs_save_dir + 'input_og.csv', delimiter=',').reshape(-1, 1)
                folded_og_array_err[i] = np.loadtxt(inputs_save_dir + 'input_og_err.csv', delimiter=',').reshape(-1, 1)
            self.assert_in_range(object_id, scalar_values[i], None)
            self.assert_in_range(object_id, global_flux_array[i], None)
            self.assert_in_range(object_id, star_array[i], None)
            self.assert_in_range(object_id, folded_flux_even_array[i], None)
            self.assert_in_range(object_id, folded_flux_odd_array[i], None)
            self.assert_in_range(object_id, folded_flux_even_subhar_array[i], None)
            self.assert_in_range(object_id, folded_flux_odd_subhar_array[i], None)
            self.assert_in_range(object_id, folded_flux_even_har_array[i], None)
            self.assert_in_range(object_id, folded_flux_odd_har_array[i], None)
            self.assert_in_range(object_id, folded_centroids_array[i], None)
            self.assert_in_range(object_id, folded_og_array[i], None)
            if df_index == 0:
                self._plot_input(global_flux_array[i], None, target_row['object_id'], "original_global",
                                 save_dir=inputs_save_dir)
                self._plot_input(folded_flux_even_array[i], None, target_row['object_id'], "original_secondary",
                                 save_dir=inputs_save_dir)
                self._plot_input(folded_flux_odd_array[i], None, target_row['object_id'], "original_main",
                                 save_dir=inputs_save_dir)
                self._plot_input(folded_flux_even_har_array[i], None, target_row['object_id'], "original_even",
                                 save_dir=inputs_save_dir)
                self._plot_input(folded_flux_odd_har_array[i], None, target_row['object_id'], "original_odd",
                                 save_dir=inputs_save_dir)
                self._plot_input(folded_og_array[i], None, target_row['object_id'], "original_og", save_dir=inputs_save_dir)
                self._plot_input(folded_centroids_array[i], None, target_row['object_id'], "original_centroids",
                                 save_dir=inputs_save_dir)
                np.savetxt(inputs_save_dir + 'input_scalar_values.csv', scalar_values[i], delimiter=',')
                np.savetxt(inputs_save_dir + 'input_star.csv', star_array[i], delimiter=',')
                np.savetxt(inputs_save_dir + 'input_nb.csv', star_neighbours_array[i], delimiter=',')
                np.savetxt(inputs_save_dir + 'input_global.csv', global_flux_array[i], delimiter=',')
                np.savetxt(inputs_save_dir + 'input_global_err.csv', global_flux_array_err[i], delimiter=',')
                np.savetxt(inputs_save_dir + 'input_even.csv', folded_flux_even_array[i], delimiter=',')
                np.savetxt(inputs_save_dir + 'input_even_err.csv', folded_flux_even_array_err[i], delimiter=',')
                np.savetxt(inputs_save_dir + 'input_odd.csv', folded_flux_odd_array[i], delimiter=',')
                np.savetxt(inputs_save_dir + 'input_odd_err.csv', folded_flux_odd_array_err[i], delimiter=',')
                np.savetxt(inputs_save_dir + 'input_even_sh.csv', folded_flux_even_subhar_array[i], delimiter=',')
                np.savetxt(inputs_save_dir + 'input_even_sh_err.csv', folded_flux_even_subhar_array_err[i], delimiter=',')
                np.savetxt(inputs_save_dir + 'input_odd_sh.csv', folded_flux_odd_subhar_array[i], delimiter=',')
                np.savetxt(inputs_save_dir + 'input_odd_sh_err.csv', folded_flux_odd_subhar_array_err[i], delimiter=',')
                np.savetxt(inputs_save_dir + 'input_even_h.csv', folded_flux_even_har_array[i], delimiter=',')
                np.savetxt(inputs_save_dir + 'input_even_h_err.csv', folded_flux_even_har_array_err[i], delimiter=',')
                np.savetxt(inputs_save_dir + 'input_odd_h.csv', folded_flux_odd_har_array[i], delimiter=',')
                np.savetxt(inputs_save_dir + 'input_odd_h_err.csv', folded_flux_odd_har_array_err[i], delimiter=',')
                np.savetxt(inputs_save_dir + 'input_centroids.csv', folded_centroids_array[i], delimiter=',')
                np.savetxt(inputs_save_dir + 'input_centroids_err.csv', folded_centroids_array_err[i], delimiter=',')
                np.savetxt(inputs_save_dir + 'input_og.csv', folded_og_array[i], delimiter=',')
                np.savetxt(inputs_save_dir + 'input_og_err.csv', folded_og_array_err[i], delimiter=',')
            if self.explain:
                scenario = None
                if 'EXPLAIN_PERIOD_VALUE' in target_row and not np.isnan(target_row['EXPLAIN_PERIOD_VALUE']):
                    scalar_values[i, 0] = target_row['EXPLAIN_PERIOD_VALUE']
                if 'EXPLAIN_DURATION_VALUE' in target_row and not np.isnan(target_row['EXPLAIN_DURATION_VALUE']):
                    scalar_values[i, 1] = target_row['EXPLAIN_DURATION_VALUE']
                if 'EXPLAIN_RADIUS_VALUE' in target_row and not np.isnan(target_row['EXPLAIN_RADIUS_VALUE']):
                    scalar_values[i, 3] = target_row['EXPLAIN_RADIUS_VALUE']
                if 'EXPLAIN_GTCN_VALUE' in target_row and not np.isnan(target_row['EXPLAIN_GTCN_VALUE']):
                    scalar_values[i, 4] = target_row['EXPLAIN_GTCN_VALUE']
                if 'EXPLAIN_GTR_VALUE' in target_row and not np.isnan(target_row['EXPLAIN_GTR_VALUE']):
                    scalar_values[i, 5] = target_row['EXPLAIN_GTR_VALUE']
                if 'EXPLAIN_OFFSET_VALUE' in target_row and not np.isnan(target_row['EXPLAIN_OFFSET_VALUE']):
                    scalar_values[i, 7] = target_row['EXPLAIN_OFFSET_VALUE']
                if 'EXPLAIN_ODDEVEN_VALUE' in target_row and not np.isnan(target_row['EXPLAIN_ODDEVEN_VALUE']):
                    scalar_values[i, 8] = target_row['EXPLAIN_ODDEVEN_VALUE']
                if 'EXPLAIN_BFAP_VALUE' in target_row and not np.isnan(target_row['EXPLAIN_BFAP_VALUE']):
                    scalar_values[i, 9] = target_row['EXPLAIN_BFAP_VALUE']
                explain_temp_albedo_value = str(target_row['EXPLAIN_TEMP_ALBEDO_VALUE'])
                if ('EXPLAIN_TEMP_ALBEDO_VALUE' in target_row and len(explain_temp_albedo_value) > 0
                        and explain_temp_albedo_value != 'nan'):
                    scalar_values[i, 10] = explain_temp_albedo_value.split(',')[0]
                    scalar_values[i, 11] = explain_temp_albedo_value.split(',')[1]
                if 'EXPLAIN_STARTEFF_VALUE' in target_row and not np.isnan(target_row['EXPLAIN_STARTEFF_VALUE']):
                    star_array[i, 0] = target_row['EXPLAIN_STARTEFF_VALUE']
                if 'EXPLAIN_STARRAD_VALUE' in target_row and not np.isnan(target_row['EXPLAIN_STARRAD_VALUE']):
                    star_array[i, 1] = target_row['EXPLAIN_STARRAD_VALUE']
                std = np.nanstd(folded_flux_odd_array[i])
                if 'EXPLAIN_GLOBAL_VIEW' in target_row:
                    if target_row['EXPLAIN_GLOBAL_VIEW'] == 'hide':
                        global_flux_array[i] = np.zeros(global_flux_array[i].shape)
                        self._plot_input(global_flux_array[i], None, target_row['object_id'], f"global",
                                         save_dir=inputs_save_dir)
                if 'EXPLAIN_MAIN_VIEW' in target_row:
                    if target_row['EXPLAIN_MAIN_VIEW'] == 'hide':
                        folded_flux_odd_array[i] = np.zeros(folded_flux_odd_array[i].shape)
                        self._plot_input(folded_flux_even_array[i], None, target_row['object_id'], f"main",
                                         save_dir=inputs_save_dir)
                    elif target_row['EXPLAIN_MAIN_VIEW'] == 'strong':
                        folded_flux_odd_array[i] = folded_flux_odd_array[i]
                        self._plot_input(folded_flux_even_array[i], None, target_row['object_id'], f"main",
                                         save_dir=inputs_save_dir)
                    elif target_row['EXPLAIN_MAIN_VIEW'] == 'plain':
                        folded_flux_odd_array[i] = np.random.normal(loc=0.5, scale=std, size=folded_flux_odd_array[i].shape)
                        self._plot_input(folded_flux_even_array[i], None, target_row['object_id'], f"main",
                                         save_dir=inputs_save_dir)
                if 'EXPLAIN_SECONDARY_VIEW' in target_row:
                    if target_row['EXPLAIN_SECONDARY_VIEW'] == 'hide':
                        folded_flux_even_array[i] = np.zeros(folded_flux_even_array[i].shape)
                        self._plot_input(folded_flux_even_array[i], None, target_row['object_id'], f"even",
                                         save_dir=inputs_save_dir)
                    elif target_row['EXPLAIN_SECONDARY_VIEW'] == 'strong':
                        folded_flux_even_array[i] = folded_flux_even_array[i]
                        self._plot_input(folded_flux_even_array[i], None, target_row['object_id'], f"even",
                                         save_dir=inputs_save_dir)
                    elif target_row['EXPLAIN_SECONDARY_VIEW'] == 'plain':
                        folded_flux_even_array[i] = np.random.normal(loc=0.5, scale=std, size=folded_flux_even_array[i].shape)
                        self._plot_input(folded_flux_even_array[i], None, target_row['object_id'], f"even",
                                         save_dir=inputs_save_dir)
                if 'EXPLAIN_ODD_VIEW' in target_row:
                    if target_row['EXPLAIN_ODD_VIEW'] == 'hide':
                        folded_flux_odd_har_array[i] = np.zeros(folded_flux_odd_har_array[i].shape)
                        self._plot_input(folded_flux_odd_har_array[i], None, target_row['object_id'], f"odd",
                                         save_dir=inputs_save_dir)
                    elif target_row['EXPLAIN_ODD_VIEW'] == 'strong':
                        folded_flux_odd_har_array[i] = folded_flux_odd_har_array[i]
                        self._plot_input(folded_flux_odd_har_array[i], None, target_row['object_id'], f"odd",
                                         save_dir=inputs_save_dir)
                    elif target_row['EXPLAIN_ODD_VIEW'] == 'plain':
                        folded_flux_odd_har_array[i] = np.random.normal(loc=1.0, scale=std, size=folded_flux_odd_har_array[i].shape)
                        self._plot_input(folded_flux_odd_har_array[i], None, target_row['object_id'], f"odd",
                                         save_dir=inputs_save_dir)
                if 'EXPLAIN_EVEN_VIEW' in target_row:
                    if target_row['EXPLAIN_EVEN_VIEW'] == 'hide':
                        folded_flux_even_har_array[i] = np.zeros(folded_flux_even_har_array[i].shape)
                        self._plot_input(folded_flux_even_har_array[i], None, target_row['object_id'], f"even",
                                         save_dir=inputs_save_dir)
                    elif target_row['EXPLAIN_EVEN_VIEW'] == 'strong':
                        folded_flux_even_har_array[i] = folded_flux_even_har_array[i]
                        self._plot_input(folded_flux_even_array[i], None, target_row['object_id'], f"even",
                                         save_dir=inputs_save_dir)
                    elif target_row['EXPLAIN_EVEN_VIEW'] == 'plain':
                        folded_flux_even_har_array[i] = np.random.normal(loc=1.0, scale=std, size=folded_flux_even_har_array[i].shape)
                        self._plot_input(folded_flux_even_array[i], None, target_row['object_id'], f"even",
                                         save_dir=inputs_save_dir)
                if 'EXPLAIN_CENTROIDS_RA_VIEW' in target_row or 'EXPLAIN_CENTROIDS_DEC_VIEW' in target_row:
                    if target_row['EXPLAIN_CENTROIDS_RA_VIEW'] == 'hide':
                        folded_centroids_array[i, :, 0] = np.zeros(folded_centroids_array[i, :, 0].shape)
                        self._plot_input(folded_centroids_array[i], None, target_row['object_id'], f"centroids",
                                         save_dir=inputs_save_dir)
                    elif target_row['EXPLAIN_CENTROIDS_RA_VIEW'] == 'strong':
                        folded_centroids_array[i, :, 0] = folded_flux_odd_array[i].flatten()
                        self._plot_input(folded_centroids_array[i], None, target_row['object_id'], f"centroids",
                                         save_dir=inputs_save_dir)
                    elif target_row['EXPLAIN_CENTROIDS_RA_VIEW'] == 'plain':
                        folded_centroids_array[i, :, 0] = np.random.normal(loc=1.0, scale=std, size=folded_centroids_array[i, :, 0].shape)
                        self._plot_input(folded_centroids_array[i], None, target_row['object_id'], f"centroids",
                                         save_dir=inputs_save_dir)
                    if target_row['EXPLAIN_CENTROIDS_DEC_VIEW'] == 'hide':
                        folded_centroids_array[i, :, 1] = np.zeros(folded_centroids_array[i, :, 1].shape)
                        self._plot_input(folded_centroids_array[i], None, target_row['object_id'], f"centroids",
                                         save_dir=inputs_save_dir)
                    elif target_row['EXPLAIN_CENTROIDS_DEC_VIEW'] == 'strong':
                        folded_centroids_array[i, :, 1] = folded_flux_odd_array[i].flatten()
                        self._plot_input(folded_centroids_array[i], None, target_row['object_id'], f"centroids",
                                         save_dir=inputs_save_dir)
                    elif target_row['EXPLAIN_CENTROIDS_DEC_VIEW'] == 'plain':
                        folded_centroids_array[i, :, 1] = np.random.normal(loc=1.0, scale=std, size=folded_centroids_array[i, :, 1].shape)
                        self._plot_input(folded_centroids_array[i], None, target_row['object_id'], f"centroids",
                                         save_dir=inputs_save_dir)
                if 'EXPLAIN_OG_VIEW' in target_row:
                    if target_row['EXPLAIN_OG_VIEW'] == 'hide':
                        folded_og_array[i] = np.zeros(folded_og_array[i].shape)
                        self._plot_input(folded_og_array[i], None, target_row['object_id'], f"og",
                                         save_dir=inputs_save_dir)
                    elif target_row['EXPLAIN_OG_VIEW'] == 'core':
                        folded_og_array[i] = folded_og_array[i]
                        self._plot_input(folded_og_array[i], None, target_row['object_id'], f"og",
                                         save_dir=inputs_save_dir)
                    elif target_row['EXPLAIN_OG_VIEW'] == 'halo':
                        folded_og_array[i] = (1 - folded_og_array[i])
                        self._plot_input(folded_og_array[i], None, target_row['object_id'], f"og",
                                         save_dir=inputs_save_dir)
                    elif target_row['EXPLAIN_OG_VIEW'] == 'plain':
                        folded_og_array[i] = np.random.normal(loc=1.0, scale=std, size=folded_og_array[i].shape)
                        self._plot_input(folded_og_array[i], None, target_row['object_id'], f"og",
                                         save_dir=inputs_save_dir)
            i = i + 1
        filter_channels = np.array([0, 1, 6, 7, 8, 9, 10, 11])
        return (scalar_values[:, [0, 1, 3, 4, 5, 8, 9, 10, 11]], scalar_values[:, [7]],
                star_array, #Only Teff, Rad and Mass
                global_flux_array,
                folded_flux_even_array,
                folded_flux_odd_array,
                folded_flux_even_har_array,
                folded_flux_odd_har_array,
                folded_centroids_array, folded_og_array), \
            batch_data_values

    def __iter__(self):
        for i in range(len(self)):
            yield self[i]

    def get_dataset(self):
        input_sizes = self.input_sizes
        mpp = self.measurements_per_point

        x_spec = (
            tf.TensorSpec(shape=(None, 9, 1), dtype=tf.float32),  # scalar_values[:, [0,1,3,4,5,8,9,10,11]]
            tf.TensorSpec(shape=(None, 1, 1), dtype=tf.float32),  # scalar_values[:, [7]]
            tf.TensorSpec(shape=(None, 2, 1), dtype=tf.float32),  # star_array[:, [2, 6]]
            tf.TensorSpec(shape=(None, input_sizes[2], mpp), dtype=tf.float32),  # global_flux_array
            tf.TensorSpec(shape=(None, input_sizes[3], mpp), dtype=tf.float32),  # folded_flux_even_array
            tf.TensorSpec(shape=(None, input_sizes[3], mpp), dtype=tf.float32),  # folded_flux_odd_array
            tf.TensorSpec(shape=(None, input_sizes[3], mpp), dtype=tf.float32),  # folded_flux_even_har_array
            tf.TensorSpec(shape=(None, input_sizes[3], mpp), dtype=tf.float32),  # folded_flux_odd_har_array
            tf.TensorSpec(shape=(None, input_sizes[3], 2), dtype=tf.float32),  # folded_centroids_array
            tf.TensorSpec(shape=(None, input_sizes[3], 1), dtype=tf.float32),  # folded_og_array
        )

        y_spec = tf.TensorSpec(shape=(None, 1,), dtype=tf.float32)  # Adjust if label shape is different

        return tf.data.Dataset.from_generator(
            lambda: iter(self),
            output_signature=(x_spec, y_spec)
        ).take(len(self))
