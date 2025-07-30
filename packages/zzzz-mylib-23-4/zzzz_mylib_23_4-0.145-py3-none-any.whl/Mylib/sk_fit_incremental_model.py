from xgboost import XGBClassifier, XGBRegressor
from lightgbm import LGBMClassifier, LGBMRegressor
from sklearn.ensemble import (
    RandomForestClassifier,
    ExtraTreesClassifier,
    RandomForestRegressor,
    ExtraTreesRegressor,
)


def fit_model_incremental_learning(model, feature, target):
    """Fit model với cài đặt incremental learning, một số model đặc biệt như XGBClassifier, LGBMClassifier, CustomStackingClassifier, ...

    Args:
        model (_type_): _description_
        feature (_type_): _description_
        target (_type_): _description_
    """
    # 2 model không nằm trong thư viện sklearn
    if isinstance(model, (XGBClassifier, XGBRegressor)):
        model.fit(feature, target, xgb_model=model.get_booster())
        return

    if isinstance(model, (LGBMClassifier, LGBMRegressor)):
        model.fit(feature, target, init_model=model.booster_)

        return

    # Mấy này có warm_start = True nhưng phải tăng số cây lên thì mới học tiếp được
    if isinstance(
        model,
        (
            RandomForestClassifier,
            ExtraTreesClassifier,
            RandomForestRegressor,
            ExtraTreesRegressor,
        ),
    ):
        model.n_estimators += 50
        model.fit(feature, target)

        return

    # Các model khác có tham số warm_start = True, vd: LogisticRegression, .... là đủ rồi
    model.fit(feature, target)
