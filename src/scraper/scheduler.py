"""
Pipeline principal : scraping → NLP → base de données.
Lance également le scheduler APScheduler pour les rafraîchissements automatiques.
"""
import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Dict

# Ajouter le dossier racine au path
ROOT_DIR = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

from src.database.db import init_db, get_db, upsert_job_with_categories, save_trend_snapshot, get_jobs_count
from src.scraper.remotive import fetch_all_categories, normalize_job
from src.nlp.skill_extractor import extract_skills, get_skill_category
from src.nlp.job_classifier import classify_job

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


def run_pipeline() -> Dict[str, int]:
    """
    Pipeline complet de collecte et traitement des données.
    Returns:
        Stats : {'fetched': int, 'saved': int, 'skills_found': int}
    """
    logger.info("=" * 60)
    logger.info("🚀 Démarrage du pipeline Job Market Intelligence")
    logger.info("=" * 60)

    # 1. Initialiser la base de données
    init_db()
    db = get_db()

    stats = {"fetched": 0, "saved": 0, "skills_found": 0}

    try:
        # 2. Récupérer les offres depuis Remotive
        logger.info("📡 Collecte des offres Remotive...")
        raw_jobs = fetch_all_categories(limit_per_category=100)
        stats["fetched"] = len(raw_jobs)
        logger.info(f"   → {len(raw_jobs)} offres récupérées")

        if not raw_jobs:
            logger.warning("⚠️  Aucune offre récupérée. Vérifie ta connexion internet.")
            return stats

        # 3. Traitement de chaque offre
        logger.info("🧠 Traitement NLP en cours...")
        for i, raw_job in enumerate(raw_jobs):
            try:
                # Normaliser
                job_data = normalize_job(raw_job)

                # Classifier (niveau + remote type)
                job_data = classify_job(job_data)

                # Extraire les skills (nom + catégorie) depuis le titre + description
                text_to_analyze = f"{job_data['title']} {job_data['description']}"
                skill_with_cat = extract_skills(text_to_analyze)
                stats["skills_found"] += len(skill_with_cat)

                # Sauvegarder en base avec les catégories
                upsert_job_with_categories(db, job_data, skill_with_cat)
                stats["saved"] += 1

                if (i + 1) % 50 == 0:
                    logger.info(f"   → {i + 1}/{len(raw_jobs)} offres traitées...")

            except Exception as e:
                logger.warning(f"⚠️  Erreur sur job {raw_job.get('id')}: {e}")
                continue

        # 4. Sauvegarder le snapshot de tendances
        logger.info("📸 Sauvegarde snapshot tendances...")
        save_trend_snapshot(db)

        total_jobs = get_jobs_count(db)
        logger.info("=" * 60)
        logger.info(f"✅ Pipeline terminé avec succès !")
        logger.info(f"   📦 Offres récupérées  : {stats['fetched']}")
        logger.info(f"   💾 Offres sauvegardées : {stats['saved']}")
        logger.info(f"   🧠 Skills trouvés      : {stats['skills_found']}")
        logger.info(f"   📊 Total dans la DB    : {total_jobs}")
        logger.info("=" * 60)

    except Exception as e:
        logger.error(f"❌ Erreur critique dans le pipeline: {e}")
        raise
    finally:
        db.close()

    return stats


def start_scheduler(interval_hours: int = 6) -> None:
    """
    Lance le scheduler APScheduler pour des mises à jour automatiques.
    """
    try:
        from apscheduler.schedulers.blocking import BlockingScheduler
        from apscheduler.triggers.interval import IntervalTrigger

        scheduler = BlockingScheduler(timezone="UTC")
        scheduler.add_job(
            run_pipeline,
            trigger=IntervalTrigger(hours=interval_hours),
            id="job_pipeline",
            name="Job Market Intelligence Pipeline",
            replace_existing=True,
        )

        logger.info(f"⏰ Scheduler démarré — rafraîchissement toutes les {interval_hours}h")
        logger.info("   Appuie sur Ctrl+C pour arrêter.")

        # Lancer une première fois immédiatement
        run_pipeline()
        scheduler.start()

    except (KeyboardInterrupt, SystemExit):
        logger.info("👋 Scheduler arrêté.")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Job Market Intelligence — Pipeline")
    parser.add_argument(
        "--mode",
        choices=["once", "scheduled"],
        default="once",
        help="'once' = une seule exécution, 'scheduled' = rafraîchissement auto",
    )
    parser.add_argument("--interval", type=int, default=6, help="Intervalle en heures (mode scheduled)")
    args = parser.parse_args()

    if args.mode == "scheduled":
        start_scheduler(interval_hours=args.interval)
    else:
        run_pipeline()
