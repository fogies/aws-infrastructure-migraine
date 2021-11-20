"""
Tests for CouchDB account creation and deletion.

Executed against the development database.
"""

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
assert couchdb_config
assert couchdb_session_admin

AccountTuple = collections.namedtuple('AccountTuple', ['user', 'password'])


@pytest.fixture
def account_primary():
    """
    Account information for a primary test user.
    """

    return AccountTuple('test.account.primary', secrets.token_urlsafe())


@pytest.fixture
def account_secondary():
    """
    Account information for a secondary test user.
    """

    return AccountTuple('test.account.secondary', secrets.token_urlsafe())


def test_admin_account_creation_and_deletion(
    couchdb_config: migraine_shared.config.CouchDBConfig,
    couchdb_session_admin: requests.Session,
    account_primary: AccountTuple
):
    """
    Test session_admin can create a user and their corresponding database.
    """

    # Name of a corresponding user document and database.
    user_doc_id = "org.couchdb.user:{}".format(account_primary.user)
    user_database = migraine_shared.database.database_for_user(user=account_primary.user)

    # Ensure account does not exist, in case of previous test failure.
    response = migraine_shared.database.delete_account(
        couchdb_session_admin=couchdb_session_admin,
        couchdb_baseurl=couchdb_config.baseurl,
        account=account_primary.user,
    )
    assert response.status_code in [204, 404]  # OK No Content, Not Found

    # Ensure the user does not exist.
    response = couchdb_session_admin.get(
        urljoin(couchdb_config.baseurl, "_users/{}".format(user_doc_id)),
    )
    assert response.status_code == 404  # Not found

    # Ensure the database does not exist.
    response = couchdb_session_admin.get(
        urljoin(couchdb_config.baseurl, user_database)
    )
    assert response.status_code == 404  # Not found

    # Perform account creation.
    response = migraine_shared.database.create_account(
        couchdb_session_admin=couchdb_session_admin,
        couchdb_baseurl=couchdb_config.baseurl,
        account=account_primary.user,
        password=account_primary.password,
    )
    assert response.status_code == 200  # OK

    # Confirm the user now exists.
    response = couchdb_session_admin.get(
        urljoin(couchdb_config.baseurl, "_users/{}".format(user_doc_id)),
    )
    assert response.ok

    # Confirm the database now exists.
    response = couchdb_session_admin.get(
        urljoin(couchdb_config.baseurl, user_database)
    )
    assert response.ok

    # Perform account deletion.
    response = migraine_shared.database.delete_account(
        couchdb_session_admin=couchdb_session_admin,
        couchdb_baseurl=couchdb_config.baseurl,
        account=account_primary.user,
    )
    assert response.status_code == 204  # OK No Content

    # Ensure the user does not exist.
    response = couchdb_session_admin.get(
        urljoin(couchdb_config.baseurl, "_users/{}".format(user_doc_id)),
    )
    assert response.status_code == 404  # Not found

    # Ensure the database does not exist.
    response = couchdb_session_admin.get(
        urljoin(couchdb_config.baseurl, user_database)
    )
    assert response.status_code == 404  # Not found


def _session_account(
    couchdb_config: migraine_shared.config.CouchDBConfig,
    couchdb_session_admin: requests.Session,
    account_tuple: AccountTuple,
) -> requests.Session:
    """
    Helper that creates an account and provides a session authenticated as that account.
    """

    # Create the account
    response = migraine_shared.database.create_account(
        couchdb_session_admin=couchdb_session_admin,
        couchdb_baseurl=couchdb_config.baseurl,
        account=account_tuple.user,
        password=account_tuple.password,
    )
    assert response.ok

    # Obtain the session
    account_session = requests.Session()

    # Authenticate the session
    response = account_session.post(
        urljoin(couchdb_config.baseurl, "_session"),
        json={
            "name": account_tuple.user,
            "password": account_tuple.password,
        },
    )
    assert response.ok

    # Return the session
    yield account_session

    # Delete the account
    response = migraine_shared.database.delete_account(
        couchdb_session_admin=couchdb_session_admin,
        couchdb_baseurl=couchdb_config.baseurl,
        account=account_tuple.user,
    )
    assert response.ok


@pytest.fixture
def session_account_primary(
    couchdb_config: migraine_shared.config.CouchDBConfig,
    couchdb_session_admin: requests.Session,
    account_primary: AccountTuple,
) -> requests.Session:
    """
    Fixture providing session that is authenticated as a primary account.
    """

    yield from _session_account(
        couchdb_session_admin=couchdb_session_admin,
        couchdb_config=couchdb_config,
        account_tuple=account_primary,
    )


@pytest.fixture
def session_account_secondary(
    couchdb_config: migraine_shared.config.CouchDBConfig,
    couchdb_session_admin: requests.Session,
    account_secondary: AccountTuple,
) -> requests.Session:
    """
    Fixture providing session that is authenticated as a secondary account.
    """

    yield from _session_account(
        couchdb_session_admin=couchdb_session_admin,
        couchdb_config=couchdb_config,
        account_tuple=account_secondary,
    )


def test_account_document_access(
    couchdb_config: migraine_shared.config.CouchDBConfig,
    session_account_primary: requests.Session,
    account_primary: AccountTuple,
):
    """
    Test session_account_primary can create and access documents in their database.
    """

    # Name of a corresponding database.
    account_primary_database = migraine_shared.database.database_for_user(user=account_primary.user)

    # Random token for a document
    doc_test = {
        "test_account_document_access": secrets.token_urlsafe()
    }

    # Post a new document
    response = session_account_primary.post(
        urljoin(
            couchdb_config.baseurl,
            account_primary_database,
        ),
        json=doc_test,
    )
    assert response.ok

    # Retrieve all documents
    response = session_account_primary.post(
        urljoin(couchdb_config.baseurl, "{}/{}".format(account_primary_database, "_all_docs")),
        json={
            "include_docs": True
        },
    )
    assert response.ok

    # Filter off other fields
    documents = []
    for row_current in response.json()["rows"]:
        doc_current = row_current["doc"]
        del doc_current["_id"]
        del doc_current["_rev"]

        documents.append(doc_current)

    assert doc_test in documents


def test_account_document_secure(
    couchdb_config: migraine_shared.config.CouchDBConfig,
    session_account_primary: requests.Session,
    account_primary: AccountTuple,
    session_account_secondary: requests.Session,
):
    """
    Test that documents require corresponding authentication to access.
    """

    # Name of a corresponding database.
    account_primary_database = migraine_shared.database.database_for_user(user=account_primary.user)

    # Primary user should be able to access their own database
    response = session_account_primary.get(
        urljoin(couchdb_config.baseurl, "{}/{}".format(account_primary_database, "_all_docs"))
    )
    assert response.ok

    # Secondary user should be unable to access the database
    response = session_account_secondary.get(
        urljoin(couchdb_config.baseurl, "{}/{}".format(account_primary_database, "_all_docs"))
    )
    assert response.status_code == 403  # Forbidden

    # Unauthenticated session also should be unable to access the database
    session_unauthenticated = requests.Session()
    response = session_unauthenticated.get(
        urljoin(couchdb_config.baseurl, "{}/{}".format(account_primary_database, "_all_docs"))
    )
    assert response.status_code == 401  # Unauthorized
