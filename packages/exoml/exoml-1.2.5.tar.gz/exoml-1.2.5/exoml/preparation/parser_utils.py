import glob
import logging
import multiprocessing
import os
import sys
import pathlib
import re
from itertools import chain
from multiprocessing import Pool

import gzip
import shutil
import lcbuilder.constants
#import triceratops.triceratops as tr
import astropy.units as u
import foldedleastsquares
import lightkurve
import numpy as np
import wotan
import pandas as pd
from lcbuilder import constants
from astropy.coordinates import SkyCoord
from astropy.wcs import WCS
from astroquery.mast import Catalogs, TesscutClass
from lcbuilder.helper import LcbuilderHelper
from lcbuilder.lcbuilder_class import LcBuilder
from lcbuilder.objectinfo.MissionInputObjectInfo import MissionInputObjectInfo
from lcbuilder.objectinfo.MissionObjectInfo import MissionObjectInfo
from lcbuilder.objectinfo.preparer.MissionInputLightcurveBuilder import MissionInputLightcurveBuilder
from lcbuilder.objectinfo.preparer.MissionLightcurveBuilder import MissionLightcurveBuilder
from lcbuilder.photometry.aperture_extractor import ApertureExtractor
from lcbuilder.star.HabitabilityCalculator import HabitabilityCalculator
from lcbuilder.star.starinfo import StarInfo
from lightkurve import TessLightCurve, KeplerLightCurve, LightCurveCollection
from uncertainties import ufloat
from watson.watson import Watson


