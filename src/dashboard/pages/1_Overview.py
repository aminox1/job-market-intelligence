"""
📊 Market Overview — Vue globale du marché de l'emploi
"""
import sys
from pathlib import Path

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

ROOT_DIR = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

from src.database.db import init_db, get_db, get_jobs_by_category, get_top_companies, get_all_jobs

st.set_page_config(page_title="Market Overview · JMI", page_icon="📊", layout="wide")

# Dark theme CSS (réutilisé sur toutes les pages)
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif !important; }
.page-title {
    font-size: 2rem; font-weight: 700;
    background: linear-gradient(135deg, #58a6ff, #bc8cff);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    background-clip: text; margin-bottom: 4px;
}
.page-subtitle { color: #8b949e; font-size: 0.95rem; margin-bottom: 24px; }
.section-header {
    font-size: 1.1rem; font-weight: 600; color: #c9d1d9;
    margin: 28px 0 14px 0; padding-bottom: 8px; border-bottom: 1px solid #21262d;
}
</style>
""", unsafe_allow_html=True)

PLOTLY_DARK = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(13,17,23,0.5)",
    font=dict(color="#c9d1d9", family="Inter"),
    colorway=["#58a6ff", "#bc8cff", "#3fb950", "#d29922", "#f85149", "#79c0ff", "#ffa657"],
)

init_db()
db = get_db()

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown('<div class="page-title">📊 Market Overview</div>', unsafe_allow_html=True)
st.markdown('<div class="page-subtitle">Vue globale du marché de l\'emploi tech en temps réel</div>', unsafe_allow_html=True)

jobs = get_all_jobs(db, limit=1000)

if not jobs:
    st.warning("⚠️ Aucune donnée. Lance le pipeline depuis la page Home (bouton dans la sidebar).")
    db.close()
    st.stop()

# ── DataFrames ────────────────────────────────────────────────────────────────
df_jobs = pd.DataFrame([{
    "title": j.title,
    "company": j.company or "Unknown",
    "category": j.category or "Other",
    "level": j.level or "mid",
    "remote_type": j.remote_type or "remote",
    "country": j.country or "Worldwide",
    "published_at": j.published_at,
    "url": j.url,
} for j in jobs])

# ── Row 1 : Catégories + Remote ───────────────────────────────────────────────
st.markdown('<div class="section-header">📂 Répartition des offres</div>', unsafe_allow_html=True)
col1, col2 = st.columns(2)

with col1:
    cat_data = df_jobs["category"].value_counts().reset_index()
    cat_data.columns = ["category", "count"]
    fig_cat = px.pie(
        cat_data, values="count", names="category",
        title="Par catégorie",
        hole=0.5,
        color_discrete_sequence=["#58a6ff", "#bc8cff", "#3fb950", "#d29922", "#f85149", "#79c0ff"],
    )
    fig_cat.update_layout(**PLOTLY_DARK, title_font_size=14,
                          legend=dict(orientation="v", font=dict(size=11)))
    fig_cat.update_traces(textposition="outside", textinfo="percent+label",
                          marker=dict(line=dict(color="#0d1117", width=2)))
    st.plotly_chart(fig_cat, use_container_width=True)

with col2:
    remote_data = df_jobs["remote_type"].value_counts().reset_index()
    remote_data.columns = ["type", "count"]
    colors_remote = {"remote": "#3fb950", "hybrid": "#d29922", "onsite": "#f85149"}
    fig_remote = px.bar(
        remote_data, x="type", y="count",
        title="Remote vs Hybrid vs Onsite",
        color="type",
        color_discrete_map=colors_remote,
        text="count",
    )
    fig_remote.update_layout(**PLOTLY_DARK, title_font_size=14,
                             showlegend=False, xaxis_title="", yaxis_title="Nombre d'offres")
    fig_remote.update_traces(texttemplate="%{text}", textposition="outside",
                             marker_line_color="rgba(0,0,0,0)")
    st.plotly_chart(fig_remote, use_container_width=True)

# ── Row 2 : Top entreprises + Niveau ─────────────────────────────────────────
st.markdown('<div class="section-header">🏢 Entreprises & Niveaux</div>', unsafe_allow_html=True)
col3, col4 = st.columns(2)

with col3:
    companies_data = df_jobs["company"].value_counts().head(15).reset_index()
    companies_data.columns = ["company", "count"]
    fig_comp = px.bar(
        companies_data.sort_values("count"), x="count", y="company",
        title="Top 15 entreprises qui recrutent",
        orientation="h",
        color="count",
        color_continuous_scale=[[0, "#1a2744"], [1, "#58a6ff"]],
        text="count",
    )
    fig_comp.update_layout(**PLOTLY_DARK, title_font_size=14,
                           showlegend=False, yaxis_title="", xaxis_title="Offres",
                           coloraxis_showscale=False, height=420)
    fig_comp.update_traces(texttemplate="%{text}", textposition="outside")
    st.plotly_chart(fig_comp, use_container_width=True)

with col4:
    level_data = df_jobs["level"].value_counts().reset_index()
    level_data.columns = ["level", "count"]
    level_colors = {"junior": "#d29922", "mid": "#58a6ff", "senior": "#bc8cff", "lead": "#f85149"}
    fig_level = px.pie(
        level_data, values="count", names="level",
        title="Niveau d'expérience requis",
        hole=0.4,
        color="level",
        color_discrete_map=level_colors,
    )
    fig_level.update_layout(**PLOTLY_DARK, title_font_size=14)
    fig_level.update_traces(textposition="outside", textinfo="percent+label",
                            marker=dict(line=dict(color="#0d1117", width=2)))
    st.plotly_chart(fig_level, use_container_width=True)

# ── Row 3 : Pays ──────────────────────────────────────────────────────────────
st.markdown('<div class="section-header">🌍 Distribution géographique</div>', unsafe_allow_html=True)
country_data = df_jobs["country"].value_counts().head(20).reset_index()
country_data.columns = ["country", "count"]

fig_geo = px.bar(
    country_data, x="country", y="count",
    title="Offres par pays/région",
    color="count",
    color_continuous_scale=[[0, "#0d2137"], [0.5, "#1a4a7a"], [1, "#58a6ff"]],
    text="count",
)
fig_geo.update_layout(**PLOTLY_DARK, title_font_size=14, showlegend=False,
                      xaxis_title="", yaxis_title="Offres",
                      coloraxis_showscale=False)
fig_geo.update_traces(texttemplate="%{text}", textposition="outside")
st.plotly_chart(fig_geo, use_container_width=True)

# ── Table des offres ──────────────────────────────────────────────────────────
st.markdown('<div class="section-header">📋 Toutes les offres</div>', unsafe_allow_html=True)

search = st.text_input("🔍 Rechercher (titre, entreprise, catégorie...)", "")
df_display = df_jobs.copy()
if search:
    mask = (
        df_display["title"].str.contains(search, case=False, na=False) |
        df_display["company"].str.contains(search, case=False, na=False) |
        df_display["category"].str.contains(search, case=False, na=False)
    )
    df_display = df_display[mask]

st.dataframe(
    df_display[["title", "company", "category", "level", "remote_type", "country"]].rename(columns={
        "title": "Titre", "company": "Entreprise", "category": "Catégorie",
        "level": "Niveau", "remote_type": "Remote", "country": "Pays"
    }),
    use_container_width=True,
    height=400,
)
st.caption(f"📊 {len(df_display)} offres affichées")

db.close()
