import logging
from abc import ABC
import matplotlib.pyplot as plt
import random
from typing import Tuple
import ellc
import numpy as np
from numpy import ndarray
from numpy.random import default_rng
import astropy.units as u
import astropy.constants as ac
import timesynth
from sklearn.preprocessing import MinMaxScaler


class FeaturesInjector(ABC):
    random_number_generator = default_rng()

    def __init__(self, time_series: ndarray):
        super().__init__()
        self.time_series = time_series

    def inject(self) -> tuple[ndarray, ndarray, ndarray]:
        pass

class RedNoiseInjector(FeaturesInjector):
    def __init__(self, time_series: ndarray, power: tuple[float, float], period: tuple[float, float], number_of_signals: int):
        super().__init__(time_series)
        self.power = power
        self.period = period
        self.number_of_signals = number_of_signals

    def inject(self) -> tuple[ndarray, ndarray, ndarray]:
        number_of_red_noise = random.uniform(0, 100)
        if number_of_red_noise < 50:
            number_of_red_noise = 0
        elif number_of_red_noise < 75:
            number_of_red_noise = 1
        elif number_of_red_noise < 90:
            number_of_red_noise = 2
        else:
            number_of_red_noise = int(random.uniform(0, self.number_of_signals))
        flux: ndarray = np.ones(self.time_series.shape[1])
        for index in range(0, number_of_red_noise):
            red_noise_freq: float = self.random_number_generator.uniform(self.period[0], self.period[1])
            red_noise_power: float = self.random_number_generator.uniform(self.power[0], self.power[1])
            logging.info(f'Injecting red noise with power={red_noise_power} and freq={red_noise_freq}')
            red_noise = timesynth.noise.RedNoise(std=red_noise_power, tau=red_noise_freq)
            timeseries_rn: ndarray = np.zeros(self.time_series.shape[1])
            for time_index, value in enumerate(self.time_series[0]):
                rn_value = red_noise.sample_next(value, None, None)
                rn_value = rn_value[0] if isinstance(rn_value, (list, np.ndarray)) else rn_value
                timeseries_rn[time_index] = rn_value
            flux = flux + timeseries_rn
        return self.time_series[0], self.time_series[1] + flux - 1, flux


class SinusoidalInjector(FeaturesInjector):
    def __init__(self, time_series: ndarray, amplitude: tuple[float, float], period: tuple[float, float], number_of_signals: int):
        super().__init__(time_series)
        self.power = amplitude
        self.period = period
        self.number_of_signals = number_of_signals

    def inject(self) -> tuple[ndarray, ndarray, ndarray]:
        number_of_signals = random.uniform(0, 100)
        if number_of_signals < 50:
            number_of_signals = 0
        elif number_of_signals < 75:
            number_of_signals = 1
        elif number_of_signals < 90:
            number_of_signals = 2
        else:
            number_of_signals = int(random.uniform(0, self.number_of_signals))
        flux: ndarray = np.ones(self.time_series.shape[1])
        for index in range(0, number_of_signals):
            period: float = self.random_number_generator.uniform(self.period[0], self.period[1])
            amplitude: float = self.random_number_generator.uniform(self.power[0], self.power[1])
            logging.info(f'Injecting sinusoidal signal with power={amplitude} and freq={period}')
            flux = flux + amplitude * np.sin(2 * np.pi * self.time_series[0] / period + random.uniform(0, 2 * np.pi))
        return self.time_series[0], self.time_series[1] + flux - 1, flux

