from config.base import Config
import migraine_shared.config

# Path is relative to server_flask
DEV_FLASK_CONFIG_PATH = "../secrets/configuration/dev_local_flask.yaml"


class DevelopmentConfig(Config):
    def __init__(self):
        flask_config = migraine_shared.config.FlaskConfig.load(DEV_FLASK_CONFIG_PATH)

        Config.__init__(
            self=self,
            secret_key=flask_config.secret_key,
            database_baseurl=flask_config.database_baseurl,
            database_admin_user=flask_config.database_admin_user,
            database_admin_password=flask_config.database_admin_password,
        )
