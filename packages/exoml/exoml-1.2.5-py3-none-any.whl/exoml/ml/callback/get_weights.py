from keras.callbacks import Callback


class GetWeights(Callback):
    # Keras callback which collects values of weights and biases at each epoch
    def __init__(self, model_weights_logger, save_dict=False):
        super(GetWeights, self).__init__()
        self.weight_dict = {}
        self.save_dict = save_dict
        self.model_weights_logger = model_weights_logger

    def on_batch_end(self, batch, logs=None):
        self.model_weights_logger.log_model_weights(self.model)
