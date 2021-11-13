from pathlib import Path
import ruamel.yaml
from typing import Union


class CouchDBClientConfig:
    """
    Parse configuration for clients of a CouchDB instance.
    """

    _baseurl: str
    _password: str
    _user: str

    def __init__(self, *, baseurl: str, user: str, password: str):
        self._baseurl = baseurl
        self._user = user
        self._password = password

    @staticmethod
    def load(couchdb_client_config_path: Union[Path, str]):
        couchdb_client_config_path = Path(couchdb_client_config_path)

        with open(couchdb_client_config_path) as config_file:
            yaml_config = ruamel.yaml.safe_load(config_file)

        return CouchDBClientConfig(
            baseurl=yaml_config["baseurl"],
            user=yaml_config["admin"]["user"],
            password=yaml_config["admin"]["password"],
        )

    @property
    def baseurl(self) -> str:
        return self._baseurl

    @property
    def password(self) -> str:
        return self._password

    @property
    def user(self) -> str:
        return self._user


class FlaskConfig:
    """
    Parse configuration for a Flask instance.
    """

    _secret_key: str
    _client_secret_key: str

    def __init__(self, *, secret_key: str, client_secret_key: str):
        self._secret_key = secret_key
        self._client_secret_key = client_secret_key

    @staticmethod
    def load(flask_config_path: Union[Path, str]):
        flask_config_path = Path(flask_config_path)

        with open(flask_config_path) as config_file:
            yaml_config = ruamel.yaml.safe_load(config_file)

        return FlaskConfig(
            secret_key=yaml_config["secret_key"],
            client_secret_key=yaml_config["client_secret_key"],
        )

    @property
    def client_secret_key(self) -> str:
        return self._client_secret_key

    @property
    def secret_key(self) -> str:
        return self._secret_key
