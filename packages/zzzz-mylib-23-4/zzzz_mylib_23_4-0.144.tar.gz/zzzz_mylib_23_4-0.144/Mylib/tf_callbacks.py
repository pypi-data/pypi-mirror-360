import tensorflow as tf
from Mylib import myfuncs
import numpy as np
import pandas as pd
import time


class CustomisedModelCheckpoint(tf.keras.callbacks.Callback):
    """Callback để lưu model tốt nhất theo từng epoch

    Attributes:
        filepath (str): đường dẫn đến best model
        scoring_path (str): đường dẫn lưu các scoring ứng với best model tìm được
        monitor (str): chỉ số đánh giá (đánh giá theo **val**), *vd:* val_accuracy, val_loss , ...
        indicator (str): chỉ tiêu



    Examples:
        Với **monitor = val_accuracy và indicator = 0.99**

        Tìm model thỏa val_accuracy > 0.99 và train_accuracy > 0.99 (1) và val_accuracy là lớn nhất trong số đó

        Nếu không thỏa (1) thì lấy theo val_accuracy lớn nhất

    """

    SCORINGS_PREFER_MININUM = ["loss", "mse", "mae"]
    SCORINGS_PREFER_MAXIMUM = ["accuracy", "roc_auc"]

    def __init__(
        self, filepath: str, scoring_path: str, monitor: str, indicator: float
    ):
        super().__init__()
        self.filepath = filepath
        self.scoring_path = scoring_path
        self.monitor = monitor
        self.indicator = indicator

    def on_train_begin(self, logs=None):
        # Nếu thuộc SCORINGS_PREFER_MININUM thì lấy âm đẩy về bài toán tìm giá trị lớn nhất
        self.sign_for_score = None
        if self.monitor in self.SCORINGS_PREFER_MAXIMUM:
            self.sign_for_score = 1
        elif self.monitor in self.SCORINGS_PREFER_MININUM:
            self.sign_for_score = -1
        else:
            raise ValueError(f"Chưa định nghĩa cho {self.monitor}")

        self.per_epoch_val_scores = []
        self.per_epoch_train_scores = []
        self.models = []

    def on_epoch_end(self, epoch, logs=None):
        self.models.append(self.model)
        self.per_epoch_val_scores.append(logs.get(self.monitor) * self.sign_for_score)
        self.per_epoch_train_scores.append(
            logs.get(self.monitor[4:]) * self.sign_for_score
        )

    def on_train_end(self, logs=None):
        # Tìm model tốt nhất
        self.per_epoch_val_scores = np.asarray(self.per_epoch_val_scores)
        self.per_epoch_train_scores = np.asarray(self.per_epoch_train_scores)

        # Tìm các model thỏa train_scoring, val_scoring > target (đề ra)
        indexs_good_model = np.where(
            (self.per_epoch_val_scores > self.indicator)
            & (self.per_epoch_train_scores > self.indicator)
        )[0]

        # Tìm model tốt nhất
        index_best_model = None
        if (
            len(indexs_good_model) == 0
        ):  # Nếu ko có model nào đạt chỉ tiêu thì lấy cái tốt nhất
            index_best_model = np.argmax(self.per_epoch_val_scores)
        else:
            val_series = pd.Series(
                self.per_epoch_val_scores[indexs_good_model], index=indexs_good_model
            )
            index_best_model = val_series.idxmax()

        # TODO: d
        print(f"index best model thông qua modelcheckpoint = {index_best_model}")
        # d

        best_model = self.models[index_best_model]
        best_model_train_scoring = self.per_epoch_train_scores[index_best_model]
        best_model_val_scoring = self.per_epoch_val_scores[index_best_model]

        # Lưu model tốt nhất và train,val scoring tương ứng
        best_model.save(self.filepath)
        myfuncs.save_python_object(
            self.scoring_path, (best_model_train_scoring, best_model_val_scoring)
        )


