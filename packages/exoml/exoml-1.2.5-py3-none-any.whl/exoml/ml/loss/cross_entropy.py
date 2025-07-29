from keras.activations import softmax, sigmoid
from keras.losses import CategoricalCrossentropy, BinaryCrossentropy, binary_crossentropy
from keras.metrics import CategoricalAccuracy, BinaryAccuracy
import tensorflow as tf
from keras import backend as K
import numpy as np


def categorical_cross_entropy_with_dca_loss(y_true, y_pred, alpha=1., beta=10., from_logits=False,
                                            activation_function=softmax):
    """
    DCA loss applied to categorical classification
    :param y_true: the real labels values (typically one hot encoded)
    :param y_pred: the predicted probabilities
    :param alpha: the alpha corrector for the categorical cross entropy loss
    :param beta: the beta corrector for the dca (difference between confidence and accuracy)
    :param from_logits: whether use weights or probabilities
    :param activation_function: the activation function to be applied if from_logits=True
    :return: the dca loss
    """
    return dca_loss(y_true, y_pred, CategoricalCrossentropy(from_logits=from_logits), CategoricalAccuracy(), alpha,
                    beta, from_logits, activation_function)


def binary_cross_entropy_with_dca_loss(y_true, y_pred, alpha=1., beta=10., from_logits=False,
                                       activation_function=sigmoid):
    """
    DCA loss applied to binary classification
    :param y_true: the real labels values (typically one hot encoded)
    :param y_pred: the predicted probabilities
    :param alpha: the alpha corrector for the categorical cross entropy loss
    :param beta: the beta corrector for the dca (difference between confidence and accuracy)
    :param from_logits: whether use weights or probabilities
    :param activation_function: the activation function to be applied if from_logits=True
    :return: the dca loss
    """
    return dca_loss(y_true, y_pred, BinaryCrossentropy(from_logits=from_logits), BinaryAccuracy(), alpha, beta,
                    from_logits, activation_function)


def dca_loss(y_true, y_pred, loss, accuracy, alpha=1., beta=10., from_logits=False, activation_function=softmax):
    """
    Loss function applying penalization to loss decrements when accuracy keeps flatten from Liang et al. (2020)
    https://arxiv.org/abs/2009.04057 (https://stackoverflow.com/questions/68755788/keras-version-of-the-combined-cross-entropy-and-calibration-loss)
    :param y_true: the real labels values (typically one hot encoded)
    :param y_pred: the predicted probabilities
    :param alpha: the alpha corrector for the categorical cross entropy loss
    :param beta: the beta corrector for the dca (difference between confidence and accuracy)
    :param from_logits: whether use weights or probabilities
    :param activation_function: the activation function to be applied if from_logits=True
    :return: the computed loss
    """
    loss_value = loss(y_true, y_pred)
    pred_values = y_pred
    if from_logits and activation_function is not None:
        pred_values = softmax(y_true, axis=1)
    predictions = tf.math.argmax(pred_values, axis=1)
    confidences = tf.reduce_max(pred_values, axis=1)
    mean_conf = tf.reduce_mean(confidences)
    accuracy.update_state(pred_values, y_pred)
    acc = accuracy.result().numpy()
    dca = tf.abs(mean_conf - acc)
    loss_value = alpha * loss_value + beta * dca
    return loss_value


def binary_focal_loss(y_true, y_pred, gamma=2., alpha=.2):
    """
    Binary form of focal loss.
      FL(p_t) = -alpha * (1 - p_t)**gamma * log(p_t)
      where p = sigmoid(x), p_t = p or 1 - p depending on if the label is 1 or 0, respectively.
    References:
        https://arxiv.org/pdf/1708.02002.pdf
    Usage:
     model.compile(loss=[binary_focal_loss(alpha=.25, gamma=2)], metrics=["accuracy"], optimizer=adam)
    """
    y_true = tf.cast(y_true, tf.float32)
    # Define epsilon so that the back-propagation will not result in NaN for 0 divisor case
    epsilon = K.epsilon()
    # Add the epsilon to prediction value
    # y_pred = y_pred + epsilon
    # Clip the prediciton value
    y_pred = K.clip(y_pred, epsilon, 1.0 - epsilon)
    # Calculate p_t
    p_t = tf.where(K.equal(y_true, 1), y_pred, 1 - y_pred)
    # Calculate alpha_t
    alpha_factor = K.ones_like(y_true) * alpha
    alpha_t = tf.where(K.equal(y_true, 1), alpha_factor, 1 - alpha_factor)
    # Calculate cross entropy
    cross_entropy = -K.log(p_t)
    weight = alpha_t * K.pow((1 - p_t), gamma)
    # Calculate focal loss
    loss = weight * cross_entropy
    # Sum the losses in mini_batch
    loss = K.mean(K.sum(loss, axis=1))
    return loss


