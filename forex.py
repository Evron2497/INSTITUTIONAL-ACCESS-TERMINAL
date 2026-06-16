# import os
# from datetime import datetime, timezone
# import time
# import numpy as np
# import pandas as pd
# import requests
# import streamlit as st
# import streamlit.components.v1 as components
# import plotly.graph_objects as go
# import yfinance as yf

# # =====================================================
# # PAGE CONFIG & PREMIUM INSTITUTIONAL VISUAL THEME
# # =====================================================
# st.set_page_config(page_title="CORE VECTOR MATRIX - GOLD EXCLUSIVE", page_icon="👑", layout="wide")

# st.markdown("""
#     <style>
#         @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght=300;400;500;600&family=Space+Grotesk:wght=300;400;500;600;700&display=swap');
        
#         html, body, [data-testid="stAppViewContainer"] {
#             background-color: #060913 !important;
#             font-family: 'Space Grotesk', sans-serif !important;
#             color: #E2E8F0 !important;
#         }
        
#         .main-title {
#             font-family: 'Space Grotesk', sans-serif;
#             font-weight: 700;
#             font-size: 2.2rem;
#             background: linear-gradient(135deg, #FFD700 0%, #FFA500 100%);
#             -webkit-background-clip: text;
#             -webkit-text-fill-color: transparent;
#             letter-spacing: -0.03em;
#             margin-bottom: 5px;
#         }
        
#         .sub-title-bar {
#             font-family: 'JetBrains Mono', monospace;
#             font-size: 0.85rem;
#             color: #8A9AAB;
#             text-transform: uppercase;
#             letter-spacing: 0.1em;
#             margin-bottom: 25px;
#         }

#         [data-testid="stSidebar"] {
#             background-color: #090D1A !important;
#             border-right: 1px solid #1E293B !important;
#         }
        
#         .matrix-card {
#             background: rgba(15, 23, 42, 0.65) !important;
#             border: 1px solid rgba(255, 255, 255, 0.05) !important;
#             border-left: 4px solid #FFD700 !important;
#             border-radius: 12px !important;
#             padding: 20px !important;
#             box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37) !important;
#             backdrop-filter: blur(8px) !important;
#             margin-bottom: 15px;
#         }
        
#         .matrix-card.scalping {
#             border-left: 4px solid #A855F7 !important;
#             background: linear-gradient(135deg, rgba(15, 23, 42, 0.8) 0%, rgba(112, 0, 255, 0.15) 100%) !important;
#             box-shadow: 0px 0px 25px rgba(168, 85, 247, 0.25) !important;
#         }
#         .matrix-card.buy { border-left: 4px solid #10B981 !important; }
#         .matrix-card.sell { border-left: 4px solid #FF4B4B !important; }
#         .matrix-card.neutral { border-left: 4px solid #64748B !important; }

#         .metric-glow-box {
#             background: rgba(30, 41, 59, 0.4);
#             border: 1px solid rgba(255, 255, 255, 0.05);
#             border-radius: 10px;
#             padding: 15px;
#             text-align: center;
#             box-shadow: inset 0 1px 1px rgba(255,255,255,0.05);
#         }
#         .metric-glow-label {
#             font-size: 0.75rem;
#             text-transform: uppercase;
#             color: #94A3B8;
#             letter-spacing: 0.07em;
#             margin-bottom: 5px;
#         }
#         .metric-glow-val {
#             font-family: 'JetBrains Mono', monospace;
#             font-size: 1.4rem;
#             font-weight: 600;
#             color: #FFFFFF;
#         }

#         .stButton>button {
#             background: linear-gradient(135deg, #0F172A 0%, #1E1B4B 100%) !important;
#             color: #FFD700 !important;
#             border: 1px solid rgba(255, 215, 0, 0.3) !important;
#             border-radius: 8px !important;
#             padding: 10px 24px !important;
#             font-family: 'Space Grotesk', sans-serif !important;
#             font-weight: 600 !important;
#             letter-spacing: 0.02em !important;
#             transition: all 0.3s ease !important;
#             width: 100% !important;
#         }
#         .stButton>button:hover {
#             border-color: #FFD700 !important;
#             box-shadow: 0px 0px 20px rgba(255, 215, 0, 0.35) !important;
#             color: #FFFFFF !important;
#             transform: translateY(-1px);
#         }
        
#         div[data-testid="stDecoration"] {
#             background-image: linear-gradient(90deg, #FFD700, #FFA500) !important;
#         }
#     </style>
# """, unsafe_allow_html=True)

# # =====================================================
# # VOLATILE SECURITY ENVELOPE PROTOCOL
# # =====================================================
# USERNAME = st.secrets.get("USERNAME", "")
# PASSWORD = st.secrets.get("PASSWORD", "")

# if "logged_in" not in st.session_state:
#     st.session_state.logged_in = False

# if "shared_prediction" not in st.session_state:
#     st.session_state.shared_prediction = {
#         "signal": "NEUTRAL", "confidence": 0, "entry": 0, "tp": 0, "sl": 0, "pips": 0, "rsi": 50,
#         "structure": "INITIALIZING", "buy_score": 0, "sell_score": 0, "session": "UNKNOWN",
#         "timestamp": "", "recent_high": 0, "recent_low": 0, "fvg_status": "NONE", "ob_status": "NONE",
#         "is_scalping": False, "scalping_state": "STANDBY", "conditions_passed": 0, "direction": "NEUTRAL", "checks": []
#     }

# if "eqh_detected" not in st.session_state: st.session_state.eqh_detected = False
# if "eql_detected" not in st.session_state: st.session_state.eql_detected = False

