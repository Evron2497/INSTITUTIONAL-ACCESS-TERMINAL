# import os
# from datetime import datetime, timezone
# import time
# import json
# import numpy as np
# import pandas as pd
# import requests
# import streamlit as st
# import streamlit.components.v1 as components
# import plotly.graph_objects as go
# import MetaTrader5 as mt5

# # =====================================================
# # PAGE CONFIG
# # =====================================================
# st.set_page_config(page_title="PRO FORWARD ALGO TERMINAL", page_icon="🏦", layout="wide")

# # =====================================================
# # LOGIN SYSTEM
# # =====================================================
# USERNAME = st.secrets.get("USERNAME", "")
# PASSWORD = st.secrets.get("PASSWORD", "")

# if "logged_in" not in st.session_state:
#     st.session_state.logged_in = False

# if "shared_prediction" not in st.session_state:
#     st.session_state.shared_prediction = {
#         "signal": "NEUTRAL", "confidence": 0, "entry": 0, "tp": 0, "sl": 0,
#         "pips": 0, "rsi": 50, "structure": "INITIALIZING", "buy_score": 0, "sell_score": 0,
#         "session": "UNKNOWN", "timestamp": "", "recent_high": 0, "recent_low": 0
#     }

# def login():
#     st.title("🏦 Institutional Access Terminal")
#     u = st.text_input("Username")
#     p = st.text_input("Password", type="password")
#     if st.button("Login"):
#         if u == USERNAME and p == PASSWORD:
#             st.session_state.logged_in = True
#             st.rerun()
#         else:
#             st.error("Invalid credentials")

# if not st.session_state.logged_in:
#     login()
#     st.stop()

# # =====================================================
# # MT5 INITIALIZATION — Connection Guard
# # =====================================================
# MT5_LOGIN    = int(st.secrets["MT5_LOGIN"])
# MT5_PASSWORD = st.secrets["MT5_PASSWORD"]
# MT5_SERVER   = st.secrets["MT5_SERVER"]

# if "mt5_connected" not in st.session_state:
#     st.session_state.mt5_connected = False

# if not st.session_state.mt5_connected:
#     if not mt5.initialize():
#         st.error("MT5 initialization failed. Verify terminal paths or administrative permissions.")
#         st.stop()
#     if not mt5.login(MT5_LOGIN, MT5_PASSWORD, MT5_SERVER):
#         st.error("MT5 authentication rejected. Check login keys or broker server strings.")
#         mt5.shutdown()
#         st.stop()
#     st.session_state.mt5_connected = True

# st.sidebar.success("✅ MT5 Mainframe Connected")

# # =====================================================
# # TELEGRAM DISPATCH PIPELINE
# # =====================================================
# BOT_TOKEN = st.secrets.get("BOT_TOKEN", "")
# CHAT_IDS  = st.secrets.get("CHAT_IDS", [])

# def send_telegram(message: str):
#     if not BOT_TOKEN or not CHAT_IDS:
#         return False, "Telegram vectors unconfigured."
#     url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
#     errors = []
#     for chat_id in CHAT_IDS:
#         try:
#             r = requests.post(url, data={"chat_id": chat_id, "text": message, "parse_mode": "HTML"}, timeout=10)
#             if r.status_code != 200:
#                 errors.append(f"Chat {chat_id}: {r.text}")
#         except Exception as e:
#             errors.append(str(e))
#     return (len(errors) == 0), "; ".join(errors)

# # =====================================================
# # CORE CONFIG & METATRADER DATA INGESTION
# # =====================================================
# pairs = [
#     "EURUSD", "GBPUSD", "USDJPY", "USDCHF", "USDCAD",
#     "AUDUSD", "NZDUSD", "EURGBP", "EURJPY", "GBPJPY",
#     "XAUUSD", "BTCUSD"
# ]

# selected_pair = st.sidebar.selectbox("Select Core Vector Pair", pairs)

# @st.cache_data(ttl=3)
# def get_data(symbol, timeframe=mt5.TIMEFRAME_M15, bars=300):
#     rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, bars)
#     if rates is None or len(rates) == 0:
#         return pd.DataFrame()
#     df = pd.DataFrame(rates)
#     df["time"] = pd.to_datetime(df["time"], unit="s")
#     df.rename(columns={
#         "open": "Open", "high": "High", "low": "Low",
#         "close": "Close", "tick_volume": "Volume"
#     }, inplace=True)
#     return df

