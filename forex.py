# =====================================================
# VOLATILE SECURITY ENVELOPE PROTOCOL (PERSISTENT)
# =====================================================
USERNAME = st.secrets.get("USERNAME", "")
PASSWORD = st.secrets.get("PASSWORD", "")

# Initialize session states cleanly
if "logged_in" not in st.session_state:
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
                st.success("Node authorized. Access granted.")
                st.rerun()  # Forces immediate layout draw with the updated session state
            else:
                st.error("Invalid node validation configuration profile.")
    st.markdown('</div>', unsafe_allow_html=True)

# Enforcement Checkpoint
if not st.session_state.logged_in:
    render_login_form()
    st.stop() # Prevents the rest of the application dashboard from displaying prematurely

# Disconnect logic configuration
if st.sidebar.button("🔒 Terminal Session Disconnect"):
    st.session_state.logged_in = False
    st.rerun()
