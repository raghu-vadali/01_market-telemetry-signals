# app/services/signal/confidence.py

import numpy as np
import pandas as pd


class SignalConfidenceCalculator:
    """
    Computes confidence metrics from Monte Carlo simulations.
    """

    @staticmethod
    def from_monte_carlo(current_price: float, simulated_prices: pd.DataFrame) -> dict[str, float]:
        """
        Uses final simulated prices to compute confidence metrics.
        """
        final_prices = simulated_prices.iloc[-1]

        prob_gain = (final_prices > current_price).mean()
        prob_loss = (final_prices < current_price).mean()

        expected_return = (final_prices.mean() / current_price) - 1

        downside_var_95 = np.percentile(final_prices, 5)

        return {
            "expected_return": float(expected_return),
            "prob_gain": float(prob_gain),
            "prob_loss": float(prob_loss),
            "downside_pct_95": float(downside_var_95),
        }