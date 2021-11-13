from pathlib import Path
import ruamel.yaml
from typing import Union


class CouchDBClientConfig:
    """
    Configuration for connection to a CouchDB instance.
    """

    _baseurl: str
    _password: str
    _user: str

    def __init__(self, *, baseurl: str, user: str, password: str):
        self._baseurl = baseurl
        self._user = user
        self._password = password

    @staticmethod
    def load(documentdb_config_path: Union[Path, str]):
        documentdb_config_path = Path(documentdb_config_path)

        with open(documentdb_config_path) as documentdb_config_file:
            yaml_config = ruamel.yaml.safe_load(documentdb_config_file)

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