class PseudoPeriodicInjector(FeaturesInjector):
    def __init__(self, time_series: ndarray, amplitude: tuple[float, float], period: tuple[float, float],
                 amplitude_std: tuple[float, float], period_std: tuple[float, float],
                 number_of_signals: int):
        super().__init__(time_series)
        self.power = amplitude
        self.period = period
        self.number_of_signals = number_of_signals
        self.power_std = amplitude_std
        self.period_std = period_std

    def inject(self) -> tuple[ndarray, ndarray, ndarray]:
        number_of_signals = random.uniform(0, 100)
        if number_of_signals < 50:
            number_of_signals = 0
        elif number_of_signals < 75:
            number_of_signals = 1
        elif number_of_signals < 90:
            number_of_signals = 2
        else:
            number_of_signals = int(random.uniform(0, self.number_of_signals))
        flux: ndarray = np.ones(self.time_series.shape[1])
        for index in range(0, number_of_signals):
            period: float = self.random_number_generator.uniform(self.period[0], self.period[1])
            amplitude: float = self.random_number_generator.uniform(self.power[0], self.power[1])
            period_std: float = self.random_number_generator.uniform(self.period_std[0], self.period_std[1])
            amplitude_std: float = self.random_number_generator.uniform(0, amplitude / 10)
            logging.info(f'Injecting pseudo-periodic signal with power={amplitude} and freq={period}')
            pseudo_periodic_signal = timesynth.signals.PseudoPeriodic(amplitude=amplitude, frequency=period, ampSD=amplitude_std, freqSD=0)
            timeseries_pp: ndarray = np.zeros(self.time_series.shape[1])
            for time_index, value in enumerate(self.time_series[0]):
                rn_value = pseudo_periodic_signal.sample_next(value, None, None)
                rn_value = rn_value[0] if isinstance(rn_value, (list, np.ndarray)) else rn_value
                timeseries_pp[time_index] = rn_value
            flux = flux + timeseries_pp
        return self.time_series[0], self.time_series[1] + flux - 1, flux


class TransitsInjector(FeaturesInjector):

    def __init__(self, time_series: ndarray, transit_period_avg_std: tuple[float, float], transit_depth_boundaries: tuple[float, float]):
        super().__init__(time_series)
        self.transit_period_avg_std = transit_period_avg_std
        self.transit_depth_boundaries = transit_depth_boundaries

    def inject(self) -> tuple[ndarray, ndarray, ndarray]:
        number_of_planets = random.uniform(0, 100)
        if number_of_planets < 50:
            number_of_planets = 1
        elif number_of_planets < 80:
            number_of_planets = 2
        else:
            number_of_planets = 3
        star_radius = 1
        star_mass = 1
        flux = np.ones(self.time_series.shape[1])
        for index in range(0, number_of_planets):
            period = 0
            while period < 0.5:
                period = random.gauss(self.transit_period_avg_std[0], self.transit_period_avg_std[1])
            t0 = self.time_series[0][0] + period / random.uniform(0, 1)
            if t0 > self.time_series[0][-1]:
                t0 = np.random.uniform(self.time_series[0][0], self.time_series[0][-1])
            std = np.nanstd(self.time_series[1])
            depth = 0
            while depth < std / 3 or depth >= 0.4:
                depth = random.gauss(self.transit_depth_boundaries[0], self.transit_depth_boundaries[1]) * std
            planet_radius = np.sqrt(depth * (star_radius ** 2))
            logging.info(f'Injecting planet with P={period}, D={depth}')
            P1 = period * u.day
            a = np.cbrt((ac.G * star_mass * u.M_sun * P1 ** 2) / (4 * np.pi ** 2)).to(u.au)
            ld = [0.5, 0.5]
            planet_model = ellc.lc(
                t_obs=self.time_series[0],
                radius_1=(star_radius * u.R_sun).to(u.au) / a,  # star radius convert from AU to in units of a
                radius_2=(planet_radius * u.R_sun).to(u.au) / a,
                # convert from Rearth (equatorial) into AU and then into units of a
                sbratio=0,
                incl=90,
                light_3=0,
                t_zero=t0,
                period=period,
                a=None,
                q=planet_radius / star_radius * 0.1,
                f_c=None, f_s=None,
                ldc_1=ld, ldc_2=None,
                gdc_1=None, gdc_2=None,
                didt=None,
                domdt=None,
                rotfac_1=1, rotfac_2=1,
                hf_1=1.5, hf_2=1.5,
                bfac_1=None, bfac_2=None,
                heat_1=None, heat_2=None,
                lambda_1=None, lambda_2=None,
                vsini_1=None, vsini_2=None,
                t_exp=None, n_int=None,
                grid_1='default', grid_2='default',
                ld_1='quad', ld_2=None,
                shape_1='sphere', shape_2='sphere',
                spots_1=None, spots_2=None,
                exact_grav=False, verbose=1)
            flux = flux + planet_model - 1
        return self.time_series[0], self.time_series[1] + flux - 1, flux


