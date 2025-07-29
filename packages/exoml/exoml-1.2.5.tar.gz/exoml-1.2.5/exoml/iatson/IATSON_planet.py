import logging
import os
import pickle

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import keras
import tensorflow as tf
from keras.layers import LeakyReLU, Dropout
from keras.metrics import RecallAtPrecision
from mpl_toolkits.axes_grid1 import make_axes_locatable
from sklearn.isotonic import IsotonicRegression

from sklearn.linear_model import LogisticRegression
from sklearn.utils import shuffle
from astropy import units as u

from exoml.ete6.ete6_generator import Ete6ModelGenerator
from exoml.iatson.iatson_planet_generator import IatsonPlanetModelGenerator
from exoml.iatson.watson_planet_generator import WatsonPlanetModelGenerator
from exoml.ml.calibration.calibrator import PlattCalibrator
from exoml.ml.layers.branch_dropout import BranchDropoutLayer
from exoml.ml.layers.random_reverse import RandomReverseLayer
from exoml.ml.layers.transformer_classifier import TransformerClassifier
from exoml.ml.metrics.auc import ThresholdAtPrecision, ThresholdAtRecall, SpecificityAtNPV, NegativePredictiveValue, \
    ThresholdAtNPV, Specificity
from exoml.ml.model.base_model import CategoricalPredictionSetStats
from exoml.ml.model.imbalanced_binary_model import ImbalancedBinaryModel


