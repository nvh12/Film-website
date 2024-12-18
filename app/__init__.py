from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from config import Config
import app.email_sending

db = SQLAlchemy()
bcrypt = Bcrypt()
loginManager = LoginManager()

def create_app(config_class = Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    bcrypt.init_app(app)
    loginManager.init_app(app)
    email_sending.init(app)
    from . import routes
    app.register_blueprint(routes.main_bp)
    return app
    

