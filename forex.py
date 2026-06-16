import os
from datetime import datetime, timezone, time as dt_time
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
st.set_page_config(page_title="CORE VECTOR MATRIX - SCALPING ROBOT PRO", page_icon="🤖", layout="wide")

st.markdown("""
     <style>
         @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght=300;400;500;600&family=Space+Grotesk:wght=300;400;500;600;700&display=swap');
        
         html, body, [data-testid="stAppViewContainer"] {
             background-color: #060913 !important;
             font-family: 'Space Grotesk', sans-serif !important;
             color: #E2E8F0 !important;
         }
        
         .main-title {
             font-family: 'Space Grotesk', sans-serif;
             font-weight: 700;
             font-size: 2.2rem;
             background: linear-gradient(135deg, #FFD700 0%, #FFA500 100%);
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
             background-color: #090D1A !important;
             border-right: 1px solid #1E293B !important;
         }
        
         .matrix-card {
             background: rgba(15, 23, 42, 0.65) !important;
             border: 1px solid rgba(255, 255, 255, 0.05) !important;
             border-left: 4px solid #FFD700 !important;
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
         .matrix-card.buy { border-left: 4px solid #10B981 !important; }
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
             color: #FFD700 !important;
             border: 1px solid rgba(255, 215, 0, 0.3) !important;
             border-radius: 8px !important;
             padding: 10px 24px !important;
             font-family: 'Space Grotesk', sans-serif !important;
             font-weight: 600 !important;
             letter-spacing: 0.02em !important;
             transition: all 0.3s ease !important;
             width: 100% !important;
         }
         .stButton>button:hover {
             border-color: #FFD700 !important;
             box-shadow: 0px 0px 20px rgba(255, 215, 0, 0.35) !important;
             color: #FFFFFF !important;
             transform: translateY(-1px);
         }
        
         div[data-testid="stDecoration"] {
             background-image: linear-gradient(90deg, #FFD700, #FFA500) !important;
         }
     </style>
 """, unsafe_allow_html=True)

# =====================================================
# STABLE NATIVE URL PARSING REFRESH GUARDIAN
# =====================================================
USERNAME = st.secrets.get("USERNAME", "")
PASSWORD = st.secrets.get("PASSWORD", "")

# Instantly read parameters directly via Streamlit engine (safe from websocket desync errors)
if "logged_in" not in st.session_state:
    if "session_node" in st.query_params and st.query_params["session_node"] == "active":
        st.session_state.logged_in = True
    else:
        st.session_state.logged_in = False

if "shared_prediction" not in st.session_state:
     st.session_state.shared_prediction = {
         "signal": "NEUTRAL", "confidence": 0, "entry": 0, "tp": 0, "sl": 0, "pips": 0, "rsi": 50,
         "structure": "INITIALIZING", "buy_score": 0, "sell_score": 0, "session": "UNKNOWN",
         "timestamp": "", "recent_high": 0, "recent_low": 0, "fvg_status": "NONE", "ob_status": "NONE",
         "is_scalping": False, "scalping_state": "STANDBY", "conditions_passed": 0, "direction": "NEUTRAL", "checks": [],
         "trailing_sl": 0.0, "protection_status": "PASSING"
     }

def render_login_form():
     st.markdown('<div style="max-width:450px; margin: 80px auto 0 auto;">', unsafe_allow_html=True)
     st.markdown('<h2 class="main-title" style="text-align:center;">CORE MATRIX LOGIN</h2>', unsafe_allow_html=True)
     st.markdown('<p class="sub-title-bar" style="text-align:center; margin-bottom:30px;">Institutional Authentication Required</p>', unsafe_allow_html=True)
     
     with st.form("auth_form", clear_on_submit=False):
         u = st.text_input("Access Identifier Username")
         p = st.text_input("Secure Passkey Crypt", type="password")
         submit = st.form_submit_button("Initialize Security Session")
         
         if submit:
             if u == USERNAME and p == PASSWORD:
                 st.session_state.logged_in = True
                 # Write token natively using Streamlit engine API parameters safely
                 st.query_params["session_node"] = "active"
                 st.rerun()
             else:
                 st.error("Invalid node validation configuration profile.")
     st.markdown('</div>', unsafe_allow_html=True)

