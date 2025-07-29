from keras.metrics import Mean


class FixedMean(Mean):
    """Fixed mean as the tf.keras.metrics.Mean tries to compute the Mean with a wrong signature method:
    https://stackoverflow.com/questions/68354367/getting-an-error-when-using-tf-keras-metrics-mean-in-functional-keras-api"""
    def update_state(self, y_true, y_pred, sample_weight=None):
        super().update_state(y_pred, sample_weight=sample_weight)