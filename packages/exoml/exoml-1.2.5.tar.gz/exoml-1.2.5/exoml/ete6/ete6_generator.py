import logging
from abc import abstractmethod

import foldedleastsquares
import scipy
#import timesynth
from lcbuilder.helper import LcbuilderHelper
from numpy.random import default_rng
from scipy import stats
from sklearn.preprocessing import StandardScaler, MinMaxScaler

from exoml.ete6.NanException import NanException
from sklearn.utils import shuffle
import tensorflow as tf
import numpy as np
import pandas as pd

from exoml.ml.functions.functions import sigmoid


class Ete6ModelGenerator(tf.keras.utils.Sequence):
    random_number_generator = default_rng()
    standard_scaler = StandardScaler()

    def __init__(self, zero_epsilon=1e-6, shuffle_batch=True, flag_incomplete=False, throw_nan_exception=False):
        self.zero_epsilon = zero_epsilon
        self.minmax_scaler = MinMaxScaler(feature_range=(self.zero_epsilon, 1 - self.zero_epsilon))
        self.shuffle_batch = shuffle_batch
        self.flag_incomplete = flag_incomplete
        self.throw_nan_exception = throw_nan_exception

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


    def fold(self, time, period, epoch):
        return foldedleastsquares.fold(time, period, epoch) if len(time) > 0 else time

    def bin_interp(self, array, new_size):
        result = np.zeros((array.shape[1], new_size))
        for index, nested_array in enumerate(np.transpose(array)):
            try:
                nested_array = nested_array[nested_array > self.zero_epsilon]
                arr_interp = scipy.interpolate.interp1d(np.arange(nested_array.size), nested_array)
                result[index] = arr_interp(np.linspace(0, nested_array.size - 1, new_size))
            except Exception as e:
                a = 1
                # logging.exception("Error when interpolating, will create empty input array")
        return np.transpose(result)

    def bin_by_time(self, array, new_size, target, min_points=50):
        result = np.full((array.shape[1], new_size), self.zero_epsilon)
        result_err = np.full((array.shape[1], new_size), self.zero_epsilon)
        transposed_array = np.transpose(array)
        time_array = transposed_array[0]
        any_nan = False
        for index, nested_array in enumerate(transposed_array):
            if index > 0:
                mask = nested_array > self.zero_epsilon
                nested_array = nested_array[mask]
                masked_time_array = time_array[mask]
                if len(masked_time_array) < min_points:
                    continue
                try:
                    bin_means, bin_edges, binnumber = stats.binned_statistic(masked_time_array, nested_array,
                                                                             statistic='mean', bins=new_size)
                    bin_stds, _, _ = stats.binned_statistic(masked_time_array, nested_array, statistic='std',
                                                            bins=new_size)
                    nans, x = self.nan_helper(bin_means)
                    any_nan = any_nan or np.any(nans)
                    bin_means[nans] = np.interp(x(nans), x(~nans), bin_means[~nans])
                    nans, x = self.nan_helper(bin_stds)
                    any_nan = any_nan or np.any(nans)
                    bin_stds[nans] = np.interp(x(nans), x(~nans), bin_stds[~nans])
                    bin_width = (bin_edges[1] - bin_edges[0])
                    bin_centers = bin_edges[1:] - bin_width / 2
                    if np.max(result[0]) == self.zero_epsilon:
                        result[0] = bin_centers
                        result_err[0] = np.full((new_size), 0.5)
                    # Store binning values for flux
                    result[index] = self.minmax_scaler.fit_transform(bin_means.reshape(-1, 1)).flatten()
                    result_err[index] = bin_stds if len(np.isnan(bin_stds)) == 0 else np.full((new_size), np.nanstd(bin_means))
                except Exception as e:
                    logging.exception("Error when interpolating for target " + str(target) + ", will create empty input array")
        if self.throw_nan_exception and any_nan:
            raise NanException(f"Nan values in array for target {target}")
        return np.transpose(np.nan_to_num(result[1:])), np.transpose(np.nan_to_num(result_err[1:]))

    @staticmethod
    def nan_helper(y):
        """Helper to handle indices and logical indices of NaNs.

        Input:
            - y, 1d numpy array with possible NaNs
        Output:
            - nans, logical indices of NaNs
            - index, a function, with signature indices= index(logical_indices),
              to convert logical indices of NaNs to 'equivalent' indices
        Example:
            >>> # linear interpolation of NaNs
            >>> nans, x= nan_helper(y)
            >>> y[nans]= np.interp(x(nans), x(~nans), y[~nans])
        """
        return np.isnan(y), lambda z: z.nonzero()[0]

    def _prepare_input_centroids(self, input_df):
        input_df_clipped = input_df
        if len(input_df) > 0:
            _, ra_outliers_mask = LcbuilderHelper.clip_outliers(input_df['centroids_ra'].to_numpy(), 3)
            _, dec_outliers_mask = LcbuilderHelper.clip_outliers(input_df['centroids_dec'].to_numpy(), 3)
            outliers_mask = np.logical_or(ra_outliers_mask, dec_outliers_mask)
            input_df_clipped = input_df.loc[~outliers_mask].copy()
            if len(input_df_clipped) > 0:
                # transform data
                input_df_clipped['centroids_ra'] = self.minmax_scaler.fit_transform(input_df_clipped['centroids_ra'].values.reshape(-1, 1)).flatten()
                input_df_clipped['centroids_dec'] = self.minmax_scaler.fit_transform(input_df_clipped['centroids_dec'].values.reshape(-1, 1)).flatten()
                input_df_clipped = input_df_clipped.fillna(self.zero_epsilon)
                input_df_clipped = input_df_clipped.replace(0.0, self.zero_epsilon)
                input_df_clipped = input_df_clipped.replace(0, self.zero_epsilon)
        return input_df_clipped

    def _prepare_input_og(self, input_df):
        input_df_clipped = input_df
        if len(input_df) > 0:
            _, outliers_mask = LcbuilderHelper.clip_outliers(input_df['og_flux'].to_numpy(), 3)
            input_df_clipped = input_df.loc[~outliers_mask].copy()
            if len(input_df_clipped) > 0:
                input_df_clipped['og_flux'] = self.minmax_scaler.fit_transform(input_df_clipped['og_flux'].values.reshape(-1, 1)).flatten()
            input_df_clipped = input_df_clipped.fillna(self.zero_epsilon)
            input_df_clipped = input_df_clipped.replace(0.0, self.zero_epsilon)
            input_df_clipped = input_df_clipped.replace(0, self.zero_epsilon)
        return input_df_clipped

    def _prepare_input_lc(self, input_df, period, epoch, duration, focus_range_in_durations=6,
                          required_range_percent=0.75, time_key='#time', flux_key='flux_0'):
        time = input_df[time_key].to_numpy()
        cadence_s = np.round(np.nanmedian(time[1:] - time[:-1]) * 3600 * 24)
        cadences_per_transit = LcbuilderHelper.estimate_transit_cadences(cadence_s, duration * focus_range_in_durations)
        transit_t0s_list = LcbuilderHelper.compute_t0s(time, period, epoch, duration)
        t0s_in_curve_indexes = np.argwhere((transit_t0s_list > time[0] - duration) &
                                          (transit_t0s_list < time[-1] + duration)).flatten()
        transit_t0s_list = transit_t0s_list[t0s_in_curve_indexes]
        good_quality_t0s = []
        t0s_with_data = []
        for t0 in transit_t0s_list:
            transit_with_baseline_half_length = (duration * focus_range_in_durations / 2)
            t0_in_curve_indexes = np.argwhere((time > t0 - transit_with_baseline_half_length) &
                                              (time < t0 + transit_with_baseline_half_length)).flatten()
            cadences_ratio = len(t0_in_curve_indexes) / cadences_per_transit
            if cadences_ratio > 0:
                t0s_with_data.append(t0)
            if cadences_ratio >= required_range_percent:
                good_quality_t0s.append(t0)
            else:
                input_df = input_df.loc[(input_df[time_key] < t0 - transit_with_baseline_half_length) |
                                    (input_df[time_key] > t0 + transit_with_baseline_half_length)]

        # We don't want time encoding because time will be used for folding and then dropped
        # input_df["#time"] = value_encode_times(time - time[0])
        # red_noise_freq = self.random_number_generator.uniform(0.01, 0.1)
        # flux_std = np.std(input_df['flux'])
        # red_noise_sd = self.random_number_generator.uniform(0, flux_std * 3)
        # red_noise = timesynth.noise.RedNoise(std=red_noise_sd, tau=red_noise_freq)
        # timeseries_rn = np.zeros(len(time))
        # TODO red noise algorithm is too slow for long time series
        # timeseries_rn = []
        # for value in time:
        #     rn_value = red_noise.sample_next(value, None, None)
        #     rn_value = rn_value[0] if isinstance(rn_value, (list, np.ndarray)) else rn_value
        #     timeseries_rn = timeseries_rn + [rn_value]
        # timeseries_rn = np.array(timeseries_rn)
        # input_df['flux_0'] = input_df['flux_0'] + timeseries_rn
        input_df[flux_key] = input_df[flux_key] / 2
        input_df[flux_key][input_df[flux_key] > 1] = 1
        input_df = input_df.fillna(self.zero_epsilon)
        input_df = input_df.replace(0.0, self.zero_epsilon)
        input_df = input_df.replace(0, self.zero_epsilon)
        return input_df, len(good_quality_t0s), len(t0s_with_data)

    def _prepare_input_star(self, target_row, star_df, teff_mod=1, rad_mod=1, mass_mod=1):
        if 'ra' in star_df.columns:
            ra = star_df['ra'].iloc[0]
        if 'dec' in star_df.columns:
            dec = star_df['dec'].iloc[0]
        if 'id' in star_df.columns:
            star_df.drop('id', inplace=True, axis=1)
        elif 'obj_id' in star_df.columns:
            star_df.drop('obj_id', inplace=True, axis=1)
        if 'Unnamed: 0' in star_df.columns:
            star_df.drop('Unnamed: 0', inplace=True, axis=1)
        if 'ra' in star_df.columns:
            star_df.drop('ra', inplace=True, axis=1)
        if pd.Series(['ra,']).isin(star_df.columns).any():
            star_df.drop('ra,', inplace=True, axis=1)
        if 'dec' in star_df.columns:
            star_df.drop('dec', inplace=True, axis=1)
        if 'dist_arcsec' in star_df.columns:
            star_df.drop('dist_arcsec', inplace=True, axis=1)
        if 'ld_a' in star_df.columns:
            star_df['ld_a'] = star_df['ld_a'].fillna(0.25)
        if 'ld_a' in star_df.columns:
            star_df['ld_b'] = star_df['ld_b'].fillna(0.25)
        if 'st_teff' in target_row and not np.isnan(target_row['st_teff']):
            star_df['Teff'] = target_row['st_teff']
        elif 'koi_steff' in target_row and not np.isnan(target_row['koi_steff']):
            star_df['Teff'] = target_row['koi_steff']
        elif 'tce_steff' in target_row and not np.isnan(target_row['tce_steff']):
            star_df['Teff'] = target_row['tce_steff']
        star_df['Teff'] = star_df['Teff'].fillna(6000)
        if 'st_rad' in target_row and not np.isnan(target_row['st_rad']):
            star_df['radius'] = target_row['st_rad']
        elif 'koi_srad' in target_row and not np.isnan(target_row['koi_srad']):
            star_df['radius'] = target_row['koi_srad']
        elif 'tce_sradius' in target_row and not np.isnan(target_row['tce_sradius']):
            star_df['radius'] = target_row['tce_sradius']
        if 'lum' in star_df.columns:
            star_df['lum'] = star_df['lum'].fillna(1)
        if 'logg' in star_df.columns:
            star_df['logg'] = star_df['logg'].fillna(1)
        if 'v' in star_df.columns:
            star_df['v'] = star_df['v'].fillna(-10)
        if 'j' in star_df.columns:
            star_df['j'] = star_df['j'].fillna(-10)
        if 'k' in star_df.columns:
            star_df['k'] = star_df['k'].fillna(-10)
        if 'h' in star_df.columns:
            star_df['h'] = star_df['h'].fillna(-10)
        star_df['Teff'] = star_df['Teff'] / 60000 * teff_mod
        star_df['Teff'] = star_df['Teff'] if star_df['Teff'].iloc[0] <= 1 else 1
        star_df['radius'] = star_df['radius'] / 3 * rad_mod
        star_df['radius'] = star_df['radius'] if star_df['radius'].iloc[0] <= 1 else 1
        if 'mass' in star_df:
            star_df['mass'] = star_df['mass'] / 3 * mass_mod
            star_df['mass'] = star_df['mass'] if star_df['mass'].iloc[0] <= 1 else 1
        if 'lum' in star_df.columns:
            star_df['lum'] = sigmoid(star_df['lum'])
        if 'logg' in star_df.columns:
            star_df['logg'] = sigmoid(star_df['logg'])
        if 'v' in star_df.columns:
            star_df['v'] = (30 - star_df['v']) / 40
        if 'j' in star_df.columns:
            star_df['j'] = (30 - star_df['j']) / 40
        if 'k' in star_df.columns:
            star_df['k'] = (30 - star_df['k']) / 40
        if 'h' in star_df.columns:
            star_df['h'] = (30 - star_df['h']) / 40
        return star_df.iloc[0], ra, dec

    def _prepare_input_neighbour_stars(self, star_df):
        search_radius = 10
        pixel_size = 20.25
        max_distance = search_radius * pixel_size
        # Limiting the set to 15 stars, removing the first one, which is the target star
        star_df = star_df.iloc[1:16, :].copy()
        if len(star_df) > 0:
            star_df['Teff'] = star_df['Teff'].fillna(6000)
            star_df['radius'] = star_df['radius'].fillna(1)
            star_df['mass'] = star_df['mass'].fillna(1)
            star_df['lum'] = star_df['lum'].fillna(1)
            star_df['v'] = star_df['v'].fillna(-10)
            star_df['j'] = star_df['j'].fillna(-10)
            star_df['k'] = star_df['k'].fillna(-10)
            star_df['h'] = star_df['h'].fillna(-10)
            star_df['Teff'] = star_df['Teff'] / 40000
            star_df['radius'] = star_df['radius'] / 3
            star_df['radius'] = star_df['radius'] if star_df['radius'].iloc[0] <= 1 else 1
            star_df['mass'] = star_df['mass'] / 3
            star_df['mass'] = star_df['mass'] if star_df['mass'].iloc[0] <= 1 else 1
            star_df['lum'] = star_df['lum'] / 1000
            star_df['v'] = (30 - star_df['v']) / 40
            star_df['j'] = (30 - star_df['j']) / 40
            star_df['k'] = (30 - star_df['k']) / 40
            star_df['h'] = (30 - star_df['h']) / 40
            if 'dist_arcsec' in star_df.columns:
                star_df['dist_arcsec'] = star_df['dist_arcsec'] / max_distance
                star_df['dist_arcsec'] = star_df['dist_arcsec'].fillna(max_distance)
        return star_df

    @staticmethod
    def compute_snr(file_prefix, time, flux, duration, period, epoch, oot_range=5, fold=False, baseline=1, zero_epsilon=1e-7):
        duration_to_period = duration / period
        lc_df = pd.DataFrame(columns=['time', 'time_folded', 'flux'])
        lc_df['time'] = time
        lc_df['flux'] = flux
        if fold:
            lc_df['time_folded'] = foldedleastsquares.fold(lc_df['time'].to_numpy(), period, epoch + period / 2)
            lc_df = lc_df.sort_values(by=['time_folded'], ascending=True)
        else:
            lc_df['time_folded'] = lc_df['time']
        lc_it = lc_df[(lc_df['time_folded'] > 0.5 - duration_to_period / 2) &
                      (lc_df['time_folded'] < 0.5 + duration_to_period / 2)]
        lc_oot = lc_df[((lc_df['time_folded'] < 0.5 - duration_to_period) & (
                    lc_df['time_folded'] > 0.5 - duration_to_period * oot_range / 2)) |
                       ((lc_df['time_folded'] > 0.5 + duration_to_period) & (
                                   lc_df['time_folded'] < 0.5 + duration_to_period * oot_range / 2))]
        snr = (baseline - lc_it['flux'].mean()) * np.sqrt(len(lc_it)) / lc_oot['flux'].std()
        if np.isnan(snr):
            logging.info(f"NaN SNR for {file_prefix}")
            snr = zero_epsilon
        elif snr >= 20 - zero_epsilon:
            snr = 1 - zero_epsilon
        elif snr < -20:
            snr = zero_epsilon
        else:
            snr = (snr + 20) / 40 + zero_epsilon
        return snr

    def compute_og_df(self, read_og_df, object_id, duration):
        if len(read_og_df) > 0:
            if read_og_df['core_flux'].isnull().values.all():
                logging.info("Nan values found for CORE_OG for %s, zeroing OG", object_id)
                read_og_df.loc[read_og_df['core_flux'].isnull(), 'core_flux'] = 1
            if read_og_df['halo_flux'].isnull().values.all():
                logging.info("Nan values found for HALO_OG for %s, zeroing OG", object_id)
                read_og_df.loc[read_og_df['halo_flux'].isnull(), 'halo_flux'] = 1
            read_og_df['core_flux'], _ = LcbuilderHelper.detrend(read_og_df['time'].to_numpy(),
                                                              read_og_df['core_flux'].to_numpy(), duration * 4,
                                                              check_cadence=True)
            read_og_df['halo_flux'], _ = LcbuilderHelper.detrend(read_og_df['time'].to_numpy(),
                                                              read_og_df['halo_flux'].to_numpy(), duration * 4,
                                                              check_cadence=True)
            read_og_df['og_flux'] = read_og_df['halo_flux'] - read_og_df['core_flux']
        read_og_df = read_og_df.drop(columns=['halo_flux', 'core_flux'])
        return read_og_df

    @abstractmethod
    def class_weights(self):
        pass


# df = pd.read_csv("/mnt/DATA-2/ete6/injected_objects.csv", index_col=False)
# df = shuffle(df)
# df.reset_index(inplace=True, drop=True)
# img = IatsonModelGenerator(df, "/mnt/DATA-2/ete6/lcs", 20, [11, 2500, 500, 500, 500, 500, 500, 500])
# img.__getitem__(20)