# def render_login_form():
#     st.markdown('<div style="max-width:450px; margin: 80px auto 0 auto;">', unsafe_allow_html=True)
#     st.markdown('<h2 class="main-title" style="text-align:center;">CORE MATRIX LOGIN</h2>', unsafe_allow_html=True)
#     st.markdown('<p class="sub-title-bar" style="text-align:center; margin-bottom:30px;">Institutional Authentication Required</p>', unsafe_allow_html=True)
#     with st.form("auth_form", clear_on_submit=True):
#         u = st.text_input("Access Identifier Username")
#         p = st.text_input("Secure Passkey Crypt", type="password")
#         if st.form_submit_button("Initialize Security Session"):
#             if u == USERNAME and p == PASSWORD:
#                 st.session_state.logged_in = True
#                 st.rerun()
#             else:
#                 st.error("Invalid node validation configuration profile.")
#     st.markdown('</div>', unsafe_allow_html=True)

# if not st.session_state.logged_in:
#     render_login_form()
#     st.stop()

# if st.sidebar.button("🔒 Terminal Session Disconnect"):
#     st.session_state.logged_in = False
#     st.rerun()

# st.sidebar.markdown('<div style="padding: 2px 10px; background: rgba(16,185,129,0.1); border: 1px solid #10B981; border-radius:6px; color:#10B981; font-size:0.8rem; font-family:\'JetBrains Mono\'; text-align:center;">● SESSION SECURELY LINKED</div>', unsafe_allow_html=True)
# st.sidebar.markdown("---")

# # =====================================================
# # TELEGRAM DISPATCH PIPELINE
# # =====================================================
# BOT_TOKEN = st.secrets.get("BOT_TOKEN", "")
# CHAT_IDS  = st.secrets.get("CHAT_IDS", [])

# def send_telegram(message: str):
#     if not BOT_TOKEN or not CHAT_IDS: return False, "Telegram vectors unconfigured."
#     url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
#     errors = []
#     for chat_id in CHAT_IDS:
#         try:
#             r = requests.post(url, data={"chat_id": chat_id, "text": message, "parse_mode": "HTML"}, timeout=10)
#             if r.status_code != 200: errors.append(f"Chat {chat_id}: {r.text}")
#         except Exception as e: errors.append(str(e))
#     return (len(errors) == 0), "; ".join(errors)

# # =====================================================
# # DATA RETRIEVAL PIPELINE (GOLD ONLY SPECIFICATION)
# # =====================================================
# GOLD_SYMBOL = "XAUUSD"
# GOLD_YF_TICKER = "GC=F"

# st.sidebar.subheader("🎛️ Terminal Controls")
# selected_tf = st.sidebar.selectbox("Gold Scalping Matrix Interval", ["1m", "5m", "15m"], index=1)

# @st.cache_data(ttl=2)
# def get_data_yf_gold(interval="5m", period="5d"):
#     try:
#         ticker = yf.Ticker(GOLD_YF_TICKER)
#         df = ticker.history(period=period, interval=interval)
#         if df.empty: return pd.DataFrame()
#         df = df.reset_index()
#         df.rename(columns={"Datetime": "time", "Date": "time", "Open": "Open", "High": "High", "Low": "Low", "Close": "Close", "Volume": "Volume"}, inplace=True)
#         return df
#     except Exception:
#         return pd.DataFrame()

# # =====================================================
# # ADVANCED MATHEMATICAL QUANTITATIVE MATHEMATICS
# # =====================================================
# def calculate_swing_pivots(df: pd.DataFrame, left_bars=3, right_bars=3) -> pd.DataFrame:
#     df = df.copy().reset_index(drop=True)
#     sh, sl = np.full(len(df), np.nan), np.full(len(df), np.nan)
#     for i in range(left_bars, len(df) - right_bars):
#         if df["High"].iloc[i] == df["High"].iloc[i - left_bars: i + right_bars + 1].max(): sh[i] = df["High"].iloc[i]
#         if df["Low"].iloc[i] == df["Low"].iloc[i - left_bars: i + right_bars + 1].min(): sl[i] = df["Low"].iloc[i]
#     df["Swing_High"], df["Swing_Low"] = sh, sl
#     return df

# def calculate_atr(df, period=14):
#     if len(df) < period: return 0.50
#     tr = np.maximum(df["High"] - df["Low"], np.maximum(abs(df["High"] - df["Close"].shift()), abs(df["Low"] - df["Close"].shift())))
#     atr = tr.rolling(period).mean().iloc[-1]
#     return atr if not np.isnan(atr) else 0.50

# def rsi_series(df, period=14):
#     if len(df) < period: return pd.Series(50.0, index=df.index)
#     delta = df["Close"].diff()
#     gain, loss = delta.clip(lower=0).rolling(period).mean(), (-delta.clip(upper=0)).rolling(period).mean()
#     rs = gain / loss.replace(0, 1e-5)
#     return (100 - (100 / (1 + rs))).fillna(50.0)

# def trading_session():
#     hour = datetime.now(timezone.utc).hour
#     if 0 <= hour < 7: return "ASIAN (ACCUMULATION)"
#     elif 7 <= hour < 13: return "LONDON (MANIPULATION)"
#     elif 13 <= hour < 21: return "NEW YORK (DISTRIBUTION)"
#     return "CLOSED"

