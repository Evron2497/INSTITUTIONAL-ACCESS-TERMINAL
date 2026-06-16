import os
from datetime import datetime, timezone, timedelta, time as dt_time
import time
import numpy as np
import pandas as pd
import requests
import streamlit as st
import streamlit.components.v1 as components
import plotly.graph_objects as go
import yfinance as yf

# =====================================================
# 1. PREMIUM SCARLET FORGE VISUAL COCKPIT LAYOUT
# =====================================================
st.set_page_config(page_title="ALGOSPHERE QUANT - INTEGRATED TERMINAL", page_icon="🛡️", layout="wide")

st.markdown("""
     <style>
         @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght=300;400;500;600&family=Space+Grotesk:wght=300;400;500;600;700&display=swap');
        
         html, body, [data-testid="stAppViewContainer"] {
             background-color: #080A11 !important;
             font-family: 'Space Grotesk', sans-serif !important;
             color: #E2E8F0 !important;
         }
        
         .main-title {
             font-family: 'Space Grotesk', sans-serif;
             font-weight: 700;
             font-size: 2.2rem;
             background: linear-gradient(135deg, #FF3E3E 0%, #FF8E43 100%);
             -webkit-background-clip: text;
             -webkit-text-fill-color: transparent;
             letter-spacing: -0.03em;
             margin-bottom: 5px;
         }
        
         .sub-title-bar {
             font-family: 'JetBrains Mono', monospace;
             font-size: 0.85rem;
             color: #8A9AAB;
             text-transform: uppercase;
             letter-spacing: 0.1em;
             margin-bottom: 25px;
         }

         [data-testid="stSidebar"] {
             background-color: #0D111C !important;
             border-right: 1px solid #1E293B !important;
         }
        
         .matrix-card {
             background: rgba(15, 23, 42, 0.65) !important;
             border: 1px solid rgba(255, 255, 255, 0.05) !important;
             border-radius: 12px !important;
             padding: 20px !important;
             box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37) !important;
             backdrop-filter: blur(8px) !important;
             margin-bottom: 15px;
         }
        
         .matrix-card.safescalper {
             border-left: 4px solid #FF3E3E !important;
             background: linear-gradient(135deg, rgba(15, 23, 42, 0.8) 0%, rgba(255, 62, 62, 0.12) 100%) !important;
             box-shadow: 0px 0px 25px rgba(255, 62, 62, 0.2) !important;
         }
         .matrix-card.suleiman {
             border-left: 4px solid #3B82F6 !important;
             background: linear-gradient(135deg, rgba(15, 23, 42, 0.8) 0%, rgba(59, 130, 246, 0.12) 100%) !important;
             box-shadow: 0px 0px 25px rgba(59, 130, 246, 0.2) !important;
         }
         .matrix-card.bridzik {
             border-left: 4px solid #F59E0B !important;
             background: linear-gradient(135deg, rgba(15, 23, 42, 0.8) 0%, rgba(245, 158, 11, 0.12) 100%) !important;
             box-shadow: 0px 0px 25px rgba(245, 158, 11, 0.2) !important;
         }

         .metric-glow-box {
             background: rgba(21, 28, 46, 0.5);
             border: 1px solid rgba(255, 255, 255, 0.04);
             border-radius: 10px;
             padding: 15px;
             text-align: center;
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
             font-size: 1.3rem;
             font-weight: 600;
             color: #FFFFFF;
         }

         .stButton>button {
             background: linear-gradient(135deg, #111827 0%, #271111 100%) !important;
             color: #FF3E3E !important;
             border: 1px solid rgba(255, 62, 62, 0.3) !important;
             border-radius: 8px !important;
             padding: 10px 24px !important;
             font-family: 'Space Grotesk', sans-serif !important;
             font-weight: 600 !important;
             transition: all 0.3s ease !important;
             width: 100% !important;
         }
         .stButton>button:hover {
             border-color: #FF3E3E !important;
             box-shadow: 0px 0px 20px rgba(255, 62, 62, 0.35) !important;
             color: #FFFFFF !important;
         }
     </style>
 """, unsafe_allow_html=True)

# =====================================================
# 2. REFRESH GUARDIAN & SECURITY AUTHENTICATION
# =====================================================
USERNAME = st.secrets.get("USERNAME", "admin")
PASSWORD = st.secrets.get("PASSWORD", "quant_forge_2026")

if "logged_in" not in st.session_state:
    if "session_node" in st.query_params and st.query_params["session_node"] == "active":
        st.session_state.logged_in = True
    else:
        st.session_state.logged_in = False

