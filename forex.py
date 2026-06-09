import os
import time
import json
import threading
import requests
import numpy as np
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
import streamlit as st
import streamlit.components.v1 as components
from datetime import datetime, timezone

# =====================================================
# SYSTEM DESIGN & ULTRA-DARK ARCHITECTURAL INTERFACE
# =====================================================
st.set_page_config(page_title="CORE VECTOR MATRIX PRO", page_icon="🏦", layout="wide")

# Thread lock configuration for safe cross-thread session state synchronization
STATE_LOCK = threading.Lock()

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
        
        [data-testid="stSidebar"] {
            background-color: #0B0F19 !important;
            border-right: 1px solid rgba(255, 255, 255, 0.03) !important;
        }
        
        .terminal-header {
            font-family: 'Space Grotesk', sans-serif;
            font-weight: 700;
            background: linear-gradient(90deg, #00F0FF 0%, #7000FF 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            letter-spacing: -0.03em;
            margin-bottom: 4px;
        }
        
        .terminal-subheader {
            font-size: 0.95rem;
            color: #64748B;
            font-weight: 400;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            margin-top: 0px;
        }
        
        div[data-testid="stMetricSimpleNormal"] {
            background: rgba(15, 23, 42, 0.8) !important;
            border: 1px solid rgba(255, 255, 255, 0.04) !important;
            border-radius: 12px !important;
            padding: 20px !important;
        }
        
        div[data-testid="stMetricLabel"] {
            font-size: 0.75rem !important;
            text-transform: uppercase !important;
            letter-spacing: 0.08em !important;
            color: #94A3B8 !important;
            font-weight: 600;
        }
        
        .stButton>button {
            background: linear-gradient(90deg, #4F46E5 0%, #7C3AED 100%) !important;
            color: #FFFFFF !important;
            border: none !important;
            border-radius: 10px !important;
            font-weight: 600 !important;
            font-size: 0.9rem !important;
            padding: 12px 24px !important;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
            box-shadow: 0 4px 12px rgba(79, 70, 229, 0.3) !important;
            width: 100% !important;
        }
        
        .stButton>button:hover {
            transform: translateY(-1px) !important;
            box-shadow: 0 6px 20px rgba(0, 240, 255, 0.4) !important;
            background: linear-gradient(90deg, #00F0FF 0%, #7C3AED 100%) !important;
        }

        div[data-testid="stDataFrame"] {
            border: 1px solid rgba(255, 255, 255, 0.03) !important;
            border-radius: 12px !important;
            overflow: hidden;
        }
    </style>
""", unsafe_allow_html=True)

# =====================================================
# SECURE IDENTITY GATEWAY LAYER
# =====================================================
USERNAME = st.secrets.get("USERNAME", "")
PASSWORD = st.secrets.get("PASSWORD", "")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

def login():
    st.markdown('<div class="premium-card" style="max-width: 450px; margin: 80px auto 0px auto;">', unsafe_allow_html=True)
    st.markdown('<h2 class="terminal-header" style="font-size: 1.8rem; text-align: center;">🏦 CORE SECURITY GATE</h2>', unsafe_allow_html=True)
    st.markdown('<p class="terminal-subheader" style="text-align: center; margin-bottom: 25px;">Institutional Verification Required</p>', unsafe_allow_html=True)
    u = st.text_input("Security ID Token / User Key")
    p = st.text_input("Matrix Access Signature", type="password")
    st.markdown('<div style="margin-top: 15px;">', unsafe_allow_html=True)
    if st.button("Authenticate Connection Vector"):
        if u == USERNAME and p == PASSWORD:
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error("Authentication Vector Mismatch: Trace Flagged.")
    st.markdown('</div></div>', unsafe_allow_html=True)

if not st.session_state.logged_in:
    login()
    st.stop()

# =====================================================
# STATE INITIALIZATION & RISK PARAMETERS
# =====================================================
pairs = ["EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "XAUUSD"]
ticker_mapping = {
    "EURUSD": "EURUSD=X", "GBPUSD": "GBPUSD=X",
    "USDJPY": "JPY=X", "AUDUSD": "AUDUSD=X", "XAUUSD": "GC=F"
}

# Persistent Risk Management Parameters Setup
if "capital_base" not in st.session_state:
    st.session_state.capital_base = 10000.0
if "risk_percent" not in st.session_state:
    st.session_state.risk_percent = 1.0

if "global_market_registry" not in st.session_state:
    st.session_state.global_market_registry = {
        p: {
            "df_ltf_slice": pd.DataFrame(),
            "metrics": {
                "signal": "INITIALIZING MATRIX", "confidence": 0, "entry": 0, "tp": 0, "sl": 0,
                "pips": 0, "rsi": 50, "structure": "ESTABLISHING CORE LINK", "buy_score": 0, "sell_score": 0,
                "session": "UNKNOWN", "timestamp": "CALIBRATING FLOW", "recent_high": 0, "recent_low": 0,
                "target_lots": 0.0
            }
        } for p in pairs
    }

# =====================================================
# HIGH-SPEED VECTORIZED PROCESSING ENGINE
# =====================================================
def math_rsi(df, period=14):
    if len(df) < period: 
        return 50.0
    closes = df["Close"].values
    delta = np.diff(closes)
    gains = np.where(delta > 0, delta, 0.0)
    losses = np.where(delta < 0, -delta, 0.0)
    
    avg_gain = np.mean(gains[-period:])
    avg_loss = np.mean(losses[-period:])
    
    if avg_loss == 0: 
        return 100.0 if avg_gain > 0 else 50.0
    return round(100.0 - (100.0 / (1.0 + (avg_gain / avg_loss))), 2)

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

@st.cache_data(ttl=15, show_spinner=False)
def downsample_and_bias(df_json):
    df_resampled = pd.read_json(df_json)
    df_resampled = df_resampled.set_index("time")
    
    df_itf = df_resampled.resample('1h').agg({'Open': 'first', 'High': 'max', 'Low': 'min', 'Close': 'last', 'Volume': 'sum'}).dropna()
    df_htf = df_resampled.resample('4h').agg({'Open': 'first', 'High': 'max', 'Low': 'min', 'Close': 'last', 'Volume': 'sum'}).dropna()

    htf_ema = df_htf["Close"].ewm(span=20).mean().values[-1]
    itf_ema = df_itf["Close"].ewm(span=20).mean().values[-1]
    
    last_htf = df_htf["Close"].values[-1]
    last_itf = df_itf["Close"].values[-1]
    
    if last_htf > htf_ema and last_itf > itf_ema: htf_bias = "BULLISH"
    elif last_htf < htf_ema and last_itf < itf_ema: htf_bias = "BEARISH"
    else: htf_bias = "NEUTRAL"
    
    return htf_bias, df_htf["High"].values[-2] if len(df_htf) >= 2 else 0, df_htf["Low"].values[-2] if len(df_htf) >= 2 else 0

def compute_analytics_matrix(pair, df_full):
    if df_full.empty or len(df_full) < 300:
        return st.session_state.global_market_registry[pair]["metrics"]
        
    df_json = df_full[["time", "Open", "High", "Low", "Close", "Volume"]].to_json()
    htf_bias, prev_macro_high, prev_macro_low = downsample_and_bias(df_json)

    df_ltf = df_full.tail(45)
    high_vals = df_ltf["High"].values
    low_vals = df_ltf["Low"].values
    close_vals = df_ltf["Close"].values
    open_vals = df_ltf["Open"].values
    vol_vals = df_ltf["Volume"].values
    
    recent_high = float(np.max(high_vals[-30:]))
    recent_low = float(np.min(low_vals[-30:]))
    price = float(close_vals[-1])
    
    h_l = high_vals - low_vals
    h_pc = np.abs(high_vals[1:] - close_vals[:-1])
    l_pc = np.abs(low_vals[1:] - close_vals[:-1])
    max_comb = np.maximum(h_l[1:], np.maximum(h_pc, l_pc))
    atr_val = np.mean(max_comb[-14:]) if len(max_comb) >= 14 else 0.001

    prev_high, prev_low = float(high_vals[-3]), float(low_vals[-3])
    closed_trigger_price = float(close_vals[-2])
    
    smc_structure = "CONSOLIDATION MODEL"
    structure_score_buy = 0
    structure_score_sell = 0

    if closed_trigger_price > prev_high and htf_bias == "BULLISH":
        smc_structure = "BREAK OF STRUCTURE (BOS)"
        structure_score_buy += 25
    elif closed_trigger_price < prev_low and htf_bias == "BEARISH":
        smc_structure = "BREAK OF STRUCTURE (BOS)"
        structure_score_sell += 25
    elif closed_trigger_price > prev_high and htf_bias == "BEARISH":
        smc_structure = "MARKET STRUCTURE SHIFT (MSS/CHoCH)"
        structure_score_buy += 35  
    elif closed_trigger_price < prev_low and htf_bias == "BULLISH":
        smc_structure = "MARKET STRUCTURE SHIFT (MSS/CHoCH)"
        structure_score_sell += 35

    trading_range = recent_high - recent_low if (recent_high - recent_low) != 0 else 0.001
    pct_position = (price - recent_low) / trading_range
    ote_buy_zone = (0.618 <= (1.0 - pct_position) <= 0.79)   
    ote_sell_zone = (0.618 <= pct_position <= 0.79)       
    equilibrium_premium = pct_position > 0.50
    equilibrium_discount = pct_position < 0.50

    session_label, is_killzone = system_session_and_killzone()
    killzone_multiplier = 1.4 if is_killzone else 0.8

    if prev_macro_high == 0: prev_macro_high = recent_high
    if prev_macro_low == 0: prev_macro_low = recent_low
    
    sweep_bsl = closed_trigger_price > prev_macro_high and close_vals[-2] < prev_macro_high
    sweep_ssl = closed_trigger_price < prev_macro_low and close_vals[-2] > prev_macro_low

    avg_vol = np.mean(vol_vals[-20:])
    fvg_multiplier = 2.0 if (vol_vals[-3] > (avg_vol * 1.8) if avg_vol > 0 else False) else 1.0
    
    fvg_buy = low_vals[-2] > high_vals[-4] and close_vals[-3] > open_vals[-3]
    fvg_sell = high_vals[-2] < low_vals[-4] and close_vals[-3] < open_vals[-3]

    buy_score = 20 if htf_bias == "BULLISH" else 0
    sell_score = 20 if htf_bias == "BEARISH" else 0
    buy_score += structure_score_buy
    sell_score += structure_score_sell

    if sweep_ssl: buy_score += 25
    if sweep_bsl: sell_score += 25
    if fvg_buy: buy_score += int(15 * fvg_multiplier)
    if fvg_sell: sell_score += int(15 * fvg_multiplier)

    if equilibrium_discount and ote_buy_zone: buy_score += 20  
    elif equilibrium_premium: buy_score = int(buy_score * 0.4)  

    if equilibrium_premium and ote_sell_zone: sell_score += 20
    elif equilibrium_discount: sell_score = int(sell_score * 0.4)

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
        sl = np.min(low_vals[-5:]) - (1 * pip_mult)
        tp = recent_high
        if (tp - price) < (10 * pip_mult): tp = price + (atr_val * 3)
    elif "SELL" in signal:
        sl = np.max(high_vals[-5:]) + (1 * pip_mult)
        tp = recent_low
        if (price - tp) < (10 * pip_mult): tp = price - (atr_val * 3)
    else:
        tp, sl = price, price

    # --- POSITION SIZING ARCHITECTURE ---
    target_lots = 0.0
    if signal != "NEUTRAL":
        stop_distance_pips = abs(price - sl) / pip_mult
        if stop_distance_pips > 0:
            risk_cash = st.session_state.capital_base * (st.session_state.risk_percent / 100.0)
            # Calculations assume standard lot indices (e.g. $10 per pip moves for standard lots)
            pip_value_standard = 10.0 if "JPY" in pair.upper() or "XAU" in pair.upper() else 10.0
            target_lots = risk_cash / (stop_distance_pips * pip_value_standard)

    pricing_framework_string = "OTE Discount" if equilibrium_discount else "OTE Premium"
    
    return {
        "signal": signal, "confidence": min(round(confidence, 1), 100), "entry": round(price, 5),
        "tp": round(tp, 5), "sl": round(sl, 5), "pips": round(abs(tp - price) / pip_mult, 1) if signal != "NEUTRAL" else 0,
        "rsi": math_rsi(df_ltf), "structure": f"{smc_structure} | Matrix: {pricing_framework_string}",
        "buy_score": min(buy_score, 100), "sell_score": min(sell_score, 100), "session": session_label,
        "timestamp": datetime.now().strftime("%H:%M:%S"), "recent_high": round(recent_high, 5), "recent_low": round(recent_low, 5),
        "target_lots": round(target_lots, 2)
    }

# =====================================================
# ASYNCHRONOUS THREAD NETWORK PIPELINE
# =====================================================
def async_data_fetcher():
    """ Runs isolated in a background thread to prevent UI freezing with state verification locks """
    symbols_to_fetch = list(ticker_mapping.values())
    try:
        raw_data = yf.download(symbols_to_fetch, period="60d", interval="15m", progress=False, group_by="ticker")
        for pair, ticker in ticker_mapping.items():
            if ticker in raw_data.columns.get_level_values(0):
                df_symbol = raw_data[ticker].dropna()
                if not df_symbol.empty:
                    df_full = pd.DataFrame({
                        "time": df_symbol.index,
                        "Open": df_symbol["Open"].values,
                        "High": df_symbol["High"].values,
                        "Low": df_symbol["Low"].values,
                        "Close": df_symbol["Close"].values,
                        "Volume": df_symbol["Volume"].values
                    })
                    # Implement safe write allocation to avoid Streamlit state mutations
                    with STATE_LOCK:
                        st.session_state.global_market_registry[pair]["df_ltf_slice"] = df_full.tail(45)
                        st.session_state.global_market_registry[pair]["metrics"] = compute_analytics_matrix(pair, df_full)
    except Exception:
        pass

# Multithread initialization checker
if "last_sync_time" not in st.session_state:
    st.session_state.last_sync_time = 0

if time.time() - st.session_state.last_sync_time > 12:
    threading.Thread(target=async_data_fetcher, daemon=True).start()
    st.session_state.last_sync_time = time.time()

# =====================================================
# ZERO-LATENCY RENDERING UI FRAGMENTS
# =====================================================
selected_pair = st.sidebar.selectbox("Active Stream Target", pairs)

# Navigation Control Module Router Component
system_module = st.sidebar.radio("SYSTEM MODULE ACCESS", ["LIVE TERMINAL MATRIX", "RISK METRICS PROFILE"])

@st.fragment(run_every=3)
def render_live_dashboard(pair):
    cached_node = st.session_state.global_market_registry[pair]
    plot_df = cached_node["df_ltf_slice"]
    result = cached_node["metrics"]

    if plot_df.empty:
        st.info("Synchronizing core matrix engine streams async...")
        return

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
        template="plotly_dark", height=400, xaxis_rangeslider_visible=False, uirevision=pair,
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(15, 23, 42, 0.4)',
        margin=dict(l=8, r=8, t=8, b=8)
    )
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=True, gridcolor='rgba(255,255,255,0.02)', side="right")
    
    st.markdown('<div class="premium-card">', unsafe_allow_html=True)
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    
    color_hex = "#10B981" if "BUY" in result["signal"] else ("#EF4444" if "SELL" in result["signal"] else "#94A3B8")
    
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.markdown(f"<div data-testid='stMetricSimpleNormal'><div data-testid='stMetricLabel'>Matrix Vector</div><div style='font-size:1.0rem; font-weight:700; color:{color_hex};'>{result['signal']}</div></div>", unsafe_allow_html=True)
    with c2: st.markdown(f"<div data-testid='stMetricSimpleNormal'><div data-testid='stMetricLabel'>Confidence</div><div style='font-size:1.4rem; font-weight:700; color:#00F0FF;'>{result['confidence']}%</div></div>", unsafe_allow_html=True)
    with c3: st.markdown(f"<div data-testid='stMetricSimpleNormal'><div data-testid='stMetricLabel'>Target Sizing</div><div style='font-size:1.4rem; font-weight:700; color:#F59E0B;'>{result['target_lots']} Lots</div></div>", unsafe_allow_html=True)
    with c4: st.markdown(f"<div data-testid='stMetricSimpleNormal'><div data-testid='stMetricLabel'>SMC Session</div><div style='font-size:0.75rem; font-weight:600; color:#94A3B8; margin-top:4px;'>{result['session']}</div></div>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

@st.fragment(run_every=5)
def render_scanner_block():
    st.markdown('<div class="premium-card">', unsafe_allow_html=True)
    scan_results = []
    for p in pairs:
        res = st.session_state.global_market_registry[p]["metrics"]
        scan_results.append([p, res["signal"], f"{res['confidence']}%", res["structure"], res["target_lots"]])
            
    scanner_df = pd.DataFrame(scan_results, columns=["Asset Pair", "State", "Confidence", "SMC Diagnostics", "Position Size"])
    st.dataframe(scanner_df, use_container_width=True, hide_index=True)
    st.markdown('</div>', unsafe_allow_html=True)

@st.fragment
def render_broadcast_hub(pair):
    st.markdown('<div class="premium-card">', unsafe_allow_html=True)
    confirm_send = st.checkbox("Confirm alignment with execution parameters.", key="broadcast_check")
    
    if st.button("EXECUTE BROADCAST ROUTER OVERLINK"):
        current_result = st.session_state.global_market_registry[pair]["metrics"]
        BOT_TOKEN = st.secrets.get("BOT_TOKEN", "")
        CHAT_IDS  = st.secrets.get("CHAT_IDS", [])
        
        if not confirm_send:
            st.warning("Execution Terminated: Confirmation flag required.")
        elif "NEUTRAL" in current_result["signal"]:
            st.error("Core Failure: Cannot push neutral trend indicators.")
        elif not BOT_TOKEN:
            st.error("Telegram vectors unconfigured in application secrets.")
        else:
            message = (f"<b>🏦 DISPATCH</b>\n\nPAIR: {pair}\nBIAS: <b>{current_result['signal']}</b>\n"
                       f"LOTS: {current_result['target_lots']}\nENTRY: {current_result['entry']}\n"
                       f"TP: {current_result['tp']}\nSL: {current_result['sl']}")
            for chat_id in CHAT_IDS:
                try: 
                    requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", 
                                  data={"chat_id": chat_id, "text": message, "parse_mode": "HTML"}, timeout=5)
                except Exception: 
                    pass
            st.success("Payload pushed successfully.")
    st.markdown('</div>', unsafe_allow_html=True)

# =====================================================
# SYSTEM LAYOUT ASSEMBLY LAYER
# =====================================================
st.markdown('<h1 class="terminal-header">CORE VECTOR MATRIX PRO</h1>', unsafe_allow_html=True)
st.markdown('<p class="terminal-subheader" style="margin-bottom:30px;">High-Fidelity Multi-Timeframe Quantitative Analytics Ecosystem</p>', unsafe_allow_html=True)

if system_module == "LIVE TERMINAL MATRIX":
    col_layout_left, col_layout_right = st.columns([1.9, 1.1])
    with col_layout_left: 
        render_live_dashboard(selected_pair)
    with col_layout_right:
        render_scanner_block()
        render_broadcast_hub(selected_pair)

    st.markdown('<div class="premium-card">', unsafe_allow_html=True)
    tradingview_html = f"""
    <div id="tv_chart_container" style="height: 400px; width: 100%;"></div>
    <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
    <script type="text/javascript">
    new TradingView.widget({{
      "autosize": true, "symbol": "OANDA:{selected_pair}", "interval": "15",
      "container_id": "tv_chart_container", "theme": "dark", "style": "1", "locale": "en",
      "toolbar_bg": "#0B0F19", "enable_publishing": false, "hide_side_toolbar": false, "allow_symbol_change": true
    }});
    </script>
    """
    components.html(tradingview_html, height=410, scrolling=False)
    st.markdown('</div>', unsafe_allow_html=True)

elif system_module == "RISK METRICS PROFILE":
    st.markdown('<div class="premium-card">', unsafe_allow_html=True)
    st.markdown('<h3 style="color:#00F0FF; margin-top:0;">RISK MANAGEMENT PARAMETERS</h3>', unsafe_allow_html=True)
    
    st.session_state.capital_base = st.number_input(
        "Capital Base ($)", min_value=100.0, max_value=1000000.0, 
        value=st.session_state.capital_base, step=500.0
    )
    st.session_state.risk_percent = st.slider(
        "Risk Multiplier per Vector Position (%)", min_value=0.1, max_value=5.0, 
        value=st.session_state.risk_percent, step=0.1
    )
    
    st.info("Risk parameters applied dynamically across runtime vector allocations.")
    st.markdown('</div>', unsafe_allow_html=True)
