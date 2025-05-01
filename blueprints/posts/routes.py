import os
from flask import render_template, redirect, url_for, flash, request, current_app, abort
from flask_login import current_user, login_required
from app import db
from models import Post, Category, Tag, post_tags
from forms import PostForm, SearchForm, CategoryForm, TagForm
from utils import save_image, delete_image, parse_tags
from blueprints.posts import posts_bp

@posts_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    """Create a new blog post."""
    form = PostForm()

    # Populate category choices
    form.category.choices = [(0, 'Select a category')] + [
        (c.id, c.name) for c in Category.query.order_by(Category.name).all()
    ]

    if form.validate_on_submit():
        # Save image if uploaded
        image_path = None
        if form.image.data:
            image_path = save_image(form.image.data)

        # Create new post
        post = Post(
            title=form.title.data,
            content=form.content.data,
            author=current_user,
            category_id=form.category.data if form.category.data != 0 else None,
            image_path=image_path
        )

        # Process tags
        tag_names = parse_tags(form.tags.data)
        for tag_name in tag_names:
            # Check if tag exists, create if not
            tag = Tag.query.filter_by(name=tag_name).first()
            if not tag:
                tag = Tag(name=tag_name)
                db.session.add(tag)
            post.tags.append(tag)

        # Save to database
        db.session.add(post)
        db.session.commit()

        flash('Your post has been created!', 'success')
        return redirect(url_for('posts.view', post_id=post.id))

    return render_template('posts/create.html', title='Create Post', form=form)

@posts_bp.route('/<int:post_id>')
def view(post_id):
    """View a specific blog post."""
    post = Post.query.get_or_404(post_id)
    return render_template('posts/view.html', title=post.title, post=post)

