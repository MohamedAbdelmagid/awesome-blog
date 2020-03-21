from flask import render_template, current_app
from webapp.utils import send_email


# Method for sending password reset email 
def send_password_reset_email(user):
    token = user.get_reset_password_token()
    send_email('Reset Your Password [Awesome Blog]',
        sender=current_app.config['MAIL_ADMIN'],
        recipients=[user.email],
        text_body=render_template('email/reset_password.txt', user=user, token=token),
        html_body=render_template('email/reset_password.html', user=user, token=token)
    )
