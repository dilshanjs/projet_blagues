#!/usr/bin/env python3
import os
from dotenv import load_dotenv
import vertexai
from vertexai.preview.generative_models import GenerativeModel
from google.api_core.exceptions import NotFound, PermissionDenied

def main():
    # 1) Charge le .env (contenant GOOGLE_APPLICATION_CREDENTIALS, PROJECT_ID, LOCATION)
    load_dotenv()
    
    # 2) Récupère les variables
    cred_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    project_id = os.getenv("PROJECT_ID")
    location   = os.getenv("LOCATION")
    
    print(f"🔐 Credentials : {cred_path}")
    print(f"📦 Project ID  : {project_id}")
    print(f"🌐 Région     : {location}")
    
    if not all([cred_path, project_id, location]):
        print("❌ Vérifie que toutes les variables d'env sont définies dans ton .env")
        return

    # 3) Initialise Vertex AI
    try:
        vertexai.init(project=project_id, location=location)
        print("✅ Vertex AI initialisé")
    except Exception as e:
        print("❌ Erreur lors de l'initialisation de Vertex AI :", e)
        return

    # 4) Tente de charger un modèle disponible dans la région
    #    Adapte ici le nom du modèle si besoin (europe-west1 → gemini-2.0-flash-001, global/us-central1 → gemini-2.5-pro-preview-05-06)
    model_name = "gemini-2.0-flash-001"
    try:
        model = GenerativeModel(model_name)
        print(f"✅ Modèle {model_name} chargé")
    except NotFound:
        print(f"❌ Modèle {model_name} introuvable dans la région {location}")
        return
    except PermissionDenied:
        print("❌ Accès refusé : vérifie les permissions du service account")
        return
    except Exception as e:
        print("❌ Erreur lors du chargement du modèle :", e)
        return

    # 5) Envoie une requête test
    try:
        response = model.generate_content("Tell me a joke")
        # Selon version de la lib, soit response.text, soit response.candidates[0].content.text
        joke = getattr(response, "text", None) or response.candidates[0].content.text
        print("🤖 Blague générée :", joke)
    except Exception as e:
        print("❌ Erreur lors de l'appel au modèle :", e)

if __name__ == "__main__":
    main()
