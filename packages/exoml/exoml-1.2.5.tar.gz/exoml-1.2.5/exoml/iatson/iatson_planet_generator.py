import logging
import os
import random

import matplotlib.pyplot as plt
import foldedleastsquares
from lcbuilder.constants import MISSION_TESS, MISSION_ID_TESS, MISSION_KEPLER
from lcbuilder.helper import LcbuilderHelper
from lcbuilder.star.HabitabilityCalculator import HabitabilityCalculator
from numpy.random import default_rng
import astropy.units as u
from exoml.ete6.ete6_generator import Ete6ModelGenerator
from sklearn.utils import shuffle
import numpy as np
import pandas as pd
import tensorflow as tf


class IatsonPlanetModelGenerator(Ete6ModelGenerator):
    def __init__(self, injected_objects_df, lcs_dir, batch_size, input_sizes, type_to_label, zero_epsilon=1e-7,
                 measurements_per_point=1, plot_inputs=False, fixed_target_id=None, store_arrays=False,
                 from_arrays=True, shuffle_batch=True, validation_objects_df=None, mask_previous_signals=False,
                 flag_incomplete=False, throw_nan_exception=False, offset_mode='mean', explain=False):
        super().__init__(zero_epsilon, shuffle_batch=shuffle_batch, flag_incomplete=flag_incomplete,
                         throw_nan_exception=throw_nan_exception)
        self.injected_objects_df = injected_objects_df
        self.injected_objects_df = injected_objects_df
        self.EXPLAIN_PERIOD_VALUE = [self.zero_epsilon, 0.5, 1 - self.zero_epsilon]
        self.EXPLAIN_DURATION_VALUE = [self.zero_epsilon, 0.5, 1 - self.zero_epsilon]
        self.EXPLAIN_RADIUS_VALUE = [self.zero_epsilon, 0.5, 1 - self.zero_epsilon]
        self.EXPLAIN_GTCN_VALUE = [self.zero_epsilon, 0.5, 1 - self.zero_epsilon]
        self.EXPLAIN_GTR_VALUE = [self.zero_epsilon, 0.5, 1 - self.zero_epsilon]
        self.EXPLAIN_OFFSET_VALUE = [self.zero_epsilon, 0.5, 1 - self.zero_epsilon]
        self.EXPLAIN_BFAP_VALUE = [self.zero_epsilon, 0.5, 1 - self.zero_epsilon]
        self.EXPLAIN_ODDEVEN_VALUE = [self.zero_epsilon, 0.5, 1 - self.zero_epsilon]
        self.EXPLAIN_TEMP_VALUE = [self.zero_epsilon, 0.5, 1 - self.zero_epsilon]
        self.EXPLAIN_ALBEDO_VALUE = [self.zero_epsilon, 0.5, 1 - self.zero_epsilon]
        self.EXPLAIN_STARTEFF_VALUE = [self.zero_epsilon, 0.5, 1 - self.zero_epsilon]
        self.EXPLAIN_STARRAD_VALUE = [self.zero_epsilon, 0.5, 1 - self.zero_epsilon]
        self.kics_lcs_dir = lcs_dir + '/q1_q17/lcs/'
        self.ete6_lcs_dir = lcs_dir + '/ete6/lcs/'
        self.tess_lcs_dir = lcs_dir + '/tess/lcs/'
        self.batch_size = batch_size
        self.input_sizes = input_sizes
        self.random_number_generator = default_rng()
        self.measurements_per_point = measurements_per_point
        self.type_to_label = type_to_label
        self.plot_inputs = plot_inputs
        self.fixed_target_id = fixed_target_id
        self.store_arrays = store_arrays
        self.from_arrays = from_arrays
        self.validation_objects_df = validation_objects_df
        self.mask_previous_signals = mask_previous_signals
        self.offset_mode = offset_mode
        self.explain = explain
        if self.explain:
            final_df = pd.DataFrame(
                columns=['object_id', 'period', 'duration(h)', 'depth_primary', 'radius(earth)', 'type',
                         'EXPLAIN_PERIOD_VALUE', 'EXPLAIN_DURATION_VALUE', 'EXPLAIN_RADIUS_VALUE', 'EXPLAIN_GTCN_VALUE',
                         'EXPLAIN_GTR_VALUE', 'EXPLAIN_OFFSET_VALUE', 'EXPLAIN_BFAP_VALUE',
                         'EXPLAIN_ODDEVEN_VALUE', 'EXPLAIN_TEMP_VALUE', 'EXPLAIN_ALBEDO_VALUE',
                         'EXPLAIN_STARTEFF_VALUE', 'EXPLAIN_STARRAD_VALUE',
                         'EXPLAIN_GLOBAL_VIEW', 'EXPLAIN_MAIN_VIEW', 'EXPLAIN_SECONDARY_VIEW',
                         'EXPLAIN_ODD_VIEW', 'EXPLAIN_EVEN_VIEW', 'EXPLAIN_CENTROIDS_RA_VIEW',
                         'EXPLAIN_CENTROIDS_DEC_VIEW', 'EXPLAIN_OG_VIEW'])
            for index, row in self.injected_objects_df.iterrows():
                row_copy_df = row.copy().to_frame().T
                final_df = pd.concat([final_df, row_copy_df], ignore_index=True)
                row_copy_df = row.copy().to_frame().T
                row_copy_df['EXPLAIN_GLOBAL_VIEW'] = True
                row_copy_df['object_id'] = row_copy_df['object_id'] + '_global'
                final_df = pd.concat([final_df, row_copy_df], ignore_index=True)
                row_copy_df = row.copy().to_frame().T
                row_copy_df['EXPLAIN_MAIN_VIEW'] = True
                row_copy_df['object_id'] = row_copy_df['object_id'] + '_main'
                final_df = pd.concat([final_df, row_copy_df], ignore_index=True)
                row_copy_df = row.copy().to_frame().T
                row_copy_df['EXPLAIN_SECONDARY_VIEW'] = True
                row_copy_df['object_id'] = row_copy_df['object_id'] + '_secondary'
                final_df = pd.concat([final_df, row_copy_df], ignore_index=True)
                row_copy_df = row.copy().to_frame().T
                row_copy_df['EXPLAIN_ODD_VIEW'] = True
                row_copy_df['object_id'] = row_copy_df['object_id'] + '_odd'
                final_df = pd.concat([final_df, row_copy_df], ignore_index=True)
                row_copy_df = row.copy().to_frame().T
                row_copy_df['EXPLAIN_EVEN_VIEW'] = True
                row_copy_df['object_id'] = row_copy_df['object_id'] + '_even'
                final_df = pd.concat([final_df, row_copy_df], ignore_index=True)
                row_copy_df = row.copy().to_frame().T
                row_copy_df['EXPLAIN_CENTROIDS_RA_VIEW'] = True
                row_copy_df['object_id'] = row_copy_df['object_id'] + '_ra'
                final_df = pd.concat([final_df, row_copy_df], ignore_index=True)
                row_copy_df = row.copy().to_frame().T
                row_copy_df['EXPLAIN_CENTROIDS_DEC_VIEW'] = True
                row_copy_df['object_id'] = row_copy_df['object_id'] + '_dec'
                final_df = pd.concat([final_df, row_copy_df], ignore_index=True)
                row_copy_df = row.copy().to_frame().T
                row_copy_df['EXPLAIN_OG_VIEW'] = True
                row_copy_df['object_id'] = row_copy_df['object_id'] + '_og'
                final_df = pd.concat([final_df, row_copy_df], ignore_index=True)
                for value in self.EXPLAIN_PERIOD_VALUE:
                    row_copy_df = row.copy().to_frame().T
                    row_copy_df['EXPLAIN_PERIOD_VALUE'] = value
                    row_copy_df['object_id'] = row_copy_df['object_id'] + f'_period_{value}'
                    final_df = pd.concat([final_df, row_copy_df], ignore_index=True)
                for value in self.EXPLAIN_DURATION_VALUE:
                    row_copy_df = row.copy().to_frame().T
                    row_copy_df['EXPLAIN_DURATION_VALUE'] = value
                    row_copy_df['object_id'] = row_copy_df['object_id'] + f'_duration_{value}'
                    final_df = pd.concat([final_df, row_copy_df], ignore_index=True)
                for value in self.EXPLAIN_RADIUS_VALUE:
                    row_copy_df = row.copy().to_frame().T
                    row_copy_df['EXPLAIN_RADIUS_VALUE'] = value
                    row_copy_df['object_id'] = row_copy_df['object_id'] + f'_radius_{value}'
                    final_df = pd.concat([final_df, row_copy_df], ignore_index=True)
                for value in self.EXPLAIN_GTCN_VALUE:
                    row_copy_df = row.copy().to_frame().T
                    row_copy_df['EXPLAIN_GTCN_VALUE'] = value
                    row_copy_df['object_id'] = row_copy_df['object_id'] + f'_gtcn_{value}'
                    final_df = pd.concat([final_df, row_copy_df], ignore_index=True)
                for value in self.EXPLAIN_GTR_VALUE:
                    row_copy_df = row.copy().to_frame().T
                    row_copy_df['EXPLAIN_GTR_VALUE'] = value
                    row_copy_df['object_id'] = row_copy_df['object_id'] + f'_gtr_{value}'
                    final_df = pd.concat([final_df, row_copy_df], ignore_index=True)
                for value in self.EXPLAIN_OFFSET_VALUE:
                    row_copy_df = row.copy().to_frame().T
                    row_copy_df['EXPLAIN_OFFSET_VALUE'] = value
                    row_copy_df['object_id'] = row_copy_df['object_id'] + f'_offset_{value}'
                    final_df = pd.concat([final_df, row_copy_df], ignore_index=True)
                for value in self.EXPLAIN_BFAP_VALUE:
                    row_copy_df = row.copy().to_frame().T
                    row_copy_df['EXPLAIN_BFAP_VALUE'] = value
                    row_copy_df['object_id'] = row_copy_df['object_id'] + f'_bfap_{value}'
                    final_df = pd.concat([final_df, row_copy_df], ignore_index=True)
                for value in self.EXPLAIN_ODDEVEN_VALUE:
                    row_copy_df = row.copy().to_frame().T
                    row_copy_df['EXPLAIN_ODDEVEN_VALUE'] = value
                    row_copy_df['object_id'] = row_copy_df['object_id'] + f'_oddeven_{value}'
                    final_df = pd.concat([final_df, row_copy_df], ignore_index=True)
                for value in self.EXPLAIN_TEMP_VALUE:
                    row_copy_df = row.copy().to_frame().T
                    row_copy_df['EXPLAIN_TEMP_VALUE'] = value
                    row_copy_df['object_id'] = row_copy_df['object_id'] + f'_temp_{value}'
                    final_df = pd.concat([final_df, row_copy_df], ignore_index=True)
                for value in self.EXPLAIN_ALBEDO_VALUE:
                    row_copy_df = row.copy().to_frame().T
                    row_copy_df['EXPLAIN_ALBEDO_VALUE'] = value
                    row_copy_df['object_id'] = row_copy_df['object_id'] + f'_albedo_{value}'
                    final_df = pd.concat([final_df, row_copy_df], ignore_index=True)
                for value in self.EXPLAIN_STARTEFF_VALUE:
                    row_copy_df = row.copy().to_frame().T
                    row_copy_df['EXPLAIN_STARTEFF_VALUE'] = value
                    row_copy_df['object_id'] = row_copy_df['object_id'] + f'_starteff_{value}'
                    final_df = pd.concat([final_df, row_copy_df], ignore_index=True)
                for value in self.EXPLAIN_STARRAD_VALUE:
                    row_copy_df = row.copy().to_frame().T
                    row_copy_df['EXPLAIN_STARRAD_VALUE'] = value
                    row_copy_df['object_id'] = row_copy_df['object_id'] + f'_starrad_{value}'
                    final_df = pd.concat([final_df, row_copy_df], ignore_index=True)
            self.injected_objects_df = final_df

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

    def _plot_numeric_values(self, target_id, scalar_values, star_array):
        if self.plot_inputs:
            logging.info(
                f"{target_id} raw values: {scalar_values[0] * 1200} d, {scalar_values[1] * 15} d, {scalar_values[2] * 1000} ppt, {scalar_values[3] * 300} Re,"
                f" {scalar_values[4] * 20} gtcn, {scalar_values[5]} gtr, {scalar_values[6]} arcsec, {scalar_values[7]} arcsec_err, {scalar_values[8]} fap,"
                f" {scalar_values[9]} oef, {star_array[2] * 60000} K, {star_array[5] * 3} Rsun, {star_array[6] * 3} M_sun")
            logging.info(
                f"{target_id} normalized values: {scalar_values[0]} d, {scalar_values[1]} d, {scalar_values[2]} ppt, {scalar_values[3]} Re,"
                f" {scalar_values[4]} gtcn, {scalar_values[5]} gtr, {scalar_values[6]} arcsec, {scalar_values[7]} arcsec_err, {scalar_values[8]} fap,"
                f" {scalar_values[9]} oef, {star_array[2]} K, {star_array[5]} Rsun, {star_array[6]} M_sun")

    def _plot_input(self, input_array, type, scenario):
        if self.plot_inputs:
            fig, axs = plt.subplots(1, 1, figsize=(24, 12), constrained_layout=True)
            current_array_mask = np.argwhere((~np.isnan(input_array)) & (input_array > self.zero_epsilon)).flatten()
            current_array = input_array[current_array_mask]
            axs.scatter(np.arange(0, len(current_array)), current_array)
            axs.set_title(type + '_' + scenario)
            fig.suptitle(type + " " + scenario)
            plt.show()
            plt.clf()
            plt.close()

    def mask_other_signals(self, data_df, target_row, time_key):
        other_signals_df = self.injected_objects_df[(self.injected_objects_df['object_id'] == target_row['object_id']) &
                                                    (self.injected_objects_df['period'] != target_row['period'])]
        if self.validation_objects_df is not None:
            other_signals_val_df = self.validation_objects_df[
                (self.validation_objects_df['object_id'] == target_row['object_id']) &
                (self.validation_objects_df['period'] != target_row['period'])]
            other_signals_df = pd.concat([other_signals_df, other_signals_val_df])
        for index, other_signal_row in other_signals_df.iterrows():
            mask_signal = True
            if 'KIC' in target_row['object_id']:
                other_koi_tce_plnt_num = 999
                other_tce_plnt_num = 999
                target_koi_tce_plnt_num = 999
                target_tce_plnt_num = 999
                if 'koi_tce_plnt_num_y' in other_signal_row and not np.isnan(other_signal_row['koi_tce_plnt_num_y']):
                    other_koi_tce_plnt_num = other_signal_row['koi_tce_plnt_num_y']
                elif 'koi_tce_plnt_num_x' in other_signal_row and not np.isnan(other_signal_row['koi_tce_plnt_num_x']):
                    other_koi_tce_plnt_num = other_signal_row['koi_tce_plnt_num_x']
                elif 'koi_tce_plnt_num' in other_signal_row and not np.isnan(other_signal_row['koi_tce_plnt_num']):
                    other_koi_tce_plnt_num = other_signal_row['koi_tce_plnt_num']
                if 'koi_tce_plnt_num_y' in target_row and not np.isnan(target_row['koi_tce_plnt_num_y']):
                    target_koi_tce_plnt_num = target_row['koi_tce_plnt_num_y']
                elif 'koi_tce_plnt_num_x' in target_row and not np.isnan(target_row['koi_tce_plnt_num_x']):
                    target_koi_tce_plnt_num = target_row['koi_tce_plnt_num_x']
                elif 'koi_tce_plnt_num' in target_row and not np.isnan(target_row['koi_tce_plnt_num']):
                    target_koi_tce_plnt_num = target_row['koi_tce_plnt_num']
                if 'tce_plnt_num_y' in other_signal_row and not np.isnan(other_signal_row['tce_plnt_num_y']):
                    other_tce_plnt_num = other_signal_row['tce_plnt_num_y']
                elif 'tce_plnt_num_x' in other_signal_row and not np.isnan(other_signal_row['tce_plnt_num_x']):
                    other_tce_plnt_num = other_signal_row['tce_plnt_num_x']
                elif 'tce_plnt_num' in other_signal_row and not np.isnan(other_signal_row['tce_plnt_num']):
                    other_tce_plnt_num = other_signal_row['tce_plnt_num']
                if 'tce_plnt_num_y' in target_row and not np.isnan(target_row['tce_plnt_num_y']):
                    target_tce_plnt_num = target_row['tce_plnt_num_y']
                elif 'tce_plnt_num_x' in target_row and not np.isnan(target_row['tce_plnt_num_x']):
                    target_tce_plnt_num = target_row['tce_plnt_num_x']
                elif 'tce_plnt_num' in target_row and not np.isnan(target_row['tce_plnt_num']):
                    target_tce_plnt_num = target_row['tce_plnt_num']
                mask_signal = (not np.isnan(target_koi_tce_plnt_num) and not np.isnan(other_koi_tce_plnt_num) and \
                               target_koi_tce_plnt_num > other_koi_tce_plnt_num) or \
                              (not (np.isnan(target_tce_plnt_num) & np.isnan(other_tce_plnt_num)) and \
                               target_tce_plnt_num > other_tce_plnt_num)
            if mask_signal:
                mask = foldedleastsquares.transit_mask(data_df[time_key].to_numpy(), other_signal_row['period'],
                                                       2 * other_signal_row['duration(h)'] / 24,
                                                       other_signal_row['epoch'])
                data_df = data_df[~mask]
        return data_df

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
        star_array = np.empty((len(target_indexes), self.input_sizes[0], 1))
        # [period, planet radius, number of transits, ratio of good transits, transit depth, transit_offset_pos - transit_offset_err]
        scalar_values = np.empty((len(target_indexes), 12, 1))
        global_flux_array = np.empty((len(target_indexes), self.input_sizes[2], self.measurements_per_point))
        folded_flux_even_array = np.empty((len(target_indexes), self.input_sizes[3], self.measurements_per_point))
        folded_flux_odd_array = np.empty((len(target_indexes), self.input_sizes[3], self.measurements_per_point))
        folded_flux_even_subhar_array = np.empty(
            (len(target_indexes), self.input_sizes[3], self.measurements_per_point))
        folded_flux_odd_subhar_array = np.empty((len(target_indexes), self.input_sizes[3], self.measurements_per_point))
        folded_flux_even_har_array = np.empty((len(target_indexes), self.input_sizes[3], self.measurements_per_point))
        folded_flux_odd_har_array = np.empty((len(target_indexes), self.input_sizes[3], self.measurements_per_point))
        global_flux_array_err = np.empty((len(target_indexes), self.input_sizes[2], self.measurements_per_point))
        folded_flux_even_array_err = np.empty((len(target_indexes), self.input_sizes[3], self.measurements_per_point))
        folded_flux_odd_array_err = np.empty((len(target_indexes), self.input_sizes[3], self.measurements_per_point))
        folded_flux_even_subhar_array_err = np.empty(
            (len(target_indexes), self.input_sizes[3], self.measurements_per_point))
        folded_flux_odd_subhar_array_err = np.empty(
            (len(target_indexes), self.input_sizes[3], self.measurements_per_point))
        folded_flux_even_har_array_err = np.empty(
            (len(target_indexes), self.input_sizes[3], self.measurements_per_point))
        folded_flux_odd_har_array_err = np.empty(
            (len(target_indexes), self.input_sizes[3], self.measurements_per_point))
        folded_centroids_array = np.empty((len(target_indexes), self.input_sizes[3], 2))
        folded_centroids_array_err = np.empty((len(target_indexes), self.input_sizes[3], 2))
        folded_og_array = np.empty((len(target_indexes), self.input_sizes[3], 1))
        folded_og_array_err = np.empty((len(target_indexes), self.input_sizes[3], 1))
        batch_data_values = np.empty((len(target_indexes), 1))
        i = 0
        for df_index, target_row in injected_objects_df.iterrows():
            if self.fixed_target_id is not None:
                target_row = self.injected_objects_df[self.injected_objects_df['object_id'] == self.fixed_target_id[0]]
                target_row = target_row[target_row['period'] == self.fixed_target_id[1]]
            # TODO refactor to use mission for object_id
            object_id = target_row['object_id'].split(' ')
            mission_id = object_id[0]
            target_id = int(object_id[1].split('_')[0])
            period = target_row['period']
            lcs_dir = self.kics_lcs_dir if mission_id == 'KIC' else self.ete6_lcs_dir if 'OI' not in self.injected_objects_df else self.tess_lcs_dir
            if mission_id == 'KIC' or 'OI' in self.injected_objects_df:
                file_prefix = lcs_dir + '/' + mission_id + '_' + str(target_id) + '_' + str(round(period, 2))
            else:
                file_prefix = lcs_dir + '/' + mission_id + ' ' + str(target_id) + '_' + str(round(period, 2))
            if 'pl_orbper' in target_row and not np.isnan(target_row['pl_orbper']):
                period = target_row['pl_orbper']
            elif 'koi_period' in target_row and not np.isnan(target_row['koi_period']):
                period = target_row['koi_period']
            elif 'tce_period_x' in target_row and not np.isnan(target_row['tce_period_x']):
                period = target_row['tce_period_x']
            elif 'tce_period_y' in target_row and not np.isnan(target_row['tce_period_y']):
                period = target_row['tce_period_y']
            # period = target_row['koi_period']
            epoch = target_row['epoch']
            if 'pl_tranmid' in target_row and not np.isnan(target_row['pl_tranmid']):
                epoch = target_row['pl_tranmid'] - 2454833.0
            elif 'koi_time0bk' in target_row and not np.isnan(target_row['koi_time0bk']):
                epoch = target_row['koi_time0bk']
            elif 'tce_time0bk' in target_row and not np.isnan(target_row['tce_time0bk']):
                epoch = target_row['tce_time0bk']
            # epoch = target_row['koi_time0bk']
            duration = target_row['duration(h)'] / 24
            metrics_short_filename = file_prefix + '_metrics_short.csv'
            metrics_long_filename = file_prefix + '_metrics_long.csv'
            if 'tce_ptemp_stat' in target_row and not np.isnan(target_row['tce_ptemp_stat']):
                temperature_stat = target_row['tce_ptemp_stat']
            elif mission_id == 'TIC':
                temperature_stat = 0
                if os.path.exists(metrics_short_filename):
                    metrics_df = pd.read_csv(metrics_short_filename)
                    temperature_stat = metrics_df.loc[metrics_df['name'] == 'temp_stat'].iloc[0]['value']
                if os.path.exists(metrics_long_filename):
                    metrics_df = pd.read_csv(metrics_long_filename)
                    if temperature_stat is None:
                        temperature_stat = metrics_df.loc[metrics_df['name'] == 'temp_stat'].iloc[0]['value']
                    else:
                        temperature_stat = np.nanmean([temperature_stat,
                                                       metrics_df.loc[metrics_df['name'] == 'temp_stat'].iloc[0][
                                                           'value']])
            if 'tce_albedo_stat' in target_row and not np.isnan(target_row['tce_albedo']):
                albedo_stat = target_row['tce_albedo_stat']
            elif mission_id == 'TIC':
                albedo_stat = 0
                if os.path.exists(metrics_short_filename):
                    metrics_df = pd.read_csv(metrics_short_filename)
                    albedo_stat = metrics_df.loc[metrics_df['name'] == 'albedo_stat'].iloc[0]['value']
                if os.path.exists(metrics_long_filename):
                    metrics_df = pd.read_csv(metrics_long_filename)
                    if albedo_stat is None:
                        albedo_stat = metrics_df.loc[metrics_df['name'] == 'albedo_stat'].iloc[0]['value']
                    else:
                        albedo_stat = np.nanmean([albedo_stat,
                                                  metrics_df.loc[metrics_df['name'] == 'albedo_stat'].iloc[0][
                                                      'value']])
            if 'boot_fap' in target_row and not np.isnan(target_row['boot_fap']):
                bootstrap_fap = target_row['boot_fap']
                if np.isnan(bootstrap_fap) or bootstrap_fap <= 0:
                    bootstrap_fap = self.zero_epsilon
            elif mission_id == 'TIC':
                bootstrap_fap = 1 - self.zero_epsilon
                if os.path.exists(metrics_short_filename):
                    metrics_df = pd.read_csv(metrics_short_filename)
                    bootstrap_fap = metrics_df.loc[metrics_df['name'] == 'bootstrap_fap'].iloc[0]['value']
                if os.path.exists(metrics_long_filename):
                    metrics_df = pd.read_csv(metrics_long_filename)
                    if bootstrap_fap is None:
                        bootstrap_fap = metrics_df.loc[metrics_df['name'] == 'bootstrap_fap'].iloc[0]['value']
                    else:
                        bootstrap_fap = np.nanmean([bootstrap_fap,
                                                    metrics_df.loc[metrics_df['name'] == 'bootstrap_fap'].iloc[0][
                                                        'value']])
            duration_to_period = duration / period
            type = target_row['type']
            batch_data_values[i] = [float(x) for x in self.type_to_label[type]]
            if self.from_arrays:
                try:
                    scalar_values[i] = [[e] for e in
                                        np.loadtxt(file_prefix + '_input_scalar_values.csv', delimiter=',')]
                except Exception as e:
                    logging.info("FAILED FILE PREFIX: %s", file_prefix)
                    raise e
                star_array[i] = [[e] for e in np.loadtxt(file_prefix + '_input_star.csv', delimiter=',')]
                global_flux_array[i] = np.loadtxt(file_prefix + '_input_global.csv', delimiter=',').reshape(-1, 1)
                global_flux_array_err[i] = np.loadtxt(file_prefix + '_input_global_err.csv', delimiter=',').reshape(-1,
                                                                                                                    1)
                folded_flux_even_array[i] = np.loadtxt(file_prefix + '_input_even.csv', delimiter=',').reshape(-1, 1)
                folded_flux_even_array_err[i] = np.loadtxt(file_prefix + '_input_even_err.csv', delimiter=',').reshape(
                    -1, 1)
                folded_flux_odd_array[i] = np.loadtxt(file_prefix + '_input_odd.csv', delimiter=',').reshape(-1, 1)
                folded_flux_odd_array_err[i] = np.loadtxt(file_prefix + '_input_odd_err.csv', delimiter=',').reshape(-1,
                                                                                                                     1)
                folded_flux_even_subhar_array[i] = np.loadtxt(file_prefix + '_input_even_sh.csv',
                                                              delimiter=',').reshape(-1, 1)
                folded_flux_even_subhar_array_err[i] = np.loadtxt(file_prefix + '_input_even_sh_err.csv',
                                                                  delimiter=',').reshape(-1, 1)
                folded_flux_odd_subhar_array[i] = np.loadtxt(file_prefix + '_input_odd_sh.csv', delimiter=',').reshape(
                    -1, 1)
                folded_flux_odd_subhar_array_err[i] = np.loadtxt(file_prefix + '_input_odd_sh_err.csv',
                                                                 delimiter=',').reshape(-1, 1)
                folded_flux_even_har_array[i] = np.loadtxt(file_prefix + '_input_even_h.csv', delimiter=',').reshape(-1,
                                                                                                                     1)
                folded_flux_even_har_array_err[i] = np.loadtxt(file_prefix + '_input_even_h_err.csv',
                                                               delimiter=',').reshape(-1, 1)
                folded_flux_odd_har_array[i] = np.loadtxt(file_prefix + '_input_odd_h.csv', delimiter=',').reshape(-1,
                                                                                                                   1)
                folded_flux_odd_har_array_err[i] = np.loadtxt(file_prefix + '_input_odd_h_err.csv',
                                                              delimiter=',').reshape(-1, 1)
                folded_centroids_array[i] = np.loadtxt(file_prefix + '_input_centroids.csv', delimiter=',')
                folded_centroids_array_err[i] = np.loadtxt(file_prefix + '_input_centroids_err.csv', delimiter=',')
                folded_og_array[i] = np.loadtxt(file_prefix + '_input_og.csv', delimiter=',').reshape(-1, 1)
                folded_og_array_err[i] = np.loadtxt(file_prefix + '_input_og_err.csv', delimiter=',').reshape(-1, 1)
            else:
                # TODO refactor to use mission for _lc files
                lc_filename = file_prefix + '_lc.csv'
                centroids_filename = file_prefix + '_cent.csv'
                og_filename = file_prefix + '_og.csv'
                lc_short_filename = file_prefix + '_lc_short.csv'
                centroids_short_filename = file_prefix + '_cent_short.csv'
                og_short_filename = file_prefix + '_og_short.csv'
                lc_long_filename = file_prefix + '_lc_long.csv'
                centroids_long_filename = file_prefix + '_cent_long.csv'
                og_long_filename = file_prefix + '_og_long.csv'
                lc_df = None
                centroids_df = None
                og_df = None
                if os.path.exists(lc_long_filename):
                    read_df = pd.read_csv(lc_long_filename, usecols=['#time', 'flux_0'], low_memory=True)
                    lc_df = read_df if lc_df is None else lc_df.append(read_df, ignore_index=True)
                if os.path.exists(lc_short_filename):
                    read_df = pd.read_csv(lc_short_filename, usecols=['#time', 'flux_0'], low_memory=True)
                    lc_df = read_df if lc_df is None else lc_df.append(read_df, ignore_index=True)
                if lc_df is None:
                    logging.warning("No curve for target " + file_prefix)
                    raise ValueError("No curve for target " + file_prefix)
                if os.path.exists(centroids_long_filename):
                    read_centroids_df = pd.read_csv(centroids_long_filename,
                                                    usecols=['time', 'centroids_ra', 'centroids_dec'],
                                                    low_memory=True)
                    read_centroids_df = read_centroids_df.sort_values(by=['time'])
                    if len(read_centroids_df) > 0:
                        read_centroids_df['centroids_ra'], _ = LcbuilderHelper.detrend(
                            read_centroids_df['time'].to_numpy(),
                            read_centroids_df['centroids_ra'].to_numpy(), duration * 4,
                            check_cadence=True)
                        read_centroids_df['centroids_dec'], _ = LcbuilderHelper.detrend(
                            read_centroids_df['time'].to_numpy(),
                            read_centroids_df['centroids_dec'].to_numpy(), duration * 4,
                            check_cadence=True)
                        centroids_df = read_centroids_df if centroids_df is None \
                            else centroids_df.append(read_centroids_df, ignore_index=True)
                if os.path.exists(og_long_filename):
                    read_og_df = pd.read_csv(og_long_filename, usecols=['time', 'og_flux', 'halo_flux', 'core_flux'],
                                             low_memory=True)
                    read_og_df = self.compute_og_df(read_og_df, object_id, duration)
                    og_df = read_og_df if og_df is None else og_df.append(read_og_df, ignore_index=True)
                if os.path.exists(centroids_short_filename):
                    read_centroids_df = pd.read_csv(centroids_short_filename,
                                                    usecols=['time', 'centroids_ra', 'centroids_dec'],
                                                    low_memory=True)
                    if len(read_centroids_df) > 0:
                        read_centroids_df = read_centroids_df.sort_values(by=['time'])
                        read_centroids_df['centroids_ra'], _ = LcbuilderHelper.detrend(
                            read_centroids_df['time'].to_numpy(),
                            read_centroids_df['centroids_ra'].to_numpy(), duration * 4,
                            check_cadence=True)
                        read_centroids_df['centroids_dec'], _ = LcbuilderHelper.detrend(
                            read_centroids_df['time'].to_numpy(),
                            read_centroids_df['centroids_dec'].to_numpy(), duration * 4,
                            check_cadence=True)
                    centroids_df = read_centroids_df if centroids_df is None \
                        else centroids_df.append(read_centroids_df, ignore_index=True)
                if os.path.exists(og_short_filename):
                    read_og_df = pd.read_csv(og_short_filename, usecols=['time', 'og_flux', 'halo_flux', 'core_flux'],
                                             low_memory=True)
                    read_og_df = self.compute_og_df(read_og_df, object_id, duration)
                    og_df = read_og_df if og_df is None else og_df.append(read_og_df, ignore_index=True)
                lc_df = lc_df.sort_values(by=['#time'])
                if self.mask_previous_signals:
                    lc_df = self.mask_other_signals(lc_df, target_row, '#time')
                    centroids_df = self.mask_other_signals(centroids_df, target_row, 'time')
                    og_df = self.mask_other_signals(og_df, target_row, 'time')
                centroids_df['time'] = self.fold(centroids_df['time'].to_numpy(), period, epoch + period / 2)
                og_df['time'] = self.fold(og_df['time'].to_numpy(), period, epoch + period / 2)
                centroids_df = centroids_df.sort_values(by=['time'])
                og_df = og_df.sort_values(by=['time'])
                centroids_df = self._prepare_input_centroids(centroids_df)
                og_df = self._prepare_input_og(og_df)
                og_df = og_df[(og_df['time'] > 0.5 - duration_to_period * 3) & (
                        og_df['time'] < 0.5 + duration_to_period * 3)]
                centroids_df = centroids_df[(centroids_df['time'] > 0.5 - duration_to_period * 3) & (
                        centroids_df['time'] < 0.5 + duration_to_period * 3)]
                folded_centroids_array[i], folded_centroids_array_err[i] = self.bin_by_time(centroids_df.to_numpy(),
                                                                                            self.input_sizes[3],
                                                                                            target_row['object_id'])
                folded_og_array[i], folded_og_array_err[i] = self.bin_by_time(og_df.to_numpy(), self.input_sizes[3],
                                                                              target_row['object_id'])
                # TODO refactor to use mission for star files
                star_filename = lcs_dir + '/' + mission_id + ' ' + str(target_id) + '_star.csv'
                star_df = pd.read_csv(star_filename, index_col=False)
                star_neighbours_df = pd.read_csv(star_filename,
                                                 usecols=['Teff', 'lum', 'v', 'j', 'k', 'h', 'radius', 'mass',
                                                          'dist_arcsec'], index_col=False)
                star_neighbours_df = self._prepare_input_neighbour_stars(star_neighbours_df)
                star_df, ra, dec = self._prepare_input_star(target_row, star_df)
                lc_df, good_transits_count, transits_count = self._prepare_input_lc(lc_df, period, epoch, duration)
                not_null_times_args = np.argwhere(lc_df['#time'].to_numpy() > 0).flatten()
                lc_df = lc_df.iloc[not_null_times_args]
                offset_long_filename = file_prefix + '_offset_long.csv'
                offset_short_filename = file_prefix + '_offset_short.csv'
                offset_short_df = None
                offset_long_df = None
                offset_ra = None
                offset_dec = None
                offset_ra_err = None
                offset_dec_err = None
                if os.path.exists(offset_long_filename):
                    offset_long_df = pd.read_csv(offset_long_filename, low_memory=True)
                    row = offset_long_df[offset_long_df['name'] == self.offset_mode].iloc[0]
                    offset_ra = row['ra']
                    offset_dec = row['dec']
                    offset_ra_err = row['ra_err']
                    offset_dec_err = row['dec_err']
                if os.path.exists(offset_short_filename):
                    offset_short_df = pd.read_csv(offset_short_filename, low_memory=True)
                    row = offset_short_df[offset_short_df['name'] == self.offset_mode].iloc[0]
                    row_mean = offset_short_df[offset_short_df['name'] == 'mean'].iloc[0]
                    offset_ra = row['ra'] if offset_long_df is None or np.isnan(offset_ra) else np.mean(
                        [row['ra'], offset_ra])
                    offset_dec = row['dec'] if offset_long_df is None or np.isnan(offset_dec) else np.mean(
                        [row['dec'], offset_dec])
                    offset_ra_err = self.zero_epsilon if np.isnan(offset_ra) else offset_ra_err
                    offset_dec_err = self.zero_epsilon if np.isnan(offset_dec) else offset_dec_err
                    row_ra_err = row['ra_err'] if not np.isnan(row['ra_err']) and row['ra_err'] > 0 else row_mean[
                        'ra_err']
                    row_dec_err = row['dec_err'] if not np.isnan(row['dec_err']) and row['dec_err'] > 0 else row_mean[
                        'dec_err']
                    offset_ra_err = row_ra_err if offset_long_df is None or np.isnan(offset_ra_err) else np.sqrt(
                        offset_ra_err ** 2 + row_ra_err ** 2)
                    offset_dec_err = row_dec_err if offset_long_df is None or np.isnan(offset_dec_err) else np.sqrt(
                        offset_dec_err ** 2 + row_dec_err ** 2)
                target_dist = np.sqrt((offset_ra - ra) ** 2 + (offset_dec - dec) ** 2)
                if target_dist < self.zero_epsilon:
                    logging.info(f"target_dist was zero for {file_prefix}")
                    target_dist = random.uniform(self.zero_epsilon, 1 / 3600 * LcbuilderHelper.mission_pixel_size(
                        MISSION_TESS if mission_id == MISSION_ID_TESS else MISSION_KEPLER))
                target_dist = target_dist if target_dist > 0 else self.zero_epsilon
                offset_err = offset_ra_err if offset_ra_err > offset_dec_err else offset_dec_err
                offset_err = offset_err if offset_err > 0 else target_dist * 2
                offset_err = offset_err / (target_dist * 2)
                offset_err = 1 - self.zero_epsilon if offset_err >= 1 else offset_err
                offset_err = offset_err if offset_err > 0 else self.zero_epsilon
                good_transits_count_norm = good_transits_count / 20
                good_transits_count_norm = good_transits_count_norm if good_transits_count_norm < 1 else 1 - self.zero_epsilon
                good_transits_ratio = good_transits_count / transits_count if transits_count > 0 else self.zero_epsilon
                good_transits_ratio = good_transits_ratio if good_transits_ratio < 1 else 1 - self.zero_epsilon
                depth = target_row['depth_primary'] / 1e6
                planet_radius = target_row['radius(earth)']
                # if not np.isnan(star_df['radius']) and not np.isnan(target_row['depth_primary']):
                #     planet_radius = np.sqrt(depth * LcbuilderHelper.convert_from_to(star_df['radius'], u.R_sun, u.R_earth) ** 2)
                planet_radius = planet_radius / 300
                depth = depth if depth < 1 else 1 - self.zero_epsilon
                planet_radius = planet_radius if planet_radius < 1 else 1 - self.zero_epsilon
                # ['ld_a', 'ld_b', 'Teff', 'lum', 'logg', 'radius', 'mass', 'v', 'j', 'h', 'k'])
                neighbours_array = star_neighbours_df.to_numpy().flatten()
                star_array[i] = np.transpose([star_df.to_numpy()])
                time = lc_df['#time'].to_numpy()
                # Global flux
                # Shifting data 1/4 so that main transit and possible occultation don't get cut by the borders
                lc_df_sorted_fold = lc_df.copy()
                lc_df_sorted_fold['#time'] = self.fold(time, period, epoch + period / 4)
                lc_df_sorted_fold = lc_df_sorted_fold.sort_values(by=['#time'])
                global_flux_array[i], global_flux_array_err[i] = \
                    self.bin_by_time(lc_df_sorted_fold.to_numpy(), self.input_sizes[2], target_row['object_id'])
                # Focus flux even (secondary event)
                lc_df_focus = lc_df.copy()
                lc_df_focus['#time'] = self.fold(time, period, epoch)
                lc_df_focus = lc_df_focus.sort_values(by=['#time'])
                lc_df_focus = lc_df_focus[(lc_df_focus['#time'] > 0.5 - duration_to_period * 3) &
                                          (lc_df_focus['#time'] < 0.5 + duration_to_period * 3)]
                folded_flux_even_array[i], folded_flux_even_array_err[i] = \
                    self.bin_by_time(lc_df_focus.to_numpy(), self.input_sizes[3], target_row['object_id'])
                # Focus flux odd
                lc_df_focus = lc_df.copy()
                lc_df_focus['#time'] = self.fold(time, period, epoch + period / 2)
                lc_df_focus = lc_df_focus.sort_values(by=['#time'])
                lc_df_focus = lc_df_focus[(lc_df_focus['#time'] > 0.5 - duration_to_period * 3) &
                                          (lc_df_focus['#time'] < 0.5 + duration_to_period * 3)]
                folded_flux_odd_array[i], folded_flux_odd_array_err[i] = \
                    self.bin_by_time(lc_df_focus.to_numpy(), self.input_sizes[4], target_row['object_id'])
                # Focus flux harmonic even
                lc_df_focus = lc_df.copy()
                lc_df_focus['#time'] = self.fold(time, period * 2, epoch)
                lc_df_focus = lc_df_focus.sort_values(by=['#time'])
                lc_df_focus = lc_df_focus[(lc_df_focus['#time'] > 0.5 - duration_to_period * 1.5) &
                                          (lc_df_focus['#time'] < 0.5 + duration_to_period * 1.5)]
                oot_lc_df_focus = lc_df_focus[((lc_df_focus['#time'] <= 0.5 - duration_to_period / 4) |
                                               (lc_df_focus['#time'] >= 0.5 + duration_to_period / 4))]
                it_lc_df_focus = lc_df_focus[((lc_df_focus['#time'] > 0.5 - duration_to_period / 4) &
                                              (lc_df_focus['#time'] < 0.5 + duration_to_period / 4))]
                depth_even = (oot_lc_df_focus['flux_0'].mean() - it_lc_df_focus['flux_0'].mean()) * np.sqrt(
                    len(it_lc_df_focus)) / oot_lc_df_focus['flux_0'].std()
                folded_flux_even_har_array[i], folded_flux_even_har_array_err[i] = \
                    self.bin_by_time(lc_df_focus.to_numpy(), self.input_sizes[7], target_row['object_id'])
                # Focus flux harmonic odd
                lc_df_focus = lc_df.copy()
                lc_df_focus['#time'] = self.fold(time, period * 2, epoch + period)
                lc_df_focus = lc_df_focus.sort_values(by=['#time'])
                lc_df_focus = lc_df_focus[(lc_df_focus['#time'] > 0.5 - duration_to_period * 1.5) &
                                          (lc_df_focus['#time'] < 0.5 + duration_to_period * 1.5)]
                oot_lc_df_focus = lc_df_focus[((lc_df_focus['#time'] <= 0.5 - duration_to_period / 4) |
                                               (lc_df_focus['#time'] >= 0.5 + duration_to_period / 4))]
                it_lc_df_focus = lc_df_focus[((lc_df_focus['#time'] > 0.5 - duration_to_period / 4) &
                                              (lc_df_focus['#time'] < 0.5 + duration_to_period / 4))]
                depth_odd = (oot_lc_df_focus['flux_0'].mean() - it_lc_df_focus['flux_0'].mean()) * np.sqrt(
                    len(it_lc_df_focus)) / oot_lc_df_focus['flux_0'].std()
                folded_flux_odd_har_array[i], folded_flux_odd_har_array_err[i] = \
                    self.bin_by_time(lc_df_focus.to_numpy(), self.input_sizes[8], target_row['object_id'])
                # Focus flux sub-harmonic even
                lc_df_focus = pd.DataFrame(columns=['#time', 'flux_0'])
                time, flux0, _ = LcbuilderHelper.mask_transits(time,
                                                               lc_df.copy()['flux_0'].to_numpy(), period, duration * 6,
                                                               epoch)
                lc_df_focus['#time'] = time
                lc_df_focus['flux_0'] = flux0
                lc_df_focus['#time'] = self.fold(time, period / 2, epoch)
                lc_df_focus = lc_df_focus.sort_values(by=['#time'])
                lc_df_focus = lc_df_focus[(lc_df_focus['#time'] > 0.5 - duration_to_period * 3) &
                                          (lc_df_focus['#time'] < 0.5 + duration_to_period * 3)]
                folded_flux_even_subhar_array[i], folded_flux_even_subhar_array_err[i] = \
                    self.bin_by_time(lc_df_focus.to_numpy(), self.input_sizes[5], target_row['object_id'])
                # Focus flux sub-harmonic odd
                lc_df_focus = pd.DataFrame(columns=['#time', 'flux_0'])
                lc_df_focus['#time'] = time
                lc_df_focus['flux_0'] = flux0
                lc_df_focus['#time'] = self.fold(time, period / 2, epoch + period / 4)
                lc_df_focus = lc_df_focus.sort_values(by=['#time'])
                lc_df_focus = lc_df_focus[(lc_df_focus['#time'] > 0.5 - duration_to_period * 3) &
                                          (lc_df_focus['#time'] < 0.5 + duration_to_period * 3)]
                folded_flux_odd_subhar_array[i], folded_flux_odd_subhar_array_err[i] = \
                    self.bin_by_time(lc_df_focus.to_numpy(), self.input_sizes[6], target_row['object_id'])
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
                scalar_values[i] = np.transpose([[period / 1200 if period < 1200 else 1,
                                                  duration / 15,
                                                  depth,
                                                  planet_radius,
                                                  good_transits_count_norm,
                                                  good_transits_ratio,
                                                  target_dist if not np.isnan(target_dist) else self.zero_epsilon,
                                                  offset_err,
                                                  bootstrap_fap,
                                                  oe_factor,
                                                  temperature_stat,
                                                  albedo_stat]])
            self.assert_in_range(object_id, scalar_values[i], None)
            self.assert_in_range(object_id, global_flux_array[i], global_flux_array_err[i])
            self.assert_in_range(object_id, star_array[i], None)
            self.assert_in_range(object_id, folded_flux_even_array[i], folded_flux_even_array_err[i])
            self.assert_in_range(object_id, folded_flux_odd_array[i], folded_flux_odd_array_err[i])
            self.assert_in_range(object_id, folded_flux_even_subhar_array[i], folded_flux_even_subhar_array_err[i])
            self.assert_in_range(object_id, folded_flux_odd_subhar_array[i], folded_flux_odd_subhar_array_err[i])
            self.assert_in_range(object_id, folded_flux_even_har_array[i], folded_flux_even_har_array_err[i])
            self.assert_in_range(object_id, folded_flux_odd_har_array[i], folded_flux_odd_har_array_err[i])
            self.assert_in_range(object_id, folded_centroids_array[i], folded_centroids_array_err[i])
            self.assert_in_range(object_id, folded_og_array[i], folded_og_array_err[i])
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
            self._plot_input(np.transpose(global_flux_array[i])[0], target_row['object_id'] + "_" + type, "global")
            self._plot_input(np.transpose(folded_flux_even_array[i])[0], target_row['object_id'] + "_" + type, "even")
            self._plot_input(np.transpose(folded_flux_odd_array[i])[0], target_row['object_id'] + "_" + type, "odd")
            self._plot_input(np.transpose(folded_flux_even_har_array[i])[0], target_row['object_id'] + "_" + type,
                             "even_har")
            self._plot_input(np.transpose(folded_flux_odd_har_array[i])[0], target_row['object_id'] + "_" + type,
                             "odd_har")
            self._plot_input(np.transpose(folded_og_array[i])[0], target_row['object_id'] + "_" + type, "OG")
            self._plot_input(np.transpose(folded_centroids_array[i])[0], target_row['object_id'] + "_" + type,
                             "CENTROIDS RA")
            self._plot_input(np.transpose(folded_centroids_array[i])[1], target_row['object_id'] + "_" + type,
                             "CENTROIDS DEC")
            self._plot_numeric_values(object_id, scalar_values[i], star_array[i])
            if self.store_arrays:
                logging.info("Storing arrays into prefix " + file_prefix)
                np.savetxt(file_prefix + '_input_scalar_values.csv', scalar_values[i], delimiter=',')
                np.savetxt(file_prefix + '_input_star.csv', star_array[i], delimiter=',')
                np.savetxt(file_prefix + '_input_global.csv', global_flux_array[i], delimiter=',')
                np.savetxt(file_prefix + '_input_global_err.csv', global_flux_array_err[i], delimiter=',')
                np.savetxt(file_prefix + '_input_even.csv', folded_flux_even_array[i], delimiter=',')
                np.savetxt(file_prefix + '_input_even_err.csv', folded_flux_even_array_err[i], delimiter=',')
                np.savetxt(file_prefix + '_input_odd.csv', folded_flux_odd_array[i], delimiter=',')
                np.savetxt(file_prefix + '_input_odd_err.csv', folded_flux_odd_array_err[i], delimiter=',')
                np.savetxt(file_prefix + '_input_even_sh.csv', folded_flux_even_subhar_array[i], delimiter=',')
                np.savetxt(file_prefix + '_input_even_sh_err.csv', folded_flux_even_subhar_array_err[i], delimiter=',')
                np.savetxt(file_prefix + '_input_odd_sh.csv', folded_flux_odd_subhar_array[i], delimiter=',')
                np.savetxt(file_prefix + '_input_odd_sh_err.csv', folded_flux_odd_subhar_array_err[i], delimiter=',')
                np.savetxt(file_prefix + '_input_even_h.csv', folded_flux_even_har_array[i], delimiter=',')
                np.savetxt(file_prefix + '_input_even_h_err.csv', folded_flux_even_har_array_err[i], delimiter=',')
                np.savetxt(file_prefix + '_input_odd_h.csv', folded_flux_odd_har_array[i], delimiter=',')
                np.savetxt(file_prefix + '_input_odd_h_err.csv', folded_flux_odd_har_array_err[i], delimiter=',')
                np.savetxt(file_prefix + '_input_centroids.csv', folded_centroids_array[i], delimiter=',')
                np.savetxt(file_prefix + '_input_centroids_err.csv', folded_centroids_array_err[i], delimiter=',')
                np.savetxt(file_prefix + '_input_og.csv', folded_og_array[i], delimiter=',')
                np.savetxt(file_prefix + '_input_og_err.csv', folded_og_array_err[i], delimiter=',')
            if self.explain:
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
                if 'EXPLAIN_TEMP_VALUE' in target_row and not np.isnan(target_row['EXPLAIN_TEMP_VALUE']):
                    scalar_values[i, 10] = target_row['EXPLAIN_TEMP_VALUE']
                if 'EXPLAIN_ALBEDO_VALUE' in target_row and not np.isnan(target_row['EXPLAIN_ALBEDO_VALUE']):
                    scalar_values[i, 11] = target_row['EXPLAIN_ALBEDO_VALUE']
                if 'EXPLAIN_STARTEFF_VALUE' in target_row and not np.isnan(target_row['EXPLAIN_STARTEFF_VALUE']):
                    star_array[i, 2] = target_row['EXPLAIN_STARTEFF_VALUE']
                if 'EXPLAIN_STARRAD_VALUE' in target_row and not np.isnan(target_row['EXPLAIN_STARRAD_VALUE']):
                    star_array[i, 6] = target_row['EXPLAIN_STARRAD_VALUE']
                if 'EXPLAIN_GLOBAL_VIEW' in target_row and not np.isnan(target_row['EXPLAIN_GLOBAL_VIEW']):
                    global_flux_array[i] = np.zeros(global_flux_array[i].shape)
                if 'EXPLAIN_MAIN_VIEW' in target_row and not np.isnan(target_row['EXPLAIN_MAIN_VIEW']):
                    folded_flux_odd_array[i] = np.zeros(folded_flux_odd_array[i].shape)
                if 'EXPLAIN_SECONDARY_VIEW' in target_row and not np.isnan(target_row['EXPLAIN_SECONDARY_VIEW']):
                    folded_flux_even_array[i] = np.zeros(folded_flux_even_array[i].shape)
                if 'EXPLAIN_ODD_VIEW' in target_row and not np.isnan(target_row['EXPLAIN_ODD_VIEW']):
                    folded_flux_odd_har_array[i] = np.zeros(folded_flux_odd_har_array[i].shape)
                if 'EXPLAIN_EVEN_VIEW' in target_row and not np.isnan(target_row['EXPLAIN_EVEN_VIEW']):
                    folded_flux_even_har_array[i] = np.zeros(folded_flux_even_har_array[i].shape)
                if 'EXPLAIN_CENTROIDS_RA_VIEW' in target_row and not np.isnan(target_row['EXPLAIN_CENTROIDS_RA_VIEW']):
                    folded_centroids_array[i, :, 0] = np.zeros(folded_centroids_array[i].shape[0])
                if 'EXPLAIN_CENTROIDS_DEC_VIEW' in target_row and not np.isnan(
                        target_row['EXPLAIN_CENTROIDS_DEC_VIEW']):
                    folded_centroids_array[i, :, 1] = np.zeros(folded_centroids_array[i].shape[0])
                if 'EXPLAIN_OG_VIEW' in target_row and not np.isnan(target_row['EXPLAIN_OG_VIEW']):
                    folded_og_array[i] = np.zeros(folded_og_array[i].shape)
            i = i + 1
        return (scalar_values[:, [0, 1, 3, 4, 5, 8, 9, 10, 11]], scalar_values[:, [7]],
                star_array[:, [2, 6]],  # Only Teff, Rad
                global_flux_array,
                folded_flux_even_array,
                folded_flux_odd_array,
                folded_flux_even_har_array,
                folded_flux_odd_har_array,
                folded_centroids_array,
                folded_og_array), \
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
