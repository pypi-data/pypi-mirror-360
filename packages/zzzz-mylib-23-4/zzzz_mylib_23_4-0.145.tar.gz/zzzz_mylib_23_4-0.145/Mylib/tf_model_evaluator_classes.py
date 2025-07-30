import numpy as np
from Mylib import tf_myfuncs, myfuncs, tf_myclasses
from sklearn import metrics


class RegressorEvaluator:
    def __init__(self, model, train_ds, val_ds=None):
        self.model = model
        self.train_ds = train_ds
        self.val_ds = val_ds

    def evaluate_train_classifier(self):
        train_target_data, train_pred = (
            tf_myfuncs.get_full_target_and_pred_for_regression_model(
                self.model, self.train_ds
            )
        )
        val_target_data, val_pred = (
            tf_myfuncs.get_full_target_and_pred_for_regression_model(
                self.model, self.val_ds
            )
        )

        # RMSE
        train_rmse = np.sqrt(metrics.mean_squared_error(train_target_data, train_pred))
        val_rmse = np.sqrt(metrics.mean_squared_error(val_target_data, val_pred))

        # MAE
        train_mae = metrics.mean_absolute_error(train_target_data, train_pred)
        val_mae = metrics.mean_absolute_error(val_target_data, val_pred)

        model_result_text = f"Train RMSE: {train_rmse}\n"
        model_result_text += f"Val RMSE: {val_rmse}\n"
        model_result_text += f"Train MAE: {train_mae}\n"
        model_result_text += f"Val MAE: {val_mae}"

        return model_result_text

    def evaluate_test_classifier(self):
        test_target_data, test_pred = (
            tf_myfuncs.get_full_target_and_pred_for_regression_model(
                self.model, self.train_ds
            )
        )

        # RMSE
        test_rmse = np.sqrt(metrics.mean_squared_error(test_target_data, test_pred))

        # MAE
        test_mae = metrics.mean_absolute_error(test_target_data, test_pred)

        model_result_text = f"Test RMSE: {test_rmse}\n"
        model_result_text += f"Test MAE: {test_mae}\n"

        return model_result_text


class MachineTranslationEvaluator:
    """Dùng để đánh giá tổng quát bài toán Dịch Máy <br>
    Đánh giá chỉ số BLEU

    Args:
        model (_type_): _description_
        train_ds (_type_): _description_
        val_ds (_type_, optional): Nếu None thì chỉ đánh giá trên 1 tập thôi (tập test). Defaults to None.
    """

    def __init__(self, model, train_ds, val_ds=None):
        self.model = model
        self.train_ds = train_ds
        self.val_ds = val_ds

    def evaluate_train_classifier(self):
        # Get thực tế và dự đoán
        train_target, train_pred = (
            tf_myfuncs.get_full_target_and_pred_for_softmax_model(
                self.model, self.train_ds
            )
        )
        val_target, val_pred = tf_myfuncs.get_full_target_and_pred_for_softmax_model(
            self.model, self.val_ds
        )

        # Đánh giá: bleu + ...
        train_bleu = np.mean(
            tf_myclasses.ListBleuGetter(train_target, train_pred).next()
        )
        val_bleu = np.mean(tf_myclasses.ListBleuGetter(val_target, val_pred).next())

        result = f"Train BLEU: {train_bleu}\n"
        result += f"Val BLEU: {val_bleu}\n"

        return result

    def evaluate_test_classifier(self):
        # Get thực tế và dự đoán
        test_target, test_pred = tf_myfuncs.get_full_target_and_pred_for_softmax_model(
            self.model, self.train_ds
        )

        # Đánh giá: bleu + ...
        test_bleu = np.mean(tf_myclasses.ListBleuGetter(test_target, test_pred).next())

        result = f"Test BLEU: {test_bleu}\n"

        return result

    def evaluate(self):
        return (
            self.evaluate_train_classifier()
            if self.val_ds is not None
            else self.evaluate_test_classifier()
        )
