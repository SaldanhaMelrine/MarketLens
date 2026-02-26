import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from data_fetcher import fetch_stock_data
from processor import add_indicators
from database import init_db, save_to_db, load_from_db

st.set_page_config(layout="wide")
st.title("Stock & Portfolio Analytics Dashboard")

init_db()

# ---------------------------------------------------
# CACHED DATA LOADER
# ---------------------------------------------------
@st.cache_data(show_spinner=False)
def cached_load(ticker):
    return load_from_db(ticker)

# ---------------------------------------------------
# CACHED PORTFOLIO METRICS
# ---------------------------------------------------
@st.cache_data(show_spinner=False)
def compute_portfolio_metrics(returns_df):
    portfolio_returns = returns_df.mean(axis=1)
    portfolio_equity = (1 + portfolio_returns).cumprod()

    portfolio_vol = portfolio_returns.std() * (252 ** 0.5)

    rolling_max = portfolio_equity.cummax()
    portfolio_drawdown = portfolio_equity / rolling_max - 1
    max_drawdown = portfolio_drawdown.min()

    return portfolio_equity, portfolio_vol, portfolio_drawdown, max_drawdown

# ---------------------------------------------------
# Inputs
# ---------------------------------------------------
tickers = st.multiselect(
    "Select Stocks",
    ["AAPL", "MSFT", "NVDA", "TSLA"],
    default=["AAPL"]
)

period = st.selectbox(
    "Select Time Period",
    ["1mo", "3mo", "6mo", "1y"]
)

# ---------------------------------------------------
# Manual Update Button
# ---------------------------------------------------
if st.button("Update Data"):
    for ticker in tickers:
        data = fetch_stock_data(ticker, period)
        data = add_indicators(data)
        save_to_db(data, ticker)

    st.cache_data.clear()  # Clear cached DB loads + portfolio calcs
    st.success("Data Updated and Stored in Database")

# ---------------------------------------------------
# Load & Filter Data
# ---------------------------------------------------
all_data = {}

for ticker in tickers:
    df = cached_load(ticker)

    if not df.empty:
        df = df.sort_index()

        if period == "1mo":
            df = df.last("30D")
        elif period == "3mo":
            df = df.last("90D")
        elif period == "6mo":
            df = df.last("180D")
        elif period == "1y":
            df = df.last("365D")

        df["returns"] = df["close"].pct_change()
        all_data[ticker] = df

if not all_data:
    st.info("No data available. Click 'Update Data' to fetch stock information.")
    st.stop()

if len(all_data) < len(tickers):
    st.warning("Some selected tickers have no stored data.")

# ===================================================
# SINGLE STOCK VIEW
# ===================================================
if len(all_data) == 1:

    ticker, data = next(iter(all_data.items()))

    st.header("📈 Individual Stock Analysis")

    cumulative_return = (data["close"].iloc[-1] / data["close"].iloc[0] - 1)
    volatility = data["returns"].std() * (252 ** 0.5)

    rolling_max = data["close"].cummax()
    drawdown = data["close"] / rolling_max - 1
    max_drawdown = drawdown.min()

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Return", f"{cumulative_return:.2%}")
    col2.metric("Volatility (Annualized)", f"{volatility:.2%}")
    col3.metric("Max Drawdown", f"{max_drawdown:.2%}")

    fig = go.Figure()

    fig.add_trace(go.Candlestick(
        x=data.index,
        open=data["open"],
        high=data["high"],
        low=data["low"],
        close=data["close"],
        name="Price"
    ))

    fig.add_trace(go.Scatter(
        x=data.index,
        y=data["ma20"],
        mode='lines',
        name='MA20'
    ))

    fig.update_layout(title=f"{ticker} Price Chart")

    st.plotly_chart(fig, use_container_width=True)

# ===================================================
# MULTI-STOCK COMPARISON
# ===================================================
if len(all_data) >= 2:

    st.header("📊 Multi-Stock Comparison (Normalized)")

    cols = st.columns(2)

    for i, (ticker, data) in enumerate(all_data.items()):

        with cols[i % 2]:

            st.subheader(ticker)

            cumulative_return = (data["close"].iloc[-1] / data["close"].iloc[0] - 1)
            volatility = data["returns"].std() * (252 ** 0.5)

            col1, col2 = st.columns(2)
            col1.metric("Return", f"{cumulative_return:.2%}")
            col2.metric("Volatility", f"{volatility:.2%}")

            normalized = data["close"] / data["close"].iloc[0] * 100

            fig = go.Figure()

            fig.add_trace(go.Scatter(
                x=data.index,
                y=normalized,
                mode="lines",
                name="Normalized Price"
            ))

            fig.update_layout(
                height=300,
                margin=dict(l=10, r=10, t=30, b=10)
            )

            st.plotly_chart(fig, use_container_width=True)

# ===================================================
# PORTFOLIO SECTION
# ===================================================
if len(all_data) >= 2:

    st.header("📈 Portfolio Analysis (Equal Weight)")

    returns_df = pd.DataFrame()

    for ticker, df in all_data.items():
        returns_df[ticker] = df["returns"]

    returns_df.dropna(inplace=True)

    portfolio_equity, portfolio_vol, portfolio_drawdown, max_drawdown = compute_portfolio_metrics(returns_df)

    col1, col2, col3 = st.columns(3)
    col1.metric("Portfolio Return", f"{portfolio_equity.iloc[-1] - 1:.2%}")
    col2.metric("Portfolio Volatility (Annualized)", f"{portfolio_vol:.2%}")
    col3.metric("Max Drawdown", f"{max_drawdown:.2%}")

    equity_fig = go.Figure()
    equity_fig.add_trace(go.Scatter(
        x=portfolio_equity.index,
        y=portfolio_equity,
        mode="lines",
        name="Portfolio Equity"
    ))

    st.plotly_chart(equity_fig, use_container_width=True)

    dd_fig = go.Figure()
    dd_fig.add_trace(go.Scatter(
        x=portfolio_drawdown.index,
        y=portfolio_drawdown,
        mode="lines",
        name="Drawdown"
    ))

    st.plotly_chart(dd_fig, use_container_width=True)