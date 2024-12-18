from credentials import mail_username, mail_password

class Config:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///Database.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = '2a0f76e24979a57e'

    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    
    MAIL_USERNAME = mail_username
    MAIL_PASSWORD = mail_password
    MAIL_DEFAULT_SENDER = mail_username