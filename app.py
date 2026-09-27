"""
app.py
------
Obsidian — AI Trading Agent
A risk-first, "Luxury & Comfort" themed trading dashboard.

Run with:
    streamlit run app.py

This tool is a demonstration of algorithmic decision-support and risk
management UX. It does not execute real trades and is not financial
advice. See the on-screen risk disclaimer for details.
"""

import time
from datetime import datetime

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from config import AppConfig, SUPPORTED_ASSETS
from data_feed import PriceFeed
from ai_engine import AIDecisionEngine
from risk_manager import RiskManager
from styles import build_css

# --------------------------------------------------------------------------
# Page setup
# --------------------------------------------------------------------------
st.set_page_config(
    page_title="Obsidian — AI Trading Agent",
    page_icon="◆",
    layout="wide",
    initial_sidebar_state="expanded",
)


# --------------------------------------------------------------------------
# Session-state bootstrap
# --------------------------------------------------------------------------
def init_state():
    if "config" not in st.session_state:
        st.session_state.config = AppConfig()
    if "price_history" not in st.session_state:
        st.session_state.price_history = []   # list of (timestamp_ms, price)
    if "trade_log" not in st.session_state:
        st.session_state.trade_log = []        # list of dicts
    if "position_open" not in st.session_state:
        st.session_state.position_open = False
    if "risk_manager" not in st.session_state:
        cfg = st.session_state.config
        st.session_state.risk_manager = RiskManager(
            cfg.risk.stop_loss_pct, cfg.risk.take_profit_pct, cfg.risk.max_daily_loss_pct
        )
    if "last_coin_id" not in st.session_state:
        st.session_state.last_coin_id = st.session_state.config.market.coin_id


init_state()
cfg: AppConfig = st.session_state.config
rm: RiskManager = st.session_state.risk_manager

st.markdown(build_css(cfg.theme), unsafe_allow_html=True)


# --------------------------------------------------------------------------
# Sidebar — configurable control panel
# --------------------------------------------------------------------------
with st.sidebar:
    st.markdown("### ◆ Control Panel")
    st.caption("Every parameter below is live — changes apply on next refresh.")

    asset_label = st.selectbox("Asset", list(SUPPORTED_ASSETS.keys()), index=0)
    selected_coin_id = SUPPORTED_ASSETS[asset_label]
    cfg.market.coin_id = selected_coin_id

    # Reset history if the user switches assets, so the chart doesn't mix series.
    if selected_coin_id != st.session_state.last_coin_id:
        st.session_state.price_history = []
        st.session_state.last_coin_id = selected_coin_id

    st.markdown("---")
    st.markdown("**Risk Management**")
    cfg.risk.stop_loss_pct = st.slider("Stop-Loss (%)", 0.5, 15.0, cfg.risk.stop_loss_pct, 0.5)
    cfg.risk.take_profit_pct = st.slider("Take-Profit (%)", 0.5, 30.0, cfg.risk.take_profit_pct, 0.5)
    cfg.risk.max_daily_loss_pct = st.slider("Max Daily Loss (%)", 1.0, 20.0, cfg.risk.max_daily_loss_pct, 0.5)
    cfg.risk.position_size_usd = st.number_input("Position Size (USD)", 100.0, 1_000_000.0,
                                                  cfg.risk.position_size_usd, 100.0)

    # Keep the risk manager's live thresholds in sync with the sidebar.
    rm.stop_loss_pct = cfg.risk.stop_loss_pct
    rm.take_profit_pct = cfg.risk.take_profit_pct
    rm.max_daily_loss_pct = cfg.risk.max_daily_loss_pct

    st.markdown("---")
    st.markdown("**AI Engine**")
    cfg.ai.short_window = st.slider("Short MA window", 2, 20, cfg.ai.short_window)
    cfg.ai.long_window = st.slider("Long MA window", 5, 60, cfg.ai.long_window)

    st.markdown("---")
    st.markdown("**Data Source**")
    cfg.api_key = st.text_input("CoinGecko Pro API Key (optional)", value=cfg.api_key, type="password")
    st.caption("Leave blank to use the free public endpoint. A simulated feed "
               "activates automatically if the API is unreachable or rate-limited.")

    st.markdown("---")
    col_a, col_b = st.columns(2)
    with col_a:
        refresh_clicked = st.button("↻ Refresh", use_container_width=True)
    with col_b:
        auto_refresh = st.toggle("Auto", value=False)

    st.markdown("---")
    if not st.session_state.position_open:
        open_clicked = st.button("▲ Open Position", use_container_width=True)
    else:
        close_clicked = st.button("■ Close Position", use_container_width=True)


# --------------------------------------------------------------------------
# Header + risk disclaimer
# --------------------------------------------------------------------------
st.markdown('<div class="obsidian-title">OBSIDIAN</div>', unsafe_allow_html=True)
st.markdown('<div class="obsidian-subtitle">AI Trading Agent · Risk-First Terminal</div>',
            unsafe_allow_html=True)
