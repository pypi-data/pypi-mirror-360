import tensorflow as tf
#from keras_core.src.layers import LeakyReLU
from keras.layers import MultiHeadAttention, LeakyReLU
#from keras.src.layers import Dense
from keras_hub.layers import TransformerEncoder

from exoml.ml.layers.dropout import AdaptiveStdDropout


@tf.keras.utils.register_keras_serializable()
class ClassToken(tf.keras.layers.Layer):
    """Append a class token to an input layer."""

    def build(self, input_shape):
        cls_init = tf.zeros_initializer()
        self.hidden_size = input_shape[-1]
        self.cls = tf.Variable(
            name="cls",
            initial_value=cls_init(shape=(1, 1, self.hidden_size), dtype="float32"),
            trainable=True,
        )

    def call(self, inputs):
        batch_size = tf.shape(inputs)[0]
        cls_broadcasted = tf.cast(
            tf.broadcast_to(self.cls, [batch_size, 1, self.hidden_size]),
            dtype=inputs.dtype,
        )
        return tf.concat([cls_broadcasted, inputs], 1)

    def get_config(self):
        config = super().get_config()
        return config

    @classmethod
    def from_config(cls, config):
        return cls(**config)


@tf.keras.utils.register_keras_serializable()
class AddPositionEmbs(tf.keras.layers.Layer):
    """Adds (optionally learned) positional embeddings to the inputs."""

    def build(self, input_shape):
        assert (
            len(input_shape) == 3
        ), f"Number of dimensions should be 3, got {len(input_shape)}"
        self.pe = tf.Variable(
            name="pos_embedding",
            initial_value=tf.random_normal_initializer(stddev=0.06)(
                shape=(1, input_shape[1], input_shape[2])
            ),
            dtype="float32",
            trainable=True,
        )

    def call(self, inputs):
        return inputs + tf.cast(self.pe, dtype=inputs.dtype)

    def get_config(self):
        config = super().get_config()
        return config

    @classmethod
    def from_config(cls, config):
        return cls(**config)


# @tf.keras.utils.register_keras_serializable()
# class TransformerEncoder(tf.keras.layers.Layer):
#     """Implements a Transformer block."""
#
#     def __init__(self, *args, num_heads, mlp_dim, hyperparams, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.num_heads = num_heads
#         self.mlp_dim = mlp_dim
#         self.hyperparams = hyperparams
#         self.regularizer_value = 0.1
#
#     def build(self, input_shape):
#         self.att = MultiHeadAttention(num_heads=self.num_heads,
#             key_dim=input_shape[-1],
#             name="MultiHeadDotProductAttention_1"
#         )
#         self.mlpblock = tf.keras.Sequential(
#             [
#                 tf.keras.layers.Dense(self.mlp_dim, activation=LeakyReLU(), name=f"{self.name}/Dense_0",
#                                       activity_regularizer=tf.keras.regularizers.L1L2(
#                                           l1=self.hyperparams.l1_regularization,
#                                           l2=self.hyperparams.l2_regularization)
#                                       ),
#                 AdaptiveStdDropout(rate=self.hyperparams.dropout_rate,
#                                    max_rate=self.hyperparams.dropout_max_rate),
#                 tf.keras.layers.Dense(input_shape[-1], name=f"{self.name}/Dense_1", activation=LeakyReLU(),
#                                       activity_regularizer=tf.keras.regularizers.L1L2(
#                                           l1=self.hyperparams.l1_regularization,
#                                           l2=self.hyperparams.l2_regularization)
#                                       )
#             ],
#             name="MlpBlock_3",
#         )
#         self.layernorm1 = tf.keras.layers.LayerNormalization(
#             epsilon=1e-6, name="LayerNorm_1"
#         )
#         self.layernorm2 = tf.keras.layers.LayerNormalization(
#             epsilon=1e-6, name="LayerNorm_2"
#         )
#         self.layernorm3 = tf.keras.layers.LayerNormalization(
#             epsilon=1e-6, name="LayerNorm_3"
#         )
#         self.dropout_layer = AdaptiveStdDropout(rate=self.hyperparams.dropout_rate,
#                                          max_rate=self.hyperparams.dropout_max_rate)
#
#     def call(self, inputs, training=True, return_attention_scores=True):
#         x = inputs
#         #x = self.layernorm1(x)
#         x = self.att(x, x, training=training, return_attention_scores=return_attention_scores)
#         x = self.dropout_layer(x, training=training)
#         x = x + inputs
#         y = self.layernorm2(x)
#         y = self.mlpblock(y, training=training)
#         return self.layernorm3(x + y)
#
#     def get_config(self):
#         config = super().get_config()
#         config.update(
#             {
#                 "num_heads": self.num_heads,
#                 "mlp_dim": self.mlp_dim,
#                 "dropout": self.hyperparams.dropout_rate,
#             }
#         )
#         return config
#
#     @classmethod
#     def from_config(cls, config):
#         return cls(**config)


