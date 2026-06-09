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
# PAGE CONFIG & ULTRADARK PREMIUM CUSTOM STYLE
# =====================================================
st.set_page_config(page_title="CORE VECTOR MATRIX PRO", page_icon="🏦", layout="wide")

# Custom injection to build a clean neon-accented dark grid terminal ecosystem
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;600&family=Space+Grotesk:wght@400;500;600;700&display=swap');
        
        /* App Structure Core Overrides */
        html, body, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
            background-color: #060913 !important;
            font-family: 'Space Grotesk', sans-serif !important;
            color: #F1F5F9 !important;
        }
        
        /* Premium Dashboard Card Wrap Elements */
        .premium-card {
            background: linear-gradient(135deg, rgba(15, 23, 42, 0.6) 0%, rgba(30, 41, 59, 0.4) 100%);
            border: 1px solid rgba(255, 255, 255, 0.05);
            border-radius: 16px;
            padding: 24px;
            box-shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.7);
            backdrop-filter: blur(12px);
            margin-bottom: 20px;
        }
        
        /* Sidebar Styling Layout */
        [data-testid="stSidebar"] {
            background-color: #0B0F19 !important;
            border-right: 1px solid rgba(255, 255, 255, 0.03) !important;
        }
        
        /* Clean Header Architecture Elements */
        .terminal-header {
            font-family: 'Space Grotesk', sans-serif;
            font-weight: 700;
            background: linear-gradient(90deg, #00F0FF 0%, #7000FF 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            letter-spacing: -0.03em;
            margin-bottom: 4px;
        }
        
        .terminal-subheader {
            font-size: 0.95rem;
            color: #64748B;
            font-weight: 400;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            margin-top: 0px;
        }
        
        /* Overriding Custom Metrics Framework */
        div[data-testid="stMetric"] {
            background: rgba(15, 23, 42, 0.8) !important;
            border: 1px solid rgba(255, 255, 255, 0.04) !important;
            border-radius: 12px !important;
            padding: 15px !important;
        }
        
        div[data-testid="stMetricLabel"] {
            font-size: 0.75rem !important;
            text-transform: uppercase !important;
            letter-spacing: 0.08em !important;
            color: #94A3B8 !important;
            font-weight: 600;
        }
        
        /* Buttons Design Overhaul */
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
            width: 100% !important;
        }
        
        .stButton>button:hover {
            transform: translateY(-1px) !important;
            box-shadow: 0 6px 20px rgba(0, 240, 255, 0.4) !important;
            background: linear-gradient(90deg, #00F0FF 0%, #7C3AED 100%) !important;
        }

        div[data-testid="stDataFrame"] {
            border: 1px solid rgba(255, 255, 255, 0.03) !important;
            border-radius: 12px !important;
            overflow: hidden;
        }
    </style>
""", unsafe_allow_html=True)

# =====================================================
# SECURE IDENTITY GATEWAY LAYER
# =====================================================
USERNAME = st.secrets.get("USERNAME", "admin")
PASSWORD = st.secrets.get("PASSWORD", "matrix_pro_2026")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "shared_prediction" not in st.session_state:
    st.session_state.shared_prediction = {
        "signal": "NEUTRAL", "confidence": 0, "entry": 0, "tp": 0, "sl": 0,
        "pips": 0, "rsi": 50, "structure": "INITIALIZING", "buy_score": 0, "sell_score": 0,
        "session": "UNKNOWN", "timestamp": "", "recent_high": 0, "recent_low": 0
    }

def login():
    st.markdown('<div class="premium-card" style="max-width: 450px; margin: 80px auto 0px auto;">', unsafe_allow_html=True)
    st.markdown('<h2 class="terminal-header" style="font-size: 1.8rem; text-align: center;">🏦 CORE SECURITY GATE</h2>', unsafe_allow_html=True)
    st.markdown('<p class="terminal-subheader" style="text-align: center; margin-bottom: 25px;">Institutional Verification Required</p>', unsafe_allow_html=True)
    u = st.text_input("Security ID Token / User Key")
    p = st.text_input("Matrix Access Signature", type="password")
    st.markdown('<div style="margin-top: 15px;">', unsafe_allow_html=True)
    if st.button("Authenticate Connection Vector"):
        if u == USERNAME and p == PASSWORD:
            st.session_state.logged_in = True
            st.sidebar.success("Institutional Data Engaged")
            st.rerun()
        else:
            st.error("Authentication Vector Mismatch: Trace Flagged.")
    st.markdown('</div></div>', unsafe_allow_html=True)

if not st.session_state.logged_in:
    login()
    st.stop()

# =====================================================
# DATA STREAMING INFRASTRUCTURE BACKBONE
# =====================================================
st.sidebar.markdown("<div style='padding: 10px 0px;'><b style='color:#00F0FF; font-size:1.1rem;'>📡 PIPELINE STATUS</b></div>", unsafe_allow_html=True)

BOT_TOKEN = st.secrets.get("BOT_TOKEN", "")
CHAT_IDS  = st.secrets.get("CHAT_IDS", [])

def send_telegram(message: str):
    if not BOT_TOKEN or not CHAT_IDS:
        return False, "Telegram vectors unconfigured."
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    errors = []
    for chat_id in CHAT_IDS:
        try:
            r = requests.post(url, data={"chat_id": chat_id, "text": message, "parse_mode": "HTML"}, timeout=10)
            if r.status_code != 200:
                errors.append(f"Chat {chat_id}: {r.text}")
        except Exception as e:
            errors.append(str(e))
    return (len(errors) == 0), "; ".join(errors)

pairs = ["EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "XAUUSD"]
selected_pair = st.sidebar.selectbox("Active Stream Target", pairs)

@st.cache_data(ttl=10)
def fetch_ticker_backbone(symbol, period, interval):
    mapping = {
        "EURUSD": "EURUSD=X", "GBPUSD": "GBPUSD=X",
        "USDJPY": "JPY=X", "AUDUSD": "AUDUSD=X", "XAUUSD": "GC=F"
    }
    ticker = mapping.get(symbol)
    try:
        # Avoid MultiIndex column issues by forcing direct formatting
        df = yf.download(ticker, period=period, interval=interval, progress=False, group_by='ticker')
        if df is None or df.empty: 
            return pd.DataFrame()
        
        # Handle structural flattening if MultiIndex occurs
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(1)
            
        df_res = df.reset_index()
        t_col = "Datetime" if "Datetime" in df_res.columns else "Date"
        
        # Explicit serialization to prevent object-squeezing failures
        return pd.DataFrame({
            "time": df_res[t_col],
            "Open": df_res["Open"].astype(float),
            "High": df_res["High"].astype(float),
            "Low": df_res["Low"].astype(float),
            "Close": df_res["Close"].astype(float),
            "Volume": df_res["Volume"].astype(float) if "Volume" in df_res.columns else 0.0
        }).dropna().reset_index(drop=True)
    except Exception as e:
        st.sidebar.error(f"Stream Sync Error: {str(e)}")
        return pd.DataFrame()

# =====================================================
# ADVANCED STRUCTURAL QUANT MATH ALGORITHMS
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
    if len(df_htf) < 2 or len(df_ltf) < 1: return False, False
    prev_macro_high = df_htf["High"].iloc[-2]
    prev_macro_low = df_htf["Low"].iloc[-2]
    current_high = df_ltf["High"].iloc[-1]
    current_low = df_ltf["Low"].iloc[-1]
    current_close = df_ltf["Close"].iloc[-1]
    sweep_bsl = current_high > prev_macro_high and current_close < prev_macro_high
    sweep_ssl = current_low < prev_macro_low and current_close > prev_macro_low
    return sweep_bsl, sweep_ssl

def detect_volume_weighted_fvg(df):
    if len(df) < 3: return False, False, 1.0
    avg_vol = df["Volume"].tail(20).mean()
    trigger_vol = df["Volume"].iloc[-2]
    is_institutional_displacement = trigger_vol > (avg_vol * 2.0) if avg_vol > 0 else False
    volume_multiplier = 2.5 if is_institutional_displacement else 1.0
    fvg_buy = df["Low"].iloc[-1] > df["High"].iloc[-3] and df["Close"].iloc[-2] > df["Open"].iloc[-2]
    fvg_sell = df["High"].iloc[-1] < df["Low"].iloc[-3] and df["Close"].iloc[-2] < df["Open"].iloc[-2]
    return fvg_buy, fvg_sell, volume_multiplier

def detect_institutional_order_block(df):
    ob_bull = ob_bear = False
    if len(df) >= 5:
        candle = df.iloc[-3]
        next_two = df.iloc[-2:]
        if candle["Close"] < candle["Open"] and all(next_two["Close"] > next_two["Open"]): ob_bull = True
        if candle["Close"] > candle["Open"] and all(next_two["Close"] < next_two["Open"]): ob_bear = True
    return ob_bull, ob_bear

# =====================================================
# TRIPLE TIMEFRAME MATHEMATICAL EVALUATION MATRIX ENGINE
# =====================================================
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
    macro_bullish = df_htf["Close"].iloc[-1] > htf_ema and df_itf["Close"].iloc[-1] > itf_ema
    macro_bearish = df_htf["Close"].iloc[-1] < htf_ema and df_itf["Close"].iloc[-1] < itf_ema
    htf_bias = "BULLISH" if macro_bullish else ("BEARISH" if macro_bearish else "NEUTRAL")

    df_ltf = calculate_swing_pivots(df_ltf, left=5, right=5)
    recent_high = float(df_ltf["High"].tail(30).max())
    recent_low = float(df_ltf["Low"].tail(30).min())
    price = float(df_ltf["Close"].iloc[-1])
    atr_val = calculate_atr(df_ltf)

    sweep_bsl, sweep_ssl = detect_true_liquidity_sweeps(df_ltf, df_htf)
    fvg_buy, fvg_sell, vol_multiplier = detect_volume_weighted_fvg(df_ltf)
    ob_bull, ob_bear = detect_institutional_order_block(df_ltf)

    buy_score = 0
    sell_score = 0

    if htf_bias == "BULLISH": buy_score += 30
    if htf_bias == "BEARISH": sell_score += 30
    if sweep_ssl: buy_score += 25
    if sweep_bsl: sell_score += 25
    if fvg_buy: buy_score += int(15 * vol_multiplier)
    if fvg_sell: sell_score += int(15 * vol_multiplier)
    if ob_bull: buy_score += 15
    if ob_bear: sell_score += 15

    midpoint = recent_low + ((recent_high - recent_low) * 0.5)
    if price > midpoint: buy_score = int(buy_score * 0.5)
    if price < midpoint: sell_score = int(sell_score * 0.5)

    signal = "NEUTRAL"
    confidence = max(buy_score, sell_score)

    if buy_score >= 65 and htf_bias == "BULLISH": signal = "STRONG BUY"
    elif buy_score >= 45 and htf_bias == "BULLISH": signal = "BUY RE-ENTRY"
    elif sell_score >= 65 and htf_bias == "BEARISH": signal = "STRONG SELL"
    elif sell_score >= 45 and htf_bias == "BEARISH": signal = "SELL RE-ENTRY"

    entry = price
    pip_mult = 0.01 if "JPY" in pair.upper() else (0.10 if "XAU" in pair.upper() else 0.0001)

    if "BUY" in signal:
        sl = df_ltf["Low"].tail(5).min() - (1 * pip_mult)
        tp = recent_high
        if (tp - entry) < (10 * pip_mult): tp = entry + (atr_val * 3)
    elif "SELL" in signal:
        sl = df_ltf["High"].tail(5).max() + (1 * pip_mult)
        tp = recent_low
        if (entry - tp) < (10 * pip_mult): tp = entry - (atr_val * 3)
    else:
        tp, sl = entry, entry

    pip_yield = round(abs(tp - entry) / pip_mult, 1) if signal != "NEUTRAL" else 0
    rsi_val = rsi(df_ltf)

    return {
        "signal": signal, "confidence": min(round(confidence, 1), 100), "entry": round(entry, 5),
        "tp": round(tp, 5), "sl": round(sl, 5), "pips": pip_yield, "rsi": rsi_val,
        "structure": f"HTF Bias: {htf_bias} | Vol Factor: {vol_multiplier}x",
        "buy_score": min(buy_score, 100), "sell_score": min(sell_score, 100), "session": trading_session(),
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "recent_high": round(recent_high, 5), "recent_low": round(recent_low, 5)
    }

# =====================================================
# CACHED CROSS-PORTFOLIO CALCULATOR
# =====================================================
@st.cache_data(ttl=10)
def run_matrix_portfolio_scan(pairs_tuple):
    scan_results = []
    for p in pairs_tuple:
        try:
            res = predictive_matrix_engine(p)
            scan_results.append([p, res["signal"], f"{res['confidence']}%", res["structure"], res["pips"], res["session"]])
        except Exception:
            scan_results.append([p, "TIMEOUT", "—", "—", 0, "—"])
    return scan_results

# =====================================================
# MODULAR HIGH-PERFORMANCE RENDERING SEGMENTS
# =====================================================
@st.experimental_fragment(run_every=5)
def render_live_dashboard(pair):
    market_data = fetch_ticker_backbone(pair, period="5d", interval="15m")
    if market_data.empty:
        st.warning("Data network array pipeline recovering from system limit parameters...")
        return

    result = predictive_matrix_engine(pair)
    st.session_state.shared_prediction = result

    # Interactive Analytical Chart Framing
    plot_df = market_data.tail(100)
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
        template="plotly_dark", height=450, xaxis_rangeslider_visible=False, uirevision="keep",
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(15, 23, 42, 0.5)',
        margin=dict(l=10, r=10, t=10, b=10)
    )
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=True, gridcolor='rgba(255,255,255,0.03)', side="right")
    
    st.markdown('<div class="premium-card">', unsafe_allow_html=True)
    st.markdown(f"<div style='display:flex; justify-content:space-between; margin-bottom:15px;'><b style='font-size:1.1rem; color:#FFFFFF;'>🛰️ LIVE FLOW VECTOR: {pair}</b><span style='font-family:JetBrains Mono; color:#64748B;'>{result['timestamp']}</span></div>", unsafe_allow_html=True)
    st.plotly_chart(fig, use_container_width=True)
    
    # Corrected HTML containment encapsulation for standard layout structure
    st.markdown('</div>', unsafe_allow_html=True)
    
    color_hex = "#10B981" if "BUY" in result["signal"] else ("#EF4444" if "SELL" in result["signal"] else "#94A3B8")
    
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.metric("Validated Matrix Vector", result["signal"])
    with c2: st.metric("Confluence Confidence", f"{result['confidence']}%")
    with c3: st.metric("Target Proportional Yield", f"{result['pips']} Pips")
    with c4: st.metric("Active Global Session", result["session"])
    
    # Visual Matrix Factor Breakdown Pools
    st.markdown("<div style='margin-top:20px;'></div>", unsafe_allow_html=True)
    sc1, sc2 = st.columns(2)
    sc1.markdown(f"<div style='background:rgba(16, 185, 129, 0.08); padding:14px; border-radius:10px; border:1px solid rgba(16, 185, 129, 0.15); font-size:0.9rem;'>🟢 Buy Confluence Weight: <b style='color:#10B981; font-family:JetBrains Mono; float:right;'>{result['buy_score']}/100</b></div>", unsafe_allow_html=True)
    sc2.markdown(f"<div style='background:rgba(239, 68, 68, 0.08); padding:14px; border-radius:10px; border:1px solid rgba(239, 68, 68, 0.15); font-size:0.9rem;'>🔴 Sell Confluence Weight: <b style='color:#EF4444; font-family:JetBrains Mono; float:right;'>{result['sell_score']}/100</b></div>", unsafe_allow_html=True)

    if "STRONG" in result["signal"] and result["pips"] >= 12.0:
        components.html('<audio autoplay style="display:none;"><source src="https://actions.google.com/sounds/v1/alarms/digital_watch_alarm_long.ogg" type="audio/ogg"></audio>', height=0)
        st.toast(f"🚨 EXECUTABLE SMC MATRIX QUANT SIGNAL DETECTED FOR {pair}!", icon="⚡")

@st.experimental_fragment(run_every=12)
def render_scanner_block():
    st.markdown('<div class="premium-card" style="height: 100%;">', unsafe_allow_html=True)
    st.markdown("<b style='font-size:1.1rem; color:#FFFFFF; display:block; margin-bottom:15px;'>📡 CROSS-PORTFOLIO ASSET MONITOR</b>", unsafe_allow_html=True)
    scan_data = run_matrix_portfolio_scan(tuple(pairs))
    scanner_df = pd.DataFrame(scan_data, columns=["Asset Pair", "Vector State", "Confidence", "SMC Structural Diagnostics", "Risk Range", "Session Flow"])
    st.dataframe(scanner_df, use_container_width=True, hide_index=True)
    st.markdown('</div>', unsafe_allow_html=True)

def render_broadcast_hub(pair):
    st.markdown('<div class="premium-card">', unsafe_allow_html=True)
    st.markdown("<b style='font-size:1.1rem; color:#FFFFFF; display:block; margin-bottom:15px;'>📩 ROUTED NETWORK TELEGRAM DISPATCH</b>", unsafe_allow_html=True)
    confirm_send = st.checkbox("Confirm alignment with architectural execution parameters.", key="broadcast_check")
    st.markdown("<div style='margin-top:10px;'></div>", unsafe_allow_html=True)
    
    if st.button("EXECUTE BROADCAST ROUTER OVERLINK"):
        current_result = st.session_state.shared_prediction
        if not confirm_send:
            st.warning("Execution Terminated: Structural confirmation rule acceptance flag required.")
        elif "NEUTRAL" in current_result["signal"]:
            st.error("Routing Core Failure: Cannot push inactive trend indicators through the secure line.")
        else:
            message = f"<b>🏦 CORE STRUCTURAL SIGNAL DETECTED</b>\n\nVECTOR PAIR: {pair}\nSIGNAL BIAS: <b>{current_result['signal']}</b>\nCONFIDENCE: {current_result['confidence']}%\nSMC STRUCTURE: {current_result['structure']}\n\nENTRY RATE: {current_result['entry']}\nTARGET PROFIT (TP): {current_result['tp']}\nSTOP LOSS (SL): {current_result['sl']}\n\n📊 EXPECTED RANGE YIELD: <b>{current_result['pips']} Pips</b>\n\nSYSTEM TIMESTAMP: {current_result['timestamp']}"
            ok, err = send_telegram(message)
            if ok: st.success("Matrix payload pushed successfully to secure Telegram down-channels.")
            else: st.error(f"Transmission Exception Refused: {err}")
    st.markdown('</div>', unsafe_allow_html=True)

# =====================================================
# SYSTEM LAYOUT COMPOSITOR ASSEMBLY
# =====================================================
st.markdown('<h1 class="terminal-header">CORE VECTOR MATRIX PRO</h1>', unsafe_allow_html=True)
st.markdown('<p class="terminal-subheader" style="margin-bottom:30px;">High-Fidelity Multi-Timeframe Quantitative Analytics Ecosystem</p>', unsafe_allow_html=True)

col_layout_left, col_layout_right = st.columns([1.9, 1.1])

with col_layout_left:
    render_live_dashboard(selected_pair)

with col_layout_right:
    render_scanner_block()
    render_broadcast_hub(selected_pair)

# Deep Embedded Tradingview Dynamic Engine Base 
st.markdown("<div style='margin-top:10px;'></div>", unsafe_allow_html=True)
st.markdown('<div class="premium-card">', unsafe_allow_html=True)
st.markdown("<b style='font-size:1.1rem; color:#FFFFFF; display:block; margin-bottom:15px;'>📊 INTERACTIVE QUANTITATIVE ANALYTICS ENGINE STREAM</b>", unsafe_allow_html=True)
tradingview_html = f"""
<div id="tv_chart_container" style="height: 480px; width: 100%;"></div>
<script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
<script type="text/javascript">
new TradingView.widget({{
  "autosize": true, "symbol": "OANDA:{selected_pair}", "interval": "15",
  "container_id": "tv_chart_container", "theme": "dark", "style": "1", "locale": "en",
  "toolbar_bg": "#0B0F19", "enable_publishing": false, "hide_side_toolbar": false, "allow_symbol_change": true
}});
</script>
"""
components.html(tradingview_html, height=490, scrolling=False)
st.markdown('</div>', unsafe_allow_html=True)
