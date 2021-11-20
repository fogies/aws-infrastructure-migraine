"""
Configuration for testing against only development.
"""

from pathlib import Path
import pytest
import requests
from urllib.parse import urljoin

import migraine_shared.config
import tests.config.test_config


@pytest.fixture(
    params=[
        tests.config.test_config.DEV_COUCHDB_CONFIG_PATH,
    ]
)
def couchdb_config(request) -> migraine_shared.config.CouchDBConfig:
    """
    Fixture providing CouchDB configuration.
    """
    return tests.config.test_config.couchdb_config(Path(request.param))


@pytest.fixture
def session_admin(couchdb_config: migraine_shared.config.CouchDBConfig) -> requests.Session:
    """
    Fixture providing session authenticated as administrator.
    """
    return tests.config.test_config.session_admin(couchdb_config=couchdb_config)


def test_session_admin_authenticated(
    session_admin: requests.Session,
    couchdb_config: migraine_shared.config.CouchDBConfig,
):
    """
    Test session_admin is actually authenticated as an administrator.
    """

    # Only an administrator can access the _users database
    response = session_admin.get(
        urljoin(couchdb_config.baseurl, "_users"),
    )
    assert response.ok
