from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from controllers.home import home_bp
from controllers.auth import auth_bp
from controllers.dashboard import dashboard_bp
from controllers.api import api_bp
from config import Config
from models import db 

# Configurações
app = Flask(__name__, template_folder='views', static_folder='static')
app.config.from_object(Config)
db.init_app(app)

# Registrando os Blueprints
app.register_blueprint(home_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(api_bp)

# Iniciar
if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Cria as tabelas no banco de dados se não existirem
    app.run(host='0.0.0.0', port=5000)
