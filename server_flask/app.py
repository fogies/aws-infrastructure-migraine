from flask import Flask
from flask_cors import CORS
from flask_json import FlaskJSON
import logging
import os

from users import users_blueprint


def create_app():
    # Our app.
    app = Flask(__name__)

    # For debugging.
    logging.basicConfig(level=logging.DEBUG)

    flask_environment = os.getenv("FLASK_ENV")
    if flask_environment == "production":
        from config.prod import ProductionConfig

        app.config.from_object(ProductionConfig())
    elif flask_environment == "development":
        from config.dev import DevelopmentConfig

        app.config.from_object(DevelopmentConfig())
    else:
        raise ValueError

    # Although ingress could provide CORS in production,
    # our development configuration also generates CORS requests.
    # Simple CORS wrapper of the application allows any and all requests.
    CORS(app)

    # Improved JSON support.
    FlaskJSON(app)

    # Register blue prints.
    # TODO - maybe move blue prints to their own folder if functions explode.
    app.register_blueprint(users_blueprint, url_prefix='/users')

    return app


# Instead of using `flask run`, import the app normally, then run it.
# Did this because `flask run` was eating an ImportError, not giving a useful error message.
if __name__ == '__main__':
    app = create_app()

    app.run(
        host=os.getenv('FLASK_RUN_HOST'),
        port=os.getenv('FLASK_RUN_PORT'),
    )
