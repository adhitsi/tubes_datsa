import pandas as pd
import joblib
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from utils.feature_engineering import FeatureEngineer

# ==========================
# LOAD DATA
# ==========================
df = pd.read_csv(r'tubes_datsa\data\insurance.csv')

X = df.drop('charges', axis=1)
y = df['charges']

# ==========================
# KOLOM SETELAH FE
# ==========================
cat_cols = ['sex', 'smoker', 'region', 'bmi_category', 'age_group']
num_cols = ['age', 'bmi', 'children', 'bmi_smoker', 'high_risk']

preprocessor = ColumnTransformer([
    ('cat', OneHotEncoder(drop='first'), cat_cols),
    ('num', 'passthrough', num_cols)
])

# ==========================
# PIPELINE FULL
# ==========================
model = Pipeline([
    ('fe', FeatureEngineer()), 
    ('prep', preprocessor),
    ('rf', RandomForestRegressor(
        n_estimators=100,
        max_depth=10,
        min_samples_leaf=2,
        min_samples_split=5,
        random_state=42
    ))
])

# ==========================
# TRAIN
# ==========================
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

model.fit(X_train, y_train)

# ==========================
# SAVE MODEL
# ==========================
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
MODEL_PATH = os.path.join(BASE_DIR, 'model', 'model_rf.pkl')

os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)

joblib.dump(model, MODEL_PATH)


MODEL_PATH = os.path.join(BASE_DIR, 'model', 'model_rf.pkl')
