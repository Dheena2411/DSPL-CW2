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
st.caption("Note: The sharp rise in April 2026 reflects fewer countries reporting data for that period, which skews the average upward.")

trend_df = (
    filtered[filtered['usd_price'] < filtered['usd_price'].quantile(0.95)]
    .groupby('reference_period_start')['usd_price']
    .mean()
    .reset_index()
)
trend_df.columns = ['Date', 'Average USD Price']

fig_trend = px.line(
    trend_df,
    x='Date',
    y='Average USD Price',
    title='Average Global Food Price Over Time (USD) — Outliers Excluded',
    markers=True,
    labels={'Date': 'Reporting Period', 'Average USD Price': 'Avg USD Price'}
)
fig_trend.update_traces(line_color='#00b4d8', marker=dict(size=8))
st.plotly_chart(fig_trend, use_container_width=True)

st.divider()

st.subheader("🌐 Country Comparison")
st.caption("Top 20 countries by average food price in USD. Country codes follow ISO 3166-1 alpha-3 standard.")

country_df = (
    filtered.groupby('location_code')['usd_price']
    .mean()
    .reset_index()
    .sort_values('usd_price', ascending=False)
    .head(20)
)
country_df.columns = ['Country Code', 'Average USD Price']

fig_country = px.bar(
    country_df,
    x='Country Code',
    y='Average USD Price',
    title='Top 20 Countries by Average Food Price (USD)',
    color='Average USD Price',
    color_continuous_scale='Reds',
    labels={'Country Code': 'Country (ISO Code)', 'Average USD Price': 'Avg Price (USD)'}
)
fig_country.update_layout(xaxis_tickangle=-45)
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
        color_continuous_scale='Blues',
        labels={'Category': 'Commodity Category', 'Average USD Price': 'Avg Price (USD)'}
    )
    st.plotly_chart(fig_cat, use_container_width=True)

with col_right:
    top_commodities = (
        filtered[filtered['usd_price'] < filtered['usd_price'].quantile(0.95)]
        .groupby('commodity_name')['usd_price']
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
        color_continuous_scale='Greens',
        labels={'Commodity': 'Commodity Name', 'Average USD Price': 'Avg Price (USD)'}
    )
    st.plotly_chart(fig_com, use_container_width=True)

st.divider()

st.subheader("🗺️ Price Map by Market Location")
st.caption("Each dot represents a market. Colour indicates median USD price — darker red means higher prices. Size indicates number of commodities traded.")

map_df = (
    filtered.dropna(subset=['lat', 'lon'])
    .groupby(['market_name', 'lat', 'lon'])
    .agg(avg_price=('usd_price', 'median'), commodity_count=('commodity_name', 'nunique'))
    .reset_index()
)

fig_map = px.scatter_mapbox(
    map_df,
    lat='lat',
    lon='lon',
    color='avg_price',
    size='commodity_count',
    hover_name='market_name',
    hover_data={'avg_price': ':.2f', 'commodity_count': True, 'lat': False, 'lon': False},
    color_continuous_scale='YlOrRd',
    size_max=15,
    zoom=1,
    title='Median Food Price by Market Location',
    labels={'avg_price': 'Median USD Price', 'commodity_count': 'No. of Commodities'}
)
fig_map.update_layout(mapbox_style="open-street-map")
st.plotly_chart(fig_map, use_container_width=True)

st.divider()

with st.expander("📄 View Raw Data"):
    st.dataframe(filtered)