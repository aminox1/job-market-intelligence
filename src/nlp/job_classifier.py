"""
Classification des offres d'emploi :
- Niveau d'expérience (junior / mid / senior / lead)
- Type de remote (remote / hybrid / onsite)
"""
import re
from typing import Optional


# ─────────────────────────────────────────────────────────────────────────────
# Patterns de détection du niveau
# ─────────────────────────────────────────────────────────────────────────────
LEVEL_PATTERNS = {
    "senior": [
        r"\bsenior\b", r"\bsr\.?\b", r"\blead\b", r"\bstaff\b",
        r"\bprincipal\b", r"\barchitect\b", r"\b5\+?\s*years?\b",
        r"\b7\+?\s*years?\b", r"\b10\+?\s*years?\b", r"\bexpertise\b",
    ],
    "lead": [
        r"\blead\b", r"\btech lead\b", r"\btechnical lead\b",
        r"\bteam lead\b", r"\bengineering manager\b", r"\bcto\b",
        r"\bvp of engineering\b", r"\bhead of\b",
    ],
    "junior": [
        r"\bjunior\b", r"\bjr\.?\b", r"\bentry.?level\b", r"\bintern\b",
        r"\bstagiaire\b", r"\bgrad(uate)?\b", r"\bfresher\b",
        r"\b0.?2\s*years?\b", r"\b1\+?\s*years?\b",
    ],
    "mid": [
        r"\bmid.?level\b", r"\bintermediate\b", r"\bconfirm[eé]\b",
        r"\b2\+?\s*years?\b", r"\b3\+?\s*years?\b", r"\b4\+?\s*years?\b",
    ],
}

# ─────────────────────────────────────────────────────────────────────────────
# Patterns de détection du type remote
# ─────────────────────────────────────────────────────────────────────────────
REMOTE_PATTERNS = {
    "remote": [
        r"\bfully remote\b", r"\b100%\s*remote\b", r"\bremote.?only\b",
        r"\bwork from home\b", r"\bwfh\b", r"\bremote position\b",
        r"\bremote role\b", r"\bteletravail\b", r"\btélétravail\b",
        r"\bremote\b",
    ],
    "hybrid": [
        r"\bhybrid\b", r"\bhybride\b", r"\bpartially remote\b",
        r"\bflexible.?work\b", r"\b2.3\s*days?\s*remote\b",
    ],
    "onsite": [
        r"\bon.?site\b", r"\bin.?office\b", r"\bin.?person\b",
        r"\bpresentiel\b", r"\bprésentiel\b", r"\bon location\b",
    ],
}


def classify_level(title: str, description: str = "") -> str:
    """
    Détermine le niveau d'expérience requis.
    Priorité : title > description
    """
    text = f"{title} {description}".lower()

    # Lead a la priorité sur senior
    for pattern in LEVEL_PATTERNS["lead"]:
        if re.search(pattern, text, re.IGNORECASE):
            return "lead"

    for pattern in LEVEL_PATTERNS["senior"]:
        if re.search(pattern, text, re.IGNORECASE):
            return "senior"

    for pattern in LEVEL_PATTERNS["junior"]:
        if re.search(pattern, text, re.IGNORECASE):
            return "junior"

    for pattern in LEVEL_PATTERNS["mid"]:
        if re.search(pattern, text, re.IGNORECASE):
            return "mid"

    return "mid"  # Par défaut


def classify_remote_type(location: str, description: str = "") -> str:
    """
    Détermine le type de travail à distance.
    """
    text = f"{location} {description}".lower()

    for pattern in REMOTE_PATTERNS["hybrid"]:
        if re.search(pattern, text, re.IGNORECASE):
            return "hybrid"

    for pattern in REMOTE_PATTERNS["remote"]:
        if re.search(pattern, text, re.IGNORECASE):
            return "remote"

    for pattern in REMOTE_PATTERNS["onsite"]:
        if re.search(pattern, text, re.IGNORECASE):
            return "onsite"

    # Si location contient "Worldwide" ou "Anywhere" → remote
    if any(kw in location.lower() for kw in ["worldwide", "anywhere", "global", "remote"]):
        return "remote"

    return "onsite"


def classify_job(job_data: dict) -> dict:
    """
    Classifie un job et enrichit le dict avec level et remote_type.
    """
    title = job_data.get("title", "")
    description = job_data.get("description", "")
    location = job_data.get("location", "")

    job_data["level"] = classify_level(title, description)
    job_data["remote_type"] = classify_remote_type(location, description)
    return job_data
