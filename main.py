import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

from health_analyzer import HealthAnalyzer


def generate_sample_data(n=500, seed=42):
    rng = np.random.default_rng(seed)
    start = datetime(2020, 1, 1)
    admission_dates = [start + timedelta(days=int(x)) for x in rng.integers(0, 1000, size=n)]
    discharge_offsets = rng.integers(0, 30, size=n)
    discharge_dates = [d + timedelta(days=int(x)) for d, x in zip(admission_dates, discharge_offsets)]
    outcomes = rng.choice(["discharge", "dama", "death"], size=n, p=[0.85, 0.1, 0.05])
    ages = rng.integers(0, 100, size=n)
    genders = rng.choice(["Male", "Female", "Other"], size=n, p=[0.48, 0.5, 0.02])
    departments = rng.choice(["Cardiology", "Oncology", "Emergency", "Pediatrics", "General"], size=n)
    satisfaction = rng.integers(1, 6, size=n)
    diagnosis = rng.choice(["Flu", "COVID-19", "Fracture", "Cancer", "Infection"], size=n)

    df = pd.DataFrame({
        "patient_id": [f"P{i:05d}" for i in range(n)],
        "admission_date": admission_dates,
        "discharge_date": discharge_dates,
        "outcome": outcomes,
        "age": ages,
        "gender": genders,
        "department": departments,
        "satisfaction": satisfaction,
        "diagnosis": diagnosis,
    })
    return df


st.set_page_config(page_title="Public Health Dashboard", layout="wide")

st.title("Public Health: Patient & Hospital Data Dashboard")

st.markdown("Upload a CSV of hospital patient records, or use generated sample data.")

uploaded = st.file_uploader("Upload CSV", type=["csv"] )
if uploaded is not None:
    df = pd.read_csv(uploaded)
else:
    if st.checkbox("Use sample demo dataset", value=True):
        df = generate_sample_data()
    else:
        st.info("Upload a CSV or check the sample dataset box.")
        st.stop()

ha = HealthAnalyzer(df)
ha.clean_data()

# Sidebar filters
st.sidebar.header("Filters")
age_min, age_max = int(ha.df["age"].min()), int(ha.df["age"].max()) if "age" in ha.df.columns else (0,100)
age_range = st.sidebar.slider("Age range", min_value=0, max_value=120, value=(age_min, min(age_max,120)))
selected_genders = st.sidebar.multiselect("Gender", options=sorted(ha.df["gender"].unique()), default=sorted(ha.df["gender"].unique()))
selected_departments = st.sidebar.multiselect("Department", options=sorted(ha.df["department"].unique()), default=sorted(ha.df["department"].unique()))

df_filtered = ha.df[(ha.df["age"] >= age_range[0]) & (ha.df["age"] <= age_range[1]) & ha.df["gender"].isin(selected_genders) & ha.df["department"].isin(selected_departments)]

st.header("Key Questions")
col1, col2 = st.columns(2)
with col1:
    st.subheader("Outcome distribution by age")
    chart = HealthAnalyzer(df_filtered).plot_outcomes_by_age_hist(age_bin_width=10)
    if chart is not None:
        st.altair_chart(chart, use_container_width=True)
    else:
        st.info("Insufficient data for this chart.")

with col2:
    st.subheader("Admissions over time")
    chart2 = HealthAnalyzer(df_filtered).plot_admissions_over_time(freq="M")
    if chart2 is not None:
        st.altair_chart(chart2, use_container_width=True)
    else:
        st.info("No admission_date available.")

st.subheader("Average service satisfaction by department")
chart3 = HealthAnalyzer(df_filtered).plot_satisfaction_by_department()
if chart3 is not None:
    st.altair_chart(chart3, use_container_width=True)
else:
    st.info("No satisfaction data available.")

st.subheader("Summary statistics")
counts, pct = HealthAnalyzer(df_filtered).summarize_outcomes()
st.write("Outcome counts:")
st.dataframe(pd.concat([counts.rename("count"), pct.rename("percent")], axis=1))

st.markdown("---")
st.subheader("Data sample")
st.dataframe(df_filtered.head(50))