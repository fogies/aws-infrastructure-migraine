from pathlib import Path
import ruamel.yaml
from typing import Union


class CouchDBConfig:
    """
    Parse configuration for clients of a CouchDB instance.
    """

    _admin_password: str
    _admin_user: str
    _baseurl: str
    _cookie_auth_secret: str
    _uuid: str

    def __init__(
        self,
        *,
        baseurl: str,
        admin_user: str,
        admin_password: str,
        cookie_auth_secret: str,
        uuid: str,
    ):
        self._baseurl = baseurl
        self._admin_user = admin_user
        self._admin_password = admin_password
        self._cookie_auth_secret = cookie_auth_secret
        self._uuid = uuid

    @staticmethod
    def load(couchdb_client_config_path: Union[Path, str]):
        couchdb_client_config_path = Path(couchdb_client_config_path)

        with open(couchdb_client_config_path) as config_file:
            yaml = ruamel.yaml.YAML(typ="safe", pure=True)
            yaml_config = yaml.load(config_file)

        return CouchDBConfig.parse(yaml_config)

    @staticmethod
    def parse(yaml_config: dict):

        return CouchDBConfig(
            baseurl=yaml_config["baseurl"],
            admin_user=yaml_config["admin"]["user"],
            admin_password=yaml_config["admin"]["password"],
            cookie_auth_secret=yaml_config["cookieAuthSecret"],
            uuid=yaml_config["uuid"]
        )

    @property
    def admin_password(self) -> str:
        return self._admin_password

    @property
    def admin_user(self) -> str:
        return self._admin_user

    @property
    def baseurl(self) -> str:
        return self._baseurl

    @property
    def cookie_auth_secret(self) -> str:
        return self._cookie_auth_secret

    @property
    def uuid(self) -> str:
        return self._uuid


class FlaskConfig:
    """
    Parse configuration for a Flask instance.
    """

    _base_url: str
    _secret_key: str

    _database_baseurl: str
    _database_admin_password: str
    _database_admin_user: str


    def __init__(
        self,
        *,
        baseurl: str,
        secret_key: str,
        database_baseurl: str,
        database_admin_user: str,
        database_admin_password: str,
    ):
        self._base_url = baseurl
        self._secret_key = secret_key
        self._database_baseurl = database_baseurl
        self._database_admin_user = database_admin_user
        self._database_admin_password = database_admin_password

    @staticmethod
    def load(flask_config_path: Union[Path, str]):
        flask_config_path = Path(flask_config_path)

        with open(flask_config_path) as config_file:
            yaml = ruamel.yaml.YAML(typ="safe", pure=True)
            yaml_config = yaml.load(config_file)

        return FlaskConfig.parse(yaml_config)

    @staticmethod
    def parse(yaml_config: dict):
        return FlaskConfig(
            baseurl=yaml_config["baseurl"],
            secret_key=yaml_config["secret_key"],
            database_baseurl=yaml_config["database_baseurl"],
            database_admin_user=yaml_config["database_admin"]["user"],
            database_admin_password=yaml_config["database_admin"]["password"],
        )

    @property
    def baseurl(self) -> str:
        return self._baseurl

    @property
    def database_admin_password(self) -> str:
        return self._database_admin_password

    @property
    def database_admin_user(self) -> str:
        return self._database_admin_user

    @property
    def database_baseurl(self) -> str:
        return self._database_baseurl

    @property
    def secret_key(self) -> str:
        return self._secret_key