st.write("")

st.markdown(
    """
    <div class="risk-banner">
        <b>Risk Warning:</b> Trading digital assets involves substantial risk of loss and is not
        suitable for every investor. Signals shown here are generated by a simplified,
        rule-based model for demonstration purposes only and do not constitute financial,
        investment, or trading advice. This dashboard does not execute real orders.
        Past or simulated performance is not indicative of future results. Only ever
        risk capital you can afford to lose, and consult a licensed financial advisor
        before making investment decisions.
    </div>
    """,
    unsafe_allow_html=True,
)


# --------------------------------------------------------------------------
# Pull live data
# --------------------------------------------------------------------------
feed = PriceFeed(cfg.market.coin_id, cfg.market.vs_currency, cfg.api_key)

if refresh_clicked or not st.session_state.price_history:
    hist = feed.get_history(cfg.market.history_days)
    st.session_state.price_history = hist

current_price, is_live = feed.get_live_price()
now_ms = int(time.time() * 1000)
st.session_state.price_history.append((now_ms, current_price))
st.session_state.price_history = st.session_state.price_history[-200:]  # cap memory

prices_only = [p for _, p in st.session_state.price_history]

# --------------------------------------------------------------------------
# AI signal
# --------------------------------------------------------------------------
engine = AIDecisionEngine(
    cfg.ai.short_window, cfg.ai.long_window, cfg.ai.rsi_period,
    cfg.ai.rsi_overbought, cfg.ai.rsi_oversold,
)
decision = engine.analyze(prices_only)

# --------------------------------------------------------------------------
# Handle sidebar position actions
# --------------------------------------------------------------------------
if not st.session_state.position_open and "open_clicked" in dir() and open_clicked:
    rm.open_position(current_price)
    st.session_state.position_open = True
    st.session_state.trade_log.append({
        "time": datetime.now().strftime("%H:%M:%S"),
        "action": "OPEN",
        "price": current_price,
        "pnl_pct": None,
    })

if st.session_state.position_open and "close_clicked" in dir() and close_clicked:
    risk_state_now = rm.evaluate(current_price)
    rm.register_close(risk_state_now.pnl_pct)
    st.session_state.position_open = False
    st.session_state.trade_log.append({
        "time": datetime.now().strftime("%H:%M:%S"),
        "action": "MANUAL CLOSE",
        "price": current_price,
        "pnl_pct": risk_state_now.pnl_pct,
    })

# --------------------------------------------------------------------------
# Evaluate risk guardrails — these ALWAYS override the AI signal
# --------------------------------------------------------------------------
risk_state = rm.evaluate(current_price)

if risk_state.action in ("STOP_LOSS", "TAKE_PROFIT") and st.session_state.position_open:
    rm.register_close(risk_state.pnl_pct)
    st.session_state.position_open = False
    st.session_state.trade_log.append({
        "time": datetime.now().strftime("%H:%M:%S"),
        "action": risk_state.action,
        "price": current_price,
        "pnl_pct": risk_state.pnl_pct,
    })
    if risk_state.action == "STOP_LOSS":
        st.toast("Hard stop-loss triggered — position closed.", icon="🛑")
    else:
        st.toast("Take-profit reached — position closed.", icon="✅")


