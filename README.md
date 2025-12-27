
# EduPath – Plateforme d’Apprentissage Basée sur les Microservices

## Présentation Générale

EduPath est une plateforme d’apprentissage intelligente, modulaire et évolutive, conçue selon une architecture microservices. Elle vise à offrir une expérience personnalisée aux étudiants, enseignants et administrateurs, en intégrant des modules de recommandation, de prédiction de parcours, de gestion de profils, de coaching, et bien plus.

---

## Architecture Générale

L’architecture d’EduPath repose sur plusieurs microservices indépendants, chacun responsable d’un domaine fonctionnel précis. Cette approche permet une grande flexibilité, une scalabilité horizontale et une maintenance facilitée.

![Architecture Microservices](../EDU/ArchitectureMicroService.PNG)

### Microservices Principaux

- **LMSConnector** : Connecteur principal avec les systèmes LMS externes, gestion des synchronisations et de la sécurité.
- **path-predictor** : Prédiction intelligente des parcours étudiants à l’aide de modèles de machine learning.
- **prepa-data** : Préparation, ingestion et orchestration des données pour l’ensemble de la plateforme.
- **reco-builder** : Génération de recommandations personnalisées pour les étudiants.
- **student-coach** : Module de coaching et d’accompagnement personnalisé.
- **student-profiler** : Gestion et analyse des profils étudiants.
- **teacher-console** : Console dédiée aux enseignants pour le suivi, l’alerte et la gestion des étudiants.

---

## BPMN – Orchestration des Processus Métier

La plateforme s’appuie sur des processus métier orchestrés via BPMN pour garantir la cohérence et l’automatisation des flux entre microservices.

![BPMN Application](../EDU/BPMN Application complete_page-0001.jpg)

---

## Fonctionnalités par Service & Captures d’Écran

### 1. LMSConnector
- Synchronisation avec les LMS
- Sécurité et gestion des accès

### 2. path-predictor
- Prédiction de parcours
- Analyse des données d’apprentissage
- **Capture d’écran :**
	- ![Path Predictor Health](../EDU/Service4_PathPredictor_health.PNG)

### 3. prepa-data
- Orchestration et préparation des données

### 4. reco-builder
- Génération de recommandations

### 5. student-coach
- Coaching personnalisé
- Suivi des cours, quiz et progression
- **Captures d’écran :**
	- ![Student Coach – Vue Cours](../EDU/Service7_StudentCoach_courses.PNG)
	- ![Student Coach – Quizz](../EDU/Service7_StudentCoach_quizz.PNG)
	- ![Student Coach – Dashboard](../EDU/Service7_StudentCoach_StudentDashboard.PNG)
	- ![Student Coach – Vue Générale](../EDU/Service7_StudentCoach_courseOverview.PNG)

### 6. student-profiler
- Analyse et gestion des profils étudiants
- **Captures d’écran :**
	- ![Student Profiler – Health](../EDU/Service3_StudentProfiler_health.PNG)
	- ![Student Profiler – Routes](../EDU/Service3_StudentProfiler_routes.PNG)

### 7. teacher-console
- Console de gestion pour enseignants
- Alertes, suivi et dashboard
- **Captures d’écran :**
	- ![Teacher Console – Alerts](../EDU/Service6_TeacherConsole_Alerts.PNG)
	- ![Teacher Console – Dashboard](../EDU/Service6_TeacherConsole_dashboard.PNG)
	- ![Teacher Console – Étudiant](../EDU/Service6_TeacherConsole_Student.PNG)

### 8. AirFlow (prépa-data)
- Orchestration des workflows de données
- **Captures d’écran :**
	- ![AirFlow – Dashboard](../EDU/Service2_AirFlow_Dashboard.PNG)
	- ![AirFlow – Login](../EDU/Service2_AirFlow_Login.PNG)

---

## Technologies Utilisées
- Node.js, Python, Docker, Airflow, React Native, etc.
- Communication via API REST et message broker
- Orchestration des workflows avec Airflow et BPMN

---

## Démarrage & Déploiement

Chaque microservice dispose de son propre fichier `README.md` pour les instructions spécifiques. Le déploiement global s’effectue via Docker Compose à la racine de chaque service.

---

## Contribution

Merci de consulter les guides de contribution dans chaque dossier de service.

---

## Contact
Pour toute question ou suggestion, veuillez contacter l’équipe EduPath.

