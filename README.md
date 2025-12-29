# EduPath – Plateforme d’Apprentissage Basée sur les Microservices

## Présentation Générale

EduPath est une plateforme d’apprentissage intelligente, modulaire et évolutive, conçue selon une architecture microservices. Elle vise à offrir une expérience personnalisée aux étudiants, enseignants et administrateurs, en intégrant des modules de recommandation, de prédiction de parcours, de gestion de profils, de coaching, et bien plus.

---

## Architecture Générale

L’architecture d’EduPath repose sur plusieurs microservices indépendants, chacun responsable d’un domaine fonctionnel précis. Cette approche permet une grande flexibilité, une scalabilité horizontale et une maintenance facilitée.

<img width="596" height="361" alt="ArchitectureMicroService" src="https://github.com/user-attachments/assets/2ba06fff-75d8-43a0-9484-6e3b4d302388" />

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

<img width="800" alt="BPMN Application complete_page-0001" src="https://github.com/user-attachments/assets/7b33f2f2-e01b-4716-891d-d99259c91469" />

---

## Fonctionnalités par Service & Captures d’Écran

### 1. LMSConnector
- Synchronisation avec les LMS
- Sécurité et gestion des accès

### 2. path-predictor
- Prédiction de parcours
- Analyse des données d’apprentissage
- **Capture d’écran :**
    <img width="268" height="165" alt="Service4_PathPredictor_health" src="https://github.com/user-attachments/assets/13d88177-58cb-4e64-96e1-68c02a8d322e" />

### 3. prepa-data
- Orchestration et préparation des données

### 4. reco-builder
- Génération de recommandations

### 5. student-coach
- Coaching personnalisé
- Suivi des cours, quiz et progression
- **Captures d’écran :**
    <img width="952" height="244" alt="Service7_StudentCoach_courses" src="https://github.com/user-attachments/assets/ced779c4-20a8-4f10-be11-05cb6db72d7c" />
    <img width="582" height="451" alt="Service7_StudentCoach_quizz" src="https://github.com/user-attachments/assets/444c11a2-705c-4ed5-b29a-27cdf0c21788" />
    <img width="959" height="449" alt="Service7_StudentCoach_StudentDashboard" src="https://github.com/user-attachments/assets/057a1891-007c-4f95-bab4-61c752dd4808" />
    <img width="901" height="417" alt="Service7_StudentCoach_courseOverview" src="https://github.com/user-attachments/assets/ea152731-5113-41d6-b649-02391258bc79" />

### 6. student-profiler
- Analyse et gestion des profils étudiants
- **Captures d’écran :**
    <img width="395" height="319" alt="Service3_StudentProfiler_health" src="https://github.com/user-attachments/assets/25178beb-7a32-48a4-a0bb-d6ea94d770ee" />
    <img width="949" height="442" alt="Service3_StudentProfiler_routes" src="https://github.com/user-attachments/assets/167d246d-bc3d-41b3-92fd-0de33e54231b" />

### 7. teacher-console
- Console de gestion pour enseignants
- Alertes, suivi et dashboard
- **Captures d’écran :**
    <img width="1096" height="219" alt="Service6_TeacherConsole_Alerts" src="https://github.com/user-attachments/assets/4d334bf7-0076-4bd7-99f4-518aa48dbe5a" />
    <img width="954" height="467" alt="Service6_TeacherConsole_dashboard" src="https://github.com/user-attachments/assets/2d50d660-91fb-4ae7-8018-29be68b095fa" />
    <img width="953" height="236" alt="Service6_TeacherConsole_Student" src="https://github.com/user-attachments/assets/3e3b9c6d-2af2-48d1-8c64-f729a5304714" />

### 8. AirFlow (prépa-data)
- Orchestration des workflows de données
- **Captures d’écran :**
    <img width="954" height="486" alt="Service2_AirFlow_Dashboard" src="https://github.com/user-attachments/assets/746076f2-1534-42ca-a9ca-30c4b173ca07" />
    <img width="960" height="413" alt="Service2_AirFlow_Login" src="https://github.com/user-attachments/assets/dbca7ee7-f831-4d60-bd6e-b7f740f9f1d2" />

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

## Demo


https://github.com/user-attachments/assets/944b5f33-fe74-402d-bd3d-4cfb6898dcf7



https://github.com/user-attachments/assets/eb08715b-bce6-4160-9fab-22853455b80b


Pour toute question ou suggestion, veuillez contacter l’équipe EduPath.
