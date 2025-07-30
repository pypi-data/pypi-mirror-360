import tensorflow as tf
from Mylib.tf_myclasses import ListBleuGetter


class BleuScoreCustomMetric(tf.keras.metrics.Metric):
    def __init__(self, name="bleu", **kwargs):
        super().__init__(name=name, **kwargs)
        self.list_bleu = []

    def update_state(self, y_true, y_pred, sample_weight=None):
        y_pred = tf.argmax(y_pred, axis=-1)  # Convert về giống shape của y_true

        list_bleu_on_1batch = ListBleuGetter(y_true, y_pred).next()
        self.list_bleu += (
            list_bleu_on_1batch  # Thêm batch mới vào kết quả cuối cùng của epoch
        )

    def result(self):  # Tính toán vào cuối epoch
        return tf.reduce_mean(self.list_bleu)

    def reset_state(self):  # Trước khi vào epoch mới
        self.list_bleu = []
