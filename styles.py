"""
styles.py
---------
All custom CSS for the "Black & Red" cyberpunk cockpit theme lives here,
kept apart from layout logic so the visual identity can be tuned without
touching app.py. Returns a single <style> block to inject via st.markdown.
"""

from config import ThemeConfig


def build_css(theme: ThemeConfig) -> str:
    return f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@500;700&display=swap');

    /* ---------- Global canvas ---------- */
    .stApp {{
        background:
            radial-gradient(circle at 15% 0%, rgba(239, 68, 68, 0.08) 0%, transparent 45%),
            radial-gradient(circle at 85% 100%, rgba(153, 27, 27, 0.10) 0%, transparent 50%),
            {theme.bg_primary};
        color: {theme.text_primary};
        font-family: 'Inter', 'Segoe UI', sans-serif;
    }}

    /* Hide default Streamlit chrome for a cleaner cockpit feel */
    #MainMenu, footer, header {{visibility: hidden;}}

    /* ---------- Sidebar ---------- */
    section[data-testid="stSidebar"] {{
        background: {theme.bg_secondary};
        border-right: 1px solid {theme.border};
    }}
    section[data-testid="stSidebar"] * {{
        color: {theme.text_primary} !important;
    }}
    section[data-testid="stSidebar"] .stCaption, section[data-testid="stSidebar"] small {{
        color: {theme.text_muted} !important;
    }}
    section[data-testid="stSidebar"] hr {{
        border-color: {theme.border};
    }}
    /* Sidebar sliders / inputs pick up the red accent */
    section[data-testid="stSidebar"] [data-baseweb="slider"] div[role="slider"] {{
        background-color: {theme.red_bright} !important;
        box-shadow: 0 0 8px rgba(239, 68, 68, 0.6);
    }}
    section[data-testid="stSidebar"] input, section[data-testid="stSidebar"] textarea {{
        background: rgba(255,255,255,0.03) !important;
        border: 1px solid {theme.border} !important;
        color: {theme.text_primary} !important;
    }}

    /* ---------- Typography ---------- */
    h1, h2, h3, h4 {{
        font-weight: 700;
        letter-spacing: 0.02em;
        color: {theme.text_primary};
    }}
    .obsidian-title {{
        font-size: 2.3rem;
        font-weight: 800;
        letter-spacing: 0.06em;
        background: linear-gradient(90deg, {theme.text_primary} 0%, {theme.red_bright} 60%, {theme.red_crimson} 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0;
        text-shadow: 0 0 30px rgba(239, 68, 68, 0.25);
    }}
    .obsidian-subtitle {{
        color: {theme.text_muted};
        font-size: 0.85rem;
        font-family: 'JetBrains Mono', monospace;
        margin-top: -4px;
        letter-spacing: 0.22em;
        text-transform: uppercase;
    }}

    /* ---------- Glassmorphism cards ---------- */
    .card {{
        background: {theme.card_bg};
        backdrop-filter: blur(14px) saturate(130%);
        -webkit-backdrop-filter: blur(14px) saturate(130%);
        border: 1px solid {theme.card_border};
        border-radius: 18px;
        padding: 22px 24px;
        box-shadow:
            0 8px 32px rgba(0, 0, 0, 0.55),
            0 0 24px rgba(239, 68, 68, 0.06),
            inset 0 1px 0 rgba(255, 255, 255, 0.04);
        margin-bottom: 18px;
        transition: border-color 0.2s ease, box-shadow 0.2s ease;
    }}
    .card:hover {{
        border-color: rgba(239, 68, 68, 0.4);
        box-shadow:
            0 8px 32px rgba(0, 0, 0, 0.6),
            0 0 32px rgba(239, 68, 68, 0.14),
            inset 0 1px 0 rgba(255, 255, 255, 0.05);
    }}
    .card-label {{
        color: {theme.text_muted};
        font-size: 0.74rem;
        font-family: 'JetBrains Mono', monospace;
        text-transform: uppercase;
        letter-spacing: 0.14em;
        margin-bottom: 6px;
    }}
    .card-value {{
        font-size: 1.9rem;
        font-weight: 800;
        color: {theme.text_primary};
        font-family: 'JetBrains Mono', monospace;
    }}
    .card-sub {{
        font-size: 0.85rem;
        color: {theme.text_muted};
        margin-top: 4px;
    }}

    /* ---------- Status glows ---------- */
    .glow-emerald {{
        color: {theme.emerald};
        text-shadow: 0 0 14px rgba(34, 197, 94, 0.6);
    }}
    .glow-crimson {{
        color: {theme.crimson};
        text-shadow: 0 0 14px rgba(239, 68, 68, 0.65);
    }}
    .glow-gold, .glow-red {{
        color: {theme.red_bright};
        text-shadow: 0 0 14px rgba(239, 68, 68, 0.55);
    }}
    .glow-amber {{
        color: {theme.amber};
        text-shadow: 0 0 12px rgba(245, 158, 11, 0.5);
    }}

    /* ---------- Signal badge ---------- */
    .badge {{
        display: inline-block;
        padding: 6px 18px;
        border-radius: 999px;
        font-weight: 800;
        letter-spacing: 0.1em;
        font-size: 0.9rem;
        font-family: 'JetBrains Mono', monospace;
    }}
    .badge-buy {{
        background: rgba(34, 197, 94, 0.12);
        color: {theme.emerald};
        border: 1px solid rgba(34, 197, 94, 0.45);
        box-shadow: 0 0 16px rgba(34, 197, 94, 0.15);
    }}
    .badge-sell {{
        background: rgba(239, 68, 68, 0.14);
        color: {theme.red_bright};
        border: 1px solid rgba(239, 68, 68, 0.5);
        box-shadow: 0 0 16px rgba(239, 68, 68, 0.2);
    }}
    .badge-hold {{
        background: rgba(161, 161, 170, 0.10);
        color: {theme.text_muted};
        border: 1px solid rgba(161, 161, 170, 0.35);
    }}

    /* ---------- Disclaimer banner ---------- */
    .risk-banner {{
        background: linear-gradient(90deg, rgba(239, 68, 68, 0.14), rgba(153, 27, 27, 0.06));
        border: 1px solid rgba(239, 68, 68, 0.4);
        border-left: 4px solid {theme.red_bright};
        border-radius: 12px;
        padding: 14px 20px;
        margin-bottom: 22px;
        font-size: 0.87rem;
        color: {theme.text_primary};
        line-height: 1.5;
        box-shadow: 0 0 24px rgba(239, 68, 68, 0.08);
    }}
    .risk-banner b {{ color: {theme.red_bright}; }}

    /* ---------- Buttons ---------- */
    .stButton > button {{
        background: linear-gradient(135deg, {theme.red_bright} 0%, {theme.red_crimson} 100%);
        color: #ffffff;
        border: none;
        border-radius: 10px;
        font-weight: 700;
        font-size: 0.92rem;
        letter-spacing: 0.04em;
        padding: 0.55rem 1.2rem;
        box-shadow: 0 4px 18px rgba(239, 68, 68, 0.25);
        transition: all 0.18s ease;
    }}
    .stButton > button:hover {{
        transform: translateY(-1px);
        box-shadow: 0 6px 26px rgba(239, 68, 68, 0.5);
        filter: brightness(1.08);
    }}
    .stButton > button:active {{
        transform: translateY(0px);
        background: linear-gradient(135deg, {theme.red_crimson} 0%, {theme.red_dark} 100%);
    }}
    /* Secondary/toggle controls (Auto refresh, etc.) */
    .stToggle label div[data-checked="true"] {{
        background-color: {theme.red_bright} !important;
    }}

    /* ---------- Dataframe / table ---------- */
    [data-testid="stDataFrame"] {{
        border: 1px solid {theme.card_border};
        border-radius: 14px;
        overflow: hidden;
        box-shadow: 0 4px 20px rgba(0,0,0,0.4);
    }}

    /* ---------- Divider ---------- */
    .obsidian-divider {{
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(239, 68, 68, 0.35), transparent);
        margin: 22px 0;
        border: none;
    }}

    /* ---------- Progress bars ---------- */
    .stProgress > div > div > div {{
        background-image: linear-gradient(90deg, {theme.red_dark}, {theme.red_bright});
        box-shadow: 0 0 10px rgba(239, 68, 68, 0.5);
    }}
    .stProgress > div > div {{
        background-color: rgba(255,255,255,0.06);
    }}

    /* ---------- Metric label micro-styling ---------- */
    [data-testid="stMetricValue"] {{
        color: {theme.text_primary};
        font-family: 'JetBrains Mono', monospace;
    }}
</style>
"""
