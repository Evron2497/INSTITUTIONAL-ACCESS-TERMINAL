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
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght=400;500;700&family=Space+Grotesk:wght=400;500;600;700&display=swap');  
      
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
                "reasons": []  
            }  
        } for p in pairs  
    }

if "last_signal" not in st.session_state:
    st.session_state.last_signal = {p: None for p in pairs}

# =====================================================
# PERSISTENT SECURE IDENTITY GATEWAY (ANTI-REFRESH)
# =====================================================
USERNAME = st.secrets.get("USERNAME", "admin")
PASSWORD = st.secrets.get("PASSWORD", "matrix")

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
# REBUILT INSTITUTIONAL SMC/ICT TELEMETRY ENGINE
# =====================================================
def system_session_and_killzone():
    now_utc = datetime.now(timezone.utc)  
    hour = now_utc.hour  
      
    if 2 <= hour < 5:  
        return "LONDON OPEN (KILL ZONE)", True  
    elif 7 <= hour < 10:  
        return "NY OPEN (KILL ZONE)", True  
    elif 10 <= hour < 12:  
        return "LONDON CLOSE (KILL ZONE)", True  
      
    if 0 <= hour < 7: return "ASIAN (ACCUMULATION)", False  
    elif 7 <= hour < 13: return "LONDON (MANIPULATION)", False  
    elif 13 <= hour < 21: return "NEW YORK (DISTRIBUTION)", False  
    return "CLOSED (RESTRICTED SYSTEM)", False

