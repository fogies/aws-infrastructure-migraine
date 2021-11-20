"""
Tests for confirming existence and expected state of our databases.
"""

import requests
import requests.auth
from urllib.parse import urljoin


# Execute tests against both development and production.
from tests.common.test_config_all import couchdb_config
assert couchdb_config


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
