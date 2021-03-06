# coding=utf-8
from flask import Flask
from config import config
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from flask_login import LoginManager
from flask_admin import Admin

mail = Mail()
db = SQLAlchemy()
bootstrap = Bootstrap()
admin = Admin()

login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'auth.login'

app = Flask(__name__)
app.config.from_object(config["default"])

config["default"].init_app(app)
mail.init_app(app)
db.init_app(app)
bootstrap.init_app(app)
login_manager.init_app(app)
admin.init_app(app)

from .main import main as main_blueprint
app.register_blueprint(main_blueprint)

from .auth import auth as auth_blueprint
app.register_blueprint(auth_blueprint)
