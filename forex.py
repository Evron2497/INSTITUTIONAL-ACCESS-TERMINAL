import os
from datetime import datetime, timezone
import time
import json
import numpy as np
import pandas as pd
import requests
import streamlit as st
import streamlit.components.v1 as components
import plotly.graph_objects as go
import yfinance as yf

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
# CONFIG & DATA INGESTION — Flattened & Squeezed
# =====================================================
pairs = ["EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "XAUUSD"]
selected_pair = st.sidebar.selectbox("Select Active Vector Pair", pairs)

@st.cache_data(ttl=15)
def get_data(symbol, bars=300, period="7d", interval="15m"):
    mapping = {
        "EURUSD": "EURUSD=X",
        "GBPUSD": "GBPUSD=X",
        "USDJPY": "JPY=X",
        "AUDUSD": "AUDUSD=X",
        "XAUUSD": "GC=F"
    }

    ticker = mapping.get(symbol)
    if ticker is None:
        return pd.DataFrame()

    if interval == "30m" or bars > 100:
        period = "7d"

    try:
        df = yf.download(ticker, period=period, interval=interval, progress=False)
    except Exception:
        return pd.DataFrame()

    if df is None or df.empty:
        return pd.DataFrame()

    # Step 1: Handle MultiIndex columns by extracting the base level explicitly
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    # Step 2: Ensure strictly 1D arrays using .squeeze() to drop accidental dimensions
    def to_flat_1d(dataframe, target_col):
        if target_col not in dataframe.columns:
            return np.zeros(len(dataframe))
        series = dataframe[target_col].squeeze()
        return np.asarray(series).flatten()

    try:
        opens = to_flat_1d(df, "Open")
        highs = to_flat_1d(df, "High")
        lows = to_flat_1d(df, "Low")
        closes = to_flat_1d(df, "Close")
        volumes = to_flat_1d(df, "Volume")
        
        df_reset = df.reset_index()
        time_col = "Datetime" if "Datetime" in df_reset.columns else "Date"
        time_series = to_flat_1d(df_reset, time_col)
    except Exception:
        return pd.DataFrame()

    clean_df = pd.DataFrame({
        "time": time_series,
        "Open": opens.astype(float),
        "High": highs.astype(float),
        "Low": lows.astype(float),
        "Close": closes.astype(float),
        "Volume": volumes.astype(float)
    })

    return clean_df.tail(int(bars)).reset_index(drop=True)

# =====================================================
# MATH & OPTIMIZED STRUCTURAL PIPELINE
# =====================================================
def calculate_swing_pivots(df: pd.DataFrame, left_bars: int = 5, right_bars: int = 5) -> pd.DataFrame:
    df = df.copy().reset_index(drop=True)
    
    # Vectorized Rolling Window Optimization
    roll_high = df["High"].rolling(window=left_bars + right_bars + 1, center=True).max()
    roll_low = df["Low"].rolling(window=left_bars + right_bars + 1, center=True).min()
    
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
    last_gain = gain.iloc[-1]
    last_loss = loss.iloc[-1]
    if last_loss == 0: return 100.0 if last_gain > 0 else 50.0
    rs = last_gain / last_loss
    return round(100 - (100 / (1 + rs)), 2)

def trading_session():
    hour = datetime.now(timezone.utc).hour
    if 0 <= hour < 7: return "ASIAN (ACCUMULATION)"
    elif 7 <= hour < 13: return "LONDON (MANIPULATION)"
    elif 13 <= hour < 21: return "NEW YORK (DISTRIBUTION)"
    return "CLOSED"

def calculate_pips(entry, tp, pair):
    if "JPY" in pair.upper(): pip_value = 0.01
    elif "XAU" in pair.upper(): pip_value = 0.10  
    else: pip_value = 0.0001
    return round(abs(tp - entry) / pip_value, 1)

def is_trending(df, period=20, threshold=0.3):
    recent_range = df["High"].tail(period).max() - df["Low"].tail(period).min()
    atr = calculate_atr(df)
    return recent_range > (atr * threshold * period)

def detect_fvg(df, lookback=20):
    fvg_buy = fvg_sell = False
    limit = min(lookback, len(df) - 2)
    for i in range(2, limit):
        if df["Low"].iloc[-i+1] > df["High"].iloc[-i-1]: fvg_buy = True
        if df["High"].iloc[-i+1] < df["Low"].iloc[-i-1]: fvg_sell = True
    return fvg_buy, fvg_sell

def detect_choch(df, recent_high, recent_low):
    if len(df) < 15: return False, False
    prev_trend_bearish = df["Close"].iloc[-5] < df["Close"].iloc[-12]
    choch_bull = prev_trend_bearish and df["Close"].iloc[-1] > recent_high
    
    prev_trend_bullish = df["Close"].iloc[-5] > df["Close"].iloc[-12]
    choch_bear = prev_trend_bullish and df["Close"].iloc[-1] < recent_low
    return choch_bull, choch_bear

def detect_order_block(df):
    ob_bull = ob_bear = False
    limit = min(20, len(df) - 3)
    for i in range(3, limit):
        candle = df.iloc[-i]
        next_two = df.iloc[-i+1:-i+3]
        if candle["Close"] < candle["Open"] and all(next_two["Close"] > next_two["Open"]):
            ob_bull = True
        if candle["Close"] > candle["Open"] and all(next_two["Close"] < next_two["Open"]):
            ob_bear = True
    return ob_bull, ob_bear

def volume_spike(df, threshold=1.5):
    avg_vol = df["Volume"].tail(20).mean()
    last_vol = df["Volume"].iloc[-1]
    return last_vol > (avg_vol * threshold) if avg_vol > 0 else False

def neutral_result():
    return {
        "signal": "NEUTRAL", "confidence": 0, "entry": 0, "tp": 0, "sl": 0,
        "pips": 0, "rsi": 50, "structure": "INSUFFICIENT CONFLUENCE", "buy_score": 0,
        "sell_score": 0, "session": trading_session(), "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "recent_high": 0, "recent_low": 0
    }

# =====================================================
# DEEP STRUCTURAL CONFLUENCE SMC ENGINE
# =====================================================
def institutional_engine(df, pair):
    if df is None or df.empty or len(df) < 50:
        return neutral_result()

    if "JPY" in pair.upper(): pip_multiplier = 0.01
    elif "XAU" in pair.upper(): pip_multiplier = 0.10
    else: pip_multiplier = 0.0001

    if not is_trending(df):
        return neutral_result()

    current_time_utc = datetime.now(timezone.utc)
    float_time = current_time_utc.hour + (current_time_utc.minute / 60.0)
    is_algo_killzone = (6.0 <= float_time <= 10.0) or (12.0 <= float_time <= 16.0)

    atr_val = calculate_atr(df)

    # Structural M30 Filters
    df_m30 = get_data(pair, bars=100, period="7d", interval="30m")
    htf_bias = "NEUTRAL"
    if df_m30 is not None and not df_m30.empty and len(df_m30) >= 30:
        m30_ema20 = df_m30["Close"].ewm(span=20).mean().iloc[-1]
        m30_ema50 = df_m30["Close"].ewm(span=50).mean().iloc[-1]
        if df_m30["Close"].iloc[-1] > m30_ema20 > m30_ema50: htf_bias = "BULLISH"
        elif df_m30["Close"].iloc[-1] < m30_ema20 < m30_ema50: htf_bias = "BEARISH"

    df = calculate_swing_pivots(df, left_bars=5, right_bars=5)
    valid_highs = df["Swing_High"].dropna()
    valid_lows = df["Swing_Low"].dropna()
    recent_high = float(valid_highs.iloc[-1]) if not valid_highs.empty else float(df["High"].max())
    recent_low = float(valid_lows.iloc[-1]) if not valid_lows.empty else float(df["Low"].min())

    current_range = recent_high - recent_low if (recent_high - recent_low) > 0 else 0.001
    price = float(df["Close"].iloc[-1])
    midpoint = recent_low + (current_range * 0.50)

    sweep_buy = any(df["Low"].tail(6) < recent_low) and (price > recent_low)
    sweep_sell = any(df["High"].tail(6) > recent_high) and (price < recent_high)

    choch_bull, choch_bear = detect_choch(df, recent_high, recent_low)
    fvg_buy_present, fvg_sell_present = detect_fvg(df)
    ob_bullish, ob_bearish = detect_order_block(df)

    buy_score, sell_score = 0, 0
    if htf_bias == "BULLISH": buy_score += 25
    if htf_bias == "BEARISH": sell_score += 25
    if sweep_buy: buy_score += 25
    if sweep_sell: sell_score += 25
    if choch_bull: buy_score += 25
    if choch_bear: sell_score += 25
    if fvg_buy_present: buy_score += 15
    if fvg_sell_present: sell_score += 15
    if ob_bullish: buy_score += 15
    if ob_bearish: sell_score += 15
    if volume_spike(df):
        if htf_bias == "BULLISH": buy_score += 10
        if htf_bias == "BEARISH": sell_score += 10

    discount_factor = 1.0 - max(0, (price - midpoint) / current_range) * 0.6
    premium_factor = 1.0 - max(0, (midpoint - price) / current_range) * 0.6
    buy_score = int(buy_score * discount_factor)
    sell_score = int(sell_score * premium_factor)

    if not is_algo_killzone:
        buy_score = int(buy_score * 0.7)
        sell_score = int(sell_score * 0.7)

    signal = "NEUTRAL"
    confidence = max(buy_score, sell_score)

    if buy_score >= 70: signal = "STRONG BUY (SMC Convergence)"
    elif buy_score >= 50: signal = "BUY"
    if sell_score >= 70: signal = "STRONG SELL (SMC Convergence)"
    elif sell_score >= 50 and "BUY" not in signal: signal = "SELL"

    entry = price
    if "BUY" in signal:
        sl = entry - (atr_val * 1.5)
        tp1 = entry + (atr_val * 1.5 * 2.0)
        tp = min(recent_high, tp1)
        if (tp - entry) < (10 * pip_multiplier): tp = entry + (atr_val * 3.0)
    elif "SELL" in signal:
        sl = entry + (atr_val * 1.5)
        tp1 = entry - (atr_val * 1.5 * 2.0)
        tp = max(recent_low, tp1)
        if (entry - tp) < (10 * pip_multiplier): tp = entry - (atr_val * 3.0)
    else:
        tp, sl = entry, entry

    pips = calculate_pips(entry, tp, pair) if "NEUTRAL" not in signal else 0
    rsi_val = rsi(df)

    return {
        "signal": signal, "confidence": round(confidence, 1), "entry": round(entry, 5),
        "tp": round(tp, 5), "sl": round(sl, 5), "pips": round(pips, 1), "rsi": round(rsi_val, 1),
        "structure": f"M30 Vector: {htf_bias} | Loop Timing: {'KILLZONE ACTIVE' if is_algo_killzone else 'STANDARD'}",
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
            pair_df = get_data(p, bars=300)
            if pair_df is None or pair_df.empty:
                scan_data.append([p, "NO SYMBOL DATA", "—", "—", 0, "—"])
                continue
            pair_res = institutional_engine(pair_df, p)
            scan_data.append([p, pair_res["signal"], f"{pair_res['confidence']}%", pair_res["structure"], pair_res["pips"], pair_res["session"]])
        except Exception:
            scan_data.append([p, "COMPLETION ERROR", "—", "—", 0, "—"])
    return scan_data

# =====================================================
# LIVE DASHBOARD DISPLAY FRAGMENT
# =====================================================
@st.fragment(run_every=4)
def render_live_dashboard(pair):
    market_data = get_data(pair, bars=300)
    if market_data is None or market_data.empty:
        st.warning(f"Market Stream for {pair} is currently offline.")
        return

    result = institutional_engine(market_data, pair)
    
    if "last_signal" not in st.session_state:
        st.session_state.last_signal = {"signal": "NEUTRAL", "count": 0}
    
    last = st.session_state.last_signal
    if result["signal"] == last["signal"]:
        last["count"] += 1
    else:
        last["count"] = 1
        last["signal"] = result["signal"]
    st.session_state.last_signal = last

    if last["count"] < 2 and last["signal"] != "NEUTRAL":
        result["signal"] = "NEUTRAL"

    st.session_state.shared_prediction = result

    plot_df = calculate_swing_pivots(market_data, left_bars=5, right_bars=5)
    fig = go.Figure()
    fig.add_trace(go.Candlestick(
        x=plot_df["time"], open=plot_df["Open"], high=plot_df["High"], low=plot_df["Low"], close=plot_df["Close"], name=pair,
        increasing_line_color='#00E676', increasing_fillcolor='#00E676',
        decreasing_line_color='#FF1744', decreasing_fillcolor='#FF1744'
    ))
    fig.add_trace(go.Scatter(x=plot_df["time"], y=plot_df["Swing_High"], mode="markers", name="BSL Liquidity", marker=dict(color="#FF9100", size=6, symbol="diamond")))
    fig.add_trace(go.Scatter(x=plot_df["time"], y=plot_df["Swing_Low"], mode="markers", name="SSL Liquidity", marker=dict(color="#00E5FF", size=6, symbol="diamond")))

    if result["recent_high"] > 0:
        fig.add_hline(y=result["recent_high"], line_dash="dash", line_color="rgba(255, 145, 0, 0.4)", annotation_text="BSL")
        fig.add_hline(y=result["recent_low"],  line_dash="dash", line_color="rgba(0, 229, 255, 0.4)", annotation_text="SSL")

    fig.update_layout(title=f"📡CHART: {pair}", template="plotly_dark", height=450, xaxis_rangeslider_visible=False, uirevision="keep", paper_bgcolor='#0A0E17', plot_bgcolor='#0F1626', margin=dict(l=10, r=10, t=40, b=10))
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=True, gridcolor='#1E293B')
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("### 🔍 Accumulation Metrics")
    sc1, sc2 = st.columns(2)
    sc1.markdown(f"<div style='background-color:#0F1626; padding:12px; border-radius:8px; border-left:4px solid #00E676;'>🟢 Bullish Engine Momentum: <b style='color:#00E676; font-family:JetBrains Mono;'>{result['buy_score']}/100</b></div>", unsafe_allow_html=True)
    sc2.markdown(f"<div style='background-color:#0F1626; padding:12px; border-radius:8px; border-left:4px solid #FF1744;'>🔴 Bearish Distribution Weight: <b style='color:#FF1744; font-family:JetBrains Mono;'>{result['sell_score']}/100</b></div>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    color_hex = "#FFFFFF"
    if "BUY" in result["signal"]: color_hex = "#00E676"
    elif "SELL" in signal: color_hex = "#FF1744"
        
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.markdown(f"<div data-testid='stMetricSimpleNormal'><div data-testid='stMetricLabel'>Structural Vector</div><div style='font-size:1.5rem; font-weight:600; color:{color_hex};'>{result['signal']}</div></div>", unsafe_allow_html=True)
    with c2: st.markdown(f"<div data-testid='stMetricSimpleNormal'><div data-testid='stMetricLabel'>Matrix Confidence</div><div style='font-size:1.5rem; font-weight:600; color:#00E5FF;'>{result['confidence']}%</div></div>", unsafe_allow_html=True)
    with c3: st.markdown(f"<div data-testid='stMetricSimpleNormal'><div data-testid='stMetricLabel'>Range Target</div><div style='font-size:1.5rem; font-weight:600; color:#FF9100;'>{result['pips']} Pips</div></div>", unsafe_allow_html=True)
    with c4: st.markdown(f"<div data-testid='stMetricSimpleNormal'><div data-testid='stMetricLabel'>Session Active</div><div style='font-size:1.1rem; font-weight:600; color:#94A3B8; margin-top:5px;'>{result['session']}</div></div>", unsafe_allow_html=True)

    if "STRONG" in result["signal"] and result["pips"] >= 12.0:
        components.html('<audio autoplay><source src="https://actions.google.com/sounds/v1/alarms/digital_watch_alarm_long.ogg" type="audio/ogg"></audio>', height=0)
        st.toast(f"🚨 STRATEGIC SYSTEM SETUP DETECTED FOR {pair}!", icon="💰")

# =====================================================
# SYSTEM GRID SCANNER ENGINE BLOCK
# =====================================================
@st.fragment(run_every=10)
def render_scanner_block():
    st.subheader("📡 Portfolio Matrix Scanner")
    scan_data = run_scanner(tuple(pairs))
    scanner_df = pd.DataFrame(scan_data, columns=["Pair", "Signal Bias", "Confidence", "SMC Architecture Status", "Range Projection", "Current Session Flow"])
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
            message = f"""🏦 <b>CORE STRUCTURAL SIGNAL SETUP</b>\n\nVECTOR PAIR: {pair}\nSIGNAL BIAS: <b>{current_result['signal']}</b>\nCONFIDENCE COEFFICIENT: {current_result['confidence']}%\nSMC STRUCTURE: {current_result['structure']}\n\nENTRY RATE: {current_result['entry']}\nTARGET PROFIT (TP): {current_result['tp']}\nSTOP LOSS (SL): {current_result['sl']}\n\n📊 EXPECTED RANGE YIELD: <b>{current_result['pips']} Pips</b>\nCeiling Liquidity Line: {current_result['recent_high']}\nFloor Liquidity Line: {current_result['recent_low']}\n\nRSI VALUE: {current_result['rsi']}\nSYSTEM TIME STAMP: {current_result['timestamp']}"""
            ok, err = send_telegram(message)
            if ok: st.success("✅ Configuration array deployed to configured channels.")
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
components.html(f"""
<script src="https://s3.tradingview.com/tv.js"></script>
<div id="tv_chart_container"></div>
<script>
new TradingView.widget({{
  "symbol": "OANDA:{selected_pair}",
  "interval": "15",
  "container_id": "tv_chart_container",
  "width": "100%",
  "height": 500,
  "theme": "dark",
  "style": "1",
  "locale": "en",
  "toolbar_bg": "#0F1626",
  "enable_publishing": false,
  "hide_side_toolbar": false,
  "allow_symbol_change": true
}});
</script>
""", height=520)
