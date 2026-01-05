# app/services/analytics/price.py

import pandas as pd

class PriceAnalytics:
    """
    Price-based analytics (no returns, no risk).
    """

    @staticmethod
    def moving_averages(panel_df: pd.DataFrame, ticker: str,  windows: list[int]) -> pd.DataFrame:
        df = panel_df.copy()

        close_col = f"Close_{ticker}"
        if close_col not in df.columns:
            raise KeyError(f"Missing column {close_col}")

        for w in windows:
            df[f"SMA_{w}_{ticker}"] = df[close_col].rolling(w).mean()

        return df