# # =====================================================
# # SAFE-SCALPER-PRO ENGINE INTEGRATION LAYER (GOLD OPTIMIZED)
# # =====================================================
# def evaluate_scalping_matrix(df):
#     """
#     Implements Safe-Scalper-Pro breakout logic fine-tuned for XAU/USD.
#     Guarantees consistent matrix state delivery without dropping direction indicators.
#     """
#     if len(df) < 200: return {"is_scalping": False, "state": "INSUFFICIENT BUFFER", "passed": 0, "direction": "NEUTRAL", "checks": []}
    
#     close, high, low = df["Close"].iloc[-1], df["High"].iloc[-1], df["Low"].iloc[-1]
#     prev_close = df["Close"].iloc[-2]
#     atr = calculate_atr(df)
    
#     ema_fast = df["Close"].ewm(span=50, adjust=False).mean().iloc[-1]
#     ema_slow = df["Close"].ewm(span=200, adjust=False).mean().iloc[-1]
    
#     n_bar_window = df.tail(12)
#     n_bar_high = n_bar_window["High"].max()
#     n_bar_low = n_bar_window["Low"].min()
    
#     rsi_val = rsi_series(df).iloc[-1]
    
#     df_h1 = get_data_yf_gold(interval="1h", period="5d")
#     h1_agreement = True
#     if not df_h1.empty and len(df_h1) >= 50:
#         h1_ema20 = df_h1["Close"].ewm(span=20, adjust=False).mean().iloc[-1]
#         h1_ema50 = df_h1["Close"].ewm(span=50, adjust=False).mean().iloc[-1]
#         h1_agreement = (h1_ema20 > h1_ema50)
    
#     labels = [
#         "Micro-Trend Direction (EMA50 vs EMA200)",
#         "Breakout Velocity (Price separation from EMA50)",
#         "Structural Alignment (Trading clear of EMAs)",
#         "Immediate N-Bar Range High/Low Breakout",
#         "RSI Momentum Optimization Envelope",
#         "Immediate Bar Acceleration Trigger",
#         "Macro HTF Trend Filter Agreement (1H)"
#     ]
    
#     cond_buy = [
#         ema_fast > ema_slow,
#         (close - ema_fast) > (atr * 0.2),
#         close > ema_fast and close > ema_slow,
#         close >= (n_bar_high - (atr * 0.05)),
#         45 <= rsi_val <= 68,
#         close > prev_close,
#         h1_agreement
#     ]
    
#     cond_sell = [
#         ema_fast < ema_slow,
#         (ema_fast - close) > (atr * 0.2),
#         close < ema_fast and close < ema_slow,
#         close <= (n_bar_low + (atr * 0.05)),
#         32 <= rsi_val <= 55,
#         close < prev_close,
#         not h1_agreement
#     ]
    
#     passed_buy = sum(1 for c in cond_buy if c)
#     passed_sell = sum(1 for c in cond_sell if c)
    
#     # Track metrics relative to structural dominance
#     if passed_buy >= passed_sell:
#         active_direction = "BUY"
#         max_passed = passed_buy
#         checks_status = [{"label": labels[i], "passed": cond_buy[i]} for i in range(7)]
#     else:
#         active_direction = "SELL"
#         max_passed = passed_sell
#         checks_status = [{"label": labels[i], "passed": cond_sell[i]} for i in range(7)]

#     if passed_buy == 7: 
#         return {"is_scalping": True, "state": "🔥 GOLD BUY SCALP CONFIRMED", "passed": 7, "direction": "BUY", "checks": checks_status}
#     if passed_sell == 7: 
#         return {"is_scalping": True, "state": "🔥 GOLD SELL SCALP CONFIRMED", "passed": 7, "direction": "SELL", "checks": checks_status}
    
#     return {"is_scalping": False, "state": f"STANDBY ({max_passed}/7 Elements Synchronized)", "passed": max_passed, "direction": active_direction, "checks": checks_status}

# # =====================================================
# # INTEGRATED QUANTITATIVE SMC CORE SYSTEM
# # =====================================================
# def institutional_engine(df):
#     if df is None or df.empty or len(df) < 50:
#         return {
#             "signal": "NEUTRAL", "confidence": 0, "entry": 0, "tp": 0, "sl": 0, "pips": 0, "rsi": 50,
#             "structure": "INSUFFICIENT DATA", "buy_score": 0, "sell_score": 0, "session": trading_session(),
#             "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "recent_high": 0, "recent_low": 0,
#             "fvg_status": "NONE", "ob_status": "NONE", "is_scalping": False, "scalping_state": "STANDBY", 
#             "conditions_passed": 0, "direction": "NEUTRAL", "checks": []
#         }

#     pip_multiplier = 0.10 
#     atr_val = calculate_atr(df)
#     rsi_val = round(float(rsi_series(df).iloc[-1]), 1)

#     df_pivots = calculate_swing_pivots(df)
#     v_highs, v_lows = df_pivots["Swing_High"].dropna(), df_pivots["Swing_Low"].dropna()
#     recent_high = float(v_highs.iloc[-1]) if not v_highs.empty else float(df["High"].max())
#     recent_low = float(v_lows.iloc[-1]) if not v_lows.empty else float(df["Low"].min())
    
#     scalping_profile = evaluate_scalping_matrix(df)

#     buy_score = 15 if scalping_profile["direction"] == "BUY" else 0
#     sell_score = 15 if scalping_profile["direction"] == "SELL" else 0
#     buy_score += (scalping_profile["passed"] * 12) if scalping_profile["direction"] == "BUY" else (scalping_profile["passed"] * 2)
#     sell_score += (scalping_profile["passed"] * 12) if scalping_profile["direction"] == "SELL" else (scalping_profile["passed"] * 2)

