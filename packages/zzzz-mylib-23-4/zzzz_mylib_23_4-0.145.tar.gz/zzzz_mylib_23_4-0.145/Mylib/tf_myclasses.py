from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction
import tensorflow as tf


class ListBleuGetter:
    def __init__(self, y_true, y_pred):
        self.y_true = y_true
        self.y_pred = y_pred

    def next(self):
        words_in_true = [self.get_values_g1(item) for item in self.y_true]
        words_in_pred = [self.get_values_g1(item) for item in self.y_pred]

        smooth = SmoothingFunction()
        list_bleu = [
            sentence_bleu([ref], pred, smoothing_function=smooth.method1)
            for ref, pred in zip(words_in_true, words_in_pred)
        ]

        return list_bleu

    def get_values_g1(self, tensor):
        filtered = tf.boolean_mask(tensor, tensor > 1)
        filtered = filtered.numpy().astype("str").tolist()
        return filtered