class FlaresInjector(FeaturesInjector):

    def __init__(self, time_series: ndarray,
                 number_of_signals: int,
                 period_avg_std: tuple[float, float],
                 amplitude_avg_std: tuple[float, float],
                 length_avg_std: tuple[float, float]):
        super().__init__(time_series)
        self.number_of_signals = number_of_signals
        self.amplitude_avg_std = amplitude_avg_std
        self.period_avg_std = period_avg_std
        self.length_avg_std = length_avg_std

    def inject(self) -> tuple[ndarray, ndarray, ndarray]:
        if self.number_of_signals == 0:
            number_of_flares = 0
        else:
            number_of_flares = random.uniform(0, 100)
            if number_of_flares < 50:
                number_of_flares = 1
            elif number_of_flares < 80:
                number_of_flares = 2
            else:
                number_of_flares = int(random.uniform(0, self.number_of_signals))
        flux = np.ones(self.time_series.shape[1])
        for index in range(0, number_of_flares):
            logging.info(f'Injecting flare')
            flux, flares = self.inject_pseudo_periodic_flares(
                self.time_series[0], flux
            )
        return self.time_series[0], self.time_series[1] + flux - 1, flux

    def generate_flare_times(self, T_start, T_end):
        """
        Generate pseudo-periodic flare times between T_start and T_end.
        Periods are drawn from a normal distribution around P_med ± P_std.
        """
        flare_times = []
        current_time = T_start
        while current_time < T_end:
            period = 0
            while period < 5:
                period = random.gauss(self.period_avg_std[0], self.period_avg_std[1])
            current_time += period
            if current_time < T_end:
                flare_times.append(current_time)
        return np.array(flare_times)

    def inject_pseudo_periodic_flares(self, time, flux):
        """
        Inject pseudo-periodic flares with varying amplitude and duration.

        Parameters:
        - times: array of time values
        - fluxes: baseline light curve
        - P_med: median flare period (same units as times)
        - P_std: standard deviation of period
        - amplitude_range: (min, max) relative flare amplitudes
        - t_half_range: (min, max) duration to half-maximum of flares

        Returns:
        - new_fluxes: light curve with flares added
        - flare_metadata: list of dictionaries with flare parameters
        """
        T_start, T_end = time[0], time[-1]
        flare_peaks = self.generate_flare_times(T_start, T_end)
        new_flux = flux.copy()
        flare_metadata = []
        for t_peak in flare_peaks:
            amplitude = 0
            while amplitude < 0.01:
                amplitude = random.gauss(self.amplitude_avg_std[0], self.amplitude_avg_std[1])
            length = 0
            while length < 1 / 24 / 60 * 10 or length > 1 / 24 * 3:
                length = random.gauss(self.length_avg_std[0], self.length_avg_std[1])
            t_half = length / 2
            new_flux = self.inject_flare(time, new_flux, t_peak, amplitude, t_half)
            flare_metadata.append({
                't_peak': t_peak,
                'amplitude': amplitude,
                't_half': t_half
            })
        return new_flux, flare_metadata

    def davenport_flare_model(self, t_normalized):
        """
        Empirical flare shape from Davenport et al. (2014).
        Input: normalized time array (t_peak = 0, normalized by half-time)
        Output: relative flux (normalized to flare peak = 1)
        """
        flux = np.zeros_like(t_normalized)
        # Rise phase (t < 0)
        rise = t_normalized < 0
        t_rise = t_normalized[rise]
        flux[rise] = 1 + 1.941 * t_rise - 0.175 * t_rise ** 2 - 2.246 * t_rise ** 3 - 1.125 * t_rise ** 4
        # Decay phase (t >= 0)
        decay = t_normalized >= 0
        t_decay = t_normalized[decay]
        flux[decay] = 0.689 * np.exp(-1.600 * t_decay) + 0.303 * np.exp(-0.278 * t_decay)
        return flux

    def inject_flare(self, time, flux, t_peak, amplitude, t_half, window_factor=5):
        """
        Inject a synthetic flare into a light curve within a local time window.

        Parameters:
        - times: array of time stamps
        - fluxes: array of flux values
        - t_peak: time of flare peak
        - amplitude: relative flare amplitude (e.g., 0.01 for +1%)
        - t_half: half-duration (same units as times)
        - window_factor: number of t_half widths to define the flare window

        Returns:
        - new_fluxes: array with the flare added
        """
        new_fluxes = flux.copy()
        # Define flare injection window
        mask = np.argwhere((time > t_peak - t_half) &
                           (time < t_peak + t_half * window_factor)).flatten()
        t_norm = (time[mask] - t_peak) / t_half
        flare_shape = self.davenport_flare_model(t_norm)
        flare_flux = amplitude * flare_shape
        new_fluxes[mask] += flare_flux
        return new_fluxes

