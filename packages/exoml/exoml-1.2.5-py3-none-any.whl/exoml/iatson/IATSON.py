import multiprocessing

import numpy as np
import pandas as pd
import keras
from keras.layers import LeakyReLU
from keras.utils import losses_utils
from sklearn.utils import shuffle

from exoml.iatson.iatson_generator import IatsonModelGenerator
from exoml.ml.model.base_model import CategoricalPredictionSetStats
from exoml.ml.model.imbalanced_categorical_model import ImbalancedCategoricalModel


class IATSON(ImbalancedCategoricalModel):
    def __init__(self, class_ids, class_names, dropout_rate=0.1) -> None:
        super().__init__(class_names, 'IATSON', [11, 9 * 15, 2500, 500, 500, 500, 500, 500, 500], class_ids, dropout_rate)
        self.class_names = class_names

    def _get_flux_conv_branch(self, name):
        # (time, flux, [detrended_flux1 ... detrended_flux5], flux_model, centroidx, centroidy, motionx, motiony, bck)
        # flux model by transit params and stellar params
        leaky_relu_alpha = 0.01
        flux_input = keras.Input(shape=(2500, 13), name=name)
        flux_branch = keras.layers.normalization.batch_normalization.BatchNormalization()(flux_input)
        flux_branch = keras.layers.SpatialDropout1D(rate=self.dropout_rate)(flux_branch)
        flux_branch = keras.layers.Conv1D(filters=512, kernel_size=5, padding="same",
                                          activation=LeakyReLU(leaky_relu_alpha))(flux_branch)
        flux_branch = keras.layers.MaxPooling1D(pool_size=5, strides=3)(flux_branch)
        flux_branch = keras.layers.normalization.batch_normalization.BatchNormalization()(flux_branch)
        flux_branch = keras.layers.SpatialDropout1D(rate=self.dropout_rate)(flux_branch)
        flux_branch = keras.layers.Conv1D(filters=256, kernel_size=5, padding="same",
                                          activation=LeakyReLU(leaky_relu_alpha))(flux_branch)
        flux_branch = keras.layers.MaxPooling1D(pool_size=5, strides=2)(flux_branch)
        flux_branch = keras.layers.normalization.batch_normalization.BatchNormalization()(flux_branch)
        flux_branch = keras.layers.SpatialDropout1D(rate=self.dropout_rate)(flux_branch)
        flux_branch = keras.layers.Conv1D(filters=128, kernel_size=5, padding="same",
                                          activation=LeakyReLU(leaky_relu_alpha))(flux_branch)
        flux_branch = keras.layers.MaxPooling1D(pool_size=5, strides=2)(flux_branch)
        flux_branch = keras.layers.normalization.batch_normalization.BatchNormalization()(flux_branch)
        flux_branch = keras.layers.SpatialDropout1D(rate=self.dropout_rate)(flux_branch)
        flux_branch = keras.layers.Conv1D(filters=64, kernel_size=4, padding="same",
                                          activation=LeakyReLU(leaky_relu_alpha))(flux_branch)
        flux_branch = keras.layers.MaxPooling1D(pool_size=4, strides=2)(flux_branch)
        flux_branch = keras.layers.normalization.batch_normalization.BatchNormalization()(flux_branch)
        flux_branch = keras.layers.SpatialDropout1D(rate=self.dropout_rate)(flux_branch)
        flux_branch = keras.layers.Conv1D(filters=32, kernel_size=3, padding="same",
                                          activation=LeakyReLU(leaky_relu_alpha))(flux_branch)
        flux_branch = keras.layers.MaxPooling1D(pool_size=3, strides=2)(flux_branch)
        flux_branch = keras.layers.normalization.batch_normalization.BatchNormalization()(flux_branch)
        flux_branch = keras.layers.SpatialDropout1D(rate=self.dropout_rate)(flux_branch)
        flux_branch = keras.layers.Conv1D(filters=16, kernel_size=3, padding="same",
                                          activation=LeakyReLU(leaky_relu_alpha))(flux_branch)
        flux_branch = keras.layers.MaxPooling1D(pool_size=3, strides=2)(flux_branch)
        return flux_input, flux_branch

    def _get_flux_model_branch(self):
        leaky_relu_alpha = 0.01
        flux_input, flux_branch = self._get_flux_conv_branch("global_flux_branch")
        flux_branch = keras.layers.Dense(16, activation=LeakyReLU(leaky_relu_alpha))(flux_branch)
        flux_branch = keras.layers.Dropout(rate=self.dropout_rate)(flux_branch)
        flux_branch = keras.layers.Dense(16, activation='linear')(flux_branch)
        flux_branch = keras.layers.LayerNormalization()(flux_branch)
        flux_branch = keras.Model(inputs=[flux_input], outputs=flux_branch)
        return flux_branch

    def _get_focus_flux_branch(self, name):
        leaky_relu_alpha = 0.01
        focus_flux_input = keras.Input(shape=(500, 13), name=name)
        focus_flux_branch = keras.layers.normalization.batch_normalization.BatchNormalization()(focus_flux_input)
        # (time, flux, detrended_flux1... detrended_flux5, flux_model, centroidx, centroidy, motionx, motiony, bck)
        # flux model by transit params and stellar params
        focus_flux_branch = keras.layers.SpatialDropout1D(rate=self.dropout_rate)(focus_flux_branch)
        focus_flux_branch = keras.layers.Conv1D(filters=256, kernel_size=10, padding="same",
                                                activation=LeakyReLU(leaky_relu_alpha), use_bias=True)(
            focus_flux_branch)
        focus_flux_branch = keras.layers.MaxPooling1D(pool_size=10, strides=2)(focus_flux_branch)
        focus_flux_branch = keras.layers.normalization.batch_normalization.BatchNormalization()(focus_flux_branch)
        focus_flux_branch = keras.layers.SpatialDropout1D(rate=self.dropout_rate)(focus_flux_branch)
        focus_flux_branch = keras.layers.Conv1D(filters=128, kernel_size=6, padding="same",
                                                activation=LeakyReLU(leaky_relu_alpha), use_bias=True)(
            focus_flux_branch)
        focus_flux_branch = keras.layers.MaxPooling1D(pool_size=6, strides=2)(focus_flux_branch)
        focus_flux_branch = keras.layers.normalization.batch_normalization.BatchNormalization()(focus_flux_branch)
        focus_flux_branch = keras.layers.SpatialDropout1D(rate=self.dropout_rate)(focus_flux_branch)
        focus_flux_branch = keras.layers.Conv1D(filters=64, kernel_size=3, padding="same",
                                                activation=LeakyReLU(leaky_relu_alpha), use_bias=True)(
            focus_flux_branch)
        focus_flux_branch = keras.layers.MaxPooling1D(pool_size=3, strides=2)(focus_flux_branch)
        focus_flux_branch = keras.layers.normalization.batch_normalization.BatchNormalization()(focus_flux_branch)
        focus_flux_branch = keras.layers.SpatialDropout1D(rate=self.dropout_rate)(focus_flux_branch)
        focus_flux_branch = keras.layers.Conv1D(filters=32, kernel_size=3, padding="same",
                                                activation=LeakyReLU(leaky_relu_alpha), use_bias=True)(
            focus_flux_branch)
        focus_flux_branch = keras.layers.MaxPooling1D(pool_size=3, strides=2)(focus_flux_branch)
        focus_flux_branch = keras.layers.normalization.batch_normalization.BatchNormalization()(focus_flux_branch)
        focus_flux_branch = keras.layers.SpatialDropout1D(rate=self.dropout_rate)(focus_flux_branch)
        focus_flux_branch = keras.layers.Conv1D(filters=16, kernel_size=2, padding="same",
                                                activation=LeakyReLU(leaky_relu_alpha), use_bias=True)(
            focus_flux_branch)
        focus_flux_branch = keras.layers.MaxPooling1D(pool_size=2, strides=2)(focus_flux_branch)
        focus_flux_branch = keras.layers.normalization.batch_normalization.BatchNormalization()(focus_flux_branch)
        focus_flux_branch = keras.layers.SpatialDropout1D(rate=self.dropout_rate)(focus_flux_branch)
        focus_flux_branch = keras.layers.Conv1D(filters=9, kernel_size=2, padding="same",
                                                activation=LeakyReLU(leaky_relu_alpha), use_bias=True)(
            focus_flux_branch)
        focus_flux_branch = keras.layers.MaxPooling1D(pool_size=2, strides=2)(focus_flux_branch)
        focus_flux_branch = keras.layers.normalization.batch_normalization.BatchNormalization()(focus_flux_branch)
        focus_flux_branch = keras.layers.Dense(16, activation=LeakyReLU(leaky_relu_alpha))(focus_flux_branch)
        focus_flux_branch = keras.layers.Dropout(rate=self.dropout_rate)(focus_flux_branch)
        focus_flux_branch = keras.layers.LayerNormalization()(focus_flux_branch)
        return focus_flux_input, focus_flux_branch

    def _get_focus_flux_model_branch(self):
        leaky_relu_alpha = 0.01
        odd_flux_input, odd_flux_branch = self._get_focus_flux_branch("focus_odd_flux_branch")
        even_flux_input, even_flux_branch = self._get_focus_flux_branch("focus_even_flux_branch")
        harmonic_odd_flux_input, harmonic_odd_flux_branch = self._get_focus_flux_branch("focus_harmonic_odd_flux_branch")
        harmonic_even_flux_input, harmonic_even_flux_branch = self._get_focus_flux_branch("focus_harmonic_even_flux_branch")
        subharmonic_odd_flux_input, subharmonic_odd_flux_branch = self._get_focus_flux_branch(
            "focus_subharmonic_odd_flux_branch")
        subharmonic_even_flux_input, subharmonic_even_flux_branch = self._get_focus_flux_branch(
            "focus_subharmonic_even_flux_branch")
        odd_flux_branch = keras.layers.Add()(
            [odd_flux_branch, harmonic_odd_flux_branch, subharmonic_odd_flux_branch])
        even_flux_branch = keras.layers.Add()(
            [even_flux_branch, harmonic_even_flux_branch, subharmonic_even_flux_branch])
        odd_flux_branch = keras.layers.Dense(16, activation=LeakyReLU(leaky_relu_alpha))(odd_flux_branch)
        odd_flux_branch = keras.layers.Dropout(rate=self.dropout_rate)(odd_flux_branch)
        even_flux_branch = keras.layers.Dense(16, activation=LeakyReLU(leaky_relu_alpha))(even_flux_branch)
        even_flux_branch = keras.layers.Dropout(rate=self.dropout_rate)(even_flux_branch)
        odd_flux_branch = keras.layers.Dense(32, activation='linear')(odd_flux_branch)
        even_flux_branch = keras.layers.Dense(32, activation='linear')(even_flux_branch)
        odd_flux_branch = keras.layers.LayerNormalization()(odd_flux_branch)
        even_flux_branch = keras.layers.LayerNormalization()(even_flux_branch)
        focus_flux_branch = keras.layers.Add()([odd_flux_branch, even_flux_branch])
        focus_flux_branch = keras.layers.Dense(24, activation=LeakyReLU(leaky_relu_alpha))(focus_flux_branch)
        focus_flux_branch = keras.layers.Dropout(rate=self.dropout_rate)(focus_flux_branch)
        focus_flux_branch = keras.layers.Dense(16, activation='linear')(focus_flux_branch)
        input = [even_flux_input, odd_flux_input, subharmonic_even_flux_input, subharmonic_odd_flux_input,
                 harmonic_even_flux_input, harmonic_odd_flux_input]
        focus_flux_branch = keras.Model(inputs=input, outputs=focus_flux_branch)
        return focus_flux_branch

    def _get_singletransit_tpf_model(self):
        video_image_width = 13
        video_image_height = 13
        video_image_channels = 1
        sequences_per_video = 100
        tpf_model_input = keras.Input(
            shape=(video_image_height, video_image_width, sequences_per_video, video_image_channels),
            name="tpf_input")
        tpf_model = keras.layers.SpatialDropout3D(rate=0.3)(tpf_model_input)
        tpf_model = keras.layers.Conv3D(filters=100, kernel_size=(3, 3, 5), strides=(1, 1, 3), activation="relu")(
            tpf_model)
        tpf_model = keras.layers.SpatialDropout3D(rate=0.2)(tpf_model)
        tpf_model = keras.layers.Conv3D(filters=200, kernel_size=(3, 3, 5), strides=(1, 1, 3), activation="relu")(
            tpf_model)
        tpf_model = keras.layers.SpatialDropout3D(rate=0.1)(tpf_model)
        tpf_model = keras.layers.MaxPooling3D(pool_size=(5, 5, 10), strides=(3, 3, 6), padding='same')(tpf_model)
        tpf_model = keras.layers.Dense(200, activation="relu")(tpf_model)
        tpf_model = keras.layers.Dense(100, activation="relu")(tpf_model)
        tpf_model = keras.layers.Dense(20, activation="relu")(tpf_model)
        tpf_model = keras.layers.Flatten()(tpf_model)
        return keras.Model(inputs=tpf_model_input, outputs=tpf_model)

    def _get_singletransit_motion_centroids_model(self):
        mc_input = keras.Input(
            shape=(100, 4),
            name="motion_centroids_input")
        mc_model = keras.layers.Conv1D(filters=50, kernel_size=3, strides=3, activation="relu", use_bias=True,
                                       padding='same')(mc_input)
        mc_model = keras.layers.SpatialDropout1D(rate=0.3)(mc_model)
        mc_model = keras.layers.Conv1D(filters=100, kernel_size=5, strides=5, activation="relu", use_bias=True,
                                       padding='same')(mc_model)
        mc_model = keras.layers.SpatialDropout1D(rate=0.2)(mc_model)
        mc_model = keras.layers.MaxPooling1D(pool_size=5, strides=3, padding='same')(mc_model)
        mc_model = keras.layers.Dense(50, activation="relu")(mc_model)
        mc_model = keras.layers.Dense(20, activation="relu")(mc_model)
        mc_model = keras.layers.Flatten()(mc_model)
        return keras.Model(inputs=mc_input, outputs=mc_model)

    def _get_singletransit_bckflux_model(self):
        bck_input = keras.Input(shape=(100, 1), name="bck_input")
        bck_model = keras.layers.Conv1D(filters=25, kernel_size=2, strides=2, activation="relu", use_bias=True,
                                        padding='same')(bck_input)
        bck_model = keras.layers.SpatialDropout1D(rate=0.3)(bck_model)
        bck_model = keras.layers.Conv1D(filters=50, kernel_size=3, strides=3, activation="relu", use_bias=True,
                                        padding='same')(bck_model)
        bck_model = keras.layers.SpatialDropout1D(rate=0.2)(bck_model)
        bck_model = keras.layers.MaxPooling1D(pool_size=5, strides=3, padding='same')(bck_model)
        bck_model = keras.layers.Dense(50, activation="relu")(bck_model)
        bck_model = keras.layers.Dense(10, activation="relu")(bck_model)
        bck_model = keras.layers.Flatten()(bck_model)
        return keras.Model(inputs=bck_input, outputs=bck_model)

    def _get_singletransit_flux_model(self):
        bck_input = keras.Input(shape=(100, 1), name="flux_input")
        bck_model = keras.layers.Conv1D(filters=25, kernel_size=2, strides=2, activation="relu", use_bias=True,
                                        padding='same')(bck_input)
        bck_model = keras.layers.SpatialDropout1D(rate=0.3)(bck_model)
        bck_model = keras.layers.Conv1D(filters=50, kernel_size=3, strides=3, activation="relu", use_bias=True,
                                        padding='same')(bck_model)
        bck_model = keras.layers.SpatialDropout1D(rate=0.2)(bck_model)
        bck_model = keras.layers.MaxPooling1D(pool_size=5, strides=3, padding='same')(bck_model)
        bck_model = keras.layers.Dense(50, activation="relu")(bck_model)
        bck_model = keras.layers.Dense(10, activation="relu")(bck_model)
        bck_model = keras.layers.Flatten()(bck_model)
        return keras.Model(inputs=bck_input, outputs=bck_model)

    def _get_single_transit_model(self):
        tpf_branch = self._get_singletransit_tpf_model()
        mc_branch = self._get_singletransit_motion_centroids_model()
        bck_branch = self._get_singletransit_bckflux_model()
        flux_branch = self._get_singletransit_flux_model()
        final_branch = keras.layers.concatenate(
            [tpf_branch.output, mc_branch.output, bck_branch.output, flux_branch.output], axis=1)
        final_branch = keras.layers.Dense(64, activation="relu", name="final-dense1")(final_branch)
        final_branch = keras.layers.Dense(32, activation="relu", name="final-dense2")(final_branch)
        final_branch = keras.layers.Dense(1, activation="softmax", name="final-dense-softmax")(final_branch)
        inputs = tpf_branch.inputs + mc_branch.inputs + bck_branch.inputs + flux_branch.inputs
        model = keras.Model(inputs=inputs, outputs=final_branch, name="mnist_model")
        keras.utils.vis_utils.plot_model(model, "IATSON_model.png", show_shapes=True)

    def build(self):
        leaky_relu_alpha = 0.01
        stellar_model_input = keras.Input(shape=(11, 1), name="stellar_model")
        stellar_model_branch = keras.layers.Dense(16, activation=LeakyReLU(leaky_relu_alpha), name="stellar-first")(
            stellar_model_input)
        stellar_model_branch = keras.layers.Dropout(rate=self.dropout_rate, name="stellar-first-dropout-0.1")(stellar_model_branch)
        stellar_model_branch = keras.layers.Dense(16, activation=LeakyReLU(leaky_relu_alpha), name="stellar-refinement")(
            stellar_model_branch)
        #(TEFF, lum, 4 magnitudes, distance, radius, mass) * 15 stars
        stellar_neighbours_input = keras.Input(shape=(9 * 15, 1), name="stellar_neighbours_model")
        stellar_neighbours_branch = keras.layers.Dense(100, activation=LeakyReLU(leaky_relu_alpha), name="stellar-neighbours-1")(
            stellar_neighbours_input)
        stellar_neighbours_branch = keras.layers.Dropout(rate=self.dropout_rate, name="stellar-neighbours-1-dropout-0.1")(stellar_neighbours_branch)
        stellar_neighbours_branch = keras.layers.Dense(50, activation=LeakyReLU(leaky_relu_alpha), name="stellar-neighbours-2")(
            stellar_neighbours_branch)
        stellar_neighbours_branch = keras.layers.Dropout(rate=self.dropout_rate, name="stellar-neighbours-2-dropout-0.1")(stellar_neighbours_branch)
        stellar_neighbours_branch = keras.layers.Dense(16, activation=LeakyReLU(leaky_relu_alpha), name="stellar-neighbours_3")(
            stellar_neighbours_branch)
        flux_model_branch = self._get_flux_model_branch()
        focus_flux_model_branch = self._get_focus_flux_model_branch()
        final_branch = keras.layers.Concatenate(axis=1)(
            [stellar_model_branch, stellar_neighbours_branch, flux_model_branch.output, focus_flux_model_branch.output])
        final_branch = keras.layers.GlobalAveragePooling1D()(final_branch)
        final_branch = keras.layers.Dense(64, activation=LeakyReLU(leaky_relu_alpha), name="final-dense1")(final_branch)
        final_branch = keras.layers.Dropout(rate=self.dropout_rate)(final_branch)
        final_branch = keras.layers.Dense(32, activation=LeakyReLU(leaky_relu_alpha), name="final-dense2")(final_branch)
        final_branch = keras.layers.Dropout(rate=self.dropout_rate)(final_branch)
        final_branch = keras.layers.Dense(4, activation="softmax", name="final-dense-softmax")(final_branch)
        inputs = [stellar_model_input, stellar_neighbours_input] + flux_model_branch.inputs + focus_flux_model_branch.inputs
        self.set_model(keras.Model(inputs=inputs, outputs=final_branch, name="IATSON"))
        return self

    def load_training_set(self, **kwargs):
        training_dir = kwargs.get('training_dir')
        injected_objects_df = pd.read_csv(training_dir + "/injected_objects.csv", index_col=None)
        injected_objects_df = shuffle(injected_objects_df)
        injected_objects_df.reset_index(inplace=True, drop=True)
        return injected_objects_df

    def instance_generator(self, dataset, dir, batch_size, input_sizes, zero_epsilon):
        return IatsonModelGenerator(dataset, dir, batch_size, input_sizes, zero_epsilon)

    def predict(self, input):
        prediction = self.model(input, training=False)
        return self.predict_threshold([prediction])

    def predict_batch(self, inputs, expected_outputs=None, batch_size=20, cores=multiprocessing.cpu_count() - 1):
        predictions = self.model.predict(inputs, use_multiprocessing=True, batch_size=batch_size, workers=cores)
        max_prediction_indexes, max_prediction_values = self.predict_threshold(predictions)
        if expected_outputs is not None:
            bckeb_stats = self.test_metrics(expected_outputs, predictions, 0)
            eb_stats = self.test_metrics(expected_outputs, predictions, 1)
            planet_stats = self.test_metrics(expected_outputs, predictions, 2)
            none_stats = self.test_metrics(expected_outputs, predictions, 3)
            return max_prediction_indexes, max_prediction_values, [bckeb_stats, eb_stats, planet_stats, none_stats]
        else:
            return max_prediction_indexes, max_prediction_values

    def predict_threshold(self, predictions, threshold=[0.5, 0.5, 0.5, 0.5]):
        max_prediction_indexes = [np.argmax(prediction) for prediction in predictions]
        max_prediction_values = [predictions[index][max_prediction_index]
                                 if predictions[index][max_prediction_index] > threshold[predictions[index][max_prediction_index]]
                                 else -1
                                 for index, max_prediction_index in enumerate(max_prediction_indexes)]
        max_prediction_indexes[max_prediction_values == -1] = -1
        return max_prediction_indexes, max_prediction_values

    def predict_test_set(self, training_dir, model_dir, batch_size=20, test_set_limit=None, zero_epsilon=1e-7):
        test_dataset = pd.read_csv(model_dir + '/test_dataset.csv')
        test_dataset = shuffle(test_dataset)
        if test_set_limit is not None:
            test_dataset = test_dataset.iloc[0:test_set_limit]
        lcs_dir = training_dir + '/lcs/'
        testing_batch_generator = IatsonModelGenerator(test_dataset, lcs_dir, batch_size, self.input_size,
                                                       zero_epsilon)
        expected_outputs = None
        for i in np.arange(0, len(test_dataset) // batch_size + 1, 1):
            input, expected_output = testing_batch_generator.__getitem__(i)
            expected_outputs = np.concatenate((expected_outputs, expected_output)) if expected_outputs is not None else expected_output
        return self.predict_batch(testing_batch_generator, expected_outputs, batch_size)

    def test_metrics(self, expected_outputs, max_prediction_indexes, label_index):
        set_count = len(expected_outputs)
        max_output_indexes = [np.max(expected_output) for expected_output in expected_outputs]
        matches_indexes = np.argwhere(max_output_indexes == max_prediction_indexes).flatten()
        matches_count = len(matches_indexes)
        accuracy = matches_count / set_count
        expected_label_indexes = np.argwhere(max_output_indexes == label_index).flatten()
        output_label_indexes = np.argwhere(max_output_indexes == label_index).flatten()
        label_tp_indexes = np.intersect1d(expected_label_indexes, output_label_indexes)
        label_fp_indexes = output_label_indexes[~np.isin(output_label_indexes, expected_label_indexes)]
        label_fn_indexes = expected_label_indexes[~np.isin(expected_label_indexes, output_label_indexes)]
        label_tp = len(label_tp_indexes)
        label_fp = len(label_fp_indexes)
        label_fn = len(label_fn_indexes)
        precision = label_tp / (label_tp + label_fp)
        recall = label_tp / (label_tp + label_fn)
        return CategoricalPredictionSetStats(label_tp, label_fp, label_fn, accuracy, precision, recall)
