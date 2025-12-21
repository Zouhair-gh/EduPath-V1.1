# PathPredictor

PathPredictor prédit la probabilité d'échec/réussite pour les modules à venir en utilisant XGBoost, explique les prédictions (SHAP), génère des alertes et trace les métriques via MLflow.

## Fonctionnalités
- Features: engagement, réussite, ponctualité, profil (StudentProfiler), tendance engagement, note précédente, forum, ratio temps, absences, complétion devoirs
- Modèle: `xgboost.XGBClassifier` avec validation croisée (StratifiedKFold)
- Explainability: SHAP top 3 features
- Alertes: HIGH/MEDIUM/LOW selon seuils
- MLOps: MLflow tracking (params, metrics, model)

## Schéma DB
Tables créées automatiquement: `predictions`, `alerts`, `model_registry`.

## Configuration
Env par défaut (adaptés à PrepaData DB sur port 5433):
- ANALYTICS_DB_HOST=localhost
- ANALYTICS_DB_PORT=5433
- ANALYTICS_DB_NAME=analytics_db
- ANALYTICS_DB_USER=postgres
- ANALYTICS_DB_PASSWORD=postgres
- MLFLOW_TRACKING_URI=http://localhost:5000 (sinon fallback à `file:mlruns`)
- MLFLOW_EXPERIMENT_NAME=path_predictor
- API_PORT=8003
- ALERT_THRESHOLD_HIGH=0.70
- ALERT_THRESHOLD_MEDIUM=0.50

## Démarrage API
```bash
cd path-predictor
python -m venv .venv
. .venv/Scripts/activate
pip install -r requirements.txt
uvicorn src.main:app --host 0.0.0.0 --port 8003 --reload
```

## Entraînement
```bash
# Trace dans MLflow, enregistre dans model_registry (STAGING)
python -m src.training.train_model

# Évaluation CV
python -m src.training.evaluate_model
```

## Endpoints
- POST `/api/predict`: prédiction unitaire (student_id + features sinon récup DB)
- POST `/api/predict/batch` (CSV upload): prédictions batch
- GET `/api/alerts?severity=HIGH`: alertes actives
- GET `/api/explain/{prediction_id}`: SHAP top 3
- GET `/api/models/current`: modèle en production (DB registry)
- POST `/api/models/promote/{model_id}`: promote STAGING → PRODUCTION
- GET `/api/metrics/performance`: consulter MLflow pour détails

## Docker
```bash
cd path-predictor
docker build -t path-predictor:latest .
# Connect to host DB and MLflow
docker run --rm -p 8003:8003 \
  -e ANALYTICS_DB_HOST=host.docker.internal \
  -e ANALYTICS_DB_PORT=5433 \
  -e ANALYTICS_DB_NAME=analytics_db \
  -e ANALYTICS_DB_USER=postgres \
  -e ANALYTICS_DB_PASSWORD=postgres \
  -e MLFLOW_TRACKING_URI=http://host.docker.internal:5000 \
  path-predictor:latest
```