class GapsInjector(FeaturesInjector):
    def __init__(self, time_series: ndarray,
                 gaps_size_boundaries: tuple[float, float], curve_cadence):
        super().__init__(time_series)
        self.gaps_size_boundaries = gaps_size_boundaries
        self.curve_cadence = curve_cadence

    def inject(self) -> tuple[ndarray, ndarray, ndarray]:
        number_of_gaps = random.uniform(0, 100)
        if number_of_gaps < 50:
            number_of_gaps = 1
        elif number_of_gaps < 80:
            number_of_gaps = 2
        else:
            number_of_gaps = 3
        mask_indexes = []
        for _ in np.arange(0, number_of_gaps):
            gap_size = np.random.uniform(self.gaps_size_boundaries[0], self.gaps_size_boundaries[1])
            gap_size_cadences = int(gap_size / self.curve_cadence)
            gap_start_position = int(np.random.uniform(0, self.time_series.shape[1]))
            new_gap_indexes = np.arange(gap_start_position, min(gap_start_position + gap_size_cadences, self.time_series.shape[1]))
            mask_indexes = list(set(mask_indexes).union(new_gap_indexes))
        mask = np.ones(self.time_series.shape[1], dtype=bool)
        mask[mask_indexes] = False
        flux = self.time_series[1]
        flux_model = self.time_series[2]
        flux[~mask] = 0
        flux_model[~mask] = 0
        return self.time_series[0], flux, flux_model


