import os
from flask import Flask
from app.routes import register_routes
from dotenv import load_dotenv

# Forcer le répertoire de travail
os.chdir(os.path.dirname(os.path.abspath(__file__)))

load_dotenv()

# Création de l'application Flask avec le bon chemin pour les templates et les fichiers statiques
template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'app', 'templates'))
static_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'app', 'static'))
app = Flask(__name__, 
           template_folder=template_dir,
           static_folder=static_dir,
           static_url_path='/static')
register_routes(app)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
