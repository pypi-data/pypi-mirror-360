import gzip
import logging
import multiprocessing
import os
import pathlib
import random
import shutil
from multiprocessing import Pool
from random import randrange

import re
from pathlib import Path
import ellc
import pandas as pd
import numpy as np
#import timesynth
from lcbuilder.star import starinfo
from lcbuilder.star.HabitabilityCalculator import HabitabilityCalculator
from lcbuilder.star.TicStarCatalog import TicStarCatalog

import astropy.units as u
import astropy.constants as ac
from lightkurve import TessLightCurve
from numpy.random import default_rng
from exoml.ml.physics.transit_functions import t14
from exoml.preparation.parser_utils import CreateTargetInput, create_star_csvs, detrend, prepare_lc_data


def create_injection_dataframe(injections_dir, lcs_dir):
    backeb_df = pd.read_csv(injections_dir + '/ete6_backeb_data.txt', comment="#")
    eb_df = pd.read_csv(injections_dir + '/ete6_eb_data.txt', comment="#")
    planet_df = pd.read_csv(injections_dir + '/ete6_planet_data.txt', comment="#")
    df = pd.DataFrame(columns=['object_id', 'type', 'period', 'epoch', 'Rsec/Rpri', 'b',
                                'a/Rstar', 'duration(h)', 'depth_primary', 'depth_secondary',
                               'insolation', 'Rstar_primary', 'Rstar_secondary', 'contact_amplitude', 'Mstar',
                               'radius(earth)'])
    i = 0
    log_count = 100
    random_number_generator = default_rng()
    for lc_file in list(pathlib.Path(lcs_dir).glob('*.fits')):
        object_id_no = int(str(lc_file).split('-')[1])
        object_id = 'TIC ' + str(object_id_no)
        # lc = TessLightCurve.read(lc_file)
        # object_id = lc.meta['OBJECT']
        star_file = lcs_dir + '/' + object_id + '_star.csv'
        star_df = pd.read_csv(star_file)
        star_radius = star_df['radius'].iloc[0]
        try:
            star_radius = 1 if np.isnan(star_radius) else star_radius
        except:
            print("ERROR WITH " + str(star_file))
        star_mass = star_df['mass'].iloc[0]
        try:
            if np.isnan(star_mass) and np.isnan(star_df['radius'].iloc[0]):
                star_mass = 1
            elif np.isnan(star_mass):
                star_mass = star_radius ** (1 / 0.8)
        except:
            print("ERROR WITH " + str(star_file))
        has_injected_object = False
        target_rows = backeb_df[backeb_df['TIC ID'] == object_id_no]
        for index, target_row in target_rows.iterrows():
            has_injected_object = True
            period = target_row['Orbital Period']
            epoch = target_row['Epoch [BTJD]']
            binary_rad = (target_row['Primary Star Depth'] * 1e-6 * (star_radius ** 2)) ** (1 / 2)
            if not np.isnan(target_row['Primary Rstar']):
                duration = t14(star_radius, star_mass, period, R_p=binary_rad)
            else:
                duration = t14(star_radius, star_mass, period)
            duration = duration * 24
            df = df.append({'object_id': object_id, 'type': 'bckEB', 'period': period,
                       'epoch': epoch,
                       'Rsec/Rpri': binary_rad / star_radius,
                       'b': target_row['Impact Parameter'],
                       'a/Rstar': 0, 'duration(h)': duration,
                       'depth_primary': target_row['Primary Star Depth'],
                       'depth_secondary': target_row['Primary Star Depth'],
                       'insolation': 0, 'Rstar_primary': target_row['Primary Rstar'],
                       'Rstar_secondary': target_row['Secondary Rstar'],
                       'contact_amplitude': target_row['Contact Binary Amplitude'],
                       'Mstar': star_mass,
                       'radius(earth)': (binary_rad * u.R_sun).to(u.R_earth).value}, ignore_index=True)
        target_rows = eb_df[eb_df['TIC ID'] == object_id_no]
        for index, target_row in target_rows.iterrows():
            has_injected_object = True
            period = target_row['Orbital Period']
            epoch = target_row['Epoch [BTJD]']
            if not np.isnan(target_row['Primary Rstar']):
                duration = t14(star_radius, star_mass, period, R_p=target_row['Primary Rstar'])
            else:
                duration = t14(star_radius, star_mass, period)
            duration = duration * 24
            binary_rad = (target_row['Primary Star Depth'] * 1e-6 * (star_radius ** 2)) ** (1 / 2)
            df = df.append({'object_id': object_id, 'type': 'EB', 'period': period,
                       'epoch': epoch,
                       'Rsec/Rpri': binary_rad / star_radius,
                       'b': target_row['Impact Parameter'],
                       'a/Rstar': 0, 'duration(h)': duration,
                       'depth_primary': target_row['Primary Star Depth'],
                       'depth_secondary': target_row['Primary Star Depth'],
                       'insolation': 0, 'Rstar_primary': target_row['Primary Rstar'],
                       'Rstar_secondary': target_row['Secondary Rstar'],
                       'contact_amplitude': target_row['Contact Binary Amplitude'],
                       'Mstar': star_mass,
                       'radius(earth)': (binary_rad * u.R_sun).to(u.R_earth).value}, ignore_index=True)
        target_rows = planet_df[planet_df['TIC ID'] == object_id_no]
        for index, target_row in target_rows.iterrows():
            has_injected_object = True
            period = target_row['Orbital Period']
            epoch = target_row['Epoch [BTJD]']
            duration = target_row['duration[h]']
            if np.isnan(duration) or duration == 0:
                duration = t14(star_radius, star_mass, period)
                duration = duration * 24
            df = df.append({'object_id': object_id, 'type': 'planet', 'period': period,
                       'epoch': epoch,
                       'Rsec/Rpri': target_row['Rp/Rstar'],
                       'b': target_row['Impact Parameter'],
                       'a/Rstar': target_row['a/Rstar'], 'duration(h)': duration,
                       'depth_primary': target_row['depth'],
                       'depth_secondary': 0,
                       'insolation': target_row['Insolation Flux'],
                       'Rstar_primary': target_row['Rstar'],
                       'Rstar_secondary': target_row['Rstar'] * target_row['Rp/Rstar'],
                       'contact_amplitude': 0,
                       'Mstar': star_mass,
                       'radius(earth)': target_row['Rp']}, ignore_index=True)
        while not has_injected_object:
            min_period = 0.5
            max_period = 10
            period = random_number_generator.uniform(min_period, max_period)
            depth_ppm = random_number_generator.uniform(100, 500)
            planet_radius = (depth_ppm / 1e6 * ((star_radius * u.R_sun).to(u.R_earth).value ** 2)) ** 0.5
            # min_lc_time = 1612.85 + 0.5
            # epoch = random_number_generator.uniform(min_lc_time, min_lc_time + period)
            # duration = t14(star_radius, star_mass, period)
            # if 2 * duration < period:
            #     duration = duration * 24
            #     df = df.append({'object_id': object_id, 'type': 'none', 'period': period,
            #                     'epoch': epoch,
            #                     'Rsec/Rpri': 1e-7,
            #                     'b': 0,
            #                     'a/Rstar': 1e-7, 'duration(h)': duration,
            #                     'depth_primary': depth_ppm,
            #                     'depth_secondary': 0,
            #                     'insolation': 0, 'Rstar_primary': 1e-7,
            #                     'Rstar_secondary': 1e-7,
            #                     'contact_amplitude': 0,
            #                     'Mstar': star_mass,
            #                     'radius(earth)': planet_radius}, ignore_index=True)
            #     has_injected_object = True
            for match in Path("/data/scratch/ml/ete6/lcs/").glob(object_id + '_*_input_scalar_values.csv'):
                period = float(re.findall("\d+\.\d+", str(match))[0])
                min_lc_time = 1612.85 + 0.5
                epoch = random_number_generator.uniform(min_lc_time, min_lc_time + period)
                duration = t14(star_radius, star_mass, period)
                while 2 * duration >= period:
                    duration = duration / 2
                if 2 * duration < period:
                    duration = duration * 24
                    df = df.append({'object_id': object_id, 'type': 'none', 'period': period,
                                    'epoch': epoch,
                                    'Rsec/Rpri': 1e-7,
                                    'b': 0,
                                    'a/Rstar': 1e-7, 'duration(h)': duration,
                                    'depth_primary': depth_ppm,
                                    'depth_secondary': 0,
                                    'insolation': 0, 'Rstar_primary': 1e-7,
                                    'Rstar_secondary': 1e-7,
                                    'contact_amplitude': 0,
                                    'Mstar': star_mass,
                                    'radius(earth)': planet_radius}, ignore_index=True)
                    has_injected_object = True
                    break
                else:
                    print("inloop")
        print("Processed " + str(i) + " TICs.")
        if (i + 1) % log_count == 0:
            print("Processed " + str(i) + " TICs.")
            #df = df.sort_values(["TIC ID", "type"], ascending=True)
            #df.to_csv(injections_dir + '/injected_objects.csv')
        i = i + 1
    df = df.sort_values(["object_id", "type"], ascending=True)
    df.to_csv(injections_dir + '/injected_objects.csv')


