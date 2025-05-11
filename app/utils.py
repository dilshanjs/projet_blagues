import os, json
from dotenv import load_dotenv
from google.cloud import storage

load_dotenv()

BUCKET_NAME = os.getenv("BUCKET_NAME")
FILE_NAME   = os.getenv("FILE_NAME")

def get_gcs_file():
    client = storage.Client()
    bucket = client.bucket(BUCKET_NAME)
    blob   = bucket.blob(FILE_NAME)

    if not blob.exists():
        # Aucun fichier : on renvoie une liste vide
        return []

    content = blob.download_as_text()
    if not content.strip():
        # Fichier vide : on renvoie une liste vide
        return []

    try:
        return json.loads(content)
    except json.JSONDecodeError as e:
        # JSON malformé
        raise ValueError(
            f"Le contenu du fichier {FILE_NAME} n'est pas un JSON valide : {e}"
        )

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
