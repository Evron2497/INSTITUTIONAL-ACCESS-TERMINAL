# import os
# from datetime import datetime, timezone
# import time
# import json
# import numpy as np
# import pandas as pd
# import requests
# import streamlit as st
# import plotly.graph_objects as go
# import yfinance as yf
# import streamlit.components.v1 as components

# # =====================================================
# # SYSTEM DESIGN & ULTRA-DARK ARCHITECTURAL INTERFACE
# # =====================================================
# st.set_page_config(page_title="VECTOR MATRIX PRO", page_icon="🏦", layout="wide")
# st.markdown("""
# <style>  
#     @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;700&family=Space+Grotesk:wght@400;500;600;700&display=swap');  
      
#     html, body, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {  
#         background-color: #030712 !important;  
#         font-family: 'Space Grotesk', sans-serif !important;  
#         color: #F8FAFC !important;  
#     }  
      
#     .premium-card {  
#         background: linear-gradient(145deg, #0f172a 0%, #1e293b 100%);  
#         border: 1px solid #334155;  
#         border-radius: 12px;  
#         padding: 24px;  
#         box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.5), 0 10px 10px -5px rgba(0, 0, 0, 0.4);  
#         margin-bottom: 24px;  
#     }  
      
#     [data-testid="stSidebar"] {   
#         background-color: #090d16 !important;  
#         border-right: 1px solid #1e293b !important;  
#     }  
      
#     .terminal-header {   
#         font-family: 'Space Grotesk';   
#         font-weight: 700;   
#         letter-spacing: -0.05em;  
#         background: linear-gradient(90deg, #38BDF8 0%, #818CF8 100%);   
#         -webkit-background-clip: text;   
#         -webkit-text-fill-color: transparent;   
#     }  
      
#     .section-title {  
#         font-size: 1.15rem;  
#         font-weight: 600;  
#         color: #F1F5F9;  
#         border-left: 4px solid #38BDF8;  
#         padding-left: 10px;  
#         margin-bottom: 16px;  
#     }  
      
#     .custom-metric {  
#         background: #0b1329 !important;  
#         border: 1px solid #1e293b !important;  
#         border-radius: 8px !important;  
#         padding: 16px !important;  
#         text-align: left;  
#     }  
#     .metric-label {  
#         font-size: 0.75rem !important;  
#         text-transform: uppercase !important;  
#         color: #94A3B8 !important;  
#         font-weight: 600 !important;  
#         letter-spacing: 0.05em;  
#         margin-bottom: 6px;  
#     }  
#     .metric-value {  
#         font-size: 1.4rem !important;  
#         font-weight: 700 !important;  
#         font-family: 'JetBrains Mono', monospace !important;  
#     }  
      
#     .stButton>button {   
#         background: linear-gradient(90deg, #2563EB 0%, #4F46E5 100%) !important;   
#         color: #FFFFFF !important;   
#         font-weight: 600 !important;  
#         border: none !important;  
#         border-radius: 6px !important;   
#         padding: 12px 24px !important;  
#         transition: all 0.2s ease !important;  
#         box-shadow: 0 4px 6px -1px rgba(37, 99, 235, 0.2) !important;  
#     }  
#     .stButton>button:hover {  
#         transform: translateY(-1px) !important;  
#         box-shadow: 0 10px 15px -3px rgba(37, 99, 235, 0.4) !important;  
#     }  
      
#     div[data-testid="stDataFrame"] {  
#         border: 1px solid #1e293b !important;  
#         border-radius: 8px !important;  
#         overflow: hidden;  
#     }  
      
#     .reasoning-box {  
#         background: rgba(15, 23, 42, 0.6);  
#         border: 1px dashed #475569;  
#         border-radius: 8px;  
#         padding: 16px;  
#         margin-top: 15px;  
#     }  
# </style>
# """, unsafe_allow_html=True)

# # =====================================================
# # GLOBAL CONFIGURATION & STATE INITIALIZATION
# # =====================================================
# pairs = ["EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "XAUUSD"]
# ticker_mapping = {
#     "EURUSD": "EURUSD=X", "GBPUSD": "GBPUSD=X",  
#     "USDJPY": "JPY=X", "AUDUSD": "AUDUSD=X", "XAUUSD": "GC=F"
# }

# if "global_market_registry" not in st.session_state:
#     st.session_state.global_market_registry = {  
#         p: {  
#             "df_ltf_slice": pd.DataFrame(),  
#             "metrics": {  
#                 "signal": "INITIALIZING MATRIX", "confidence": 0, "entry": 0, "tp": 0, "sl": 0,  
#                 "pips": 0, "rsi": 50, "structure": "ESTABLISHING CORE LINK", "buy_score": 0, "sell_score": 0,  
#                 "session": "UNKNOWN", "timestamp": "CALIBRATING FLOW", "recent_high": 0, "recent_low": 0,  
#                 "reasons": [], "fib_618": 0, "fib_786": 0
#             }  
#         } for p in pairs  
#     }

# if "last_signal" not in st.session_state:
#     st.session_state.last_signal = {p: None for p in pairs}

# # =====================================================
# # PERSISTENT SECURE IDENTITY GATEWAY (ANTI-REFRESH)
# # =====================================================
# USERNAME = st.secrets.get("USERNAME", "")
# PASSWORD = st.secrets.get("PASSWORD", "")

# if "logged_in" not in st.session_state:
#     if st.query_params.get("auth_session") == "active":  
#         st.session_state.logged_in = True  
#     else:  
#         st.session_state.logged_in = False

# def login_gate():
#     st.markdown('<div class="premium-card" style="max-width: 450px; margin: 100px auto 0px auto;">', unsafe_allow_html=True)  
#     st.markdown('<h2 class="terminal-header" style="font-size: 1.8rem; text-align: center; margin-bottom: 8px;">🏦 CORE SECURITY GATE</h2>', unsafe_allow_html=True)  
#     st.markdown('<p style="text-align: center; color: #94A3B8; margin-bottom: 24px; font-size: 0.9rem;">Institutional Verification Required</p>', unsafe_allow_html=True)  
      
#     u = st.text_input("Security ID Token / User Key", key="auth_user_input")  
#     p = st.text_input("Matrix Access Signature", type="password", key="auth_pass_input")  
      
#     st.markdown('<div style="margin-top: 20px;">', unsafe_allow_html=True)  
#     if st.button("Authenticate Connection Vector"):  
#         if u == USERNAME and p == PASSWORD:  
#             st.session_state.logged_in = True  
#             st.query_params["auth_session"] = "active"  
#             st.rerun()  
#         else:  
#             st.error("Authentication Vector Mismatch: Trace Flagged.")  
#     st.markdown('</div></div>', unsafe_allow_html=True)

# if not st.session_state.logged_in:
#     login_gate()  
#     st.stop()

