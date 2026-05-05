import streamlit as st
import os
import base64
from lesson_data import MODULES
import auth
import streamlit.components.v1 as components
import ai_assistant

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Didactics Hub",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CUSTOM CSS FOR NEW THEME ---
st.markdown("""
    <style>
    /* Global Styles */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    
    * {
        font-family: 'Inter', system-ui, sans-serif !important;
    }
    
    /* Hide default Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stAppDeployButton {display:none;}
    
    /* App Background */
    .stApp {
        background-color: #f9fafb !important;
        background-image: none !important;
    }
    
    /* Main container max-width & centering */
    .block-container {
        max-width: 1150px !important;
        padding-top: 5rem !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
    }
    
    /* Top Navbar (stHeader) */
    header[data-testid="stHeader"] {
        background-color: #ffffff !important;
        height: 64px !important;
        border-bottom: 1px solid #e5e7eb !important;
        box-shadow: none !important;
    }
    
    header[data-testid="stHeader"]::before {
        content: "🎓 Didactics Hub";
        position: absolute;
        left: 24px;
        top: 18px;
        font-size: 1.25rem;
        font-weight: 700;
        color: #111827;
        z-index: 10;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #ffffff !important;
        background-image: none !important;
        border-right: 1px solid #e5e7eb !important;
        min-width: 280px !important;
        max-width: 280px !important;
    }
    
    [data-testid="stSidebar"] * {
        color: #111827 !important;
    }
    
    /* Sidebar Buttons (Lesson List) */
    [data-testid="stSidebar"] .stButton > button {
        background-color: transparent !important;
        border: none !important;
        box-shadow: none !important;
        color: #4b5563 !important;
        font-weight: 500 !important;
        text-align: left !important;
        justify-content: flex-start !important;
        padding: 10px 16px !important;
        border-radius: 10px !important;
        width: 100% !important;
        transition: all 0.2s ease;
        margin-bottom: 4px;
    }
    [data-testid="stSidebar"] .stButton > button:hover {
        background-color: #f3f4f6 !important;
        color: #111827 !important;
    }
    
    [data-testid="stSidebar"] .stButton > button[disabled] {
        opacity: 0.6 !important;
        color: #9ca3af !important;
    }
    [data-testid="stSidebar"] .stButton > button[disabled] p::after {
        content: "🔒";
        position: absolute;
        right: 16px;
    }
    
    [data-testid="stSidebar"] .stButton > button.active-lesson {
        background-color: #eff6ff !important;
        color: #2563eb !important;
        font-weight: 600 !important;
    }
    
    /* Typography Overrides */
    h1 {
        color: #111827 !important;
        font-size: 32px !important;
        font-weight: 800 !important;
        line-height: 1.2 !important;
        margin-bottom: 4px !important;
    }
    h2 {
        color: #111827 !important;
        font-size: 24px !important;
        font-weight: 700 !important;
    }
    h3 {
        color: #111827 !important;
        font-size: 18px !important;
        font-weight: 600 !important;
    }
    p, li, span {
        color: #4b5563 !important;
        font-size: 15px !important;
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
        transition: border-color 0.15s ease-in-out, box-shadow 0.15s ease-in-out;
    }
    .stTextInput > div > div > input:focus {
        border-color: #2563eb !important;
        box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1) !important;
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
        gap: 8px;
        border-bottom: none !important;
        margin-bottom: 24px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: transparent !important;
        border: none !important;
        border-radius: 9999px !important;
        padding: 8px 16px !important;
        margin: 0 !important;
        color: #6b7280 !important;
        font-weight: 500 !important;
        transition: all 0.2s ease;
    }
    .stTabs [data-baseweb="tab"]:hover {
        background-color: #f3f4f6 !important;
        color: #111827 !important;
    }
    .stTabs [aria-selected="true"] {
        background-color: #eff6ff !important;
        color: #2563eb !important;
        font-weight: 600 !important;
    }
    .stTabs [data-baseweb="tab-highlight"] {
        display: none !important;
    }
    
    /* Main Content Card (Wrapper for Tabs) */
    [data-testid="stVerticalBlock"] > [data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #ffffff;
        border-radius: 16px !important;
        padding: 24px !important;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06) !important;
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
        background-color: #ffffff;
        border-radius: 12px;
        padding: 16px;
        border: 1px solid #e5e7eb;
        box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
        margin-bottom: 24px;
    }
    .sidebar-progress-title {
        font-size: 0.85rem;
        font-weight: 700;
        color: #111827;
        margin-bottom: 4px;
    }
    .sidebar-progress-text {
        font-size: 0.75rem;
        color: #6b7280;
        margin-bottom: 12px;
    }
    .progress-bar-bg {
        width: 100%;
        height: 6px;
        background-color: #e5e7eb;
        border-radius: 9999px;
        overflow: hidden;
    }
    .progress-bar-fill {
        height: 100%;
        background-color: #2563eb;
        border-radius: 9999px;
        transition: width 0.5s ease-in-out;
    }
    
    /* Primary buttons */
    .stButton > button[kind="primary"] {
        background-color: #2563eb !important;
        color: white !important;
        border-radius: 8px !important;
        border: none !important;
        font-weight: 600 !important;
        padding: 10px 16px !important;
    }
    .stButton > button[kind="primary"]:hover {
        background-color: #1d4ed8 !important;
    }
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
    st.session_state.current_view = 0
if 'last_view' not in st.session_state:
    st.session_state.last_view = -1
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = [{"role": "assistant", "content": "Hello! I am your Didactics AI Assistant. Ask me to explain a concept or give you a practice scenario!"}]
if 'chat_open' not in st.session_state:
    st.session_state.chat_open = False

def save_current_progress():
    auth.save_user_progress(st.session_state.username, st.session_state.unlocked_index, st.session_state.quiz_scores)

# --- TOP BAR RENDERING ---
if st.session_state.logged_in:
    col_profile, col_logout = st.columns([2, 1])
    with col_profile:
        st.markdown('<div id="nav-anchor"></div>', unsafe_allow_html=True)
        st.markdown(f"<div style='text-align: right; font-weight: 600; font-size: 0.95rem; color: #374151; padding-top: 8px;'>👤 {st.session_state.username}</div>", unsafe_allow_html=True)
    with col_logout:
        if st.button("Logout", key="top_logout_btn", help="Sign out of your account"):
            st.session_state.logged_in = False
            st.session_state.username = ""
            st.rerun()

    components.html("""
    <script>
        const anchor = window.parent.document.getElementById('nav-anchor');
        if(anchor) {
            const row = anchor.closest('div[data-testid="stHorizontalBlock"]');
            if(row) {
                row.style.position = 'fixed';
                row.style.top = '12px';
                row.style.right = '20px';
                row.style.width = '300px';
                row.style.zIndex = '999999';
            }
        }
    </script>
    """, height=0)


# --- ROUTER: AUTHENTICATION ---
if not st.session_state.logged_in:
    if 'auth_mode' not in st.session_state:
        st.session_state.auth_mode = "Login"

    # Inject Login-Specific CSS
    st.markdown("""
    <style>
    /* Hide Sidebar and Top Navbar */
    [data-testid="collapsedControl"] {display: none !important;}
    [data-testid="stSidebar"] {display: none !important;}
    header[data-testid="stHeader"] {display: none !important;}
    
    /* Login Background */
    .stApp {
        background: linear-gradient(135deg, #f8fafc, #eef2ff) !important;
    }
    
    /* Center the container and shrink max width to fit the card */
    .block-container {
        display: flex !important;
        flex-direction: column !important;
        justify-content: center !important;
        align-items: center !important;
        min-height: 100vh !important;
        padding-top: 0 !important;
        max-width: 480px !important;
    }
    
    /* Style the native Streamlit card */
    [data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #ffffff !important;
        border-radius: 24px !important;
        padding: 32px !important;
        box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.05), 0 8px 10px -6px rgba(0, 0, 0, 0.01) !important;
        border: 1px solid #e5e7eb !important;
        width: 100% !important;
    }
    
    /* Form Inputs */
    .stTextInput > div > div > input {
        height: 48px !important;
        border-radius: 12px !important;
        font-size: 15px !important;
        border: 1px solid #d1d5db !important;
    }
    
    /* Primary Login Button */
    .stButton > button[kind="primary"] {
        height: 48px !important;
        border-radius: 12px !important;
        font-weight: 600 !important;
        font-size: 16px !important;
        background-color: #2563eb !important;
    }
    .stButton > button[kind="primary"]:hover {
        background-color: #1d4ed8 !important;
    }
    
    /* Secondary Buttons */
    .stButton > button[kind="secondary"] {
        height: 44px !important;
        border-radius: 12px !important;
        border: 1px solid #e5e7eb !important;
        background-color: #ffffff !important;
        color: #374151 !important;
        font-weight: 500 !important;
    }
    .stButton > button[kind="secondary"]:hover {
        background-color: #f9fafb !important;
        border-color: #d1d5db !important;
    }
    
    /* Mobile adjustments */
    @media (max-width: 768px) {
        .block-container {
            max-width: 100% !important;
            padding: 24px !important;
        }
        [data-testid="stVerticalBlockBorderWrapper"] {
            padding: 24px 20px !important;
        }
    }
    </style>
    """, unsafe_allow_html=True)
    
    with st.container(border=True):
        st.markdown("<div style='text-align:center; font-size: 40px; margin-bottom: 10px;'>🎓</div>", unsafe_allow_html=True)
        st.markdown("<h2 style='text-align:center; color: #111827; margin-bottom: 5px; font-size: 26px;'>Welcome to Didactics Hub</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align:center; color: #6b7280; font-size: 15px; margin-bottom: 30px;'>Sign in to continue your learning journey.</p>", unsafe_allow_html=True)
        
        if st.session_state.auth_mode == "Login":
            st.markdown("<h3 style='margin-bottom: 16px; font-size: 18px;'>Sign In</h3>", unsafe_allow_html=True)
            username = st.text_input("Username", key="login_user")
            password = st.text_input("Password", type="password", key="login_pass")
            
            st.write("")
            if st.button("Sign In", use_container_width=True, type="primary"):
                success, msg, user_data = auth.verify_login(username, password)
                if success:
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.session_state.unlocked_index = user_data.get("unlocked_index", 0)
                    st.session_state.quiz_scores = user_data.get("quiz_scores", {})
                    st.rerun()
                else:
                    st.error(msg)
                    
            st.markdown("<hr style='margin: 24px 0; border-color: #e5e7eb;'>", unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Create Account", use_container_width=True):
                    st.session_state.auth_mode = "Sign Up"
                    st.rerun()
            with col2:
                if st.button("Forgot Password?", use_container_width=True):
                    st.session_state.auth_mode = "Forgot Password"
                    st.rerun()
    
        elif st.session_state.auth_mode == "Sign Up":
            st.markdown("<h3 style='margin-bottom: 16px; font-size: 18px;'>Create Account</h3>", unsafe_allow_html=True)
            new_user = st.text_input("Choose Username", key="signup_user")
            new_pass = st.text_input("Choose Password", type="password", key="signup_pass")
            sec_ans = st.text_input("Security Question: Name of your first pet?", key="signup_sec")
            
            st.write("")
            if st.button("Create Account", use_container_width=True, type="primary"):
                if new_user and new_pass and sec_ans:
                    success, msg = auth.create_user(new_user, new_pass, sec_ans)
                    if success:
                        st.success(msg + " You can now login.")
                    else:
                        st.error(msg)
                else:
                    st.warning("Please fill in all fields.")
                    
            st.markdown("<hr style='margin: 24px 0; border-color: #e5e7eb;'>", unsafe_allow_html=True)
            if st.button("Back to Login", use_container_width=True):
                st.session_state.auth_mode = "Login"
                st.rerun()
    
        elif st.session_state.auth_mode == "Forgot Password":
            st.markdown("<h3 style='margin-bottom: 16px; font-size: 18px;'>Reset Password</h3>", unsafe_allow_html=True)
            reset_user = st.text_input("Username", key="reset_user")
            reset_sec = st.text_input("Security Question: Name of your first pet?", key="reset_sec")
            reset_pass = st.text_input("New Password", type="password", key="reset_pass")
            
            st.write("")
            if st.button("Reset Password", use_container_width=True, type="primary"):
                if reset_user and reset_sec and reset_pass:
                    success, msg = auth.reset_password(reset_user, reset_sec, reset_pass)
                    if success:
                        st.success(msg + " You can now login with your new password.")
                    else:
                        st.error(msg)
                else:
                    st.warning("Please fill in all fields.")
                    
            st.markdown("<hr style='margin: 24px 0; border-color: #e5e7eb;'>", unsafe_allow_html=True)
            if st.button("Back to Login", use_container_width=True):
                st.session_state.auth_mode = "Login"
                st.rerun()

else:
    # --- MAIN APPLICATION (LOGGED IN) ---
    
    # Sidebar
    total_modules = len(MODULES)
    modules_unlocked_count = st.session_state.unlocked_index + 1
    progress = min(modules_unlocked_count / total_modules, 1.0)
    
    st.sidebar.markdown(f"""
    <div class="sidebar-progress-card">
        <div class="sidebar-progress-title">Progression</div>
        <div class="sidebar-progress-text">Reach 80% to unlock next</div>
        <div class="progress-bar-bg">
            <div class="progress-bar-fill" style="width: {progress * 100}%;"></div>
        </div>
        <div style="text-align: right; font-size: 0.75rem; color: #6b7280; font-weight: 600; margin-top: 8px;">
            {min(modules_unlocked_count, total_modules)} / {total_modules} modules
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    for i, mod in enumerate(MODULES):
        is_unlocked = i <= st.session_state.unlocked_index
        # We rely on CSS ::after to render the lock/unlock emoji, so we just pass the title!
        if st.sidebar.button(mod['title'], key=f"nav_{i}", disabled=not is_unlocked, use_container_width=True):
            st.session_state.current_view = i
            st.rerun()

    # Add JS to highlight active sidebar button
    active_btn_js = f"""
    <script>
    setTimeout(() => {{
        const buttons = window.parent.document.querySelectorAll('[data-testid="stSidebar"] button');
        if (buttons.length > {st.session_state.current_view}) {{
            buttons[{st.session_state.current_view}].classList.add('active-lesson');
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
        
    current_mod = MODULES[st.session_state.current_view]
    
    st.markdown(f"<h1>{current_mod['title']}</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='margin-bottom: 24px;'>{current_mod['description']}</p>", unsafe_allow_html=True)
    
    if st.session_state.current_view > st.session_state.unlocked_index:
        st.markdown("<div class='locked-msg'>🔒 This lesson is locked. Pass the previous module's quiz to unlock it!</div>", unsafe_allow_html=True)
    else:
        # We use a native container instead of raw HTML to prevent invisible text clipping
        with st.container(border=True):
            tab1, tab2 = st.tabs(["📚 Lesson Materials", "🧠 Knowledge Check"])
            
            with tab1:
                PDF_FILES = [
                    "lessons/1) BASIC NOTIONS AND FUNDAMENTALS OF DIDACTICS 1 presentation.pdf",
                    "lessons/2) Basic Notions and Fundamentals of Didactics (Foundations of Didacticic).pdf",
                    "lessons/3) Learning Theories Behaviorism to TDS.pdf",
                    "lessons/3Outline English teaching dedactics (1)_250512_111430.pdf",
                    "lessons/4) Methods_and_approaches1_GTM DM ALM SUG SW CLL.pdf",
                    "lessons/5)Methods and approaches in language teaching 2 (1).pdf",
                    "lessons/6)Didactics-Teaching the Four Skills PPT.pdf",
                    "lessons/7) new presentaion for grammar , vocabulary and functions .pdf",
                    "lessons/8) Approach.pdf",
                    "lessons/9) Fundamentals of ELT-EFL.pdf",
                    "lessons/10) FUNDAMENTALS of EFL.pdf"
                ]
                pdf_path = PDF_FILES[st.session_state.current_view]
                if os.path.exists(pdf_path):
                    with open(pdf_path, "rb") as f:
                        base64_pdf = base64.b64encode(f.read()).decode('utf-8')
                    pdf_display = f'''
                    <div class="pdf-container">
                        <div class="pdf-header">📄 Lesson Presentation</div>
                        <iframe src="data:application/pdf;base64,{base64_pdf}#toolbar=0" width="100%" height="700px" type="application/pdf" style="border: none;"></iframe>
                    </div>
                    '''
                    st.markdown(pdf_display, unsafe_allow_html=True)
                else:
                    st.error(f"Could not find PDF file at {pdf_path}")
                    
            with tab2:
                st.markdown("<h3 style='color: #2980b9;'>Module Assessment</h3>", unsafe_allow_html=True)
                st.info("You must score **at least 8 out of 10** to unlock the next lesson.")
                
                quiz_data = current_mod['quiz']
                with st.form(key=f"quiz_form_{st.session_state.current_view}"):
                    user_answers = {}
                    for q_idx, q in enumerate(quiz_data):
                        st.markdown(f"<div class='quiz-container'><b style='font-size:1.1rem;'>Question {q_idx + 1}:</b> {q['question']}</div>", unsafe_allow_html=True)
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

    # --- FLOATING AI PANEL ---
    if not st.session_state.chat_open:
        st.button("💬 Chat with AI", key="toggle_chat_btn", on_click=lambda: st.session_state.update(chat_open=True))
        components.html("""
        <script>
            const btn = window.parent.document.querySelector('button[kind="secondary"][aria-label="💬 Chat with AI"]');
            if (btn) {
                btn.style.position = 'fixed';
                btn.style.bottom = '24px';
                btn.style.right = '24px';
                btn.style.zIndex = '999999';
                btn.style.borderRadius = '50px';
                btn.style.backgroundColor = '#2b7bb9';
                btn.style.color = 'white';
                btn.style.boxShadow = '0 10px 20px rgba(0,0,0,0.2)';
                btn.style.border = 'none';
                btn.style.padding = '10px 20px';
                btn.style.fontWeight = 'bold';
                btn.style.fontSize = '1.1rem';
                btn.style.cursor = 'pointer';
                const parentDiv = btn.closest('div[data-testid="stVerticalBlock"]');
                if (parentDiv) parentDiv.style.minHeight = '0';
            }
        </script>
        """, height=0)
    else:
        chat_wrapper = st.container()
        with chat_wrapper:
            st.markdown('<div class="floating-chat-anchor"></div>', unsafe_allow_html=True)
            
            col1, col2 = st.columns([4, 1])
            with col1:
                st.markdown("<h4 style='margin:0; padding-top: 5px; color: #1a365d;'>🤖 AI Assistant</h4><div style='color: gray; font-size: 0.8rem; margin-top:-5px;'>Didactics Assistant</div>", unsafe_allow_html=True)
            with col2:
                if st.button("✖", key="close_chat_btn", help="Close chat"):
                    st.session_state.chat_open = False
                    st.rerun()
                    
            st.markdown("<hr style='margin: 10px 0; border-color: #e5e7eb;'>", unsafe_allow_html=True)
            
            import markdown
            chat_html = "<div id='chat-messages' style='height: 400px; overflow-y: auto; padding: 15px; background-color: #f7f7f8; border-radius: 12px; margin-bottom: 10px; display: flex; flex-direction: column; scroll-behavior: smooth;'>"
            for msg in st.session_state.chat_history:
                if msg["role"] == "user":
                    chat_html += f'''
                    <div style='align-self: flex-end; background-color: #2563eb; color: white; padding: 10px 15px; border-radius: 18px 18px 0px 18px; max-width: 85%; box-shadow: 0 2px 5px rgba(0,0,0,0.05); font-size: 0.95rem; line-height: 1.4; margin-bottom: 15px;'>
                        {msg["content"]}
                    </div>
                    '''
                else:
                    html_content = markdown.markdown(msg["content"])
                    chat_html += f'''
                    <div style='align-self: flex-start; background-color: white; color: #1f2937; padding: 10px 15px; border-radius: 18px 18px 18px 0px; max-width: 85%; box-shadow: 0 2px 5px rgba(0,0,0,0.05); font-size: 0.95rem; line-height: 1.4; border: 1px solid #e5e7eb; margin-bottom: 15px;'>
                        {html_content}
                    </div>
                    '''
            chat_html += "</div>"
            
            chat_html += """
            <script>
                setTimeout(() => {
                    const chatBoxes = window.parent.document.querySelectorAll('#chat-messages');
                    chatBoxes.forEach(box => {
                        box.scrollTop = box.scrollHeight;
                    });
                }, 100);
            </script>
            """
            
            st.markdown(chat_html, unsafe_allow_html=True)
            
            if prompt := st.chat_input("Ask about didactics..."):
                st.session_state.chat_history.append({"role": "user", "content": prompt})
                st.rerun()
                
        if st.session_state.chat_history[-1]["role"] == "user":
            with chat_wrapper:
                with st.spinner("Thinking..."):
                    try:
                        response = ai_assistant.get_real_response(st.session_state.chat_history)
                        if not response:
                            response = "⚠️ Received an empty response from the AI. Please try again."
                    except Exception as e:
                        response = f"⚠️ An unexpected error occurred: {str(e)}"
                    
                st.session_state.chat_history.append({"role": "assistant", "content": response})
                st.rerun()

        components.html("""
        <script>
            setTimeout(() => {
                const anchor = window.parent.document.querySelector('.floating-chat-anchor');
                if (anchor) {
                    const block = anchor.closest('div[data-testid="stVerticalBlock"]');
                    if (block) {
                        block.style.position = 'fixed';
                        block.style.bottom = '24px';
                        block.style.right = '24px';
                        block.style.width = '420px';
                        block.style.height = '620px';
                        block.style.backgroundColor = 'white';
                        block.style.borderRadius = '18px';
                        block.style.boxShadow = '0 20px 50px rgba(0,0,0,0.18)';
                        block.style.border = '1px solid #e5e7eb';
                        block.style.zIndex = '999999';
                        block.style.overflow = 'hidden';
                        block.style.padding = '15px';
                        block.style.display = 'flex';
                        block.style.flexDirection = 'column';
                        
                        if (window.innerWidth <= 768) {
                            block.style.width = 'calc(100vw - 24px)';
                            block.style.height = '75vh';
                            block.style.right = '12px';
                            block.style.bottom = '12px';
                        }
                    }
                }
            }, 100);
        </script>
        """, height=0)