def compute_analytics_matrix(pair, df):
    if df.empty or len(df) < 50:  
        return st.session_state.global_market_registry[pair]["metrics"]  

    reasons = []  
    pip_mult = 0.01 if "JPY" in pair.upper() else (0.10 if "XAU" in pair.upper() else 0.0001)

    # MT5 Indicator Emulations  
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

    # Fractal Swing Analysis  
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
      
    # Structural Transitions  
    smc_structure = "CONSOLIDATION FRAMEWORK"  
    structure_score_buy = 0  
    structure_score_sell = 0  
      
    if len(swing_highs) >= 2 and len(swing_lows) >= 2:  
        last_sh = swing_highs[-1][1]  
        prev_sh = swing_highs[-2][1]  
        last_sl = swing_lows[-1][1]  
        prev_sl = swing_lows[-2][1]  
          
        if price > last_sh:  
            if last_sh < prev_sh:  
                smc_structure = "SWING CHoCH (BULLISH)"  
                structure_score_buy += 35  
                reasons.append("A clean Swing-based CHoCH was triggered, identifying an early bullish architectural shift.")  
            else:  
                smc_structure = "SWING BOS (BULLISH)"  
                structure_score_buy += 25  
                reasons.append("A structural Swing-based BOS occurred, confirming clean bullish matrix continuation.")  
        elif price < last_sl:  
            if last_sl > prev_sl:  
                smc_structure = "SWING CHoCH (BEARISH)"  
                structure_score_sell += 35  
                reasons.append("A clean Swing-based CHoCH was triggered, identifying an early bearish architectural shift.")  
            else:  
                smc_structure = "SWING BOS (BEARISH)"  
                structure_score_sell += 25  
                reasons.append("A structural Swing-based BOS occurred, confirming clean bearish matrix continuation.")  

    # Complete Fibonacci Array Setup & OTE Setup (62% - 79%)  
    trading_range = recent_high - recent_low if (recent_high - recent_low) != 0 else 0.001  
    pct_position = (price - recent_low) / trading_range  
      
    fib_500 = recent_high - (0.500 * trading_range)
    fib_618 = recent_high - (0.618 * trading_range)
    fib_705 = recent_high - (0.705 * trading_range)  # Institutional Sweet Spot
    fib_786 = recent_high - (0.786 * trading_range)

    ote_buy_zone = (0.62 <= (1 - pct_position) <= 0.79)  
    ote_sell_zone = (0.62 <= pct_position <= 0.79)  

    if ote_buy_zone: reasons.append("Market price rests precisely within the premium 62% - 79% Optimal Trade Entry (OTE) Buy Discount matrix.")  
    if ote_sell_zone: reasons.append("Market price rests precisely within the premium 62% - 79% Optimal Trade Entry (OTE) Sell Premium matrix.")  

    # Advanced ICT Order Block Identification Engine
    ob_bullish = False
    ob_bearish = False
    avg_tick_volume = df["Volume"].tail(20).mean()  
    volume_expansion = df["Volume"].iloc[-1] > avg_tick_volume * 1.5  

    for idx in range(-5, -1):
        # Bullish OB: Last down candle before an aggressive upward vector break
        if df["Close"].iloc[idx] < df["Open"].iloc[idx] and df["Close"].iloc[-1] > df["High"].iloc[idx]:
            if price < df["High"].iloc[idx] and price > df["Low"].iloc[idx]:
                ob_bullish = True
        # Bearish OB: Last up candle before an aggressive downward vector break
        if df["Close"].iloc[idx] > df["Open"].iloc[idx] and df["Close"].iloc[-1] < df["Low"].iloc[idx]:
            if price > df["Low"].iloc[idx] and price < df["High"].iloc[idx]:
                ob_bearish = True

    if ob_bullish and price < fib_500:
        structure_score_buy += 25
        reasons.append("Mitigation of validated Bullish ICT Order Block inside Discount profile verified.")
    if ob_bearish and price > fib_500:
        structure_score_sell += 25
        reasons.append("Mitigation of validated Bearish ICT Order Block inside Premium profile verified.")

    # Liquidity Calculations  
    sweep_ssl = df["Low"].iloc[-1] < recent_low and price > recent_low  
    sweep_bsl = df["High"].iloc[-1] > recent_high and price < recent_high  

    if sweep_ssl: reasons.append("Sell-Side Liquidity (SSL) swept below the recent swing low cluster before rejection.")  
    if sweep_bsl: reasons.append("Buy-Side Liquidity (BSL) swept above the recent swing high cluster before rejection.")  

    # FVG Detections  
    fvg_buy = df["Low"].iloc[-1] > df["High"].iloc[-3] and df["Close"].iloc[-2] > df["Open"].iloc[-2]  
    fvg_sell = df["High"].iloc[-1] < df["Low"].iloc[-3] and df["Close"].iloc[-2] < df["Open"].iloc[-2]  

    if fvg_buy:  
        v_status = "with institutional MT5 volume expansion confirmation" if volume_expansion else "lacking high tick volume validation"  
        reasons.append(f"A Bullish Fair Value Gap (FVG) validation pattern was localized {v_status}.")  
    if fvg_sell:  
        v_status = "with institutional MT5 volume expansion confirmation" if volume_expansion else "lacking high tick volume validation"  
        reasons.append(f"A Bearish Fair Value Gap (FVG) validation pattern was localized {v_status}.")  

    # Execution System Weight Confluences  
    buy_score = 25 if trend_bullish else 0  
    sell_score = 25 if trend_bearish else 0  
      
    buy_score += structure_score_buy  
    sell_score += structure_score_sell  
      
    if sweep_ssl: buy_score += 30  
    if sweep_bsl: sell_score += 30  
    if fvg_buy: buy_score += 20 if volume_expansion else 10  
    if fvg_sell: sell_score += 20 if volume_expansion else 10  

    if ote_buy_zone: buy_score += 25  
    else: buy_score = int(buy_score * 0.3)  
          
    if ote_sell_zone: sell_score += 25  
    else: sell_score = int(sell_score * 0.3)  

    session_label, is_killzone = system_session_and_killzone()  
    killzone_multiplier = 1.3 if is_killzone else 0.8  
    buy_score = int(buy_score * killzone_multiplier)  
    sell_score = int(sell_score * killzone_multiplier)  

    if is_killzone: reasons.append(f"Active market telemetry is within the hyper-fluid {session_label} sequence.")  

    signal = "NEUTRAL"  
    confidence = max(buy_score, sell_score)  

    if buy_score >= 65: signal = "STRONG ICT BUY"  
    elif buy_score >= 45: signal = "ICT OTE BUY"  
    elif sell_score >= 65: signal = "STRONG ICT SELL"  
    elif sell_score >= 45: signal = "ICT OTE SELL"  

    if signal == "NEUTRAL":  
        reasons.append("Insufficient confluence array weightings. Restricting system risk entry parameters.")  

    # Volatility Risk Matrix Optimization Floor Engine (Minimum Floor = 10 Pips Enforced)
    min_pips_floor = 10.0
    if "BUY" in signal:  
        sl = recent_low - (2 * pip_mult)  
        risk = price - sl if (price - sl) > 0 else (5 * pip_mult)  
        tp_calculated = price + (risk * 2.1)  
        if ((tp_calculated - price) / pip_mult) < min_pips_floor:
            tp_calculated = price + (min_pips_floor * pip_mult)
        tp = tp_calculated
    elif "SELL" in signal:  
        sl = recent_high + (2 * pip_mult)  
        risk = sl - price if (sl - price) > 0 else (5 * pip_mult)  
        tp_calculated = price - (risk * 2.1)  
        if ((price - tp_calculated) / pip_mult) < min_pips_floor:
            tp_calculated = price - (min_pips_floor * pip_mult)
        tp = tp_calculated
    else:  
        tp, sl = price, price  

    return {  
        "signal": signal, "confidence": min(round(confidence, 1), 100), "entry": round(price, 5),  
        "tp": round(tp, 5), "sl": round(sl, 5), "pips": round(abs(tp - price) / pip_mult, 1) if "NEUTRAL" not in signal else 0,  
        "rsi": int(max(0, min(100, pct_position * 100))), "structure": smc_structure,  
        "buy_score": min(buy_score, 100), "sell_score": min(sell_score, 100), "session": session_label,  
        "timestamp": datetime.now().strftime("%H:%M:%S"), "recent_high": round(recent_high, 5), "recent_low": round(recent_low, 5),  
        "reasons": reasons, "fib_500": fib_500, "fib_618": fib_618, "fib_705": fib_705, "fib_786": fib_786
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
                    st.session_state.global_market_registry[pair]["df_ltf_slice"] = df_ltf.tail(60)  
                    st.session_state.global_market_registry[pair]["metrics"] = compute_analytics_matrix(pair, df_ltf)  
                      
        st.sidebar.markdown(f"<div style='font-family:JetBrains Mono; font-size:0.75rem; color:#64748B; text-align:center;'>TELEMETRY LINK SYNC: {datetime.now().strftime('%H:%M:%S')}</div>", unsafe_allow_html=True)  
    except Exception:  
        pass

background_telemetry_pipeline()

# =====================================================
# ZERO-LATENCY HIGH-VISIBILITY RENDERING UI
# =====================================================
st.sidebar.markdown("<div style='margin-top:15px;'></div>", unsafe_allow_html=True)
selected_pair = st.sidebar.selectbox("Active Stream Target", pairs)

@st.fragment(run_every=2)
def render_live_dashboard(pair):
    cached_node = st.session_state.global_market_registry[pair]  
    plot_df = cached_node["df_ltf_slice"]  
    result = cached_node["metrics"]  

    if plot_df.empty:  
        st.info("Synchronizing multi-timeframe vectors with system node parameters...")  
        return  

    if "STRONG" in result["signal"] and result["pips"] >= 10.0:  
        if result["signal"] != st.session_state.last_signal[pair]:  
            components.html('<audio autoplay style="display:none;"><source src="https://actions.google.com/sounds/v1/alarms/digital_watch_alarm_long.ogg" type="audio/ogg"></audio>', height=0)  
            st.toast(f"🚨 EXECUTABLE SMC QUANT SIGNAL ON {pair}!", icon="⚡")  
            st.session_state.last_signal[pair] = result["signal"]  
    else:  
        st.session_state.last_signal[pair] = None  

    # Candlestick Plot  
    fig = go.Figure()  
    fig.add_trace(go.Candlestick(  
        x=plot_df["time"], open=plot_df["Open"], high=plot_df["High"], low=plot_df["Low"], close=plot_df["Close"], name=pair,  
        increasing_line_color='#10B981', increasing_fillcolor='#10B981',  
        decreasing_line_color='#EF4444', decreasing_fillcolor='#EF4444'  
    ))  
      
    if result["recent_high"] > 0:  
        fig.add_hline(y=result["recent_high"], line_dash="dash", line_color="#F59E0B", opacity=0.4, annotation_text="SWING HIGH / FIB 0.0%")  
        if "fib_500" in result:
            fig.add_hline(y=result["fib_500"], line_dash="dot", line_color="#475569", opacity=0.5, annotation_text="EQUILIBRIUM 50.0%")
            fig.add_hline(y=result["fib_618"], line_dash="dash", line_color="#38BDF8", opacity=0.3, annotation_text="OTE 61.8%")
            fig.add_hline(y=result["fib_705"], line_dash="dash", line_color="#6366F1", opacity=0.5, annotation_text="OTE SWEET SPOT 70.5%")
            fig.add_hline(y=result["fib_786"], line_dash="dash", line_color="#818CF8", opacity=0.3, annotation_text="OTE 78.6%")
        fig.add_hline(y=result["recent_low"],  line_dash="dash", line_color="#06B6D4", opacity=0.4, annotation_text="SWING LOW / FIB 100.0%")  

    fig.update_layout(  
        template="plotly_dark", height=380, xaxis_rangeslider_visible=False, uirevision=pair,  
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='#090d16',  
        margin=dict(l=10, r=10, t=10, b=10)  
    )  
    fig.update_xaxes(showgrid=False)  
    fig.update_yaxes(showgrid=True, gridcolor='#1e293b', side="right")  
      
    st.markdown('<div class="premium-card">', unsafe_allow_html=True)  
    st.markdown(f"<div style='display:flex; justify-content:space-between; margin-bottom:16px;'><span class='section-title'>🛰️ SYSTEM MATRIX CORE: {pair}</span><span style='font-family:JetBrains Mono; color:#64748B;'>TICK: {result['timestamp']}</span></div>", unsafe_allow_html=True)  
    st.plotly_chart(fig, use_container_width=True)  
      
    # Custom Grid Metrics Row Layout  
    color_hex = "#10B981" if "BUY" in result["signal"] else ("#EF4444" if "SELL" in result["signal"] else "#94A3B8")  
      
    c1, c2, c3, c4 = st.columns(4)  
    with c1:  
        st.markdown(f"""<div class='custom-metric'>  
            <div class='metric-label'>Matrix Vector Bias</div>  
            <div class='metric-value' style='color: {color_hex};'>{result['signal']}</div>  
        </div>""", unsafe_allow_html=True)  
    with c2:  
        st.markdown(f"""<div class='custom-metric'>  
            <div class='metric-label'>SMC Confluence</div>  
            <div class='metric-value' style='color: #06B6D4;'>{result['confidence']}%</div>  
        </div>""", unsafe_allow_html=True)  
    with c3:  
        st.markdown(f"""<div class='custom-metric'>  
            <div class='metric-label'>Calculated Pip Distance</div>  
            <div class='metric-value' style='color: #F59E0B;'>{result['pips']} Pips</div>  
        </div>""", unsafe_allow_html=True)  
    with c4:  
        st.markdown(f"""<div class='custom-metric'>  
            <div class='metric-label'>Target Parameters</div>  
            <div class='metric-value' style='color: #818CF8; font-size:1.1rem !important;'>TP: {result['tp']}<br>SL: {result['sl']}</div>  
        </div>""", unsafe_allow_html=True)  

    # Live Execution Framework Logs Below Chart
    st.markdown('<div class="reasoning-box">', unsafe_allow_html=True)
    st.markdown("<p style='font-family:JetBrains Mono; font-size:0.85rem; color:#38BDF8; font-weight:700; margin:0;'>📜 QUANT ENGINE SIGNAL RATIONALE LOGS:</p>", unsafe_allow_html=True)
    for reason in result["reasons"]:
        st.markdown(f"<p style='font-family:JetBrains Mono; font-size:0.75rem; color:#94A3B8; margin:4px 0;'>• {reason}</p>", unsafe_allow_html=True)
    st.markdown('</div></div>', unsafe_allow_html=True)

render_live_dashboard(selected_pair)