if "shared_prediction" not in st.session_state:
     st.session_state.shared_prediction = {
         "signal": "NEUTRAL", "confidence": 0.0, "entry": 0.0, "tp": "0.0", "sl": 0.0, "pips": 0.0, "rsi": 50.0,
         "structure": "INITIALIZING", "session": "UNKNOWN", "timestamp": "",
         "recent_high": 0.0, "recent_low": 0.0, "is_scalping": False, "scalping_state": "STANDBY",
         "conditions_passed": 0, "direction": "NEUTRAL", "checks": [], "protection_status": "PASSING",
         "calculated_lot": 0.1, "sl_pips": 0, "smc_market_bias": "NEUTRAL", "last_structure_type": "NONE",
         "pd_zone": "EQUILIBRIUM", "candle_time_remaining": "00:00", "suleiman_res": 0.0, "suleiman_sup": 0.0,
         "bridzik_subpositions": 1, "bridzik_exit_state": "STANDBY"
     }

def render_login_form():
     st.markdown('<div style="max-width:450px; margin: 80px auto 0 auto;">', unsafe_allow_html=True)
     st.markdown('<h2 class="main-title" style="text-align:center;">ALGOSPHERE AUTH</h2>', unsafe_allow_html=True)
     st.markdown('<p class="sub-title-bar" style="text-align:center; margin-bottom:30px;">Quant Ecosystem Identity Validation</p>', unsafe_allow_html=True)
     with st.form("auth_form"):
         u = st.text_input("Access Identifier")
         p = st.text_input("Secure Passkey", type="password")
         if st.form_submit_button("Initialize Security Session"):
             if u == USERNAME and p == PASSWORD:
                 st.session_state.logged_in = True
                 st.query_params["session_node"] = "active"
                 st.rerun()
             else:
                 st.error("Invalid node verification parameter sequence.")
     st.markdown('</div>', unsafe_allow_html=True)

if not st.session_state.logged_in:
     render_login_form()
     st.stop()

if st.sidebar.button("🔒 Disconnect Terminal Node"):
     st.session_state.logged_in = False
     st.query_params.clear()
     st.rerun()

st.sidebar.markdown('<div style="padding: 2px 10px; background: rgba(239,68,68,0.1); border: 1px solid #FF3E3E; border-radius:6px; color:#FF3E3E; font-size:0.8rem; font-family:\'JetBrains Mono\'; text-align:center;">● INTEGRITY NODE CONNECTED</div>', unsafe_allow_html=True)
st.sidebar.markdown("---")

# =====================================================
# 3. TELEGRAM DATA BROADCAST DISPATCHER
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
# 4. CONFIGURATION CONTROLS & SIDEBAR ENGINES
# =====================================================
st.sidebar.subheader("⚙️ AlgoSphere EA Engine Mod")
engine_mode = st.sidebar.radio("Active Engine Core", ["SafeScalperPro (Free Base)", "SMC & Suleiman Analytics", "XAUUSD 5 Minute (v7.2 Bridzik)"])

selected_tf = st.sidebar.selectbox("Signal Timeframe Window", ["M5", "M15", "H1"], index=0)
selected_symbol = st.sidebar.selectbox("Instrument Allocation Vector", ["XAUUSD", "XAGUSD", "EURUSD", "GBPUSD"], index=0)

# Time Candle Suleiman Customization Inputs
st.sidebar.markdown("**⏰ Time Candle Suleiman Customization**")
timer_display_enabled = st.sidebar.checkbox("Display Candle Timer HUD", value=True)
timer_color = st.sidebar.color_picker("Timer Font Color Specifier", value="#3B82F6")
timer_font_size = st.sidebar.slider("Timer Font Point Scale", 10, 24, 14)
timer_position = st.sidebar.selectbox("HUD Chart Node Offset Position", ["Above Current Price", "Below Current Price"], index=0)

# SafeScalperPro 7-Condition EA Subsystem Constraints
st.sidebar.markdown("**🧬 SafeScalperPro Parametric Presets**")
fast_ema_period = st.sidebar.number_input("Fast Trend Horizon (EMA Fast)", value=150)
slow_ema_period = st.sidebar.number_input("Slow Trend Horizon (EMA Slow)", value=510)
n_bar_breakout = st.sidebar.slider("Breakout Reference Window (N Bars)", 5, 50, 20)
atr_buffer_mult = st.sidebar.slider("ATR Breakout Boundary Extension", 0.1, 2.5, 0.5, step=0.1)

