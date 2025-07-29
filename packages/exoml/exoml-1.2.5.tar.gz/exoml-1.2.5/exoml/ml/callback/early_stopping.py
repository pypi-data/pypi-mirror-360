import logging

from keras.callbacks import EarlyStopping
import numpy as np


class ExoMlEarlyStopping(EarlyStopping):
    def on_train_end(self, logs=None):
        super().on_train_end(logs)
        if self.stopped_epoch > 0 and self.verbose > 0:
            logging.warning('Epoch %05d: early stopping', (self.stopped_epoch + 1))

    def on_train_batch_begin(self, batch, logs=None):
        if np.isnan(self.model.loss):
            raise ValueError("Loss is NaN")
        return super().on_train_batch_begin(batch, logs)
