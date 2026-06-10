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
# PAGE CONFIG
# =====================================================
st.set_page_config(page_title="PRO FOREX TERMINAL", page_icon="🏦", layout="wide")

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
        "pips": 0, "rsi": 0, "structure": "INITIALIZING", "buy_score": 0, "sell_score": 0,
        "session": "UNKNOWN", "timestamp": "", "recent_high": 0, "recent_low": 0
    }

def login():
    st.title("🏦 Institutional Access Terminal")
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

st.sidebar.success("✅ Low-Latency Engine Active")

# =====================================================
# TELEGRAM CONFIG
# =====================================================
BOT_TOKEN = st.secrets.get("BOT_TOKEN", "")
CHAT_IDS = st.secrets.get("CHAT_IDS", [])

def send_telegram(message: str):
    if not BOT_TOKEN or not CHAT_IDS:
        st.error("❌ Telegram not configured")
        return False

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    success = True
    for chat_id in CHAT_IDS:
        try:
            r = requests.post(url, data={
                "chat_id": chat_id,
                "text": message,
                "parse_mode": "HTML"
            })
            if r.status_code != 200:
                success = False
        except Exception:
            success = False
    return success

# =====================================================
# ASSET MULTIPLIER CONFIG ENGINE
# =====================================================
pairs = ["EURUSD", "GBPUSD", "USDJPY", "XAUUSD", "BTCUSD"]
selected_pair = st.sidebar.selectbox("Select Active Engine Pair", pairs)

def get_asset_metrics(pair):
    """
    Returns the appropriate asset ticker format for Yahoo Finance 
    along with correct pip/point calculations.
    """
    p = pair.upper()
    if p == "BTCUSD":
        return "BTC-USD", 1.0, "Points"
    elif p == "XAUUSD":
        return "GC=F", 0.1, "Pips"
    elif "JPY" in p:
        return f"{p}=X", 0.01, "Pips"
    else:
        return f"{p}=X", 0.0001, "Pips"

@st.cache_data(ttl=2)
def get_data(symbol, interval="15m", period="5d"):
    yf_symbol, _, _ = get_asset_metrics(symbol)
    try:
        ticker = yf.Ticker(yf_symbol)
        df = ticker.history(interval=interval, period=period)
        if df.empty:
            return pd.DataFrame()
        df = df.reset_index()
        time_col = "Datetime" if "Datetime" in df.columns else ("Date" if "Date" in df.columns else df.columns[0])
        df.rename(columns={time_col: "time", "Open": "Open", "High": "High", "Low": "Low", "Close": "Close", "Volume": "Volume"}, inplace=True)
        return df
    except Exception:
        return pd.DataFrame()

# =====================================================
# MATHEMATICAL MATRICES
# =====================================================
def calculate_swing_pivots(df: pd.DataFrame, left_bars: int = 5, right_bars: int = 5) -> pd.DataFrame:
    df = df.copy()
    df["Swing_High"] = np.nan
    df["Swing_Low"] = np.nan
    for i in range(left_bars, len(df) - right_bars):
        window_highs = df["High"].iloc[i - left_bars: i + right_bars + 1]
        window_lows = df["Low"].iloc[i - left_bars: i + right_bars + 1]
        if df["High"].iloc[i] == window_highs.max():
            df.at[df.index[i], "Swing_High"] = df["High"].iloc[i]
        if df["Low"].iloc[i] == window_lows.min():
            df.at[df.index[i], "Swing_Low"] = df["Low"].iloc[i]
    return df

def calculate_atr(df, period=14):
    tr = np.maximum(df["High"] - df["Low"], np.maximum(abs(df["High"] - df["Close"].shift()), abs(df["Low"] - df["Close"].shift())))
    return tr.rolling(period).mean().iloc[-1]

def rsi(df, period=14):
    delta = df["Close"].diff()
    gain = delta.clip(lower=0).rolling(period).mean()
    loss = (-delta.clip(upper=0)).rolling(period).mean()
    if loss.iloc[-1] == 0: return 50.0
    rs = gain / loss
    return 100 - (100 / (1 + rs.iloc[-1]))

def trading_session():
    hour = datetime.now(timezone.utc).hour
    if 0 <= hour < 7: return "ASIAN"
    elif 7 <= hour < 13: return "LONDON"
    elif 13 <= hour < 21: return "NEW YORK"
    return "OFF-PEAK"

