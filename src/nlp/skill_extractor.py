"""
Extraction automatique des compétences techniques depuis les descriptions de job.
Utilise une base de données curatée de 400+ skills tech — zéro dépendance lourde.
"""
import re
import logging
from typing import List, Dict, Tuple, Set

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────────────────────
# BASE DE DONNÉES DES SKILLS (400+ compétences tech)
# ─────────────────────────────────────────────────────────────────────────────
SKILLS_DATABASE: Dict[str, List[str]] = {
    "language": [
        "python", "javascript", "typescript", "java", "c++", "c#", "go", "golang",
        "rust", "kotlin", "swift", "scala", "r", "php", "ruby", "dart", "lua",
        "perl", "matlab", "julia", "haskell", "erlang", "elixir", "groovy",
        "objective-c", "bash", "shell", "powershell", "cobol", "fortran", "zig",
    ],
    "frontend": [
        "react", "react.js", "vue", "vue.js", "angular", "next.js", "nuxt.js",
        "svelte", "jquery", "html", "css", "sass", "less", "tailwind", "bootstrap",
        "material-ui", "chakra-ui", "webpack", "vite", "gatsby", "remix",
        "three.js", "d3.js", "storybook", "figma", "web components",
    ],
    "backend": [
        "node.js", "express", "fastapi", "flask", "django", "spring boot", "spring",
        "laravel", "rails", "asp.net", ".net", "nestjs", "gin", "fiber",
        "actix", "phoenix", "grpc", "rest api", "graphql", "microservices", "serverless",
        "quarkus", "micronaut", "ktor",
    ],
    "database": [
        "postgresql", "mysql", "mongodb", "redis", "elasticsearch", "sqlite",
        "cassandra", "dynamodb", "neo4j", "oracle", "sql server", "mariadb",
        "cockroachdb", "firebase", "supabase", "influxdb", "clickhouse",
        "snowflake", "bigquery", "couchdb", "arangodb", "timescaledb",
    ],
    "cloud": [
        "aws", "azure", "gcp", "google cloud", "heroku", "vercel", "netlify",
        "digitalocean", "cloudflare", "lambda", "ec2", "s3", "rds",
        "eks", "ecs", "fargate", "cloud functions", "app engine", "cloud run",
        "azure functions", "azure devops",
    ],
    "devops": [
        "docker", "kubernetes", "k8s", "terraform", "ansible", "jenkins",
        "github actions", "gitlab ci", "circleci", "travis ci", "helm",
        "prometheus", "grafana", "datadog", "nginx", "apache",
        "linux", "ubuntu", "ci/cd", "pulumi", "vagrant", "chef", "puppet",
        "argocd", "istio", "vault", "consul",
    ],
    "ml_ai": [
        "machine learning", "deep learning", "neural network", "nlp",
        "computer vision", "tensorflow", "pytorch", "keras", "scikit-learn",
        "pandas", "numpy", "matplotlib", "seaborn", "jupyter", "huggingface",
        "transformers", "bert", "gpt", "llm", "langchain", "openai",
        "stable diffusion", "reinforcement learning", "xgboost", "lightgbm",
        "catboost", "opencv", "pillow", "spacy", "nltk", "mlflow",
        "feature engineering", "data science", "statistics", "a/b testing",
        "face recognition", "object detection", "yolo", "cnn", "rnn", "lstm",
        "random forest", "gradient boosting", "pca", "clustering", "rag",
        "vector database", "embedding", "fine-tuning",
    ],
    "big_data": [
        "spark", "apache spark", "pyspark", "hadoop", "kafka", "flink",
        "hive", "presto", "dbt", "airflow", "luigi", "prefect", "dagster",
        "data warehouse", "data lake", "etl", "databricks", "nifi",
        "storm", "samza", "beam", "dataflow",
    ],
    "mobile": [
        "flutter", "react native", "android", "ios", "swift", "kotlin",
        "xamarin", "ionic", "cordova", "expo", "swiftui", "jetpack compose",
    ],
    "tool": [
        "git", "github", "gitlab", "bitbucket", "jira", "confluence",
        "postman", "swagger", "openapi", "vscode", "intellij",
        "agile", "scrum", "kanban", "tdd", "bdd", "solid", "design patterns",
        "rest", "soap", "microservices", "ddd", "clean architecture",
        "wiremock", "junit", "pytest", "jest", "selenium", "cypress",
    ],
}

# ─────────────────────────────────────────────────────────────────────────────
# Pré-compilation des patterns regex pour la performance
# ─────────────────────────────────────────────────────────────────────────────
_COMPILED_PATTERNS: Dict[str, List[Tuple[re.Pattern, str, str]]] = {}


def _build_patterns() -> None:
    """Compile tous les patterns regex une seule fois au démarrage."""
    global _COMPILED_PATTERNS
    if _COMPILED_PATTERNS:
        return

    for category, skills in SKILLS_DATABASE.items():
        _COMPILED_PATTERNS[category] = []
        for skill in skills:
            # Escape les caractères spéciaux (ex: "c++", ".net", "node.js")
            escaped = re.escape(skill)
            # Word boundary adapté : \b ne fonctionne pas avec "c++" ou ".net"
            pattern = re.compile(
                r"(?<![a-z0-9\-\._])" + escaped + r"(?![a-z0-9\-\._])",
                re.IGNORECASE,
            )
            _COMPILED_PATTERNS[category].append((pattern, skill, category))


def extract_skills(text: str) -> List[Dict[str, str]]:
    """
    Extrait les skills techniques d'un texte.

    Args:
        text: Description de l'offre d'emploi (texte brut)

    Returns:
        Liste de dicts {'name': str, 'category': str}
    """
    if not text:
        return []

    _build_patterns()

    found: Set[str] = set()
    results: List[Dict[str, str]] = []
    text_lower = text.lower()

    for category, patterns in _COMPILED_PATTERNS.items():
        for pattern, skill_name, skill_cat in patterns:
            if skill_name not in found and pattern.search(text_lower):
                found.add(skill_name)
                results.append({"name": skill_name, "category": skill_cat})

    return results


def extract_skill_names(text: str) -> List[str]:
    """Retourne uniquement les noms des skills extraits."""
    return [s["name"] for s in extract_skills(text)]


def get_skill_category(skill_name: str) -> str:
    """Retourne la catégorie d'un skill donné."""
    skill_lower = skill_name.lower()
    for category, skills in SKILLS_DATABASE.items():
        if skill_lower in skills:
            return category
    return "other"


def get_all_known_skills() -> List[str]:
    """Retourne tous les skills connus dans la base."""
    all_skills = []
    for skills in SKILLS_DATABASE.values():
        all_skills.extend(skills)
    return sorted(set(all_skills))


# ─────────────────────────────────────────────────────────────────────────────
# Statistiques
# ─────────────────────────────────────────────────────────────────────────────

def skill_frequency(texts: List[str]) -> Dict[str, int]:
    """Calcule la fréquence de chaque skill dans une liste de textes."""
    freq: Dict[str, int] = {}
    for text in texts:
        for skill in extract_skill_names(text):
            freq[skill] = freq.get(skill, 0) + 1
    return dict(sorted(freq.items(), key=lambda x: x[1], reverse=True))
