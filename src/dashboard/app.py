"""
🏠 Job Market Intelligence — Page d'accueil
Dashboard principal avec stats globales et lancement du pipeline.
"""
import sys
import logging
from pathlib import Path
from datetime import datetime

import streamlit as st

# ── Path setup ────────────────────────────────────────────────────────────────
ROOT_DIR = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

from src.database.db import (
    init_db, get_db, get_jobs_count, get_skills_count,
    get_recent_jobs, get_last_update, get_top_companies,
)

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Job Market Intelligence",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif !important;
}

/* Hero Banner */
.hero-banner {
    background: linear-gradient(135deg, #0d1117 0%, #161b22 50%, #0d2137 100%);
    border: 1px solid rgba(88, 166, 255, 0.15);
    border-radius: 20px;
    padding: 40px 50px;
    margin-bottom: 30px;
    position: relative;
    overflow: hidden;
}
.hero-banner::before {
    content: '';
    position: absolute;
    top: -50%;
    right: -10%;
    width: 400px;
    height: 400px;
    background: radial-gradient(circle, rgba(88,166,255,0.08) 0%, transparent 70%);
    pointer-events: none;
}
.hero-title {
    font-size: 2.8rem;
    font-weight: 700;
    background: linear-gradient(135deg, #58a6ff 0%, #bc8cff 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin: 0 0 8px 0;
    line-height: 1.2;
}
.hero-subtitle {
    font-size: 1.1rem;
    color: #8b949e;
    margin: 0;
    font-weight: 400;
}
.hero-badge {
    display: inline-block;
    background: rgba(63, 185, 80, 0.15);
    color: #3fb950;
    border: 1px solid rgba(63, 185, 80, 0.3);
    border-radius: 20px;
    padding: 4px 14px;
    font-size: 0.8rem;
    font-weight: 600;
    margin-bottom: 16px;
}

/* Metric Cards */
.metric-card {
    background: linear-gradient(135deg, #161b22 0%, #0d1117 100%);
    border: 1px solid rgba(88, 166, 255, 0.15);
    border-radius: 16px;
    padding: 24px;
    text-align: center;
    transition: all 0.3s ease;
    position: relative;
    overflow: hidden;
}
.metric-card:hover {
    border-color: rgba(88, 166, 255, 0.4);
    transform: translateY(-2px);
    box-shadow: 0 8px 32px rgba(88, 166, 255, 0.1);
}
.metric-icon {
    font-size: 2rem;
    margin-bottom: 8px;
}
.metric-value {
    font-size: 2.4rem;
    font-weight: 700;
    background: linear-gradient(135deg, #58a6ff, #bc8cff);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    line-height: 1;
    margin-bottom: 4px;
}
.metric-label {
    font-size: 0.85rem;
    color: #8b949e;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

/* Job Cards */
.job-card {
    background: #161b22;
    border: 1px solid #30363d;
    border-radius: 12px;
    padding: 16px 20px;
    margin-bottom: 10px;
    transition: all 0.2s ease;
}
.job-card:hover {
    border-color: #58a6ff;
    background: #1c2333;
}
.job-title { color: #58a6ff; font-weight: 600; font-size: 0.95rem; }
.job-company { color: #c9d1d9; font-size: 0.88rem; }
.job-meta { color: #8b949e; font-size: 0.8rem; }
.badge {
    display: inline-block;
    padding: 2px 10px;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 500;
    margin-right: 5px;
}
.badge-remote { background: rgba(63,185,80,0.15); color: #3fb950; }
.badge-cat { background: rgba(88,166,255,0.15); color: #58a6ff; }
.badge-level-junior { background: rgba(210,153,34,0.15); color: #d29922; }
.badge-level-senior { background: rgba(188,140,255,0.15); color: #bc8cff; }
.badge-level-mid { background: rgba(88,166,255,0.15); color: #58a6ff; }
.badge-level-lead { background: rgba(248,81,73,0.15); color: #f85149; }

/* Section headers */
.section-header {
    font-size: 1.2rem;
    font-weight: 600;
    color: #c9d1d9;
    margin: 24px 0 16px 0;
    padding-bottom: 8px;
    border-bottom: 1px solid #21262d;
}

/* Alert box */
.alert-info {
    background: rgba(88,166,255,0.08);
    border: 1px solid rgba(88,166,255,0.25);
    border-radius: 10px;
    padding: 16px 20px;
    color: #c9d1d9;
    margin-bottom: 20px;
}
</style>
""", unsafe_allow_html=True)


# ── Init DB ───────────────────────────────────────────────────────────────────
init_db()


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🧠 Job Market Intelligence")
    st.markdown("---")
    st.markdown("**Navigation**")
    st.markdown("""
    - 🏠 **Home** ← vous êtes ici
    - 📊 **Market Overview**
    - 🧠 **Skills Analysis**
    - 📈 **Trends & Predictions**
    - 🎯 **Skill Recommender**
    """)
    st.markdown("---")

    # Bouton de refresh
    if st.button("🔄 Collecter les offres", use_container_width=True, type="primary"):
        with st.spinner("⏳ Pipeline en cours... (30-60 sec)"):
            try:
                from src.scraper.scheduler import run_pipeline
                stats = run_pipeline()
                st.success(f"✅ {stats['saved']} offres sauvegardées !")
                st.balloons()
                st.rerun()
            except Exception as e:
                st.error(f"❌ Erreur: {e}")

    st.markdown("---")
    st.markdown("""
    <div style='font-size:0.75rem; color:#8b949e;'>
    🔗 Sources : Remotive API<br>
    ⚙️ NLP : regex + 400+ skills<br>
    🤖 ML : Scikit-Learn
    </div>
    """, unsafe_allow_html=True)


# ── Hero Banner ───────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero-banner">
    <div class="hero-badge">🟢 LIVE DATA</div>
    <h1 class="hero-title">Job Market Intelligence</h1>
    <p class="hero-subtitle">
        Analyse en temps réel du marché de l'emploi tech · 
        Extraction automatique de compétences · 
        Prédiction de tendances par Machine Learning
    </p>
</div>
""", unsafe_allow_html=True)


# ── Métriques globales ────────────────────────────────────────────────────────
db = get_db()
jobs_count = get_jobs_count(db)
skills_count = get_skills_count(db)
last_update = get_last_update(db)
companies = get_top_companies(db, limit=500)
companies_count = len(companies)

last_update_str = last_update.strftime("%d/%m %H:%M") if last_update else "Jamais"

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-icon">💼</div>
        <div class="metric-value">{jobs_count:,}</div>
        <div class="metric-label">Offres collectées</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-icon">🧠</div>
        <div class="metric-value">{skills_count}</div>
        <div class="metric-label">Skills détectés</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-icon">🏢</div>
        <div class="metric-value">{companies_count}</div>
        <div class="metric-label">Entreprises</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-icon">🕐</div>
        <div class="metric-value" style="font-size:1.4rem;">{last_update_str}</div>
        <div class="metric-label">Dernière MàJ</div>
    </div>
    """, unsafe_allow_html=True)


# ── Alerte si pas de données ──────────────────────────────────────────────────
if jobs_count == 0:
    st.markdown("""
    <div class="alert-info">
        ℹ️ <strong>Aucune donnée disponible.</strong> 
        Clique sur <strong>🔄 Collecter les offres</strong> dans la sidebar pour lancer le pipeline.
        La collecte prend environ 30-60 secondes.
    </div>
    """, unsafe_allow_html=True)
else:
    # ── Offres récentes ───────────────────────────────────────────────────────
    st.markdown('<div class="section-header">🕐 Dernières offres collectées</div>', unsafe_allow_html=True)

    recent = get_recent_jobs(db, limit=8)
    for job in recent:
        level_class = f"badge-level-{job.level or 'mid'}"
        remote_class = "badge-remote"
        date_str = job.published_at.strftime("%d/%m/%Y") if job.published_at else "N/A"

        skills_html = ""
        for skill in (job.skills or [])[:5]:
            skills_html += f'<span class="badge badge-cat">{skill.name}</span>'

        st.markdown(f"""
        <div class="job-card">
            <div class="job-title">
                <a href="{job.url}" target="_blank" style="color:#58a6ff; text-decoration:none;">
                    {job.title}
                </a>
            </div>
            <div class="job-company">🏢 {job.company or 'Unknown'} &nbsp;·&nbsp; 📍 {job.location or 'Remote'}</div>
            <div style="margin-top: 8px;">
                <span class="badge {remote_class}">{job.remote_type or 'remote'}</span>
                <span class="badge {level_class}">{job.level or 'mid'}</span>
                <span class="badge badge-cat">{job.category or 'Tech'}</span>
                {skills_html}
            </div>
            <div class="job-meta" style="margin-top:6px;">📅 Publié le {date_str}</div>
        </div>
        """, unsafe_allow_html=True)

db.close()

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("""
<div style="text-align:center; color:#8b949e; font-size:0.8rem; padding: 10px;">
    🧠 Job Market Intelligence · Built with Python, Streamlit & Scikit-Learn · 
    <a href="https://github.com" style="color:#58a6ff;">GitHub</a>
</div>
""", unsafe_allow_html=True)
