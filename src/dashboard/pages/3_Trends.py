"""
📈 Trends & Predictions — Prédiction de tendances par Machine Learning
"""
import sys
from pathlib import Path
from datetime import datetime

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

ROOT_DIR = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

from src.database.db import init_db, get_db, get_top_skills, get_trend_data, get_all_skills
from src.ml.trend_predictor import predict_trend, simulate_historical_data, rank_skills_by_growth

st.set_page_config(page_title="Trends & Predictions · JMI", page_icon="📈", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif !important; }
.page-title {
    font-size: 2rem; font-weight: 700;
    background: linear-gradient(135deg, #58a6ff, #3fb950);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
}
.page-subtitle { color: #8b949e; font-size: 0.95rem; margin-bottom: 24px; }
.section-header {
    font-size: 1.1rem; font-weight: 600; color: #c9d1d9;
    margin: 28px 0 14px 0; padding-bottom: 8px; border-bottom: 1px solid #21262d;
}
.trend-card {
    background: #161b22; border: 1px solid #30363d; border-radius: 12px;
    padding: 16px; text-align: center; margin-bottom: 10px;
}
.trend-rising { border-color: rgba(63,185,80,0.4); }
.trend-declining { border-color: rgba(248,81,73,0.4); }
.trend-stable { border-color: rgba(88,166,255,0.2); }
.trend-emoji { font-size: 1.8rem; margin-bottom: 4px; }
.trend-name { font-weight: 600; color: #c9d1d9; font-size: 0.9rem; margin-bottom: 4px; }
.trend-rate-up { color: #3fb950; font-size: 1.1rem; font-weight: 700; }
.trend-rate-down { color: #f85149; font-size: 1.1rem; font-weight: 700; }
.trend-rate-stable { color: #58a6ff; font-size: 1.1rem; font-weight: 700; }
.ml-badge {
    display: inline-block;
    background: rgba(188,140,255,0.15);
    border: 1px solid rgba(188,140,255,0.3);
    color: #bc8cff; border-radius: 20px; padding: 3px 12px;
    font-size: 0.75rem; font-weight: 600;
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

st.markdown('<div class="page-title">📈 Trends & Predictions</div>', unsafe_allow_html=True)
st.markdown("""
<div class="page-subtitle">
    Prédiction de la demande future par Machine Learning (régression polynomiale Scikit-Learn)
    &nbsp;<span class="ml-badge">🤖 ML Powered</span>
</div>
""", unsafe_allow_html=True)

top_skills = get_top_skills(db, limit=40)

if not top_skills:
    st.warning("⚠️ Aucune donnée. Lance le pipeline depuis la page Home.")
    db.close()
    st.stop()

# ── Simulation des données historiques pour la démo ──────────────────────────
# (En production, on utilise les vrais snapshots de TrendSnapshot)
skills_snapshots = {}
for skill_info in top_skills[:20]:
    skill_name = skill_info["skill"]
    # Essayer les vrais snapshots d'abord
    real_snapshots = get_trend_data(db, skill_name)
    if len(real_snapshots) >= 3:
        skills_snapshots[skill_name] = real_snapshots
    else:
        # Simuler des données historiques réalistes
        skills_snapshots[skill_name] = simulate_historical_data(
            skill_name, base_count=skill_info["count"], days=60
        )

# ── Classement par croissance ─────────────────────────────────────────────────
st.markdown('<div class="section-header">🚀 Skills en hausse vs en baisse (30 prochains jours)</div>', unsafe_allow_html=True)

rankings = rank_skills_by_growth(skills_snapshots)

rising = [r for r in rankings if r["trend"] == "rising"][:5]
stable = [r for r in rankings if r["trend"] == "stable"][:5]
declining = [r for r in rankings if r["trend"] == "declining"][:5]

col_r, col_s, col_d = st.columns(3)

def trend_card(skill_info: dict) -> str:
    rate = skill_info["growth_rate"]
    trend = skill_info["trend"]
    if trend == "rising":
        emoji = "🚀"
        rate_class = "trend-rate-up"
        card_class = "trend-rising"
        rate_str = f"+{rate:.1f}%"
    elif trend == "declining":
        emoji = "📉"
        rate_class = "trend-rate-down"
        card_class = "trend-declining"
        rate_str = f"{rate:.1f}%"
    else:
        emoji = "➡️"
        rate_class = "trend-rate-stable"
        card_class = "trend-stable"
        rate_str = f"{rate:+.1f}%"

    return f"""
    <div class="trend-card {card_class}">
        <div class="trend-emoji">{emoji}</div>
        <div class="trend-name">{skill_info['skill']}</div>
        <div class="{rate_class}">{rate_str}</div>
        <div style="color:#8b949e; font-size:0.75rem;">{skill_info['current_count']} offres</div>
    </div>
    """

with col_r:
    st.markdown("**🚀 En hausse**")
    for s in rising:
        st.markdown(trend_card(s), unsafe_allow_html=True)

with col_s:
    st.markdown("**➡️ Stables**")
    for s in stable:
        st.markdown(trend_card(s), unsafe_allow_html=True)

with col_d:
    st.markdown("**📉 En baisse**")
    for s in declining:
        st.markdown(trend_card(s), unsafe_allow_html=True)

# ── Graphique de prédiction interactif ───────────────────────────────────────
st.markdown('<div class="section-header">🔮 Prédiction détaillée pour un skill</div>', unsafe_allow_html=True)

selected_skill = st.selectbox(
    "Choisir un skill à analyser :",
    options=list(skills_snapshots.keys()),
    index=0,
)

horizon = st.slider("Horizon de prédiction (jours)", min_value=7, max_value=90, value=30, step=7)

if selected_skill:
    snapshots = skills_snapshots[selected_skill]
    result = predict_trend(snapshots, horizon_days=horizon)

    # Métriques
    col_m1, col_m2, col_m3, col_m4 = st.columns(4)
    trend_emoji = {"rising": "🚀", "stable": "➡️", "declining": "📉", "unknown": "❓"}
    trend_color = {"rising": "#3fb950", "stable": "#58a6ff", "declining": "#f85149", "unknown": "#8b949e"}

    with col_m1:
        st.metric("Tendance", f"{trend_emoji.get(result['trend'])} {result['trend'].title()}")
    with col_m2:
        st.metric("Croissance prévue", f"{result['growth_rate']:+.1f}%")
    with col_m3:
        st.metric("Offres actuelles", result["current_count"])
    with col_m4:
        st.metric("Offres prévues (+30j)", result["predicted_count"], delta=result["predicted_count"] - result["current_count"])

    # Graphique
    hist_dates = [h["date"] for h in result["historical"]]
    hist_counts = [h["count"] for h in result["historical"]]
    fore_dates = [f["date"] for f in result["forecast"]]
    fore_counts = [f["count"] for f in result["forecast"]]

    fig_pred = go.Figure()

    # Zone de confiance (±15%)
    upper = [c * 1.15 for c in fore_counts]
    lower = [max(0, c * 0.85) for c in fore_counts]

    fig_pred.add_trace(go.Scatter(
        x=fore_dates + fore_dates[::-1],
        y=upper + lower[::-1],
        fill="toself",
        fillcolor="rgba(88,166,255,0.08)",
        line=dict(color="rgba(0,0,0,0)"),
        name="Zone de confiance ±15%",
        showlegend=True,
    ))

    # Données historiques
    fig_pred.add_trace(go.Scatter(
        x=hist_dates, y=hist_counts,
        mode="lines+markers",
        name="Historique",
        line=dict(color="#58a6ff", width=2.5),
        marker=dict(size=5, color="#58a6ff"),
    ))

    # Prédiction
    pred_color = trend_color.get(result["trend"], "#bc8cff")
    fig_pred.add_trace(go.Scatter(
        x=fore_dates, y=fore_counts,
        mode="lines+markers",
        name=f"Prédiction ({horizon}j)",
        line=dict(color=pred_color, width=2.5, dash="dash"),
        marker=dict(size=4, color=pred_color),
    ))

    # Ligne de séparation
    if hist_dates:
        fig_pred.add_vline(
            x=hist_dates[-1],
            line_dash="dot",
            line_color="#8b949e",
            annotation_text="Aujourd'hui",
            annotation_position="top right",
        )

    fig_pred.update_layout(
        **PLOTLY_DARK,
        title=f"Tendance & Prédiction — {selected_skill.upper()}",
        xaxis_title="Date",
        yaxis_title="Nombre d'offres",
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
        height=400,
        hovermode="x unified",
    )
    st.plotly_chart(fig_pred, use_container_width=True)

    st.caption(f"🤖 Score R² du modèle : {result['r2']:.3f} — Plus c'est proche de 1.0, plus la prédiction est fiable.")

# ── Classement global avec barres ────────────────────────────────────────────
st.markdown('<div class="section-header">📊 Classement global par taux de croissance prévu</div>', unsafe_allow_html=True)

df_rank = pd.DataFrame(rankings)
if not df_rank.empty:
    df_rank["color"] = df_rank["trend"].map({
        "rising": "#3fb950", "stable": "#58a6ff", "declining": "#f85149"
    }).fillna("#8b949e")

    df_rank_sorted = df_rank.sort_values("growth_rate", ascending=True)

    fig_rank = go.Figure(go.Bar(
        y=df_rank_sorted["skill"],
        x=df_rank_sorted["growth_rate"],
        orientation="h",
        marker=dict(color=df_rank_sorted["color"]),
        text=[f"{r:+.1f}%" for r in df_rank_sorted["growth_rate"]],
        textposition="outside",
        hovertemplate="<b>%{y}</b><br>Croissance: %{x:.1f}%<extra></extra>",
    ))
    fig_rank.add_vline(x=0, line_color="#30363d", line_width=1)
    fig_rank.update_layout(
        **PLOTLY_DARK, height=500,
        xaxis_title="Taux de croissance prévu (%)",
        yaxis_title="", showlegend=False,
    )
    st.plotly_chart(fig_rank, use_container_width=True)

db.close()
