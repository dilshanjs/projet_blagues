# Générateur de Blagues avec Interface Web

Ce projet est une application web qui génère des blagues en utilisant l'API Gemini de Google Cloud Platform. Il comprend une interface utilisateur interactive et la possibilité de sauvegarder ses blagues préférées.

## Structure du Projet

```

## 1. Backend

### Technologies Utilisées
- **Flask** : Framework web Python
- **Google Cloud Platform** :
  - Vertex AI (Gemini Pro) pour la génération de blagues
  - Cloud Storage pour le stockage des données
- **Python 3.9**

### Fonctionnalités Principales
1. **Génération de Blagues** (`/api/joke`)
   - Utilise le modèle Gemini Pro
   - Génère des blagues en français
   - Gestion des erreurs et logging

2. **Gestion des Données** (`/data`)
   - Lecture/écriture dans Google Cloud Storage
   - Stockage des blagues favorites
   - Gestion des erreurs d'authentification

3. **Monitoring** (`/status`)
   - Affichage du statut du serveur
   - Horodatage des requêtes

### Configuration
- Variables d'environnement requises :
  - `GOOGLE_APPLICATION_CREDENTIALS`
  - `PROJECT_ID`
  - `LOCATION`
  - `BUCKET_NAME`
  - `FILE_NAME`

## 2. Frontend

### Technologies Utilisées
- **HTML5**
- **CSS3**
- **JavaScript** (Vanilla)

### Pages
1. **Page d'Accueil** (`/`)
   - Navigation vers les différentes fonctionnalités
   - Design responsive

2. **Générateur de Blagues** (`/joke`)
   - Interface interactive
   - Bouton de génération
   - Sauvegarde des blagues favorites
   - Animation de chargement

3. **Pages Supplémentaires**
   - Status (`/status`)
   - Données (`/data`)
   - Hello (`/hello`)

### Style
- Design moderne et responsive
- Animations fluides
- Thème de couleur cohérent
- Support mobile

## 3. Docker

### Configuration
```dockerfile
# Base image
FROM python:3.9-slim

# Configuration
ENV PYTHONUNBUFFERED=True
ENV FLASK_APP=main.py
ENV FLASK_ENV=development
ENV FLASK_DEBUG=1

# Installation des dépendances
RUN apt-get update && apt-get install -y build-essential curl

# Configuration de l'application
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Déploiement
COPY . .
EXPOSE 5000

# Démarrage
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "1", "--timeout", "120", "main:app"]
```

### Dépendances Principales
- `flask`
- `python-dotenv`
- `google-cloud-storage`
- `google-cloud-aiplatform`
- `pandas`
- `gunicorn`

## Installation et Démarrage

1. **Cloner le Repository**
```bash
git clone [URL_DU_REPO]
cd projet_blague
```

2. **Configuration des Variables d'Environnement**
```bash
cp .env.example .env
# Éditer .env avec vos credentials
```

3. **Installation des Dépendances**
```bash
pip install -r requirements.txt
```

4. **Démarrage Local**
```bash
python main.py
```

5. **Démarrage avec Docker**
```bash
docker build -t generateur-blagues .
docker run -p 8080:8080 generateur-blagues
```

## Sécurité
- Gestion sécurisée des credentials Google Cloud
- Validation des entrées utilisateur
- Logging des erreurs et des accès
- Protection contre les injections

## Maintenance
- Logs disponibles dans le dossier `logs/`
- Monitoring via la route `/status`
- Gestion des erreurs avec messages explicites

## Flux d'Exécution de l'Application

### 1. Démarrage de l'Application (`main.py`)
```python
# 1. Configuration initiale
import os
from flask import Flask
from app.routes import register_routes
from dotenv import load_dotenv

# 2. Configuration du répertoire de travail
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# 3. Chargement des variables d'environnement
load_dotenv()

# 4. Création de l'application Flask
template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'app', 'templates'))
app = Flask(__name__, template_folder=template_dir)

# 5. Enregistrement des routes
register_routes(app)
```

### 2. Initialisation des Routes (`app/routes.py`)
```python
# 1. Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / f"app_{datetime.now().strftime('%Y%m%d')}.log"),
        logging.StreamHandler()
    ]
)

# 2. Configuration de Vertex AI
vertexai.init(project=PROJECT_ID, location=LOCATION)
joke_model = GenerativeModel("gemini-2.0-flash-001")
```

### 3. Flux d'Exécution des Routes

#### Route `/` (Page d'accueil)
1. L'utilisateur accède à la page d'accueil
2. Flask appelle la fonction `index()`
3. Le template `home.html` est rendu
4. Les fichiers statiques (CSS, JS) sont chargés

#### Route `/joke` (Générateur de blagues)
1. L'utilisateur accède à la page des blagues
2. Flask appelle la fonction `joke_page()`
3. Le template `index.html` est rendu
4. Le JavaScript initialise l'interface

#### Route `/api/joke` (API de génération de blagues)
1. Le bouton "Générer une blague" est cliqué
2. Une requête AJAX est envoyée à `/api/joke`
3. Flask appelle la fonction `get_joke()`
4. Le modèle Gemini est utilisé pour générer une blague
5. La réponse est renvoyée au frontend
6. La blague est affichée dans l'interface

#### Route `/data` (Gestion des données)
1. L'utilisateur accède à la page des données
2. Flask appelle la fonction `read_data()`
3. Les données sont lues depuis Google Cloud Storage
4. Le template `data.html` est rendu avec les données

### 4. Utilisation des Services Google Cloud

#### Vertex AI (Gemini)
- Utilisé pour la génération de blagues
- Configuration via les credentials Google Cloud
- Modèle : `gemini-2.0-flash-001`

#### Cloud Storage
- Stockage des blagues favorites
- Configuration via les variables d'environnement
- Gestion des erreurs d'authentification

### 5. Gestion des Erreurs
- Logging des erreurs dans `logs/app_YYYYMMDD.log`
- Messages d'erreur explicites pour l'utilisateur
- Gestion des erreurs d'authentification Google Cloud
- Validation des entrées utilisateur

### 6. Structure des Templates
```
app/templates/
├── home.html      # Page d'accueil
├── index.html     # Générateur de blagues
├── data.html      # Affichage des données
├── status.html    # Page de statut
└── hello.html     # Page de test
```

### 7. Fichiers Statiques
```
app/static/
└── style.css      # Styles CSS de l'application
```

Cette structure permet une séparation claire des responsabilités :
- `main.py` : Point d'entrée de l'application
- `routes.py` : Définition des routes et logique métier
- `utils.py` : Fonctions utilitaires et interactions avec Google Cloud
- Templates : Interface utilisateur
- Static : Ressources statiques (CSS, JS)