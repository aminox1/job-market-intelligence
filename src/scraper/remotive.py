"""
Client Remotive API — 100% gratuit, aucune clé nécessaire
https://remotive.com/api/remote-jobs
"""
import logging
import re
from datetime import datetime
from typing import List, Dict, Optional
from bs4 import BeautifulSoup

import requests

logger = logging.getLogger(__name__)

REMOTIVE_API_URL = "https://remotive.com/api/remote-jobs"

# Catégories disponibles sur Remotive
CATEGORIES = [
    "software-dev",
    "data",
    "devops-sysadmin",
    "backend",
    "frontend",
]

COUNTRY_KEYWORDS = {
    "france": "France", "paris": "France", "fr": "France",
    "usa": "USA", "united states": "USA", "us": "USA", "america": "USA",
    "uk": "UK", "united kingdom": "UK", "london": "UK",
    "germany": "Germany", "berlin": "Germany",
    "canada": "Canada", "toronto": "Canada",
    "worldwide": "Worldwide", "remote": "Worldwide", "anywhere": "Worldwide",
    "europe": "Europe",
}


def strip_html(html: str) -> str:
    """Supprime les balises HTML et retourne le texte brut."""
    if not html:
        return ""
    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text(separator=" ")
    # Nettoyer espaces multiples
    text = re.sub(r"\s+", " ", text).strip()
    return text


def extract_country(location: str) -> str:
    """Extrait le pays depuis la chaîne de localisation."""
    if not location:
        return "Worldwide"
    loc_lower = location.lower()
    for keyword, country in COUNTRY_KEYWORDS.items():
        if keyword in loc_lower:
            return country
    return location.strip() or "Worldwide"


def parse_date(date_str: Optional[str]) -> Optional[datetime]:
    """Parse une date ISO 8601."""
    if not date_str:
        return None
    try:
        # Format: "2024-03-15T10:00:00"
        return datetime.fromisoformat(date_str.replace("Z", "+00:00").replace("+00:00", ""))
    except (ValueError, TypeError):
        return None


def fetch_jobs(category: str = None, limit: int = 100) -> List[Dict]:
    """
    Récupère les offres depuis l'API Remotive.
    Args:
        category: Catégorie (ex: 'software-dev', 'data')
        limit: Nombre max d'offres
    Returns:
        Liste de dicts bruts depuis l'API
    """
    params: Dict = {}
    if category:
        params["category"] = category

    try:
        logger.info(f"🔍 Fetching Remotive jobs — category={category}")
        response = requests.get(REMOTIVE_API_URL, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        jobs = data.get("jobs", [])
        logger.info(f"✅ {len(jobs)} offres récupérées (category={category})")
        return jobs[:limit]
    except requests.exceptions.ConnectionError:
        logger.error("❌ Impossible de se connecter à Remotive API. Vérifie ta connexion.")
        return []
    except requests.exceptions.Timeout:
        logger.error("❌ Timeout lors de la requête Remotive API.")
        return []
    except Exception as e:
        logger.error(f"❌ Erreur Remotive API: {e}")
        return []


def fetch_all_categories(limit_per_category: int = 100) -> List[Dict]:
    """Récupère les offres de toutes les catégories tech."""
    all_jobs = []
    seen_ids = set()

    for category in CATEGORIES:
        jobs = fetch_jobs(category=category, limit=limit_per_category)
        for job in jobs:
            if job.get("id") not in seen_ids:
                seen_ids.add(job["id"])
                all_jobs.append(job)

    logger.info(f"📦 Total offres uniques récupérées: {len(all_jobs)}")
    return all_jobs


def normalize_job(job: Dict) -> Dict:
    """
    Normalise un job brut Remotive vers le format de la base de données.
    """
    description_clean = strip_html(job.get("description", ""))
    location = job.get("candidate_required_location", "Worldwide")

    return {
        "remote_id": f"remotive_{job['id']}",
        "title": job.get("title", "").strip(),
        "company": job.get("company_name", "").strip(),
        "location": location,
        "country": extract_country(location),
        "category": normalize_category(job.get("category", "")),
        "job_type": job.get("job_type", "full_time"),
        "description": description_clean,
        "url": job.get("url", ""),
        "source": "remotive",
        "published_at": parse_date(job.get("publication_date")),
        "salary_min": None,
        "salary_max": None,
    }


def normalize_category(category: str) -> str:
    """Uniformise les noms de catégories."""
    mapping = {
        "software-dev": "Software Dev",
        "data": "Data / AI",
        "devops-sysadmin": "DevOps",
        "backend": "Backend",
        "frontend": "Frontend",
        "machine-learning": "ML / AI",
        "": "Other",
    }
    return mapping.get(category.lower(), category.title())
