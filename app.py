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

st.sidebar.title("🔎 Filters")

countries = sorted(df['location_code'].unique())
selected_countries = st.sidebar.multiselect(
    "Select Countries",
    options=countries,
    default=countries
)

categories = sorted(df['commodity_category'].unique())
selected_categories = st.sidebar.multiselect(
    "Select Commodity Categories",
    options=categories,
    default=categories
)

commodities = sorted(df['commodity_name'].unique())
selected_commodity = st.sidebar.multiselect(
    "Select Commodity",
    options=commodities,
    default=commodities
)

filtered = df[
    (df['location_code'].isin(selected_countries)) &
    (df['commodity_category'].isin(selected_categories)) &
    (df['commodity_name'].isin(selected_commodity))
]

st.title("🌍 Global Food Price Dashboard")
st.markdown("Analysing food price trends across countries and commodities — 2026")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Records", f"{len(filtered):,}")
col2.metric("Countries", filtered['location_code'].nunique())
col3.metric("Commodities", filtered['commodity_name'].nunique())
col4.metric("Avg USD Price", f"${filtered['usd_price'].mean():.2f}")

st.divider()

st.subheader("📈 Price Trends Over Time")

trend_df = (
    filtered.groupby('reference_period_start')['usd_price']
    .mean()
    .reset_index()
)
trend_df.columns = ['Date', 'Average USD Price']

fig_trend = px.line(
    trend_df,
    x='Date',
    y='Average USD Price',
    title='Average Global Food Price Over Time (USD)',
    markers=True
)
st.plotly_chart(fig_trend, use_container_width=True)

st.divider()

st.subheader("🌐 Country Comparison")

country_df = (
    filtered.groupby('location_code')['usd_price']
    .mean()
    .reset_index()
    .sort_values('usd_price', ascending=False)
    .head(20)
)
country_df.columns = ['Country', 'Average USD Price']

fig_country = px.bar(
    country_df,
    x='Country',
    y='Average USD Price',
    title='Top 20 Countries by Average Food Price (USD)',
    color='Average USD Price',
    color_continuous_scale='Reds'
)
st.plotly_chart(fig_country, use_container_width=True)

st.divider()

st.subheader("🛒 Commodity Breakdown")

col_left, col_right = st.columns(2)

with col_left:
    cat_df = (
        filtered.groupby('commodity_category')['usd_price']
        .mean()
        .reset_index()
        .sort_values('usd_price', ascending=False)
    )
    cat_df.columns = ['Category', 'Average USD Price']
    fig_cat = px.bar(
        cat_df,
        x='Average USD Price',
        y='Category',
        orientation='h',
        title='Average Price by Commodity Category (USD)',
        color='Average USD Price',
        color_continuous_scale='Blues'
    )
    st.plotly_chart(fig_cat, use_container_width=True)

with col_right:
    top_commodities = (
        filtered.groupby('commodity_name')['usd_price']
        .mean()
        .reset_index()
        .sort_values('usd_price', ascending=False)
        .head(10)
    )
    top_commodities.columns = ['Commodity', 'Average USD Price']
    fig_com = px.bar(
        top_commodities,
        x='Average USD Price',
        y='Commodity',
        orientation='h',
        title='Top 10 Most Expensive Commodities (USD)',
        color='Average USD Price',
        color_continuous_scale='Greens'
    )
    st.plotly_chart(fig_com, use_container_width=True)

st.divider()

with st.expander("📄 View Raw Data"):
    st.dataframe(filtered)