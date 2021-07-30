from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app(config_file):
    app = Flask(__name__)
    app.config.from_pyfile(config_file)
    db.init_app(app)
    with app.app_context():
        db.create_all()
        import routes
    return app