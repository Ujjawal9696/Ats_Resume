"""
History Page - Browse and manage all past analyses
"""

import streamlit as st
import requests
from backend.config import settings


def _headers():
    return {"Authorization": f"Bearer {st.session_state.token}"}


def _fetch_history(limit=50):
    try:
        r = requests.get(
            f"{settings.BACKEND_URL}/history/?limit={limit}",
            headers=_headers(), timeout=15,
        )
        return r.json().get("analyses", []) if r.status_code == 200 else []
    except Exception:
        return []


def _delete_analysis(analysis_id: str) -> bool:
    try:
        r = requests.delete(
            f"{settings.BACKEND_URL}/history/{analysis_id}",
            headers=_headers(), timeout=10,
        )
        return r.status_code == 200
    except Exception:
        return False


def render_history_page():
    st.markdown("""
<div class="page-header slide-in">
  <h1>📋 Analysis History</h1>
  <p>Browse all your previous resume analyses and download reports</p>
</div>
""", unsafe_allow_html=True)

    analyses = _fetch_history()

    if not analyses:
        st.markdown("""
<div style="text-align:center; padding:80px 20px;">
  <div style="font-size:64px; margin-bottom:16px;">📂</div>
  <h3 style="color:var(--text-secondary);">No history yet</h3>
  <p style="color:var(--text-muted); font-size:14px;">Your analyzed resumes will appear here</p>
</div>
""", unsafe_allow_html=True)
        return

    # ── Search / Filter Bar ──────────────────────────────────────────────────
    search_col, filter_col = st.columns([3, 1])
    with search_col:
        search = st.text_input("🔍 Search by job title or company",
                               placeholder="e.g. Software Engineer, Google",
                               label_visibility="collapsed", key="history_search")
    with filter_col:
        sort_by = st.selectbox("Sort", ["Newest First", "Highest Score", "Lowest Score"],
                               label_visibility="collapsed", key="history_sort")

    # Apply filter
    filtered = analyses
    if search:
        s = search.lower()
        filtered = [
            a for a in analyses
            if s in (a.get("job_title") or "").lower()
            or s in (a.get("company_name") or "").lower()
        ]

    if sort_by == "Highest Score":
        filtered.sort(key=lambda x: x.get("ats_score", 0), reverse=True)
    elif sort_by == "Lowest Score":
        filtered.sort(key=lambda x: x.get("ats_score", 0))

    st.markdown(f"<p style='color:var(--text-muted);font-size:13px;margin-bottom:16px;'>"
                f"Showing {len(filtered)} of {len(analyses)} analyses</p>",
                unsafe_allow_html=True)

    # ── Analysis Cards ───────────────────────────────────────────────────────
    for a in filtered:
        _render_analysis_card(a)


def _render_analysis_card(a: dict):
    score   = a.get("ats_score", 0)
    sem     = a.get("semantic_similarity", 0)
    kw      = a.get("keyword_match_pct", 0)
    title   = a.get("job_title") or "Untitled Position"
    company = a.get("company_name") or ""
    date    = (a.get("created_at") or "")[:10]
    aid     = a.get("id", "")
    color   = "#10b981" if score >= 70 else "#f59e0b" if score >= 45 else "#ef4444"

    with st.expander(f"{'🟢' if score>=70 else '🟡' if score>=45 else '🔴'}  **{title}**"
                     + (f" · {company}" if company else "")
                     + f"  —  ATS: **{score:.0f}/100**  ·  {date}"):

        c1, c2, c3 = st.columns(3)
        for col, label, val in [
            (c1, "ATS Score",       f"{score:.1f}/100"),
            (c2, "Semantic Match",  f"{sem:.1f}%"),
            (c3, "Keyword Match",   f"{kw:.1f}%"),
        ]:
            with col:
                st.markdown(f"""
<div class="stat-card" style="padding:14px;">
  <div class="value" style="font-size:22px;">{val}</div>
  <div class="label">{label}</div>
</div>
""", unsafe_allow_html=True)

        col_btns = st.columns([1, 1, 1, 2])
        with col_btns[0]:
            if st.button("📄 Report", key=f"report_{aid}", use_container_width=True):
                _generate_report(aid)
        with col_btns[1]:
            if st.button("🔄 Re-Analyze", key=f"rerun_{aid}", use_container_width=True):
                st.session_state.current_page = "analyzer"
                st.rerun()
        with col_btns[2]:
            if st.button("🗑️ Delete", key=f"del_{aid}", use_container_width=True):
                if _delete_analysis(aid):
                    st.success("Deleted")
                    st.rerun()
                else:
                    st.error("Delete failed")


def _generate_report(analysis_id: str):
    headers = {"Authorization": f"Bearer {st.session_state.token}"}
    try:
        r = requests.get(
            f"{settings.BACKEND_URL}/report/{analysis_id}/generate",
            headers=headers, timeout=60,
        )
        if r.status_code == 200:
            report = r.json()
            url = f"{settings.BACKEND_URL}{report['download_url']}"
            st.success("Report ready!")
            st.markdown(
                f'<a href="{url}" target="_blank">⬇️ Download PDF</a>',
                unsafe_allow_html=True,
            )
        else:
            st.error("Report generation failed")
    except Exception as e:
        st.error(str(e))
