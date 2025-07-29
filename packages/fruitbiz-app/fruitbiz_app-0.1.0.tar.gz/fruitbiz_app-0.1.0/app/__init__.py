from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate

# After db = SQLAlchemy(app)


db = SQLAlchemy()
login_manager = LoginManager()

def create_app(template_folder=None, static_folder=None):
    app = Flask(__name__,template_folder=template_folder, static_folder=static_folder)
    app.config['SECRET_KEY'] = 'supersecret'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///fruitbiz.db'
    migrate = Migrate(app, db)
    db.init_app(app)
    login_manager.init_app(app)

    from .routes import main
    app.register_blueprint(main)

    # ⛔️ Avoid circular import by importing here
    from .models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    return app
