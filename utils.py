import os
import uuid
from datetime import datetime
from flask import current_app
from werkzeug.utils import secure_filename

def allowed_file(filename):
    """Check if the file extension is allowed."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

def save_image(file):
    """Save the uploaded image and return the file path."""
    if file and allowed_file(file.filename):
        # Create a unique filename
        filename = secure_filename(file.filename)
        filename = f"{uuid.uuid4()}_{filename}"

        # Define upload path (inside static folder)
        upload_dir = os.path.join(current_app.root_path, current_app.config['UPLOAD_FOLDER'])

        # Ensure directory exists
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir)

        # Save the file
        file_path = os.path.join(upload_dir, filename)
        file.save(file_path)

        # Return the relative path to be stored in the database
        return os.path.join(current_app.config['UPLOAD_FOLDER'], filename).replace('\\', '/')

    return None

def delete_image(file_path):
    """Delete the image file from the filesystem."""
    if file_path:
        absolute_path = os.path.join(current_app.root_path, file_path)
        if os.path.exists(absolute_path):
            os.remove(absolute_path)
            return True

    return False

def format_date(date):
    """Format a datetime object to a readable string."""
    return date.strftime('%B %d, %Y at %I:%M %p')

def parse_tags(tags_string):
    """Parse a comma-separated string of tags and return a list of tag names."""
    if not tags_string:
        return []

    # Split by comma, strip whitespace, remove empty tags
    tag_names = [tag.strip() for tag in tags_string.split(',')]
    return [tag for tag in tag_names if tag]
