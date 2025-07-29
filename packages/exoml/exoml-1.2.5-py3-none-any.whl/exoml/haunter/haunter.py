import logging
import tensorflow as tf
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import keras
import pandas as pd
from keras import Model
from keras.layers import LeakyReLU
from keras.losses import MeanSquaredError, MeanAbsoluteError
from keras.metrics import RootMeanSquaredError
from keras_core.src.metrics import R2Score
from lcbuilder.helper import LcbuilderHelper

from exoml.haunter.haunter_generator import HaunterModelGenerator
from exoml.ml.log.with_logging import WithLogging
from exoml.ml.loss.unsupervised import intransit_weighted_mean_squared_error
from exoml.ml.metrics.fixed_mean import FixedMean
import astropy.units as u

from exoml.ml.model.base_model import BaseModel, HyperParams


G = 6.67430e-11  # Constante de gravitación universal en unidades SI (m^3 kg^-1 s^-2)
M_EARTH = 5.972e24  # Masa de la Tierra en kg
R_EARTH = 6.371e6   # Radio de la Tierra en metros
P_PASCAL = 1e5
RHO_CORE = 13000.0
RHO_MANTLE = 5000.0
RHO_WATER = 1000.0
RHO_GAS = 0.2
GAMMA_SCALING = 0.5  # Ajustable según calibración
PI = tf.constant(np.pi, dtype=tf.float32)


