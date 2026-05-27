"""
Auth UI - Premium login/signup page with Google OAuth
"""

import streamlit as st
import requests
from backend.config import settings


def _api(endpoint: str, payload: dict) -> dict:
    try:
        r = requests.post(
            f"{settings.BACKEND_URL}{endpoint}",
            json=payload,
            timeout=15,
        )
        if r.status_code in (200, 201):
            return {"ok": True, "data": r.json()}
        return {"ok": False, "error": r.json().get("detail", "Request failed")}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def render_auth_page():
    """Render the login/signup authentication page."""

    # Full-page auth layout
    st.markdown("""
<div style="min-height:100vh; display:flex; align-items:center; justify-content:center;
            background: var(--bg-primary);">
</div>
""", unsafe_allow_html=True)

    # Centered columns
    _, col, _ = st.columns([1, 1.6, 1])

    with col:
        # ── Hero Header ────────────────────────────────────────────────────────
        st.markdown("""
<div style="text-align:center; padding: 32px 0 24px;">
  <div style="font-size:52px; margin-bottom:12px;">🎯</div>
  <div style="font-family:'Space Grotesk',sans-serif; font-size:32px; font-weight:800;
              background:linear-gradient(135deg,#667eea,#764ba2);
              -webkit-background-clip:text; -webkit-text-fill-color:transparent;
              background-clip:text; letter-spacing:-0.5px;">
    ATSPro
  </div>
  <p style="color:var(--text-secondary); font-size:15px; margin-top:6px;">
    AI-Powered Resume Intelligence Platform
  </p>
  <div style="display:flex; gap:8px; justify-content:center; margin-top:14px; flex-wrap:wrap;">
    <span style="background:rgba(16,185,129,0.12); color:#10b981; padding:4px 12px;
                 border-radius:20px; font-size:11px; font-weight:600;">✓ NLP Scoring</span>
    <span style="background:rgba(102,126,234,0.12); color:#667eea; padding:4px 12px;
                 border-radius:20px; font-size:11px; font-weight:600;">✓ Groq AI Suggestions</span>
    <span style="background:rgba(245,158,11,0.12); color:#f59e0b; padding:4px 12px;
                 border-radius:20px; font-size:11px; font-weight:600;">✓ PDF Reports</span>
  </div>
</div>
""", unsafe_allow_html=True)

        # ── Tab: Login / Signup ─────────────────────────────────────────────
        tab_login, tab_signup = st.tabs(["🔐 Sign In", "✨ Create Account"])

        # ── LOGIN TAB ─────────────────────────────────────────────────────────
        with tab_login:
            st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

            with st.form("login_form", clear_on_submit=False):
                email    = st.text_input("📧 Email", placeholder="you@example.com", key="login_email")
                password = st.text_input("🔒 Password", type="password", placeholder="••••••••", key="login_pw")
                submitted = st.form_submit_button("Sign In →", use_container_width=True)

                if submitted:
                    if not email or not password:
                        st.error("Please enter email and password")
                    else:
                        with st.spinner("Signing you in..."):
                            result = _api("/auth/login", {"email": email, "password": password})
                        if result["ok"]:
                            data = result["data"]
                            st.session_state.authenticated = True
                            st.session_state.token = data["access_token"]
                            st.session_state.user  = data["user"]
                            st.success("✅ Welcome back!")
                            st.rerun()
                        else:
                            st.error(f"❌ {result['error']}")

            # Google OAuth
            st.markdown("<div style='text-align:center; padding:12px 0; color:var(--text-muted); font-size:13px;'>— or —</div>", unsafe_allow_html=True)
            google_url = f"{settings.BACKEND_URL}/auth/google"
            st.markdown(f"""
<div style="text-align:center;">
  <a href="{google_url}" target="_self" style="text-decoration:none;">
    <div style="display:inline-flex; align-items:center; gap:10px; padding:11px 28px;
                background:var(--bg-card); border:1px solid var(--border); border-radius:12px;
                font-size:14px; font-weight:600; color:var(--text-primary); cursor:pointer;
                transition:all 0.2s ease;">
      <svg width="18" height="18" viewBox="0 0 48 48">
        <path fill="#EA4335" d="M24 9.5c3.5 0 6.6 1.2 9.1 3.2l6.8-6.8C35.8 2.4 30.3 0 24 0 14.7 0 6.7 5.4 2.6 13.4l7.9 6.1C12.5 13 17.8 9.5 24 9.5z"/>
        <path fill="#4285F4" d="M46.5 24.5c0-1.6-.1-3.1-.4-4.5H24v8.5h12.7c-.5 2.9-2.2 5.4-4.7 7l7.2 5.6c4.2-3.9 6.3-9.6 6.3-16.6z"/>
        <path fill="#FBBC05" d="M10.5 28.5c-.6-1.6-.9-3.2-.9-5s.3-3.4.9-5l-7.9-6.1C.9 15.3 0 19.5 0 24s.9 8.7 2.6 12.6l7.9-6.1z"/>
        <path fill="#34A853" d="M24 48c6.3 0 11.6-2.1 15.5-5.7l-7.2-5.6c-2.1 1.4-4.8 2.3-8.3 2.3-6.2 0-11.5-3.5-13.5-9L2.6 36.1C6.7 42.6 14.7 48 24 48z"/>
      </svg>
      Continue with Google
    </div>
  </a>
</div>
""", unsafe_allow_html=True)

        # ── SIGNUP TAB ────────────────────────────────────────────────────────
        with tab_signup:
            st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

            with st.form("signup_form", clear_on_submit=False):
                full_name = st.text_input("👤 Full Name", placeholder="Jane Doe", key="signup_name")
                email     = st.text_input("📧 Email", placeholder="you@example.com", key="signup_email")
                password  = st.text_input("🔒 Password", type="password", placeholder="Min 8 characters", key="signup_pw")
                confirm   = st.text_input("🔒 Confirm Password", type="password", placeholder="Repeat password", key="signup_confirm")
                submitted = st.form_submit_button("Create Account →", use_container_width=True)

                if submitted:
                    if not all([full_name, email, password, confirm]):
                        st.error("All fields are required")
                    elif len(password) < 8:
                        st.error("Password must be at least 8 characters")
                    elif password != confirm:
                        st.error("Passwords do not match")
                    else:
                        with st.spinner("Creating your account..."):
                            result = _api("/auth/signup", {
                                "email": email,
                                "password": password,
                                "full_name": full_name,
                            })
                        if result["ok"]:
                            data = result["data"]
                            st.session_state.authenticated = True
                            st.session_state.token = data["access_token"]
                            st.session_state.user  = data["user"]
                            st.success("🎉 Account created! Welcome to ATSPro.")
                            st.rerun()
                        else:
                            st.error(f"❌ {result['error']}")

        # ── Footer ─────────────────────────────────────────────────────────────
        st.markdown("""
<div style="text-align:center; padding:24px 0 0; color:var(--text-muted); font-size:11px;">
  Protected by enterprise-grade security · Your data stays private
</div>
""", unsafe_allow_html=True)
