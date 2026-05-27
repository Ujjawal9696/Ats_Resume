"""
Dashboard Page - Analytics overview of all analyses
"""

import streamlit as st
import requests
from frontend.charts.visualizations import (
    render_score_gauge, render_history_trend,
    render_skill_donut, render_score_breakdown_radar,
)
from backend.config import settings


def _headers():
    return {"Authorization": f"Bearer {st.session_state.token}"}


def _fetch_history():
    try:
        r = requests.get(
            f"{settings.BACKEND_URL}/history/?limit=20",
            headers=_headers(), timeout=15,
        )
        return r.json().get("analyses", []) if r.status_code == 200 else []
    except Exception:
        return []


def render_dashboard_page():
    st.markdown("""
<div class="page-header slide-in">
  <h1>📊 Analytics Dashboard</h1>
  <p>Track your resume performance and improvement over time</p>
</div>
""", unsafe_allow_html=True)

    analyses = _fetch_history()

    if not analyses:
        st.markdown("""
<div style="text-align:center; padding:80px 20px;">
  <div style="font-size:64px; margin-bottom:16px;">📭</div>
  <h3 style="color:var(--text-secondary); font-weight:600;">No analyses yet</h3>
  <p style="color:var(--text-muted); font-size:14px;">
    Run your first resume analysis to see your dashboard
  </p>
</div>
""", unsafe_allow_html=True)
        if st.button("🔍 Go to Analyzer", key="dash_goto_analyzer"):
            st.session_state.current_page = "analyzer"
            st.rerun()
        return

    # ── Summary Stat Cards ───────────────────────────────────────────────────
    total     = len(analyses)
    avg_score = sum(a.get("ats_score", 0) for a in analyses) / max(total, 1)
    best      = max(a.get("ats_score", 0) for a in analyses)
    avg_sem   = sum(a.get("semantic_similarity", 0) for a in analyses) / max(total, 1)

    c1, c2, c3, c4 = st.columns(4)
    stats = [
        (c1, "📋", "Total Analyses", str(total), ""),
        (c2, "🎯", "Avg ATS Score",  f"{avg_score:.1f}", "/100"),
        (c3, "🏆", "Best Score",     f"{best:.1f}",      "/100"),
        (c4, "🧠", "Avg Semantic",   f"{avg_sem:.1f}",   "%"),
    ]
    for col, icon, label, val, suffix in stats:
        with col:
            st.markdown(f"""
<div class="stat-card">
  <div style="font-size:24px; margin-bottom:8px;">{icon}</div>
  <div class="value">{val}<span style="font-size:14px;opacity:0.6;">{suffix}</span></div>
  <div class="label">{label}</div>
</div>
""", unsafe_allow_html=True)

    st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)

    # ── Latest Analysis + Trend ──────────────────────────────────────────────
    col_left, col_right = st.columns([1, 1.4], gap="large")

    with col_left:
        latest = analyses[0]
        st.markdown("#### 🎯 Latest ATS Score")
        render_score_gauge(latest.get("ats_score", 0))
        st.markdown(f"""
<div style="text-align:center; margin-top:-8px;">
  <span style="font-size:12px; color:var(--text-muted);">
    {latest.get('job_title','Unknown Role')}
    {(' @ ' + latest['company_name']) if latest.get('company_name') else ''}
  </span>
</div>
""", unsafe_allow_html=True)

    with col_right:
        st.markdown("#### 📈 Score Trend Over Time")
        if len(analyses) >= 2:
            render_history_trend(analyses)
        else:
            st.info("Run at least 2 analyses to see your trend")

    st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)

    # ── Recent Analyses Table ────────────────────────────────────────────────
    st.markdown("#### 📋 Recent Analyses")
    for a in analyses[:8]:
        score = a.get("ats_score", 0)
        color = "#10b981" if score >= 70 else "#f59e0b" if score >= 40 else "#ef4444"
        bar   = min(score, 100)
        title = a.get("job_title") or "Untitled Position"
        company = a.get("company_name") or ""
        date  = (a.get("created_at") or "")[:10]

        st.markdown(f"""
<div class="history-row fade-in">
  <div style="flex:1;">
    <div style="font-weight:600; font-size:14px; color:var(--text-primary);">{title}</div>
    <div style="font-size:12px; color:var(--text-muted); margin-top:2px;">
      {company + ' · ' if company else ''}{date}
    </div>
  </div>
  <div style="width:140px; margin:0 20px;">
    <div style="display:flex; justify-content:space-between; margin-bottom:4px;">
      <span style="font-size:11px; color:var(--text-muted);">ATS Score</span>
      <span style="font-size:11px; font-weight:700; color:{color};">{score:.0f}</span>
    </div>
    <div style="background:var(--border); height:5px; border-radius:3px; overflow:hidden;">
      <div style="width:{bar}%; height:100%; background:{color}; border-radius:3px;"></div>
    </div>
  </div>
  <span class="tag {'tag-success' if score>=70 else 'tag-warning' if score>=40 else 'tag-error'}">
    {'Excellent' if score>=85 else 'Good' if score>=70 else 'Fair' if score>=40 else 'Weak'}
  </span>
</div>
""", unsafe_allow_html=True)

    if st.button("📋 View Full History →", key="dash_history_btn"):
        st.session_state.current_page = "history"
        st.rerun()