class Haunter(BaseModel):
    def __init__(self, hyperparameters: HyperParams, name='Haunter', input_size=6):
        super().__init__(name, input_size, None, None, hyperparameters)

    @staticmethod
    def load_data(dir):
        dataset = pd.read_csv(f"{dir}/table.csv", sep=',')
        dataset_large = pd.read_csv(f"{dir}/kunal_table.csv", sep=',')
        dataset = pd.concat([dataset, dataset_large])
        dataset = dataset.loc[dataset['physical?'] == True]
        dataset = dataset.loc[dataset['job_path'] != 'run_folders/model_0019663']
        return dataset

    def build(self):
        input = keras.Input(shape=(self.input_size,))
        nn = keras.layers.GaussianNoise(self.hyperparams.white_noise_std)(input)
        nn = keras.layers.Dense(128, activation=LeakyReLU(0.01))(nn)
        nn = keras.layers.Dropout(rate=self.hyperparams.dropout_rate)(nn)
        nn = keras.layers.Dense(256, activation=LeakyReLU(0.01))(nn)
        nn = keras.layers.Dropout(rate=self.hyperparams.dropout_rate)(nn)
        nn = keras.layers.Dense(512, activation=LeakyReLU(0.01))(nn)
        nn = keras.layers.Dropout(rate=self.hyperparams.dropout_rate)(nn)
        nn = keras.layers.Dense(1024, activation=LeakyReLU(0.01))(nn)
        nn = keras.layers.Dropout(rate=self.hyperparams.dropout_rate)(nn)
        nn = keras.layers.Dense(2048, activation=LeakyReLU(0.01))(nn)
        nn = keras.layers.Dropout(rate=self.hyperparams.dropout_rate)(nn)
        nn = keras.layers.Dense(2048, activation=LeakyReLU(0.01))(nn)
        nn = keras.layers.Dropout(rate=self.hyperparams.dropout_rate)(nn)
        nn = keras.layers.Dense(1024, activation=LeakyReLU(0.01))(nn)
        nn = keras.layers.Dropout(rate=self.hyperparams.dropout_rate)(nn)
        nn = keras.layers.Dense(512, activation=LeakyReLU(0.01))(nn)
        nn = keras.layers.Dropout(rate=self.hyperparams.dropout_rate)(nn)
        nn = keras.layers.Dense(256, activation=LeakyReLU(0.01))(nn)
        nn = keras.layers.Dropout(rate=self.hyperparams.dropout_rate)(nn)
        nn = keras.layers.Dense(128, activation=LeakyReLU(0.01))(nn)
        nn = keras.layers.Dropout(rate=self.hyperparams.dropout_rate)(nn)
        nn = keras.layers.Dense(3, activation="linear")(nn)
        nn = keras.layers.Concatenate()([nn, input])
        self.set_model(Model(inputs=input, outputs=nn))
        return self

    def load_training_set(self, **kwargs):
        training_dir = kwargs.get('training_dir')
        dataset = Haunter.load_data(training_dir)
        self.input_means = tf.constant([
            dataset['mass_Mearth_input'].mean(),
            dataset['CMF_input'].mean(),
            dataset['Zenv_input'].mean(),
            dataset['Zwater_core_input'].mean(),
            dataset['Tsurf_K_input'].mean(),
            dataset['Psurf_bar_input'].mean()], dtype=tf.float32)
        self.input_stds = tf.constant([
            dataset['mass_Mearth_input'].std(),
            dataset['CMF_input'].std(),
            dataset['Zenv_input'].std(),
            dataset['Zwater_core_input'].std(),
            dataset['Tsurf_K_input'].std(),
            dataset['Psurf_bar_input'].std()], dtype=tf.float32)
        self.input_mins = tf.constant([
            dataset['mass_Mearth_input'].min(),
            dataset['CMF_input'].min(),
            dataset['Zenv_input'].min(),
            dataset['Zwater_core_input'].min(),
            dataset['Tsurf_K_input'].min(),
            dataset['Psurf_bar_input'].min()], dtype=tf.float32)
        self.input_maxs = tf.constant([
            dataset['mass_Mearth_input'].max(),
            dataset['CMF_input'].max(),
            dataset['Zenv_input'].max(),
            dataset['Zwater_core_input'].max(),
            dataset['Tsurf_K_input'].max(),
            dataset['Psurf_bar_input'].max()], dtype=tf.float32)
        self.output_means = tf.constant([
            dataset['radius_Rearth_output'].mean(),
            dataset['entropy_SI_output'].mean(),
            dataset['f_s_SI_output'].mean()], dtype=tf.float32)
        self.output_stds = tf.constant([
            dataset['radius_Rearth_output'].std(),
            dataset['entropy_SI_output'].std(),
            dataset['f_s_SI_output'].std()], dtype=tf.float32)
        self.output_mins = tf.constant([
            dataset['radius_Rearth_output'].min(),
            dataset['entropy_SI_output'].min(),
            dataset['f_s_SI_output'].min()], dtype=tf.float32)
        self.output_maxs = tf.constant([
            dataset['radius_Rearth_output'].max(),
            dataset['entropy_SI_output'].max(),
            dataset['f_s_SI_output'].max()], dtype=tf.float32)
        dataset = self.add_standardized_columns(dataset, dataset)
        return dataset

    def instance_scaler(self):
        return MinMaxScaler()

    def add_standardized_columns(self, dataset, training_dataset):
        scaler = self.instance_scaler()
        scaler.fit(training_dataset.loc[:, 'mass_Mearth_input'])
        dataset.loc[:, 'mass_Mearth_input_norm'] = scaler.transform(dataset.loc[:, 'mass_Mearth_input'].to_numpy())
        scaler = self.instance_scaler()
        scaler.fit(training_dataset.loc[:, 'CMF_input'])
        dataset.loc[:, 'CMF_input_norm'] = scaler.transform(dataset.loc[:, 'CMF_input'].to_numpy())
        scaler = self.instance_scaler()
        scaler.fit(training_dataset.loc[:, 'Zenv_input'])
        dataset.loc[:, 'Zenv_input_norm'] = scaler.transform(dataset.loc[:, 'Zenv_input'].to_numpy())
        scaler = self.instance_scaler()
        scaler.fit(training_dataset.loc[:, 'Zwater_core_input'])
        dataset.loc[:, 'Zwater_core_input_norm'] = scaler.transform(dataset.loc[:, 'Zwater_core_input'].to_numpy())
        scaler = self.instance_scaler()
        scaler.fit(training_dataset.loc[:, 'Tsurf_K_input'])
        dataset.loc[:, 'Tsurf_K_input_norm'] = scaler.transform(dataset.loc[:, 'Tsurf_K_input'].to_numpy())
        scaler = self.instance_scaler()
        scaler.fit(training_dataset.loc[:, 'Psurf_bar_input'])
        dataset.loc[:, 'Psurf_bar_input_norm'] = scaler.transform(dataset.loc[:, 'Psurf_bar_input'].to_numpy())
        scaler = self.instance_scaler()
        scaler.fit(training_dataset.loc[:, 'radius_Rearth_output'])
        dataset.loc[:, 'radius_Rearth_output_norm'] = scaler.transform(
            dataset.loc[:, 'radius_Rearth_output'].to_numpy())
        scaler = self.instance_scaler()
        scaler.fit(training_dataset.loc[:, 'entropy_SI_output'])
        dataset.loc[:, 'entropy_SI_output_norm'] = scaler.transform(dataset.loc[:, 'entropy_SI_output'].to_numpy())
        scaler = self.instance_scaler()
        scaler.fit(training_dataset.loc[:, 'f_s_SI_output'])
        dataset.loc[:, 'f_s_SI_output_norm'] = scaler.transform(dataset.loc[:, 'f_s_SI_output'].to_numpy())
        logging.info("Mass " + str(training_dataset.loc[:, 'mass_Mearth_input'].mean()) + ' +- ' + str(
            training_dataset.loc[:, 'mass_Mearth_input'].std()) +
                     ' ' + str(training_dataset.loc[:, 'mass_Mearth_input'].min()) + ' ' + str(
            training_dataset.loc[:, 'mass_Mearth_input'].max()))
        logging.info("CMF " + str(training_dataset.loc[:, 'CMF_input'].mean()) + ' +- ' + str(
            training_dataset.loc[:, 'CMF_input'].std()) +
                     ' ' + str(training_dataset.loc[:, 'CMF_input'].min()) + ' ' + str(
            training_dataset.loc[:, 'CMF_input'].max()))
        logging.info("Zenv " + str(training_dataset.loc[:, 'Zenv_input'].mean()) + ' +- ' + str(
            training_dataset.loc[:, 'Zenv_input'].std()) +
                     ' ' + str(training_dataset.loc[:, 'Zenv_input'].min()) + ' ' + str(
            training_dataset.loc[:, 'Zenv_input'].max()))
        logging.info("Zwater " + str(training_dataset.loc[:, 'Zwater_core_input'].mean()) + ' +- ' + str(
            training_dataset.loc[:, 'Zwater_core_input'].std()) +
                     ' ' + str(training_dataset.loc[:, 'Zwater_core_input'].min()) + ' ' + str(
            training_dataset.loc[:, 'Zwater_core_input'].max()))
        logging.info("Tsurf " + str(training_dataset.loc[:, 'Tsurf_K_input'].mean()) + ' +- ' + str(
            training_dataset.loc[:, 'Tsurf_K_input'].std()) +
                     ' ' + str(training_dataset.loc[:, 'Tsurf_K_input'].min()) + ' ' + str(
            training_dataset.loc[:, 'Tsurf_K_input'].max()))
        logging.info("Psurf " + str(training_dataset.loc[:, 'Psurf_bar_input'].mean()) + ' +- ' + str(
            training_dataset.loc[:, 'Psurf_bar_input'].std()) +
                     ' ' + str(training_dataset.loc[:, 'Psurf_bar_input'].min()) + ' ' + str(
            training_dataset.loc[:, 'Psurf_bar_input'].max()))
        logging.info("Radius " + str(training_dataset.loc[:, 'radius_Rearth_output'].mean()) + ' +- ' + str(
            training_dataset.loc[:, 'radius_Rearth_output'].std()) +
                     ' ' + str(training_dataset.loc[:, 'radius_Rearth_output'].min()) + ' ' + str(
            training_dataset.loc[:, 'radius_Rearth_output'].max()))
        logging.info("Entropy " + str(training_dataset.loc[:, 'entropy_SI_output'].mean()) + ' +- ' + str(
            training_dataset.loc[:, 'entropy_SI_output'].std()) +
                     ' ' + str(training_dataset.loc[:, 'entropy_SI_output'].min()) + ' ' + str(
            training_dataset.loc[:, 'entropy_SI_output'].max()))
        logging.info("F_S " + str(training_dataset.loc[:, 'f_s_SI_output'].mean()) + ' +- ' + str(
            training_dataset.loc[:, 'f_s_SI_output'].std()) +
                     ' ' + str(training_dataset.loc[:, 'f_s_SI_output'].min()) + ' ' + str(
            training_dataset.loc[:, 'f_s_SI_output'].max()))
        return dataset

    def add_destandardized_columns(self, dataset, training_dataset, predictions):
        logging.info("Mass " + str(training_dataset.loc[:, 'mass_Mearth_input'].mean()) + ' +- ' + str(
            training_dataset.loc[:, 'mass_Mearth_input'].std()) +
                     ' ' + str(training_dataset.loc[:, 'mass_Mearth_input'].min()) + ' ' + str(
            training_dataset.loc[:, 'mass_Mearth_input'].max()))
        logging.info(
            "CMF " + str(training_dataset.loc[:, 'CMF_input'].mean()) + ' +- ' + str(
                training_dataset.loc[:, 'CMF_input'].std()) +
            ' ' + str(training_dataset.loc[:, 'CMF_input'].min()) + ' ' + str(
                training_dataset.loc[:, 'CMF_input'].max()))
        logging.info(
            "Zenv " + str(training_dataset.loc[:, 'Zenv_input'].mean()) + ' +- ' + str(
                training_dataset.loc[:, 'Zenv_input'].std()) +
            ' ' + str(training_dataset.loc[:, 'Zenv_input'].min()) + ' ' + str(
                training_dataset.loc[:, 'Zenv_input'].max()))
        logging.info("Zwater " + str(training_dataset.loc[:, 'Zwater_core_input'].mean()) + ' +- ' + str(
            training_dataset.loc[:, 'Zwater_core_input'].std()) +
                     ' ' + str(training_dataset.loc[:, 'Zwater_core_input'].min()) + ' ' + str(
            training_dataset.loc[:, 'Zwater_core_input'].max()))
        logging.info("Tsurf " + str(training_dataset.loc[:, 'Tsurf_K_input'].mean()) + ' +- ' + str(
            training_dataset.loc[:, 'Tsurf_K_input'].std()) +
                     ' ' + str(training_dataset.loc[:, 'Tsurf_K_input'].min()) + ' ' + str(
            training_dataset.loc[:, 'Tsurf_K_input'].max()))
        logging.info("Psurf " + str(training_dataset.loc[:, 'Psurf_bar_input'].mean()) + ' +- ' + str(
            training_dataset.loc[:, 'Psurf_bar_input'].std()) +
                     ' ' + str(training_dataset.loc[:, 'Psurf_bar_input'].min()) + ' ' + str(
            training_dataset.loc[:, 'Psurf_bar_input'].max()))
        logging.info("Radius " + str(training_dataset.loc[:, 'radius_Rearth_output'].mean()) + ' +- ' + str(
            training_dataset.loc[:, 'radius_Rearth_output'].std()) +
                     ' ' + str(training_dataset.loc[:, 'radius_Rearth_output'].min()) + ' ' + str(
            training_dataset.loc[:, 'radius_Rearth_output'].max()))
        logging.info("Entropy " + str(training_dataset.loc[:, 'entropy_SI_output'].mean()) + ' +- ' + str(
            training_dataset.loc[:, 'entropy_SI_output'].std()) +
                     ' ' + str(training_dataset.loc[:, 'entropy_SI_output'].min()) + ' ' + str(
            training_dataset.loc[:, 'entropy_SI_output'].max()))
        logging.info(
            "F_S " + str(training_dataset.loc[:, 'f_s_SI_output'].mean()) + ' +- ' + str(
                training_dataset.loc[:, 'f_s_SI_output'].std()) +
            ' ' + str(training_dataset.loc[:, 'f_s_SI_output'].min()) + ' ' + str(
                training_dataset.loc[:, 'f_s_SI_output'].max()))
        scaler = self.instance_scaler()
        scaler.fit(training_dataset.loc[:, 'radius_Rearth_output'])
        dataset.loc[:, 'radius_Rearth_output_pred'] = scaler.inverse_transform(predictions[:, 0])
        scaler = self.instance_scaler()
        scaler.fit(training_dataset.loc[:, 'entropy_SI_output'])
        dataset.loc[:, 'entropy_SI_output_pred'] = scaler.inverse_transform(predictions[:, 1])
        scaler = self.instance_scaler()
        scaler.fit(training_dataset.loc[:, 'f_s_SI_output'])
        dataset.loc[:, 'f_s_SI_output_pred'] = scaler.inverse_transform(predictions[:, 2])
        return dataset

    def instance_generator(self, dataset, dir, batch_size, input_sizes, type_to_label, zero_epsilon=1e-7, shuffle=True):
        return HaunterModelGenerator(dataset, batch_size, input_sizes, zero_epsilon, shuffle=shuffle)

    def instance_loss_accuracy(self):
        # loss = tf.keras.losses.MeanAbsolutePercentageError(reduction=losses_utils.ReductionV2.AUTO)
        loss = tf.keras.losses.MeanSquaredError()
        return loss, None

    def instance_metrics(self):
        return [self.rmse_radius, self.rmse_entropy, self.rmse_fs,
                self.mae_radius, self.mae_entropy, self.mae_fs,
                self.r2_radius, self.r2_entropy, self.r2_fs, self.r2_total]

    def plot_metrics(self, model_dir, steps_per_epoch, with_validation=False):
        return []

    def load_model(self, dir, custom_objects={}, compile=False):
        custom_objects['mse_radius'] = self.mse_radius
        custom_objects['mse_entropy'] = self.mse_entropy
        custom_objects['mse_fs'] = self.mse_fs
        custom_objects['rmse_radius'] = self.rmse_radius
        custom_objects['rmse_entropy'] = self.rmse_entropy
        custom_objects['rmse_fs'] = self.rmse_fs
        custom_objects['mae_radius'] = self.mae_radius
        custom_objects['mae_entropy'] = self.mae_entropy
        custom_objects['mae_fs'] = self.mae_fs
        custom_objects['r2_radius'] = self.r2_radius
        custom_objects['r2_entropy'] = self.r2_entropy
        custom_objects['r2_fs'] = self.r2_fs
        logging.info("Loading model from %s", dir)
        self.set_model(tf.keras.models.load_model(dir, compile=compile, custom_objects=custom_objects))
        return self

    def predict_non_physical(self, dir, batch_size=128):
        dataset = pd.read_csv(f"{dir}/table.csv", sep=',')
        dataset_large = pd.read_csv(f"{dir}/kunal_table.csv", sep=',')
        dataset = pd.concat([dataset, dataset_large])
        dataset_training = dataset.loc[dataset['physical?'] == True]
        dataset_training = dataset_training.loc[dataset_training['job_path'] != 'run_folders/model_0019663']
        dataset_testing = dataset.loc[dataset['physical?'] == False]
        dataset_testing = self.add_standardized_columns(dataset_testing, dataset_training)
        predict_batch_generator = self.instance_generator(dataset_testing, None, batch_size, self.input_size, None)
        predictions = self.model.predict(predict_batch_generator, batch_size=batch_size, workers=1)
        dataset_testing['radius_Rearth_output_norm_pred'] = predictions[:, 0]
        dataset_testing['entropy_SI_output_norm_pred'] = predictions[:, 1]
        dataset_testing['f_s_SI_output_norm_pred'] = predictions[:, 2]
        dataset_testing = self.add_destandardized_columns(dataset_testing, dataset_training, predictions)
        dataset_testing['radius_Rearth_output_pred_diff'] = np.abs(
            dataset_testing['radius_Rearth_output_pred'] - dataset_testing['radius_Rearth_output'])
        dataset_testing['entropy_SI_output_pred_diff'] = np.abs(
            dataset_testing['entropy_SI_output_pred'] - dataset_testing['entropy_SI_output'])
        dataset_testing['f_s_SI_output_pred_diff'] = np.abs(
            dataset_testing['f_s_SI_output_pred'] - dataset_testing['f_s_SI_output'])
        dataset_testing['radius_Rearth_output_pred_diff_ratio'] = np.abs(
            dataset_testing['radius_Rearth_output_pred'] - dataset_testing['radius_Rearth_output']) / dataset_testing[
                                                                      'radius_Rearth_output']
        dataset_testing['entropy_SI_output_pred_diff_ratio'] = np.abs(
            dataset_testing['entropy_SI_output_pred'] - dataset_testing['entropy_SI_output']) / dataset_testing[
                                                                   'entropy_SI_output']
        dataset_testing['f_s_SI_output_pred_diff_ratio'] = np.abs(
            dataset_testing['f_s_SI_output_pred'] - dataset_testing['f_s_SI_output']) / dataset_testing['f_s_SI_output']
        results_df = dataset_testing[['radius_Rearth_output', 'radius_Rearth_output_norm',
                                      'radius_Rearth_output_pred', 'radius_Rearth_output_norm_pred',
                                      'radius_Rearth_output_pred_diff', 'radius_Rearth_output_pred_diff_ratio',
                                      'f_s_SI_output', 'f_s_SI_output_norm',
                                      'f_s_SI_output_pred', 'f_s_SI_output_norm_pred',
                                      'f_s_SI_output_pred_diff', 'f_s_SI_output_pred_diff_ratio',
                                      'entropy_SI_output', 'entropy_SI_output_norm',
                                      'entropy_SI_output_pred', 'entropy_SI_output_norm_pred',
                                      'entropy_SI_output_pred_diff', 'entropy_SI_output_pred_diff_ratio']]
        logging.info("Results non physical: \n%s", results_df.to_string())
        logging.info("Non physical radius diff ratio mean: " + str(
            dataset_testing.loc[:, 'radius_Rearth_output_pred_diff_ratio'].mean()) + '+-' +
                     str(dataset_testing.loc[:, 'radius_Rearth_output_pred_diff_ratio'].std()))
        logging.info("Non physical f_s_SI diff ratio mean: " + str(
            dataset_testing.loc[:, 'f_s_SI_output_pred_diff_ratio'].mean()) + '+-' +
                     str(dataset_testing.loc[:, 'f_s_SI_output_pred_diff_ratio'].std()))
        logging.info("Non physical entropy_SI diff ratio mean: " + str(
            dataset_testing.loc[:, 'entropy_SI_output_pred_diff_ratio'].mean()) + '+-' +
                     str(dataset_testing.loc[:, 'entropy_SI_output_pred_diff_ratio'].std()))
        logging.info("Non physical radius diff ratio median: " + str(
            dataset_testing.loc[:, 'radius_Rearth_output_pred_diff_ratio'].median()) + '+-' +
                     str(dataset_testing.loc[:, 'radius_Rearth_output_pred_diff_ratio'].std()))
        logging.info("Non physical f_s_SI diff ratio median: " + str(
            dataset_testing.loc[:, 'f_s_SI_output_pred_diff_ratio'].median()) + '+-' +
                     str(dataset_testing.loc[:, 'f_s_SI_output_pred_diff_ratio'].std()))
        logging.info("Non physical entropy_SI diff ratio median: " + str(
            dataset_testing.loc[:, 'entropy_SI_output_pred_diff_ratio'].median()) + '+-' +
                     str(dataset_testing.loc[:, 'entropy_SI_output_pred_diff_ratio'].std()))
        return dataset_testing

    def predict_validation(self, model_dir, dir, batch_size=128):
        dataset = pd.read_csv(f"{dir}/table.dat", sep=' ')
        dataset_training = dataset.loc[dataset['physical?'] == True]
        dataset_training = dataset_training.loc[dataset_training['job_path'] != 'run_folders/model_0019663']
        dataset_validation = pd.read_csv(f"{model_dir}/validation_dataset.csv")
        dataset_training = self.add_standardized_columns(dataset_validation, dataset_training)
        predict_batch_generator = self.instance_generator(dataset_validation, None, batch_size, self.input_size, None,
                                                          shuffle=False)
        predictions = self.model.predict(predict_batch_generator, batch_size=batch_size)
        dataset_validation['radius_Rearth_output_norm_pred'] = predictions[:, 0]
        dataset_validation['entropy_SI_output_norm_pred'] = predictions[:, 1]
        dataset_validation['f_s_SI_output_norm_pred'] = predictions[:, 2]
        dataset_validation = self.add_destandardized_columns(dataset_validation, dataset_training, predictions)
        dataset_validation['radius_Rearth_output_pred_diff'] = np.abs(
            dataset_validation['radius_Rearth_output_pred'] - dataset_validation['radius_Rearth_output'])
        dataset_validation['entropy_SI_output_pred_diff'] = np.abs(
            dataset_validation['entropy_SI_output_pred'] - dataset_validation['entropy_SI_output'])
        dataset_validation['f_s_SI_output_pred_diff'] = np.abs(
            dataset_validation['f_s_SI_output_pred'] - dataset_validation['f_s_SI_output'])
        dataset_validation['radius_Rearth_output_pred_diff_ratio'] = np.abs(
            dataset_validation['radius_Rearth_output_pred'] - dataset_validation['radius_Rearth_output']) / \
                                                                     dataset_validation['radius_Rearth_output']
        dataset_validation['entropy_SI_output_pred_diff_ratio'] = np.abs(
            dataset_validation['entropy_SI_output_pred'] - dataset_validation['entropy_SI_output']) / \
                                                                  dataset_validation['entropy_SI_output']
        dataset_validation['f_s_SI_output_pred_diff_ratio'] = np.abs(
            dataset_validation['f_s_SI_output_pred'] - dataset_validation['f_s_SI_output']) / np.abs(
            dataset_validation['f_s_SI_output'])
        results_df = dataset_validation[['radius_Rearth_output', 'radius_Rearth_output_norm',
                                         'radius_Rearth_output_pred', 'radius_Rearth_output_norm_pred',
                                         'radius_Rearth_output_pred_diff', 'radius_Rearth_output_pred_diff_ratio',
                                         'f_s_SI_output', 'f_s_SI_output_norm',
                                         'f_s_SI_output_pred', 'f_s_SI_output_norm_pred',
                                         'f_s_SI_output_pred_diff', 'f_s_SI_output_pred_diff_ratio',
                                         'entropy_SI_output', 'entropy_SI_output_norm',
                                         'entropy_SI_output_pred', 'entropy_SI_output_norm_pred',
                                         'entropy_SI_output_pred_diff', 'entropy_SI_output_pred_diff_ratio']]
        logging.info("Results validation: \n%s", results_df.to_string())
        logging.info("Validation radius diff mean: " + str(
            dataset_validation.loc[:, 'radius_Rearth_output_pred_diff'].mean()) + '+-' +
                     str(dataset_validation.loc[:, 'radius_Rearth_output_pred_diff'].std()))
        logging.info("Validation f_s_SI diff mean: " + str(
            dataset_validation.loc[:, 'f_s_SI_output_pred_diff'].mean()) + '+-' +
                     str(dataset_validation.loc[:, 'f_s_SI_output_pred_diff'].std()))
        logging.info("Validation entropy_SI diff mean: " + str(
            dataset_validation.loc[:, 'entropy_SI_output_pred_diff'].mean()) + '+-' +
                     str(dataset_validation.loc[:, 'entropy_SI_output_pred_diff'].std()))
        logging.info("Validation radius diff ratio median: " + str(
            dataset_validation.loc[:, 'radius_Rearth_output_pred_diff_ratio'].median()) + '+-' +
                     str(dataset_validation.loc[:, 'radius_Rearth_output_pred_diff_ratio'].std()))
        logging.info("Validation f_s_SI diff ratio median: " + str(
            dataset_validation.loc[:, 'f_s_SI_output_pred_diff_ratio'].median()) + '+-' +
                     str(dataset_validation.loc[:, 'f_s_SI_output_pred_diff_ratio'].std()))
        logging.info("Validation entropy_SI diff ratio median: " + str(
            dataset_validation.loc[:, 'entropy_SI_output_pred_diff_ratio'].median()) + '+-' +
                     str(dataset_validation.loc[:, 'entropy_SI_output_pred_diff_ratio'].std()))
        logging.info("Validation radius diff ratio mean: " + str(
            dataset_validation.loc[:, 'radius_Rearth_output_pred_diff_ratio'].mean()) + '+-' +
                     str(dataset_validation.loc[:, 'radius_Rearth_output_pred_diff_ratio'].std()))
        logging.info("Validation f_s_SI diff ratio mean: " + str(
            dataset_validation.loc[:, 'f_s_SI_output_pred_diff_ratio'].mean()) + '+-' +
                     str(dataset_validation.loc[:, 'f_s_SI_output_pred_diff_ratio'].std()))
        logging.info("Validation entropy_SI diff ratio mean: " + str(
            dataset_validation.loc[:, 'entropy_SI_output_pred_diff_ratio'].mean()) + '+-' +
                     str(dataset_validation.loc[:, 'entropy_SI_output_pred_diff_ratio'].std()))
        return dataset_validation

    def plot_hists(self, df, additional_columns=[]):
        columns = ['mass_Mearth_input', 'mass_Mearth_input_norm',
                   'CMF_input', 'CMF_input_norm',
                   'Zenv_input', 'Zenv_input_norm',
                   'Zwater_core_input', 'Zwater_core_input_norm',
                   'Tsurf_K_input', 'Tsurf_K_input_norm',
                   'Psurf_bar_input', 'Psurf_bar_input_norm',
                   'radius_Rearth_output', 'radius_Rearth_output_norm',
                   'f_s_SI_output', 'f_s_SI_output_norm',
                   'entropy_SI_output', 'entropy_SI_output_norm',
                   ]
        fig, axs = plt.subplots(9, 2, figsize=(10, 30))
        for i, col in enumerate(columns):
            axs[i // 2][i % 2].hist(df[col].dropna(), bins=15, color='lightblue', edgecolor='black')
            axs[i // 2][i % 2].set_title(f"Distribution of {col}")
            axs[i // 2][i % 2].set_xlabel(col)
            axs[i // 2][i % 2].set_ylabel('Frequency')
        plt.tight_layout()
        plt.show()
        if len(additional_columns) > 0:
            fig, axs = plt.subplots(len(additional_columns) // 2, 2, figsize=(10, 30))
            for i, col in enumerate(additional_columns):
                axs[i // 2][i % 2].hist(df[col].dropna(), bins=15, color='lightblue', edgecolor='black')
                axs[i // 2][i % 2].set_title(f"Distribution of {col}")
                axs[i // 2][i % 2].set_xlabel(col)
                axs[i // 2][i % 2].set_ylabel('Frequency')
            plt.tight_layout()
            plt.show()


    def mse_radius(self, y_true, y_pred):
        y_pred_outputs = y_pred[:, :3]
        y_true_outputs = y_true[:, :3]
        y_pred_outputs = y_pred_outputs * (self.output_maxs - self.output_mins + 1e-8) + self.output_mins
        y_true_outputs = y_true_outputs * (self.output_maxs - self.output_mins + 1e-8) + self.output_mins
        return tf.reduce_mean(tf.square(y_true_outputs[:, 0] - y_pred_outputs[:, 0]))

    def mse_entropy(self, y_true, y_pred):
        y_pred_outputs = y_pred[:, :3]
        y_true_outputs = y_true[:, :3]
        y_pred_outputs = y_pred_outputs * (self.output_maxs - self.output_mins + 1e-8) + self.output_mins
        y_true_outputs = y_true_outputs * (self.output_maxs - self.output_mins + 1e-8) + self.output_mins
        return tf.reduce_mean(tf.square(y_true_outputs[:, 1] - y_pred_outputs[:, 1]))

    def mse_fs(self, y_true, y_pred):
        y_pred_outputs = y_pred[:, :3]
        y_true_outputs = y_true[:, :3]
        y_pred_outputs = y_pred_outputs * (self.output_maxs - self.output_mins + 1e-8) + self.output_mins
        y_true_outputs = y_true_outputs * (self.output_maxs - self.output_mins + 1e-8) + self.output_mins
        return tf.reduce_mean(tf.square(y_true_outputs[:, 2] - y_pred_outputs[:, 2]))

    def rmse_radius(self, y_true, y_pred):
        y_pred_outputs = y_pred[:, :3]
        y_true_outputs = y_true[:, :3]
        y_pred_outputs = y_pred_outputs * (self.output_maxs - self.output_mins + 1e-8) + self.output_mins
        y_true_outputs = y_true_outputs * (self.output_maxs - self.output_mins + 1e-8) + self.output_mins
        return tf.sqrt(tf.reduce_mean(tf.square(y_true_outputs[:, 0] - y_pred_outputs[:, 0])))

    def rmse_entropy(self, y_true, y_pred):
        y_pred_outputs = y_pred[:, :3]
        y_true_outputs = y_true[:, :3]
        y_pred_outputs = y_pred_outputs * (self.output_maxs - self.output_mins + 1e-8) + self.output_mins
        y_true_outputs = y_true_outputs * (self.output_maxs - self.output_mins + 1e-8) + self.output_mins
        return tf.sqrt(tf.reduce_mean(tf.square(y_true_outputs[:, 1] - y_pred_outputs[:, 1])))

    def rmse_fs(self, y_true, y_pred):
        y_pred_outputs = y_pred[:, :3]
        y_true_outputs = y_true[:, :3]
        y_pred_outputs = y_pred_outputs * (self.output_maxs - self.output_mins + 1e-8) + self.output_mins
        y_true_outputs = y_true_outputs * (self.output_maxs - self.output_mins + 1e-8) + self.output_mins
        return tf.sqrt(tf.reduce_mean(tf.square(y_true_outputs[:, 2] - y_pred_outputs[:, 2])))

    def mae_radius(self, y_true, y_pred):
        y_pred_outputs = y_pred[:, :3]
        y_true_outputs = y_true[:, :3]
        y_pred_outputs = y_pred_outputs * (self.output_maxs - self.output_mins + 1e-8) + self.output_mins
        y_true_outputs = y_true_outputs * (self.output_maxs - self.output_mins + 1e-8) + self.output_mins
        return tf.reduce_mean(tf.abs(y_true_outputs[:, 0] - y_pred_outputs[:, 0]))

    def mae_entropy(self, y_true, y_pred):
        y_pred_outputs = y_pred[:, :3]
        y_true_outputs = y_true[:, :3]
        y_pred_outputs = y_pred_outputs * (self.output_maxs - self.output_mins + 1e-8) + self.output_mins
        y_true_outputs = y_true_outputs * (self.output_maxs - self.output_mins + 1e-8) + self.output_mins
        return tf.reduce_mean(tf.abs(y_true_outputs[:, 1] - y_pred_outputs[:, 1]))

    def mae_fs(self, y_true, y_pred):
        y_pred_outputs = y_pred[:, :3]
        y_true_outputs = y_true[:, :3]
        y_pred_outputs = y_pred_outputs * (self.output_maxs - self.output_mins + 1e-8) + self.output_mins
        y_true_outputs = y_true_outputs * (self.output_maxs - self.output_mins + 1e-8) + self.output_mins
        return tf.reduce_mean(tf.abs(y_true_outputs[:, 2] - y_pred_outputs[:, 2]))

    def r2_radius(self, y_true, y_pred):
        y_pred_outputs = y_pred[:, :3]
        y_true_outputs = y_true[:, :3]
        y_pred_outputs = y_pred_outputs * (self.output_maxs - self.output_mins + 1e-8) + self.output_mins
        y_true_outputs = y_true_outputs * (self.output_maxs - self.output_mins + 1e-8) + self.output_mins
        ss_res = tf.reduce_sum(tf.square(y_true_outputs[:, 0] - y_pred_outputs[:, 0]))
        ss_tot = tf.reduce_sum(tf.square(y_true_outputs[:, 0] - tf.reduce_mean(y_true_outputs[:, 0])))
        return 1 - ss_res / (ss_tot + 1e-7)  # Add epsilon to avoid division by zero

    def r2_entropy(self, y_true, y_pred):
        y_pred_outputs = y_pred[:, :3]
        y_true_outputs = y_true[:, :3]
        y_pred_outputs = y_pred_outputs * (self.output_maxs - self.output_mins + 1e-8) + self.output_mins
        y_true_outputs = y_true_outputs * (self.output_maxs - self.output_mins + 1e-8) + self.output_mins
        ss_res = tf.reduce_sum(tf.square(y_true_outputs[:, 1] - y_pred_outputs[:, 1]))
        ss_tot = tf.reduce_sum(tf.square(y_true_outputs[:, 1] - tf.reduce_mean(y_true_outputs[:, 1])))
        return 1 - ss_res / (ss_tot + 1e-7)

    def r2_fs(self, y_true, y_pred):
        y_pred_outputs = y_pred[:, :3]
        y_true_outputs = y_true[:, :3]
        y_pred_outputs = y_pred_outputs * (self.output_maxs - self.output_mins + 1e-8) + self.output_mins
        y_true_outputs = y_true_outputs * (self.output_maxs - self.output_mins + 1e-8) + self.output_mins
        ss_res = tf.reduce_sum(tf.square(y_true_outputs[:, 2] - y_pred_outputs[:, 2]))
        ss_tot = tf.reduce_sum(tf.square(y_true_outputs[:, 2] - tf.reduce_mean(y_true_outputs[:, 2])))
        return 1 - ss_res / (ss_tot + 1e-7)

    def r2_total(self, y_true, y_pred):
        y_pred_outputs = y_pred[:, :3]
        y_true_outputs = y_true[:, :3]
        ss_res = tf.reduce_sum(tf.square(y_true_outputs[:, 2] - y_pred_outputs[:, 2]))
        ss_tot = tf.reduce_sum(tf.square(y_true_outputs[:, 2] - tf.reduce_mean(y_true_outputs[:, 2])))
        r2_f = 1 - ss_res / (ss_tot + 1e-7)
        y_pred_outputs = y_pred[:, :3]
        y_true_outputs = y_true[:, :3]
        ss_res = tf.reduce_sum(tf.square(y_true_outputs[:, 1] - y_pred_outputs[:, 1]))
        ss_tot = tf.reduce_sum(tf.square(y_true_outputs[:, 1] - tf.reduce_mean(y_true_outputs[:,1])))
        r2_e = 1 - ss_res / (ss_tot + 1e-7)
        y_pred_outputs = y_pred[:, :3]
        y_true_outputs = y_true[:, :3]
        ss_res = tf.reduce_sum(tf.square(y_true_outputs[:, 0] - y_pred_outputs[:, 0]))
        ss_tot = tf.reduce_sum(tf.square(y_true_outputs[:, 0] - tf.reduce_mean(y_true_outputs[:,0])))
        r2_r = 1 - ss_res / (ss_tot + 1e-7)
        return (r2_f + r2_e + r2_r) / 3

    def combined_loss(self, y_true, y_pred):
        y_pred_outputs = y_pred[:, :3]
        y_pred_inputs = y_pred[:, 3:]
        y_true_outputs = y_true[:, :3]
        y_pred_inputs = y_pred_inputs * (self.input_maxs - self.input_mins + 1e-8) + self.input_mins
        y_pred_outputs = y_pred_outputs * (self.output_maxs - self.output_mins + 1e-8) + self.output_mins
        y_true_outputs = y_true_outputs * (self.output_maxs - self.output_mins + 1e-8) + self.output_mins
        # Original inputs
        mass = y_pred_inputs[:, 0] * M_EARTH
        CMF = y_pred_inputs[:, 1]
        Zenv = y_pred_inputs[:, 2]
        Zwater = y_pred_inputs[:, 3]
        Tsurf = y_pred_inputs[:, 4]
        Psurf = y_pred_inputs[:, 5] * P_PASCAL
        # Predicted outputs
        radius_pred = y_pred_outputs[:, 0] * R_EARTH
        entropy_pred = y_pred_outputs[:, 1]
        f_s_pred = y_pred_outputs[:, 2]
        # Original outputs
        radius_true = y_true_outputs[:, 0] * R_EARTH
        entropy_true = y_true_outputs[:, 1]
        f_s_true = y_true_outputs[:, 2]
        # ---------- Average density by mass/radius ----------
        rho_mean_pred = mass / (4.0 / 3.0 * tf.constant(PI) * tf.pow(radius_pred, 3))
        rho_mean_true = mass / (4.0 / 3.0 * tf.constant(PI) * tf.pow(radius_true, 3))
        # ---------- Composition density ----------
        rho_comp = (
            CMF * RHO_CORE +
            Zwater * RHO_WATER +
            Zenv * RHO_GAS +
            (1.0 - CMF - Zwater - Zenv) * RHO_MANTLE
        )
        # ---------- Surface gravity ----------
        g_surface_pred = G * mass / tf.square(radius_pred)
        g_surface_true = G * mass / tf.square(radius_pred)
        # ---------- Physical equations (residuals) ----------
        # Eq1: dP/dr ≈ -rho * g
        dP_dr_estimate_pred = -rho_mean_pred * g_surface_pred
        dP_dr_estimate_true = -rho_mean_true * g_surface_true
        loss_dpdr = tf.reduce_mean(tf.abs((Psurf / radius_pred - dP_dr_estimate_pred) - (Psurf / radius_true - dP_dr_estimate_true)))
        # Eq2: dg/dr ≈ -4πGρ - 2Gm/r³
        dg_dr_estimate_pred = -4 * tf.constant(PI) * G * rho_mean_pred - 2 * G * mass / tf.pow(radius_pred, 3)
        dg_dr_estimate_true = -4 * tf.constant(PI) * G * rho_mean_true - 2 * G * mass / tf.pow(radius_pred, 3)
        loss_dgdr = tf.reduce_mean(tf.abs(dg_dr_estimate_pred - dg_dr_estimate_true))
        # Eq3: dT/dr ≈ -g γT/φ, using γ ≈ entropy * escalar
        gamma_pred = entropy_pred * GAMMA_SCALING
        gamma_true = entropy_true * GAMMA_SCALING
        phi_pred = Psurf / (rho_mean_pred + 1e-6)
        phi_true = Psurf / (rho_mean_true + 1e-6)
        dT_dr_estimate_pred = -g_surface_pred * gamma_pred * Tsurf / (phi_pred + 1e-6)
        dT_dr_estimate_true = -g_surface_true * gamma_true * Tsurf / (phi_true + 1e-6)
        loss_dTdr = tf.reduce_mean(tf.abs(dT_dr_estimate_pred - dT_dr_estimate_true))
        # Eq6: dm/dr ≈ 4πr²ρ
        dm_dr_estimate_pred = 4.0 * tf.constant(PI) * tf.square(radius_pred) * rho_mean_pred
        dm_dr_estimate_true = 4.0 * tf.constant(PI) * tf.square(radius_true) * rho_mean_true
        loss_dmdr = tf.reduce_mean(tf.abs((mass / radius_pred - dm_dr_estimate_pred) - (mass / radius_true - dm_dr_estimate_true)))
        # Densities consistency (estimated by percents of composition vs mass/radius densities)
        loss_rho_match = tf.reduce_mean(tf.abs((rho_mean_pred - rho_comp) - (rho_mean_true - rho_comp)))
        # MSE
        radius_mse_outputs = tf.reduce_mean(tf.square(radius_true - radius_pred))
        entropy_mse_outputs = tf.reduce_mean(tf.square(entropy_true - entropy_pred))
        f_s_mae_outputs = tf.reduce_mean(tf.abs(f_s_true - f_s_pred))
        print(f'{radius_mse_outputs} {entropy_mse_outputs} {f_s_mae_outputs}')
        total_loss = radius_mse_outputs + entropy_mse_outputs + f_s_mae_outputs
        # total_loss = (
        #     total_loss +
        #     0.2 * loss_dpdr +
        #     0.2 * loss_dgdr +
        #     0.2 * loss_dTdr +
        #     0.2 * loss_dmdr +
        #     0.2 * loss_rho_match
        # )
        return total_loss

class StandardizeMinMaxScaler:
    def __init__(self):
        self.mean_ = None
        self.std_ = None
        self.min_ = None
        self.max_ = None

    def fit(self, data):
        self.mean_ = np.nanmean(data, axis=0)
        self.std_ = np.nanstd(data, axis=0)
        standardized = (data - self.mean_) / (self.std_ + 1e-8)
        self.min_ = np.nanmin(standardized, axis=0)
        self.max_ = np.nanmax(standardized, axis=0)

    def transform(self, data):
        standardized = (data - self.mean_) / (self.std_ + 1e-8)
        scaled = (standardized - self.min_) / (self.max_ - self.min_ + 1e-8)
        indices = np.argwhere(scaled == 0.0).flatten()
        scaled[indices] = 1e-8
        indices = np.argwhere(scaled == 1.0).flatten()
        scaled[indices] = 1 - 1e-8
        return scaled

    def inverse_transform(self, data_scaled):
        standardized = data_scaled * (self.max_ - self.min_ + 1e-8) + self.min_
        original = standardized * (self.std_ + 1e-8) + self.mean_
        return original

class MinMaxScaler:
    def __init__(self):
        self.mean_ = None
        self.std_ = None
        self.min_ = None
        self.max_ = None

    def fit(self, data):
        self.min_ = np.nanmin(data, axis=0)
        self.max_ = np.nanmax(data, axis=0)

    def transform(self, data):
        scaled = (data - self.min_) / (self.max_ - self.min_ + 1e-8)
        indices = np.argwhere(scaled == 0.0).flatten()
        scaled[indices] = 1e-8
        indices = np.argwhere(scaled == 1.0).flatten()
        scaled[indices] = 1 - 1e-8
        return scaled

    def inverse_transform(self, data_scaled):
        return data_scaled * (self.max_ - self.min_ + 1e-8) + self.min_

class StandardizeScaler:
    def __init__(self):
        self.mean_ = None
        self.std_ = None

    def fit(self, data):
        self.mean_ = np.nanmean(data, axis=0)
        self.std_ = np.nanstd(data, axis=0)

    def transform(self, data):
        return (data - self.mean_) / (self.std_ + 1e-8)

    def inverse_transform(self, data_scaled):
        return data_scaled * (self.std_ + 1e-8) + self.mean_


