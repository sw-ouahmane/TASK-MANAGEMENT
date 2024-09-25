from flask import Flask
from flask_login import LoginManager
from .config import Config
from .models import db
from flask_migrate import Migrate
from .utils import create_default_admin
import os


# Initialize Flask-Login
login_manager = LoginManager()
login_manager.login_view = 'auth.login'  # Ensure this matches your login route


def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)
    migrate = Migrate(app, db)
    login_manager.init_app(app)

    # Register blueprints
    from .routes.auth import bp as auth_bp
    from .routes.admin import bp as admin_bp
    from .routes.main import bp as main_bp
    from .routes.tasks import bp as tasks_bp
    from .routes.user import bp as user_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(tasks_bp)
    app.register_blueprint(user_bp)

    # Define user loader
    from .models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Create default admin
    with app.app_context():
        # Be cautious with these lines in production
        """

        db.drop_all()
        db.create_all()
        """

        create_default_admin()

    return app