# # =====================================================
# # TELEGRAM BROADCAST ENGINE
# # =====================================================
# def send_telegram_notification(pair, signal, confidence, tp, sl, pips):
#     bot_token = st.secrets.get("TELEGRAM_BOT_TOKEN", "")
#     chat_id = st.secrets.get("TELEGRAM_CHAT_ID", "")
    
#     if not bot_token or not chat_id:
#         return  
        
#     message = (
#         f"🚨 *VECTOR MATRIX PRO ALPHA SIGNAL*\n\n"
#         f"📊 *Asset Pair:* {pair}\n"
#         f"⚡ *Action Bias:* {signal}\n"
#         f"🎯 *Confluence Score:* {confidence}%\n"
#         f"📏 *Calculated Target:* {pips} Pips\n\n"
#         f"🟢 *Take Profit:* {tp}\n"
#         f"🔴 *Stop Loss:* {sl}\n\n"
#         f"🕒 _Timestamp (UTC):_ {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}"
#     )
    
#     url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
#     payload = {"chat_id": chat_id, "text": message, "parse_mode": "Markdown"}
#     try:
#         requests.post(url, json=payload, timeout=5)
#     except Exception:
#         pass  

# # =====================================================
# # REBUILT INSTITUTIONAL SMC/ICT/FIBONACCI TELEMETRY ENGINE
# # =====================================================
# def system_session_and_killzone():
#     now_utc = datetime.now(timezone.utc)  
#     hour = now_utc.hour  
      
#     if 2 <= hour < 5:  
#         return "LONDON OPEN (KILL ZONE)", True  
#     elif 7 <= hour < 10:  
#         return "NY OPEN (KILL ZONE)", True  
#     elif 10 <= hour < 12:  
#         return "LONDON CLOSE (KILL ZONE)", True  
      
#     if 0 <= hour < 7: return "ASIAN (ACCUMULATION)", False  
#     elif 7 <= hour < 13: return "LONDON (MANIPULATION)", False  
#     elif 13 <= hour < 21: return "NEW YORK (DISTRIBUTION)", False  
#     return "CLOSED (RESTRICTED SYSTEM)", False

# def compute_analytics_matrix(pair, df):
#     if df.empty or len(df) < 50:  
#         return st.session_state.global_market_registry[pair]["metrics"]  

#     reasons = []  

#     ema20 = df["Close"].ewm(span=20, adjust=False).mean()  
#     ema50 = df["Close"].ewm(span=50, adjust=False).mean()  
#     ema200 = df["Close"].ewm(span=200, adjust=False).mean()  
      
#     curr_ema20 = ema20.iloc[-1]  
#     curr_ema50 = ema50.iloc[-1]  
#     curr_ema200 = ema200.iloc[-1]  
      
#     trend_bullish = curr_ema20 > curr_ema50 > curr_ema200  
#     trend_bearish = curr_ema20 < curr_ema50 < curr_ema200  

#     if trend_bullish: reasons.append("EMAs (20/50/200) match a clear Bullish Structural Trend alignment.")  
#     elif trend_bearish: reasons.append("EMAs (20/50/200) match a clear Bearish Structural Trend alignment.")  

#     swing_highs = []  
#     swing_lows = []  
#     for i in range(5, len(df) - 5):  
#         if df["High"].iloc[i] == df["High"].iloc[i-5:i+6].max():  
#             swing_highs.append((df["time"].iloc[i], df["High"].iloc[i]))  
#         if df["Low"].iloc[i] == df["Low"].iloc[i-5:i+6].min():  
#             swing_lows.append((df["time"].iloc[i], df["Low"].iloc[i]))  

#     recent_high = swing_highs[-1][1] if swing_highs else float(df["High"].max())  
#     recent_low = swing_lows[-1][1] if swing_lows else float(df["Low"].min())  
#     price = float(df["Close"].iloc[-1])  
      
#     smc_structure = "CONSOLIDATION FRAMEWORK"  
#     structure_score_buy = 0  
#     structure_score_sell = 0  
      
#     if len(swing_highs) >= 2 and len(swing_lows) >= 2:  
#         last_sh = swing_highs[-1][1]  
#         prev_sh = swing_highs[-2][1]  
#         last_sl = swing_lows[-1][1]  
#         prev_sl = swing_lows[-2][1]  
          
#         if price > last_sh:  
#             if last_sh < prev_sh:  
#                 smc_structure = "SWING CHoCH (BULLISH)"  
#                 structure_score_buy += 35  
#                 reasons.append("A clean Swing-based CHoCH was triggered, identifying an early bullish architectural shift.")  
#             else:  
#                 smc_structure = "SWING BOS (BULLISH)"  
#                 structure_score_buy += 25  
#                 reasons.append("A structural Swing-based BOS occurred, confirming clean bullish matrix continuation.")  
#         elif price < last_sl:  
#             if last_sl > prev_sl:  
#                 smc_structure = "SWING CHoCH (BEARISH)"  
#                 structure_score_sell += 35  
#                 reasons.append("A clean Swing-based CHoCH was triggered, identifying an early bearish architectural shift.")  
#             else:  
#                 smc_structure = "SWING BOS (BEARISH)"  
#                 structure_score_sell += 25  
#                 reasons.append("A structural Swing-based BOS occurred, confirming clean bearish matrix continuation.")  

#     trading_range = recent_high - recent_low if (recent_high - recent_low) != 0 else 0.001
#     fib_618 = recent_high - (0.618 * trading_range)
#     fib_786 = recent_high - (0.786 * trading_range)

#     pct_position = (price - recent_low) / trading_range  
#     ote_buy_zone = (0.62 <= (1 - pct_position) <= 0.79)  
#     ote_sell_zone = (0.62 <= pct_position <= 0.79)  

#     fib_confluence_buy = False
#     fib_confluence_sell = False

#     if ote_buy_zone: 
#         fib_confluence_buy = True
#         reasons.append(f"Price targeted inside Golden Fibonacci Retracement Array: 61.8% ({round(fib_618,5)}) - 78.6% ({round(fib_786,5)}) Optimal Buy Entry.")  
#     if ote_sell_zone: 
#         fib_confluence_sell = True
#         reasons.append(f"Price targeted inside Golden Fibonacci Retracement Array: 61.8% ({round(fib_618,5)}) - 78.6% ({round(fib_786,5)}) Optimal Sell Entry.")  

#     sweep_ssl = df["Low"].iloc[-1] < recent_low and price > recent_low  
#     sweep_bsl = df["High"].iloc[-1] > recent_high and price < recent_high  

#     if sweep_ssl: reasons.append("Sell-Side Liquidity (SSL) swept below the recent swing low cluster before rejection.")  
#     if sweep_bsl: reasons.append("Buy-Side Liquidity (BSL) swept above the recent swing high cluster before rejection.")  

#     fvg_buy = df["Low"].iloc[-1] > df["High"].iloc[-3] and df["Close"].iloc[-2] > df["Open"].iloc[-2]  
#     fvg_sell = df["High"].iloc[-1] < df["Low"].iloc[-3] and df["Close"].iloc[-2] < df["Open"].iloc[-2]  
      
