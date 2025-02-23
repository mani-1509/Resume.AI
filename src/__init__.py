from flask import Flask
from .routes import routes
from .database import db
import os

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://resume_ai_vpnk_user:c5l3eADxjYrcIUyhw8t3seetjmDssDci@dpg-cut0cnggph6c73au868g-a.singapore-postgres.render.com/resume_ai_vpnk'
    app.config['SECRET_KEY'] = 'c5l3eADxjYrcIUyhw8t3seetjmDssDci'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    app.register_blueprint(routes)

    return app