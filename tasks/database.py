import hashlib
from invoke import Collection
from invoke import task
from pathlib import Path
import re
import requests
import requests.auth
import requests.exceptions
import ruamel.yaml
from typing import Union
from urllib.parse import urljoin

COUCHDB_CLIENT_CONFIG_PATH = './secrets/client/couchdb_client_config.yaml'


class CouchDBClientConfig:
    """
    Configuration for connection to a CouchDB instance.
    """

    _baseurl: str
    _admin_password: str
    _admin_user: str

    def __init__(self, *, baseurl: str, admin_user: str, admin_password: str):
        self._baseurl = baseurl
        self._admin_user = admin_user
        self._admin_password = admin_password

    @staticmethod
    def load(couchdb_client_config_path: Union[Path, str]):
        couchdb_client_config_path = Path(couchdb_client_config_path)

        with open(couchdb_client_config_path) as couchdb_client_config_file:
            yaml_config = ruamel.yaml.safe_load(couchdb_client_config_file)

        return CouchDBClientConfig(
            baseurl=yaml_config['baseurl'],
            admin_user=yaml_config['admin']['user'],
            admin_password=yaml_config['admin']['password'],
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


def _database_for_user(*, user: str):
    """
    Obtain the name of the database for a specified user.

    CouchDB requirement of database names:
    - Only lowercase characters (a-z), digits (0-9), and any of the characters _$()+-/ are allowed.
    - Must begin with a letter.

    Database names will therefore be 'user_' followed by hex encoding of an MD5 hash of the user name.
    """

    return 'user_{}'.format(hashlib.md5(user.encode('utf-8')).digest().hex())


def _validate_user(*, user: str) -> bool:
    """
    Determine whether a provided user name is allowable.

    At least characters :+ are not allowed in CouchDB user names, possibly others.
    Instead of requiring encoding of user names, require that names are alphanumeric with ._ allowed.
    """

    # Forbid user that start with 'user_', as that conflicts with our database encoding
    if user.startswith('user_'):
        return False

    # Limit to 32 characters, just to avoid any issues
    if len(user) > 32:
        return False

    return re.match(pattern='^[a-zA-Z0-9_.]+$', string=user) is not None


@task
def initialize(context):
    """
    Initialize the database.
    """

    #
    # Obtain our connection information and admin credentials
    #
    couchdb_client_config = CouchDBClientConfig.load(couchdb_client_config_path=COUCHDB_CLIENT_CONFIG_PATH)
    admin_auth = requests.auth.HTTPBasicAuth(
        username=couchdb_client_config.admin_user,
        password=couchdb_client_config.admin_password
    )

    #
    # Ensure the database is initialized
    #
    try:
        # Confirm the database is online
        response = requests.get(
            urljoin(couchdb_client_config.baseurl, ''),
        )
        response.raise_for_status()

        # Check whether the cluster has previously been finished (i.e., in a previous initialize)
        response = requests.get(
            urljoin(couchdb_client_config.baseurl, '_cluster_setup'),
            auth=admin_auth,
        )
        response.raise_for_status()

        # If the cluster was not finished in a previous initialize, do that now
        if response.json()['state'] != 'cluster_finished':
            response = requests.post(
                urljoin(couchdb_client_config.baseurl, '_cluster_setup'),
                json={
                    'action': 'finish_cluster'
                },
                auth=admin_auth,
            )
            response.raise_for_status()
    except requests.exceptions.HTTPError as error:
        print(error)


ns = Collection('database')
ns.add_task(initialize, 'initialize')
