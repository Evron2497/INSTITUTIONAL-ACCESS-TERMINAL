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
st.set_page_config(page_title="FOREX SIGNALS", page_icon="🏦", layout="wide")

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

# =====================================================
# YFINANCE INITIALIZATION & STATUS
# =====================================================
st.sidebar.success("✅ Yahoo Finance Engine Active")

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
                st.error(f"Telegram error: {r.text}")
        except Exception as e:
            success = False
            st.error(f"Telegram connection error: {str(e)}")
    return success

# =====================================================
# CONFIG & DATA FETCHING
# =====================================================
pairs = [
    "EURUSD", "GBPUSD", "USDJPY", "USDCHF", "USDCAD",
    "AUDUSD", "NZDUSD", "EURGBP", "EURJPY", "GBPJPY",
    "XAUUSD", "BTCUSD"
]

selected_pair = st.sidebar.selectbox("Select Pair", pairs)

@st.cache_data(ttl=1)
def get_data(symbol, interval="15m", period="5d"):
    """
    Fetches historical data from Yahoo Finance.
    Converts currency pairs to Yahoo format (e.g., EURUSD=X or BTC-USD).
    """
    # Format ticker for Yahoo Finance
    if symbol == "BTCUSD":
        yf_symbol = "BTC-USD"
    elif symbol == "XAUUSD":
        yf_symbol = "GC=F"  # Gold Futures; use "XAUUSD=X" if your feed supports it
    else:
        yf_symbol = f"{symbol}=X"

    try:
        ticker = yf.Ticker(yf_symbol)
        df = ticker.history(interval=interval, period=period)
        
        if df.empty:
            return pd.DataFrame()
            
        df = df.reset_index()
        # Handle different datetime naming formats from yfinance versions
        if "Datetime" in df.columns:
            df.rename(columns={"Datetime": "time"}, inplace=True)
        elif "Date" in df.columns:
            df.rename(columns={"Date": "time"}, inplace=True)
            
        # Standardize columns to match downstream logic
        df.rename(columns={
            "Open": "Open",
            "High": "High",
            "Low": "Low",
            "Close": "Close",
            "Volume": "Volume"
        }, inplace=True)
        
        return df
    except Exception as e:
        st.error(f"Error fetching data for {symbol}: {str(e)}")
        return pd.DataFrame()

# =====================================================
# DYNAMIC FRACTAL & MATHEMATICAL INDICATORS
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
    tr = np.maximum(
        df["High"] - df["Low"],
        np.maximum(
            abs(df["High"] - df["Close"].shift()),
            abs(df["Low"] - df["Close"].shift())
        )
    )
    return tr.rolling(period).mean().iloc[-1]

def rsi(df, period=14):
    delta = df["Close"].diff()
    gain = delta.clip(lower=0).rolling(period).mean()
    loss = (-delta.clip(upper=0)).rolling(period).mean()
    rs = gain / loss
    if loss.iloc[-1] == 0:
        return 50.0
    return (100 - (100 / (1 + rs))).iloc[-1]

def trading_session():
    hour = datetime.now(timezone.utc).hour
    if hour >= 0 and hour < 7:
        return "ASIAN"
    elif hour >= 7 and hour < 13:
        return "LONDON"
    elif hour >= 13 and hour < 21:
        return "NEW YORK"
    return "CLOSED"

def calculate_pips(entry, tp, pair):
    pip_value = 0.01 if "JPY" in pair.upper() else 0.0001
    return round(abs(tp - entry) / pip_value, 1)

