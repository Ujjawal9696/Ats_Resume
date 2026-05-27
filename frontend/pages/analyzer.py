"""
Analyzer Page - Core resume analysis workflow
Upload → Paste JD → Analyze → View Results
"""

import streamlit as st
import requests
from frontend.charts.visualizations import (
    render_score_gauge,
    render_score_breakdown_radar,
    render_skill_bars,
    render_keyword_heatmap,
)
from backend.config import settings


def _headers():
    return {"Authorization": f"Bearer {st.session_state.token}"}


def _upload_resume(file) -> dict:
    try:
        r = requests.post(
            f"{settings.BACKEND_URL}/resume/upload",
            files={"file": (file.name, file.getvalue(), file.type)},
            headers=_headers(),
            timeout=60,
        )
        if r.status_code == 200:
            return {"ok": True, "data": r.json()}
        return {"ok": False, "error": r.json().get("detail", "Upload failed")}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def _run_analysis(resume_id: str, jd: str, title: str, company: str) -> dict:
    try:
        r = requests.post(
            f"{settings.BACKEND_URL}/analyze/",
            json={
                "resume_id":       resume_id,
                "job_description": jd,
                "job_title":       title or None,
                "company_name":    company or None,
            },
            headers=_headers(),
            timeout=120,
        )
        if r.status_code == 200:
            return {"ok": True, "data": r.json()}
        return {"ok": False, "error": r.json().get("detail", "Analysis failed")}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def render_analyzer_page():
    st.markdown("""
<div class="page-header slide-in">
  <h1>🔍 Resume Analyzer</h1>
  <p>Upload your resume and paste a job description to get your ATS compatibility score</p>
</div>
""", unsafe_allow_html=True)

    # ── Step 1 & 2: Upload + JD side by side ─────────────────────────────────
    col_left, col_right = st.columns([1, 1], gap="large")

    with col_left:
        st.markdown("#### 📄 Step 1 · Upload Resume")
        st.markdown("<p style='color:var(--text-muted);font-size:13px;margin-bottom:12px;'>"
                    "Supports PDF, DOCX, DOC · Max 10MB</p>", unsafe_allow_html=True)

        uploaded_file = st.file_uploader(
            "Drop your resume here",
            type=["pdf", "docx", "doc"],
            label_visibility="collapsed",
            key="resume_uploader",
        )

        if uploaded_file:
            st.markdown(f"""
<div style="background:rgba(16,185,129,0.08); border:1px solid rgba(16,185,129,0.25);
            border-radius:12px; padding:12px 16px; margin-top:8px; display:flex;
            align-items:center; gap:10px;">
  <span style="font-size:20px;">📎</span>
  <div>
    <div style="font-weight:600; font-size:13px; color:#10b981;">{uploaded_file.name}</div>
    <div style="font-size:11px; color:var(--text-muted);">
      {uploaded_file.size / 1024:.1f} KB · {uploaded_file.type or 'document'}
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

            if not st.session_state.get("upload_done") or \
               st.session_state.get("last_file") != uploaded_file.name:
                with st.spinner("🔄 Parsing resume with NLP..."):
                    result = _upload_resume(uploaded_file)
                if result["ok"]:
                    data = result["data"]
                    st.session_state.resume_id     = data["resume_id"]
                    st.session_state.resume_text   = data["raw_text"]
                    st.session_state.resume_parsed = data["parsed_data"]
                    st.session_state.upload_done   = True
                    st.session_state.last_file     = uploaded_file.name
                    st.success(f"✅ Resume parsed! {data['word_count']} words · {data['page_count']} page(s)")

                    # Show extracted skills
                    skills = data["parsed_data"].get("skills", [])
                    if skills:
                        badges = " ".join([
                            f'<span class="skill-badge neutral">{s}</span>'
                            for s in skills[:15]
                        ])
                        st.markdown(f"<div style='margin-top:10px;'>{badges}</div>",
                                    unsafe_allow_html=True)
                else:
                    st.error(f"❌ {result['error']}")

    with col_right:
        st.markdown("#### 📋 Step 2 · Paste Job Description")
        st.markdown("<p style='color:var(--text-muted);font-size:13px;margin-bottom:12px;'>"
                    "Paste the full JD for best results (min. 50 characters)</p>", unsafe_allow_html=True)

        jd_col1, jd_col2 = st.columns(2)
        with jd_col1:
            job_title = st.text_input("Job Title", placeholder="e.g. Senior ML Engineer",
                                      key="job_title_input")
        with jd_col2:
            company = st.text_input("Company", placeholder="e.g. Google",
                                    key="company_input")

        jd_text = st.text_area(
            "Job Description",
            placeholder="Paste the full job description here...\n\nInclude requirements, responsibilities, qualifications, and tech stack for the most accurate analysis.",
            height=260,
            key="jd_textarea",
            label_visibility="collapsed",
        )

        if jd_text:
            word_count = len(jd_text.split())
            color = "#10b981" if word_count >= 50 else "#f59e0b"
            st.markdown(f"<p style='font-size:11px; color:{color}; margin-top:4px;'>"
                        f"{'✅' if word_count >= 50 else '⚠️'} {word_count} words "
                        f"{'· Good length' if word_count >= 100 else '· Add more for better results'}"
                        f"</p>", unsafe_allow_html=True)

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    # ── Step 3: Analyze Button ────────────────────────────────────────────────
    _, btn_col, _ = st.columns([1, 2, 1])
    with btn_col:
        analyze_btn = st.button(
            "🚀  Analyze Resume Against JD",
            use_container_width=True,
            key="analyze_btn",
            disabled=not (st.session_state.get("resume_id") and jd_text and len(jd_text) >= 50),
        )

    if analyze_btn:
        if not st.session_state.get("resume_id"):
            st.warning("⚠️ Please upload a resume first")
        elif not jd_text or len(jd_text) < 50:
            st.warning("⚠️ Please paste a job description (min 50 characters)")
        else:
            with st.spinner("🧠 Running ATS analysis with NLP + Groq AI... This may take 30–60 seconds"):
                result = _run_analysis(
                    resume_id=st.session_state.resume_id,
                    jd=jd_text,
                    title=job_title,
                    company=company,
                )
            if result["ok"]:
                st.session_state.analysis_result = result["data"]
                st.session_state.analysis_done   = True
                st.success("✅ Analysis complete! Scroll down to see your results.")
                st.rerun()
            else:
                st.error(f"❌ Analysis failed: {result['error']}")

    # ── Results Section ───────────────────────────────────────────────────────
    if st.session_state.get("analysis_done") and st.session_state.get("analysis_result"):
        _render_results(st.session_state.analysis_result)


def _render_results(data: dict):
    st.markdown("<hr>", unsafe_allow_html=True)
    scores    = data.get("scores", {})
    ats_score = scores.get("ats_score", 0)

    # ── Score Hero ─────────────────────────────────────────────────────────
    grade, color = _get_grade(ats_score)

    st.markdown(f"""
<div class="slide-in" style="background: linear-gradient(135deg, rgba(102,126,234,0.1), rgba(118,75,162,0.07));
     border: 1px solid rgba(102,126,234,0.2); border-radius: 20px; padding: 32px; text-align:center; margin-bottom:28px;">
  <div style="font-size: 88px; font-weight: 900; font-family:'Space Grotesk',sans-serif;
              background: linear-gradient(135deg, {'#10b981' if ats_score>=75 else '#f59e0b' if ats_score>=50 else '#ef4444'},
              {'#059669' if ats_score>=75 else '#d97706' if ats_score>=50 else '#dc2626'});
              -webkit-background-clip: text; -webkit-text-fill-color: transparent;
              background-clip: text; line-height: 1;">
    {ats_score:.0f}
  </div>
  <div style="font-size:16px; color:var(--text-secondary); margin-top:4px; font-weight:500;">
    ATS Compatibility Score
  </div>
  <div style="margin-top:10px;">
    <span style="background:{'rgba(16,185,129,0.15)' if ats_score>=75 else 'rgba(245,158,11,0.15)' if ats_score>=50 else 'rgba(239,68,68,0.15)'};
                 color:{color}; padding:6px 20px; border-radius:20px; font-weight:700; font-size:14px;">
      {grade}
    </span>
  </div>
  <div style="margin-top:12px; font-size:12px; color:var(--text-muted);">
    {'🎉 Great match! Apply with confidence.' if ats_score>=75 else '💪 Decent match. Polish a few areas.' if ats_score>=50 else '⚠️ Needs improvement before applying.'}
  </div>
</div>
""", unsafe_allow_html=True)

    # ── Score Breakdown Cards ──────────────────────────────────────────────
    st.markdown("#### 📊 Score Breakdown")
    cols = st.columns(3)
    metrics = [
        ("🔑 Keyword Match",   scores.get("keyword_match_pct", 0),    "%"),
        ("🧠 Semantic Match",  scores.get("semantic_similarity", 0),   "%"),
        ("⚡ Skill Overlap",   scores.get("skill_overlap_pct", 0),     "%"),
        ("📐 Formatting",      scores.get("formatting_score", 0),      "%"),
        ("📋 Sections",        scores.get("section_completeness", 0),  "%"),
        ("⭐ Quality Score",   scores.get("resume_quality_score", 0),  "%"),
    ]
    for i, (label, value, unit) in enumerate(metrics):
        with cols[i % 3]:
            bar_color = "#10b981" if value >= 70 else "#f59e0b" if value >= 40 else "#ef4444"
            st.markdown(f"""
<div class="stat-card" style="margin-bottom:12px;">
  <div class="value" style="font-size:28px; background:linear-gradient(135deg,
       {'#10b981,#059669' if value>=70 else '#f59e0b,#d97706' if value>=40 else '#ef4444,#dc2626'});
       -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text;">
    {value:.1f}{unit}
  </div>
  <div class="label">{label}</div>
  <div style="background:var(--border); height:4px; border-radius:2px; margin-top:10px; overflow:hidden;">
    <div style="width:{min(value,100)}%; height:100%; border-radius:2px;
                background:linear-gradient(90deg, {bar_color}, {bar_color}cc);
                transition:width 1s ease;"></div>
  </div>