def create_target_csvs(lcs_dir, models_dir, cores=multiprocessing.cpu_count() - 1, max_lc_length=20610, force=False,
                       ids=None, mode=['all']):
    injected_files_df = pd.read_csv(models_dir + '/injected_objects.csv')
    inputs = []
    if ids is not None:
        injected_files_df = injected_files_df[injected_files_df['object_id'].isin(ids)]
    injected_files_df = injected_files_df.sort_values(by=["period"], ascending=True)
    injected_files_df = injected_files_df.reset_index(drop=True)
    ranges = range(0, len(injected_files_df))
    print("Total number of targets is " + str(len(injected_files_df)))
    for index in ranges:
        target_row = injected_files_df.iloc[index]
        object_id = target_row['object_id']
        mission_id = object_id.split(' ')[1]
        lc_file = lcs_dir + "/tess2019128220341-" + str(mission_id).zfill(16) + "-0016-s_lc.fits"
        tpf_file = lcs_dir + "/tpfs/tess2019128220341-" + str(mission_id).zfill(16) + "-0016-s_tp.fits"
        inputs = inputs + [CreateTargetInput('TIC', object_id, lc_file, lcs_dir, models_dir, target_row,
                                             None, index, max_lc_length, tpf_files=[tpf_file], force=force, mode=mode)]
    with Pool(processes=cores, maxtasksperchild=1) as pool:
        pool.map(_create_target_csv, inputs, chunksize=1)

