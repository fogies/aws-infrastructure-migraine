"""
Tests for confirming how to manage CouchDB users and databases.

Executed against the development database.

Intended to build our own understanding of CouchDB,
so code used in these tests ultimately duplicates code that should be in an application server.
"""

import collections
import pytest
import requests
import requests.auth
import secrets
from urllib.parse import urljoin

import migraine_shared.config
import migraine_shared.database

DEV_COUCHDB_CONFIG_PATH = "./secrets/configuration/dev_couchdb.yaml"


@pytest.fixture
def couchdb_config() -> migraine_shared.config.CouchDBConfig:
    """
    Fixture providing database configuration.
    """

    return migraine_shared.config.CouchDBConfig.load(DEV_COUCHDB_CONFIG_PATH)


@pytest.fixture
def couchdb_baseurl(couchdb_config: migraine_shared.config.CouchDBConfig) -> str:
    """
    Fixture providing baseurl.
    """
    return couchdb_config.baseurl


@pytest.fixture
def session_admin(couchdb_config: migraine_shared.config.CouchDBConfig, couchdb_baseurl: str) -> requests.Session:
    """
    Fixture providing session that is authenticated as an administrator.
    """

    # Obtain the session
    session_admin = requests.Session()

    # Authenticate the session
    response = session_admin.post(
        urljoin(couchdb_baseurl, "_session"),
        json={
            "name": couchdb_config.admin_user,
            "password": couchdb_config.admin_password,
        },
    )
    assert response.ok

    return session_admin


def test_session_admin_authenticated(session_admin: requests.Session, couchdb_baseurl: str):
    """
    Test session_admin is actually authenticated as an administrator.
    """

    # Only an administrator can access the _users database
    response = session_admin.get(
        urljoin(couchdb_baseurl, "_users"),
    )
    assert response.ok


user_tuple = collections.namedtuple('user_tuple', ['user', 'password'])


@pytest.fixture
def user_primary():
    """
    Account information for a primary test user.
    """

    return user_tuple('tests.user.primary', secrets.token_urlsafe())


@pytest.fixture
def user_secondary():
    """
    Account information for a secondary test user.
    """

    return user_tuple('tests.user.secondary', secrets.token_urlsafe())


def _create_user(
    session_admin: requests.Session,
    couchdb_baseurl: str,
    user: str,
    password: str,
):
    """
    Helper to use an session_admin to create a requested account.
    """

    # Ensure the requested_user is valid.
    if not migraine_shared.database.validate_user(user=user):
        raise ValueError('Invalid user "{}".'.format(user))

    # ID of the user document and its content.
    user_doc_id = "org.couchdb.user:{}".format(user)
    user_doc = {
        "type": "user",
        "name": user,
        "password": password,
        "roles": [],
    }

    # Name of a corresponding database.
    user_database = migraine_shared.database.database_for_user(user=user)

    # Ensure the user does not already exist.
    response = session_admin.get(
        urljoin(couchdb_baseurl, "_users/{}".format(user_doc_id)),
    )
    if response.ok:
        # Get succeeded, so the user already exists.
        raise ValueError('User already exists "{}"'.format(user))

    # Ensure the database does not already exist.
    response = session_admin.head(
        urljoin(couchdb_baseurl, user_database)
    )
    if response.ok:
        # Get succeeded, so the database already exists.
        raise ValueError('Database already exists "{}"'.format(user_database))

    # Create the requested user.
    response = session_admin.put(
        urljoin(couchdb_baseurl, "_users/{}".format(user_doc_id)),
        json=user_doc,
    )
    response.raise_for_status()

    # Create the requested database.
    response = session_admin.put(
        urljoin(couchdb_baseurl, user_database),
    )
    response.raise_for_status()

    # Apply a _security document granting the user access to the database.
    response = session_admin.put(
        urljoin(couchdb_baseurl, "{}/_security".format(user_database)),
        json={
            "members": {
                "names": [
                    user,
                ],
                "roles": [
                    "_admin",
                ],
            },
            "admins": {
                "roles": [
                    "_admin",
                ],
            },
        },
    )
    response.raise_for_status()


def _delete_user_if_exists(
    session_admin: requests.Session,
    couchdb_baseurl: str,
    user: str,
):
    """
    Helper to use an session_admin to delete an account if it exists.

    If the account does not exist, no action is taken.
    """

    # Name of a corresponding user document and database.
    user_doc_id = "org.couchdb.user:{}".format(user)
    user_database = migraine_shared.database.database_for_user(user=user)

    # Check if the user exists.
    response = session_admin.get(
        urljoin(couchdb_baseurl, "_users/{}".format(user_doc_id)),
    )
    if response.ok:
        # The user exists, issue a delete including the "_rev" we obtained.
        existing_user_doc = response.json()
        response = session_admin.delete(
            urljoin(couchdb_baseurl, "_users/{}".format(user_doc_id)),
            headers={"If-Match": existing_user_doc["_rev"]},
        )
        response.raise_for_status()

    # Check if the database exists.
    response = session_admin.get(
        urljoin(couchdb_baseurl, user_database),
    )
    if response.ok:
        # The database exists, issue a delete.
        response = session_admin.delete(
            urljoin(couchdb_baseurl, user_database)
        )
        response.raise_for_status()


