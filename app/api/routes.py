# app/api/routes.py
import pandas as pd
import numpy as np
from fastapi import APIRouter, Query
from datetime import datetime

from app.services.market_data import MarketDataService
from app.services.analytics.returns import DailyReturnsAnalyzer
from app.services.analytics.monte_carlo import MonteCarloSimulator
from app.services.signal.confidence import SignalConfidenceCalculator
from app.services.signal.ranking import SignalRanker
from app.api.schemas import SignalsResponse, SignalMetrics
from app.services.analytics.price import PriceAnalytics

router = APIRouter()

def to_json_safe(series: pd.Series) -> list:
    """
    Convert pandas Series to JSON-safe Python list:
    - NaN / +inf / -inf → None
    - numpy scalars → Python floats
    """
    result = []
    for v in series:
        if v is None:
            result.append(None)
        elif isinstance(v, (float, int)) and np.isfinite(v):
            result.append(float(v))
        else:
            result.append(None)
    return result


@router.get("/signals", response_model=SignalsResponse)
def get_signals(tickers: list[str] = Query(...),  years: int = 1,  simulations: int = 500):
    """
    Generate BUY / SELL / NO_TRADE signals for given tickers.
    """

    end = datetime.now()
    start = datetime(end.year - 1, end.month, end.day)

    # 1. Load market data
    svc = MarketDataService(start, end)
    panel_df = svc.load_panel(tickers)

    # 2. Compute returnss
    panel_df = DailyReturnsAnalyzer.compute(panel_df, tickers)

    signals = []

    for ticker in tickers:
        # 3. Monte Carlo simulation
        sim_df = MonteCarloSimulator.simulate(
            panel_df,
            ticker=ticker,
            years=years,
            simulations=simulations
        )

        current_price = panel_df[f"Close_{ticker}"].iloc[-1]

        # 4. Confidence metrics
        metrics = SignalConfidenceCalculator.from_monte_carlo(
            current_price,
            sim_df
        )

        # Using current baseline confidence logic
        confidence = abs(metrics["expected_return"]) * (1 - metrics["prob_loss"])

        decision = SignalRanker.classify({
            **metrics,
            "confidence": confidence
        })

        signals.append(
            SignalMetrics(
                ticker=ticker,
                current_price=float(current_price),
                expected_return=metrics["expected_return"],
                expected_price=current_price * (1 + metrics["expected_return"]),
                prob_gain=metrics["prob_gain"],
                prob_loss=metrics["prob_loss"],
                downside_95=metrics["downside_pct_95"],
                signal=decision["signal"],
                confidence=round(confidence, 4)
            )
        )

    ranked = SignalRanker.rank([s.dict() for s in signals])

    return SignalsResponse(
        signals=[SignalMetrics(**s) for s in ranked]
    )


@router.get("/prices/{ticker}")
def get_prices(ticker: str, years: int = 1):
    end = datetime.now()
    start = datetime(end.year - years, end.month, end.day)

    svc = MarketDataService(start, end)
    panel_df = svc.load_panel([ticker])

    panel_df = PriceAnalytics.moving_averages(
        panel_df,
        ticker=ticker,
        windows=[20, 50]
    )
    
    # JSON supports null → Python uses None
    close_col = f"Close_{ticker}"
    sma20_col = f"SMA_20_{ticker}"
    sma50_col = f"SMA_50_{ticker}"

    return {
        "dates": panel_df.index.astype(str).tolist(),
        "prices": to_json_safe(panel_df[close_col]),
        "sma20": to_json_safe(panel_df[sma20_col]),
        "sma50": to_json_safe(panel_df[sma50_col]),
    }

        
@router.get("/returns/{ticker}")
def get_daily_returns(ticker: str, years: int = 1):
    end = datetime.now()
    start = datetime(end.year - years, end.month, end.day)

    svc = MarketDataService(start, end)
    panel_df = svc.load_panel([ticker])

    prices = panel_df[f"Close_{ticker}"]
    returns = prices.pct_change().dropna()

    return {
        "returns": returns.tolist()
    }
    
@router.get("/monte-carlo/{ticker}")
def get_monte_carlo_paths(ticker: str, years: int = 1, simulations: int = 300):
    end = datetime.now()
    start = datetime(end.year - 1, end.month, end.day)

    svc = MarketDataService(start, end)
    panel_df = svc.load_panel([ticker])
    panel_df = DailyReturnsAnalyzer.compute(panel_df, [ticker])

    sim_df = MonteCarloSimulator.simulate(
        panel_df,
        ticker=ticker,
        years=years,
        simulations=simulations
    )

    safe_paths = (
        sim_df
        .replace([np.inf, -np.inf], None)
        .where(pd.notna(sim_df), None)
        .values
        .tolist()
    )

    safe_final = to_json_safe(sim_df.iloc[-1])

    return {
        "paths": safe_paths,
        "final_prices": safe_final
    }