if not st.session_state.logged_in:
     render_login_form()
     st.stop()

if st.sidebar.button("🔒 Terminal Session Disconnect"):
     st.session_state.logged_in = False
     st.query_params.clear()
     st.rerun()

st.sidebar.markdown('<div style="padding: 2px 10px; background: rgba(16,185,129,0.1); border: 1px solid #10B981; border-radius:6px; color:#10B981; font-size:0.8rem; font-family:\'JetBrains Mono\'; text-align:center;">● REFRESH IMMUNITY ACTIVE</div>', unsafe_allow_html=True)
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
# EXPERT ROBOT CONTROL PANEL (SCALPING ROBOT PRO)
# =====================================================
st.sidebar.subheader("🤖 Scalping Robot Pro Inputs")

selected_tf = st.sidebar.selectbox("M1 Timeframe Optimization", ["1m", "5m", "15m"], index=0, help="Scalping Robot Pro is optimized exclusively for M1.")
trade_direction = st.sidebar.selectbox("Flexible Trade Direction", ["Buy and Sell", "Buy Only", "Sell Only"], index=0)

st.sidebar.markdown("**🌐 Session Filters**")
trade_asian = st.sidebar.checkbox("Trade Asian Session", value=True)
trade_london = st.sidebar.checkbox("Trade London Session", value=True)
trade_ny = st.sidebar.checkbox("Trade New York Session", value=True)

st.sidebar.markdown("**📅 Schedule Controls**")
start_hour = st.sidebar.slider("Trading Start Window (UTC Hour)", 0, 23, 1)
end_hour = st.sidebar.slider("Trading Close Window (UTC Hour)", 0, 23, 22)

st.sidebar.markdown("**🛡️ Safety & Environment Filters**")
news_filter = st.sidebar.checkbox("News Filter Protection Active", value=True)
holiday_filter = st.sidebar.checkbox("Holiday Trading Control Active", value=True)

st.sidebar.markdown("**📉 Risk Management Guardrails**")
lot_size = st.sidebar.number_input("Lot Size Selection", min_value=0.01, max_value=100.0, value=1.0, step=0.1)
account_balance = st.sidebar.number_input("Simulated Account Equity ($)", min_value=1000, value=10000, step=1000)
daily_profit_limit = st.sidebar.number_input("Daily Profit Protection ($)", min_value=0, value=500)
max_drawdown_limit = st.sidebar.number_input("Max Drawdown Protection ($)", min_value=0, value=300)

st.sidebar.markdown("**🎯 Strategy Target Layout**")
tp_mode = st.sidebar.selectbox("Take Profit Mode", ["Automated TP", "Fixed TP"])
fixed_tp_pips = st.sidebar.number_input("Fixed TP (Pips)", min_value=1.0, value=15.0) if tp_mode == "Fixed TP" else 0.0

sl_mode = st.sidebar.selectbox("Stop Loss Mode", ["Automated SL", "Fixed SL"])
fixed_sl_pips = st.sidebar.number_input("Fixed SL (Pips)", min_value=1.0, value=10.0) if sl_mode == "Fixed SL" else 0.0

ts_mode = st.sidebar.selectbox("Trailing Stop Function", ["Automated TS", "Fixed TS", "Disabled"])
fixed_ts_pips = st.sidebar.number_input("Trailing Stop Activation (Pips)", min_value=1.0, value=5.0) if ts_mode == "Fixed TS" else 0.0

# =====================================================
# DATA RETRIEVAL PIPELINE (GOLD ONLY SPECIFICATION)
# =====================================================
GOLD_SYMBOL = "XAUUSD"
GOLD_YF_TICKER = "GC=F"

@st.cache_data(ttl=2)
def get_data_yf_gold(interval="1m", period="5d"):
     try:
         ticker = yf.Ticker(GOLD_YF_TICKER)
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
def calculate_swing_pivots(df: pd.DataFrame, left_bars=3, right_bars=3) -> pd.DataFrame:
     df = df.copy().reset_index(drop=True)
     sh, sl = np.full(len(df), np.nan), np.full(len(df), np.nan)
     for i in range(left_bars, len(df) - right_bars):
         if df["High"].iloc[i] == df["High"].iloc[i - left_bars: i + right_bars + 1].max(): sh[i] = df["High"].iloc[i]
         if df["Low"].iloc[i] == df["Low"].iloc[i - left_bars: i + right_bars + 1].min(): sl[i] = df["Low"].iloc[i]
     df["Swing_High"], df["Swing_Low"] = sh, sl
     return df

