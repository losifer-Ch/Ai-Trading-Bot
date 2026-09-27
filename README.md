# Obsidian — AI Trading Agent

A risk-first, "Luxury & Comfort" themed crypto trading dashboard built with
Streamlit. Live price data, an explainable rule-based AI signal engine, and
hard-coded stop-loss / take-profit guardrails that always override the AI.

## Project structure

```
obsidian_trading_agent/
├── app.py            # Streamlit UI — layout, cards, chart, control flow
├── config.py         # All tunable parameters (risk, market, AI, theme)
├── data_feed.py       # CoinGecko live price + history, with offline fallback
├── ai_engine.py       # Moving-average / RSI signal generator (BUY/SELL/HOLD)
├── risk_manager.py    # Stop-loss, take-profit, daily loss circuit-breaker
├── styles.py          # Custom CSS for the obsidian + matte-gold theme
├── requirements.txt
└── README.md
```

## Setup

```bash
cd obsidian_trading_agent
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Run

```bash
streamlit run app.py
```

The app opens at `http://localhost:8501`.

## Notes

- **Live data**: uses the free public CoinGecko API by default. If you have a
  CoinGecko Pro key, paste it into the sidebar field to raise rate limits.
- **Offline resilience**: if the API call fails or is rate-limited, the app
  automatically switches to a simulated random-walk price feed and clearly
  labels the feed as "SIMULATED" so you're never misled about data quality.
- **Risk guardrails always win**: the stop-loss / take-profit checks run
  before the AI signal is ever displayed as actionable, and a triggered
  guardrail force-closes the simulated position regardless of what the AI
  engine says.
- **No real trades are executed.** This is a decision-support and UX
  demonstration only — wire in a real exchange API (e.g. via `ccxt`) at your
  own risk, and only after extensive paper-trading and testing.
- **Auto-refresh** uses `time.sleep` + `st.rerun()`, which blocks the script
  thread while sleeping (standard Streamlit pattern for polling UIs). For
  production use, consider `streamlit-autorefresh` or a websocket feed.

## Disclaimer

This software is provided for educational and demonstration purposes only.
It is not financial advice, and trading digital assets carries substantial
risk of loss. Always consult a licensed financial advisor before making
investment decisions.
