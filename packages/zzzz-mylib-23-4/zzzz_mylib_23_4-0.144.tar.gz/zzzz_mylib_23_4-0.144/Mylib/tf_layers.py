from tensorflow.keras import layers
from tensorflow import keras
import tensorflow as tf


class PositionalEmbedding(layers.Layer):
    def __init__(self, sequence_length, input_dim, output_dim, **kwargs):

        super().__init__(**kwargs)
        # Các layers
        self.token_embeddings = layers.Embedding(
            input_dim=input_dim, output_dim=output_dim
        )  # Embedding layers cho token indices
        self.position_embeddings = layers.Embedding(
            input_dim=sequence_length, output_dim=output_dim
        )  # Layer này cho token positions

        # Các siêu tham số
        self.sequence_length = sequence_length
        self.input_dim = input_dim
        self.output_dim = output_dim

    def call(self, inputs):

        length = tf.shape(inputs)[-1]
        positions = tf.range(start=0, limit=length, delta=1)
        embedded_tokens = self.token_embeddings(inputs)
        embedded_positions = self.position_embeddings(positions)
        embedded = embedded_tokens + embedded_positions  # Cộng 2 embedding vectors lại

        # Save mask using Keras's _keras_mask mechanism
        embedded._keras_mask = tf.not_equal(inputs, 0)
        return embedded

    def build(self, input_shape):
        super().build(input_shape)

    def compute_mask(
        self, inputs, mask=None
    ):  # Giống với Embedding layer,  layer này nên tạo ra mask để ignore paddings 0 trong inputs
        return None

    def get_config(self):  # Để lưu được model
        config = super().get_config()
        config.update(
            {
                "output_dim": self.output_dim,
                "sequence_length": self.sequence_length,
                "input_dim": self.input_dim,
            }
        )
        return config


class TransformerEncoder(layers.Layer):
    def __init__(self, embed_dim, dense_dim, num_heads, **kwargs):
        super().__init__(**kwargs)
        # Các siêu tham số
        self.supports_masking = True  # Có hỗ trợ masking
        self.embed_dim = embed_dim  # size của input token vectors
        self.dense_dim = dense_dim  # Size của Denser layer
        self.num_heads = num_heads  # Số lượng attention heads

        # Các layers
        self.attention = layers.MultiHeadAttention(
            num_heads=num_heads, key_dim=embed_dim
        )
        self.dense_proj = keras.Sequential(
            [
                layers.Dense(dense_dim, activation="relu"),
                layers.Dense(embed_dim),
            ]
        )
        self.layernorm_1 = layers.LayerNormalization()
        self.layernorm_2 = layers.LayerNormalization()

    def call(self, inputs, mask=None):  # Tính toán là ở trong hàm call()
        if mask is not None:
            mask = mask[
                :, tf.newaxis, :
            ]  # mask được tạo ra bởi Embedding layer là 2D, nhưng attention layer thì yêu cầu 3D hoặc 4D -> thêm chiều
        attention_output = self.attention(inputs, inputs, attention_mask=mask)
        proj_input = self.layernorm_1(inputs + attention_output)
        proj_output = self.dense_proj(proj_input)
        return self.layernorm_2(proj_input + proj_output)

    def build(self, input_shape):
        super().build(input_shape)

    def get_config(self):  # Cần thiết để lưu model
        config = super().get_config()
        config.update(
            {
                "embed_dim": self.embed_dim,
                "num_heads": self.num_heads,
                "dense_dim": self.dense_dim,
            }
        )
        return config


