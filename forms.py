from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, SelectField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from models import User

class RegistrationForm(FlaskForm):
    """Form for user registration."""
    username = StringField('Username', validators=[
        DataRequired(),
        Length(min=3, max=64)
    ])
    email = StringField('Email', validators=[
        DataRequired(),
        Email(),
        Length(max=120)
    ])
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=8, max=128)
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(),
        EqualTo('password')
    ])
    submit = SubmitField('Register')

    def validate_username(self, username):
        """Check if username is already taken."""
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username is already taken. Please choose a different one.')

    def validate_email(self, email):
        """Check if email is already registered."""
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email is already registered. Please use a different one.')

class LoginForm(FlaskForm):
    """Form for user login."""
    email = StringField('Email', validators=[
        DataRequired(),
        Email()
    ])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Login')

class PostForm(FlaskForm):
    """Form for creating and editing blog posts."""
    title = StringField('Title', validators=[
        DataRequired(),
        Length(min=3, max=200)
    ])
    content = TextAreaField('Content', validators=[DataRequired()])
    category = SelectField('Category', coerce=int)
    tags = StringField('Tags (comma separated)', validators=[Length(max=200)])
    image = FileField('Upload Image (Optional)', validators=[
        FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Images only!')
    ])
    submit = SubmitField('Submit')

class CategoryForm(FlaskForm):
    """Form for creating and editing categories."""
    name = StringField('Name', validators=[
        DataRequired(),
        Length(min=2, max=50)
    ])
    description = StringField('Description', validators=[Length(max=200)])
    submit = SubmitField('Submit')

class TagForm(FlaskForm):
    """Form for creating and editing tags."""
    name = StringField('Name', validators=[
        DataRequired(),
        Length(min=2, max=50)
    ])
    submit = SubmitField('Submit')

class SearchForm(FlaskForm):
    """Form for searching posts."""
    query = StringField('Search', validators=[DataRequired()])
    category = SelectField('Category', coerce=int, validators=[])
    submit = SubmitField('Search')

class ProfileForm(FlaskForm):
    """Form for editing user profile."""
    username = StringField('Username', validators=[
        DataRequired(),
        Length(min=3, max=64)
    ])
    email = StringField('Email', validators=[
        DataRequired(),
        Email(),
        Length(max=120)
    ])
    bio = TextAreaField('Bio', validators=[Length(max=500)])
    submit = SubmitField('Update Profile')

    def __init__(self, original_username, original_email, *args, **kwargs):
        super(ProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username
        self.original_email = original_email

    def validate_username(self, username):
        """Check if username is already taken, excluding the current user."""
        if username.data != self.original_username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('Username is already taken. Please choose a different one.')

    def validate_email(self, email):
        """Check if email is already registered, excluding the current user."""
        if email.data != self.original_email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('Email is already registered. Please use a different one.')

class PasswordChangeForm(FlaskForm):
    """Form for changing user password."""
    current_password = PasswordField('Current Password', validators=[DataRequired()])
    new_password = PasswordField('New Password', validators=[
        DataRequired(),
        Length(min=8, max=128)
    ])
    confirm_new_password = PasswordField('Confirm New Password', validators=[
        DataRequired(),
        EqualTo('new_password')
    ])
    submit = SubmitField('Change Password')

