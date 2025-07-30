from sklearn.linear_model import LogisticRegression, ElasticNet
from sklearn.ensemble import (
    RandomForestClassifier,
    RandomForestRegressor,
    ExtraTreesClassifier,
    ExtraTreesRegressor,
)
from xgboost import XGBClassifier, XGBRegressor
from lightgbm import LGBMClassifier, LGBMRegressor
import pandas as pd
from Mylib.sk_classes import LRBaggingClassifier, LR_RF_XGB_VotingClassifier


class ObjectCreatorFromDict:
    """Create layer từ param và text đại diện cho layer đó <br>

    Examples:
    ```
    param = {
        'patience': 10,
        'min_delta': 0.001,
        'learning_rate': 0.01,
        'layer1__start_units': 8,
        'layer1__num_layers': 4,
        'layer1__name': 'DenseBatchNormalizationTuner',
        'layer0__start_units': 16,
        'layer0__num_layers': 5,
        'layer0__name': 'DenseBatchNormalizationDropoutTuner',
        'layer0__dropout_rate': 0.5,
        'epochs': 30
    }
    layer_text = 'layer0'

    ```
    Khi đó tạo layer từ các key có chứa 'layer0' là: start_units, num_layers, name, dropout_rate

    Args:
        param (_type_): dict
        layer_text (_type_): text thể hiện cho layer cần tạo
    """

    def __init__(self, param, layer_text):
        self.param = param
        self.layer_text = layer_text

    def next(self):
        # Get param ứng với layer_text
        keys = pd.Series(self.param.keys())
        values = pd.Series(self.param.values())

        filter_mask = keys.str.startswith(self.layer_text)
        keys = keys[filter_mask]
        values = values[filter_mask]

        keys = keys.apply(self.get_param_name)
        layer_param = dict(zip(keys, values))

        # Tạo class
        class_name = layer_param.pop("name")
        ClassName = globals()[class_name]

        # Tạo object
        layer = ClassName(**layer_param)
        return layer

    def get_param_name(self, key):
        parts = key.split("__", 1)
        return parts[1]