# # =====================================================
# # TECHNICAL INDICATORS & ALGORITHMIC FUNCTIONS
# # =====================================================
# def calculate_swing_pivots(df: pd.DataFrame, left_bars: int = 5, right_bars: int = 5) -> pd.DataFrame:
#     df = df.copy().reset_index(drop=True)
#     swing_high = np.full(len(df), np.nan)
#     swing_low  = np.full(len(df), np.nan)

#     for i in range(left_bars, len(df) - right_bars):
#         window_h = df["High"].iloc[i - left_bars: i + right_bars + 1]
#         window_l = df["Low"].iloc[i - left_bars: i + right_bars + 1]
#         if df["High"].iloc[i] == window_h.max():
#             swing_high[i] = df["High"].iloc[i]
#         if df["Low"].iloc[i] == window_l.min():
#             swing_low[i] = df["Low"].iloc[i]

#     df["Swing_High"] = swing_high
#     df["Swing_Low"]  = swing_low
#     return df

# def calculate_atr(df, period=14):
#     if len(df) < period:
#         return 0.001
#     tr = np.maximum(
#         df["High"] - df["Low"],
#         np.maximum(
#             abs(df["High"] - df["Close"].shift()),
#             abs(df["Low"]  - df["Close"].shift())
#         )
#     )
#     atr = tr.rolling(period).mean().iloc[-1]
#     return atr if not np.isnan(atr) else 0.001

# def rsi(df, period=14):
#     if len(df) < period:
#         return 50.0
#     delta = df["Close"].diff()
#     gain  = delta.clip(lower=0).rolling(period).mean()
#     loss  = (-delta.clip(upper=0)).rolling(period).mean()
#     last_gain = gain.iloc[-1]
#     last_loss = loss.iloc[-1]
#     if last_loss == 0 and last_gain == 0: return 50.0
#     if last_loss == 0: return 100.0
#     rs = last_gain / last_loss
#     return round(100 - (100 / (1 + rs)), 2)

# def trading_session():
#     hour = datetime.now(timezone.utc).hour
#     if 0 <= hour < 7: return "ASIAN (ACCUMULATION)"
#     elif 7 <= hour < 13: return "LONDON (MANIPULATION)"
#     elif 13 <= hour < 21: return "NEW YORK (DISTRIBUTION)"
#     return "CLOSED"

# def calculate_pips(entry, tp, pair):
#     pip_value = 0.01 if "JPY" in pair.upper() else 0.0001
#     return round(abs(tp - entry) / pip_value, 1)

# def neutral_result():
#     return {
#         "signal": "NEUTRAL", "confidence": 0, "entry": 0, "tp": 0, "sl": 0,
#         "pips": 0, "rsi": 50, "structure": "INSUFFICIENT HISTORICAL DATA", "buy_score": 0,
#         "sell_score": 0, "session": trading_session(), "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
#         "recent_high": 0, "recent_low": 0
#     }

# # =====================================================
# # ADVANCED INSTITUTIONAL SMC ENGINE
# # =====================================================
# def institutional_engine(df, pair):
#     if df is None or df.empty or len(df) < 50:
#         return neutral_result()

#     pip_multiplier = 0.01 if "JPY" in pair.upper() else 0.0001

#     # 1. TIME ALIGNMENT & KILLZONES
#     current_time_utc = datetime.now(timezone.utc)
#     float_time       = current_time_utc.hour + (current_time_utc.minute / 60.0)
#     is_active_killzone = (6.0 <= float_time <= 10.0) or (12.0 <= float_time <= 16.0)

#     # 2. ATR COMPUTATION
#     atr_val = calculate_atr(df)

#     # 3. HIGH-TIMEFRAME (HTF) TREND FILTER (M30 Structural Control)
#     df_m30   = get_data(pair, timeframe=mt5.TIMEFRAME_M30, bars=100)
#     htf_bias = "NEUTRAL"
#     if df_m30 is not None and not df_m30.empty and len(df_m30) >= 30:
#         m30_ema  = df_m30["Close"].ewm(span=30).mean().iloc[-1]
#         htf_bias = "BULLISH" if df_m30["Close"].iloc[-1] > m30_ema else "BEARISH"

