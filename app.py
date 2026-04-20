import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Global Food Prices", layout="wide")

@st.cache_data
def load_data():
    df = pd.read_excel('data/hdx_hapi_food_price_global_2026.xlsx')
    df.drop(columns=['warning', 'error'], inplace=True)
    df.dropna(subset=['usd_price'], inplace=True)
    df['reference_period_start'] = pd.to_datetime(df['reference_period_start'])
    df['reference_period_end'] = pd.to_datetime(df['reference_period_end'])
    return df

df = load_data()

st.title("🌍 Global Food Price Dashboard")
st.write(f"Dataset: {len(df):,} records across {df['location_code'].nunique()} countries")
st.dataframe(df.head(20))