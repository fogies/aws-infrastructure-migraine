import ruamel.yaml


# Path is relative to server_flask
COUCHDB_CLIENT_CONFIG_PATH = "../secrets/client/couchdb_client_config.yaml"


class Config:
    # Expected by Flask
    SECRET_KEY: str = "SECRET_KEY"

    CLIENT_SECRET_KEY: str = "CLIENT_SECRET"

    URI_DATABASE: str
    DB_USER: str
    DB_PASSWORD: str

    def __init__(self):
        with open(COUCHDB_CLIENT_CONFIG_PATH) as file_couchdb_client_config:
            couchdb_client_config = ruamel.yaml.safe_load(file_couchdb_client_config)

        self.URI_DATABASE = couchdb_client_config["baseurl"]
        self.DB_USER = couchdb_client_config["admin"]["user"]
        self.DB_PASSWORD = couchdb_client_config["admin"]["password"]
