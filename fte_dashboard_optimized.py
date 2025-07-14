
import streamlit as st
import pandas as pd
import plotly.express as px
import os

st.set_page_config(page_title="FTE Optimization Dashboard", layout="wide")

# File paths
BASENAME_ACTUAL = "FTE_analysis_AG.xlsx"
BASENAME_OPTIMAL = "optimal_fte.xlsx"
BASENAME_FORECAST = "fte_forecast.xlsx"

# --- Efficient Caching for Data Loading ---
@st.cache_data
def load_excel_data(filename, sheet):
    if os.path.exists(filename):
        try:
            df = pd.read_excel(filename, sheet_name=sheet)
            return df
        except Exception as e:
            st.error(f"Failed to load {sheet} from {filename}: {e}")
    return pd.DataFrame()

@st.cache_data
def load_file_or_blank(filename, columns):
    if os.path.exists(filename):
        return pd.read_excel(filename)
    else:
        return pd.DataFrame(columns=columns)

# Loaders
def get_actual_fte():
    df = load_excel_data(BASENAME_ACTUAL, "FYTD 25-26- Cumulative Summary")
    if "Section" in df and "Rolling 12month FTE" in df:
        df = df[["Section", "Rolling 12month FTE"]].dropna()
        return df.groupby("Section", as_index=False)["Rolling 12month FTE"].sum()
    return pd.DataFrame(columns=["Section", "Rolling 12month FTE"])

def get_optimal_fte():
    return load_file_or_blank(BASENAME_OPTIMAL, ["Section", "Optimal FTE"])

def get_forecast_data():
    return load_file_or_blank(BASENAME_FORECAST, ["Radiologist", "Type", "Effective Date", "FTE Change", "Section"])

# --- Sidebar Navigation ---
page = st.sidebar.radio("Navigate", ["📊 Overview", "✍️ Optimal FTE Input", "📅 Forecast Tracker"])

# --- Pages ---
if page == "📊 Overview":
    st.title("📊 Actual vs Optimal FTE Overview")

    actual_df = get_actual_fte()
    optimal_df = get_optimal_fte()

    if actual_df.empty:
        st.warning("Please upload 'FTE_analysis_AG.xlsx' to the main folder.")
    else:
        merged = pd.merge(actual_df, optimal_df, on="Section", how="left")
        melted = merged.melt(id_vars="Section", value_vars=["Rolling 12month FTE", "Optimal FTE"],
                             var_name="FTE Type", value_name="FTE")

        fig = px.bar(melted, x="Section", y="FTE", color="FTE Type",
                     barmode="group", title="Actual vs Optimal FTE by Section")
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)

elif page == "✍️ Optimal FTE Input":
    st.title("✍️ Enter/Edit Optimal FTE by Section")

    optimal_df = get_optimal_fte()
    updated_optimal = st.data_editor(optimal_df, num_rows="dynamic", key="optimal_editor")

    if st.button("💾 Save Optimal FTE"):
        updated_optimal.to_excel(BASENAME_OPTIMAL, index=False)
        st.success("Optimal FTE saved.")

elif page == "📅 Forecast Tracker":
    st.title("📅 FTE Forecast Tracker")

    forecast_df = get_forecast_data()
    updated_forecast = st.data_editor(forecast_df, num_rows="dynamic", key="forecast_editor")

    if st.button("💾 Save Forecast Data"):
        updated_forecast.to_excel(BASENAME_FORECAST, index=False)
        st.success("Forecast tracker saved.")
