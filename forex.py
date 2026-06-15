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
# MODERN GOOGLE AI MULTI-AUTH SDK UPGRADE
# =====================================================
from google import genai
from google.oauth2.credentials import Credentials
from google.genai import types

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
        .ai-analysis-box {
            background: linear-gradient(135deg, #0F172A 0%, #1E1B4B 100%);
            border-left: 4px solid #8B5CF6;
            padding: 20px;
            border-radius: 0 12px 12px 0;
            margin-top: 20px;
            box-shadow: inset 0 1px 0 0 rgba(255, 255, 255, 0.05);
        }
    </style>
""", unsafe_allow_html=True)

# =====================================================
# AI API INITIALIZATION LAYER (PROJECT RESOLVED)
# =====================================================
GEMINI_API_KEY = str(st.secrets.get("GEMINI_API_KEY", "")).strip()
GCP_PROJECT_ID = str(st.secrets.get("GCP_PROJECT_ID", "")).strip()

if not GEMINI_API_KEY or GEMINI_API_KEY == "None":
    GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")

if not GCP_PROJECT_ID or GCP_PROJECT_ID == "None":
    GCP_PROJECT_ID = os.environ.get("GCP_PROJECT_ID", "")

ai_client = None
is_vertex = False

if GEMINI_API_KEY:
    try:
        if GEMINI_API_KEY.startswith("AQ."):
            gcp_credentials = Credentials(token=GEMINI_API_KEY)
            ai_client = genai.Client(
                vertexai=True, 
                project=GCP_PROJECT_ID if GCP_PROJECT_ID else None,
                credentials=gcp_credentials
            )
            is_vertex = True
            st.sidebar.success("🤖 Vertex AI Engine Authenticated!")
        else:
            ai_client = genai.Client(api_key=GEMINI_API_KEY)
            is_vertex = False
            st.sidebar.success("🤖 Google AI Studio Authenticated!")
    except Exception as e:
        st.sidebar.error(f"AI Init Error: {e}")
        ai_client = None
else:
    st.sidebar.warning("⚠️ Waiting for a valid API Key entry in secrets...")

# =====================================================
# GOOGLE GEMINI AI CONTEXTUAL ANALYZER
# =====================================================
@st.cache_data(ttl=60)
def run_cached_ai_analysis(res, pair):
    if not ai_client:
        return "⚠️ **AI Engine Offline**: Initialize your setup keys by assigning a valid `GEMINI_API_KEY` token string inside environment secrets."

    prompt = f"""
    You are an expert institutional risk engineer and quant operator specializing in Inner Circle Trader (ICT) setups and Smart Money Concepts (SMC).
    Run an advanced executive confluence risk validation sweep on the market telemetry parameters captured below for {pair}.
    
    Matrix Variables:
    - Current Matrix Signal: {res['signal']}
    - Engine Confidence Factor: {res['confidence']}%
    - Multi-Timeframe Structural Bias: {res['structure']}
    - Momentum RSI Scalar: {res['rsi']}
    - Fair Value Gap Verification: {res['fvg_status']}
    - System Order Block Allocation: {res['ob_status']}
    - Session Pattern Recognition Strategy: {res['pattern']}
    - Momentum Wick Divergence State: {res['divergence']}
    - Active Macro Time Window: {res['session']}

    Provide an elite, highly concise trading-desk layout analysis formatted strictly as 3 structural bullet points using professional quant terminology. 
    Explicitly detail if any underlying technical discrepancies exist (e.g., trying to buy within a Premium pricing band or selling inside a Discount zone). Keep it punchy, aggressive, and highly readable.
    """
    try:
        target_model = 'gemini-1.5-flash-001' if is_vertex else 'gemini-1.5-flash'
        response = ai_client.models.generate_content(
            model=target_model,
            contents=prompt,
        )
        return response.text
    except Exception as e:
        return f"❌ **AI Server Communication Exception**: {str(e)}"

# =====================================================
# PERSISTENT LOGIN MANAGEMENT (FIXED REFRESH LOOP)
# =====================================================
USERNAME = st.secrets.get("USERNAME", "")
PASSWORD = st.secrets.get("PASSWORD", "")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "shared_prediction" not in st.session_state:
    st.session_state.shared_prediction = {
        "signal": "NEUTRAL", "confidence": 0, "entry": 0, "tp": 0, "sl": 0,
        "pips": 0, "rsi": 50, "structure": "INITIALIZING", "buy_score": 0, "sell_score": 0,
        "session": "UNKNOWN", "timestamp": "", "recent_high": 0, "recent_low": 0,
        "fvg_status": "NONE", "ob_status": "NONE", "pattern": "NONE", "divergence": "NONE",
        "execution_timing": "AWAITING ENGINE SEED"
    }

def login():
    st.markdown('<h2 class="terminal-header">🏦 Institutional Access Terminal</h2>', unsafe_allow_html=True)
    u = st.text_input("Username", key="auth_user")
    p = st.text_input("Password", type="password", key="auth_pass")
    if st.button("Login"):
        if u == USERNAME and p == PASSWORD:
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error("Invalid credentials")

# Guard page layout initialization
if not st.session_state.logged_in:
    login()
    st.stop()

st.sidebar.success("✅ Session Active (Password Bypassed)")

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
# YFINANCE SYMBOL MAPPING
# =====================================================
pair_mapping = {
    "EURUSD": "EURUSD=X",
    "GBPUSD": "GBPUSD=X",
    "USDJPY": "USDJPY=X",
    "AUDUSD": "AUDUSD=X",
    "XAUUSD": "GC=F"
}

pairs = list(pair_mapping.keys())
selected_pair = st.sidebar.selectbox("Select Active Vector Pair", pairs)

@st.cache_data(ttl=5)
def get_data_yf(display_symbol, interval="15m", period="5d"):
    yf_symbol = pair_mapping.get(display_symbol, f"{display_symbol}=X")
    try:
        ticker = yf.Ticker(yf_symbol)
        df = ticker.history(period=period, interval=interval)
        if df.empty:
            return pd.DataFrame()
        df = df.reset_index()
        df.rename(columns={"Datetime": "time", "Date": "time", "Open": "Open", "High": "High", "Low": "Low", "Close": "Close", "Volume": "Volume"}, inplace=True)
        return df
    except Exception:
        return pd.DataFrame()

# =====================================================
# PURE ALGORIHTMIC ICT ENGINE CALCULATIONS
# =====================================================
def calculate_swing_pivots(df: pd.DataFrame, left_bars: int = 5, right_bars: int = 5) -> pd.DataFrame:
    df = df.copy().reset_index(drop=True)
    swing_high = np.full(len(df), np.nan)
    swing_low  = np.full(len(df), np.nan)

    for i in range(left_bars, len(df) - right_bars):
        window_h = df["High"].iloc[i - left_bars: i + right_bars + 1]
        window_l = df["Low"].iloc[i - left_bars: i + right_bars + 1]
        if df["High"].iloc[i] == window_h.max():
            swing_high[i] = df["High"].iloc[i]
        if df["Low"].iloc[i] == window_l.min():
            swing_low[i] = df["Low"].iloc[i]

    df["Swing_High"] = swing_high
    df["Swing_Low"]  = swing_low
    return df

def calculate_atr(df, period=14):
    if len(df) < period: return 0.001
    tr = np.maximum(df["High"] - df["Low"], np.maximum(abs(df["High"] - df["Close"].shift()), abs(df["Low"] - df["Close"].shift())))
    atr = tr.rolling(period).mean().iloc[-1]
    return atr if not np.isnan(atr) else 0.001

def rsi_series(df, period=14):
    if len(df) < period: return pd.Series(50.0, index=df.index)
    delta = df["Close"].diff()
    gain  = delta.clip(lower=0).rolling(period).mean()
    loss  = (-delta.clip(upper=0)).rolling(period).mean()
    rs = gain / loss.replace(0, 1e-5)
    rsi_vals = 100 - (100 / (1 + rs))
    return rsi_vals.fillna(50.0)

def rsi(df, period=14):
    vals = rsi_series(df, period)
    return round(float(vals.iloc[-1]), 2)

def trading_session():
    hour = datetime.now(timezone.utc).hour
    if 0 <= hour < 7: return "ASIAN (ACCUMULATION)"
    elif 7 <= hour < 13: return "LONDON (MANIPULATION)"
    elif 13 <= hour < 21: return "NEW YORK (DISTRIBUTION)"
    return "CLOSED"

def calculate_pips(entry, tp, pair):
    if "JPY" in pair.upper(): pip_value = 0.01
    elif "XAU" in pair.upper() or "GC=F" in pair.upper(): pip_value = 0.10  
    else: pip_value = 0.0001
    return round(abs(tp - entry) / pip_value, 1)

def detect_ict_structural_shifts(df: pd.DataFrame, left=5, right=5):
    df_pivots = calculate_swing_pivots(df, left_bars=left, right_bars=right)
    highs_idx = df_pivots["Swing_High"].dropna().index
    lows_idx = df_pivots["Swing_Low"].dropna().index
    
    mss_bullish = mss_bearish = bos_bullish = bos_bearish = False
    sweep_bsl = sweep_ssl = False
    
    if len(highs_idx) >= 2 and len(lows_idx) >= 2:
        last_sh = df_pivots["Swing_High"].loc[highs_idx[-1]]
        prev_sh = df_pivots["Swing_High"].loc[highs_idx[-2]]
        last_sl = df_pivots["Swing_Low"].loc[lows_idx[-1]]
        prev_sl = df_pivots["Swing_Low"].loc[lows_idx[-2]]
        
        current_close = df_pivots["Close"].iloc[-1]
        current_high = df_pivots["High"].iloc[-1]
        current_low = df_pivots["Low"].iloc[-1]
        
        if current_high > last_sh and current_close < last_sh:
            sweep_bsl = True
        if current_low < last_sl and current_close > last_sl:
            sweep_ssl = True
            
        if current_close > last_sh:
            if last_sh < prev_sh:
                mss_bullish = True
            else:
                bos_bullish = True
                
        if current_close < last_sl:
            if last_sl > prev_sl:
                mss_bearish = True
            else:
                bos_bearish = True

    return mss_bullish, mss_bearish, bos_bullish, bos_bearish, sweep_bsl, sweep_ssl

def detect_fvg(df, lookback=25):
    fvg_buy = fvg_sell = False
    for i in range(2, min(lookback, len(df) - 1)):
        if df["Low"].iloc[-i+1] > df["High"].iloc[-i-1]:
            fvg_buy = True
        if df["High"].iloc[-i+1] < df["Low"].iloc[-i-1]:
            fvg_sell = True
    return fvg_buy, fvg_sell

def detect_order_block(df):
    ob_bull = ob_bear = False
    for i in range(3, min(20, len(df))):
        candle = df.iloc[-i]
        next_two = df.iloc[-i+1:-i+3]
        if candle["Close"] < candle["Open"] and all(next_two["Close"] > next_two["Open"]):
            ob_bull = True
        if candle["Close"] > candle["Open"] and all(next_two["Close"] < next_two["Open"]):
            ob_bear = True
    return ob_bull, ob_bear

def detect_amd_pattern(df):
    if len(df) < 40: return 0, 0
    range_window = df.tail(30)
    high_low_delta = range_window["High"].max() - range_window["Low"].min()
    atr = calculate_atr(df)
    is_accumulating = high_low_delta < (atr * 3.5)
    recent_candles = df.tail(5)
    lowest_low = range_window["Low"].min()
    highest_high = range_window["High"].max()
    
    sweep_low = any(recent_candles["Low"] < lowest_low * 1.0005) and df["Close"].iloc[-1] > lowest_low
    sweep_high = any(recent_candles["High"] > highest_high * 0.9995) and df["Close"].iloc[-1] < highest_high
    
    amd_buy = 30 if (is_accumulating and sweep_low) else 0
    amd_sell = 30 if (is_accumulating and sweep_high) else 0
    return amd_buy, amd_sell

def detect_rsi_divergence(df):
    if len(df) < 35: return 0, 0
    df_pivots = calculate_swing_pivots(df, left_bars=3, right_bars=3)
    rsi_vals = rsi_series(df_pivots)
    high_indices = df_pivots["Swing_High"].dropna().index[-2:] if len(df_pivots["Swing_High"].dropna()) >= 2 else []
    low_indices = df_pivots["Swing_Low"].dropna().index[-2:] if len(df_pivots["Swing_Low"].dropna()) >= 2 else []
    
    div_buy = div_sell = 0
    if len(low_indices) == 2:
        i1, i2 = low_indices[0], low_indices[1]
        if df_pivots["Low"].loc[i2] < df_pivots["Low"].loc[i1] and rsi_vals.loc[i2] > rsi_vals.loc[i1]:
            if rsi_vals.iloc[-1] < 45: div_buy = 35
            
    if len(high_indices) == 2:
        i1, i2 = high_indices[0], high_indices[1]
        if df_pivots["High"].loc[i2] > df_pivots["High"].loc[i1] and rsi_vals.loc[i2] < rsi_vals.loc[i1]:
            if rsi_vals.iloc[-1] > 55: div_sell = 35
            
    return div_buy, div_sell

def neutral_result():
    return {
        "signal": "NEUTRAL", "confidence": 0, "entry": 0, "tp": 0, "sl": 0,
        "pips": 0, "rsi": 50, "structure": "INSUFFICIENT DATA", "buy_score": 0,
        "sell_score": 0, "session": trading_session(), "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "recent_high": 0, "recent_low": 0, "fvg_status": "NONE", "ob_status": "NONE", "pattern": "NONE", "divergence": "NONE",
        "execution_timing": "AWAITING ENGINE PARAMETERS"
    }

# =====================================================
# UPGRADED SEQUENTIAL CONFLUENCE TRADING ORDER ENGINE
# =====================================================
def institutional_engine(df, pair):
    if df is None or df.empty or len(df) < 50:
        return neutral_result()

    pip_multiplier = 0.01 if "JPY" in pair.upper() else (0.10 if "XAU" in pair.upper() else 0.0001)
    atr_val = calculate_atr(df)

    df_m30 = get_data_yf(pair, interval="30m", period="5d")
    htf_bias = "NEUTRAL"
    if df_m30 is not None and not df_m30.empty and len(df_m30) >= 30:
        m30_ema = df_m30["Close"].ewm(span=30).mean().iloc[-1]
        htf_bias = "BULLISH" if df_m30["Close"].iloc[-1] > m30_ema else "BEARISH"

    df = calculate_swing_pivots(df, left_bars=5, right_bars=5)
    valid_highs = df["Swing_High"].dropna()
    valid_lows = df["Swing_Low"].dropna()
    recent_high = float(valid_highs.iloc[-1]) if not valid_highs.empty else float(df["High"].max())
    recent_low = float(valid_lows.iloc[-1]) if not valid_lows.empty else float(df["Low"].min())

    price = float(df["Close"].iloc[-1])
    midpoint = recent_low + ((recent_high - recent_low) * 0.50)
    is_in_discount = price < midpoint
    is_in_premium = price > midpoint

    mss_bull, mss_bear, bos_bull, bos_bear, sweep_bsl, sweep_ssl = detect_ict_structural_shifts(df)
    fvg_buy, fvg_sell = detect_fvg(df)
    ob_bull, ob_bear = detect_order_block(df)
    amd_buy, amd_sell = detect_amd_pattern(df)
    div_buy, div_sell = detect_rsi_divergence(df)

    buy_score = 0
    sell_score = 0

    if sweep_ssl or mss_bull:
        buy_score += 20 if htf_bias == "BULLISH" else 5
        if mss_bull: buy_score += 35
        if sweep_ssl: buy_score += 25
        if bos_bull: buy_score += 10
        
        if ob_bull: buy_score += 15
        if fvg_buy: buy_score += 15
        buy_score += amd_buy
        buy_score += div_buy

    if sweep_bsl or mss_bear:
        sell_score += 20 if htf_bias == "BEARISH" else 5
        if mss_bear: sell_score += 35
        if sweep_bsl: sell_score += 25
        if bos_bear: sell_score += 10
        
        if ob_bear: sell_score += 15
        if fvg_sell: sell_score += 15
        sell_score += amd_sell
        sell_score += div_sell

    if not is_in_discount: buy_score = int(buy_score * 0.10)
    if not is_in_premium: sell_score = int(sell_score * 0.10)

    signal = "NEUTRAL"
    confidence = max(buy_score, sell_score)

    if buy_score >= 75: signal = "STRONG BUY (A+ Setup)"
    elif buy_score >= 50: signal = "BUY"
    
    if sell_score >= 75: signal = "STRONG SELL (A+ Setup)"
    elif sell_score >= 50 and "BUY" not in signal: signal = "SELL"

    entry = price
    tp, sl = entry, entry

    if "BUY" in signal:
        tp = recent_high
        if (tp - entry) / pip_multiplier < 12.0: tp = entry + (15 * pip_multiplier)
        sl = recent_low - (atr_val * 0.5)
    elif "SELL" in signal:
        tp = recent_low
        if (entry - tp) / pip_multiplier < 12.0: tp = entry - (15 * pip_multiplier)
        sl = recent_high + (atr_val * 0.5)

    pips = calculate_pips(entry, tp, pair) if "NEUTRAL" not in signal else 0
    rsi_val = rsi(df)

    struct_str = f"M30: {htf_bias} | Range: {'DISCOUNT' if is_in_discount else 'PREMIUM'} | "
    if mss_bull or mss_bear: struct_str += "MSS CONFIRMED"
    elif sweep_bsl or sweep_ssl: struct_str += "LIQUIDITY RUN DETECTED"
    else: struct_str += "ORDERFLOW EXPANSION"

    # --- NEW CRITICAL EXECUTION TIMING MATRIX RULE ---
    if "BUY" in signal:
        execution_timing = "⏳ DO NOT BUY NOW. Wait for price to pull back down into the discount FVG / Order block zone before placing order limits."
    elif "SELL" in signal:
        execution_timing = "⏳ DO NOT SELL NOW. Wait for price to rally back up into the premium FVG / Order block zone before placing order limits."
    else:
        execution_timing = "⏸️ No institutional footprint ready. Standby."

    return {
        "signal": signal, "confidence": round(float(confidence), 1), "entry": round(entry, 5),
        "tp": round(tp, 5), "sl": round(sl, 5), "pips": round(pips, 1), "rsi": round(rsi_val, 1),
        "structure": struct_str,
        "buy_score": buy_score, "sell_score": sell_score, "session": trading_session(),
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "recent_high": round(recent_high, 5), "recent_low": round(recent_low, 5),
        "fvg_status": "BULLISH FVG" if fvg_buy else ("BEARISH FVG" if fvg_sell else "BALANCED"),
        "ob_status": "BULLISH OB" if ob_bull else ("BEARISH OB" if ob_bear else "NO TARGETS"),
        "pattern": "MSS DISPLACEMENT" if (mss_bull or mss_bear) else "CONSOLIDATION MAPPING",
        "divergence": "BULLISH MOMENTUM DIV" if div_buy > 0 else ("BEARISH MOMENTUM DIV" if div_sell > 0 else "STABLE FLOW"),
        "execution_timing": execution_timing
    }

# =====================================================
# RUN GLOBAL MONITOR SCANNER 
# =====================================================
@st.cache_data(ttl=15)
def run_scanner_yf(pairs_tuple):
    scan_data = []
    for p in pairs_tuple:
        try:
            pair_df = get_data_yf(p)
            if pair_df.empty:
                scan_data.append([p, "NO DATA", "—", "—", 0, "—"])
                continue
            pair_res = institutional_engine(pair_df, p)
            scan_data.append([p, pair_res["signal"], f"{pair_res['confidence']}%", pair_res["structure"], pair_res["pips"], pair_res["session"]])
        except Exception:
            scan_data.append([p, "ENGINE EXCEPTION", "—", "—", 0, "—"])
    return scan_data

# =====================================================
# LIVE DASHBOARD FRAGMENT LAYER 
# =====================================================
@st.fragment(run_every=4)
def render_live_dashboard(pair):
    market_data = get_data_yf(pair, interval="15m", period="5d")
    if market_data.empty:
        st.warning(f"Failed to pull active yFinance stream buffers for {pair}. Market data may be restricted or delayed.")
        return

    result = institutional_engine(market_data, pair)
    st.session_state.shared_prediction = result

    plot_df = calculate_swing_pivots(market_data, left_bars=5, right_bars=5)
    fig = go.Figure()

    fig.add_trace(go.Candlestick(x=plot_df["time"], open=plot_df["Open"], high=plot_df["High"], low=plot_df["Low"], close=plot_df["Close"], name=pair))
    fig.add_trace(go.Scatter(x=plot_df["time"], y=plot_df["Swing_High"], mode="markers", name="Buy-Side Liquidity (BSL)", marker=dict(color="#FF4B4B", size=7, symbol="triangle-down")))
    fig.add_trace(go.Scatter(x=plot_df["time"], y=plot_df["Swing_Low"], mode="markers", name="Sell-Side Liquidity (SSL)", marker=dict(color="#00F0FF", size=7, symbol="triangle-up")))

    if result["recent_high"] > 0:
        fig.add_hline(y=result["recent_high"], line_dash="dash", line_color="rgba(255,75,75,0.5)", annotation_text="BSL Pool")
        fig.add_hline(y=result["recent_low"],  line_dash="dash", line_color="rgba(0,240,255,0.5)", annotation_text="SSL Pool")
        eq = result["recent_low"] + ((result["recent_high"] - result["recent_low"]) * 0.5)
        fig.add_hline(y=eq, line_dash="dot", line_color="#FFFF00", annotation_text="Equilibrium (50%)")

    fig.update_layout(title=f"🔥 LIVE {pair} (yFinance 15M Execution Matrix Map)", template="plotly_dark", height=450, xaxis_rangeslider_visible=False, uirevision="keep", margin=dict(l=10, r=10, t=40, b=10))
    st.plotly_chart(fig, use_container_width=True)

    # --- PRIORITY TIMING NOTICE BLOCK ---
    if "STRONG" in result["signal"] or "BUY" in result["signal"] or "SELL" in signal:
        st.info(f"🚨 **TACTICAL TIMING GUIDELINE:** {result['execution_timing']}")

    st.markdown("### 🔍 Alpha Convergence Matrix Analysis")
    max_score = min(int(max(result["buy_score"], result["sell_score"])), 100)
    st.progress(max_score / 100)

    sc1, sc2 = st.columns(2)
    sc1.write(f"🟢 **Institutional Accumulation Load:** `{result['buy_score']}/100`")
    sc2.write(f"🔴 **Institutional Distribution Load:** `{result['sell_score']}/100`")
    
    st.markdown("---")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Structural Vector", result["signal"])
    c2.metric("Matrix Certainty Factor", f"{result['confidence']}%")
    c3.metric("Calculated Vector Range", f"{result['pips']} Pips")
    c4.metric("Active Session Window", result["session"])

    st.markdown("### 🤖 Institutional AI Insight Matrix")
    ai_text_block = run_cached_ai_analysis(result, pair)
    st.markdown(f'<div class="ai-analysis-box">{ai_text_block}</div>', unsafe_allow_html=True)

    with st.expander("Engine Log Buffer (JSON)"):
        st.json(result)

    if "STRONG" in result["signal"] and result["pips"] >= 12.0:
        audio_url = "https://actions.google.com/sounds/v1/alarms/digital_watch_alarm_long.ogg"
        components.html(f'<audio autoplay><source src="{audio_url}" type="audio/ogg"></audio>', height=0)
        st.toast(f"🚨 STRATEGIC ALGO DETECTED SETUP ON {pair}!", icon="💰")

# =====================================================
# HIGH REFLECTION GRID SCANNER FRAGMENT
# =====================================================
@st.fragment(run_every=20)
def render_scanner_block():
    st.subheader("📡 Cross-Asset Matrix Scanner Grid")
    scan_data = run_scanner_yf(tuple(pairs))
    scanner_df = pd.DataFrame(scan_data, columns=["Pair", "Signal Bias", "Confidence Factor", "SMC Architecture Status", "Range Projection", "Current Session Flow"])
    st.dataframe(scanner_df, use_container_width=True, hide_index=True)

# =====================================================
# MAIN ENGINE LAYOUT ASSEMBLY
# =====================================================
st.title("🏦 TECH-STAR INSTITUTIONAL QUANT MATRIX TERMINAL 🚀")
st.markdown("---")

col_layout_left, col_layout_right = st.columns([1.8, 1.2])

with col_layout_left:
    render_live_dashboard(selected_pair)

with col_layout_right:
    render_scanner_block()

st.markdown("---")
current_result = st.session_state.shared_prediction

# =====================================================
# SIGNAL DISPATCH INTERFACE
# =====================================================
st.subheader("📩 High-Priority Signal Broadcast Hub")
confirm_send = st.checkbox("Acknowledge strict compliance with algorithmic validation logic rules.")

if st.button("🚀 EXECUTE NETWORK TELEGRAM BROADCAST"):
    if not confirm_send:
        st.warning("Execution Rejected: Affirm network confirmation verification protocol.")
    elif "NEUTRAL" in current_result["signal"]:
        st.error("Execution Aborted: Algorithmic engine must contain active market matrix parameters to scale broadcast vectors.")
    else:
        message = f"""🏦 <b>TECH-STAR QUALIFIED ALGO SIGNAL</b>

VECTOR PAIR: {selected_pair}
SIGNAL BIAS: <b>{current_result['signal']}</b>
CONFIDENCE COEFFICIENT: {current_result['confidence']}%
SMC STRUCTURE: {current_result['structure']}
<b>EXECUTION TIMING: {current_result['execution_timing']}</b>

ENTRY LIMIT LAYER: {current_result['entry']}
TARGET PROFIT (TP): {current_result['tp']}
STOP LOSS (SL): {current_result['sl']}

📊 EXPECTED RANGE YIELD: <b>{current_result['pips']} Pips</b>
Ceiling Liquidity Line: {current_result['recent_high']}
Floor Liquidity Line: {current_result['recent_low']}

RSI SCALAR: {current_result['rsi']}
TEMPORAL SESSION: {current_result['session']}
SYSTEM TIME STAMP: {current_result['timestamp']}
"""
        ok, err = send_telegram(message)
        if ok:
            st.success("✅ Broadcast system arrays systematically deployed to Telegram channels.")
        else:
            st.error(f"❌ Telegram pipeline distribution exception: {err}")

# =====================================================
# SUPPLEMENTARY QUANTITATIVE ANALYTICS (TRADINGVIEW)
# =====================================================
st.markdown("---")
st.subheader("📊 Supplementary Quantitative Analytics Stream")
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
