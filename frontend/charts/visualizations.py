"""
Plotly Visualizations - Radar, gauge, skill bars, heatmaps
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
from typing import List, Dict


def _plot_config():
    return {"displayModeBar": False, "responsive": True}


def _is_dark():
    return st.session_state.get("dark_mode", True)


def _theme():
    dark = _is_dark()
    return {
        "bg":       "rgba(0,0,0,0)",
        "paper_bg": "rgba(0,0,0,0)",
        "text":     "#f1f5f9" if dark else "#1a1a2e",
        "grid":     "rgba(255,255,255,0.06)" if dark else "rgba(0,0,0,0.06)",
        "accent":   "#667eea",
        "accent2":  "#764ba2",
    }


# ── Score Gauge ────────────────────────────────────────────────────────────────

def render_score_gauge(score: float, title: str = "ATS Score"):
    t = _theme()
    color = "#10b981" if score >= 70 else "#f59e0b" if score >= 40 else "#ef4444"

    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=score,
        delta={"reference": 70, "increasing": {"color": "#10b981"}, "decreasing": {"color": "#ef4444"}},
        title={"text": title, "font": {"size": 14, "color": t["text"], "family": "Inter"}},
        number={"font": {"size": 48, "color": color, "family": "Space Grotesk"}, "suffix": ""},
        gauge={
            "axis": {"range": [0, 100], "tickwidth": 1, "tickcolor": t["grid"],
                     "tickfont": {"color": t["text"], "size": 10}},
            "bar":  {"color": color, "thickness": 0.3},
            "bgcolor": "rgba(0,0,0,0)",
            "borderwidth": 0,
            "steps": [
                {"range": [0, 40],  "color": "rgba(239,68,68,0.1)"},
                {"range": [40, 70], "color": "rgba(245,158,11,0.1)"},
                {"range": [70, 100],"color": "rgba(16,185,129,0.1)"},
            ],
            "threshold": {
                "line": {"color": "#667eea", "width": 3},
                "thickness": 0.85,
                "value": 70,
            },
        },
    ))
    fig.update_layout(
        paper_bgcolor=t["paper_bg"], plot_bgcolor=t["bg"],
        height=280, margin=dict(t=30, b=10, l=20, r=20),
        font={"family": "Inter"},
    )
    st.plotly_chart(fig, use_container_width=True, config=_plot_config())


# ── Radar Chart ────────────────────────────────────────────────────────────────

def render_score_breakdown_radar(scores: dict):
    t = _theme()
    categories = [
        "Keyword Match", "Semantic Similarity", "Skill Overlap",
        "Formatting", "Sections", "Quality"
    ]
    values = [
        scores.get("keyword_match_pct", 0),
        scores.get("semantic_similarity", 0),
        scores.get("skill_overlap_pct", 0),
        scores.get("formatting_score", 0),
        scores.get("section_completeness", 0),
        scores.get("resume_quality_score", 0),
    ]
    values_closed = values + [values[0]]
    cats_closed   = categories + [categories[0]]

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=values_closed, theta=cats_closed, fill="toself",
        fillcolor="rgba(102,126,234,0.15)",
        line=dict(color="#667eea", width=2.5),
        name="Your Resume",
        hovertemplate="<b>%{theta}</b>: %{r:.1f}%<extra></extra>",
    ))
    fig.add_trace(go.Scatterpolar(
        r=[70]*7, theta=cats_closed, fill="toself",
        fillcolor="rgba(16,185,129,0.05)",
        line=dict(color="#10b981", width=1.5, dash="dash"),
        name="Target (70%)",
        hovertemplate="Target: %{r:.0f}%<extra></extra>",
    ))
    fig.update_layout(
        polar=dict(
            bgcolor="rgba(0,0,0,0)",
            angularaxis=dict(tickfont=dict(color=t["text"], size=10), linecolor=t["grid"]),
            radialaxis=dict(
                visible=True, range=[0, 100],
                tickfont=dict(color=t["text"], size=8),
                gridcolor=t["grid"], linecolor=t["grid"],
            ),
        ),
        paper_bgcolor=t["paper_bg"], plot_bgcolor=t["bg"],
        height=320, margin=dict(t=20, b=20, l=40, r=40),
        legend=dict(
            font=dict(color=t["text"], size=11),
            bgcolor="rgba(0,0,0,0)",
        ),
        font={"family": "Inter"},
    )
    st.plotly_chart(fig, use_container_width=True, config=_plot_config())


# ── Skill Bar Chart ────────────────────────────────────────────────────────────

def render_skill_bars(matched: List[str], missing: List[str], max_show: int = 12):
    t = _theme()
    labels = matched[:max_show//2] + missing[:max_show//2]
    colors = ["#10b981"] * min(len(matched), max_show//2) + \
             ["#ef4444"] * min(len(missing), max_show//2)
    values = [1] * len(labels)

    if not labels:
        st.markdown("<p style='color:var(--text-muted);font-size:13px;'>No skills to display.</p>",
                    unsafe_allow_html=True)
        return

    fig = go.Figure(go.Bar(
        x=values, y=labels,
        orientation="h",
        marker=dict(
            color=colors,
            opacity=0.85,
            line=dict(width=0),
        ),
        hovertemplate="<b>%{y}</b><br>%{marker.color}<extra></extra>",
        width=0.6,
    ))
    fig.update_layout(
        paper_bgcolor=t["paper_bg"], plot_bgcolor=t["bg"],
        height=max(280, len(labels) * 28),
        xaxis=dict(showticklabels=False, showgrid=False, zeroline=False),
        yaxis=dict(tickfont=dict(color=t["text"], size=11), gridcolor=t["grid"]),
        margin=dict(t=10, b=10, l=10, r=10),
        showlegend=False,
        font={"family": "Inter"},
    )
    st.plotly_chart(fig, use_container_width=True, config=_plot_config())


# ── Keyword Heatmap ───────────────────────────────────────────────────────────

def render_keyword_heatmap(matched_kw: List[str], missing_kw: List[str]):
    t = _theme()
    if not matched_kw and not missing_kw:
        return

    all_kw = (matched_kw[:10] + missing_kw[:10])[:20]
    values = [1 if k in matched_kw else 0 for k in all_kw]
    colors = ["#10b981" if v == 1 else "#ef4444" for v in values]

    fig = go.Figure(go.Bar(
        x=all_kw, y=values,
        marker=dict(color=colors, opacity=0.8, line=dict(width=0)),
        hovertemplate="<b>%{x}</b><br>%{customdata}<extra></extra>",
        customdata=["Matched" if v == 1 else "Missing" for v in values],
        width=0.7,
    ))
    fig.update_layout(
        paper_bgcolor=t["paper_bg"], plot_bgcolor=t["bg"],
        height=240,
        xaxis=dict(tickfont=dict(color=t["text"], size=10), gridcolor=t["grid"],
                   tickangle=-30),
        yaxis=dict(showticklabels=False, showgrid=False, zeroline=False),
        margin=dict(t=10, b=60, l=10, r=10),
        showlegend=False,
        font={"family": "Inter"},
    )
    st.plotly_chart(fig, use_container_width=True, config=_plot_config())


# ── History Trend Line ─────────────────────────────────────────────────────────

def render_history_trend(analyses: List[dict]):
    t = _theme()
    if len(analyses) < 2:
        return

    dates  = [a.get("created_at", "")[:10] for a in analyses]
    scores = [a.get("ats_score", 0) for a in analyses]
    dates.reverse(); scores.reverse()

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=dates, y=scores,
        mode="lines+markers",
        line=dict(color="#667eea", width=2.5, shape="spline"),
        marker=dict(size=8, color="#764ba2", line=dict(color="white", width=2)),
        fill="tozeroy",
        fillcolor="rgba(102,126,234,0.08)",
        hovertemplate="<b>%{x}</b><br>ATS Score: %{y:.1f}<extra></extra>",
        name="ATS Score",
    ))
    fig.add_hline(y=70, line_dash="dash", line_color="#10b981",
                  annotation_text="Target (70)", annotation_font_color="#10b981")
    fig.update_layout(
        paper_bgcolor=t["paper_bg"], plot_bgcolor=t["bg"],
        height=280,
        xaxis=dict(tickfont=dict(color=t["text"], size=10), gridcolor=t["grid"]),
        yaxis=dict(
            range=[0, 105], tickfont=dict(color=t["text"], size=10), gridcolor=t["grid"],
            title=dict(text="ATS Score", font=dict(color=t["text"])),
        ),
        margin=dict(t=20, b=40, l=50, r=20),
        showlegend=False,
        font={"family": "Inter"},
    )
    st.plotly_chart(fig, use_container_width=True, config=_plot_config())


# ── Donut Chart ────────────────────────────────────────────────────────────────

def render_skill_donut(matched: int, missing: int):
    t = _theme()
    fig = go.Figure(go.Pie(
        labels=["Matched", "Missing"],
        values=[matched, missing],
        hole=0.65,
        marker=dict(
            colors=["#10b981", "#ef4444"],
            line=dict(color=t["bg"], width=3),
        ),
        textfont=dict(color=t["text"]),
        hovertemplate="<b>%{label}</b>: %{value} skills (%{percent})<extra></extra>",
    ))
    fig.update_layout(
        paper_bgcolor=t["paper_bg"], plot_bgcolor=t["bg"],
        height=240, margin=dict(t=10, b=10, l=10, r=10),
        showlegend=True,
        legend=dict(font=dict(color=t["text"]), bgcolor="rgba(0,0,0,0)"),
        annotations=[dict(
            text=f"{matched}<br><span style='font-size:10px'>matched</span>",
            x=0.5, y=0.5, font_size=22, showarrow=False,
            font=dict(color="#10b981", family="Space Grotesk"),
        )],
        font={"family": "Inter"},
    )
    st.plotly_chart(fig, use_container_width=True, config=_plot_config())
