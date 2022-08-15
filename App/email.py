from flask_mail import Message
from App import mail, app
from flask import render_template
from threading import Thread

def send_async_emial(app, msg):
    with app.app_context():
        mail.send(msg)

def send_email(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    Thread(target=send_async_emial, args=(app, msg)).start()  

def send_password_reset_email(user):
    token = user.get_reset_password_token()
    send_email("FPSOPedia - Reset Your Password",
                sender= app.config['MAIL_DEFAULT_SENDER'],
                recipients=[user.user_email],
                text_body=render_template('email/reset_password.txt', user=user, token=token),
                html_body=render_template('email/reset_password.html', user=user, token=token))