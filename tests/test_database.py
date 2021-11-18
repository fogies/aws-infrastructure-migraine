from pathlib import Path
import pytest
import requests
import requests.auth
from urllib.parse import urljoin

import migraine_shared.config

DEV_COUCHDB_CONFIG_PATH = "./secrets/configuration/dev_couchdb.yaml"
PROD_COUCHDB_CONFIG_PATH = "./secrets/configuration/prod_couchdb.yaml"


@pytest.fixture(
    params=[
        DEV_COUCHDB_CONFIG_PATH,
        PROD_COUCHDB_CONFIG_PATH,
    ]
)
def couchdb_config(request) -> migraine_shared.config.CouchDBConfig:
    """
    Fixture providing database configurations.
    """

    config_path = request.param

    # Skip configurations that do not exist
    if not Path(config_path).exists():
        pytest.skip()

    return migraine_shared.config.CouchDBConfig.load(config_path)


def test_database_exists(couchdb_config):
    """
    Test existence of the database.

    Uses admin credentials to verify the database has been initialized.
    """

    # Confirm the database is online.
    session = requests.session()
    response = session.get(
        urljoin(couchdb_config.baseurl, ''),
    )
    assert response.ok

    # Credentials for admin authentication.
    admin_auth = requests.auth.HTTPBasicAuth(
        username=couchdb_config.admin_user,
        password=couchdb_config.admin_password
    )

    # Check the cluster has been initialized (i.e., finished).
    response = requests.get(
        urljoin(couchdb_config.baseurl, '_cluster_setup'),
        auth=admin_auth,
    )
    assert response.ok
    assert response.json()['state'] == 'cluster_finished'
