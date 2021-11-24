from dataclasses import dataclass
from pathlib import Path
import ruamel.yaml
from typing import Union


@dataclass(frozen=True)
class CouchDBConfig:
    """
    Parse configuration for clients of a CouchDB instance.
    """

    admin_password: str
    admin_user: str
    baseurl: str
    cookie_auth_secret: str
    uuid: str

    @staticmethod
    def load(couchdb_config_path: Union[Path, str]):
        couchdb_config_path = Path(couchdb_config_path)

        with open(couchdb_config_path) as config_file:
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


@dataclass(frozen=True)
class FlaskConfig:
    """
    Parse configuration for a Flask instance.
    """

    baseurl: str
    secret_key: str

    database_baseurl: str
    database_admin_password: str
    database_admin_user: str


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
