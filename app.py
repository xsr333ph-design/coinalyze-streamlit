import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go

# 🔑 Твой API ключ
API_KEY = "54cdc166-45ae-42fd-bdbb-eff6ad8f3731"
BASE_URL = "https://coinalyze.net/api/v1/liquidations"

# ========================
# Функция для запроса API
# ========================
def get_liquidations(symbol: str):
    headers = {"Authorization": f"Bearer {API_KEY}"}
    params = {"symbol": symbol, "interval": "1h"}  # пример: 1h свечи
    response = requests.get(BASE_URL, headers=headers, params=params)

    if response.status_code != 200:
        return None, f"Ошибка {response.status_code}: {response.text}"

    try:
        data = response.json()
        return data, None
    except Exception as e:
        return None, str(e)

# ========================
# Streamlit UI
# ========================
st.set_page_config(page_title="Индикатор ликвидаций Coinalyze", layout="wide")
st.title("📊 Индикатор ликвидаций Coinalyze")

# Символ
symbol = st.selectbox("Выберите символ", ["BTCUSDT", "ETHUSDT", "BNBUSDT"])

# Получаем данные
data, error = get_liquidations(symbol)

# Отладка
st.write("DEBUG: API ответ")
st.json(data if data else {})

if error:
    st.error(f"Ошибка получения данных: {error}")
elif not data:
    st.warning("Нет данных от API.")
else:
    try:
        # Предполагаем, что API возвращает список объектов с полями:
        # timestamp, long_liquidations, short_liquidations
        df = pd.DataFrame(data)

        # Приводим время
        if "timestamp" in df.columns:
            df["timestamp"] = pd.to_datetime(df["timestamp"], unit="s")

        # Строим график
        fig = go.Figure()
        if "long_liquidations" in df.columns:
            fig.add_trace(go.Bar(x=df["timestamp"], y=df["long_liquidations"], name="Longs", marker_color="green"))
        if "short_liquidations" in df.columns:
            fig.add_trace(go.Bar(x=df["timestamp"], y=df["short_liquidations"], name="Shorts", marker_color="red"))

        fig.update_layout(
            title=f"Ликвидации {symbol}",
            xaxis_title="Время",
            yaxis_title="USD",
            barmode="stack"
        )

        st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.error(f"Ошибка обработки данных: {e}")