def detrend(time_array, flux_array, detrend_window, time_threshold=0.0001, smooth=True, smooth_window_len=11,
            window='blackman'):
    flux_without_zeros = flux_array[time_array > time_threshold]
    time_without_zeros = time_array[time_array > time_threshold]
    if smooth:
        if window not in ['flat', 'hanning', 'hamming', 'bartlett', 'blackman']:
            raise ValueError("Window is on of 'flat', 'hanning', 'hamming', 'bartlett', 'blackman'")
        s = np.r_[np.ones(smooth_window_len // 2), flux_without_zeros, np.ones(smooth_window_len // 2)]
        # print(len(s))
        if smooth_window_len >= 3:
            if window == 'flat':  # moving average
                w = np.ones(smooth_window_len, 'd')
            else:
                w = eval('np.' + window + '(smooth_window_len)')
            flux_without_zeros = np.convolve(w / w.sum(), s, mode='valid')
    flux_without_zeros = np.nan_to_num(wotan.flatten(time_without_zeros, flux_without_zeros, detrend_window,
                                                     method="biweight"))
    flux_array[time_array > time_threshold] = flux_without_zeros
    return flux_array


class CreateStarCsvInput:
    def __init__(self, object_id, pixel_size, search_radius, star_catalog, output_dir, force) -> None:
        super().__init__()
        self.object_id = object_id
        self.search_radius = search_radius
        self.pixel_size = pixel_size * u.arcsec
        self.star_catalog = star_catalog
        self.output_dir = output_dir
        self.force = force

def create_star_csvs(lcs_dir, search_radius, pixel_size, star_catalog, csv,
                     cores=os.cpu_count() - 1, ids=None, force=False):
    tces_df = pd.read_csv(csv, comment='#')
    tces_df = tces_df.sort_values(by=["object_id"], ascending=True)
    tces_df = tces_df.drop_duplicates(subset=["object_id"], keep='last')
    tces_df = tces_df.sample(frac=1).reset_index(drop=True)
    print("Total number of targets is " + str(len(tces_df)))
    create_star_inputs = []
    if ids is not None:
        tces_df = tces_df[tces_df['object_id'].isin(ids)]
    for index, tce_row in tces_df.iterrows():
        create_star_inputs = create_star_inputs + [CreateStarCsvInput(tce_row['object_id'], pixel_size,
                                                                      search_radius, star_catalog, lcs_dir,
                                                                      force)]
    with Pool(processes=cores, maxtasksperchild=1) as pool:
        pool.map(create_star_csv, create_star_inputs, chunksize=1)

def create_star_csv(create_star_input):
    tries = 0
    star_file = create_star_input.output_dir + '/' + create_star_input.object_id + '_star.csv'
    mission, mission_prefix, mission_id = LcBuilder().parse_object_info(create_star_input.object_id)
    if not os.path.exists(star_file) or create_star_input.force:
        while tries < 3:
            try:
                star_info = create_star_input.star_catalog.catalog_info(mission_id)
                star_df = pd.DataFrame(
                    columns=['id', 'ra', 'dec', 'ld_a', 'ld_b', 'Teff', 'lum', 'logg', 'radius', 'mass', 'v', 'j', 'h',
                             'k',
                             'dist_arcsec'])
                star_df = pd.concat([star_df, pd.DataFrame.from_dict({'id': [create_star_input.object_id], 'ra': [star_info[11]], 'dec': [star_info[12]],
                                          'ld_a': [star_info[0][0]],
                                          'ld_b': [star_info[0][1]], 'Teff': [star_info[1]],
                                          'lum': [star_info[2]], 'logg': [star_info[3]], 'radius': [star_info[5]],
                                          'mass': [star_info[8]], 'v': [star_info[13]], 'j': [star_info[15]],
                                          'h': [star_info[17]],
                                          'k': [star_info[19]], 'dist_arcsec': [0]}, orient='columns')], ignore_index=True)
                break
            except Exception as e:
                logging.exception("Failed object %s try", create_star_input.object_id)
                tries = tries + 1
        if tries >= 3:
            print("Failed downloading object id " + str(create_star_input.object_id))
        assert tries < 3
        try:  # Acquiring neighbours parameters
            ra = star_df['ra'].iloc[0]
            dec = star_df['dec'].iloc[0]
            if ra is not None and dec is not None:
                ticid = Catalogs.query_region(
                    SkyCoord(ra, dec, unit="deg"),
                    radius=(create_star_input.search_radius * (create_star_input.pixel_size / 3600)) * u.deg,
                    catalog="TIC"
                )[0]["ID"]
            df = Catalogs.query_object(
                "TIC" + str(ticid),
                radius=(create_star_input.search_radius * (create_star_input.pixel_size / 3600)) * u.deg,
                catalog="TIC"
            )
            stars = df.to_pandas()
            sep = [0]
            pa = [0]
            c_target = SkyCoord(
                stars["ra"].values[0],
                stars["dec"].values[0],
                unit="deg"
            )
            for i in range(1, len(stars)):
                c_star = SkyCoord(
                    stars["ra"].values[i],
                    stars["dec"].values[i],
                    unit="deg"
                )
                sep.append(
                    np.round(
                        c_target.separation(c_star).to(u.arcsec).value,
                        3
                    )
                )
                pa.append(
                    np.round(
                        c_target.position_angle(c_star).to(u.deg).value,
                        3
                    )
                )
            stars["dist_arcsec"] = sep
            stars["PA (E of N)"] = pa  # TODO should we use this?
            for index, star in stars.iterrows():
                star_df = pd.concat([star_df, pd.DataFrame.from_dict({'id': [star['ID']], 'ra': [star['ra']], 'dec': [star['dec']], 'ld_a': [0],
                                          'ld_b': [0], 'Teff': [star['Teff']],
                                          'lum': [star['lum']], 'logg': [star['logg']], 'radius': [star['rad']],
                                          'mass': [star['mass']], 'v': [star['Vmag']], 'j': [star['Jmag']],
                                          'h': [star['Hmag']],
                                          'k': [star['Kmag']], 'dist_arcsec': [star['dist_arcsec']]}, orient='columns')], ignore_index=True)
            star_df = star_df.sort_values(["dist_arcsec"], ascending=True)
        except Exception as e:
            logging.exception('Something failed when retrieving neighbours info for object id %s',
                              str(create_star_input.object_id))
        star_df.to_csv(star_file)
    logging.info('Processed object id ' + str(create_star_input.object_id))

def prepare_lc_data(file_prefix, object_id, lc_data, transit_duration, transit_period, epoch, ra, dec, star_info: StarInfo,
                    authors: list[str], cadences: list[int], cadence_name, tpf_files=None, modes=['all'], sectors='all'):
    lc_df = None
    if 'quality' in lc_data.columns:
        lc_data = lc_data.drop(['quality'], axis=1)
    lc_data = lc_data.loc[~lc_data['flux'].isna()]
    lcbuilder = LcBuilder()
    mission, mission_prefix, id = lcbuilder.parse_object_info(object_id)
    if tpf_files is None:
        tpfs = lightkurve.search_targetpixelfile(object_id, sector=sectors if isinstance(sectors, list) else None,
                                                 campaign=sectors if isinstance(sectors, list)  else None,
                                                 quarter=sectors if isinstance(sectors, list)  else None,
                                                 exptime=cadences, author=authors).download_all()
    else:
        tpfs = []
        for file in tpf_files:
            tpfs.append(lightkurve.TessTargetPixelFile(file, ignore_missing_simple=True))
    lc_filename = str(file_prefix) + '_lc_' + str(cadence_name) + '.csv'
    transit_duration = transit_duration if transit_duration < transit_period else transit_period / 2
    duration_to_period = transit_duration / transit_period
    if 'all' in modes or 'lc' in modes:
        lc_df = pd.DataFrame(columns=['#time', 'flux', 'flux_err', 'planet_model', 'eb_model', 'bckeb_model',
                                      'centroid_x', 'centroid_y', 'motion_x', 'motion_y', 'bck_flux'])
        flux_values = np.array(lc_data.flux)
        # Normalizing PDCSAP flux, but not using the normalization for detrending
        median_flux = np.nanmedian(flux_values)
        flux_values = flux_values / median_flux
        if len(np.argwhere(flux_values < 0).flatten()) > 0:
            flux_values = np.array(lc_data.flux)
            flux_values = flux_values + 2 * np.abs(np.nanmin(flux_values))
            median_flux = np.nanmedian(flux_values)
            flux_values = flux_values / median_flux
        time_values = np.array(lc_data.time)
        series_len = len(time_values)
        median_cadence = LcbuilderHelper.compute_cadence(time_values) / 3600 / 24
        for j in np.arange(0, 1, 1):
            detrend_window = transit_duration * (4 + j)
            logging.info("Detrending no %s for target %s with %s points with duration %s", j, object_id, series_len, detrend_window)
            if detrend_window > median_cadence * 2:
                flux_detrend_j = detrend(time_values, np.array(lc_data.flux), detrend_window, smooth=False)
            else:
                flux_detrend_j = np.array(lc_data.flux)
            lc_df['flux_' + str(j)] = flux_detrend_j
        logging.info("Detrending bck for target %s with %s points with duration %s", object_id, series_len, transit_duration * 4)
        bck_flux_detrended = np.array(lc_data.background_flux)
        bck_flux_detrend = detrend(time_values, bck_flux_detrended, transit_duration * 4, smooth=False)
        logging.info("Finished detrending for target %s with %s points", object_id, series_len)
        lc_df['bck_flux'] = bck_flux_detrend
        flux_err_values = np.array(lc_data.flux_err) / flux_values
        lc_df['#time'] = time_values
        lc_df['flux'] = flux_values
        lc_df['flux_err'] = flux_err_values
        lc_df['centroid_x'] = np.array(lc_data.centroids_x)
        lc_df['centroid_y'] = np.array(lc_data.centroids_y)
        lc_df['motion_x'] = np.array(lc_data.motion_x)
        lc_df['motion_y'] = np.array(lc_data.motion_y)
        lc_df = lc_df.fillna(0)
        lc_df.to_csv(lc_filename)
    logging.info("Computing T0s for %s", object_id)
    t0s_list = LcbuilderHelper.compute_t0s(lc_data['time'].to_numpy(), transit_period, epoch, transit_duration)
    source_offsets_diffimg = []
    source_offsets_bls = []
    centroids_offsets_ra_list = []
    centroids_offsets_dec_list = []
    centroids_offsets_time_list = []
    og_time_list = []
    og_core_flux_list = []
    og_halo_flux_list = []
    logging.info("Computing TPFs data for %s", object_id)
    if tpfs is not None:
        for tpf in tpfs:
            sector_name, sector = LcbuilderHelper.mission_lightkurve_sector_extraction(mission, tpf)
            logging.info("Computing TPF data for %s sector %s", object_id, sector)
            aperture = tpf.pipeline_mask
            cadence_s = np.round(np.nanmedian(tpf.time.value[1:] - tpf.time.value[:-1]) * 3600 * 24)
            cadences_per_transit = LcbuilderHelper.estimate_transit_cadences(cadence_s, transit_duration * 2)
            t0s_in_tpf_indexes = np.argwhere((t0s_list > tpf.time.value[0] - transit_duration) &
                                             (t0s_list < tpf.time.value[-1] + transit_duration)).flatten()
            if len(t0s_in_tpf_indexes) == 0:
                continue
            tpf_t0s_list = t0s_list[t0s_in_tpf_indexes]
            good_quality_t0s = []
            for t0 in tpf_t0s_list:
                t0_in_tpf_indexes = \
                    np.argwhere((tpf.time.value > t0 - transit_duration) & (tpf.time.value < t0 + transit_duration)).flatten()
                cadences_ratio = len(t0_in_tpf_indexes) / cadences_per_transit
                if cadences_ratio >= 0.75:
                    good_quality_t0s.append(t0)
                else:
                    try:
                        tpf = tpf[(tpf.time.value < t0 - transit_duration) | (tpf.time.value > t0 + transit_duration)]
                        trash = tpf[0] #we try to make it crash and if so, we discard the TPF
                    except:
                        logging.exception("TPF filtering error for %s and T0 %.02f", object_id, t0)
                        continue
            if len(good_quality_t0s) == 0:
                continue
            hdu = tpf.hdu[2].header
            wcs = WCS(hdu)
            if 'all' in modes or 'centroids' in modes:
                logging.info("Computing TPF data centroids for %s sector %s", object_id, sector)
                centroids_drift = \
                    Watson.compute_centroids_for_tpf(ra, dec, lc_data, tpf, wcs, transit_period, epoch, duration_to_period)
                centroids_offsets_time_list.append(centroids_drift[0])
                centroids_offsets_ra_list.append(centroids_drift[1])
                centroids_offsets_dec_list.append(centroids_drift[2])
            if 'all' in modes or 'og' in modes:
                logging.info("Computing TPF data og for %s sector %s", object_id, sector)
                optical_ghost_data = Watson.compute_optical_ghost_data(tpf, aperture, transit_period, epoch, transit_duration)
                og_time_list.append(optical_ghost_data[0])
                og_core_flux_list.append(optical_ghost_data[1])
                og_halo_flux_list.append(optical_ghost_data[2])
            if 'all' in modes or 'source_offset' in modes:
                pixel_values_i = np.array(range(tpf.shape[1]))
                pixel_values_j = np.array(range(tpf.shape[2]))
                logging.info("Computing TPF data per-pixel BLS for %s sector %s", object_id, sector)
                snr_map, ax = Watson.plot_pixels(tpf, title=mission_prefix + ' ' + str(id) + ' ' + sector_name + ' ' + str(sector) + ' TPF BLS Analysis',
                                                 period=transit_period, epoch=epoch, duration=transit_duration, aperture_mask=aperture, dry=True)
                source_offset_px = Watson.light_centroid(snr_map, pixel_values_i, pixel_values_j)
                source_offset_bls = wcs.pixel_to_world(source_offset_px[1], source_offset_px[0])
                source_offsets_bls.append((source_offset_bls.ra.value, source_offset_bls.dec.value))
                logging.info("Computing TPF data differential image for %s sector %s", object_id, sector)
                tpf_sub = Watson.compute_tpf_diff_image(tpf, transit_period, epoch, transit_duration)
                source_offset_diffimg_px = Watson.light_centroid(tpf_sub, pixel_values_i, pixel_values_j)
                source_offset_diffimg = wcs.pixel_to_world(source_offset_diffimg_px[1], source_offset_diffimg_px[0])
                source_offsets_diffimg.append((source_offset_diffimg.ra.value, source_offset_diffimg.dec.value))
        if 'all' in modes or 'og' in modes:
            og_df = pd.DataFrame(columns=['time', 'core_flux', 'halo_flux', 'og_flux'])
            og_df['time'] = list(chain.from_iterable(og_time_list))
            og_df['core_flux'] = list(chain.from_iterable(og_core_flux_list))
            og_df['halo_flux'] = list(chain.from_iterable(og_halo_flux_list))
            og_df['og_flux'] = og_df['halo_flux'] - og_df['core_flux']
            og_df.fillna(1, inplace=True)
            og_df.to_csv(file_prefix + '_og_' + str(cadence_name) + '.csv')
        if 'all' in modes or 'centroids' in modes:
            centroid_coords_df = pd.DataFrame(columns=['time', 'centroids_ra', 'centroids_dec'])
            centroid_coords_df['centroids_ra'] = list(chain.from_iterable(centroids_offsets_ra_list))
            centroid_coords_df['centroids_dec'] = list(chain.from_iterable(centroids_offsets_dec_list))
            centroid_coords_df['time'] = list(chain.from_iterable(centroids_offsets_time_list))
            centroid_coords_df.fillna(0, inplace=True)
            centroid_coords_df.to_csv(file_prefix + '_cent_' + str(cadence_name) + '.csv')
        if 'all' in modes or 'source_offset' in modes:
            if len(source_offsets_diffimg) > 0:
                source_offset_diffimg_ra = np.nanmedian(np.array(source_offsets_diffimg)[:, 0])
                source_offset_diffimg_dec = np.nanmedian(np.array(source_offsets_diffimg)[:, 1])
                source_offset_diffimg_ra_err = np.nanstd(np.array(source_offsets_diffimg)[:, 0])
                source_offset_diffimg_dec_err = np.nanstd(np.array(source_offsets_diffimg)[:, 1])
            else:
                source_offset_diffimg_ra = ra
                source_offset_diffimg_dec = dec
                source_offset_diffimg_ra_err = 0
                source_offset_diffimg_dec_err = 0
            if len(source_offsets_bls) > 0:
                source_offset_bls_ra = np.nanmedian(np.array(source_offsets_bls)[:, 0])
                source_offset_bls_dec = np.nanmedian(np.array(source_offsets_bls)[:, 1])
                source_offset_bls_ra_err = np.nanstd(np.array(source_offsets_bls)[:, 0])
                source_offset_bls_dec_err = np.nanstd(np.array(source_offsets_bls)[:, 1])
            else:
                source_offset_bls_ra = ra
                source_offset_bls_dec = dec
                source_offset_bls_ra_err = 0
                source_offset_bls_dec_err = 0
            offset_ra = np.mean([source_offset_bls_ra, source_offset_diffimg_ra])
            offset_dec = np.mean([source_offset_bls_dec, source_offset_diffimg_dec])
            offset_ra_err = 1/2 * np.sqrt(source_offset_bls_ra_err ** 2 + source_offset_diffimg_ra_err ** 2)
            offset_dec_err = 1/2 * np.sqrt(source_offset_bls_dec_err ** 2 + source_offset_diffimg_dec_err ** 2)
            if np.isnan(offset_ra_err) or offset_ra_err == 0.0:
                offset_ra_err = np.nanstd([source_offset_bls_ra, source_offset_diffimg_ra])
            if np.isnan(offset_dec_err) or offset_dec_err == 0.0:
                offset_dec_err = np.nanstd([source_offset_bls_dec, source_offset_diffimg_dec])
            offsets_df = pd.DataFrame(columns=['name', 'ra', 'dec', 'ra_err', 'dec_err'])
            offsets_df = offsets_df.append({'name': 'diff_img', 'ra': source_offset_diffimg_ra, 'dec': source_offset_diffimg_dec,
                               'ra_err': source_offset_diffimg_ra_err, 'dec_err': source_offset_diffimg_dec_err}, ignore_index=True)
            offsets_df = offsets_df.append({'name': 'px_bls', 'ra': source_offset_bls_ra, 'dec': source_offset_bls_dec,
                               'ra_err': source_offset_bls_ra_err, 'dec_err': source_offset_bls_dec_err}, ignore_index=True)
            offsets_df = offsets_df.append({'name': 'mean', 'ra': offset_ra, 'dec': offset_dec,
                               'ra_err': offset_ra_err, 'dec_err': offset_dec_err}, ignore_index=True)
            offsets_df.to_csv(file_prefix + '_offset_' + str(cadence_name) + '.csv')
    if 'all' in modes or 'metrics' in modes:
        logging.info("Computing bootstrap fap for %s", object_id)
        if lc_df is None:
            lc_df = pd.read_csv(lc_filename)
        if np.isnan(star_info.mass):
            star_info.mass = 1
        if np.isnan(star_info.mass_min):
            star_info.mass_min = star_info.mass - star_info.mass / 100
        if np.isnan(star_info.mass_max):
            star_info.mass_max = star_info.mass + star_info.mass / 100
        if np.isnan(star_info.radius):
            star_info.radius = 1
        if np.isnan(star_info.radius_min):
            star_info.radius_min = star_info.radius - star_info.radius / 100
        if np.isnan(star_info.radius_max):
            star_info.radius_max = star_info.radius + star_info.radius / 100
        if np.isnan(star_info.teff):
            star_info.teff = 6000
        lc_df = lc_df.loc[(~lc_df['flux_0'].isna()) & (lc_df['flux_0'] > 0)]
        bootstrap_fap = Watson.compute_bootstrap_fap(lc_df['#time'].to_numpy(), lc_df['flux_0'].to_numpy(), transit_period, transit_duration, star_info, flux_err=None)
        logging.info("Computing metrics for %s", object_id)
        lc_df['time_folded'] = foldedleastsquares.fold(lc_df['#time'].to_numpy(), transit_period, epoch + transit_period / 2)
        lc_df['time_folded_sec'] = foldedleastsquares.fold(lc_df['#time'].to_numpy(), transit_period, epoch)
        lc_df_it = lc_df[(lc_df['time_folded'] > 0.5 - duration_to_period / 2) & (lc_df['time_folded'] < 0.5 + duration_to_period / 2)]
        lc_df_it = lc_df_it.sort_values(by=['time_folded'])
        lc_df_secit = lc_df[(lc_df['time_folded_sec'] > 0.5 - duration_to_period / 2) & (lc_df['time_folded_sec'] < 0.5 + duration_to_period / 2)]
        lc_df_secit = lc_df_secit.sort_values(by=['time_folded_sec'])
        sec_depth = 1 - lc_df_secit['flux_0'].dropna().median()
        sec_depth_err = lc_df_secit['flux_0'].dropna().std()
        depth = 1 - lc_df_it['flux_0'].dropna().median()
        depth_err = lc_df_it['flux_0'].dropna().std()
        if depth <= 0:
            depth = 1 - lc_df_it['flux_0'].dropna().min()
        if sec_depth <= 0:
            sec_depth = 1 - lc_df_secit['flux_0'].dropna().min()
        rad_p = (ufloat(depth, depth_err) * (ufloat(star_info.radius, np.nanmax([star_info.radius - star_info.radius_min, star_info.radius_max - star_info.radius])) ** 2)) ** 0.5
        rp = rad_p.n
        rp_err = rad_p.s
        rp = LcbuilderHelper.convert_from_to(rp, u.R_sun, u.R_earth)
        habitability_calculator = HabitabilityCalculator()
        planet_eq_temp, planet_eq_temp_low_err, planet_eq_temp_up_err = (
            habitability_calculator.calculate_teq(star_info.mass, star_info.mass - star_info.mass_min, star_info.mass_max - star_info.mass,
                                                  star_info.radius, star_info.radius - star_info.radius_min, star_info.radius_max - star_info.radius,
                                                  transit_period, 0.0001, 0.0001, star_info.teff, star_info.teff / 100, star_info.teff / 100,
                                                  albedo=0.3))
        planet_eff_temp, planet_eff_temp_low_err, planet_eff_temp_up_err = (
            habitability_calculator.calculate_teff(star_info.teff, star_info.teff / 100, star_info.teff / 100,
                                                   sec_depth, sec_depth_err, sec_depth_err, depth, depth_err, depth_err))
        albedo, albedo_low_err, albedo_up_err = (
            habitability_calculator.calculate_albedo(sec_depth, sec_depth_err, sec_depth_err,
                                                     transit_period, 0.0001, 0.0001,
                                                     star_info.mass, star_info.mass - star_info.mass_min, star_info.mass_max - star_info.mass,
                                                     rp, rp_err, rp_err))
        temp_stat = habitability_calculator.calculate_planet_temperature_stat(
            planet_eq_temp, planet_eq_temp_low_err, planet_eq_temp_up_err,
            planet_eff_temp, planet_eff_temp_low_err, planet_eff_temp_up_err
        )
        albedo_stat = habitability_calculator.calculate_albedo_stat(albedo, albedo_low_err, albedo_up_err)
        statistics_df = pd.DataFrame(columns=['name', 'value'])
        statistics_df = pd.concat([statistics_df, pd.DataFrame.from_dict({'name': ['depth'], 'value': [depth]}, orient='columns')], ignore_index=True)
        statistics_df = pd.concat([statistics_df, pd.DataFrame.from_dict({'name': ['depth_err'], 'value': [depth_err]}, orient='columns')], ignore_index=True)
        statistics_df = pd.concat([statistics_df, pd.DataFrame.from_dict({'name': ['bootstrap_fap'], 'value': [bootstrap_fap]}, orient='columns')], ignore_index=True)
        statistics_df = pd.concat([statistics_df, pd.DataFrame.from_dict({'name': ['sec_depth'], 'value': [sec_depth]}, orient='columns')], ignore_index=True)
        statistics_df = pd.concat([statistics_df, pd.DataFrame.from_dict({'name': ['sec_depth_err'], 'value': [sec_depth_err]}, orient='columns')], ignore_index=True)
        statistics_df = pd.concat([statistics_df, pd.DataFrame.from_dict({'name': ['teff'], 'value': [planet_eff_temp]}, orient='columns')], ignore_index=True)
        statistics_df = pd.concat([statistics_df, pd.DataFrame.from_dict({'name': ['teff_err'], 'value': [np.nanmax([planet_eff_temp_low_err, planet_eff_temp_up_err])]}, orient='columns')], ignore_index=True)
        statistics_df = pd.concat([statistics_df, pd.DataFrame.from_dict({'name': ['teq'], 'value': [planet_eq_temp]}, orient='columns')], ignore_index=True)
        statistics_df = pd.concat([statistics_df, pd.DataFrame.from_dict({'name': ['teq_err'], 'value': [np.nanmax([planet_eq_temp_low_err, planet_eq_temp_up_err])]}, orient='columns')], ignore_index=True)
        statistics_df = pd.concat([statistics_df, pd.DataFrame.from_dict({'name': ['temp_stat'], 'value': [temp_stat]}, orient='columns')], ignore_index=True)
        statistics_df = pd.concat([statistics_df, pd.DataFrame.from_dict({'name': ['geom_albedo'], 'value': [albedo]}, orient='columns')], ignore_index=True)
        statistics_df = pd.concat([statistics_df, pd.DataFrame.from_dict({'name': ['geom_albedo_err'], 'value': [np.nanmax([albedo_low_err, albedo_up_err])]}, orient='columns')], ignore_index=True)
        statistics_df = pd.concat([statistics_df, pd.DataFrame.from_dict({'name': ['albedo_stat'], 'value': [albedo_stat]}, orient='columns')], ignore_index=True)
        statistics_df.to_csv(file_prefix + '_metrics_' + str(cadence_name) + '.csv')
    return lc_df

class CreateTargetInput:
    def __init__(self, mission, id, lc_file, target_dir, models_dir, injected_files_df, cache_dir, index,
                 max_lc_length=20610, force=False, tpf_files=None, inject_random=False, mode='all') -> None:
        super().__init__()
        self.mission = mission
        self.id = id
        self.lc_file = lc_file
        self.target_dir = target_dir
        self.models_dir = models_dir
        self.injected_files_df = injected_files_df
        self.max_lc_length = max_lc_length
        self.cache_dir = cache_dir
        self.index = index
        self.force = force
        self.tpf_files = tpf_files
        self.inject_random = inject_random
        self.mode = mode

def create_target_csv(create_target_input):
    mission_lightcurve_builder = MissionLightcurveBuilder()
    mission_input_lightcurve_builder = MissionInputLightcurveBuilder()
    mission_id = create_target_input.id
    file_id = mission_id.replace(' ', '_')
    file_prefix = create_target_input.target_dir + file_id
    file_planet_prefix = file_prefix + '_' + \
                         str(round(create_target_input.injected_files_df['period'], 2))
    pid = multiprocessing.current_process().pid
    tpfs_dir = create_target_input.target_dir + 'tpfs/'
    sectors = 'all'
    if 'Sectors' in create_target_input.injected_files_df:
        sectors = [int(item) for item in create_target_input.injected_files_df['Sectors'].split(",")]
    elif 'sectors' in create_target_input.injected_files_df:
        sectors = [int(create_target_input.injected_files_df['sectors'])] if create_target_input.injected_files_df['sectors'].isdigit() else 'all'
    try:
        logging.info("PID %s: Trying to get short cadence info for %s", pid, file_planet_prefix)
        file_name = file_planet_prefix + '_metrics_short.csv'
        authors = [constants.KEPLER_AUTHOR] if mission_id.startswith('KIC') else [constants.SPOC_AUTHOR]
        cadences = [60] if mission_id.startswith('KIC') else [120]
        if create_target_input.force or not os.path.exists(file_name):
            if create_target_input.lc_file is None:
                lcbuild_short = \
                    mission_lightcurve_builder.build(MissionObjectInfo(sectors,
                                                                       mission_id, author=authors,
                                                                       cadence=cadences,
                                                                       high_rms_enabled=False),
                                                                       create_target_input.target_dir,
                                                                       create_target_input.cache_dir)
                if os.path.exists(tpfs_dir):
                    for f in glob.glob(tpfs_dir + f"*{mission_id}*.fits"):
                        os.remove(f)
            else:
                if isinstance(create_target_input.lc_file, (list, np.ndarray)):
                    lc = None
                    for file in create_target_input.lc_file:
                        if lc is None:
                            lc = KeplerLightCurve.read(file)
                            csv_filename = os.path.splitext(file)[0] + '.csv'
                        else:
                            lc.append(KeplerLightCurve.read(file))
                else:
                    lc = KeplerLightCurve.read(create_target_input.lc_file)
                    csv_filename = os.path.splitext(create_target_input.lc_file)[0] + '.csv'
                lc_data = mission_input_lightcurve_builder.extract_lc_data(LightCurveCollection([lc]))
                lc_data['#time'] = lc_data['time']
                lc_data.to_csv(csv_filename, index=False)
                lcbuild_short = \
                    mission_input_lightcurve_builder.build(
                        MissionInputObjectInfo(mission_id, input_file=csv_filename, high_rms_enabled=False),
                        create_target_input.target_dir,
                        create_target_input.cache_dir)
            prepare_lc_data(file_planet_prefix, mission_id, lcbuild_short.lc_data,
                            create_target_input.injected_files_df['duration(h)'] / 24,
                            create_target_input.injected_files_df['period'],
                            create_target_input.injected_files_df['epoch'],
                            lcbuild_short.star_info.ra, lcbuild_short.star_info.dec, lcbuild_short.star_info,
                            sectors=sectors, authors=authors, cadences=cadences, cadence_name='short',
                            modes=create_target_input.mode)
            for f in pathlib.Path(tpfs_dir).glob(f"*{file_id.split('_')[1]}*"):
                os.remove(f)
        logging.info("PID %s: Finished to get short cadence info for %s", pid, file_planet_prefix)
    except Exception as e:
        logging.exception("PID %s: Failed short cadence for %s", pid, file_planet_prefix)
    logging.info(f"lc file is {create_target_input.lc_file}")
    if create_target_input.lc_file is None:
        authors = [constants.KEPLER_AUTHOR] if mission_id.startswith('KIC') else [constants.SPOC_AUTHOR, constants.TESS_SPOC_AUTHOR, 'QLP']
        cadences = [1800] if mission_id.startswith('KIC') else [200, 600, 1800]
        try:
            logging.info("PID %s: Trying to get long cadence info for %s", pid, file_planet_prefix)
            file_name = file_planet_prefix + '_metrics_long.csv'
            if create_target_input.force or not os.path.exists(file_name):
                lcbuild_long = \
                    mission_lightcurve_builder.build(MissionObjectInfo(sectors,
                                            mission_id, author=authors, cadence=cadences, high_rms_enabled=False),
                                            create_target_input.target_dir, create_target_input.cache_dir)
                prepare_lc_data(file_planet_prefix, mission_id, lcbuild_long.lc_data,
                                create_target_input.injected_files_df['duration(h)'] / 24,
                                create_target_input.injected_files_df['period'],
                                create_target_input.injected_files_df['epoch'],
                                lcbuild_long.star_info.ra, lcbuild_long.star_info.dec, lcbuild_long.star_info,
                                sectors=sectors, authors=authors, cadences=cadences, cadence_name='long',
                                modes=create_target_input.mode)
                for f in pathlib.Path(tpfs_dir).glob(f"*{file_id.split('_')[1]}*"):
                    os.remove(f)
            logging.info("PID %s: Finished to get long cadence info for index %s for file %s", pid,
                         create_target_input.index, file_planet_prefix)
        except Exception as e:
            logging.exception("PID %s: Failed long cadence for %s", pid, file_planet_prefix)

def create_triceratops_prob(create_target_input):
    object_id = create_target_input.id
    file_id = object_id.replace(' ', '_')
    file_prefix = create_target_input.target_dir + file_id
    file_planet_prefix = file_prefix + '_' + \
                         str(round(create_target_input.injected_files_df['period'], 2))
    logging.exception(f"Trying triceratops for target {file_planet_prefix}")
    triceratops_file = file_planet_prefix + '_triceratops.csv'
    if os.path.exists(triceratops_file) and not create_target_input.force:
        return
    try:
        period = create_target_input.injected_files_df['period']
        duration = create_target_input.injected_files_df['duration(h)']
        epoch = create_target_input.injected_files_df['epoch']
        depth = create_target_input.injected_files_df['depth'] / 1e6
        mission, mission_prefix, id_int = LcBuilder().parse_object_info(object_id)
        apertures = {}
        lc_short_filename = str(file_prefix) + '_lc_short.csv'
        lc_long_filename = str(file_prefix) + '_lc_long.csv'
        if create_target_input.tpf_files is None:
            if os.path.exists(lc_short_filename):
                tpfs = lightkurve.search_targetpixelfile(object_id, exptime="short", author=lcbuilder.constants.KEPLER_AUTHOR).download_all()
            elif os.path.exists(lc_long_filename):
                tpfs = lightkurve.search_targetpixelfile(object_id, exptime="long", author=lcbuilder.constants.KEPLER_AUTHOR).download_all()
        else:
            tpfs = []
            for file in create_target_input.tpf_files:
                tpfs.append(lightkurve.TessTargetPixelFile(file, ignore_missing_simple=True))
        sectors = []
        for tpf in tpfs:
            if mission_prefix == constants.MISSION_ID_KEPLER:
                sector = tpf.quarter
            elif mission_prefix == constants.MISSION_ID_TESS:
                sector = tpf.sector
            if mission_prefix == constants.MISSION_ID_KEPLER_2:
                sector = tpf.campaign
            sectors = sectors + [sector]
            apertures[sector] = ApertureExtractor.from_boolean_mask(tpf.pipeline_mask, tpf.column, tpf.row)
        sectors = np.array(sectors)
        logging.info(f"Will execute validation for sectors: {sectors}")
        lc_df = None
        if os.path.exists(lc_short_filename):
            lc_df = pd.read_csv(lc_short_filename, header=0)
        if os.path.exists(lc_long_filename):
            if lc_df is None:
                lc_df = pd.read_csv(lc_long_filename, header=0)
            else:
                lc_df = pd.concat([lc_df, pd.read_csv(lc_long_filename, header=0)])
        lc_df['time_folded'] = foldedleastsquares.core.fold(lc_df['#time'].to_numpy(), period, epoch + period / 2)
        range = 5
        bins = 200
        lc_df = lc_df.sort_values(by=['time_folded'], ascending=True)
        half_duration_phase = duration / 2 / period
        folded_plot_range = half_duration_phase * range
        folded_plot_range = folded_plot_range if folded_plot_range < 0.5 else 0.5
        lc_df = lc_df.loc[(lc_df['time_folded'] > 0.5 - folded_plot_range) &
                          (lc_df['time_folded'] < 0.5 + folded_plot_range)]
        bin_centers, bin_means, bin_width, bin_stds = \
            LcbuilderHelper.bin(lc_df['time_folded'].to_numpy(), lc_df['flux'].to_numpy(), bins,
                                values_err=lc_df['flux_err'].to_numpy(), bin_err_mode='values_snr')
        bin_centers = (bin_centers - 0.5) * period
        sigma = np.nanmean(bin_stds)
        logging.info("Flux err (ppm) = %s", sigma * 1000000)
        logging.info("Acquiring triceratops target")
        target = tr.target(ID=id_int, mission=mission, sectors=sectors)
        # TODO allow user input apertures
        logging.info("Reading apertures from directory")
        logging.info("Calculating validation closest stars depths")
        target.calc_depths(depth, apertures)
        logging.info("Preparing validation processes inputs")
        target.calc_probs(time=bin_centers, flux_0=bin_means, flux_err_0=sigma, P_orb=float(period),
                          contrast_curve_file=None, parallel=True)
        target.probs.to_csv(triceratops_file, index=False)
    except Exception as e:
        logging.exception(f"Failed triceratops for target {file_planet_prefix}")

    #input.target.probs
    # scenario  prob
    # group by scenario with sum of probs
    # FPP
    # NFPP
    # TP
    # EB
    # EBx2P
    # PTP
    # PEB
    # PEBx2P
    # STP
    # SEB
    # SEBx2P
    # DTP
    # DEB
    # DEBx2P
    # BTP
    # BEB
    # BEBx2P
    # NTP other stars
    # NEB other stars
    # NEBx2P other stars

    # input.target.plot_fits(save=True, fname=input.save_dir + "/scenario_" + str(input.run) + "_fits",
    #                        time=input.time, flux_0=input.flux, flux_err_0=input.sigma)
    # return input.target.FPP, input.target.NFPP, fpp2, fpp3, input.target.probs, input.target.star_num, \
    #     input.target.u1, input.target.u2, input.target.fluxratio_EB, input.target.fluxratio_comp