def categorical_focal_loss(y_true, y_pred, alpha=0.2, gamma=2.):
    """
    Softmax version of focal loss.
    When there is a skew between different categories/labels in your data set, you can try to apply this function as a
    loss.
           m
      FL = ∑  -alpha * (1 - p_o,c)^gamma * y_o,c * log(p_o,c)
          c=1
      where m = number of classes, c = class and o = observation
    Parameters:
      alpha -- the same as weighing factor in balanced cross entropy. Alpha is used to specify the weight of different
      categories/labels, the size of the array needs to be consistent with the number of classes.
      gamma -- focusing parameter for modulating factor (1-p)
    Default value:
      gamma -- 2.0 as mentioned in the paper
      alpha -- 0.25 as mentioned in the paper
    References:
        Official paper: https://arxiv.org/pdf/1708.02002.pdf
        https://www.tensorflow.org/api_docs/python/tf/keras/backend/categorical_crossentropy
    Usage:
     model.compile(loss=[categorical_focal_loss(alpha=[[.25, .25, .25]], gamma=2)], metrics=["accuracy"], optimizer=adam)
    """
    # Clip the prediction value to prevent NaN's and Inf's
    epsilon = K.epsilon()
    y_pred = K.clip(y_pred, epsilon, 1. - epsilon)
    # Calculate Cross Entropy
    cross_entropy = -y_true * K.log(y_pred)
    # Calculate Focal Loss
    loss = alpha * K.pow(1 - y_pred, gamma) * cross_entropy
    # Compute mean loss in mini_batch
    return K.mean(K.sum(loss, axis=-1))


def fb_loss(y_true, y_pred, beta=1):
    """
    The macro F1-score has one big trouble. It's non-differentiable. Which means we cannot use it as a loss function.

    But we can modify it to be differentiable. Instead of accepting 0/1 integer predictions, let's accept probabilities
    instead. Thus if the ground truth is 1 and the model prediction is 0.4, we calculate it as 0.4 true positive and
    0.6 false negative. If the ground truth is 0 and the model prediction is 0.4, we calculate it as 0.6 true negative
    and 0.4 false positive.
    :param y_true: the real outputs
    :param y_pred: the predicted outputs
    :return:
    """
    tp = K.sum(K.cast(y_true * y_pred, 'float'), axis=0)
    tn = K.sum(K.cast((1 - y_true) * (1 - y_pred), 'float'), axis=0)
    fp = K.sum(K.cast((1 - y_true) * y_pred, 'float'), axis=0)
    fn = K.sum(K.cast(y_true * (1 - y_pred), 'float'), axis=0)
    p = tp / (tp + fp + K.epsilon())
    r = tp / (tp + fn + K.epsilon())
    f1 = (1 + beta ** 2) * p * r / (beta ** 2 * p + r + K.epsilon())
    f1 = tf.where(tf.math.is_nan(f1), tf.zeros_like(f1), f1)
    return 1 - K.mean(f1)


def dice_loss(targets, inputs, smooth=1e-6):
    """
    From https://www.kaggle.com/code/bigironsphere/loss-function-library-keras-pytorch/notebook
    :param targets: the expected outputs
    :param inputs: the given inputs
    :param smooth:
    :return: the dice loss
    """
    inputs = K.flatten(inputs)
    targets = K.flatten(targets)
    intersection = K.sum((inputs * targets))
    dice = (2 * intersection + smooth) / (K.sum(targets) + K.sum(inputs) + smooth)
    return 1 - dice


def dice_bce_loss(targets, inputs, smooth=1e-6):
    """
    This loss combines Dice loss with the standard binary cross-entropy (BCE) loss that is generally the default for
    segmentation models. Combining the two methods allows for some diversity in the loss, while benefitting from the
    stability of BCE.
    From https://www.kaggle.com/code/bigironsphere/loss-function-library-keras-pytorch/notebook
    :param targets: the expected outputs
    :param inputs: the given inputs
    :param smooth: the dice loss smooth parameter
    :return:
    """
    inputs = K.flatten(inputs)
    targets = K.flatten(targets)
    bce = binary_crossentropy(targets, inputs)
    intersection = K.sum((inputs * targets))
    dice_loss = 1 - (2 * intersection + smooth) / (K.sum(targets) + K.sum(inputs) + smooth)
    dice_bce = bce + dice_loss
    return dice_bce