# Bridzik v7.2 Explicit Sizing Engine Restrictions 
st.sidebar.markdown("**🛡️ Bridzik Protection Constraints**")
bridzik_risk_mode = st.sidebar.checkbox("Enable Automated Conviction Risk Scale-In", value=True)
bridzik_safety_sl = st.sidebar.number_input("Hard Emergency Safety SL (Pips)", value=250)

# Sizing Core Architecture
st.sidebar.markdown("**📐 Risk Allocation Matrix**")
risk_variant = st.sidebar.selectbox("Sizing Core Logic", ["Percent of Balance", "Fixed Lot Sizing"])
risk_weight_pct = st.sidebar.slider("Configured Risk Weight (% per Trade)", 0.1, 5.0, 2.0, step=0.1)
fixed_lot_fallback = st.sidebar.number_input("Manual Fixed Contract Lot Fallback", value=0.1, step=0.01)

# Operational Session Limits (SafeScalper Mode)
st.sidebar.markdown("**📅 Execution Time Windows**")
start_trading_hour = st.sidebar.slider("System Awake Hour (UTC)", 0, 23, 8)
end_trading_hour = st.sidebar.slider("System Cutoff Hour (UTC)", 0, 23, 20)
friday_cutoff = st.sidebar.checkbox("Enforce Friday Afternoon Liquidation", value=True)
news_protection = st.sidebar.checkbox("Midnight Rollover News Filtering Protection", value=True)

account_equity = st.sidebar.number_input("Mock Valuation Account Equity ($)", min_value=1000, value=10000)

# =====================================================
# 5. DATA PIPELINE (M5 TO M15 AUTO-CORRECTION LOGIC)
# =====================================================
SYMBOL_MAP = {"XAUUSD": "GC=F", "XAGUSD": "SI=F", "EURUSD": "EURUSD=X", "GBPUSD": "GBPUSD=X"}

@st.cache_data(ttl=2)
def fetch_live_market_dataframe(symbol, tf_str):
     if engine_mode == "XAUUSD 5 Minute (v7.2 Bridzik)" and tf_str == "M5":
          runtime_tf = "M15"
     else:
          runtime_tf = tf_str
          
     interval_dict = {"M5": "5m", "M15": "15m", "H1": "60m"}
     yf_interval = interval_dict.get(runtime_tf, "15m")
     ticker_str = SYMBOL_MAP.get(symbol, "GC=F")
     try:
          df = yf.Ticker(ticker_str).history(period="5d", interval=yf_interval)
          if df.empty: return pd.DataFrame()
          df = df.reset_index()
          df.rename(columns={"Datetime": "time", "Date": "time", "Open": "Open", "High": "High", "Low": "Low", "Close": "Close", "Volume": "Volume"}, inplace=True)
          return df
     except Exception:
          return pd.DataFrame()

# =====================================================
# 6. SULEIMAN REAL-TIME COUNTDOWN LOOP ENGINE
# =====================================================
def get_suleiman_candle_countdown(tf_str):
    now = datetime.now(timezone.utc)
    resolved_tf = "M15" if (engine_mode == "XAUUSD 5 Minute (v7.2 Bridzik)" and tf_str == "M5") else tf_str
    interval_minutes = {"M5": 5, "M15": 15, "H1": 60}.get(resolved_tf, 5)
    
    elapsed_minutes = (now.minute % interval_minutes)
    elapsed_seconds = (elapsed_minutes * 60) + now.second
    remaining_seconds = (interval_minutes * 60) - elapsed_seconds
    mins, secs = divmod(remaining_seconds, 60)
    return f"{int(mins):02d}:{int(secs):02d}"

# =====================================================
# 7. MATHEMATICAL MATRIX TECHNICAL ENVELOPES
# =====================================================
def compute_atr_series(df, window=14):
     if len(df) < window: return pd.Series(0.50, index=df.index)
     tr = np.maximum(df["High"] - df["Low"], np.maximum(abs(df["High"] - df["Close"].shift()), abs(df["Low"] - df["Close"].shift())))
     return tr.rolling(window).mean().fillna(0.50)

def compute_rsi_series(df, period=14):
     if len(df) < period: return pd.Series(50.0, index=df.index)
     delta = df["Close"].diff()
     gain = delta.clip(lower=0).rolling(period).mean()
     loss = (-delta.clip(upper=0)).rolling(period).mean()
     rs = gain / loss.replace(0, 1e-5)
     return (100 - (100 / (1 + rs))).fillna(50.0)

