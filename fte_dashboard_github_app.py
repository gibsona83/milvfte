
import streamlit as st
import pandas as pd
import os
from datetime import datetime
import plotly.express as px

st.set_page_config(page_title="FTE Optimization Dashboard", layout="wide")

# --- Sidebar Navigation ---
page = st.sidebar.radio("Navigate", ["📊 Overview", "✍️ Optimal FTE Input", "📅 Forecast Tracker"])

# --- File paths ---
optimal_path = "data/optimal_fte.xlsx"
forecast_path = "data/fte_forecast.xlsx"
bri_data_path = "data/FTE_analysis_AG.xlsx"

# --- Load Data Functions ---
@st.cache_data
def load_actual_fte_data():
    if os.path.exists(bri_data_path):
        xls = pd.ExcelFile(bri_data_path)
        df = xls.parse("FYTD 25-26- Cumulative Summary")
        df = df[["Section", "Rolling 12month FTE"]].dropna()
        return df.groupby("Section")["Rolling 12month FTE"].sum().reset_index()
    else:
        return pd.DataFrame(columns=["Section", "Rolling 12month FTE"])

@st.cache_data
def load_optimal_fte():
    if os.path.exists(optimal_path):
        return pd.read_excel(optimal_path)
    else:
        return pd.DataFrame(columns=["Section", "Optimal FTE"])

@st.cache_data
def load_forecast_data():
    if os.path.exists(forecast_path):
        return pd.read_excel(forecast_path)
    else:
        return pd.DataFrame(columns=["Radiologist", "Type", "Effective Date", "FTE Change", "Section"])

# --- Pages ---
if page == "📊 Overview":
    st.title("📊 Actual vs Optimal FTE Overview")

    actual_df = load_actual_fte_data()
    optimal_df = load_optimal_fte()

    if actual_df.empty:
        st.warning("Upload 'FTE_analysis_AG.xlsx' to the /data folder.")
    else:
        merged = pd.merge(actual_df, optimal_df, on="Section", how="left")

        st.subheader("Actual vs Optimal FTE - Bar Chart")
        fig = px.bar(
            merged.melt(id_vars="Section", value_vars=["Rolling 12month FTE", "Optimal FTE"]),
            x="Section",
            y="value",
            color="variable",
            barmode="group",
            labels={"value": "FTE", "variable": "FTE Type"},
            title="Actual vs Optimal FTE by Section"
        )
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)

elif page == "✍️ Optimal FTE Input":
    st.title("✍️ Enter/Edit Optimal FTE by Section")

    optimal_df = load_optimal_fte()
    edited_optimal = st.data_editor(optimal_df, num_rows="dynamic", key="optimal_editor")

    if st.button("💾 Save Optimal FTE"):
        edited_optimal.to_excel(optimal_path, index=False)
        st.success("✅ Optimal FTE values saved for all users.")

elif page == "📅 Forecast Tracker":
    st.title("📅 FTE Forecast Input & Tracker")

    forecast_df = load_forecast_data()
    edited_forecast = st.data_editor(forecast_df, num_rows="dynamic", key="forecast_editor")

    if st.button("💾 Save Forecast Data"):
        edited_forecast.to_excel(forecast_path, index=False)
        st.success("✅ Forecast data saved for all users.")
