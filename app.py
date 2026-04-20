import streamlit as st
import pandas as pd
import joblib

# ======================
# LOAD PIPELINE MODEL
# ======================
model = joblib.load("model/model_rf.pkl")

st.title("💰 MediPredict")

# ======================
# INPUT USER
# ======================
age = st.number_input("Age", 1, 100, 25)
bmi = st.number_input("BMI", 10.0, 60.0, 25.0)
children = st.number_input("Children", 0, 10, 0)

sex = st.selectbox("Sex", ["male", "female"])
smoker = st.selectbox("Smoker", ["yes", "no"])
region = st.selectbox("Region", ["northeast", "northwest", "southeast", "southwest"])

# ======================
# DATAFRAME (TIDAK PERLU ENCODING MANUAL)
# ======================
input_data = pd.DataFrame([{
    "age": age,
    "bmi": bmi,
    "children": children,
    "sex": sex,
    "smoker": smoker,
    "region": region
}])

# ======================
# PREDICTION
# ======================
if st.button("Predict"):
    try:
        pred = model.predict(input_data)[0]

        st.success(f"💵 Prediksi biaya: ${pred:,.2f}")

        st.info(f"""
        📊 Range:
        - Lower: ${pred * 0.8:,.2f}
        - Upper: ${pred * 1.2:,.2f}
        """)

    except Exception as e:
        st.error(f"Error: {str(e)}")