import streamlit as st
import os
import base64
from lesson_data import MODULES
import auth
import streamlit.components.v1 as components
import ai_assistant
import pypdfium2 as pdfium

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Didactics Hub",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CUSTOM CSS FOR NEW THEME ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    
    * {
        font-family: 'Inter', system-ui, sans-serif;
    }
    .stIcon, .material-symbols-rounded, [class*="icon"] {
        font-family: 'Material Symbols Rounded', 'Material Icons' !important;
    }
    
    /* Hide default Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stAppDeployButton {display:none;}
    
    /* App Background — soft lavender like reference design */
    .stApp {
        background: #edf1fb !important;
        background-image: none !important;
    }
    
    /* Main container max-width & responsive padding */
    .block-container {
        max-width: 1200px !important;
        padding-top: 5rem !important;
        padding-bottom: 3rem !important;
    }
    @media (min-width: 1024px) {
        .block-container { padding-left: 32px !important; padding-right: 32px !important; }
    }
    @media (min-width: 768px) and (max-width: 1023px) {
        .block-container { padding-left: 24px !important; padding-right: 24px !important; }
    }
    @media (max-width: 767px) {
        .block-container { padding-left: 16px !important; padding-right: 16px !important; }
    }
    
    /* Top Navbar — clean white */
    header[data-testid="stHeader"] {
        background: #ffffff !important;
        height: 64px !important;
        border-bottom: 1px solid #e5e7eb !important;
        box-shadow: 0 1px 8px rgba(0,0,0,0.07) !important;
        z-index: 999990 !important;
        left: 0 !important;
        right: 0 !important;
        top: 0 !important;
        width: 100vw !important;
    }
    
    /* Hide the native title pseudo-element since we'll use a real button */
    header[data-testid="stHeader"]::before {
        display: none !important;
    }
    
    /* Fix the native Streamlit sidebar toggles (both header and inside sidebar) */
    /* Hide the native Streamlit sidebar toggles since we use the custom top navbar button */
    [data-testid="collapsedControl"], [data-testid="stSidebarCollapseButton"],
    button[aria-label="Collapse sidebar"], button[aria-label="Expand sidebar"] {
        opacity: 0 !important;
        position: absolute !important;
        top: -9999px !important;
    }

    
    /* Sidebar — clean white panel */
    [data-testid="stSidebar"] {
        background: #ffffff !important;
        background-image: none !important;
        border-right: 1px solid #e5e7eb !important;
    }
    @media (min-width: 1024px) {
        [data-testid="stSidebar"] { min-width: 260px !important; max-width: 260px !important; }
    }
    /* Sidebar text colors */
    [data-testid="stSidebar"] * { color: #111827 !important; }
    [data-testid="stSidebar"] summary p { color: #6b7280 !important; font-weight: 700 !important; text-transform: uppercase !important; font-size: 11px !important; letter-spacing: 1.2px !important; }
    
    /* Sidebar nav buttons */
    [data-testid="stSidebar"] button {
        background: transparent !important; border: none !important;
        box-shadow: none !important; color: #111827 !important;
        font-weight: 500 !important; text-align: left !important;
        justify-content: flex-start !important; padding: 10px 12px !important;
        border-radius: 8px !important; width: 100% !important;
        display: flex !important; margin-bottom: 2px; font-size: 14px !important;
        transition: background 0.15s, color 0.15s;
    }
    [data-testid="stSidebar"] button div, 
    [data-testid="stSidebar"] button p {
        text-align: left !important; margin: 0 !important; color: inherit !important;
        width: 100% !important; display: flex !important; justify-content: flex-start !important; align-items: center !important;
    }
    [data-testid="stSidebar"] button:hover {
        background: #f3f4f6 !important;
    }
    [data-testid="stSidebar"] button[disabled] { opacity: 0.42 !important; }
    [data-testid="stSidebar"] button.active-lesson {
        background: #e0edff !important; color: #2563eb !important;
        font-weight: 700 !important;
    }
    /* Expanders styling */
    [data-testid="stExpander"] { border: none !important; box-shadow: none !important; background: transparent !important; }
    [data-testid="stExpanderDetails"] { padding-left: 0 !important; padding-right: 0 !important; }
    
    /* Typography Overrides */
    h1, .stMarkdown h1 {
        color: #111827;
        font-weight: 800 !important;
        line-height: 1.2 !important;
        margin-bottom: 4px !important;
    }
    @media (min-width: 1024px) { h1, .stMarkdown h1 { font-size: 38px !important; } }
    @media (min-width: 768px) and (max-width: 1023px) { h1, .stMarkdown h1 { font-size: 32px !important; } }
    @media (max-width: 767px) { h1, .stMarkdown h1 { font-size: 28px !important; } }
    
    h2, .stMarkdown h2 { color: #111827; font-size: 30px !important; font-weight: 800 !important; }
    h3, .stMarkdown h3 { color: #111827; font-size: 24px !important; font-weight: 700 !important; }
    p, li, span, .stMarkdown p, .stMarkdown li, .stMarkdown span {
        color: #4b5563;
        font-size: 16px !important;
        line-height: 1.6 !important;
    }
    
    /* Auth Cards */
    .auth-card {
        background-color: #ffffff;
        padding: 32px;
        border-radius: 16px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
        border: 1px solid #e5e7eb;
        margin: 0 auto;
        max-width: 400px; 
    }
    
    /* Text Inputs */
    .stTextInput > div > div > input {
        background-color: #ffffff !important;
        border: 1px solid #d1d5db !important;
        border-radius: 8px !important;
        color: #111827 !important;
        padding: 10px 12px !important;
    }
    .stTextInput > div > div > input:focus {
        border-color: #2563eb !important;
        box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1) !important;
    }
    /* Hide "Press Enter to apply" */
    div[data-testid="InputInstructions"] {
        display: none !important;
    }
    
    /* Locked Message */
    .locked-msg {
        text-align: center;
        padding: 40px;
        background-color: #f3f4f6;
        border-radius: 16px;
        color: #6b7280;
        font-size: 1.25rem;
        font-weight: 600;
        border: 1px solid #e5e7eb;
        margin-top: 24px;
    }
    
    /* Tabs styling (Pills) */
    .stTabs [data-baseweb="tab-list"] {
        gap: 12px;
        border-bottom: none !important;
        margin-bottom: 24px;
        overflow-x: auto !important; /* Horizontal scroll on mobile */
        justify-content: flex-start;
        padding-bottom: 8px; /* space for scrollbar if any */
    }
    @media (min-width: 768px) {
        .stTabs [data-baseweb="tab-list"] { justify-content: center; }
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: #f3f4f6 !important;
        border: none !important;
        border-radius: 999px !important;
        padding: 8px 16px !important;
        margin: 0 !important;
        color: #6b7280 !important;
        font-weight: 500 !important;
        white-space: nowrap !important;
    }
    .stTabs [data-baseweb="tab"]:hover {
        background-color: #e5e7eb !important;
        color: #111827 !important;
    }
    .stTabs [aria-selected="true"] {
        background-color: #2563eb !important;
        color: #ffffff !important;
        font-weight: 600 !important;
    }
    .stTabs [data-baseweb="tab-highlight"] { display: none !important; }
    
    /* Main Content Card (Wrapper for content) */
    [data-testid="stVerticalBlock"] > [data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #ffffff;
        border-radius: 16px !important;
        padding: 24px !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03) !important;
        border: 1px solid #e5e7eb !important;
    }
    
    /* PDF Container */
    .pdf-container {
        border-radius: 12px;
        overflow: hidden;
        border: 1px solid #e5e7eb;
        background-color: #f9fafb;
        margin-top: 16px;
    }
    .pdf-header {
        background-color: #f3f4f6;
        padding: 12px 16px;
        border-bottom: 1px solid #e5e7eb;
        font-weight: 600;
        color: #374151;
        display: flex;
        align-items: center;
        gap: 8px;
        font-size: 0.9rem;
    }
    
    /* Sidebar Custom Progress Card */
    .sidebar-progress-card {
        background: linear-gradient(135deg, rgba(255,255,255,0.18), rgba(255,255,255,0.08));
        border-radius: 14px;
        padding: 18px 16px;
        border: 1px solid rgba(255, 255, 255, 0.25);
        margin-bottom: 24px;
        backdrop-filter: blur(4px);
    }
    .sidebar-progress-title {
        font-size: 0.8rem;
        font-weight: 800;
        color: #ffffff;
        letter-spacing: 0.05em;
        text-transform: uppercase;
        margin-bottom: 4px;
    }
    .sidebar-progress-text {
        font-size: 0.73rem;
        color: rgba(255, 255, 255, 0.75);
        margin-bottom: 12px;
    }
    .progress-bar-bg {
        width: 100%;
        height: 7px;
        background-color: rgba(255, 255, 255, 0.2);
        border-radius: 9999px;
        overflow: hidden;
    }
    .progress-bar-fill {
        height: 100%;
        background: linear-gradient(90deg, #93c5fd, #ffffff);
        border-radius: 9999px;
        transition: width 0.6s cubic-bezier(.4,0,.2,1);
    }
    .sidebar-progress-count {
        text-align: right;
        font-size: 0.73rem;
        color: rgba(255,255,255,0.85);
        font-weight: 700;
        margin-top: 8px;
    }

    /* In-page tab bar */
    .tab-bar {
        display: flex;
        gap: 6px;
        background: #f1f5f9;
        border-radius: 12px;
        padding: 5px;
        margin-bottom: 24px;
    }
    .tab-btn {
        flex: 1;
        text-align: center;
        padding: 9px 0;
        border-radius: 8px;
        font-size: 13.5px;
        font-weight: 600;
        cursor: pointer;
        border: none;
        background: transparent;
        color: #64748b;
        transition: all 0.2s ease;
    }
    .tab-btn:hover { background: #e2e8f0; color: #1e293b; }
    .tab-btn.active {
        background: #2563eb;
        color: #ffffff;
        box-shadow: 0 2px 8px rgba(37,99,235,0.3);
    }

    /* Module card hover */
    .module-card {
        background: #ffffff;
        border: 1px solid #e5e7eb;
        border-radius: 14px;
        padding: 20px;
        margin-bottom: 16px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        box-shadow: 0 1px 4px rgba(0,0,0,0.05);
        transition: box-shadow 0.2s ease, transform 0.2s ease, border-color 0.2s ease;
        height: 200px;
    }
    .module-card:hover {
        box-shadow: 0 8px 24px rgba(37,99,235,0.12);
        transform: translateY(-2px);
        border-color: #bfdbfe;
    }
    .module-card-badge {
        display: inline-flex;
        align-items: center;
        gap: 4px;
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 0.04em;
        text-transform: uppercase;
        padding: 3px 8px;
        border-radius: 999px;
        margin-bottom: 10px;
    }
    .badge-unlocked { background: #dcfce7; color: #16a34a; }
    .badge-locked   { background: #f3f4f6; color: #9ca3af; }
    
    /* Primary buttons */
    .stButton > button[kind="primary"] {
        background: #2563eb !important; color: #fff !important;
        border-radius: 10px !important; border: none !important;
        font-weight: 600 !important; padding: 10px 20px !important;
        box-shadow: 0 4px 12px rgba(37,99,235,0.28) !important;
        transition: background 0.2s, transform 0.15s, box-shadow 0.2s !important;
    }
    .stButton > button[kind="primary"]:hover {
        background: #1d4ed8 !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 6px 18px rgba(37,99,235,0.35) !important;
    }
    .stButton > button[kind="secondary"] {
        border-radius: 10px !important; border: 1px solid #e5e7eb !important;
        background: #fff !important; color: #374151 !important; font-weight: 500 !important;
    }
    .stButton > button[kind="secondary"]:hover {
        background: #f9fafb !important; border-color: #d1d5db !important;
    }
    
    .stButton p, .stButton span, .stButton div { color: inherit !important; }
    
    .welcome-banner h1, .welcome-banner p, .welcome-banner span {
        color: #ffffff !important;
    }
    /* Navbar logo */
    .custom-nav-title button {
        background: transparent !important; border: none !important;
        color: #111827 !important; font-weight: 700 !important;
        font-size: 17px !important; padding: 0 !important;
    }
    .custom-nav-title button:hover { color: #2563eb !important; }
    </style>
""", unsafe_allow_html=True)

# Old JS hack removed


# --- STATE MANAGEMENT INITIALIZATION ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'username' not in st.session_state:
    st.session_state.username = ""
if 'unlocked_index' not in st.session_state:
    st.session_state.unlocked_index = 0
if 'quiz_scores' not in st.session_state:
    st.session_state.quiz_scores = {}
if 'current_view' not in st.session_state:
    st.session_state.current_view = -1 # -1 is the Homepage
if 'last_view' not in st.session_state:
    st.session_state.last_view = -2
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = [{"role": "assistant", "content": "Hello! I am your Didactics AI Assistant. Ask me to explain a concept or give you a practice scenario!"}]
if 'chat_open' not in st.session_state:
    st.session_state.chat_open = False
if 'active_tab' not in st.session_state:
    st.session_state.active_tab = "Materials"

def save_current_progress():
    auth.save_user_progress(st.session_state.username, st.session_state.unlocked_index, st.session_state.quiz_scores)

# --- TOP BAR RENDERING (GLOBAL) ---
if st.session_state.logged_in:
    username_initial = st.session_state.username[0].upper() if st.session_state.username else "U"
    uname = st.session_state.username
    right_side_html = f'<div id="nav-user"><div id="nav-avatar">{username_initial}</div><span id="nav-username">{uname}</span></div><form method="get" style="margin:0;"><button id="nav-logout" type="button">⏏ Logout</button></form>'
else:
    right_side_html = '<form method="get" style="margin:0;"><button id="nav-logout" type="button">➔ Sign In</button></form>'

st.markdown(f"""
<style>
/* Hide the native Streamlit header */
header[data-testid="stHeader"] {{ display: none !important; }}
/* Push content down so it doesn't hide under our navbar */
.block-container {{ padding-top: 5rem !important; }}
/* Our custom navbar */
#custom-navbar {{
    position: fixed; top: 0; left: 0; right: 0; height: 60px;
    background: #ffffff;
    border-bottom: 1px solid #e5e7eb;
    box-shadow: 0 1px 8px rgba(0,0,0,0.07);
    z-index: 999999;
    display: flex; align-items: center;
    padding: 0 20px 0 0;
    gap: 12px;
}}
#nav-hamburger {{
    width: 60px; height: 60px;
    display: flex; align-items: center; justify-content: center;
    cursor: pointer; font-size: 22px; color: #374151;
    flex-shrink: 0;
    border: none; background: transparent;
    transition: background 0.15s;
}}
#nav-hamburger:hover {{ background: #f3f4f6; }}
#nav-logo {{
    font-size: 17px; font-weight: 700; color: #111827;
    flex: 1; white-space: nowrap;
    text-decoration: none;
    cursor: pointer;
}}
#nav-logo span {{ color: #2563eb; }}
#nav-user {{
    display: flex; align-items: center; gap: 10px;
}}
#nav-avatar {{
    width: 34px; height: 34px; border-radius: 50%;
    background: linear-gradient(135deg,#2563eb,#3b82f6);
    display: flex; align-items: center; justify-content: center;
    color: white; font-weight: 700; font-size: 14px; flex-shrink:0;
}}
#nav-username {{ font-size:14px; font-weight:500; color:#374151; white-space:nowrap; }}
#nav-logout {{
    background: #2563eb; color: white;
    border: none; border-radius: 20px;
    padding: 6px 18px; font-size: 13px; font-weight: 600;
    cursor: pointer; white-space: nowrap;
    box-shadow: 0 2px 8px rgba(37,99,235,0.3);
    transition: background 0.15s;
}}
#nav-logout:hover {{ background: #1d4ed8; }}
</style>
<div id="custom-navbar">
    <button id="nav-hamburger" title="Toggle sidebar">☰</button>
    <div id="nav-logo">📚 Didactics <span>Hub</span></div>
    {right_side_html}