def create_injected_target_csvs(lcs_dir, models_dir, cores=multiprocessing.cpu_count() - 1,
                                max_lc_length=20610, force=False, ids=None):
    injected_files_df = pd.read_csv(models_dir + '/injected_objects.csv')
    injected_files_df = injected_files_df[injected_files_df['type'] == 'none']
    inputs = []
    if ids is not None:
        injected_files_df = injected_files_df[injected_files_df['object_id'].isin(ids)]
    for index, target_row in injected_files_df.iterrows():
        object_id = target_row['object_id']
        mission_id = object_id.split(' ')[1]
        lc_file = lcs_dir + "/tess2019128220341-" + str(mission_id).zfill(16) + "-0016-s_lc.fits"
        tpf_file = lcs_dir + "/tpfs/tess2019128220341-" + str(mission_id).zfill(16) + "-0016-s_tp.fits"
        inputs = inputs + [CreateTargetInput('TIC', object_id, lc_file, lcs_dir, models_dir, target_row,
                                             None, max_lc_length, tpf_files=[tpf_file], force=force,
                                             inject_random=True)]
    with Pool(processes=cores, maxtasksperchild=1) as pool:
        pool.map(_create_target_csv, inputs, chunksize=1)

def _create_target_csv(create_target_input):
    pid = multiprocessing.current_process().pid
    type_dict = {0: 'none', 1: 'bckEB', 2: 'EB', 3: 'planet'}
    file_prefix = create_target_input.target_dir + '/' + create_target_input.id
    file_planet_prefix = file_prefix + '_' + \
                         str(round(create_target_input.injected_files_df['period'], 2))
    logging.info("PID %s: Trying to get info for %s", pid, file_planet_prefix)
    file_name = file_planet_prefix + '_metrics_short.csv'
    if create_target_input.force or not os.path.exists(file_name):
        try:
            lc_df = pd.DataFrame(columns=['#time', 'flux', 'flux_err', 'planet_model', 'eb_model', 'bckeb_model',
                                          'centroid_ra', 'centroid_dec', 'og_flux', 'bck_flux'])
            lc = TessLightCurve.read(create_target_input.lc_file)
            mission_id = lc.meta['OBJECT']
            mission_id = int(mission_id.split(' ')[1])
            leading_zeros_object_id = '{:09}'.format(mission_id)
            lc_length = len(lc)
            eb_model_flux = np.ones(lc_length)
            backeb_model_flux = np.ones(lc_length)
            planet_model_flux = np.ones(lc_length)
            model_file = create_target_input.models_dir + '/ebs/EBs/EBs' + '_' + leading_zeros_object_id + '.txt'
            star_info = starinfo.StarInfo(create_target_input.id, *TicStarCatalog().catalog_info(mission_id))
            if create_target_input.inject_random:
                type_random = randrange(4)
                type = type_dict[type_random]
                rstar = star_info.radius * u.Rsun
                time = lc.time.value
                flux = lc.flux.value
                period = create_target_input.injected_files_df['period']
                t0 = create_target_input.injected_files_df['epoch']
                texpo = 120 / 60. / 60. / 24.
                if type == 'none':
                    a = 1
                elif type == 'bckEB':
                    rtransit = random.uniform(0.1, rstar / 2) * u.Rsun
                    a = HabitabilityCalculator().calculate_semi_major_axis(period, star_info.mass)
                    model = lc(
                        t_obs=time,
                        radius_1=rstar.to(u.au) / a,  # star radius convert from AU to in units of a
                        radius_2=rtransit.to(u.au) / a,
                        # convert from Rearth (equatorial) into AU and then into units of a
                        sbratio=0,
                        incl=90,
                        light_3=0,
                        t_zero=t0,
                        period=period,
                        a=None,
                        q=1e-6,
                        f_c=None, f_s=None,
                        ldc_1=[0.5, 0.5], ldc_2=None,
                        gdc_1=None, gdc_2=None,
                        didt=None,
                        domdt=None,
                        rotfac_1=1, rotfac_2=1,
                        hf_1=1.5, hf_2=1.5,
                        bfac_1=None, bfac_2=None,
                        heat_1=None, heat_2=None,
                        lambda_1=None, lambda_2=None,
                        vsini_1=None, vsini_2=None,
                        t_exp=texpo, n_int=None,
                        grid_1='default', grid_2='default',
                        ld_1='quad', ld_2=None,
                        shape_1='sphere', shape_2='sphere',
                        spots_1=None, spots_2=None,
                        exact_grav=False, verbose=1)
                    model = model / 10
                    planet_model_flux = flux + model - 1.
                elif type == 'EB':
                    rtransit = random.uniform(0.1, rstar / 2) * u.Rsun
                    a = HabitabilityCalculator().calculate_semi_major_axis(period, star_info.mass)
                    model = lc(
                        t_obs=time,
                        radius_1=rstar.to(u.au) / a,  # star radius convert from AU to in units of a
                        radius_2=rtransit.to(u.au) / a,
                        # convert from Rearth (equatorial) into AU and then into units of a
                        sbratio=0,
                        incl=90,
                        light_3=0,
                        t_zero=t0,
                        period=period,
                        a=None,
                        q=1e-6,
                        f_c=None, f_s=None,
                        ldc_1=[0.5, 0.5], ldc_2=None,
                        gdc_1=None, gdc_2=None,
                        didt=None,
                        domdt=None,
                        rotfac_1=1, rotfac_2=1,
                        hf_1=1.5, hf_2=1.5,
                        bfac_1=None, bfac_2=None,
                        heat_1=None, heat_2=None,
                        lambda_1=None, lambda_2=None,
                        vsini_1=None, vsini_2=None,
                        t_exp=texpo, n_int=None,
                        grid_1='default', grid_2='default',
                        ld_1='quad', ld_2=None,
                        shape_1='sphere', shape_2='sphere',
                        spots_1=None, spots_2=None,
                        exact_grav=False, verbose=1)
                    planet_model_flux = flux + model - 1.
                elif type == 'planet':
                    curve_rms = np.std(flux)
                    rms_in_radius = (curve_rms * (star_info.radius ** 2)) ** (1 / 2)
                    rtransit = random.uniform(rms_in_radius / 3, 0.1) * u.Rsun
                    a = HabitabilityCalculator().calculate_semi_major_axis(period, star_info.mass)
                    model = lc(
                        t_obs=time,
                        radius_1=rstar.to(u.au) / a,  # star radius convert from AU to in units of a
                        radius_2=rtransit.to(u.au) / a,
                        # convert from Rearth (equatorial) into AU and then into units of a
                        sbratio=0,
                        incl=90,
                        light_3=0,
                        t_zero=t0,
                        period=period,
                        a=None,
                        q=1e-6,
                        f_c=None, f_s=None,
                        ldc_1=[0.5, 0.5], ldc_2=None,
                        gdc_1=None, gdc_2=None,
                        didt=None,
                        domdt=None,
                        rotfac_1=1, rotfac_2=1,
                        hf_1=1.5, hf_2=1.5,
                        bfac_1=None, bfac_2=None,
                        heat_1=None, heat_2=None,
                        lambda_1=None, lambda_2=None,
                        vsini_1=None, vsini_2=None,
                        t_exp=texpo, n_int=None,
                        grid_1='default', grid_2='default',
                        ld_1='quad', ld_2=None,
                        shape_1='sphere', shape_2='sphere',
                        spots_1=None, spots_2=None,
                        exact_grav=False, verbose=1)
                    planet_model_flux = flux + model - 1.
            if os.path.exists(model_file):
                model_df = pd.read_csv(model_file, header=None)
                eb_model_flux = model_df[0].to_numpy()
                eb_model_flux = eb_model_flux / np.median(eb_model_flux)
                eb_model_flux = resample_model(eb_model_flux, lc.time.value)
            model_file = create_target_input.models_dir + '/backebs/BackEBs/BackEBs_' + leading_zeros_object_id + '.txt'
            if os.path.exists(model_file):
                model_df = pd.read_csv(model_file, header=None)
                backeb_model_flux = model_df[0].to_numpy()
                backeb_model_flux = backeb_model_flux / np.median(backeb_model_flux)
                backeb_model_flux = resample_model(backeb_model_flux, lc.time.value)
                # import matplotlib.pyplot as plt
                # plt.scatter(np.linspace(lc.time.value[0], lc.time.value[-1], len(eb_model_flux)), eb_model_flux)
                # plt.scatter(lc.time.value, lc.pdcsap_flux.value / np.median(lc.pdcsap_flux.value))
                # plt.show()
            model_file = create_target_input.models_dir + '/planets/Planets/Planets' + '_' + leading_zeros_object_id + '.txt'
            if os.path.exists(model_file):
                model_df = pd.read_csv(model_file, header=None)
                planet_model_flux = model_df[0].to_numpy()
                planet_model_flux = planet_model_flux / np.median(planet_model_flux)
                planet_model_flux = resample_model(planet_model_flux, lc.time.value)
            padding_zeros_count = create_target_input.max_lc_length - lc_length
            padding_zeros_count = 0 if padding_zeros_count < 0 else padding_zeros_count
            padding_zeros_count_left = padding_zeros_count // 2 + 1 if padding_zeros_count % 2 != 0 else padding_zeros_count // 2
            padding_zeros_count_right = padding_zeros_count // 2
            padding_zeros_left = np.zeros(padding_zeros_count_left)
            padding_zeros_right = np.zeros(padding_zeros_count_right)
            padding_ones_left = np.zeros(padding_zeros_count_left)
            padding_ones_right = np.zeros(padding_zeros_count_right)
            flux_values = np.array(lc.pdcsap_flux.value)
            median_flux = np.median(flux_values)
            flux_values = flux_values / median_flux
            if len(np.argwhere(flux_values < 0).flatten()) > 0:
                flux_values = np.array(lc.pdcsap_flux.value) + 2 * np.abs(np.nanmin(lc.pdcsap_flux.value))
                median_flux = np.median(flux_values)
                flux_values = flux_values / median_flux
            time_values = lc.time.value
            duration = create_target_input.injected_files_df['duration(h)'] / 24
            duration_to_period = duration / create_target_input.injected_files_df['period']
            flux_detrend_0 = detrend(time_values, flux_values, duration_to_period * 4)
            lc_df['flux_0'] = flux_detrend_0
            bck_flux_detrend = detrend(time_values, flux_values, duration_to_period * 4, smooth=False)
            lc_df['background_flux'] = bck_flux_detrend
            flux_err_values = np.array(lc.flux_err.value) / median_flux
            lc_df['time'] = np.array(lc.time.value)
            lc_df['flux'] = flux_values
            lc_df['flux_err'] = flux_err_values
            lc_df['centroids_x'] = np.array(lc.mom_centr1.value)
            lc_df['centroids_y'] = np.array(lc.mom_centr2.value)
            lc_df['motion_x'] = np.array(lc.pos_corr1.value)
            lc_df['motion_y'] = np.array(lc.pos_corr2.value)
            lc_df['eb_model'] = np.array(eb_model_flux)
            lc_df['bckeb_model'] = np.array(backeb_model_flux)
            lc_df['planet_model'] = np.array(planet_model_flux)
            lc_df = lc_df.fillna(0)
            prepare_lc_data(file_planet_prefix, create_target_input.id, lc_df,
                            create_target_input.injected_files_df['duration(h)'] / 24,
                            create_target_input.injected_files_df['period'],
                            create_target_input.injected_files_df['epoch'],
                            star_info.ra, star_info.dec, star_info, False, tpf_files=create_target_input.tpf_files,
                            modes=create_target_input.mode)
        except Exception as e:
            logging.exception("PID %s: Failed get info for %s", pid, file_planet_prefix)


