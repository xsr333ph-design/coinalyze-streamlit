import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="Индикатор ликвидаций", layout="wide")

st.title("📊 Индикатор ликвидаций Coinalyze")

# --- Выбор торгового символа
symbol = st.selectbox("Выберите символ", ["BTCUSDT", "ETHUSDT", "BNBUSDT"])

# --- Функция запроса данных с API Coinalyze (замени URL на реальный!)
def get_liquidation_data(symbol: str):
    url = f"https://api.coinalyze.net/liquidations?symbol={symbol}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            return {}
    except Exception as e:
        return {"error": str(e)}

# --- Загружаем данные
data = get_liquidation_data(symbol)

# --- Отладочный вывод (видно прямо в Streamlit)
st.write("DEBUG: API ответ", data)

# --- Преобразуем в DataFrame
if not data or "error" in data:
    st.error("❌ Ошибка получения данных. Проверь API.")
    st.stop()

# Если ответ — словарь, делаем список
if isinstance(data, dict):
    data = [data]

try:
    df = pd.DataFrame(data)
except Exception as e:
    st.error(f"Ошибка преобразования данных: {e}")
    st.stop()

# Проверим что в DataFrame есть данные
if df.empty:
    st.warning("⚠️ Данных нет для выбранного символа")
    st.stop()

# --- Построение графика ликвидаций
fig = go.Figure()

fig.add_trace(go.Bar(
    x=df["timestamp"], 
    y=df["long_liquidations"], 
    name="Лонг ликвидации", 
    marker_color="red"
))

fig.add_trace(go.Bar(
    x=df["timestamp"], 
    y=df["short_liquidations"], 
    name="Шорт ликвидации", 
    marker_color="green"
))

fig.update_layout(
    title=f"Ликвидации {symbol}",
    xaxis_title="Время",
    yaxis_title="Объём ликвидаций",
    barmode="group"
)

st.plotly_chart(fig, use_container_width=True)
