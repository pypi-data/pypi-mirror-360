import tensorflow as tf
from tensorflow.keras import layers
from Mylib import tf_layers, tf_image_layers


class RNNList(layers.Layer):
    def __init__(
        self,
        layer_name,
        list_units,
        recurrent_dropout,
        do_have_last_layer=True,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.layer_name = layer_name
        self.list_units = list_units
        self.recurrent_dropout = recurrent_dropout
        self.do_have_last_layer = do_have_last_layer

    def get_config(self):
        # Trả về cấu hình của lớp tùy chỉnh
        config = super().get_config()
        config.update(
            {
                "layer_name": self.layer_name,
                "list_units": self.list_units,
                "recurrent_dropout": self.recurrent_dropout,
                "do_have_last_layer": self.do_have_last_layer,
            }
        )
        return config

    def build(self, input_shape):
        self.list_RNN = [
            tf_layers.RNNLayerNormalization(
                layer_name=self.layer_name,
                units=units,
                recurrent_dropout=self.recurrent_dropout,
                return_sequences=True,
            )
            for units in self.list_units
        ]

        self.lastRNN = tf_layers.RNNLayerNormalization(
            layer_name=self.layer_name,
            units=self.list_units[-1],
            recurrent_dropout=0,
            return_sequences=False,
        )

        super().build(input_shape)

    def call(self, x):
        # Xử lí x
        for layer in self.list_RNN:
            x = layer(x)

        # Xử lí x thông qua layer cuối cùng
        if self.do_have_last_layer:
            x = self.lastRNN(x)

        return x

    @classmethod
    def from_config(cls, config):
        # Giải mã lại lớp từ cấu hình
        return cls(**config)


class TransformerEncoderList(layers.Layer):
    def __init__(self, embed_dim, dense_dim, num_heads, num_layers, **kwargs):
        super().__init__(**kwargs)
        self.embed_dim = embed_dim
        self.dense_dim = dense_dim
        self.num_heads = num_heads
        self.num_layers = num_layers

    def get_config(self):
        # Trả về cấu hình của lớp tùy chỉnh
        config = super().get_config()
        config.update(
            {
                "embed_dim": self.embed_dim,
                "dense_dim": self.dense_dim,
                "num_heads": self.num_heads,
                "num_layers": self.num_layers,
            }
        )
        return config

    def build(self, input_shape):
        self.list_TransformerEncoder = [
            tf_layers.TransformerDecoder(
                embed_dim=self.embed_dim,
                dense_dim=self.dense_dim,
                num_heads=self.num_heads,
            )
            for _ in range(self.num_layers)
        ]

        super().build(input_shape)

    def call(self, x):
        # Xử lí x
        for layer in self.list_TransformerEncoder:
            x = layer(x)

        return x

    @classmethod
    def from_config(cls, config):
        # Giải mã lại lớp từ cấu hình
        return cls(**config)


class TransformerDecoderList(layers.Layer):
    def __init__(self, embed_dim, dense_dim, num_heads, num_layers, **kwargs):
        super().__init__(**kwargs)
        self.embed_dim = embed_dim
        self.dense_dim = dense_dim
        self.num_heads = num_heads
        self.num_layers = num_layers

    def get_config(self):
        # Trả về cấu hình của lớp tùy chỉnh
        config = super().get_config()
        config.update(
            {
                "embed_dim": self.embed_dim,
                "dense_dim": self.dense_dim,
                "num_heads": self.num_heads,
                "num_layers": self.num_layers,
            }
        )
        return config

    def build(self, input_shape):
        self.list_TransformerDecoder = [
            tf_layers.TransformerDecoder(
                embed_dim=self.embed_dim,
                dense_dim=self.dense_dim,
                num_heads=self.num_heads,
            )
            for _ in range(self.num_layers)
        ]

        super().build(input_shape)

    def call(self, x, encoder_outputs):
        # Xử lí x
        for layer in self.list_TransformerDecoder:
            x = layer(x, encoder_outputs)

        return x

    @classmethod
    def from_config(cls, config):
        # Giải mã lại lớp từ cấu hình
        return cls(**config)
