import logging

from keras.losses import BinaryCrossentropy
from keras.metrics import Precision, Recall, AUC, BinaryAccuracy, RecallAtPrecision
from exoml.ml.loss.cross_entropy import binary_focal_loss
from exoml.ml.metrics.auc import precision_at_k, mean_true_positive_value, mean_true_negative_value, \
    mean_false_negative_value, mean_false_positive_value, ThresholdAtPrecision
from exoml.ml.model.base_model import BaseModel
import pandas as pd
import matplotlib.pyplot as plt


class BinaryModel(BaseModel):
    def __init__(self, name, input_size, class_ids, type_to_label, hyperparams) -> None:
        super().__init__(name, input_size, class_ids, type_to_label, hyperparams)

    def instance_loss_accuracy(self):
        return BinaryCrossentropy(), BinaryAccuracy()

    def instance_metrics(self):
        return [Precision(name="precision"), Recall(name="recall"),
                #F1Score(num_classes=1, threshold=0.5, average='weighted', name='f1_score'),
                RecallAtPrecision(precision=0.99, name="r@p99", num_thresholds=1000),
                RecallAtPrecision(precision=1.0, name="r@p100", num_thresholds=1000),
                #ThresholdAtPrecision(precision=0.99, name="t@p99", num_thresholds=1000),
                AUC(name="roc_auc"),
                AUC(curve="PR", name="pr_auc")]

    def plot_metrics(self, model_dir, steps_per_epoch, with_validation=False):
        logging.info("Plotting metrics")
        training_log_df = pd.read_csv(model_dir + '/training_log.csv')
        training_log_df['batch_total'] = training_log_df['batch'] + (training_log_df['epoch'] * steps_per_epoch)
        validation_log_df = training_log_df.dropna(subset = ['val_precision', 'val_recall', 'val_r@p99', 'val_loss', 'val_binary_accuracy',
                                                             'val_pr_auc', 'val_roc_auc'])
        fig, axs = plt.subplots(2, 2, figsize=(25, 7), constrained_layout=True)
        fig.suptitle(self.name + ' Model Metrics', fontsize=14)
        axs[0][0].plot(training_log_df['batch_total'], training_log_df['lr'])
        axs[0][1].plot(training_log_df['batch_total'], training_log_df['loss'], color='blue', label='Train loss')
        if with_validation:
            axs[0][1].plot(validation_log_df['epoch'] * steps_per_epoch, validation_log_df['val_loss'], color='red',
                           label='Val. loss')
        axs[1][0].plot(training_log_df['batch_total'], training_log_df['precision'], color='red', label='Train Prec.')
        axs[1][0].plot(training_log_df['batch_total'], training_log_df['recall'], color='blue', label='Train Recall.')
        axs[1][0].plot(training_log_df['batch_total'], training_log_df['r@p99'], color='green', label='Train r@p.')
        axs[1][1].plot(training_log_df['batch_total'], training_log_df['binary_accuracy'], color='black', label='Train Acc.')
        axs[1][1].plot(training_log_df['batch_total'], training_log_df['roc_auc'], color='blue', label='Train ROC AUC')
        axs[1][1].plot(training_log_df['batch_total'], training_log_df['pr_auc'], color='green',
                       label='Train PR AUC')
        if with_validation:
            axs[1][0].plot(validation_log_df['batch_total'], validation_log_df['val_precision'],
                           color='red', label='Val. prec.', linestyle='--')
            axs[1][0].plot(validation_log_df['batch_total'], validation_log_df['val_recall'],
                           color='blue', label='Val. recall.', linestyle='--')
            axs[1][0].plot(validation_log_df['batch_total'], validation_log_df['val_r@p99'],
                           color='green', label='Val. r@p', linestyle='--')
            axs[1][1].plot(validation_log_df['batch_total'], validation_log_df['val_binary_accuracy'],
                           color='black', label='Val. acc.', linestyle='--')
            axs[1][1].plot(validation_log_df['batch_total'], validation_log_df['val_roc_auc'],
                           color='blue', label='Val. ROC AUC', linestyle='--')
            axs[1][1].plot(validation_log_df['batch_total'], validation_log_df['val_pr_auc'],
                           color='green', label='Val. PR AUC', linestyle='--')
        axs[0][0].set_xlabel("Batch")
        secx = axs[0][0].secondary_xaxis('top',
                                         functions=(lambda x: x / steps_per_epoch, lambda x: x / steps_per_epoch))
        secx.set_xlabel('Epoch')
        axs[0][0].set_ylabel("Learning rate")
        axs[0][0].legend(loc='upper right')
        axs[0][1].set_xlabel("Batch")
        secx = axs[0][1].secondary_xaxis('top',
                                         functions=(lambda x: x / steps_per_epoch, lambda x: x / steps_per_epoch))
        secx.set_xlabel('Epoch')
        axs[0][1].set_ylabel("Loss")
        axs[0][1].legend(loc='upper right')
        axs[1][0].set_xlabel("Batch")
        secx = axs[1][0].secondary_xaxis('top',
                                         functions=(lambda x: x / steps_per_epoch, lambda x: x / steps_per_epoch))
        secx.set_xlabel('Epoch')
        axs[1][0].set_ylabel("Precision/Recall/R@P")
        axs[1][0].legend(loc='upper left')
        axs[1][1].set_xlabel("Batch")
        secx = axs[1][1].secondary_xaxis('top',
                                         functions=(lambda x: x / steps_per_epoch, lambda x: x / steps_per_epoch))
        secx.set_xlabel('Epoch')
        axs[1][1].set_ylabel("Accuracy/F1/AUCs")
        axs[1][1].legend(loc='upper left')
        plt.savefig(model_dir + '/metrics.png')
        plt.close(fig)
        plt.clf()
        logging.info("Plotted metrics")
