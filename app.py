import streamlit as st
import requests

# Адрес твоего прокси на Render
PROXY_URL = "https://coinalyze-proxy.onrender.com"

# Функция для получения данных через прокси
def fetch_data(endpoint: str, params: dict = None):
    url = f"{PROXY_URL}/{endpoint}"
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"error": str(e)}

# Интерфейс Streamlit
st.set_page_config(page_title="Coinalyze Dashboard", layout="wide")

st.title("📊 Coinalyze Data via Proxy")

# Пример 1: Список рынков
st.subheader("Список рынков")
markets = fetch_data("v1/markets")
st.json(markets)

# Пример 2: Ликвидации (с параметрами)
st.subheader("Ликвидации")
symbol = st.text_input("Введите символ (например, BTCUSDT):", "BTCUSDT")
interval = st.selectbox("Интервал:", ["1h", "4h", "1d"], index=0)

if st.button("Получить ликвидации"):
    liquidations = fetch_data("v1/liquidations", {"symbol": symbol, "interval": interval})
    st.json(liquidations)

# Пример 3: Открытый интерес
st.subheader("Открытый интерес")
if st.button("Получить Open Interest"):
    oi = fetch_data("v1/open-interest", {"symbol": symbol, "interval": interval})
    st.json(oi)