#     # 4. SWING PIVOT LIQUIDITY ANALYSIS
#     df          = calculate_swing_pivots(df, left_bars=5, right_bars=5)
#     valid_highs = df["Swing_High"].dropna()
#     valid_lows  = df["Swing_Low"].dropna()
#     recent_high = float(valid_highs.iloc[-1]) if not valid_highs.empty else float(df["High"].max())
#     recent_low  = float(valid_lows.iloc[-1])  if not valid_lows.empty  else float(df["Low"].min())

#     # 5. PREMIUM VS DISCOUNT DISTRIBUTION MODEL
#     current_range  = recent_high - recent_low
#     price          = float(df["Close"].iloc[-1])
#     midpoint       = recent_low + (current_range * 0.50)
#     is_in_discount = price < midpoint
#     is_in_premium  = price > midpoint

#     # 6. INSTANTANEOUS LIQUIDITY SWEEP DETECTORS (Using Closed Candles to prevent lagging repaints)
#     sweep_buy  = False
#     sweep_sell = False
#     lookback   = min(6, len(df) - 1)
#     for idx in range(-lookback, -1):
#         if df["Low"].iloc[idx] < recent_low and df["Close"].iloc[idx] > recent_low:
#             sweep_buy = True
#         if df["High"].iloc[idx] > recent_high and df["Close"].iloc[idx] < recent_high:
#             sweep_sell = True

#     # 7. MARKET STRUCTURE SHIFT (MSS) VALIDATION
#     last_body   = abs(df["Close"].iloc[-2] - df["Open"].iloc[-2])
#     avg_body    = abs(df["Close"] - df["Open"]).iloc[-22:-2].mean()
#     mss_bullish = df["Close"].iloc[-2] > recent_high and last_body > avg_body
#     mss_bearish = df["Close"].iloc[-2] < recent_low and last_body > avg_body

#     # 8. REFINED CLOSED-CANDLE FAIR VALUE GAPS (FVG)
#     # Evaluated strictly over historic data points to guarantee zero execution time drift
#     fvg_buy  = df["Low"].iloc[-2] > df["High"].iloc[-4]
#     fvg_sell = df["High"].iloc[-2] < df["Low"].iloc[-4]

#     # 9. COMPREHENSIVE VECTOR WEIGHT SCORING
#     buy_score, sell_score = 0, 0

#     if htf_bias == "BULLISH": buy_score  += 35
#     if htf_bias == "BEARISH": sell_score += 35
#     if sweep_buy:             buy_score  += 25
#     if sweep_sell:            sell_score += 25
#     if mss_bullish:           buy_score  += 25
#     if mss_bearish:           sell_score += 25
#     if fvg_buy:               buy_score  += 15
#     if fvg_sell:              sell_score += 15

#     # Premium / Discount Logic: Structural Gatekeeper
#     if not is_in_discount: buy_score = int(buy_score * 0.25)
#     if not is_in_premium:  sell_score = int(sell_score * 0.25)

#     # 10. SYSTEM SIGNAL GENERATION
#     signal = "NEUTRAL"
#     confidence = max(buy_score, sell_score)

#     if buy_score >= 75: signal = "STRONG BUY (A+ Setup)"
#     elif buy_score >= 55: signal = "BUY"
    
#     if sell_score >= 75: signal = "STRONG SELL (A+ Setup)"
#     elif sell_score >= 55 and "BUY" not in signal: signal = "SELL"

#     # 11. QUANTITATIVE TRADE MANAGEMENT DESIGN (Dynamic SL / TP Protection)
#     entry = price
#     tp, sl = entry, entry

#     if "BUY" in signal:
#         tp = recent_high
#         if (tp - entry) / pip_multiplier < 12.0:
#             tp = entry + (15 * pip_multiplier)
#         sl = recent_low - (atr_val * 0.75)
#     elif "SELL" in signal:
#         tp = recent_low
#         if (entry - tp) / pip_multiplier < 12.0:
#             tp = entry - (15 * pip_multiplier)
#         sl = recent_high + (atr_val * 0.75)

#     pips = calculate_pips(entry, tp, pair) if "NEUTRAL" not in signal else 0
#     rsi_val = rsi(df)

