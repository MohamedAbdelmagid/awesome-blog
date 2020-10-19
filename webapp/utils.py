import os
import secrets
from threading import Thread
from datetime import datetime

from PIL import Image
from flask import render_template, current_app
from flask_mail import Message

from webapp import mail



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
    
    Thread(target=send_async_email, args=(current_app._get_current_object(), msg)).start()


# Method for informing the admins about an error by sending emails to all of them 
def tell_admin_with_error(subject, error):
    send_email(subject=subject,
            sender=current_app.config['MAIL_ADMIN'],
            recipients=current_app.config['ADMINS'],
            text_body=render_template('email/microsoft_translator_failure.txt', error=error),
            html_body=render_template('email/microsoft_translator_failure.html', error=error)
        )

# Method for converting the last_seen date to string time 
def get_last_seen(last_seen):
    now = datetime.utcnow()
    diff = now - last_seen
    seconds = diff.seconds
    days = diff.days

    if (days > 0):
        if (days == 1):
            return 'a day ago'
        return str(days + 1) + ' days ago'
    elif ((seconds > (60*60)) and (seconds < (60*60*24))):
        if (seconds % (60*60) == 0):
            return 'less than an hour ago'
        return str(int(seconds / (60*60) + 1)) + ' hours ago'
    elif ((seconds > 60) and (seconds < (60*60))):
        if (seconds % 60) == 0:
            return 'a minute ago'
        return str(int(seconds / 60) + 1) + ' minutes ago'
    elif ((seconds < 60) and (seconds > 5)):
        return  'a minute ago'
    else:
        return 'online'
