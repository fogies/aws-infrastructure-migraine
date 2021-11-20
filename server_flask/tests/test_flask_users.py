import collections
import pytest
import requests
import requests.auth
import secrets
from urllib.parse import urljoin

import migraine_shared.config
import migraine_shared.database


# Execute tests against only development.
from tests.common.test_config_dev import couchdb_config
from tests.common.test_config_dev import couchdb_session_admin
from tests.common.test_config_dev import flask_config
assert couchdb_config
assert couchdb_session_admin
assert flask_config


AccountTuple = collections.namedtuple('AccountTuple', ['user', 'password'])


@pytest.fixture
def sample_account() -> AccountTuple:
    return AccountTuple('flask_user', secrets.token_urlsafe())


@pytest.fixture()
def sample_account_delete(couchdb_config, couchdb_session_admin, sample_account):
    """
    Fixture to delete sample_account.

    The account may have been created by sample_account_create or by a test.
    """

    yield

    response = migraine_shared.database.delete_account(
        couchdb_session_admin=couchdb_session_admin,
        couchdb_baseurl=couchdb_config.baseurl,
        account=sample_account.user,
    )
    assert response.ok


@pytest.fixture()
def sample_account_create(couchdb_config, couchdb_session_admin, sample_account, sample_account_delete):
    """
    Fixture to create sample_account.  Uses sample_account_delete to also delete sample_account.
    """

    response = migraine_shared.database.create_account(
        couchdb_session_admin=couchdb_session_admin,
        couchdb_baseurl=couchdb_config.baseurl,
        account=sample_account.user,
        password=sample_account.password,
    )
    assert response.ok

    yield


@pytest.mark.xfail
def test_flask_get_all_users(flask_config: migraine_shared.config.FlaskConfig):
    """
    Test retrieval of all current users.
    """

    session = requests.session()
    response = session.post(
        urljoin(flask_config.baseurl, 'users/get_all_users'),
        json={
            'secret_key': flask_config.secret_key
        }
    )
    assert response.ok

    assert False