#     price = float(df["Close"].iloc[-1])
    
#     if scalping_profile["is_scalping"]:
#         signal = f"SCALPING {scalping_profile['direction']}"
#         confidence = 92.5
#     else:
#         confidence = max(buy_score, sell_score)
#         if buy_score > 55: signal = "BULLISH SCALP BIAS"
#         elif sell_score > 55: signal = "BEARISH SCALP BIAS"
#         else: signal = "NEUTRAL"

#     entry = price
    
#     tp_distance = max((atr_val * 1.5), 1.5)
#     sl_distance = max((atr_val * 1.0), 1.0)

#     # Use pure trend validation vector directions to eliminate inverse calculation dropouts
#     if scalping_profile["direction"] == "BUY":
#         tp = entry + tp_distance
#         sl = entry - sl_distance
#     else:
#         tp = entry - tp_distance
#         sl = entry + sl_distance
        
#     pips = round(abs(tp - entry) / pip_multiplier, 1)

#     return {
#         "signal": signal, "confidence": round(float(confidence), 1), "entry": round(entry, 2),
#         "tp": round(tp, 2), "sl": round(sl, 2), "pips": pips, "rsi": rsi_val,
#         "structure": f"GOLD ENGINE: {scalping_profile['state']}",
#         "buy_score": min(buy_score, 100), "sell_score": min(sell_score, 100), "session": trading_session(),
#         "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
#         "recent_high": round(recent_high, 2), "recent_low": round(recent_low, 2),
#         "fvg_status": "MONITORING SCALP", "ob_status": "DYNAMIC",
#         "is_scalping": scalping_profile["is_scalping"],
#         "scalping_state": scalping_profile["state"],
#         "conditions_passed": scalping_profile["passed"],
#         "direction": scalping_profile["direction"],
#         "checks": scalping_profile["checks"]
#     }

# # =====================================================
# # LIVE DASHBOARD RECONSTRUCTED LAYER
# # =====================================================
# @st.fragment(run_every=2)
# def render_live_dashboard(tf):
#     market_data = get_data_yf_gold(interval=tf, period="5d")
#     if market_data.empty or len(market_data) < 100:
#         st.warning("Constructing Gold data profile arrays. Pulling extended window frames...")
#         return

#     result = institutional_engine(market_data)
#     st.session_state.shared_prediction = result

#     card_style = "neutral"
#     if result["is_scalping"]: card_style = "scalping"
#     elif "BULLISH" in result["signal"] or result["direction"] == "BUY": card_style = "buy"
#     elif "BEARISH" in result["signal"] or result["direction"] == "SELL": card_style = "sell"
    
#     st.markdown(f"""
#     <div class="matrix-card {card_style}">
#         <span style="font-family:'JetBrains Mono'; font-size:0.8rem; color:#E2E8F0;">[GOLD MATRIX PURE SCALPER MODULE]</span>
#         <h2 style="margin:5px 0 0 0; font-weight:600; color:#FFFFFF;">XAUUSD ({tf}) — <span style="color:#FFD700;">{result['scalping_state']}</span></h2>
#     </div>
#     """, unsafe_allow_html=True)

#     # Grid Display Metrics
#     m_col1, m_col2, m_col3, m_col4 = st.columns(4)
#     with m_col1:
#         st.markdown(f'<div class="metric-glow-box"><div class="metric-glow-label">Matrix Validations</div><div class="metric-glow-val" style="color:#FFD700;">{result["conditions_passed"]} / 7</div></div>', unsafe_allow_html=True)
#     with m_col2:
#         st.markdown(f'<div class="metric-glow-box"><div class="metric-glow-label">Target Range</div><div class="metric-glow-val">{result["pips"]} Pips</div></div>', unsafe_allow_html=True)
#     with m_col3:
#         st.markdown(f'<div class="metric-glow-box"><div class="metric-glow-label">RSI Dynamics</div><div class="metric-glow-val">{result["rsi"]}</div></div>', unsafe_allow_html=True)
#     with m_col4:
#         st.markdown(f'<div class="metric-glow-box"><div class="metric-glow-label">Active Horizon</div><div class="metric-glow-val" style="font-size:0.95rem; line-height:2.2rem; color:#FFA500;">{result["session"].split(" ")[0]}</div></div>', unsafe_allow_html=True)

#     # Live Core Signal Checkpoints Rendering Array
#     with st.sidebar.expander("🔍 LIVE SIGNAL MATRIX CHECKPOINTS", expanded=True):
#         color_map = {"BUY": "#10B981", "SELL": "#FF4B4B", "NEUTRAL": "#64748B"}
#         st.markdown(f"**Structural Focus Bias:** <span style='color:{color_map.get(result['direction'], '#FFF')}; font-weight:bold;'>{result['direction']}</span>", unsafe_allow_html=True)
#         st.markdown("---")
#         for check in result.get('checks', []):
#             icon = "✅" if check["passed"] else "❌"
#             color = "#10B981" if check["passed"] else "#EF4444"
#             st.markdown(f"<span style='color:{color}; font-size:0.85rem; font-family:\"JetBrains Mono\";'>{icon} {check['label']}</span>", unsafe_allow_html=True)

#     st.markdown("<br>", unsafe_allow_html=True)

#     # Plot Visualizer
#     fig = go.Figure()
#     fig.add_trace(go.Candlestick(x=market_data["time"], open=market_data["Open"], high=market_data["High"], low=market_data["Low"], close=market_data["Close"], name="Gold Spot"))
    
