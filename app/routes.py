from flask import jsonify, request, render_template
import os
from app.utils import get_gcs_file, append_gcs_file, setup_credentials
from google.cloud import aiplatform
from vertexai.preview.generative_models import GenerativeModel
from pathlib import Path
import logging
from datetime import datetime
import json
from google.oauth2 import service_account
import random

# Configuration du logging
log_dir = Path(__file__).parent.parent / "logs"
log_dir.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / f"app_{datetime.now().strftime('%Y%m%d')}.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('app_routes')

# Configuration des variables d'environnement
PROJECT_ID = os.getenv("PROJECT_ID", "mini-projet-459407")
LOCATION = "europe-west1"
os.environ["LOCATION"] = LOCATION
os.environ["GOOGLE_CLOUD_LOCATION"] = LOCATION
os.environ["CLOUD_ML_REGION"] = LOCATION

# Configuration des credentials
credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "/app/mini-projet-459407-5eeaa3b13b0e.json")

if not os.path.exists(credentials_path):
    raise FileNotFoundError(f"Le fichier de credentials n'existe pas: {credentials_path}")

# Vérification des credentials
if not setup_credentials():
    logger.error("Les credentials ne sont pas correctement configurés")

try:
    # Initialisation de Vertex AI
    credentials = service_account.Credentials.from_service_account_file(
        credentials_path,
        scopes=["https://www.googleapis.com/auth/cloud-platform"]
    )
    
    aiplatform.init(
        project=PROJECT_ID,
        location=LOCATION,
        credentials=credentials
    )
    
    # Chargement du modèle
    joke_model = GenerativeModel("gemini-2.0-flash-001")
    logger.info("Modèle Gemini chargé avec succès")
except Exception as e:
    logger.error(f"Erreur lors de l'initialisation de Vertex AI: {str(e)}")
    joke_model = None

def register_routes(app):
    @app.route("/")
    def index():
        return render_template('home.html')

    @app.route("/hello", methods=["GET"])
    def hello():
        if request.headers.get('Accept') == 'application/json':
            return jsonify({"message": "Bienvenue sur notre mini API GCP !"})
        return render_template('hello.html')

    @app.route("/status", methods=["GET"])
    def status():
        if request.headers.get('Accept') == 'application/json':
            return jsonify({"server_time": datetime.now().isoformat()})
        return render_template('status.html')

    @app.route("/data", methods=["GET"])
    def read_data():
        try:
            data = get_gcs_file()
            if request.headers.get('Accept') == 'application/json':
                return jsonify(data)
            return render_template('data.html')
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route("/data", methods=["POST"])
    def write_data():
        try:
            new_entry = request.get_json()
            result = append_gcs_file(new_entry)
            return jsonify(result)
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route("/joke", methods=["GET"])
    def joke_page():
        return render_template('index.html')

    @app.route("/api/joke", methods=["GET"])
    def get_joke():
        try:
            if joke_model is None:
                return jsonify({
                    "error": "Le modèle n'est pas disponible",
                    "error_type": "ModelNotInitialized"
                }), 500

            # Liste de thèmes pour les blagues
            themes = [
                "animaux", "restaurant", "école", "travail", "vacances", 
                "sport", "technologie", "musique", "cinéma", "cuisine",
                "voyage", "famille", "amitié", "amour", "argent"
            ]
            
            # Liste de styles pour les blagues
            styles = [
                "jeu de mots", "situation absurde", "quiproquo", 
                "ironie", "exagération", "contrepèterie"
            ]
            
            # Sélection aléatoire d'un thème et d'un style
            theme = random.choice(themes)
            style = random.choice(styles)
            
            # Exemples de blagues drôles
            example_jokes = """
            Voici des exemples de blagues drôles :
            - Pourquoi les plongeurs plongent-ils toujours en arrière et jamais en avant ? Parce que sinon ils tombent dans le bateau.
            - J'ai demandé à un escargot quel était son plat préféré. Il m'a répondu : « La salade, bien sûr, c'est rapide à préparer ! »
            - Si deux vegans se disputent, est-ce qu'on peut appeler ça une prise de tofu ?
            - Mon chien sait faire du kung-fu... mais seulement quand personne ne regarde.
            - Quel est le comble pour un électricien ? De ne pas être au courant.
            - Que fait une fraise sur un cheval ? Tagada tagada !
            """
            
            # Construction du prompt
            prompt = f"""Crée une blague drôle en français sur le thème '{theme}' en utilisant un style de '{style}'. 
            La blague doit être courte, percutante et dans le même style que ces exemples :
            {example_jokes}
            Ta blague doit être dans le même style que ces exemples, avec un jeu de mots ou une situation absurde."""
            
            try:
                generation_config = {
                    "temperature": 0.95,
                    "top_p": 0.9,
                    "top_k": 40
                }
                
                response = joke_model.generate_content(
                    prompt,
                    generation_config=generation_config
                )
                
                if not response or not response.candidates:
                    return jsonify({
                        "error": "Le modèle n'a pas généré de réponse",
                        "error_type": "EmptyResponse"
                    }), 500

                # Nettoyage de la réponse
                joke_text = response.candidates[0].content.text
                # Suppression uniquement des caractères spéciaux indésirables
                # On garde la ponctuation : . , ; : ! ? ' " ( )
                joke_text = joke_text.replace('>', '').replace('<', '')
                joke_text = joke_text.replace('*', '').replace('^', '').replace('$', '')
                joke_text = joke_text.replace('`', '').replace('~', '').replace('|', '')
                joke_text = joke_text.replace('{', '').replace('}', '').replace('[', '').replace(']', '')
                joke_text = joke_text.replace('\\', '').replace('/', '')
                # Suppression des espaces multiples
                joke_text = " ".join(joke_text.split())
                
                return jsonify({"joke": joke_text})
                
            except Exception as model_error:
                return jsonify({
                    "error": "Erreur lors de l'appel au modèle",
                    "error_type": type(model_error).__name__,
                    "details": str(model_error)
                }), 500
                
        except Exception as e:
            return jsonify({
                "error": str(e),
                "error_type": type(e).__name__
            }), 500