# =====================================================
# 8. SUBSYSTEM ENGINE CORES
# =====================================================

# --- ENGINE A: SAFESCALPERPRO 7-GATE MATRIX ---
def process_safescalperpro_logic(df):
    if len(df) < max(slow_ema_period, 100):
        return {"is_scalping": False, "state": "GUARD: INSUFFICIENT DATA", "passed": 0, "direction": "NEUTRAL", "checks": []}
    
    close, prev_close = float(df["Close"].iloc[-1]), float(df["Close"].iloc[-2])
    df["EMA_Fast"] = df["Close"].ewm(span=fast_ema_period, adjust=False).mean()
    df["EMA_Slow"] = df["Close"].ewm(span=slow_ema_period, adjust=False).mean()
    df["ATR"] = compute_atr_series(df, 14)
    df["RSI"] = compute_rsi_series(df, 14)
    
    ema_fast_val, ema_slow_val = float(df["EMA_Fast"].iloc[-1]), float(df["EMA_Slow"].iloc[-1])
    atr_val, rsi_val = float(df["ATR"].iloc[-1]), float(df["RSI"].iloc[-1])
    
    lookback_slice = df.iloc[-(n_bar_breakout + 1): -1]
    n_bar_high, n_bar_low = float(lookback_slice["High"].max()), float(lookback_slice["Low"].min())
    
    now_utc = datetime.now(timezone.utc)
    current_utc_hour = now_utc.hour
    
    session_pass = start_trading_hour <= current_utc_hour < end_trading_hour
    if friday_cutoff and now_utc.weekday() == 4 and current_utc_hour >= 16: session_pass = False
    if news_protection and current_utc_hour in [23, 0, 1]: session_pass = False
        
    c1_buy, c1_sell = ema_fast_val > ema_slow_val, ema_fast_val < ema_slow_val
    c2_buy = (ema_fast_val - ema_slow_val) > (atr_val * 0.2)
    c2_sell = (ema_slow_val - ema_fast_val) > (atr_val * 0.2)
    c3_buy = close > ema_fast_val and close > ema_slow_val
    c3_sell = close < ema_fast_val and close < ema_slow_val
    c4_buy = close > (n_bar_high + (atr_val * atr_buffer_mult))
    c4_sell = close < (n_bar_low - (atr_val * atr_buffer_mult))
    c5_buy, c5_sell = 40.0 <= rsi_val <= 65.0, 35.0 <= rsi_val <= 60.0
    c6_buy, c6_sell = close > prev_close, close < prev_close
    c7_pass = session_pass
    
    labels = [
        "1. EMA Trend Structure Direction Mapping", "2. Trend Strength Multiplier Gate Threshold",
        "3. Price Space Relative Position Alignment", "4. N-Bar Structural Breakout ATR Envelope",
        "5. RSI Momentum Band Optimization Filter", "6. Micro Candle Momentum Shift Confirmation",
        "7. Time Window Filter / Midnight Protection"
    ]
    
    cond_buy = [c1_buy, c2_buy, c3_buy, c4_buy, c5_buy, c6_buy, c7_pass]
    cond_sell = [c1_sell, c2_sell, c3_sell, c4_sell, c5_sell, c6_sell, c7_pass]
    
    passed_buy, passed_sell = sum(1 for c in cond_buy if c), sum(1 for c in cond_sell if c)
    
    if passed_buy >= passed_sell:
        active_direction, max_passed = "BUY", passed_buy
        checks_status = [{"label": labels[i], "passed": cond_buy[i]} for i in range(7)]
    else:
        active_direction, max_passed = "SELL", passed_sell
        checks_status = [{"label": labels[i], "passed": cond_sell[i]} for i in range(7)]
        
    is_fully_synchronized = (max_passed == 7)
    state_str = f"🚀 EXECUTION ACTIVE [{active_direction}]" if is_fully_synchronized else f"⚖️ TRACKING ({max_passed}/7 SYNCED)"
    
    return {
        "is_scalping": is_fully_synchronized, "state": state_str, "passed": max_passed,
        "direction": active_direction, "checks": checks_status, "atr": atr_val, "rsi": rsi_val,
        "fast_ema": ema_fast_val, "slow_ema": ema_slow_val
    }

