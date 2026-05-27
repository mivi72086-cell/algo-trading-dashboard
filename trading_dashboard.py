# --- ALGORITHMIC TRADING WEB DASHBOARD (WITH ALPACA LINK) ---
import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from alpaca.trading.client import TradingClient
# 1. PAGE SETUP & AUTHENTICATION
st.set_page_config(page_title="Quant Dashboard", layout="wide")
st.title("📈 Live Algorithmic Trading Dashboard")

# Pull secrets from Streamlit's secure vault instead of hardcoding them!
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