#     avg_tick_volume = df["Volume"].tail(20).mean()  
#     volume_expansion = df["Volume"].iloc[-1] > avg_tick_volume * 1.5  

#     if fvg_buy:  
#         v_status = "with institutional MT5 volume expansion confirmation" if volume_expansion else "lacking high tick volume validation"  
#         reasons.append(f"A Bullish Fair Value Gap (FVG) validation pattern was localized {v_status}.")  
#     if fvg_sell:  
#         v_status = "with institutional MT5 volume expansion confirmation" if volume_expansion else "lacking high tick volume validation"  
#         reasons.append(f"A Bearish Fair Value Gap (FVG) validation pattern was localized {v_status}.")  

#     buy_score = 25 if trend_bullish else 0  
#     sell_score = 25 if trend_bearish else 0  
      
#     buy_score += structure_score_buy  
#     sell_score += structure_score_sell  
      
#     if sweep_ssl: buy_score += 30  
#     if sweep_bsl: sell_score += 30  
#     if fvg_buy: buy_score += 20 if volume_expansion else 10  
#     if fvg_sell: sell_score += 20 if volume_expansion else 10  

#     if fib_confluence_buy: buy_score += 30  
#     else: buy_score = int(buy_score * 0.25)  
        
#     if fib_confluence_sell: sell_score += 30  
#     else: sell_score = int(sell_score * 0.25)  

#     session_label, is_killzone = system_session_and_killzone()  
#     killzone_multiplier = 1.35 if is_killzone else 0.75  
#     buy_score = int(buy_score * killzone_multiplier)  
#     sell_score = int(sell_score * killzone_multiplier)  

#     if is_killzone: reasons.append(f"Active market telemetry is within the hyper-fluid {session_label} sequence.")  

#     signal = "NEUTRAL"  
#     confidence = max(buy_score, sell_score)  

#     if buy_score >= 75: signal = "STRONG ICT BUY"  
#     elif buy_score >= 50: signal = "ICT OTE BUY"  
#     elif sell_score >= 75: signal = "STRONG ICT SELL"  
#     elif sell_score >= 50: signal = "ICT OTE SELL"  

#     if signal == "NEUTRAL":  
#         reasons.append("Insufficient confluence array weightings. Restricting system risk entry parameters.")  

#     pip_mult = 0.01 if "JPY" in pair.upper() else (0.10 if "XAU" in pair.upper() else 0.0001)  
#     minimum_pip_target = 12.0
#     min_delta_price = minimum_pip_target * pip_mult

#     if "BUY" in signal:  
#         sl = min(recent_low - (2 * pip_mult), price - min_delta_price / 2.5)
#         risk = price - sl if (price - sl) > 0 else min_delta_price / 2.5
#         tp = price + max(risk * 2.5, min_delta_price)
#     elif "SELL" in signal:  
#         sl = max(recent_high + (2 * pip_mult), price + min_delta_price / 2.5)
#         risk = sl - price if (sl - price) > 0 else min_delta_price / 2.5
#         tp = price - max(risk * 2.5, min_delta_price)
#     else:  
#         tp, sl = price, price  

#     return {  
#         "signal": signal, "confidence": min(round(confidence, 1), 100), "entry": round(price, 5),  
#         "tp": round(tp, 5), "sl": round(sl, 5), "pips": round(abs(tp - price) / pip_mult, 1) if "NEUTRAL" not in signal else 0,  
#         "rsi": int(pct_position * 100), "structure": smc_structure,  
#         "buy_score": min(buy_score, 100), "sell_score": min(sell_score, 100), "session": session_label,  
#         "timestamp": datetime.now().strftime("%H:%M:%S"), "recent_high": round(recent_high, 5), "recent_low": round(recent_low, 5),  
#         "reasons": reasons, "fib_618": round(fib_618, 5), "fib_786": round(fib_786, 5)
#     }

# @st.fragment(run_every=4)
# def background_telemetry_pipeline():
#     symbols_to_fetch = list(ticker_mapping.values())  
#     try:  
#         raw_data = yf.download(symbols_to_fetch, period="15d", interval="15m", progress=False, group_by="ticker")  
#         for pair, ticker in ticker_mapping.items():  
#             if ticker in raw_data.columns.get_level_values(0):  
#                 df_symbol = raw_data[ticker].dropna().reset_index()  
#                 t_col = "Datetime" if "Datetime" in df_symbol.columns else "Date"  
                  
#                 df_ltf = pd.DataFrame({  
#                     "time": pd.to_datetime(df_symbol[t_col]),  
#                     "Open": df_symbol["Open"].astype(float),  
#                     "High": df_symbol["High"].astype(float),  
#                     "Low": df_symbol["Low"].astype(float),  
#                     "Close": df_symbol["Close"].astype(float),  
#                     "Volume": df_symbol["Volume"].astype(float)  
#                 })  
                  
#                 if not df_ltf.empty:  
#                     st.session_state.global_market_registry[pair]["df_ltf_slice"] = df_ltf.tail(45)  
#                     st.session_state.global_market_registry[pair]["metrics"] = compute_analytics_matrix(pair, df_ltf)  
                      
#         st.sidebar.markdown(f"<div style='font-family:JetBrains Mono; font-size:0.75rem; color:#64748B; text-align:center;'>TELEMETRY LINK SYNC: {datetime.now().strftime('%H:%M:%S')}</div>", unsafe_allow_html=True)  
#     except Exception:  
#         pass

# background_telemetry_pipeline()

# # =====================================================
# # TRADINGVIEW EMBED COMPONENTS ENGINE
# # =====================================================
# def render_tradingview_widget(pair):
#     """Generates an asynchronous institutional TradingView Advanced Widget frame."""
#     tv_symbol = f"FX:{pair}" if pair != "XAUUSD" else "OANDA:XAUUSD"
#     tv_html = f"""
#     <div class="tradingview-widget-container" style="height:450px;width:100%;">
#       <div id="tradingview_matrix"></div>
#       <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
#       <script type="text/javascript">
#       new TradingView.widget({{
#         "width": "100%",
#         "height": 450,
#         "symbol": "{tv_symbol}",
#         "interval": "15",
#         "timezone": "Etc/UTC",
#         "theme": "dark",
#         "style": "1",
#         "locale": "en",
#         "enable_publishing": false,
#         "hide_side_toolbar": false,
#         "allow_symbol_change": true,
#         "container_id": "tradingview_matrix"
#       }});
#       </script>
#     </div>
#     """
#     components.html(tv_html, height=450)

# # =====================================================
# # MULTI-PAIR LIVE TRACKING SCANNER GRID
# # =====================================================
# @st.fragment(run_every=3)
# def render_market_scanner():
#     """Renders a structural dashboard matrix tracking all pairs simultaneously."""
#     st.markdown('<div class="premium-card">', unsafe_allow_html=True)
#     st.markdown("<span class='section-title'>🛰️ REAL-TIME SMC / ICT SCANNED MATRIX GRID</span>", unsafe_allow_html=True)
#     st.markdown("<div style='margin-bottom:12px;'></div>", unsafe_allow_html=True)
    
