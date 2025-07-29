import multiprocessing

import numpy as np
import pandas as pd
import keras
from keras.layers import LeakyReLU
from sklearn.utils import shuffle

from exoml.ml.model.base_model import CategoricalPredictionSetStats
from exoml.ml.model.imbalanced_binary_model import ImbalancedBinaryModel
from transpot.transpot_generator import TranspotModelGenerator

class TRANSPOT(ImbalancedBinaryModel):
    def __init__(self, class_ids, input_size=(20610, 13)) -> None:
        super().__init__('TRANSPOT', input_size, class_ids)

    def _get_flux_conv_branch(self):
        # (time, flux, [detrended_flux1 ... detrended_flux5], flux_model, centroidx, centroidy, motionx, motiony, bck)
        # flux model by transit params and stellar params
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
        flux_input = keras.Input(shape=(self.input_size))
        flux_branch = keras.layers.SpatialDropout1D(rate=0.1)(flux_input)
        flux_branch = keras.layers.Conv1D(filters=autoencoder_layer1_filters, kernel_size=autoencoder_layer1_ks,
                                                padding="same", activation=LeakyReLU(0.01))(flux_branch)
        flux_branch = keras.layers.MaxPooling1D(pool_size=50, strides=autoencoder_layer1_strides, padding="same")(
            flux_branch)
        flux_branch = keras.layers.Dropout(rate=0.1)(flux_branch)
        flux_branch = keras.layers.Conv1D(filters=autoencoder_layer2_filters, kernel_size=autoencoder_layer2_ks,
                                                padding="same", activation=LeakyReLU(0.01))(flux_branch)
        flux_branch = keras.layers.MaxPooling1D(pool_size=20, strides=autoencoder_layer2_strides, padding="same")(
            flux_branch)
        flux_branch = keras.layers.Dropout(rate=0.1)(flux_branch)
        flux_branch = keras.layers.Conv1D(filters=autoencoder_layer3_filters, kernel_size=autoencoder_layer3_ks,
                                                padding="same", activation=LeakyReLU(0.01))(flux_branch)
        flux_branch = keras.layers.MaxPooling1D(pool_size=15, strides=autoencoder_layer3_strides, padding="same")(
            flux_branch)
        flux_branch = keras.layers.Dropout(rate=0.1)(flux_branch)
        flux_branch = keras.layers.Conv1D(filters=autoencoder_layer4_filters, kernel_size=autoencoder_layer4_ks,
                                                padding="same", activation=LeakyReLU(0.01))(flux_branch)
        flux_branch = keras.layers.MaxPooling1D(pool_size=10, strides=autoencoder_layer4_strides, padding="same")(
            flux_branch)
        flux_branch = keras.layers.Dropout(rate=0.1)(flux_branch)
        flux_branch = keras.layers.Conv1D(filters=autoencoder_layer5_filters, kernel_size=autoencoder_layer5_ks,
                                                padding="same", activation=LeakyReLU(0.01))(flux_branch)
        flux_branch = keras.layers.MaxPooling1D(pool_size=4, strides=autoencoder_layer5_strides, padding="same")(
            flux_branch)
        flux_branch = keras.layers.Dropout(rate=0.1)(flux_branch)
        flux_branch = keras.layers.Conv1D(filters=autoencoder_layer6_filters, kernel_size=autoencoder_layer6_ks,
                                                padding="same", activation=LeakyReLU(0.01))(flux_branch)
        flux_branch = keras.layers.MaxPooling1D(pool_size=3, strides=autoencoder_layer6_strides, padding="same")(
            flux_branch)
        flux_branch = keras.layers.Dropout(rate=0.1)(flux_branch)
        #flux_branch = keras.layers.LayerNormalization()(flux_branch)
        return flux_input, flux_branch

    def _get_flux_model_branch(self):
        leaky_relu_alpha = 0.01
        flux_input, flux_branch = self._get_flux_conv_branch()
        flux_branch = keras.layers.Dense(16, activation=LeakyReLU(leaky_relu_alpha))(flux_branch)
        flux_branch = keras.layers.Dropout(rate=0.1)(flux_branch)
        flux_branch = keras.layers.Dense(16, activation='linear')(flux_branch)
        #flux_branch = keras.layers.LayerNormalization()(flux_branch)
        flux_branch = keras.Model(inputs=[flux_input], outputs=flux_branch)
        return flux_branch

    def build(self):
        leaky_relu_alpha = 0.01
        stellar_model_input = keras.Input(shape=(11, 1), name="stellar_model")
        stellar_model_branch = keras.layers.Dense(16, activation=LeakyReLU(leaky_relu_alpha), name="stellar-first")(stellar_model_input)
        stellar_model_branch = keras.layers.Dropout(rate=0.1, name="stellar-first-dropout-0.1")(stellar_model_branch)
        stellar_model_branch = keras.layers.Dense(16, activation="relu", name="stellar-refinement")(
            stellar_model_branch)
        flux_model_branch = self._get_flux_model_branch()
        final_branch = keras.layers.Concatenate(axis=1)([stellar_model_branch, flux_model_branch.output])
        final_branch = keras.layers.GlobalAveragePooling1D()(final_branch)
        final_branch = keras.layers.Dense(64, activation=LeakyReLU(leaky_relu_alpha), name="final-dense1")(final_branch)
        final_branch = keras.layers.Dropout(rate=0.1)(final_branch)
        final_branch = keras.layers.Dense(32, activation=LeakyReLU(leaky_relu_alpha), name="final-dense2")(final_branch)
        final_branch = keras.layers.Dropout(rate=0.1)(final_branch)
        final_branch = keras.layers.Dense(1, activation="sigmoid", name="final-dense-softmax")(final_branch)
        inputs = [stellar_model_input] + flux_model_branch.inputs
        self.set_model(keras.Model(inputs=inputs, outputs=final_branch, name="TRANSPOT"))
        return self

    def load_training_set(self, **kwargs):
        training_dir = kwargs.get('training_dir')
        injected_objects_df = pd.read_csv(training_dir + "/injected_objects.csv", index_col=None)
        injected_objects_df = injected_objects_df.sort_values(by=['TIC ID', 'type'])
        #TODO remove 'none' types when there is more than one entry for same TIC (keeping first as none is the latest
        #  from bckEB, EB, planet and none
        injected_objects_df['type'] = injected_objects_df['type'].astype('category')
        injected_objects_df['type'] = injected_objects_df['type'].cat.set_categories(['bckEB', 'EB', 'planet', 'none'],
                                                                                     ordered=True)
        injected_objects_df.sort_values(by=['TIC ID', 'type'], inplace=True)
        injected_objects_df = injected_objects_df.drop_duplicates(subset='TIC ID', keep="first")
        injected_objects_df = shuffle(injected_objects_df)
        injected_objects_df.reset_index(inplace=True, drop=True)
        return injected_objects_df

    def instance_generator(self, dataset, dir, batch_size, input_sizes, zero_epsilon):
        return TranspotModelGenerator(dataset, dir, batch_size, input_sizes, zero_epsilon)

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

    def predict_test_set(self, training_dir, test_set_file, batch_size=20, zero_epsilon=1e-7):
        test_dataset = pd.read_csv(test_set_file)
        lcs_dir = training_dir + '/lcs/'
        testing_batch_generator = TranspotModelGenerator(test_dataset, lcs_dir, batch_size, self.input_size,
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
