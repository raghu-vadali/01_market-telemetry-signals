# app/api/schemas.py

from pydantic import BaseModel

class SignalMetrics(BaseModel):
    ticker: str
    current_price: float
    expected_return: float
    expected_price: float
    prob_gain: float
    prob_loss: float
    downside_95: float
    signal: str
    confidence: float

class SignalsResponse(BaseModel):
    signals: list[SignalMetrics]