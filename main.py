from flask import Flask
from app.routes import register_routes
from dotenv import load_dotenv


load_dotenv()

app = Flask(__name__)
register_routes(app)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