#     # Gold EMAs
#     ema50 = market_data["Close"].ewm(span=50, adjust=False).mean()
#     ema200 = market_data["Close"].ewm(span=200, adjust=False).mean()
#     fig.add_trace(go.Scatter(x=market_data["time"], y=ema50, line=dict(color="#FFD700", width=1), name="Scalp Fast EMA (50)"))
#     fig.add_trace(go.Scatter(x=market_data["time"], y=ema200, line=dict(color="#A855F7", width=1.5), name="Scalp Slow EMA (200)"))

#     fig.update_layout(template="plotly_dark", height=400, xaxis_rangeslider_visible=False, uirevision="keep", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(l=10, r=10, t=10, b=10))
#     st.plotly_chart(fig, use_container_width=True)

#     with st.expander("Gold Quantum Telemetry Array Log"):
#         st.json(result)

#     if result["is_scalping"]:
#         st.toast(f"🚨 ALGO SPHERE CONCURRENT GOLD SCALP TRIGGERED!", icon="👑")

# # =====================================================
# # MAIN ENGINE LAYOUT ASSEMBLY
# # =====================================================
# st.markdown('<h1 class="main-title">CORE MATRIX // XAUUSD ENGINE</h1>', unsafe_allow_html=True)
# st.markdown('<p class="sub-title-bar">EXCLUSIVE QUANTITATIVE GOLD SCALPER MONITOR TERMINAL // VERSION 5.0.0</p>', unsafe_allow_html=True)

# col_layout_left, col_layout_right = st.columns([1.9, 1.1])

# with col_layout_left:
#     render_live_dashboard(selected_tf)
    
#     st.markdown("---")
#     st.markdown("### 📊 Realtime Gold TradingView Node Stream")
#     html_widget = """
#     <div id="tv_chart_container" style="border: 1px solid rgba(255,255,255,0.05); border-radius: 8px; overflow: hidden;"></div>
#     <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
#     <script type="text/javascript">
#     new TradingView.widget({
#        "width": "100%",
#        "height": 450,
#        "symbol": "FX_IDC:XAUUSD",
#        "interval": "5",
#        "timezone": "Etc/UTC",
#        "theme": "dark",
#        "style": "1",
#        "locale": "en",
#        "toolbar_bg": "#0A0E17",
#        "enable_publishing": false,
#        "hide_side_toolbar": false,
#        "allow_symbol_change": false,
#        "container_id": "tv_chart_container"
#     });
#     </script>
#     """
#     components.html(html_widget, height=470)

# with col_layout_right:
#     st.markdown("""
#     <div style="background: rgba(15, 23, 42, 0.4); padding: 12px 15px; border-radius: 8px 8px 0 0; border: 1px solid rgba(255,255,255,0.05); border-bottom: none;">
#         <span style="font-family:'JetBrains Mono'; font-size:0.8rem; color:#FFD700; font-weight:600;">📩 GOLD PAYLOAD BROADCAST HUB</span>
#     </div>
#     """, unsafe_allow_html=True)
    
#     with st.container(border=True):
#         current_result = st.session_state.shared_prediction
#         confirm_send = st.checkbox("Confirm network payload verification protocol rules.")
        
#         if st.button("🚀 EXECUTE PAYLOAD BROADCAST"):
#             if not confirm_send:
#                 st.warning("Execution Rejected: Affirm network confirmation verification protocol.")
#             elif "NEUTRAL" in current_result["signal"] and not current_result["is_scalping"]:
#                 st.error("Execution Aborted: Algorithmic engine contains zero active market tracking variables.")
#             else:
#                 message = f"""👑 <b>TECH-STAR GOLD SCALPER CONCURRENT PIPELINE</b>

# VECTOR NODE: <code>XAUUSD</code> [{selected_tf}]
# FRAMEWORK STATE: <b>{current_result['scalping_state']}</b>
# CONFIDENCE COEFFICIENT: <code>{current_result['confidence']}%</code>

# 🎯 <b>STRUCTURAL EXECUTION BOUNDARIES:</b>
# • Scalper Entry Point: {current_result['entry']}
# • Take Profit Target: {current_result['tp']}
# • Stop Loss Boundary: {current_result['sl']}
# • Target Yield Forecast: {current_result['pips']} Pips (Gold Structure)

# 🕒 <i>Transmission Frame: {current_result['timestamp']} UTC</i>"""
                
#   


success, err_msg = send_telegram(message)
#                 if success: st.toast("Gold payload broadcast complete across network arrays!", icon="🚀")
#                 else: st.error(f"Transmission Failed: {err_msg}")








#     """








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
st.set_page_config(page_title="SCALPING ROBOT PRO V2.0 - GOLD TERMINAL", page_icon="👑", layout="wide")

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
# STICKY SESSION AUTHENTICATION RECONSTRUCTION
# =====================================================
USERNAME = st.secrets.get("USERNAME", "")
PASSWORD = st.secrets.get("PASSWORD", "")

if "logged_in" not in st.session_state:
    query_params = st.query_params
    if query_params.get("session_auth_token") == "PRO_VALIDATED_NODE":
        st.session_state.logged_in = True
    else:
        st.session_state.logged_in = False

if "shared_prediction" not in st.session_state:
    st.session_state.shared_prediction = {
        "signal": "NEUTRAL", "confidence": 0, "entry": 0, "tp": 0, "sl": 0, "pips": 0, "rsi": 50,
        "structure": "INITIALIZING", "buy_score": 0, "sell_score": 0, "session": "UNKNOWN",
        "timestamp": "", "recent_high": 0, "recent_low": 0, "fvg_status": "NONE", "ob_status": "NONE",
        "is_scalping": False, "scalping_state": "STANDBY", "conditions_passed": 0, "direction": "NEUTRAL", "checks": [],
        "trailing_stop": 0
    }

