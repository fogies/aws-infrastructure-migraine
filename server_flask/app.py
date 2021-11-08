import io
import json
import logging
import os
import sys
from pathlib import Path
from urllib.parse import urljoin

import requests
from flask import Flask, current_app, request
from flask_cors import CORS
from flask_json import FlaskJSON, as_json
from markupsafe import escape
from users import users_blueprint


def create_app():
    app = Flask(__name__)

    # For debugging.
    logging.basicConfig(level=logging.DEBUG)

    flask_environment = os.getenv("FLASK_ENV")
    if flask_environment == "production":
        from config.prod import Config

        app.config.from_object(Config())
    elif flask_environment == "development":
        from config.dev import Config

        app.config.from_object(Config())
    else:
        raise ValueError

    # Although ingress could provide CORS in production,
    # our development configuration also generates CORS requests.
    # Simple CORS wrapper of the application allows any and all requests.
    CORS(app)
    FlaskJSON(app)

    # Register blue prints.
    # TODO - maybe move blue prints to their own folder if functions explode.
    app.register_blueprint(users_blueprint, url_prefix='/users')

    return app
