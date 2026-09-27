"""
data_feed.py
------------
Handles all market-data acquisition. Wraps the public CoinGecko API and
falls back to a locally-simulated random-walk feed if the network call
fails (rate limit, no internet, invalid key, etc.) so the dashboard
never crashes mid-session — it just flags the data as "simulated".
"""

import time
import random
from typing import List, Tuple, Optional

import requests

COINGECKO_BASE = "https://api.coingecko.com/api/v3"


class PriceFeed:
    """Fetches live and historical price data for a given asset."""

    def __init__(self, coin_id: str, vs_currency: str = "usd", api_key: str = ""):
        self.coin_id = coin_id
        self.vs_currency = vs_currency
        self.api_key = api_key
        self._last_good_price: Optional[float] = None

    def _headers(self) -> dict:
        headers = {"accept": "application/json"}
        if self.api_key:
            headers["x-cg-pro-api-key"] = self.api_key
        return headers

    def get_live_price(self) -> Tuple[float, bool]:
        """
        Returns (price, is_live).
        is_live=False means the simulated fallback feed was used instead
        of a real network response.
        """
        try:
            url = f"{COINGECKO_BASE}/simple/price"
            params = {"ids": self.coin_id, "vs_currencies": self.vs_currency}
            resp = requests.get(url, params=params, headers=self._headers(), timeout=5)
            resp.raise_for_status()
            data = resp.json()
            price = float(data[self.coin_id][self.vs_currency])
            self._last_good_price = price
            return price, True
        except Exception:
            return self._simulate_price(), False

    def _simulate_price(self) -> float:
        """Random-walk fallback so the UI keeps functioning offline / rate-limited."""
        base = self._last_good_price or 65000.0
        drift = random.uniform(-0.004, 0.004)
        new_price = base * (1 + drift)
        self._last_good_price = new_price
        return new_price

    def get_history(self, days: int = 1) -> List[Tuple[float, float]]:
        """
        Returns a list of (timestamp_ms, price) tuples for charting.
        Falls back to a synthetic series if the API call fails.
        """
        try:
            url = f"{COINGECKO_BASE}/coins/{self.coin_id}/market_chart"
            params = {"vs_currency": self.vs_currency, "days": days}
            resp = requests.get(url, params=params, headers=self._headers(), timeout=6)
            resp.raise_for_status()
            data = resp.json()
            return [(p[0], p[1]) for p in data["prices"]]
        except Exception:
            return self._simulate_history()

    def _simulate_history(self, points: int = 60) -> List[Tuple[float, float]]:
        now_ms = int(time.time() * 1000)
        base = self._last_good_price or 65000.0
        series = []
        price = base
        for i in range(points):
            price *= (1 + random.uniform(-0.003, 0.003))
            ts = now_ms - (points - i) * 60_000
            series.append((ts, price))
        self._last_good_price = price
        return series
