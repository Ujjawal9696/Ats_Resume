"""
Sidebar Navigation Component - Premium SaaS sidebar
"""

import streamlit as st


def render_sidebar() -> str:
    """Render sidebar and return selected page key."""

    with st.sidebar:
        # ── Logo ──────────────────────────────────────────────────────────────
        st.markdown("""
<div style="padding: 24px 20px 16px; border-bottom: 1px solid var(--border);">
  <div class="logo-text">🎯 ATSPro</div>
  <div style="font-size:11px; color:var(--text-muted); margin-top:4px; font-weight:500;">
    AI Resume Intelligence
  </div>
</div>
""", unsafe_allow_html=True)

        st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

        # ── User Profile ───────────────────────────────────────────────────────
        user = st.session_state.get("user", {})
        if user:
            name  = user.get("full_name") or user.get("email", "User")
            email = user.get("email", "")
            plan  = user.get("plan", "free").upper()
            count = user.get("analyses_count", 0)
            avatar_letter = name[0].upper() if name else "U"

            st.markdown(f"""
<div style="margin: 0 8px 16px; background: var(--bg-card); border: 1px solid var(--border);
            border-radius: 14px; padding: 14px 16px; display: flex; align-items: center; gap: 12px;">
  <div style="width:40px; height:40px; border-radius:50%;
              background: linear-gradient(135deg, #667eea, #764ba2);
              display:flex; align-items:center; justify-content:center;
              font-weight:700; font-size:16px; color:white; flex-shrink:0;">
    {avatar_letter}
  </div>
  <div style="overflow:hidden;">
    <div style="font-weight:600; font-size:13px; color:var(--text-primary);
                white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">
      {name[:22]}
    </div>
    <div style="font-size:10px; color:var(--text-muted); margin-top:1px;">
      <span style="background:rgba(102,126,234,0.15); color:#667eea;
                   padding:1px 7px; border-radius:6px; font-weight:600;">
        {plan}
      </span>
      &nbsp;·&nbsp; {count} analyses
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

        # ── Navigation ─────────────────────────────────────────────────────────
        pages = [
            ("analyzer",  "🔍", "Resume Analyzer"),
            ("dashboard", "📊", "Dashboard"),
            ("history",   "📋", "History"),
            ("settings",  "⚙️", "Settings"),
        ]

        current = st.session_state.get("current_page", "analyzer")

        st.markdown("<div style='padding: 0 8px;'>", unsafe_allow_html=True)
        st.markdown("<p style='font-size:10px; font-weight:600; color:var(--text-muted); "
                    "text-transform:uppercase; letter-spacing:0.08em; padding:0 8px; margin-bottom:6px;'>"
                    "NAVIGATION</p>", unsafe_allow_html=True)

        selected = current
        for key, icon, label in pages:
            active_class = "active" if key == current else ""
            if st.button(
                f"{icon}  {label}",
                key=f"nav_{key}",
                use_container_width=True,
                type="primary" if key == current else "secondary",
            ):
                selected = key
                st.session_state.current_page = key

        st.markdown("</div>", unsafe_allow_html=True)

        # ── Divider ───────────────────────────────────────────────────────────
        st.markdown("<hr style='margin:16px 8px;'>", unsafe_allow_html=True)

        # ── Dark Mode Toggle ──────────────────────────────────────────────────
        col1, col2 = st.columns([3, 2])
        with col1:
            st.markdown("<span style='font-size:13px; color:var(--text-secondary); "
                        "font-weight:500;'>🌙 Dark Mode</span>", unsafe_allow_html=True)
        with col2:
            dark = st.toggle("", value=st.session_state.get("dark_mode", True), key="dark_toggle")
            if dark != st.session_state.get("dark_mode", True):
                st.session_state.dark_mode = dark
                st.rerun()

        # ── ATS Score Tip ─────────────────────────────────────────────────────
        st.markdown("""
<div style="margin: 16px 8px 0; padding: 14px 16px; background: linear-gradient(135deg,
            rgba(102,126,234,0.12), rgba(118,75,162,0.08));
            border: 1px solid rgba(102,126,234,0.2); border-radius: 14px;">
  <div style="font-size:12px; font-weight:600; color: #667eea; margin-bottom:6px;">
    💡 ATS Tip
  </div>
  <div style="font-size:11px; color:var(--text-secondary); line-height:1.5;">
    Mirror the job description's exact keywords to maximize your ATS score.
  </div>
</div>
""", unsafe_allow_html=True)

        # ── Logout ────────────────────────────────────────────────────────────
        st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
        if st.button("🚪  Sign Out", use_container_width=True, key="logout_btn"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

    return selected
