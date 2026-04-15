"""Tests pour le module NLP skill_extractor."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.nlp.skill_extractor import extract_skills, extract_skill_names, get_skill_category


class TestSkillExtractor:

    def test_extract_python(self):
        text = "We need a Python developer with experience in Django and REST APIs."
        skills = extract_skill_names(text)
        assert "python" in skills
        assert "django" in skills

    def test_extract_docker(self):
        text = "Experience with Docker, Kubernetes and CI/CD pipelines required."
        skills = extract_skill_names(text)
        assert "docker" in skills
        assert "kubernetes" in skills

    def test_extract_ml_skills(self):
        text = "Strong knowledge of Machine Learning, TensorFlow, PyTorch and scikit-learn."
        skills = extract_skill_names(text)
        assert "tensorflow" in skills or "pytorch" in skills or "scikit-learn" in skills

    def test_no_false_positives(self):
        text = "We are looking for a great team player with communication skills."
        skills = extract_skill_names(text)
        # Aucun skill tech ne devrait être extrait ici
        assert "python" not in skills
        assert "docker" not in skills

    def test_categories_returned(self):
        text = "Python, React, Docker, AWS, TensorFlow"
        skills = extract_skills(text)
        categories = {s["category"] for s in skills}
        assert len(categories) > 1  # Plusieurs catégories attendues

    def test_get_skill_category(self):
        assert get_skill_category("python") == "language"
        assert get_skill_category("docker") == "devops"
        assert get_skill_category("tensorflow") == "ml_ai"

    def test_case_insensitive(self):
        text = "PYTHON and TENSORFLOW are required"
        skills = extract_skill_names(text)
        assert "python" in skills
        assert "tensorflow" in skills


class TestJobClassifier:

    def test_senior_detection(self):
        from src.nlp.job_classifier import classify_level
        assert classify_level("Senior Python Developer") == "senior"

    def test_junior_detection(self):
        from src.nlp.job_classifier import classify_level
        assert classify_level("Junior Software Engineer") == "junior"

    def test_remote_detection(self):
        from src.nlp.job_classifier import classify_remote_type
        assert classify_remote_type("Worldwide", "This is a fully remote position") == "remote"

    def test_hybrid_detection(self):
        from src.nlp.job_classifier import classify_remote_type
        assert classify_remote_type("Paris, France", "Hybrid work policy") == "hybrid"