# --- ENGINE B: SMC & SULEIMAN INSTITUTIONAL ANALYTICS & FLOW ---
def process_suleiman_analytics_engine(df):
    if len(df) < 30: return {"bias": "NEUTRAL", "structure": "RANGE-LOCK", "pd_zone": "EQUILIBRIUM", "suleiman_sup": 0.0, "suleiman_res": 0.0}
    
    h_bound, l_bound = float(df["High"].tail(30).max()), float(df["Low"].tail(30).min())
    mid, close = (h_bound + l_bound) / 2.0, float(df["Close"].iloc[-1])
    
    volume_surge = df["Volume"].iloc[-1] > (df["Volume"].tail(15).mean() * 1.8)
    money_flow = "INSTITUTIONAL BANK INJECTION" if volume_surge else "STANDARD RETAIL TURNOVER"
    pd_zone = "SULEIMAN PREMIUM" if close > mid else "SULEIMAN DISCOUNT"
    bias = "BULLISH" if close > df["Close"].ewm(span=50).mean().iloc[-1] else "BEARISH"
    
    return {
        "bias": bias, "structure": money_flow, "pd_zone": pd_zone, 
        "high": h_bound, "low": l_bound, "suleiman_res": h_bound - 0.2, "suleiman_sup": l_bound + 0.2
    }

# --- ENGINE C: BRIDZIK v7.2 MEAN REVERSION BLOCK ---
def process_bridzik_v72_matrix(df):
    if len(df) < 30: return {"is_triggered": False, "bias": "NEUTRAL", "subpositions": 1, "exit_state": "STANDBY"}
    
    close = float(df["Close"].iloc[-1])
    df["EMA_Basis"] = df["Close"].ewm(span=20, adjust=False).mean()
    df["StdDev"] = df["Close"].rolling(window=20).std()
    
    basis, std = df["EMA_Basis"].iloc[-1], df["StdDev"].iloc[-1] if df["StdDev"].iloc[-1] > 0 else 0.5
    deviation = (close - basis) / std
    is_sideways = df["Close"].tail(10).max() - df["Close"].tail(10).min() < (std * 1.5)
    
    subpositions = 1
    if deviation < -1.8:
        bias, is_triggered = "BUY", True
        if abs(deviation) > 2.4 and not is_sideways: subpositions = 5
    elif deviation > 1.8:
        bias, is_triggered = "SELL", True
        if abs(deviation) > 2.1: subpositions = 5
    else:
        bias, is_triggered = "NEUTRAL", False
        
    exit_state = "RUNNING"
    if is_triggered:
        if bias == "BUY" and close >= basis: exit_state = "CLOSE: MEAN REACHED"
        elif bias == "SELL" and close <= basis: exit_state = "CLOSE: MEAN REACHED"
        
    return {"is_triggered": is_triggered, "bias": bias, "subpositions": subpositions, "exit_state": exit_state, "deviation": round(deviation, 2), "basis": basis}

