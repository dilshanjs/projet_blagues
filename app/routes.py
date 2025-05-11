from flask import jsonify, request
import os
from app.utils import get_gcs_file, append_gcs_file
import vertexai
from vertexai.preview.generative_models import GenerativeModel

# Chargement des variables d'env
# (déjà fait si tu utilises python-dotenv dans main.py ou utils.py)

PROJECT_ID = os.getenv("PROJECT_ID")
LOCATION   = os.getenv("LOCATION")

# Initialisation Vertex AI avec le projet et la région
vertexai.init(project=PROJECT_ID, location=LOCATION)  # :contentReference[oaicite:0]{index=0}

# Chargement du modèle (ici Gemini 2.5 Pro Preview)
joke_model = GenerativeModel("gemini-2.5-pro-preview-05-06")  # :contentReference[oaicite:1]{index=1}

# ------------------------

def register_routes(app):
    @app.route("/hello", methods=["GET"])
    def hello():
        return jsonify({"message": "Bienvenue sur notre mini API GCP !"})

    @app.route("/status", methods=["GET"])
    def status():
        from datetime import datetime
        return jsonify({"server_time": datetime.now().isoformat()})

    @app.route("/data", methods=["GET"])
    def read_data():
        try:
            data = get_gcs_file()
            return jsonify(data)
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
    def get_joke():
        try:
            # Envoi de la requête au modèle
            response = joke_model.generate_content("Tell me a joke")  # :contentReference[oaicite:2]{index=2}

            # Récupération du texte de la première réponse
            joke_text = response.candidates[0].content.text
            return jsonify({"joke": joke_text})
        except Exception as e:
            return jsonify({"error": str(e)}), 500
