"""
Settings Page - User profile and app preferences
"""

import streamlit as st
import requests
from backend.config import settings


def _headers():
    return {"Authorization": f"Bearer {st.session_state.token}"}


def render_settings_page():
    st.markdown("""
<div class="page-header slide-in">
  <h1>⚙️ Settings</h1>
  <p>Manage your profile, preferences, and account</p>
</div>
""", unsafe_allow_html=True)

    user  = st.session_state.get("user", {})
    tab1, tab2, tab3 = st.tabs(["👤 Profile", "🎨 Preferences", "📦 API & Export"])

    # ── Profile Tab ──────────────────────────────────────────────────────────
    with tab1:
        st.markdown("#### Your Profile")
        name_val  = user.get("full_name", "")
        email_val = user.get("email", "")
        plan_val  = user.get("plan", "free").upper()
        count_val = user.get("analyses_count", 0)

        # Avatar
        letter = (name_val or email_val or "U")[0].upper()
        st.markdown(f"""
<div style="display:flex; align-items:center; gap:20px; margin-bottom:24px;">
  <div style="width:72px; height:72px; border-radius:50%;
              background:linear-gradient(135deg,#667eea,#764ba2);
              display:flex; align-items:center; justify-content:center;
              font-size:30px; font-weight:700; color:white;">
    {letter}
  </div>
  <div>
    <div style="font-size:18px; font-weight:700; color:var(--text-primary);">{name_val or 'User'}</div>
    <div style="font-size:13px; color:var(--text-muted);">{email_val}</div>
    <div style="margin-top:6px;">
      <span class="tag tag-info">{plan_val} PLAN</span>
      <span style="margin-left:8px; font-size:12px; color:var(--text-muted);">
        {count_val} analyses run
      </span>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            new_name = st.text_input("Full Name", value=name_val, key="settings_name")
        with col2:
            st.text_input("Email", value=email_val, disabled=True,
                          help="Email cannot be changed", key="settings_email")

        if st.button("💾 Save Changes", key="save_profile"):
            st.session_state.user["full_name"] = new_name
            st.success("✅ Profile updated!")

        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown("#### 🔐 Change Password")
        col_a, col_b = st.columns(2)
        with col_a:
            new_pw = st.text_input("New Password", type="password", key="new_pw")
        with col_b:
            confirm_pw = st.text_input("Confirm Password", type="password", key="confirm_pw")
        if st.button("🔒 Update Password", key="update_pw"):
            if new_pw and new_pw == confirm_pw and len(new_pw) >= 8:
                st.success("✅ Password updated")
            elif new_pw != confirm_pw:
                st.error("Passwords do not match")
            else:
                st.error("Password must be at least 8 characters")

    # ── Preferences Tab ───────────────────────────────────────────────────────
    with tab2:
        st.markdown("#### 🎨 Appearance")
        dark = st.toggle("Dark Mode", value=st.session_state.get("dark_mode", True),
                         key="settings_dark")
        if dark != st.session_state.get("dark_mode", True):
            st.session_state.dark_mode = dark
            st.rerun()

        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown("#### 🔔 Analysis Defaults")
        st.selectbox("Default Groq Model",
                     ["llama3-70b-8192", "llama3-8b-8192", "mixtral-8x7b-32768"],
                     key="pref_model")
        st.slider("Max Skills to Extract", 10, 50, 30, key="pref_max_skills")
        st.slider("Max Keywords to Extract", 10, 60, 40, key="pref_max_keywords")
        st.markdown("""
<div style="background:rgba(102,126,234,0.08); border:1px solid rgba(102,126,234,0.2);
            border-radius:12px; padding:14px 18px; margin-top:16px;">
  <div style="font-size:13px; color:#667eea; font-weight:600; margin-bottom:4px;">
    💡 Pro Tip
  </div>
  <div style="font-size:12px; color:var(--text-secondary); line-height:1.5;">
    Use <strong>llama3-70b-8192</strong> for the most detailed AI suggestions.
    Switch to <strong>llama3-8b-8192</strong> for faster but lighter analysis.
  </div>
</div>
""", unsafe_allow_html=True)

    # ── API & Export Tab ─────────────────────────────────────────────────────
    with tab3:
        st.markdown("#### 🔑 API Configuration")
        st.markdown("<p style='color:var(--text-muted);font-size:13px;'>Keys are loaded from your .env file</p>",
                    unsafe_allow_html=True)

        cfg_items = [
            ("GROQ_API_KEY",     settings.GROQ_API_KEY,    "Groq (LLM)"),
            ("SUPABASE_URL",     settings.SUPABASE_URL,    "Supabase"),
            ("BACKEND_URL",      settings.BACKEND_URL,     "Backend API"),
        ]
        for key, val, label in cfg_items:
            masked = val[:8] + "••••••••" if val and len(val) > 8 else "Not set"
            color  = "#10b981" if val else "#ef4444"
            st.markdown(f"""
<div style="display:flex; align-items:center; justify-content:space-between;
            padding:12px 16px; background:var(--bg-card); border:1px solid var(--border);
            border-radius:12px; margin-bottom:8px;">
  <div>
    <div style="font-size:13px; font-weight:600; color:var(--text-primary);">{label}</div>
    <div style="font-size:11px; font-family:monospace; color:var(--text-muted); margin-top:2px;">{key}</div>
  </div>
  <span style="background:{'rgba(16,185,129,0.12)' if val else 'rgba(239,68,68,0.12)'};
               color:{color}; padding:4px 12px; border-radius:8px; font-size:11px; font-weight:600;">
    {'● Connected' if val else '○ Not set'}
  </span>
</div>
""", unsafe_allow_html=True)

        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown("#### 📤 Export Data")
        if st.button("📊 Export All Analyses as JSON", key="export_json"):
            st.info("Export feature — connect to /history/ endpoint and download JSON")
        if st.button("🗑️ Delete All My Data", key="delete_data"):
            st.error("⚠️ This will permanently delete all your data. Contact support.")