#     return {
#         "signal": signal,
#         "confidence": round(confidence, 1),
#         "entry": round(entry, 5),
#         "tp": round(tp, 5),
#         "sl": round(sl, 5),
#         "pips": round(pips, 1),
#         "rsi": round(rsi_val, 1),
#         "structure": f"M30 Control: {htf_bias} | Volume Loop: {'ACTIVE KILLZONE' if is_active_killzone else 'OFF-PEAK FLOW'}",
#         "buy_score": buy_score,
#         "sell_score": sell_score,
#         "session": trading_session(),
#         "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
#         "recent_high": round(recent_high, 5),
#         "recent_low": round(recent_low, 5)
#     }

# # =====================================================
# # ENGINE SCANNER (Isolated Execution Cache)
# # =====================================================
# @st.cache_data(ttl=25)
# def run_scanner(pairs_tuple):
#     scan_data = []
#     for p in pairs_tuple:
#         try:
#             pair_df = get_data(p)
#             if pair_df.empty:
#                 scan_data.append([p, "NO DATA", "—", "—", 0, "—"])
#                 continue
#             pair_res = institutional_engine(pair_df, p)
#             scan_data.append([
#                 p, pair_res["signal"], f"{pair_res['confidence']}%",
#                 pair_res["structure"], pair_res["pips"], pair_res["session"]
#             ])
#         except Exception:
#             scan_data.append([p, "ENGINE EXCEPTION", "—", "—", 0, "—"])
#     return scan_data

# # =====================================================
# # LIVE DASHBOARD FRAGMENT (Isolated Rapid Frame)
# # =====================================================
# @st.fragment(run_every=4)
# def render_live_dashboard(pair):
#     market_data = get_data(pair, timeframe=mt5.TIMEFRAME_M15, bars=300)
#     if market_data.empty:
#         st.warning(f"Failed to pull active stream buffers for {pair}. Market may be closed.")
#         return

#     result = institutional_engine(market_data, pair)
#     st.session_state.shared_prediction = result

#     # Candlestick Visualizations
#     plot_df = calculate_swing_pivots(market_data, left_bars=5, right_bars=5)
#     fig = go.Figure()

#     fig.add_trace(go.Candlestick(
#         x=plot_df["time"], open=plot_df["Open"], high=plot_df["High"],
#         low=plot_df["Low"], close=plot_df["Close"], name=pair
#     ))
#     fig.add_trace(go.Scatter(
#         x=plot_df["time"], y=plot_df["Swing_High"], mode="markers",
#         name="Buy-Side Liquidity (BSL)", marker=dict(color="#FF4B4B", size=7, symbol="triangle-down")
#     ))
#     fig.add_trace(go.Scatter(
#         x=plot_df["time"], y=plot_df["Swing_Low"], mode="markers",
#         name="Sell-Side Liquidity (SSL)", marker=dict(color="#00F0FF", size=7, symbol="triangle-up")
#     ))

#     if result["recent_high"] > 0:
#         fig.add_hline(y=result["recent_high"], line_dash="dash", line_color="rgba(255,75,75,0.5)", annotation_text="BSL Pool")
#         fig.add_hline(y=result["recent_low"],  line_dash="dash", line_color="rgba(0,240,255,0.5)", annotation_text="SSL Pool")
#         eq = result["recent_low"] + ((result["recent_high"] - result["recent_low"]) * 0.5)
#         fig.add_hline(y=eq, line_dash="dot", line_color="#FFFF00", annotation_text="Equilibrium (50%)")

#     fig.update_layout(
#         title=f"🔥 LIVE {pair} (15M Execution Matrix Map)", template="plotly_dark",
#         height=480, xaxis_rangeslider_visible=False, uirevision="keep",
#         margin=dict(l=10, r=10, t=40, b=10)
#     )
#     st.plotly_chart(fig, use_container_width=True)

#     # Scoring Analytics Frame
#     st.markdown("### 🔍 Alpha Convergence Matrix Analysis")
#     max_score = min(int(max(result["buy_score"], result["sell_score"])), 100)
#     st.progress(max_score / 100)

#     sc1, sc2 = st.columns(2)
#     sc1.write(f"🟢 **Institutional Accumulation Load:** `{result['buy_score']}/100`")
#     sc2.write(f"🔴 **Institutional Distribution Load:** `{result['sell_score']}/100`")
    
