import keras
import tensorflow as tf
import numpy as np
from keras import layers
from tensorflow.python.ops.gen_nn_ops import LeakyRelu


class TransformerEncoder(layers.Layer):
    def __init__(self, key_dim, num_heads, dropout_rate=0.1):
        super(TransformerEncoder, self).__init__()
        self.key_dim = key_dim
        self.num_heads = num_heads
        self.dropout_rate = dropout_rate

    def build(self, input_shape):
        self.input_dim = input_shape[-1]
        self.att = layers.MultiHeadAttention(num_heads=self.num_heads, key_dim=self.key_dim)
        self.ffn = keras.Sequential(
            [layers.Dense(self.input_dim, activation=LeakyRelu(0.01)), layers.Dense(self.key_dim), ]
        )
        self.att_norm = layers.LayerNormalization(epsilon=1e-6)
        self.ffn_norm = layers.LayerNormalization(epsilon=1e-6)
        self.att_dropout = layers.Dropout(self.dropout_rate)
        self.ffn_dropout = layers.Dropout(self.dropout_rate)

    def call(self, inputs, attention_mask, training):
        attn_output = self.att(inputs, inputs, inputs, mask=attention_mask)
        attn_output = self.att_dropout(attn_output, training=training)
        out1 = self.att_norm(inputs + attn_output)
        ffn_output = self.ffn(out1)
        ffn_output = self.ffn_dropout(ffn_output, training=training)
        return self.ffn_norm(out1 + ffn_output)


class TransformerDecoder(layers.Layer):
    def __init__(self, key_dim, num_heads, dropout_rate=0.1):
        super(TransformerDecoder, self).__init__()
        self.key_dim = key_dim
        self.num_heads = num_heads
        self.dropout_rate = dropout_rate

    def build(self, input_shape):
        self.att1 = layers.MultiHeadAttention(num_heads=self.num_heads, key_dim=self.key_dim)
        self.att1_dropout = layers.Dropout(self.dropout_rate)
        self.att1_norm = layers.LayerNormalization(epsilon=1e-6)
        self.att2 = layers.MultiHeadAttention(num_heads=self.num_heads, key_dim=self.key_dim)
        self.att2_dropout = layers.Dropout(self.dropout_rate)
        self.att2_norm = layers.LayerNormalization(epsilon=1e-6)
        self.ffn = keras.Sequential(
            [layers.Dense(self.input_shape, activation=LeakyRelu(0.01)), layers.Dense(self.key_dim), ]
        )
        self.ffn_dropout = layers.Dropout(self.dropout_rate)
        self.ffn_norm = layers.LayerNormalization(epsilon=1e-6)

    def call(self, inputs, encoder_inputs, attention_mask, decoder_mask, training):
        attn_output = self.att1(inputs, inputs, inputs, attention_mask=attention_mask)
        attn_output = self.att1_dropout(attn_output, training=training)
        norm1_output = self.att1_norm(inputs + attn_output)
        attn_output = self.att2(norm1_output, encoder_inputs, encoder_inputs, decoder_mask)
        attn_output = self.att2_dropout(attn_output, training=training)
        norm2_output = self.att2_norm(norm1_output + attn_output)
        ffn_output = self.ffn(norm2_output)
        ffn_output = self.ffn_dropout(ffn_output, training=training)
        return self.ffn_norm(norm2_output + ffn_output)


class Transformer(layers.Layer):
    """
    Implementation of Vaswani et. al (2017) Transformer design with multihead attention
    """
    def __init__(self, key_dim, num_heads, ffn_units, output_dim, stack_depth=2, dropout_rate=0.1):
        super(Transformer, self).__init__()
        self.key_dim = key_dim
        self.ffn_units = ffn_units
        self.output_dim = output_dim
        self.num_heads = num_heads
        self.dropout_rate = dropout_rate
        self.stack_depth = stack_depth

    def build(self, input_shape):
        self.input_dim = input_shape
        self.encoders = np.array([])
        for i in np.arange(0, self.stack_depth):
            self.encoders.append(TransformerEncoder(self.key_dim, self.num_heads, self.dropout_rate))
        self.decoders = np.array([])
        for i in np.arange(0, self.stack_depth):
            self.decoders.append(TransformerDecoder(self.key_dim, self.num_heads, self.dropout_rate))
        self.average_pooling = layers.GlobalAveragePooling1D()
        self.average_pooling_dropout = layers.Dropout(self.dropout_rate)
        self.pooling_dense = layers.Dense(self.ffn_units, activation=LeakyRelu(0.01))
        self.pooling_dense_dropout = layers.Dropout(self.dropout_rate)
        # The output is linear, in case this is a classification problem the softmax is applied in the loss function
        # TODO I don't see where softmax is applied in the loss function
        self.output_dense = layers.Dense(self.output_dim, activation="linear")

    def call(self, input, predicted_output, attention_mask, training):
        encoder_mask = Transformer.__create_padding_mask(input)
        for encoder in self.encoders:
            encoder_output = encoder(input, encoder_mask, training)
        # As the values to be masked are those == 1, we take the maximum to mask any values included in padding mask or
        # look ahead mask
        look_ahead_and_padding_mask = tf.maximum(
            Transformer.__create_padding_mask(predicted_output),
            Transformer.__create_look_ahead_mask(predicted_output)
        )
        decoder_mask = Transformer.__create_padding_mask(input)
        for decoder in self.decoders:
            decoder_output = decoder(predicted_output, encoder_output, look_ahead_and_padding_mask,
                                     decoder_mask, training)
        linear_proj_output = self.average_pooling(decoder_output)
        linear_proj_output = self.pooling_dense(linear_proj_output)
        linear_proj_output = self.pooling_dense_dropout(linear_proj_output, training=training)
        linear_proj_output = self.output_dense(linear_proj_output, training=training)
        return linear_proj_output

    @staticmethod
    def __create_padding_mask(input_sequence):
        """
        Creates the mask for zero-padded input sequences with dimension (batch_size, seq_length)
        :param input_sequence: 
        :return: the mask redimensioned to ?????
        """
        # TODO clarify the return step where new dimensions are created somehow?
        mask = tf.cast(tf.math.equal(input_sequence, 0), tf.float32)
        return mask[:, tf.newaxis, tf.newaxis, :]

    @staticmethod
    def __create_look_ahead_mask(seq):
        """Creates a mask taking all the elements from the diagonal and above of a tensor of (seq_length, seq_length)
        dimension. This ensures that we are masking the future tokens only:
        1 1 1
        0 1 1
        0 0 1
        """
        # Create the mask for the causal attention
        seq_len = tf.shape(seq)[1]
        look_ahead_mask = 1 - tf.linalg.band_part(tf.ones((seq_len, seq_len)), -1, 0)
        return look_ahead_mask