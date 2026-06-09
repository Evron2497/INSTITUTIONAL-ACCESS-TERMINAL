import os
from datetime import datetime, timezone
import time
import json
import numpy as np
import pandas as pd
import requests
import streamlit as st
import plotly.graph_objects as go
import yfinance as yf
import streamlit.components.v1 as components

# =====================================================
# PREMIUM HIGH-END CYBER INDUSTRIAL THEME ARCHITECTURE
# =====================================================
st.set_page_config(page_title="QUANTUM VECTOR MATRIX", page_icon="⚡", layout="wide")

st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght=300;400;500;600;700&family=JetBrains+Mono:wght=400;500;700&display=swap');
        
        /* Base Configuration Elements */
        html, body, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
            background-color: #060913 !important;
            font-family: 'Plus Jakarta Sans', sans-serif !important;
            color: #F1F5F9 !important;
        }
        
        /* Custom Container Blocks (Cards) */
        .premium-card {
            background: linear-gradient(135deg, rgba(15, 23, 42, 0.6) 0%, rgba(30, 41, 59, 0.4) 100%);
            border: 1px solid rgba(255, 255, 255, 0.05);
            border-radius: 16px;
            padding: 24px;
            box-shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.7);
            backdrop-filter: blur(12px);
            margin-bottom: 20px;
        }
        
        /* Sidebar Restructuring */
        [data-testid="stSidebar"] {
            background-color: #0B0F19 !important;
            border-right: 1px solid rgba(255, 255, 255, 0.03) !important;
        }
        
        /* Typography System Overhaul */
        .terminal-super-title {
            font-size: 2.2rem;
            font-weight: 700;
            letter-spacing: -0.04em;
            background: linear-gradient(135deg, #00F0FF 0%, #7000FF 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 4px;
        }
        
        .terminal-subtitle {
            font-size: 0.95rem;
            color: #64748B;
            font-weight: 400;
            margin-top: 0px;
            margin-bottom: 30px;
            text-transform: uppercase;
            letter-spacing: 0.1em;
        }
        
        /* Streamlit Core Components Override */
        div[data-testid="stMetricSimpleNormal"] {
            background: rgba(15, 23, 42, 0.8) !important;
            border: 1px solid rgba(255, 255, 255, 0.04) !important;
            border-radius: 12px !important;
            padding: 20px !important;
        }
        
        div[data-testid="stMetricLabel"] {
            font-size: 0.75rem !important;
            text-transform: uppercase !important;
            letter-spacing: 0.08em !important;
            color: #94A3B8 !important;
            font-weight: 600;
        }

        /* Metric Value Text Color Rules */
        div[data-testid="stMetricValue"] {
            font-family: 'JetBrains Mono', monospace !important;
            font-weight: 700 !important;
            color: #FFFFFF !important;
        }
        
        /* Buttons Action Suite styling */
        .stButton>button {
            background: linear-gradient(90deg, #4F46E5 0%, #7C3AED 100%) !important;
            color: #FFFFFF !important;
            border: none !important;
            border-radius: 10px !important;
            font-weight: 600 !important;
            font-size: 0.9rem !important;
            padding: 12px 24px !important;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
            box-shadow: 0 4px 12px rgba(79, 70, 229, 0.3) !important;
        }
        
        .stButton>button:hover {
            transform: translateY(-2px) !important;
            box-shadow: 0 6px 20px rgba(0, 240, 255, 0.4) !important;
            background: linear-gradient(90deg, #00F0FF 0%, #7C3AED 100%) !important;
        }

        /* Custom Table & Dataframes adjustments */
        div[data-testid="stDataFrame"] {
            border: 1px solid rgba(255, 255, 255, 0.03) !important;
            border-radius: 12px !important;
            overflow: hidden;
        }
    </style>
""", unsafe_allow_html=True)

# =====================================================
# SECURITY LAYER ACCESS AUTHENTICATION
# =====================================================
USERNAME = st.secrets.get("USERNAME", "")
PASSWORD = st.secrets.get("PASSWORD", "")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "shared_prediction" not in st.session_state:
    st.session_state.shared_prediction = {
        "signal": "NEUTRAL", "confidence": 0, "entry": 0, "tp": 0, "sl": 0,
        "pips": 0, "rsi": 50, "structure": "INITIALIZING", "buy_score": 0, "sell_score": 0,
        "session": "UNKNOWN", "timestamp": "", "recent_high": 0, "recent_low": 0
    }

def login():
    st.markdown('<div class="premium-card" style="max-width: 450px; margin: 100px auto;">', unsafe_allow_html=True)
    st.markdown('<h2 class="terminal-super-title" style="font-size: 1.8rem; text-align: center;">🏦 CORE SECURITY PASS</h2>', unsafe_allow_html=True)
    st.markdown('<p class="terminal-subtitle" style="text-align: center; margin-bottom: 20px;">Identity Verification Stream</p>', unsafe_allow_html=True)
    u = st.text_input("Security ID Token")
    p = st.text_input("Matrix Password Access", type="password")
    st.markdown('<div style="margin-top: 20px;">', unsafe_allow_html=True)
    if st.button("Authenticate Terminal Connection"):
        if u == USERNAME and p == PASSWORD:
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error("Trace Failure: Invalid Security Key Signature")
    st.markdown('</div></div>', unsafe_allow_html=True)

if not st.session_state.logged_in:
    login()
    st.stop()

# =====================================================
# BACKGROUND DATA STREAMING INFRASTRUCTURE
# =====================================================
st.sidebar.markdown("<div style='padding: 10px 0px;'><b style='color:#00F0FF; font-size:1.1rem;'>🛰️ MATRIX NET</b></div>", unsafe_allow_html=True)
pairs = ["EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "XAUUSD"]
selected_pair = st.sidebar.selectbox("Active Asset Stream Target", pairs)

BOT_TOKEN = st.secrets.get("BOT_TOKEN", "")
CHAT_IDS  = st.secrets.get("CHAT_IDS", [])

def send_telegram(message: str):
    if not BOT_TOKEN or not CHAT_IDS: return False, "Telegram vectors unconfigured."
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    errors = []
    for chat_id in CHAT_IDS:
        try:
            r = requests.post(url, data={"chat_id": chat_id, "text": message, "parse_mode": "HTML"}, timeout=10)
            if r.status_code != 200: errors.append(f"Chat {chat_id}: {r.text}")
        except Exception as e: errors.append(str(e))
    return (len(errors) == 0), "; ".join(errors)

@st.cache_data(ttl=10)
def fetch_ticker_backbone(symbol, period, interval):
    mapping = {"EURUSD": "EURUSD=X", "GBPUSD": "GBPUSD=X", "USDJPY": "JPY=X", "AUDUSD": "AUDUSD=X", "XAUUSD": "GC=F"}
    ticker = mapping.get(symbol)
    try:
        df = yf.download(ticker, period=period, interval=interval, progress=False)
        if df is None or df.empty: return pd.DataFrame()
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
        df_res = df.reset_index()
        t_col = "Datetime" if "Datetime" in df_res.columns else "Date"
        return pd.DataFrame({
            "time": df_res[t_col].squeeze(), "Open": df_res["Open"].squeeze().astype(float),
            "High": df_res["High"].squeeze().astype(float), "Low": df_res["Low"].squeeze().astype(float),
            "Close": df_res["Close"].squeeze().astype(float), "Volume": df_res["Volume"].squeeze().astype(float)
        }).dropna().reset_index(drop=True)
    except Exception: return pd.DataFrame()

# =====================================================
# ALGORITHMIC LOGIC MATHEMATICAL PROCESSING
# =====================================================
def calculate_swing_pivots(df: pd.DataFrame, left=5, right=5) -> pd.DataFrame:
    df = df.copy().reset_index(drop=True)
    roll_high = df["High"].rolling(window=left + right + 1, center=True).max()
    roll_low = df["Low"].rolling(window=left + right + 1, center=True).min()
    df["Swing_High"] = np.where(df["High"] == roll_high, df["High"], np.nan)
    df["Swing_Low"] = np.where(df["Low"] == roll_low, df["Low"], np.nan)
    return df

def calculate_atr(df, period=14):
    if len(df) < period: return 0.001
    h_l = df["High"] - df["Low"]
    h_pc = abs(df["High"] - df["Close"].shift(1))
    l_pc = abs(df["Low"] - df["Close"].shift(1))
    tr = pd.concat([h_l, h_pc, l_pc], axis=1).max(axis=1)
    atr = tr.rolling(period).mean().iloc[-1]
    return atr if not np.isnan(atr) else 0.001

def rsi(df, period=14):
    if len(df) < period: return 50.0
    delta = df["Close"].diff()
    gain = delta.clip(lower=0).rolling(period).mean()
    loss = (-delta.clip(upper=0)).rolling(period).mean()
    l_gain, l_loss = gain.iloc[-1], loss.iloc[-1]
    if l_loss == 0: return 100.0 if l_gain > 0 else 50.0
    return round(100 - (100 / (1 + (l_gain / l_loss))), 2)

def trading_session():
    hour = datetime.now(timezone.utc).hour
    if 0 <= hour < 7: return "ASIAN (ACCUMULATION)"
    elif 7 <= hour < 13: return "LONDON (MANIPULATION)"
    elif 13 <= hour < 21: return "NEW YORK (DISTRIBUTION)"
    return "CLOSED"

def detect_true_liquidity_sweeps(df_ltf, df_htf):
    prev_macro_high = df_htf["High"].iloc[-2]
    prev_macro_low = df_htf["Low"].iloc[-2]
    current_high = df_ltf["High"].iloc[-1]
    current_low = df_ltf["Low"].iloc[-1]
    current_close = df_ltf["Close"].iloc[-1]
    return (current_high > prev_macro_high and current_close < prev_macro_high), (current_low < prev_macro_low and current_close > prev_macro_low)

def detect_volume_weighted_fvg(df):
    if len(df) < 3: return False, False, 0
    avg_vol = df["Volume"].tail(20).mean()
    trigger_vol = df["Volume"].iloc[-2]
    is_institutional_displacement = trigger_vol > (avg_vol * 2.0) if avg_vol > 0 else False
    fvg_buy = df["Low"].iloc[-1] > df["High"].iloc[-3] and df["Close"].iloc[-2] > df["Open"].iloc[-2]
    fvg_sell = df["High"].iloc[-1] < df["Low"].iloc[-3] and df["Close"].iloc[-2] < df["Open"].iloc[-2]
    return fvg_buy, fvg_sell, (2.5 if is_institutional_displacement else 1.0)

def predictive_matrix_engine(pair):
    df_ltf = fetch_ticker_backbone(pair, period="5d", interval="15m")
    df_itf = fetch_ticker_backbone(pair, period="15d", interval="1h")
    df_htf = fetch_ticker_backbone(pair, period="30d", interval="4h")

    if df_ltf.empty or df_itf.empty or df_htf.empty or len(df_ltf) < 40 or len(df_htf) < 20:
        return {
            "signal": "NEUTRAL", "confidence": 0, "entry": 0, "tp": 0, "sl": 0, "pips": 0, "rsi": 50,
            "structure": "DATA FEED STABILIZING MATRIX", "buy_score": 0, "sell_score": 0,
            "session": trading_session(), "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "recent_high": 0, "recent_low": 0
        }

    htf_ema = df_htf["Close"].ewm(span=20).mean().iloc[-1]
    itf_ema = df_itf["Close"].ewm(span=20).mean().iloc[-1]
    htf_bias = "BULLISH" if (df_htf["Close"].iloc[-1] > htf_ema and df_itf["Close"].iloc[-1] > itf_ema) else ("BEARISH" if (df_htf["Close"].iloc[-1] < htf_ema and df_itf["Close"].iloc[-1] < itf_ema) else "NEUTRAL")

    df_ltf = calculate_swing_pivots(df_ltf, left=5, right=5)
    recent_high, recent_low = float(df_ltf["High"].tail(30).max()), float(df_ltf["Low"].tail(30).min())
    price, atr_val = float(df_ltf["Close"].iloc[-1]), calculate_atr(df_ltf)

    sweep_bsl, sweep_ssl = detect_true_liquidity_sweeps(df_ltf, df_htf)
    fvg_buy, fvg_sell, vol_multiplier = detect_volume_weighted_fvg(df_ltf)

    buy_score = (30 if htf_bias == "BULLISH" else 0) + (25 if sweep_ssl else 0) + (int(15 * vol_multiplier) if fvg_buy else 0)
    sell_score = (30 if htf_bias == "BEARISH" else 0) + (25 if sweep_bsl else 0) + (int(15 * vol_multiplier) if fvg_sell else 0)

    midpoint = recent_low + ((recent_high - recent_low) * 0.5)
    if price > midpoint: buy_score = int(buy_score * 0.5)
    if price < midpoint: sell_score = int(sell_score * 0.5)

    signal = "NEUTRAL"
    if buy_score >= 65 and htf_bias == "BULLISH": signal = "STRONG BUY"
    elif buy_score >= 45 and htf_bias == "BULLISH": signal = "BUY"
    elif sell_score >= 65 and htf_bias == "BEARISH": signal = "STRONG SELL"
    elif sell_score >= 45 and htf_bias == "BEARISH": signal = "SELL"

    pip_mult = 0.01 if "JPY" in pair.upper() else (0.10 if "XAU" in pair.upper() else 0.0001)
    sl = (df_ltf["Low"].tail(5).min() - (1 * pip_mult)) if "BUY" in signal else ((df_ltf["High"].tail(5).max() + (1 * pip_mult)) if "SELL" in signal else price)
    tp = recent_high if "BUY" in signal else (recent_low if "SELL" in signal else price)
    
    if "BUY" in signal and (tp - price) < (10 * pip_mult): tp = price + (atr_val * 3)
    if "SELL" in signal and (price - tp) < (10 * pip_mult): tp = price - (atr_val * 3)

    return {
        "signal": signal, "confidence": min(max(buy_score, sell_score), 100), "entry": round(price, 5),
        "tp": round(tp, 5), "sl": round(sl, 5), "pips": (round(abs(tp - price) / pip_mult, 1) if signal != "NEUTRAL" else 0), "rsi": round(rsi(df_ltf), 1),
        "structure": f"HTF Confluence: {htf_bias} | Volume: {vol_multiplier}x", "buy_score": buy_score, "sell_score": sell_score,
        "session": trading_session(), "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "recent_high": round(recent_high, 5), "recent_low": round(recent_low, 5)
    }

# =====================================================
# MODERNIZE VISUALS INFRASTRUCTURE COMPONENT FRAGMENTS
# =====================================================
@st.fragment(run_every=5)
def render_live_dashboard(pair):
    market_data = fetch_ticker_backbone(pair, period="5d", interval="15m")
    if market_data.empty: return

    result = predictive_matrix_engine(pair)
    st.session_state.shared_prediction = result

    # Chart Processing styling setup
    plot_df = market_data.tail(90)
    fig = go.Figure()
    fig.add_trace(go.Candlestick(
        x=plot_df["time"], open=plot_df["Open"], high=plot_df["High"], low=plot_df["Low"], close=plot_df["Close"], name=pair,
        increasing_line_color='#10B981', increasing_fillcolor='#10B981',
        decreasing_line_color='#EF4444', decreasing_fillcolor='#EF4444'
    ))
    
    if result["recent_high"] > 0:
        fig.add_hline(y=result["recent_high"], line_dash="dash", line_color="rgba(245, 158, 11, 0.4)", annotation_text="BSL Pool")
        fig.add_hline(y=result["recent_low"],  line_dash="dash", line_color="rgba(6, 182, 212, 0.4)", annotation_text="SSL Pool")

    fig.update_layout(
        template="plotly_dark", height=460, xaxis_rangeslider_visible=False, uirevision="keep",
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(15, 23, 42, 0.5)',
        margin=dict(l=8, r=8, t=10, b=10)
    )
    fig.update_xaxes(showgrid=False, bordercolor="rgba(255,255,255,0.05)")
    fig.update_yaxes(showgrid=True, gridcolor='rgba(255,255,255,0.03)', side="right")
    
    # Render Layout Wrap Card
    st.markdown('<div class="premium-card">', unsafe_allow_html=True)
    st.markdown(f"<div style='display:flex; justify-content:space-between; margin-bottom:15px;'><b style='font-size:1.2rem; color:#FFFFFF;'>📊 QUANT ENGINE DATA TRACK</b><span style='font-family:JetBrains Mono; color:#64748B;'>{result['timestamp']}</span></div>", unsafe_allow_html=True)
    st.plotly_chart(fig, use_container_width=True)
    
    # Metrics System Grid Layout Wrap
    st.markdown("<div style='margin-top:25px;'></div>", unsafe_allow_html=True)
    color_hex = "#10B981" if "BUY" in result["signal"] else ("#EF4444" if "SELL" in signal else "#94A3B8")
    
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.markdown(f"<div data-testid='stMetricSimpleNormal'><div data-testid='stMetricLabel'>Validated Signal Execution</div><div style='font-size:1.15rem; font-weight:700; color:{color_hex};'>{result['signal']}</div></div>", unsafe_allow_html=True)
    with c2: st.markdown(f"<div data-testid='stMetricSimpleNormal'><div data-testid='stMetricLabel'>Matrix Confidence Metric</div><div style='font-size:1.4rem; font-weight:700; color:#06B6D4; font-family:JetBrains Mono;'>{result['confidence']}%</div></div>", unsafe_allow_html=True)
    with c3: st.markdown(f"<div data-testid='stMetricSimpleNormal'><div data-testid='stMetricLabel'>Target Pip Range Deviation</div><div style='font-size:1.4rem; font-weight:700; color:#F59E0B; font-family:JetBrains Mono;'>{result['pips']} Pips</div></div>", unsafe_allow_html=True)
    with c4: st.markdown(f"<div data-testid='stMetricSimpleNormal'><div data-testid='stMetricLabel'>Institutional Structure</div><div style='font-size:0.85rem; font-weight:500; color:#E2E8F0; margin-top:4px;'>{result['structure']}</div></div>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

@st.fragment(run_every=12)
def render_scanner_block():
    st.markdown('<div class="premium-card" style="height:100%;">', unsafe_allow_html=True)
    st.markdown("<b style='font-size:1.1rem; color:#FFFFFF; display:block; margin-bottom:15px;'>📡 NETWORK CROSS-ASSET MONITOR</b>", unsafe_allow_html=True)
    
    scan_results = []
    for p in pairs:
        try:
            res = predictive_matrix_engine(p)
            scan_results.append([p, res["signal"], f"{res['confidence']}%", res["pips"]])
        except Exception:
            scan_results.append([p, "ERR", "—", 0])
            
    df = pd.DataFrame(scan_results, columns=["Asset", "Vector State", "Confidence", "Target Pips"])
    st.dataframe(df, use_container_width=True, hide_index=True)
    st.markdown('</div>', unsafe_allow_html=True)

@st.fragment
def render_broadcast_hub(pair):
    st.markdown('<div class="premium-card">', unsafe_allow_html=True)
    st.markdown("<b style='font-size:1.1rem; color:#FFFFFF; display:block; margin-bottom:15px;'>📩 INSTANT REUTER MATRIX BROADCAST DISPATCHER</b>", unsafe_allow_html=True)
    
    c_check = st.checkbox("Confirm system structural verification execution parameters align with core protocol rules.")
    if st.button("EXECUTE BROADCAST ROUTER TRANSMISSION"):
        current_result = st.session_state.shared_prediction
        if not c_check:
            st.warning("Aborted: Verification protocol clearance checked value required.")
        elif "NEUTRAL" in current_result["signal"]:
            st.error("Execution Failure: Neutral vector signals cannot be transmitted down-channel.")
        else:
            msg = f"<b>🏦 QUANT VECTOR TERMINAL</b>\nASSET: {pair}\nSTATE: <b>{current_result['signal']}</b>\nCONFIDENCE: {current_result['confidence']}%\n\nENTRY: {current_result['entry']}\nTP: {current_result['tp']} | SL: {current_result['sl']}\n\nTARGET: <b>{current_result['pips']} Pips</b>"
            ok, err = send_telegram(msg)
            if ok: st.success("Vector Payload Transmitted Successfully.")
            else: st.error(f"Routing Error: {err}")
    st.markdown('</div>', unsafe_allow_html=True)

# =====================================================
# INTERFACE MAIN VIEW ASSEMBLY CONSTRUX
# =====================================================
st.markdown('<h1 class="terminal-super-title">TECH-STAR</h1>', unsafe_allow_html=True)
st.markdown('<p class="terminal-subtitle">High-Fidelity Quantitative Institutional Core</p>', unsafe_allow_html=True)

grid_col_left, grid_col_right = st.columns([2.0, 1.0])

with grid_col_left:
    render_live_dashboard(selected_pair)

with grid_col_right:
    render_scanner_block()
    render_broadcast_hub(selected_pair)

# Interactive Technical Execution Layer Widget Frame
st.markdown("<div style='margin-top:10px;'></div>", unsafe_allow_html=True)
st.markdown('<div class="premium-card">', unsafe_allow_html=True)
st.markdown("<b style='font-size:1.1rem; color:#FFFFFF; display:block; margin-bottom:15px;'>📊 LIVE INTERACTIVE ORDER BOOK GRAPH MATRIX</b>", unsafe_allow_html=True)
tradingview_html = f"""
<div id="tv_chart" style="height: 480px; width: 100%;"></div>
<script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
<script type="text/javascript">
new TradingView.widget({{
  "autosize": true, "symbol": "OANDA:{selected_pair}", "interval": "15",
  "container_id": "tv_chart", "theme": "dark", "style": "1", "locale": "en",
  "toolbar_bg": "#0B0F19", "enable_publishing": false, "hide_side_toolbar": false, "allow_symbol_change": true
}});
</script>"""
components.html(tradingview_html, height=490, scrolling=False)
st.markdown('</div>', unsafe_allow_html=True)
