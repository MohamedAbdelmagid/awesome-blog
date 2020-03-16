import os
import secrets
from threading import Thread

from PIL import Image
from flask import render_template
from flask_mail import Message

from webapp import app, mail



# Method for randomise image's name and save in the static/pic file 
def store_image(form_image):
    # Get a random hex 
    random_hex = secrets.token_hex(8)
    # Get the extention of the pic file and concatenate it the hex
    _, f_ext = os.path.splitext(form_image.filename)
    image_fn = random_hex + f_ext
    # Make a path to the static/pics directory
    image_path = os.path.join(app.root_path, 'static/pics', image_fn)

    # Resize the image before saving it
    output_size = (125, 125)
    image = Image.open(form_image)
    image.thumbnail(output_size)
    image.save(image_path)

    return image_fn


def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)

# Method for sending email from a sender to many recipients 
def send_email(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    
    Thread(target=send_async_email, args=(app, msg)).start()

# Method for sending password reset email 
def send_password_reset_email(user):
    token = user.get_reset_password_token()
    send_email('Reset Your Password [Awesome Blog]',
        sender=app.config['ADMINS'][0],
        recipients=[user.email],
        text_body=render_template('email/reset_password.txt', user=user, token=token),
        html_body=render_template('email/reset_password.html', user=user, token=token)
    )