</div>
""", unsafe_allow_html=True)

# Hidden Streamlit buttons for system actions
if st.session_state.logged_in:
    if st.button("SysLogout", key="sys_logout_btn"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.rerun()
    if st.button("SysHome", key="sys_home_btn"):
        st.session_state.current_view = -1
        st.session_state.active_tab = "Materials"
        st.rerun()
else:
    if st.button("SysSignIn", key="sys_signin_btn"):
        st.session_state.auth_mode = "Login"
        st.rerun()

components.html("""
<script>
const doc = window.parent.document;
const btns = doc.querySelectorAll('button');

// Hide system buttons
for(let b of btns) {
    const t = b.innerText ? b.innerText.trim() : '';
    if(t === 'SysLogout' || t === 'SysSignIn' || t === 'SysHome') {
        const container = b.closest('[data-testid="stElementContainer"]');
        if(container) container.style.display = 'none';
    }
}

// Click Handlers
function clickSys(text) {
    for(let b of btns) {
        const t = b.innerText ? b.innerText.trim() : '';
        if(t === text) { b.click(); break; }
    }
}

const hamburger = doc.getElementById('nav-hamburger');
if(hamburger) {
    hamburger.onclick = function() {
        const sidebar = doc.querySelector('[data-testid="stSidebar"]');
        if(sidebar) {
            const isHidden = window.getComputedStyle(sidebar).display === 'none';
            if(isHidden) {
                sidebar.style.setProperty('display', 'block', 'important');
                sidebar.style.setProperty('transform', 'none', 'important');
            } else {
                sidebar.style.setProperty('display', 'none', 'important');
            }
        }
    };
}

