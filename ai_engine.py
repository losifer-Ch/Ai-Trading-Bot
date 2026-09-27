"""
ai_engine.py
------------
A lightweight, explainable decision engine. It is intentionally simple
and auditable (moving-average crossover + RSI confirmation) rather than
a black box, because a risk-first trading tool must be able to explain
every signal it produces in plain language.

IMPORTANT: This is a rule-based decision-support heuristic for
demonstration purposes. It is NOT investment advice and carries no
guarantee of profitability. Markets are risky; past or simulated
performance does not predict future results.
"""

from dataclasses import dataclass
from typing import List, Literal

Signal = Literal["BUY", "SELL", "HOLD"]


@dataclass
class AIDecision:
    signal: Signal
    confidence: float          # 0-100
    reasoning: str
    short_ma: float
    long_ma: float
    rsi: float


def _sma(values: List[float], window: int) -> float:
    """Simple moving average over the last `window` samples."""
    if len(values) < window:
        window = len(values)
    if window == 0:
        return 0.0
    return sum(values[-window:]) / window


def _rsi(values: List[float], period: int) -> float:
    """Relative Strength Index over the last `period` deltas."""
    if len(values) < 2:
        return 50.0
    period = min(period, len(values) - 1)
    deltas = [values[i] - values[i - 1] for i in range(len(values) - period, len(values))]
    gains = [d for d in deltas if d > 0]
    losses = [-d for d in deltas if d < 0]
    avg_gain = (sum(gains) / period) if gains else 0.0001
    avg_loss = (sum(losses) / period) if losses else 0.0001
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))


class AIDecisionEngine:
    """Analyzes recent price history and produces a trading signal."""

    def __init__(self, short_window: int, long_window: int, rsi_period: int,
                 rsi_overbought: float, rsi_oversold: float):
        self.short_window = short_window
        self.long_window = long_window
        self.rsi_period = rsi_period
        self.rsi_overbought = rsi_overbought
        self.rsi_oversold = rsi_oversold

    def analyze(self, price_history: List[float]) -> AIDecision:
        if len(price_history) < 3:
            return AIDecision("HOLD", 0.0, "Insufficient data to form a signal yet.", 0, 0, 50)

        short_ma = _sma(price_history, self.short_window)
        long_ma = _sma(price_history, self.long_window)
        rsi = _rsi(price_history, self.rsi_period)

        trend_bullish = short_ma > long_ma
        spread_pct = abs(short_ma - long_ma) / long_ma * 100 if long_ma else 0

        # Combine trend crossover with RSI as a confirmation filter, so a
        # single noisy indicator can't produce a signal on its own.
        if trend_bullish and rsi < self.rsi_overbought:
            signal: Signal = "BUY"
            confidence = min(95.0, 50 + spread_pct * 8 + (self.rsi_overbought - rsi) / 4)
            reasoning = (f"Short-term average (${short_ma:,.2f}) is above the long-term "
                         f"average (${long_ma:,.2f}); RSI at {rsi:.1f} is not yet overbought.")
        elif not trend_bullish and rsi > self.rsi_oversold:
            signal = "SELL"
            confidence = min(95.0, 50 + spread_pct * 8 + (rsi - self.rsi_oversold) / 4)
            reasoning = (f"Short-term average (${short_ma:,.2f}) is below the long-term "
                         f"average (${long_ma:,.2f}); RSI at {rsi:.1f} is not yet oversold.")
        else:
            signal = "HOLD"
            confidence = 40.0
            reasoning = f"Mixed signals — RSI at {rsi:.1f} conflicts with the moving-average trend."

        return AIDecision(signal, round(confidence, 1), reasoning, short_ma, long_ma, rsi)
