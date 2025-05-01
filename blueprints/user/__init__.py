from flask import Blueprint

user_bp = Blueprint('user', __name__, url_prefix='/user')

# Import routes at the bottom to avoid circular imports
from blueprints.user import routes
