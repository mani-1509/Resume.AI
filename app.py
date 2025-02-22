from flask import Flask
from src.database import db
from src.routes import routes
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://resume_ai_vpnk_user:c5l3eADxjYrcIUyhw8t3seetjmDssDci@dpg-cut0cnggph6c73au868g-a.singapore-postgres.render.com/resume_ai_vpnk'
app.config['SECRET_KEY'] = os.getenv('sql_database_Key')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
app.register_blueprint(routes)

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run()
