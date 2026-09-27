"""
config.py
---------
Centralized configuration for the Obsidian AI Trading Agent.
Every tunable parameter lives here so the rest of the codebase never
hardcodes a "magic number" — everything flows from AppConfig.
"""

from dataclasses import dataclass, field
from typing import Dict


@dataclass
class RiskConfig:
    """Risk management parameters. These are the guardrails of the agent."""
    stop_loss_pct: float = 2.0         # Hard stop-loss, in percent below entry
    take_profit_pct: float = 5.0       # Take-profit target, in percent above entry
    position_size_usd: float = 1000.0  # Simulated position size
    max_daily_loss_pct: float = 6.0    # Session-wide circuit breaker


@dataclass
class MarketConfig:
    """Market data source parameters."""
    coin_id: str = "bitcoin"           # CoinGecko asset id
    vs_currency: str = "usd"
    history_days: int = 1              # lookback window for chart / indicators
    poll_interval_sec: int = 15        # suggested refresh cadence (seconds)


@dataclass
class AIConfig:
    """Parameters for the signal-generation engine."""
    short_window: int = 5              # short moving-average window (samples)
    long_window: int = 20              # long moving-average window (samples)
    rsi_period: int = 14
    rsi_overbought: float = 70.0
    rsi_oversold: float = 30.0


@dataclass
class ThemeConfig:
    """Black & Red visual identity — pitch-black cockpit + neon crimson glow."""
    bg_primary: str = "#000000"                     # true black canvas
    bg_secondary: str = "#09090b"                    # deep obsidian panel
    card_bg: str = "rgba(17, 17, 20, 0.55)"          # glassmorphism card fill
    card_border: str = "rgba(239, 68, 68, 0.20)"     # neon-red glass edge
    border: str = "rgba(239, 68, 68, 0.15)"          # hairline dividers
    red_bright: str = "#ef4444"                       # electric neon red — primary accent
    red_crimson: str = "#dc2626"                      # deep crimson — secondary accent
    red_dark: str = "#991b1b"                         # deep red — hover / pressed states
    text_primary: str = "#ffffff"                     # crisp white headers
    text_muted: str = "#a1a1aa"                        # soft metallic grey
    emerald: str = "#22c55e"                           # profit / safe status glow
    crimson: str = "#ef4444"                           # loss / danger status glow
    amber: str = "#f59e0b"                             # caution / simulated-data glow


@dataclass
class AppConfig:
    risk: RiskConfig = field(default_factory=RiskConfig)
    market: MarketConfig = field(default_factory=MarketConfig)
    ai: AIConfig = field(default_factory=AIConfig)
    theme: ThemeConfig = field(default_factory=ThemeConfig)
    api_key: str = ""                  # Optional: CoinGecko Pro key
    demo_mode: bool = True              # Use simulated feed if live API fails


# Assets selectable in the sidebar, mapped to their CoinGecko ids.
SUPPORTED_ASSETS: Dict[str, str] = {
    "Bitcoin (BTC)": "bitcoin",
    "Ethereum (ETH)": "ethereum",
    "Solana (SOL)": "solana",
    "BNB": "binancecoin",
    "XRP": "ripple",
}