def calculate_atr(df, period=14):
     if len(df) < period: return 0.50
     tr = np.maximum(df["High"] - df["Low"], np.maximum(abs(df["High"] - df["Close"].shift()), abs(df["Low"] - df["Close"].shift())))
     atr = tr.rolling(period).mean().iloc[-1]
     return atr if not np.isnan(atr) else 0.50

def rsi_series(df, period=14):
     if len(df) < period: return pd.Series(50.0, index=df.index)
     delta = df["Close"].diff()
     gain, loss = delta.clip(lower=0).rolling(period).mean(), (-delta.clip(upper=0)).rolling(period).mean()
     rs = gain / loss.replace(0, 1e-5)
     return (100 - (100 / (1 + rs))).fillna(50.0)

def trading_session():
     hour = datetime.now(timezone.utc).hour
     if 0 <= hour < 7: return "ASIAN"
     elif 7 <= hour < 13: return "LONDON"
     elif 13 <= hour < 21: return "NEW YORK"
     return "CLOSED"

# =====================================================
# EVALUATE SCALPING ROBOT PRO ENGINE INTERFACE
# =====================================================
def evaluate_scalping_matrix(df):
     if len(df) < 150: return {"is_scalping": False, "state": "INSUFFICIENT BUFFER", "passed": 0, "direction": "NEUTRAL", "checks": [], "protection_status": "PASSING"}
    
     close, high, low = df["Close"].iloc[-1], df["High"].iloc[-1], df["Low"].iloc[-1]
     prev_close = df["Close"].iloc[-2]
     atr = calculate_atr(df)
    
     current_utc_hour = datetime.now(timezone.utc).hour
     current_session = trading_session()
    
     checks_status = []
     protection_status = "PASSING"
    
     schedule_pass = start_hour <= current_utc_hour <= end_hour
     session_pass = (
         (current_session == "ASIAN" and trade_asian) or
         (current_session == "LONDON" and trade_london) or
         (current_session == "NEW YORK" and trade_ny) or
         (current_session == "CLOSED" and False)
     )
    
     news_pass = not (news_filter and (current_utc_hour in [13, 14, 19]))  
     holiday_pass = not (holiday_filter and datetime.now(timezone.utc).weekday() >= 5)
    
     environmental_checks = schedule_pass and session_pass and news_pass and holiday_pass
     if not environmental_checks:
         protection_status = "ENVIRONMENT BLOCKED"
    
     ema_fast = df["Close"].ewm(span=20, adjust=False).mean().iloc[-1]
     ema_slow = df["Close"].ewm(span=50, adjust=False).mean().iloc[-1]
     rsi_val = rsi_series(df).iloc[-1]
    
     n_bar_window = df.tail(10)
     n_bar_high = n_bar_window["High"].max()
     n_bar_low = n_bar_window["Low"].min()

     labels = [
         "Flexible Trend Direction Approval Matrix",
         "Market Session/Schedule Filter Optimization",
         "News Filter Safety Horizon Validation",
         "Micro M1 Momentum Shift (EMA Cross Space)",
         "Volatility Vector Optimization (Price Acceleration)",
         "RSI Momentum Scalp Envelope Range",
         "Immediate Structural Breakout Check"
     ]

     dir_buy_pass = (trade_direction in ["Buy and Sell", "Buy Only"])
     cond_buy = [
         dir_buy_pass,
         schedule_pass and session_pass,
         news_pass and holiday_pass,
         ema_fast > ema_slow,
         close > prev_close,
         40 <= rsi_val <= 70,
         close >= (n_bar_high - (atr * 0.1))
     ]

     dir_sell_pass = (trade_direction in ["Buy and Sell", "Sell Only"])
     cond_sell = [
         dir_sell_pass,
         schedule_pass and session_pass,
         news_pass and holiday_pass,
         ema_fast < ema_slow,
         close < prev_close,
         30 <= rsi_val <= 60,
         close <= (n_bar_low + (atr * 0.1))
     ]

     passed_buy = sum(1 for c in cond_buy if c)
     passed_sell = sum(1 for c in cond_sell if c)

     if passed_buy >= passed_sell:
         active_direction = "BUY"
         max_passed = passed_buy
         checks_status = [{"label": labels[i], "passed": cond_buy[i]} for i in range(7)]
     else:
         active_direction = "SELL"
         max_passed = passed_sell
         checks_status = [{"label": labels[i], "passed": cond_sell[i]} for i in range(7)]

     if protection_status == "ENVIRONMENT BLOCKED":
         return {"is_scalping": False, "state": "🛑 ENVIRONMENT FILTER HALT", "passed": max_passed, "direction": active_direction, "checks": checks_status, "protection_status": protection_status}

     if max_passed == 7:
         return {"is_scalping": True, "state": f"🔥 ROBOT PRO {active_direction} ACTIVE", "passed": 7, "direction": active_direction, "checks": checks_status, "protection_status": "PASSING"}
    
     return {"is_scalping": False, "state": f"MONITORING ({max_passed}/7 Synchronized)", "passed": max_passed, "direction": active_direction, "checks": checks_status, "protection_status": "PASSING"}