# =====================================================
# 9. CENTRAL PROCESSING & POSITION ARCHITECTURE
# =====================================================
def run_integrated_quant_pipeline(df):
     if df is None or df.empty or len(df) < 10: return st.session_state.shared_prediction

     pip_scale = 0.10 if selected_symbol in ["XAUUSD", "XAGUSD"] else 0.0001
     price = float(df["Close"].iloc[-1])
     
     ea_matrix = process_safescalperpro_logic(df)
     suleiman_matrix = process_suleiman_analytics_engine(df)
     countdown_timer = get_suleiman_candle_countdown(selected_tf)
     
     if engine_mode == "XAUUSD 5 Minute (v7.2 Bridzik)":
          brk = process_bridzik_v72_matrix(df)
          sl_distance = bridzik_safety_sl * pip_scale
          sl = price - sl_distance if brk["bias"] == "BUY" else price + sl_distance
          
          calculated_lot = account_equity * (risk_weight_pct / 100.0) / bridzik_safety_sl if risk_variant == "Percent of Balance" else fixed_lot_fallback
          if bridzik_risk_mode and brk["subpositions"] > 1: calculated_lot *= brk["subpositions"]
              
          return {
              "signal": f"BRIDZIK {brk['bias']}", "confidence": 90.0 if brk["is_triggered"] else 0.0,
              "entry": round(price, 2), "tp": "NONE (DYNAMIC EXITS)", "sl": round(sl, 2), "pips": 0.0,
              "rsi": 50.0, "structure": f"DEVIATION: {brk['deviation']} SD", "session": "V7.2 LIVE MATRIX",
              "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "is_scalping": brk["is_triggered"],
              "scalping_state": brk["exit_state"], "conditions_passed": brk["subpositions"], "direction": brk["bias"],
              "checks": [], "protection_status": "ACTIVE", "calculated_lot": max(0.01, round(calculated_lot, 2)), "sl_pips": bridzik_safety_sl,
              "smc_market_bias": brk["bias"], "last_structure_type": "MEAN REVERSION", "pd_zone": "REVERSION MATRIX",
              "candle_time_remaining": countdown_timer, "bridzik_subpositions": brk["subpositions"], "bridzik_exit_state": brk["exit_state"],
              "suleiman_res": suleiman_matrix["suleiman_res"], "suleiman_sup": suleiman_matrix["suleiman_sup"]
          }
          
     elif engine_mode == "SMC & Suleiman Analytics":
          atr_val = ea_matrix.get("atr", 0.50)
          sl = price - (atr_val * 2.0) if suleiman_matrix["bias"] == "BULLISH" else price + (atr_val * 2.0)
          tp = price + (atr_val * 4.0) if suleiman_matrix["bias"] == "BULLISH" else price - (atr_val * 4.0)
          return {
              "signal": f"SULEIMAN {suleiman_matrix['bias']}", "confidence": 88.0, "entry": round(price, 2),
              "tp": round(tp, 2), "sl": round(sl, 2), "pips": round(abs(tp-price)/pip_scale, 1), "rsi": round(ea_matrix["rsi"], 1),
              "structure": "SULEIMAN LEVEL MATRIX", "session": suleiman_matrix["structure"], "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
              "is_scalping": True, "scalping_state": "ANALYSIS ACTIVE", "conditions_passed": 7, "direction": "BUY" if suleiman_matrix["bias"] == "BULLISH" else "SELL",
              "checks": [], "protection_status": "PASSING", "calculated_lot": fixed_lot_fallback, "sl_pips": 20, "smc_market_bias": suleiman_matrix["bias"],
              "last_structure_type": suleiman_matrix["structure"], "pd_zone": suleiman_matrix["pd_zone"], "candle_time_remaining": countdown_timer,
              "suleiman_res": suleiman_matrix["suleiman_res"], "suleiman_sup": suleiman_matrix["suleiman_sup"], "bridzik_subpositions": 1, "bridzik_exit_state": "STANDBY"
          }
     else:
          atr_val = ea_matrix.get("atr", 0.50)
          sl_distance = max((atr_val * 1.5), 0.8)
          tp, sl = (price + (sl_distance * 2.0), price - sl_distance) if ea_matrix["direction"] == "BUY" else (price - (sl_distance * 2.0), price + sl_distance)
          sl_pips_calc = round(sl_distance / pip_scale, 1)
          calculated_lot = (account_equity * (risk_weight_pct / 100.0) / (sl_pips_calc * (10.0 if selected_symbol in ["XAUUSD", "XAGUSD"] else 1.0))) if risk_variant == "Percent of Balance" else fixed_lot_fallback
          
          return {
              "signal": f"PRO ACTIVE {ea_matrix['direction']}" if ea_matrix["is_scalping"] else "NEUTRAL", "confidence": round((ea_matrix["passed"] / 7) * 100, 1),
              "entry": round(price, 2), "tp": round(tp, 2), "sl": round(sl, 2), "pips": round(abs(tp-price)/pip_scale, 1), "rsi": round(ea_matrix["rsi"], 1),
              "structure": ea_matrix["state"], "session": "RETAIL LIQUIDITY FLOW", "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
              "is_scalping": ea_matrix["is_scalping"], "scalping_state": ea_matrix["state"], "conditions_passed": ea_matrix["passed"], "direction": ea_matrix["direction"],
              "checks": ea_matrix["checks"], "protection_status": "PASSING", "calculated_lot": max(0.01, round(calculated_lot, 2)), "sl_pips": sl_pips_calc,
              "smc_market_bias": "NEUTRAL", "last_structure_type": "RETAIL FLOW", "pd_zone": "EQUILIBRIUM", "candle_time_remaining": countdown_timer,
              "suleiman_res": suleiman_matrix["suleiman_res"], "suleiman_sup": suleiman_matrix["suleiman_sup"], "bridzik_subpositions": 1, "bridzik_exit_state": "STANDBY"
          }

