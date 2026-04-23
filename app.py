import streamlit as st
import pandas as pd
import joblib
import numpy as np
import matplotlib.pyplot as plt
from io import BytesIO

from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split

# ======================
# CONFIG
# ======================
st.set_page_config(page_title="MediPrediction", layout="wide")

# ======================
# CSS
# ======================
st.markdown("""
<style>
.stApp {background: linear-gradient(135deg, #0f172a, #1e293b); color: white;}
.card {background: #1e293b; padding: 20px; border-radius: 15px; margin-bottom: 20px;}
.metric {font-size: 22px; font-weight: bold; color: #22c55e;}
h1, h2, h3 {color: #38bdf8;}
</style>
""", unsafe_allow_html=True)

# ======================
# NAVIGATION
# ======================
page = st.sidebar.radio("MediPrediction", ["Dashboard", "Prediksi", "Laporan"])

# ======================
# MODEL LOAD
# ======================
model = joblib.load("model/model_rf.pkl")

# ======================
# DASHBOARD
# ======================
if page == "Dashboard":
    st.title("📊 Dashboard Analisis")

    uploaded_file = st.file_uploader("Upload CSV", type=["csv"])

    if uploaded_file:
        df = pd.read_csv(uploaded_file)

        required_cols = ["age", "bmi", "children", "sex", "smoker", "region", "charges"]

        if not all(col in df.columns for col in required_cols):
            st.error("Format CSV tidak sesuai!")
        else:
            st.dataframe(df.head())

            # ======================
            # METRIK
            # ======================
            col1, col2, col3 = st.columns(3)
            col1.metric("Mean", f"${df['charges'].mean():,.2f}")
            col2.metric("Min", f"${df['charges'].min():,.2f}")
            col3.metric("Max", f"${df['charges'].max():,.2f}")

            # ======================
            # VISUALISASI
            # ======================
            fig, ax = plt.subplots()
            ax.scatter(df["bmi"], df["charges"])
            ax.set_xlabel("BMI")
            ax.set_ylabel("Charges")
            st.pyplot(fig)

            # ======================
            # 🚬 FILTER SMOKER
            # ======================
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.subheader("🚬 Perokok vs Non-Perokok")

            smoker_filter = st.selectbox("Filter", ["all", "yes", "no"])

            if smoker_filter != "all":
                df_filtered = df[df["smoker"] == smoker_filter]
            else:
                df_filtered = df

            st.dataframe(df_filtered)
            st.write("Rata-rata biaya:", df_filtered["charges"].mean())

            st.markdown('</div>', unsafe_allow_html=True)

    else:
        st.info("Silakan upload dataset terlebih dahulu")
# ======================
# PREDIKSI
# ======================
elif page == "Prediksi":
    st.title("🔮 Prediksi Biaya")

    col1, col2 = st.columns(2)

    with col1:
        age = st.number_input("Age", 1, 100, 25)
        bmi = st.number_input("BMI", 10.0, 60.0, 25.0)
        children = st.number_input("Children", 0, 10, 0)

    with col2:
        sex = st.selectbox("Sex", ["male", "female"])
        smoker = st.selectbox("Smoker", ["yes", "no"])
        region = st.selectbox("Region", ["northeast", "northwest", "southeast", "southwest"])

    input_data = pd.DataFrame([{
        "age": age,
        "bmi": bmi,
        "children": children,
        "sex": sex,
        "smoker": smoker,
        "region": region
    }])

    if st.button("Predict"):
        pred = model.predict(input_data)[0]
        st.success(f"Prediksi: ${pred:,.2f}")

# ======================
# LAPORAN (MULTI MODEL)
# ======================
elif page == "Laporan":
    st.title("📄 Laporan Perbandingan Model")

    uploaded_file = st.file_uploader("Upload CSV untuk Training", type=["csv"])

    if uploaded_file:
        df = pd.read_csv(uploaded_file)

        X = df.drop("charges", axis=1)
        y = df["charges"]

        X = pd.get_dummies(X, drop_first=True)

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

        models = {
            "Linear Regression": LinearRegression(),
            "Decision Tree": DecisionTreeRegressor(),
            "Random Forest": RandomForestRegressor()
        }

        results = []

        for name, m in models.items():
            m.fit(X_train, y_train)
            pred = m.predict(X_test)

            mae = mean_absolute_error(y_test, pred)
            mse = mean_squared_error(y_test, pred)
            rmse = np.sqrt(mse)
            r2 = r2_score(y_test, pred)

            results.append([name, mae, mse, rmse, r2])

        df_results = pd.DataFrame(results, columns=["Model", "MAE", "MSE", "RMSE", "R2"])

        st.dataframe(df_results)

        # Best model
        best_model = df_results.loc[df_results['R2'].idxmax()]
        st.success(f"Model terbaik: {best_model['Model']}")

        # Plot
        fig2, ax2 = plt.subplots()
        ax2.bar(df_results["Model"], df_results["R2"])
        ax2.set_title("Perbandingan R2")
        st.pyplot(fig2)

        # Export
        def to_excel(data):
            output = BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                data.to_excel(writer, index=False)
            return output.getvalue()

        excel = to_excel(df_results)

        st.download_button("Download Laporan", data=excel, file_name="laporan.xlsx")