</div>
""", unsafe_allow_html=True)

    # ── Charts Row ─────────────────────────────────────────────────────────
    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
    chart_col1, chart_col2 = st.columns([1.2, 1])

    with chart_col1:
        st.markdown("#### 🕸️ Radar Analysis")
        render_score_breakdown_radar(scores)

    with chart_col2:
        st.markdown("#### 📈 Skill Breakdown")
        matched = data.get("matched_skills", [])
        missing = data.get("missing_skills", [])
        render_skill_bars(matched, missing)

    # ── Skills ─────────────────────────────────────────────────────────────
    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
    skill_col1, skill_col2 = st.columns(2)

    with skill_col1:
        st.markdown("#### ✅ Matched Skills")
        matched = data.get("matched_skills", [])
        if matched:
            badges = " ".join([f'<span class="skill-badge matched">{s}</span>' for s in matched[:25]])
            st.markdown(f"<div class='fade-in'>{badges}</div>", unsafe_allow_html=True)
        else:
            st.markdown("<p style='color:var(--text-muted);font-size:13px;'>No skill matches found.</p>",
                        unsafe_allow_html=True)

    with skill_col2:
        st.markdown("#### ❌ Missing Skills")
        missing = data.get("missing_skills", [])
        if missing:
            badges = " ".join([f'<span class="skill-badge missing">{s}</span>' for s in missing[:25]])
            st.markdown(f"<div class='fade-in'>{badges}</div>", unsafe_allow_html=True)
        else:
            st.markdown("<p style='color:#10b981;font-size:13px;'>🎉 No critical skills missing!</p>",
                        unsafe_allow_html=True)

    # ── Keywords ───────────────────────────────────────────────────────────
    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
    st.markdown("#### 🔑 Keyword Analysis")
    kw_col1, kw_col2 = st.columns(2)

    with kw_col1:
        st.markdown("<p style='font-size:13px;color:var(--text-secondary);margin-bottom:8px;'>"
                    "✅ Matched Keywords</p>", unsafe_allow_html=True)
        matched_kw = data.get("matched_keywords", [])
        if matched_kw:
            tags = " ".join([
                f'<span style="background:rgba(102,126,234,0.12);color:#667eea;padding:4px 11px;'
                f'border-radius:8px;font-size:11px;font-weight:600;margin:3px;display:inline-block;">{k}</span>'
                for k in matched_kw[:20]
            ])
            st.markdown(f"<div>{tags}</div>", unsafe_allow_html=True)

    with kw_col2:
        st.markdown("<p style='font-size:13px;color:var(--text-secondary);margin-bottom:8px;'>"
                    "⚠️ Missing Keywords</p>", unsafe_allow_html=True)
        missing_kw = data.get("missing_keywords", [])
        if missing_kw:
            tags = " ".join([
                f'<span style="background:rgba(245,158,11,0.1);color:#f59e0b;padding:4px 11px;'
                f'border-radius:8px;font-size:11px;font-weight:600;margin:3px;display:inline-block;">{k}</span>'
                for k in missing_kw[:20]
            ])
            st.markdown(f"<div>{tags}</div>", unsafe_allow_html=True)

    # ── AI Suggestions ─────────────────────────────────────────────────────
    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
    _render_ai_suggestions(data.get("ai_suggestions", {}))

    # ── Download Report ─────────────────────────────────────────────────────
    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
    st.markdown("#### 📥 Download Report")
    _, dl_col, _ = st.columns([1, 2, 1])
    with dl_col:
        if st.button("📄 Generate PDF Report", use_container_width=True, key="gen_report"):
            analysis_id = data.get("analysis_id")
            try:
                r = requests.get(
                    f"{settings.BACKEND_URL}/report/{analysis_id}/generate",
                    headers=_headers(),
                    timeout=60,
                )
                if r.status_code == 200:
                    report = r.json()
                    download_url = f"{settings.BACKEND_URL}{report['download_url']}"
                    st.success(f"✅ Report generated!")
                    st.markdown(f'<a href="{download_url}" target="_blank">'
                                f'<button style="background:linear-gradient(135deg,#10b981,#059669);'
                                f'color:white;border:none;border-radius:12px;padding:10px 24px;'
                                f'font-weight:600;cursor:pointer;width:100%;">⬇️ Download PDF</button>'
                                f'</a>', unsafe_allow_html=True)
                else:
                    st.error("Report generation failed")
            except Exception as e:
                st.error(f"Error: {e}")


def _render_ai_suggestions(ai: dict):
    if not ai:
        return
    st.markdown("#### 🤖 AI-Powered Suggestions")

    if ai.get("overall_summary"):
        st.markdown(f"""
