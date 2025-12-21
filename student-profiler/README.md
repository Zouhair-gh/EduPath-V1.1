# StudentProfiler

StudentProfiler classe automatiquement les étudiants en profils comportementaux (assidu, procrastinateur, en difficulté, décrocheur) à partir des features préparées par PrepaData. Il applique StandardScaler, PCA et KMeans, versionne les modèles (joblib), persiste les assignations, les définitions de profils et l’historique de clustering dans PostgreSQL.

## Fonctionnalités
- Récupération des features (`student_metrics`, `temporal_features`) depuis la base analytique
- Pipeline: StandardScaler → PCA (2 composants) → KMeans (5 clusters)
- Validation: silhouette score, inertia
- Labellisation des clusters et assignation des étudiants avec score de confiance
- API FastAPI: profils par étudiant, définitions, distribution, métriques, re-train, visualisation PCA (image base64)
- Sauvegarde des modèles: `models/model_vX.pkl` + meta JSON

## Schéma PostgreSQL
Tables créées automatiquement si absentes:
- `student_profiles(student_id, profile_id, profile_label, confidence_score, assigned_at, model_version)`
- `profile_definitions(profile_id, label, description, avg_engagement, avg_success_rate, avg_punctuality, student_count, created_at)`
- `clustering_history(model_version, n_clusters, silhouette_score, inertia, features_used, trained_at)`

## Configuration
Variables d’environnement:
- `ANALYTICS_DB_HOST` (default: localhost)
- `ANALYTICS_DB_PORT` (default: 5433)
- `ANALYTICS_DB_NAME` (default: analytics_db)
- `ANALYTICS_DB_USER` (default: postgres)
- `ANALYTICS_DB_PASSWORD` (default: password)
- `API_PORT` (default: 8002)
- `N_CLUSTERS` (default: 5)
- `PCA_COMPONENTS` (default: 2)
- `MODEL_VERSION` (default: v1.0)

## Démarrage
Installer les dépendances puis lancer l’API:

```bash
cd student-profiler
python -m venv .venv
. .venv/Scripts/activate
pip install -r requirements.txt
uvicorn src.main:app --host 0.0.0.0 --port 8002 --reload
```

### Docker
Build et run via Docker:

```bash
cd student-profiler
docker build -t student-profiler:latest .
docker run --rm -p 8002:8002 \
	-e ANALYTICS_DB_HOST=host.docker.internal \
	-e ANALYTICS_DB_PORT=5433 \
	-e ANALYTICS_DB_NAME=analytics_db \
	-e ANALYTICS_DB_USER=postgres \
	-e ANALYTICS_DB_PASSWORD=postgres \
	student-profiler:latest
```

Ou avec Compose:

```bash
cd student-profiler
docker compose up --build -d
```

## Endpoints
- GET `/api/profiles/student/{id}`: profil d’un étudiant
- GET `/api/profiles/definitions`: liste des profils types
- GET `/api/profiles/distribution`: répartition étudiants par profil
- POST `/api/profiles/retrain`: ré-entraînement du modèle et assignations
- GET `/api/profiles/metrics`: dernière métrique de clustering
- GET `/api/profiles/visualization`: image PCA base64

## Réentraînement
Script CLI:
```bash
python -m src.scripts.train_model
```
Évaluation rapide:
```bash
python -m src.scripts.evaluate_model
```

## Notes
- Port par défaut 5433 pour se connecter à la base analytique PrepaData (compose map). Ajustez `ANALYTICS_DB_PORT` si besoin.
- Les labels sont dérivés par règles simples basées sur les moyennes de `engagement_score`, `success_rate`, `punctuality_score`.
- L’image de visualisation s’appuie sur la projection PCA du modèle en mémoire.
