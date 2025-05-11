import os
from google.cloud import storage
from dotenv import load_dotenv

load_dotenv()  # Charge les variables d'environnement depuis .env

def test_gcs_connection():
    try:
        # Charge le nom du bucket depuis l'environnement
        bucket_name = os.getenv("BUCKET_NAME")

        # Initialise le client avec les identifiants du compte de service
        client = storage.Client()
        bucket = client.get_bucket(bucket_name)

        print(f"✅ Connexion réussie au bucket : {bucket_name}")
        print("📂 Fichiers dans le bucket :")
        for blob in bucket.list_blobs():
            print(" -", blob.name)
    except Exception as e:
        print("❌ Erreur lors de la connexion à GCS :", e)

if __name__ == "__main__":
    test_gcs_connection()
