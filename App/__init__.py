from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_moment import Moment
from flask_mail import Mail

from config import Config

app = Flask(__name__)
app.config.from_object(Config)

# Setting up databese
db = SQLAlchemy(app)

# Setting up Migrate
migrate = Migrate(app, db)

# Setting up the Login Manager
login=LoginManager(app)
login.login_view = "login"

# Setting up the flask-moment
moment = Moment(app)

# Setting up the Mail service
mail = Mail(app)

from App import routes, models, forms, errors