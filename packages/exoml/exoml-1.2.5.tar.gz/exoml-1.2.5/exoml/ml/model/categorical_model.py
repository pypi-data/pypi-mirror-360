import logging

from keras.losses import CategoricalCrossentropy
from keras.metrics import CategoricalAccuracy, Precision, Recall, AUC, RecallAtPrecision
import pandas as pd
from exoml.ml.model.base_model import BaseModel
import matplotlib.pyplot as plt
from matplotlib.pyplot import cm
import numpy as np


class CategoricalModel(BaseModel):
    def __init__(self, class_names, name, input_size, class_ids, dropout_rate=0.1) -> None:
        super().__init__(name, input_size, class_ids, dropout_rate)
        self.class_names = class_names

    def instance_loss_accuracy(self):
        return CategoricalCrossentropy(), CategoricalAccuracy()

    def instance_metrics(self):
        metrics = []
        for index, class_name in enumerate(self.class_names):
            class_name_string = str(class_name)
            metrics = metrics + [Precision(class_id=index, name=class_name_string + "_precision", thresholds=0.5),
                                 Recall(class_id=index, name=class_name_string + "_recall", thresholds=0.5),
                                 RecallAtPrecision(0.99, class_id=index, name=class_name_string + "_r@p99"),
                                 RecallAtPrecision(0.975, class_id=index, name=class_name_string + "_r@p975"),
                                 RecallAtPrecision(0.95, class_id=index, name=class_name_string + "_r@p95")]
        classes_count = len(self.class_names)
        return metrics + [AUC(multi_label=True, num_labels=classes_count, name="roc_auc"),
                          AUC(multi_label=True, curve="PR", num_labels=classes_count, name="pr_auc")]

    def plot_metrics(self, model_dir, steps_per_epoch, with_validation=False):
        logging.info("Plotting metrics")
        training_log_df = pd.read_csv(model_dir + '/training_log.csv')
        training_log_df['batch_total'] = training_log_df['batch'] + (training_log_df['epoch'] * steps_per_epoch)
        validation_log_df = training_log_df.dropna()
        fig, axs = plt.subplots(3, 2, figsize=(25, 12), constrained_layout=True)
        fig.suptitle(self.name + ' Model Metrics', fontsize=14)
        axs[0][0].plot(training_log_df['batch_total'], training_log_df['lr'])
        axs[0][0].set_title("Learning rate")
        axs[0][0].set_xlabel("Batch")
        secx = axs[0][0].secondary_xaxis('top',
                                         functions=(lambda x: x / steps_per_epoch, lambda x: x / steps_per_epoch))
        secx.set_xlabel('Epoch')
        axs[0][0].set_ylabel("Learning rate")
        axs[0][0].legend(loc='upper right')
        axs[0][1].plot(training_log_df['batch_total'], training_log_df['loss'], color='blue', label='Train loss')
        axs[2][1].plot(training_log_df['batch_total'], training_log_df['categorical_accuracy'], color='black',
                       label='Train Acc.')
        axs[2][1].plot(training_log_df['batch_total'], training_log_df['f1_score'],
                       color='red', label='Train F1')
        axs[2][1].plot(training_log_df['batch_total'], training_log_df['roc_auc'],
                       color='blue', label='Train ROC AUC')
        axs[2][1].plot(training_log_df['batch_total'], training_log_df['pr_auc'],
                       color='green', label='Train PR AUC')
        if with_validation:
            validation_log_df['batch_total'] = (validation_log_df['epoch'] + 1) * (steps_per_epoch - 1)
            axs[0][1].plot(validation_log_df['batch_total'], validation_log_df['val_loss'],
                           color='blue', label='Val. loss', linestyle='--')
            axs[2][1].plot(validation_log_df['batch_total'],
                           validation_log_df['val_categorical_accuracy'], color='black', label='Val. acc.',
                           linestyle='--')
            axs[2][1].plot(validation_log_df['batch_total'],
                           validation_log_df['val_f1_score'], color='red', label='Val. F1', linestyle='--')
            axs[2][1].plot(validation_log_df['batch_total'],
                           validation_log_df['val_roc_auc'], color='blue', label='Val. ROC AUC', linestyle='--')
            axs[2][1].plot(validation_log_df['batch_total'],
                           validation_log_df['val_pr_auc'], color='green', label='Val. PR AUC', linestyle='--')
        axs[0][1].set_title("Loss")
        axs[0][1].set_xlabel("Batch")
        secx = axs[0][1].secondary_xaxis('top',
                                         functions=(lambda x: x / steps_per_epoch, lambda x: x / steps_per_epoch))
        secx.set_xlabel('Epoch')
        axs[0][1].set_ylabel("Loss")
        axs[0][1].legend(loc='upper right')
        axs[2][1].set_title("Accuracy, F1 Score, ROC and PR AUCs")
        axs[2][1].set_xlabel("Batch")
        secx = axs[2][1].secondary_xaxis('top',
                                         functions=(lambda x: x / steps_per_epoch, lambda x: x / steps_per_epoch))
        secx.set_xlabel('Epoch')
        axs[2][1].set_ylabel("Accuracy/F1/AUCs")
        axs[2][1].legend(loc='upper left')
        classes_count = len(self.class_names)
        colors = cm.rainbow(np.linspace(0, 1, classes_count))
        for index, class_name in enumerate(self.class_names):
            class_name_string = str(class_name)
            axs[1][0].plot(training_log_df['batch_total'], training_log_df[class_name_string + '_precision'],
                           color=colors[index], label='Train ' + class_name_string + ' Prec.')
            axs[1][1].plot(training_log_df['batch_total'], training_log_df[class_name_string + '_recall'],
                           color=colors[index], label='Train ' + class_name_string + ' Recall.')
            axs[2][0].plot(training_log_df['batch_total'], training_log_df[class_name_string + '_r@p99'],
                           color=colors[index], label='Train ' + class_name_string + ' r@p.')
            if with_validation:
                axs[1][0].plot(validation_log_df['batch_total'],
                               validation_log_df['val_' + class_name_string + '_precision'],
                               color=colors[index], label='Val. ' + class_name_string + ' prec.', linestyle='--')
                axs[1][1].plot(validation_log_df['batch_total'],
                               validation_log_df['val_' + class_name_string + '_recall'],
                               color=colors[index], label='Val. ' + class_name_string + ' recall.', linestyle='--')
                axs[2][0].plot(validation_log_df['batch_total'],
                               validation_log_df['val_' + class_name_string + '_r@p99'],
                               color=colors[index], label='Val. ' + class_name_string + ' r@p', linestyle='--')
        axs[1][0].set_title("Precision (threshold = 0.5)")
        axs[1][0].set_xlabel("Batch")
        secx = axs[1][0].secondary_xaxis('top',
                                         functions=(lambda x: x / steps_per_epoch, lambda x: x / steps_per_epoch))
        secx.set_xlabel('Epoch')
        axs[1][0].set_ylabel("Precision")
        axs[1][0].legend(loc='upper left')
        axs[1][1].set_title("Recall (threshold = 0.5)")
        axs[1][1].set_xlabel("Batch")
        secx = axs[1][1].secondary_xaxis('top',
                                         functions=(lambda x: x / steps_per_epoch, lambda x: x / steps_per_epoch))
        secx.set_xlabel('Epoch')
        axs[1][1].set_ylabel("Recall")
        axs[1][1].legend(loc='upper left')
        axs[2][0].set_title("Recall at Precision=0.99")
        axs[2][0].set_xlabel("Batch")
        secx = axs[2][0].secondary_xaxis('top',
                                         functions=(lambda x: x / steps_per_epoch, lambda x: x / steps_per_epoch))
        secx.set_xlabel('Epoch')
        axs[2][0].set_ylabel("R@P")
        axs[2][0].legend(loc='upper left')
        plt.savefig(model_dir + '/metrics.png')
        plt.close(fig)
        plt.clf()
        logging.info("Plotted metrics")
