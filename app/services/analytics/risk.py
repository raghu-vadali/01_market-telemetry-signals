# app/services/analytics/risk.py

import pandas as pd
import numpy as np


class ValueAtRiskAnalyzer:
    """
    Computes Value at Risk (VaR) based on historical returns.
    """

    @staticmethod
    def var_from_returns(returns: pd.Series,  confidence_levels: list[int]) -> dict[int, float]:
        """
        Compute VaR for a single return series.

        Returns:
            { confidence_level : VaR }
        """
        clean_returns = returns.dropna()

        if clean_returns.empty:
            raise ValueError("Returns series is empty")

        return {
            level: np.percentile(clean_returns, 100 - level)
            for level in confidence_levels
        }

    @staticmethod
    def var_for_tickers(panel_df: pd.DataFrame, tickers: list[str], confidence_levels: list[int]) -> pd.DataFrame:
        """
            Compute VaR for multiple tickers.

            Output columns:
            - ticker
            - confidence
            - var
        """
        records = []

        for ticker in tickers:
            col = f"Daily_Return_{ticker}"
            if col not in panel_df.columns:
                raise KeyError(f"Missing daily returns for {ticker}")

            var_map = ValueAtRiskAnalyzer.var_from_returns(panel_df[col], confidence_levels)

            for conf, value in var_map.items():
                records.append({
                    "ticker": ticker,
                    "confidence": conf,
                    "var": value
                })

        return pd.DataFrame(records)
