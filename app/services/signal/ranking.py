# app/services/signal/ranking.py

class SignalRanker:
    """
    Converts risk & confidence metrics into actionable signals.
    """

    @staticmethod
    def classify(metrics: dict) -> dict:
        """
        BUY / SELL / NO_TRADE classification with confidence score.
        """

        exp_ret = metrics["expected_return"]
        prob_loss = metrics["prob_loss"]

        # Core decision rules (transparent & explainable)
        if exp_ret > 0.05 and prob_loss < 0.30:
            signal = "BUY"
            confidence = min(1.0, exp_ret * (1 - prob_loss))

        elif exp_ret < -0.05 and prob_loss > 0.60:
            signal = "SELL"
            confidence = min(1.0, abs(exp_ret) * prob_loss)

        else:
            signal = "NO_TRADE"
            confidence = 1 - abs(exp_ret)

        return {
            "signal": signal,
            "confidence": round(confidence, 3)
        }

    @staticmethod
    def rank(signals: list[dict]) -> list[dict]:
        """
        Rank signals by confidence.
        """
        return sorted(signals, key=lambda x: x["confidence"], reverse=True)