def test_admin_user_creation_and_deletion(
    session_admin: requests.Session,
    couchdb_baseurl: str,
    user_primary: user_tuple
):
    """
    Test session_admin can create a user and their corresponding database.
    """

    # Name of a corresponding user document and database.
    user_doc_id = "org.couchdb.user:{}".format(user_primary.user)
    user_database = migraine_shared.database.database_for_user(user=user_primary.user)

    # Ensure user and database do not exist, in case of previous test failure.
    _delete_user_if_exists(
        session_admin=session_admin,
        couchdb_baseurl=couchdb_baseurl,
        user=user_primary.user,
    )

    # Ensure the user does not exist.
    response = session_admin.get(
        urljoin(couchdb_baseurl, "_users/{}".format(user_doc_id)),
    )
    assert response.status_code == 404  # Not found

    # Ensure the database does not exist.
    response = session_admin.get(
        urljoin(couchdb_baseurl, user_database)
    )
    assert response.status_code == 404  # Not found

    # Perform user and database creation.
    _create_user(
        session_admin=session_admin,
        couchdb_baseurl=couchdb_baseurl,
        user=user_primary.user,
        password=user_primary.password,
    )

    # Confirm the user now exists.
    response = session_admin.get(
        urljoin(couchdb_baseurl, "_users/{}".format(user_doc_id)),
    )
    assert response.ok

    # Confirm the database now exists.
    response = session_admin.get(
        urljoin(couchdb_baseurl, user_database)
    )
    assert response.ok

    # Perform user and database deletion.
    _delete_user_if_exists(
        session_admin=session_admin,
        couchdb_baseurl=couchdb_baseurl,
        user=user_primary.user,
    )

    # Ensure the user does not exist.
    response = session_admin.get(
        urljoin(couchdb_baseurl, "_users/{}".format(user_doc_id)),
    )
    assert response.status_code == 404  # Not found

    # Ensure the database does not exist.
    response = session_admin.get(
        urljoin(couchdb_baseurl, user_database)
    )
    assert response.status_code == 404  # Not found


@pytest.fixture
def session_user_primary(
    session_admin: requests.Session,
    couchdb_baseurl: str,
    user_primary: user_tuple,
) -> requests.Session:
    """
    Fixture providing session that is authenticated as a primary user.
    """

    # Create the user
    _create_user(
        session_admin=session_admin,
        couchdb_baseurl=couchdb_baseurl,
        user=user_primary.user,
        password=user_primary.password,
    )

    # Obtain the session
    user_session = requests.Session()

    # Authenticate the session
    response = user_session.post(
        urljoin(couchdb_baseurl, "_session"),
        json={
            "name": user_primary.user,
            "password": user_primary.password,
        },
    )
    assert response.ok

    # Return the session
    yield user_session

    # Delete the user
    _delete_user_if_exists(
        session_admin=session_admin,
        couchdb_baseurl=couchdb_baseurl,
        user=user_primary.user,
    )


@pytest.fixture
def session_user_secondary(
    session_admin: requests.Session,
    couchdb_baseurl: str,
    user_secondary: user_tuple,
) -> requests.Session:
    """
    Fixture providing session that is authenticated as a secondary user.
    """
    
    # Create the user
    _create_user(
        session_admin=session_admin,
        couchdb_baseurl=couchdb_baseurl,
        user=user_secondary.user,
        password=user_secondary.password,
    )
    
    # Obtain the session
    user_session = requests.Session()

    # Authenticate the session
    response = user_session.post(
        urljoin(couchdb_baseurl, "_session"),
        json={
            "name": user_secondary.user,
            "password": user_secondary.password,
        },
    )
    assert response.ok

    # Return the session
    yield user_session

    # Delete the user
    _delete_user_if_exists(
        session_admin=session_admin,
        couchdb_baseurl=couchdb_baseurl,
        user=user_secondary.user,
    )


def test_user_document_access(
    couchdb_baseurl: str,
    user_primary: user_tuple,
    session_user_primary: requests.Session
):
    """
    Test session_user_primary can create and access documents in their database.
    """

    # Name of a corresponding database.
    user_primary_database = migraine_shared.database.database_for_user(user=user_primary.user)

    # Random token for a document
    doc_test = {
        "test_user_document_access": secrets.token_urlsafe()
    }

    # Post a new document
    response = session_user_primary.post(
        urljoin(
            couchdb_baseurl,
            user_primary_database,
        ),
        json=doc_test,
    )
    assert response.ok

    # Retrieve all documents
    response = session_user_primary.post(
        urljoin(couchdb_baseurl, "{}/{}".format(user_primary_database, "_all_docs")),
        json={
            "include_docs": True
        },
    )
    assert response.ok

    # Filter off
    documents = []
    for row_current in response.json()["rows"]:
        doc_current = row_current["doc"]
        del doc_current["_id"]
        del doc_current["_rev"]

        documents.append(doc_current)

    assert doc_test in documents


def test_user_document_secure(
    couchdb_baseurl: str,
    user_primary: user_tuple,
    session_user_primary: requests.Session,
    session_user_secondary: requests.Session,
):
    """
    Test that user documents require corresponding authentication to access.
    """

    # Name of a corresponding database.
    user_primary_database = migraine_shared.database.database_for_user(user=user_primary.user)

    # Primary user should be able to access their own database
    response = session_user_primary.get(
        urljoin(couchdb_baseurl, "{}/{}".format(user_primary_database, "_all_docs"))
    )
    assert response.ok

    # Secondary user should be unable to access the database
    response = session_user_secondary.get(
        urljoin(couchdb_baseurl, "{}/{}".format(user_primary_database, "_all_docs"))
    )
    assert response.status_code == 403  # Forbidden

    # Unauthenticated session also should be unable to access the database
    session_unauthenticated = requests.Session()
    response = session_unauthenticated.get(
        urljoin(couchdb_baseurl, "{}/{}".format(user_primary_database, "_all_docs"))
    )
    assert response.status_code == 401  # Unauthorized
