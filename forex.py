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

st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;600&family=Space+Grotesk:wght@400;500;600;700&display=swap');
        html, body, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
            background-color: #060913 !important;
            font-family: 'Space Grotesk', sans-serif !important;
            color: #F1F5F9 !important;
        }
        .premium-card {
            background: linear-gradient(135deg, rgba(15, 23, 42, 0.6) 0%, rgba(30, 41, 59, 0.4) 100%);
            border: 1px solid rgba(255, 255, 255, 0.05);
            border-radius: 16px;
            padding: 24px;
            box-shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.7);
            backdrop-filter: blur(12px);
            margin-bottom: 20px;
        }
        [data-testid="stSidebar"] { background-color: #0B0F19 !important; }
        .terminal-header { font-family: 'Space Grotesk'; font-weight: 700; background: linear-gradient(90deg, #00F0FF 0%, #7000FF 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
        div[data-testid="stMetricSimpleNormal"] { background: rgba(15, 23, 42, 0.8) !important; border: 1px solid rgba(255, 255, 255, 0.04) !important; border-radius: 12px !important; padding: 20px !important; }
        div[data-testid="stMetricLabel"] { font-size: 0.75rem !important; text-transform: uppercase !important; color: #94A3B8 !important; font-weight: 600; }
        .stButton>button { background: linear-gradient(90deg, #4F46E5 0%, #7C3AED 100%) !important; color: #FFFFFF !important; border-radius: 10px !important; width: 100% !important; }
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

# Sync session state with browser query params to survive F5 refreshes
if "logged_in" not in st.session_state:
    if st.query_params.get("auth_session") == "active":
        st.session_state.logged_in = True
    else:
        st.session_state.logged_in = False

def login_gate():
    st.markdown('<div class="premium-card" style="max-width: 450px; margin: 80px auto 0px auto;">', unsafe_allow_html=True)
    st.markdown('<h2 class="terminal-header" style="font-size: 1.8rem; text-align: center;">🏦 CORE SECURITY GATE</h2>', unsafe_allow_html=True)
    st.markdown('<p class="terminal-subheader" style="text-align: center; margin-bottom: 25px;">Institutional Verification Required</p>', unsafe_allow_html=True)
    
    u = st.text_input("Security ID Token / User Key", key="auth_user_input")
    p = st.text_input("Matrix Access Signature", type="password", key="auth_pass_input")
    
    st.markdown('<div style="margin-top: 15px;">', unsafe_allow_html=True)
    if st.button("Authenticate Connection Vector"):
        if u == USERNAME and p == PASSWORD:
            st.session_state.logged_in = True
            st.query_params["auth_session"] = "active"  # Saved in browser URL bar
            st.rerun()
        else:
            st.error("Authentication Vector Mismatch: Trace Flagged.")
    st.markdown('</div></div>', unsafe_allow_html=True)

if not st.session_state.logged_in:
    login_gate()
    st.stop()

# =====================================================
# DETACHED HIGH-SPEED SYSTEM TELEMETRY PROCESSING ENGINE
# =====================================================
def math_rsi(df, period=14):
    if len(df) < period: return 50.0
    delta = df["Close"].diff()
    gain = delta.clip(lower=0).rolling(period).mean()
    loss = (-delta.clip(upper=0)).rolling(period).mean()
    l_gain, l_loss = gain.iloc[-1], loss.iloc[-1]
    if l_loss == 0: return 100.0 if l_gain > 0 else 50.0
    return round(100 - (100 / (1 + (l_gain / l_loss))), 2)

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

def compute_analytics_matrix(pair, df_ltf):
    if df_ltf.empty or len(df_ltf) < 40:
        return st.session_state.global_market_registry[pair]["metrics"]
        
    df_resampled = df_ltf.set_index("time")
    df_itf = df_resampled.resample('1h').agg({'Open': 'first', 'High': 'max', 'Low': 'min', 'Close': 'last', 'Volume': 'sum'}).dropna().reset_index()
    df_htf = df_resampled.resample('4h').agg({'Open': 'first', 'High': 'max', 'Low': 'min', 'Close': 'last', 'Volume': 'sum'}).dropna().reset_index()

    htf_ema = df_htf["Close"].ewm(span=20).mean().iloc[-1]
    itf_ema = df_itf["Close"].ewm(span=20).mean().iloc[-1]
    macro_bullish = df_htf["Close"].iloc[-1] > htf_ema and df_itf["Close"].iloc[-1] > itf_ema
    macro_bearish = df_htf["Close"].iloc[-1] < htf_ema and df_itf["Close"].iloc[-1] < itf_ema
    htf_bias = "BULLISH" if macro_bullish else ("BEARISH" if macro_bearish else "NEUTRAL")

    recent_high = float(df_ltf["High"].tail(30).max())
    recent_low = float(df_ltf["Low"].tail(30).min())
    price = float(df_ltf["Close"].iloc[-1])
    
    h_l = df_ltf["High"] - df_ltf["Low"]
    h_pc = abs(df_ltf["High"] - df_ltf["Close"].shift(1))
    l_pc = abs(df_ltf["Low"] - df_ltf["Close"].shift(1))
    atr_val = pd.concat([h_l, h_pc, l_pc], axis=1).max(axis=1).rolling(14).mean().iloc[-1]
    if np.isnan(atr_val): atr_val = 0.001

    prev_high = float(df_ltf["High"].iloc[-2])
    prev_low = float(df_ltf["Low"].iloc[-2])
    
    smc_structure = "CONSOLIDATION MODEL"
    structure_score_buy = 0
    structure_score_sell = 0

    if price > prev_high and htf_bias == "BULLISH":
        smc_structure = "BREAK OF STRUCTURE (BOS)"
        structure_score_buy += 25
    elif price < prev_low and htf_bias == "BEARISH":
        smc_structure = "BREAK OF STRUCTURE (BOS)"
        structure_score_sell += 25
    elif price > prev_high and htf_bias == "BEARISH":
        smc_structure = "MARKET STRUCTURE SHIFT (MSS/CHoCH)"
        structure_score_buy += 35 
    elif price < prev_low and htf_bias == "BULLISH":
        smc_structure = "MARKET STRUCTURE SHIFT (MSS/CHoCH)"
        structure_score_sell += 35

    trading_range = recent_high - recent_low
    if trading_range == 0: trading_range = 0.001
    
    pct_position = (price - recent_low) / trading_range
    ote_buy_zone = (0.618 <= (1 - pct_position) <= 0.79)   
    ote_sell_zone = (0.618 <= pct_position <= 0.79)       

    equilibrium_premium = pct_position > 0.50
    equilibrium_discount = pct_position < 0.50

    session_label, is_killzone = system_session_and_killzone()
    killzone_multiplier = 1.4 if is_killzone else 0.8

    prev_macro_high = df_htf["High"].iloc[-2] if len(df_htf) >= 2 else recent_high
    prev_macro_low = df_htf["Low"].iloc[-2] if len(df_htf) >= 2 else recent_low
    sweep_bsl = price > prev_macro_high and df_ltf["Close"].iloc[-1] < prev_macro_high
    sweep_ssl = price < prev_macro_low and df_ltf["Close"].iloc[-1] > prev_macro_low

    avg_vol = df_ltf["Volume"].tail(20).mean()
    fvg_multiplier = 2.0 if (df_ltf["Volume"].iloc[-2] > (avg_vol * 1.8) if avg_vol > 0 else False) else 1.0
    fvg_buy = df_ltf["Low"].iloc[-1] > df_ltf["High"].iloc[-3] and df_ltf["Close"].iloc[-2] > df_ltf["Open"].iloc[-2]
    fvg_sell = df_ltf["High"].iloc[-1] < df_ltf["Low"].iloc[-3] and df_ltf["Close"].iloc[-2] < df_ltf["Open"].iloc[-2]

    buy_score = 20 if htf_bias == "BULLISH" else 0
    sell_score = 20 if htf_bias == "BEARISH" else 0
    
    buy_score += structure_score_buy
    sell_score += structure_score_sell

    if sweep_ssl: buy_score += 25
    if sweep_bsl: sell_score += 25
    if fvg_buy: buy_score += int(15 * fvg_multiplier)
    if fvg_sell: sell_score += int(15 * fvg_multiplier)

    if equilibrium_discount and ote_buy_zone:
        buy_score += 20  
    elif equilibrium_premium:
        buy_score = int(buy_score * 0.4)  

    if equilibrium_premium and ote_sell_zone:
        sell_score += 20
    elif equilibrium_discount:
        sell_score = int(sell_score * 0.4)

    buy_score = int(buy_score * killzone_multiplier)
    sell_score = int(sell_score * killzone_multiplier)

    signal = "NEUTRAL"
    confidence = max(buy_score, sell_score)

    if buy_score >= 70 and htf_bias == "BULLISH": signal = "STRONG ICT BUY"
    elif buy_score >= 50: signal = "ICT OTE BUY"
    elif sell_score >= 70 and htf_bias == "BEARISH": signal = "STRONG ICT SELL"
    elif sell_score >= 50: signal = "ICT OTE SELL"

    pip_mult = 0.01 if "JPY" in pair.upper() else (0.10 if "XAU" in pair.upper() else 0.0001)
    
    if "BUY" in signal:
        sl = df_ltf["Low"].tail(5).min() - (1 * pip_mult)
        tp = recent_high
        if (tp - price) < (10 * pip_mult): tp = price + (atr_val * 3)
    elif "SELL" in signal:
        sl = df_ltf["High"].tail(5).max() + (1 * pip_mult)
        tp = recent_low
        if (price - tp) < (10 * pip_mult): tp = price - (atr_val * 3)
    else:
        tp, sl = price, price

    pricing_framework_string = "OTE Discount" if equilibrium_discount else "OTE Premium"
    
    return {
        "signal": signal, "confidence": min(round(confidence, 1), 100), "entry": round(price, 5),
        "tp": round(tp, 5), "sl": round(sl, 5), "pips": round(abs(tp - price) / pip_mult, 1) if signal != "NEUTRAL" else 0,
        "rsi": math_rsi(df_ltf), "structure": f"{smc_structure} | Matrix: {pricing_framework_string}",
        "buy_score": min(buy_score, 100), "sell_score": min(sell_score, 100), "session": session_label,
        "timestamp": datetime.now().strftime("%H:%M:%S"), "recent_high": round(recent_high, 5), "recent_low": round(recent_low, 5)
    }

@st.fragment(run_every=4)
def background_telemetry_pipeline():
    symbols_to_fetch = list(ticker_mapping.values())
    try:
        raw_data = yf.download(symbols_to_fetch, period="10d", interval="15m", progress=False, group_by="ticker")
        
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
                    
        st.sidebar.markdown(f"<div style='font-family:JetBrains Mono; font-size:0.75rem; color:#64748B; text-align:center;'>MATRIX TELEMETRY SYNC: {datetime.now().strftime('%H:%M:%S')}</div>", unsafe_allow_html=True)
    except Exception:
        pass

background_telemetry_pipeline()

# =====================================================
# ZERO-LATENCY RENDERING UI FRAGMENTS
# =====================================================
selected_pair = st.sidebar.selectbox("Active Stream Target", pairs)

@st.fragment(run_every=2)
def render_live_dashboard(pair):
    cached_node = st.session_state.global_market_registry[pair]
    plot_df = cached_node["df_ltf_slice"]
    result = cached_node["metrics"]

    if plot_df.empty:
        st.info("Synchronizing data matrix structures with the core engine stream...")
        return

    # Anti-Spam Alerts Throttle & Component Update
    if "STRONG" in result["signal"] and result["pips"] >= 15.0:
        if result["signal"] != st.session_state.last_signal[pair]:
            components.html('<audio autoplay style="display:none;"><source src="https://actions.google.com/sounds/v1/alarms/digital_watch_alarm_long.ogg" type="audio/ogg"></audio>', height=0)
            st.toast(f"🚨 EXECUTABLE SMC QUANT SIGNAL ON {pair}!", icon="⚡")
            st.session_state.last_signal[pair] = result["signal"]
    else:
        st.session_state.last_signal[pair] = None

    fig = go.Figure()
    fig.add_trace(go.Candlestick(
        x=plot_df["time"], open=plot_df["Open"], high=plot_df["High"], low=plot_df["Low"], close=plot_df["Close"], name=pair,
        increasing_line_color='#10B981', increasing_fillcolor='#10B981',
        decreasing_line_color='#EF4444', decreasing_fillcolor='#EF4444'
    ))
    
    if result["recent_high"] > 0:
        fig.add_hline(y=result["recent_high"], line_dash="dash", line_color="rgba(245, 158, 11, 0.35)")
        fig.add_hline(y=result["recent_low"],  line_dash="dash", line_color="rgba(6, 182, 212, 0.35)")

    fig.update_layout(
        template="plotly_dark", height=420, xaxis_rangeslider_visible=False, uirevision=pair,
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(15, 23, 42, 0.4)',
        margin=dict(l=8, r=8, t=8, b=8)
    )
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=True, gridcolor='rgba(255,255,255,0.02)', side="right")
    
    st.markdown('<div class="premium-card">', unsafe_allow_html=True)
    st.markdown(f"<div style='display:flex; justify-content:space-between; margin-bottom:12px;'><b style='font-size:1.1rem; color:#FFFFFF;'>🛰️ SYSTEM MATRIX CORE: {pair}</b><span style='font-family:JetBrains Mono; color:#475569;'>REFRESH TICK</span></div>", unsafe_allow_html=True)
    st.plotly_chart(fig, use_container_width=True)
    
    color_hex = "#10B981" if "BUY" in result["signal"] else ("#EF4444" if "SELL" in result["signal"] else "#94A3B8")
    
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.markdown(f"<div data-testid='stMetricSimpleNormal'><div data-testid='stMetricLabel'>Validated Matrix Vector</div><div style='font-size:1.0rem; font-weight:700; color:{color_hex};'>{result['signal']}</div></div>", unsafe_allow_html=True)
    with c2: st.markdown(f"<div data-testid='stMetricSimpleNormal'><div data-testid='stMetricLabel'>Confluence Confidence</div><div style='font-size:1.4rem; font-weight:700; color:#00F0FF; font-family:JetBrains Mono;'>{result['confidence']}%</div></div>", unsafe_allow_html=True)
    with c3: st.markdown(f"<div data-testid='stMetricSimpleNormal'><div data-testid='stMetricLabel'>Target Proportional Yield</div><div style='font-size:1.4rem; font-weight:700; color:#F59E0B; font-family:JetBrains Mono;'>{result['pips']} Pips</div></div>", unsafe_allow_html=True)
    with c4: st.markdown(f"<div data-testid='stMetricSimpleNormal'><div data-testid='stMetricLabel'>Active Algorithmic Session</div><div style='font-size:0.75rem; font-weight:600; color:#94A3B8; margin-top:4px;'>{result['session']}</div></div>", unsafe_allow_html=True)
    
    st.markdown("<div style='margin-top:15px;'></div>", unsafe_allow_html=True)
    sc1, sc2 = st.columns(2)
    sc1.markdown(f"<div style='background:rgba(16, 185, 129, 0.06); padding:12px; border-radius:10px; border:1px solid rgba(16, 185, 129, 0.12); font-size:0.9rem;'>🟢 Buy Confluence Weight: <b style='color:#10B981; font-family:JetBrains Mono; float:right;'>{result['buy_score']}/100</b></div>", unsafe_allow_html=True)
    sc2.markdown(f"<div style='background:rgba(239, 68, 68, 0.06); padding:12px; border-radius:10px; border:1px solid rgba(239, 68, 68, 0.12); font-size:0.9rem;'>🔴 Sell Confluence Weight: <b style='color:#EF4444; font-family:JetBrains Mono; float:right;'>{result['sell_score']}/100</b></div>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

@st.fragment(run_every=4)
def render_scanner_block():
    st.markdown('<div class="premium-card" style="height: 100%;">', unsafe_allow_html=True)
    st.markdown("<b style='font-size:1.1rem; color:#FFFFFF; display:block; margin-bottom:15px;'>📡 CROSS-PORTFOLIO MONITOR ARRAY</b>", unsafe_allow_html=True)
    
    scan_results = []
    for p in pairs:
        res = st.session_state.global_market_registry[p]["metrics"]
        scan_results.append([p, res["signal"], f"{res['confidence']}%", res["structure"], res["pips"], res["session"]])
            
    scanner_df = pd.DataFrame(scan_results, columns=["Asset Pair", "Vector State", "Confidence", "SMC/ICT Diagnostics", "Risk Proportional Range", "Session Flow"])
    st.dataframe(scanner_df, use_container_width=True, hide_index=True)
    st.markdown('</div>', unsafe_allow_html=True)

@st.fragment
def render_broadcast_hub(pair):
    st.markdown('<div class="premium-card">', unsafe_allow_html=True)
    st.markdown("<b style='font-size:1.1rem; color:#FFFFFF; display:block; margin-bottom:15px;'>📩 ROUTED TELEGRAM DISPATCH</b>", unsafe_allow_html=True)
    confirm_send = st.checkbox("Confirm alignment with architectural execution parameters.", key="broadcast_check")
    st.markdown("<div style='margin-top:10px;'></div>", unsafe_allow_html=True)
    
    if st.button("EXECUTE BROADCAST ROUTER OVERLINK"):
        current_result = st.session_state.global_market_registry[pair]["metrics"]
        BOT_TOKEN = st.secrets.get("BOT_TOKEN", "")
        CHAT_IDS  = st.secrets.get("CHAT_IDS", [])
        
        if not confirm_send:
            st.warning("Execution Terminated: Confirmation flag required.")
        elif "NEUTRAL" in current_result["signal"] or "INITIALIZING" in current_result["signal"]:
            st.error("Routing Core Failure: Cannot push inactive trend indicators.")
        elif not BOT_TOKEN or not CHAT_IDS:
            st.error("Telegram vectors unconfigured in application secrets.")
        else:
            message = f"<b>🏦 SYSTEM SIGNAL VECTOR DISPATCH</b>\n\nASSET PAIR: {pair}\nSIGNAL BIAS: <b>{current_result['signal']}</b>\nCONFIDENCE: {current_result['confidence']}%\nSMC STRUCTURE: {current_result['structure']}\n\nENTRY RATE: {current_result['entry']}\nTARGET PROFIT (TP): {current_result['tp']}\nSTOP LOSS (SL): {current_result['sl']}\n\n📊 EXPECTED RANGE YIELD: <b>{current_result['pips']} Pips</b>"
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
st.markdown('<h1 class="terminal-header">TECH-STAR PRO</h1>', unsafe_allow_html=True)
st.markdown('<p class="terminal-subheader" style="margin-bottom:30px;">High-Fidelity Multi-Timeframe Quantitative Analytics Ecosystem</p>', unsafe_allow_html=True)

col_layout_left, col_layout_right = st.columns([1.9, 1.1])

with col_layout_left:
    render_live_dashboard(selected_pair)

with col_layout_right:
    render_scanner_block()
    render_broadcast_hub(selected_pair)

st.markdown("<div style='margin-top:10px;'></div>", unsafe_allow_html=True)
st.markdown('<div class="premium-card">', unsafe_allow_html=True)
st.markdown("<b style='font-size:1.1rem; color:#FFFFFF; display:block; margin-bottom:15px;'>📊 INTERACTIVE QUANTITATIVE ANALYTICS ENGINE STREAM</b>", unsafe_allow_html=True)
tradingview_html = f"""
<div id="tv_chart_container" style="height: 480px; width: 100%;"></div>
<script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
<script type="text/javascript">
new TradingView.widget({{
  "autosize": true, "symbol": "OANDA:{selected_pair}", "interval": "15",
  "container_id": "tv_chart_container", "theme": "dark", "style": "1", "locale": "en",
  "toolbar_bg": "#0B0F19", "enable_publishing": false, "hide_side_toolbar": false, "allow_symbol_change": true
}});
</script>
"""
components.html(tradingview_html, height=490, scrolling=False)
st.markdown('</div>', unsafe_allow_html=True)
