"""Streamlit entrypoint for VideoGuard."""

from __future__ import annotations

import json
import shutil
import tempfile
from pathlib import Path

import streamlit as st

from src.adapters import get_adapter
from src.config import get_config
from src.core.decision_engine import run_full_pipeline
from src.core.preprocessor import compute_video_hash
from src.report.report_generator import generate_report

st.set_page_config(
    page_title="VideoGuard",
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items={"About": "VideoGuard — Academic copyright detection system"},
)

if "app_ready" not in st.session_state:
    st.session_state.app_ready = False

# ─────────────────────────────────────────────────────────────────────────────
#  STYLES
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600;0,9..40,700;1,9..40,400&family=DM+Mono:wght@400;500&family=Playfair+Display:wght@700;800&display=swap');

:root {
    --green:       #16a34a;
    --green-dark:  #14532d;
    --green-mid:   #22c55e;
    --green-light: #dcfce7;
    --green-pale:  #f0fdf4;
    --red:         #dc2626;
    --red-pale:    #fef2f2;
    --red-border:  #fecaca;
    --ink:         #0f172a;
    --ink-2:       #334155;
    --ink-3:       #64748b;
    --ink-4:       #94a3b8;
    --border:      #e2e8f0;
    --surface:     #ffffff;
    --bg:          #f8fafc;
    --shadow-sm:   0 1px 3px rgba(0,0,0,.06),0 1px 2px rgba(0,0,0,.04);
    --shadow-md:   0 4px 16px rgba(0,0,0,.08),0 2px 6px rgba(0,0,0,.04);
    --shadow-lg:   0 12px 40px rgba(0,0,0,.10),0 4px 12px rgba(0,0,0,.05);
    --radius:      14px;
}

html,body,[class*="css"]{font-family:'DM Sans',sans-serif !important;color:var(--ink);}
.stApp{background:var(--bg) !important;}
#MainMenu,footer,header{visibility:hidden;}
.block-container{padding:0 2.5rem 5rem !important;max-width:1100px !important;}

