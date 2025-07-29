from keras.callbacks import Callback


class ModelDirDataAwareCallback(Callback):
    def __init__(self, model_dir=None):
        super().__init__()
        self.model_dir = model_dir

    def set_model_dir(self, model_dir):
        self.model_dir = model_dir


class ValidationDataAwareCallback(ModelDirDataAwareCallback):
    def __init__(self, model_dir=None, validation_data=None):
        super().__init__(model_dir=model_dir)
        self.validation_data = validation_data

    def set_validation_data(self, validation_data):
        self.validation_data = validation_data