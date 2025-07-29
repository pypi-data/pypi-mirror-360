import glob
import logging
import os
from threading import Thread
from typing import List

import foldedleastsquares.stats
import numpy
import matplotlib.pyplot as plt
import pandas as pd
from keras import backend as K
import keras
import numpy as np
import tensorflow as tf
import time

from astropy.timeseries import LombScargle
from keras.layers.activation.relu import ReLU
from keras.losses import BinaryCrossentropy
from keras.metrics import Precision, PrecisionAtRecall, Recall, AUC, BinaryAccuracy
from keras.optimizers import Adam
from keras.utils import plot_model
from keras.layers import LeakyReLU
from keras_nlp.src.layers import TransformerEncoder
from lightkurve import TessLightCurve
from numpy import ndarray
from sklearn.utils import shuffle

from exoml.ml.callback.early_stopping import ExoMlEarlyStopping
from exoml.ml.callback.learning_rate import WarmUpAndLinDecreaseCallback
from exoml.ml.callback.training_data_aware import ModelDirDataAwareCallback, ValidationDataAwareCallback
from exoml.ml.log.get_weights_logger import ModelWeightsLogger
from exoml.ml.log.with_logging import WithLogging
from exoml.ml.model.base_model import HyperParams
from exoml.santo.santo_generator import SantoGenerator
from exoml.santo.santo_predict_generator import SantoPredictGenerator


def weighted_binary_crossentropy_param(weight=1):
    def weighted_binary_crossentropy(y_true, y_pred, weight=weight):
        y_true = K.clip(y_true, K.epsilon(), 1 - K.epsilon())
        y_pred = K.clip(y_pred, K.epsilon(), 1 - K.epsilon())
        logloss = -(y_true * K.log(y_pred) * weight + (1 - y_true) * K.log(1 - y_pred))
        return K.mean(logloss, axis=-1)
    return weighted_binary_crossentropy


def clean_to_float(x):
    return float(str(x).strip("\"'").strip("\"").strip("'"))


