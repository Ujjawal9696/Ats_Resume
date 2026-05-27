"""
ATS Resume Scorer - Main Streamlit Application
Premium SaaS UI with dark/light mode, glassmorphism, animations
"""

import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from frontend.styles.theme import inject_css
from frontend.auth.auth_ui import render_auth_page
from frontend.pages.analyzer import render_analyzer_page
from frontend.pages.dashboard import render_dashboard_page
from frontend.pages.history import render_history_page
from frontend.pages.settings import render_settings_page
from frontend.components.sidebar import render_sidebar

# ── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="ATS Resume Scorer | AI-Powered Resume Analyzer",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "Get help": "https://github.com/your-repo/ats-scorer",
        "Report a bug": "https://github.com/your-repo/ats-scorer/issues",
        "About": "## 🎯 ATS Resume Scorer\nAI-powered resume analysis platform",
    },
)

# ── Inject Global CSS ─────────────────────────────────────────────────────────
inject_css()

# ── Session State Defaults ────────────────────────────────────────────────────
defaults = {
    "authenticated": False,
    "token": None,
    "user": None,
    "current_page": "analyzer",
    "dark_mode": True,
    "analysis_result": None,
    "resume_id": None,
    "resume_text": None,
    "resume_parsed": None,
    "upload_done": False,
    "analysis_done": False,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# Check URL token (from Google OAuth redirect)
query_params = st.query_params
if "token" in query_params and not st.session_state.authenticated:
    st.session_state.token = query_params["token"]
    st.session_state.authenticated = True
    st.query_params.clear()

# ── Routing ────────────────────────────────────────────────────────────────────
if not st.session_state.authenticated:
    render_auth_page()
else:
    page = render_sidebar()
    if page == "analyzer":
        render_analyzer_page()
    elif page == "dashboard":
        render_dashboard_page()
    elif page == "history":
        render_history_page()
    elif page == "settings":
        render_settings_page()
