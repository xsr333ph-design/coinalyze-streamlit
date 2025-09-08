import os
import streamlit as st
import pandas as pd
import plotly.express as px
import requests

st.set_page_config(page_title="Coinalyze Aggregated Indicator", layout="wide")
st.title("🛠 Coinalyze Aggregated Liquidation / OI / Ratio Indicator")

API_KEY = os.getenv("COINALYZE_API_KEY", "")
if not API_KEY:
    st.error("API key missing! Set COINALYZE_API_KEY env var or configure in secrets.")
    st.stop()

HEADERS = {"api_key": API_KEY}
BASE_URL = "https://api.coinalyze.net/v1"

symbol = st.selectbox("Choose symbol", ["BTCUSDT_PERP.A", "ETHUSDT_PERP.A"])
tf = st.selectbox("Timeframe", ["5m","1h","1d"])

# --- Helper to fetch historical series ---
def fetch_history(endpoint: str, series_name: str):
    url = f"{BASE_URL}/{endpoint}"
    params = {"symbols": symbol, "interval": tf}
    resp = requests.get(url, headers=HEADERS, params=params, timeout=15)
    if resp.status_code != 200:
        st.error(f"Error {resp.status_code} at {endpoint}: {resp.text}")
        st.stop()
    data = resp.json()
    df = pd.DataFrame(data)
    df["timestamp"] = pd.to_datetime(df["update"], unit="ms")
    df = df.set_index("timestamp").sort_index()
    return df

st.subheader("Fetching aggregated data (liquidations, OI, ratio)...")
liqs = fetch_history("liquidation-history", "liq")
oi = fetch_history("open-interest-history", "oi")
lsr = fetch_history("long-short-ratio-history", "lsr")

# Merge into single DataFrame
df = pd.concat([liqs["value"].rename("liquidations"),
                oi["value"].rename("open_interest"),
                lsr["value"].rename("long_short_ratio")], axis=1).dropna()

st.subheader(f"Latest data for `{symbol}` ({tf} timeframe):")
st.dataframe(df.tail(10))

st.subheader("Charts")

fig = px.line(df, y=["liquidations","open_interest","long_short_ratio"])
fig.update_layout(xaxis_title="Time", yaxis_title="Value", legend_title="Series")
st.plotly_chart(fig, use_container_width=True)