#     st.markdown("---")
#     c1, c2, c3, c4 = st.columns(4)
#     c1.metric("Structural Vector", result["signal"])
#     c2.metric("Matrix Certainty Factor", f"{result['confidence']}%")
#     c3.metric("Calculated Vector Range", f"{result['pips']} Pips")
#     c4.metric("Active Session Window", result["session"])

#     with st.expander("Engine Log Buffer (JSON)"):
#         st.json(result)

#     # Intrusive Signal Capture Alert
#     if "STRONG" in result["signal"] and result["pips"] >= 12.0:
#         audio_url = "https://actions.google.com/sounds/v1/alarms/digital_watch_alarm_long.ogg"
#         components.html(f'<audio autoplay><source src="{audio_url}" type="audio/ogg"></audio>', height=0)
#         st.toast(f"🚨 STRATEGIC ALGO DETECTED SETUP ON {pair}!", icon="💰")

# # =====================================================
# # HIGH REFLECTION GRID SCANNER FRAGMENT
# # =====================================================
# @st.fragment(run_every=20)
# def render_scanner_block():
#     st.subheader("📡 Cross-Asset Matrix Scanner Grid")
#     scan_data = run_scanner(tuple(pairs))
#     scanner_df = pd.DataFrame(scan_data, columns=["Pair", "Signal Bias", "Confidence Factor", "SMC Architecture Status", "Range Projection", "Current Session Flow"])
#     st.dataframe(scanner_df, use_container_width=True, hide_index=True)

# # =====================================================
# # MAIN ENGINE LAYOUT ASSEMBLY
# # =====================================================
# st.title("🏦 TECH-STAR INSTITUTIONAL QUANT MATRIX TERMINAL 🚀")
# st.markdown("---")

# # Left Column: Operational Control & Terminal Charts | Right Column: Global Cross Scanner Grid
# col_layout_left, col_layout_right = st.columns([1.8, 1.2])

# with col_layout_left:
#     render_live_dashboard(selected_pair)

# with col_layout_right:
#     render_scanner_block()

# st.markdown("---")
# current_result = st.session_state.shared_prediction

# # =====================================================
# # SIGNAL DISPATCH INTERFACE
# # =====================================================
# st.subheader("📩 High-Priority Signal Broadcast Hub")
# confirm_send = st.checkbox("Acknowledge strict compliance with algorithmic validation logic rules.")

# if st.button("🚀 EXECUTE NETWORK TELEGRAM BROADCAST"):
#     if not confirm_send:
#         st.warning("Execution Rejected: Affirm network confirmation verification protocol.")
#     elif "NEUTRAL" in current_result["signal"]:
#         st.error("Execution Aborted: Algorithmic engine must contain active market matrix parameters to scale broadcast vectors.")
#     else:
#         message = f"""🏦 <b>TECH-STAR QUALIFIED ALGO SIGNAL</b>

# VECTOR PAIR: {selected_pair}
# SIGNAL BIAS: <b>{current_result['signal']}</b>
# CONFIDENCE COEFFICIENT: {current_result['confidence']}%
# SMC STRUCTURE: {current_result['structure']}

# ENTRY RATE: {current_result['entry']}
# TARGET PROFIT (TP): {current_result['tp']}
# STOP LOSS (SL): {current_result['sl']}

# 📊 EXPECTED RANGE YIELD: <b>{current_result['pips']} Pips</b>
# Ceiling Liquidity Line: {current_result['recent_high']}
# Floor Liquidity Line: {current_result['recent_low']}

# RSI SCALAR: {current_result['rsi']}
# TEMPORAL SESSION: {current_result['session']}
# SYSTEM TIME STAMP: {current_result['timestamp']}
# """
#         ok, err = send_telegram(message)
#         if ok:
#             st.success("✅ Broadcast system arrays systematically deployed to Telegram channels.")
#         else:
#             st.error(f"❌ Telegram pipeline distribution exception: {err}")

