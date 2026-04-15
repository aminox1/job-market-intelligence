"""
🧠 Skills Analysis — Analyse détaillée des compétences techniques
"""
import sys
from pathlib import Path
from io import BytesIO

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from wordcloud import WordCloud
import matplotlib.pyplot as plt

ROOT_DIR = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

from src.database.db import init_db, get_db, get_top_skills, get_skills_by_category, get_all_jobs

st.set_page_config(page_title="Skills Analysis · JMI", page_icon="🧠", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif !important; }
.page-title {
    font-size: 2rem; font-weight: 700;
    background: linear-gradient(135deg, #58a6ff, #bc8cff);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
}
.page-subtitle { color: #8b949e; font-size: 0.95rem; margin-bottom: 24px; }
.section-header {
    font-size: 1.1rem; font-weight: 600; color: #c9d1d9;
    margin: 28px 0 14px 0; padding-bottom: 8px; border-bottom: 1px solid #21262d;
}
.skill-pill {
    display: inline-block;
    background: rgba(88,166,255,0.12);
    border: 1px solid rgba(88,166,255,0.25);
    color: #58a6ff;
    border-radius: 20px;
    padding: 4px 14px;
    font-size: 0.82rem;
    font-weight: 500;
    margin: 3px;
}
</style>
""", unsafe_allow_html=True)

PLOTLY_DARK = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(13,17,23,0.5)",
    font=dict(color="#c9d1d9", family="Inter"),
    colorway=["#58a6ff", "#bc8cff", "#3fb950", "#d29922", "#f85149", "#79c0ff", "#ffa657"],
)

CATEGORY_COLORS = {
    "language": "#58a6ff",
    "frontend": "#bc8cff",
    "backend": "#3fb950",
    "database": "#d29922",
    "cloud": "#f85149",
    "devops": "#79c0ff",
    "ml_ai": "#ffa657",
    "big_data": "#ff7b72",
    "mobile": "#56d364",
    "tool": "#8b949e",
}

init_db()
db = get_db()

st.markdown('<div class="page-title">🧠 Skills Analysis</div>', unsafe_allow_html=True)
st.markdown('<div class="page-subtitle">Analyse approfondie des 400+ compétences techniques extraites par NLP</div>', unsafe_allow_html=True)

top_skills = get_top_skills(db, limit=50)
skills_by_cat = get_skills_by_category(db)

if not top_skills:
    st.warning("⚠️ Aucune donnée. Lance le pipeline depuis la page Home.")
    db.close()
    st.stop()

df_skills = pd.DataFrame(top_skills)
df_by_cat = pd.DataFrame(skills_by_cat)

# ── Filtre catégorie ──────────────────────────────────────────────────────────
all_cats = sorted(df_skills["category"].dropna().unique().tolist())
selected_cats = st.multiselect(
    "🔽 Filtrer par catégorie",
    options=all_cats,
    default=all_cats,
    help="Sélectionne les catégories à afficher"
)
df_filtered = df_skills[df_skills["category"].isin(selected_cats)] if selected_cats else df_skills

# ── Top Skills Bar Chart ──────────────────────────────────────────────────────
st.markdown('<div class="section-header">🏆 Top 30 Skills les plus demandés</div>', unsafe_allow_html=True)

df_top = df_filtered.head(30).sort_values("count", ascending=True)
colors = [CATEGORY_COLORS.get(cat, "#58a6ff") for cat in df_top["category"]]

fig_bar = go.Figure(go.Bar(
    y=df_top["skill"],
    x=df_top["count"],
    orientation="h",
    marker=dict(
        color=colors,
        line=dict(color="rgba(0,0,0,0)", width=0),
    ),
    text=df_top["count"],
    textposition="outside",
    hovertemplate="<b>%{y}</b><br>Occurrences: %{x}<extra></extra>",
))
fig_bar.update_layout(
    **PLOTLY_DARK,
    height=700,
    yaxis=dict(tickfont=dict(size=12)),
    xaxis_title="Nombre d'offres",
    showlegend=False,
    margin=dict(l=10, r=60, t=10, b=40),
)
st.plotly_chart(fig_bar, use_container_width=True)

# ── Treemap par catégorie ─────────────────────────────────────────────────────
st.markdown('<div class="section-header">🗂️ Compétences par catégorie (Treemap)</div>', unsafe_allow_html=True)

df_tree = df_by_cat[df_by_cat["category"].isin(selected_cats)].head(60) if selected_cats else df_by_cat.head(60)

if not df_tree.empty:
    fig_tree = px.treemap(
        df_tree,
        path=["category", "skill"],
        values="count",
        color="category",
        color_discrete_map=CATEGORY_COLORS,
        hover_data=["count"],
    )
    fig_tree.update_layout(
        **PLOTLY_DARK,
        height=500,
        margin=dict(l=0, r=0, t=0, b=0),
    )
    fig_tree.update_traces(
        textinfo="label+value",
        hovertemplate="<b>%{label}</b><br>Occurrences: %{value}<extra></extra>",
    )
    st.plotly_chart(fig_tree, use_container_width=True)

# ── WordCloud ─────────────────────────────────────────────────────────────────
st.markdown('<div class="section-header">☁️ Cloud de compétences</div>', unsafe_allow_html=True)

col_wc1, col_wc2 = st.columns([2, 1])

with col_wc1:
    skill_freq = {row["skill"]: row["count"] for _, row in df_filtered.iterrows()}
    if skill_freq:
        wc = WordCloud(
            width=900, height=400,
            background_color="#0d1117",
            colormap="Blues",
            prefer_horizontal=0.85,
            max_words=80,
            min_font_size=10,
        ).generate_from_frequencies(skill_freq)

        fig_wc, ax = plt.subplots(figsize=(9, 4))
        fig_wc.patch.set_facecolor("#0d1117")
        ax.imshow(wc, interpolation="bilinear")
        ax.axis("off")
        st.pyplot(fig_wc, use_container_width=True)
        plt.close()

with col_wc2:
    st.markdown("**Top 10 Skills**")
    for i, row in df_filtered.head(10).iterrows():
        cat_color = CATEGORY_COLORS.get(row["category"], "#58a6ff")
        pct = int((row["count"] / df_filtered["count"].max()) * 100)
        st.markdown(f"""
        <div style="margin-bottom:8px;">
            <div style="display:flex; justify-content:space-between; margin-bottom:2px;">
                <span style="color:#c9d1d9; font-size:0.85rem; font-weight:500;">{row['skill']}</span>
                <span style="color:#8b949e; font-size:0.8rem;">{row['count']}</span>
            </div>
            <div style="background:#21262d; border-radius:4px; height:6px;">
                <div style="width:{pct}%; background:{cat_color}; border-radius:4px; height:6px;"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

# ── Heatmap catégories ────────────────────────────────────────────────────────
st.markdown('<div class="section-header">🔥 Heatmap — Intensité par catégorie</div>', unsafe_allow_html=True)

cat_summary = df_by_cat.groupby("category")["count"].agg(["sum", "mean", "count"]).reset_index()
cat_summary.columns = ["category", "total", "moyenne", "nb_skills"]
cat_summary = cat_summary.sort_values("total", ascending=False)

fig_heat = go.Figure(go.Bar(
    x=cat_summary["category"],
    y=cat_summary["total"],
    marker=dict(
        color=cat_summary["total"],
        colorscale=[[0, "#0d2137"], [0.5, "#1a4a7a"], [1, "#58a6ff"]],
        showscale=False,
    ),
    text=cat_summary["total"],
    textposition="outside",
    hovertemplate="<b>%{x}</b><br>Total occurrences: %{y}<br>Skills: %{customdata}",
    customdata=cat_summary["nb_skills"],
))
fig_heat.update_layout(
    **PLOTLY_DARK,
    xaxis_title="", yaxis_title="Total occurrences",
    showlegend=False, height=350,
)
st.plotly_chart(fig_heat, use_container_width=True)

db.close()