/* ══════════════════════════════════════════════
   SPLASH
══════════════════════════════════════════════ */
.vg-splash{
    position:fixed;inset:0;z-index:9999;
    background:var(--surface);
    display:flex;flex-direction:column;
    align-items:center;justify-content:center;
}
.vg-splash-ring{
    position:relative;width:96px;height:96px;
    animation:vg-pop .7s cubic-bezier(.34,1.56,.64,1) .2s both;
}
.vg-splash-ring::before{
    content:'';position:absolute;inset:-8px;
    border-radius:30px;background:var(--green-light);
    animation:vg-pulse 2s ease-in-out 1.4s infinite;
}
@keyframes vg-pulse{0%,100%{transform:scale(1);opacity:.5}50%{transform:scale(1.1);opacity:1}}
.vg-splash-icon{
    position:relative;z-index:1;width:96px;height:96px;
    background:linear-gradient(135deg,#16a34a,#22c55e);
    border-radius:22px;
    display:flex;align-items:center;justify-content:center;
    box-shadow:0 12px 40px rgba(22,163,74,.35);
}
.vg-splash-icon svg{width:46px;height:46px;}
@keyframes vg-pop{from{transform:scale(.3) rotate(-10deg);opacity:0}to{transform:scale(1) rotate(0);opacity:1}}
.vg-splash-wordmark{
    margin-top:2rem;
    font-family:'Playfair Display',serif;
    font-size:3.2rem;font-weight:800;color:var(--ink);
    letter-spacing:-.04em;line-height:1;
    animation:vg-rise .6s ease .8s both;
}
.vg-splash-wordmark em{font-style:normal;color:var(--green);}
.vg-splash-tagline{
    margin-top:.5rem;font-size:.7rem;font-weight:500;
    letter-spacing:.22em;text-transform:uppercase;
    color:var(--ink-4);animation:vg-rise .6s ease 1s both;
}
@keyframes vg-rise{from{transform:translateY(14px);opacity:0}to{transform:translateY(0);opacity:1}}
.vg-splash-bar-wrap{margin-top:2.8rem;width:220px;animation:vg-rise .5s ease 1.2s both;}
.vg-splash-bar-track{height:3px;border-radius:99px;background:var(--green-light);overflow:hidden;}
.vg-splash-bar-fill{
    height:100%;border-radius:99px;
    background:linear-gradient(90deg,var(--green),var(--green-mid));
    animation:vg-fill 2.2s cubic-bezier(.4,0,.2,1) 1.3s both;
}
@keyframes vg-fill{from{width:0%}60%{width:72%}to{width:100%}}
.vg-splash-status{
    margin-top:.8rem;font-size:.62rem;font-weight:500;
    letter-spacing:.18em;text-transform:uppercase;
    color:var(--ink-4);animation:vg-rise .5s ease 1.2s both;
}
.vg-sc{position:fixed;width:40px;height:40px;pointer-events:none;z-index:9998;animation:vg-rise .4s ease .4s both;}
.vg-sc-tl{top:20px;left:20px;border-top:2px solid var(--green-light);border-left:2px solid var(--green-light);}
.vg-sc-tr{top:20px;right:20px;border-top:2px solid var(--green-light);border-right:2px solid var(--green-light);}
.vg-sc-bl{bottom:20px;left:20px;border-bottom:2px solid var(--green-light);border-left:2px solid var(--green-light);}
.vg-sc-br{bottom:20px;right:20px;border-bottom:2px solid var(--green-light);border-right:2px solid var(--green-light);}

/* ══════════════════════════════════════════════
   HERO HEADER
══════════════════════════════════════════════ */
.vg-hero{
    background:linear-gradient(135deg,#0f172a 0%,#1a2e1a 50%,#0f2a1a 100%);
    border-radius:20px;
    padding:2.2rem 2.6rem;
    margin-bottom:1.6rem;
    position:relative;overflow:hidden;
    box-shadow:0 8px 40px rgba(22,163,74,.15);
}
.vg-hero::before{
    content:'';position:absolute;inset:0;
    background:
        radial-gradient(ellipse 60% 50% at 90% 50%,rgba(34,197,94,.08) 0%,transparent 70%),
        radial-gradient(ellipse 40% 60% at 5% 80%,rgba(22,163,74,.06) 0%,transparent 60%);
    pointer-events:none;
}
.vg-hero-grid{
    position:absolute;inset:0;pointer-events:none;
    background-image:
        linear-gradient(rgba(255,255,255,.03) 1px,transparent 1px),
        linear-gradient(90deg,rgba(255,255,255,.03) 1px,transparent 1px);
    background-size:32px 32px;
}
.vg-hero-inner{
    position:relative;z-index:1;
    display:flex;align-items:center;justify-content:space-between;gap:2rem;
}
.vg-hero-left{display:flex;align-items:center;gap:18px;}
.vg-hero-logo{
    width:54px;height:54px;
    background:linear-gradient(135deg,#16a34a,#22c55e);
    border-radius:14px;flex-shrink:0;
    display:flex;align-items:center;justify-content:center;
    box-shadow:0 4px 20px rgba(22,163,74,.4);
}
.vg-hero-logo svg{width:26px;height:26px;}
.vg-hero-wordmark{
    font-family:'Playfair Display',serif;
    font-size:2rem;font-weight:800;color:#ffffff;
    letter-spacing:-.04em;line-height:1;
}
.vg-hero-wordmark em{font-style:normal;color:#4ade80;}
.vg-hero-sub{
    font-size:.65rem;font-weight:500;
    letter-spacing:.18em;text-transform:uppercase;
    color:rgba(255,255,255,.35);margin-top:4px;
}
.vg-hero-badge{
    display:flex;align-items:center;gap:7px;
    padding:6px 14px;border-radius:99px;
    background:rgba(34,197,94,.12);
    border:1px solid rgba(34,197,94,.25);
    font-size:.68rem;font-weight:600;
    color:#4ade80;letter-spacing:.06em;
}
.vg-hero-badge::before{
    content:'';width:8px;height:8px;border-radius:50%;
    background:#4ade80;
    box-shadow:0 0 8px #4ade80;
    animation:vg-blink 2s ease infinite;
}
@keyframes vg-blink{0%,100%{opacity:1}50%{opacity:.3}}

/* Stats row inside hero */
.vg-stats{
    display:grid;grid-template-columns:repeat(3,1fr);
    gap:1px;margin-top:2rem;
    background:rgba(255,255,255,.06);
    border-radius:12px;overflow:hidden;
    border:1px solid rgba(255,255,255,.06);
}
.vg-stat{
    padding:.9rem 1.2rem;
    background:rgba(255,255,255,.025);
    text-align:center;
}
.vg-stat-val{
    font-family:'DM Mono',monospace;
    font-size:1.4rem;font-weight:500;color:#ffffff;
    line-height:1;
}
.vg-stat-val span{font-size:.9rem;color:#4ade80;}
.vg-stat-lbl{
    font-size:.6rem;font-weight:600;
    letter-spacing:.12em;text-transform:uppercase;
    color:rgba(255,255,255,.3);margin-top:4px;
}

/* How it works pills */
.vg-how{
    display:flex;align-items:center;gap:0;
    margin-top:1.4rem;
    background:rgba(255,255,255,.03);
    border:1px solid rgba(255,255,255,.06);
    border-radius:10px;padding:.7rem 1rem;
}
.vg-how-step{
    display:flex;align-items:center;gap:8px;
    padding:0 .8rem;
    font-size:.72rem;font-weight:500;color:rgba(255,255,255,.5);
    flex:1;
}
.vg-how-step:first-child{padding-left:0;}
.vg-how-num{
    width:22px;height:22px;border-radius:50%;
    background:rgba(34,197,94,.15);
    border:1px solid rgba(34,197,94,.3);
    display:flex;align-items:center;justify-content:center;
    font-size:.62rem;font-weight:700;color:#4ade80;flex-shrink:0;
}
.vg-how-arrow{color:rgba(255,255,255,.15);font-size:.8rem;flex-shrink:0;}

/* ══════════════════════════════════════════════
   FEATURE CARDS ROW
══════════════════════════════════════════════ */
.vg-features{
    display:grid;grid-template-columns:repeat(3,1fr);
    gap:.9rem;margin-bottom:1.6rem;
}
.vg-feat{
    background:var(--surface);
    border:1.5px solid var(--border);
    border-radius:var(--radius);
    padding:1.1rem 1.3rem;
    box-shadow:var(--shadow-sm);
    display:flex;align-items:flex-start;gap:12px;
    transition:border-color .2s,box-shadow .2s;
}
.vg-feat:hover{
    border-color:#86efac;
    box-shadow:0 4px 20px rgba(22,163,74,.08);
}
.vg-feat-icon{
    width:38px;height:38px;border-radius:10px;
    background:var(--green-pale);
    border:1px solid var(--green-light);
    display:flex;align-items:center;justify-content:center;
    font-size:17px;flex-shrink:0;
}
.vg-feat-title{
    font-size:.82rem;font-weight:700;
    color:var(--ink);margin-bottom:2px;
}
.vg-feat-desc{
    font-size:.72rem;color:var(--ink-4);line-height:1.5;
}

/* ══════════════════════════════════════════════
   TABS
══════════════════════════════════════════════ */
.stTabs [data-baseweb="tab-list"]{
    background:transparent !important;
    border-bottom:1.5px solid var(--border) !important;gap:0 !important;
}
.stTabs [data-baseweb="tab"]{
    font-family:'DM Sans',sans-serif !important;
    font-size:.72rem !important;font-weight:600 !important;
    letter-spacing:.1em !important;text-transform:uppercase !important;
    color:var(--ink-4) !important;padding:.7rem 1.5rem !important;
    border:none !important;border-bottom:2.5px solid transparent !important;
    background:transparent !important;transition:color .2s !important;
}
.stTabs [aria-selected="true"]{
    color:var(--green) !important;
    border-bottom:2.5px solid var(--green) !important;
    background:transparent !important;
}
.stTabs [data-baseweb="tab-panel"]{padding-top:1.8rem !important;}

/* ══════════════════════════════════════════════
   UPLOAD PANEL
══════════════════════════════════════════════ */
.vg-upload-panel{
    background:var(--surface);
    border:1.5px solid var(--border);
    border-radius:var(--radius);
    padding:1.6rem 1.8rem;
    box-shadow:var(--shadow-sm);
    margin-bottom:1rem;
}
.vg-panel-title{
    font-size:.65rem;font-weight:700;
    letter-spacing:.16em;text-transform:uppercase;
    color:var(--ink-4);margin-bottom:1.2rem;
    display:flex;align-items:center;gap:8px;
}
.vg-panel-title::after{content:'';flex:1;height:1px;background:var(--border);}

[data-testid="stFileUploader"]{background:transparent !important;}
[data-testid="stFileUploader"]>div{
    background:var(--bg) !important;
    border:2px dashed #cbd5e1 !important;
    border-radius:10px !important;
    transition:border-color .2s,background .2s !important;
}
[data-testid="stFileUploader"]>div:hover{
    border-color:var(--green) !important;
    background:var(--green-pale) !important;
}
[data-testid="stFileUploaderDropzone"]{background:transparent !important;color:var(--ink-2) !important;}
[data-testid="stFileUploaderDropzoneInput"]{background:transparent !important;}
[data-testid="stFileUploader"] small,
[data-testid="stFileUploader"] span,
[data-testid="stFileUploader"] p{color:var(--ink-3) !important;font-family:'DM Sans',sans-serif !important;}
[data-testid="stFileUploader"] button,
[data-testid="stFileUploaderDropzone"] button{
    background:var(--green) !important;color:#fff !important;
    border:none !important;border-radius:7px !important;
    font-family:'DM Sans',sans-serif !important;
    font-size:.72rem !important;font-weight:600 !important;
    padding:.4rem 1rem !important;
    box-shadow:0 2px 6px rgba(22,163,74,.2) !important;
}
[data-testid="stFileUploader"] button:hover{
    background:var(--green-dark) !important;transform:translateY(-1px) !important;
}
[data-testid="stFileUploader"] svg{color:var(--ink-4) !important;fill:var(--ink-4) !important;}
[data-testid="stFileUploader"] label,.stFileUploader label{
    font-family:'DM Sans',sans-serif !important;
    font-size:.68rem !important;font-weight:700 !important;
    letter-spacing:.12em !important;text-transform:uppercase !important;
    color:var(--ink-3) !important;
}

.stTextInput input{
    font-family:'DM Sans',sans-serif !important;
    background:var(--surface) !important;
    border:1.5px solid var(--border) !important;
    border-radius:9px !important;color:var(--ink) !important;
    font-size:.92rem !important;padding:.6rem .9rem !important;
    box-shadow:var(--shadow-sm) !important;
    transition:border-color .2s,box-shadow .2s !important;
}
.stTextInput input:focus{
    border-color:var(--green) !important;
    box-shadow:0 0 0 3px rgba(22,163,74,.1) !important;
}
.stTextInput input::placeholder{color:var(--ink-4) !important;}
.stTextInput label{
    font-family:'DM Sans',sans-serif !important;
    font-size:.68rem !important;font-weight:700 !important;
    letter-spacing:.12em !important;text-transform:uppercase !important;
    color:var(--ink-3) !important;
}

/* ══════════════════════════════════════════════
   BUTTONS
══════════════════════════════════════════════ */
.stButton>button[kind="primary"]{
    font-family:'DM Sans',sans-serif !important;
    font-size:.82rem !important;font-weight:700 !important;
    letter-spacing:.1em !important;text-transform:uppercase !important;
    background:linear-gradient(135deg,#16a34a,#22c55e) !important;
    color:#ffffff !important;border:none !important;
    border-radius:10px !important;padding:.78rem 2rem !important;
    box-shadow:0 4px 18px rgba(22,163,74,.3) !important;
    transition:opacity .2s,transform .15s,box-shadow .2s !important;
    margin-top:.4rem !important;
}
.stButton>button[kind="primary"]:hover{
    opacity:.9 !important;transform:translateY(-2px) !important;
    box-shadow:0 8px 28px rgba(22,163,74,.35) !important;
}
.stButton>button[kind="primary"]:active{transform:translateY(0) !important;}
.stDownloadButton>button{
    font-family:'DM Sans',sans-serif !important;
    font-size:.72rem !important;font-weight:600 !important;
    letter-spacing:.08em !important;text-transform:uppercase !important;
    background:var(--surface) !important;color:var(--ink-2) !important;
    border:1.5px solid var(--border) !important;border-radius:9px !important;
    box-shadow:var(--shadow-sm) !important;transition:all .2s !important;
}
.stDownloadButton>button:hover{
    border-color:var(--green) !important;color:var(--green-dark) !important;
    background:var(--green-pale) !important;
}

/* ══════════════════════════════════════════════
   ANALYSIS PROGRESS CARD
══════════════════════════════════════════════ */
.vg-analyzing{
    background:linear-gradient(135deg,#0f172a 0%,#1a2e20 100%);
    border-radius:var(--radius);padding:1.8rem 2rem;margin:1rem 0;
    box-shadow:0 8px 32px rgba(22,163,74,.15);
    border:1px solid rgba(34,197,94,.2);
}
.vg-analyzing-header{display:flex;align-items:center;gap:14px;margin-bottom:1.6rem;}
.vg-analyzing-spinner{
    width:38px;height:38px;flex-shrink:0;
    border:3px solid rgba(34,197,94,.15);
    border-top-color:#22c55e;border-radius:50%;
    animation:vg-spin .8s linear infinite;
}
@keyframes vg-spin{to{transform:rotate(360deg)}}
.vg-analyzing-title{font-size:1rem;font-weight:700;color:#fff;letter-spacing:-.01em;}
.vg-analyzing-subtitle{font-size:.72rem;color:rgba(255,255,255,.35);font-weight:400;margin-top:2px;}
.vg-step{
    display:flex;align-items:center;gap:12px;
    padding:.55rem 0;border-bottom:1px solid rgba(255,255,255,.05);font-size:.82rem;
}
.vg-step:last-child{border-bottom:none;}
.vg-step-icon{
    width:26px;height:26px;border-radius:50%;
    display:flex;align-items:center;justify-content:center;
    font-size:.7rem;flex-shrink:0;
}
.vg-step-done{background:rgba(34,197,94,.2);color:#22c55e;}
.vg-step-active{background:rgba(34,197,94,.1);border:1px solid #22c55e;}
.vg-step-active .vg-step-dot{
    width:8px;height:8px;border-radius:50%;
    background:#22c55e;animation:vg-blink .7s ease infinite;
}
.vg-step-wait{background:rgba(255,255,255,.05);}
.vg-step-wait .vg-step-dot{
    width:6px;height:6px;border-radius:50%;background:rgba(255,255,255,.2);
}
.vg-step-label-done{color:rgba(255,255,255,.4);text-decoration:line-through;}
.vg-step-label-active{color:#fff;font-weight:600;}
.vg-step-label-wait{color:rgba(255,255,255,.25);}
.vg-analyze-bar-wrap{margin-top:1.4rem;}
.vg-analyze-bar-track{
    height:4px;border-radius:99px;
    background:rgba(255,255,255,.07);overflow:hidden;
}
.vg-analyze-bar-fill{
    height:100%;border-radius:99px;
    background:linear-gradient(90deg,var(--green),var(--green-mid));
}
.vg-analyze-bar-label{
    font-size:.6rem;font-weight:500;letter-spacing:.12em;text-transform:uppercase;
    color:rgba(255,255,255,.25);margin-top:7px;text-align:right;
}

/* Hide default Streamlit status */
[data-testid="stStatusWidget"]{display:none !important;}

/* ══════════════════════════════════════════════
   RESULT CARDS
══════════════════════════════════════════════ */
.vg-card{
    border-radius:var(--radius);padding:1.7rem 1.9rem;margin:1rem 0;
    box-shadow:var(--shadow-md);animation:vg-rise .4s ease both;
}
.vg-card-success{background:var(--surface);border:1.5px solid #86efac;border-top:4px solid var(--green);}
.vg-card-danger{background:var(--surface);border:1.5px solid var(--red-border);border-top:4px solid var(--red);}
.vg-card-header{
    display:flex;align-items:center;gap:12px;
    margin-bottom:1.3rem;padding-bottom:1rem;
    border-bottom:1px solid var(--border);
}
.vg-card-icon{
    width:40px;height:40px;border-radius:10px;
    display:flex;align-items:center;justify-content:center;
    font-size:18px;flex-shrink:0;
}
.vg-card-icon-success{background:var(--green-light);}
.vg-card-icon-danger{background:#fee2e2;}
.vg-card-title{font-size:1.05rem;font-weight:700;letter-spacing:-.01em;margin:0;line-height:1.2;}
.vg-card-title-success{color:var(--green-dark);}
.vg-card-title-danger{color:var(--red);}
.vg-card-subtitle{font-size:.72rem;color:var(--ink-4);font-weight:400;margin-top:2px;}

.vg-fields-grid{display:grid;grid-template-columns:1fr 1fr;gap:.65rem 1.4rem;margin-bottom:1.2rem;}
.vg-field{display:flex;flex-direction:column;gap:4px;}
.vg-field-label{
    font-size:.6rem;font-weight:700;letter-spacing:.14em;
    text-transform:uppercase;color:var(--ink-4);
}
.vg-field-value{
    font-family:'DM Mono',monospace;font-size:.74rem;color:var(--ink-2);
    background:var(--bg);border:1px solid var(--border);
    border-radius:6px;padding:5px 10px;word-break:break-all;
}
.vg-field-value-plain{font-size:.92rem;font-weight:600;color:var(--ink);}
.vg-field-full{grid-column:1/-1;}

.vg-scores-title{
    font-size:.6rem;font-weight:700;letter-spacing:.14em;text-transform:uppercase;
    color:var(--ink-4);margin-bottom:.75rem;
    display:flex;align-items:center;gap:8px;
}
.vg-scores-title::after{content:'';flex:1;height:1px;background:var(--border);}
.vg-score-row{display:flex;align-items:center;gap:12px;margin-bottom:.55rem;}
.vg-score-label{
    font-size:.64rem;font-weight:600;letter-spacing:.08em;text-transform:uppercase;
    color:var(--ink-3);min-width:78px;
}
.vg-score-bar-bg{flex:1;height:7px;border-radius:99px;background:#f1f5f9;overflow:hidden;}
.vg-score-bar-fill{height:100%;border-radius:99px;background:linear-gradient(90deg,var(--green),var(--green-mid));}
.vg-score-bar-fill-danger{height:100%;border-radius:99px;background:linear-gradient(90deg,var(--red),#f97316);}
.vg-score-num{font-family:'DM Mono',monospace;font-size:.74rem;font-weight:500;color:var(--ink-3);min-width:38px;text-align:right;}
.vg-sim-badge{
    display:inline-flex;align-items:center;gap:5px;
    padding:3px 10px;border-radius:99px;font-size:.8rem;font-weight:700;
}
.vg-sim-badge-danger{background:#fee2e2;color:var(--red);}
.vg-sim-badge-success{background:var(--green-light);color:var(--green-dark);}

/* ══════════════════════════════════════════════
   INFO & MISC
══════════════════════════════════════════════ */
.vg-info{
    background:var(--green-pale);border:1px solid #bbf7d0;
    border-left:3px solid var(--green);
    border-radius:9px;padding:.85rem 1.1rem;
    font-size:.8rem;color:var(--ink-2);line-height:1.65;
}
[data-testid="stMetric"]{
    background:var(--surface) !important;border:1.5px solid var(--border) !important;
    border-radius:10px !important;padding:.85rem 1rem !important;
    box-shadow:var(--shadow-sm) !important;
}
[data-testid="stMetricLabel"]{
    font-family:'DM Sans',sans-serif !important;font-size:.62rem !important;
    font-weight:700 !important;letter-spacing:.12em !important;
    text-transform:uppercase !important;color:var(--ink-4) !important;
}
[data-testid="stMetricValue"]{
    font-family:'DM Mono',monospace !important;font-size:1.3rem !important;color:var(--ink) !important;
}
.stDataFrame,[data-testid="stDataFrame"]{
    border:1.5px solid var(--border) !important;border-radius:10px !important;
    overflow:hidden !important;box-shadow:var(--shadow-sm) !important;
}
.stAlert{
    border-radius:9px !important;border:none !important;
    font-family:'DM Sans',sans-serif !important;font-size:.84rem !important;
}
.vg-empty{text-align:center;padding:3rem 1rem;color:var(--ink-4);}
.vg-empty-icon{font-size:2.5rem;margin-bottom:.8rem;opacity:.4;}
.vg-empty-text{font-size:.84rem;line-height:1.6;}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
#  CONSTANTS
# ─────────────────────────────────────────────────────────────────────────────
SHIELD_SVG = """<svg viewBox="0 0 24 24" fill="none" stroke="#ffffff" stroke-width="2"
    stroke-linecap="round" stroke-linejoin="round">
  <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
  <polyline points="9 12 11 14 15 10"/>
</svg>"""


# ─────────────────────────────────────────────────────────────────────────────
#  SPLASH
# ─────────────────────────────────────────────────────────────────────────────
if not st.session_state.app_ready:
    import time
    st.markdown(f"""
    <div class="vg-sc vg-sc-tl"></div><div class="vg-sc vg-sc-tr"></div>
    <div class="vg-sc vg-sc-bl"></div><div class="vg-sc vg-sc-br"></div>
    <div class="vg-splash">
        <div class="vg-splash-ring"><div class="vg-splash-icon">{SHIELD_SVG}</div></div>
        <div class="vg-splash-wordmark">Video<em>Guard</em></div>
        <div class="vg-splash-tagline">Copyright Detection &amp; Ownership Verification</div>
        <div class="vg-splash-bar-wrap">
            <div class="vg-splash-bar-track"><div class="vg-splash-bar-fill"></div></div>
            <div class="vg-splash-status">Initialising system…</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    time.sleep(3.4)
    st.session_state.app_ready = True
    st.rerun()
    st.stop()


# ─────────────────────────────────────────────────────────────────────────────
#  HELPERS — identical logic
# ─────────────────────────────────────────────────────────────────────────────

def _save_uploaded_file(uploaded_file: st.runtime.uploaded_file_manager.UploadedFile) -> str:
    suffix = Path(uploaded_file.name).suffix or ".mp4"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(uploaded_file.getbuffer())
        return tmp.name


def _load_registry_records() -> list[dict]:
    registry_path = Path(__file__).resolve().parent / "data" / "registry.json"
    if not registry_path.exists():
        return []
    try:
        content = registry_path.read_text(encoding="utf-8").strip()
        if not content:
            return []
        parsed = json.loads(content)
        return parsed if isinstance(parsed, list) else []
    except (json.JSONDecodeError, OSError):
        return []


def _video_store_dir() -> Path:
    store = Path(__file__).resolve().parent / "data" / "video_store"
    store.mkdir(parents=True, exist_ok=True)
    return store


def _persist_registered_video(video_path: str, video_hash: str) -> str:
    source = Path(video_path)
    target = _video_store_dir() / f"{video_hash}{source.suffix.lower() or '.mp4'}"
    if not target.exists():
        shutil.copy2(source, target)
    return str(target)


def _find_best_registry_match(
    new_video_path: str, records: list[dict]
) -> tuple[dict | None, dict | None]:
    best_result: dict | None = None
    best_record: dict | None = None
    for record in records:
        candidate_path = record.get("source_video_path")
        if candidate_path is None and isinstance(record.get("fingerprint"), dict):
            candidate_path = record["fingerprint"].get("source_video_path")
        if not candidate_path:
            continue
        candidate_file = Path(str(candidate_path))
        if not candidate_file.exists():
            continue
        candidate_result = run_full_pipeline(new_video_path, str(candidate_file))
        if best_result is None or float(candidate_result.get("final_score", 0.0)) > float(
            best_result.get("final_score", 0.0)
        ):
            best_result = candidate_result
            best_record = record
    return best_result, best_record


def _render_download_report(result: dict, record: dict) -> None:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        report_path = generate_report(result=result, record=record, output_path=tmp.name)
    st.download_button(
        label="↓  Export PDF Report",
        data=Path(report_path).read_bytes(),
        file_name="videoguard_report.pdf",
        mime="application/pdf",
        use_container_width=True,
    )


def _analyzing_card(steps: list[tuple[str, str]]) -> str:
    done_count = sum(1 for _, s in steps if s == "done")
    pct = int(done_count / len(steps) * 100) if steps else 0
    rows = ""
    for label, state in steps:
        if state == "done":
            icon = '<span style="color:#22c55e;font-size:13px">✓</span>'
            icls, lcls = "vg-step-icon vg-step-done", "vg-step-label-done"
        elif state == "active":
            icon = '<span class="vg-step-dot"></span>'
            icls, lcls = "vg-step-icon vg-step-active", "vg-step-label-active"
        else:
            icon = '<span class="vg-step-dot"></span>'
            icls, lcls = "vg-step-icon vg-step-wait", "vg-step-label-wait"
        rows += f'<div class="vg-step"><div class="{icls}">{icon}</div><span class="{lcls}">{label}</span></div>'
    return f"""
    <div class="vg-analyzing">
        <div class="vg-analyzing-header">
            <div class="vg-analyzing-spinner"></div>
            <div>
                <div class="vg-analyzing-title">Analysing video…</div>
                <div class="vg-analyzing-subtitle">Please wait while the pipeline runs</div>
            </div>
        </div>
        {rows}
        <div class="vg-analyze-bar-wrap">
            <div class="vg-analyze-bar-track">
                <div class="vg-analyze-bar-fill" style="width:{pct}%"></div>
            </div>
            <div class="vg-analyze-bar-label">{pct}% complete</div>
        </div>
    </div>"""


def _score_bar(label: str, value: float, danger: bool = False) -> str:
    cls = "vg-score-bar-fill-danger" if danger else "vg-score-bar-fill"
    pct = min(max(value * 100, 0), 100)
    return f"""<div class="vg-score-row">
        <span class="vg-score-label">{label}</span>
        <div class="vg-score-bar-bg"><div class="{cls}" style="width:{pct:.1f}%"></div></div>
        <span class="vg-score-num">{value:.3f}</span>
    </div>"""


def _field(label: str, value: str, mono: bool = True, full: bool = False) -> str:
    val_cls  = "vg-field-value" if mono else "vg-field-value-plain"
    grid_cls = "vg-field vg-field-full" if full else "vg-field"
    return f'<div class="{grid_cls}"><div class="vg-field-label">{label}</div><div class="{val_cls}">{value}</div></div>'


# ─────────────────────────────────────────────────────────────────────────────
#  TABS
# ─────────────────────────────────────────────────────────────────────────────

def _render_check_video_tab() -> None:
    # Upload panel
    st.markdown('<div class="vg-upload-panel"><div class="vg-panel-title">Upload Videos</div>', unsafe_allow_html=True)
    col_left, col_right = st.columns([1, 1], gap="large")
    with col_left:
        new_video  = st.file_uploader("New Video", type=["mp4","mov","avi","mkv"], key="new_video")
        owner_name = st.text_input("Owner Name", placeholder="e.g. Mithilesh Kumar")
    with col_right:
        reference_video = st.file_uploader("Reference Video (optional)", type=["mp4","mov","avi","mkv"], key="reference_video")
        st.markdown(
            '<div class="vg-info" style="margin-top:.4rem">Upload a previously registered video as reference. '
            'If omitted, the system automatically scans all registered videos and compares against the closest match.</div>',
            unsafe_allow_html=True,
        )
    st.markdown('</div>', unsafe_allow_html=True)

    analyze_clicked = st.button("Run Analysis", type="primary", use_container_width=True)

    if not analyze_clicked:
        return

    if new_video is None:
        st.error("Please upload a video to analyze.")
        return
    if not owner_name.strip():
        st.error("Please enter the owner name.")
        return

    progress_slot  = st.empty()
    adapter        = get_adapter()
    new_video_path = _save_uploaded_file(new_video)
    reference_path = _save_uploaded_file(reference_video) if reference_video else None
    new_video_hash = compute_video_hash(new_video_path)
    matched_record = None

    if reference_path:
        progress_slot.markdown(_analyzing_card([
            ("Extracting audio features",  "active"),
            ("Extracting video frames",    "wait"),
            ("Computing similarity scores","wait"),
            ("Applying decision threshold","wait"),
        ]), unsafe_allow_html=True)
        progress_slot.markdown(_analyzing_card([
            ("Extracting audio features",  "done"),
            ("Extracting video frames",    "active"),
            ("Computing similarity scores","wait"),
            ("Applying decision threshold","wait"),
        ]), unsafe_allow_html=True)
        progress_slot.markdown(_analyzing_card([
            ("Extracting audio features",  "done"),
            ("Extracting video frames",    "done"),
            ("Computing similarity scores","active"),
            ("Applying decision threshold","wait"),
        ]), unsafe_allow_html=True)
        result = run_full_pipeline(new_video_path, reference_path)
        progress_slot.markdown(_analyzing_card([
            ("Extracting audio features",  "done"),
            ("Extracting video frames",    "done"),
            ("Computing similarity scores","done"),
            ("Applying decision threshold","active"),
        ]), unsafe_allow_html=True)
    else:
        records = _load_registry_records()
        exact   = next((e for e in records if e.get("video_hash") == new_video_hash), None)
        if exact is not None:
            progress_slot.markdown(_analyzing_card([
                ("Loading registry records",           "done"),
                ("Comparing against registered videos","done"),
                ("Scoring best match",                 "done"),
                ("Applying decision threshold",        "active"),
            ]), unsafe_allow_html=True)
            result = {"audio_score":1.0,"video_score":1.0,"final_score":1.0,
                      "verdict":"COPY","message":"Exact duplicate found in registry."}
            matched_record = exact
        else:
            progress_slot.markdown(_analyzing_card([
                ("Loading registry records",           "done"),
                ("Comparing against registered videos","active"),
                ("Scoring best match",                 "wait"),
                ("Applying decision threshold",        "wait"),
            ]), unsafe_allow_html=True)
            best_result, best_record = _find_best_registry_match(new_video_path, records)
            progress_slot.markdown(_analyzing_card([
                ("Loading registry records",           "done"),
                ("Comparing against registered videos","done"),
                ("Scoring best match",                 "active"),
                ("Applying decision threshold",        "wait"),
            ]), unsafe_allow_html=True)
            if best_result is None:
                result = {"audio_score":0.0,"video_score":0.0,"final_score":0.0,
                          "verdict":"ORIGINAL","message":"No comparable registered videos found."}
            else:
                result, matched_record = best_result, best_record
            progress_slot.markdown(_analyzing_card([
                ("Loading registry records",           "done"),
                ("Comparing against registered videos","done"),
                ("Scoring best match",                 "done"),
                ("Applying decision threshold",        "active"),
            ]), unsafe_allow_html=True)

        threshold = float(get_config().get("analysis", {}).get("threshold", 0.75))
        result["verdict"] = "COPY" if float(result.get("final_score", 0.0)) >= threshold else "ORIGINAL"

    progress_slot.empty()

    # ── ORIGINAL ──────────────────────────────────────────────────────────
    if result.get("verdict") == "ORIGINAL":
        record = adapter.register_video(
            video_hash=new_video_hash,
            owner=owner_name.strip(),
            fingerprint={
                "audio_score": result.get("audio_score", 0.0),
                "video_score": result.get("video_score", 0.0),
                "final_score": result.get("final_score", 0.0),
                "source_video_path": _persist_registered_video(new_video_path, new_video_hash),
            },
        )
        scores = (
            _score_bar("Audio", float(result.get("audio_score", 0.0)))
            + _score_bar("Video", float(result.get("video_score", 0.0)))
            + _score_bar("Final", float(result.get("final_score", 0.0)))
        )
        st.markdown(f"""
        <div class="vg-card vg-card-success">
            <div class="vg-card-header">
                <div class="vg-card-icon vg-card-icon-success">✓</div>
                <div>
                    <div class="vg-card-title vg-card-title-success">Video Registered Successfully</div>
                    <div class="vg-card-subtitle">Ownership record stored in mock blockchain registry</div>
                </div>
            </div>
            <div class="vg-fields-grid">
                {_field("Owner",     record.get("owner","N/A"),     mono=False)}
                {_field("Timestamp", record.get("timestamp","N/A"), mono=False)}
                {_field("IPFS CID",  record.get("cid","N/A"),       full=True)}
                {_field("TX Hash",   record.get("tx_hash","N/A"),   full=True)}
            </div>
            <div class="vg-scores-title">Similarity Scores</div>
            {scores}
        </div>""", unsafe_allow_html=True)
        _render_download_report(result=result, record=record)

    # ── COPY ──────────────────────────────────────────────────────────────
    else:
        ref_hash = compute_video_hash(reference_path) if reference_path else new_video_hash
        orig     = matched_record or adapter.lookup_video(ref_hash)
        fs       = float(result.get("final_score", 0.0))
        scores   = (
            _score_bar("Audio", float(result.get("audio_score", 0.0)), True)
            + _score_bar("Video", float(result.get("video_score", 0.0)), True)
            + _score_bar("Final", fs, True)
        )
        od = orig.get("owner","Unknown")   if orig else "Unknown"
        cd = orig.get("cid","N/A")         if orig else "N/A"
        td = orig.get("tx_hash","N/A")     if orig else "N/A"
        ts = orig.get("timestamp","N/A")   if orig else "N/A"
        st.markdown(f"""
        <div class="vg-card vg-card-danger">
            <div class="vg-card-header">
                <div class="vg-card-icon vg-card-icon-danger">⚠</div>
                <div>
                    <div class="vg-card-title vg-card-title-danger">Copyright Violation Detected</div>
                    <div class="vg-card-subtitle">
                        This video matches a registered original —
                        <span class="vg-sim-badge vg-sim-badge-danger">{fs*100:.1f}% similarity</span>
                    </div>
                </div>
            </div>
            <div class="vg-fields-grid">
                {_field("Original Owner", od, mono=False)}
                {_field("Registered On",  ts, mono=False)}
                {_field("IPFS CID",       cd, full=True)}
                {_field("TX Hash",        td, full=True)}
            </div>
            <div class="vg-scores-title">Similarity Scores</div>
            {scores}
        </div>""", unsafe_allow_html=True)
        _render_download_report(result=result, record=orig or {"owner":od,"cid":cd,"tx_hash":td,"timestamp":ts})


def _render_registry_tab() -> None:
    records = _load_registry_records()
    n = len(records)

    # Live registry stats
    st.markdown(f"""
    <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:.9rem;margin-bottom:1.4rem">
        <div style="background:var(--surface);border:1.5px solid var(--border);border-radius:12px;
                    padding:1.1rem 1.3rem;text-align:center;box-shadow:var(--shadow-sm)">
            <div style="font-family:'DM Mono',monospace;font-size:2rem;font-weight:500;
                        color:var(--green);line-height:1">{n}</div>
            <div style="font-size:.62rem;font-weight:700;letter-spacing:.14em;
                        text-transform:uppercase;color:var(--ink-4);margin-top:4px">Videos Registered</div>
        </div>
        <div style="background:var(--surface);border:1.5px solid var(--border);border-radius:12px;
                    padding:1.1rem 1.3rem;text-align:center;box-shadow:var(--shadow-sm)">
            <div style="font-family:'DM Mono',monospace;font-size:2rem;font-weight:500;
                        color:var(--ink);line-height:1">0.75</div>
            <div style="font-size:.62rem;font-weight:700;letter-spacing:.14em;
                        text-transform:uppercase;color:var(--ink-4);margin-top:4px">Detection Threshold</div>
        </div>
        <div style="background:var(--surface);border:1.5px solid var(--border);border-radius:12px;
                    padding:1.1rem 1.3rem;text-align:center;box-shadow:var(--shadow-sm)">
            <div style="font-family:'DM Mono',monospace;font-size:2rem;font-weight:500;
                        color:var(--ink);line-height:1">3</div>
            <div style="font-size:.62rem;font-weight:700;letter-spacing:.14em;
                        text-transform:uppercase;color:var(--ink-4);margin-top:4px">Analysis Methods</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if not records:
        st.markdown("""
        <div class="vg-empty">
            <div class="vg-empty-icon">🗄️</div>
            <div class="vg-empty-text">No videos registered yet.<br>
            Use the <strong>Check Video</strong> tab to register your first video.</div>
        </div>""", unsafe_allow_html=True)
    else:
        st.dataframe(
            [{"Owner": r.get("owner",""), "CID": r.get("cid",""),
              "TX Hash": r.get("tx_hash",""), "Timestamp": r.get("timestamp","")}
             for r in records],
            use_container_width=True, hide_index=True,
        )


# ─────────────────────────────────────────────────────────────────────────────
#  MAIN
# ─────────────────────────────────────────────────────────────────────────────

def main() -> None:
    records = _load_registry_records()
    n       = len(records)

    # ── Dark hero banner ──────────────────────────────────────────────────
    st.markdown(f"""
    <div class="vg-hero">
        <div class="vg-hero-grid"></div>
        <div class="vg-hero-inner">
            <div class="vg-hero-left">
                <div class="vg-hero-logo">{SHIELD_SVG}</div>
                <div>
                    <div class="vg-hero-wordmark">Video<em>Guard</em></div>
                    <div class="vg-hero-sub">Copyright Detection &amp; Ownership Verification</div>
                </div>
            </div>
            <div class="vg-hero-badge">System Active</div>
        </div>
        <div class="vg-stats">
            <div class="vg-stat">
                <div class="vg-stat-val">{n}<span> videos</span></div>
                <div class="vg-stat-lbl">In Registry</div>
            </div>
            <div class="vg-stat">
                <div class="vg-stat-val">3<span> layers</span></div>
                <div class="vg-stat-lbl">Analysis Pipeline</div>
            </div>
            <div class="vg-stat">
                <div class="vg-stat-val">0.75<span> score</span></div>
                <div class="vg-stat-lbl">Detection Threshold</div>
            </div>
        </div>
        <div class="vg-how">
            <div class="vg-how-step"><div class="vg-how-num">1</div>Upload Video</div>
            <span class="vg-how-arrow">→</span>
            <div class="vg-how-step"><div class="vg-how-num">2</div>Extract Features</div>
            <span class="vg-how-arrow">→</span>
            <div class="vg-how-step"><div class="vg-how-num">3</div>Compute Similarity</div>
            <span class="vg-how-arrow">→</span>
            <div class="vg-how-step"><div class="vg-how-num">4</div>Fusion Model</div>
            <span class="vg-how-arrow">→</span>
            <div class="vg-how-step"><div class="vg-how-num">5</div>Verdict + Register</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Feature cards ─────────────────────────────────────────────────────
    st.markdown("""
    <div class="vg-features">
        <div class="vg-feat">
            <div class="vg-feat-icon">🔊</div>
            <div>
                <div class="vg-feat-title">Audio Analysis</div>
                <div class="vg-feat-desc">MFCC + Chroma features with DTW and cosine similarity for robust audio fingerprinting</div>
            </div>
        </div>
        <div class="vg-feat">
            <div class="vg-feat-icon">🎞️</div>
            <div>
                <div class="vg-feat-title">Visual Analysis</div>
                <div class="vg-feat-desc">ORB keypoints, perceptual hashing, and color histogram correlation across sampled frames</div>
            </div>
        </div>
        <div class="vg-feat">
            <div class="vg-feat-icon">⛓️</div>
            <div>
                <div class="vg-feat-title">Blockchain Registry</div>
                <div class="vg-feat-desc">Immutable ownership records with IPFS CID and transaction hash for tamper-proof provenance</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Tabs ──────────────────────────────────────────────────────────────
    tab_check, tab_registry = st.tabs(["Check Video", "Registry"])
    with tab_check:
        _render_check_video_tab()
    with tab_registry:
        _render_registry_tab()


if __name__ == "__main__":
    main()