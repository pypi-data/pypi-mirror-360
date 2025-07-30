from sklearn.base import BaseEstimator, ClassifierMixin, RegressorMixin
from sklearn.ensemble import BaggingClassifier, RandomForestClassifier, VotingClassifier
from sklearn.linear_model import LogisticRegression
from xgboost import XGBClassifier


class LRBaggingClassifier(BaseEstimator, ClassifierMixin):
    def __init__(
        self,
        penalty,
        solver,
        C,
        l1_ratio,
        max_iter,
        n_estimators,
        max_samples,
        max_features,
        warm_start=True,
    ):
        lr = LogisticRegression(
            penalty=penalty,
            solver=solver,
            C=C,
            l1_ratio=l1_ratio,
            max_iter=max_iter,
            warm_start=warm_start,
        )
        self.model = BaggingClassifier(
            estimator=lr,
            n_estimators=n_estimators,
            max_samples=max_samples,
            max_features=max_features,
        )

    def fit(self, X, y):
        self.model.fit(X, y)

        self.is_fitted_ = True
        return self

    def predict(self, X):
        return self.model.predict(X)

    def predict_proba(self, X):
        return self.model.predict_proba(X)


class LR_RF_XGB_VotingClassifier(BaseEstimator, ClassifierMixin):
    def __init__(
        self,
        lr_penalty,
        lr_solver,
        lr_C,
        lr_l1_ratio,
        lr_max_iter,
        rf_n_estimators,
        rf_max_depth,
        rf_max_samples,
        rf_max_features,
        xgb_n_estimators,
        xgb_max_depth,
        xgb_learning_rate,
        xgb_subsample,
        xgb_colsample_bytree,
        xgb_reg_alpha,
        xgb_reg_lambda,
    ):
        lr = LogisticRegression(
            penalty=lr_penalty,
            solver=lr_solver,
            C=lr_C,
            l1_ratio=lr_l1_ratio,
            max_iter=lr_max_iter,
        )
        rf = RandomForestClassifier(
            n_estimators=rf_n_estimators,
            max_depth=rf_max_depth,
            max_samples=rf_max_samples,
            max_features=rf_max_features,
        )
        xgb = XGBClassifier(
            n_estimators=xgb_n_estimators,
            max_depth=xgb_max_depth,
            learning_rate=xgb_learning_rate,
            subsample=xgb_subsample,
            colsample_bytree=xgb_colsample_bytree,
            reg_alpha=xgb_reg_alpha,
            reg_lambda=xgb_reg_lambda,
        )
        self.model = VotingClassifier(
            estimators=[("lr", lr), ("rf", rf), ("xgb", xgb)], voting="soft"
        )

    def fit(self, X, y):
        self.model.fit(X, y)

        self.is_fitted_ = True
        return self

    def predict(self, X):
        return self.model.predict(X)

    def predict_proba(self, X):
        return self.model.predict_proba(X)
