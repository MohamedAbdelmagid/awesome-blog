import os
from dotenv import load_dotenv

from flask import Flask


basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

app = Flask(__name__)
app.config.from_object(os.environ.get('APP_SETTINGS'))

from webapp import routes