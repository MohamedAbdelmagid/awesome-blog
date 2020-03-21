from flask import Blueprint

auth_blueprint = Blueprint('auth', __name__)

from webapp.auth import routes