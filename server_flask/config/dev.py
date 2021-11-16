from config.base import Config
import migraine_shared.config

# Path is relative to server_flask
COUCHDB_CLIENT_CONFIG_PATH = "../secrets/client/couchdb_client_config.yaml"
# Path is relative to server_flask
FLASK_CONFIG_PATH = "../secrets/configuration/flask_config.yaml"


class DevelopmentConfig(Config):
    def __init__(self):
        couchdb_client_config = migraine_shared.config.CouchDBClientConfig.load(COUCHDB_CLIENT_CONFIG_PATH)
        flask_config = migraine_shared.config.FlaskConfig.load(FLASK_CONFIG_PATH)

        Config.__init__(
            self=self,
            secret_key=flask_config.secret_key,
            client_secret_key=flask_config.client_secret_key,
            db_baseurl=couchdb_client_config.baseurl,
            db_admin_user=couchdb_client_config.user,
            db_admin_password=couchdb_client_config.password,
        )