#     scan_cols = st.columns(len(pairs))
#     for idx, p in enumerate(pairs):
#         with scan_cols[idx]:
#             metrics = st.session_state.global_market_registry[p]["metrics"]
#             sig_lbl = metrics["signal"]
#             conf = metrics["confidence"]
            
#             # Action Colors Mapping
#             if "BUY" in sig_lbl:
#                 bg_color, text_color = "rgba(16, 185, 129, 0.1)", "#10B981"
#             elif "SELL" in sig_lbl:
#                 bg_color, text_color = "rgba(239, 68, 68, 0.1)", "#EF4444"
#             else:
#                 bg_color, text_color = "#0b1329", "#94A3B8"
                
#             st.markdown(f"""
#             <div style='background:{bg_color}; border: 1px solid #1e293b; border-radius:8px; padding:12px; text-align:center;'>
#                 <div style='font-weight:700; font-size:1.05rem; letter-spacing:0.02em;'>{p}</div>
#                 <div style='color:{text_color}; font-size:0.8rem; font-weight:700; margin:6px 0;'>{sig_lbl}</div>
#                 <div style='font-family:JetBrains Mono; font-size:1.1rem; font-weight:700; color:#38BDF8;'>{conf}%</div>
#                 <div style='font-size:0.7rem; color:#64748B; margin-top:4px;'>Pips Target: {metrics['pips']}</div>
#             </div>
#             """, unsafe_allow_html=True)
#     st.markdown('</div>', unsafe_allow_html=True)

# # =====================================================
# # ZERO-LATENCY HIGH-VISIBILITY RENDERING UI
# # =====================================================
# st.sidebar.markdown("<div style='margin-top:15px;'></div>", unsafe_allow_html=True)
# selected_pair = st.sidebar.selectbox("Active Stream Target", pairs)

# # Inject Global Scanner Matrix at the top
# render_market_scanner()

# @st.fragment(run_every=2)
# def render_live_dashboard(pair):
#     cached_node = st.session_state.global_market_registry[pair]  
#     plot_df = cached_node["df_ltf_slice"]  
#     result = cached_node["metrics"]  

#     if plot_df.empty:  
#         st.info("Synchronizing multi-timeframe vectors with system node parameters...")  
#         return  

#     if "STRONG" in result["signal"] and result["pips"] >= 10.0:  
#         if result["signal"] != st.session_state.last_signal[pair]:  
#             components.html('<audio autoplay style="display:none;"><source src="https://actions.google.com/sounds/v1/alarms/digital_watch_alarm_long.ogg" type="audio/ogg"></audio>', height=0)  
#             st.toast(f"🚨 CONFIRMED HIGH-ACCURACY SIGNAL ON {pair}!", icon="⚡")  
            
#             send_telegram_notification(
#                 pair=pair, signal=result["signal"], confidence=result["confidence"],
#                 tp=result["tp"], sl=result["sl"], pips=result["pips"]
#             )
#             st.session_state.last_signal[pair] = result["signal"]  
#     else:  
#         st.session_state.last_signal[pair] = None  

#     # Structural Layout Split: Native Vector Quant Chart vs TradingView Chart Engine
#     tab_vector, tab_tv = st.tabs(["📊 NATIVE VECTOR MATRIX PLOT", "📈 TRADINGVIEW LIGHTWEIGHT CORE"])
    
#     with tab_vector:
#         fig = go.Figure()  
#         fig.add_trace(go.Candlestick(  
#             x=plot_df["time"], open=plot_df["Open"], high=plot_df["High"], low=plot_df["Low"], close=plot_df["Close"], name=pair,  
#             increasing_line_color='#10B981', increasing_fillcolor='#10B981',  
#             decreasing_line_color='#EF4444', decreasing_fillcolor='#EF4444'  
#         ))  
          
#         if result["recent_high"] > 0:  
#             fig.add_hline(y=result["recent_high"], line_dash="dash", line_color="#F59E0B", opacity=0.4, annotation_text="SWING HIGH", annotation_position="top left")  
#             fig.add_hline(y=result["recent_low"],  line_dash="dash", line_color="#06B6D4", opacity=0.4, annotation_text="SWING LOW", annotation_position="bottom left")  
#             fig.add_hline(y=result["fib_618"], line_dash="dot", line_color="#818CF8", opacity=0.5, annotation_text="FIB 61.8%", annotation_position="top right")
#             fig.add_hline(y=result["fib_786"], line_dash="dot", line_color="#4F46E5", opacity=0.5, annotation_text="FIB 78.6%", annotation_position="bottom right")

#         fig.update_layout(  
#             template="plotly_dark", height=380, xaxis_rangeslider_visible=False, uirevision=pair,  
#             paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='#090d16',  
#             margin=dict(l=10, r=10, t=10, b=10)  
#         )  
#         fig.update_xaxes(showgrid=False)  
#         fig.update_yaxes(showgrid=True, gridcolor='#1e293b', side="right")  
#         st.plotly_chart(fig, use_container_width=True)  

#     with tab_tv:
#         render_tradingview_widget(pair)
      
#     # Custom Grid Metrics Row Layout  
#     color_hex = "#10B981" if "BUY" in result["signal"] else ("#EF4444" if "SELL" in result["signal"] else "#94A3B8")  
      
#     st.markdown('<div class="premium-card">', unsafe_allow_html=True)
#     st.markdown(f"<div style='display:flex; justify-content:space-between; margin-bottom:16px;'><span class='section-title'>🛰️ MATRIX INSTRUMENT METRICS: {pair}</span><span style='font-family:JetBrains Mono; color:#64748B;'>TICK: {result['timestamp']}</span></div>", unsafe_allow_html=True)  
    
#     c1, c2, c3, c4 = st.columns(4)  
#     with c1:  
#         st.markdown(f"""<div class='custom-metric'>  
#             <div class='metric-label'>Matrix Vector Bias</div>  
#             <div class='metric-value' style='color: {color_hex};'>{result['signal']}</div>  
#         </div>""", unsafe_allow_html=True)  
#     with c2:  
#         st.markdown(f"""<div class='custom-metric'>  
#             <div class='metric-label'>SMC Confluence</div>  
#             <div class='metric-value' style='color: #06B6D4;'>{result['confidence']}%</div>  
#         </div>""", unsafe_allow_html=True)  
#     with c3:  
#         st.markdown(f"""<div class='custom-metric'>  
#             <div class='metric-label'>Calculated Pip Distance</div>  
#             <div class='metric-value' style='color: #F59E0B;'>{result['pips']} Pips</div>  
#         </div>""", unsafe_allow_html=True)  
#     with c4:  
#         st.markdown(f"""<div class='custom-metric'>  
#             <div class='metric-label'>Target Parameters</div>  
#             <div class='metric-value' style='color: #F8FAFC; font-size:1.1rem !important;'>TP: {result['tp']}<br><span style='color:#94A3B8; font-size:0.75rem;'>SL: {result['sl']}</span></div>  
#         </div>""", unsafe_allow_html=True)  