# =====================================================
# 10. DYNAMIC FRAGMENT DISPLAY LAYERS
# =====================================================
@st.fragment(run_every=1)
def render_live_dashboard_layer(tf):
     market_df = fetch_live_market_dataframe(selected_symbol, tf)
     if market_df.empty or len(market_df) < 30:
          st.warning("Constructing Scarlet Forge buffer channels... Listening for tick feeds.")
          return

     res = run_integrated_quant_pipeline(market_df)
     st.session_state.shared_prediction = res

     card_class = "neutral"
     if engine_mode == "XAUUSD 5 Minute (v7.2 Bridzik)": card_class = "bridzik"
     elif engine_mode == "SMC & Suleiman Analytics": card_class = "suleiman"
     elif res["is_scalping"]: card_class = "safescalper"
    
     if engine_mode == "XAUUSD 5 Minute (v7.2 Bridzik)" and tf == "M5":
          st.toast("⚠️ v7.2 Protocol Constraint: M5 routing redirected to optimized M15 frame architecture.", icon="ℹ️")

     st.markdown(f"""
     <div class="matrix-card {card_class}">
         <span style="font-family:'JetBrains Mono'; font-size:0.75rem; color:#8A9AAB;">[MASTER QUANT CONSOLE ENGINE - LIVE TRADING NODE]</span>
         <h2 style="margin:4px 0 0 0; font-weight:600; color:#FFFFFF;">{selected_symbol} ({tf}) — <span style="color:#FF3E3E;">{res['signal']}</span></h2>
     </div>
     """, unsafe_allow_html=True)

     m1, m2, m3, m4 = st.columns(4)
     with m1: st.markdown(f'<div class="metric-glow-box"><div class="metric-glow-label">Suleiman Clock HUD</div><div class="metric-glow-val" style="color:{str(timer_color)}; font-size:{int(timer_font_size)+2}px;">⏳ {res["candle_time_remaining"]}</div></div>', unsafe_allow_html=True)
     with m2: st.markdown(f'<div class="metric-glow-box"><div class="metric-glow-label">Conviction / Positions</div><div class="metric-glow-val">{res["bridzik_subpositions"] if engine_mode == "XAUUSD 5 Minute (v7.2 Bridzik)" else res["conditions_passed"]} Units</div></div>', unsafe_allow_html=True)
     with m3: st.markdown(f'<div class="metric-glow-box"><div class="metric-glow-label">Allocated Contract Lot</div><div class="metric-glow-val" style="color:#10B981;">{res["calculated_lot"]} Lots</div></div>', unsafe_allow_html=True)
     with m4: st.markdown(f'<div class="metric-glow-box"><div class="metric-glow-label">Engine Tracking Mode</div><div class="metric-glow-val" style="font-size:0.85rem; color:#3B82F6;">{res["scalping_state"]}</div></div>', unsafe_allow_html=True)

     if engine_mode == "SafeScalperPro (Free Base)":
          st.markdown("<br>", unsafe_allow_html=True)
          st.markdown("### 🧬 Strategy Gates Synchronicity Status")
          chk_cols = st.columns(len(res["checks"]) if res["checks"] else 1)
          for index, check in enumerate(res["checks"]):
              with chk_cols[index]:
                  pill_box = "🟢 PASS" if check["passed"] else "🔴 BLOCK"
                  st.markdown(f"**Gate {index+1}**\n\n`{pill_box}`\n\n<p style='font-size:0.72rem; color:#94A3B8;'>{check['label']}</p>", unsafe_allow_html=True)

     # Canvas Mapping
     fig = go.Figure()
     fig.add_trace(go.Candlestick(x=market_df["time"], open=market_df["Open"], high=market_df["High"], low=market_df["Low"], close=market_df["Close"], name="Spot Price"))
    
     # Base Plotly Layout Setup
     fig.update_layout(
         template="plotly_dark", 
         height=380, 
         xaxis_rangeslider_visible=False, 
         uirevision="keep", 
         paper_bgcolor='rgba(0,0,0,0)', 
         plot_bgcolor='rgba(0,0,0,0)', 
         margin=dict(l=10, r=10, t=10, b=10)
     )

     # High-Performance Suleiman HUD Text Injector via Layout Annotations (Fixes go.Scatter property exceptions)
     if timer_display_enabled:
          try:
              text_y_position = float(res["entry"]) + 0.5 if timer_position == "Above Current Price" else float(res["entry"]) - 0.5
              fig.add_annotation(
                  x=market_df["time"].iloc[-1],
                  y=text_y_position,
                  text=f"⏱️ {res['candle_time_remaining']}",
                  showarrow=False,
                  xanchor="right",
                  yanchor="top",
                  font=dict(
                      color=str(timer_color),
                      size=int(timer_font_size),
                      family="JetBrains Mono"
                  )
              )
          except Exception as e:
              st.toast(f"HUD Clock Sync Lag: {str(e)}", icon="⚠️")

     # Plot Exclusive Overlays
     if engine_mode == "SMC & Suleiman Analytics":
          fig.add_shape(type="line", x0=market_df["time"].iloc[-30], y0=res["suleiman_res"], x1=market_df["time"].iloc[-1], y1=res["suleiman_res"], line=dict(color="rgba(239, 68, 68, 0.7)", width=1.5, dash="dash"))
          fig.add_shape(type="line", x0=market_df["time"].iloc[-30], y0=res["suleiman_sup"], x1=market_df["time"].iloc[-1], y1=res["suleiman_sup"], line=dict(color="rgba(16, 185, 129, 0.7)", width=1.5, dash="dash"))

     st.plotly_chart(fig, use_container_width=True)

