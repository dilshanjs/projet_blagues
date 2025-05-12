from flask import jsonify, request, render_template
import os
from app.utils import get_gcs_file, append_gcs_file
import vertexai
from vertexai.preview.generative_models import GenerativeModel
from pathlib import Path

# Chargement des variables d'env
# (déjà fait si tu utilises python-dotenv dans main.py ou utils.py)

PROJECT_ID = os.getenv("PROJECT_ID")
LOCATION   = os.getenv("LOCATION")

# Forcer le chemin des credentials
current_dir = Path(__file__).parent.parent
credentials_path = current_dir / "mini-projet-459407-943395c7a1f3.json"
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = str(credentials_path)

print(f"Using credentials from: {credentials_path}")
print(f"Credentials file exists: {credentials_path.exists()}")

# Initialisation Vertex AI avec le projet et la région
vertexai.init(project=PROJECT_ID, location=LOCATION)

# Chargement du modèle (ici Gemini 2.5 Pro Preview)
joke_model = GenerativeModel("gemini-2.5-pro-preview-05-06")

# ------------------------

def register_routes(app):
    @app.route("/")
    def index():
        print("Tentative d'accès à la page d'accueil")
        try:
            return render_template('home.html')
        except Exception as e:
            print(f"Erreur lors du rendu du template: {str(e)}")
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
        try:
            return render_template('index.html')
        except Exception as e:
            print(f"Erreur lors du rendu du template: {str(e)}")
            return str(e), 500

    @app.route("/api/joke", methods=["GET"])
    def get_joke():
        try:
            # Envoi de la requête au modèle
            response = joke_model.generate_content("Tell me a joke")

            # Récupération du texte de la première réponse
            joke_text = response.candidates[0].content.text
            return jsonify({"joke": joke_text})
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"Erreur détaillée : {error_details}")
            return jsonify({
                "error": str(e),
                "error_type": type(e).__name__,
                "error_details": error_details
            }), 500
