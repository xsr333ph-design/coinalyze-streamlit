import streamlit as st
import requests
import time
import pandas as pd
import altair as alt
import os

# Получаем API ключ из секрета Streamlit
API_KEY = os.getenv("COINALYZE_API_KEY")

# Список символов (можно расширить)
symbols = ["BTCUSDT_PERP.A", "ETHUSDT_PERP.A"]

# Доступные таймфреймы (только часовые и дневные, без минутных)
timeframes = ["1hour", "2hour", "4hour", "6hour", "12hour", "daily"]

st.title("🔧 Coinalyze Aggregated Liquidation / OI / Ratio Indicator")

# Выбор символа и таймфрейма
symbol = st.selectbox("Choose symbol", symbols)
interval = st.selectbox("Timeframe", timeframes)

# Время: сейчас и 7 дней назад
now = int(time.time())
seven_days_ago = now - 7 * 24 * 60 * 60

def fetch_data(endpoint, symbol, interval):
    """Запрос к Coinalyze API"""
    url = f"https://fapi.coinalyze.net/v1/{endpoint}"
    params = {
        "instrument": symbol,
        "interval": interval,
        "from": seven_days_ago,
        "to": now
    }
    headers = {"x-api-key": API_KEY}

    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Error {response.status_code} at {endpoint}: {response.text}")
        return None

st.write("Fetching aggregated data (liquidations, OI, ratio)...")

# Загружаем данные
liquidations = fetch_data("liquidation-history", symbol, interval)
open_interest = fetch_data("open-interest-history", symbol, interval)
long_short = fetch_data("long-short-ratio-history", symbol, interval)

# Визуализация
if liquidations and open_interest and long_short:
    # Ликвидации
    df_liq = pd.DataFrame(liquidations)
    df_liq["time"] = pd.to_datetime(df_liq["time"], unit="s")

    chart_liq = (
        alt.Chart(df_liq)
        .mark_line()
        .encode(x="time:T", y="sum:Q")
        .properties(title="Aggregated Liquidations")
    )
    st.altair_chart(chart_liq, use_container_width=True)

    # OI
    df_oi = pd.DataFrame(open_interest)
    df_oi["time"] = pd.to_datetime(df_oi["time"], unit="s")

    chart_oi = (
        alt.Chart(df_oi)
        .mark_line(color="orange")
        .encode(x="time:T", y="value:Q")
        .properties(title="Open Interest")
    )
    st.altair_chart(chart_oi, use_container_width=True)

    # Long/Short ratio
    df_ratio = pd.DataFrame(long_short)
    df_ratio["time"] = pd.to_datetime(df_ratio["time"], unit="s")

    chart_ratio = (
        alt.Chart(df_ratio)
        .mark_line(color="green")
        .encode(x="time:T", y="value:Q")
        .properties(title="Long/Short Ratio")
    )
    st.altair_chart(chart_ratio, use_container_width=True)
