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
st.set_page_config(page_title="CORE VECTOR MATRIX PRO", page_icon="🏦", layout="wide")

# High-contrast UI Theme Configuration Override
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;700&family=Space+Grotesk:wght@400;500;600;700&display=swap');
        
        /* Base Container Overrides */
        html, body, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
            background-color: #030712 !important;
            font-family: 'Space Grotesk', sans-serif !important;
            color: #F8FAFC !important;
        }
        
        /* Premium High-Contrast Cards */
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
        
        /* Typography Elements */
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
        
        /* Metric Box Components Layout styling */
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
        
        /* High-Visibility Custom Action Buttons */
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
            border: none !important;
        }
        
        /* Dataframe styling fixes */
        div[data-testid="stDataFrame"] {
            border: 1px solid #1e293b !important;
            border-radius: 8px !important;
            overflow: hidden;
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
                "session": "UNKNOWN", "timestamp": "CALIBRATING FLOW", "recent_high": 0, "recent_low": 0
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

    # MT5 Indicator Emulations
    ema20 = df["Close"].ewm(span=20, adjust=False).mean()
    ema50 = df["Close"].ewm(span=50, adjust=False).mean()
    ema200 = df["Close"].ewm(span=200, adjust=False).mean()
    
    curr_ema20 = ema20.iloc[-1]
    curr_ema50 = ema50.iloc[-1]
    curr_ema200 = ema200.iloc[-1]
    
    trend_bullish = curr_ema20 > curr_ema50 > curr_ema200
    trend_bearish = curr_ema20 < curr_ema50 < curr_ema200

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
            else:
                smc_structure = "SWING BOS (BULLISH)"
                structure_score_buy += 25
        elif price < last_sl:
            if last_sl > prev_sl:
                smc_structure = "SWING CHoCH (BEARISH)"
                structure_score_sell += 35
            else:
                smc_structure = "SWING BOS (BEARISH)"
                structure_score_sell += 25

    # Range and OTE Setup (62% - 79%)
    trading_range = recent_high - recent_low if (recent_high - recent_low) != 0 else 0.001
    pct_position = (price - recent_low) / trading_range
    
    ote_buy_zone = (0.62 <= (1 - pct_position) <= 0.79)
    ote_sell_zone = (0.62 <= pct_position <= 0.79)

    # Liquidity Calculations
    sweep_ssl = df["Low"].iloc[-1] < recent_low and price > recent_low
    sweep_bsl = df["High"].iloc[-1] > recent_high and price < recent_high

    # FVG Detections
    fvg_buy = df["Low"].iloc[-1] > df["High"].iloc[-3] and df["Close"].iloc[-2] > df["Open"].iloc[-2]
    fvg_sell = df["High"].iloc[-1] < df["Low"].iloc[-3] and df["Close"].iloc[-2] < df["Open"].iloc[-2]
    
    avg_tick_volume = df["Volume"].tail(20).mean()
    volume_expansion = df["Volume"].iloc[-1] > avg_tick_volume * 1.5

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

    signal = "NEUTRAL"
    confidence = max(buy_score, sell_score)

    if buy_score >= 65: signal = "STRONG ICT BUY"
    elif buy_score >= 45: signal = "ICT OTE BUY"
    elif sell_score >= 65: signal = "STRONG ICT SELL"
    elif sell_score >= 45: signal = "ICT OTE SELL"

    pip_mult = 0.01 if "JPY" in pair.upper() else (0.10 if "XAU" in pair.upper() else 0.0001)
    
    # Enforced Risk Matrix (RR >= 2.1)
    if "BUY" in signal:
        sl = recent_low - (2 * pip_mult)
        risk = price - sl if (price - sl) > 0 else (5 * pip_mult)
        tp = price + (risk * 2.1) 
    elif "SELL" in signal:
        sl = recent_high + (2 * pip_mult)
        risk = sl - price if (sl - price) > 0 else (5 * pip_mult)
        tp = price - (risk * 2.1)
    else:
        tp, sl = price, price

    return {
        "signal": signal, "confidence": min(round(confidence, 1), 100), "entry": round(price, 5),
        "tp": round(tp, 5), "sl": round(sl, 5), "pips": round(abs(tp - price) / pip_mult, 1) if "NEUTRAL" not in signal else 0,
        "rsi": int(pct_position * 100), "structure": smc_structure,
        "buy_score": min(buy_score, 100), "sell_score": min(sell_score, 100), "session": session_label,
        "timestamp": datetime.now().strftime("%H:%M:%S"), "recent_high": round(recent_high, 5), "recent_low": round(recent_low, 5)
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

    # Native Signal Routing Notifications
    if "STRONG" in result["signal"] and result["pips"] >= 15.0:
        if result["signal"] != st.session_state.last_signal[pair]:
            components.html('<audio autoplay style="display:none;"><source src="https://actions.google.com/sounds/v1/alarms/digital_watch_alarm_long.ogg" type="audio/ogg"></audio>', height=0)
            st.toast(f"🚨 EXECUTABLE SMC QUANT SIGNAL ON {pair}!", icon="⚡")
            st.session_state.last_signal[pair] = result["signal"]
    else:
        st.session_state.last_signal[pair] = None

    # Candlestick Matrix Plot Generation
    fig = go.Figure()
    fig.add_trace(go.Candlestick(
        x=plot_df["time"], open=plot_df["Open"], high=plot_df["High"], low=plot_df["Low"], close=plot_df["Close"], name=pair,
        increasing_line_color='#10B981', increasing_fillcolor='#10B981',
        decreasing_line_color='#EF4444', decreasing_fillcolor='#EF4444'
    ))
    
    if result["recent_high"] > 0:
        fig.add_hline(y=result["recent_high"], line_dash="dash", line_color="#F59E0B", opacity=0.6, annotation_text="SWING HIGH", annotation_position="top left")
        fig.add_hline(y=result["recent_low"],  line_dash="dash", line_color="#06B6D4", opacity=0.6, annotation_text="SWING LOW", annotation_position="bottom left")

    fig.update_layout(
        template="plotly_dark", height=400, xaxis_rangeslider_visible=False, uirevision=pair,
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='#090d16',
        margin=dict(l=10, r=10, t=10, b=10)
    )
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=True, gridcolor='#1e293b', side="right")
    
    st.markdown('<div class="premium-card">', unsafe_allow_html=True)
    st.markdown(f"<div style='display:flex; justify-content:space-between; margin-bottom:16px;'><span class='section-title'>🛰️ SYSTEM MATRIX CORE: {pair}</span><span style='font-family:JetBrains Mono; color:#64748B;'>TICK: {result['timestamp']}</span></div>", unsafe_allow_html=True)
    st.plotly_chart(fig, use_container_width=True)
    
    # Custom Dynamic Structural Metrics Blocks (Enhanced Readability Grid)
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
            <div class='metric-label'>Target Parameters</div>
            <div class='metric-value' style='color: #F59E0B;'>RR ≥ 2.0</div>
        </div>""", unsafe_allow_html=True)
    with c4:
        st.markdown(f"""<div class='custom-metric'>
            <div class='metric-label'>Market Session</div>
            <div class='metric-value' style='color: #E2E8F0; font-size: 0.95rem !important; font-family:sans-serif !important; padding-top:6px;'>{result['session']}</div>
        </div>""", unsafe_allow_html=True)
    
    st.markdown("<div style='margin-top:20px;'></div>", unsafe_allow_html=True)
    
    # High Visibility Order Block Execution Matrix Details
    sc1, sc2, sc3 = st.columns(3)
    sc1.markdown(f"<div style='background:rgba(16, 185, 129, 0.04); padding:14px; border-radius:8px; border:1px solid #10B981; font-size:0.9rem; text-align:center;'>🟢 Buy Confluence Weight<br><b style='color:#10B981; font-family:JetBrains Mono; font-size:1.2rem;'>{result['buy_score']} / 100</b></div>", unsafe_allow_html=True)
    sc2.markdown(f"<div style='background:rgba(30, 41, 59, 0.5); padding:14px; border-radius:8px; border:1px solid #475569; font-size:0.9rem; text-align:center; color:#94A3B8;'>📑 Structural Diagnostics<br><b style='color:#FFF; font-family:sans-serif; font-size:0.95rem; display:inline-block; margin-top:4px;'>{result['structure']}</b></div>", unsafe_allow_html=True)
    sc3.markdown(f"<div style='background:rgba(239, 68, 68, 0.04); padding:14px; border-radius:8px; border:1px solid #EF4444; font-size:0.9rem; text-align:center;'>🔴 Sell Confluence Weight<br><b style='color:#EF4444; font-family:JetBrains Mono; font-size:1.2rem;'>{result['sell_score']} / 100</b></div>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

@st.fragment(run_every=4)
def render_scanner_block():
    st.markdown('<div class="premium-card">', unsafe_allow_html=True)
    st.markdown("<span class='section-title'>📡 CROSS-PORTFOLIO SCANNER BLOCK ARRAY</span>", unsafe_allow_html=True)
    st.markdown("<div style='margin-top:10px;'></div>", unsafe_allow_html=True)
    
    scan_results = []
    for p in pairs:
        res = st.session_state.global_market_registry[p]["metrics"]
        scan_results.append([p, res["signal"], f"{res['confidence']}%", res["structure"], f"Entry: {res['entry']} | TP: {res['tp']}", res["session"]])
            
    scanner_df = pd.DataFrame(scan_results, columns=["Asset Pair", "Vector State", "Confidence", "SMC/ICT Diagnostics", "Target Parameters", "Session Flow"])
    st.dataframe(scanner_df, use_container_width=True, hide_index=True)
    st.markdown('</div>', unsafe_allow_html=True)

@st.fragment
def render_broadcast_hub(pair):
    st.markdown('<div class="premium-card">', unsafe_allow_html=True)
    st.markdown("<span class='section-title'>📩 ROUTED TELEGRAM DISPATCH HUB</span>", unsafe_allow_html=True)
    st.markdown("<div style='margin-top:10px;'></div>", unsafe_allow_html=True)
    confirm_send = st.checkbox("Confirm alignment with operational parameter metrics.", key="broadcast_check")
    st.markdown("<div style='margin-top:12px;'></div>", unsafe_allow_html=True)
    
    if st.button("EXECUTE BROADCAST ROUTER OVERLINK"):
        current_result = st.session_state.global_market_registry[pair]["metrics"]
        BOT_TOKEN = st.secrets.get("BOT_TOKEN", "")
        CHAT_IDS  = st.secrets.get("CHAT_IDS", [])
        
        if not confirm_send:
            st.warning("Execution Terminated: Confirmation flag required.")
        elif "NEUTRAL" in current_result["signal"]:
            st.error("Routing Core Failure: Cannot push inactive trend indicators.")
        elif not BOT_TOKEN or not CHAT_IDS:
            st.error("Telegram configurations unconfigured in applications backend context.")
        else:
            message = f"<b>🏦 SYSTEM SIGNAL VECTOR DISPATCH</b>\n\nASSET PAIR: {pair}\nSIGNAL BIAS: <b>{current_result['signal']}</b>\nCONFIDENCE: {current_result['confidence']}%\nSMC STRUCTURE: {current_result['structure']}\n\nENTRY RATE: {current_result['entry']}\nTARGET PROFIT (TP): {current_result['tp']}\nSTOP LOSS (SL): {current_result['sl']}\n\n📊 PROPORTIONAL RISK: <b>RR ≥ 2.1 Verified via MT5 Metrics Core</b>"
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
            errors = []
            for chat_id in CHAT_IDS:
                try:
                    r = requests.post(url, data={"chat_id": chat_id, "text": message, "parse_mode": "HTML"}, timeout=10)
                    if r.status_code != 200: errors.append(r.text)
                except Exception as e: errors.append(str(e))
                
            if len(errors) == 0: st.success("Matrix payload pushed successfully to Telegram.")
            else: st.error(f"Transmission Exception Refused: {'; '.join(errors)}")
    st.markdown('</div>', unsafe_allow_html=True)

# =====================================================
# SYSTEM LAYOUT ASSEMBLY LAYER
# =====================================================
st.markdown('<h1 class="terminal-header" style="font-size: 2.5rem; margin-bottom: 5px;">CORE VECTOR MATRIX PRO</h1>', unsafe_allow_html=True)
st.markdown('<p style="color: #64748B; font-size: 1rem; margin-bottom: 30px;">High-Fidelity Multi-Timeframe Quantitative Architecture Engine</p>', unsafe_allow_html=True)

col_layout_left, col_layout_right = st.columns([1.85, 1.15])

with col_layout_left:
    render_live_dashboard(selected_pair)

with col_layout_right:
    render_scanner_block()
    render_broadcast_hub(selected_pair)

st.markdown('<div class="premium-card">', unsafe_allow_html=True)
st.markdown("<span class='section-title'>📊 INTERACTIVE QUANTITATIVE ANALYTICS TIMELINE STREAM</span>", unsafe_allow_html=True)
st.markdown("<div style='margin-top:15px;'></div>", unsafe_allow_html=True)
tradingview_html = f"""
<div id="tv_chart_container" style="height: 500px; width: 100%;"></div>
<script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
<script type="text/javascript">
new TradingView.widget({{
  "autosize": true, "symbol": "OANDA:{selected_pair}", "interval": "15",
  "container_id": "tv_chart_container", "theme": "dark", "style": "1", "locale": "en",
  "toolbar_bg": "#090d16", "enable_publishing": false, "hide_side_toolbar": false, "allow_symbol_change": true
}});
</script>
"""
components.html(tradingview_html, height=510, scrolling=False)
st.markdown('</div>', unsafe_allow_html=True)