<div style="background:linear-gradient(135deg,rgba(102,126,234,0.08),rgba(118,75,162,0.05));
            border:1px solid rgba(102,126,234,0.2); border-radius:16px; padding:18px 22px; margin-bottom:16px;">
  <div style="font-size:12px;font-weight:600;color:#667eea;margin-bottom:6px;">💡 AI Summary</div>
  <div style="font-size:14px;color:var(--text-secondary);line-height:1.65;">{ai['overall_summary']}</div>
</div>
""", unsafe_allow_html=True)

    tab1, tab2, tab3, tab4 = st.tabs([
        "⚡ Optimization", "🎯 ATS Tips", "✍️ Better Bullets", "🚀 Action Verbs"
    ])

    with tab1:
        for tip in ai.get("optimization_tips", []):
            st.markdown(f'<div class="suggestion-item">💡 {tip}</div>', unsafe_allow_html=True)

    with tab2:
        for tip in ai.get("ats_feedback", []):
            st.markdown(f'<div class="suggestion-item">🎯 {tip}</div>', unsafe_allow_html=True)

    with tab3:
        for bullet in ai.get("better_bullet_points", []):
            st.markdown(f'<div class="suggestion-item">→ {bullet}</div>', unsafe_allow_html=True)

    with tab4:
        verbs = ai.get("action_verbs", [])
        if verbs:
            tags = " ".join([
                f'<span style="background:linear-gradient(135deg,rgba(102,126,234,0.15),rgba(118,75,162,0.1));'
                f'color:#667eea;padding:6px 16px;border-radius:20px;font-size:13px;font-weight:700;'
                f'margin:4px;display:inline-block;border:1px solid rgba(102,126,234,0.25);">{v}</span>'
                for v in verbs
            ])
            st.markdown(f"<div style='line-height:2.4;'>{tags}</div>", unsafe_allow_html=True)


def _get_grade(score: float):
    if score >= 85: return "Excellent Match 🏆", "#10b981"
    if score >= 70: return "Good Match ✅", "#10b981"
    if score >= 55: return "Fair Match ⚡", "#f59e0b"
    if score >= 40: return "Weak Match ⚠️", "#f59e0b"
    return "Poor Match ❌", "#ef4444"
