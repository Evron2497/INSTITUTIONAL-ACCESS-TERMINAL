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

# High-end Custom CSS injection for dark glassmorphism aesthetic
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;500;600&family=Space+Grotesk:wght@300;400;500;600;700&display=swap');
        
        /* Global Reset and Cyber Dark Background */
        html, body, [data-testid="stAppViewContainer"] {
            background-color: #060913 !important;
            font-family: 'Space Grotesk', sans-serif !important;
            color: #E2E8F0 !important;
        }
        
        /* Header styling */
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

        /* Sidebar Styling */
        [data-testid="stSidebar"] {
            background-color: #090D1A !important;
            border-right: 1px solid #1E293B !important;
        }
        
        /* Glassmorphic Panel Wrapper */
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
        
        .matrix-card.sell {
            border-left: 4px solid #FF4B4B !important;
        }
        .matrix-card.neutral {
            border-left: 4px solid #64748B !important;
        }

        /* Metric Grid Blocks */
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

        /* Custom Buttons */
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
        
        /* Hide default Streamlit block elements decorations */
        div[data-testid="stDecoration"] {
            background-image: linear-gradient(90deg, #00F0FF, #7000FF) !important;
        }
    </style>
""", unsafe_allow_html=True)

# =====================================================
# VOLATILE LOGIN PROTOCOL (FORCED RESET ON REFRESH)
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
        "execution_timing": "AWAITING ENGINE SEED", "eqh_status": "CLEAR", "eql_status": "CLEAR"
    }

def render_login_form():
    st.markdown('<div style="max-width:450px; margin: 80px auto 0 auto;">', unsafe_allow_html=True)
    st.markdown('<h2 class="main-title" style="text-align:center;">CORE MATRIX LOGIN</h2>', unsafe_allow_html=True)
    st.markdown('<p class="sub-title-bar" style="text-align:center; margin-bottom:30px;">Institutional Authentication Required</p>', unsafe_allow_html=True)
    with st.form("auth_form", clear_on_submit=True):
        u = st.text_input("Access Identifier Username")
        p = st.text_input("Secure Passkey Crypt", type="password")
        submit_btn = st.form_submit_button("Initialize Security Session")
        if submit_btn:
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
st.sidebar.subheader("🎛️ Terminal Controls")
selected_pair = st.sidebar.selectbox("Active Liquidity Node Vector", pairs)

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
# ADVANCED SMC ANALYTICS ALGORITHMIC ENGINE
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

def calculate_mtf_levels(pair):
    """Fetches higher timeframe (Daily) structural boundaries for key MTF confluence."""
    yf_symbol = pair_mapping.get(pair, f"{pair}=X")
    try:
        df_daily = yf.Ticker(yf_symbol).history(period="1mo", interval="1d")
        if df_daily.empty or len(df_daily) < 2:
            return {"daily_high": 0, "daily_low": 0}
        prev_day = df_daily.iloc[-2]
        return {"daily_high": float(prev_day["High"]), "daily_low": float(prev_day["Low"])}
    except Exception:
        return {"daily_high": 0, "daily_low": 0}

def detect_equal_high_low(df, threshold_pct=0.0004, bars_lookback=25):
    """Tracks Relative Equal Highs/Lows (EQH/EQL) engineering institutional liquidity targets."""
    df_pivots = calculate_swing_pivots(df, left_bars=3, right_bars=3)
    sh_vals = df_pivots["Swing_High"].dropna().tail(3).values
    sl_vals = df_pivots["Swing_Low"].dropna().tail(3).values
    
    eqh = False
    eql = False
    
    if len(sh_vals) >= 2:
        if abs(sh_vals[-1] - sh_vals[-2]) / sh_vals[-2] < threshold_pct:
            eqh = True
    if len(sl_vals) >= 2:
        if abs(sl_vals[-1] - sl_vals[-2]) / sl_vals[-2] < threshold_pct:
            eql = True
            
    return eqh, eql

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
        "execution_timing": "AWAITING ENGINE PARAMETERS", "eqh_status": "CLEAR", "eql_status": "CLEAR"
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

    # Advanced Multi-Timeframe and Engineered Liquidity Extraction
    mtf_levels = calculate_mtf_levels(pair)
    eqh_detected, eql_detected = detect_equal_high_low(df)

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
        if eql_detected: buy_score += 20  # Structural confluence: retail flat bottoms cleared
        buy_score += amd_buy
        buy_score += div_buy

    if sweep_bsl or mss_bear:
        sell_score += 20 if htf_bias == "BEARISH" else 5
        if mss_bear: sell_score += 35
        if sweep_bsl: sell_score += 25
        if bos_bear: sell_score += 10
        if ob_bear: sell_score += 15
        if fvg_sell: sell_score += 15
        if eqh_detected: sell_score += 20  # Structural confluence: retail flat tops cleared
        sell_score += amd_sell
        sell_score += div_sell

    # High Timeframe Daily Target Intersections
    if mtf_levels["daily_high"] > 0 and price >= mtf_levels["daily_high"] and sweep_bsl:
        sell_score += 25
    if mtf_levels["daily_low"] > 0 and price <= mtf_levels["daily_low"] and sweep_ssl:
        buy_score += 25

    # Premium vs Discount Execution Filter Matrices
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
        if (tp - entry) / pip_multiplier < 5.0: 
            tp = entry + (5.0 * pip_multiplier)
        sl = recent_low - (atr_val * 0.5)
    elif "SELL" in signal:
        tp = recent_low
        if (entry - tp) / pip_multiplier < 5.0: 
            tp = entry - (5.0 * pip_multiplier)
        sl = recent_high + (atr_val * 0.5)

    pips = calculate_pips(entry, tp, pair) if "NEUTRAL" not in signal else 0
    rsi_val = rsi(df)

    struct_str = f"M30: {htf_bias} | Range: {'DISCOUNT' if is_in_discount else 'PREMIUM'} | "
    if mss_bull or mss_bear: struct_str += "MSS CONFIRMED"
    elif sweep_bsl or sweep_ssl: struct_str += "LIQUIDITY RUN DETECTED"
    else: struct_str += "ORDERFLOW EXPANSION"

    current_time_str = datetime.now().strftime("%H:%M:%S")
    if "BUY" in signal:
        execution_timing = f"🎯 EXECUTION NOW ELIGIBLE (Detected at {current_time_str} UTC). Strategy: Enter Limit Orders exclusively at structural Fair Value Gaps or discount Order Blocks. Do not chase market momentum."
    elif "SELL" in signal:
        execution_timing = f"🎯 EXECUTION NOW ELIGIBLE (Detected at {current_time_str} UTC). Strategy: Enter Limit Orders exclusively at premium Fair Value Gaps or premium Order Blocks. Do not chase market momentum."
    else:
        execution_timing = "⏸️ Framework scanning. Matrix requirements unfulfilled."

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
        "execution_timing": execution_timing,
        "eqh_status": "ENG_TARGET_EQH" if eqh_detected else "CLEAR",
        "eql_status": "ENG_TARGET_EQL" if eql_detected else "CLEAR"
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

    # Display Dynamic Header Panel based on Signal
    card_type = "neutral"
    if "BUY" in result["signal"]: card_type = "buy"
    elif "SELL" in result["signal"]: card_type = "sell"
    
    st.markdown(f"""
    <div class="matrix-card {card_type}">
        <span style="font-family:'JetBrains Mono'; font-size:0.8rem; color:#64748B;">[CURRENT NODE VECTOR TARGET]</span>
        <h2 style="margin:5px 0 0 0; font-weight:600; color:#FFFFFF;">{pair} — <span style="color:{'#00F0FF' if card_type=='buy' else ('#FF4B4B' if card_type=='sell' else '#94A3B8')};">{result['signal']}</span></h2>
    </div>
    """, unsafe_allow_html=True)

    # 4-Column Glossy Metric Bar
    m_col1, m_col2, m_col3, m_col4 = st.columns(4)
    with m_col1:
        st.markdown(f'<div class="metric-glow-box"><div class="metric-glow-label">Matrix Certainty</div><div class="metric-glow-val" style="color:#00F0FF;">{result["confidence"]}%</div></div>', unsafe_allow_html=True)
    with m_col2:
        st.markdown(f'<div class="metric-glow-box"><div class="metric-glow-label">Target Projection</div><div class="metric-glow-val">{result["pips"]} Pips</div></div>', unsafe_allow_html=True)
    with m_col3:
        st.markdown(f'<div class="metric-glow-box"><div class="metric-glow-label">Momentum Scalar</div><div class="metric-glow-val">{result["rsi"]} RSI</div></div>', unsafe_allow_html=True)
    with m_col4:
        st.markdown(f'<div class="metric-glow-box"><div class="metric-glow-label">Active Session</div><div class="metric-glow-val" style="font-size:0.95rem; line-height:2.2rem; color:#A855F7;">{result["session"].split(" ")[0]}</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    plot_df = calculate_swing_pivots(market_data, left_bars=5, right_bars=5)
    fig = go.Figure()

    fig.add_trace(go.Candlestick(x=plot_df["time"], open=plot_df["Open"], high=plot_df["High"], low=plot_df["Low"], close=plot_df["Close"], name=pair))
    fig.add_trace(go.Scatter(x=plot_df["time"], y=plot_df["Swing_High"], mode="markers", name="Buy-Side Liquidity (BSL)", marker=dict(color="#FF4B4B", size=7, symbol="triangle-down")))
    fig.add_trace(go.Scatter(x=plot_df["time"], y=plot_df["Swing_Low"], mode="markers", name="Sell-Side Liquidity (SSL)", marker=dict(color="#00F0FF", size=7, symbol="triangle-up")))

    # Structural Range Tools
    if result["recent_high"] > 0:
        fig.add_hline(y=result["recent_high"], line_dash="dash", line_color="rgba(255,75,75,0.4)", annotation_text="BSL Pool")
        fig.add_hline(y=result["recent_low"],  line_dash="dash", line_color="rgba(0,240,255,0.4)", annotation_text="SSL Pool")
        eq = result["recent_low"] + ((result["recent_high"] - result["recent_low"]) * 0.50)
        fig.add_hline(y=eq, line_dash="dot", line_color="rgba(255,255,0,0.4)", annotation_text="Equilibrium (50%)")

    # MTF High Timeframe Mapping Overlay
    mtf_boundaries = calculate_mtf_levels(pair)
    if mtf_boundaries["daily_high"] > 0:
        fig.add_hline(y=mtf_boundaries["daily_high"], line_color="#EF4444", line_dash="solid", annotation_text="PDH Support/Resistance Pool")
        fig.add_hline(y=mtf_boundaries["daily_low"], line_color="#10B981", line_dash="solid", annotation_text="PDL Support/Resistance Pool")

    fig.update_layout(
        template="plotly_dark", 
        height=400, 
        xaxis_rangeslider_visible=False, 
        uirevision="keep", 
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=10, r=10, t=10, b=10)
    )
    st.plotly_chart(fig, use_container_width=True)

    if "STRONG" in result["signal"] or "BUY" in result["signal"] or "SELL" in result["signal"]:
        st.info(f"🚨 **TACTICAL TIMING GUIDELINE:** {result['execution_timing']}")

    # Side-panel telemetry warnings for equal formations
    if result["eqh_status"] == "ENG_TARGET_EQH":
        st.sidebar.warning("⚠️ ENGINE TARGET: EQH RESISTANCE DETECTED (LIQUIDITY POOL)")
    if result["eql_status"] == "ENG_TARGET_EQL":
        st.sidebar.warning("⚠️ ENGINE TARGET: EQL SUPPORT DETECTED (LIQUIDITY POOL)")

    # Quantitative score distribution slider mapping
    st.markdown("#### 🔍 Structural Orderflow Distribution Index")
    max_score = min(int(max(result["buy_score"], result["sell_score"])), 100)
    st.progress(max_score / 100)

    sc1, sc2 = st.columns(2)
    sc1.markdown(f"🟢 Institutional Accumulation Load: <b style='font-family:monospace; color:#10B981;'>{result['buy_score']}/100</b>", unsafe_allow_html=True)
    sc2.markdown(f"🔴 Institutional Distribution Load: <b style='font-family:monospace; color:#EF4444;'>{result['sell_score']}/100</b>", unsafe_allow_html=True)
    
    with st.expander("Engine Log Buffer Frame (JSON Data Validation)"):
        st.json(result)

    if "STRONG" in result["signal"] and result["pips"] >= 5.0:
        audio_url = "https://actions.google.com/sounds/v1/alarms/digital_watch_alarm_long.ogg"
        components.html(f'<audio autoplay><source src="{audio_url}" type="audio/ogg"></audio>', height=0)
        st.toast(f"🚨 SETUP SIGNAL CONFIRMED FOR {pair}!", icon="💰")

# =====================================================
# HIGH REFLECTION GRID SCANNER FRAGMENT
# =====================================================
@st.fragment(run_every=20)
def render_scanner_block():
    st.markdown("""
    <div style="background: rgba(15, 23, 42, 0.4); padding: 12px 15px; border-radius: 8px 8px 0 0; border: 1px solid rgba(255,255,255,0.05); border-bottom: none;">
        <span style="font-family:'JetBrains Mono'; font-size:0.8rem; color:#00F0FF; font-weight:600;">📡 ASSET NETWORK TELEMETRY MATRIX SCANNER</span>
    </div>
    """, unsafe_allow_html=True)
    scan_data = run_scanner_yf(tuple(pairs))
    scanner_df = pd.DataFrame(scan_data, columns=["Asset Pair", "Signal Bias State", "Certainty", "SMC Architecture Flow", "Projection Yield", "Session Flow"])
    st.dataframe(scanner_df, use_container_width=True, hide_index=True)

# =====================================================
# MAIN ENGINE LAYOUT ASSEMBLY
# =====================================================
st.markdown('<h1 class="main-title">CORE MATRIX</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-title-bar">INSTITUTIONAL QUANTITATIVE FOREX TERMINAL // VERSION 4.2.0</p>', unsafe_allow_html=True)

col_layout_left, col_layout_right = st.columns([1.8, 1.2])

with col_layout_left:
    render_live_dashboard(selected_pair)
    
    # Premium styled TradingView Analytical frame
    st.markdown("---")
    st.markdown("### 📊 Live TradingView Stream Platform")
    symbol_tv = f"OANDA:{selected_pair}"
    html_widget = f"""
    <div id="tv_chart_container" style="border: 1px solid rgba(255,255,255,0.05); border-radius: 8px; overflow: hidden;"></div>
    <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
    <script type="text/javascript">
    new TradingView.widget({{
       "width": "100%",
       "height": 500,
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
    components.html(html_widget, height=520)

with col_layout_right:
    render_scanner_block()
    
    # Repositioned Signal Deployment Control Box inside right column for a cleaner workspace flow
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
            elif "NEUTRAL" in current_result["signal"]:
                st.error("Execution Aborted: Algorithmic engine contains zero active market tracking variables.")
            else:
                message = f"""🏦 <b>TECH-STAR QUALIFIED ALGO SIGNAL</b>

VECTOR PAIR: <code>{selected_pair}</code>
SIGNAL BIAS: <b>{current_result['signal']}</b>
CONFIDENCE COEFFICIENT: <code>{current_result['confidence']}%</code>
SMC STRUCTURE FLOW: {current_result['structure']}

🎯 <b>STRUCTURAL EXECUTION BOUNDARIES:</b>
• Matrix Entry Point: {current_result['entry']}
• Take Profit Target: {current_result['tp']}
• Stop Loss Boundary: {current_result['sl']}
• Target Yield Forecast: {current_result['pips']} Pips

🕒 <i>Transmission Frame: {current_result['timestamp']} UTC</i>"""
                
                success, err_msg = send_telegram(message)
                if success:
                    st.toast("Payload broadcast complete across network arrays!", icon="🚀")
                else:
                    st.error(f"Transmission Failed: {err_msg}")
