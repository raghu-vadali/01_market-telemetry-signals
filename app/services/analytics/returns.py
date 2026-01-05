# app/services/analytics/returns.py

import pandas as pd


class DailyReturnsAnalyzer:
    """
    Computes daily percentage returns for one or more tickers.
    """

    @staticmethod
    def compute(panel_df: pd.DataFrame, tickers: list[str]) -> pd.DataFrame:
        """
        Adds daily returns columns to a copy of panel_df.

        Output columns:
        - Daily_Return_<TICKER>
        """
        df = panel_df.copy()

        for ticker in tickers:
            close_col = f"Close_{ticker}"
            if close_col not in df.columns:
                raise KeyError(f"Missing column: {close_col}")

            df[f"Daily_Return_{ticker}"] = df[close_col].pct_change()

        return df

    @staticmethod
    def extract(panel_df: pd.DataFrame, tickers: list[str]) -> pd.DataFrame:
        """
        Returns a DataFrame with only daily returns.
        """
        data = {}

        for ticker in tickers:
            col = f"Daily_Return_{ticker}"
            if col not in panel_df.columns:
                raise KeyError(f"Column not found: {col}")
            data[ticker] = panel_df[col]

        return pd.DataFrame(data)
