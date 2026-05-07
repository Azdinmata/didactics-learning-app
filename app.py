import streamlit as st
import lesson_data
import ai_assistant
import os

# Set page configuration
st.set_page_config(
    page_title="Didactics Hub - Streamlit Portal",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 1) Session state initialization
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "active_module_idx" not in st.session_state:
    st.session_state.active_module_idx = 0
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "quiz_scores" not in st.session_state:
    st.session_state.quiz_scores = {}

# Premium Custom CSS to make Streamlit look high-end and responsive
st.markdown("""
    <style>
    /* Premium visual overrides */
    .stApp {
        background-color: #0b0f19 !important;
        color: #f3f4f6 !important;
    }
    div[data-testid="stSidebar"] {
        background-color: #0f172a !important;
        border-right: 1px solid rgba(255, 255, 255, 0.08);
    }
    .stButton>button {
        background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 700 !important;
    }
    
    /* Make lesson inline-flex rows wrap beautifully on mobile */
    div[style*="display:flex"], 
    div[style*="display: flex"] {
        flex-wrap: wrap !important;
    }
    
    .info-box {
        flex: 1 1 calc(33.333% - 16px) !important;
        min-width: 240px !important;
        padding: 16px !important;
        margin: 8px 0 !important;
        border-radius: 12px !important;
        color: #1e293b !important; /* Elegant slate color for contrast */
    }

    /* Stop columns or input components from collapsing inappropriately on small screens */
    @media (max-width: 768px) {
        div[data-testid="column"] {
            width: 100% !important;
            flex: 1 1 calc(50% - 1rem) !important;
            min-width: unset !important;
            display: block !important;
        }
        
        /* Force flex container rows to stack vertically on phones */
        div[style*="display:flex"], 
        div[style*="display: flex"] {
            flex-direction: column !important;
            align-items: stretch !important;
        }
        
        .info-box {
            flex: 1 1 100% !important;
            width: 100% !important;
            margin: 6px 0 !important;
        }
    }
    </style>
""", unsafe_allow_html=True)

# 2) Auth Screen
if not st.session_state.logged_in:
    st.title("🎓 Didactics Hub Portal Entrance")
    st.subheader("Sign in to access your course panel")
    
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    
    if st.button("Sign In"):
        if username.strip() and password.strip():
            st.session_state.logged_in = True
            st.session_state.username = username
            st.rerun()
        else:
            st.error("Please enter credentials.")
else:
    # 3) Main Application Interface
    st.sidebar.title("🎓 Didactics Hub")
    st.sidebar.write(f"Welcome back, **Teacher {st.session_state.username}**!")
    
    if st.sidebar.button("Logout 🚪"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.session_state.chat_history = []
        st.rerun()
        
    st.sidebar.markdown("---")
    st.sidebar.subheader("Course Progression")
    
    # Render syllabus modules in sidebar
    modules = lesson_data.MODULES
    
    # Store dynamic selections
    module_options = [f"Module {i+1}: {mod['title']}" for i, mod in enumerate(modules)]
    selected_option = st.sidebar.radio(
        "Select Lesson Module:",
        module_options,
        index=st.session_state.active_module_idx
    )
    
    # Sync selected index
    active_idx = module_options.index(selected_option)
    if active_idx != st.session_state.active_module_idx:
        st.session_state.active_module_idx = active_idx
        st.session_state.chat_history = []  # Clear chat history when switching modules
        st.rerun()
        
    # Main Dashboard Panel
    current_module = modules[st.session_state.active_module_idx]
    
    st.title(current_module["title"])
    st.write(current_module["description"])
    
    tab1, tab2, tab3 = st.tabs(["📖 Lesson Content", "📝 Knowledge Check", "🤖 Socratic AI Tutor"])
    
    with tab1:
        st.markdown(current_module["structured_lesson"], unsafe_allow_html=True)
        
    with tab2:
        st.header("📝 Module Assessment")
        quiz_questions = current_module.get("quiz", [])
        
        user_answers = {}
        for q_idx, q in enumerate(quiz_questions):
            st.subheader(f"Question {q_idx+1}")
            st.write(q["question"])
            user_answers[q_idx] = st.radio(
                "Choose answer:",
                q["options"],
                key=f"q_{st.session_state.active_module_idx}_{q_idx}"
            )
            
        if st.button("Submit Assessment"):
            correct_count = 0
            for q_idx, q in enumerate(quiz_questions):
                selected_ans = user_answers[q_idx]
                correct_ans = q["options"][q["correct_index"]]
                if selected_ans == correct_ans:
                    correct_count += 1
            
            st.session_state.quiz_scores[st.session_state.active_module_idx] = correct_count
            st.success(f"Graded successfully! Score: {correct_count} / {len(quiz_questions)}")
            
    with tab3:
        st.header("🤖 Socratic Didactics Assistant")
        st.write("Ask your Socratic Tutor anything about the active module textbook contents!")
        
        # Display chat history
        for msg in st.session_state.chat_history:
            with st.chat_message(msg["role"]):
                st.write(msg["content"])
                
        # Chat input
        user_prompt = st.chat_input("Ask a pedagogy question...")
        if user_prompt:
            with st.chat_message("user"):
                st.write(user_prompt)
            st.session_state.chat_history.append({"role": "user", "content": user_prompt})
            
            # Fetch AI Socratic Response using our existing ai_assistant helper
            with st.spinner("Tutor is reflecting..."):
                tutor_response = ai_assistant.get_real_response(
                    st.session_state.chat_history,
                    current_module
                )
                
            with st.chat_message("assistant"):
                st.write(tutor_response)
            st.session_state.chat_history.append({"role": "assistant", "content": tutor_response})
