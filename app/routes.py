from flask import jsonify, request, render_template
import os
from app.utils import get_gcs_file, append_gcs_file, setup_credentials
import vertexai
from vertexai.preview.generative_models import GenerativeModel
from pathlib import Path
import logging
from datetime import datetime
import random

# Configuration du logging
log_dir = Path(__file__).parent.parent / "logs"
log_dir.mkdir(exist_ok=True)

# Configuration du logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / f"app_{datetime.now().strftime('%Y%m%d')}.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('app_routes')

# Chargement des variables d'env
# (déjà fait si tu utilises python-dotenv dans main.py ou utils.py)

PROJECT_ID = os.getenv("PROJECT_ID", "mini-projet-459407")
LOCATION = os.getenv("LOCATION", "us-central1")

# Configuration des credentials
credentials_path = "C:/Users/dilsh/Documents/Credentials/mini-projet-459407-5eeaa3b13b0e.json"
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path

print(f"Using credentials from: {credentials_path}")
print(f"Credentials file exists: {os.path.exists(credentials_path)}")

# Vérification des credentials
if not setup_credentials():
    logger.error("Les credentials ne sont pas correctement configurés")

try:
    logger.info("Initialisation de Vertex AI")
    vertexai.init(project=PROJECT_ID, location=LOCATION)
    logger.info("Vertex AI init réussi")
    
    # Chargement du modèle avec le nom correct
    joke_model = GenerativeModel("gemini-2.0-flash-001")
    logger.info("Modèle Gemini chargé avec succès")
except Exception as e:
    logger.error(f"Erreur lors de l'initialisation de Vertex AI: {str(e)}")
    joke_model = None

# ------------------------

def register_routes(app):
    @app.route("/")
    def index():
        logger.info("Accès à la page d'accueil")
        try:
            return render_template('home.html')
        except Exception as e:
            logger.error(f"Erreur lors du rendu du template: {str(e)}")
            return str(e), 500

    @app.route("/hello", methods=["GET"])
    def hello():
        if request.headers.get('Accept') == 'application/json':
            return jsonify({"message": "Bienvenue sur notre mini API GCP !"})
        return render_template('hello.html')

    @app.route("/status", methods=["GET"])
    def status():
        from datetime import datetime
        if request.headers.get('Accept') == 'application/json':
            return jsonify({"server_time": datetime.now().isoformat()})
        return render_template('status.html')

    @app.route("/data", methods=["GET"])
    def read_data():
        try:
            print("Variables d'environnement :")
            print(f"GOOGLE_APPLICATION_CREDENTIALS : {os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')}")
            print(f"BUCKET_NAME : {os.environ.get('BUCKET_NAME')}")
            print(f"FILE_NAME : {os.environ.get('FILE_NAME')}")
            
            data = get_gcs_file()
            if request.headers.get('Accept') == 'application/json':
                return jsonify(data)
            return render_template('data.html')
        except Exception as e:
            print(f"ERREUR dans /data : {str(e)}")
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
        try:
            return render_template('index.html')
        except Exception as e:
            print(f"Erreur lors du rendu du template: {str(e)}")
            return str(e), 500

    @app.route("/api/joke", methods=["GET"])
    def get_joke():
        try:
            logger.info("Génération d'une blague")
            # Liste de différents types de blagues avec plus de variété
            prompts = [
                "Raconte-moi une blague drôle en français sur la vie quotidienne",
                "Génère une blague courte et amusante en français sur le travail",
                "Fais-moi rire avec une blague en français sur les animaux",
                "Donne-moi une blague originale en français sur la technologie",
                "Crée une blague marrante en français sur la cuisine",
                "Invente une blague en français sur les voyages",
                "Partage une blague drôle en français sur l'école",
                "Écris une blague humoristique en français sur le sport",
                "Raconte une blague en français sur les relations",
                "Génère une blague en français sur la météo",
                "Crée une blague en français sur les transports",
                "Invente une blague en français sur les loisirs"
            ]
            prompt = random.choice(prompts)
            
            # Configuration de la génération avec des paramètres optimisés pour la variété
            generation_config = {
                "temperature": 0.95,  # Très proche du maximum pour plus de créativité
                "top_p": 0.95,       # Augmentation significative de la diversité
                
            }
            
            response = joke_model.generate_content(
                prompt,
                generation_config=generation_config
            )
            joke_text = response.candidates[0].content.text
            logger.info("Blague générée avec succès")
            return jsonify({"joke": joke_text})
        except Exception as e:
            logger.error(f"Erreur lors de la génération de la blague: {str(e)}")
            return jsonify({
                "error": str(e),
                "error_type": type(e).__name__
            }), 500
