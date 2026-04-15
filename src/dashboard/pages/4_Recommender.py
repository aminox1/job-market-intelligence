"""
🎯 Skill Recommender — Recommandation personnalisée basée sur ton profil
"""
import sys
from pathlib import Path
from collections import Counter

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np

ROOT_DIR = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

from src.database.db import init_db, get_db, get_top_skills, get_all_jobs, get_jobs_count
from src.nlp.skill_extractor import SKILLS_DATABASE, get_all_known_skills

st.set_page_config(page_title="Skill Recommender · JMI", page_icon="🎯", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif !important; }
.page-title {
    font-size: 2rem; font-weight: 700;
    background: linear-gradient(135deg, #f85149, #ffa657);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
}
.page-subtitle { color: #8b949e; font-size: 0.95rem; margin-bottom: 24px; }
.section-header {
    font-size: 1.1rem; font-weight: 600; color: #c9d1d9;
    margin: 28px 0 14px 0; padding-bottom: 8px; border-bottom: 1px solid #21262d;
}
.rec-card {
    background: linear-gradient(135deg, #161b22 0%, #0d1117 100%);
    border: 1px solid rgba(255,166,87,0.2);
    border-radius: 14px; padding: 20px; margin-bottom: 12px;
    transition: all 0.2s;
}
.rec-card:hover { border-color: rgba(255,166,87,0.5); transform: translateX(4px); }
.rec-rank { font-size: 1.5rem; font-weight: 700; color: #ffa657; }
.rec-skill { font-size: 1.1rem; font-weight: 600; color: #c9d1d9; }
.rec-desc { font-size: 0.85rem; color: #8b949e; margin-top: 4px; }
.rec-demand { font-size: 0.85rem; color: #3fb950; font-weight: 500; }
.match-card {
    background: #161b22; border: 1px solid #30363d;
    border-radius: 12px; padding: 16px; margin-bottom: 8px;
}
.match-title { color: #58a6ff; font-weight: 600; font-size: 0.9rem; text-decoration: none; }
.match-company { color: #8b949e; font-size: 0.83rem; }
.match-score {
    background: rgba(63,185,80,0.15); color: #3fb950;
    border-radius: 20px; padding: 2px 10px;
    font-size: 0.8rem; font-weight: 600;
}
.profile-card {
    background: linear-gradient(135deg, #1a1f35 0%, #0d1117 100%);
    border: 1px solid rgba(88,166,255,0.2);
    border-radius: 16px; padding: 24px; margin-bottom: 20px;
}
.score-circle {
    width: 80px; height: 80px;
    border-radius: 50%;
    background: conic-gradient(#3fb950 var(--pct), #21262d 0);
    display: flex; align-items: center; justify-content: center;
    font-weight: 700; color: #c9d1d9; font-size: 1.1rem;
}
</style>
""", unsafe_allow_html=True)

PLOTLY_DARK = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(13,17,23,0.5)",
    font=dict(color="#c9d1d9", family="Inter"),
)

init_db()
db = get_db()

st.markdown('<div class="page-title">🎯 Skill Recommender</div>', unsafe_allow_html=True)
st.markdown('<div class="page-subtitle">Analyse ton profil et découvre quelles compétences apprendre pour maximiser tes chances de recrutement</div>', unsafe_allow_html=True)

jobs_count = get_jobs_count(db)
if jobs_count == 0:
    st.warning("⚠️ Aucune donnée. Lance le pipeline depuis la page Home.")
    db.close()
    st.stop()

all_known = get_all_known_skills()
top_skills_data = get_top_skills(db, limit=100)
market_skills = {s["skill"]: s["count"] for s in top_skills_data}

# ── Input profil ──────────────────────────────────────────────────────────────
st.markdown('<div class="section-header">👤 Ton profil de compétences</div>', unsafe_allow_html=True)

col_inp1, col_inp2 = st.columns([2, 1])

with col_inp1:
    user_skills_raw = st.multiselect(
        "🧠 Sélectionne tes compétences actuelles :",
        options=sorted(all_known),
        default=[s for s in ["python", "docker", "machine learning", "flask", "git", "sql"] if s in all_known],
        help="Commence à taper pour filtrer les compétences",
        max_selections=30,
    )

    target_role = st.selectbox(
        "🎯 Rôle ciblé :",
        options=["Data Scientist / ML Engineer", "Backend Developer", "Full Stack Developer",
                 "DevOps / Cloud Engineer", "Data Engineer", "Frontend Developer"],
        index=0,
    )

with col_inp2:
    experience = st.select_slider(
        "📅 Expérience",
        options=["Étudiant", "Junior (0-2 ans)", "Mid (2-5 ans)", "Senior (5+ ans)"],
        value="Junior (0-2 ans)",
    )
    remote_pref = st.radio("🌍 Préférence", ["Remote", "Hybrid", "Pas de préférence"], index=0)

if not user_skills_raw:
    st.info("👆 Sélectionne tes compétences pour voir les recommandations.")
    db.close()
    st.stop()

user_skills = set(s.lower() for s in user_skills_raw)

# ── Score de matching ─────────────────────────────────────────────────────────
st.markdown('<div class="section-header">📊 Ton profil vs le marché</div>', unsafe_allow_html=True)

market_top20 = set(list(market_skills.keys())[:20])
matched = user_skills.intersection(market_top20)
match_rate = int((len(matched) / max(len(market_top20), 1)) * 100)

col_s1, col_s2, col_s3 = st.columns(3)
with col_s1:
    st.metric("🎯 Match avec le Top 20", f"{match_rate}%",
              delta="Excellent !" if match_rate >= 60 else "À améliorer")
with col_s2:
    st.metric("✅ Skills validés", len(matched), f"sur {len(market_top20)} top skills")
with col_s3:
    total_demand = sum(market_skills.get(s, 0) for s in user_skills)
    st.metric("📈 Demande totale", total_demand, "offres matching tes skills")

# Radar chart du profil
categories_present = {}
for skill in user_skills:
    for cat, skills_list in SKILLS_DATABASE.items():
        if skill in skills_list:
            categories_present[cat] = categories_present.get(cat, 0) + 1

cat_labels = list(categories_present.keys())
cat_values = list(categories_present.values())

if cat_labels:
    fig_radar = go.Figure(go.Scatterpolar(
        r=cat_values + [cat_values[0]],
        theta=cat_labels + [cat_labels[0]],
        fill="toself",
        fillcolor="rgba(88,166,255,0.15)",
        line=dict(color="#58a6ff", width=2),
        name="Ton profil",
    ))
    fig_radar.update_layout(
        **PLOTLY_DARK,
        polar=dict(
            radialaxis=dict(visible=True, color="#30363d"),
            angularaxis=dict(color="#8b949e"),
            bgcolor="rgba(0,0,0,0)",
        ),
        height=350, showlegend=False,
        title="Répartition de tes compétences par domaine",
    )
    st.plotly_chart(fig_radar, use_container_width=True)

# ── Recommandations ───────────────────────────────────────────────────────────
st.markdown('<div class="section-header">🚀 Skills recommandés à apprendre</div>', unsafe_allow_html=True)

missing_market_skills = [
    (skill, count) for skill, count in market_skills.items()
    if skill not in user_skills and count > 0
]
missing_market_skills.sort(key=lambda x: x[1], reverse=True)

ROLE_BOOST = {
    "Data Scientist / ML Engineer": ["python", "machine learning", "deep learning", "tensorflow",
                                      "pytorch", "pandas", "numpy", "scikit-learn", "mlflow", "pyspark"],
    "Backend Developer": ["node.js", "postgresql", "redis", "docker", "kubernetes", "fastapi",
                           "spring boot", "kafka", "grpc", "microservices"],
    "Full Stack Developer": ["react", "typescript", "next.js", "postgresql", "docker",
                              "graphql", "tailwind", "jest", "mongodb"],
    "DevOps / Cloud Engineer": ["kubernetes", "terraform", "aws", "prometheus", "grafana",
                                  "helm", "ansible", "argocd", "docker", "linux"],
    "Data Engineer": ["apache spark", "kafka", "airflow", "dbt", "snowflake", "postgresql",
                       "python", "pyspark", "bigquery", "databricks"],
    "Frontend Developer": ["react", "typescript", "next.js", "tailwind", "vue.js", "webpack",
                            "jest", "storybook", "graphql", "vite"],
}

role_skills = set(ROLE_BOOST.get(target_role, []))

# Score composite : demande marché + pertinence pour le rôle cible
recommendations = []
for skill, market_count in missing_market_skills[:50]:
    role_bonus = 2.0 if skill in role_skills else 1.0
    score = market_count * role_bonus
    recommendations.append({
        "skill": skill, "market_count": market_count,
        "role_relevant": skill in role_skills, "score": score,
    })

recommendations.sort(key=lambda x: x["score"], reverse=True)
top_recs = recommendations[:8]

for i, rec in enumerate(top_recs, 1):
    role_tag = "⭐ Prioritaire pour ton rôle cible" if rec["role_relevant"] else "📈 Très demandé"
    role_color = "#ffa657" if rec["role_relevant"] else "#58a6ff"
    st.markdown(f"""
    <div class="rec-card">
        <div style="display:flex; align-items:center; gap:16px;">
            <div class="rec-rank">#{i}</div>
            <div style="flex:1;">
                <div class="rec-skill">{rec['skill'].upper()}</div>
                <div style="margin-top:4px;">
                    <span style="background:rgba(63,185,80,0.12); color:#3fb950;
                                 border-radius:20px; padding:2px 10px; font-size:0.78rem; font-weight:500;">
                        {rec['market_count']} offres dans la base
                    </span>
                    &nbsp;
                    <span style="background:rgba(255,166,87,0.12); color:{role_color};
                                 border-radius:20px; padding:2px 10px; font-size:0.78rem; font-weight:500;">
                        {role_tag}
                    </span>
                </div>
            </div>
            <div style="font-size:1.8rem;">{"🎯" if rec['role_relevant'] else "📊"}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ── Offres matching ───────────────────────────────────────────────────────────
st.markdown('<div class="section-header">💼 Offres qui correspondent à ton profil</div>', unsafe_allow_html=True)

all_jobs = get_all_jobs(db, limit=500)

def compute_match_score(job, user_skills_set):
    job_skill_names = {s.name.lower() for s in (job.skills or [])}
    if not job_skill_names:
        return 0, set()
    common = user_skills_set.intersection(job_skill_names)
    score = int((len(common) / len(job_skill_names)) * 100)
    return score, common

matching_jobs = []
for job in all_jobs:
    score, common = compute_match_score(job, user_skills)
    if score > 0:
        matching_jobs.append((job, score, common))

matching_jobs.sort(key=lambda x: x[1], reverse=True)
top_matches = matching_jobs[:10]

if top_matches:
    for job, score, common_skills in top_matches:
        common_str = " ".join([f'<span style="background:rgba(88,166,255,0.1); color:#58a6ff; border-radius:10px; padding:1px 8px; font-size:0.75rem; margin-right:3px;">{s}</span>' for s in list(common_skills)[:6]])
        st.markdown(f"""
        <div class="match-card">
            <div style="display:flex; justify-content:space-between; align-items:start;">
                <div style="flex:1;">
                    <div>
                        <a href="{job.url}" target="_blank" class="match-title">{job.title}</a>
                    </div>
                    <div class="match-company">🏢 {job.company or 'N/A'} &nbsp;·&nbsp; 📍 {job.location or 'Remote'}</div>
                    <div style="margin-top:8px;">{common_str}</div>
                </div>
                <div style="text-align:right; margin-left:16px;">
                    <div class="match-score">{score}% match</div>
                    <div style="color:#8b949e; font-size:0.75rem; margin-top:4px;">{len(common_skills)} skills</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
else:
    st.info("Aucune offre trouvée avec ces critères. Essaie de sélectionner plus de compétences !")

# ── Gap Analysis ──────────────────────────────────────────────────────────────
st.markdown('<div class="section-header">🔍 Analyse des lacunes (Skill Gap Analysis)</div>', unsafe_allow_html=True)

gap_data = []
for skill, count in list(market_skills.items())[:20]:
    has_skill = skill in user_skills
    gap_data.append({"skill": skill, "count": count, "has_skill": has_skill})

df_gap = pd.DataFrame(gap_data)
df_gap_sorted = df_gap.sort_values("count", ascending=True)

fig_gap = go.Figure()
fig_gap.add_trace(go.Bar(
    y=df_gap_sorted["skill"],
    x=df_gap_sorted["count"],
    orientation="h",
    marker=dict(
        color=["#3fb950" if h else "#30363d" for h in df_gap_sorted["has_skill"]],
        line=dict(color=["#3fb950" if h else "#58a6ff" for h in df_gap_sorted["has_skill"]], width=1),
    ),
    text=["✅ Tu l'as" if h else "❌ Manquant" for h in df_gap_sorted["has_skill"]],
    textposition="inside",
    hovertemplate="<b>%{y}</b><br>Demande: %{x} offres<extra></extra>",
))

fig_gap.update_layout(
    **PLOTLY_DARK,
    height=500,
    title="Top 20 skills du marché — Vert = tu l'as déjà",
    xaxis_title="Nombre d'offres",
    yaxis_title="",
    showlegend=False,
)
st.plotly_chart(fig_gap, use_container_width=True)

db.close()
