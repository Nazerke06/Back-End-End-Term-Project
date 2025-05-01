from flask import Blueprint

main_bp = Blueprint('main', __name__)

# Import routes at the bottom to avoid circular imports
from blueprints.main import routes