#     st.markdown(f"""  
#     <div class='reasoning-box'>  
#         <div style='font-size:0.8rem; text-transform:uppercase; color:#38BDF8; font-weight:700; letter-spacing:0.05em; margin-bottom:8px;'>Structural Telemetry Logs</div>  
#         <div style='font-family:JetBrains Mono; font-size:0.85rem; color:#E2E8F0; line-height:1.6;'>  
#             {"<br>".join([f"• {r}" for r in result['reasons']])}  
#         </div>  
#     </div>  
#     </div>  
#     """, unsafe_allow_html=True)  

# render_live_dashboard(selected_pair)

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
# SYSTEM DESIGN & ULTRA-DARK ARCHITECTURAL INTERFACE
# =====================================================
st.set_page_config(page_title="VECTOR MATRIX PRO", page_icon="🏦", layout="wide")
st.markdown("""
<style>  
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;700&family=Space+Grotesk:wght@400;500;600;700&display=swap');  
      
    html, body, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {  
        background-color: #030712 !important;  
        font-family: 'Space Grotesk', sans-serif !important;  
        color: #F8FAFC !important;  
    }  
      
    .premium-card {  
        background: linear-gradient(145deg, #0f172a 0%, #1e293b 100%);  
        border: 1px solid #334155;  
        border-radius: 12px;  
        padding: 24px;  
        box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.5), 0 10px 10px -5px rgba(0, 0, 0, 0.4);  
        margin-bottom: 24px;  
    }  
      
    [data-testid="stSidebar"] {   
        background-color: #090d16 !important;  
        border-right: 1px solid #1e293b !important;  
    }  
      
    .terminal-header {   
        font-family: 'Space Grotesk';   
        font-weight: 700;   
        letter-spacing: -0.05em;  
        background: linear-gradient(90deg, #38BDF8 0%, #818CF8 100%);   
        -webkit-background-clip: text;   
        -webkit-text-fill-color: transparent;   
    }  
      
    .section-title {  
        font-size: 1.15rem;  
        font-weight: 600;  
        color: #F1F5F9;  
        border-left: 4px solid #38BDF8;  
        padding-left: 10px;  
        margin-bottom: 16px;  
    }  
      
    .custom-metric {  
        background: #0b1329 !important;  
        border: 1px solid #1e293b !important;  
        border-radius: 8px !important;  
        padding: 16px !important;  
        text-align: left;  
    }  
    .metric-label {  
        font-size: 0.75rem !important;  
        text-transform: uppercase !important;  
        color: #94A3B8 !important;  
        font-weight: 600 !important;  
        letter-spacing: 0.05em;  
        margin-bottom: 6px;  
    }  
    .metric-value {  
        font-size: 1.4rem !important;  
        font-weight: 700 !important;  
        font-family: 'JetBrains Mono', monospace !important;  
    }  
      
    .stButton>button {   
        background: linear-gradient(90deg, #2563EB 0%, #4F46E5 100%) !important;   
        color: #FFFFFF !important;   
        font-weight: 600 !important;  
        border: none !important;  
        border-radius: 6px !important;   
        padding: 12px 24px !important;  
        transition: all 0.2s ease !important;  
        box-shadow: 0 4px 6px -1px rgba(37, 99, 235, 0.2) !important;  
        width: 100%;  
    }  
    .stButton>button:hover {  
        transform: translateY(-1px) !important;  
        box-shadow: 0 10px 15px -3px rgba(37, 99, 235, 0.4) !important;  
    }  
      
    div[data-testid="stDataFrame"] {  
        border: 1px solid #1e293b !important;  
        border-radius: 8px !important;  
        overflow: hidden;  
    }  
      
    .reasoning-box {  
        background: rgba(15, 23, 42, 0.6);  
        border: 1px dashed #475569;  
        border-radius: 8px;  
        padding: 16px;  
        margin-top: 15px;  
    }  
</style>
""", unsafe_allow_html=True)

