import requests
from urllib.parse import urljoin

import migraine_shared.config

# Execute tests against only development.
from tests.common.test_config_dev import couchdb_config
from tests.common.test_config_dev import couchdb_session_admin
assert couchdb_config
assert couchdb_session_admin


def test_couchdb_session_admin_authenticated(
    couchdb_session_admin: requests.Session,
    couchdb_config: migraine_shared.config.CouchDBConfig,
):
    """
    Test couchdb_session_admin is actually authenticated as an administrator.
    """

    # Only an administrator can access the _users database
    response = couchdb_session_admin.get(
        urljoin(couchdb_config.baseurl, "_users"),
    )
    assert response.ok