class SantoTestDataGenerator:
    random_number_generator = default_rng()

    def __init__(self, output_dir: str, minimum_curve_size: int,
                 curves_time_boundaries: Tuple[float, float],
                 transit_depth_boundaries: Tuple[float, float],
                 transit_period_avg_std: Tuple[float, float],
                 white_noise_power_boundaries: Tuple[float, float],
                 red_noise_frequency_boundaries: Tuple[float, float],
                 red_noise_power_boundaries: Tuple[float, float],
                 sinusoid_frequency_boundaries: Tuple[float, float],
                 sinusoid_power_boundaries: Tuple[float, float],
                 pseudo_periodic_frequency_boundaries: Tuple[float, float],
                 pseudo_periodic_power_boundaries: Tuple[float, float],
                 pseudo_periodic_frequency_std_boundaries: Tuple[float, float],
                 pseudo_periodic_power_std_boundaries: Tuple[float, float],
                 gaps_size_boundaries: Tuple[float, float],
                 max_number_of_flares: int = 0,
                 max_number_of_pseudo_periodic: int = 3,
                 max_number_of_sinusoid: int = 3,
                 max_number_of_red_noise: int = 5,
                 flares_period_avg_std: Tuple[float, float] = (10, 5),
                 flares_amplitude_avg_std: Tuple[float, float] = (0.05, 0.05),
                 flares_length_avg_std: Tuple[float, float] = (0.05, 0.05),
                 curves_count=10000, curves_cadences: list=[60, 120, 300, 600, 1800],
                 only_plot=False):
        for curve_index in range(0, curves_count):
            curve_cadences = 1
            while curve_cadences < minimum_curve_size:
                curve_timespan: float = random.uniform(curves_time_boundaries[0], curves_time_boundaries[1])
                selected_cadence = random.choice(curves_cadences) / 3600 / 24
                curve_cadences = int(curve_timespan // selected_cadence)
            flux: ndarray = np.ones((36, curve_cadences))
            flux[0] = np.linspace(0, curve_timespan, curve_cadences)
            white_noise_std: float = 0.0
            while white_noise_std < 0.00001:
                white_noise_std = random.gauss(white_noise_power_boundaries[0], white_noise_power_boundaries[1])
            logging.info(f'Injecting white noise with std={white_noise_std}')
            flux[1] = flux[1] + np.random.normal(loc=0, scale=white_noise_std, size=curve_cadences)
            flux[0], flux[1], flux[2] = RedNoiseInjector(flux, red_noise_power_boundaries, red_noise_frequency_boundaries, max_number_of_red_noise).inject()
            #flux[0] = SinusoidalInjector(time, flux[0], sinusoid_power_boundaries, sinusoid_frequency_boundaries, max_number_of_sinusoid).inject()
            flux[0], flux[1], flux[2] = PseudoPeriodicInjector(flux, pseudo_periodic_power_boundaries, pseudo_periodic_frequency_boundaries,
                                             pseudo_periodic_power_std_boundaries, pseudo_periodic_frequency_std_boundaries, max_number_of_pseudo_periodic).inject()
            flux[0], flux[1], flux[2] = FlaresInjector(flux, max_number_of_flares, flares_period_avg_std, flares_amplitude_avg_std, flares_length_avg_std).inject()
            flux[0], flux[1], flux[2] = TransitsInjector(flux, transit_period_avg_std, transit_depth_boundaries).inject()
            flux[0], flux[1], flux[2] = GapsInjector(flux, gaps_size_boundaries, selected_cadence).inject()
            flux[3] = np.copy(flux[2])
            flux[3, np.argwhere((flux[3] <= 1e-7) | (flux[3] > 1 - 1e-7)).flatten()] = float(0)
            flux[3, np.argwhere(flux[3] > 1e-7).flatten()] = float(1)
            flux[4:36] = self.timestamp_encoding(flux[0])
            if only_plot:
                args_empty = np.argwhere(flux[1] > 0).flatten()
                fig, axs = plt.subplots(1, 1, figsize=(10, 5))
                axs.scatter(flux[0][args_empty], flux[1][args_empty], s=2)
                axs.plot(flux[0][args_empty], flux[2][args_empty], c='orange')
                plt.show()
            else:
                np.savetxt(f'{output_dir}/{curve_index}_model.csv', flux, delimiter=',')

    def timestamp_encoding(self, timestamps: np.ndarray, d_model: int = 32) -> np.ndarray:
        """
        Encode real timestamps into a positional encoding-like representation.

        Args:
            timestamps (np.ndarray): Array of shape (500,) with time values.
            d_model (int): Embedding dimension (must be even).

        Returns:
            np.ndarray: Array of shape (500, d_model) with time embeddings.
        """
        timestamps = timestamps.reshape(-1, 1)  # Ensure shape (500, 1)
        div_term = np.exp(np.arange(0, d_model, 2) * (-np.log(10000.0) / d_model))
        angles = timestamps * div_term
        pos_encoding = np.zeros((timestamps.shape[0], d_model))
        pos_encoding[:, 0::2] = (np.sin(angles) + 1) / 2
        pos_encoding[:, 1::2] = (np.cos(angles) + 1) / 2
        pos_encoding[pos_encoding > 1 - 1e-7] = 1 - 1e-7
        pos_encoding[pos_encoding < 0 + 1e-7] = 1 - 1e-7
        return np.transpose(pos_encoding)

