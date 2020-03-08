import os
import config
from dotenv import load_dotenv

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager


basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

app = Flask(__name__)

app.config.from_object(os.environ.get('APP_SETTINGS'))
# print some infomation regarding the app settings 
print('+++++\n' + str(os.environ.get('APP_SETTINGS')))
print('Database is ' + app.config['SQLALCHEMY_DATABASE_URI'] + '\n+++++\n')

db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)
login.login_view = 'login'

from webapp import routes, models