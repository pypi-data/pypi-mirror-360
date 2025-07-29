import logging
import os
from functools import reduce

import numpy as np
import pandas as pd
import keras
import tensorflow as tf
from keras.layers import LeakyReLU
from sklearn.utils import shuffle

from exoml.iatson.iatson_og_generator import IatsonOgModelGenerator
from exoml.ml.layers.dropout import AdaptiveStdDropout
from exoml.ml.layers.transformer_classifier import TransformerClassifier
from exoml.ml.model.base_model import CategoricalPredictionSetStats
from exoml.ml.model.imbalanced_binary_model import ImbalancedBinaryModel


class IATSON_og(ImbalancedBinaryModel):
    def __init__(self, class_ids, class_names, type_to_label, hyperparams, channels=2, name='IATSON_og',
                 mode="all") -> None:
        super().__init__(name,
                         [11, 9 * 15, 300, 75, 75, 75, 75, 75, 75],
                         class_ids,
                         type_to_label,
                         hyperparams)
        self.channels = channels
        self.mode = mode

    def _get_focus_flux_conv_branch(self, name, channels=None, additional_inputs=None):
        if not channels:
            channels = self.channels
        leaky_relu_alpha = 0.01
        # TODO use binning error as channel
        focus_flux_input = keras.Input(shape=(self.input_size[3], channels), name=name)
        focus_flux_input_mod = focus_flux_input
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
        focus_flux_branch = keras.layers.Conv1D(filters=32, kernel_size=20, padding="same",
                                                activation=LeakyReLU(leaky_relu_alpha), use_bias=True)(
            focus_flux_branch)
        focus_flux_branch = keras.layers.MaxPooling1D(pool_size=5, strides=1)(focus_flux_branch)
        #focus_flux_branch = keras.layers.normalization.batch_normalization.BatchNormalization()(focus_flux_branch)
        focus_flux_branch = keras.layers.SpatialDropout1D(rate=self.hyperparams.spatial_dropout_rate)(focus_flux_branch)
        focus_flux_branch = keras.layers.Conv1D(filters=64, kernel_size=10, padding="same",
                                                activation=LeakyReLU(leaky_relu_alpha), use_bias=True)(
            focus_flux_branch)
        #focus_flux_branch = keras.layers.normalization.batch_normalization.BatchNormalization()(focus_flux_branch)
        focus_flux_branch = keras.layers.MaxPooling1D(pool_size=3, strides=1)(focus_flux_branch)
        focus_flux_branch = keras.layers.SpatialDropout1D(rate=self.hyperparams.spatial_dropout_rate)(focus_flux_branch)
        focus_flux_branch = keras.layers.Conv1D(filters=128, kernel_size=5, padding="same",
                                                activation=LeakyReLU(leaky_relu_alpha), use_bias=True)(
            focus_flux_branch)
        #focus_flux_branch = keras.layers.normalization.batch_normalization.BatchNormalization()(focus_flux_branch)
        focus_flux_branch = keras.layers.MaxPooling1D(pool_size=3, strides=1)(focus_flux_branch)
        if additional_inputs is not None:
            additional_inputs_branch = additional_inputs
            if self.hyperparams.numerical_white_noise_std is not None:
                additional_inputs_branch = keras.layers.GaussianNoise(
                    stddev=self.hyperparams.numerical_white_noise_std)(additional_inputs_branch)
            focus_flux_branch = keras.layers.Concatenate(axis=1)(
                [focus_flux_branch, keras.layers.Flatten()(additional_inputs_branch)])
        focus_flux_branch = keras.layers.Dense(64, kernel_regularizer=tf.keras.regularizers.L1L2(l1=self.hyperparams.l1_regularization, l2=self.hyperparams.l2_regularization),
                                               activation=LeakyReLU(leaky_relu_alpha))(focus_flux_branch)
        focus_flux_branch = AdaptiveStdDropout(rate=self.hyperparams.dropout_rate,
                                         max_rate=self.hyperparams.dropout_max_rate)(focus_flux_branch)
        focus_flux_branch = keras.layers.LayerNormalization()(focus_flux_branch)
        return focus_flux_input, focus_flux_branch

    def _get_focus_flux_transformer_branch(self, name, transformer_blocks=6, transformer_heads=6, channels=None, additional_inputs=None):
        leaky_relu_alpha = 0.01
        # TODO use binning error as channel
        if channels is None:
            channels = self.channels
        focus_flux_input = keras.Input(shape=(self.input_size[3], channels), name=name)
        focus_flux_input_mod = focus_flux_input
        if self.hyperparams.white_noise_std is not None:
            focus_flux_input_mod = keras.layers.GaussianNoise(stddev=self.hyperparams.white_noise_std)(focus_flux_input_mod)
        focus_flux_input_final = focus_flux_input_mod
        transformer_input_size = self.input_size[3]
        transformer_output_size = self.input_size[3]
        kernel_size = 1
        classes = 128
        flux_branch = TransformerClassifier(transformer_input_size=transformer_input_size, patch_size=kernel_size,
                              num_heads=transformer_heads, mlp_dim=transformer_output_size, hyperparams=self.hyperparams,
                              num_blocks=transformer_blocks, classes=classes)(focus_flux_input_final)
        #flux_branch = keras.layers.GlobalMaxPooling1D()(flux_branch)
        flux_branch = keras.layers.Flatten()(flux_branch)
        if additional_inputs is not None:
            additional_inputs_branch = additional_inputs
            if self.hyperparams.numerical_white_noise_std is not None:
                additional_inputs_branch = keras.layers.GaussianNoise(
                    stddev=self.hyperparams.numerical_white_noise_std)(additional_inputs_branch)
            flux_branch = keras.layers.Concatenate(axis=1)(
                [flux_branch, keras.layers.Flatten()(additional_inputs_branch)])
        flux_branch = keras.layers.Dense(50, kernel_regularizer=tf.keras.regularizers.L1L2(
            l1=self.hyperparams.l1_regularization, l2=self.hyperparams.l2_regularization),
                                         activation=LeakyReLU(leaky_relu_alpha))(flux_branch)
        flux_branch = AdaptiveStdDropout(rate=self.hyperparams.dropout_rate,
                                         max_rate=self.hyperparams.dropout_max_rate)(flux_branch)
        flux_branch = keras.layers.LayerNormalization()(flux_branch)
        return focus_flux_input, flux_branch

    def build(self, use_transformers=False, transformer_blocks=6, transformer_heads=6):
        inputs, final_branch = self.build_transformer(transformer_blocks, transformer_heads) \
            if use_transformers else self.build_convolutional()
        self.set_model(keras.Model(inputs=inputs, outputs=final_branch, name=self.name))
        return self

    def build_convolutional(self):
        leaky_relu_alpha = 0.01
        og_input, og_branch = self._get_focus_flux_conv_branch("og_branch", 2)
        og_branch = keras.layers.Flatten()(og_branch)
        # og_branch = keras.layers.Dense(1000, kernel_regularizer=tf.keras.regularizers.L1L2(
        #     l1=self.hyperparams.l1_regularization, l2=self.hyperparams.l2_regularization),
        #                                activation=LeakyReLU(leaky_relu_alpha), name="final-dense2")(og_branch)
        # og_branch = AdaptiveStdDropout(rate=self.hyperparams.dropout_rate,
        #                                max_rate=self.hyperparams.dropout_max_rate, name="final-dropout2")(og_branch)
        # og_branch = keras.layers.Dense(250, kernel_regularizer=tf.keras.regularizers.L1L2(
        #     l1=self.hyperparams.l1_regularization, l2=self.hyperparams.l2_regularization),
        #                                activation=LeakyReLU(leaky_relu_alpha), name="final-dense3")(og_branch)
        # og_branch = AdaptiveStdDropout(rate=self.hyperparams.dropout_rate,
        #                                max_rate=self.hyperparams.dropout_max_rate, name="final-dropout3")(og_branch)
        # og_branch = keras.layers.Dense(32, kernel_regularizer=tf.keras.regularizers.L1L2(
        #     l1=self.hyperparams.l1_regularization, l2=self.hyperparams.l2_regularization),
        #                                activation=LeakyReLU(leaky_relu_alpha), name="final-dense4")(og_branch)
        # og_branch = AdaptiveStdDropout(rate=self.hyperparams.dropout_rate,
        #                                max_rate=self.hyperparams.dropout_max_rate, name="final-dropout4")(og_branch)
        og_branch = keras.layers.Dense(16, kernel_regularizer=tf.keras.regularizers.L1L2(
            l1=self.hyperparams.l1_regularization, l2=self.hyperparams.l2_regularization),
                                       activation=LeakyReLU(leaky_relu_alpha), name="final-dense5")(og_branch)
        og_branch = AdaptiveStdDropout(rate=self.hyperparams.dropout_rate,
                                       max_rate=self.hyperparams.dropout_max_rate, name="final-dropout5")(og_branch)
        og_branch = keras.layers.Dense(1, activation="sigmoid", name="logits")(og_branch)
        return og_input, og_branch

    def build_transformer(self, transformer_blocks=6, transformer_heads=6):
        leaky_relu_alpha = 0.01
        og_input, og_branch = self._get_focus_flux_transformer_branch("og_branch", transformer_blocks, transformer_heads, channels=2)
        og_branch = keras.layers.Dense(16, kernel_regularizer=tf.keras.regularizers.L1L2(
            l1=self.hyperparams.l1_regularization, l2=self.hyperparams.l2_regularization),
                                       activation=LeakyReLU(leaky_relu_alpha), name="final-dense6")(og_branch)
        og_branch = AdaptiveStdDropout(rate=self.hyperparams.dropout_rate,
                                       max_rate=self.hyperparams.dropout_max_rate, name="final-dropout6")(og_branch)
        final_branch = keras.layers.Dense(1, activation="sigmoid", name="logits")(og_branch)
        return og_input, final_branch

    def load_training_set(self, **kwargs):
        training_dir = kwargs.get('training_dir')
        injected_objects_df_q1_q17 = pd.read_csv(training_dir + "/q1_q17/injected_objects_tces_multi.csv", index_col=None)
        injected_objects_df_q1_q17 = injected_objects_df_q1_q17.loc[(injected_objects_df_q1_q17['multitype'].str.contains('tce')) |
                                                                    (injected_objects_df_q1_q17['type'] == 'planet') |
                                                                    (injected_objects_df_q1_q17['type'] == 'planet_transit')]
        df = [injected_objects_df_q1_q17]
        injected_objects_df = pd.concat(df)
        injected_objects_df.reset_index(inplace=True, drop=True)
        return injected_objects_df

    def instance_generator(self, dataset, dir, batch_size, input_sizes, type_to_label, zero_epsilon, shuffle=True):
        return IatsonOgModelGenerator(dataset, dir, batch_size, input_sizes, type_to_label, zero_epsilon, shuffle_batch=shuffle)

    def predict(self, input):
        prediction = self.model(input, training=False)
        return self.predict_threshold([prediction])

    def predict_batch(self, inputs, expected_outputs=None, dataset=None, training_dir=None, plot_mismatches=False,
                      batch_size=20, cores=os.cpu_count() - 1, threshold=[0.5]):
        predictions = self.model.predict(inputs, use_multiprocessing=True, batch_size=batch_size, workers=cores)
        max_prediction_indexes, max_prediction_values = self.predict_threshold(predictions, threshold)
        if expected_outputs is not None:
            planet_stats = self.test_metrics(expected_outputs, max_prediction_indexes, max_prediction_values, predictions,
                                             dataset, training_dir=training_dir, plot_mismatches=plot_mismatches)
            return max_prediction_indexes, max_prediction_values, [planet_stats]
        else:
            return max_prediction_indexes, max_prediction_values

    def predict_threshold(self, predictions, threshold=[0.5]):
        max_prediction_indexes = np.array([np.argmax(prediction) for prediction in predictions])
        max_prediction_values = np.array([predictions[index][max_prediction_index]
                                 if predictions[index][max_prediction_index] > threshold[max_prediction_index]
                                 else -1
                                 for index, max_prediction_index in enumerate(max_prediction_indexes)])
        max_prediction_indexes[np.argwhere(max_prediction_values < 0).flatten()] = -1
        return max_prediction_indexes, max_prediction_values

    def predict_df(self, df, training_dir, batch_size=20, cores=os.cpu_count() - 1, zero_epsilon=1e-7,
                   thresholds=[0.5], plot_mismatches=False):
        expected_outputs = None
        testing_batch_generator = IatsonOgModelGenerator(df, training_dir, batch_size,
                                                             self.input_size,
                                                             self.type_to_label, zero_epsilon, from_arrays=True,
                                                             shuffle_batch=False)
        for i in np.arange(0, len(df) // batch_size + 1, 1):
            input, expected_output = testing_batch_generator.__getitem__(i)
            expected_outputs = np.concatenate((expected_outputs, expected_output)) if expected_outputs is not None else expected_output
        for threshold in thresholds:
            max_prediction_indexes, max_prediction_values, prediction_stats = \
                self.predict_batch(testing_batch_generator, expected_outputs, df, training_dir, plot_mismatches,
                                   batch_size, cores=cores, threshold=[threshold])
            prediction_stats = prediction_stats[0]
            logging.info("Prediction stats for label %.0f and threshold %s: TP=%.0f, FP=%.0f, FN=%.0f, ACC=%.3f, PRE=%.3f, REC=%.3f", 0,
                         threshold, prediction_stats.tp, prediction_stats.fp, prediction_stats.fn, prediction_stats.accuracy,
                         prediction_stats.precision, prediction_stats.recall)
            logging.info("Prediction stats @ k top predictions: \n%s", prediction_stats.k_df.to_string())
            logging.info("Mismatches: \n%s", prediction_stats.predictions_df.to_string())
            logging.info("Mismatches by types: \n%s", prediction_stats.predictions_df
                         .groupby(by=['type', 'predicted_class'])['object_id'].count().to_string())

    def predict_test_set(self, training_dir, model_dir, batch_size=20, cores=os.cpu_count() - 1, test_set_limit=None,
                         zero_epsilon=1e-7, plot_mismatches=False):
        test_dataset = pd.read_csv(model_dir + '/test_dataset.csv')
        if test_set_limit is not None:
            test_dataset = test_dataset.iloc[0:test_set_limit]
        expected_outputs = None
        testing_batch_generator = IatsonOgModelGenerator(test_dataset, training_dir, batch_size,
                                                             self.input_size,
                                                             self.type_to_label, zero_epsilon, from_arrays=True,
                                                             shuffle_batch=False)
        for i in np.arange(0, len(test_dataset) // batch_size + 1, 1):
            input, expected_output = testing_batch_generator.__getitem__(i)
            expected_outputs = np.concatenate((expected_outputs, expected_output)) if expected_outputs is not None else expected_output
        for threshold in np.arange(0.5, 1, 0.01):
            max_prediction_indexes, max_prediction_values, prediction_stats = \
                self.predict_batch(testing_batch_generator, expected_outputs, test_dataset, training_dir, plot_mismatches,
                                   batch_size, cores=cores, threshold=[threshold])
            prediction_stats = prediction_stats[0]
            logging.info("Prediction stats for label %.0f and threshold %s: TP=%.0f, FP=%.0f, FN=%.0f, ACC=%.3f, PRE=%.3f, REC=%.3f", 0,
                         threshold, prediction_stats.tp, prediction_stats.fp, prediction_stats.fn, prediction_stats.accuracy,
                         prediction_stats.precision, prediction_stats.recall)
            logging.info("Prediction stats @ k top predictions: \n%s", prediction_stats.k_df.to_string())
            logging.info("Mismatches: \n%s", prediction_stats.predictions_df.to_string())
            logging.info("Mismatches by types: \n%s", prediction_stats.predictions_df
                         .groupby(by=['type', 'predicted_class'])['object_id'].count().to_string())


    def test_metrics(self, expected_outputs, max_prediction_indexes, max_prediction_values, predictions,
                     dataset=None, training_dir=None, plot_mismatches=False):
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
                k_df = k_df.append(
                    {'k': k, 'precision': precision, 'recall': recall, 'accuracy': accuracy, 'tp': label_tp,
                     'fp': label_fp, 'fp': label_fp, 'fn': label_fn}, ignore_index=True)
        mismatches_df = pd.DataFrame(columns=['object_id', 'type', 'expected_class', 'predicted_class',
                                              'prediction_value'])
        if dataset is not None:
            found_classes = [0 if prediction  == -1 else 1 for prediction in max_prediction_values]
            dataset = dataset.reset_index(drop=True)
            for i, row in dataset.iterrows():
                object_id = row['object_id']
                period = row['period']
                id = object_id + "_" + str(period)
                expected_tag = row['type']
                expected_output = expected_outputs[i]
                predicted_output = found_classes[i]
                predicted_value = predictions[i][max_prediction_indexes[i]]
                if expected_output != predicted_output:
                    mismatches_df = mismatches_df.append({'object_id': object_id + '_' + str(round(period, 2)), "type": expected_tag,
                                          "expected_class": expected_output, "predicted_class": predicted_output,
                                          "prediction_value": predicted_value}, ignore_index=True)
                    if plot_mismatches:
                        logging.info("%s with label %s mismatched with value %s", id, expected_tag, predicted_value)
                        IatsonOgModelGenerator(dataset[(dataset['object_id'] == object_id) & (dataset['period'] == period)],
                                                                             training_dir, 1,
                                                                             self.input_size,
                                                                             self.type_to_label,
                                                                             from_arrays=True,
                                                                             shuffle_batch=False,
                                                                             plot_inputs=True).__getitem__(0)
        mismatches_df = mismatches_df.sort_values(by=['type', 'predicted_class'])
        return CategoricalPredictionSetStats(label_tp, label_fp, label_fn, accuracy, precision, recall, k_df,
                                             mismatches_df)
