import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or "JebacPIS"
    
    # SETTING UP THE DATABASE
    SQLALCHEMY_DATABASE_URI = 'postgresql://tmxpoqdhixpwse:3fd312a8ee455ef8b14a684b8e2f576efcd1b9b4b87dd76c4947db9ced87a755@ec2-44-205-112-253.compute-1.amazonaws.com:5432/degj1vngc2c20l'
    #   or 'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATOR = False

    # SETTING THE EMAIL
    MAIL_SERVER = 'fpsopedia.atthost24.pl'
    MAIL_PORT = 465
    MAIL_USE_TLS = False
    MAIL_USE_SSL = True
    MAIL_USERNAME = 'info@fpsopedia.com'
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD_1')
    MAIL_DEFAULT_SENDER = 'info@fpsopedia.com'
    MAIL_MAX_EMAILS = None
    MAIL_SUPPRESS_SEND = False
    MAIL_ASCII_ATTACHMENTS = False