# --------------------------------------------------------------------------
# Top metric cards
# --------------------------------------------------------------------------
data_badge = "LIVE" if is_live else "SIMULATED"
data_glow = "glow-emerald" if is_live else "glow-amber"  # emerald=live, amber=simulated feed

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="card">
        <div class="card-label">Live Price · {asset_label}</div>
        <div class="card-value">${current_price:,.2f}</div>
        <div class="card-sub {data_glow}">● {data_badge} FEED</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    badge_class = {"BUY": "badge-buy", "SELL": "badge-sell", "HOLD": "badge-hold"}[decision.signal]
    st.markdown(f"""
    <div class="card">
        <div class="card-label">AI Signal</div>
        <div class="card-value"><span class="badge {badge_class}">{decision.signal}</span></div>
        <div class="card-sub">Confidence: {decision.confidence:.0f}%</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    if st.session_state.position_open:
        pnl_class = "glow-emerald" if risk_state.pnl_pct >= 0 else "glow-crimson"
        st.markdown(f"""
        <div class="card">
            <div class="card-label">Open Position P/L</div>
            <div class="card-value {pnl_class}">{risk_state.pnl_pct:+.2f}%</div>
            <div class="card-sub">Entry: ${rm.entry_price:,.2f}</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="card">
            <div class="card-label">Position Status</div>
            <div class="card-value glow-red">FLAT</div>
            <div class="card-sub">No open position</div>
        </div>
        """, unsafe_allow_html=True)

with col4:
    session_class = "glow-emerald" if rm.session_realized_pnl_pct >= 0 else "glow-crimson"
    st.markdown(f"""
    <div class="card">
        <div class="card-label">Session Realized P/L</div>
        <div class="card-value {session_class}">{rm.session_realized_pnl_pct:+.2f}%</div>
        <div class="card-sub">Daily limit: -{cfg.risk.max_daily_loss_pct:.1f}%</div>
    </div>
    """, unsafe_allow_html=True)


# --------------------------------------------------------------------------
# Chart + AI reasoning
# --------------------------------------------------------------------------
st.markdown('<hr class="obsidian-divider">', unsafe_allow_html=True)
chart_col, reasoning_col = st.columns([2, 1])

with chart_col:
    st.markdown("#### Price Action")
    df = pd.DataFrame(st.session_state.price_history, columns=["ts", "price"])
    df["time"] = pd.to_datetime(df["ts"], unit="ms")

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["time"], y=df["price"], mode="lines", name="Price",
        line=dict(color=cfg.theme.red_bright, width=2.2),
        fill="tozeroy", fillcolor="rgba(239, 68, 68, 0.08)",
    ))
    if rm.entry_price is not None:
        fig.add_hline(y=rm.entry_price, line_dash="dot", line_color=cfg.theme.text_muted,
                       annotation_text="Entry", annotation_font_color=cfg.theme.text_muted)
        fig.add_hline(y=rm.entry_price * (1 - cfg.risk.stop_loss_pct / 100),
                       line_dash="dash", line_color=cfg.theme.crimson,
                       annotation_text="Stop-Loss", annotation_font_color=cfg.theme.crimson)
        fig.add_hline(y=rm.entry_price * (1 + cfg.risk.take_profit_pct / 100),
                       line_dash="dash", line_color=cfg.theme.emerald,
                       annotation_text="Take-Profit", annotation_font_color=cfg.theme.emerald)

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=cfg.theme.text_primary),
        margin=dict(l=10, r=10, t=10, b=10),
        height=380,
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor=cfg.theme.border, tickprefix="$"),
        showlegend=False,
    )
    st.plotly_chart(fig, use_container_width=True)

with reasoning_col:
    st.markdown("#### AI Reasoning")
    st.markdown(f"""
    <div class="card">
        <div class="card-sub">{decision.reasoning}</div>
        <br>
        <div class="card-label">Short MA</div>
        <div class="card-value" style="font-size:1.2rem;">${decision.short_ma:,.2f}</div>
        <div class="card-label" style="margin-top:10px;">Long MA</div>
        <div class="card-value" style="font-size:1.2rem;">${decision.long_ma:,.2f}</div>
        <div class="card-label" style="margin-top:10px;">RSI ({cfg.ai.rsi_period})</div>
        <div class="card-value" style="font-size:1.2rem;">{decision.rsi:.1f}</div>
    </div>
    """, unsafe_allow_html=True)


# --------------------------------------------------------------------------
# Risk status panel
# --------------------------------------------------------------------------
st.markdown('<hr class="obsidian-divider">', unsafe_allow_html=True)
st.markdown("#### Risk Guardrails")

r1, r2, r3 = st.columns(3)
with r1:
    st.markdown('<div class="card-label">Distance to Stop-Loss</div>', unsafe_allow_html=True)
    st.progress(rm.distance_to_stop_loss(current_price) / 100)
with r2:
    st.markdown('<div class="card-label">Distance to Take-Profit</div>', unsafe_allow_html=True)
    st.progress(rm.distance_to_take_profit(current_price) / 100)
with r3:
    st.markdown('<div class="card-label">Daily Loss Limit Used</div>', unsafe_allow_html=True)
    used = min(100.0, max(0.0, -rm.session_realized_pnl_pct / cfg.risk.max_daily_loss_pct * 100)) \
        if rm.session_realized_pnl_pct < 0 else 0.0
    st.progress(used / 100)

status_color = {
    "NONE": "glow-emerald", "STOP_LOSS": "glow-crimson",
    "TAKE_PROFIT": "glow-emerald", "DAILY_LIMIT": "glow-crimson",
}[risk_state.action]
st.markdown(f'<div class="{status_color}" style="margin-top:8px;">● {risk_state.message}</div>',
            unsafe_allow_html=True)


# --------------------------------------------------------------------------
# Trade log
# --------------------------------------------------------------------------
st.markdown('<hr class="obsidian-divider">', unsafe_allow_html=True)
st.markdown("#### Trade Log")

if st.session_state.trade_log:
    log_df = pd.DataFrame(st.session_state.trade_log)
    log_df["price"] = log_df["price"].map(lambda x: f"${x:,.2f}")
    log_df["pnl_pct"] = log_df["pnl_pct"].map(lambda x: f"{x:+.2f}%" if x is not None else "—")
    st.dataframe(log_df, use_container_width=True, hide_index=True)
else:
    st.caption("No trades yet this session.")


# --------------------------------------------------------------------------
# Auto-refresh loop
# --------------------------------------------------------------------------
if auto_refresh:
    time.sleep(cfg.market.poll_interval_sec)
    st.rerun()
