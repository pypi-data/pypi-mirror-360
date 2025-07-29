import logging

import numpy as np
from tensorflow.keras import Layer


class ModelWeightsLogger:
    def log_model_weights(self, model):
        # this function runs at the end of each epoch
        #logging.info('Generating layer weights info')
        # loop over each layer and get weights and biases
        min_w = 0
        max_w = 0
        min_layer = ""
        max_layer = ""
        for layer_i in range(len(model.layers)):
            weights_and_bias = model.layers[layer_i].get_weights()
            if len(weights_and_bias) > 0:
                w = weights_and_bias[0]
                b = weights_and_bias[1]
                # logging.debug('Layer no %s of type %s has weights of shape %s and biases of shape %s' % (
                #     layer_i, model.layers[layer_i], np.shape(w), np.shape(b)))
                nan_weight_indexes = np.argwhere(np.isnan(w)).flatten()
                nan_bias_indexes = np.argwhere(np.isnan(w)).flatten()
                nan_weight_indexes_count = len(nan_weight_indexes)
                nan_bias_indexes_count = len(nan_bias_indexes)
                min_layer = min_layer if np.min(w) > min_w else model.layers[layer_i]
                max_layer = max_layer if np.max(w) < max_w else model.layers[layer_i]
                min_w = min_w if np.min(w) > min_w else np.min(w)
                max_w = max_w if np.max(w) < max_w else np.max(w)
                # logging.debug('Layer max weight is ' + str(np.nanmax(w)) + ' and min weight is ' + str(np.nanmin(w)))
                # logging.debug('Layer max bias is ' + str(np.nanmax(b)) + ' and min bias is ' + str(np.nanmin(b)))
                if nan_weight_indexes_count > 0 or nan_bias_indexes_count > 0:
                    logging.warning('Layer ' + str(layer_i) + ' with name ' + model.layers[layer_i].name + ' has ' + str(nan_weight_indexes_count) +
                          ' nan weights and ' + str(nan_bias_indexes_count) + ' nan biases')
        if isinstance(min_layer, Layer):
            logging.info("Min weights: %s from layer %s", min_w, min_layer.name)
        if isinstance(max_layer, Layer):
            logging.info("Max weights: %s from layer %s", max_w, max_layer.name)