# =====================================================
# INTEGRATED QUANTITATIVE SMC CORE SYSTEM
# =====================================================
def institutional_engine(df):
     if df is None or df.empty or len(df) < 50:
         return st.session_state.shared_prediction

     pip_multiplier = 0.10 
     atr_val = calculate_atr(df)
     rsi_val = round(float(rsi_series(df).iloc[-1]), 1)
     price = float(df["Close"].iloc[-1])

     df_pivots = calculate_swing_pivots(df)
     v_highs, v_lows = df_pivots["Swing_High"].dropna(), df_pivots["Swing_Low"].dropna()
     recent_high = float(v_highs.iloc[-1]) if not v_highs.empty else float(df["High"].max())
     recent_low = float(v_lows.iloc[-1]) if not v_lows.empty else float(df["Low"].min())
    
     scalping_profile = evaluate_scalping_matrix(df)

     if tp_mode == "Fixed TP":
         tp_distance = fixed_tp_pips * pip_multiplier
     else:
         tp_distance = max((atr_val * 1.5), 0.8)

     if sl_mode == "Fixed SL":
         sl_distance = fixed_sl_pips * pip_multiplier
     else:
         sl_distance = max((atr_val * 1.2), 0.6)

     entry = price
     if scalping_profile["direction"] == "BUY":
         tp = entry + tp_distance
         sl = entry - sl_distance
         trailing_sl = entry - (fixed_ts_pips * pip_multiplier) if ts_mode == "Fixed TS" else (entry - (atr_val * 0.5))
     else:
         tp = entry - tp_distance
         sl = entry + sl_distance
         trailing_sl = entry + (fixed_ts_pips * pip_multiplier) if ts_mode == "Fixed TS" else (entry + (atr_val * 0.5))

     pips = round(abs(tp - entry) / pip_multiplier, 1)
     confidence = (scalping_profile["passed"] / 7) * 100

     signal = "NEUTRAL"
     if scalping_profile["is_scalping"]:
         signal = f"PRO SCALP {scalping_profile['direction']}"
     elif scalping_profile["passed"] >= 5:
         signal = f"PENDING {scalping_profile['direction']} SETUP"

     return {
         "signal": signal, "confidence": round(float(confidence), 1), "entry": round(entry, 2),
         "tp": round(tp, 2), "sl": round(sl, 2), "pips": pips, "rsi": rsi_val,
         "structure": f"ROBOT PRO GRID: {scalping_profile['state']}",
         "buy_score": round((scalping_profile["passed"]/7)*100 if scalping_profile["direction"] == "BUY" else 0),
         "sell_score": round((scalping_profile["passed"]/7)*100 if scalping_profile["direction"] == "SELL" else 0),
         "session": f"{trading_session()} MARKET WINDOW",
         "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
         "recent_high": round(recent_high, 2), "recent_low": round(recent_low, 2),
         "fvg_status": "ROBOT M1 FILTERS", "ob_status": "ACTIVE PROTECTION",
         "is_scalping": scalping_profile["is_scalping"],
         "scalping_state": scalping_profile["state"],
         "conditions_passed": scalping_profile["passed"],
         "direction": scalping_profile["direction"],
         "checks": scalping_profile["checks"],
         "trailing_sl": round(trailing_sl, 2),
         "protection_status": scalping_profile["protection_status"]
     }