@tf.keras.utils.register_keras_serializable()
class Transformer(tf.keras.layers.Layer):
    def __init__(self, *args, num_heads, mlp_dim, hyperparams, num_blocks, **kwargs):
        super().__init__(*args, **kwargs)
        self.num_heads = num_heads
        self.mlp_dim = mlp_dim
        self.hyperparams = hyperparams
        self.num_blocks = num_blocks
        self.transformer_encoders = []
        self.regularizer_value = 0.1

    def build(self, input_shape):
        for n in range(self.num_blocks):
            self.transformer_encoders = self.transformer_encoders + \
                                         [TransformerEncoder(
                self.mlp_dim,
                self.num_heads,
                dropout=self.hyperparams.dropout_rate,
                activation=LeakyReLU(),
                layer_norm_epsilon=self.hyperparams.transformer_layer_norm_epsilon,
                kernel_initializer="glorot_uniform",
                bias_initializer="zeros",
                normalize_first=False
            )]
            # self.transformer_encoders = self.transformer_encoders + [TransformerEncoder(
            #     num_heads=self.num_heads,
            #     mlp_dim=self.mlp_dim,
            #     hyperparams=self.hyperparams,
            #     name=f"Transformer/encoderblock_{n}"
            # )]

    def call(self, inputs):
        result = inputs
        for n in range(self.num_blocks):
            result = self.transformer_encoders[n](result)
        return result

    def get_config(self):
        config = super().get_config()
        config.update(
            {
                "num_heads": self.num_heads,
                "mlp_dim": self.mlp_dim,
                "dropout": self.hyperparams.dropout_rate,
                "num_blocks": self.num_blocks,
            }
        )
        return config

    @classmethod
    def from_config(cls, config):
        return cls(**config)


@tf.keras.utils.register_keras_serializable()
class TransformerClassifier(tf.keras.layers.Layer):
    def __init__(self, *args, transformer_input_size, patch_size, num_heads, mlp_dim, hyperparams, num_blocks, classes,
                 **kwargs):
        super().__init__(*args, **kwargs)
        self.transformer_input_size = transformer_input_size
        self.patch_size = patch_size
        self.num_heads = num_heads
        self.mlp_dim = mlp_dim
        self.hyperparams = hyperparams
        self.num_blocks = num_blocks
        self.classes = classes
        self.regularizer_value = 0.1

    def build(self, input_shape):
        # The linear projection could be a conv1d if the input was an image to be patched in pieces. As it is not,
        # we don't need a convolutional layer because for us a patch is of kernel=1
        # self.linear_proj = tf.keras.layers.Conv1D(
        #     filters=self.transformer_input_size,
        #     kernel_size=self.patch_size,
        #     strides=self.patch_size,
        #     padding="same",
        #     name="embedding"
        # )
        #self.linear_proj = tf.keras.layers.Dense(self.transformer_input_size)
        # self.linear_proj = tf.keras.layers.Dense(self.transformer_input_size, activation="relu")
        #self.class_token = ClassToken(name="class_token")
        #self.add_pos_embedding = AddPositionEmbs(name="add_pos_embedding")
        self.transformer = Transformer(num_heads=self.num_heads, mlp_dim=self.mlp_dim,
                                       hyperparams=self.hyperparams, num_blocks=self.num_blocks)
        self.layer_norm = tf.keras.layers.LayerNormalization(epsilon=self.hyperparams.transformer_layer_norm_epsilon, name="Transformer/encoder_norm")
        activation = "softmax" if self.classes > 1 else "sigmoid"
        self.output_flatten = tf.keras.layers.Flatten()
        self.head = tf.keras.layers.Dense(self.classes, name="head", activation=activation,
                                          activity_regularizer=tf.keras.regularizers.L1L2(
                                              l1=self.hyperparams.l1_regularization,
                                              l2=self.hyperparams.l2_regularization)
                                          )


    def call(self, inputs):
        # result = self.linear_proj(inputs)
        # Assuming we don't need to reshape our data as we don't need to flatten the resulting image of the linear_proj
        #result = tf.keras.layers.Reshape((result.shape[1] * result.shape[2], self.transformer_input_size))(result)
        #result = self.class_token(result)
        #result = self.add_pos_embedding(result)
        result = self.transformer(inputs)
        # result = tf.keras.layers.Lambda(
        #      lambda v: v[:, 0],
        #      name="ExtractToken")(result)
        result = self.layer_norm(result)
        result = self.output_flatten(result)
        result = self.head(result)
        #result = self.dropout_layer(result, training=training)
        return result