# # =====================================================
# # ADVANCED ANALYTICAL ENGINE FRAMEWORK (TRADINGVIEW)
# # =====================================================
# st.markdown("---")
# st.subheader("📊 Supplementary Quantitative Analytics Stream")
# symbol_tv = f"OANDA:{selected_pair}"
# html_widget = f"""
# <script src="https://s3.tradingview.com/tv.js"></script>
# <div id="tv_chart_container"></div>
# <script>
# new TradingView.widget({{
#   "symbol": "{symbol_tv}",
#   "interval": "15",
#   "container_id": "tv_chart_container",
#   "width": "100%",
#   "height": 500,
#   "theme": "dark",
#   "style": "1",
#   "locale": "en",
#   "toolbar_bg": "#f1f3f6",
#   "enable_publishing": false,
#   "hide_side_toolbar": false,
#   "allow_symbol_change": true
# }});
# </script>
# """
# components.html(html_widget, height=520)

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
import MetaTrader5 as mt5

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
# MT5 INITIALIZATION
# =====================================================
MT5_LOGIN    = int(st.secrets["MT5_LOGIN"])
MT5_PASSWORD = st.secrets["MT5_PASSWORD"]
MT5_SERVER   = st.secrets["MT5_SERVER"]

if "mt5_connected" not in st.session_state:
    st.session_state.mt5_connected = False

if not st.session_state.mt5_connected:
    if not mt5.initialize():
        st.error("MT5 initialization failed.")
        st.stop()
    if not mt5.login(MT5_LOGIN, MT5_PASSWORD, MT5_SERVER):
        st.error("MT5 authentication rejected.")
        mt5.shutdown()
        st.stop()
    st.session_state.mt5_connected = True

st.sidebar.success("✅ MT5 Mainframe Connected")

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
# CONFIG & DATA INGESTION — Streamlined Pairs Array
# =====================================================
# Reduced to top 4 high-volume majors + Gold for maximum responsiveness
pairs = [
    "EURUSD", 
    "GBPUSD", 
    "USDJPY", 
    "AUDUSD", 
    "XAUUSD"
]

selected_pair = st.sidebar.selectbox("Select Active Vector Pair", pairs)

@st.cache_data(ttl=2)
def get_data(symbol, timeframe=mt5.TIMEFRAME_M15, bars=300):
    rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, bars)
    if rates is None or len(rates) == 0:
        return pd.DataFrame()
    df = pd.DataFrame(rates)
    df["time"] = pd.to_datetime(df["time"], unit="s")
    df.rename(columns={"open": "Open", "high": "High", "low": "Low", "close": "Close", "tick_volume": "Volume"}, inplace=True)
    return df

# =====================================================
# MATH & RE-ARCHITECTED ADVANCED SIGNAL ALGORITHMS
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

def rsi(df, period=14):
    if len(df) < period: return 50.0
    delta = df["Close"].diff()
    gain  = delta.clip(lower=0).rolling(period).mean()
    loss  = (-delta.clip(upper=0)).rolling(period).mean()
    last_gain = gain.iloc[-1]
    last_loss = loss.iloc[-1]
    if last_loss == 0 and last_gain == 0: return 50.0
    if last_loss == 0: return 100.0
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
    for i in range(2, min(lookback, len(df))):
        if df["Low"].iloc[-i+1] > df["High"].iloc[-i-1]:
            fvg_buy = True
        if df["High"].iloc[-i+1] < df["Low"].iloc[-i-1]:
            fvg_sell = True
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
    for i in range(3, min(20, len(df))):
        candle = df.iloc[-i]
        next_two = df.iloc[-i+1:-i+3]
        if candle["Close"] < candle["Open"]:
            if all(next_two["Close"] > next_two["Open"]):
                ob_bull = True
        if candle["Close"] > candle["Open"]:
            if all(next_two["Close"] < next_two["Open"]):
                ob_bear = True
    return ob_bull, ob_bear