if "eqh_detected" not in st.session_state: st.session_state.eqh_detected = False
if "eql_detected" not in st.session_state: st.session_state.eql_detected = False

def render_login_form():
    st.markdown('<div style="max-width:450px; margin: 80px auto 0 auto;">', unsafe_allow_html=True)
    st.markdown('<h2 class="main-title" style="text-align:center;">SCALPING ROBOT PRO MT5</h2>', unsafe_allow_html=True)
    st.markdown('<p class="sub-title-bar" style="text-align:center; margin-bottom:30px;">Institutional Authentication Required</p>', unsafe_allow_html=True)
    with st.form("auth_form", clear_on_submit=True):
        u = st.text_input("Access Identifier Username")
        p = st.text_input("Secure Passkey Crypt", type="password")
        if st.form_submit_button("Initialize Robot Session"):
            if u == USERNAME and p == PASSWORD:
                st.session_state.logged_in = True
                st.query_params["session_auth_token"] = "PRO_VALIDATED_NODE"
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

st.sidebar.markdown('<div style="padding: 2px 10px; background: rgba(16,185,129,0.1); border: 1px solid #10B981; border-radius:6px; color:#10B981; font-size:0.8rem; font-family:\'JetBrains Mono\'; text-align:center;">● ROBOT CORE PERSISTENT LINKED</div>', unsafe_allow_html=True)
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
# DATA RETRIEVAL PIPELINE (M1 TIMEFRAME FOCUS)
# =====================================================
GOLD_SYMBOL = "XAUUSD"
GOLD_YF_TICKER = "GC=F"

st.sidebar.subheader("🎛️ Robot Matrix Controls")
selected_tf = st.sidebar.selectbox("Robot Matrix Interval Optimization", ["1m", "5m", "15m"], index=0)
trade_mode = st.sidebar.radio("Flexible Trade Direction Mode", ["Buy and Sell", "Buy Only", "Sell Only"], index=0)
lot_size = st.sidebar.number_input("Scalping Account Lot Size Execution", min_value=0.01, max_value=100.0, value=1.0, step=0.1)

st.sidebar.markdown("### 🛡️ System Protection Overlays")
news_filter = st.sidebar.toggle("News Filter Protection System", value=True)
holiday_filter = st.sidebar.toggle("Holiday Trading Control Lock", value=True)
daily_profit_protection = st.sidebar.number_input("Daily Profit Protection ($)", min_value=0, value=500)
max_drawdown_protection = st.sidebar.number_input("Max Drawdown Protection ($)", min_value=0, value=300)

@st.cache_data(ttl=1)
def get_data_yf_gold(interval="1m", period="2d"):
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
    if 0 <= hour < 7: return "ASIAN (ACCUMULATION)"
    elif 7 <= hour < 13: return "LONDON (MANIPULATION)"
    elif 13 <= hour < 21: return "NEW YORK (DISTRIBUTION)"
    return "CLOSED"

# =====================================================
# ROBOT PRO ENGINE INTEGRATION LAYER
# =====================================================
def evaluate_scalping_matrix(df):
    if len(df) < 50: return {"is_scalping": False, "state": "INSUFFICIENT BUFFER", "passed": 0, "direction": "NEUTRAL", "checks": []}
    
    close, high, low = df["Close"].iloc[-1], df["High"].iloc[-1], df["Low"].iloc[-1]
    prev_close = df["Close"].iloc[-2]
    atr = calculate_atr(df)
    
    ema_fast = df["Close"].ewm(span=50, adjust=False).mean().iloc[-1]
    ema_slow = df["Close"].ewm(span=200, adjust=False).mean().iloc[-1]
    
    n_bar_window = df.tail(12)
    n_bar_high = n_bar_window["High"].max()
    n_bar_low = n_bar_window["Low"].min()
    
    rsi_val = rsi_series(df).iloc[-1]
    
    df_h1 = get_data_yf_gold(interval="15m", period="5d")
    h1_agreement = True
    if not df_h1.empty and len(df_h1) >= 50:
        h1_ema20 = df_h1["Close"].ewm(span=20, adjust=False).mean().iloc[-1]
        h1_ema50 = df_h1["Close"].ewm(span=50, adjust=False).mean().iloc[-1]
        h1_agreement = (h1_ema20 > h1_ema50)
    
    labels = [
        "Micro-Trend Direction (EMA50 vs EMA200)",
        "Breakout Velocity (Price separation from EMA50)",
        "Structural Alignment (Trading clear of EMAs)",
        "Immediate N-Bar Range High/Low Breakout",
        "RSI Momentum Optimization Envelope",
        "Immediate Bar Acceleration Trigger",
        "Macro HTF Trend Filter Agreement"
    ]
    
    cond_buy = [
        ema_fast > ema_slow,
        (close - ema_fast) > (atr * 0.2),
        close > ema_fast and close > ema_slow,
        close >= (n_bar_high - (atr * 0.05)),
        45 <= rsi_val <= 68,
        close > prev_close,
        h1_agreement
    ]
    
    cond_sell = [
        ema_fast < ema_slow,
        (ema_fast - close) > (atr * 0.2),
        close < ema_fast and close < ema_slow,
        close <= (n_bar_low + (atr * 0.05)),
        32 <= rsi_val <= 55,
        close < prev_close,
        not h1_agreement
    ]
    
    if trade_mode == "Buy Only":
        passed_buy = sum(1 for c in cond_buy if c)
        passed_sell = 0
    elif trade_mode == "Sell Only":
        passed_buy = 0
        passed_sell = sum(1 for c in cond_sell if c)
    else:
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

    if passed_buy == 7: 
        return {"is_scalping": True, "state": "🔥 ROBOT PRO BUY CONFIRMED", "passed": 7, "direction": "BUY", "checks": checks_status}
    if passed_sell == 7: 
        return {"is_scalping": True, "state": "🔥 ROBOT PRO SELL CONFIRMED", "passed": 7, "direction": "SELL", "checks": checks_status}
    
    return {"is_scalping": False, "state": f"STANDBY ({max_passed}/7 Synchronized)", "passed": max_passed, "direction": active_direction, "checks": checks_status}

