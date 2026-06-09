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
st.set_page_config(page_title="CORE VECTOR MATRIX PRO", page_icon="🏦", layout="wide")

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
st.sidebar.success("✅ Institutional Data Pipeline Engaged")

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
# HIGH-FIDELITY DATA INGESTION ENGINE (WebSocket/API Fallback)
# =====================================================
pairs = ["EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "XAUUSD"]
selected_pair = st.sidebar.selectbox("Select Active Vector Pair", pairs)

@st.cache_data(ttl=10)
def fetch_ticker_backbone(symbol, period, interval):
    mapping = {
        "EURUSD": "EURUSD=X", "GBPUSD": "GBPUSD=X",
        "USDJPY": "JPY=X", "AUDUSD": "AUDUSD=X", "XAUUSD": "GC=F"
    }
    ticker = mapping.get(symbol)
    try:
        df = yf.download(ticker, period=period, interval=interval, progress=False)
        if df is None or df.empty: return pd.DataFrame()
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        df_res = df.reset_index()
        t_col = "Datetime" if "Datetime" in df_res.columns else "Date"
        return pd.DataFrame({
            "time": df_res[t_col].squeeze(),
            "Open": df_res["Open"].squeeze().astype(float),
            "High": df_res["High"].squeeze().astype(float),
            "Low": df_res["Low"].squeeze().astype(float),
            "Close": df_res["Close"].squeeze().astype(float),
            "Volume": df_res["Volume"].squeeze().astype(float)
        }).dropna().reset_index(drop=True)
    except Exception:
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

# 2 & 3: ADVANCED INSTITUTIONAL ALGORITHMIC MATRICES
def detect_true_liquidity_sweeps(df_ltf, df_htf):
    """Calculates actual Daily/Macro Structural sweeps rather than simple local ranges"""
    prev_macro_high = df_htf["High"].iloc[-2]
    prev_macro_low = df_htf["Low"].iloc[-2]
    
    current_high = df_ltf["High"].iloc[-1]
    current_low = df_ltf["Low"].iloc[-1]
    current_close = df_ltf["Close"].iloc[-1]
    
    sweep_bsl = current_high > prev_macro_high and current_close < prev_macro_high
    sweep_ssl = current_low < prev_macro_low and current_close > prev_macro_low
    return sweep_bsl, sweep_ssl

def detect_volume_weighted_fvg(df):
    """Calculates Imbalances and amplifies weight if backed by Institutional Displacement Volume"""
    if len(df) < 3: return False, False, 0
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
# ULTIMATE TRIPLE MULTI-TIMEFRAME CONFLUENCE MATRIX ENGINE
# =====================================================
def predictive_matrix_engine(pair):
    # Core Data Tiers Execution
    df_ltf = fetch_ticker_backbone(pair, period="5d", interval="15m")  # Execution Tier
    df_itf = fetch_ticker_backbone(pair, period="15d", interval="1h")  # Intermediary Structural Shift Tier
    df_htf = fetch_ticker_backbone(pair, period="30d", interval="4h")  # Macro Institutional Flow Tier

    if df_ltf.empty or df_itf.empty or df_htf.empty or len(df_ltf) < 40 or len(df_htf) < 20:
        return {
            "signal": "NEUTRAL", "confidence": 0, "entry": 0, "tp": 0, "sl": 0, "pips": 0, "rsi": 50,
            "structure": "DATA FEED STABILIZING MATRIX", "buy_score": 0, "sell_score": 0,
            "session": trading_session(), "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "recent_high": 0, "recent_low": 0
        }

    # 1. TRIPLE TIMEFRAME STRUCTURAL VALIDATION MATRIX
    htf_ema = df_htf["Close"].ewm(span=20).mean().iloc[-1]
    itf_ema = df_itf["Close"].ewm(span=20).mean().iloc[-1]
    
    macro_bullish = df_htf["Close"].iloc[-1] > htf_ema and df_itf["Close"].iloc[-1] > itf_ema
    macro_bearish = df_htf["Close"].iloc[-1] < htf_ema and df_itf["Close"].iloc[-1] < itf_ema
    
    htf_bias = "BULLISH" if macro_bullish else ("BEARISH" if macro_bearish else "NEUTRAL")

    # 2. QUANT EXTRACTION & CONFLUENCE CALCULATOR
    df_ltf = calculate_swing_pivots(df_ltf, left=5, right=5)
    recent_high = float(df_ltf["High"].tail(30).max())
    recent_low = float(df_ltf["Low"].tail(30).min())
    price = float(df_ltf["Close"].iloc[-1])
    atr_val = calculate_atr(df_ltf)

    # Invoke Premium Analytics Features
    sweep_bsl, sweep_ssl = detect_true_liquidity_sweeps(df_ltf, df_htf)
    fvg_buy, fvg_sell, vol_multiplier = detect_volume_weighted_fvg(df_ltf)
    ob_bull, ob_bear = detect_institutional_order_block(df_ltf)

    buy_score = 0
    sell_score = 0

    # Apply Structured Multiplier Equations
    if htf_bias == "BULLISH": buy_score += 30
    if htf_bias == "BEARISH": sell_score += 30
    if sweep_ssl: buy_score += 25
    if sweep_bsl: sell_score += 25
    if fvg_buy: buy_score += int(15 * vol_multiplier)
    if fvg_sell: sell_score += int(15 * vol_multiplier)
    if ob_bull: buy_score += 15
    if ob_bear: sell_score += 15

    # Premium/Discount Filtering Rule Protection
    midpoint = recent_low + ((recent_high - recent_low) * 0.5)
    if price > midpoint: buy_score = int(buy_score * 0.5)
    if price < midpoint: sell_score = int(sell_score * 0.5)

    # 4. SIGNAL FILTRATION BARRIER
    signal = "NEUTRAL"
    confidence = max(buy_score, sell_score)

    if buy_score >= 65 and htf_bias == "BULLISH": signal = "STRONG BUY (SMC QUANT MATRIX)"
    elif buy_score >= 45 and htf_bias == "BULLISH": signal = "BUY RE-ENTRY VECTOR"
    elif sell_score >= 65 and htf_bias == "BEARISH": signal = "STRONG SELL (SMC QUANT MATRIX)"
    elif sell_score >= 45 and htf_bias == "BEARISH": signal = "SELL RE-ENTRY VECTOR"

    # Risk Target Deployments
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
        "tp": round(tp, 5), "sl": round(sl, 5), "pips": pip_yield, "rsi": round(rsi_val, 1),
        "structure": f"HTF Confluence: {htf_bias} | Vol Displacement Factor: {vol_multiplier}x",
        "buy_score": min(buy_score, 100), "sell_score": min(sell_score, 100), "session": trading_session(),
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "recent_high": round(recent_high, 5), "recent_low": round(recent_low, 5)
    }

