import os
import secrets
from PIL import Image
from flask import url_for, current_app as app
from flask_mail import Message # type: ignore
from flask_login import current_user # type: ignore
from blogapp import mail

def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)
    
    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)
    
    prev_picture = os.path.join(app.root_path, 'static/profile_pics', current_user.image_file)
    if os.path.exists(prev_picture) and os.path.basename(prev_picture) != 'default.jpg':
        os.remove(prev_picture)
        
    return picture_fn

def delete_picture(picture_file, directory='static/profile_pics'):
    picture_path = os.path.join(app.root_path, directory, picture_file)
    if os.path.exists(picture_path) and os.path.basename(picture_path) != 'default.jpg':
        os.remove(picture_path)

def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request', sender = 'noreply@demo.com', recipients=[user.email])
    msg.body = f'''To reset your password, visit the following link:
{url_for('users.reset_token', token=token, _external=True)}

If you did not make this request, ignore this email.
'''
    mail.send(msg)

