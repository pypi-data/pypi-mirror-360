import collections
import copy
import csv
import keras.backend as K
from keras.callbacks import CSVLogger
import numpy as np
from exoml.ml.callback.learning_rate import MultiOptimizer


class BatchAwareCsvLogger(CSVLogger):

    def __init__(self, filename, steps_per_epoch, separator=',', append=False):
        super().__init__(filename, separator, append)
        self.steps_per_epoch = steps_per_epoch
        self.current_epoch = 0

    def on_epoch_end(self, epoch, logs=None):
        self.__store_log(logs, self.steps_per_epoch - 1, self.current_epoch, False)

    def on_epoch_begin(self, epoch, logs=None):
        self.current_epoch = epoch

    def on_batch_end(self, batch, logs=None):
        self.__store_log(logs, batch, self.current_epoch)

    def __store_log(self, logs, batch, epoch, with_validation=True):
        formatted_logs = copy.deepcopy(logs) or {}

        def handle_value(k):
            is_zero_dim_ndarray = isinstance(k, np.ndarray) and k.ndim == 0
            if isinstance(k, str):
                return k
            elif isinstance(k, collections.abc.Iterable) and not is_zero_dim_ndarray:
                return '"[%s]"' % (', '.join(map(str, k)))
            else:
                return k
        keys = formatted_logs.keys()
        if self.model.stop_training:
            # We set NA so that csv parsers do not fail for this last epoch.
            formatted_logs = dict((k, formatted_logs[k]) if k in formatted_logs else (k, 'NA') for k in keys)
        validation_fields = ['val_' + key for key in keys] if with_validation else []
        metric_fieldnames = list(keys) + validation_fields
        if not self.writer:
            class CustomDialect(csv.excel):
                delimiter = self.sep
            lr_fieldnames = ['lr']
            if isinstance(self.model.optimizer, MultiOptimizer):
                lr_fieldnames = lr_fieldnames + ['lr_last']
            fieldnames = ['epoch', 'batch'] + lr_fieldnames +  metric_fieldnames
            self.writer = csv.DictWriter(
                self.csv_file,
                fieldnames=fieldnames,
                dialect=CustomDialect)
            if self.append_header:
                self.writer.writeheader()
        row_dict = {}
        if isinstance(self.model.optimizer, MultiOptimizer):
            learning_rate = K.eval(K.eval(self.model.optimizer.optimizer_specs[0]['optimizer'].lr))
            last_learning_rate = K.eval(K.eval(self.model.optimizer.optimizer_specs[-1]['optimizer'].lr))
            row_dict['lr_last'] = last_learning_rate
        else:
            learning_rate = self.model.optimizer.learning_rate.numpy()
        row_dict['epoch'] = epoch
        row_dict['batch'] = batch
        row_dict['lr'] = learning_rate
        for metric_key in metric_fieldnames:
            row_dict[metric_key] = handle_value(formatted_logs[metric_key][0]
                                                if isinstance(formatted_logs[metric_key], (list, np.ndarray))
                                                else formatted_logs[metric_key]) if metric_key in formatted_logs else np.nan
        self.writer.writerow(row_dict)
        self.csv_file.flush()
