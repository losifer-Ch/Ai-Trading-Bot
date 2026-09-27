"""
risk_manager.py
---------------
The safety core of the agent. Nothing in this module is optional or
merely "advisory" — a stop-loss or take-profit breach here always
overrides any AI signal. Order of precedence in the app is:

    1. Daily loss circuit-breaker
    2. Hard stop-loss
    3. Take-profit
    4. AI signal (only consulted if none of the above fired)
"""

from dataclasses import dataclass
from typing import Literal, Optional

RiskAction = Literal["NONE", "STOP_LOSS", "TAKE_PROFIT", "DAILY_LIMIT"]


@dataclass
class RiskState:
    action: RiskAction
    pnl_pct: float
    message: str


class RiskManager:
    """Tracks an open position against configured stop-loss / take-profit levels."""

    def __init__(self, stop_loss_pct: float, take_profit_pct: float,
                 max_daily_loss_pct: float):
        self.stop_loss_pct = stop_loss_pct
        self.take_profit_pct = take_profit_pct
        self.max_daily_loss_pct = max_daily_loss_pct
        self.entry_price: Optional[float] = None
        self.session_realized_pnl_pct: float = 0.0

    def open_position(self, price: float) -> None:
        self.entry_price = price

    def close_position(self) -> None:
        self.entry_price = None

    def evaluate(self, current_price: float) -> RiskState:
        """Check the current price against every active guardrail, in priority order."""
        if self.session_realized_pnl_pct <= -abs(self.max_daily_loss_pct):
            return RiskState(
                "DAILY_LIMIT", self.session_realized_pnl_pct,
                "Daily loss limit reached — trading halted for this session."
            )

        if self.entry_price is None:
            return RiskState("NONE", 0.0, "No open position.")

        pnl_pct = (current_price - self.entry_price) / self.entry_price * 100

        if pnl_pct <= -abs(self.stop_loss_pct):
            return RiskState(
                "STOP_LOSS", pnl_pct,
                f"Hard stop-loss triggered at {pnl_pct:.2f}% — position closed automatically."
            )

        if pnl_pct >= abs(self.take_profit_pct):
            return RiskState(
                "TAKE_PROFIT", pnl_pct,
                f"Take-profit target reached at {pnl_pct:.2f}% — profit secured automatically."
            )

        return RiskState("NONE", pnl_pct, f"Position open — unrealized P/L {pnl_pct:+.2f}%.")

    def register_close(self, pnl_pct: float) -> None:
        """Roll a closed trade's P/L into the session total, then flatten the position."""
        self.session_realized_pnl_pct += pnl_pct
        self.close_position()

    def distance_to_stop_loss(self, current_price: float) -> float:
        """Returns 0-100, how close the current price is to hitting the stop-loss."""
        if self.entry_price is None:
            return 0.0
        pnl_pct = (current_price - self.entry_price) / self.entry_price * 100
        if pnl_pct >= 0:
            return 0.0
        return min(100.0, abs(pnl_pct) / abs(self.stop_loss_pct) * 100)

    def distance_to_take_profit(self, current_price: float) -> float:
        """Returns 0-100, how close the current price is to hitting take-profit."""
        if self.entry_price is None:
            return 0.0
        pnl_pct = (current_price - self.entry_price) / self.entry_price * 100
        if pnl_pct <= 0:
            return 0.0
        return min(100.0, pnl_pct / abs(self.take_profit_pct) * 100)
