"""
Database engine, session factory, and CRUD helpers
"""
import logging
from pathlib import Path
from datetime import datetime, date
from typing import List, Optional, Dict, Any

from sqlalchemy import create_engine, func, text
from sqlalchemy.orm import sessionmaker, Session

from .models import Base, Job, Skill, TrendSnapshot

logger = logging.getLogger(__name__)

# ── Chemins ──────────────────────────────────────────────────────────────────
ROOT_DIR = Path(__file__).parent.parent.parent
DATA_DIR = ROOT_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

DB_PATH = DATA_DIR / "jobs.db"
DATABASE_URL = f"sqlite:///{DB_PATH}"

# ── Engine & Session ──────────────────────────────────────────────────────────
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=False,
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db() -> None:
    """Crée toutes les tables si elles n'existent pas encore."""
    Base.metadata.create_all(bind=engine)
    logger.info(f"✅ Base de données initialisée → {DB_PATH}")


def get_db() -> Session:
    """Retourne une session SQLAlchemy."""
    return SessionLocal()


# ── CRUD — Jobs ───────────────────────────────────────────────────────────────

def upsert_job(db: Session, job_data: Dict[str, Any], skills: List[str]) -> Job:
    """Insère ou met à jour un job avec une liste de noms de skills."""
    existing = db.query(Job).filter(Job.remote_id == job_data["remote_id"]).first()
    if existing:
        return existing

    job = Job(**{k: v for k, v in job_data.items() if hasattr(Job, k)})
    db.add(job)
    db.flush()

    for skill_name in skills:
        skill = get_or_create_skill(db, skill_name)
        if skill not in job.skills:
            job.skills.append(skill)

    db.commit()
    db.refresh(job)
    return job


def upsert_job_with_categories(db: Session, job_data: Dict[str, Any], skills_with_cat: List[Dict]) -> Job:
    """Insère ou met à jour un job avec les skills + leurs catégories."""
    existing = db.query(Job).filter(Job.remote_id == job_data["remote_id"]).first()
    if existing:
        return existing

    job = Job(**{k: v for k, v in job_data.items() if hasattr(Job, k)})
    db.add(job)
    db.flush()

    for skill_info in skills_with_cat:
        skill = get_or_create_skill(db, skill_info["name"], category=skill_info.get("category"))
        if skill not in job.skills:
            job.skills.append(skill)

    db.commit()
    db.refresh(job)
    return job


def get_all_jobs(db: Session, limit: int = 500) -> List[Job]:
    return db.query(Job).order_by(Job.scraped_at.desc()).limit(limit).all()


def get_jobs_count(db: Session) -> int:
    return db.query(func.count(Job.id)).scalar() or 0


def get_jobs_by_category(db: Session) -> List[Dict]:
    rows = (
        db.query(Job.category, func.count(Job.id).label("count"))
        .group_by(Job.category)
        .order_by(func.count(Job.id).desc())
        .all()
    )
    return [{"category": r.category or "Other", "count": r.count} for r in rows]


def get_top_companies(db: Session, limit: int = 15) -> List[Dict]:
    rows = (
        db.query(Job.company, func.count(Job.id).label("count"))
        .group_by(Job.company)
        .order_by(func.count(Job.id).desc())
        .limit(limit)
        .all()
    )
    return [{"company": r.company or "Unknown", "count": r.count} for r in rows]


def get_recent_jobs(db: Session, limit: int = 20) -> List[Job]:
    return db.query(Job).order_by(Job.published_at.desc()).limit(limit).all()


# ── CRUD — Skills ─────────────────────────────────────────────────────────────

def get_or_create_skill(db: Session, name: str, category: str = None) -> Skill:
    name = name.lower().strip()
    skill = db.query(Skill).filter(Skill.name == name).first()
    if not skill:
        skill = Skill(name=name, category=category)
        db.add(skill)
        db.flush()
    return skill


def get_top_skills(db: Session, limit: int = 30) -> List[Dict]:
    """Retourne les N skills les plus demandés."""
    rows = (
        db.query(Skill.name, Skill.category, func.count(Job.id).label("count"))
        .join(Skill.jobs)
        .group_by(Skill.id)
        .order_by(func.count(Job.id).desc())
        .limit(limit)
        .all()
    )
    return [{"skill": r.name, "category": r.category, "count": r.count} for r in rows]


def get_skills_count(db: Session) -> int:
    return db.query(func.count(Skill.id)).scalar() or 0


def get_skills_by_category(db: Session) -> List[Dict]:
    rows = (
        db.query(Skill.category, Skill.name, func.count(Job.id).label("count"))
        .join(Skill.jobs)
        .group_by(Skill.id)
        .order_by(func.count(Job.id).desc())
        .all()
    )
    return [{"category": r.category or "other", "skill": r.name, "count": r.count} for r in rows]


def get_all_skills(db: Session) -> List[Skill]:
    return db.query(Skill).all()


# ── CRUD — Tendances ──────────────────────────────────────────────────────────

def save_trend_snapshot(db: Session) -> None:
    """Enregistre un snapshot quotidien des counts de skills."""
    today = datetime.utcnow().date()
    skills = get_all_skills(db)
    for skill in skills:
        count = len(skill.jobs)
        snapshot = TrendSnapshot(skill_id=skill.id, date=datetime.utcnow(), count=count)
        db.add(snapshot)
    db.commit()
    logger.info(f"📸 Snapshot tendances sauvegardé — {len(skills)} skills")


def get_trend_data(db: Session, skill_name: str) -> List[Dict]:
    """Historique des counts pour un skill donné."""
    skill = db.query(Skill).filter(Skill.name == skill_name.lower()).first()
    if not skill:
        return []
    rows = (
        db.query(TrendSnapshot.date, TrendSnapshot.count)
        .filter(TrendSnapshot.skill_id == skill.id)
        .order_by(TrendSnapshot.date)
        .all()
    )
    return [{"date": r.date, "count": r.count} for r in rows]


def get_last_update(db: Session) -> Optional[datetime]:
    result = db.query(func.max(Job.scraped_at)).scalar()
    return result