# =====================================================
# SYSTEM MATRIX ASYNC INFRASTRUCTURE SCANNER
# =====================================================
@st.cache_data(ttl=10)
def run_matrix_portfolio_scan(pairs_tuple):
    scan_results = []
    for p in pairs_tuple:
        try:
            res = predictive_matrix_engine(p)
            scan_results.append([p, res["signal"], f"{res['confidence']}%", res["structure"], res["pips"], res["session"]])
        except Exception:
            scan_results.append([p, "MATRIX COMPILING TIMEOUT", "—", "—", 0, "—"])
    return scan_results

# =====================================================
# INTERFACE RENDER LAYOUT SEGMENTS
# =====================================================
@st.fragment(run_every=5)
def render_live_dashboard(pair):
    market_data = fetch_ticker_backbone(pair, period="5d", interval="15m")
    if market_data.empty:
        st.warning("Data network array pipeline recovering from system limit parameters...")
        return

    result = predictive_matrix_engine(pair)
    st.session_state.shared_prediction = result

    plot_df = market_data.tail(100)
    fig = go.Figure()
    fig.add_trace(go.Candlestick(
        x=plot_df["time"], open=plot_df["Open"], high=plot_df["High"], low=plot_df["Low"], close=plot_df["Close"], name=pair,
        increasing_line_color='#00E676', increasing_fillcolor='#00E676',
        decreasing_line_color='#FF1744', decreasing_fillcolor='#FF1744'
    ))
    
    if result["recent_high"] > 0:
        fig.add_hline(y=result["recent_high"], line_dash="dash", line_color="rgba(255, 145, 0, 0.5)", annotation_text="BSL Pool Target")
        fig.add_hline(y=result["recent_low"],  line_dash="dash", line_color="rgba(0, 229, 255, 0.5)", annotation_text="SSL Pool Target")

    fig.update_layout(title=f"📡 QUANT MATRIX MULTI-TIMEFRAME ENGINE: {pair}", template="plotly_dark", height=450, xaxis_rangeslider_visible=False, uirevision="keep", paper_bgcolor='#0A0E17', plot_bgcolor='#0F1626', margin=dict(l=10, r=10, t=40, b=10))
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=True, gridcolor='#1E293B')
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("### 🔍 Advanced Vector Accumulation Metrics")
    sc1, sc2 = st.columns(2)
    sc1.markdown(f"<div style='background-color:#0F1626; padding:12px; border-radius:8px; border-left:4px solid #00E676;'>🟢 Weighted Buy Confluence Factor: <b style='color:#00E676; font-family:JetBrains Mono;'>{result['buy_score']}/100</b></div>", unsafe_allow_html=True)
    sc2.markdown(f"<div style='background-color:#0F1626; padding:12px; border-radius:8px; border-left:4px solid #FF1744;'>🔴 Weighted Sell Distribution Weight: <b style='color:#FF1744; font-family:JetBrains Mono;'>{result['sell_score']}/100</b></div>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    color_hex = "#FFFFFF"
    if "BUY" in result["signal"]: color_hex = "#00E676"
    elif "SELL" in result["signal"]: color_hex = "#FF1744"
        
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.markdown(f"<div data-testid='stMetricSimpleNormal'><div data-testid='stMetricLabel'>Validated Matrix Vector</div><div style='font-size:1.0rem; font-weight:600; color:{color_hex};'>{result['signal']}</div></div>", unsafe_allow_html=True)
    with c2: st.markdown(f"<div data-testid='stMetricSimpleNormal'><div data-testid='stMetricLabel'>Confluence Confidence</div><div style='font-size:1.5rem; font-weight:600; color:#00E5FF;'>{result['confidence']}%</div></div>", unsafe_allow_html=True)
    with c3: st.markdown(f"<div data-testid='stMetricSimpleNormal'><div data-testid='stMetricLabel'>Proportional Target Yield</div><div style='font-size:1.5rem; font-weight:600; color:#FF9100;'>{result['pips']} Pips</div></div>", unsafe_allow_html=True)
    with c4: st.markdown(f"<div data-testid='stMetricSimpleNormal'><div data-testid='stMetricLabel'>Active Global Session</div><div style='font-size:0.95rem; font-weight:600; color:#94A3B8; margin-top:5px;'>{result['session']}</div></div>", unsafe_allow_html=True)

    if "STRONG" in result["signal"] and result["pips"] >= 12.0:
        components.html('<audio autoplay style="display:none;"><source src="https://actions.google.com/sounds/v1/alarms/digital_watch_alarm_long.ogg" type="audio/ogg"></audio>', height=0)
        st.toast(f"🚨 STRATEGIC MULTI-TIMEFRAME QUANT SIGNAL DETECTED FOR {pair}!", icon="💰")

@st.fragment(run_every=12)
def render_scanner_block():
    st.subheader("📡 Portfolio Matrix Scanner")
    scan_data = run_matrix_portfolio_scan(tuple(pairs))
    scanner_df = pd.DataFrame(scan_data, columns=["Pair", "Structural Signal Bias", "Confidence Factor", "SMC Architecture Status", "Risk Range Projection", "Current Session Flow"])
    st.dataframe(scanner_df, use_container_width=True, hide_index=True)

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
            message = f"<b>🏦 CORE STRUCTURAL SIGNAL SETUP DETECTED</b>\n\nVECTOR PAIR: {pair}\nSIGNAL BIAS: <b>{current_result['signal']}</b>\nCONFIDENCE: {current_result['confidence']}%\nSMC STRUCTURE: {current_result['structure']}\n\nENTRY RATE: {current_result['entry']}\nTARGET PROFIT (TP): {current_result['tp']}\nSTOP LOSS (SL): {current_result['sl']}\n\n📊 EXPECTED RANGE YIELD: <b>{current_result['pips']} Pips</b>\nCeiling Liquidity Line: {current_result['recent_high']}\nFloor Liquidity Line: {current_result['recent_low']}\n\nRSI VALUE: {current_result['rsi']}\nSYSTEM TIME STAMP: {current_result['timestamp']}"
            ok, err = send_telegram(message)
            if ok: st.success("✅ Configuration array deployed to configured channels.")
            else: st.error(f"❌ Transmission exception: {err}")

# =====================================================
# LAYOUT ASSEMBLE ARCHITECTURE
# =====================================================
st.markdown('<h1 class="terminal-header">TECH-STAR🚨</h1>', unsafe_allow_html=True)
st.markdown('<h2 class="terminal-header">🏦 INSTITUTIONAL FOREX TERMINAL PRO</h2>', unsafe_allow_html=True)
st.markdown("<p style='color:#64748B; margin-top:-15px;'>High-Fidelity Multi-Timeframe Confluence Analytics Core</p>", unsafe_allow_html=True)
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
