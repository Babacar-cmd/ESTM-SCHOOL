# GLAR REVISION HUB - Licence 3 GLAR - ESTM Dakar

Application web de révision universitaire moderne, responsive, Python + Streamlit.

## Fonctionnalités
- Tableau de bord KPIs, graphiques Plotly, objectifs
- Matières CRUD - 10 matières exemple GLAR pré-chargées
- Cours & Documents : import PDF/TXT/MD avec extraction PyMuPDF, détection PDF scannés
- Fiches : auto depuis cours + manuel
- Quiz & QCM : unique/multiple, correction immédiate ou fin, score /20, historique
- Exercices avec correction masquée
- Assistant RAG local + option OpenAI via st.secrets
- Flashcards révision espacée
- Planning avec retard
- Statistiques réelles
- Recherche globale

Design vert foncé #1B4332, blanc, doré #D4A017

## Lancement local
```bash
python -m pip install -r requirements.txt
streamlit run app.py
```

## Déploiement Streamlit Community Cloud
1. Créer dépôt GitHub
2. Pousser dossier
```bash
git init
git add .
git commit -m "init GLAR Revision Hub"
git branch -M main
git remote add origin https://github.com/<user>/GLAR-Revision-Hub.git
git push -u origin main
```
3. Aller sur share.streamlit.io -> New app -> repo / main / app.py
4. Deploy

### Secrets optionnel
Dans Streamlit Cloud : Settings -> Secrets, coller:
```toml
[general]
storage_mode="sqlite"
# [openai]
# api_key="sk-..."
# [postgres]
# host="db.xxx.supabase.co"
# ...
```

## Persistance données - IMPORTANT
- SQLite local glar_revision.db est éphémère sur Streamlit Cloud (effacé au reboot)
- Pour persistance durable : utiliser PostgreSQL hébergé (Supabase, Neon)
  - Ajouter psycopg2-binary à requirements
  - Dans database.py, brancher st.secrets["postgres"] si storage_mode="postgres"
- App affiche toujours mode stockage utilisé

## Sécurité
- Requêtes paramétrées
- Pas de clé API en dur
- Limite upload 15 Mo
- Pas d'exécution code arbitraire
- .gitignore exclut secrets et db

## Tests effectués
- Démarrage app sans erreur : OK
- Matières CRUD : OK
- Import PDF texte : OK, PDF scanné : warning affiché OK
- Quiz score calcul : OK (test unitaire utils.calculate_quiz_score)
- Corrections masquées jusqu'à demande : OK
- Flashcards changement statut : OK
- Planning retard : OK
- Fonctionne sans clé API : OK
- Dépendances compatibles Streamlit Cloud : OK

## Structure
```
GLAR-Revision-Hub/
 app.py
 config.py
 database.py
 utils.py
 models.py
 data/seed.py
 components/
 .streamlit/config.toml
 .streamlit/secrets.toml.example
 requirements.txt
 README.md
```

## Limites
- OCR non inclus
- Pas d'auth multi-user (futur via Postgres)
- Assistant IA externe optionnel

Licence pédagogique ESTM Dakar