class TransformerDecoder(layers.Layer):
    def __init__(self, embed_dim, dense_dim, num_heads, **kwargs):
        super().__init__(**kwargs)
        self.embed_dim = embed_dim
        self.dense_dim = dense_dim
        self.num_heads = num_heads
        self.attention_1 = layers.MultiHeadAttention(
            num_heads=num_heads, key_dim=embed_dim
        )
        self.attention_2 = layers.MultiHeadAttention(
            num_heads=num_heads, key_dim=embed_dim
        )
        self.dense_proj = keras.Sequential(
            [
                layers.Dense(dense_dim, activation="relu"),
                layers.Dense(embed_dim),
            ]
        )
        self.layernorm_1 = layers.LayerNormalization()
        self.layernorm_2 = layers.LayerNormalization()
        self.layernorm_3 = layers.LayerNormalization()
        self.supports_masking = True

    def call(self, inputs, encoder_outputs, mask=None):
        causal_mask = self.get_causal_attention_mask(inputs)  # Get causal_mask
        padding_mask = None  # Define để né lỗi UnboundLocalError
        if mask is not None:  # Chuẩn bị input mask
            padding_mask = tf.cast(mask[:, tf.newaxis, :], dtype="int32")
            padding_mask = tf.minimum(
                padding_mask, causal_mask
            )  # merge 2 masks với nhau
        attention_output_1 = self.attention_1(
            query=inputs,
            value=inputs,
            key=inputs,
            attention_mask=causal_mask,  # pass causal_mask vào layer attention đâu tiên,
            # cái thực hiện  self-attention cho target sequence
        )
        attention_output_1 = self.layernorm_1(inputs + attention_output_1)
        attention_output_2 = self.attention_2(
            query=attention_output_1,
            value=encoder_outputs,
            key=encoder_outputs,
            attention_mask=padding_mask,  # pass combined mask cho layer attention thứ 2,
            # cái mà relates the source sequence to the target sequence.
        )
        attention_output_2 = self.layernorm_2(attention_output_1 + attention_output_2)
        proj_output = self.dense_proj(attention_output_2)
        return self.layernorm_3(attention_output_2 + proj_output)

    def get_config(self):
        config = super().get_config()
        config.update(
            {
                "embed_dim": self.embed_dim,
                "num_heads": self.num_heads,
                "dense_dim": self.dense_dim,
            }
        )
        return config

    def get_causal_attention_mask(self, inputs):
        input_shape = tf.shape(inputs)
        batch_size, sequence_length = input_shape[0], input_shape[1]
        i = tf.range(sequence_length)[:, tf.newaxis]
        j = tf.range(sequence_length)
        mask = tf.cast(i >= j, dtype="int32")
        mask = tf.reshape(mask, (1, input_shape[1], input_shape[1]))
        mult = tf.concat(
            [tf.expand_dims(batch_size, -1), tf.constant([1, 1], dtype=tf.int32)],
            axis=0,
        )
        return tf.tile(mask, mult)

    def build(self, input_shape):
        # No custom weights to create, so just mark as built
        super().build(input_shape)


class RNNLayerNormalization(layers.Layer):
    def __init__(
        self, layer_name, units, return_sequences=False, recurrent_dropout=0, **kwargs
    ):
        super().__init__(**kwargs)
        self.layer_name = layer_name
        self.units = units
        self.return_sequences = return_sequences
        self.recurrent_dropout = recurrent_dropout

    def get_config(self):
        # Trả về cấu hình của lớp tùy chỉnh
        config = super().get_config()
        config.update(
            {
                "layer_name": self.layer_name,
                "units": self.units,
                "return_sequences": self.return_sequences,
                "recurrent_dropout": self.recurrent_dropout,
            }
        )
        return config

    def build(self, input_shape):
        ClassName = globals()[self.layer_name]
        self.RNN = ClassName(
            units=self.units,
            return_sequences=self.return_sequences,
            recurrent_dropout=self.recurrent_dropout,
        )
        self.LayerNormalization = layers.LayerNormalization()

        super().build(input_shape)

    def call(self, x):
        # Xử lí x
        x = self.RNN(x)
        x = self.LayerNormalization(x)

        return x

    @classmethod
    def from_config(cls, config):
        # Giải mã lại lớp từ cấu hình
        return cls(**config)