class IATSON_planet(ImbalancedBinaryModel):
    def __init__(self, class_ids, class_names, type_to_label, hyperparams, channels=1, name='IATSON_planet',
                 mode=['q1q17', 'ete6', 'with_tce_candidates', 'no_val', 'with_radius']) -> None:
        super().__init__(name,
                         [11, 9 * 15, 300, 75, 75, 75, 75, 75, 75],
                         class_ids,
                         type_to_label,
                         hyperparams)
        self.channels = channels
        self.mode = mode

    def _get_flux_transformer_branch(self, name, transformer_blocks=2, transformer_heads=2):
        leaky_relu_alpha = 0.01
        # TODO use binning error as channel
        flux_input = keras.Input(shape=(self.input_size[2], self.channels), name=name)
        #flux_err_input = keras.Input(shape=(self.input_size[2], self.channels), name=name + "_err")
        #flux_input_mod = keras.layers.Dropout(self.hyperparams.dropout_rate)(flux_input)
        flux_input_mod = flux_input
        #flux_err_input_mod = keras.layers.Dropout(self.hyperparams.dropout_rate)(flux_err_input)
        if self.hyperparams.white_noise_std is not None:
            flux_input_mod = keras.layers.GaussianNoise(stddev=self.hyperparams.white_noise_std)(flux_input_mod)
            #flux_err_input_mod = keras.layers.GaussianNoise(stddev=self.hyperparams.white_noise_std)(flux_err_input_mod)
        #flux_input_final = keras.layers.concatenate([flux_input_mod, flux_err_input_mod], axis=2)
        flux_input_final = flux_input_mod
        transformer_input_size = self.input_size[2]
        transformer_output_size = self.input_size[2]
        kernel_size = 1
        classes = 128
        flux_branch = TransformerClassifier(transformer_input_size=transformer_input_size, patch_size=kernel_size,
                                            num_heads=transformer_heads, mlp_dim=transformer_output_size,
                                            hyperparams=self.hyperparams,
                                            num_blocks=transformer_blocks, classes=classes)(flux_input_final)
        flux_branch = keras.layers.Dense(64, name=f"{name}_dense_1", kernel_regularizer=tf.keras.regularizers.L1L2(l1=self.hyperparams.l1_regularization, l2=self.hyperparams.l2_regularization),
                                               activation=LeakyReLU(leaky_relu_alpha))(flux_branch)
        flux_branch = Dropout(self.hyperparams.dropout_rate)(flux_branch)
        flux_branch = keras.layers.LayerNormalization(epsilon=self.hyperparams.layer_norm_epsilon)(flux_branch)
        #return flux_input, flux_err_input, flux_branch
        return flux_input, flux_branch

    def _get_flux_conv_branch(self, name, channels=None):
        # (time, flux, [detrended_flux1 ... detrended_flux5], flux_model, centroidx, centroidy, motionx, motiony, bck)
        # flux model by transit params and stellar params
        # TODO use binning error as channel
        if not channels:
            channels = self.channels
        leaky_relu_alpha = 0.01
        flux_input = keras.Input(shape=(self.input_size[2], channels), name=name)
        flux_input_mod = flux_input
        #flux_err_input = keras.Input(shape=(self.input_size[2], channels), name=name + "_err")
        #flux_input_mod = keras.layers.Dropout(self.hyperparams.dropout_rate)(flux_input)
        #flux_err_input_mod = keras.layers.Dropout(self.hyperparams.dropout_rate)(flux_err_input)
        if self.hyperparams.white_noise_std is not None:
            flux_input_mod = keras.layers.GaussianNoise(stddev=self.hyperparams.white_noise_std, name="gn_flux")(flux_input_mod)
            #flux_err_input_mod = keras.layers.GaussianNoise(stddev=self.hyperparams.white_noise_std, name="gn_flux_err")(flux_err_input_mod)
        #flux_input_final = keras.layers.concatenate([flux_input_mod, flux_err_input_mod], axis=2)
        flux_input_final = flux_input_mod
        flux_branch = flux_input_final
        #flux_branch = keras.layers.normalization.batch_normalization.BatchNormalization()(flux_branch)
        flux_branch = keras.layers.Conv1D(name=name + '_1', filters=16, kernel_size=90, padding="same",
                                          kernel_regularizer=tf.keras.regularizers.L1L2(l1=self.hyperparams.l1_regularization_conv,
                                                                     l2=self.hyperparams.l2_regularization_conv),
                                          activation=LeakyReLU(leaky_relu_alpha))(flux_branch)
        flux_branch = keras.layers.MaxPooling1D(pool_size=10, strides=1)(flux_branch)
        #flux_branch = keras.layers.normalization.batch_normalization.BatchNormalization()(flux_branch)
        flux_branch = keras.layers.SpatialDropout1D(rate=self.hyperparams.spatial_dropout_rate)(flux_branch)
        flux_branch = keras.layers.Conv1D(name=name + '_2', filters=32, kernel_size=30, padding="same",
                                          kernel_regularizer=tf.keras.regularizers.L1L2(l1=self.hyperparams.l1_regularization_conv,
                                                                     l2=self.hyperparams.l2_regularization_conv),
                                          activation=LeakyReLU(leaky_relu_alpha))(flux_branch)
        flux_branch = keras.layers.MaxPooling1D(pool_size=4, strides=1)(flux_branch)
        #flux_branch = keras.layers.normalization.batch_normalization.BatchNormalization()(flux_branch)
        flux_branch = keras.layers.SpatialDropout1D(rate=self.hyperparams.spatial_dropout_rate)(flux_branch)
        flux_branch = keras.layers.Conv1D(name=name + '_3', filters=64, kernel_size=15, padding="same",
                                          kernel_regularizer=tf.keras.regularizers.L1L2(l1=self.hyperparams.l1_regularization_conv,
                                                                     l2=self.hyperparams.l2_regularization_conv),
                                          activation=LeakyReLU(leaky_relu_alpha))(flux_branch)
        flux_branch = keras.layers.MaxPooling1D(pool_size=3, strides=2)(flux_branch)
        #flux_branch = keras.layers.normalization.batch_normalization.BatchNormalization()(flux_branch)
        flux_branch = keras.layers.SpatialDropout1D(rate=self.hyperparams.spatial_dropout_rate)(flux_branch)
        flux_branch = keras.layers.Conv1D(name=name + '_4', filters=128, kernel_size=8, padding="same",
                                          kernel_regularizer=tf.keras.regularizers.L1L2(l1=self.hyperparams.l1_regularization_conv,
                                                                     l2=self.hyperparams.l2_regularization_conv),
                                          activation=LeakyReLU(leaky_relu_alpha))(flux_branch)
        flux_branch = keras.layers.MaxPooling1D(pool_size=2, strides=2)(flux_branch)
        return flux_input, flux_branch
        #return flux_input, flux_err_input, flux_branch

    def _get_flux_conv_model_branch(self, normalization_mode='layer_norm'):
        leaky_relu_alpha = 0.01
        flux_input, flux_branch = self._get_flux_conv_branch("global_flux_branch")
        flux_branch = keras.layers.Dense(64, kernel_regularizer=tf.keras.regularizers.L1L2(l1=self.hyperparams.l1_regularization, l2=self.hyperparams.l2_regularization),
                                         activation=LeakyReLU(leaky_relu_alpha))(flux_branch)
        flux_branch = Dropout(self.hyperparams.dropout_rate)(flux_branch)
        flux_branch = self._apply_normalization_mode(flux_branch, normalization_mode=normalization_mode)
        #flux_branch = keras.Model(inputs=[flux_input, flux_err_input], outputs=flux_branch)
        flux_branch = keras.Model(inputs=[flux_input], outputs=flux_branch)
        return flux_branch

    def _get_focus_flux_conv_branch(self, name, channels=None, additional_inputs=None, normalization_mode='layer_norm'):
        if not channels:
            channels = self.channels
        leaky_relu_alpha = 0.01
        # TODO use binning error as channel
        focus_flux_input = keras.Input(shape=(self.input_size[3], channels), name=name)
        focus_flux_input_mod = focus_flux_input
        focus_flux_input_mod = RandomReverseLayer(0.5)(focus_flux_input_mod)
        #focus_flux_err_input = keras.Input(shape=(self.input_size[3], channels), name=name + "_err")
        #focus_flux_input_mod = keras.layers.Dropout(self.hyperparams.dropout_rate)(focus_flux_input)
        #focus_flux_err_input_mod = keras.layers.Dropout(self.hyperparams.dropout_rate)(focus_flux_err_input)
        if self.hyperparams.white_noise_std is not None:
            focus_flux_input_mod = keras.layers.GaussianNoise(stddev=self.hyperparams.white_noise_std)(focus_flux_input_mod)
            #focus_flux_err_input_mod = keras.layers.GaussianNoise(stddev=self.hyperparams.white_noise_std)(focus_flux_err_input_mod)
        #focus_flux_input_final = keras.layers.concatenate([focus_flux_input_mod, focus_flux_err_input_mod], axis=2)
        focus_flux_input_final = focus_flux_input_mod
        focus_flux_branch = focus_flux_input_final
        #focus_flux_branch = keras.layers.normalization.batch_normalization.BatchNormalization()(focus_flux_input_final)
        # (time, flux, detrended_flux1... detrended_flux5, flux_model, centroidx, centroidy, motionx, motiony, bck)
        # flux model by transit params and stellar params
        #focus_flux_branch = keras.layers.SpatialDropout1D(rate=self.hyperparams.spatial_dropout_rate)(focus_flux_branch)
        focus_flux_branch = keras.layers.Conv1D(name=name + '_1', filters=32, kernel_size=20, padding="same",
                                          kernel_regularizer=tf.keras.regularizers.L1L2(l1=self.hyperparams.l1_regularization_conv,
                                                                     l2=self.hyperparams.l2_regularization_conv),
                                                activation=LeakyReLU(leaky_relu_alpha), use_bias=True)(
            focus_flux_branch)
        focus_flux_branch = keras.layers.MaxPooling1D(pool_size=5, strides=1)(focus_flux_branch)
        #focus_flux_branch = keras.layers.normalization.batch_normalization.BatchNormalization()(focus_flux_branch)
        focus_flux_branch = keras.layers.SpatialDropout1D(rate=self.hyperparams.spatial_dropout_rate)(focus_flux_branch)
        focus_flux_branch = keras.layers.Conv1D(name=name + '_2', filters=64, kernel_size=10, padding="same",
                                          kernel_regularizer=tf.keras.regularizers.L1L2(l1=self.hyperparams.l1_regularization_conv,
                                                                     l2=self.hyperparams.l2_regularization_conv),
                                                activation=LeakyReLU(leaky_relu_alpha), use_bias=True)(
            focus_flux_branch)
        #focus_flux_branch = keras.layers.normalization.batch_normalization.BatchNormalization()(focus_flux_branch)
        focus_flux_branch = keras.layers.MaxPooling1D(pool_size=3, strides=1)(focus_flux_branch)
        focus_flux_branch = keras.layers.SpatialDropout1D(rate=self.hyperparams.spatial_dropout_rate)(focus_flux_branch)
        focus_flux_branch = keras.layers.Conv1D(name=name + '_3', filters=128, kernel_size=5, padding="same",
                                          kernel_regularizer=tf.keras.regularizers.L1L2(l1=self.hyperparams.l1_regularization_conv,
                                                                     l2=self.hyperparams.l2_regularization_conv),
                                                activation=LeakyReLU(leaky_relu_alpha), use_bias=True)(
            focus_flux_branch)
        #focus_flux_branch = keras.layers.normalization.batch_normalization.BatchNormalization()(focus_flux_branch)
        focus_flux_branch = keras.layers.MaxPooling1D(pool_size=3, strides=1)(focus_flux_branch)
        focus_flux_branch = keras.layers.Flatten()(focus_flux_branch)
        if additional_inputs is not None:
            additional_inputs_branch = additional_inputs
            if self.hyperparams.numerical_white_noise_std is not None:
                additional_inputs_branch = keras.layers.GaussianNoise(stddev=self.hyperparams.numerical_white_noise_std)(additional_inputs_branch)
            focus_flux_branch = keras.layers.Concatenate(axis=1)([focus_flux_branch, keras.layers.Flatten()(additional_inputs_branch)])
        focus_flux_branch = keras.layers.Dense(64, kernel_regularizer=tf.keras.regularizers.L1L2(l1=self.hyperparams.l1_regularization, l2=self.hyperparams.l2_regularization),
                                               activation=LeakyReLU(leaky_relu_alpha))(focus_flux_branch)
        focus_flux_branch = Dropout(self.hyperparams.dropout_rate)(focus_flux_branch)
        focus_flux_branch = self._apply_normalization_mode(focus_flux_branch, normalization_mode=normalization_mode)
        focus_flux_branch = BranchDropoutLayer(dropout_rate=self.hyperparams.branch_dropout_rate)(focus_flux_branch)
        return focus_flux_input, focus_flux_branch
        #return focus_flux_input, focus_flux_err_input, focus_flux_branch

    def _get_focus_flux_transformer_branch(self, name, transformer_blocks=6, transformer_heads=6, channels=None, additional_inputs=None):
        leaky_relu_alpha = 0.01
        # TODO use binning error as channel
        if channels is None:
            channels = self.channels
        focus_flux_input = keras.Input(shape=(self.input_size[3], channels), name=name)
        focus_flux_input_mod = focus_flux_input
        #focus_flux_err_input = keras.Input(shape=(self.input_size[3], self.channels), name=name + "_err")
        #focus_flux_input_mod = keras.layers.Dropout(self.hyperparams.dropout_rate)(focus_flux_input)
        #focus_flux_err_input_mod = keras.layers.Dropout(self.hyperparams.dropout_rate)(focus_flux_err_input)
        if self.hyperparams.white_noise_std is not None:
            focus_flux_input_mod = keras.layers.GaussianNoise(stddev=self.hyperparams.white_noise_std)(focus_flux_input_mod)
            #focus_flux_err_input_mod = keras.layers.GaussianNoise(stddev=self.hyperparams.white_noise_std)(focus_flux_err_input_mod)
        focus_flux_input_final = focus_flux_input_mod
        #focus_flux_input_final = keras.layers.concatenate([focus_flux_input_mod, focus_flux_err_input_mod], axis=2)
        transformer_input_size = self.input_size[3]
        transformer_output_size = self.input_size[3]
        kernel_size = 1
        classes = 128
        flux_branch = TransformerClassifier(transformer_input_size=transformer_input_size, patch_size=kernel_size,
                              num_heads=transformer_heads, mlp_dim=transformer_output_size, hyperparams=self.hyperparams,
                              num_blocks=transformer_blocks, classes=classes)(focus_flux_input_final)
        flux_branch = keras.layers.Flatten()(flux_branch)
        if additional_inputs is not None:
            additional_inputs_branch = additional_inputs
            if self.hyperparams.numerical_white_noise_std is not None:
                additional_inputs_branch = keras.layers.GaussianNoise(stddev=self.hyperparams.numerical_white_noise_std)(additional_inputs_branch)
            flux_branch = keras.layers.Concatenate(axis=1)([flux_branch, keras.layers.Flatten()(additional_inputs_branch)])
        flux_branch = keras.layers.Dense(64, name=f"{name}_dense_1", kernel_regularizer=tf.keras.regularizers.L1L2(l1=self.hyperparams.l1_regularization, l2=self.hyperparams.l2_regularization),
                                               activation=LeakyReLU(leaky_relu_alpha))(flux_branch)
        flux_branch = Dropout(self.hyperparams.dropout_rate)(flux_branch)
        flux_branch = keras.layers.LayerNormalization(epsilon=self.hyperparams.layer_norm_epsilon)(flux_branch)
        return focus_flux_input, flux_branch
        #return focus_flux_input, focus_flux_err_input, flux_branch

    def _get_focus_flux_conv_model_branch(self, transit_params_input, normalization_mode='layer_norm'):
        leaky_relu_alpha = 0.01
        # odd_flux_input, odd_flux_err_input, odd_flux_branch = self._get_focus_flux_conv_branch("focus_odd_flux_branch")
        # even_flux_input, even_flux_err_input, even_flux_branch = self._get_focus_flux_conv_branch(
        #     "focus_even_flux_branch")
        # harmonic_odd_flux_input, harmonic_odd_flux_err_input, harmonic_odd_flux_branch = \
        #     self._get_focus_flux_conv_branch("focus_harmonic_odd_flux_branch")
        # harmonic_even_flux_input, harmonic_even_flux_err_input, harmonic_even_flux_branch = \
        #     self._get_focus_flux_conv_branch("focus_harmonic_even_flux_branch")
        # subharmonic_odd_flux_input, subharmonic_odd_flux_err_input, subharmonic_odd_flux_branch = \
        #     self._get_focus_flux_conv_branch("focus_subharmonic_odd_flux_branch")
        # subharmonic_even_flux_input, subharmonic_even_flux_err_input, subharmonic_even_flux_branch = \
        #     self._get_focus_flux_conv_branch("focus_subharmonic_even_flux_branch")
        odd_flux_input, odd_flux_branch = self._get_focus_flux_conv_branch("focus_odd_flux_branch",
                                                                           additional_inputs=transit_params_input, normalization_mode=normalization_mode)
        even_flux_input, even_flux_branch = self._get_focus_flux_conv_branch("focus_even_flux_branch",
                                                                             additional_inputs=transit_params_input, normalization_mode=normalization_mode)
        harmonic_odd_flux_input, harmonic_odd_flux_branch = \
            self._get_focus_flux_conv_branch("focus_harmonic_odd_flux_branch",
                                             additional_inputs=transit_params_input, normalization_mode=normalization_mode)
        harmonic_even_flux_input, harmonic_even_flux_branch = \
            self._get_focus_flux_conv_branch("focus_harmonic_even_flux_branch",
                                             additional_inputs=transit_params_input, normalization_mode=normalization_mode)
        # subharmonic_odd_flux_input, subharmonic_odd_flux_branch = \
        #     self._get_focus_flux_conv_branch("focus_subharmonic_odd_flux_branch")
        # subharmonic_even_flux_input, subharmonic_even_flux_branch = \
        #     self._get_focus_flux_conv_branch("focus_subharmonic_even_flux_branch")
        flux_branch = keras.layers.Add()(
            [odd_flux_branch, even_flux_branch])#, subharmonic_odd_flux_branch])
        har_flux_branch = keras.layers.Add()(
            [harmonic_odd_flux_branch, harmonic_even_flux_branch])#, subharmonic_even_flux_branch])
        # odd_flux_branch = keras.layers.Dense(16, kernel_regularizer=tf.keras.regularizers.L1L2(l1=self.hyperparams.l1_regularization, l2=self.hyperparams.l2_regularization),
        #                                      activation=LeakyReLU(leaky_relu_alpha))(odd_flux_branch)
        # odd_flux_branch = keras.layers.Dropout(rate=self.hyperparams.dropout_rate)(odd_flux_branch)
        # even_flux_branch = keras.layers.Dense(16, kernel_regularizer=tf.keras.regularizers.L1L2(l1=self.hyperparams.l1_regularization, l2=self.hyperparams.l2_regularization),
        #                                       activation=LeakyReLU(leaky_relu_alpha))(even_flux_branch)
        # even_flux_branch = keras.layers.Dropout(rate=self.hyperparams.dropout_rate)(even_flux_branch)
        # odd_flux_branch = keras.layers.Dense(32, kernel_regularizer=tf.keras.regularizers.L1L2(l1=self.hyperparams.l1_regularization, l2=self.hyperparams.l2_regularization),
        #                                      activation='linear')(odd_flux_branch)
        # even_flux_branch = keras.layers.Dense(32, kernel_regularizer=tf.keras.regularizers.L1L2(l1=self.hyperparams.l1_regularization, l2=self.hyperparams.l2_regularization),
        #                                       activation='linear')(even_flux_branch)
        # odd_flux_branch = keras.layers.LayerNormalization()(odd_flux_branch)
        # even_flux_branch = keras.layers.LayerNormalization()(even_flux_branch)
        focus_flux_branch = keras.layers.Add()([flux_branch, har_flux_branch])
        # focus_flux_branch = keras.layers.Dense(24, kernel_regularizer=tf.keras.regularizers.L1L2(l1=self.hyperparams.l1_regularization, l2=self.hyperparams.l2_regularization),
        #                                        activation=LeakyReLU(leaky_relu_alpha))(focus_flux_branch)
        # focus_flux_branch = keras.layers.Dropout(rate=self.hyperparams.dropout_rate)(focus_flux_branch)
        # focus_flux_branch = keras.layers.Dense(16, kernel_regularizer=tf.keras.regularizers.L1L2(l1=self.hyperparams.l1_regularization, l2=self.hyperparams.l2_regularization),
        #                                        activation='linear')(focus_flux_branch)
        input = [even_flux_input, odd_flux_input, #subharmonic_even_flux_input, subharmonic_odd_flux_input,
                 harmonic_even_flux_input, harmonic_odd_flux_input]
        # input = [even_flux_input, even_flux_err_input, odd_flux_input, odd_flux_err_input,
        #          subharmonic_even_flux_input, subharmonic_even_flux_err_input, subharmonic_odd_flux_input,
        #          subharmonic_odd_flux_err_input, harmonic_even_flux_input, harmonic_even_flux_err_input,
        #          harmonic_odd_flux_input, harmonic_odd_flux_err_input]
        return input, focus_flux_branch

    def _get_focus_flux_transformer_model_branch(self, transformer_blocks=6, transformer_heads=6, transit_params_input=None):
        leaky_relu_alpha = 0.01
        # odd_flux_input, odd_flux_err_input, odd_flux_branch = self._get_focus_flux_transformer_branch("focus_odd_flux_branch")
        # even_flux_input, even_flux_err_input, even_flux_branch = self._get_focus_flux_transformer_branch("focus_even_flux_branch")
        # harmonic_odd_flux_input, harmonic_odd_flux_err_input, harmonic_odd_flux_branch = \
        #     self._get_focus_flux_transformer_branch("focus_harmonic_odd_flux_branch", transformer_blocks,
        #                                             transformer_heads)
        # harmonic_even_flux_input, harmonic_even_flux_err_input, harmonic_even_flux_branch = \
        #     self._get_focus_flux_transformer_branch("focus_harmonic_even_flux_branch", transformer_blocks,
        #                                             transformer_heads)
        # subharmonic_odd_flux_input, subharmonic_odd_flux_err_input, subharmonic_odd_flux_branch = \
        #     self._get_focus_flux_transformer_branch("focus_subharmonic_odd_flux_branch", transformer_blocks,
        #                                             transformer_heads)
        # subharmonic_even_flux_input, subharmonic_even_flux_err_input, subharmonic_even_flux_branch = \
        #     self._get_focus_flux_transformer_branch("focus_subharmonic_even_flux_branch", transformer_blocks,
        #                                             transformer_heads)
        odd_flux_input, odd_flux_branch = self._get_focus_flux_transformer_branch(
            "focus_odd_flux_branch", transformer_blocks, transformer_heads, additional_inputs=transit_params_input)
        even_flux_input, even_flux_branch = self._get_focus_flux_transformer_branch(
            "focus_even_flux_branch", transformer_blocks, transformer_heads, additional_inputs=transit_params_input)
        harmonic_odd_flux_input, harmonic_odd_flux_branch = \
            self._get_focus_flux_transformer_branch("focus_harmonic_odd_flux_branch", transformer_blocks,
                                                    transformer_heads)
        harmonic_even_flux_input, harmonic_even_flux_branch = \
            self._get_focus_flux_transformer_branch("focus_harmonic_even_flux_branch", transformer_blocks,
                                                    transformer_heads)
        # subharmonic_odd_flux_input, subharmonic_odd_flux_branch = \
        #     self._get_focus_flux_transformer_branch("focus_subharmonic_odd_flux_branch", transformer_blocks,
        #                                             transformer_heads)
        # subharmonic_even_flux_input, subharmonic_even_flux_branch = \
        #     self._get_focus_flux_transformer_branch("focus_subharmonic_even_flux_branch", transformer_blocks,
        #                                             transformer_heads)
        odd_flux_branch = keras.layers.Add()(
            [odd_flux_branch, harmonic_odd_flux_branch])#, subharmonic_odd_flux_branch])
        even_flux_branch = keras.layers.Add()(
            [even_flux_branch, harmonic_even_flux_branch])#, subharmonic_even_flux_branch])
        focus_flux_branch = keras.layers.Add()([odd_flux_branch, even_flux_branch])
        # input = [even_flux_input, even_flux_err_input, odd_flux_input, odd_flux_err_input,
        #          subharmonic_even_flux_input, subharmonic_even_flux_err_input, subharmonic_odd_flux_input,
        #          subharmonic_odd_flux_err_input, harmonic_even_flux_input, harmonic_even_flux_err_input,
        #          harmonic_odd_flux_input, harmonic_odd_flux_err_input]
        input = [even_flux_input, odd_flux_input, #subharmonic_even_flux_input, subharmonic_odd_flux_input,
                 harmonic_even_flux_input, harmonic_odd_flux_input]
        return input, focus_flux_branch

    def build(self, use_transformers=False, transformer_blocks=6, transformer_heads=6, normalization_mode='layer_norm'):
        inputs, final_branch = self.build_transformer(transformer_blocks, transformer_heads) \
            if use_transformers else self.build_convolutional(normalization_mode=normalization_mode)
        self.set_model(keras.Model(inputs=inputs, outputs=final_branch, name=self.name))
        return self

    def build_convolutional(self, normalization_mode='layer_norm'):
        leaky_relu_alpha = 0.01
        transit_params_input = keras.Input(shape=(9, 1), name="transit_params")
        offset_params_input = keras.Input(shape=(1, 1), name="offset_params")
        # transit_params_input = None
        # offset_params_input = None
        stellar_model_input = keras.Input(shape=(2, 1), name="stellar_model")
        stellar_model_branch = stellar_model_input
        if self.hyperparams.numerical_white_noise_std is not None:
            stellar_model_branch = keras.layers.GaussianNoise(stddev=self.hyperparams.numerical_white_noise_std)(stellar_model_branch)
        # (TEFF, lum, 4 magnitudes, distance, radius, mass) * 15 stars
        # stellar_neighbours_input = keras.Input(shape=(9 * 15, 1), name="stellar_neighbours_model")
        # stellar_neighbours_branch = keras.layers.Dense(100, kernel_regularizer=tf.keras.regularizers.L1L2(l1=self.hyperparams.l1_regularization, l2=self.hyperparams.l2_regularization),
        #                                                activation=LeakyReLU(leaky_relu_alpha),
        #                                                name="stellar-neighbours-1")(
        #     stellar_neighbours_input)
        # stellar_neighbours_branch = keras.layers.Dropout(rate=self.hyperparams.dropout_rate,
        #                                                  name="stellar-neighbours-1-dropout")(
        #     stellar_neighbours_branch)
        # stellar_neighbours_branch = keras.layers.Dense(50, kernel_regularizer=tf.keras.regularizers.L1L2(l1=self.hyperparams.l1_regularization, l2=self.hyperparams.l2_regularization),
        #                                                activation=LeakyReLU(leaky_relu_alpha),
        #                                                name="stellar-neighbours-2")(
        #     stellar_neighbours_branch)
        # stellar_neighbours_branch = keras.layers.Dropout(rate=self.hyperparams.dropout_rate,
        #                                                  name="stellar-neighbours-2-dropout")(
        #     stellar_neighbours_branch)
        # stellar_neighbours_branch = keras.layers.Dense(16, kernel_regularizer=tf.keras.regularizers.L1L2(l1=self.hyperparams.l1_regularization, l2=self.hyperparams.l2_regularization),
        #                                                activation=LeakyReLU(leaky_relu_alpha),
        #                                                name="stellar-neighbours_3")(
        #     stellar_neighbours_branch)
        flux_model_branch = self._get_flux_conv_model_branch()
        focus_flux_model_input, focus_flux_model_branch = self._get_focus_flux_conv_model_branch(transit_params_input)
        #centroids_input, centroids_err_input, centroids_branch = self._get_focus_flux_conv_branch("centroids_branch", 3)
        centroids_input, centroids_branch = self._get_focus_flux_conv_branch("centroids_branch", 2,
                                                                             offset_params_input, normalization_mode=normalization_mode)
        # centroids_inputs = [centroids_input, centroids_err_input]
        # og_input, og_err_input, og_branch = self._get_focus_flux_conv_branch("og_branch", 2)
        og_input, og_branch = self._get_focus_flux_conv_branch("og_branch", 1, normalization_mode=normalization_mode)
        # og_inputs = [og_input, og_err_input]
        # final_branch = keras.layers.Concatenate(axis=-1)(
        #     [stellar_model_branch,
        #      #stellar_neighbours_branch,
        #      flux_model_branch.output, focus_flux_model_branch,
        #      centroids_branch, og_branch])
        # final_branch = keras.layers.GlobalMaxPooling1D()(final_branch)
        final_branch = keras.layers.Concatenate(axis=-1)(
            [keras.layers.Flatten()(stellar_model_branch),
             # stellar_neighbours_branch,
             keras.layers.Flatten()(flux_model_branch.output),
             keras.layers.Flatten()(focus_flux_model_branch),
             keras.layers.Flatten()(centroids_branch),
             keras.layers.Flatten()(og_branch)])
        final_branch = keras.layers.Dense(1000, kernel_regularizer=tf.keras.regularizers.L1L2(l1=self.hyperparams.l1_regularization, l2=self.hyperparams.l2_regularization),
                                         activation=LeakyReLU(leaky_relu_alpha), name="final-dense2")(final_branch)
        final_branch = Dropout(rate=self.hyperparams.dropout_rate, name="final-dropout2")(final_branch)
        final_branch = keras.layers.Dense(250, kernel_regularizer=tf.keras.regularizers.L1L2(l1=self.hyperparams.l1_regularization, l2=self.hyperparams.l2_regularization),
                                         activation=LeakyReLU(leaky_relu_alpha), name="final-dense3")(final_branch)
        final_branch = Dropout(self.hyperparams.dropout_rate, name="final-dropout3")(final_branch)
        final_branch = keras.layers.Dense(75, kernel_regularizer=tf.keras.regularizers.L1L2(l1=self.hyperparams.l1_regularization, l2=self.hyperparams.l2_regularization),
                                          activation=LeakyReLU(leaky_relu_alpha), name="final-dense4")(final_branch)
        final_branch = Dropout(self.hyperparams.dropout_rate, name="final-dropout4")(final_branch)
        final_branch = keras.layers.Dense(35, kernel_regularizer=tf.keras.regularizers.L1L2(l1=self.hyperparams.l1_regularization, l2=self.hyperparams.l2_regularization),
                                         activation=LeakyReLU(leaky_relu_alpha), name="final-dense5")(final_branch)
        final_branch = Dropout(self.hyperparams.dropout_rate, name="final-dropout5")(final_branch)
        final_branch = keras.layers.Dense(16, kernel_regularizer=tf.keras.regularizers.L1L2(l1=self.hyperparams.l1_regularization, l2=self.hyperparams.l2_regularization),
                                          activation=LeakyReLU(leaky_relu_alpha), name="final-dense6")(final_branch)
        final_branch = Dropout(self.hyperparams.dropout_rate, name="final-dropout6")(final_branch)
        final_branch = keras.layers.Dense(1, activation="sigmoid", name="logits")(final_branch)
        # inputs = [stellar_model_input, stellar_neighbours_input] + \
        #                  flux_model_branch.inputs + focus_flux_model_branch.inputs + \
        #                  centroids_inputs + og_inputs
        inputs = []
        if transit_params_input is not None:
            inputs = inputs + [transit_params_input]
        if offset_params_input is not None:
            inputs = inputs + [offset_params_input]
        # inputs = inputs + [stellar_model_input] + \
        #          [focus_flux_model_input] + \
        #          [centroids_input, og_input]
        inputs = inputs + [stellar_model_input] + \
                 flux_model_branch.inputs + \
                 [focus_flux_model_input] + \
                 [centroids_input, og_input]
        return inputs, final_branch

    def build_transformer(self, transformer_blocks=6, transformer_heads=6):
        leaky_relu_alpha = 0.01
        transit_params_input = keras.Input(shape=(6, 1), name="transit_params")
        offset_params_input = keras.Input(shape=(1, 1), name="offset_params")
        stellar_model_input = keras.Input(shape=(2, 1), name="stellar_model")
        stellar_model_branch = stellar_model_input
        #(TEFF, lum, 4 magnitudes, distance, radius, mass) * 15 stars
        # stellar_neighbours_input = keras.Input(shape=(9 * 15, 1), name="stellar_neighbours_model")
        # stellar_neighbours_branch = keras.layers.Dense(100, kernel_regularizer=tf.keras.regularizers.L1L2(l1=self.hyperparams.l1_regularization, l2=self.hyperparams.l2_regularization),
        #                                                activation=LeakyReLU(leaky_relu_alpha), name="stellar-neighbours-1")(stellar_neighbours_input)
        # stellar_neighbours_branch = keras.layers.Dropout(rate=self.hyperparams.dropout_rate,
        #                                                  name="stellar-neighbours-1-dropout-0.1")\
        #     (stellar_neighbours_branch)
        # stellar_neighbours_branch = keras.layers.Dense(50, kernel_regularizer=tf.keras.regularizers.L1L2(l1=self.hyperparams.l1_regularization, l2=self.hyperparams.l2_regularization),
        #                                                activation=LeakyReLU(leaky_relu_alpha), name="stellar-neighbours-2")(
        #     stellar_neighbours_branch)
        # stellar_neighbours_branch = keras.layers.Dropout(rate=self.hyperparams.dropout_rate,
        #                                                  name="stellar-neighbours-2-dropout-0.1")\
        #     (stellar_neighbours_branch)
        # stellar_neighbours_branch = keras.layers.Dense(16, activation=LeakyReLU(leaky_relu_alpha),
        #                                                kernel_regularizer=tf.keras.regularizers.L1L2(l1=self.hyperparams.l1_regularization, l2=self.hyperparams.l2_regularization),
        #                                                name="stellar-neighbours_3")(stellar_neighbours_branch)
        # flux_model_input, flux_model_err_input, flux_model_branch = \
        #     self._get_flux_transformer_branch("global_flux_branch", transformer_blocks, transformer_heads)

        if self.hyperparams.numerical_white_noise_std is not None:
            stellar_model_branch = keras.layers.GaussianNoise(stddev=self.hyperparams.numerical_white_noise_std)(stellar_model_branch)
        flux_model_input, flux_model_branch = \
            self._get_flux_transformer_branch("global_flux_branch", transformer_blocks, transformer_heads)
        focus_flux_model_input, focus_flux_model_branch = \
            self._get_focus_flux_transformer_model_branch(transformer_blocks, transformer_heads, transit_params_input)
        #centroids_input, centroids_err_input, centroids_branch = self._get_focus_flux_conv_branch("centroids_branch", 3)
        centroids_input, centroids_branch = self._get_focus_flux_transformer_branch("centroids_branch",
                transformer_blocks, transformer_heads, additional_inputs=offset_params_input, channels=2)
        # og_input, og_err_input, og_branch = self._get_focus_flux_conv_branch("og_branch", 2)
        og_input, og_branch = self._get_focus_flux_transformer_branch("og_branch", transformer_blocks, transformer_heads, channels=1)
        final_branch = keras.layers.Concatenate(axis=-1, name="concat-final")(
            [keras.layers.Flatten()(stellar_model_branch),
             # stellar_neighbours_branch,
             keras.layers.Flatten()(flux_model_branch),
             keras.layers.Flatten()(focus_flux_model_branch),
             keras.layers.Flatten()(centroids_branch),
             keras.layers.Flatten()(og_branch)])
        final_branch = keras.layers.Dense(1000, kernel_regularizer=tf.keras.regularizers.L1L2(
            l1=self.hyperparams.l1_regularization, l2=self.hyperparams.l2_regularization),
                                          activation=LeakyReLU(leaky_relu_alpha), name="final-dense2")(final_branch)
        final_branch = Dropout(self.hyperparams.dropout_rate)(final_branch)
        final_branch = keras.layers.Dense(250, kernel_regularizer=tf.keras.regularizers.L1L2(
            l1=self.hyperparams.l1_regularization, l2=self.hyperparams.l2_regularization),
                                          activation=LeakyReLU(leaky_relu_alpha), name="final-dense3")(final_branch)
        final_branch = Dropout(self.hyperparams.dropout_rate)(final_branch)
        final_branch = keras.layers.Dense(75, kernel_regularizer=tf.keras.regularizers.L1L2(
            l1=self.hyperparams.l1_regularization, l2=self.hyperparams.l2_regularization),
                                          activation=LeakyReLU(leaky_relu_alpha), name="final-dense4")(final_branch)
        final_branch = Dropout(self.hyperparams.dropout_rate)(final_branch)
        final_branch = keras.layers.Dense(35, kernel_regularizer=tf.keras.regularizers.L1L2(
            l1=self.hyperparams.l1_regularization, l2=self.hyperparams.l2_regularization),
                                          activation=LeakyReLU(leaky_relu_alpha), name="final-dense5")(final_branch)
        final_branch = Dropout(self.hyperparams.dropout_rate)(final_branch)
        final_branch = keras.layers.Dense(16, kernel_regularizer=tf.keras.regularizers.L1L2(
            l1=self.hyperparams.l1_regularization, l2=self.hyperparams.l2_regularization),
                                          activation=LeakyReLU(leaky_relu_alpha), name="final-dense6")(final_branch)
        final_branch = Dropout(self.hyperparams.dropout_rate)(final_branch)
        final_branch = keras.layers.Dense(1, activation="sigmoid", name="logits")(final_branch)
        # inputs = [stellar_model_input, stellar_neighbours_input] + \
        #                  flux_model_branch.inputs + focus_flux_model_branch.inputs + \
        #                  centroids_inputs + og_inputs
        inputs = [transit_params_input, offset_params_input, stellar_model_input] + \
                 [flux_model_input, focus_flux_model_input] + \
                 [centroids_input, og_input]
        return inputs, final_branch

    def load_training_set(self, **kwargs):
        df = None
        training_dir = kwargs.get('training_dir')
        injected_objects_df_q1_q17_tces = pd.read_csv(training_dir + "/q1_q17/classified_tces.csv", index_col=None)
        injected_objects_df_ete6 = pd.read_csv(training_dir + "/ete6/injected_objects.csv", index_col=None)
        tess_df = pd.read_csv(training_dir + "/tess/tess_tois.csv", index_col=None)
        tess_df = tess_df.loc[~tess_df['object_id'].isin(["TIC 9837861",
        "TIC 114103136",
        "TIC 303867090",
        "TIC 365683032",
        "TIC 233059608",
        "TIC 349790953",
        "TIC 241102583",
        "TIC 124709665",
        "TIC 374847873",
        "TIC 244089109",
        "TIC 269450900",
        "TIC 317520667",
        "TIC 233602827",
        "TIC 367366318",
        "TIC 242460075",
        "TIC 98286422",
        "TIC 110178537",
        "TIC 305512837",
        "TIC 20892672",
        "TIC 167227214",
        "TIC 194179013",
        "TIC 16102323",
        "TIC 350153977",
        "TIC 23863106",
        "TIC 325670253",
        "TIC 183979262",
        "TIC 331034236",
        "TIC 387527558",
        "TIC 257060897",
        "TIC 284326455",
        "TIC 369861731",
        "TIC 15827263",
        "TIC 610976842",
        "TIC 24094603",
        "TIC 232038798",
        "TIC 1965256662",
        "TIC 229400092",
        "TIC 104866616",
        "TIC 376740324",
        "TIC 233602827",
        "TIC 429302040",
        "TIC 258777134",
        "TIC 387690507",
        "TIC 277987172",
        "TIC 290348382",
        "TIC 45684223",
        "TIC 155986102",
        "TIC 29830212",
        "TIC 468997317",
        "TIC 1717732429",
        "TIC 286696848",
        "TIC 219821826",
        "TIC 271749758",
        "TIC 139158696",
        "TIC 160162987",
        "TIC 1101909431",
        "TIC 235678745",
        "TIC 232982558",
        "TIC 269701147",
        "TIC 219854519",
        "TIC 230086768",
        "TIC 394029948",
        "TIC 374908020",
        "TIC 364075352",
        "TIC 29781292",
        "TIC 141488193",
        "TIC 157698565",
        "TIC 229742722",
        "TIC 466206508",
        "TIC 33878688",
        "TIC 164652245",
        "TIC 232608943",
        "TIC 55525572",
        "TIC 261257684",
        "TIC 29781292",
        "TIC 150151262",
        "TIC 367855829",
        "TIC 27769688",
        "TIC 349095149",
        "TIC 388130235",
        "TIC 260128333",
        "TIC 309792357",
        "TIC 209464063",
        "TIC 362220495",
        "TIC 224313733",
        "TIC 309402106",
        "TIC 349576261",
        "TIC 298663873",
        "TIC 307958020",
        "TIC 70887357",
        "TIC 251086776",
        "TIC 332630868",
        "TIC 434100688",
        "TIC 304142124",
        "TIC 150151262",
        "TIC 441739020",
        "TIC 350618622",
        "TIC 425163745",
        "TIC 146434840",
        "TIC 190430205",
        "TIC 329145325",
        "TIC 410528770",
        "TIC 420288086",
        "TIC 270333769"])]
        if 'ete6_period' in self.mode:
            logging.info("Removing ETE6 long periods")
            injected_objects_df_ete6 = injected_objects_df_ete6.loc[injected_objects_df_ete6['period'] < 20]
        q1q17_df = injected_objects_df_q1_q17_tces
        if 'q1q17_period' in self.mode:
            logging.info("Removing Q1Q17 long periods")
            q1q17_df = q1q17_df.loc[q1q17_df['period'] < 50]
        if 'no_close_period' in self.mode:
            logging.info("Removing close period signals")
            q1q17_df = q1q17_df.loc[(q1q17_df['close_period'] == 0)]
        if "q1q17" in self.mode and "no_val" in self.mode:
            logging.info("Removing validated signals")
            q1q17_df.loc[q1q17_df['disc_refname'].str.contains('Valizadegan', na=False), ['type']] = 'candidate'
            #q1q17_df.loc[q1q17_df['disc_refname'].str.contains('Armstrong et al. 2021', na=False), ['type']] = 'candidate'
        if 'q1q17' in self.mode and not 'with_kois_without_tce' in self.mode:
            logging.info("Removing signals without matching TCE")
            q1q17_df = q1q17_df.loc[q1q17_df['koi_without_tce'] != 1]
        #if 'q1q17' in self.mode and 'with_radius' in self.mode:
        #    q1q17_df = q1q17_df.loc[q1q17_df['type'] != 'planet']
        if 'q1q17' in self.mode and not 'with_ephemeris_contamination' in self.mode:
            q1q17_df = q1q17_df.loc[q1q17_df['ephemeris_contamination'] == 0]
        if 'q1q17' in self.mode:
            df = q1q17_df
        if 'ete6' in self.mode and df is not None:
            df = pd.concat([injected_objects_df_ete6, df])
        elif 'ete6' in self.mode:
            df = injected_objects_df_ete6
        if 'tess' in self.mode and df is not None:
            df = pd.concat([tess_df, df])
        elif 'tess' in self.mode:
            df = tess_df
        if 'with_radius' in self.mode:
            df = df[~df['radius(earth)'].isna()]
        include_categories = ['fa', 'planet', 'planet_transit', 'tce', 'tce_og', 'tce_secondary',
                              'tce_source_offset', 'tce_centroids_offset', 'tce_odd_even', 'EB', 'bckEB']
        if 'with_fp_candidates' in self.mode:
            include_categories = include_categories + ['fp_candidate']
        if 'with_tce_candidates' in self.mode:
            include_categories = include_categories + ['tce_candidate']
        if 'with_candidates' in self.mode:
            include_categories = include_categories + ['candidate']
        if 'with_fp' in self.mode:
            include_categories = include_categories + ['fp']
        if 'with_random_folded' in self.mode:
            include_categories = include_categories + ['none']
        df = df[df['type'].isin(include_categories)]
        df.reset_index(inplace=True, drop=True)
        return df

    def instance_generator(self, dataset, dir, batch_size, input_sizes, type_to_label, zero_epsilon, shuffle=True):
        return IatsonPlanetModelGenerator(dataset, dir, batch_size, input_sizes, type_to_label, zero_epsilon,
                                          shuffle_batch=shuffle)

    def predict(self, input, calibrator_path=None, batch_size=1):
        calibrator = self.load_calibrator(calibrator_path)
        dataset = input.get_dataset()
        dataset.batch(batch_size)
        prediction = self.model.predict(dataset, batch_size=batch_size, steps=len(input))
        prediction_cal = prediction
        if calibrator:
            prediction_cal = calibrator.predict(prediction)
        return prediction, prediction_cal

    def predict_cv(self, input, models_dir, calibrator_path=None, batch_size=1):
        models = os.listdir(models_dir)
        injected_objects_df = input.injected_objects_df
        predictions_df = pd.DataFrame(columns=['object_id', 'prediction_value', 'prediction_value_cal'])
        for model in sorted(models):
            if '_chk_' in model:
                model_dir = f'{models_dir}/{model}'
                calibrator = f"{model_dir}/{calibrator_path}" if calibrator_path is not None else None
                calibrator = self.load_calibrator(calibrator)
                self.load_model(model_dir + '/' + os.path.basename(model_dir) + '.h5')
                model_dir = f'{models_dir}/'
                prediction, _ = self.predict(input, batch_size=batch_size)
                input.plot_inputs = False
                prediction_cal = prediction
                if calibrator:
                    prediction_cal = calibrator.predict(prediction)
                iteration_predictions_df = pd.DataFrame(columns=['object_id', 'prediction_value', 'prediction_value_cal'])
                iteration_predictions_df['object_id'] = injected_objects_df['object_id']
                iteration_predictions_df['prediction_value'] = np.array(prediction).flatten().tolist()
                iteration_predictions_df['prediction_value_cal'] = prediction_cal.tolist()
                predictions_df = pd.concat([predictions_df, iteration_predictions_df])
        return predictions_df, injected_objects_df

    def predict_batch(self, input_generator: Ete6ModelGenerator, expected_outputs=None, dataset=None, training_dir=None, plot_mismatches=False,
                      batch_size=20, cores=os.cpu_count() - 1, threshold=[0.5], calibrator_path=None, explain=False):
        generator_dataset = input_generator.get_dataset()
        generator_dataset.batch(batch_size)
        predictions = self.model.predict(generator_dataset, batch_size=batch_size, steps=len(input_generator))
        calibrator = None
        if calibrator_path is not None:
            calibrator = self.load_calibrator(calibrator_path)
        predictions = calibrator.predict(predictions).tolist() if calibrator is not None \
            else predictions
        if len(np.array(predictions).shape) == 1:
            predictions = np.reshape(predictions, (np.array(predictions).shape[0], 1))
        max_prediction_indexes, max_prediction_values = self.predict_threshold(predictions, threshold)
        if expected_outputs is not None:
            planet_stats = self.test_metrics(expected_outputs, max_prediction_indexes, max_prediction_values, predictions,
                                             dataset if not explain else input_generator.injected_objects_df,
                                             training_dir=training_dir, plot_mismatches=plot_mismatches, explain=explain)
            if not explain:
                return max_prediction_indexes, max_prediction_values, [planet_stats]
            else:
                return max_prediction_indexes, max_prediction_values, [planet_stats] #TODO return explain df
        else:
            if not explain:
                return max_prediction_indexes, max_prediction_values
            else:
                return max_prediction_indexes, max_prediction_values  #TODO return explain df

    def predict_threshold(self, predictions, threshold=[0.5]):
        max_prediction_indexes = np.array([np.argmax(prediction) for prediction in predictions])
        max_prediction_values = np.array([predictions[index][max_prediction_index]
                                 if predictions[index][max_prediction_index] > threshold[max_prediction_index]
                                 else -1
                                 for index, max_prediction_index in enumerate(max_prediction_indexes)])
        max_prediction_indexes[np.argwhere(max_prediction_values < 0).flatten()] = -1
        return max_prediction_indexes, max_prediction_values

    def predict_df(self, df, training_dir, batch_size=20, cores=os.cpu_count() - 1, zero_epsilon=1e-7,
                   thresholds=[0.5], plot_mismatches=False, log=False, validation_df=None, from_arrays=False,
                   calibrator_path=None, explain=False):
        expected_outputs = None
        testing_batch_generator = IatsonPlanetModelGenerator(df, training_dir, batch_size,
                                                             self.input_size,
                                                             self.type_to_label, zero_epsilon, from_arrays=from_arrays,
                                                             shuffle_batch=False, validation_objects_df=validation_df,
                                                             explain=explain)
        for i in np.arange(0, len(df) // batch_size + 1, 1):
            input, expected_output = testing_batch_generator.__getitem__(i)
            expected_outputs = np.concatenate((expected_outputs, expected_output)) if expected_outputs is not None else expected_output
        prediction_stats_for_thresholds = {}
        max_prediction_indexes, max_prediction_values, prediction_stats = \
            self.predict_batch(testing_batch_generator, expected_outputs, df, training_dir, plot_mismatches,
                               batch_size, cores=cores, threshold=[0.5], calibrator_path=calibrator_path, explain=explain)
        for threshold in thresholds:
            prediction_stats_for_thresholds[threshold] = prediction_stats
            if log:
                prediction_stats = prediction_stats[0]
                logging.info("Prediction stats for label %.0f and threshold %s: TP=%.0f, FP=%.0f, FN=%.0f, ACC=%.3f, PRE=%.3f, REC=%.3f", 0,
                             threshold, prediction_stats.tp, prediction_stats.fp, prediction_stats.fn, prediction_stats.accuracy,
                             prediction_stats.precision, prediction_stats.recall)
                logging.info("Prediction stats @ k top predictions: \n%s", prediction_stats.k_df.to_string())
                mistmatches_df = prediction_stats.predictions_df[prediction_stats.predictions_df['expected_class'] !=
                                                                 prediction_stats.predictions_df['predicted_class']]
                logging.info("Mismatches: \n%s", mistmatches_df.to_string())
                logging.info("Mismatches by types: \n%s", mistmatches_df
                             .groupby(by=['type', 'predicted_class'])['object_id'].count().to_string())
        return prediction_stats_for_thresholds

    def predict_test_set(self, training_dir, model_dir, batch_size=20, cores=os.cpu_count() - 1, test_set_limit=None,
                         zero_epsilon=1e-7, plot_mismatches=False, test_dataset_filename='test_dataset.csv',
                         thresholds=[0.5], logs=False, additional_test_df=None, calibrator_path=None):
        test_dataset = pd.read_csv(model_dir + '/' + test_dataset_filename)
        if test_set_limit is not None:
            test_dataset = test_dataset.iloc[0:test_set_limit]
        if additional_test_df is not None:
            test_dataset = pd.concat([test_dataset, additional_test_df])
        expected_outputs = None
        testing_batch_generator = IatsonPlanetModelGenerator(test_dataset, training_dir, batch_size,
                                                             self.input_size,
                                                             self.type_to_label, zero_epsilon, from_arrays=True,
                                                             shuffle_batch=False)
        for i in np.arange(0, len(test_dataset) // batch_size + 1, 1):
            input, expected_output = testing_batch_generator.__getitem__(i)
            expected_outputs = np.concatenate((expected_outputs, expected_output)) if expected_outputs is not None else expected_output
        threshold_to_results = {}
        for threshold in thresholds:
            max_prediction_indexes, max_prediction_values, prediction_stats = \
                self.predict_batch(testing_batch_generator, expected_outputs, test_dataset, training_dir, plot_mismatches,
                                   batch_size, cores=cores, threshold=[threshold], calibrator_path=calibrator_path)
            prediction_stats = prediction_stats[0]
            threshold_to_results[threshold] = prediction_stats
            if logs:
                logging.info("Prediction stats for label %.0f and threshold %s: TP=%.0f, FP=%.0f, FN=%.0f, ACC=%.3f, PRE=%.3f, REC=%.3f", 0,
                             threshold, prediction_stats.tp, prediction_stats.fp, prediction_stats.fn, prediction_stats.accuracy,
                             prediction_stats.precision, prediction_stats.recall)
                logging.info("Prediction stats @ k top predictions: \n%s", prediction_stats.k_df.to_string())
                mistmatches_df = prediction_stats.predictions_df[prediction_stats.predictions_df['expected_class'] !=
                                                                 prediction_stats.predictions_df['predicted_class']]
                logging.info("Mismatches: \n%s", mistmatches_df.to_string())
                logging.info("Mismatches by types: \n%s", mistmatches_df
                             .groupby(by=['type', 'predicted_class'])['object_id'].count().to_string())
        return threshold_to_results

    def predict_test_set_cv(self, training_dir, model_dir_prefix, batch_size=20, cores=os.cpu_count() - 1,
                            test_set_limit=None,
                            zero_epsilon=1e-7, plot_mismatches=False, folds=10, thresholds=[0.5],
                            k_values=np.arange(100, 2200, 100),
                            additional_test_set_filename=None, calibration_method=None, calibrator_path=None):
        fold_thresholds_to_results = {}
        prediction_dfs_thresholds = None
        predictions_df = None
        rp99s = np.zeros(folds)
        threshold_p99s = np.zeros(folds)
        fold_indexes = None
        if additional_test_set_filename is not None:
            additional_test_df = pd.read_csv(additional_test_set_filename)
            #additional_test_df = additional_test_df[additional_test_df['object_id'] == 'KIC 4380558']
            additional_dataset_len = len(additional_test_df)
            fold_indexes = [int(fold_index) for fold_index in np.linspace(additional_dataset_len // folds, additional_dataset_len, folds)]
        additional_test_fold_df = None
        for index, fold in enumerate(np.arange(0, folds)):
            model_dir = f"{model_dir_prefix}_{fold}"
            self.load_model(model_dir + '/' + os.path.basename(model_dir) + '.h5')
            model_dir = model_dir + '/'
            if fold_indexes is not None:
                previous_fold_index = fold_indexes[index - 1] if index > 0 else 0
                additional_test_fold_df = additional_test_df.iloc[previous_fold_index:fold_indexes[index]]
            calibrator = f"{model_dir}{calibrator_path}" if calibrator_path is not None else None
            fold_thresholds_to_results[fold] = self.predict_test_set(training_dir, model_dir, batch_size, cores,
                                                                     test_set_limit, zero_epsilon,
                                                                     plot_mismatches,
                                                                     test_dataset_filename='validation_dataset.csv',
                                                                     thresholds=thresholds, logs=False,
                                                                     additional_test_df=additional_test_fold_df,
                                                                     calibrator_path=calibrator)
            for fold_threshold_to_results in fold_thresholds_to_results[fold].values():
                fold_threshold_to_results.predictions_df['fold'] = fold
            predictions_df = fold_thresholds_to_results[fold][thresholds[0]].predictions_df if predictions_df is None \
                else pd.concat([predictions_df, fold_thresholds_to_results[fold][thresholds[0]].predictions_df])
            if calibration_method:
                predictions_df.loc[predictions_df['fold'] == fold], _ = (
                    self.calibrate(predictions_df.loc[predictions_df['fold'] == fold], calibration_method,
                                                   calibrator_dir=f'{model_dir}/{self.name}'))
        predictions_df = predictions_df.sort_values(by=['prediction_value'], ascending=False)
        predictions_df_q1q17 = predictions_df[predictions_df['object_id'].str.contains("KIC")]
        #predictions_df_ete6 = predictions_df[predictions_df['object_id'].str.contains("TIC")]
        predictions_df_q1q17 = predictions_df_q1q17.sort_values(by=['prediction_value'], ascending=False)
        #predictions_df_ete6 = predictions_df_ete6.sort_values(by=['prediction_value'], ascending=False)
        logging.info("----------------------------------COMPLETE SET METRICS ---------------------------------------")
        rp100_thresholds, rp100_values = self.compute_metrics_p100(predictions_df, True)
        npv100_thresholds, np100_values = self.compute_metrics_npv100(predictions_df, True)
        rp_values = [0.95, 0.975, 0.99, 0.995, 0.999, 1.0]
        all_recalls, selected_rp_thresholds, all_precisions, selected_pr_thresholds, all_sensitivities, selected_snpv_thresholds = \
            self.compute_rp_thresholds(predictions_df, rp_values=rp_values, log=True)
        self.compute_metrics(predictions_df, thresholds=[float(np.squeeze(np.mean(selected_snpv_thresholds[4]))),
                                                         float(np.squeeze(np.mean(selected_snpv_thresholds[3]))),
                                                         float(np.squeeze(np.mean(selected_snpv_thresholds[2]))),
                                                         0.5,
                                                         float(np.squeeze(np.mean(selected_rp_thresholds[2]))),
                                                         float(np.squeeze(np.mean(selected_rp_thresholds[4])))], log=True)
        self.log_prediction_metrics(predictions_df, k_values, "K_METRICS_COMPLETE")
        #IATSON_planet.compute_statistics_map(fps_fns_df, './', filename=f"fps_fns_{message}_distribution", markersize=60)
        self.compute_rp_metrics(predictions_df, log=True)
        # self.compute_pr_thresholds(fold_thresholds_to_results, log=True)
        # self.compute_pr_metrics(predictions_df, log=True)
        # logging.info("----------------------------------Q1Q17 SET METRICS ---------------------------------------")
        # self.compute_metrics(predictions_df_q1q17, thresholds=[float(np.squeeze(np.mean(selected_snpv_thresholds[2]))),
        #                                                  float(np.squeeze(np.mean(selected_snpv_thresholds[3]))),
        #                                                  float(np.squeeze(np.mean(selected_snpv_thresholds[4]))),
        #                                                  0.5,
        #                                                  float(np.squeeze(np.mean(selected_rp_thresholds[2]))),
        #                                                  float(np.squeeze(np.mean(selected_rp_thresholds[4])))], log=True)
        # self.log_prediction_metrics(predictions_df_q1q17, k_values, "K_METRICS_Q1Q17")
        # self.compute_rp_metrics(predictions_df_q1q17, log=True)
        # self.compute_pr_metrics(predictions_df_q1q17, log=True)
        # logging.info("----------------------------------Ete6 SET METRICS ---------------------------------------")
        # self.compute_metrics(predictions_df_ete6, thresholds=[float(np.squeeze(np.mean(selected_snpv_thresholds[2]))),
        #                                                  float(np.squeeze(np.mean(selected_snpv_thresholds[3]))),
        #                                                  float(np.squeeze(np.mean(selected_snpv_thresholds[4]))),
        #                                                  float(np.squeeze(np.mean(selected_pr_thresholds[2]))),
        #                                                  float(np.squeeze(np.mean(selected_pr_thresholds[4])))], log=True)
        # self.log_prediction_metrics(predictions_df_ete6, k_values, "K_METRICS_ETE6")
        # self.compute_rp_metrics(predictions_df_ete6, log=True)
        # self.compute_pr_metrics(predictions_df_ete6, log=True)
        #IATSON_planet.compute_statistics_map(predictions_df, './')
        # IATSON_planet.compute_statistics_map(predictions_df_ete6, './', filename="predictions_map_ete6")
        # IATSON_planet.compute_statistics_map(predictions_df_q1q17, './', filename="predictions_map_dr25")
        return predictions_df

    def load_calibrator(self, calibrator_path):
        if calibrator_path is None:
            return None
        logging.info(f"Loading calibrator from path {calibrator_path}")
        with open(calibrator_path, 'rb') as fid:
            return pickle.load(fid)

    def predict_df_cv(self, training_dir, model_dir_prefix, df, batch_size=20, cores=os.cpu_count() - 1, test_set_limit=None,
                      zero_epsilon=1e-7, plot_mismatches=False, folds=10, thresholds=[0.5],
                      k_values=np.arange(100, 2200, 100), validation_df=None, from_arrays=False,
                      calibrator_path=None, skip_folds=[], explain=False):
        prediction_stats_for_folds_thresholds = {}
        available_folds = np.arange(0, folds)
        available_folds = set(available_folds).symmetric_difference(set(skip_folds))
        for fold in available_folds:
            model_dir = f"{model_dir_prefix}_{fold}"
            self.load_model(model_dir + '/' + os.path.basename(model_dir) + '.h5')
            model_dir = f"{model_dir}/"
            calibrator = f"{model_dir}{calibrator_path}" if calibrator_path is not None else None
            prediction_stats_for_folds_thresholds[fold] = \
                self.predict_df(df, training_dir, batch_size, cores, zero_epsilon=zero_epsilon,
                                plot_mismatches=plot_mismatches, thresholds=thresholds, log=False,
                                validation_df=validation_df, from_arrays=from_arrays,
                                calibrator_path=calibrator, explain=explain)
        average_predictions_df_thresholds = {}
        for threshold in thresholds:
            for fold in available_folds:
                prediction_stats_for_folds_thresholds[fold][threshold][0].predictions_df = \
                    prediction_stats_for_folds_thresholds[fold][threshold][0].predictions_df.sort_values(by=['object_id'], ascending=True)
            average_predictions_df = pd.DataFrame(columns=['object_id', 'period', 'type', 'expected_class', 'predicted_class',
                                                           'prediction_value', 'prediction_value_std'])
            if explain:
                average_predictions_df = pd.DataFrame(columns=['object_id', 'period', 'type', 'expected_class', 'predicted_class',
                                                           'prediction_value', 'prediction_value_std',
                                                           'EXPLAIN_PERIOD_VALUE', 'EXPLAIN_DURATION_VALUE',
                                                           'EXPLAIN_RADIUS_VALUE', 'EXPLAIN_GTCN_VALUE',
                                                           'EXPLAIN_GTR_VALUE', 'EXPLAIN_OFFSET_VALUE',
                                                           'EXPLAIN_BFAP_VALUE',
                                                           'EXPLAIN_ODDEVEN_VALUE', 'EXPLAIN_TEMP_VALUE',
                                                           'EXPLAIN_ALBEDO_VALUE',
                                                           'EXPLAIN_STARTEFF_VALUE', 'EXPLAIN_STARRAD_VALUE',
                                                           'EXPLAIN_GLOBAL_VIEW', 'EXPLAIN_MAIN_VIEW',
                                                           'EXPLAIN_SECONDARY_VIEW',
                                                           'EXPLAIN_ODD_VIEW', 'EXPLAIN_EVEN_VIEW',
                                                           'EXPLAIN_CENTROIDS_RA_VIEW',
                                                           'EXPLAIN_CENTROIDS_DEC_VIEW', 'EXPLAIN_OG_VIEW'
                                                        ])
            for index, prediction_row in prediction_stats_for_folds_thresholds[0][threshold][0].predictions_df.iterrows():
                prediction_values = []
                for fold in available_folds:
                    prediction_for_object = prediction_stats_for_folds_thresholds[fold][threshold][0].predictions_df.loc[prediction_stats_for_folds_thresholds[fold][threshold][0].predictions_df['object_id'] == prediction_row['object_id']]['prediction_value']
                    prediction_values = prediction_values + [prediction_for_object.iloc[0]]
                avg_prediction_value = np.nanmean(prediction_values)
                std_prediction_value = np.nanstd(prediction_values)
                if explain:
                    average_predictions_df = pd.concat([average_predictions_df, pd.DataFrame.from_dict(
                        {'object_id': [prediction_row['object_id']],
                         'period': [prediction_row['period']],
                         'type': [prediction_row['type']],
                         'expected_class': [prediction_row['expected_class']],
                         'predicted_class': [1 if avg_prediction_value > threshold else 0],
                         'prediction_value': [avg_prediction_value],
                         'prediction_value_std': [std_prediction_value],
                         'EXPLAIN_PERIOD_VALUE': [prediction_row['EXPLAIN_PERIOD_VALUE']],
                         'EXPLAIN_DURATION_VALUE': [prediction_row['EXPLAIN_DURATION_VALUE']],
                         'EXPLAIN_RADIUS_VALUE': [prediction_row['EXPLAIN_RADIUS_VALUE']],
                         'EXPLAIN_GTCN_VALUE': [prediction_row['EXPLAIN_GTCN_VALUE']],
                         'EXPLAIN_GTR_VALUE': [prediction_row['EXPLAIN_GTR_VALUE']],
                         'EXPLAIN_OFFSET_VALUE': [prediction_row['EXPLAIN_OFFSET_VALUE']],
                         'EXPLAIN_BFAP_VALUE': [prediction_row['EXPLAIN_BFAP_VALUE']],
                         'EXPLAIN_ODDEVEN_VALUE': [prediction_row['EXPLAIN_ODDEVEN_VALUE']],
                         'EXPLAIN_TEMP_VALUE': [prediction_row['EXPLAIN_TEMP_VALUE']],
                         'EXPLAIN_ALBEDO_VALUE': [prediction_row['EXPLAIN_ALBEDO_VALUE']],
                         'EXPLAIN_STARTEFF_VALUE': [prediction_row['EXPLAIN_STARTEFF_VALUE']],
                         'EXPLAIN_STARRAD_VALUE': [prediction_row['EXPLAIN_STARRAD_VALUE']],
                         'EXPLAIN_GLOBAL_VIEW': [prediction_row['EXPLAIN_GLOBAL_VIEW']],
                         'EXPLAIN_MAIN_VIEW': [prediction_row['EXPLAIN_MAIN_VIEW']],
                        'EXPLAIN_SECONDARY_VIEW': [prediction_row['EXPLAIN_SECONDARY_VIEW']],
                        'EXPLAIN_ODD_VIEW': [prediction_row['EXPLAIN_ODD_VIEW']],
                        'EXPLAIN_EVEN_VIEW': [prediction_row['EXPLAIN_EVEN_VIEW']],
                        'EXPLAIN_CENTROIDS_RA_VIEW': [prediction_row['EXPLAIN_CENTROIDS_RA_VIEW']],
                        'EXPLAIN_CENTROIDS_DEC_VIEW': [prediction_row['EXPLAIN_CENTROIDS_DEC_VIEW']],
                        'EXPLAIN_OG_VIEW': [prediction_row['EXPLAIN_CENTROIDS_DEC_VIEW']]
                    },
                        orient='columns')], ignore_index=True)
                else:
                    average_predictions_df = pd.concat([average_predictions_df, pd.DataFrame.from_dict(
                        {'object_id': [prediction_row['object_id']],
                         'period': [prediction_row['period']],
                         'type': [prediction_row['type']],
                         'expected_class': [prediction_row['expected_class']],
                         'predicted_class': [1 if avg_prediction_value > threshold else 0],
                         'prediction_value': [avg_prediction_value],
                         'prediction_value_std': [std_prediction_value]},
                        orient='columns')], ignore_index=True)
            average_predictions_df_thresholds[threshold] = average_predictions_df
            #logging.info(f"Predictions for threshold {threshold}: \n" + average_predictions_df.to_string())
            self.compute_metrics(average_predictions_df_thresholds[threshold], [threshold], log=True)
            logging.info(f"Signals predicted as negative for threshold {threshold}: \n" +
                         average_predictions_df.loc[(average_predictions_df['prediction_value'] <= threshold)]
                         .sort_values(by=['prediction_value'], ascending=True).to_string())
            logging.info(f"Signals predicted as positive for threshold {threshold}: \n" +
                         average_predictions_df.loc[(average_predictions_df['prediction_value'] > threshold)]
                         .sort_values(by=['prediction_value'], ascending=True).to_string())
        return average_predictions_df_thresholds

    @staticmethod
    def compute_statistics_map(predictions_df, report_dir, filename='predictions_map', vp_threshold=0.9901, lp_threshold=0.74,
                               vn_threshold=0.00031, ln_threshold=0.0072, markersize=20):
        min_fpp = 0.000001
        fig, axs = plt.subplots(1, 1, figsize=(16, 16), constrained_layout=True)
        # fig.suptitle("Predictions Map", fontsize=25)
        fig.supylabel("Prediction", fontsize=35)
        divider = make_axes_locatable(axs)
        ax_log_top = divider.append_axes("top", size=5, pad=0, sharex=axs)
        ax_log = divider.append_axes("bottom", size=5, pad=0, sharex=axs)
        periods_0 = predictions_df.loc[predictions_df['expected_class'] == 0, 'period'].to_numpy()
        prediction_values_0 = predictions_df.loc[predictions_df['expected_class'] == 0, 'prediction_value'].to_numpy()
        periods_1 = predictions_df.loc[predictions_df['expected_class'] == 1, 'period'].to_numpy()
        prediction_values_1 = predictions_df.loc[predictions_df['expected_class'] == 1, 'prediction_value'].to_numpy()
        if len(prediction_values_0) > 0:
            prediction_values_0[prediction_values_0 < np.nanmin(prediction_values_0)] = min_fpp
        if len(prediction_values_1) > 0:
            prediction_values_1[prediction_values_1 < np.nanmin(prediction_values_1)] = min_fpp
        division = 0.1
        top_division = 0.95
        if top_division > lp_threshold:
            axs.axhspan(lp_threshold, 1, color="cyan", label="LP", alpha=0.3)
        up_indexes = np.argwhere((prediction_values_0 > division) & (prediction_values_0 <= top_division)).flatten()
        axs.scatter(periods_0[up_indexes], prediction_values_0[up_indexes], color="red", s=markersize)
        up_indexes = np.argwhere((prediction_values_1 > division) & (prediction_values_1 <= top_division)).flatten()
        axs.scatter(periods_1[up_indexes], prediction_values_1[up_indexes], color="blue", s=markersize)
        axs.set_yscale("linear")
        axs.set_xscale("log")
        axs.set_ylim([division, top_division])
        axs.tick_params(axis='both', which='major', labelsize=25)
        axs.tick_params(axis='both', which='minor', labelsize=25)
        axs.spines["bottom"].set_visible(False)  # hide bottom of box
        axs.spines["top"].set_visible(False)  # hide top of box
        axs.get_xaxis().set_visible(False)  # hide x-axis entirely
        axs.axhline(y=division, color="black", linestyle="dashed", linewidth=1)
        axs.axhline(y=top_division, color="black", linestyle="dashed", linewidth=1)

        # Acting on the log axis
        ax_log_top.set_xscale("log")
        ax_log_top.set_yscale("log")
        ax_log_top.set_ylim([top_division, 1.0])
        down_indexes = np.argwhere(prediction_values_0 > top_division).flatten()
        ax_log_top.axhspan(lp_threshold, 1, color="cyan", label="LP", alpha=0.3)
        ax_log_top.axhspan(vp_threshold, 1, color="lightgreen", label="VP", alpha=0.3)
        ax_log_top.scatter(periods_0[down_indexes], prediction_values_0[down_indexes], color="red", s=markersize)
        down_indexes = np.argwhere(prediction_values_1 > top_division).flatten()
        ax_log_top.scatter(periods_1[down_indexes], prediction_values_1[down_indexes], color="blue", s=markersize)
        ax_log_top.tick_params(axis='both', which='major', labelsize=25)
        ax_log_top.tick_params(axis='both', which='minor', labelsize=25)
        ax_log_top.spines["bottom"].set_visible(False)  # hide bottom of box
        ax_log_top.get_xaxis().set_visible(False)

        # Acting on the log axis
        ax_log.set_ylim([min_fpp, division])
        ax_log.set_xscale("log")
        ax_log.set_yscale("log")
        down_indexes = np.argwhere(prediction_values_0 <= division).flatten()
        ax_log.scatter(periods_0[down_indexes], prediction_values_0[down_indexes], color="red", s=markersize)
        down_indexes = np.argwhere(prediction_values_1 <= division).flatten()
        ax_log.scatter(periods_1[down_indexes], prediction_values_1[down_indexes], color="blue", s=markersize)
        ax_log.plot(1, min_fpp, markersize=0)
        ax_log.axhspan(0, ln_threshold, color="gray", label="VN", alpha=0.3)
        ax_log.axhspan(0, vn_threshold, color="lightcoral", label="LN", alpha=0.3)
        ax_log.spines["top"].set_visible(False)  # hide top of box
        ax_log.tick_params(axis='both', which='major', labelsize=25)
        ax_log.tick_params(axis='both', which='minor', labelsize=25)
        ax_log.set_xlabel('Period (d)', fontsize=35)
        fig.tight_layout()
        plt.show()
        plt.close(fig)

    def log_prediction_metrics(self, df, k_range, message):
        logging.info(f"{message}")
        for k in k_range:
            kp_df = df.iloc[:k]
            kp_tps = len(kp_df.loc[(kp_df['expected_class'] == kp_df['predicted_class']) & (kp_df['expected_class'] == 1)])
            kp_fps = len(kp_df.loc[(kp_df['expected_class'] != kp_df['predicted_class']) & (kp_df['expected_class'] == 0)])
            k_precisions = kp_tps / (kp_tps + kp_fps)
            logging.info("P@K%.0f = %.3f", k, k_precisions)
            logging.info("FPs@K%.0f = %.3f", k, kp_fps)
            kr_df = df.iloc[-k:]
            kr_fns = len(kr_df.loc[(kr_df['expected_class'] != kr_df['predicted_class']) & (kr_df['expected_class'] == 1)])
            logging.info("FNs@K%.0f = %.3f", k, kr_fns)
        k = len(df[df['expected_class'] == 1])
        kp_df = df.iloc[:k]
        kp_tps = len(kp_df.loc[(kp_df['expected_class'] == kp_df['predicted_class']) & (kp_df['expected_class'] == 1)])
        kp_fps = len(kp_df.loc[(kp_df['expected_class'] != kp_df['predicted_class']) & (kp_df['expected_class'] == 0)])
        k_precisions = kp_tps / (kp_tps + kp_fps)
        logging.info("P@K%.0f = %.3f", k, k_precisions)
        logging.info("FPs@K%.0f = %.3f", k, kp_fps)
        kr_df = df.iloc[-k:]
        kr_fns = len(kr_df.loc[(kr_df['expected_class'] != kr_df['predicted_class']) & (kr_df['expected_class'] == 1)])
        logging.info("FNs@K%.0f = %.3f", k, kr_fns)
        fns_df = df.loc[(df['expected_class'] != df['predicted_class']) & (df['expected_class'] == 1)]
        fns_df = fns_df.sort_values(by=['prediction_value'], ascending=True)
        logging.info("FNs DF: \n" + fns_df.to_string())
        fps_df = df.loc[(df['expected_class'] != df['predicted_class']) & (df['expected_class'] == 0)]
        fps_df = fps_df.sort_values(by=['prediction_value'], ascending=False)
        logging.info("FPs DF: \n" + fps_df.to_string())


    def compute_metrics_p100(self, predictions_df, folds=10, log=False):
        first_fp_thresholds = []
        r_at_p100 = []
        for fold in np.arange(0, folds):
            sorted_pred_df = predictions_df.loc[predictions_df['fold'] == fold] \
                .sort_values(by=['prediction_value'], ascending=False)
            first_fp_thresholds.append(
                sorted_pred_df.loc[(sorted_pred_df['expected_class'] == 0), 'prediction_value'].iloc[0])
            metric_rp = tf.keras.metrics.RecallAtPrecision(precision=1, num_thresholds=10000)
            metric_rp.update_state(sorted_pred_df['expected_class'].to_numpy(),
                                   sorted_pred_df['prediction_value'].to_numpy())
            r_at_p100.append(metric_rp.result().numpy())
            if log:
                logging.info(f'Fold {fold} T@P100={first_fp_thresholds[fold]}, R@P100={r_at_p100[fold]}')
        return first_fp_thresholds, r_at_p100

    def compute_metrics_npv100(self, predictions_df, folds=10, log=False):
        first_fp_thresholds = []
        s_at_npv100 = []
        for fold in np.arange(0, folds):
            sorted_pred_df = predictions_df.loc[predictions_df['fold'] == fold]\
                .sort_values(by=['prediction_value'], ascending=True)
            first_fp_thresholds.append(
                sorted_pred_df.loc[(sorted_pred_df['expected_class'] == 1) & (sorted_pred_df['predicted_class'] == 0),
                'prediction_value'].iloc[0])
            metric = SpecificityAtNPV(npv=1, num_thresholds=10000)
            metric.update_state(sorted_pred_df['expected_class'].to_numpy(),
                                sorted_pred_df['prediction_value'].to_numpy())
            s_at_npv100.append(metric.result().numpy())
            if log:
                logging.info(f'Fold {fold} T@NPV100={first_fp_thresholds[fold]}, S@NPV100={s_at_npv100[fold]}')
        return first_fp_thresholds, s_at_npv100

    def compute_rp_thresholds(self, predictions_df, folds=10, rp_values=[0.95, 0.975, 0.99, 0.995, 1.0], thresholds=1000,
                              log=False):
        selected_rp_thresholds = []
        selected_pr_thresholds = []
        selected_snpv_thresholds = []
        all_recalls = []
        all_precisions = []
        all_sensitivities = []
        for fold in np.arange(0, folds):
            logging.info(f"R@P metrics for fold no {fold}")
            selected_rp_threshold, recalls, selected_snpv_threshold, sensitivities = \
                self.compute_rp_metrics(predictions_df.loc[predictions_df["fold"] == fold], rp_values, thresholds,
                                        log)
            selected_rp_threshold = np.array(selected_rp_threshold).flatten()
            selected_rp_thresholds = selected_rp_thresholds + [selected_rp_threshold]
            all_recalls = all_recalls + [recalls]
            selected_snpv_threshold = np.array(selected_snpv_threshold).flatten()
            selected_snpv_thresholds = selected_snpv_thresholds + [selected_snpv_threshold]
            all_sensitivities = all_sensitivities + [sensitivities]
            # logging.info(f"P@R metrics for fold no {fold}")
            # selected_pr_threshold, precisions = \
            #     self.compute_pr_metrics(predictions_df.loc[predictions_df["fold"] == fold], rp_values, thresholds,
            #                             log)
            # selected_pr_threshold = np.array(selected_pr_threshold).flatten()
            # selected_pr_thresholds = selected_pr_thresholds + [selected_pr_threshold]
            # all_precisions = all_precisions + [precisions]
        all_recalls = np.transpose(all_recalls)
        selected_rp_thresholds = np.transpose(selected_rp_thresholds)
        all_sensitivities = np.transpose(all_sensitivities)
        selected_snpv_thresholds = np.transpose(selected_snpv_thresholds)
        for index, rp_value in enumerate(rp_values):
            logging.info(f"R@P{rp_value} Values: {all_recalls[index, :]}")
            logging.info(f"Average R@P{rp_value}: {np.nanmean(all_recalls[index, :])} +- "
                         f"{np.nanstd(all_recalls[index, :])}")
            logging.info(f"Median R@P{rp_value}: {np.nanmedian(all_recalls[index, :])} +- "
                         f"{np.nanstd(all_recalls[index, :])}")
            logging.info(f"R@P{rp_value} Thresholds: {selected_rp_thresholds[index]}")
            logging.info(f"Average T@P{rp_value}: {np.nanmean(selected_rp_thresholds[index])} +- "
                         f"{np.nanstd(selected_rp_thresholds[index])}")
            logging.info(f"Median T@P{rp_value}: {np.nanmedian(selected_rp_thresholds[index])} +- "
                         f"{np.nanstd(selected_rp_thresholds[index])}")
            logging.info(f"S@NPV{rp_value} Values: {all_sensitivities[index, :]}")
            logging.info(f"Average S@NPV{rp_value}: {np.nanmean(all_sensitivities[index, :])} +- "
                         f"{np.nanstd(all_sensitivities[index, :])}")
            logging.info(f"Median S@NPV{rp_value}: {np.nanmedian(all_sensitivities[index, :])} +- "
                         f"{np.nanstd(all_sensitivities[index, :])}")
            logging.info(f"S@NPV{rp_value} Thresholds: {selected_snpv_thresholds[index]}")
            logging.info(f"Average T@NPV{rp_value}: {np.nanmean(selected_snpv_thresholds[index])} +- "
                         f"{np.nanstd(selected_snpv_thresholds[index])}")
            logging.info(f"Median T@NPV{rp_value}: {np.nanmedian(selected_snpv_thresholds[index])} +- "
                         f"{np.nanstd(selected_snpv_thresholds[index])}")
        #all_precisions = np.transpose(all_precisions)
        selected_pr_thresholds = np.transpose(selected_pr_thresholds)
        # for index, pr_value in enumerate(rp_values):
        #     logging.info(f"Average P@R{pr_value}: {np.nanmean(all_precisions[index, :])} +- "
        #                  f"{np.nanstd(all_precisions[index, :])}")
        #     logging.info(f"R@P{pr_value} Thresholds: {selected_pr_thresholds[index]}")
        return all_recalls, selected_rp_thresholds, None, selected_pr_thresholds, all_sensitivities, selected_snpv_thresholds

    def compute_pr_thresholds(self, fold_thresholds_to_results, pr_values=[0.95, 0.975, 0.99], thresholds=1000,
                              log=False):
        selected_thresholds = []
        all_precisions = []
        for fold in fold_thresholds_to_results:
            #logging.info(f"P@R metrics for fold no {fold}")
            selected_threshold, precisions = \
                self.compute_pr_metrics(fold_thresholds_to_results[fold][0.5].predictions_df, pr_values, thresholds, log)
            selected_threshold = np.array(selected_threshold).flatten()
            selected_thresholds = selected_thresholds + [selected_threshold]
            all_precisions = all_precisions + [precisions]
        all_precisions = np.transpose(all_precisions)
        selected_thresholds = np.transpose(selected_thresholds)
        # for index, rp_value in enumerate(pr_values):
        #     logging.info(f"Average P@R{rp_value}: {np.nanmean(all_precisions[index, :])} +- "
        #                  f"{np.nanstd(all_precisions[index, :])}")
        #     logging.info(f"P@R{rp_value} Thresholds: {selected_thresholds[index]}")
        return all_precisions, selected_thresholds

    def compute_rp_metrics(self, df, rp_values=[0.95, 0.975, 0.99, 0.995, 0.999, 1.0], thresholds=1000, log=False):
        best_recall_thresholds = []
        best_recalls = []
        best_sensitivity_thresholds = []
        best_sensitivities = []
        for rp_value in rp_values:
            metric = tf.keras.metrics.RecallAtPrecision(rp_value, num_thresholds=thresholds)
            metric.update_state(df['expected_class'].to_numpy(), df['prediction_value'].to_numpy())
            best_recalls = best_recalls + [metric.result().numpy()]
            metric = ThresholdAtPrecision(rp_value, num_thresholds=thresholds)
            metric.update_state(df['expected_class'].to_numpy(), df['prediction_value'].to_numpy())
            best_recall_thresholds = best_recall_thresholds + [metric.result() if isinstance(metric.result(), float) else metric.result().numpy()]
            logging.info(f"Keras R@P{rp_value}: {best_recalls[-1]}, {best_recall_thresholds[-1]}")
            metric = SpecificityAtNPV(rp_value, num_thresholds=thresholds)
            metric.update_state(df['expected_class'].to_numpy(), df['prediction_value'].to_numpy())
            best_sensitivities = best_sensitivities + [metric.result() if isinstance(metric.result(), float) else metric.result().numpy()]
            metric = ThresholdAtNPV(rp_value, num_thresholds=thresholds)
            metric.update_state(df['expected_class'].to_numpy(), df['prediction_value'].to_numpy())
            best_sensitivity_thresholds = best_sensitivity_thresholds + [metric.result() if isinstance(metric.result(), float) else metric.result().numpy()]
            logging.info(f"Keras S@NPV{rp_value}: {best_sensitivities[-1]}, {best_sensitivity_thresholds[-1]}")
        return best_recall_thresholds, best_recalls, best_sensitivity_thresholds, best_sensitivities

    def compute_pr_metrics(self, df, pr_values=[0.95, 0.975, 0.99], thresholds=1000, log=False):
        best_precision_thresholds = []
        best_precisions = []
        for pr_value in pr_values:
            metric = tf.keras.metrics.PrecisionAtRecall(pr_value, num_thresholds=thresholds)
            metric.update_state(df['expected_class'].to_numpy(), df['prediction_value'].to_numpy())
            best_precisions = best_precisions + [metric.result() if isinstance(metric.result(), float) else metric.result().numpy()]
            metric = ThresholdAtRecall(pr_value, num_thresholds=thresholds)
            metric.update_state(df['expected_class'].to_numpy(), df['prediction_value'].to_numpy())
            best_precision_thresholds = best_precision_thresholds + [metric.result() if isinstance(metric.result(), float) else metric.result().numpy()]
            #logging.info(f"Keras P@R{pr_value}: {best_precisions[-1]}, {best_precision_thresholds[-1]}")
        return best_precision_thresholds, best_precisions

    def compute_metrics(self, df, thresholds=[0.5, 0.99], log=False):
        precisions = {}
        recalls = {}
        accuracies = {}
        npvs = {}
        sensitivities = {}
        tps = {}
        fps = {}
        tns = {}
        fns = {}
        rps99 = {}
        rps100 = {}
        snpvs999 = {}
        snpvs1000 = {}
        tps99 = {}
        tps100 = {}
        tnpvs999 = {}
        tnpvs1000 = {}
        for threshold in thresholds:
            metric = tf.keras.metrics.TruePositives(thresholds=threshold)
            metric.update_state(df['expected_class'].to_numpy(), df['prediction_value'].to_numpy())
            tps[threshold] = metric.result() if isinstance(metric.result(), float) else metric.result().numpy()
            metric = tf.keras.metrics.FalsePositives(thresholds=threshold)
            metric.update_state(df['expected_class'].to_numpy(), df['prediction_value'].to_numpy())
            fps[threshold] = metric.result() if isinstance(metric.result(), float) else metric.result().numpy()
            metric = tf.keras.metrics.TrueNegatives(thresholds=threshold)
            metric.update_state(df['expected_class'].to_numpy(), df['prediction_value'].to_numpy())
            tns[threshold] = metric.result() if isinstance(metric.result(), float) else metric.result().numpy()
            metric = tf.keras.metrics.FalseNegatives(thresholds=threshold)
            metric.update_state(df['expected_class'].to_numpy(), df['prediction_value'].to_numpy())
            fns[threshold] = metric.result() if isinstance(metric.result(), float) else metric.result().numpy()
            metric = tf.keras.metrics.Precision(thresholds=threshold)
            metric.update_state(df['expected_class'].to_numpy(), df['prediction_value'].to_numpy())
            precisions[threshold] = metric.result() if isinstance(metric.result(), float) else metric.result().numpy()
            metric = tf.keras.metrics.Recall(thresholds=threshold)
            metric.update_state(df['expected_class'].to_numpy(), df['prediction_value'].to_numpy())
            recalls[threshold] = metric.result() if isinstance(metric.result(), float) else metric.result().numpy()
            metric = tf.keras.metrics.BinaryAccuracy(threshold=threshold)
            metric.update_state(df['expected_class'].to_numpy(), df['prediction_value'].to_numpy())
            accuracies[threshold] = metric.result() if isinstance(metric.result(), float) else metric.result().numpy()
            metric = NegativePredictiveValue(thresholds=threshold)
            metric.update_state(df['expected_class'].to_numpy(), df['prediction_value'].to_numpy())
            npvs[threshold] = metric.result() if isinstance(metric.result(), float) else metric.result().numpy()
            metric = Specificity(thresholds=threshold)
            metric.update_state(df['expected_class'].to_numpy(), df['prediction_value'].to_numpy())
            sensitivities[threshold] = metric.result() if isinstance(metric.result(), float) else metric.result().numpy()
            metric = RecallAtPrecision(precision=0.99, num_thresholds=1000)
            metric.update_state(df['expected_class'].to_numpy(), df['prediction_value'].to_numpy())
            rps99[threshold] = metric.result() if isinstance(metric.result(), float) else metric.result().numpy()
            metric = ThresholdAtPrecision(precision=0.99, num_thresholds=1000)
            metric.update_state(df['expected_class'].to_numpy(), df['prediction_value'].to_numpy())
            tps99[threshold] = metric.result() if isinstance(metric.result(), float) else metric.result().numpy()
            metric = RecallAtPrecision(precision=1.0, num_thresholds=1000)
            metric.update_state(df['expected_class'].to_numpy(), df['prediction_value'].to_numpy())
            rps100[threshold] = metric.result() if isinstance(metric.result(), float) else metric.result().numpy()
            metric = ThresholdAtPrecision(precision=1.0, num_thresholds=1000)
            metric.update_state(df['expected_class'].to_numpy(), df['prediction_value'].to_numpy())
            tps100[threshold] = metric.result() if isinstance(metric.result(), float) else metric.result().numpy()
            metric = SpecificityAtNPV(npv=0.999, num_thresholds=1000)
            metric.update_state(df['expected_class'].to_numpy(), df['prediction_value'].to_numpy())
            snpvs999[threshold] = metric.result() if isinstance(metric.result(), float) else metric.result().numpy()
            metric = ThresholdAtNPV(npv=0.999, num_thresholds=1000)
            metric.update_state(df['expected_class'].to_numpy(), df['prediction_value'].to_numpy())
            tnpvs999[threshold] = metric.result() if isinstance(metric.result(), float) else metric.result().numpy()
            metric = SpecificityAtNPV(npv=1.0, num_thresholds=1000)
            metric.update_state(df['expected_class'].to_numpy(), df['prediction_value'].to_numpy())
            snpvs1000[threshold] = metric.result() if isinstance(metric.result(), float) else metric.result().numpy()
            metric = ThresholdAtNPV(npv=1.0, num_thresholds=1000)
            metric.update_state(df['expected_class'].to_numpy(), df['prediction_value'].to_numpy())
            tnpvs1000[threshold] = metric.result() if isinstance(metric.result(), float) else metric.result().numpy()
            if log:
                logging.info(f"Metrics: tps={tps}, fps={fps}, tns={tns}, fns={fns},"
                             f"precision={precisions[threshold]}, recall={recalls[threshold]}, "
                             f"accuracy={accuracies[threshold]}, npv={npvs[threshold]}, "
                             f"sensitivity={sensitivities[threshold]}, "
                             f"rp@99={rps99[threshold]}, "
                             f"tp@99={tps99[threshold]}, "
                             f"rp@100={rps100[threshold]}, "
                             f"tp@100={tps100[threshold]}, "
                             f"s@npv999={snpvs999[threshold]}, "
                             f"t@npv999={tnpvs999[threshold]}, "
                             f"s@npv1000={snpvs1000[threshold]}, "
                             f"t@npv1000={tnpvs1000[threshold]}, ")
        return tps, fps, tns, fns, precisions, recalls, accuracies

    def test_metrics(self, expected_outputs, max_prediction_indexes, max_prediction_values, predictions,
                     dataset=None, training_dir=None, plot_mismatches=False, explain=False):
        expected_outputs = expected_outputs.flatten()
        positive_preds = np.argwhere(max_prediction_indexes.flatten() != -1).flatten()
        negative_preds = np.argwhere(max_prediction_indexes.flatten() == -1).flatten()
        positive_outputs = np.argwhere(expected_outputs == 1).flatten()
        negative_outputs = np.argwhere(expected_outputs == 0).flatten()
        label_tp_indexes = np.intersect1d(positive_preds, positive_outputs)
        label_tn_indexes = np.intersect1d(negative_preds, negative_preds)
        label_fp_indexes = positive_preds[np.isin(positive_preds, negative_outputs)]
        label_fn_indexes = negative_preds[np.isin(negative_preds, positive_outputs)]
        label_tp = len(label_tp_indexes)
        label_tn = len(label_tn_indexes)
        label_fp = len(label_fp_indexes)
        label_fn = len(label_fn_indexes)
        accuracy = (label_tp + label_tn) / len(expected_outputs)
        precision = label_tp / (label_tp + label_fp + 1e-7)
        recall = label_tp / (label_tp + label_fn + 1e-7)
        max_predictions = np.array([np.max(prediction) for prediction in predictions])
        max_predictions_sort_args = np.flip(np.argsort(max_predictions))
        max_predictions_sort = max_predictions[max_predictions_sort_args]
        max_prediction_indexes_sort = max_prediction_indexes[max_predictions_sort_args]
        max_prediction_values_sort = max_prediction_values[max_predictions_sort_args]
        expected_outputs_sort = expected_outputs[max_predictions_sort_args]
        k_df = pd.DataFrame(columns=['k', 'precision', 'recall', 'accuracy', 'tp', 'fp', 'tn', 'fn'])
        if 100 < len(expected_outputs):
            for k in np.arange(100, len(expected_outputs) if len(expected_outputs) < 2500 else 2500, 100):
                max_predictions_sort_k = max_predictions_sort[0:k]
                max_prediction_indexes_sort_k = max_prediction_indexes_sort[0:k]
                max_prediction_values_sort_k = max_prediction_values_sort[0:k]
                expected_outputs_sort_k = expected_outputs_sort[0:k]
                positive_preds = np.argwhere(max_prediction_indexes_sort_k.flatten() != -1).flatten()
                negative_preds = np.argwhere(max_prediction_indexes_sort_k.flatten() == -1).flatten()
                positive_outputs = np.argwhere(expected_outputs_sort_k == 1).flatten()
                negative_outputs = np.argwhere(expected_outputs_sort_k == 0).flatten()
                label_tp_indexes = np.intersect1d(positive_preds, positive_outputs)
                label_tn_indexes = np.intersect1d(negative_preds, negative_preds)
                label_fp_indexes = positive_preds[np.isin(positive_preds, negative_outputs)]
                label_fn_indexes = negative_preds[np.isin(negative_preds, positive_outputs)]
                label_tp = len(label_tp_indexes)
                label_tn = len(label_tn_indexes)
                label_fp = len(label_fp_indexes)
                label_fn = len(label_fn_indexes)
                accuracy = (label_tp + label_tn) / len(expected_outputs_sort_k)
                precision = label_tp / (label_tp + label_fp + 1e-7)
                recall = label_tp / (label_tp + label_fn + 1e-7)
                k_df = pd.concat([k_df, pd.DataFrame.from_dict(
                    {'k': [k], 'precision': [precision], 'recall': [recall], 'accuracy': [accuracy], 'tp': [label_tp],
                     'fp': [label_fp], 'tn': [label_tn], 'fn': [label_fn]}, orient='columns')], ignore_index=True)
        if not explain:
            predictions_df = pd.DataFrame(columns=['object_id', 'type', 'expected_class', 'predicted_class',
                                              'prediction_value'])
        else:
            predictions_df = pd.DataFrame(columns=['object_id', 'type', 'expected_class', 'predicted_class',
                                              'prediction_value',
                                               'EXPLAIN_PERIOD_VALUE', 'EXPLAIN_DURATION_VALUE',
                                               'EXPLAIN_RADIUS_VALUE', 'EXPLAIN_GTCN_VALUE',
                                               'EXPLAIN_GTR_VALUE', 'EXPLAIN_OFFSET_VALUE',
                                               'EXPLAIN_BFAP_VALUE',
                                               'EXPLAIN_ODDEVEN_VALUE', 'EXPLAIN_TEMP_VALUE',
                                               'EXPLAIN_ALBEDO_VALUE',
                                               'EXPLAIN_STARTEFF_VALUE', 'EXPLAIN_STARRAD_VALUE',
                                               'EXPLAIN_GLOBAL_VIEW', 'EXPLAIN_MAIN_VIEW',
                                               'EXPLAIN_SECONDARY_VIEW',
                                               'EXPLAIN_ODD_VIEW', 'EXPLAIN_EVEN_VIEW',
                                               'EXPLAIN_CENTROIDS_RA_VIEW',
                                               'EXPLAIN_CENTROIDS_DEC_VIEW', 'EXPLAIN_OG_VIEW'])
        if dataset is not None:
            found_classes = [0 if prediction == -1 else 1 for prediction in max_prediction_values]
            dataset = dataset.reset_index(drop=True)
            for i, row in dataset.iterrows():
                object_id = row['object_id']
                period = row['period']
                id = object_id + "_" + str(period)
                expected_tag = row['type']
                expected_output = expected_outputs[i]
                predicted_output = found_classes[i]
                predicted_value = predictions[i][max_prediction_indexes[i]]
                if not explain:
                    predictions_df = pd.concat([predictions_df, pd.DataFrame.from_dict(
                        {'object_id': [object_id + '_' + str(round(period, 2))], "type": [expected_tag], 'period': period,
                         "expected_class": [expected_output], "predicted_class": [predicted_output],
                         "prediction_value": [predicted_value]}, orient='columns')],
                                               ignore_index=True)
                else:
                    predictions_df = pd.concat([predictions_df, pd.DataFrame.from_dict(
                        {'object_id': [object_id + '_' + str(round(period, 2))], "type": [expected_tag], 'period': period,
                         "expected_class": [expected_output], "predicted_class": [predicted_output],
                         "prediction_value": [predicted_value],
                         'EXPLAIN_PERIOD_VALUE': [row['EXPLAIN_PERIOD_VALUE']],
                         'EXPLAIN_DURATION_VALUE': [row['EXPLAIN_DURATION_VALUE']],
                        'EXPLAIN_RADIUS_VALUE': [row['EXPLAIN_RADIUS_VALUE']],
                         'EXPLAIN_GTCN_VALUE': [row['EXPLAIN_GTCN_VALUE']],
                        'EXPLAIN_GTR_VALUE': [row['EXPLAIN_GTR_VALUE']],
                         'EXPLAIN_OFFSET_VALUE': [row['EXPLAIN_OFFSET_VALUE']],
                        'EXPLAIN_BFAP_VALUE': [row['EXPLAIN_BFAP_VALUE']],
                        'EXPLAIN_ODDEVEN_VALUE': [row['EXPLAIN_ODDEVEN_VALUE']],
                         'EXPLAIN_TEMP_VALUE': [row['EXPLAIN_TEMP_VALUE']],
                        'EXPLAIN_ALBEDO_VALUE': [row['EXPLAIN_ALBEDO_VALUE']],
                        'EXPLAIN_STARTEFF_VALUE': [row['EXPLAIN_STARTEFF_VALUE']],
                         'EXPLAIN_STARRAD_VALUE': [row['EXPLAIN_STARRAD_VALUE']],
                         'EXPLAIN_GLOBAL_VIEW': [row['EXPLAIN_GLOBAL_VIEW']],
                         'EXPLAIN_MAIN_VIEW': [row['EXPLAIN_MAIN_VIEW']],
                        'EXPLAIN_SECONDARY_VIEW': [row['EXPLAIN_SECONDARY_VIEW']],
                        'EXPLAIN_ODD_VIEW': [row['EXPLAIN_ODD_VIEW']],
                        'EXPLAIN_EVEN_VIEW': [row['EXPLAIN_EVEN_VIEW']],
                        'EXPLAIN_CENTROIDS_RA_VIEW': [row['EXPLAIN_CENTROIDS_RA_VIEW']],
                        'EXPLAIN_CENTROIDS_DEC_VIEW': [row['EXPLAIN_CENTROIDS_DEC_VIEW']],
                        'EXPLAIN_OG_VIEW': [row['EXPLAIN_CENTROIDS_DEC_VIEW']]
                    }, orient='columns')],
                                               ignore_index=True)
                if plot_mismatches:
                    logging.info("%s with label %s mismatched with value %s", id, expected_tag, predicted_value)
                    IatsonPlanetModelGenerator(dataset[(dataset['object_id'] == object_id) & (dataset['period'] == period)],
                                                                         training_dir, 1,
                                                                         self.input_size,
                                                                         self.type_to_label,
                                                                         from_arrays=True,
                                                                         shuffle_batch=False,
                                                                         plot_inputs=True).__getitem__(0)
        # predictions_df = predictions_df.sort_values(by=['prediction_value'], ascending=True)
        return CategoricalPredictionSetStats(label_tp, label_fp, label_fn, accuracy, precision, recall, k_df,
                                             predictions_df)

    def predict_watson(self, target_id, period, duration, epoch, depth_ppt, watson_dir, star_filename, lc_filename,
                       transits_mask=None, plot_inputs=False, cv_dir=None, calibrator_path=None, use_csvs=False, explain=False,
                       batch_size=1):
        df = pd.DataFrame(columns=['object_id', 'period', 'duration(h)', 'depth_primary', 'radius(earth)', 'type'])
        star_df = pd.read_csv(star_filename)
        df = pd.concat([df, pd.DataFrame.from_dict(
            {'object_id': target_id,
             'period': [period],
             'duration(h)': [duration],
             'epoch': [epoch],
             'depth_primary': [depth_ppt],
             'radius(earth)': [((((depth_ppt / 1000) * (star_df.iloc[0]['radius'] ** 2)) ** (1/2)) * u.R_sun).to(u.R_earth).value]},
            orient='columns')], ignore_index=True)
        testing_batch_generator = WatsonPlanetModelGenerator(df, watson_dir, star_filename,
                                                             lc_filename, batch_size,
                                                             self.input_size, zero_epsilon=1e-7,
                                                             transits_mask=transits_mask, plot_inputs=plot_inputs, use_csvs=use_csvs, explain=explain)
        return self.predict_cv(testing_batch_generator, cv_dir, calibrator_path=calibrator_path, batch_size=batch_size)


    def calibration_metrics(self, predictions_train_df, predictions_val_df=None, validation_set_percent=0.2, title="",
                            method='none', plot=False):
        if predictions_val_df is None:
            predictions_df_shuffled = shuffle(predictions_train_df)
            predictions_val_df = predictions_df_shuffled[int(len(predictions_df_shuffled) * (1 - validation_set_percent)):]
            predictions_train_df = predictions_df_shuffled[0:-int(len(predictions_df_shuffled) * validation_set_percent)]
        prediction_train_values = predictions_train_df['prediction_value'].to_numpy()
        expected_train_classes = predictions_train_df['expected_class'].to_numpy()
        prediction_val_values = predictions_val_df['prediction_value'].to_numpy()
        if method == 'none':
            calibrated_pred_train_df = predictions_train_df
            calibrated_pred_val_df = predictions_val_df
            title = f"{title}"
        elif method == 'platt':
            platt = PlattCalibrator(log_odds=True)
            platt.fit(np.float64(prediction_train_values), np.float64(expected_train_classes))
            calibrated_train = platt.predict(prediction_train_values)
            calibrated_val = platt.predict(prediction_val_values)
            calibrated_pred_train_df = predictions_train_df.copy()
            calibrated_pred_train_df['prediction_value'] = calibrated_train
            calibrated_pred_val_df = predictions_val_df.copy()
            calibrated_pred_val_df['prediction_value'] = calibrated_val
            title=f"{title} Platt Calibration"
        elif method == 'isotonic':
            clf = IsotonicRegression()
            clf = clf.fit(predictions_train_df[['prediction_value']],
                          predictions_train_df['expected_class'].to_numpy())
            calibrated_train = clf.predict(prediction_train_values)
            calibrated_val = clf.predict(predictions_val_df['prediction_value'].to_numpy())
            calibrated_pred_train_df = predictions_train_df.copy()
            calibrated_pred_train_df['prediction_value'] = calibrated_train
            calibrated_pred_val_df = predictions_val_df.copy()
            calibrated_pred_val_df['prediction_value'] = calibrated_val
            title=f"{title} Isotonic Calibration"
        else:
            raise ValueError(f"Unsupported calibration method {method}")
        if plot:
            self.plot_reliability_diagrams(predictions_train_df, predictions_val_df, title=f"{title}")
        return calibrated_pred_train_df, calibrated_pred_val_df
        #diagram.plot(calibrated, ground_truth)  # visualize miscalibration of calibrated
        #calibrated_ece = ece.measure(calibrated, predictions_df['expected_class'].to_numpy())

    def calibrate(self, predictions_df, method=None, calibrator_dir=None):
        prediction_values = predictions_df['prediction_value'].to_numpy()
        expected_classes = predictions_df['expected_class'].to_numpy()
        calibrator = None
        results_df = predictions_df
        if method == 'logistic':
            logging.info("Calibrating with logistic regression")
            calibrator = LogisticRegression(random_state=0).fit(predictions_df[['prediction_value']],
                                                         predictions_df['expected_class'].to_numpy())
            calibrated = calibrator.predict_proba(predictions_df[['prediction_value']])
            results_df = predictions_df.copy()
            results_df['prediction_value'] = calibrated[:, 1]
        elif method == 'platt':
            logging.info("Calibrating with Platt Scaling")
            calibrator = PlattCalibrator(log_odds=True)
            calibrator.fit(np.float64(prediction_values), np.float64(expected_classes))
            calibrated = calibrator.predict(prediction_values)
            results_df = predictions_df.copy()
            results_df['prediction_value'] = calibrated
        elif method == 'isotonic':
            logging.info("Calibrating with isotonic regression")
            calibrator = IsotonicRegression()
            calibrator = calibrator.fit(predictions_df[['prediction_value']],
                          predictions_df['expected_class'].to_numpy())
            calibrated = calibrator.predict(prediction_values)
            results_df = predictions_df.copy()
            results_df['prediction_value'] = calibrated
        if calibrator is not None and calibrator_dir is not None:
            try:
                with open(f'{calibrator_dir}_cal_{method}.pkl', 'wb') as fid:
                    pickle.dump(calibrator, fid)
            except Exception as e:
                logging.exception("Failed calibrator storage")
        results_df.loc[results_df['prediction_value'] >= 0.5, ['predicted_class']] = 1
        results_df.loc[results_df['prediction_value'] < 0.5, ['predicted_class']] = 0
        return results_df, calibrator

    def plot_reliability_diagrams(self, predictions_train_df, predictions_val_df, title="", n_bins=10):
        import netcal.metrics
        ece = netcal.metrics.ECE(n_bins)
        mce = netcal.metrics.MCE(n_bins)
        predictions_train = predictions_train_df['prediction_value'].to_numpy()
        expected_classes_train = predictions_train_df['expected_class'].to_numpy()
        predictions_val = predictions_val_df['prediction_value'].to_numpy()
        expected_classes_val = predictions_val_df['expected_class'].to_numpy()
        calibrated_train_ece = ece.measure(predictions_train, expected_classes_train)
        calibrated_train_mce = mce.measure(predictions_train, expected_classes_train)
        calibrated_val_ece = ece.measure(predictions_val, expected_classes_val)
        calibrated_val_mce = mce.measure(predictions_val, expected_classes_val)
        logging.info(f"{title} train calibration metrics: ECE={calibrated_train_ece}, MCE={calibrated_train_mce}")
        logging.info(f"{title} validation calibration metrics: ECE={calibrated_val_ece}, MCE={calibrated_val_mce}")
        #_, values = pd.qcut(predictions_df['prediction_value'], q=10, retbins=True)
        values = [0, 0.01, 0.05, 0.1, 0.2, 0.4, 0.7, 0.8, 0.9, 0.93, 0.96, 0.98, 0.99, 0.995, 1]
        self.plot_reliability_diagram(values, predictions_train_df, predictions_val_df, title=title)
        values = [0.9, 0.92, 0.94, 0.95, 0.96, 0.975, 0.985, 0.99, 0.9925, 0.995, 0.9975, 1]
        self.plot_reliability_diagram(values, predictions_train_df, predictions_val_df, title=title)
        values = [0, 0.0025, 0.005, 0.0075, 0.01, 0.015, 0.025, 0.04, 0.05, 0.06, 0.08, 0.1]
        self.plot_reliability_diagram(values, predictions_train_df, predictions_val_df, title=title)

    def plot_reliability_diagram(self, values, predictions_train_df, predictions_val_df, title=""):
        mpvs_train = []  # mean predicted values
        fops_train = []  # fraction of positives
        noss_train = []  # number of samples
        mpvs_val = []  # mean predicted values
        fops_val = []  # fraction of positives
        noss_val = []  # number of samples
        for index, value in enumerate(values[0:-1]):
            subset_pred_train_df = predictions_train_df.loc[(predictions_train_df['prediction_value'] > value) & (
                    predictions_train_df['prediction_value'] <= values[index + 1])]
            fop = len(subset_pred_train_df[subset_pred_train_df['expected_class'] == 1]) / (
                    len(subset_pred_train_df) + 1e-7)
            mpv = subset_pred_train_df['prediction_value'].mean()
            nos = len(subset_pred_train_df)
            mpvs_train = mpvs_train + [mpv]
            fops_train = fops_train + [fop]
            noss_train = noss_train + [nos]
            logging.info(f"Train Values [{value}, {values[index + 1]}] and MPV {mpv} and FOP {fop} and NOS {nos}")
            subset_pred_val_df = predictions_val_df.loc[(predictions_val_df['prediction_value'] > value) & (
                    predictions_val_df['prediction_value'] <= values[index + 1])]
            fop = len(subset_pred_val_df[subset_pred_val_df['expected_class'] == 1]) / (
                    len(subset_pred_val_df) + 1e-7)
            mpv = subset_pred_val_df['prediction_value'].mean()
            nos = len(subset_pred_val_df)
            mpvs_val = mpvs_val + [mpv]
            fops_val = fops_val + [fop]
            noss_val = noss_val + [nos]
            logging.info(f"Validation Values [{value}, {values[index + 1]}] and MPV {mpv} and FOP {fop} and NOS {nos}")
        nan_values_train_indexes = np.argwhere(~np.isnan(mpvs_train)).flatten()
        nan_values_val_indexes = np.argwhere(~np.isnan(mpvs_val)).flatten()
        mpvs_train = np.array(mpvs_train)[nan_values_train_indexes]
        fops_train = np.array(fops_train)[nan_values_train_indexes]
        noss_train = np.array(noss_train)[nan_values_train_indexes]
        mpvs_val = np.array(mpvs_val)[nan_values_val_indexes]
        fops_val = np.array(fops_val)[nan_values_val_indexes]
        noss_val = np.array(noss_val)[nan_values_val_indexes]
        fig, axs = plt.subplots(2, 1, figsize=(20, 20))
        axs[0].set_title(f"{title} Reliability Diagram from [{np.nanmin(values)} to {np.nanmax(values)}]", size=40)
        axs[0].scatter(mpvs_train, fops_train, color='red', marker='.', s=1000)
        axs[0].scatter(mpvs_val, fops_val, color='green', marker='.', s=1000)
        axs[0].plot([np.nanmin(values), np.nanmax(values)], [np.nanmin(values), np.nanmax(values)], '--')
        axs[0].set_xlabel("Mean Predicted Values", size=30)
        axs[0].set_ylabel("Fraction Of Positives", size=30)
        axs[0].xaxis.set_tick_params(labelsize=30)
        axs[0].yaxis.set_tick_params(labelsize=30)
        axs[1].plot(np.concatenate([np.repeat(mpvs_train, 2)[1:], [mpvs_train[-1]]]), np.repeat(noss_train, 2),
                    color='red')
        axs[1].fill_between(np.concatenate([np.repeat(mpvs_train, 2)[1:], [mpvs_train[-1]]]), 0,
                            np.repeat(noss_train, 2), color='red')
        axs[1].plot(np.concatenate([np.repeat(mpvs_val, 2)[1:], [mpvs_val[-1]]]), np.repeat(noss_val, 2), color='green')
        axs[1].fill_between(np.concatenate([np.repeat(mpvs_val, 2)[1:], [mpvs_val[-1]]]), 0, np.repeat(noss_val, 2),
                            color='green')
        axs[1].set_xlabel("Mean Predicted Values", size=30)
        axs[1].set_ylabel("Number Of Samples", size=30)
        axs[1].set_yscale('log', base=10)
        axs[1].xaxis.set_tick_params(labelsize=30)
        axs[1].yaxis.set_tick_params(labelsize=30)
        plt.show()

    def calibration_metrics_cv(self, training_dir, model_prefix, batch_size=20, cores=os.cpu_count() - 1,
                        thresholds=[0.5], folds=10, log=True):
        train_predictions_df_uncal = None
        val_predictions_df_uncal = None
        train_predictions_df_platt = None
        val_predictions_df_platt = None
        train_predictions_df_iso = None
        val_predictions_df_iso = None
        for fold in np.arange(0, folds):
            model_dir = model_prefix + f'_{fold}'
            self.load_model(model_dir + '/' + os.path.basename(model_dir) + '.keras')
            calibration_df = pd.read_csv(f'{model_dir}/validation_dataset.csv')
            prediction_stats_for_thresholds = self.predict_df(calibration_df, training_dir, batch_size, cores,
                                                              thresholds=thresholds, from_arrays=True)
            prediction_stats = prediction_stats_for_thresholds[thresholds[0]][0]
            fold_predictions_df = prediction_stats.predictions_df
            logging.info(f"Calibration metrics for fold {fold}")
            fold_cal_train_df, fold_cal_val_df = self.calibration_metrics(fold_predictions_df, method='none', title=f"Fold {fold} Uncalibrated", plot=False)
            train_predictions_df_uncal = fold_cal_train_df if train_predictions_df_uncal is None else \
                pd.concat([train_predictions_df_uncal, fold_cal_train_df])
            val_predictions_df_uncal = fold_cal_val_df if val_predictions_df_uncal is None else \
                pd.concat([val_predictions_df_uncal, fold_cal_val_df])
            fold_cal_train_df, fold_cal_val_df = self.calibration_metrics(fold_predictions_df, method='platt', title=f"Fold {fold}", plot=False)
            train_predictions_df_platt = fold_cal_train_df if train_predictions_df_platt is None else \
                pd.concat([train_predictions_df_platt, fold_cal_train_df])
            val_predictions_df_platt = fold_cal_val_df if val_predictions_df_platt is None else \
                pd.concat([val_predictions_df_platt, fold_cal_val_df])
            fold_cal_train_df, fold_cal_val_df = self.calibration_metrics(fold_predictions_df, method='isotonic', title=f"Fold {fold}", plot=False)
            train_predictions_df_iso = fold_cal_train_df if train_predictions_df_iso is None else \
                pd.concat([train_predictions_df_iso, fold_cal_train_df])
            val_predictions_df_iso = fold_cal_val_df if val_predictions_df_iso is None else \
                pd.concat([val_predictions_df_iso, fold_cal_val_df])
        logging.info(f"Calibration metrics for CV")
        self.calibration_metrics(train_predictions_df_uncal, val_predictions_df_uncal, title=f"Combined Uncalibrated", plot=True)
        self.calibration_metrics(train_predictions_df_platt, val_predictions_df_platt, title=f"Combined Platt", plot=True)
        self.calibration_metrics(train_predictions_df_iso, val_predictions_df_iso, title=f"Combined Isotonic", plot=True)

# 2526 (6.824076075210719 %) items of class ['planet_transit']
# 2023-05-31 16:08:15 INFO     1857 (5.016749513723795 %) items of class ['planet']
# 2023-05-31 16:08:15 INFO     3559 (9.614761184352712 %) items of class ['fp']
# 2023-05-31 16:08:15 INFO     311 (0.8401772206613357 %) items of class ['fa']
# 2023-05-31 16:08:15 INFO     804 (2.172033715150205 %) items of class ['tce']
# 2023-05-31 16:08:15 INFO     2370 (6.402636697644263 %) items of class ['tce_secondary']
# 2023-05-31 16:08:15 INFO     1029 (2.7798789712556733 %) items of class ['tce_centroids_offset']
# 2023-05-31 16:08:15 INFO     3222 (8.7043440674303 %) items of class ['tce_source_offset']
# 2023-05-31 16:08:15 INFO     6980 (18.856710611627403 %) items of class ['tce_og']
# 2023-05-31 16:08:15 INFO     733 (1.9802247676680356 %) items of class ['tce_odd_even']
# 2023-05-31 16:08:15 INFO     12631 (34.12308191052518 %) items of class ['none']
# 2023-05-31 16:08:15 INFO     279 (0.7537281175707802 %) items of class ['EB']
# 2023-05-31 16:08:15 INFO     715 (1.9315971471795979 %) items of class ['bckEB']