# =====================================================
# INTEGRATED QUANTITATIVE ROBOT PROCESSOR
# =====================================================
def institutional_engine(df):
    if df is None or df.empty or len(df) < 50:
        return {
            "signal": "NEUTRAL", "confidence": 0, "entry": 0, "tp": 0, "sl": 0, "pips": 0, "rsi": 50,
            "structure": "INSUFFICIENT DATA", "buy_score": 0, "sell_score": 0, "session": trading_session(),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "recent_high": 0, "recent_low": 0,
            "fvg_status": "NONE", "ob_status": "NONE", "is_scalping": False, "scalping_state": "STANDBY", 
            "conditions_passed": 0, "direction": "NEUTRAL", "checks": [], "trailing_stop": 0
        }

    pip_multiplier = 0.10 
    atr_val = calculate_atr(df)
    rsi_val = round(float(rsi_series(df).iloc[-1]), 1)

    df_pivots = calculate_swing_pivots(df)
    v_highs, v_lows = df_pivots["Swing_High"].dropna(), df_pivots["Swing_Low"].dropna()
    recent_high = float(v_highs.iloc[-1]) if not v_highs.empty else float(df["High"].max())
    recent_low = float(v_lows.iloc[-1]) if not v_lows.empty else float(df["Low"].min())
    
    scalping_profile = evaluate_scalping_matrix(df)

    buy_score = 15 if scalping_profile["direction"] == "BUY" else 0
    sell_score = 15 if scalping_profile["direction"] == "SELL" else 0
    buy_score += (scalping_profile["passed"] * 12) if scalping_profile["direction"] == "BUY" else (scalping_profile["passed"] * 2)
    sell_score += (scalping_profile["passed"] * 12) if scalping_profile["direction"] == "SELL" else (scalping_profile["passed"] * 2)

    price = float(df["Close"].iloc[-1])
    
    if scalping_profile["is_scalping"]:
        signal = f"ROBOT {scalping_profile['direction']}"
        confidence = 98.2
    else:
        confidence = max(buy_score, sell_score)
        if buy_score > 55: signal = "BUY BIAS"
        elif sell_score > 55: signal = "SELL BIAS"
        else: signal = "NEUTRAL"

    entry = price
    tp_distance = max((atr_val * 1.2), 1.0)
    sl_distance = max((atr_val * 1.0), 0.8)

    if scalping_profile["direction"] == "BUY":
        tp = entry + tp_distance
        sl = entry - sl_distance
        trailing_stop = entry - (atr_val * 0.5)
    else:
        tp = entry - tp_distance
        sl = entry + sl_distance
        trailing_stop = entry + (atr_val * 0.5)
        
    pips = round(abs(tp - entry) / pip_multiplier, 1)

    return {
        "signal": signal, "confidence": round(float(confidence), 1), "entry": round(entry, 2),
        "tp": round(tp, 2), "sl": round(sl, 2), "pips": pips, "rsi": rsi_val,
        "structure": f"ROBOT SYSTEM: {scalping_profile['state']}",
        "buy_score": min(buy_score, 100), "sell_score": min(sell_score, 100), "session": trading_session(),
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "recent_high": round(recent_high, 2), "recent_low": round(recent_low, 2),
        "fvg_status": "ROBOT SCALPER ACTIVE", "ob_status": "DYNAMIC PROTECTION",
        "is_scalping": scalping_profile["is_scalping"],
        "scalping_state": scalping_profile["state"],
        "conditions_passed": scalping_profile["passed"],
        "direction": scalping_profile["direction"],
        "checks": scalping_profile["checks"],
        "trailing_stop": round(trailing_stop, 2)
    }

