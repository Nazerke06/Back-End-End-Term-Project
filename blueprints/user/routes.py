from flask import render_template, redirect, url_for, flash, request, abort
from flask_login import current_user, login_required
from app import db
from models import User, Post
from forms import ProfileForm, PasswordChangeForm
from blueprints.user import user_bp

@user_bp.route('/profile/<username>')
def profile(username):
    """View a user's profile."""
    user = User.query.filter_by(username=username).first_or_404()

    # Get user's posts
    posts = Post.query.filter_by(author=user).order_by(
        Post.created_at.desc()
    ).all()

    return render_template('user/profile.html',
                           title=f'{user.username}\'s Profile',
                           user=user,
                           posts=posts)

@user_bp.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    """Edit current user's profile."""
    form = ProfileForm(original_username=current_user.username,
                       original_email=current_user.email)

    if form.validate_on_submit():
        # Update user profile
        current_user.username = form.username.data
        current_user.email = form.email.data
        current_user.bio = form.bio.data

        # Save changes
        db.session.commit()

        flash('Your profile has been updated!', 'success')
        return redirect(url_for('user.profile', username=current_user.username))

    # Pre-populate form fields
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
        form.bio.data = current_user.bio

    return render_template('user/edit_profile.html',
                           title='Edit Profile',
                           form=form)

@user_bp.route('/password/change', methods=['GET', 'POST'])
@login_required
def change_password():
    """Change current user's password."""
    form = PasswordChangeForm()

    if form.validate_on_submit():
        # Verify current password
        if not current_user.check_password(form.current_password.data):
            flash('Current password is incorrect.', 'danger')
            return redirect(url_for('user.change_password'))

        # Set new password
        current_user.set_password(form.new_password.data)
        db.session.commit()

        flash('Your password has been updated!', 'success')
        return redirect(url_for('user.profile', username=current_user.username))

    return render_template('user/change_password.html',
                           title='Change Password',
                           form=form)

@user_bp.route('/posts')
@login_required
def my_posts():
    """View current user's posts."""
    posts = Post.query.filter_by(author=current_user).order_by(
        Post.created_at.desc()
    ).all()

    return render_template('user/my_posts.html',
                           title='My Posts',
                           posts=posts)
