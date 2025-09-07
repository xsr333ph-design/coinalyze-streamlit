import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go

# ======================
# Настройки API
# ======================
API_KEY = "54cdc166-45ae-42fd-bdbb-eff6ad8f37312"
BASE_URL = "https://api.coinalyze.net/v1/"

headers = {"X-API-Key": API_KEY}

# ======================
# Функция получения данных
# ======================
def get_data(symbol="BTCUSDT"):
    # Здесь для примера делаем вид, что Coinalyze отдаёт JSON
    # В реальном запросе нужно будет подставить правильные endpoints
    try:
        resp = requests.get(
            BASE_URL + f"market-data?symbol={symbol}",
            headers=headers,
            timeout=10
        )
        return resp.json()
    except Exception as e:
        st.error(f"Ошибка при запросе: {e}")
        return None

# ======================
# Логика сигналов
# ======================
def generate_signals(df):
    signals = []
    for i in range(len(df)):
        row = df.iloc[i]

        # Условие входа в лонг
        if (row["short_liquidations"] > row["long_liquidations"] * 1.1
            and row["oi"] > 0
            and row["long_short_ratio"] > 0):
            signals.append("⬆️")

        # Условие входа в шорт
        elif (row["long_liquidations"] > row["short_liquidations"] * 1.1
              and row["oi"] > 0
              and row["long_short_ratio"] < 0):
            signals.append("⬇️")

        # Условие выхода из лонга
        elif (row["long_liquidations"] > row["short_liquidations"] * 1.1
              and row["oi"] < 0
              and row["long_short_ratio"] < 0):
            signals.append("❌🔵")

        # Условие выхода из шорта
        elif (row["short_liquidations"] > row["long_liquidations"] * 1.1
              and row["oi"] < 0
              and row["long_short_ratio"] < 0):
            signals.append("❌🔴")
        else:
            signals.append("")

    df["signal"] = signals
    return df

# ======================
# Интерфейс Streamlit
# ======================
st.title("📊 Индикатор ликвидаций Coinalyze")

# Выбор монеты
symbol = st.selectbox("Выберите символ", ["BTCUSDT", "ETHUSDT", "BNBUSDT"])

# Получаем данные
data = get_data(symbol)

if data:
    # Пример тестовой таблицы
    df = pd.DataFrame(data)  # предполагаем, что Coinalyze API вернул JSON-таблицу
else:
    # Для отладки используем моковые данные
    df = pd.DataFrame({
        "time": pd.date_range(start="2025-01-01", periods=20, freq="H"),
        "long_liquidations": [i*100 for i in range(20)],
        "short_liquidations": [i*120 for i in range(20)],
        "oi": [100 if i % 2 == 0 else -100 for i in range(20)],
        "long_short_ratio": [1 if i % 3 == 0 else -1 for i in range(20)]
    })

df = generate_signals(df)

# График
fig = go.Figure()
fig.add_trace(go.Scatter(x=df["time"], y=df["long_liquidations"], mode="lines", name="Long Liquidations"))
fig.add_trace(go.Scatter(x=df["time"], y=df["short_liquidations"], mode="lines", name="Short Liquidations"))

# Добавляем сигналы
for i, row in df.iterrows():
    if row["signal"] != "":
        fig.add_annotation(
            x=row["time"],
            y=row["long_liquidations"],
            text=row["signal"],
            showarrow=True,
            arrowhead=1
        )

st.plotly_chart(fig, use_container_width=True)
