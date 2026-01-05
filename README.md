# Market Telemetry & Signal Ranking

Probabilistic market signal generation using Monte Carlo simulation, FastAPI, and Streamlit.

---

## Overview

This project is an end-to-end **market telemetry system** that generates **risk-aware trading signals** based on probabilistic future price simulations rather than point forecasts.

Instead of predicting a single future price, the system:
- simulates thousands of possible future price paths,
- quantifies upside/downside risk,
- and ranks signals based on confidence and risk metrics.

The result is a **more realistic, uncertainty-aware decision framework**.

---

## Key Concepts

- **Market Telemetry**  
  Continuous extraction of price behavior, returns, and risk characteristics.

- **Monte Carlo Simulation**  
  Future prices are modeled as stochastic processes using historical return distributions.

- **Risk-Aware Signals**  
  Signals are driven by probabilities (gain vs loss) and downside risk (VaR), not just expected return.

---

## Architecture

### Layers

- **Analytics Layer (pandas / numpy)**
  - Daily returns
  - Monte Carlo simulations
  - Moving averages

- **Signal Layer**
  - Expected return
  - Probability of gain / loss
  - Value-at-Risk (VaR)
  - Confidence scoring

- **API Layer (FastAPI)**
  - Exposes analytics as JSON endpoints
  - Ensures strict JSON compliance

- **Visualization Layer (Streamlit)**
  - Interactive dashboard
  - Price trends & indicators
  - Monte Carlo uncertainty visualization

---

## Signal Logic (High-Level)

1. Download historical price data
2. Compute daily returns
3. Simulate future price paths (Monte Carlo)
4. Extract risk metrics:
   - Expected return
   - Probability of gain / loss
   - Downside VaR (95%)
5. Compute confidence score
6. Classify signals:
   - **BUY**
   - **NO_TRADE**

> The goal is not prediction accuracy, but **decision quality under uncertainty**.

---

## 🧪 Example Metrics

- Expected Return  
- Probability of Gain  
- Probability of Loss  
- Value-at-Risk (95%)  
- Confidence Score  

Signals are ranked by confidence for comparison across tickers.

---

## Dashboard Features

- Price & trend visualization
- Moving averages (20D / 50D)
- Monte Carlo simulated price paths
- Distribution of final simulated prices
- Ranked signal table

---

## How to Run

### Install dependencies

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
API documentation: 
http://127.0.0.1:8000/docs
streamlit run app/streamlit/dashboard.py
