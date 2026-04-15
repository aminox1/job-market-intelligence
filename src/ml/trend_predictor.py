"""
Prédiction des tendances des skills avec Scikit-Learn.
Utilise une régression polynomiale sur les snapshots historiques.
"""
import logging
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple

from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn.pipeline import make_pipeline
from sklearn.metrics import r2_score

logger = logging.getLogger(__name__)


def prepare_time_series(snapshots: List[Dict]) -> Optional[pd.DataFrame]:
    """
    Prépare les données de snapshots pour la modélisation.
    Args:
        snapshots: [{'date': datetime, 'count': int}, ...]
    Returns:
        DataFrame avec colonnes ['date', 'count', 'day_num']
    """
    if not snapshots or len(snapshots) < 2:
        return None

    df = pd.DataFrame(snapshots)
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date").reset_index(drop=True)

    # Numéroter les jours à partir du premier snapshot
    min_date = df["date"].min()
    df["day_num"] = (df["date"] - min_date).dt.days

    return df


def predict_trend(
    snapshots: List[Dict],
    horizon_days: int = 30,
    degree: int = 2,
) -> Dict:
    """
    Prédit la tendance d'un skill sur les `horizon_days` prochains jours.

    Args:
        snapshots: Historique des counts
        horizon_days: Nombre de jours à prédire dans le futur
        degree: Degré du polynôme (1=linéaire, 2=quadratique)

    Returns:
        Dict avec:
            - 'historical': données historiques
            - 'forecast': prédictions futures
            - 'trend': 'rising' | 'stable' | 'declining'
            - 'r2': score R² du modèle
            - 'growth_rate': % de croissance prévu
    """
    df = prepare_time_series(snapshots)

    if df is None:
        return _empty_result()

    X = df[["day_num"]].values
    y = df["count"].values

    # Modèle polynomial pour capturer les courbes non-linéaires
    model = make_pipeline(PolynomialFeatures(degree=degree), LinearRegression())
    model.fit(X, y)

    # Score du modèle
    y_pred = model.predict(X)
    r2 = float(r2_score(y, y_pred)) if len(y) > 2 else 0.0

    # Prédictions futures
    max_day = int(df["day_num"].max())
    future_days = np.arange(max_day + 1, max_day + horizon_days + 1).reshape(-1, 1)
    future_counts = model.predict(future_days)
    future_counts = np.maximum(future_counts, 0)  # Pas de valeurs négatives

    # Dates futures
    last_date = df["date"].max()
    future_dates = [last_date + timedelta(days=i + 1) for i in range(horizon_days)]

    # Calcul de la tendance
    current_count = float(y[-1]) if len(y) > 0 else 0
    predicted_end = float(future_counts[-1])
    growth_rate = ((predicted_end - current_count) / (current_count + 1)) * 100

    if growth_rate > 10:
        trend = "rising"
    elif growth_rate < -10:
        trend = "declining"
    else:
        trend = "stable"

    return {
        "historical": [
            {"date": row["date"].isoformat(), "count": int(row["count"])}
            for _, row in df.iterrows()
        ],
        "forecast": [
            {"date": d.isoformat(), "count": max(0, int(c))}
            for d, c in zip(future_dates, future_counts)
        ],
        "trend": trend,
        "r2": round(r2, 3),
        "growth_rate": round(growth_rate, 1),
        "current_count": int(current_count),
        "predicted_count": int(predicted_end),
    }


def _empty_result() -> Dict:
    return {
        "historical": [],
        "forecast": [],
        "trend": "unknown",
        "r2": 0.0,
        "growth_rate": 0.0,
        "current_count": 0,
        "predicted_count": 0,
    }


def rank_skills_by_growth(skills_snapshots: Dict[str, List[Dict]]) -> List[Dict]:
    """
    Classe tous les skills par taux de croissance prévu (les plus en hausse en premier).

    Args:
        skills_snapshots: {'python': [snapshots], 'docker': [snapshots], ...}

    Returns:
        Liste triée de {'skill': str, 'growth_rate': float, 'trend': str, 'current_count': int}
    """
    results = []
    for skill_name, snapshots in skills_snapshots.items():
        if not snapshots:
            continue
        prediction = predict_trend(snapshots, horizon_days=30)
        results.append({
            "skill": skill_name,
            "growth_rate": prediction["growth_rate"],
            "trend": prediction["trend"],
            "current_count": prediction["current_count"],
            "predicted_count": prediction["predicted_count"],
        })

    return sorted(results, key=lambda x: x["growth_rate"], reverse=True)


def simulate_historical_data(skill_name: str, base_count: int, days: int = 60) -> List[Dict]:
    """
    Génère des données historiques simulées pour la démo
    quand les vrais snapshots sont insuffisants.
    """
    np.random.seed(hash(skill_name) % 2**31)
    trend = np.random.choice(["rising", "stable", "declining"])

    if trend == "rising":
        values = np.linspace(base_count * 0.6, base_count, days)
    elif trend == "declining":
        values = np.linspace(base_count, base_count * 0.6, days)
    else:
        values = np.ones(days) * base_count

    # Ajouter du bruit réaliste
    noise = np.random.normal(0, base_count * 0.08, days)
    values = np.maximum(values + noise, 0).astype(int)

    start_date = datetime.utcnow() - timedelta(days=days)
    return [
        {"date": start_date + timedelta(days=i), "count": int(v)}
        for i, v in enumerate(values)
    ]
