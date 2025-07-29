import logging
import os
import pathlib
import re
import shutil
import sys
from multiprocessing import Pool

import foldedleastsquares
import sklearn
import wotan
from sshkeyboard import listen_keyboard, stop_listening
import keras
import pandas as pd
import lightkurve as lk
import foldedleastsquares as tls
import matplotlib.pyplot as plt
import astropy.units as u
import requests
from astropy.coordinates import SkyCoord
from astropy.wcs import WCS
from astroquery.mast import Catalogs, Tesscut
from keras import Sequential
from keras.layers import Conv1D, Dropout, MaxPooling1D, Flatten, Dense, Embedding, LSTM, ConvLSTM2D
from lightkurve import TessTargetPixelFile
from matplotlib.gridspec import GridSpec

from sherlockpipe.ois.OisManager import OisManager

from lcbuilder.objectinfo.MissionObjectInfo import MissionObjectInfo
from lcbuilder.objectinfo.preparer.MissionLightcurveBuilder import MissionLightcurveBuilder
from lcbuilder.eleanor import TargetData
from lcbuilder import eleanor
from lcbuilder.star.TicStarCatalog import TicStarCatalog
import numpy as np
# import tsfresh
# from tsfresh.utilities.dataframe_functions import impute

class PrepareTicInput:
    def __init__(self, dir, tic, target_ois, sector):
        self.dir = dir
        self.tic = tic
        self.target_ois = target_ois
        self.sector = sector

