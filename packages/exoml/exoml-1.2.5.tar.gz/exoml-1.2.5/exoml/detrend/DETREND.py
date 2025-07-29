import logging
import os
import pathlib

import keras
from keras import Model
from keras.layers import LeakyReLU

from exoml.ml import thread_config
from exoml.detrend.detrend_generator import DetrendModelGenerator
from exoml.ml.loss.unsupervised import intransit_weighted_mean_squared_error
from exoml.ml.metrics.fixed_mean import FixedMean

from exoml.ml.model.base_model import BaseModel, HyperParams

thread_config.setup_threads(5)


class DETREND(BaseModel):
    def __init__(self, hyperparameters, name='DETREND', input_size=(20610, 8)):
        super().__init__(name, input_size, None, None, hyperparameters)

    def build(self):
        # (time, flux, flux_err, centroidx, centroidy, motionx, motiony, bck)
        autoencoder_layer1_strides = 10
        autoencoder_layer1_filters = 5000
        autoencoder_layer1_ks = 100
        autoencoder_layer2_strides = 5
        autoencoder_layer2_filters = 1250
        autoencoder_layer2_ks = 33
        autoencoder_layer3_strides = 5
        autoencoder_layer3_filters = 420
        autoencoder_layer3_ks = 15
        autoencoder_layer4_strides = 2
        autoencoder_layer4_filters = 128
        autoencoder_layer4_ks = 9
        autoencoder_layer5_strides = 2
        autoencoder_layer5_filters = 64
        autoencoder_layer5_ks = 7
        autoencoder_layer6_strides = 1
        autoencoder_layer6_filters = 32
        autoencoder_layer6_ks = 5
        input = keras.Input(shape=(self.input_size))
        self.batch_norm_input = keras.layers.normalization.batch_normalization.BatchNormalization()(input)
        self.enc_layer1 = keras.layers.SpatialDropout1D(rate=0.1)(input)
        self.enc_layer1_r = keras.layers.Conv1D(filters=autoencoder_layer1_filters, kernel_size=autoencoder_layer1_ks,
                                                padding="same", activation=LeakyReLU(0.01))(self.enc_layer1)
        self.enc_layer1 = keras.layers.normalization.batch_normalization.BatchNormalization()(self.enc_layer1_r)
        self.enc_layer1 = keras.layers.MaxPooling1D(pool_size=50, strides=autoencoder_layer1_strides, padding="same")(self.enc_layer1)
        self.enc_layer1 = keras.layers.Dropout(rate=0.1)(self.enc_layer1)
        self.enc_layer2_r = keras.layers.Conv1D(filters=autoencoder_layer2_filters, kernel_size=autoencoder_layer2_ks,
                                                padding="same", activation=LeakyReLU(0.01))(self.enc_layer1)
        self.enc_layer2 = keras.layers.normalization.batch_normalization.BatchNormalization()(self.enc_layer2_r)
        self.enc_layer2 = keras.layers.MaxPooling1D(pool_size=20, strides=autoencoder_layer2_strides, padding="same")(self.enc_layer2)
        self.enc_layer2 = keras.layers.Dropout(rate=0.1)(self.enc_layer2)
        self.enc_layer3_r = keras.layers.Conv1D(filters=autoencoder_layer3_filters, kernel_size=autoencoder_layer3_ks,
                                                padding="same", activation=LeakyReLU(0.01))(self.enc_layer2)
        self.enc_layer3 = keras.layers.normalization.batch_normalization.BatchNormalization()(self.enc_layer3_r)
        self.enc_layer3 = keras.layers.MaxPooling1D(pool_size=15, strides=autoencoder_layer3_strides, padding="same")(self.enc_layer3)
        self.enc_layer3 = keras.layers.Dropout(rate=0.1)(self.enc_layer3)
        self.enc_layer4_r = keras.layers.Conv1D(filters=autoencoder_layer4_filters, kernel_size=autoencoder_layer4_ks,
                                                padding="same", activation=LeakyReLU(0.01))(self.enc_layer3)
        self.enc_layer4 = keras.layers.normalization.batch_normalization.BatchNormalization()(self.enc_layer4_r)
        self.enc_layer4 = keras.layers.MaxPooling1D(pool_size=10, strides=autoencoder_layer4_strides, padding="same")(self.enc_layer4)
        self.enc_layer4 = keras.layers.Dropout(rate=0.1)(self.enc_layer4)
        self.enc_layer5_r = keras.layers.Conv1D(filters=autoencoder_layer5_filters, kernel_size=autoencoder_layer5_ks,
                                                padding="same", activation=LeakyReLU(0.01))(self.enc_layer4)
        self.enc_layer5 = keras.layers.normalization.batch_normalization.BatchNormalization()(self.enc_layer5_r)
        self.enc_layer5 = keras.layers.MaxPooling1D(pool_size=4, strides=autoencoder_layer5_strides, padding="same")(self.enc_layer5)
        self.enc_layer5 = keras.layers.Dropout(rate=0.1)(self.enc_layer5)
        self.enc_layer6_r = keras.layers.Conv1D(filters=autoencoder_layer6_filters, kernel_size=autoencoder_layer6_ks,
                                                padding="same", activation=LeakyReLU(0.01))(self.enc_layer5)
        self.enc_layer6 = keras.layers.normalization.batch_normalization.BatchNormalization()(self.enc_layer6_r)
        self.enc_layer6 = keras.layers.MaxPooling1D(pool_size=3, strides=autoencoder_layer6_strides, padding="same")(self.enc_layer6)
        self.enc_layer6 = keras.layers.Dropout(rate=0.1)(self.enc_layer6)
        self.dec_layer6 = keras.layers.UpSampling1D(autoencoder_layer6_strides)(self.enc_layer6)
        self.dec_layer6 = keras.layers.Conv1DTranspose(filters=autoencoder_layer6_filters, kernel_size=autoencoder_layer6_ks,
                                                       padding="same", activation=LeakyReLU(0.01))(self.dec_layer6)
        self.dec_layer6 = keras.layers.normalization.batch_normalization.BatchNormalization()(self.dec_layer6)
        self.dec_layer6 = keras.layers.Add()([self.enc_layer6_r, self.dec_layer6])
        self.dec_layer5 = keras.layers.UpSampling1D(autoencoder_layer5_strides)(self.dec_layer6)
        self.dec_layer5 = keras.layers.Conv1DTranspose(filters=autoencoder_layer5_filters,
                                                       kernel_size=autoencoder_layer5_ks, padding="same",
                                                       activation=LeakyReLU(0.01))(self.dec_layer5)
        self.dec_layer5 = keras.layers.normalization.batch_normalization.BatchNormalization()(self.dec_layer5)
        self.dec_layer5 = keras.layers.Add()([self.enc_layer5_r, self.dec_layer5])
        self.dec_layer4 = keras.layers.UpSampling1D(autoencoder_layer4_strides)(self.dec_layer5)
        self.dec_layer4 = keras.layers.Cropping1D(cropping=(0, 1))(self.dec_layer4)
        self.dec_layer4 = keras.layers.Conv1DTranspose(filters=autoencoder_layer4_filters,
                                                       kernel_size=autoencoder_layer4_ks, padding="same",
                                                       activation=LeakyReLU(0.01))(self.dec_layer4)
        self.dec_layer4 = keras.layers.normalization.batch_normalization.BatchNormalization()(self.dec_layer4)
        self.dec_layer4 = keras.layers.Add()([self.enc_layer4_r, self.dec_layer4])
        self.dec_layer3 = keras.layers.UpSampling1D(autoencoder_layer3_strides)(self.dec_layer4)
        self.dec_layer3 = keras.layers.Cropping1D(cropping=1)(self.dec_layer3)
        self.dec_layer3 = keras.layers.Conv1DTranspose(filters=autoencoder_layer3_filters,
                                                       kernel_size=autoencoder_layer3_ks, padding="same",
                                                       activation=LeakyReLU(0.01))(self.dec_layer3)
        self.dec_layer3 = keras.layers.normalization.batch_normalization.BatchNormalization()(self.dec_layer3)
        self.dec_layer3 = keras.layers.Add()([self.enc_layer3_r, self.dec_layer3])
        self.dec_layer2 = keras.layers.UpSampling1D(autoencoder_layer2_strides)(self.dec_layer3)
        self.dec_layer2 = keras.layers.Cropping1D(cropping=2)(self.dec_layer2)
        self.dec_layer2 = keras.layers.Conv1DTranspose(filters=autoencoder_layer2_filters,
                                                       kernel_size=autoencoder_layer2_ks, padding="same",
                                                       activation=LeakyReLU(0.01))(self.dec_layer2)
        self.dec_layer2 = keras.layers.normalization.batch_normalization.BatchNormalization()(self.dec_layer2)
        self.dec_layer2 = keras.layers.Add()([self.enc_layer2_r, self.dec_layer2])
        self.dec_layer1 = keras.layers.UpSampling1D(autoencoder_layer1_strides)(self.dec_layer2)
        self.dec_layer1 = keras.layers.Conv1DTranspose(filters=autoencoder_layer1_filters,
                                                       kernel_size=autoencoder_layer1_ks, padding="same",
                                                       activation=LeakyReLU(0.01))(self.dec_layer1)
        self.dec_layer1 = keras.layers.normalization.batch_normalization.BatchNormalization()(self.dec_layer1)
        self.dec_layer1 = keras.layers.Add()([self.enc_layer1_r, self.dec_layer1])
        self.linear_proj = keras.layers.GlobalAveragePooling1D()(self.dec_layer1)
        self.linear_proj = keras.layers.Dense(self.input_size[0], activation=LeakyReLU(0.01))(self.linear_proj)
        self.linear_proj = keras.layers.Dropout(rate=0.1)(self.linear_proj)
        self.linear_proj = keras.layers.Dense(self.input_size[0], activation="linear")(self.linear_proj)
        self.set_model(Model(inputs=input, outputs=self.linear_proj))
        return self

    def load_training_set(self, **kwargs):
        training_dir = kwargs.get('training_dir')
        return [str(file) for file in list(pathlib.Path(training_dir).glob('*_lc.csv'))]

    def instance_generator(self, dataset, dir, batch_size, input_sizes, type_to_label, zero_epsilon):
        return DetrendModelGenerator(dataset, batch_size, input_sizes, zero_epsilon)

    def instance_loss_accuracy(self):
        #loss = tf.keras.losses.MeanAbsolutePercentageError(reduction=losses_utils.ReductionV2.AUTO)
        loss = intransit_weighted_mean_squared_error
        accuracy = FixedMean()
        return loss, accuracy

    def instance_metrics(self):
        return []

    def plot_metrics(self, model_dir, steps_per_epoch, with_validation=False):
        return []