def volume_spike(df, threshold=1.5):
    avg_vol = df["Volume"].tail(20).mean()
    last_vol = df["Volume"].iloc[-1]
    return last_vol > (avg_vol * threshold)

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
    float_time       = current_time_utc.hour + (current_time_utc.minute / 60.0)
    is_algo_killzone = (6.0 <= float_time <= 10.0) or (12.0 <= float_time <= 16.0)

    atr_val = calculate_atr(df)

    # Multi-Timeframe Trend Stack (M30 Structural Filters)
    df_m30 = get_data(pair, timeframe=mt5.TIMEFRAME_M30, bars=100)
    htf_bias = "NEUTRAL"
    if df_m30 is not None and not df_m30.empty and len(df_m30) >= 30:
        m30_ema20 = df_m30["Close"].ewm(span=20).mean().iloc[-1]
        m30_ema50 = df_m30["Close"].ewm(span=50).mean().iloc[-1]
        if df_m30["Close"].iloc[-1] > m30_ema20 > m30_ema50:
            htf_bias = "BULLISH"
        elif df_m30["Close"].iloc[-1] < m30_ema20 < m30_ema50:
            htf_bias = "BEARISH"

    df          = calculate_swing_pivots(df, left_bars=5, right_bars=5)
    valid_highs = df["Swing_High"].dropna()
    valid_lows  = df["Swing_Low"].dropna()
    recent_high = float(valid_highs.iloc[-1]) if not valid_highs.empty else float(df["High"].max())
    recent_low  = float(valid_lows.iloc[-1])  if not valid_lows.empty  else float(df["Low"].min())

    # Premium / Discount Models
    current_range  = recent_high - recent_low if (recent_high - recent_low) > 0 else 0.001
    price          = float(df["Close"].iloc[-1])
    midpoint       = recent_low + (current_range * 0.50)

    sweep_buy = any(df["Low"].tail(6) < recent_low) and (df["Close"].iloc[-1] > recent_low)
    sweep_sell = any(df["High"].tail(6) > recent_high) and (df["Close"].iloc[-1] < recent_high)

    choch_bull, choch_bear = detect_choch(df, recent_high, recent_low)
    fvg_buy_present, fvg_sell_present = detect_fvg(df)
    ob_bullish, ob_bearish = detect_order_block(df)

    # Matrix Point Evaluation Weighting
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

    # Soft Linear Matrix Discount Gradients
    discount_factor = 1.0 - max(0, (price - midpoint) / current_range) * 0.6
    premium_factor  = 1.0 - max(0, (midpoint - price) / current_range) * 0.6
    buy_score       = int(buy_score * discount_factor)
    sell_score      = int(sell_score * premium_factor)

    if not is_algo_killzone:
        buy_score  = int(buy_score * 0.7)
        sell_score = int(sell_score * 0.7)

    signal = "NEUTRAL"
    confidence = max(buy_score, sell_score)

    if buy_score >= 70: signal = "STRONG BUY (SMC Convergence)"
    elif buy_score >= 50: signal = "BUY"
    if sell_score >= 70: signal = "STRONG SELL (SMC Convergence)"
    elif sell_score >= 50 and "BUY" not in signal: signal = "SELL"

    entry = price
    # Adaptive ATR Geometry for Target Scaling
    if "BUY" in signal:
        sl  = entry - (atr_val * 1.5)
        tp1 = entry + (atr_val * 1.5 * 2.0)
        tp  = min(recent_high, tp1)
        if (tp - entry) < (10 * pip_multiplier):
            tp = entry + (atr_val * 3.0)
    elif "SELL" in signal:
        sl  = entry + (atr_val * 1.5)
        tp1 = entry - (atr_val * 1.5 * 2.0)
        tp  = max(recent_low, tp1)
        if (entry - tp) < (10 * pip_multiplier):
            tp = entry - (atr_val * 3.0)
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
            pair_df = get_data(p)
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
    market_data = get_data(pair, timeframe=mt5.TIMEFRAME_M15, bars=300)
    if market_data.empty:
        st.warning(f"Market Stream for {pair} is currently offline.")
        return

    result = institutional_engine(market_data, pair)
    
    # Hysteresis Filter Engine Frame to Avoid Rapid Toggling
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

    # Advanced Chart Processing Matrix
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

    # Core Metric Mapping Interface
    st.markdown("### 🔍 Accumulation Metrics")
    sc1, sc2 = st.columns(2)
    sc1.markdown(f"<div style='background-color:#0F1626; padding:12px; border-radius:8px; border-left:4px solid #00E676;'>🟢 Bullish Engine Momentum: <b style='color:#00E676; font-family:JetBrains Mono;'>{result['buy_score']}/100</b></div>", unsafe_allow_html=True)
    sc2.markdown(f"<div style='background-color:#0F1626; padding:12px; border-radius:8px; border-left:4px solid #FF1744;'>🔴 Bearish Distribution Weight: <b style='color:#FF1744; font-family:JetBrains Mono;'>{result['sell_score']}/100</b></div>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    color_hex = "#FFFFFF"
    if "BUY" in result["signal"]: color_hex = "#00E676"
    elif "SELL" in result["signal"]: color_hex = "#FF1744"
        
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
    elif "NEUTRAL" in current_result["signal"]:
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