# =====================================================
# HIGH-CONVICTION ALGO PREDICTION ENGINE (OPTIMIZED)
# =====================================================
def institutional_engine(df, pair):
    if df.empty or len(df) < 50:
        return st.session_state.shared_prediction

    _, pip_multiplier, unit_label = get_asset_metrics(pair)

    # 1. Killzone Validation
    current_time_utc = datetime.now(timezone.utc)
    float_time = current_time_utc.hour + (current_time_utc.minute / 60.0)
    is_active_killzone = (6.0 <= float_time <= 10.0) or (11.5 <= float_time <= 16.0) or (0.0 <= float_time <= 4.5)

    # 2. Volatility Analysis
    atr_val = calculate_atr(df)

    # 3. Structural Validation Flow (M30 Bias Check)
    df_m30 = get_data(pair, interval="30m", period="5d")
    m60_bias = "NEUTRAL"
    if not df_m30.empty and len(df_m30) >= 20:
        m30_ema = df_m30["Close"].ewm(span=30).mean().iloc[-1]
        m60_bias = "BULLISH" if df_m30["Close"].iloc[-1] > m30_ema else "BEARISH"

    # 4. Fractal Highs/Lows Pools
    df = calculate_swing_pivots(df, left_bars=5, right_bars=5)
    valid_highs = df["Swing_High"].dropna()
    valid_lows = df["Swing_Low"].dropna()
    recent_high = valid_highs.iloc[-1] if not valid_highs.empty else df["High"].max()
    recent_low = valid_lows.iloc[-1] if not valid_lows.empty else df["Low"].min()

    # 5. Equilibrium Matrix
    current_range = recent_high - recent_low
    price = df["Close"].iloc[-1]
    is_in_discount = price < (recent_low + (current_range * 0.50))
    is_in_premium = price > (recent_low + (current_range * 0.50))

    # 6. Fluid Sweep Identifiers
    sweep_buy = any(df["Low"].iloc[i] < recent_low and df["Close"].iloc[i] > recent_low for i in range(-6, 0) if i >= -len(df))
    sweep_sell = any(df["High"].iloc[i] > recent_high and df["Close"].iloc[i] < recent_high for i in range(-6, 0) if i >= -len(df))

    # 7. Market Structure Shift
    mss_bullish = df["Close"].iloc[-1] > recent_high and (abs(df["Close"].iloc[-1] - df["Open"].iloc[-1]) > abs(df["Close"] - df["Open"]).tail(20).mean())
    mss_bearish = df["Close"].iloc[-1] < recent_low and (abs(df["Close"].iloc[-1] - df["Open"].iloc[-1]) > abs(df["Close"] - df["Open"]).tail(20).mean())

    # 8. Imbalance Detection (FVG)
    fvg_buy = df["Low"].iloc[-1] > df["High"].iloc[-3]
    fvg_sell = df["High"].iloc[-1] < df["Low"].iloc[-3]

    # 9. Confluence Scoring
    buy_score, sell_score = 0, 0
    if m60_bias == "BULLISH": buy_score += 35
    if m60_bias == "BEARISH": sell_score += 35
    if sweep_buy: buy_score += 25
    if sweep_sell: sell_score += 25
    if mss_bullish: buy_score += 25
    if mss_bearish: sell_score += 25
    if fvg_buy: buy_score += 15
    if fvg_sell: sell_score += 15

    if not is_in_discount: buy_score = int(buy_score * 0.4)
    if not is_in_premium: sell_score = int(sell_score * 0.4)

    signal = "NEUTRAL"
    confidence = max(buy_score, sell_score)
    if buy_score >= 55: signal = "BUY" if buy_score < 75 else "STRONG BUY (A+ Setup)"
    if sell_score >= 55: signal = "SELL" if sell_score < 75 else "STRONG SELL (A+ Setup)"

    # 10. Volatility-Calibrated Targets
    entry = float(price)
    tp, sl = entry, entry
    min_move = 10.0 * pip_multiplier

    if "BUY" in signal:
        tp = recent_high if (recent_high - entry) >= min_move else entry + (15.0 * pip_multiplier)
        sl = recent_low - (atr_val * 0.5)
    elif "SELL" in signal:
        tp = recent_low if (entry - recent_low) >= min_move else entry - (15.0 * pip_multiplier)
        sl = recent_high + (atr_val * 0.5)

    pips = round(abs(tp - entry) / pip_multiplier, 1) if "NEUTRAL" not in signal else 0

    return {
        "signal": signal, "confidence": round(confidence, 1), "entry": round(entry, 5),
        "tp": round(tp, 5), "sl": round(sl, 5), "pips": pips, "rsi": round(rsi(df), 1),
        "structure": f"M30 Flow: {m60_bias} | Vol: {'ACTIVE' if is_active_killzone else 'OFF-PEAK'}",
        "buy_score": buy_score, "sell_score": sell_score, "session": trading_session(),
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "recent_high": round(float(recent_high), 5), "recent_low": round(float(recent_low), 5),
        "unit_label": unit_label
    }