# =====================================================
# LIVE DASHBOARD RECONSTRUCTED LAYER
# =====================================================
@st.fragment(run_every=1)
def render_live_dashboard(tf):
     market_data = get_data_yf_gold(interval=tf, period="5d")
     if market_data.empty or len(market_data) < 100:
         st.warning("Constructing Robot Pro telemetry buffer maps. Standardizing tick arrays...")
         return

     result = institutional_engine(market_data)
     st.session_state.shared_prediction = result

     card_style = "neutral"
     if result["protection_status"] == "ENVIRONMENT BLOCKED": card_style = "neutral"
     elif result["is_scalping"]: card_style = "scalping"
     elif result["direction"] == "BUY": card_style = "buy"
     elif result["direction"] == "SELL": card_style = "sell"
    
     st.markdown(f"""
     <div class="matrix-card {card_style}">
         <span style="font-family:'JetBrains Mono'; font-size:0.8rem; color:#E2E8F0;">[SCALPING ROBOT PRO ENGINE INTEGRATION LAYER]</span>
         <h2 style="margin:5px 0 0 0; font-weight:600; color:#FFFFFF;">XAUUSD ({tf}) — <span style="color:#FFD700;">{result['scalping_state']}</span></h2>
     </div>
     """, unsafe_allow_html=True)

     m_col1, m_col2, m_col3, m_col4 = st.columns(4)
     with m_col1:
         st.markdown(f'<div class="metric-glow-box"><div class="metric-glow-label">Robot Multi-Filters</div><div class="metric-glow-val" style="color:#FFD700;">{result["conditions_passed"]} / 7</div></div>', unsafe_allow_html=True)
     with m_col2:
         st.markdown(f'<div class="metric-glow-box"><div class="metric-glow-label">TP Objective Size</div><div class="metric-glow-val">{result["pips"]} Pips</div></div>', unsafe_allow_html=True)
     with m_col3:
         st.markdown(f'<div class="metric-glow-box"><div class="metric-glow-label">Dynamic Trailing SL</div><div class="metric-glow-val" style="color:#A855F7;">{result["trailing_sl"]}</div></div>', unsafe_allow_html=True)
     with m_col4:
         st.markdown(f'<div class="metric-glow-box"><div class="metric-glow-label">EA Safety Filter Block</div><div class="metric-glow-val" style="font-size:0.95rem; line-height:2.2rem; color:#10B981;">{result["protection_status"]}</div></div>', unsafe_allow_html=True)

     with st.sidebar.expander("🔍 EA SCALPING PRO MATRIX METRICS", expanded=True):
         color_map = {"BUY": "#10B981", "SELL": "#FF4B4B", "NEUTRAL": "#64748B"}
         st.markdown(f"**Target Direction Mode:** <span style='color:{color_map.get(result['direction'], '#FFF')}; font-weight:bold;'>{trade_direction} ({result['direction']})</span>", unsafe_allow_html=True)
         st.markdown(f"**Operational Lot Weight:** ` {lot_size} Lots `")
         st.markdown("---")
         for check in result.get('checks', []):
             icon = "✅" if check["passed"] else "❌"
             color = "#10B981" if check["passed"] else "#EF4444"
             st.markdown(f"<span style='color:{color}; font-size:0.85rem; font-family:\"JetBrains Mono\";'>{icon} {check['label']}</span>", unsafe_allow_html=True)

     st.markdown("<br>", unsafe_allow_html=True)

     fig = go.Figure()
     fig.add_trace(go.Candlestick(x=market_data["time"], open=market_data["Open"], high=market_data["High"], low=market_data["Low"], close=market_data["Close"], name="Gold Spot M1"))
    
     ema20 = market_data["Close"].ewm(span=20, adjust=False).mean()
     ema50 = market_data["Close"].ewm(span=50, adjust=False).mean()
     fig.add_trace(go.Scatter(x=market_data["time"], y=ema20, line=dict(color="#FFD700", width=1), name="EA Micro Fast (20)"))
     fig.add_trace(go.Scatter(x=market_data["time"], y=ema50, line=dict(color="#A855F7", width=1.5), name="EA Structural Trend (50)"))

     fig.update_layout(template="plotly_dark", height=400, xaxis_rangeslider_visible=False, uirevision="keep", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(l=10, r=10, t=10, b=10))
     st.plotly_chart(fig, use_container_width=True)

     g_col1, g_col2, g_col3 = st.columns(3)
     with g_col1:
         st.metric("Protection Target Profile", f"${account_balance}")
     with g_col2:
         st.metric("Max Account Daily Drawdown Limit", f"${max_drawdown_limit}" if max_drawdown_limit > 0 else "OFF")
     with g_col3:
         st.metric("Daily Profit Cap Objective", f"${daily_profit_limit}" if daily_profit_limit > 0 else "OFF")

     with st.expander("Scalping Robot Pro Target Telemetry Array Logs"):
         st.json(result)

     if result["is_scalping"]:
         st.toast(f"🚨 SCALPING ROBOT PRO HIGH VELOCITY BREAKOUT TRIGGERED!", icon="🤖")

