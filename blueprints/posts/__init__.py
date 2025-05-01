from flask import Blueprint

posts_bp = Blueprint('posts', __name__, url_prefix='/posts')

# Import routes at the bottom to avoid circular imports
from blueprints.posts import routes
