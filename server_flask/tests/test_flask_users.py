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


AccountTuple = collections.namedtuple("AccountTuple", ["user", "password"])


@pytest.fixture
def sample_account() -> AccountTuple:
    return AccountTuple("test_flask_user", secrets.token_urlsafe())


@pytest.fixture()
def sample_account_delete(
    couchdb_config: migraine_shared.config.CouchDBConfig,
    couchdb_session_admin: requests.Session,
    sample_account: AccountTuple,
):
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
def sample_account_create(
    couchdb_config: migraine_shared.config.CouchDBConfig,
    couchdb_session_admin: requests.Session,
    sample_account: AccountTuple,
    sample_account_delete,
):
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


def test_flask_create_user_account(
    flask_config: migraine_shared.config.FlaskConfig,
    sample_account: AccountTuple,
    sample_account_delete,  # None, included for fixture functionality
):
    """
    Test creation of a user account.
    """

    assert sample_account_delete is None

    session = requests.session()
    response = session.post(
        urljoin(flask_config.baseurl, "users/"),
        json={
            "user_name": sample_account.user,
            "user_password": sample_account.password,
        },
        headers={"Authorization": "Bearer " + flask_config.secret_key},
    )
    assert response.ok

    # Response json is a dictionary containing status, user_name, and database.
    # TODO: Response format across the endpoints is inconsistent.
    #       Up to Yasaman/Anant whether to address in this deployment
    assert response.json() == {
        "status": 200,
        "user_name": sample_account.user,
        "database": migraine_shared.database.database_for_user(
            user=sample_account.user
        ),
    }


def test_flask_create_user_account_bad_key_failure(
    flask_config: migraine_shared.config.FlaskConfig,
    sample_account: AccountTuple,
):
    """
    Test creation of a user account with bad key. Should return 403.
    """

    session = requests.session()
    response = session.post(
        urljoin(flask_config.baseurl, "users/"),
        json={
            "user_name": sample_account.user,
            "user_password": sample_account.password,
        },
        headers={"Authorization": "Bearer badkey"},
    )
    assert response.status_code == 403


def test_flask_create_duplicate_user_account_failure(
    flask_config: migraine_shared.config.FlaskConfig,
    sample_account: AccountTuple,
    sample_account_create,
):
    """
    Test creation of a user account when the user already exists. Should return 409.
    """

    assert sample_account_create is None

    session = requests.session()
    response = session.post(
        urljoin(flask_config.baseurl, "users/"),
        json={
            "user_name": sample_account.user,
            "user_password": sample_account.password,
        },
        headers={"Authorization": "Bearer " + flask_config.secret_key},
    )
    assert response.status_code == 409


def test_flask_get_all_users(
    flask_config: migraine_shared.config.FlaskConfig,
    sample_account: AccountTuple,
    sample_account_create,  # None, included for fixture functionality
):
    """
    Test retrieval of all current users.
    """

    assert sample_account_create is None

    session = requests.session()
    response = session.get(
        urljoin(flask_config.baseurl, "users/"),
        headers={"Authorization": "Bearer " + flask_config.secret_key},
    )
    assert response.ok

    # Response json is a list of users, with no surrounding dictionary.
    # Ensure our sample is in that list.
    # TODO: Response format across the endpoints is inconsistent.
    #       Up to Yasaman/Anant whether to address in this deployment
    # NOTE: @James - response format is consistent with other responses.
    assert sample_account.user in response.json()["users"]


def test_flask_get_user(
    flask_config: migraine_shared.config.FlaskConfig,
    sample_account: AccountTuple,
    sample_account_create,  # None, included for fixture functionality
):
    """
    Test retrieval of a user profile.
    """

    assert sample_account_create is None

    session = requests.session()
    response = session.get(
        urljoin(flask_config.baseurl, "users/" + sample_account.user),
        headers={"Authorization": "Bearer " + flask_config.secret_key},
    )
    assert response.ok

    # Response json is a dictionary containing status, user_name, and database.
    # TODO: Response format across the endpoints is inconsistent.
    #       Up to Yasaman/Anant whether to address in this deployment
    assert response.json() == {
        "status": 200,
        "user_name": sample_account.user,
        "database": migraine_shared.database.database_for_user(
            user=sample_account.user
        ),
    }


def test_flask_get_user_failure(
    flask_config: migraine_shared.config.FlaskConfig,
    sample_account: AccountTuple,
):
    """
    Test retrieval of a user profile.

    Sample account was not created, this profile retrieval should fail.
    """

    session = requests.session()
    response = session.get(
        urljoin(flask_config.baseurl, "users/" + sample_account.user),
        headers={"Authorization": "Bearer " + flask_config.secret_key},
    )
    assert response.status_code == 404  # Not Found
