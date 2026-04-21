import streamlit as st
import pandas as pd
import joblib
import numpy as np
import matplotlib.pyplot as plt
from io import BytesIO

# ======================
# CUSTOM CSS (MODERN UI)
# ======================
st.set_page_config(page_title="MediPrediction", layout="wide")

st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #0f172a, #1e293b);
    color: white;
}
.card {
    background: #1e293b;
    padding: 20px;
    border-radius: 15px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.3);
    margin-bottom: 20px;
}
.metric {
    font-size: 22px;
    font-weight: bold;
    color: #22c55e;
}
h1, h2, h3 {
    color: #38bdf8;
}
.stButton>button {
    background: linear-gradient(90deg, #06b6d4, #3b82f6);
    color: white;
    border-radius: 10px;
}
</style>
""", unsafe_allow_html=True)

# ======================
# LOAD MODEL
# ======================
model = joblib.load("model/model_rf.pkl")

# ======================
# HEADER
# ======================
st.markdown("""
<div class="card">
    <h1>💰 MediPrediction Dashboard</h1>
    <p>Analisis & Prediksi Biaya Asuransi Kesehatan</p>
</div>
""", unsafe_allow_html=True)

# =====================================================
# 1. UPLOAD CSV
# =====================================================
st.header("📂 Upload Dataset")

uploaded_file = st.file_uploader("Upload file CSV", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("📄 Preview Data")
    st.dataframe(df.head())
    st.markdown('</div>', unsafe_allow_html=True)

    # =====================================================
    # 2. STATISTIK
    # =====================================================
    st.subheader("📊 Statistik Biaya")

    col1, col2, col3 = st.columns(3)

    col1.markdown(f'<div class="card"><p>Mean</p><p class="metric">${df["charges"].mean():,.2f}</p></div>', unsafe_allow_html=True)
    col2.markdown(f'<div class="card"><p>Min</p><p class="metric">${df["charges"].min():,.2f}</p></div>', unsafe_allow_html=True)
    col3.markdown(f'<div class="card"><p>Max</p><p class="metric">${df["charges"].max():,.2f}</p></div>', unsafe_allow_html=True)

    # =====================================================
    # 3. VISUALISASI
    # =====================================================
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("📈 BMI vs Charges")

    fig, ax = plt.subplots()
    ax.scatter(df["bmi"], df["charges"])
    ax.set_xlabel("BMI")
    ax.set_ylabel("Charges")

    st.pyplot(fig)
    st.markdown('</div>', unsafe_allow_html=True)

    # =====================================================
    # 4. FILTER
    # =====================================================
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

    # =====================================================
    # 5. EXPORT
    # =====================================================
    st.subheader("📥 Export Data")

    def to_excel(data):
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            data.to_excel(writer, index=False)
        return output.getvalue()

    excel_data = to_excel(df_filtered)

    st.download_button(
        label="Download Excel",
        data=excel_data,
        file_name="hasil_analisis.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

# =====================================================
# PREDIKSI
# =====================================================
st.header("🔮 Prediksi Biaya")

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
    try:
        pred = model.predict(input_data)[0]

        st.markdown(f"""
        <div class="card">
            <h2>💵 Prediksi Biaya</h2>
            <p class="metric">${pred:,.2f}</p>
        </div>
        """, unsafe_allow_html=True)

        st.info(f"""
        📊 Range:
        - Lower: ${pred * 0.8:,.2f}
        - Upper: ${pred * 1.2:,.2f}
        """)

        # =========================================
        # FEATURE IMPORTANCE
        # =========================================
        st.subheader("📊 Faktor Model")

        rf = model.named_steps['rf']
        prep = model.named_steps['prep']

        cat_features = prep.named_transformers_['cat'].get_feature_names_out()
        num_features = prep.transformers_[1][2]

        feature_names = list(cat_features) + list(num_features)
        importances = rf.feature_importances_

        sorted_idx = np.argsort(importances)[::-1]

        top_n = 5
        top_features = [feature_names[i] for i in sorted_idx[:top_n]]
        top_importances = importances[sorted_idx[:top_n]]

        fig2, ax2 = plt.subplots()
        ax2.barh(top_features[::-1], top_importances[::-1])
        ax2.set_title("Top 5 Faktor")

        st.pyplot(fig2)

        df_importance = pd.DataFrame({
            "Feature": top_features,
            "Importance": top_importances
        })

        st.dataframe(df_importance)

    except Exception as e:
        st.error(f"Error: {str(e)}")