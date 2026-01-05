# app/services/analytics/monte_carlo.py

import numpy as np
import pandas as pd


class MonteCarloSimulator:
    """
    Monte Carlo simulation for future stock price paths.
    """

    @staticmethod
    def simulate(
                    panel_df: pd.DataFrame,
                    ticker: str,
                    years: int,
                    simulations: int,
                    seed: int = 42
                ) -> pd.DataFrame:
        """
        Simulate future price paths using geometric Brownian motion.

        Returns:
            DataFrame with shape (trading_days, simulations)
        """
        close_col = f"Close_{ticker}"
        if close_col not in panel_df.columns:
            raise KeyError(f"Missing column: {close_col}")

        prices = panel_df[close_col].dropna()
        if prices.empty:
            raise ValueError("Price series is empty")

        log_returns = np.log(prices / prices.shift(1)).dropna()

        mu = log_returns.mean() * 252
        sigma = log_returns.std() * np.sqrt(252)

        trading_days = 252 * years
        dt = 1 / trading_days

        np.random.seed(seed)

        rand = np.random.normal(
            loc=0,
            scale=1,
            size=(trading_days, simulations)
        )

        drift = (mu - 0.5 * sigma**2) * dt
        diffusion = sigma * np.sqrt(dt) * rand

        price_paths = prices.iloc[-1] * np.exp(
            np.cumsum(drift + diffusion, axis=0)
        )

        return pd.DataFrame(price_paths)

    @staticmethod
    def summary(simulations_df: pd.DataFrame) -> dict[str, float]:
        """
        Summary statistics of final simulated prices.
        """
        final_prices = simulations_df.iloc[-1]

        return {
            "mean": float(final_prices.mean()),
            "median": float(final_prices.median()),
            "min": float(final_prices.min()),
            "max": float(final_prices.max()),
            "std": float(final_prices.std()),
        }