const logoutBtn = doc.getElementById('nav-logout');
if(logoutBtn) {
    logoutBtn.onclick = function() {
        const txt = logoutBtn.innerText.includes('Sign In') ? 'SysSignIn' : 'SysLogout';
        clickSys(txt);
    };
}

const logoBtn = doc.getElementById('nav-logo');
if(logoBtn) {
    logoBtn.onclick = function() { clickSys('SysHome'); };
}
</script>
""", height=0)

# --- ROUTER: AUTHENTICATION ---
if not st.session_state.logged_in:
    if 'auth_mode' not in st.session_state:
        st.session_state.auth_mode = "Landing"

    # Login-specific CSS
    st.markdown("""
    <style>
    [data-testid="collapsedControl"] {display: none !important;}
    [data-testid="stSidebar"]        {display: none !important;}
    header[data-testid="stHeader"]   {display: none !important;}
    .stApp { background: #edf1fb !important; }
    .block-container {
        display: flex !important; flex-direction: column !important;
        justify-content: center !important; align-items: center !important;
        min-height: 100vh !important; padding-top: 0 !important;
        max-width: 960px !important;
    }
    [data-testid="stVerticalBlockBorderWrapper"] {
        background: #ffffff !important; border-radius: 24px !important;
        padding: 0 !important;
        box-shadow: 0 24px 48px rgba(37,99,235,0.10) !important;
        border: 1px solid #e5e7eb !important; width: 100% !important;
        overflow: hidden !important;
    }
    [data-testid="stVerticalBlockBorderWrapper"] [data-testid="stHorizontalBlock"] {
        align-items: center !important;
        min-height: 85vh;
    }
    [data-testid="column"]:first-of-type {
        max-width: 420px !important;
        margin: 0 auto !important;
        display: flex !important;
        flex-direction: column !important;
        justify-content: center !important;
        padding: 20px !important;
    }
    form [data-testid="stVerticalBlock"] { gap: 12px !important; }
    form .stTextInput { margin-bottom: 0px !important; padding-bottom: 0px !important; }
    [data-testid="stTextInputRootElement"] { height: 48px !important; border-radius: 12px !important; padding-right: 8px !important; }
    [data-testid="stTextInputRootElement"] input { font-size: 15px !important; width: 100% !important; margin: 0 !important; }
    .stButton > button[kind="primary"] { height: 48px !important; border-radius: 12px !important; font-size: 15px !important; margin-top: 8px !important; width: 100% !important; }
    
    @keyframes floatHero {
        0% { transform: translateY(0px); }
        50% { transform: translateY(-12px); }
        100% { transform: translateY(0px); }
    }
    .hero-img {
        mix-blend-mode: multiply;
        animation: floatHero 4s ease-in-out infinite;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Encode illustration
    import base64 as _b64
    _ill_path = "assets/hero_illustration.png"
    if os.path.exists(_ill_path):
        with open(_ill_path, "rb") as _f:
            _ill_b64 = _b64.b64encode(_f.read()).decode()
        _ill_html = f'<img src="data:image/png;base64,{_ill_b64}" class="hero-img" style="width:100%;max-width:400px;height:auto;">'
    else:
        _ill_html = '<div style="width:100%;max-width:300px;aspect-ratio:1;border-radius:32px;background:linear-gradient(135deg,#eff6ff,#dbeafe);margin:0 auto;box-shadow:inset 0 4px 20px rgba(255,255,255,0.5);"></div>'

    with st.container(border=True):
        left_col, right_col = st.columns([1, 1], gap="large")

        # RIGHT — illustration
        with right_col:
            st.markdown(f"""
            <div style="display:flex;align-items:center;justify-content:center;height:100%;padding:32px 24px 32px 0;">
                {_ill_html}
            </div>""", unsafe_allow_html=True)

        # LEFT — form
        with left_col:


            if st.session_state.auth_mode == "Landing":
                st.markdown("""
                <div style="padding: 0;">
                    <div style="font-size:13px;font-weight:700;letter-spacing:.1em;text-transform:uppercase;color:#2563eb;margin-bottom:14px;">🏫 Didactics Hub</div>
                    <h1 style="font-size:32px;font-weight:800;color:#111827;line-height:1.2;margin-bottom:12px;">
                        Master the art of <span style="color:#2563eb;">teaching.</span>
                    </h1>
                    <p style="color:#6b7280;font-size:15px;margin-bottom:28px;line-height:1.6;">Sign in to continue your journey through didactic theories and practical methodologies.</p>
                </div>
                """, unsafe_allow_html=True)
                with st.container():
                    if st.button("Sign In ➔", use_container_width=True, type="primary", key="landing_signin_btn"):
                        st.session_state.auth_mode = "Login"
                    st.markdown("</div>", unsafe_allow_html=True)

            elif st.session_state.auth_mode == "Login":
                st.markdown("""
                <div style="padding: 0;">
                    <h2 style="font-size:28px;font-weight:800;color:#111827;margin-bottom:8px;">Welcome Back 👋</h2>
                    <p style="color:#6b7280;font-size:15px;margin-bottom:16px;">Please enter your details to sign in.</p>
                </div>
                """, unsafe_allow_html=True)
                with st.container():
                    with st.form("login_form", border=False):
                        username = st.text_input("", placeholder="Username", key="login_user")
                        password = st.text_input("", placeholder="Password", type="password", key="login_pass")
                        submitted = st.form_submit_button("Sign In ➔", use_container_width=True, type="primary")
                        if submitted:
                            success, msg, user_data = auth.verify_login(username, password)
                            if success:
                                st.session_state.logged_in = True
                                st.session_state.username = username
                                st.session_state.unlocked_index = user_data.get("unlocked_index", 0)
                                st.session_state.quiz_scores = user_data.get("quiz_scores", {})
                                st.rerun()
                            else:
                                st.error(msg)
                    st.markdown("<hr style='margin:20px 0;border-color:#e5e7eb;'>", unsafe_allow_html=True)
                    c1, c2 = st.columns(2)
                    with c1:
                        if st.button("✦ Create Account", use_container_width=True, key="goto_signup_btn"):
                            st.session_state.auth_mode = "Sign Up"; st.rerun()
                    with c2:
                        if st.button("🔑 Forgot Password?", use_container_width=True, key="goto_forgot_btn"):
                            st.session_state.auth_mode = "Forgot Password"; st.rerun()

            elif st.session_state.auth_mode == "Sign Up":
                st.markdown("""
                <div style="padding: 0;">
                    <h2 style="font-size:28px;font-weight:800;color:#111827;margin-bottom:8px;">Create Account ✦</h2>
                    <p style="color:#6b7280;font-size:15px;margin-bottom:16px;">Sign up to start your didactic journey.</p>
                </div>
                """, unsafe_allow_html=True)
                with st.container():
                    with st.form("signup_form", border=False):
                        new_user = st.text_input("", placeholder="Choose Username", key="signup_user")
                        new_pass = st.text_input("", placeholder="Choose Password", type="password", key="signup_pass")
                        sec_ans  = st.text_input("", placeholder="Name of your first pet? (security)", key="signup_sec")
                        submitted = st.form_submit_button("✦ Create Account", use_container_width=True, type="primary")
                        if submitted:
                            if new_user and new_pass and sec_ans:
                                success, msg = auth.create_user(new_user, new_pass, sec_ans)
                                if success:
                                    st.success(msg + " You can now login.")
                                else:
                                    st.error(msg)
                            else:
                                st.warning("Please fill in all fields.")
                    st.markdown("<hr style='margin:20px 0;border-color:#e5e7eb;'>", unsafe_allow_html=True)
                    if st.button("⬅ Back to Login", use_container_width=True, key="back_to_login_from_signup"):
                        st.session_state.auth_mode = "Login"; st.rerun()

            elif st.session_state.auth_mode == "Forgot Password":
                st.markdown("""
                <div style="padding: 0;">
                    <h2 style="font-size:28px;font-weight:800;color:#111827;margin-bottom:8px;">Reset Password 🔑</h2>
                    <p style="color:#6b7280;font-size:15px;margin-bottom:16px;">Enter your security answer to reset.</p>
                </div>
                """, unsafe_allow_html=True)
                with st.container():
                    with st.form("forgot_form", border=False):
                        reset_user = st.text_input("", placeholder="Username", key="reset_user")
                        reset_sec  = st.text_input("", placeholder="Name of your first pet?", key="reset_sec")
                        reset_pass = st.text_input("", placeholder="New Password", type="password", key="reset_pass")
                        submitted = st.form_submit_button("🔑 Reset Password", use_container_width=True, type="primary")
                        if submitted:
                            if reset_user and reset_sec and reset_pass:
                                success, msg = auth.reset_password(reset_user, reset_sec, reset_pass)
                                if success:
                                    st.success(msg + " You can now login.")
                                else:
                                    st.error(msg)
                            else:
                                st.warning("Please fill in all fields.")
                    st.markdown("<hr style='margin:20px 0;border-color:#e5e7eb;'>", unsafe_allow_html=True)
                    if st.button("⬅ Back to Login", use_container_width=True, key="back_to_login_from_forgot"):
                        st.session_state.auth_mode = "Login"; st.rerun()

else:
    # --- MAIN APPLICATION (LOGGED IN) ---
    
    if "last_viewed_state" not in st.session_state:
        st.session_state.last_viewed_state = f"{st.session_state.current_view}_{st.session_state.active_tab}"
    
    current_state_str = f"{st.session_state.current_view}_{st.session_state.active_tab}"
    if current_state_str != st.session_state.last_viewed_state:
        import streamlit.components.v1 as components
        components.html("""
            <script>
                const p = window.parent;
                if(p) {
                    p.scrollTo({top:0, behavior:'smooth'});
                    const c = p.document.querySelector('.main') || p.document.querySelector('[data-testid="stAppViewContainer"]');
                    if(c) c.scrollTo({top:0, behavior:'smooth'});
                }
            </script>
        """, height=0, width=0)
        st.session_state.last_viewed_state = current_state_str
    # Sidebar
    total_modules = len(MODULES)
    modules_unlocked_count = st.session_state.unlocked_index + 1
    progress = min(modules_unlocked_count / total_modules, 1.0)
    
    st.sidebar.markdown(f"""
    <div class="sidebar-progress-card">
        <div class="sidebar-progress-title">Your Progress</div>
        <div class="sidebar-progress-text">Score ≥ 80% to unlock next module</div>
        <div class="progress-bar-bg">
            <div class="progress-bar-fill" style="width: {progress * 100}%;"></div>
        </div>
        <div class="sidebar-progress-count">
            {min(modules_unlocked_count, total_modules)} / {total_modules} modules
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    with st.sidebar.expander("📖 Content", expanded=True):
        for i, mod in enumerate(MODULES):
            is_unlocked = i <= st.session_state.unlocked_index
            if st.button(f"📄 {mod['title']}", key=f"nav_{i}", disabled=not is_unlocked, use_container_width=True):
                st.session_state.current_view = i
                st.session_state.active_tab = "Materials"
                st.rerun()

    with st.sidebar.expander("🎯 Assessment", expanded=True):
        if st.button("🎯 Knowledge Check", key="nav_quiz", use_container_width=True):
            st.session_state.active_tab = "Quiz"
            if st.session_state.current_view == -1:
                st.session_state.current_view = st.session_state.unlocked_index
            st.rerun()

    with st.sidebar.expander("✨ Support", expanded=True):
        if st.button("✨ Open AI Assistant", key="nav_ai", use_container_width=True):
            st.session_state.active_tab = "AI"
            if st.session_state.current_view == -1:
                st.session_state.current_view = st.session_state.unlocked_index
            st.rerun()

    # Add JS to highlight active sidebar button
    active_idx = st.session_state.current_view if st.session_state.active_tab == "Materials" else (total_modules if st.session_state.active_tab == "Quiz" else total_modules+1)
    
    active_btn_js = f"""
    <script>
    setTimeout(() => {{
        const buttons = window.parent.document.querySelectorAll('[data-testid="stSidebar"] button');
        buttons.forEach(b => b.classList.remove('active-lesson'));
        if (buttons.length > {active_idx}) {{
            if ({st.session_state.current_view} !== -1) {{
                buttons[{active_idx}].classList.add('active-lesson');
            }}
        }}
    }}, 100);
    </script>
    """
    components.html(active_btn_js, height=0)

    # --- MAIN CONTENT ---
    if st.session_state.current_view != st.session_state.last_view:
        st.session_state.last_view = st.session_state.current_view
        js = '''<script>var e=window.parent.document.querySelectorAll('.main, [data-testid="stAppViewContainer"], .stApp');for(let el of e){el.scrollTop=0;}window.parent.scrollTo(0,0);</script>'''
        components.html(js, height=0)
        
    if st.session_state.current_view == -1:
        # HOMEPAGE / DASHBOARD
        st.markdown(f"""
        <div class="welcome-banner" style="background: linear-gradient(135deg, #1e3a8a 0%, #2563eb 60%, #3b82f6 100%); padding: 52px 32px; border-radius: 20px; margin-bottom: 32px; text-align: center; box-shadow: 0 20px 40px rgba(37,99,235,0.25); position: relative; overflow: hidden;">
            <div style="position:absolute;top:-40px;right:-40px;width:200px;height:200px;border-radius:50%;background:rgba(255,255,255,0.05);"></div>
            <div style="position:absolute;bottom:-60px;left:-30px;width:250px;height:250px;border-radius:50%;background:rgba(255,255,255,0.04);"></div>
            <h1 style="font-size: 34px; font-weight: 800; margin-bottom: 14px; margin-top: 18px; line-height: 1.2;">🎓 Welcome back, {st.session_state.username}!</h1>
            <p style="font-size: 16px; margin-bottom: 0; max-width: 560px; margin-left: auto; margin-right: auto; line-height: 1.7;">
                Continue your journey mastering didactic theories and practical teaching methodologies.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button("🚀 Start Learning", use_container_width=True, type="primary"):
                st.session_state.current_view = st.session_state.unlocked_index
                st.session_state.active_tab = "Materials"
                st.rerun()
                
        st.markdown("<h2 style='margin-top: 48px; margin-bottom: 24px; color: #111827;'>📚 Course Modules</h2>", unsafe_allow_html=True)
        
        cols = st.columns(3)
        for i, mod in enumerate(MODULES[:6]):
            col = cols[i % 3]
            is_unlocked = i <= st.session_state.unlocked_index
            badge_cls = "badge-unlocked" if is_unlocked else "badge-locked"
            badge_txt = "✓ Unlocked" if is_unlocked else "🔒 Locked"
            num = i + 1
            
            with col:
                st.markdown(f"""
                <div class="module-card">
                    <div>
                        <span class="module-card-badge {badge_cls}">{badge_txt}</span>
                        <div style="font-size: 11px; color: #94a3b8; font-weight: 600; margin-bottom: 6px;">MODULE {num}</div>
                        <div style="font-weight: 700; color: #111827; font-size: 15px; line-height: 1.4; margin-bottom: 8px;">{mod['title']}</div>
                        <div style="font-size: 13px; color: #6b7280; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;">{mod['description']}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                if is_unlocked:
                    if st.button(f"Open Module {num} ➔", key=f"home_go_{i}", use_container_width=True, type="primary"):
                        st.session_state.current_view = i
                        st.session_state.active_tab = "Materials"
                        st.rerun()
                else:
                    st.button("🔒 Locked", key=f"home_go_{i}", disabled=True, use_container_width=True)

        st.markdown("<h2 style='margin-top: 48px; margin-bottom: 24px; color: #111827;'>✨ AI Assistant</h2>", unsafe_allow_html=True)
        st.markdown("""
        <div style="background-color: white; border: 1px solid #e5e7eb; border-radius: 12px; padding: 24px; display: flex; align-items: center; gap: 24px; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
            <div style="font-size: 48px; line-height: 1;">🤖</div>
            <div>
                <h3 style="margin-top: 0; margin-bottom: 8px; color: #111827;">Ask the AI Assistant</h3>
                <p style="margin: 0; color: #4b5563;">Stuck on a concept? The Didactics AI Assistant is available in every module to explain theories and provide practice scenarios.</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

    else:
        current_mod = MODULES[st.session_state.current_view]
        
        mod_num = st.session_state.current_view + 1
        st.markdown(f"""
        <div style="margin-bottom:6px;">
            <span style="font-size:11px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:#2563eb;">Module {mod_num}</span>
        </div>
        <h1 style="margin-bottom:6px;">{current_mod['title']}</h1>
        <p style="margin-bottom:24px;color:#64748b;">{current_mod['description']}</p>
        """, unsafe_allow_html=True)

        if st.session_state.current_view > st.session_state.unlocked_index:
            st.markdown("<div class='locked-msg'>🔒 This lesson is locked. Pass the previous module's quiz to unlock it!</div>", unsafe_allow_html=True)
        else:
            tab_col1, tab_col2, tab_col3 = st.columns(3)
            with tab_col1:
                if st.button("📖 Materials", key="tab_mat", use_container_width=True,
                             type="primary" if st.session_state.active_tab=="Materials" else "secondary"):
                    st.session_state.active_tab = "Materials"; st.rerun()
            with tab_col2:
                if st.button("📝 Knowledge Check", key="tab_quiz", use_container_width=True,
                             type="primary" if st.session_state.active_tab=="Quiz" else "secondary"):
                    st.session_state.active_tab = "Quiz"; st.rerun()
            with tab_col3:
                if st.button("💬 AI Assistant", key="tab_ai", use_container_width=True,
                             type="primary" if st.session_state.active_tab=="AI" else "secondary"):
                    st.session_state.active_tab = "AI"; st.rerun()

            with st.container(border=True):
                if st.session_state.active_tab == "Materials":
                    PDF_FILES = [
                        "lessons/1) BASIC NOTIONS AND FUNDAMENTALS OF DIDACTICS 1 presentation.pdf",
                        "lessons/2) Basic Notions and Fundamentals of Didactics (Foundations of Didacticic).pdf",
                        "lessons/3) Learning Theories Behaviorism to TDS.pdf",
                        "lessons/4) Methods_and_approaches1_GTM DM ALM SUG SW CLL.pdf",
                        "lessons/5)Methods and approaches in language teaching 2 (1).pdf",
                        "lessons/6)Didactics-Teaching the Four Skills PPT.pdf",
                        "lessons/7) new presentaion for grammar , vocabulary and functions -compressed.pdf",
                        "lessons/8) Approach-compressed.pdf",
                        "lessons/9) Fundamentals of ELT-EFL.pdf",
                        "lessons/10) FUNDAMENTALS of EFL-compressed.pdf"
                    ]
                    pdf_path = PDF_FILES[st.session_state.current_view]
                    if os.path.exists(pdf_path):
                        with open(pdf_path, "rb") as f:
                            pdf_bytes = f.read()
                        
                        st.markdown('''
                        <div class="pdf-container" style="border-bottom:none; border-radius: 12px 12px 0 0; margin-bottom: -1rem;">
                            <div class="pdf-header">Lesson Presentation</div>
                        </div>
                        ''', unsafe_allow_html=True)
                        
                        try:
                            # Render PDF as images using pypdfium2 (prevents all browser download triggers)
                            pdf = pdfium.PdfDocument(pdf_path)
                            with st.container(border=True):
                                st.markdown("<div style='text-align:center; color:#6b7280; font-size:13px; margin-bottom: 16px; padding-top: 8px;'>Scroll down to view all pages</div>", unsafe_allow_html=True)
                                for i in range(len(pdf)):
                                    page = pdf.get_page(i)
                                    pil_image = page.render(scale=2).to_pil()
                                    st.image(pil_image, use_container_width=True)
                        except Exception as e:
                            st.error(f"Error rendering presentation: {e}")
                        

                    else:
                        st.error(f"Could not find PDF file at {pdf_path}")
                        
                elif st.session_state.active_tab == "Quiz":
                    st.markdown("<h3 style='color: #111827;'>Module Assessment</h3>", unsafe_allow_html=True)
                    st.info("You must score **at least 8 out of 10** to unlock the next lesson.")
                    
                    quiz_data = current_mod['quiz']
                    with st.form(key=f"quiz_form_{st.session_state.current_view}"):
                        user_answers = {}
                        for q_idx, q in enumerate(quiz_data):
                            st.markdown(f"<div class='quiz-container'><b style='font-size:1.1rem; color: #111827;'>Question {q_idx + 1}:</b> <span style='color: #4b5563;'>{q['question']}</span></div>", unsafe_allow_html=True)
                            user_answers[q_idx] = st.radio("Select:", q['options'], key=f"q_{st.session_state.current_view}_{q_idx}", index=None, label_visibility="collapsed")
                            st.write("")
                        submit_button = st.form_submit_button("Submit Answers", use_container_width=True)
                        
                    if submit_button:
                        score = sum(1 for i, q in enumerate(quiz_data) if user_answers[i] == q['options'][q['correct_index']])
                        unanswered = sum(1 for i in range(len(quiz_data)) if user_answers[i] is None)
                            
                        if unanswered > 0:
                            st.warning(f"⚠️ You missed {unanswered} question(s).")
                        else:
                            if score > st.session_state.quiz_scores.get(st.session_state.current_view, 0):
                                st.session_state.quiz_scores[st.session_state.current_view] = score
                                save_current_progress()
                                
                            st.write(f"### Score: {score}/10")
                            if score >= 8:
                                st.success("🎉 **Outstanding!**")
                                if st.session_state.current_view == st.session_state.unlocked_index and st.session_state.unlocked_index < total_modules - 1:
                                    st.session_state.unlocked_index += 1
                                    save_current_progress()
                                    st.balloons()
                                    st.rerun() 
                            else:
                                st.error("❌ **Not quite there.** Review the materials and try again.")
                                
                elif st.session_state.active_tab == "AI":
                    st.markdown("<h3 style='color: #111827; margin-bottom: 16px;'>AI Assistant</h3>", unsafe_allow_html=True)
                    
                    chat_container = st.container(height=480)
                    
                    with chat_container:
                        for msg in st.session_state.chat_history:
                            avatar = "user" if msg["role"] == "user" else "assistant"
                            with st.chat_message(msg["role"], avatar=avatar):
                                st.markdown(msg["content"])
                                
                    if prompt := st.chat_input("Ask about didactics..."):
                        st.session_state.chat_history.append({"role": "user", "content": prompt})
                        with chat_container:
                            with st.chat_message("user", avatar="user"):
                                st.markdown(prompt)
                            with st.chat_message("assistant", avatar="assistant"):
                                with st.spinner("Thinking..."):
                                    try:
                                        response = ai_assistant.get_real_response(st.session_state.chat_history)
                                        if not response:
                                            response = "⚠️ Received an empty response from the AI. Please try again."
                                    except Exception as e:
                                        response = f"⚠️ An unexpected error occurred: {str(e)}"
                                    st.markdown(response)
                        st.session_state.chat_history.append({"role": "assistant", "content": response})
