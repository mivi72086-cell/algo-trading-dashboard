# --- ALGORITHMIC TRADING WEB DASHBOARD (WITH ALPACA LINK) ---
import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from alpaca.trading.client import TradingClient

# 1. PAGE SETUP & AUTHENTICATION
st.set_page_config(page_title="Quant Dashboard", layout="wide")
st.title("📈 Live Algorithmic Trading Dashboard")

# Pull secrets from Streamlit's secure vault
API_KEY = st.secrets["ALPACA_API_KEY"]
SECRET_KEY = st.secrets["ALPACA_SECRET_KEY"]

# Connect to your actual Paper Trading account
try:
    trading_client = TradingClient(API_KEY, SECRET_KEY, paper=True)
    account = trading_client.get_account()
    portfolio_value = float(account.portfolio_value)
    buying_power = float(account.buying_power)
    connection_status = "✅ Connected to Alpaca"
except Exception as e:
    portfolio_value = 0.0
    buying_power = 0.0
    connection_status = "❌ Alpaca Connection Failed (Check Keys)"

# 2. SIDEBAR CONTROLS
st.sidebar.header("Algorithm Parameters")
target_asset = st.sidebar.text_input("Asset Ticker", value="BTC-USD")
history_days = st.sidebar.slider("Days of History", min_value=10, max_value=90, value=30)
fast_window = st.sidebar.slider("Fast SMA Window", min_value=2, max_value=10, value=3)
slow_window = st.sidebar.slider("Slow SMA Window", min_value=5, max_value=50, value=5)

# 3. LIVE BROKERAGE METRICS 
st.markdown("### 🏦 Brokerage Status")
st.caption(connection_status)
b_col1, b_col2 = st.columns(2)
b_col1.metric("Total Portfolio Value", f"${portfolio_value:,.2f}")
b_col2.metric("Available Buying Power", f"${buying_power:,.2f}")

st.divider()

# 4. DATA ENGINE (Fetching and Math)
@st.cache_data(ttl=60)
def fetch_and_calculate(ticker, days, fast, slow):
    data = yf.Ticker(ticker).history(period=f"{days}d")
    data['Fast_SMA'] = data['Close'].rolling(window=fast).mean()
    data['Slow_SMA'] = data['Close'].rolling(window=slow).mean()
    return data

data = fetch_and_calculate(target_asset, history_days, fast_window, slow_window)
current_price = data['Close'].iloc[-1]

# 5. ALGORITHM METRICS
st.markdown("### 🤖 Algorithm Logic")
col1, col2, col3 = st.columns(3)
col1.metric("Current Asset", target_asset)
col2.metric("Live Price", f"${current_price:,.2f}")
col3.metric("Algorithm Status", "🟢 ACTIVE (Buy/Hold)" if data['Fast_SMA'].iloc[-1] > data['Slow_SMA'].iloc[-1] else "🔴 WAITING (Sell/Avoid)")

# 6. THE CHARTING ENGINE
fig = go.Figure()
fig.add_trace(go.Scatter(x=data.index, y=data['Close'], mode='lines', name='Actual Price', line=dict(color='gray', width=1)))
fig.add_trace(go.Scatter(x=data.index, y=data['Fast_SMA'], mode='lines', name=f'Fast SMA ({fast_window})', line=dict(color='blue', width=2)))
fig.add_trace(go.Scatter(x=data.index, y=data['Slow_SMA'], mode='lines', name=f'Slow SMA ({slow_window})', line=dict(color='orange', width=2)))

fig.update_layout(title=f"{target_asset} Momentum Analysis", xaxis_title="Date", yaxis_title="Price (USD)", template="plotly_dark", height=600)
st.plotly_chart(fig, use_container_width=True)
