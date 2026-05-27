"""
Premium CSS Theme - Dark/Light mode, glassmorphism, gradients, animations
"""

import streamlit as st


def inject_css():
    dark = st.session_state.get("dark_mode", True)

    if dark:
        bg_primary    = "#0d0d1a"
        bg_secondary  = "#12122a"
        bg_card       = "rgba(255,255,255,0.04)"
        bg_card_hover = "rgba(255,255,255,0.07)"
        border_color  = "rgba(255,255,255,0.08)"
        text_primary  = "#f1f5f9"
        text_secondary= "#94a3b8"
        text_muted    = "#64748b"
        sidebar_bg    = "#0a0a1a"
        input_bg      = "rgba(255,255,255,0.05)"
        input_border  = "rgba(255,255,255,0.12)"
    else:
        bg_primary    = "#f8faff"
        bg_secondary  = "#ffffff"
        bg_card       = "rgba(255,255,255,0.9)"
        bg_card_hover = "rgba(255,255,255,1)"
        border_color  = "rgba(0,0,0,0.08)"
        text_primary  = "#1a1a2e"
        text_secondary= "#475569"
        text_muted    = "#94a3b8"
        sidebar_bg    = "#ffffff"
        input_bg      = "rgba(0,0,0,0.03)"
        input_border  = "rgba(0,0,0,0.12)"

    st.markdown(f"""
<style>
/* ── Google Fonts ─────────────────────────────────────── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=Space+Grotesk:wght@400;500;600;700&display=swap');

/* ── Root Variables ──────────────────────────────────── */
:root {{
  --bg-primary:    {bg_primary};
  --bg-secondary:  {bg_secondary};
  --bg-card:       {bg_card};
  --bg-card-hover: {bg_card_hover};
  --border:        {border_color};
  --text-primary:  {text_primary};
  --text-secondary:{text_secondary};
  --text-muted:    {text_muted};
  --sidebar-bg:    {sidebar_bg};
  --input-bg:      {input_bg};
  --input-border:  {input_border};
  --accent:        #667eea;
  --accent2:       #764ba2;
  --green:         #10b981;
  --red:           #ef4444;
  --yellow:        #f59e0b;
  --radius:        16px;
  --shadow:        0 4px 24px rgba(102,126,234,0.12);
  --shadow-lg:     0 8px 48px rgba(102,126,234,0.2);
}}

/* ── Global Reset ─────────────────────────────────────── */
*, *::before, *::after {{ box-sizing: border-box; }}
html, body, [class*="css"] {{
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
  color: var(--text-primary);
}}

/* ── App Background ──────────────────────────────────── */
.stApp {{
  background: var(--bg-primary) !important;
  min-height: 100vh;
}}

/* ── Hide Streamlit Default UI ───────────────────────── */
#MainMenu, footer, header {{ visibility: hidden; }}
.stDeployButton {{ display: none; }}
[data-testid="stToolbar"] {{ visibility: hidden; }}

/* ── Sidebar ─────────────────────────────────────────── */
[data-testid="stSidebar"] {{
  background: var(--sidebar-bg) !important;
  border-right: 1px solid var(--border);
  padding-top: 0 !important;
}}
[data-testid="stSidebar"] > div:first-child {{
  padding: 0;
}}

/* ── Main Content Area ────────────────────────────────── */
.main .block-container {{
  padding: 2rem 2.5rem 4rem;
  max-width: 1400px;
}}

/* ── Typography ──────────────────────────────────────── */
h1, h2, h3, h4 {{
  font-family: 'Space Grotesk', 'Inter', sans-serif;
  color: var(--text-primary);
  font-weight: 700;
  letter-spacing: -0.02em;
}}

/* ── Glass Card ──────────────────────────────────────── */
.glass-card {{
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 24px;
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  box-shadow: var(--shadow);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}}
.glass-card:hover {{
  background: var(--bg-card-hover);
  box-shadow: var(--shadow-lg);
  transform: translateY(-2px);
}}

/* ── Gradient Buttons ─────────────────────────────────── */
.stButton > button {{
  background: linear-gradient(135deg, var(--accent) 0%, var(--accent2) 100%) !important;
  color: white !important;
  border: none !important;
  border-radius: 12px !important;
  padding: 0.6rem 1.8rem !important;
  font-weight: 600 !important;
  font-family: 'Inter', sans-serif !important;
  font-size: 14px !important;
  letter-spacing: 0.01em !important;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
  box-shadow: 0 4px 15px rgba(102,126,234,0.3) !important;
  cursor: pointer !important;
}}
.stButton > button:hover {{
  transform: translateY(-2px) !important;
  box-shadow: 0 8px 25px rgba(102,126,234,0.45) !important;
  filter: brightness(1.05) !important;
}}
.stButton > button:active {{
  transform: translateY(0) !important;
}}

/* Secondary Button */
.stButton.secondary > button {{
  background: var(--bg-card) !important;
  border: 1px solid var(--border) !important;
  color: var(--text-primary) !important;
  box-shadow: none !important;
}}

/* ── File Uploader ───────────────────────────────────── */
[data-testid="stFileUploader"] {{
  background: var(--bg-card);
  border: 2px dashed var(--accent);
  border-radius: var(--radius);
  padding: 32px;
  text-align: center;
  transition: all 0.3s ease;
}}
[data-testid="stFileUploader"]:hover {{
  border-color: var(--accent2);
  background: rgba(102,126,234,0.05);
}}
[data-testid="stFileUploadDropzone"] {{
  background: transparent !important;
}}

/* ── Text Input / Textarea ───────────────────────────── */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea {{
  background: var(--input-bg) !important;
  border: 1px solid var(--input-border) !important;
  border-radius: 12px !important;
  color: var(--text-primary) !important;
  font-family: 'Inter', sans-serif !important;
  font-size: 14px !important;
  padding: 12px 16px !important;
  transition: border-color 0.2s ease, box-shadow 0.2s ease !important;
}}
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {{
  border-color: var(--accent) !important;
  box-shadow: 0 0 0 3px rgba(102,126,234,0.15) !important;
  outline: none !important;
}}

/* ── Selectbox ───────────────────────────────────────── */
.stSelectbox > div > div {{
  background: var(--input-bg) !important;
  border: 1px solid var(--input-border) !important;
  border-radius: 12px !important;
  color: var(--text-primary) !important;
}}

/* ── Metric Cards ─────────────────────────────────────── */
[data-testid="stMetric"] {{
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 20px;
  transition: transform 0.2s ease;
}}
[data-testid="stMetric"]:hover {{
  transform: translateY(-2px);
}}
[data-testid="stMetricValue"] {{
  color: var(--accent) !important;
  font-family: 'Space Grotesk', sans-serif !important;
  font-size: 2rem !important;
  font-weight: 800 !important;
}}
[data-testid="stMetricLabel"] {{
  color: var(--text-secondary) !important;
  font-size: 12px !important;
  font-weight: 500 !important;
  text-transform: uppercase !important;
  letter-spacing: 0.05em !important;
}}

/* ── Progress Bar ─────────────────────────────────────── */
.stProgress > div > div > div > div {{
  background: linear-gradient(90deg, var(--accent), var(--accent2)) !important;
  border-radius: 4px !important;
}}
.stProgress > div > div {{
  background: var(--border) !important;
  border-radius: 4px !important;
}}

/* ── Tabs ────────────────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {{
  background: var(--bg-card);
  border-radius: var(--radius);
  padding: 4px;
  gap: 4px;
  border: 1px solid var(--border);
}}
.stTabs [data-baseweb="tab"] {{
  border-radius: 10px !important;
  color: var(--text-secondary) !important;
  font-weight: 500 !important;
  font-family: 'Inter', sans-serif !important;
  padding: 8px 20px !important;
  transition: all 0.2s ease !important;
}}
.stTabs [aria-selected="true"] {{
  background: linear-gradient(135deg, var(--accent), var(--accent2)) !important;
  color: white !important;
  font-weight: 600 !important;
}}

/* ── Divider ─────────────────────────────────────────── */
hr {{
  border: none;
  border-top: 1px solid var(--border);
  margin: 24px 0;
}}

/* ── Alert / Info Boxes ──────────────────────────────── */
.stAlert {{
  border-radius: var(--radius) !important;
  border: 1px solid var(--border) !important;
}}

/* ── Expander ────────────────────────────────────────── */
.streamlit-expanderHeader {{
  background: var(--bg-card) !important;
  border-radius: var(--radius) !important;
  border: 1px solid var(--border) !important;
  color: var(--text-primary) !important;
  font-weight: 600 !important;
}}

/* ── Scrollbar ───────────────────────────────────────── */
::-webkit-scrollbar {{ width: 6px; height: 6px; }}
::-webkit-scrollbar-track {{ background: transparent; }}
::-webkit-scrollbar-thumb {{
  background: var(--border);
  border-radius: 3px;
}}
::-webkit-scrollbar-thumb:hover {{ background: var(--accent); }}

/* ── Custom Components ───────────────────────────────── */
.page-header {{
  background: linear-gradient(135deg, rgba(102,126,234,0.12) 0%, rgba(118,75,162,0.08) 100%);
  border: 1px solid rgba(102,126,234,0.2);
  border-radius: 20px;
  padding: 28px 32px;
  margin-bottom: 28px;
  position: relative;
  overflow: hidden;
}}
.page-header::before {{
  content: '';
  position: absolute;
  top: -50%;
  right: -10%;
  width: 300px;
  height: 300px;
  background: radial-gradient(circle, rgba(102,126,234,0.15) 0%, transparent 70%);
  pointer-events: none;
}}
.page-header h1 {{
  font-size: 2rem;
  font-weight: 800;
  background: linear-gradient(135deg, var(--accent), var(--accent2));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin: 0;
}}
.page-header p {{
  color: var(--text-secondary);
  margin-top: 6px;
  font-size: 15px;
}}

.score-ring-container {{
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 24px;
}}

.skill-badge {{
  display: inline-block;
  padding: 5px 14px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
  margin: 3px;
  transition: transform 0.2s ease;
}}
.skill-badge:hover {{ transform: scale(1.05); }}
.skill-badge.matched {{
  background: rgba(16,185,129,0.15);
  color: #10b981;
  border: 1px solid rgba(16,185,129,0.3);
}}
.skill-badge.missing {{
  background: rgba(239,68,68,0.12);
  color: #ef4444;
  border: 1px solid rgba(239,68,68,0.25);
}}
.skill-badge.neutral {{
  background: var(--bg-card);
  color: var(--text-secondary);
  border: 1px solid var(--border);
}}

.stat-card {{
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 20px;
  text-align: center;
  transition: all 0.3s ease;
}}
.stat-card:hover {{
  transform: translateY(-3px);
  box-shadow: var(--shadow-lg);
  border-color: rgba(102,126,234,0.3);
}}
.stat-card .value {{
  font-size: 36px;
  font-weight: 800;
  font-family: 'Space Grotesk', sans-serif;
  background: linear-gradient(135deg, var(--accent), var(--accent2));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}}
.stat-card .label {{
  font-size: 12px;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.06em;
  font-weight: 600;
  margin-top: 4px;
}}

.suggestion-item {{
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-left: 3px solid var(--accent);
  border-radius: 0 12px 12px 0;
  padding: 14px 18px;
  margin-bottom: 10px;
  font-size: 14px;
  color: var(--text-secondary);
  line-height: 1.6;
  transition: all 0.2s ease;
}}
.suggestion-item:hover {{
  background: var(--bg-card-hover);
  border-left-color: var(--accent2);
  color: var(--text-primary);
}}

.logo-text {{
  font-family: 'Space Grotesk', sans-serif;
  font-size: 22px;
  font-weight: 800;
  background: linear-gradient(135deg, #667eea, #764ba2);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  letter-spacing: -0.5px;
}}

.nav-item {{
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 11px 16px;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s ease;
  margin: 2px 8px;
  font-weight: 500;
  font-size: 14px;
  color: var(--text-secondary);
  text-decoration: none;
}}
.nav-item:hover, .nav-item.active {{
  background: rgba(102,126,234,0.1);
  color: var(--accent);
}}
.nav-item.active {{
  background: linear-gradient(135deg, rgba(102,126,234,0.15), rgba(118,75,162,0.1));
  color: var(--accent);
  font-weight: 600;
}}

.upload-zone {{
  border: 2px dashed rgba(102,126,234,0.4);
  border-radius: 20px;
  padding: 48px 32px;
  text-align: center;
  transition: all 0.3s ease;
  background: rgba(102,126,234,0.03);
  cursor: pointer;
}}
.upload-zone:hover {{
  border-color: var(--accent);
  background: rgba(102,126,234,0.07);
}}

.gradient-text {{
  background: linear-gradient(135deg, #667eea, #764ba2);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}}

.pulse {{
  animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}}
@keyframes pulse {{
  0%, 100% {{ opacity: 1; }}
  50% {{ opacity: .5; }}
}}

.slide-in {{
  animation: slideIn 0.4s ease-out;
}}
@keyframes slideIn {{
  from {{ opacity: 0; transform: translateY(16px); }}
  to {{ opacity: 1; transform: translateY(0); }}
}}

.fade-in {{
  animation: fadeIn 0.5s ease-out;
}}
@keyframes fadeIn {{
  from {{ opacity: 0; }}
  to {{ opacity: 1; }}
}}

.history-row {{
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 14px;
  margin-bottom: 10px;
  transition: all 0.2s ease;
}}
.history-row:hover {{
  background: var(--bg-card-hover);
  border-color: rgba(102,126,234,0.3);
  transform: translateX(4px);
}}

.tag {{
  display: inline-block;
  padding: 3px 10px;
  border-radius: 8px;
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}}
.tag-success {{ background: rgba(16,185,129,0.12); color: #10b981; }}
.tag-warning {{ background: rgba(245,158,11,0.12); color: #f59e0b; }}
.tag-error   {{ background: rgba(239,68,68,0.12);  color: #ef4444; }}
.tag-info    {{ background: rgba(102,126,234,0.12); color: #667eea; }}

/* Plotly charts transparent background */
.js-plotly-plot .plotly .bg {{
  fill: transparent !important;
}}
</style>
""", unsafe_allow_html=True)