class EmptyTargetsPreparer:
    SECTOR_URL = "https://tess.mit.edu/wp-content/uploads/all_targets_S0{:02}_v1.csv"

    def __init__(self, dir, cache_dir):
        self.dir = dir
        if not os.path.exists(dir):
            os.mkdir(dir)
        file_dir = dir + "/ml.log"
        if os.path.exists(file_dir):
            os.remove(file_dir)
        formatter = logging.Formatter('%(message)s')
        logger = logging.getLogger()
        while len(logger.handlers) > 0:
            logger.handlers.pop()
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(logging.INFO)
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        handler = logging.FileHandler(file_dir)
        handler.setLevel(logging.INFO)
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        self.positive_dir = dir + "/tp/"
        self.negative_dir = dir + "/ntp/"
        self.false_positive_dir = dir + "/fp/"
        if not os.path.isdir(dir):
            os.mkdir(dir)
        if not os.path.isdir(self.positive_dir):
            os.mkdir(self.positive_dir)
        if not os.path.isdir(self.negative_dir):
            os.mkdir(self.negative_dir)
        if not os.path.isdir(self.false_positive_dir):
            os.mkdir(self.false_positive_dir)

    def download_neighbours(self, ID: int, sectors: np.ndarray, search_radius: int = 10):
        """
        Queries TIC for sources near the target and obtains a cutout
        of the pixels enclosing the target.
        Args:
            ID (int): TIC ID of the target.
            sectors (numpy array): Sectors in which the target
                                   has been observed.
            search_radius (int): Number of pixels from the target
                                 star to search.
        """
        ID = ID
        sectors = sectors
        search_radius = search_radius
        N_pix = 2 * search_radius + 2
        # query TIC for nearby stars
        pixel_size = 20.25 * u.arcsec
        df = Catalogs.query_object(
            str(ID),
            radius=search_radius * pixel_size,
            catalog="TIC"
        )
        new_df = df[
            "ID", "Tmag", "ra", "dec", "mass", "rad", "Teff", "plx"
        ]
        stars = new_df.to_pandas()

        TESS_images = []
        col0s, row0s = [], []
        pix_coords = []
        # for each sector, get FFI cutout and transform RA/Dec into
        # TESS pixel coordinates
        for j, sector in enumerate(sectors):
            Tmag = stars["Tmag"].values
            ra = stars["ra"].values
            dec = stars["dec"].values
            cutout_coord = SkyCoord(ra[0], dec[0], unit="deg")
            cutout_hdu = Tesscut.get_cutouts(cutout_coord, size=N_pix, sector=sector)[0]
            cutout_table = cutout_hdu[1].data
            hdu = cutout_hdu[2].header
            wcs = WCS(hdu)
            TESS_images.append(np.mean(cutout_table["FLUX"], axis=0))
            col0 = cutout_hdu[1].header["1CRV4P"]
            row0 = cutout_hdu[1].header["2CRV4P"]
            col0s.append(col0)
            row0s.append(row0)

            pix_coord = np.zeros([len(ra), 2])
            for i in range(len(ra)):
                RApix = np.asscalar(
                    wcs.all_world2pix(ra[i], dec[i], 0)[0]
                )
                Decpix = np.asscalar(
                    wcs.all_world2pix(ra[i], dec[i], 0)[1]
                )
                pix_coord[i, 0] = col0 + RApix
                pix_coord[i, 1] = row0 + Decpix
            pix_coords.append(pix_coord)

        # for each star, get the separation and position angle
        # from the targets star
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
                    c_star.separation(c_target).to(u.arcsec).value,
                    3
                )
            )
            pa.append(
                np.round(
                    c_star.position_angle(c_target).to(u.deg).value,
                    3
                )
            )
        stars["sep (arcsec)"] = sep
        stars["PA (E of N)"] = pa

        stars = stars
        TESS_images = TESS_images
        col0s = col0s
        row0s = row0s
        pix_coords = pix_coords
        return stars

    def store_lc_data(self, lc_data, file):
        # time = lc_data["time"].to_numpy()
        # dif = time[1:] - time[:-1]
        # jumps = np.where(np.abs(dif) > 0.5)[0]
        # jumps = np.append(jumps, len(lc_data))
        # previous_jump_index = 0
        # for jumpIndex in jumps:
        #     token = lc_data["centroids_x"][previous_jump_index:jumpIndex].to_numpy()
        #     lc_data["centroids_x"][previous_jump_index:jumpIndex] = np.tanh(token - np.nanmedian(token))
        #     token = lc_data["centroids_y"][previous_jump_index:jumpIndex].to_numpy()
        #     lc_data["centroids_y"][previous_jump_index:jumpIndex] = np.tanh(token - np.nanmedian(token))
        #     token = lc_data["motion_x"][previous_jump_index:jumpIndex].to_numpy()
        #     lc_data["motion_x"][previous_jump_index:jumpIndex] = np.tanh(token - np.nanmedian(token))
        #     token = lc_data["motion_y"][previous_jump_index:jumpIndex].to_numpy()
        #     lc_data["motion_y"][previous_jump_index:jumpIndex] = np.tanh(token - np.nanmedian(token))
        #     token = lc_data["background_flux"][previous_jump_index:jumpIndex].to_numpy()
        #     lc_data["background_flux"][previous_jump_index:jumpIndex] = np.tanh(token - np.nanmedian(token))
        #     previous_jump_index = jumpIndex
        lc_data.to_csv(file)
        return lc_data

    def prepare_tic(self, prepare_tic_input: PrepareTicInput):
        tic_id = str(prepare_tic_input.tic)
        target_dir = prepare_tic_input.dir
        if not os.path.isdir(target_dir):
            os.mkdir(target_dir)
        try:
            mission_lightcurve_builder = MissionLightcurveBuilder()
        except Exception as e:
            logging.exception("Failed target %s for sector %s", tic_id, prepare_tic_input.sector)
        try:
            logging.info("Trying to get short cadence info for " + str(prepare_tic_input.tic))
            lcbuild = \
                mission_lightcurve_builder.build(MissionObjectInfo([prepare_tic_input.sector], tic_id, cadence=120),
                                                 target_dir)
            lc = lcbuild.lc
            lc_df = pd.DataFrame(columns=['#time', 'flux', 'flux_err'])
            lc_df['#time'] = lc.time.value
            lc_df['flux'] = lc.flux.value
            lc_df['flux_err'] = lc.flux_err.value
            lc_df.to_csv(f"{target_dir}/{prepare_tic_input.sector}_{tic_id}_lc_short.csv")
            self.store_lc_data(lcbuild.lc_data, f"{target_dir}/{prepare_tic_input.sector}_{tic_id}_lcdata_long.csv")
        except Exception as e:
            logging.warning("Failed Short Cadence data for target " + str(prepare_tic_input.tic))
            logging.exception(e)
        logging.info("Trying to get long cadence info for " + str(prepare_tic_input.tic))
        try:
            lcbuild = \
                mission_lightcurve_builder.build(MissionObjectInfo([prepare_tic_input.sector], tic_id, cadence=1800),
                                                 target_dir)
            lc = lcbuild.lc
            lc_df = pd.DataFrame(columns=['#time', 'flux', 'flux_err'])
            lc_df['#time'] = lc.time.value
            lc_df['flux'] = lc.flux.value
            lc_df['flux_err'] = lc.flux_err.value
            lc_df.to_csv(f"{target_dir}/{prepare_tic_input.sector}_{tic_id}_lc_long.csv")
            self.store_lc_data(lcbuild.lc_data, f"{target_dir}/{prepare_tic_input.sector}_{tic_id}_lcdata_long.csv")
        except Exception as e:
            logging.warning("Failed Long Cadence data for target " + str(prepare_tic_input.tic))
            logging.exception(e)

    def prepare_negative_training_dataset(self, first_sector, cpus):
        logging.info("Preparing negatives")
        ois = OisManager(self.cache_dir).load_ois()
        inputs = []
        for sector in np.arange(first_sector, 27, 1):
            self.negative_dir = self.dir + "/original/"
            if not os.path.exists(self.negative_dir):
                os.mkdir(self.negative_dir)
            sector_url = self.SECTOR_URL.format(sector)
            logging.info("Preparing negatives for sector from url " + sector_url)
            sector_file = "sector.csv"
            tic_csv = open(sector_file, 'wb')
            request = requests.get(sector_url)
            tic_csv.write(request.content)
            tic_csv.close()
            tics_sector_df = pd.read_csv(sector_file, comment='#', sep=',')
            tics_sector_df = tics_sector_df.sample(n=500, random_state=0)
            os.remove(sector_file)
            tics_sector_df["TICID"] = "TIC " + tics_sector_df["TICID"].map(str)
            for tic in tics_sector_df["TICID"].unique():
                logging.info("Preparing negative input data for " + str(tic))
                if tic in ois["Object Id"]:
                    logging.warning(str(tic) + " has official candidates!")
                    continue
                inputs.append(PrepareTicInput(self.negative_dir, tic, ois, sector))
            with Pool(processes=cpus) as pool:
                pool.map(self.prepare_tic, inputs)

    # def prepare_tsfresh(self, positive_dir, negative_dir):
    #     tsfresh_short_df = pd.DataFrame(columns=['id', 'time', 'flux', 'flux_err', 'background_flux', 'quality', 'centroids_x',
    #                                        'centroids_y', 'motion_x', 'motion_y'])
    #     tsfresh_long_df = pd.DataFrame(columns=['id', 'time', 'flux', 'flux_err', 'background_flux', 'quality', 'centroids_x',
    #                                        'centroids_y', 'motion_x', 'motion_y'])
    #     tsfresh_tags_short = []
    #     tsfresh_tags_long = []
    #     for tic_dir in os.listdir(positive_dir):
    #         short_lc_dir = positive_dir + "/" + tic_dir + "/time_series_short.csv"
    #         if os.path.exists(short_lc_dir):
    #             lc_short_df = pd.read_csv(positive_dir + "/" + tic_dir + "/time_series_short.csv")
    #             lc_short_df['id'] = tic_dir
    #             tsfresh_short_df.append(lc_short_df)
    #             tsfresh_tags_short.append([tic_dir, 1])
    #         lc_long_df = pd.read_csv(positive_dir + "/" + tic_dir + "/time_series_long.csv")
    #         lc_long_df['id'] = tic_dir
    #         tsfresh_long_df.append(lc_long_df)
    #         tsfresh_tags_long.append([tic_dir, 1])
    #     for tic_dir in os.listdir(negative_dir):
    #         short_lc_dir = negative_dir + "/" + tic_dir + "/time_series_short.csv"
    #         if os.path.exists(short_lc_dir):
    #             lc_short_df = pd.read_csv(negative_dir + "/" + tic_dir + "/time_series_short.csv")
    #             lc_short_df['id'] = tic_dir
    #             tsfresh_short_df.append(lc_short_df)
    #             tsfresh_tags_short.append([tic_dir, 1])
    #         lc_long_df = pd.read_csv(negative_dir + "/" + tic_dir + "/time_series_long.csv")
    #         lc_long_df['id'] = tic_dir
    #         tsfresh_long_df.append(lc_long_df)
    #         tsfresh_tags_long.append([tic_dir, 0])
    #     tsfresh_tags_short = pd.Series(tsfresh_tags_short)
    #     tsfresh_tags_long = pd.Series(tsfresh_tags_long)
    #     # TODO tsfresh needs a dataframe with all the "time series" data (centroids, motion, flux, bck_flux...)
    #     # TODO with an id column specifying the target id and a "y" as a df containing the target ids and the classification
    #     # TODO tag. We need to check how to make this compatible with transit times tagging instead of entire curve
    #     # TODO classification. Maybe https://tsfresh.readthedocs.io/en/latest/text/forecasting.html is helpful.
    #     extracted_features_short = tsfresh.extract_relevant_features(tsfresh_short_df, tsfresh_tags_short, column_id='id',
    #                                                                  column_sort='time')
    #     extracted_features_long = tsfresh.extract_relevant_features(tsfresh_long_df, tsfresh_tags_long, column_id='id',
    #                                                                 column_sort='time')

    @staticmethod
    def prepare_cadence_set_dir(root_dir, mode="short"):
        """
        Creates the flattened directory for training and testing sets for the selected cadence method.
        @param root_dir: the directory where the data has been stored
        @param mode: the cadence mode [short|long]
        """
        flatten_dir = root_dir + "/" + mode
        if not os.path.exists(flatten_dir):
            os.mkdir(flatten_dir)
        positive_dir = root_dir + "/tp"
        false_positive_dir = root_dir + "/fp"
        negative_dir = root_dir + "/ntp"
        logging.info("Flattening positive dir %s", positive_dir)
        for file in os.listdir(positive_dir):
            src = positive_dir + "/" + file
            dst = flatten_dir + "/" + file + "_tp_"
            if os.path.exists(src + "/periodogram_" + mode + ".csv") and \
                    os.path.exists(src + "/time_series_" + mode + ".csv"):
                ois_df = pd.read_csv(src + "/ois.csv")
                for index, oi_row in ois_df.iterrows():
                    dst_index = dst + str(index)
                    os.symlink(src, dst_index)
        logging.info("Flattening negative dir %s", negative_dir)
        for file in os.listdir(false_positive_dir):
            src = false_positive_dir + "/" + file
            dst = flatten_dir + "/" + file + "_fp_"
            if os.path.exists(src + "/periodogram_" + mode + ".csv") and \
                    os.path.exists(src + "/time_series_" + mode + ".csv"):
                ois_df = pd.read_csv(src + "/ois.csv")
                for index, oi_row in ois_df.iterrows():
                    dst_index = dst + str(index)
                    os.symlink(src, dst_index)
        logging.info("Flattening false positive dir %s", false_positive_dir)
        np.random.seed(0)
        for file in os.listdir(negative_dir):
            tic_sector_file = negative_dir + "/" + file
            for file_in_sector in os.listdir(tic_sector_file):
                src = tic_sector_file + "/" + file_in_sector
                dst = flatten_dir + "/" + file_in_sector + "_ntp_0"
                if os.path.exists(src + "/periodogram_" + mode + ".csv") and \
                        os.path.exists(src + "/time_series_" + mode + ".csv"):
                    os.symlink(src, dst)

    @staticmethod
    def split_training_test_and_validation_sets(cadence_dir):
        labels = []
        filenames = []
        for file in os.listdir(cadence_dir):
            filenames.append(file)
            label = 0.0
            if "_tp_" in file:
                label = 1.0
            elif "_fp_" in file:
                label = 0.25 # TODO 0.25 or something else?
            labels.append(label)
        np.save(cadence_dir + '/filenames.npy', filenames)
        labels = keras.utils.to_categorical(labels)
        np.save(cadence_dir + '/labels.npy', labels)
        filenames_shuffled, y_labels_one_hot_shuffled = sklearn.utils.shuffle(filenames, labels)
        filenames_shuffled_numpy = np.array(filenames_shuffled)
        x_train_filenames, x_val_filenames, y_train, y_val = sklearn.model_selection.train_test_split(
            filenames_shuffled_numpy, labels, test_size=0.2, random_state=1)
        np.save(cadence_dir + '/x_train_filenames.npy', x_train_filenames)
        np.save(cadence_dir + '/y_train.npy', y_train)
        np.save(cadence_dir + '/x_val_filenames.npy', x_val_filenames)
        np.save(cadence_dir + '/y_val.npy', y_val)

cpus = 10
first_negative_sector = 1
training_data_dir = "/mnt/DATA-2/detrend/original/"
cache_dir = "/home/martin/"
ml_training_set_preparer = EmptyTargetsPreparer(training_data_dir, cache_dir)
ml_training_set_preparer.prepare_positive_training_dataset(cpus)
#ml_training_set_preparer.prepare_false_positive_training_dataset(cpus)
#ml_training_set_preparer.prepare_negative_training_dataset(first_negative_sector, cpus)
#MLSingleTransitsClassifier().load_candidate_single_transits(traid ning_data_dir, "tp")
#MlTrainingSetPreparer.prepare_cadence_set_dir(training_data_dir, "short")
#MLModelBuilder().get_model()
#MLModelBuilder()get_single_transit_model()