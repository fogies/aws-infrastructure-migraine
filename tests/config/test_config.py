from pathlib import Path
import requests
from urllib.parse import urljoin

import migraine_shared.config

DEV_COUCHDB_CONFIG_PATH = "./secrets/configuration/dev_couchdb.yaml"
PROD_COUCHDB_CONFIG_PATH = "./secrets/configuration/prod_couchdb.yaml"


def couchdb_config(config_path: Path) -> migraine_shared.config.CouchDBConfig:
    """
    Helper that loads a CouchDBConfig from a Path.
    """
    return migraine_shared.config.CouchDBConfig.load(couchdb_config_path=config_path)


def session_admin(couchdb_config: migraine_shared.config.CouchDBConfig) -> requests.Session:
    """
    Helper that provides session authenticated as an administrator.
    """

    # Obtain the session
    session = requests.Session()

    # Authenticate the session
    response = session.post(
        urljoin(couchdb_config.baseurl, "_session"),
        json={
            "name": couchdb_config.admin_user,
            "password": couchdb_config.admin_password,
        },
    )
    assert response.ok

    return session