# =====================================================
# LIVE GRAPHICAL INTERFACE
# =====================================================
@st.fragment(run_every=5)
def render_live_dashboard(pair):
    market_data = get_data(pair, interval="15m", period="5d")
    result = institutional_engine(market_data, pair)
    st.session_state.shared_prediction = result

    if not market_data.empty:
        plot_df = calculate_swing_pivots(market_data, left_bars=5, right_bars=5)
        fig = go.Figure()
        fig.add_trace(go.Candlestick(x=plot_df["time"], open=plot_df["Open"], high=plot_df["High"], low=plot_df["Low"], close=plot_df["Close"], name=pair))
        fig.add_trace(go.Scatter(x=plot_df["time"], y=plot_df["Swing_High"], mode="markers", name="Ceiling Liquidity Pool (BSL)", marker=dict(color="#FF4B4B", size=8, symbol="triangle-down")))
        fig.add_trace(go.Scatter(x=plot_df["time"], y=plot_df["Swing_Low"], mode="markers", name="Floor Liquidity Pool (SSL)", marker=dict(color="#00F0FF", size=8, symbol="triangle-up")))
        
        if result["recent_high"] > 0:
            fig.add_hline(y=result["recent_high"], line_dash="dash", line_color="rgba(255, 75, 75, 0.6)", annotation_text="BSL Pool")
            fig.add_hline(y=result["recent_low"], line_dash="dash", line_color="rgba(0, 240, 255, 0.6)", annotation_text="SSL Pool")
            fig.add_hline(y=result["recent_low"] + ((result["recent_high"] - result["recent_low"]) * 0.5), line_dash="dot", line_color="#FFFF00", annotation_text="Equilibrium (50%)")

        fig.update_layout(title=f"🔥 LIVE {pair} (15M Matrix Grid)", template="plotly_dark", height=500, xaxis_rangeslider_visible=False, uirevision="keep")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Awaiting market streaming connection...")

    st.markdown("### 🔍 Live Structural Scoring Matrix")
    st.progress(int(max(result["buy_score"], result["sell_score"])) / 100)
    sc1, sc2 = st.columns(2)
    sc1.write(f"🟢 **Buy Structural Accumulation:** {result['buy_score']}/100")
    sc2.write(f"🔴 **Sell Structural Accumulation:** {result['sell_score']}/100")
    st.markdown("---")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Structural Bias", result["signal"])
    c2.metric("Matrix Confidence", f"{result['confidence']}%")
    c3.metric(f"Calculated Target ({result.get('unit_label', 'Pips')})", result["pips"])
    c4.metric("Active Session Window", result["session"])

    # Decoupled Core Multi-Scanner Loop to Avoid Server 429 Bans
    st.subheader("📡 Multi-Pair Market Scanner")
    scan_data = []
    for p in pairs:
        p_df = get_data(p)
        p_res = institutional_engine(p_df, p)
        scan_data.append([p, p_res["signal"], f"{p_res['confidence']}%", p_res["structure"], f"{p_res['pips']} {p_res.get('unit_label', 'Pips')}"])
    
    st.dataframe(pd.DataFrame(scan_data, columns=["Pair", "Signal Bias", "Confidence", "SMC Structure", "Target Room"]), use_container_width=True)

# =====================================================
# SYSTEM EXPEDITING & DISPATCH
# =====================================================
st.title("🏦 Institutional Forex AI Engine (SMC/Fractal Verified)")
render_live_dashboard(selected_pair)
current_result = st.session_state.shared_prediction

st.subheader("📩 Signal Dispatch Center")
confirm_send = st.checkbox("Verify structural validation filters and authorize terminal broadcast")

if st.button("🚀 BROADCAST TERMINAL SIGNAL"):
    if not confirm_send:
        st.warning("Action Blocked: Please acknowledge verification checkbox.")
        st.stop()
    if "NEUTRAL" in current_result["signal"]:
        st.error("Action Aborted: Engine must hold an active structural Bias to broadcast.")
        st.stop()

    message = f"""
🏦 <b>EVON INSTITUTIONAL SIGNAL</b>
PAIR: {selected_pair}
SIGNAL: <b>{current_result['signal']}</b>
CONFIDENCE: {current_result['confidence']}%

ENTRY: {current_result['entry']}
TP: {current_result['tp']}
SL: {current_result['sl']}
📊 TARGET: <b>{current_result['pips']} {current_result.get('unit_label', 'Pips')}</b>

TIMESTAMP: {current_result['timestamp']}
"""
    if send_telegram(message):
        st.success("✅ Broadcast dispatched successfully to Telegram channels.")

st.subheader("📊 Interactive Analytical Sheet")
components.html(f"""
<script src="https://s3.tradingview.com/tv.js"></script>
<div id="tv_chart_container"></div>
<script>
new TradingView.widget({{"symbol": "OANDA:{selected_pair}", "interval": "15", "container_id": "tv_chart_container", "width": "100%", "height": 500, "theme": "dark", "style": "1", "locale": "en", "enable_publishing": false, "hide_side_toolbar": false, "allow_symbol_change": true}});
</script>
""", height=520)
