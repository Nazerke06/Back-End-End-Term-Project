import os

class Config:
    """Base configuration class for the application."""
    # Set secret key from environment variable
    SECRET_KEY = os.environ.get("SESSION_SECRET")
    
    # Database configuration
    # Use SQLite by default if DATABASE_URL is not provided
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", 'sqlite:///blog.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # Engine options are only needed for PostgreSQL, not for SQLite
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_recycle": 300,
        "pool_pre_ping": True,
    } if os.environ.get("DATABASE_URL") else {}
    
    # File uploads configuration
    UPLOAD_FOLDER = 'static/uploads'
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max upload size
    
    # Session configuration
    SESSION_TYPE = 'filesystem'
    PERMANENT_SESSION_LIFETIME = 1800  # 30 minutes
    
    # Pagination settings
    POSTS_PER_PAGE = 10