class SANTO(WithLogging):
    """
    Self-Attention Neural Network for Transiting Objects
    """
    def __init__(self, transformer_layers=0, transformer_heads=1, name="SANTO") -> None:
        super().__init__()
        self.name = "SANTO"
        self.steps_per_epoch = 1
        self.transformer_layers = transformer_layers
        self.transformer_heads = transformer_heads

    def load(self, dir, hyperparams: HyperParams):
        self.model = tf.keras.models.load_model(dir) #, custom_objects={'loss': self.loss(hyperparams)})


    def inform(self, dir):
        """
        Creates summary and a visual plot of the model
        :param dir: the directory to store the plot
        :return: the object itself
        """
        logging.info("Creating model plot and summary")
        dir = dir + self._get_model_dir()
        if not os.path.exists(dir):
            os.mkdir(dir)
        try:
            plot_model(self.model, dir + '/network.png', show_shapes=True)
        except Exception as e:
            logging.exception("Can't plot model network.png")
        self.model.summary()
        ModelWeightsLogger().log_model_weights(self.model)
        return self

    def initialize(self, lcs_dir, output_dir, hyperparams: HyperParams, input_dim=500,
              cores=os.cpu_count() // 2, load_checkpoint=False):
        input_layer = keras.Input(shape=(input_dim, 1), name="input")
        if self.transformer_layers > 0:
            # outputs = TransformerClassifier(transformer_input_size=input_dim, patch_size=input_dim,
            #                                 num_heads=self.transformer_heads, mlp_dim=input_dim,
            #                                 hyperparams=hyperparams, num_blocks=self.transformer_layers,
            #                                 classes=1)(input_layer)
            flux_branch: keras.layers.Layer = input_layer
            for _ in range(self.transformer_layers):
                flux_branch = TransformerEncoder(
                    intermediate_dim=input_dim,
                    num_heads=self.transformer_heads,
                    dropout=hyperparams.dropout_rate,
                    activation=LeakyReLU(),
                    layer_norm_epsilon=1e-05,
                    kernel_initializer="glorot_uniform",
                    bias_initializer="zeros",
                    normalize_first=False
                )(flux_branch)
                # flux_branch = keras.layers.MultiHeadAttention(
                #     key_dim=input_dim, num_heads=self.transformer_heads, dropout=hyperparams.dropout_rate
                # )(input_layer, input_layer)
                # flux_branch = keras.layers.Dropout(hyperparams.dropout_rate)(flux_branch)
                # flux_branch = keras.layers.LayerNormalization(epsilon=1e-6)(flux_branch)
                # res = flux_branch + input_layer
                # # Feed Forward Part
                # flux_branch = keras.layers.Conv1D(filters=input_dim, kernel_size=1, activation="relu")(res)
                # flux_branch = keras.layers.Dropout(hyperparams.dropout_rate)(flux_branch)
                # flux_branch = keras.layers.Conv1D(filters=input_layer.shape[-1], kernel_size=1)(flux_branch)
                # flux_branch = keras.layers.LayerNormalization(epsilon=1e-6)(flux_branch)
                # flux_branch = flux_branch + res
            flux_branch = keras.layers.GlobalAveragePooling1D(data_format="channels_last")(flux_branch)
            flux_branch = keras.layers.Dense(input_dim, activation="relu")(flux_branch)
            flux_branch = keras.layers.Dropout(hyperparams.dropout_rate)(flux_branch)
            outputs = keras.layers.Dense(1, activation="sigmoid")(flux_branch)
        else:
            leaky_relu_alpha = 0.01
            flux_branch: keras.layers.Layer = input_layer
            # flux_branch = keras.layers.normalization.batch_normalization.BatchNormalization()(flux_branch)
            # flux_branch = keras.layers.Dense(64, activation=LeakyReLU())(keras.layers.Flatten()(flux_branch))
            conv_small = keras.layers.Conv1D(filters=16, kernel_size=3, padding="same",
                                             activation=LeakyReLU(leaky_relu_alpha))(flux_branch)
            conv_medium = keras.layers.Conv1D(filters=16, kernel_size=15, padding="same",
                                              activation=LeakyReLU(leaky_relu_alpha))(flux_branch)
            conv_large = keras.layers.Conv1D(filters=16, kernel_size=90, padding="same",
                                             activation=LeakyReLU(leaky_relu_alpha))(flux_branch)
            flux_branch = keras.layers.Concatenate(axis=-1)([conv_small, conv_medium, conv_large])
            flux_branch = keras.layers.SpatialDropout1D(hyperparams.dropout_rate)(flux_branch)
            flux_branch = keras.layers.Conv1D(filters=16, kernel_size=90, padding="same",
                                              activation=LeakyReLU(leaky_relu_alpha))(flux_branch)
            flux_branch = keras.layers.MaxPooling1D(pool_size=10, strides=2)(flux_branch)
            # flux_branch = keras.layers.normalization.batch_normalization.BatchNormalization()(flux_branch)
            flux_branch = keras.layers.SpatialDropout1D(rate=hyperparams.spatial_dropout_rate)(flux_branch)
            conv1_branch = flux_branch
            conv1_branch: keras.layers.Layer = keras.layers.Flatten()(conv1_branch)
            conv1_branch = keras.layers.Dense(8, activation=LeakyReLU(leaky_relu_alpha),
                                              kernel_regularizer=tf.keras.regularizers.L1L2(
                                                  l1=hyperparams.l1_regularization, l2=hyperparams.l2_regularization))(
                conv1_branch)
            conv1_branch = keras.layers.Dropout(hyperparams.dropout_rate)(conv1_branch)
            flux_branch = keras.layers.Conv1D(filters=32, kernel_size=30, padding="same",
                                              activation=LeakyReLU(leaky_relu_alpha))(flux_branch)
            flux_branch = keras.layers.MaxPooling1D(pool_size=4, strides=2)(flux_branch)
            # flux_branch = keras.layers.normalization.batch_normalization.BatchNormalization()(flux_branch)
            flux_branch = keras.layers.SpatialDropout1D(rate=hyperparams.spatial_dropout_rate)(flux_branch)
            conv2_branch = flux_branch
            conv2_branch: keras.layers.Layer = keras.layers.Flatten()(conv2_branch)
            conv2_branch = keras.layers.Dense(16, activation=LeakyReLU(leaky_relu_alpha),
                                              kernel_regularizer=tf.keras.regularizers.L1L2(
                                                  l1=hyperparams.l1_regularization, l2=hyperparams.l2_regularization))(
                conv2_branch)
            conv2_branch = keras.layers.Dropout(hyperparams.dropout_rate)(conv2_branch)
            flux_branch = keras.layers.Conv1D(filters=64, kernel_size=15, padding="same",
                                              activation=LeakyReLU(leaky_relu_alpha))(flux_branch)
            flux_branch = keras.layers.MaxPooling1D(pool_size=3, strides=2)(flux_branch)
            # flux_branch = keras.layers.normalization.batch_normalization.BatchNormalization()(flux_branch)
            flux_branch = keras.layers.SpatialDropout1D(rate=hyperparams.spatial_dropout_rate)(flux_branch)
            conv3_branch = flux_branch
            conv3_branch: keras.layers.Layer = keras.layers.Flatten()(conv3_branch)
            conv3_branch = keras.layers.Dense(32, activation=LeakyReLU(leaky_relu_alpha),
                                              kernel_regularizer=tf.keras.regularizers.L1L2(
                                                  l1=hyperparams.l1_regularization, l2=hyperparams.l2_regularization))(
                conv3_branch)
            conv3_branch = keras.layers.Dropout(hyperparams.dropout_rate)(conv3_branch)
            flux_branch = keras.layers.Conv1D(filters=128, kernel_size=8, padding="same",
                                              activation=LeakyReLU(leaky_relu_alpha))(flux_branch)
            flux_branch = keras.layers.MaxPooling1D(pool_size=2, strides=2)(flux_branch)
            conv4_branch = flux_branch
            conv4_branch: keras.layers.Layer = keras.layers.Flatten()(conv4_branch)
            conv4_branch = keras.layers.Dense(64, activation=LeakyReLU(leaky_relu_alpha),
                                              kernel_regularizer=tf.keras.regularizers.L1L2(
                                                  l1=hyperparams.l1_regularization, l2=hyperparams.l2_regularization))(
                conv4_branch)
            conv4_branch = keras.layers.Dropout(hyperparams.dropout_rate)(conv4_branch)
            flux_branch = keras.layers.Concatenate(axis=1)([
                conv1_branch, conv2_branch, conv3_branch, conv4_branch])
            flux_branch = keras.layers.Dense(512, activation=LeakyReLU(leaky_relu_alpha),
                                             kernel_regularizer=tf.keras.regularizers.L1L2(
                                                 l1=hyperparams.l1_regularization, l2=hyperparams.l2_regularization))(
                flux_branch)
            # flux_branch = keras.layers.Dropout(hyperparams.dropout_rate)(flux_branch)
            # flux_branch = keras.layers.Dense(16, activation=LeakyReLU(leaky_relu_alpha),
            #                   kernel_regularizer=tf.keras.regularizers.L1L2(l1=hyperparams.l1_regularization, l2=hyperparams.l2_regularization))(flux_branch)
            flux_branch = keras.layers.Dropout(hyperparams.dropout_rate)(flux_branch)
            outputs: keras.layers.Layer = keras.layers.Dense(1, activation="sigmoid")(flux_branch)
        print("Preparing data sets")
        self.model: keras.Model = keras.Model(inputs=input_layer, outputs=outputs)
        self.model.run_eagerly = hyperparams.run_eagerly
        model_path = output_dir + self._get_model_dir()
        train_filenames, validation_filenames, test_filenames = \
            self.prepare_training_data(lcs_dir, model_path, hyperparams.batch_size, hyperparams.train_percent,
                                       hyperparams.validation_percent, hyperparams.training_set_limit,
                                       hyperparams.balance_class_id, hyperparams.balance_class_sampling)

    def train(self, lcs_dir, output_dir, hyperparams: HyperParams, input_dim=500, step_indexes=1):
        print("Begin training")
        tf.keras.backend.clear_session()
        self.inform(output_dir)
        model_path = output_dir + self._get_model_dir()
        if not os.path.exists(model_path):
            os.mkdir(model_path)
        train_df = pd.read_csv(model_path + '/train_dataset.csv')
        train_filenames = train_df.loc[:, 'name'].tolist()
        validation_df = pd.read_csv(model_path + '/validation_dataset.csv')
        validation_filenames = validation_df.loc[:, 'name'].tolist()
        training_batch_generator = self.instance_generator(train_filenames, lcs_dir, hyperparams.batch_size,
                                                           input_dim, None, hyperparams.zero_epsilon,
                                                           shuffle=False, step_indexes=step_indexes)
        steps_per_epoch = training_batch_generator.steps_per_epoch()
        optimizer: keras.optimizers.Optimizer = self.build_optimizer(hyperparams, steps_per_epoch)
        loss, accuracy = self.instance_loss_accuracy(hyperparams)
        self.compile(optimizer, loss,
                     metrics=[accuracy] + self.instance_metrics() + hyperparams.metrics,
                     run_eagerly=hyperparams.run_eagerly)
        if not hyperparams.dry_run:
            logging.info("Initializing training and validation generators with (batch_size," + str(hyperparams.batch_size) +
                         ") (self.input_size," + str(input_dim) +
                         ") (zero_epsilon," + str(hyperparams.zero_epsilon) +
                         ")")
            validation_batch_generator = self.instance_generator(validation_filenames, lcs_dir, hyperparams.batch_size,
                                                                 input_dim, None, hyperparams.zero_epsilon,
                                                                 shuffle=False, step_indexes=step_indexes)
            for callback in hyperparams.callbacks:
                if issubclass(callback.__class__, ModelDirDataAwareCallback):
                    callback.set_model_dir(model_path)
                if issubclass(callback.__class__, ValidationDataAwareCallback):
                    callback.set_validation_data(validation_batch_generator)
            if hyperparams.early_stopping_patience > 0 and hyperparams.early_stopping_delta > 0:
                hyperparams.callbacks = hyperparams.callbacks + [ExoMlEarlyStopping(
                    monitor="val_loss",
                    min_delta=hyperparams.early_stopping_delta,
                    patience=hyperparams.early_stopping_patience,
                    verbose=0,
                    mode="auto",
                    baseline=None,
                    restore_best_weights=False,
                )]
            model_validation_steps = validation_batch_generator.steps_per_epoch()
            class_weights = hyperparams.class_loss_weights if hyperparams.class_loss_weights is not None \
                else training_batch_generator.class_weights()
            logging.info("Initializing training with (epochs," + str(hyperparams.epochs) +
                         ") (steps_per_epoch," + str(steps_per_epoch) +
                         ")")
            self.save(output_dir)
            fit_history = self.fit_model(hyperparams, training_batch_generator,
                                         steps_per_epoch, class_weights,
                                         validation_batch_generator,
                                         model_validation_steps, hyperparams.epochs)
            self.save(output_dir)

    def predict(self, lcs_dir: str, target_files: list, model_dir: str, batch_size: int = 1024, input_size: int = 2500,
                zero_epsilon: float = 1e-7, plot=False, plot_positives=False, tagged_data: bool = False,
                target_name: str = ""):
        self.load_model(model_dir)
        half_window = input_size // 2
        generator = SantoPredictGenerator(lcs_dir, target_files, input_size=input_size, step_size=1,
                                          batch_size=batch_size, zero_epsilon=zero_epsilon)
        predictions = self.model.predict(generator)
        left = np.linspace(0.1, 1.0, input_size // 2, endpoint=False)
        right = np.linspace(1.0, 0.1, input_size // 2)
        triangle_weights = np.concatenate([left, right])
        current_index = 0
        files_predictions = {}
        for target_file in target_files:
            file_content = pd.read_csv(lcs_dir + '/' + target_file).values
            flux_key = 1
            if file_content.shape[0] > 40:
                file_content = np.transpose(file_content)
                flux_key = 2
            file_content = np.vectorize(clean_to_float)(file_content)
            file_predictions = predictions[current_index:current_index + file_content.shape[1]]
            files_predictions[target_file] = file_predictions.reshape(file_predictions.shape[0])
            if plot:
                N = files_predictions[target_file].shape[0]
                fig, axs = plt.subplots(2 if not tagged_data else 3, 1, figsize=(16, 8),
                                        constrained_layout=True)
                keys_greater_than_zero = np.argwhere(file_content[flux_key][0:N] > zero_epsilon).flatten()
                min_flux = np.nanmin(file_content[flux_key][keys_greater_than_zero])
                axs[0].set_ylim(bottom=min_flux)
                axs[0].scatter(np.arange(0, N), file_content[flux_key][0:N])
                axs[1].plot(np.arange(0, N), files_predictions[target_file])
                if tagged_data:
                    axs[2].plot(np.arange(0, N), file_content[2][0:N])
                plt.title(target_file)
                plt.show()
            current_index = current_index + len(file_content)
        return files_predictions

    def tokenize_found_transits(self, time, flux, predictions, window_size=500, plot=False, tagged_data=None):
        positive_predictions = predictions
        for _ in np.arange(0, 10):
            positive_predictions = np.convolve(positive_predictions, np.ones(25) / 25, mode='same')
        sigma_low_indexes = np.argwhere(predictions < 3 * np.nanstd(predictions)).flatten()
        positive_predictions[sigma_low_indexes] = 0
        diff = np.diff(positive_predictions)
        local_maxima = (np.hstack([diff, 0]) < 0) & (np.hstack([0, diff]) > 0)
        local_maxima_indexes = np.argwhere(local_maxima).flatten()
        if plot:
            for index in local_maxima_indexes:
                if index > window_size // 2:
                    fig, axs = plt.subplots(2 if tagged_data is None else 3, 1, figsize=(16, 8), constrained_layout=True)
                    above_indexes = np.argwhere(predictions[index - window_size // 2:index + window_size // 2] >= 3 * np.nanstd(predictions))
                    below_indexes = np.argwhere(predictions[index - window_size // 2:index + window_size // 2] < 3 * np.nanstd(predictions))
                    axs[0].scatter(time[index - window_size // 2:index + window_size // 2][above_indexes],
                                   flux[index - window_size // 2:index + window_size // 2][above_indexes],
                                   color='blue')
                    axs[1].scatter(time[index - window_size // 2:index + window_size // 2][above_indexes],
                                predictions[index - window_size // 2:index + window_size // 2][above_indexes],
                                color='blue')
                    axs[0].scatter(time[index - window_size // 2:index + window_size // 2][below_indexes],
                                   flux[index - window_size // 2:index + window_size // 2][below_indexes],
                                   color='firebrick')
                    axs[1].scatter(time[index - window_size // 2:index + window_size // 2][below_indexes],
                                predictions[index - window_size // 2:index + window_size // 2][below_indexes],
                                color='firebrick')
                    if tagged_data is not None:
                        axs[2].scatter(time[index - window_size // 2:index + window_size // 2][above_indexes],
                                    tagged_data[index - window_size // 2:index + window_size // 2][above_indexes],
                                    color='blue')
                    plt.show()
                    plt.close(fig)
                    plt.clf()
        return local_maxima_indexes


    def load_model(self, dir, custom_objects={}, compile=False):
        custom_objects['WarmUpAndLinDecreaseCallback'] = WarmUpAndLinDecreaseCallback
        custom_objects['ThresholdAtPrecision'] = None
        logging.info("Loading model from %s", dir)
        self.set_model(tf.keras.models.load_model(dir, compile=compile, custom_objects=custom_objects))
        return self

    def set_model(self, model):
        """
        Stores the model in a class attribute
        :param model: the model to be stored
        """
        self.model = model

    def _get_model_dir(self):
        return self.name + '_model/'

    def instance_loss_accuracy(self, hyperparams: HyperParams):
        return BinaryCrossentropy() if hyperparams.custom_loss is None else hyperparams.custom_loss, BinaryAccuracy()

    def compile(self, optimizer, loss, metrics=None, run_eagerly=False, tuner=False):
        """
        Compiles and prepares the model for training
        :param optimizer: the optimizer to be used
        :param loss: the loss to be used
        :param metrics: the metrics to be used
        :return: the object itself
        """
        if metrics is None:
            metrics = []
        metrics_str = [str(metric) for metric in metrics]
        logging.info("Compiling model with optimizer " + str(optimizer) + ", loss " + str(loss) + " and metrics [" +
                     ",".join(metrics_str) + "]")
        self.model.compile(optimizer=optimizer, loss=loss, metrics=metrics)
        self.model.run_eagerly = run_eagerly
        return self

    def instance_metrics(self):
        return [Precision(name="precision"), Recall(name="recall"),
                #F1Score(num_classes=1, threshold=0.5, average='weighted', name='f1_score'),
                PrecisionAtRecall(recall=0.99, name="p@r99", num_thresholds=1000),
                #ThresholdAtPrecision(precision=0.99, name="t@p99", num_thresholds=1000),
                AUC(name="roc_auc"),
                AUC(curve="PR", name="pr_auc")]

    def instance_generator(self, dataset, dir, batch_size, input_sizes, type_to_label, zero_epsilon, shuffle=True,
                           step_indexes=1):
        return SantoGenerator(dir, dataset, input_size=input_sizes, step_size=1, batch_size=batch_size,
                              shuffle=shuffle, zero_epsilon=zero_epsilon, indexes_steps=step_indexes)

    def load_training_set(self, **kwargs):
        training_dir = kwargs.get('training_dir')
        target_files = glob.glob(f'/{training_dir}/**/*.csv', recursive=True)
        target_files = [os.path.basename(path) for path in target_files]
        return target_files

    def prepare_training_data(self, training_dir, output_dir, batch_size, train_percent=0.8, validation_percent=0.1,
                              training_set_limit=None, balance_class_id=None, balance_class_sampling=None):
        if not os.path.exists(output_dir):
            os.mkdir(output_dir)
        training_dataset = self.load_training_set(training_dir=training_dir)
        training_dataset = shuffle(training_dataset)
        test_dataset = None
        training_dataset = shuffle(training_dataset)
        if training_set_limit is not None:
            if isinstance(training_dataset, pd.DataFrame):
                training_dataset = training_dataset[:training_set_limit]
            else:
                training_dataset = training_dataset[:training_set_limit]
        dataset_length = len(training_dataset)
        train_last_index = int(dataset_length * train_percent)
        validation_last_index = train_last_index + int(dataset_length * validation_percent)
        validation_last_index = validation_last_index if validation_last_index < dataset_length else dataset_length
        test_last_index = dataset_length - 1
        train_dataset_filename = output_dir + "/train_dataset.csv"
        validation_dataset_filename = output_dir + "/validation_dataset.csv"
        test_dataset_filename = output_dir + "/test_dataset.csv"
        logging.info("Storing train and test file names in " + train_dataset_filename + " and " +
                     validation_dataset_filename)
        if os.path.exists(train_dataset_filename):
            os.remove(train_dataset_filename)
        if os.path.exists(validation_dataset_filename):
            os.remove(validation_dataset_filename)
        if os.path.exists(test_dataset_filename):
            os.remove(test_dataset_filename)
        train_filenames = training_dataset[0:train_last_index]
        validation_filenames = training_dataset[train_last_index:validation_last_index]
        test_filenames = []
        if validation_last_index != test_last_index:
            test_filenames = test_dataset if test_dataset is not None else training_dataset[validation_last_index:test_last_index]
            test_df = pd.DataFrame(columns=[])
            test_df['name'] = test_filenames
            test_df.to_csv(test_dataset_filename)
        train_df = pd.DataFrame(columns=['name'])
        train_df['name'] = train_filenames
        val_df = pd.DataFrame(columns=['name'])
        val_df['name'] = validation_filenames
        train_df.to_csv(train_dataset_filename)
        val_df.to_csv(validation_dataset_filename)
        logging.info("Training set is of length %s (%s %%)", len(train_filenames),
                     len(train_filenames) / dataset_length * 100)
        logging.info("Validation set is of length %s (%s %%)", len(validation_filenames),
                     len(validation_filenames) / dataset_length * 100)
        logging.info("Testing set is of length %s (%s %%)", len(test_filenames),
                     len(test_filenames) / dataset_length * 100)
        return train_filenames, validation_filenames, test_filenames

    def save(self, dir, model_dir=None):
        if model_dir is None:
            dest_dir = dir + '/' + self._get_model_dir()
        else:
            dest_dir = dir + '/' + model_dir
        logging.info("Saving model into %s", dest_dir)
        self.model.save(dest_dir)
        logging.info("Saved model")
        return dest_dir

    def fit_model(self, hyperparams, training_batch_generator, steps_per_epoch, class_weights,
                  validation_batch_generator, model_validation_steps, epochs):
        fit_history = self.model.fit(x=training_batch_generator,
                                     steps_per_epoch=steps_per_epoch,
                                     epochs=hyperparams.epochs, verbose=1,
                                     validation_data=validation_batch_generator,
                                     validation_steps=model_validation_steps,
                                     callbacks=hyperparams.callbacks,
                                     use_multiprocessing=hyperparams.cores > 0, workers=1
            if hyperparams.cores <= 0 else hyperparams.cores)
        return fit_history

    def compute_initial_lr(self, hyperparams: HyperParams):
        if hyperparams.lr_progression != 1:
            initial_lr = hyperparams.initial_learning_rate
        else:
            initial_lr = hyperparams.learning_rate_schedule \
                if hyperparams.learning_rate_schedule is not None else hyperparams.initial_learning_rate
        return initial_lr

    def build_optimizer(self, hyperparams, steps_per_epoch):
        # from exoml.ml.callback.learning_rate import MultiOptimizer
        from tensorflow_addons.optimizers import MultiOptimizer
        initial_lr = self.compute_initial_lr(hyperparams)
        optimizer = self.build_swa_optimizer(hyperparams, initial_lr, steps_per_epoch)
        if hyperparams.lr_progression != 1:
            optimizer.progressive_lr_factor = 1
            optimizers_and_layers = []
            standard_layers = []
            progressive_lr_factor = 1
            for layer in self.model.layers:
                if 'final' in layer.name:
                    progressive_lr_factor = progressive_lr_factor * hyperparams.lr_progression
                    progressive_optimizer = self.build_swa_optimizer(hyperparams, progressive_lr_factor * initial_lr, steps_per_epoch)
                    progressive_optimizer.progressive_lr_factor = progressive_lr_factor
                    optimizers_and_layers = optimizers_and_layers + [
                        (progressive_optimizer, layer)]
                else:
                    standard_layers = standard_layers + [layer]
            optimizers_and_layers = [(optimizer, standard_layers)] + optimizers_and_layers
            optimizer = MultiOptimizer(optimizers_and_layers)
        return optimizer

    def build_swa_optimizer(self, hyperparams: HyperParams, lr, steps_per_epoch):
        # from exoml.ml.callback.learning_rate import SWA
        from tensorflow_addons.optimizers import SWA
        if hyperparams.stochastic_weight_average_wait > 0:
            optimizer = tf.keras.optimizers.legacy.Adam(lr,
                                                        beta_1=0.9, beta_2=0.98, epsilon=1e-9,
                                                        clipnorm=hyperparams.gradient_clip_norm,
                                                        clipvalue=hyperparams.gradient_clip_value)
            optimizer = SWA(optimizer,
                                           start_averaging=steps_per_epoch * hyperparams.stochastic_weight_average_wait,
                                           average_period=steps_per_epoch)
            if isinstance(lr, (int, float)):
                optimizer.lr = lr
            else:
                optimizer.lr = hyperparams.initial_learning_rate
        else:
            optimizer = Adam(lr,
                                                 beta_1=0.9, beta_2=0.98, epsilon=1e-9,
                                                 clipnorm=hyperparams.gradient_clip_norm,
                                                 clipvalue=hyperparams.gradient_clip_value)
        return optimizer

    def run_epoch(self, epoch, lcs_dir, model_dir, target_files, hyperparams, input_dim, transformer_model, optimizer,
                  training=False, cores=os.cpu_count() // 2, training_log_df=None):
        training_preparation_threads: list[Thread] = []
        losses = []
        accuracies = []
        precisions = []
        recalls = []
        pr99s = []
        accuracy: keras.metrics.Metric = tf.keras.metrics.SparseCategoricalAccuracy(name="accuracy")
        precision: keras.metrics.Metric = tf.keras.metrics.Precision(name="precision")
        recall: keras.metrics.Metric = tf.keras.metrics.Recall(name="recall")
        pr99: keras.metrics.Metric = tf.keras.metrics.PrecisionAtRecall(recall=0.99, name="p@r99")
        step = 0
        for file_index, last_target_file in enumerate(target_files):
            last_target_file_pos: int = 0
            flux = np.loadtxt(f'{lcs_dir}/{last_target_file}', delimiter=',')
            if np.nanmin(flux[1]) == 1:
                continue
            train_batch: ndarray = np.zeros((hyperparams.batch_size, input_dim))
            train_tags: ndarray = np.zeros((hyperparams.batch_size, 1))
            iteration: int = 0
            data_remaining: bool = True
            while data_remaining:
                # training_preparation_threads: list[Thread] = []
                # for core in range(0, cores):
                #     training_preparation_threads =
                batch_index = iteration // hyperparams.batch_size
                iteration_index = iteration % hyperparams.batch_size
                # TODO mask all out of transit information not between 3 durations of a transit
                flux_data = flux[0][last_target_file_pos:last_target_file_pos + input_dim] / 2
                tags_data_index = last_target_file_pos + input_dim // 2 - 1
                tags_data = flux[1][tags_data_index - input_dim:tags_data_index + input_dim]
                last_target_file_pos = last_target_file_pos + 1
                data_remaining = last_target_file_pos < flux.shape[1] - input_dim
                is_last_iteration = (iteration + 1) % hyperparams.batch_size == 0 or not data_remaining
                if not training or is_last_iteration or np.any(np.abs(tags_data - 1) > 1e-6):
                    tags_data = flux[1][tags_data_index]
                    train_batch[iteration_index] = flux_data
                    train_tags[iteration_index] = tags_data
                    oot_mask = np.abs(train_tags[iteration_index] - 1) < 1e-6
                    train_tags[iteration_index][oot_mask] = 0
                    train_tags[iteration_index][~oot_mask] = 1
                    if is_last_iteration:
                        #oot_mask = np.abs(train_tags.flatten()) < 1e-6
                        #plt.scatter(np.arange(0, iteration_index + 1)[oot_mask], flux[0][0:iteration_index + 1][oot_mask],
                        #            color='blue')
                        #plt.scatter(np.arange(0, iteration_index + 1)[~oot_mask], flux[0][0:iteration_index + 1][~oot_mask],
                        #            color='red')
                        #plt.show()
                        #positives_positions = np.argwhere(train_tags.flatten() == True)
                        #plt.scatter(np.arange(0, 500), train_batch[positives_positions][0], color = 'blue')
                        #plt.show()
                        train_tags_tensor = tf.convert_to_tensor(train_tags, dtype=np.float32)
                        train_batch_tensor = tf.convert_to_tensor(train_batch, dtype=np.float32)
                        train_tags_tensor = tf.reshape(train_tags_tensor, [hyperparams.batch_size, 1])
                        if training:
                            with tf.GradientTape() as tape:
                                tape.watch(transformer_model.trainable_variables)
                                flux_predictions = transformer_model(train_batch)
                                loss = transformer_model.compute_loss(train_batch_tensor, train_tags_tensor, flux_predictions)
                            losses.append(loss.numpy())
                            gradients = tape.gradient(loss, transformer_model.trainable_variables)
                            optimizer.apply_gradients(zip(gradients, transformer_model.trainable_variables))
                            for gradient in gradients:
                                if np.any(gradient.numpy() == 0):
                                    print("There are gradients with zero values")
                                    break
                            if np.all(flux_predictions == 0):
                                print("All predictions are 0")
                            if np.all(flux_predictions == 1):
                                print("All predictions are 1")
                            step = step + 1
                        else:
                            flux_predictions = transformer_model.predict_on_batch(train_batch)
                        # flux_predictions_reshape = tf.reshape(flux_predictions, [hyperparams.batch_size, input_dim])
                        train_tags_tensor = tf.reshape(train_tags_tensor, [hyperparams.batch_size, 1])
                        accuracy(train_tags_tensor, flux_predictions)
                        precision(train_tags_tensor, flux_predictions)
                        recall(train_tags_tensor, flux_predictions)
                        pr99(train_tags_tensor, flux_predictions)
                        accuracies.append(accuracy.result().numpy())
                        precisions.append(precision.result().numpy())
                        recalls.append(recall.result().numpy())
                        pr99s.append(pr99.result().numpy())
                        if training:
                            print("Epoch {} File {} Batch {} Loss {} Accuracy {} Precision {} Recall {} P@R99 {}"
                                  .format(epoch + 1, file_index, step, loss, accuracy.result(),
                                          precision.result(), recall.result(), pr99.result()))
                            if training_log_df is not None:
                                if isinstance(self.model.optimizer, MultiOptimizer):
                                    learning_rate = K.eval(K.eval(self.model.optimizer.optimizer_specs[0]['optimizer'].lr))
                                else:
                                    learning_rate = K.eval(self.model.optimizer._decayed_lr(tf.float32))
                                training_log_df = pd.concat([training_log_df, pd.DataFrame.from_dict(
                                    {'lr': [learning_rate], 'epoch': [epoch], 'batch': [step], 'loss': [loss.numpy()],
                                     'accuracy': [accuracy.result().numpy()], 'precision': [precision.result().numpy()],
                                     'recall': [recall.result().numpy()],
                                     'p@r99': [pr99.result().numpy()]})], ignore_index=True)
                                training_log_df.to_csv(model_dir + '/training_log.csv', index=False)
                                #self.plot_metrics(model_dir, self.steps_per_epoch, False)
                            accuracy.reset_state()
                            precision.reset_state()
                            recall.reset_state()
                            pr99.reset_state()
                    iteration = iteration + 1
        if not training: 
            print(f"Validation Epoch {epoch + 1} Accuracy {accuracy.result().numpy()} "
                  f"Precision {precision.result().numpy()} Recall {recall.result().numpy()} P@R99 "
                  f"{pr99.result().numpy()}")
            if training_log_df is not None:
                if isinstance(self.model.optimizer, MultiOptimizer):
                    learning_rate = K.eval(K.eval(self.model.optimizer.optimizer_specs[0]['optimizer'].lr))
                else:
                    learning_rate = K.eval(self.model.optimizer._decayed_lr(tf.float32))
                training_log_df = pd.concat([training_log_df, pd.DataFrame.from_dict(
                    {'lr': [learning_rate], 'epoch': [epoch], 'batch': [0],
                     'val_accuracy': [accuracy.result().numpy()], 'val_precision': [precision.result().numpy()],
                     'val_recall': [recall.result().numpy()], 'val_p@r99': [pr99.result().numpy()]})], ignore_index=True)
                training_log_df.to_csv(model_dir + '/training_log.csv', index=False)
        return losses, accuracies, precisions, recalls, pr99s, training_log_df

    def plot_metrics(self, model_dir, steps_per_epoch, training_metrics=[], validation_metrics=[]):
        logging.info("Plotting metrics")
        training_log_df = pd.read_csv(model_dir + '/training_log.csv')
        training_log_df['batch_total'] = training_log_df['batch'] + (training_log_df['epoch'] * steps_per_epoch)
        validation_log_df = training_log_df.dropna(subset=['val_precision', 'val_recall', 'val_p@r99', 'val_accuracy'])
        fig, axs = plt.subplots(2, 2, figsize=(25, 7), constrained_layout=True)
        fig.suptitle(self.name + ' Model Metrics', fontsize=14)
        for metric in validation_metrics:
            axs[metric[2][0]][metric[2][1]].plot(validation_log_df['batch_total'], validation_log_df['val_' + metric[0]],
                           color=metric[1], label='val_' + metric[0], linestyle='--')
        for metric in training_metrics:
            axs[metric[2][0]][metric[2][1]].plot(validation_log_df['batch_total'], validation_log_df[metric[0]],
                           color=metric[1], label=metric[0])
        axs[0][0].set_xlabel("Batch")
        secx = axs[0][0].secondary_xaxis('top',
                                         functions=(lambda x: x / steps_per_epoch, lambda x: x / steps_per_epoch))
        secx.set_xlabel('Epoch')
        axs[0][0].set_ylabel("Learning rate")
        axs[0][0].legend(loc='upper right')
        axs[0][1].set_xlabel("Batch")
        secx = axs[0][1].secondary_xaxis('top',
                                         functions=(lambda x: x / steps_per_epoch, lambda x: x / steps_per_epoch))
        secx.set_xlabel('Epoch')
        axs[0][1].set_ylabel("Loss")
        axs[0][1].legend(loc='upper right')
        axs[1][0].set_xlabel("Batch")
        secx = axs[1][0].secondary_xaxis('top',
                                         functions=(lambda x: x / steps_per_epoch, lambda x: x / steps_per_epoch))
        secx.set_xlabel('Epoch')
        axs[1][0].set_ylabel("Precision/Recall/P@R")
        axs[1][0].legend(loc='upper left')
        axs[1][1].set_xlabel("Batch")
        secx = axs[1][1].secondary_xaxis('top',
                                         functions=(lambda x: x / steps_per_epoch, lambda x: x / steps_per_epoch))
        secx.set_xlabel('Epoch')
        axs[1][1].set_ylabel("Accuracy/F1/AUCs")
        axs[1][1].legend(loc='upper left')
        plt.savefig(model_dir + '/metrics.png')
        plt.close(fig)
        plt.clf()
        logging.info("Plotted metrics")

# SANTO().train("/data/scratch/ml/santo/training_data/", "/data/scratch/exoml/SANTO",
#               hyperparams=HyperParams(batch_size=100, epochs=10, run_eagerly=True))
