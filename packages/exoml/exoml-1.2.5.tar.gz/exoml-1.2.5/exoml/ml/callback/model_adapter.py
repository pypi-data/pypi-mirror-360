import logging

import tensorflow as tf
from keras.layers import SpatialDropout1D
from tensorflow.keras.callbacks import Callback
from tensorflow.keras.layers import Dense, Dropout
from tensorflow.keras.regularizers import l1_l2


class DynamicRegularizationAndLearningRateCallback(Callback):
    def __init__(self, model, l1=0.1, l2=0.1, dropout=0.1, spatial_dropout=0.1, l1_adjustment_factor=0.1,
                 l2_adjustment_factor=0.1, dropout_adjustment_factor=0.1, patience=3, lr_adjustment_factor=0.5):
        super(DynamicRegularizationAndLearningRateCallback, self).__init__()
        self.model = model
        self.l1 = l1
        self.l2 = l2
        self.dropout = dropout
        self.spatial_dropout = spatial_dropout
        self.l1_adjustment_factor = l1_adjustment_factor
        self.l2_adjustment_factor = l2_adjustment_factor
        self.dropout_adjustment_factor = dropout_adjustment_factor
        self.lr_adjustment_factor = lr_adjustment_factor
        self.patience = patience
        self.wait_val = 0
        self.wait_train = 0
        self.best_val_loss = float('inf')
        self.best_train_loss = float('inf')

    def on_epoch_end(self, epoch, logs=None):
        current_val_loss = logs.get('val_loss')
        current_train_loss = logs.get('loss')
        current_lr = tf.keras.backend.get_value(self.model.optimizer.lr)
        if current_val_loss < self.best_val_loss:
            self.best_val_loss = current_val_loss
            self.wait_val = 0
        else:
            self.wait_val += 1
        if current_train_loss < self.best_train_loss:
            self.best_train_loss = current_train_loss
            self.wait_train = 0
        else:
            self.wait_train += 1
        if self.wait_val >= self.patience:
            if current_val_loss > current_train_loss:
                self.l1 = self.l1 * (1 + self.l1_adjustment_factor)
                self.l2 = self.l2 * (1 + self.l2_adjustment_factor)
                self.dropout = self.dropout * (1 + self.dropout_adjustment_factor)
                self.spatial_dropout = self.spatial_dropout * (1 + self.dropout_adjustment_factor)
            logging.info(f"\nAdjusting regularization: L1={self.l1}, L2={self.l2}, Dropout={self.dropout}, "
                         f"SpatialDropout={self.spatial_dropout}")
            for layer in self.model.layers:
                if isinstance(layer, Dropout):
                    layer.rate = self.dropout
                if isinstance(layer, SpatialDropout1D):
                    layer.rate = self.dropout
                if isinstance(layer, Dense):
                    layer.kernel_regularizer = l1_l2(l1=self.l1, l2=self.l2)
            self.wait_val = 0
        if self.wait_train >= self.patience:
            new_lr = current_lr * self.lr_adjustment_factor
            tf.keras.backend.set_value(self.model.optimizer.lr, new_lr)
            logging.info(f"\nAdjusting learning rate to: {new_lr}")
            self.wait_train = 0
        if self.wait_val >= self.patience or self.wait_train >= self.patience:
            self.model.compile(optimizer=self.model.optimizer, loss=self.model.loss, metrics=self.model.metrics)