# =====================================================
# 11. LAYOUT GRID MATRIX COMPOSER ASSEMBLY
# =====================================================
st.markdown('<h1 class="main-title">ALGOSPHERE QUANT // COMPLEX CORE</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-title-bar">DYNAMIC EXECUTION INTELLIGENCE HUD PANEL</p>', unsafe_allow_html=True)

layout_col_left, layout_col_right = st.columns([2.0, 1.0])

with layout_col_left:
     render_live_dashboard_layer(selected_tf)
     st.markdown("---")
     st.markdown("### 📊 TradingView Global Node Synchronized Stream")
     
     tv_ticker = f"FX_IDC:{selected_symbol}" if "USD" in selected_symbol else selected_symbol
     html_widget = f"""
     <div id="tv_chart_container" style="border: 1px solid rgba(255,255,255,0.05); border-radius: 8px; overflow: hidden;"></div>
     <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
     <script type="text/javascript">
     new TradingView.widget({{
        "width": "100%",
        "height": 420,
        "symbol": "{tv_ticker}",
        "interval": "15",
        "timezone": "Etc/UTC",
        "theme": "dark",
        "style": "1",
        "locale": "en",
        "toolbar_bg": "#0A0E17",
        "enable_publishing": false,
        "hide_side_toolbar": false,
        "allow_symbol_change": false,
        "container_id": "tv_chart_container"
     }});
     </script>
     """
     components.html(html_widget, height=440)

with layout_col_right:
     st.markdown("""
     <div style="background: rgba(25, 15, 15, 0.4); padding: 12px 15px; border-radius: 8px 8px 0 0; border: 1px solid rgba(255,62,62,0.1); border-bottom: none;">
         <span style="font-family:'JetBrains Mono'; font-size:0.8rem; color:#FF3E3E; font-weight:600;">📩 TELEMETRY PACKET OUTBOUND SERVER</span>
     </div>
     """, unsafe_allow_html=True)
    
     with st.container(border=True):
          shared_res = st.session_state.shared_prediction
          verify_payload_rules = st.checkbox("Confirm telemetry data packet structural rules verification.")
        
          if st.button("🚀 TRANSMIT TELEMETRY PIPELINE OVERLAY"):
               if not verify_payload_rules:
                    st.warning("Transmission Aborted: Accept structural communication protocol validations.")
               else:
                    payload_text = f"""🛡️ <b>ALGOSPHERE INTEGRATED CLUSTER ENGINE DISPATCH</b>

ACTIVE MODULE: <code>{engine_mode.upper()}</code>
INSTRUMENT SPECIFIER: <b>{selected_symbol}</b> [{selected_tf}]
CANDLE CLOCK TIMER REMAINING: <code>{shared_res['candle_time_remaining']}</code>
STRUCTURAL CLASSIFICATION: <code>{shared_res['session']}</code>

🎯 <b>EXPERT POSITION MATRIX DATA:</b>
• Core Intent State: <b>{shared_res['signal']}</b>
• Target Node Entry Point: <code>{shared_res['entry']}</code>
• Risk Invalidation Boundary (SL): <code>{shared_res['sl']}</code>
• Mitigation Matrix Profit Limit (TP): <code>{shared_res['tp']}</code>
• Computed Scale Allocation: <code>{shared_res['calculated_lot']} Lots</code>
"""
                    success, err_msg = send_telegram(payload_text)
                    if success:
                         st.success("Telemetry payload transmission successful.")
                    else:
                         st.error(f"Transmission Pipeline Fault: {err_msg}")
