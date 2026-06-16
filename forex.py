import os
from datetime import datetime, timezone
import time
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
        @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;500;600&family=Space+Grotesk:wght@300;400;500;600;700&display=swap');
        
        html, body, [data-testid="stAppViewContainer"] {
            background-color: #060913 !important;
            font-family: 'Space Grotesk', sans-serif !important;
            color: #E2E8F0 !important;
        }
        
        .main-title {
            font-family: 'Space Grotesk', sans-serif;
            font-weight: 700;
            font-size: 2.2rem;
            background: linear-gradient(135deg, #00F0FF 0%, #7000FF 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            letter-spacing: -0.03em;
            margin-bottom: 5px;
        }
        
        .sub-title-bar {
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.85rem;
            color: #64748B;
            text-transform: uppercase;
            letter-spacing: 0.1em;
            margin-bottom: 25px;
        }

        [data-testid="stSidebar"] {
            background-color: #090D1A !important;
            border-right: 1px solid #1E293B !important;
        }
        
        .matrix-card {
            background: rgba(15, 23, 42, 0.65) !important;
            border: 1px solid rgba(255, 255, 255, 0.05) !important;
            border-left: 4px solid #00F0FF !important;
            border-radius: 12px !important;
            padding: 20px !important;
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37) !important;
            backdrop-filter: blur(8px) !important;
            margin-bottom: 15px;
        }
        
        .matrix-card.scalping {
            border-left: 4px solid #A855F7 !important;
            background: linear-gradient(135deg, rgba(15, 23, 42, 0.8) 0%, rgba(112, 0, 255, 0.15) 100%) !important;
            box-shadow: 0px 0px 25px rgba(168, 85, 247, 0.25) !important;
        }
        .matrix-card.sell { border-left: 4px solid #FF4B4B !important; }
        .matrix-card.neutral { border-left: 4px solid #64748B !important; }

        .metric-glow-box {
            background: rgba(30, 41, 59, 0.4);
            border: 1px solid rgba(255, 255, 255, 0.05);
            border-radius: 10px;
            padding: 15px;
            text-align: center;
            box-shadow: inset 0 1px 1px rgba(255,255,255,0.05);
        }
        .metric-glow-label {
            font-size: 0.75rem;
            text-transform: uppercase;
            color: #94A3B8;
            letter-spacing: 0.07em;
            margin-bottom: 5px;
        }
        .metric-glow-val {
            font-family: 'JetBrains Mono', monospace;
            font-size: 1.4rem;
            font-weight: 600;
            color: #FFFFFF;
        }

        .stButton>button {
            background: linear-gradient(135deg, #0F172A 0%, #1E1B4B 100%) !important;
            color: #00F0FF !important;
            border: 1px solid rgba(0, 240, 255, 0.3) !important;
            border-radius: 8px !important;
            padding: 10px 24px !important;
            font-family: 'Space Grotesk', sans-serif !important;
            font-weight: 600 !important;
            letter-spacing: 0.02em !important;
            transition: all 0.3s ease !important;
            width: 100% !important;
        }
        .stButton>button:hover {
            border-color: #00F0FF !important;
            box-shadow: 0px 0px 20px rgba(0, 240, 255, 0.35) !important;
            color: #FFFFFF !important;
            transform: translateY(-1px);
        }
        
        div[data-testid="stDecoration"] {
            background-image: linear-gradient(90deg, #00F0FF, #7000FF) !important;
        }
    </style>
""", unsafe_allow_html=True)

# =====================================================
# VOLATILE SECURITY ENVELOPE PROTOCOL
# =====================================================
USERNAME = st.secrets.get("USERNAME", "")
PASSWORD = st.secrets.get("PASSWORD", "")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "shared_prediction" not in st.session_state:
    st.session_state.shared_prediction = {
        "signal": "NEUTRAL", "confidence": 0, "entry": 0, "tp": 0, "sl": 0, "pips": 0, "rsi": 50,
        "structure": "INITIALIZING", "buy_score": 0, "sell_score": 0, "session": "UNKNOWN",
        "timestamp": "", "recent_high": 0, "recent_low": 0, "fvg_status": "NONE", "ob_status": "NONE",
        "is_scalping": False, "scalping_state": "STANDBY", "conditions_passed": 0
    }

if "eqh_detected" not in st.session_state: st.session_state.eqh_detected = False
if "eql_detected" not in st.session_state: st.session_state.eql_detected = False

def render_login_form():
    st.markdown('<div style="max-width:450px; margin: 80px auto 0 auto;">', unsafe_allow_html=True)
    st.markdown('<h2 class="main-title" style="text-align:center;">CORE MATRIX LOGIN</h2>', unsafe_allow_html=True)
    st.markdown('<p class="sub-title-bar" style="text-align:center; margin-bottom:30px;">Institutional Authentication Required</p>', unsafe_allow_html=True)
    with st.form("auth_form", clear_on_submit=True):
        u = st.text_input("Access Identifier Username")
        p = st.text_input("Secure Passkey Crypt", type="password")
        if st.form_submit_button("Initialize Security Session"):
            if u == USERNAME and p == PASSWORD:
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.error("Invalid node validation configuration profile.")
    st.markdown('</div>', unsafe_allow_html=True)

if not st.session_state.logged_in:
    render_login_form()
    st.stop()

if st.sidebar.button("🔒 Terminal Session Disconnect"):
    st.session_state.logged_in = False
    st.rerun()

st.sidebar.markdown('<div style="padding: 2px 10px; background: rgba(16,185,129,0.1); border: 1px solid #10B981; border-radius:6px; color:#10B981; font-size:0.8rem; font-family:\'JetBrains Mono\'; text-align:center;">● SESSION SECURELY LINKED</div>', unsafe_allow_html=True)
st.sidebar.markdown("---")

# =====================================================
# TELEGRAM DISPATCH PIPELINE
# =====================================================
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

# =====================================================
# DATA RETRIEVAL PIPELINE
# =====================================================
pair_mapping = {
    "EURUSD": "EURUSD=X",
    "GBPUSD": "GBPUSD=X",
    "USDJPY": "USDJPY=X",
    "AUDUSD": "AUDUSD=X",
    "XAUUSD": "GC=F"
}
pairs = list(pair_mapping.keys())
st.sidebar.subheader("🎛️ Terminal Controls")
selected_pair = st.sidebar.selectbox("Active Liquidity Node Vector", pairs)
selected_tf = st.sidebar.selectbox("Execution Target Timeframe", ["5m", "15m", "1h"], index=0)

@st.cache_data(ttl=5)
def get_data_yf(display_symbol, interval="5m", period="5d"):
    yf_symbol = pair_mapping.get(display_symbol, f"{display_symbol}=X")
    try:
        ticker = yf.Ticker(yf_symbol)
        df = ticker.history(period=period, interval=interval)
        if df.empty: return pd.DataFrame()
        df = df.reset_index()
        df.rename(columns={"Datetime": "time", "Date": "time", "Open": "Open", "High": "High", "Low": "Low", "Close": "Close", "Volume": "Volume"}, inplace=True)
        return df
    except Exception:
        return pd.DataFrame()

# =====================================================
# ADVANCED MATHEMATICAL QUANTITATIVE MATHEMATICS
# =====================================================
def calculate_swing_pivots(df: pd.DataFrame, left_bars=5, right_bars=5) -> pd.DataFrame:
    df = df.copy().reset_index(drop=True)
    sh, sl = np.full(len(df), np.nan), np.full(len(df), np.nan)
    for i in range(left_bars, len(df) - right_bars):
        if df["High"].iloc[i] == df["High"].iloc[i - left_bars: i + right_bars + 1].max(): sh[i] = df["High"].iloc[i]
        if df["Low"].iloc[i] == df["Low"].iloc[i - left_bars: i + right_bars + 1].min(): sl[i] = df["Low"].iloc[i]
    df["Swing_High"], df["Swing_Low"] = sh, sl
    return df

def calculate_atr(df, period=14):
    if len(df) < period: return 0.001
    tr = np.maximum(df["High"] - df["Low"], np.maximum(abs(df["High"] - df["Close"].shift()), abs(df["Low"] - df["Close"].shift())))
    atr = tr.rolling(period).mean().iloc[-1]
    return atr if not np.isnan(atr) else 0.001

def rsi_series(df, period=14):
    if len(df) < period: return pd.Series(50.0, index=df.index)
    delta = df["Close"].diff()
    gain, loss = delta.clip(lower=0).rolling(period).mean(), (-delta.clip(upper=0)).rolling(period).mean()
    rs = gain / loss.replace(0, 1e-5)
    return (100 - (100 / (1 + rs))).fillna(50.0)

def trading_session():
    hour = datetime.now(timezone.utc).hour
    if 0 <= hour < 7: return "ASIAN (ACCUMULATION)"
    elif 7 <= hour < 13: return "LONDON (MANIPULATION)"
    elif 13 <= hour < 21: return "NEW YORK (DISTRIBUTION)"
    return "CLOSED"

# =====================================================
# SAFE-SCALPER-PRO ENGINE INTEGRATION LAYER
# =====================================================
def evaluate_scalping_matrix(df, pair):
    """
    Implements Safe-Scalper-Pro v3.41 breakout logic.
    Requires 7 criteria to trigger active scalping parameters.
    """
    if len(df) < 510: return {"is_scalping": False, "state": "INSUFFICIENT HISTORICAL BUFFER", "passed": 0, "direction": "NONE"}
    
    close, high, low = df["Close"].iloc[-1], df["High"].iloc[-1], df["Low"].iloc[-1]
    prev_close = df["Close"].iloc[-2]
    atr = calculate_atr(df)
    
    # EMAs
    ema_fast = df["Close"].ewm(span=150, adjust=False).mean().iloc[-1]
    ema_slow = df["Close"].ewm(span=510, adjust=False).mean().iloc[-1]
    
    # N-Bar breakout values
    n_bar_window = df.tail(20)
    n_bar_high = n_bar_window["High"].max()
    n_bar_low = n_bar_window["Low"].min()
    
    rsi_val = rsi_series(df).iloc[-1]
    
    # Multi-Timeframe High-TF validation logic hook
    df_h1 = get_data_yf(pair, interval="1h", period="5d")
    h1_agreement = True
    if not df_h1.empty and len(df_h1) >= 200:
        h1_ema50 = df_h1["Close"].ewm(span=50, adjust=False).mean().iloc[-1]
        h1_ema200 = df_h1["Close"].ewm(span=200, adjust=False).mean().iloc[-1]
        h1_agreement = (h1_ema50 > h1_ema200)
    
    # Check conditions
    cond_buy = [
        ema_fast > ema_slow,                                # 1. Trend direction
        (ema_fast - ema_slow) > (atr * 0.5),                # 2. Trend strength
        close > ema_fast and close > ema_slow,              # 3. Price alignment
        close > (n_bar_high - (atr * 0.1)),                 # 4. Breakout validation
        40 <= rsi_val <= 65,                                # 5. RSI range
        close > prev_close,                                 # 6. Momentum confirmation
        h1_agreement                                        # 7. Higher TF filter
    ]
    
    cond_sell = [
        ema_fast < ema_slow,                                # 1. Trend direction
        (ema_slow - ema_fast) > (atr * 0.5),                # 2. Trend strength
        close < ema_fast and close < ema_slow,              # 3. Price alignment
        close < (n_bar_low + (atr * 0.1)),                  # 4. Breakout validation
        35 <= rsi_val <= 60,                                # 5. RSI range
        close < prev_close,                                 # 6. Momentum confirmation
        not h1_agreement                                    # 7. Higher TF filter
    ]
    
    passed_buy = sum(1 for c in cond_buy if c)
    passed_sell = sum(1 for c in cond_sell if c)
    
    if passed_buy == 7: return {"is_scalping": True, "state": "🔥 SCALPING ACTIVE: BULLISH BREAKOUT", "passed": 7, "direction": "BUY"}
    if passed_sell == 7: return {"is_scalping": True, "state": "🔥 SCALPING ACTIVE: BEARISH BREAKOUT", "passed": 7, "direction": "SELL"}
    
    max_passed = max(passed_buy, passed_sell)
    return {"is_scalping": False, "state": f"STANDBY ({max_passed}/7 Conditions Synchronized)", "passed": max_passed, "direction": "NONE"}

# =====================================================
# INTEGRATED QUANTITATIVE SMC CORE SYSTEM
# =====================================================
def institutional_engine(df, pair):
    if df is None or df.empty or len(df) < 50:
        return {
            "signal": "NEUTRAL", "confidence": 0, "entry": 0, "tp": 0, "sl": 0, "pips": 0, "rsi": 50,
            "structure": "INSUFFICIENT DATA", "buy_score": 0, "sell_score": 0, "session": trading_session(),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "recent_high": 0, "recent_low": 0,
            "fvg_status": "NONE", "ob_status": "NONE", "is_scalping": False, "scalping_state": "STANDBY", "conditions_passed": 0
        }

    pip_multiplier = 0.01 if "JPY" in pair.upper() else (0.10 if "XAU" in pair.upper() else 0.0001)
    atr_val = calculate_atr(df)
    rsi_val = round(float(rsi_series(df).iloc[-1]), 1)

    # Calculate ranges
    df_pivots = calculate_swing_pivots(df)
    v_highs, v_lows = df_pivots["Swing_High"].dropna(), df_pivots["Swing_Low"].dropna()
    recent_high = float(v_highs.iloc[-1]) if not v_highs.empty else float(df["High"].max())
    recent_low = float(v_lows.iloc[-1]) if not v_lows.empty else float(df["Low"].min())
    
    # Check Safe-Scalper Matrix
    scalping_profile = evaluate_scalping_matrix(df, pair)

    buy_score = 15 if scalping_profile["direction"] == "BUY" else 0
    sell_score = 15 if scalping_profile["direction"] == "SELL" else 0
    buy_score += (scalping_profile["passed"] * 5) if scalping_profile["direction"] == "BUY" else 0
    sell_score += (scalping_profile["passed"] * 5) if scalping_profile["direction"] == "SELL" else 0

    # Fallback/Default thresholds
    price = float(df["Close"].iloc[-1])
    signal = "NEUTRAL"
    if scalping_profile["is_scalping"]:
        signal = f"SCALPING {scalping_profile['direction']}"
        confidence = 85.0
    else:
        confidence = max(buy_score, sell_score)
        if buy_score > 45: signal = "BUY BIAS"
        elif sell_score > 45: signal = "SELL BIAS"

    # Boundaries
    entry = price
    tp = entry + (25 * pip_multiplier) if "BUY" in signal else entry - (25 * pip_multiplier)
    sl = entry - (15 * pip_multiplier) if "BUY" in signal else entry + (15 * pip_multiplier)
    pips = round(abs(tp - entry) / pip_multiplier, 1)

    return {
        "signal": signal, "confidence": round(float(confidence), 1), "entry": round(entry, 5),
        "tp": round(tp, 5), "sl": round(sl, 5), "pips": pips, "rsi": rsi_val,
        "structure": f"SCALPING MODE: {scalping_profile['state']}",
        "buy_score": min(buy_score, 100), "sell_score": min(sell_score, 100), "session": trading_session(),
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "recent_high": round(recent_high, 5), "recent_low": round(recent_low, 5),
        "fvg_status": "MONITORING SCALP", "ob_status": "DYNAMIC",
        "is_scalping": scalping_profile["is_scalping"],
        "scalping_state": scalping_profile["state"],
        "conditions_passed": scalping_profile["passed"]
    }

# =====================================================
# GLOBAL TELEMETRY SCANNER LAYER
# =====================================================
@st.cache_data(ttl=5)
def run_scanner_yf(pairs_tuple, tf):
    scan_data = []
    for p in pairs_tuple:
        try:
            pair_df = get_data_yf(p, interval=tf)
            if pair_df.empty:
                scan_data.append([p, "NO DATA", "—", "—"])
                continue
            res = institutional_engine(pair_df, p)
            scan_data.append([p, res["signal"], f"{res['confidence']}%", res["scalping_state"]])
        except Exception:
            scan_data.append([p, "EXCEPTION RUN", "—", "—"])
    return scan_data

# =====================================================
# LIVE DASHBOARD RECONSTRUCTED LAYER
# =====================================================
@st.fragment(run_every=4)
def render_live_dashboard(pair, tf):
    market_data = get_data_yf(pair, interval=tf, period="5d")
    if market_data.empty or len(market_data) < 100:
        st.warning(f"Constructing data profile arrays for {pair}. Pulling extended window frames...")
        market_data = get_data_yf(pair, interval=tf, period="5d")
        if market_data.empty: return

    result = institutional_engine(market_data, pair)
    st.session_state.shared_prediction = result

    # Dynamic Layout Alert Banner for Active Scalping
    card_style = "neutral"
    if result["is_scalping"]: card_style = "scalping"
    elif "BUY" in result["signal"]: card_style = "buy"
    elif "SELL" in result["signal"]: card_style = "sell"
    
    st.markdown(f"""
    <div class="matrix-card {card_style}">
        <span style="font-family:'JetBrains Mono'; font-size:0.8rem; color:#E2E8F0;">[SCALPER PRO FRAMEWORK MONITOR]</span>
        <h2 style="margin:5px 0 0 0; font-weight:600; color:#FFFFFF;">{pair} ({tf}) — <span style="color:#FFF;">{result['scalping_state']}</span></h2>
    </div>
    """, unsafe_allow_html=True)

    # Grid Display Metrics
    m_col1, m_col2, m_col3, m_col4 = st.columns(4)
    with m_col1:
        st.markdown(f'<div class="metric-glow-box"><div class="metric-glow-label">Framework Alignment</div><div class="metric-glow-val" style="color:#A855F7;">{result["conditions_passed"]} / 7</div></div>', unsafe_allow_html=True)
    with m_col2:
        st.markdown(f'<div class="metric-glow-box"><div class="metric-glow-label">Target Projection</div><div class="metric-glow-val">{result["pips"]} Pips</div></div>', unsafe_allow_html=True)
    with m_col3:
        st.markdown(f'<div class="metric-glow-box"><div class="metric-glow-label">Momentum Scaler</div><div class="metric-glow-val">{result["rsi"]} RSI</div></div>', unsafe_allow_html=True)
    with m_col4:
        st.markdown(f'<div class="metric-glow-box"><div class="metric-glow-label">Active Session</div><div class="metric-glow-val" style="font-size:0.95rem; line-height:2.2rem; color:#00F0FF;">{result["session"].split(" ")[0]}</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Plot Visualizer
    fig = go.Figure()
    fig.add_trace(go.Candlestick(x=market_data["time"], open=market_data["Open"], high=market_data["High"], low=market_data["Low"], close=market_data["Close"], name=pair))
    
    # Add Safe Scalper EMAs for visibility
    ema150 = market_data["Close"].ewm(span=150, adjust=False).mean()
    ema510 = market_data["Close"].ewm(span=510, adjust=False).mean()
    fig.add_trace(go.Scatter(x=market_data["time"], y=ema150, line=dict(color="#00F0FF", width=1), name="Fast EMA (150)"))
    fig.add_trace(go.Scatter(x=market_data["time"], y=ema510, line=dict(color="#7000FF", width=1.5), name="Slow EMA (510)"))

    fig.update_layout(template="plotly_dark", height=380, xaxis_rangeslider_visible=False, uirevision="keep", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(l=10, r=10, t=10, b=10))
    st.plotly_chart(fig, use_container_width=True)

    with st.expander("Engine Execution Telemetry Log Frame"):
        st.json(result)

    if result["is_scalping"]:
        st.toast(f"🚨 ALGO SPHERE CONCURRENT SCALP TRIGGERED FOR {pair}!", icon="🔥")

# =====================================================
# SYSTEM FRAGMENT BLOCKS
# =====================================================
@st.fragment(run_every=15)
def render_scanner_block(tf):
    st.markdown("""
    <div style="background: rgba(15, 23, 42, 0.4); padding: 12px 15px; border-radius: 8px 8px 0 0; border: 1px solid rgba(255,255,255,0.05); border-bottom: none;">
        <span style="font-family:'JetBrains Mono'; font-size:0.8rem; color:#00F0FF; font-weight:600;">📡 ASSET NETWORK MULTI-SYMBOLS SCALP MONITOR</span>
    </div>
    """, unsafe_allow_html=True)
    scan_data = run_scanner_yf(tuple(pairs), tf)
    scanner_df = pd.DataFrame(scan_data, columns=["Asset Pair", "State Matrix Bias", "Certainty Node", "Safe-Scalper Framework Status"])
    st.dataframe(scanner_df, use_container_width=True, hide_index=True)

# =====================================================
# MAIN ENGINE LAYOUT ASSEMBLY
# =====================================================
st.markdown('<h1 class="main-title">CORE MATRIX</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-title-bar">QUANTITATIVE FOREX SCALPER MONITOR TERMINAL // VERSION 4.3.0</p>', unsafe_allow_html=True)

col_layout_left, col_layout_right = st.columns([1.8, 1.2])

with col_layout_left:
    render_live_dashboard(selected_pair, selected_tf)
    
    st.markdown("---")
    st.markdown("### 📊 Live TradingView Stream Platform")
    symbol_tv = f"OANDA:{selected_pair}"
    html_widget = f"""
    <div id="tv_chart_container" style="border: 1px solid rgba(255,255,255,0.05); border-radius: 8px; overflow: hidden;"></div>
    <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
    <script type="text/javascript">
    new TradingView.widget({{
       "width": "100%",
       "height": 450,
       "symbol": "{symbol_tv}",
       "interval": "15",
       "timezone": "Etc/UTC",
       "theme": "dark",
       "style": "1",
       "locale": "en",
       "toolbar_bg": "#0A0E17",
       "enable_publishing": false,
       "hide_side_toolbar": false,
       "allow_symbol_change": true,
       "container_id": "tv_chart_container"
    }});
    </script>
    """
    components.html(html_widget, height=470)

with col_layout_right:
    render_scanner_block(selected_tf)
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
    <div style="background: rgba(15, 23, 42, 0.4); padding: 12px 15px; border-radius: 8px 8px 0 0; border: 1px solid rgba(255,255,255,0.05); border-bottom: none;">
        <span style="font-family:'JetBrains Mono'; font-size:0.8rem; color:#7000FF; font-weight:600;">📩 HIGH-PRIORITY BROADCAST HUB</span>
    </div>
    """, unsafe_allow_html=True)
    
    with st.container(border=True):
        current_result = st.session_state.shared_prediction
        confirm_send = st.checkbox("Confirm network payload verification protocol rules.")
        
        if st.button("🚀 EXECUTE PAYLOAD BROADCAST"):
            if not confirm_send:
                st.warning("Execution Rejected: Affirm network confirmation verification protocol.")
            elif "NEUTRAL" in current_result["signal"] and not current_result["is_scalping"]:
                st.error("Execution Aborted: Algorithmic engine contains zero active market tracking variables.")
            else:
                message = f"""🏦 <b>TECH-STAR SCALPER CONCURRENT PIPELINE</b>

VECTOR NODE: <code>{selected_pair}</code> [{selected_tf}]
FRAMEWORK STATE: <b>{current_result['scalping_state']}</b>
CONFIDENCE COEFFICIENT: <code>{current_result['confidence']}%</code>

🎯 <b>STRUCTURAL EXECUTION BOUNDARIES:</b>
• Scalper Entry Point: {current_result['entry']}
• Take Profit Target: {current_result['tp']}
• Stop Loss Boundary: {current_result['sl']}
• Target Yield Forecast: {current_result['pips']} Pips

🕒 <i>Transmission Frame: {current_result['timestamp']} UTC</i>"""
                
                success, err_msg = send_telegram(message)
                if success: st.toast("Payload broadcast complete across network arrays!", icon="🚀")
                else: st.error(f"Transmission Failed: {err_msg}")
