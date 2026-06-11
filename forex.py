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
# PERSISTENT LOGIN SYSTEM (FIXED REFRESH BUG)
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
    u = st.text_input("Username", key="login_user")
    p = st.text_input("Password", type="password", key="login_pass")
    if st.button("Login"):
        if u == USERNAME and p == PASSWORD:
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error("Invalid credentials")

# Stop rendering execution loop if the user isn't authenticated yet
if not st.session_state.logged_in:
    login()
    st.stop()

# Persistent state safe banner display
st.sidebar.success("✅ Institutional Terminal Authorized")

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
# YAHOO FINANCE DATA INGESTION ENGINE (STABLE SYNCED)
# =====================================================
pairs = ["EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "XAUUSD"]
selected_pair = st.sidebar.selectbox("Select Active Vector Pair", pairs)

def map_ticker(symbol: str) -> str:
    sym = symbol.upper()
    if sym == "XAUUSD":
        return "GC=F"  # Gold Continuous Futures
    return f"{sym}=X"

@st.cache_data(ttl=15)
def get_data(symbol, interval="15m", period="5d"):
    ticker = map_ticker(symbol)
    try:
        ticker_obj = yf.Ticker(ticker)
        # CRITICAL REFACTOR: threads=False terminates RuntimeError thread exhaustion errors
        df = ticker_obj.history(period=period, interval=interval, threads=False)
        if df.empty:
            return pd.DataFrame()
            
        df = df.reset_index()
        if "Datetime" in df.columns:
            df.rename(columns={"Datetime": "time"}, inplace=True)
        elif "Date" in df.columns:
            df.rename(columns={"Date": "time"}, inplace=True)
        
        df["time"] = pd.to_datetime(df["time"]).dt.tz_localize(None)
        df.rename(columns={"Open": "Open", "High": "High", "Low": "Low", "Close": "Close", "Volume": "Volume"}, inplace=True)
        return df
    except Exception:
        return pd.DataFrame()

# =====================================================
# MATH & ADVANCED VECTORIZED SIGNAL ALGORITHMS
# =====================================================
def calculate_swing_pivots(df: pd.DataFrame, left_bars: int = 5, right_bars: int = 5) -> pd.DataFrame:
    total_bars = left_bars + right_bars + 1
    rolling_high = df["High"].rolling(window=total_bars, center=True).max()
    rolling_low = df["Low"].rolling(window=total_bars, center=True).min()
    
    df["Swing_High"] = np.where(df["High"] == rolling_high, df["High"], np.nan)
    df["Swing_Low"] = np.where(df["Low"] == rolling_low, df["Low"], np.nan)
    return df

def calculate_atr(df, period=14):
    if len(df) < period: return 0.001
    high_low = df["High"] - df["Low"]
    high_close = (df["High"] - df["Close"].shift()).abs()
    low_close = (df["Low"] - df["Close"].shift()).abs()
    tr = np.maximum(high_low, np.maximum(high_close, low_close))
    atr = tr.rolling(period).mean().iloc[-1]
    return atr if not np.isnan(atr) else 0.001

def rsi_series(df, period=14):
    if len(df) < period: return pd.Series(50.0, index=df.index)
    delta = df["Close"].diff()
    gain = delta.clip(lower=0).rolling(period).mean()
    loss = (-delta.clip(upper=0)).rolling(period).mean()
    rs = gain / loss.replace(0, 1e-5)
    return (100 - (100 / (1 + rs))).fillna(50.0)

def rsi(df, period=14):
    vals = rsi_series(df, period)
    return round(float(vals.iloc[-1]), 2)

def trading_session():
    hour = datetime.now(timezone.utc).hour
    if 0 <= hour < 7: return "ASIAN (ACCUMULATION)"
    elif 7 <= hour < 13: return "LONDON (KILLZONE)"
    elif 13 <= hour < 21: return "NEW YORK (KILLZONE)"
    return "CLOSED"

def calculate_pips(entry, tp, pair):
    if "JPY" in pair.upper(): pip_value = 0.01
    elif "XAU" in pair.upper(): pip_value = 0.10  
    else: pip_value = 0.0001
    return round(abs(tp - entry) / pip_value, 1)

def detect_fvg(df, lookback=15):
    sub_df = df.iloc[-min(lookback, len(df)):]
    fvg_buy = (sub_df["Low"].shift(-1) > sub_df["High"].shift(1)).any()
    fvg_sell = (sub_df["High"].shift(-1) < sub_df["Low"].shift(1)).any()
    return bool(fvg_buy), bool(fvg_sell)

def detect_choch(df, recent_high, recent_low):
    if len(df) < 15: return False, False
    close_array = df["Close"].values
    prev_trend_bearish = close_array[-5] < close_array[-12]
    choch_bull = prev_trend_bearish and close_array[-1] > recent_high
    
    prev_trend_bullish = close_array[-5] > close_array[-12]
    choch_bear = prev_trend_bullish and close_array[-1] < recent_low
    return choch_bull, choch_bear

def detect_order_block(df):
    ob_bull = ob_bear = False
    sub_df = df.iloc[-15:]
    for i in range(3, len(sub_df)):
        candle = sub_df.iloc[-i]
        next_two = sub_df.iloc[-i+1:-i+3]
        if candle["Close"] < candle["Open"] and all(next_two["Close"] > next_two["Open"]):
            ob_bull = True
        if candle["Close"] > candle["Open"] and all(next_two["Close"] < next_two["Open"]):
            ob_bear = True
    return ob_bull, ob_bear

# =====================================================
# ADAPTIVE ICT PAIR-SPECIFIC PROPERTIES
# =====================================================
def get_pair_coefficient(pair):
    p = pair.upper()
    if "XAU" in p:
        return {"sweep_mult": 1.0012, "name": "Gold (Highly Manipulated Sweeps)"}
    elif "USDJPY" in p:
        return {"sweep_mult": 1.0002, "name": "Yen (Trend & BOS Heavy)"}
    elif "GBPUSD" in p:
        return {"sweep_mult": 1.0006, "name": "Cable (Aggressive Stop Hunts)"}
    elif "EURUSD" in p:
        return {"sweep_mult": 1.0004, "name": "Euro (Clean Market Structure)"}
    return {"sweep_mult": 1.0004, "name": "Standard Vector Pair"}

def neutral_result():
    return {
        "signal": "NO TRADE (INSUFFICIENT CONFLUENCE)", "confidence": 0, "entry": 0, "tp": 0, "sl": 0,
        "pips": 0, "rsi": 50, "structure": "WAITING FOR SETUP", "buy_score": 0,
        "sell_score": 0, "session": trading_session(), "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "recent_high": 0, "recent_low": 0, "df_pivots": pd.DataFrame()
    }

# =====================================================
# STRICT ICT CONFLUENCE ENGINE RULES
# =====================================================
def institutional_engine(df, pair):
    if df is None or df.empty or len(df) < 50:
        return neutral_result()

    if "JPY" in pair.upper(): pip_multiplier = 0.01
    elif "XAU" in pair.upper(): pip_multiplier = 0.10
    else: pip_multiplier = 0.0001

    pair_props = get_pair_coefficient(pair)
    atr_val = calculate_atr(df)
    price = float(df["Close"].iloc[-1])

    # 1. STEP 1: Higher Timeframe Anchor Context via Hourly Processing
    df_htf = get_data(pair, interval="1h", period="5d")
    htf_bias = "NEUTRAL"
    if not df_htf.empty and len(df_htf) >= 20:
        htf_highs = df_htf["High"].tail(10)
        htf_lows = df_htf["Low"].tail(10)
        if htf_highs.iloc[-1] > htf_highs.mean() and htf_lows.iloc[-1] > htf_lows.mean():
            htf_bias = "BULLISH"
        elif htf_highs.iloc[-1] < htf_highs.mean() and htf_lows.iloc[-1] < htf_lows.mean():
            htf_bias = "BEARISH"

    # Map structural boundaries
    df = calculate_swing_pivots(df, left_bars=5, right_bars=5)
    valid_highs = df["Swing_High"].dropna()
    valid_lows  = df["Swing_Low"].dropna()
    recent_high = float(valid_highs.iloc[-1]) if not valid_highs.empty else float(df["High"].max())
    recent_low  = float(valid_lows.iloc[-1])  if not valid_lows.empty  else float(df["Low"].min())

    # 2. STEP 2 & 3: Multi-Matrix Ranges (Premium / Discount)
    current_range = recent_high - recent_low if (recent_high - recent_low) > 0 else 0.001
    midpoint = recent_low + (current_range * 0.50)
    
    is_in_discount = price < midpoint
    is_in_premium = price > midpoint

    sweep_buy = (df["Low"].iloc[-8:] < recent_low * pair_props["sweep_mult"]).any() and (price > recent_low)
    sweep_sell = (df["High"].iloc[-8:] > recent_high * (2.0 - pair_props["sweep_mult"])).any() and (price < recent_high)

    # 4. STEP 4: Break of Micro-Structure Triggers
    choch_bull, choch_bear = detect_choch(df, recent_high, recent_low)
    fvg_buy_present, fvg_sell_present = detect_fvg(df)
    ob_bullish, ob_bearish = detect_order_block(df)

    # 5. STEP 5 & 6: Engine Scoring Systems
    signal = "NO TRADE"
    buy_score = sell_score = 0
    
    if htf_bias == "BULLISH": buy_score += 25
    if sweep_buy: buy_score += 25
    if choch_bull: buy_score += 25
    if (ob_bullish or fvg_buy_present) and is_in_discount: buy_score += 25

    if htf_bias == "BEARISH": sell_score += 25
    if sweep_sell: sell_score += 25
    if choch_bear: sell_score += 25
    if (ob_bearish or fvg_sell_present) and is_in_premium: sell_score += 25

    # Confluence Alignment Verification
    if htf_bias == "BULLISH" and sweep_buy and choch_bull and is_in_discount:
        if ob_bullish or fvg_buy_present:
            signal = "STRONG BUY (ICT Matrix Alignment)"
            
    elif htf_bias == "BEARISH" and sweep_sell and choch_bear and is_in_premium:
        if ob_bearish or fvg_sell_present:
            signal = "STRONG SELL (ICT Matrix Alignment)"
            
    if signal == "NO TRADE":
        if buy_score >= 50 and is_in_discount: signal = "BUY SCALPMATRIX"
        elif sell_score >= 50 and is_in_premium: signal = "SELL SCALPMATRIX"

    # Safe Yield Projections
    entry = price
    if "BUY" in signal:
        sl  = entry - (atr_val * 1.5)
        tp = min(recent_high, entry + (atr_val * 3.5))
        if (tp - entry) < (10 * pip_multiplier): tp = entry + (atr_val * 3.0)
    elif "SELL" in signal:
        sl  = entry + (atr_val * 1.5)
        tp = max(recent_low, entry - (atr_val * 3.5))
        if (entry - tp) < (10 * pip_multiplier): tp = entry - (atr_val * 3.0)
    else:
        tp, sl = entry, entry

    pips = calculate_pips(entry, tp, pair) if "NO TRADE" not in signal else 0
    rsi_val = rsi(df)

    status_str = f"HTF: {htf_bias} | SWEEP: {'YES' if (sweep_buy or sweep_sell) else 'NO'} | " \
                 f"ZONE: {'DISCOUNT' if is_in_discount else 'PREMIUM'}"

    return {
        "signal": signal, "confidence": max(buy_score, sell_score), "entry": round(entry, 5),
        "tp": round(tp, 5), "sl": round(sl, 5), "pips": round(pips, 1), "rsi": round(rsi_val, 1),
        "structure": status_str, "buy_score": buy_score, "sell_score": sell_score, "session": trading_session(),
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 
        "recent_high": round(recent_high, 5), "recent_low": round(recent_low, 5),
        "df_pivots": df
    }

# =====================================================
# CACHED MATRIX PORTFOLIO SCANNER
# =====================================================
@st.cache_data(ttl=15)
def run_scanner(pairs_tuple):
    scan_data = []
    for p in pairs_tuple:
        try:
            pair_df = get_data(p, interval="15m")
            if pair_df.empty:
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
    market_data = get_data(pair, interval="15m", period="5d")
    if market_data.empty:
        st.warning(f"Market Stream for {pair} is currently offline.")
        return

    result = institutional_engine(market_data, pair)
    pair_meta = get_pair_coefficient(pair)
    
    if "last_signal" not in st.session_state:
        st.session_state.last_signal = {"signal": "NO TRADE", "count": 0}
    
    last = st.session_state.last_signal
    if result["signal"] == last["signal"]:
        last["count"] += 1
    else:
        last["count"] = 1
        last["signal"] = result["signal"]
    st.session_state.last_signal = last

    st.session_state.shared_prediction = result
    plot_df = result["df_pivots"]

    # Generate Chart Data
    fig = go.Figure()
    fig.add_trace(go.Candlestick(
        x=plot_df["time"], open=plot_df["Open"], high=plot_df["High"], low=plot_df["Low"], close=plot_df["Close"], name=pair,
        increasing_line_color='#00E676', increasing_fillcolor='#00E676',
        decreasing_line_color='#FF1744', decreasing_fillcolor='#FF1744'
    ))
    fig.add_trace(go.Scatter(x=plot_df["time"], y=plot_df["Swing_High"], mode="markers", name="BSL (Liquidity Highs)", marker=dict(color="#FF9100", size=6, symbol="diamond")))
    fig.add_trace(go.Scatter(x=plot_df["time"], y=plot_df["Swing_Low"], mode="markers", name="SSL (Liquidity Lows)", marker=dict(color="#00E5FF", size=6, symbol="diamond")))

    if result["recent_high"] > 0:
        fig.add_hline(y=result["recent_high"], line_dash="dash", line_color="rgba(255, 145, 0, 0.4)", annotation_text="BSL Ceiling")
        fig.add_hline(y=result["recent_low"],  line_dash="dash", line_color="rgba(0, 229, 255, 0.4)", annotation_text="SSL Floor")

    fig.update_layout(title=f"📡 SYSTEM STREAM: {pair} — Asset Target: {pair_meta['name']}", template="plotly_dark", height=450, xaxis_rangeslider_visible=False, uirevision="keep", paper_bgcolor='#0A0E17', plot_bgcolor='#0F1626', margin=dict(l=10, r=10, t=40, b=10))
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=True, gridcolor='#1E293B')
    st.plotly_chart(fig, use_container_width=True)

    # Confluence Monitoring Output
    st.markdown("### 🔍 ICT Matrix Layer Alignments")
    sc1, sc2 = st.columns(2)
    sc1.markdown(f"<div style='background-color:#0F1626; padding:12px; border-radius:8px; border-left:4px solid #00E676;'>🟢 Long Confluence Match Array: <b style='color:#00E676; font-family:JetBrains Mono;'>{result['buy_score']}%</b></div>", unsafe_allow_html=True)
    sc2.markdown(f"<div style='background-color:#0F1626; padding:12px; border-radius:8px; border-left:4px solid #FF1744;'>🔴 Short Confluence Match Array: <b style='color:#FF1744; font-family:JetBrains Mono;'>{result['sell_score']}%</b></div>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    color_hex = "#94A3B8"
    if "BUY" in result["signal"]: 
        color_hex = "#00E676"
    elif "SELL" in result["signal"]: 
        color_hex = "#FF1744"
        
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.markdown(f"<div data-testid='stMetricSimpleNormal'><div data-testid='stMetricLabel'>Strict Decision Signal</div><div style='font-size:1.15rem; font-weight:600; color:{color_hex};'>{result['signal']}</div></div>", unsafe_allow_html=True)
    with c2: st.markdown(f"<div data-testid='stMetricSimpleNormal'><div data-testid='stMetricLabel'>Confluence Match</div><div style='font-size:1.5rem; font-weight:600; color:#00E5FF;'>{result['confidence']}%</div></div>", unsafe_allow_html=True)
    with c3: st.markdown(f"<div data-testid='stMetricSimpleNormal'><div data-testid='stMetricLabel'>Target Projections</div><div style='font-size:1.5rem; font-weight:600; color:#FF9100;'>{result['pips']} Pips</div></div>", unsafe_allow_html=True)
    with c4: st.markdown(f"<div data-testid='stMetricSimpleNormal'><div data-testid='stMetricLabel'>Time Horizon</div><div style='font-size:1.1rem; font-weight:600; color:#94A3B8; margin-top:5px;'>{result['session']}</div></div>", unsafe_allow_html=True)

    if "STRONG" in result["signal"]:
        components.html('<audio autoplay><source src="https://actions.google.com/sounds/v1/alarms/digital_watch_alarm_long.ogg" type="audio/ogg"></audio>', height=0)
        st.toast(f"🚨 STRICT ICT CONFIRMED CONFLUENCE MATCH FOR {pair}!", icon="💰")

# =====================================================
# SYSTEM GRID SCANNER ENGINE BLOCK
# =====================================================
@st.fragment(run_every=10)
def render_scanner_block():
    st.subheader("📡 Portfolio Matrix Scanner")
    scan_data = run_scanner(tuple(pairs))
    scanner_df = pd.DataFrame(scan_data, columns=["Pair", "Signal Bias", "Confluence Match", "Rule Pipeline Metrics", "Range Projection", "Current Session Flow"])
    st.dataframe(scanner_df, use_container_width=True, hide_index=True)

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
current_result = st.session_state.shared_prediction

# =====================================================
# TELEGRAM DISPATCH FRAME
# =====================================================
st.subheader("📩 Broadcast Hub")
confirm_send = st.checkbox("Verify system structural rules execution criteria checklist verification pattern.")

if st.button("🚀TELEGRAM BROADCAST"):
    if not confirm_send:
        st.warning("Execution Refused: Accept confirmation protocol parameters before network push.")
    elif "NO TRADE" in current_result["signal"]:
        st.error("Execution Aborted: Algorithmic parameters require valid active trend metrics.")
    else:
        message = f"""🏦 <b>CORE STRUCTURAL SIGNAL SETUP</b>\n\nVECTOR PAIR: {selected_pair}\nSIGNAL BIAS: <b>{current_result['signal']}</b>\nCONFIDENCE COEFFICIENT: {current_result['confidence']}%\nSMC STRUCTURE: {current_result['structure']}\n\nENTRY RATE: {current_result['entry']}\nTARGET PROFIT (TP): {current_result['tp']}\nSTOP LOSS (SL): {current_result['sl']}\n\n📊 EXPECTED RANGE YIELD: <b>{current_result['pips']} Pips</b>\nCeiling Liquidity Line: {current_result['recent_high']}\nFloor Liquidity Line: {current_result['recent_low']}\n\nRSI VALUE: {current_result['rsi']}\nSYSTEM TIME STAMP: {current_result['timestamp']}"""
        ok, err = send_telegram(message)
        if ok: st.success("✅ Configuration array deployed to configured channels.")
        else: st.error(f"❌ Transmission exception: {err}")

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
