import os, json
from dotenv import load_dotenv
from google.cloud import storage
from pathlib import Path
import logging
from datetime import datetime

# Configuration du logging
log_dir = Path(__file__).parent.parent / "logs"
log_dir.mkdir(exist_ok=True)

# Configuration du logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / f"gcs_{datetime.now().strftime('%Y%m%d')}.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('gcs_operations')

# Chargement du .env depuis le répertoire du projet
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(env_path)

BUCKET_NAME = os.getenv("BUCKET_NAME")
FILE_NAME   = os.getenv("FILE_NAME")

def setup_credentials():
    """Configure les credentials Google Cloud de manière centralisée."""
    try:
        credentials_path = Path(__file__).parent.parent / "mini-projet-459407-5eeaa3b13b0e.json"
        if credentials_path.exists():
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = str(credentials_path)
            logger.info(f"Credentials configurés depuis : {credentials_path}")
            return True
        else:
            logger.error(f"Fichier de credentials non trouvé à : {credentials_path}")
            return False
    except Exception as e:
        logger.error(f"Erreur lors de la configuration des credentials: {str(e)}")
        return False

def get_gcs_file():
    try:
        # Afficher le chemin des credentials
        credentials_path = os.path.join(os.getcwd(), "mini-projet-459407-5eeaa3b13b0e.json")
        print(f"Chemin des credentials : {credentials_path}")
        print(f"Le fichier existe : {os.path.exists(credentials_path)}")
        
        # Vérifier le contenu des credentials
        if os.path.exists(credentials_path):
            with open(credentials_path, 'r') as f:
                import json
                creds = json.load(f)
                print(f"Project ID dans les credentials : {creds.get('project_id')}")
                print(f"Client Email dans les credentials : {creds.get('client_email')}")
        
        # Configurer les credentials
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path
        
        # Tenter la connexion
        print("Tentative de connexion à GCS...")
        client = storage.Client()
        print("Connexion à GCS réussie")
        
        bucket = client.bucket(BUCKET_NAME)
        print(f"Bucket trouvé : {BUCKET_NAME}")
        
        blob = bucket.blob(FILE_NAME)
        print(f"Blob trouvé : {FILE_NAME}")
        
        if not blob.exists():
            print(f"Le fichier {FILE_NAME} n'existe pas")
            return []
            
        content = blob.download_as_text()
        print("Contenu téléchargé avec succès")
        
        if not content.strip():
            print("Le fichier est vide")
            return []
            
        return json.loads(content)
        
    except Exception as e:
        print(f"ERREUR DÉTAILLÉE : {str(e)}")
        print(f"Type d'erreur : {type(e).__name__}")
        import traceback
        print(f"Traceback complet : {traceback.format_exc()}")
        raise

def append_gcs_file(new_entry):
    client = storage.Client()
    bucket = client.bucket(BUCKET_NAME)
    blob   = bucket.blob(FILE_NAME)

    if not blob.exists():
        data = []
    else:
        content = blob.download_as_text()
        if not content.strip():
            data = []
        else:
            try:
                data = json.loads(content)
            except json.JSONDecodeError as e:
                raise ValueError(
                    f"Le contenu du fichier {FILE_NAME} n'est pas un JSON valide : {e}"
                )

    if not isinstance(data, list):
        raise ValueError("Le fichier JSON doit être une liste d'objets.")

    data.append(new_entry)
    blob.upload_from_string(
        json.dumps(data, indent=2),
        content_type="application/json"
    )
    return {"message": "Entrée ajoutée avec succès.", "total_entries": len(data)}
