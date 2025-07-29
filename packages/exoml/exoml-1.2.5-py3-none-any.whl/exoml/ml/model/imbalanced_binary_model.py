from keras.losses import BinaryCrossentropy
from keras.metrics import BinaryAccuracy

from exoml.ml.loss.cross_entropy import binary_focal_loss
from exoml.ml.model.binary_model import BinaryModel


class ImbalancedBinaryModel(BinaryModel):
    def __init__(self, name, input_size, class_ids, type_to_label, hyperparams) -> None:
        super().__init__(name, input_size, class_ids, type_to_label, hyperparams)

    def instance_loss_accuracy(self):
        return BinaryCrossentropy(), BinaryAccuracy()
