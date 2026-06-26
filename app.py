from flask import Flask
from flask_cors import CORS
from config import Config
from utils.extensions import bcrypt, jwt
from utils.db import db

app = Flask(__name__)
app.config.from_object(Config)

# Initialize extensions
CORS(app)
bcrypt.init_app(app)
jwt.init_app(app)

# Register Blueprints
from routes.auth_routes import auth_bp
from routes.api_routes import api_bp
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(api_bp, url_prefix='/api')

@app.route('/')
def home():
    return {"message": "Learning Path Dashboard API is running."}

if __name__ == '__main__':
    app.run(debug=True, port=app.config.get('PORT', 5000))