class CustomisedModelCheckpoint(tf.keras.callbacks.Callback):
    """Customize từ ModelCheckpoint trong tf.keras.callbacks <br>
    Mục đích: Tìm model tốt nhất theo epoch, cập nhật model tốt nhất và lưu kết quả tương ứng trong quá trình train model <br>

    Attributes:
        model_training_result_path (_type_): kết quả train model tốt nhất theo epoch
        model_path (_type_): đường dẫn đến model tốt nhất trong quá trình train model
        result_path (_type_): kết quả tương ứng với model tốt nhất trong quá trình train model
        sign_for_val_scoring_find_best_model (_type_): dấu (-1 hoặc 1), hỗ trợ tìm model tốt nhất theo epoch và tìm model tốt nhất trong quá trình train model
        Lí do: với các chỉ số ưu tiên nhỏ nhất (mse, mae, ...) thì nhân với -1 để chuyển về logic tìm lớn nhất giống như các chỉ số ưu tiên lớn nhất (accuracy, roc_auc, ...) <br>
        model_saving_val_scoring_limit (_type_): mức tối thiểu của val scoring để lưu model
        best_val_scoring (_type_): chỉ số val scoring tốt nhất hiện tại
        scoring (_type_): chỉ số, vd: mse, mae, ....
        param (_type_): tham số của model
    """

    def __init__(
        self,
        model_training_result_path,
        model_path,
        result_path,
        sign_for_val_scoring_find_best_model,
        model_saving_val_scoring_limit,
        best_val_scoring_path,
        scoring,
        param,
    ):
        super().__init__()
        self.model_training_result_path = model_training_result_path
        self.model_path = model_path
        self.result_path = result_path
        self.sign_for_val_scoring_find_best_model = sign_for_val_scoring_find_best_model
        self.model_saving_val_scoring_limit = model_saving_val_scoring_limit
        self.best_val_scoring_path = best_val_scoring_path
        self.scoring = scoring
        self.param = param

    def on_train_begin(self, logs=None):
        self.start_time = time.time()  # Bắt đầu tính thời gian training model
        self.train_scorings = []
        self.val_scorings = []
        self.model_weights = []

    def on_epoch_end(self, epoch, logs=None):
        self.train_scorings.append(
            logs.get(self.scoring) * self.sign_for_val_scoring_find_best_model
        )
        self.val_scorings.append(
            logs.get(f"val_{self.scoring}") * self.sign_for_val_scoring_find_best_model
        )
        self.model_weights.append(self.model.get_weights())

    def on_train_end(self, logs=None):
        # Thời gian training model
        training_time = (
            time.time() - self.start_time
        )  # Thời gian training model kết thúc tại đây

        # Tìm model ứng với val scoring tốt nhất
        index_best_model = np.argmax(self.val_scorings)
        best_model_val_scoring = np.abs(self.val_scorings[index_best_model])
        best_model_train_scoring = np.abs(self.train_scorings[index_best_model])
        best_weights = self.model_weights[index_best_model]
        self.model.set_weights(best_weights)
        best_model_num_epochs_before_stopping = len(self.train_scorings)

        # Lưu lại kết quả
        myfuncs.save_python_object(
            self.model_training_result_path,
            (
                best_model_val_scoring,
                best_model_train_scoring,
                training_time,
                best_model_num_epochs_before_stopping,
            ),
        )

        # Lưu model nếu val scoring trong quá trình train model được cải thiện
        best_model_val_scoring_for_saving = (
            best_model_val_scoring * self.sign_for_val_scoring_find_best_model
        )
        best_val_scoring = myfuncs.load_python_object(self.best_val_scoring_path)

        if best_model_val_scoring_for_saving > best_val_scoring:
            best_val_scoring = best_model_val_scoring_for_saving
            myfuncs.save_python_object(self.best_val_scoring_path, best_val_scoring)

            # Lưu kết quả tương ứng
            myfuncs.save_python_object(
                self.result_path,
                (
                    self.param,
                    best_model_val_scoring,
                    best_model_train_scoring,
                    training_time,
                    best_model_num_epochs_before_stopping,
                ),
            )

            # Lưu  model
            if best_model_val_scoring_for_saving > self.model_saving_val_scoring_limit:
                self.model.save(self.model_path)