@posts_bp.route('/<int:post_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(post_id):
    """Edit an existing blog post."""
    post = Post.query.get_or_404(post_id)

    # Check if current user is the author
    if post.author != current_user:
        abort(403)

    form = PostForm()

    # Populate category choices
    form.category.choices = [(0, 'Select a category')] + [
        (c.id, c.name) for c in Category.query.order_by(Category.name).all()
    ]

    if form.validate_on_submit():
        # Update post details
        post.title = form.title.data
        post.content = form.content.data
        post.category_id = form.category.data if form.category.data != 0 else None

        # Handle image upload
        if form.image.data:
            # Delete old image if exists
            if post.image_path:
                delete_image(post.image_path)

            # Save new image
            post.image_path = save_image(form.image.data)

        # Process tags
        # Clear existing tags
        post.tags = []

        # Add new tags
        tag_names = parse_tags(form.tags.data)
        for tag_name in tag_names:
            # Check if tag exists, create if not
            tag = Tag.query.filter_by(name=tag_name).first()
            if not tag:
                tag = Tag(name=tag_name)
                db.session.add(tag)
            post.tags.append(tag)

        # Save changes
        db.session.commit()

        flash('Your post has been updated!', 'success')
        return redirect(url_for('posts.view', post_id=post.id))

    # Pre-populate form fields when GET request
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
        form.category.data = post.category_id if post.category_id else 0
        form.tags.data = ', '.join([tag.name for tag in post.tags])

    return render_template('posts/edit.html', title='Edit Post', form=form, post=post)

@posts_bp.route('/<int:post_id>/delete', methods=['POST'])
@login_required
def delete(post_id):
    """Delete a blog post."""
    post = Post.query.get_or_404(post_id)

    # Check if current user is the author
    if post.author != current_user:
        abort(403)

    # Delete associated image
    if post.image_path:
        delete_image(post.image_path)

    # Delete post
    db.session.delete(post)
    db.session.commit()

    flash('Your post has been deleted!', 'success')
    return redirect(url_for('main.index'))

@posts_bp.route('/category/<int:category_id>')
def by_category(category_id):
    """View posts filtered by category."""
    page = request.args.get('page', 1, type=int)
    category = Category.query.get_or_404(category_id)

    # Get posts by category with pagination
    posts = Post.query.filter_by(category_id=category_id).order_by(
        Post.created_at.desc()
    ).paginate(
        page=page,
        per_page=current_app.config['POSTS_PER_PAGE'],
        error_out=False
    )

    return render_template('posts/list.html',
                           title=f'Posts in {category.name}',
                           posts=posts,
                           category=category)

@posts_bp.route('/tag/<int:tag_id>')
def by_tag(tag_id):
    """View posts filtered by tag."""
    page = request.args.get('page', 1, type=int)
    tag = Tag.query.get_or_404(tag_id)

    # Get posts by tag with pagination
    posts = tag.posts.order_by(Post.created_at.desc()).paginate(
        page=page,
        per_page=current_app.config['POSTS_PER_PAGE'],
        error_out=False
    )

    return render_template('posts/list.html',
                           title=f'Posts tagged with {tag.name}',
                           posts=posts,
                           tag=tag)

@posts_bp.route('/search', methods=['GET', 'POST'])
def search():
    """Search for posts by title, content, or category."""
    form = SearchForm()

    # Populate category choices
    form.category.choices = [(0, 'All Categories')] + [
        (c.id, c.name) for c in Category.query.order_by(Category.name).all()
    ]

    # Default page number
    page = request.args.get('page', 1, type=int)

    # Initialize query results
    posts = None
    search_query = request.args.get('query', '')
    category_id = request.args.get('category', 0, type=int)

    # If form is submitted through POST, redirect to GET with parameters
    if form.validate_on_submit():
        return redirect(url_for('posts.search',
                                query=form.query.data,
                                category=form.category.data))

    # If search parameters are in URL, process search
    if search_query:
        form.query.data = search_query
        form.category.data = category_id

        # Base query
        query = Post.query

        # Filter by search term
        if search_query:
            search_term = f'%{search_query}%'
            query = query.filter(
                (Post.title.ilike(search_term)) |
                (Post.content.ilike(search_term))
            )

        # Filter by category
        if category_id != 0:
            query = query.filter_by(category_id=category_id)

        # Order and paginate results
        posts = query.order_by(Post.created_at.desc()).paginate(
            page=page,
            per_page=current_app.config['POSTS_PER_PAGE'],
            error_out=False
        )

    return render_template('posts/search.html',
                           title='Search Posts',
                           form=form,
                           posts=posts,
                           query=search_query)

@posts_bp.route('/category/manage', methods=['GET', 'POST'])
@login_required
def manage_categories():
    """Manage categories (create, edit, view)."""
    form = CategoryForm()

    if form.validate_on_submit():
        # Check if category already exists
        existing = Category.query.filter_by(name=form.name.data).first()
        if existing:
            flash('A category with that name already exists.', 'warning')
        else:
            # Create new category
            category = Category(
                name=form.name.data,
                description=form.description.data
            )
            db.session.add(category)
            db.session.commit()
            flash('Category created successfully!', 'success')
            return redirect(url_for('posts.manage_categories'))

    # Get all categories
    categories = Category.query.order_by(Category.name).all()

    return render_template('posts/manage_categories.html',
                           title='Manage Categories',
                           form=form,
                           categories=categories)

@posts_bp.route('/category/<int:category_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_category(category_id):
    """Edit an existing category."""
    category = Category.query.get_or_404(category_id)
    form = CategoryForm()

    if form.validate_on_submit():
        # Check for duplicate name
        existing = Category.query.filter(
            Category.name == form.name.data,
            Category.id != category_id
        ).first()

        if existing:
            flash('A category with that name already exists.', 'warning')
        else:
            # Update category
            category.name = form.name.data
            category.description = form.description.data
            db.session.commit()
            flash('Category updated successfully!', 'success')
            return redirect(url_for('posts.manage_categories'))

    # Pre-populate form fields
    elif request.method == 'GET':
        form.name.data = category.name
        form.description.data = category.description

    return render_template('posts/edit_category.html',
                           title='Edit Category',
                           form=form,
                           category=category)

@posts_bp.route('/category/<int:category_id>/delete', methods=['POST'])
@login_required
def delete_category(category_id):
    """Delete a category."""
    category = Category.query.get_or_404(category_id)

    # Check if category has posts
    if category.posts.count() > 0:
        flash('Cannot delete category with posts. Reassign posts first.', 'danger')
    else:
        db.session.delete(category)
        db.session.commit()
        flash('Category deleted successfully!', 'success')

    return redirect(url_for('posts.manage_categories'))

@posts_bp.route('/tag/manage', methods=['GET', 'POST'])
@login_required
def manage_tags():
    """Manage tags (create, edit, view)."""
    form = TagForm()

    if form.validate_on_submit():
        # Check if tag already exists
        existing = Tag.query.filter_by(name=form.name.data).first()
        if existing:
            flash('A tag with that name already exists.', 'warning')
        else:
            # Create new tag
            tag = Tag(name=form.name.data)
            db.session.add(tag)
            db.session.commit()
            flash('Tag created successfully!', 'success')
            return redirect(url_for('posts.manage_tags'))

    # Get all tags
    tags = Tag.query.order_by(Tag.name).all()

    return render_template('posts/manage_tags.html',
                           title='Manage Tags',
                           form=form,
                           tags=tags)

@posts_bp.route('/tag/<int:tag_id>/delete', methods=['POST'])
@login_required
def delete_tag(tag_id):
    """Delete a tag."""
    tag = Tag.query.get_or_404(tag_id)

    # Remove tag from all posts
    db.session.delete(tag)
    db.session.commit()
    flash('Tag deleted successfully!', 'success')

    return redirect(url_for('posts.manage_tags'))
