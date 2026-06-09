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
# PAGE CONFIG & PREMIUM INSTITUTIONAL VISUAL THEME
# =====================================================
st.set_page_config(page_title="CORE VECTOR MATRIX", page_icon="🏦", layout="wide")

st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght=300;400;600&family=Space+Grotesk:wght=400;600&display=swap');
        
        html, body, [data-testid="stAppViewContainer"] {
            background-color: #0A0E17 !important;
            font-family: 'Space Grotesk', sans-serif !important;
            color: #E2E8F0 !important;
        }
        
        [data-testid="stSidebar"] {
            background-color: #0F1626 !important;
            border-right: 1px solid #1E293B !important;
        }
        
        div[data-testid="stMetricSimpleNormal"] {
            background: linear-gradient(135deg, #111827 0%, #1F2937 100%) !important;
            border: 1px solid #2D3748 !important;
            border-radius: 12px !important;
            padding: 15px 20px !important;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3) !important;
        }
        
        div[data-testid="stMetricLabel"] {
            font-size: 0.85rem !important;
            text-transform: uppercase !important;
            letter-spacing: 0.05em !important;
            color: #94A3B8 !important;
        }
        
        .terminal-header {
            font-family: 'Space Grotesk', sans-serif;
            font-weight: 600;
            background: linear-gradient(90deg, #00F0FF, #7000FF);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            letter-spacing: -0.02em;
        }
        
        .stButton>button {
            background: linear-gradient(90deg, #1E1B4B 0%, #311042 100%) !important;
            color: #00F0FF !important;
            border: 1px solid #4338CA !important;
            border-radius: 8px !important;
            font-weight: 600 !important;
            transition: all 0.3s ease !important;
            width: 100% !important;
        }
        .stButton>button:hover {
            border-color: #00F0FF !important;
            box-shadow: 0px 0px 15px rgba(0, 240, 255, 0.4) !important;
            color: #FFFFFF !important;
        }
    </style>
""", unsafe_allow_html=True)

# =====================================================
# LOGIN SYSTEM
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
    st.markdown('<h2 class="terminal-header">🏦 Institutional Access Terminal</h2>', unsafe_allow_html=True)
    u = st.text_input("Username")
    p = st.text_input("Password", type="password")
    if st.button("Login"):
        if u == USERNAME and p == PASSWORD:
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error("Invalid credentials")

if not st.session_state.logged_in:
    login()
    st.stop()

# =====================================================
# INITIALIZATION
# =====================================================
st.sidebar.success("✅ Cloud Data Feed Connected")

# =====================================================
# TELEGRAM DISPATCH PIPELINE
# =====================================================
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

# =====================================================
# HARDENED DATA INGESTION MATRIX Engine
# =====================================================
pairs = ["EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "XAUUSD"]
selected_pair = st.sidebar.selectbox("Select Active Vector Pair", pairs)

@st.cache_data(ttl=15)
def get_data(symbol, period="1mo", interval="15m"):
    mapping = {
        "EURUSD": "EURUSD=X", "GBPUSD": "GBPUSD=X",
        "USDJPY": "JPY=X", "AUDUSD": "AUDUSD=X", "XAUUSD": "GC=F"
    }
    ticker = mapping.get(symbol)
    if ticker is None: return pd.DataFrame()

    try:
        df = yf.download(ticker, period=period, interval=interval, progress=False)
        if df is None or df.empty: return pd.DataFrame()
        
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        df_reset = df.reset_index()
        time_col = "Datetime" if "Datetime" in df_reset.columns else "Date"
        
        clean_df = pd.DataFrame({
            "time": df_reset[time_col].squeeze().dropna(),
            "Open": df_reset["Open"].squeeze().astype(float),
            "High": df_reset["High"].squeeze().astype(float),
            "Low": df_reset["Low"].squeeze().astype(float),
            "Close": df_reset["Close"].squeeze().astype(float),
            "Volume": df_reset["Volume"].squeeze().astype(float)
        })
        return clean_df.reset_index(drop=True)
    except Exception:
        return pd.DataFrame()

# =====================================================
# ADVANCED MATHEMATICAL INDICATORS & STRUCTURAL PIPELINE
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
    last_gain, last_loss = gain.iloc[-1], loss.iloc[-1]
    if last_loss == 0: return 100.0 if last_gain > 0 else 50.0
    return round(100 - (100 / (1 + (last_gain / last_loss))), 2)

def trading_session():
    hour = datetime.now(timezone.utc).hour
    if 0 <= hour < 7: return "ASIAN (ACCUMULATION)"
    elif 7 <= hour < 13: return "LONDON (MANIPULATION)"
    elif 13 <= hour < 21: return "NEW YORK (DISTRIBUTION)"
    return "CLOSED"

def calculate_pips(entry, tp, pair):
    pip_value = 0.01 if "JPY" in pair.upper() else (0.10 if "XAU" in pair.upper() else 0.0001)
    return round(abs(tp - entry) / pip_value, 1)

def detect_fvg(df):
    if len(df) < 3: return False, False
    fvg_buy = df["Low"].iloc[-1] > df["High"].iloc[-3] and df["Close"].iloc[-2] > df["Open"].iloc[-2]
    fvg_sell = df["High"].iloc[-1] < df["Low"].iloc[-3] and df["Close"].iloc[-2] < df["Open"].iloc[-2]
    return fvg_buy, fvg_sell

def detect_order_block(df):
    ob_bull = ob_bear = False
    if len(df) >= 5:
        candle = df.iloc[-3]
        next_two = df.iloc[-2:]
        if candle["Close"] < candle["Open"] and all(next_two["Close"] > next_two["Open"]): ob_bull = True
        if candle["Close"] > candle["Open"] and all(next_two["Close"] < next_two["Open"]): ob_bear = True
    return ob_bull, ob_bear

# =====================================================
# HIGH-PRECISION MULTI-TIMEFRAME CONFLUENCE SMC ENGINE
# =====================================================
def institutional_engine(pair):
    # Fetch Dual Timeframe Tracks
    df_ltf = get_data(pair, period="7d", interval="15m")   # Entry / Structure execution vector
    df_htf = get_data(pair, period="1mo", interval="4h")   # Structural macro order block vector

    if df_ltf.empty or df_htf.empty or len(df_ltf) < 60 or len(df_htf) < 30:
        return {
            "signal": "NEUTRAL", "confidence": 0, "entry": 0, "tp": 0, "sl": 0, "pips": 0, "rsi": 50,
            "structure": "ASYNC COOLDOWN / LOAD DATA ERROR", "buy_score": 0, "sell_score": 0,
            "session": trading_session(), "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "recent_high": 0, "recent_low": 0
        }

    # 1. EVALUATE HIGHER TIMEFRAME (4H MACRO BIAS)
    df_htf = calculate_swing_pivots(df_htf, left=3, right=3)
    htf_highs = df_htf["Swing_High"].dropna()
    htf_lows = df_htf["Swing_Low"].dropna()
    
    macro_high = float(htf_highs.iloc[-1]) if not htf_highs.empty else float(df_htf["High"].max())
    macro_low = float(htf_lows.iloc[-1]) if not htf_lows.empty else float(df_htf["Low"].min())
    macro_close = float(df_htf["Close"].iloc[-1])
    
    # Mathematical HTF Structure Validation Matrix
    htf_bias = "NEUTRAL"
    htf_ema20 = df_htf["Close"].ewm(span=20).mean().iloc[-1]
    if macro_close > htf_ema20 and macro_close > (macro_low + (macro_high - macro_low) * 0.5):
        htf_bias = "BULLISH"
    elif macro_close < htf_ema20 and macro_close < (macro_low + (macro_high - macro_low) * 0.5):
        htf_bias = "BEARISH"

    # 2. EVALUATE LOWER TIMEFRAME (15M EXECUTION ENGINE)
    df_ltf = calculate_swing_pivots(df_ltf, left=5, right=5)
    ltf_highs = df_ltf["Swing_High"].dropna()
    ltf_lows = df_ltf["Swing_Low"].dropna()
    
    recent_high = float(ltf_highs.iloc[-1]) if not ltf_highs.empty else float(df_ltf["High"].max())
    recent_low = float(ltf_lows.iloc[-1]) if not ltf_lows.empty else float(df_ltf["Low"].min())
    price = float(df_ltf["Close"].iloc[-1])
    atr_val = calculate_atr(df_ltf)

    # Liquidity Sweeps
    sweep_buy = any(df_ltf["Low"].tail(4) < recent_low) and (price > recent_low)
    sweep_sell = any(df_ltf["High"].tail(4) > recent_high) and (price < recent_high)

    # Patterns
    fvg_buy, fvg_sell = detect_fvg(df_ltf)
    ob_bull, ob_bear = detect_order_block(df_ltf)

    # 3. ADVANCED CONFLUENCE METRIC ALLOCATION
    buy_score = 0
    sell_score = 0

    if htf_bias == "BULLISH": buy_score += 35
    if htf_bias == "BEARISH": sell_score += 35
    if sweep_buy: buy_score += 25
    if sweep_sell: sell_score += 25
    if fvg_buy: buy_score += 20
    if fvg_sell: sell_score += 20
    if ob_bull: buy_score += 20
    if ob_bear: sell_score += 20

    # Discount/Premium Pricing Optimization Engine
    current_range = (recent_high - recent_low) if (recent_high - recent_low) > 0 else 0.001
    midpoint = recent_low + (current_range * 0.5)
    
    if price > midpoint: buy_score = int(buy_score * 0.6)  # Penalize buying in a premium array
    if price < midpoint: sell_score = int(sell_score * 0.6) # Penalize selling in a discount array

    # 4. STRUCTURAL SIGNALS DEPLOYMENT MATRIX
    signal = "NEUTRAL"
    confidence = max(buy_score, sell_score)

    # Require strict multi-timeframe alignment barrier to pass 70% threshold
    if buy_score >= 70 and htf_bias == "BULLISH": signal = "STRONG BUY (MTF SMC COHERENCE)"
    elif buy_score >= 50 and htf_bias == "BULLISH": signal = "BUY"
    elif sell_score >= 70 and htf_bias == "BEARISH": signal = "STRONG SELL (MTF SMC COHERENCE)"
    elif sell_score >= 50 and htf_bias == "BEARISH": signal = "SELL"

    # Risk Architecture Formulations
    entry = price
    pip_multiplier = 0.01 if "JPY" in pair.upper() else (0.10 if "XAU" in pair.upper() else 0.0001)

    if "BUY" in signal:
        sl = recent_low - (2 * pip_multiplier)
        tp = recent_high
        if (tp - entry) < (15 * pip_multiplier): tp = entry + (atr_val * 3)
    elif "SELL" in signal:
        sl = recent_high + (2 * pip_multiplier)
        tp = recent_low
        if (entry - tp) < (15 * pip_multiplier): tp = entry - (atr_val * 3)
    else:
        tp, sl = entry, entry

    pips = calculate_pips(entry, tp, pair) if signal != "NEUTRAL" else 0
    rsi_val = rsi(df_ltf)

    return {
        "signal": signal, "confidence": round(confidence, 1), "entry": round(entry, 5),
        "tp": round(tp, 5), "sl": round(sl, 5), "pips": round(pips, 1), "rsi": round(rsi_val, 1),
        "structure": f"4H Macro Flow: {htf_bias} | 15M Entry Status Array Balanced",
        "buy_score": buy_score, "sell_score": sell_score, "session": trading_session(),
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "recent_high": round(recent_high, 5), "recent_low": round(recent_low, 5)
    }

# =====================================================
# CACHED MATRIX PORTFOLIO SCANNER
# =====================================================
@st.cache_data(ttl=15)
def run_scanner(pairs_tuple):
    scan_data = []
    for p in pairs_tuple:
        try:
            pair_res = institutional_engine(p)
            scan_data.append([p, pair_res["signal"], f"{pair_res['confidence']}%", pair_res["structure"], pair_res["pips"], pair_res["session"]])
        except Exception:
            scan_data.append([p, "COMPLETION ERROR", "—", "—", 0, "—"])
    return scan_data

# =====================================================
# LIVE DASHBOARD DISPLAY FRAGMENT
# =====================================================
@st.fragment(run_every=6)
def render_live_dashboard(pair):
    market_data = get_data(pair, period="7d", interval="15m")
    if market_data.empty:
        st.warning(f"Market Stream for {pair} is buffering or experiencing provider line throttles.")
        return

    result = institutional_engine(pair)
    st.session_state.shared_prediction = result

    plot_df = calculate_swing_pivots(market_data, left=5, right=5).tail(120)
    fig = go.Figure()
    fig.add_trace(go.Candlestick(
        x=plot_df["time"], open=plot_df["Open"], high=plot_df["High"], low=plot_df["Low"], close=plot_df["Close"], name=pair,
        increasing_line_color='#00E676', increasing_fillcolor='#00E676',
        decreasing_line_color='#FF1744', decreasing_fillcolor='#FF1744'
    ))
    fig.add_trace(go.Scatter(x=plot_df["time"], y=plot_df["Swing_High"], mode="markers", name="BSL Pool", marker=dict(color="#FF9100", size=6, symbol="diamond")))
    fig.add_trace(go.Scatter(x=plot_df["time"], y=plot_df["Swing_Low"], mode="markers", name="SSL Pool", marker=dict(color="#00E5FF", size=6, symbol="diamond")))

    if result["recent_high"] > 0:
        fig.add_hline(y=result["recent_high"], line_dash="dash", line_color="rgba(255, 145, 0, 0.4)", annotation_text="15M BSL")
        fig.add_hline(y=result["recent_low"],  line_dash="dash", line_color="rgba(0, 229, 255, 0.4)", annotation_text="15M SSL")

    fig.update_layout(title=f"📡 SYSTEM QUANT GRAPH MATRIX: {pair} (15M Mode)", template="plotly_dark", height=450, xaxis_rangeslider_visible=False, uirevision="keep", paper_bgcolor='#0A0E17', plot_bgcolor='#0F1626', margin=dict(l=10, r=10, t=40, b=10))
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=True, gridcolor='#1E293B')
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("### 🔍 Accumulation Metrics")
    sc1, sc2 = st.columns(2)
    sc1.markdown(f"<div style='background-color:#0F1626; padding:12px; border-radius:8px; border-left:4px solid #00E676;'>🟢 Bullish Matrix Confluence: <b style='color:#00E676; font-family:JetBrains Mono;'>{result['buy_score']}/100</b></div>", unsafe_allow_html=True)
    sc2.markdown(f"<div style='background-color:#0F1626; padding:12px; border-radius:8px; border-left:4px solid #FF1744;'>🔴 Bearish Distribution Weight: <b style='color:#FF1744; font-family:JetBrains Mono;'>{result['sell_score']}/100</b></div>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    color_hex = "#FFFFFF"
    if "BUY" in result["signal"]: color_hex = "#00E676"
    elif "SELL" in result["signal"]: color_hex = "#FF1744"
        
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.markdown(f"<div data-testid='stMetricSimpleNormal'><div data-testid='stMetricLabel'>Structural Vector Matrix</div><div style='font-size:1.1rem; font-weight:600; color:{color_hex};'>{result['signal']}</div></div>", unsafe_allow_html=True)
    with c2: st.markdown(f"<div data-testid='stMetricSimpleNormal'><div data-testid='stMetricLabel'>Matrix Confidence</div><div style='font-size:1.5rem; font-weight:600; color:#00E5FF;'>{result['confidence']}%</div></div>", unsafe_allow_html=True)
    with c3: st.markdown(f"<div data-testid='stMetricSimpleNormal'><div data-testid='stMetricLabel'>Structural Target Profit</div><div style='font-size:1.5rem; font-weight:600; color:#FF9100;'>{result['pips']} Pips</div></div>", unsafe_allow_html=True)
    with c4: st.markdown(f"<div data-testid='stMetricSimpleNormal'><div data-testid='stMetricLabel'>Active Operational Flow</div><div style='font-size:1.0rem; font-weight:600; color:#94A3B8; margin-top:5px;'>{result['session']}</div></div>", unsafe_allow_html=True)

    if "STRONG" in result["signal"] and result["pips"] >= 15.0:
        components.html('<audio autoplay style="display:none;"><source src="https://actions.google.com/sounds/v1/alarms/digital_watch_alarm_long.ogg" type="audio/ogg"></audio>', height=0)
        st.toast(f"🚨 MULTI-TIMEFRAME ALIGNMENT MATCH FOR {pair}!", icon="💰")

# =====================================================
# SYSTEM GRID SCANNER ENGINE BLOCK
# =====================================================
@st.fragment(run_every=15)
def render_scanner_block():
    st.subheader("📡 Portfolio MTF Matrix Scanner")
    scan_data = run_scanner(tuple(pairs))
    scanner_df = pd.DataFrame(scan_data, columns=["Pair", "MTF Signal Bias", "Confidence Factor", "SMC Architecture Status", "Risk Range Delta", "Current Session"])
    st.dataframe(scanner_df, use_container_width=True, hide_index=True)

# =====================================================
# TELEGRAM LIVE DISPATCH FRAGMENT
# =====================================================
@st.fragment
def render_broadcast_hub(pair):
    st.subheader("📩 Broadcast Hub")
    confirm_send = st.checkbox("Verify system structural rules execution criteria checklist verification pattern.", key="broadcast_check")
    
    if st.button("🚀TELEGRAM BROADCAST"):
        current_result = st.session_state.shared_prediction
        if not confirm_send:
            st.warning("Execution Refused: Accept confirmation protocol parameters before network push.")
        elif "NEUTRAL" in current_result["signal"]:
            st.error("Execution Aborted: Algorithmic parameters require valid active trend metrics.")
        else:
            message = f"<b>🏦 CORE STRUCTURAL MULTI-TIMEFRAME MATCH DETECTED</b>\n\nVECTOR PAIR: {pair}\nSIGNAL BIAS: <b>{current_result['signal']}</b>\nCONFIDENCE: {current_result['confidence']}%\nDETAILS: {current_result['structure']}\n\nENTRY RATE: {current_result['entry']}\nTARGET PROFIT (TP): {current_result['tp']}\nSTOP LOSS (SL): {current_result['sl']}\n\n📊 EXPECTED TARGET PROFILE: <b>{current_result['pips']} Pips</b>\n15M Range High: {current_result['recent_high']}\n15M Range Low: {current_result['recent_low']}\n\nRSI VALUE: {current_result['rsi']}\nTIMESTAMP GMT: {current_result['timestamp']}"
            ok, err = send_telegram(message)
            if ok: st.success("✅ Configuration array deployed to network streams.")
            else: st.error(f"❌ Transmission exception: {err}")

# =====================================================
# SYSTEM BUILD LAYOUT ASSEMBLY
# =====================================================
st.markdown('<h1 class="terminal-header">TECH-STAR🚨</h1>', unsafe_allow_html=True)
st.markdown('<h2 class="terminal-header">🏦 INSTITUTIONAL FOREX TERMINAL</h2>', unsafe_allow_html=True)
st.markdown("<p style='color:#64748B; margin-top:-15px;'>Smart Market Structure Verification Pipeline</p>", unsafe_allow_html=True)
st.markdown("---")

col_layout_left, col_layout_right = st.columns([1.8, 1.2])

with col_layout_left:
    render_live_dashboard(selected_pair)

with col_layout_right:
    render_scanner_block()

st.markdown("---")
render_broadcast_hub(selected_pair)

# =====================================================
# INTEGRATED QUANTITATIVE TRADINGVIEW STREAM
# =====================================================
st.markdown("---")
st.subheader("📊 Quantitative Analytics Stream")

tradingview_html = f"""
<div id="tv_chart_container" style="height: 500px; width: 100%;"></div>
<script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
<script type="text/javascript">
new TradingView.widget({{
  "autosize": true,
  "symbol": "OANDA:{selected_pair}",
  "interval": "15",
  "container_id": "tv_chart_container",
  "theme": "dark",
  "style": "1",
  "locale": "en",
  "toolbar_bg": "#0F1626",
  "enable_publishing": false,
  "hide_side_toolbar": false,
  "allow_symbol_change": true
}});
</script>
"""
components.html(tradingview_html, height=520, scrolling=False)
