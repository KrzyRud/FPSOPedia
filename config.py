import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or "JebacPIS"
    
    # SETTING UP THE DATABASE
    # SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL_1')
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
    
    SQLALCHEMY_TRACK_MODIFICATOR = False

    MAIL_SENDGRID_API_KEY = os.environ.get('MAIL_PASSWORD_1')

    # SETTING THE EMAIL
    MAIL_SERVER = os.environ.get('MAIL_SERVER_1')
    MAIL_PORT = 465
    MAIL_USE_TLS = False
    MAIL_USE_SSL = True
    MAIL_USERNAME_1 = os.environ.get('MAIL_USERNAME_1')
    MAIL_PASSWORD_1 = os.environ.get('MAIL_PASSWORD_1')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER')
    MAIL_MAX_EMAILS = None
    MAIL_SUPPRESS_SEND = False
    MAIL_ASCII_ATTACHMENTS = False