import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin

class FeatureEngineer(BaseEstimator, TransformerMixin):
    def fit(self, X, y=None):
        return self

    def transform(self, X):
        X = X.copy()

        X['bmi_smoker'] = X['bmi'] * (X['smoker'] == 'yes').astype(int)

        X['bmi_category'] = pd.cut(X['bmi'],
            bins=[0, 18.5, 25, 30, 100],
            labels=['underweight','normal','overweight','obese']
        )

        X['age_group'] = pd.cut(X['age'],
            bins=[0, 25, 40, 60, 100],
            labels=['young','adult','middle','senior']
        )

        X['high_risk'] = (
            (X['smoker'] == 'yes') & (X['bmi'] > 30)
        ).astype(int)

        return X