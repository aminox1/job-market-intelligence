# 🧠 Job Market Intelligence

> **En clair :** C'est une application qui surveille automatiquement les offres d'emploi tech sur internet, extrait les compétences demandées, et t'affiche dans un beau tableau de bord : *quelles technologies sont les plus recherchées, lesquelles sont en hausse, et ce que tu devrais apprendre pour trouver un job plus facilement.*

🌐 **[➡️ Voir l'app en live](https://job-market-intelligence.streamlit.app)**

---

## 🤔 C'est quoi concrètement ?

Imagine que tu veux savoir :

- **"Est-ce que Python est encore demandé en 2025 ?"** → L'app te répond avec un graphique.
- **"Docker ou Kubernetes, lequel apprendre en priorité ?"** → L'app te montre lequel est le plus demandé.
- **"J'ai ces skills sur mon CV, est-ce que je match avec les offres du marché ?"** → L'app analyse ton profil et te dit ton score de compatibilité.
- **"Quels skills je dois apprendre pour décrocher plus d'offres ?"** → L'app te fait une liste personnalisée.

**En résumé :** Au lieu de passer des heures à lire des offres sur LinkedIn, l'app fait ça automatiquement pour toi et t'affiche les résultats en graphiques clairs.

---

## 🎬 Comment ça marche en 3 étapes

```
1. 🤖 COLLECTE          2. 🧠 ANALYSE            3. 📊 AFFICHAGE

L'app télécharge    →   Elle lit chaque offre  →  Tu vois tout ça dans
des centaines           et extrait les skills      un beau dashboard
d'offres d'emploi       mentionnés                 interactif
(automatiquement)       (Python, Docker...)
```

### Étape 1 — Collecte automatique 🤖
L'application se connecte à **Remotive** (un site d'offres d'emploi tech, gratuit) et télécharge toutes les offres disponibles : Software Dev, Backend, Frontend, DevOps, Data...

### Étape 2 — Analyse NLP (intelligence artificielle) 🧠
Pour chaque offre, le programme lit la description et repère automatiquement les technologies mentionnées. Il connaît **400+ compétences tech** : Python, Docker, React, TensorFlow, Kubernetes, PostgreSQL, etc.

### Étape 3 — Prédiction par Machine Learning 📈
Avec Scikit-Learn, l'app analyse l'évolution de la demande de chaque skill dans le temps et prédit si la tendance va monter, rester stable, ou baisser dans les 30 prochains jours.

---

## 🖥️ Les 5 pages du dashboard

### 🏠 Home — La page d'accueil
C'est la première chose que tu vois. Elle affiche :
- Combien d'offres ont été collectées
- Combien de compétences différentes ont été détectées
- Combien d'entreprises recrutent
- La dernière mise à jour

**Il y a aussi un bouton "🔄 Collecter les offres"** — quand tu cliques dessus, l'app va chercher les nouvelles offres sur internet en temps réel.

---

### 📊 Overview — Vue du marché
Cette page répond à la question : *"À quoi ressemble le marché de l'emploi tech en ce moment ?"*

Elle affiche :
- **Un graphique en camembert** : répartition des offres par catégorie (Backend, Frontend, DevOps...)
- **Un graphique barres** : combien d'offres sont en remote, hybride, ou présentiel
- **Les entreprises qui recrutent le plus** (classement top 15)
- **Les niveaux d'expérience demandés** : Junior, Mid, Senior, Lead
- **Un tableau de recherche** : cherche n'importe quelle offre par mot-clé

---

### 🧠 Skills Analysis — Analyse des compétences
Cette page répond à : *"Quelles sont les technologies les plus demandées ?"*

Elle affiche :
- **Le classement des 30 skills les plus demandés** (barres horizontales colorées)
- **Un treemap** : vue globale de toutes les compétences organisées par catégorie (langages, frameworks, cloud, ML...)
- **Un nuage de mots** : les skills les plus gros = les plus demandés
- **Une heatmap** : intensité de la demande par domaine

---

### 📈 Trends & Predictions — Prédictions ML
Cette page répond à : *"Est-ce que ce skill va avoir plus ou moins de demande dans 1 mois ?"*

Elle affiche :
- **🚀 Skills en hausse** : ceux dont la demande augmente
- **➡️ Skills stables** : ceux dont la demande ne bouge pas
- **📉 Skills en baisse** : ceux qui perdent en popularité
- **Un graphique de prédiction** : tu choisis un skill et tu vois sa courbe historique + la prédiction pour les 30 prochains jours (avec zone d'incertitude)

> C'est une vraie régression polynomiale Scikit-Learn qui tourne derrière !

---

### 🎯 Recommender — Recommandation personnalisée
**C'est la page la plus intéressante.** Elle répond à : *"Avec mes compétences actuelles, comment je suis positionné sur le marché ?"*

Tu sélectionnes tes compétences actuelles (ex: Python, Docker, Git...) et l'app calcule :
- **Ton score de compatibilité** avec le marché (ex: 75% de match avec le Top 20)
- **Un graphique radar** de ton profil (langages, cloud, ML, DevOps...)
- **Les skills que tu devrais apprendre en priorité** (classés par demande + pertinence pour ton rôle cible)
- **Les offres d'emploi qui correspondent à ton profil** (avec % de match pour chaque offre)
- **Skill Gap Analysis** : un graphique vert/gris qui montre ce que tu as et ce qui te manque

---

## 🚀 Lancer l'application (2 commandes)

### Prérequis
- Python 3.10 installé
- Windows, Mac ou Linux

### Installation (une seule fois)
```powershell
pip install -r requirements.txt
```

### Lancer (à chaque fois)

**Étape 1 — Collecter les offres d'emploi :**
```powershell
python -m src.scraper.scheduler
```
*Cette commande va chercher les offres sur internet. Elle prend ~30 secondes.*

**Étape 2 — Ouvrir le dashboard :**
```powershell
streamlit run src/dashboard/app.py
```
*Puis ouvre ton navigateur sur : http://localhost:8501*

---

## 🐳 Lancer avec Docker (encore plus simple)

```bash
docker-compose up --build
```
Puis ouvre http://localhost:8501. C'est tout.

---

## 🧪 Tester le code

```powershell
pytest tests/ -v
```

---

## 📁 Organisation du code

```
job-market-intelligence/
│
├── src/
│   ├── database/         ← Stockage des données (SQLite)
│   ├── scraper/          ← Collecte des offres sur internet
│   ├── nlp/              ← Extraction des compétences (NLP)
│   ├── ml/               ← Prédiction des tendances (Machine Learning)
│   └── dashboard/        ← Interface graphique (Streamlit)
│
├── tests/                ← Tests automatisés
├── requirements.txt      ← Liste des librairies Python
├── Dockerfile            ← Pour déployer avec Docker
└── README.md             ← Ce fichier
```

---

## 🛠️ Technologies utilisées

| Technologie | Rôle dans l'app |
|-------------|----------------|
| **Python** | Langage principal |
| **Streamlit** | Interface graphique du dashboard |
| **Plotly** | Graphiques interactifs |
| **SQLAlchemy + SQLite** | Base de données locale |
| **Requests** | Appels API pour collecter les offres |
| **Regex (NLP)** | Extraction des compétences depuis les textes |
| **Scikit-Learn** | Machine Learning pour les prédictions |
| **WordCloud** | Nuage de mots |
| **APScheduler** | Mise à jour automatique des données |
| **Docker** | Déploiement conteneurisé |
| **Pytest** | Tests automatisés |

---

## 👤 Auteur

**MOUMENI Mohamed Amine**  
Ingénieur en IA & Développement Logiciel · M2 MBDS + IAA2  
📍 Antibes, France · ✉️ aminemoumeni61@gmail.com

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Profil-blue?logo=linkedin)](https://www.linkedin.com/in/mohamed-amine-moumeni-598699209/)
[![GitHub](https://img.shields.io/badge/GitHub-Code-black?logo=github)](https://github.com/aminox1)
