# LMSConnector

Microservice d'ingestion et normalisation des données d'apprentissage depuis plusieurs LMS (Moodle, Canvas, Blackboard) vers PostgreSQL. Conçu pour une architecture microservices de Learning Analytics.

## Rôle
- Extraire traces d'apprentissage: notes, participations forums, complétions, soumissions, etc.
- Normaliser et persister dans PostgreSQL (tables: students, courses, enrollments, grades, activity_logs, sync_logs).
- Gérer plusieurs instances LMS simultanément.
- Planifier les synchronisations (cron toutes les 6h).
- API REST pour déclencher manuellement et consulter le statut.

## Stack
- Backend: Node.js 18+, Express.js, Axios, node-cron, helmet, dotenv.
- DB: PostgreSQL 15+.

## Configuration
Copiez `.env.example` vers `.env` et renseignez vos valeurs:

```
PORT=3001
API_KEY=change-me-please
PGHOST=localhost
PGPORT=5432
PGUSER=postgres
PGPASSWORD=postgres
PGDATABASE=edupath
DISABLE_DB=false
MOODLE_BASE_URL=https://edu-path.moodlecloud.com
MOODLE_TOKEN=your-moodle-token-here
```

> Note: Ne committez jamais vos tokens. Utilisez `.env` local ou un secret manager.

## Installation

```bash
cd LMSConnector
npm install
```

## Démarrage (dev)

```bash
# Démarrage simple
npm start

# Démarrage sans DB (dev only)
set DISABLE_DB=true & npm start
```

## API REST
- `GET /health` — état du service (et DB si active).
- `GET /sources` — liste des sources LMS (protégé API key).
- `POST /sources` — créer/activer une source LMS (protégé API key).
- `POST /sync/moodle` — lancer synchro Moodle pour toutes les sources actives (protégé API key).
- `POST /sync/moodle/:sourceId` — lancer synchro pour une source précise (protégé API key).
- `GET /jobs/:jobId` — statut d'un job de synchro.

Headers sécurité pour endpoints admin:
```
X-API-Key: <API_KEY>
```

## Schéma PostgreSQL
Tables principales créées par la migration init:
- `students(id, external_id, email, firstname, lastname, username, created_at, updated_at)`
- `courses(id, external_id, shortname, fullname, category_id, visible, created_at)`
- `enrollments(id, student_id, course_id, enrolled_at)`
- `grades(id, student_id, course_id, grade_item, grade_value, grade_max, timestamp)`
- `activity_logs(id, student_id, course_id, activity_type, resource_id, duration_seconds, timestamp, metadata JSONB)`
- `sync_logs(id, lms_type, sync_type, status, records_processed, error_message, started_at, completed_at)`
- `lms_sources(id, type, base_url, token, oauth_client_id, oauth_client_secret, active, created_at)`

## Planification
- Cron: toutes les 6 heures (`0 */6 * * *`) lance `syncMoodle()` sur les sources actives.

## Limitations et extensions
- Certaines métriques (temps de connexion, forums détaillés) requièrent des API additionnelles Moodle non configurées ici. Le service enregistre `lastaccess` et discussions si `forumId` est disponible.
- Connecteurs Canvas/Blackboard: interfaces prévues, implémentation à ajouter.

## Sécurité
- `helmet` activé, API key pour endpoints admin.
- Validation des tokens LMS via appel `core_webservice_get_site_info` lors de la synchro.

## Exécution rapide
```bash
# Variables d'environnement
copy .env.example .env
# Éditer .env et définir MOODLE_TOKEN
npm install
npm run migrate   # si DB disponible
npm start
```