# =====================================================
# GLOBAL CONFIGURATION & STATE INITIALIZATION
# =====================================================
pairs = ["EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "XAUUSD"]
ticker_mapping = {
    "EURUSD": "EURUSD=X", "GBPUSD": "GBPUSD=X",  
    "USDJPY": "JPY=X", "AUDUSD": "AUDUSD=X", "XAUUSD": "GC=F"
}

if "global_market_registry" not in st.session_state:
    st.session_state.global_market_registry = {  
        p: {  
            "df_ltf_slice": pd.DataFrame(),  
            "metrics": {  
                "signal": "INITIALIZING MATRIX", "confidence": 0, "entry": 0, "tp": 0, "sl": 0,  
                "pips": 0, "rsi": 50, "structure": "ESTABLISHING CORE LINK", "buy_score": 0, "sell_score": 0,  
                "session": "UNKNOWN", "timestamp": "CALIBRATING FLOW", "recent_high": 0, "recent_low": 0,  
                "reasons": [], "fib_618": 0, "fib_786": 0
            }  
        } for p in pairs  
    }

if "last_signal" not in st.session_state:
    st.session_state.last_signal = {p: None for p in pairs}

# =====================================================
# PERSISTENT SECURE IDENTITY GATEWAY (ANTI-REFRESH)
# =====================================================
USERNAME = st.secrets.get("USERNAME", "")
PASSWORD = st.secrets.get("PASSWORD", "")

if "logged_in" not in st.session_state:
    if st.query_params.get("auth_session") == "active":  
        st.session_state.logged_in = True  
    else:  
        st.session_state.logged_in = False

def login_gate():
    st.markdown('<div class="premium-card" style="max-width: 450px; margin: 100px auto 0px auto;">', unsafe_allow_html=True)  
    st.markdown('<h2 class="terminal-header" style="font-size: 1.8rem; text-align: center; margin-bottom: 8px;">🏦 CORE SECURITY GATE</h2>', unsafe_allow_html=True)  
    st.markdown('<p style="text-align: center; color: #94A3B8; margin-bottom: 24px; font-size: 0.9rem;">Institutional Verification Required</p>', unsafe_allow_html=True)  
      
    u = st.text_input("Security ID Token / User Key", key="auth_user_input")  
    p = st.text_input("Matrix Access Signature", type="password", key="auth_pass_input")  
      
    st.markdown('<div style="margin-top: 20px;">', unsafe_allow_html=True)  
    if st.button("Authenticate Connection Vector"):  
        if u == USERNAME and p == PASSWORD:  
            st.session_state.logged_in = True  
            st.query_params["auth_session"] = "active"  
            st.rerun()  
        else:  
            st.error("Authentication Vector Mismatch: Trace Flagged.")  
    st.markdown('</div></div>', unsafe_allow_html=True)

if not st.session_state.logged_in:
    login_gate()  
    st.stop()

# =====================================================
# TELEGRAM PHOTO BROADCAST ENGINE
# =====================================================
def send_telegram_notification(pair, signal, confidence, tp, sl, pips, entry):
    """Sends calculated market parameters along with visual chart position mapping."""
    bot_token = st.secrets.get("TELEGRAM_BOT_TOKEN", "")
    chat_id = st.secrets.get("TELEGRAM_CHAT_ID", "")
    
    if not bot_token or not chat_id:
        return False
        
    if "BUY" in signal:
        image_url = "https://raw.githubusercontent.com/tradingview/patterns/main/long_position_guide.png"
    elif "SELL" in signal:
        image_url = "https://raw.githubusercontent.com/tradingview/patterns/main/short_position_guide.png"
    else:
        image_url = "https://raw.githubusercontent.com/tradingview/patterns/main/consolidation_guide.png"

    message = (
        f"🚨 *VECTOR MATRIX PRO ALPHA SIGNAL*\n\n"
        f"📊 *Asset Pair:* {pair}\n"
        f"⚡ *Action Bias:* {signal}\n"
        f"🎯 *Confluence Score:* {confidence}%\n"
        f"📏 *Target Distance:* {pips} Pips\n\n"
        f"📐 *LIVE MARKET PLACEMENT METRICS:*\n"
        f"🔹 *Entry Threshold:* {entry}\n"
        f"🟢 *Take Profit:* {tp}\n"
        f"🔴 *Stop Loss:* {sl}\n\n"
        f"ℹ️ _Reference the image above for your Long/Short chart deployment tool._\n"
        f"🕒 _Timestamp (UTC):_ {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}"
    )
    
    url = f"https://api.telegram.org/bot{bot_token}/sendPhoto"
    payload = {
        "chat_id": chat_id,
        "photo": image_url,
        "caption": message,
        "parse_mode": "Markdown"
    }
    try:
        response = requests.post(url, json=payload, timeout=7)
        return response.status_code == 200
    except Exception:
        return False

# =====================================================
# REBUILT INSTITUTIONAL SMC/ICT/FIBONACCI TELEMETRY ENGINE
# =====================================================
def system_session_and_killzone():
    now_utc = datetime.now(timezone.utc)  
    hour = now_utc.hour  
      
    if 2 <= hour < 5: return "LONDON OPEN (KILL ZONE)", True  
    elif 7 <= hour < 10: return "NY OPEN (KILL ZONE)", True  
    elif 10 <= hour < 12: return "LONDON CLOSE (KILL ZONE)", True  
      
    if 0 <= hour < 7: return "ASIAN (ACCUMULATION)", False  
    elif 7 <= hour < 13: return "LONDON (MANIPULATION)", False  
    elif 13 <= hour < 21: return "NEW YORK (DISTRIBUTION)", False  
    return "CLOSED (RESTRICTED SYSTEM)", False

def compute_analytics_matrix(pair, df):
    if df.empty or len(df) < 50:  
        return st.session_state.global_market_registry[pair]["metrics"]  

    reasons = []  

    ema20 = df["Close"].ewm(span=20, adjust=False).mean()  
    ema50 = df["Close"].ewm(span=50, adjust=False).mean()  
    ema200 = df["Close"].ewm(span=200, adjust=False).mean()  
      
    curr_ema20 = ema20.iloc[-1]  
    curr_ema50 = ema50.iloc[-1]  
    curr_ema200 = ema200.iloc[-1]  
      
    trend_bullish = curr_ema20 > curr_ema50 > curr_ema200  
    trend_bearish = curr_ema20 < curr_ema50 < curr_ema200  

    if trend_bullish: reasons.append("EMAs (20/50/200) match a clear Bullish Structural Trend alignment.")  
    elif trend_bearish: reasons.append("EMAs (20/50/200) match a clear Bearish Structural Trend alignment.")  

    swing_highs = []  
    swing_lows = []  
    for i in range(5, len(df) - 5):  
        if df["High"].iloc[i] == df["High"].iloc[i-5:i+6].max():  
            swing_highs.append((df["time"].iloc[i], df["High"].iloc[i]))  
        if df["Low"].iloc[i] == df["Low"].iloc[i-5:i+6].min():  
            swing_lows.append((df["time"].iloc[i], df["Low"].iloc[i]))  

    recent_high = swing_highs[-1][1] if swing_highs else float(df["High"].max())  
    recent_low = swing_lows[-1][1] if swing_lows else float(df["Low"].min())  
    price = float(df["Close"].iloc[-1])  
      
    smc_structure = "CONSOLIDATION FRAMEWORK"  
    structure_score_buy = 0  
    structure_score_sell = 0  
      
    if len(swing_highs) >= 2 and len(swing_lows) >= 2:  
        last_sh = swing_highs[-1][1]  
        last_sl = swing_lows[-1][1]  
          
        if price > last_sh:  
            smc_structure = "SWING BOS (BULLISH)"  
            structure_score_buy += 25  
            reasons.append("A structural Swing-based BOS occurred, confirming clean bullish matrix continuation.")  
        elif price < last_sl:  
            smc_structure = "SWING BOS (BEARISH)"  
            structure_score_sell += 25  
            reasons.append("A structural Swing-based BOS occurred, confirming clean bearish matrix continuation.")  

    trading_range = recent_high - recent_low if (recent_high - recent_low) != 0 else 0.001
    fib_618 = recent_high - (0.618 * trading_range)
    fib_786 = recent_high - (0.786 * trading_range)

    pct_position = (price - recent_low) / trading_range  
    ote_buy_zone = (0.62 <= (1 - pct_position) <= 0.79)  
    ote_sell_zone = (0.62 <= pct_position <= 0.79)  

    fib_confluence_buy = False
    fib_confluence_sell = False

    if ote_buy_zone: 
        fib_confluence_buy = True
        reasons.append(f"Price targeted inside Golden Fibonacci Retracement Array: 61.8% ({round(fib_618,5)}) - 78.6% ({round(fib_786,5)}) Optimal Buy Entry.")  
    if ote_sell_zone: 
        fib_confluence_sell = True
        reasons.append(f"Price targeted inside Golden Fibonacci Retracement Array: 61.8% ({round(fib_618,5)}) - 78.6% ({round(fib_786,5)}) Optimal Sell Entry.")  

    sweep_ssl = df["Low"].iloc[-1] < recent_low and price > recent_low  
    sweep_bsl = df["High"].iloc[-1] > recent_high and price < recent_high  

    fvg_buy = df["Low"].iloc[-1] > df["High"].iloc[-3] and df["Close"].iloc[-2] > df["Open"].iloc[-2]  
    fvg_sell = df["High"].iloc[-1] < df["Low"].iloc[-3] and df["Close"].iloc[-2] < df["Open"].iloc[-2]  
      
    avg_tick_volume = df["Volume"].tail(20).mean()  
    volume_expansion = df["Volume"].iloc[-1] > avg_tick_volume * 1.5  

    buy_score = 25 if trend_bullish else 0  
    sell_score = 25 if trend_bearish else 0  
    buy_score += structure_score_buy  
    sell_score += structure_score_sell  
      
    if sweep_ssl: buy_score += 30  
    if sweep_bsl: sell_score += 30  
    if fvg_buy: buy_score += 20 if volume_expansion else 10  
    if fvg_sell: sell_score += 20 if volume_expansion else 10  

    if fib_confluence_buy: buy_score += 30  
    else: buy_score = int(buy_score * 0.25)  
    if fib_confluence_sell: sell_score += 30  
    else: sell_score = int(sell_score * 0.25)  

    session_label, is_killzone = system_session_and_killzone()  
    killzone_multiplier = 1.35 if is_killzone else 0.75  
    buy_score = int(buy_score * killzone_multiplier)  
    sell_score = int(sell_score * killzone_multiplier)  

    signal = "NEUTRAL"  
    confidence = max(buy_score, sell_score)  

    if buy_score >= 75: signal = "STRONG ICT BUY"  
    elif buy_score >= 50: signal = "ICT OTE BUY"  
    elif sell_score >= 75: signal = "STRONG ICT SELL"  
    elif sell_score >= 50: signal = "ICT OTE SELL"  

    pip_mult = 0.01 if "JPY" in pair.upper() else (0.10 if "XAU" in pair.upper() else 0.0001)  
    minimum_pip_target = 12.0
    min_delta_price = minimum_pip_target * pip_mult

    if "BUY" in signal:  
        sl = min(recent_low - (2 * pip_mult), price - min_delta_price / 2.5)
        risk = price - sl if (price - sl) > 0 else min_delta_price / 2.5
        tp = price + max(risk * 2.5, min_delta_price)
    elif "SELL" in signal:  
        sl = max(recent_high + (2 * pip_mult), price + min_delta_price / 2.5)
        risk = sl - price if (sl - price) > 0 else min_delta_price / 2.5
        tp = price - max(risk * 2.5, min_delta_price)
    else:  
        tp, sl = price, price  

    return {  
        "signal": signal, "confidence": min(round(confidence, 1), 100), "entry": round(price, 5),  
        "tp": round(tp, 5), "sl": round(sl, 5), "pips": round(abs(tp - price) / pip_mult, 1) if "NEUTRAL" not in signal else 0,  
        "rsi": int(pct_position * 100), "structure": smc_structure,  
        "buy_score": min(buy_score, 100), "sell_score": min(sell_score, 100), "session": session_label,  
        "timestamp": datetime.now().strftime("%H:%M:%S"), "recent_high": round(recent_high, 5), "recent_low": round(recent_low, 5),  
        "reasons": reasons, "fib_618": round(fib_618, 5), "fib_786": round(fib_786, 5)
    }

@st.fragment(run_every=4)
def background_telemetry_pipeline():
    symbols_to_fetch = list(ticker_mapping.values())  
    try:  
        raw_data = yf.download(symbols_to_fetch, period="15d", interval="15m", progress=False, group_by="ticker")  
        for pair, ticker in ticker_mapping.items():  
            if ticker in raw_data.columns.get_level_values(0):  
                df_symbol = raw_data[ticker].dropna().reset_index()  
                t_col = "Datetime" if "Datetime" in df_symbol.columns else "Date"  
                  
                df_ltf = pd.DataFrame({  
                    "time": pd.to_datetime(df_symbol[t_col]),  
                    "Open": df_symbol["Open"].astype(float),  
                    "High": df_symbol["High"].astype(float),  
                    "Low": df_symbol["Low"].astype(float),  
                    "Close": df_symbol["Close"].astype(float),  
                    "Volume": df_symbol["Volume"].astype(float)  
                })  
                  
                if not df_ltf.empty:  
                    st.session_state.global_market_registry[pair]["df_ltf_slice"] = df_ltf.tail(45)  
                    st.session_state.global_market_registry[pair]["metrics"] = compute_analytics_matrix(pair, df_ltf)  
    except Exception:  
        pass

background_telemetry_pipeline()

# =====================================================
# TRADINGVIEW EMBED COMPONENTS ENGINE
# =====================================================
def render_tradingview_widget(pair):
    tv_symbol = f"FX:{pair}" if pair != "XAUUSD" else "OANDA:XAUUSD"
    tv_html = f"""
    <div class="tradingview-widget-container" style="height:450px;width:100%;">
      <div id="tradingview_matrix"></div>
      <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
      <script type="text/javascript">
      new TradingView.widget({{
        "width": "100%", "height": 450, "symbol": "{tv_symbol}", "interval": "15",
        "timezone": "Etc/UTC", "theme": "dark", "style": "1", "locale": "en",
        "enable_publishing": false, "hide_side_toolbar": false, "allow_symbol_change": true,
        "container_id": "tradingview_matrix"
      }});
      </script>
    </div>
    """
    components.html(tv_html, height=450)

# =====================================================
# MULTI-PAIR LIVE TRACKING SCANNER GRID
# =====================================================
@st.fragment(run_every=3)
def render_market_scanner():
    st.markdown('<div class="premium-card">', unsafe_allow_html=True)
    st.markdown("<span class='section-title'>🛰️ REAL-TIME SMC / ICT SCANNED MATRIX GRID</span>", unsafe_allow_html=True)
    st.markdown("<div style='margin-bottom:12px;'></div>", unsafe_allow_html=True)
    
    scan_cols = st.columns(len(pairs))
    for idx, p in enumerate(pairs):
        with scan_cols[idx]:
            metrics = st.session_state.global_market_registry[p]["metrics"]
            sig_lbl = metrics["signal"]
            conf = metrics["confidence"]
            
            if "BUY" in sig_lbl: bg_color, text_color = "rgba(16, 185, 129, 0.1)", "#10B981"
            elif "SELL" in sig_lbl: bg_color, text_color = "rgba(239, 68, 68, 0.1)", "#EF4444"
            else: bg_color, text_color = "#0b1329", "#94A3B8"
                
            st.markdown(f"""
            <div style='background:{bg_color}; border: 1px solid #1e293b; border-radius:8px; padding:12px; text-align:center;'>
                <div style='font-weight:700; font-size:1.05rem;'>{p}</div>
                <div style='color:{text_color}; font-size:0.8rem; font-weight:700; margin:6px 0;'>{sig_lbl}</div>
                <div style='font-family:JetBrains Mono; font-size:1.1rem; font-weight:700; color:#38BDF8;'>{conf}%</div>
            </div>
            """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# =====================================================
# ZERO-LATENCY HIGH-VISIBILITY RENDERING UI
# =====================================================
st.sidebar.markdown("<div style='margin-top:15px;'></div>", unsafe_allow_html=True)
selected_pair = st.sidebar.selectbox("Active Stream Target", pairs)

# Inject Global Scanner Matrix
render_market_scanner()

def render_live_dashboard(pair):
    cached_node = st.session_state.global_market_registry[pair]  
    plot_df = cached_node["df_ltf_slice"]  
    result = cached_node["metrics"]  

    if plot_df.empty:  
        st.info("Synchronizing multi-timeframe vectors with system node parameters...")  
        return  

    # Automated Trigger Channel Alignment
    if "STRONG" in result["signal"] and result["pips"] >= 10.0:  
        if result["signal"] != st.session_state.last_signal[pair]:  
            components.html('<audio autoplay style="display:none;"><source src="https://actions.google.com/sounds/v1/alarms/digital_watch_alarm_long.ogg" type="audio/ogg"></audio>', height=0)  
            st.toast(f"🚨 AUTO-DISPATCHED CONFIRMED HIGH-ACCURACY SIGNAL ON {pair}!", icon="⚡")  
            
            send_telegram_notification(
                pair=pair, signal=result["signal"], confidence=result["confidence"],
                tp=result["tp"], sl=result["sl"], pips=result["pips"], entry=result["entry"]
            )
            st.session_state.last_signal[pair] = result["signal"]  
    else:  
        st.session_state.last_signal[pair] = None  

    # Interactive Dashboard Split Columns
    chart_view, control_view = st.columns([2.2, 0.8])
    
    with chart_view:
        tab_vector, tab_tv = st.tabs(["📊 NATIVE VECTOR MATRIX PLOT", "📈 TRADINGVIEW LIGHTWEIGHT CORE"])
        with tab_vector:
            fig = go.Figure()  
            fig.add_trace(go.Candlestick(  
                x=plot_df["time"], open=plot_df["Open"], high=plot_df["High"], low=plot_df["Low"], close=plot_df["Close"], name=pair,  
                increasing_line_color='#10B981', increasing_fillcolor='#10B981',  
                decreasing_line_color='#EF4444', decreasing_fillcolor='#EF4444'  
            ))  
            if result["recent_high"] > 0:  
                fig.add_hline(y=result["recent_high"], line_dash="dash", line_color="#F59E0B", opacity=0.4, annotation_text="SWING HIGH")  
                fig.add_hline(y=result["recent_low"],  line_dash="dash", line_color="#06B6D4", opacity=0.4, annotation_text="SWING LOW")  
                fig.add_hline(y=result["fib_618"], line_dash="dot", line_color="#818CF8", opacity=0.5, annotation_text="FIB 61.8%")
                fig.add_hline(y=result["fib_786"], line_dash="dot", line_color="#4F46E5", opacity=0.5, annotation_text="FIB 78.6%")

            fig.update_layout(template="plotly_dark", height=380, xaxis_rangeslider_visible=False, uirevision=pair, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='#090d16', margin=dict(l=10, r=10, t=10, b=10))  
            fig.update_xaxes(showgrid=False)  
            fig.update_yaxes(showgrid=True, gridcolor='#1e293b', side="right")  
            st.plotly_chart(fig, use_container_width=True)  

        with tab_tv:
            render_tradingview_widget(pair)

    # Operational Management Column (Manual Override Telegram Broadcaster Button)
    with control_view:
        st.markdown('<div class="premium-card" style="height:435px; margin-bottom:0px;">', unsafe_allow_html=True)
        st.markdown("<span class='section-title'>🎮 OVERRIDE CONTROL</span>", unsafe_allow_html=True)
        st.markdown("<p style='font-size:0.8rem; color:#94A3B8; margin-bottom:15px;'>Manually force broadcast current live parameters to your subscribers.</p>", unsafe_allow_html=True)
        
        # Interactive Control Interface Trigger Button
        btn_label = f"📤 BROADCAST {pair} SIGNAL"
        if st.button(btn_label, use_container_width=True, key="manual_broadcast_trigger"):
            with st.spinner("Processing Matrix Packets..."):
                status = send_telegram_notification(
                    pair=pair, signal=result["signal"], confidence=result["confidence"],
                    tp=result["tp"], sl=result["sl"], pips=result["pips"], entry=result["entry"]
                )
                if status:
                    st.success(f"Successfully sent {pair} blueprint photo layout!")
                else:
                    st.error("Broadcast failed. Confirm Telegram Secrets Tokens.")
        
        st.markdown("<div style='margin-top:20px; border-top:1px solid #1e293b; padding-top:15px;'></div>", unsafe_allow_html=True)
        st.markdown(f"""
        <div style='font-family:JetBrains Mono; font-size:0.75rem; color:#94A3B8;'>
            <b>Payload Cache Tracker:</b><br>
            • Entry Vector: {result['entry']}<br>
            • Limit Target: {result['tp']}<br>
            • Invalidation: {result['sl']}
        </div>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
      
    # Custom Grid Metrics Row Layout  
    color_hex = "#10B981" if "BUY" in result["signal"] else ("#EF4444" if "SELL" in result["signal"] else "#94A3B8")  
    st.markdown('<div class="premium-card">', unsafe_allow_html=True)  
    c1, c2, c3, c4 = st.columns(4)  
    with c1:  
        st.markdown(f"<div class='custom-metric'><div class='metric-label'>Matrix Vector Bias</div><div class='metric-value' style='color: {color_hex};'>{result['signal']}</div></div>", unsafe_allow_html=True)  
    with c2:  
        st.markdown(f"<div class='custom-metric'><div class='metric-label'>SMC Confluence</div><div class='metric-value' style='color: #06B6D4;'>{result['confidence']}%</div></div>", unsafe_allow_html=True)  
    with c3:  
        st.markdown(f"<div class='custom-metric'><div class='metric-label'>Calculated Pip Distance</div><div class='metric-value' style='color: #F59E0B;'>{result['pips']} Pips</div></div>", unsafe_allow_html=True)  
    with c4:  
        st.markdown(f"<div class='custom-metric'><div class='metric-label'>Target Parameters</div><div class='metric-value' style='color: #F8FAFC; font-size:1.1rem !important;'>TP: {result['tp']}<br><span style='color:#94A3B8; font-size:0.75rem;'>SL: {result['sl']}</span></div></div>", unsafe_allow_html=True)  

    st.markdown(f"""  
    <div class='reasoning-box'>  
        <div style='font-size:0.8rem; text-transform:uppercase; color:#38BDF8; font-weight:700; letter-spacing:0.05em; margin-bottom:8px;'>Structural Telemetry Logs</div>  
        <div style='font-family:JetBrains Mono; font-size:0.85rem; color:#E2E8F0; line-height:1.6;'>  
            {"<br>".join([f"• {r}" for r in result['reasons']])}  
        </div>  
    </div>  
    </div>  
    """, unsafe_allow_html=True)  

render_live_dashboard(selected_pair)

# Global Smooth UI Loop Stream 
time.sleep(2)
st.rerun()