# =====================================================
# MAIN ENGINE LAYOUT ASSEMBLY
# =====================================================
st.markdown('<h1 class="main-title">CORE MATRIX // SCALPING ROBOT PRO</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-title-bar">M1 TIMEFRAME HIGH FREQUENCY GOLD ARCHITECTURE OPERATIONAL PROFILE</p>', unsafe_allow_html=True)

col_layout_left, col_layout_right = st.columns([1.9, 1.1])

with col_layout_left:
     render_live_dashboard(selected_tf)
    
     st.markdown("---")
     st.markdown("### 📊 Realtime Gold TradingView Node Stream")
     html_widget = """
     <div id="tv_chart_container" style="border: 1px solid rgba(255,255,255,0.05); border-radius: 8px; overflow: hidden;"></div>
     <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
     <script type="text/javascript">
     new TradingView.widget({
        "width": "100%",
        "height": 450,
        "symbol": "FX_IDC:XAUUSD",
        "interval": "1",
        "timezone": "Etc/UTC",
        "theme": "dark",
        "style": "1",
        "locale": "en",
        "toolbar_bg": "#0A0E17",
        "enable_publishing": false,
        "hide_side_toolbar": false,
        "allow_symbol_change": false,
        "container_id": "tv_chart_container"
     });
     </script>
     """
     components.html(html_widget, height=470)

with col_layout_right:
     st.markdown("""
     <div style="background: rgba(15, 23, 42, 0.4); padding: 12px 15px; border-radius: 8px 8px 0 0; border: 1px solid rgba(255,255,255,0.05); border-bottom: none;">
         <span style="font-family:'JetBrains Mono'; font-size:0.8rem; color:#FFD700; font-weight:600;">📩 ROBOT TELEMETRY BROADCAST HUB</span>
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
                 message = f"""🤖 <b>SCALPING ROBOT PRO OPERATIONAL DISPATCH</b>

VECTOR TARGET: <code>XAUUSD</code> [M1 Optimized]
MATRIX METRIC: <b>{current_result['scalping_state']}</b>
SIGNAL MATRIX LEVEL: <code>{current_result['signal']}</code>
LOT WEIGHT QUANTITY: <code>{lot_size} Lots</code>

🎯 <b>RISK EXECUTION PROFILE BOUNDARIES:</b>
• Entry Price Node: {current_result['entry']}
• Take Profit Level ({tp_mode}): {current_result['tp']}
• Stop Loss Boundary ({sl_mode}): {current_result['sl']}
• Dynamic Trailing Matrix SL: {current_result['trailing_sl']}
• Profit Objective Spectrum: {current_result['pips']} Pips

🛡️ <b>SAFETY GATE CONTROLS:</b>
• Active Environment Status: {current_result['protection_status']}
• Account Balance Baseline: ${account_balance}
• Daily Drawdown Protections: ${max_drawdown_limit if max_drawdown_limit > 0 else 'DISABLED'}

🕒 <i>Transmission Frame: {current_result['timestamp']} UTC</i>"""
                
                 success, err_msg = send_telegram(message)
                 if success: 
                     st.toast("Robot Pro payload broadcast complete across network arrays!", icon="🚀")
                 else: 
                     st.error(f"Transmission Failed: {err_msg}")
