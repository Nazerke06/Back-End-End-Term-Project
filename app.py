import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from flask_login import LoginManager
from werkzeug.middleware.proxy_fix import ProxyFix

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Create SQLAlchemy base class
class Base(DeclarativeBase):
    pass

# Initialize SQLAlchemy
db = SQLAlchemy(model_class=Base)

# Initialize login manager
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'info'

def create_app(config_class=None):
    """Factory pattern to create the Flask application."""
    # Create Flask app
    app = Flask(__name__)

    # Load configuration
    if config_class:
        app.config.from_object(config_class)
    else:
        from config import Config
        app.config.from_object(Config)

    # Ensure the secret key is set
    app.secret_key = os.environ.get("SESSION_SECRET", "dev_secret_key_for_local_development")

    # Configure ProxyFix
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

    # Initialize extensions with the app
    db.init_app(app)
    login_manager.init_app(app)

    # Import and register blueprints
    from blueprints.auth import auth_bp
    from blueprints.main import main_bp
    from blueprints.posts import posts_bp
    from blueprints.user import user_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(posts_bp)
    app.register_blueprint(user_bp)

    # Ensure upload directory exists
    upload_dir = os.path.join(app.static_folder, 'uploads')
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)

    # Setup database tables
    with app.app_context():
        # Import models to ensure they're registered with SQLAlchemy
        from models import User, Post, Category, Tag, post_tags

        # Create all tables
        db.create_all()

    return app
