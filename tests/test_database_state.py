"""
Tests for confirming existence and expected state of our databases.
"""

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

    return migraine_shared.config.CouchDBConfig.load(config_path)


def test_database_reachable(couchdb_config):
    """
    Test database is responding at expected baseurl.
    """

    session = requests.session()
    response = session.get(
        urljoin(couchdb_config.baseurl, ''),
    )
    assert response.ok


def test_database_initialized(couchdb_config):
    """
    Test database has been properly initialized.

    CouchDB requires initialization request after the cluster is created.
    """

    # Credentials for basic authentication as admin.
    # If the database were not initialized, session-based authentication would fail.
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
