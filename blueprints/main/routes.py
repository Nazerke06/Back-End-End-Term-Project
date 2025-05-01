from flask import render_template, request, current_app
from flask_login import current_user
from datetime import datetime
from models import Post, Category
from blueprints.main import main_bp

@main_bp.route('/')
@main_bp.route('/index')
def index():
    """Render the home page with recent posts."""
    page = request.args.get('page', 1, type=int)

    # Get recent posts with pagination
    posts = Post.query.order_by(Post.created_at.desc()).paginate(
        page=page,
        per_page=current_app.config['POSTS_PER_PAGE'],
        error_out=False
    )

    # Get categories for sidebar
    categories = Category.query.all()

    return render_template('index.html',
                           title='Home',
                           posts=posts,
                           categories=categories)

@main_bp.route('/about')
def about():
    """Render the about page."""
    return render_template('main/about.html', title='About')

@main_bp.context_processor
def inject_categories():
    """Inject categories into all templates."""
    categories = Category.query.all()
    return dict(categories=categories)

@main_bp.context_processor
def inject_year():
    """Inject current year into all templates."""
    return dict(current_year=datetime.now().year)
