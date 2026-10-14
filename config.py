
"""Configuration générale GLAR Revision Hub"""
APP_NAME = "GLAR REVISION HUB"
APP_VERSION = "1.0.0"
AUTHOR = "ESTM Dakar - L3 GLAR"

COLORS = {
    "primary": "#1B4332",
    "primary_light": "#2D6A4F",
    "accent": "#D4A017",
    "accent_light": "#F4D35E",
    "bg": "#FFFFFF",
    "bg_secondary": "#F5F7F3",
    "text": "#1A1A1A",
    "success": "#2D6A4F",
    "warning": "#D4A017",
    "danger": "#9B2226"
}

SEMESTRES = ["S5", "S6"]
NIVEAUX_DIFFICULTE = ["Débutant", "Intermédiaire", "Avancé", "Expert"]
STATUTS_REVISION = ["Non commencé", "En cours", "Révisé", "Maîtrisé"]

MATIERES_EXEMPLE = [
    {"nom": "Génie logiciel avancé", "description": "Patrons de conception, principes SOLID, architecture propre", "semestre": "S5", "difficulte": "Avancé", "objectif": 85},
    {"nom": "Administration systèmes Linux", "description": "Gestion avancée, scripting, services, sécurité", "semestre": "S5", "difficulte": "Avancé", "objectif": 80},
    {"nom": "Administration réseaux", "description": "TCP/IP, routage, switching, VLAN, services réseau", "semestre": "S5", "difficulte": "Avancé", "objectif": 85},
    {"nom": "Sécurité informatique", "description": "Cryptographie, pentest, durcissement, SOC", "semestre": "S6", "difficulte": "Expert", "objectif": 75},
    {"nom": "Bases de données avancées", "description": "Optimisation, transactions, PL/SQL, NoSQL", "semestre": "S5", "difficulte": "Avancé", "objectif": 80},
    {"nom": "Développement web", "description": "React, API REST, Django/Flask, sécurité web", "semestre": "S5", "difficulte": "Intermédiaire", "objectif": 80},
    {"nom": "Architecture logicielle", "description": "Microservices, DDD, CQRS, event-driven", "semestre": "S6", "difficulte": "Expert", "objectif": 75},
    {"nom": "Gestion de projets informatiques", "description": "Agile, Scrum, estimation, risques", "semestre": "S6", "difficulte": "Intermédiaire", "objectif": 85},
    {"nom": "Programmation avancée", "description": "Python avancé, concurrence, structures de données", "semestre": "S5", "difficulte": "Avancé", "objectif": 85},
    {"nom": "Cloud computing et virtualisation", "description": "Docker, Kubernetes, AWS, CI/CD", "semestre": "S6", "difficulte": "Avancé", "objectif": 80},
]

STORAGE_MODE = "sqlite"
MAX_UPLOAD_MB = 15
