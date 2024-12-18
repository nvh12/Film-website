from flask_mail import Mail, Message
from flask import render_template

mail = Mail()

def init(app):
    mail.init_app(app)

def send(code, recipients):
    content = render_template('email.html', code = code)
    try:
        msg = Message(
            subject = 'Account recovery',
            recipients = recipients,
            html = content
        )
        mail.send(msg)
        return "Email sent!"
    except Exception as e:
        return "Error! Please try again!"