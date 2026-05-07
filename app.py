import streamlit as st
import threading
import time
import os

# Set page configurations to widen the layout completely for edge-to-edge aesthetics
st.set_page_config(
    page_title="Didactics Hub",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Hide Streamlit's default margins, header, and footer to give a clean white-label embedded experience!
st.markdown("""
    <style>
        /* Hide default Streamlit visual headers/footers */
        #MainMenu, header, footer {visibility: hidden;}
        
        /* Clear all default layout paddings and stretch block containers to screen edge */
        div.block-container {
            padding: 0 !important;
            margin: 0 !important;
            max-width: 100% !important;
            height: 100vh !important;
        }
        
        /* Make standard iframe fill the entire viewport flawlessly */
        iframe {
            border: none !important;
            width: 100vw !important;
            height: 100vh !important;
            display: block;
        }
        
        /* Prevent body scrolls outside the iframe context */
        body {
            overflow: hidden !important;
        }
    </style>
""", unsafe_allow_html=True)

# Helper function to run Flask in a background thread
def run_flask():
    from server import app
    # Run on local loopback only so that users on the internet can ONLY access the app via the secure Streamlit cloud interface!
    app.run(host="127.0.0.1", port=5000, debug=False, use_reloader=False)

# Start Flask only once using Streamlit session state caching to prevent duplicate threads!
if "flask_started" not in st.session_state:
    st.session_state["flask_started"] = True
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    
    # Give Flask a brief second to bind to Port 5000 and initialize
    time.sleep(1.0)

# Render the local Flask app inside a full-viewport CSS breakout iframe
# This breaks out of Streamlit's container limits, completely removing double scrollbars, outer screen bouncing, or frame-jumping!
st.components.v1.html("""
    <iframe src="http://127.0.0.1:5000/" style="position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; border: none; margin: 0; padding: 0; z-index: 999999; overflow: hidden;"></iframe>
""", height=0, width=0)