# =====================================================
# HIGH-CONVICTION ALGO PREDICTION ENGINE
# =====================================================
def institutional_engine(df, pair):
    if df.empty or len(df) < 50:  # Loosened requirements slightly for yfinance data windows
        return st.session_state.shared_prediction

    pip_multiplier = 0.01 if "JPY" in pair.upper() else 0.0001

    # 1. TIME-OF-DAY FILTER (Optimized for flexible tracking)
    current_time_utc = datetime.now(timezone.utc)
    float_time = current_time_utc.hour + (current_time_utc.minute / 60.0)
    
    london_killzone = (6.0 <= float_time <= 10.0)
    new_york_killzone = (11.5 <= float_time <= 16.0)
    asia_killzone = (0.0 <= float_time <= 4.5)
    is_active_killzone = london_killzone or new_york_killzone or asia_killzone

    # 2. VOLATILITY FLOOR CHECK
    atr_val = calculate_atr(df)
    atr_in_pips = atr_val / pip_multiplier

    # 3. INTERMEDIATE HTF TREND VALIDATION (M30 Structural Flow via yfinance)
    df_m30 = get_data(pair, interval="30m", period="5d")
    m60_bias = "NEUTRAL"
    if not df_m30.empty and len(df_m30) >= 20:
        m30_ema = df_m30["Close"].ewm(span=30).mean().iloc[-1]
        m60_bias = "BULLISH" if df_m30["Close"].iloc[-1] > m30_ema else "BEARISH"

    # 4. SWING PIVOTS & LIQUIDITY POOL TRACKING
    df = calculate_swing_pivots(df, left_bars=5, right_bars=5)
    valid_highs = df["Swing_High"].dropna()
    valid_lows = df["Swing_Low"].dropna()
    
    recent_high = valid_highs.iloc[-1] if not valid_highs.empty else df["High"].max()
    recent_low = valid_lows.iloc[-1] if not valid_lows.empty else df["Low"].min()

    # 5. PREMIUM VS DISCOUNT EQUILIBRIUM MODEL
    current_range = recent_high - recent_low
    price = df["Close"].iloc[-1]
    
    is_in_discount = price < (recent_low + (current_range * 0.50)) 
    is_in_premium = price > (recent_low + (current_range * 0.50))  

    # 6. LIQUIDITY POOL SWEEP DETECTOR
    sweep_buy = False
    sweep_sell = False
    for idx in range(-6, 0):
        if idx >= -len(df):
            if df["Low"].iloc[idx] < recent_low and df["Close"].iloc[idx] > recent_low:
                sweep_buy = True
            if df["High"].iloc[idx] > recent_high and df["Close"].iloc[idx] < recent_high:
                sweep_sell = True

    # 7. MARKET STRUCTURE SHIFT (MSS)
    mss_bullish = False
    mss_bearish = False
    last_candle_body = abs(df["Close"].iloc[-1] - df["Open"].iloc[-1])
    historical_bodies = abs(df["Close"] - df["Open"]).tail(20).mean()
    
    if df["Close"].iloc[-1] > recent_high or (df["High"].iloc[-1] > recent_high and last_candle_body > historical_bodies):
        mss_bullish = True
    if df["Close"].iloc[-1] < recent_low or (df["Low"].iloc[-1] < recent_low and last_candle_body > historical_bodies):
        mss_bearish = True

    # 8. INSTITUTIONAL IMBALANCE (Fair Value Gap)
    fvg_buy = df["Low"].iloc[-1] > df["High"].iloc[-3]
    fvg_sell = df["High"].iloc[-1] < df["Low"].iloc[-3]

    # 9. PERFORMANCE MATRIX SCORING
    buy_score, sell_score = 0, 0
    
    if m60_bias == "BULLISH": buy_score += 35
    if m60_bias == "BEARISH": sell_score += 35
    
    if sweep_buy: buy_score += 25
    if sweep_sell: sell_score += 25
    
    if mss_bullish: buy_score += 25
    if mss_bearish: sell_score += 25
    
    if fvg_buy: buy_score += 15
    if fvg_sell: sell_score += 15

    # HARD PRICING LOGIC ARCHITECTURE
    if not is_in_discount: buy_score = int(buy_score * 0.4)       
    if not is_in_premium: sell_score = int(sell_score * 0.4)       

    signal = "NEUTRAL"
    confidence = max(buy_score, sell_score)

    if buy_score >= 55: signal = "BUY"
    if buy_score >= 75: signal = "STRONG BUY (A+ Setup)"
    if sell_score >= 55: signal = "SELL"
    if sell_score >= 75: signal = "STRONG SELL (A+ Setup)"

    # 10. TARGET ARCHITECTURE VALIDATION
    entry = float(price)
    tp, sl = entry, entry

    if "BUY" in signal:
        tp = recent_high
        pips_to_target = (tp - entry) / pip_multiplier
        if pips_to_target < 10.0:
            tp = entry + (12 * pip_multiplier)
        sl = recent_low - (atr_val * 0.5)

    elif "SELL" in signal:
        tp = recent_low
        pips_to_target = (entry - tp) / pip_multiplier
        if pips_to_target < 10.0:
            tp = entry - (12 * pip_multiplier)
        sl = recent_high + (atr_val * 0.5)

    pips = calculate_pips(entry, tp, pair) if "NEUTRAL" not in signal else 0
    rsi_val = rsi(df)

    return {
        "signal": signal,
        "confidence": round(confidence, 1),
        "entry": round(entry, 5),
        "tp": round(tp, 5),
        "sl": round(sl, 5),
        "pips": round(pips, 1),
        "rsi": round(rsi_val, 1),
        "structure": f"M30 Flow: {m60_bias} | Vol Window: {'ACTIVE' if is_active_killzone else 'OFF-PEAK'}",
        "buy_score": buy_score,
        "sell_score": sell_score,
        "session": trading_session(),
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "recent_high": round(float(recent_high), 5),
        "recent_low": round(float(recent_low), 5)
    }