def create_injected_target_csvs(create_target_input):
    random_number_generator = default_rng()
    lc_df = pd.DataFrame(columns=['#time', 'flux', 'flux_err',
                                  'centroid_x', 'centroid_y', 'motion_x', 'motion_y', 'bck_flux'])
    lc_df_injected = pd.DataFrame(columns=['#time', 'flux', 'flux_err', 'planet_model',
                                  'centroid_x', 'centroid_y', 'motion_x', 'motion_y', 'bck_flux'])
    try:
        lc = TessLightCurve.read(create_target_input.lc_file)
    except Exception as e:
        print("Invalid fits file " + create_target_input.lc_file)
        return
    try:
        star_df = pd.read_csv(create_target_input.star_file)
    except Exception as e:
        print("Invalid fits file " + create_target_input.lc_file)
        return
    star_radius = star_df.loc[0, 'radius']
    star_mass = star_df.loc[0, 'mass']
    ld = (star_df.loc[0, 'ld_a'], star_df.loc[0, 'ld_b'])
    object_id = lc.meta['OBJECT']
    object_id = int(object_id.split(' ')[1])
    mission_id = 'TIC'
    injected_file_row = create_target_input.injected_files_df[
        create_target_input.injected_files_df['TIC ID'] == object_id]
    leading_zeros_object_id = '{:09}'.format(object_id)
    lc_length = len(lc)
    padding_zeros_count = create_target_input.max_lc_length - lc_length
    padding_zeros_count = 0 if padding_zeros_count < 0 else padding_zeros_count
    padding_zeros_count_left = padding_zeros_count // 2 + 1 if padding_zeros_count % 2 != 0 else padding_zeros_count // 2
    padding_zeros_count_right = padding_zeros_count // 2
    padding_zeros_left = np.zeros(padding_zeros_count_left)
    padding_zeros_right = np.zeros(padding_zeros_count_right)
    padding_ones_left = np.zeros(padding_zeros_count_left)
    padding_ones_right = np.zeros(padding_zeros_count_right)
    planet_model_flux = np.ones(lc_length)
    planets_num = random_number_generator.uniform(1, 3)
    planet_periods = np.zeros(planets_num)
    planet_t0s = np.zeros(planets_num)
    planet_radius = np.zeros(planets_num)
    rms = np.std(lc.flux)
    rms_ppm = np.std(lc.flux) * 1000000 # ppms
    times = lc.time.value
    flux = lc.flux.value
    modified_flux = flux
    max_period = 0.5
    red_noise_number = random_number_generator.uniform(0, 3)
    for red_noise in red_noise_number:
        red_noise_freq = random_number_generator.uniform(0.01, 2)
        flux_std = rms
        red_noise_sd = random_number_generator.uniform(0, flux_std * 3)
        red_noise = timesynth.noise.RedNoise(std=red_noise_sd, tau=red_noise_freq)
        timeseries_rn = np.zeros(len(times))
        timeseries_rn = []
        for value in times:
            rn_value = red_noise.sample_next(value, None, None)
            rn_value = rn_value[0] if isinstance(rn_value, (list, np.ndarray)) else rn_value
            timeseries_rn = timeseries_rn + [rn_value]
        timeseries_rn = np.array(timeseries_rn)
        modified_flux = modified_flux + timeseries_rn
    #TODO write flux with red noise
    for planet in np.arange(0, planets_num):
        planet_periods[planet] = random_number_generator.uniform(0.5, 20)
        max_period = max_period if planet_periods[planet] < max_period else planet_periods[planet]
        planet_t0s[planet] = lc.time[0] + planet_periods[planet] / random_number_generator.uniform(0, planet_periods[planet])
        num_transits_pesimistic = planet_t0s[planet] // len(lc.time.value)
        depth_ppm = random_number_generator(rms_ppm // num_transits_pesimistic, rms_ppm * 4)
        planet_radius[planet] = np.sqrt((depth_ppm / 1e6) * (star_radius ** 2))
        P1 = planet_periods[planet] * u.day
        a = np.cbrt((ac.G * star_mass * u.M_sun * P1 ** 2) / (4 * np.pi ** 2)).to(u.au)
        planet_model = ellc.lc(
            t_obs=times,
            radius_1=(star_radius * u.R_sun).to(u.au) / a,  # star radius convert from AU to in units of a
            radius_2=(planet_radius * u.R_earth).to(u.au) / a,
            # convert from Rearth (equatorial) into AU and then into units of a
            sbratio=0,
            incl=90,
            light_3=0,
            t_zero=planet_t0s[planet],
            period=planet_periods[planet],
            a=None,
            q=1e-6,
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
        modified_flux = modified_flux - planet_model + 1
    bck_flux_detrend = detrend(times, lc.background_flux.value, 1, smooth=False)
    lc_df['bck_flux'] = np.concatenate((padding_ones_left, bck_flux_detrend, padding_ones_right))
    flux_err_values = np.array(lc.flux_err.value) / np.nanmedian(modified_flux)
    lc_df['#time'] = np.concatenate((padding_zeros_left, np.array(lc.time.value), padding_zeros_right))
    lc_df['flux'] = np.concatenate((padding_ones_left, modified_flux, padding_ones_right))
    lc_df['flux_err'] = np.concatenate((padding_zeros_left, flux_err_values, padding_zeros_right))
    lc_df['centroid_x'] = np.concatenate((padding_zeros_left, np.array(lc.centroid_col.value), padding_zeros_right))
    lc_df['centroid_y'] = np.concatenate((padding_zeros_left, np.array(lc.centroid_row.value), padding_zeros_right))
    lc_df['motion_x'] = np.concatenate((padding_zeros_left, np.array(lc.mom_centr1.value), padding_zeros_right))
    lc_df['motion_y'] = np.concatenate((padding_zeros_left, np.array(lc.mom_centr2.value), padding_zeros_right))
    lc_df['planet_model'] = np.concatenate((padding_ones_left, np.array(planet_model_flux), padding_ones_right))
    lc_df = lc_df.fillna(0)
    lc_df.to_csv(lcs_dir + '/' + mission_id + '_' + str(object_id) + '_noise_lc.csv')
    #TODO write final injected flux
    padding_zeros_count = create_target_input.max_lc_length - lc_length
    padding_zeros_count = 0 if padding_zeros_count < 0 else padding_zeros_count
    padding_zeros_count_left = padding_zeros_count // 2 + 1 if padding_zeros_count % 2 != 0 else padding_zeros_count // 2
    padding_zeros_count_right = padding_zeros_count // 2
    padding_zeros_left = np.zeros(padding_zeros_count_left)
    padding_zeros_right = np.zeros(padding_zeros_count_right)
    padding_ones_left = np.zeros(padding_zeros_count_left)
    padding_ones_right = np.zeros(padding_zeros_count_right)
    flux_values = np.array(lc.pdcsap_flux.value)
    median_flux = np.nanmedian(flux_values)
    flux_values = flux_values / median_flux
    if len(np.argwhere(flux_values < 0).flatten()) > 0:
        flux_values = np.array(lc.pdcsap_flux.value) + 2 * np.abs(np.nanmin(lc.pdcsap_flux.value))
        median_flux = np.median(flux_values)
        flux_values = flux_values / median_flux
    time_values = lc.time.value
    duration = t14(star_radius, star_mass, max_period)
    duration_to_period = duration / max_period
    bck_flux_detrend = detrend(time_values, lc.background_flux.value, duration_to_period * 4, smooth=False)
    lc_df['bck_flux'] = np.concatenate((padding_ones_left, bck_flux_detrend, padding_ones_right))
    flux_err_values = np.array(lc.flux_err.value) / median_flux
    lc_df['#time'] = np.concatenate((padding_zeros_left, np.array(lc.time.value), padding_zeros_right))
    lc_df['flux'] = np.concatenate((padding_ones_left, flux_values, padding_ones_right))
    lc_df['flux_err'] = np.concatenate((padding_zeros_left, flux_err_values, padding_zeros_right))
    lc_df['centroid_x'] = np.concatenate((padding_zeros_left, np.array(lc.centroid_col.value), padding_zeros_right))
    lc_df['centroid_y'] = np.concatenate((padding_zeros_left, np.array(lc.centroid_row.value), padding_zeros_right))
    lc_df['motion_x'] = np.concatenate((padding_zeros_left, np.array(lc.mom_centr1.value), padding_zeros_right))
    lc_df['motion_y'] = np.concatenate((padding_zeros_left, np.array(lc.mom_centr2.value), padding_zeros_right))
    lc_df['planet_model'] = np.concatenate((padding_ones_left, np.array(planet_model_flux), padding_ones_right))
    lc_df = lc_df.fillna(0)
    lc_df.to_csv(lcs_dir + '/' + mission_id + '_' + str(object_id) + '_injected_lc.csv')


def resample_model(model, lc_time):
    total_missing_points = len(model) - len(lc_time)
    gaps_sizes = []
    time_gaps_indexes = np.argwhere(np.abs(lc_time[1:] - lc_time[:-1]) > 0.014).flatten()
    for time_gap_index in time_gaps_indexes:
        gaps_sizes = gaps_sizes + [lc_time[time_gap_index + 1] - lc_time[time_gap_index]]
    total_gap_size = np.sum(gaps_sizes)
    gap_sizes_percent = [gap_size / total_gap_size for gap_size in gaps_sizes]
    gap_points = []
    for gap_size_percent in gap_sizes_percent[:-1]:
        gap_points = gap_points + [int(np.round(total_missing_points * gap_size_percent))]
    gap_points = gap_points + [total_missing_points - np.sum(gap_points)]
    added_gap_points = 0
    i = 0
    corrected_time_gap_indexes = np.array([])
    for time_gap_index in time_gaps_indexes:
        corrected_time_gap_index = time_gap_index + added_gap_points
        corrected_time_gap_indexes = np.concatenate((corrected_time_gap_indexes, np.arange(corrected_time_gap_index + 1, corrected_time_gap_index + 1 + gap_points[i])))
        added_gap_points = gap_points[i]
        i = i + 1
    model = np.delete(model, corrected_time_gap_indexes.astype(int))
    return model


def uncompress_data(data_dir):
    for file in os.listdir(data_dir):
        original_file_name = data_dir + '/' + file
        destination_file_name = file.split('.')[0]
        destination_file_name = data_dir + '/' + destination_file_name + '.txt'
        with gzip.open(original_file_name, 'rb') as f_in:
            with open(destination_file_name, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
