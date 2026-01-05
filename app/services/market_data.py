# app/services/market_data.py

from datetime import datetime
import pandas as pd
import yfinance as yf


class MarketDataService:
    """
    Handles all market data ingestion from Yahoo Finance.
    """

    def __init__(self, start: datetime, end: datetime):
        self.start = start
        self.end = end

    def load_single(self, ticker: str) -> pd.DataFrame:
        """
        Load data for a single ticker.
        """
        df = yf.download(ticker, self.start, self.end, progress=False)
        if df.empty:
            raise ValueError(f"No data returned for ticker {ticker}")
        return df

    def load_multiple(self, tickers: list[str]) -> dict[str, pd.DataFrame]:
        """
        Load multiple tickers as a dictionary.
        """
        data = {}
        for t in tickers:
            data[t] = self.load_single(t)
        return data

    def load_panel(self, tickers: list[str]) -> pd.DataFrame:
        """
        Load multiple tickers into a single flattened DataFrame.
        Matches your existing 'data' variable.
        """
        df = yf.download(tickers, self.start, self.end, progress=False)

        # Reset index (Date → column)
        df = df.reset_index()

        # Flatten multi-index columns
        df.columns = [
            "_".join(col).strip() if isinstance(col, tuple) else col
            for col in df.columns
        ]

        # Normalize Date column
        df = df.rename(columns={"Date_": "Date"})

        return df