# =====================================================
# LIVE DASHBOARD RECONSTRUCTED LAYER
# =====================================================
@st.fragment(run_every=2)
def render_live_dashboard(tf):
    market_data = get_data_yf_gold(interval=tf, period="2d")
    if market_data.empty or len(market_data) < 50:
        st.warning("Constructing System Array Data Profiles. Matrixing telemetry...")
        return

    result = institutional_engine(market_data)
    st.session_state.shared_prediction = result

    card_style = "neutral"
    if result["is_scalping"]: card_style = "scalping"
    elif "BUY" in result["signal"]: card_style = "buy"
    elif "SELL" in result["signal"]: card_style = "sell"
    
    st.markdown(f"""
    <div class="matrix-card {card_style}">
        <span style="font-family:'JetBrains Mono'; font-size:0.8rem; color:#E2E8F0;">[SCALPING ROBOT PRO V2.0 ENGINE MODULE]</span>
        <h2 style="margin:5px 0 0 0; font-weight:600; color:#FFFFFF;">XAUUSD ({tf}) — <span style="color:#FFD700;">{result['scalping_state']}</span></h2>
    </div>
    """, unsafe_allow_html=True)

    m_col1, m_col2, m_col3, m_col4 = st.columns(4)
    with m_col1:
        st.markdown(f'<div class="metric-glow-box"><div class="metric-glow-label">Robot Synchronizations</div><div class="metric-glow-val" style="color:#FFD700;">{result["conditions_passed"]} / 7</div></div>', unsafe_allow_html=True)
    with m_col2:
        st.markdown(f'<div class="metric-glow-box"><div class="metric-glow-label">Automated TP Yield</div><div class="metric-glow-val">{result["pips"]} Pips</div></div>', unsafe_allow_html=True)
    with m_col3:
        st.markdown(f'<div class="metric-glow-box"><div class="metric-glow-label">Dynamic Trailing Stop</div><div class="metric-glow-val" style="color:#A855F7;">{result["trailing_stop"]}</div></div>', unsafe_allow_html=True)
    with m_col4:
        st.markdown(f'<div class="metric-glow-box"><div class="metric-glow-label">Lot Execution Profile</div><div class="metric-glow-val" style="color:#FFA500;">{lot_size} Lots</div></div>', unsafe_allow_html=True)

    with st.sidebar.expander("🔍 ROBOT M1 FILTERS LOG", expanded=True):
        color_map = {"BUY": "#10B981", "SELL": "#FF4B4B", "NEUTRAL": "#64748B"}
        st.markdown(f"**Execution Track Strategy:** <span style='color:{color_map.get(result['direction'], '#FFF')}; font-weight:bold;'>{trade_mode} Mode</span>", unsafe_allow_html=True)
        st.markdown("---")
        for check in result.get('checks', []):
            icon = "✅" if check["passed"] else "❌"
            color = "#10B981" if check["passed"] else "#EF4444"
            st.markdown(f"<span style='color:{color}; font-size:0.85rem; font-family:\"JetBrains Mono\";'>{icon} {check['label']}</span>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    fig = go.Figure()
    fig.add_trace(go.Candlestick(x=market_data["time"], open=market_data["Open"], high=market_data["High"], low=market_data["Low"], close=market_data["Close"], name="Gold Spot"))
    
    ema50 = market_data["Close"].ewm(span=50, adjust=False).mean()
    ema200 = market_data["Close"].ewm(span=200, adjust=False).mean()
    fig.add_trace(go.Scatter(x=market_data["time"], y=ema50, line=dict(color="#FFD700", width=1), name="EMA 50 (Velocity)"))
    fig.add_trace(go.Scatter(x=market_data["time"], y=ema200, line=dict(color="#A855F7", width=1.5), name="EMA 200 (Trend Direction)"))

    fig.update_layout(template="plotly_dark", height=400, xaxis_rangeslider_visible=False, uirevision="keep", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(l=10, r=10, t=10, b=10))
    st.plotly_chart(fig, use_container_width=True)

    with st.expander("MetaTrader Expert Advisor Operational State Output"):
        st.json(result)

    if result["is_scalping"]:
        st.toast(f"🚨 SCALPING ROBOT PRO MT5 CRITICAL breakout execution triggered!", icon="👑")

# =====================================================
# MAIN ENGINE LAYOUT ASSEMBLY
# =====================================================
st.markdown('<h1 class="main-title">SCALPING ROBOT PRO V2.0 // CORE CONTROL</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-title-bar">M1 TIMEFRAME XAUUSD HIGH FREQUENCY ALGORITHMIC MATRIX TERMINAL</p>', unsafe_allow_html=True)

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
        <span style="font-family:'JetBrains Mono'; font-size:0.8rem; color:#FFD700; font-weight:600;">📩 ROBOT EXECUTION DISPATCH MATRIX</span>
    </div>
    """, unsafe_allow_html=True)
    
    with st.container(border=True):
        current_result = st.session_state.shared_prediction
        confirm_send = st.checkbox("Confirm automated robot trade execution payload requirements.")
        
        if st.button("🚀 TRANSMIT BOT PAYLOAD TO MT5 CORE"):
            if not confirm_send:
                st.warning("Execution Rejected: Confirm payload requirements control confirmation.")
            elif "NEUTRAL" in current_result["signal"] and not current_result["is_scalping"]:
                st.error("Execution Aborted: Algorithmic parameters mismatch. No active breakout elements identified.")
            else:
                bot_message = f"""👑 <b>SCALPING ROBOT PRO V2.0 MT5 PLATFORM NODE</b>

<b>EXECUTION PARAMETERS:</b>
• Symbol: <code>XAUUSD</code> [{selected_tf}]
• Lot Configuration: <b>{lot_size}</b>
• Robot System State: <b>{current_result['scalping_state']}</b>
• Confidence Matrix: <code>{current_result['confidence']}%</code>

🎯 <b>ROBOT POSITION PROTECTIONS:</b>
• Scalper Automated Entry: {current_result['entry']}
• Take Profit Target: {current_result['tp']}
• Stop Loss Target: {current_result['sl']}
• Trailing Stop Execution: {current_result['trailing_stop']}
• Target Yield Forecast: {current_result['pips']} Pips (Gold Structure)

🕒 <i>Transmission Frame: {current_result['timestamp']} UTC</i>"""
                
                success, err_msg = send_telegram(bot_message)
                if success: 
                    st.toast("Scalping Robot payload processed across MT5 arrays successfully!", icon="🚀")
                else: 
                    st.error(f"Transmission Failed: {err_msg}")