# =====================================================
# SEAMLESS ASYNC REAL-TIME REFRESH MATRIX (UI PROTECTED)
# =====================================================
@st.fragment(run_every=5)
def render_live_dashboard(pair):
    market_data = get_data(pair, interval="15m", period="5d")
    result = institutional_engine(market_data, pair)
    
    # Write to session state directly so external dispatch elements can read it
    st.session_state.shared_prediction = result

    # --- Plotly Candlestick Chart with Structural Lines ---
    if not market_data.empty:
        plot_df = calculate_swing_pivots(market_data, left_bars=5, right_bars=5)
        fig = go.Figure()
        
        fig.add_trace(go.Candlestick(
            x=plot_df["time"], open=plot_df["Open"], high=plot_df["High"],
            low=plot_df["Low"], close=plot_df["Close"], name=pair
        ))
        
        fig.add_trace(go.Scatter(
            x=plot_df["time"], y=plot_df["Swing_High"], mode="markers", name="HTF Ceiling Pool (BSL)",
            marker=dict(color="#FF4B4B", size=8, symbol="triangle-down")
        ))
        
        fig.add_trace(go.Scatter(
            x=plot_df["time"], y=plot_df["Swing_Low"], mode="markers", name="HTF Floor Pool (SSL)",
            marker=dict(color="#00F0FF", size=8, symbol="triangle-up")
        ))

        if result["recent_high"] > 0:
            fig.add_hline(y=result["recent_high"], line_dash="dash", line_color="rgba(255, 75, 75, 0.6)", annotation_text="Buy-Side Liquidity Pool")
            fig.add_hline(y=result["recent_low"], line_dash="dash", line_color="rgba(0, 240, 255, 0.6)", annotation_text="Sell-Side Liquidity Pool")
            eq_calc = result["recent_low"] + ((result["recent_high"] - result["recent_low"]) * 0.5)
            fig.add_hline(y=eq_calc, line_dash="dot", line_color="#FFFF00", annotation_text="Equilibrium (50%)", annotation_position="bottom left")

        fig.update_layout(
            title=f"🔥 LIVE {pair} (15M Matrix Grid via Yahoo Finance)", template="plotly_dark",
            height=500, xaxis_rangeslider_visible=False, uirevision="keep"
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Waiting for live Yahoo Finance data stream...")

    # --- Live Main Page Structural Scoring (Relocated from Sidebar) ---
    st.markdown("### 🔍 Live Structural Scoring Matrix")
    st.progress(int(max(result["buy_score"], result["sell_score"])) / 100)
    
    sc1, sc2 = st.columns(2)
    sc1.write(f"🟢 **Buy Structural Accumulation:** {result['buy_score']}/100")
    sc2.write(f"🔴 **Sell Structural Accumulation:** {result['sell_score']}/100")
    st.markdown("---")

    # --- Topside Metric Blocks ---
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Structural Bias", result["signal"])
    c2.metric("Matrix Confidence", f"{result['confidence']}%")
    c3.metric("Calculated Target (Pips)", result["pips"])
    c4.metric("Active Session Window", result["session"])

    with st.expander("View Raw Structural Engine Logs (JSON)"):
        st.json(result)

    if "STRONG" in result["signal"] and result["pips"] >= 10.0:
        audio_url = "https://actions.google.com/sounds/v1/alarms/digital_watch_alarm_long.ogg"
        st.audio(audio_url, format="audio/ogg", autoplay=True)
        st.toast(f"🚨 {pair} SETUP DETECTED: {result['pips']} Pips Target!", icon="💰")

    # =====================================================
    # REAL-TIME SCANNER ARRAY
    # =====================================================
    st.subheader("📡 Multi-Pair Market Scanner")
    scan_data = []

    for p in pairs:
        pair_df = get_data(p)
        pair_res = institutional_engine(pair_df, p)
        scan_data.append([
            p, pair_res["signal"], f"{pair_res['confidence']}%", pair_res["structure"], pair_res["pips"], pair_res["session"]
        ])

    scanner_df = pd.DataFrame(scan_data, columns=["Pair", "Signal Bias", "Confidence Factor", "SMC Structure", "Pips Target", "Session"])
    st.dataframe(scanner_df, use_container_width=True)

# =====================================================
# DASHBOARD INTERFACE INITIALIZATION
# =====================================================
st.title("🏦 Institutional Forex AI Engine (SMC/Fractal Verified)")

# Render background fragment loop
render_live_dashboard(selected_pair)

# Access shared state safe prediction dictionary
current_result = st.session_state.shared_prediction

# =====================================================
# SIGNAL DISPATCH HUB
# =====================================================
st.subheader("📩 Signal Dispatch Center")
confirm_send = st.checkbox("Verify structural validation filters and authorize telegram broadcast")

if st.button("🚀 BROADCAST TERMINAL SIGNAL"):
    if not confirm_send:
        st.warning("Action Blocked: Please acknowledge verification checkbox.")
        st.stop()
    if "NEUTRAL" in current_result["signal"]:
        st.error("Action Aborted: Engine must hold an active structural Bias (BUY/SELL) to broadcast.")
        st.stop()

    message = f"""
🏦 <b>EVON INSTITUTIONAL SIGNAL</b>

PAIR: {selected_pair}
SIGNAL: <b>{current_result['signal']}</b>
CONFIDENCE: {current_result['confidence']}%
SMC STRUCTURE: {current_result['structure']}

ENTRY: {current_result['entry']}
TP: {current_result['tp']}
SL: {current_result['sl']}

📊 TARGET: <b>{current_result['pips']} pips</b>
Ceiling Liquidity: {current_result['recent_high']}
Floor Liquidity: {current_result['recent_low']}

RSI: {current_result['rsi']}
SESSION: {current_result['session']}
TIMESTAMP: {current_result['timestamp']}
"""
    if send_telegram(message):
        st.success("✅ Broadcast dispatched successfully to Telegram channels.")

# =====================================================
# EMBEDDED INTEGRATIONS (TRADINGVIEW)
# =====================================================
st.subheader("📊 Interactive Analytical Sheet")
symbol_tv = f"OANDA:{selected_pair}"

html_widget = f"""
<script src="https://s3.tradingview.com/tv.js"></script>
<div id="tv_chart_container"></div>
<script>
new TradingView.widget({{
  "symbol": "{symbol_tv}",
  "interval": "15",
  "container_id": "tv_chart_container",
  "width": "100%",
  "height": 500,
  "theme": "dark",
  "style": "1",
  "locale": "en",
  "toolbar_bg": "#f1f3f6",
  "enable_publishing": false,
  "hide_side_toolbar": false,
  "allow_symbol_change": true
}});
</script>
"""
components.html(html_widget, height=520)
