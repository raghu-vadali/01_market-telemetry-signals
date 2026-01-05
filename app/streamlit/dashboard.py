import streamlit as st
import requests
import pandas as pd
import numpy as np

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns

API_URL = "http://127.0.0.1:8000"

# ---------------------------------
# Page config
# ---------------------------------
st.set_page_config(
    page_title="Market Telemetry & Signal Ranking",
    layout="wide"
)

st.title("Market Telemetry & Signal Ranking")

# ---------------------------------
# Sidebar controls
# ---------------------------------
st.sidebar.header("Configuration")

tickers_input = st.sidebar.text_input(
    "Tickers (comma-separated)",
    "NVDA,AAPL,GOOG"
)

years = st.sidebar.slider(
    "Years to simulate",
    min_value=1,
    max_value=3,
    value=1
)

simulations = st.sidebar.slider(
    "Monte Carlo simulations",
    min_value=100,
    max_value=2000,
    step=100,
    value=500
)

run_button = st.sidebar.button("Run Analysis")

# ---------------------------------
# Fetch data when button is clicked
# ---------------------------------
if run_button:
    tickers = [t.strip() for t in tickers_input.split(",")]

    params = {
        "tickers": tickers,
        "years": years,
        "simulations": simulations
    }

    with st.spinner("Running simulations..."):
        response = requests.get(f"{API_URL}/signals", params=params)

    if response.status_code != 200:
        st.error("❌ Failed to fetch signals from API")
        st.stop()

    # ✅ Persist results across reruns
    st.session_state["signals_df"] = pd.DataFrame(
        response.json()["signals"]
    )

# ---------------------------------
# Stop if no data yet
# ---------------------------------
if "signals_df" not in st.session_state:
    st.info("Configure parameters and click **Run Analysis**")
    st.stop()

df = st.session_state["signals_df"]

# ---------------------------------
# Signal summary table
# ---------------------------------
st.subheader("🎯 Signal Summary")

st.dataframe(
    df.sort_values("confidence", ascending=False),
    use_container_width=True
)

# ---------------------------------
# KPI metrics
# ---------------------------------
col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "BUY signals",
        int((df["signal"] == "BUY").sum())
    )

with col2:
    st.metric(
        "NO_TRADE signals",
        int((df["signal"] == "NO_TRADE").sum())
    )

with col3:
    st.metric(
        "Average Confidence",
        round(df["confidence"].mean(), 3)
    )

# ---------------------------------
# Ticker detail section
# ---------------------------------
st.subheader("📊 Ticker Details")

selected_ticker = st.selectbox(
    "Select ticker",
    df["ticker"].tolist()
)

row = df[df["ticker"] == selected_ticker].iloc[0]

st.markdown(f"### {selected_ticker}")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Expected Return",
        f"{row.expected_return:.2%}"
    )
    
with col2:
    st.metric(
        "Expected Price",
        f"${row.expected_price:.2f}"
    )

with col3:
    st.metric(
        "Probability of Gain",
        f"{row.prob_gain:.2%}"
    )

with col4:
    st.metric(
        "Probability of Loss",
        f"{row.prob_loss:.2%}"
    )

col5, col6 = st.columns(2)

with col5:
    st.metric(
        "VaR 95% (Price)",
        f"${row.downside_95:.2f}"
    )

with col6:
    st.metric(
        "Signal",
        row.signal
    )

st.metric(
    "Confidence Score",
    round(row.confidence, 4)
)

#-------------------------------------------------------------------------
returns_response = requests.get(
    f"{API_URL}/returns/{selected_ticker}",
    params={"years": years}
)

returns_df = pd.Series(returns_response.json()["returns"])

tab1, tab2, tab3, tab4 = st.tabs(
    ["📈 Price & Trend", "📉 Returns", "⚠️ Risk (VaR)", "🔮 Monte Carlo"]
)

with tab1:
    st.subheader(f"{selected_ticker} - Price & Trend")

    price_resp = requests.get(
        f"{API_URL}/prices/{selected_ticker}",
        params={"years": years}
    )
    
    price_data = price_resp.json()
    dates = price_data["dates"]

    fig, ax = plt.subplots(figsize=(10, 4))

    ax.plot(dates, price_data["prices"], label="Price", linewidth=2)
    ax.plot(dates, price_data["sma20"], label="20D SMA", linestyle="--")
    ax.plot(dates, price_data["sma50"], label="50D SMA", linestyle="--")

    ax.set_title(f"{selected_ticker} Price & Trend")
    ax.xaxis.set_major_locator(mdates.AutoDateLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
    ax.set_xlabel("Date")
    ax.tick_params(axis="x", rotation=45)
    ax.set_ylabel("Price")
    ax.legend()
    ax.grid(alpha=0.5)

    st.pyplot(fig)

with tab2:
    st.subheader("Daily Returns Distribution")

    returns = returns_df.dropna()

    fig, ax = plt.subplots(figsize=(8, 4))
    ax.hist(returns, bins=50, density=True, alpha=0.6, label="Histogram")
    returns.plot(kind="kde", ax=ax, linewidth=2, label="KDE")

    ax.axvline(0, color="black", linestyle="--", alpha=0.5)
    ax.set_xlabel("Daily Returns")
    ax.set_ylabel("Density")
    ax.legend()
    ax.grid(alpha=0.5)

    st.pyplot(fig)

with tab3:
    st.subheader("Value at Risk (VaR)")

    var_95 = np.percentile(returns, 5)

    fig, ax = plt.subplots(figsize=(8, 4))
    kde = returns.plot(kind="kde", ax=ax)

    x = kde.get_lines()[0].get_xdata()
    y = kde.get_lines()[0].get_ydata()

    ax.fill_between(x, y, where=(x <= var_95), color="red", alpha=0.4)
    ax.fill_between(x, y, where=(x > var_95), color="green", alpha=0.4)
    ax.axvline(var_95, color="red", linestyle="--", label=f"VaR 95% = {var_95:.3f}")

    ax.legend()
    ax.grid(alpha=0.5)
    ax.set_xlabel("Returns")
    ax.set_ylabel("Density")

    st.pyplot(fig)
    
with tab4:
    st.subheader(f"{selected_ticker} - Monte Carlo Simulation")

    mc_resp = requests.get(
        f"{API_URL}/monte-carlo/{selected_ticker}",
        params={"years": years, "simulations": 300}
    )

    mc_data = mc_resp.json()
    paths = np.array(mc_data["paths"])   # shape: (days, n_paths)

    fig, ax = plt.subplots(figsize=(10, 4))

    for i in range(min(50, paths.shape[1])):
        ax.plot(paths[:, i], alpha=0.2)

    # Reference lines
    ax.axhline(
        row.current_price,
        color="black",
        linestyle="--",
        label="Current Price"
    )

    ax.axhline(
        row.expected_price,
        color="green",
        linestyle="--",
        label="Expected Price"
    )

    ax.set_title(f"{selected_ticker} Monte Carlo Price Paths")
    ax.set_xlabel("Days")
    ax.set_ylabel("Price")
    ax.legend()
    ax.grid(alpha=0.5)

    st.pyplot(fig)
