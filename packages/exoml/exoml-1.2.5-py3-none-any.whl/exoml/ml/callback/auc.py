import collections
import csv
import logging
import numpy as np
import tensorflow as tf
import pandas

from exoml.ml.callback.training_data_aware import ValidationDataAwareCallback
from exoml.ml.metrics.auc import confusion_matrix_values, area_under_curve


class ConfusionMatrixStatisticsCallback(ValidationDataAwareCallback):
    def __init__(self, filenames, validation_data=None):
        super().__init__(validation_data=validation_data)
        self.filenames = filenames
        self.stats_csv_files = []
        self.writers = []
        self.roc_dfs = []
        self.keys = None
        self.roc_df = pandas.DataFrame(columns=['epoch', 'label', 'precision', 'recall', 'thresholds'])
        mode = 'w'
        for filename in self.filenames:
            self.stats_csv_files = self.stats_csv_files + [tf.io.gfile.GFile(self.model_dir + '/' + filename +
                                                                             '_stats.csv', mode)]

    def _close_resources(self):
        for index, filename in enumerate(self.filenames):
            self.stats_csv_files[index].close()
            self.writers[index] = None
        self.writers = None
        self.roc_dfs = None

    def on_train_end(self, logs=None):
        self._close_resources()

    def on_epoch_end(self, epoch, logs={}):
        # x_train, y_train = self.train[0], self.train[1]
        # y_pred = self.model.predict(x_train)
        # confusion_matrix, accuracy, error_rate, precision, recall, f1_score = self.confusion_matrix(y_train, y_pred)
        # logs['F1_score_train'] = np.round(f1_score, 5)
        # if self.validation:
        logging.info("Computing AUC metrics")
        batches = len(self.validation_data)
        y_valid = None
        for batch in range(batches):
            x_val, y_val = self.validation_data[batch]
            if y_valid is None:
                y_valid = y_val
            else:
                y_valid = np.concatenate((y_valid, y_val))
        y_val_pred = self.model.predict(self.validation_data)
        logs = logs or {}

        def handle_value(k):
            is_zero_dim_ndarray = isinstance(k, np.ndarray) and k.ndim == 0
            if isinstance(k, str):
                return k
            elif isinstance(k, collections.abc.Iterable) and not is_zero_dim_ndarray:
                return '"[%s]"' % (', '.join(map(str, k)))
            else:
                return k

        if self.keys is None:
            self.keys = sorted(logs.keys())
        if self.model.stop_training:
            # We set NA so that csv parsers do not fail for this last epoch.
            logs = dict((k, logs[k]) if k in logs else (k, 'NA') for k in self.keys)
        if len(self.writers) == 0:
            class CustomDialect(csv.excel):
                delimiter = ','
            fieldnames = ['epoch', 'val_f1_score', 'val_tp', 'val_fp', 'val_fn', 'val_tn', 'val_precision',
                          'val_recall', 'val_roc'] + self.keys
            for csv_file in self.stats_csv_files:
                new_writer = csv.DictWriter(csv_file, fieldnames=fieldnames, dialect=CustomDialect)
                new_writer.writeheader()
                self.writers = self.writers + [new_writer]

        for index, filename in enumerate(self.filenames):
            confusion_matrix, accuracy, error_rate, precision, recall, f1_score = \
                confusion_matrix_values(y_valid, y_val_pred, label_index=index)
            recalls, precisions, thresholds, roc = area_under_curve(y_valid, y_val_pred, label_index=index)
            row_dict = collections.OrderedDict({'epoch': epoch, 'val_f1_score': f1_score,
                                                'val_tp': confusion_matrix[0][0],
                                                'val_fp': confusion_matrix[0][1],
                                                'val_fn': confusion_matrix[1][0],
                                                'val_tn': confusion_matrix[1][1],
                                                'val_precision': precision,
                                                'val_recall': recall,
                                                'val_roc': roc
                                                })
            self.writers[index].writerow(row_dict)
            self.stats_csv_files[index].flush()
            for precision_index, precision in enumerate(precisions):
                self.roc_df = self.roc_df.append({'epoch': epoch, 'label': index, 'recall': recalls[precision_index],
                                                  'precision': precisions[precision_index],
                                                  'thresholds': thresholds[precision_index]}, ignore_index=True)
        self.roc_df.to_csv(self.model_dir + '/precision_recall.csv', index=False)
        logging.info("Computed AUC metrics")