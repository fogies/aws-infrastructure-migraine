from collections import namedtuple
from invoke import Collection
from invoke import task
from pathlib import Path
import requests
import requests.auth
import requests.exceptions
import ruamel.yaml
from urllib.parse import urljoin

from tasks.database import _database_for_user
from tasks.database import _validate_user
from tasks.database import CouchDBClientConfig

COUCHDB_CLIENT_CONFIG_PATH = "./secrets/client/couchdb_client_config.yaml"

COUCHDB_TEST_ACCOUNTS_CONFIG_PATH = "./secrets/tests/accounts_config.yaml"

TestAccount = namedtuple("TestAccount", ["user", "password"])
with open(Path(COUCHDB_TEST_ACCOUNTS_CONFIG_PATH)) as test_accounts_config_file:
    test_accounts_config = ruamel.yaml.safe_load(test_accounts_config_file)

TEST_ACCOUNTS = [
    TestAccount(user=account_current["user"], password=account_current["password"])
    for account_current in test_accounts_config["accounts"]
]


@task
def create_accounts(context):
    """
    Create test accounts.
    """

    #
    # Obtain our connection information and admin credentials
    #
    couchdb_client_config = CouchDBClientConfig.load(
        couchdb_client_config_path=COUCHDB_CLIENT_CONFIG_PATH
    )
    admin_auth = requests.auth.HTTPBasicAuth(
        username=couchdb_client_config.user,
        password=couchdb_client_config.password,
    )

    try:
        # Open a session as admin
        admin_session = requests.Session()
        response = admin_session.post(
            urljoin(couchdb_client_config.baseurl, "_session"),
            json={
                "name": admin_auth.username,
                "password": admin_auth.password,
            },
        )
        response.raise_for_status()

        # Create each user and each corresponding database
        for account_current in TEST_ACCOUNTS:
            # Ensure the user is valid
            if not _validate_user(user=account_current.user):
                raise ValueError('Invalid user "{}".'.format(account_current.user))

            # ID of the user document and its content
            user_doc_id = "org.couchdb.user:{}".format(account_current.user)
            user_doc = {
                "type": "user",
                "name": account_current.user,
                "password": account_current.password,
                "roles": [],
            }

            # Check whether the user already exists (e.g., from a previous initialize)
            response = admin_session.get(
                urljoin(couchdb_client_config.baseurl, "_users/{}".format(user_doc_id)),
            )
            if response.status_code != 200:
                # The user does not already exist. Create the user.
                response = admin_session.put(
                    urljoin(
                        couchdb_client_config.baseurl, "_users/{}".format(user_doc_id)
                    ),
                    json=user_doc,
                )
                response.raise_for_status()
            else:
                # The user already exists, provide an 'If-Match' header with the revision.
                # This will result in us overwriting the current document (e.g., a potential password change).
                existing_user_doc = response.json()
                response = admin_session.put(
                    urljoin(
                        couchdb_client_config.baseurl, "_users/{}".format(user_doc_id)
                    ),
                    headers={"If-Match": existing_user_doc["_rev"]},
                    json=user_doc,
                )
                response.raise_for_status()

            # Check whether the database already exists (e.g., from a previous initialize).
            database = _database_for_user(user=account_current.user)
            response = admin_session.head(
                urljoin(
                    couchdb_client_config.baseurl,
                    _database_for_user(user=account_current.user),
                ),
            )
            if response.status_code != 200:
                # The database does not already exist. Create the database.
                response = admin_session.put(
                    urljoin(couchdb_client_config.baseurl, database),
                )
                response.raise_for_status()
            else:
                # In production, the database already existing is something we should have checked before starting.
                # It would mean the account already exists, or that _database_for_user has generated a collision.
                pass

            # Ensure the database has the desired _security document.
            response = admin_session.put(
                urljoin(couchdb_client_config.baseurl, "{}/_security".format(database)),
                json={
                    "members": {
                        "names": [
                            account_current.user,
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

    except requests.exceptions.HTTPError as error:
        print(error)


@task
def test_accounts(context):
    """
    Exercise test accounts by creating and retrieving documents.
    """

    #
    # Obtain our connection information
    #
    couchdb_client_config = CouchDBClientConfig.load(
        couchdb_client_config_path=COUCHDB_CLIENT_CONFIG_PATH
    )

    try:
        # Connect as each valid user, confirm read/write from that database, confirm fail on other databases
        for account_current in TEST_ACCOUNTS:
            session_current = requests.Session()

            # Authenticate as this user
            response = session_current.post(
                urljoin(couchdb_client_config.baseurl, "_session"),
                json={
                    "name": account_current.user,
                    "password": account_current.password,
                },
            )
            response.raise_for_status()

            # Post a new document to their database
            response = session_current.post(
                urljoin(
                    couchdb_client_config.baseurl,
                    _database_for_user(user=account_current.user),
                ),
                json={"test_doc_key": "test_doc_value"},
            )
            response.raise_for_status()

            # Read all the documents in their database
            response = session_current.get(
                urljoin(
                    couchdb_client_config.baseurl,
                    "{}/{}".format(
                        _database_for_user(user=account_current.user), "_all_docs"
                    ),
                ),
            )
            response.raise_for_status()

            # Attempt to read from other accounts, these should all fail
            for fail_account_current in TEST_ACCOUNTS:
                if account_current != fail_account_current:
                    response = session_current.get(
                        urljoin(
                            couchdb_client_config.baseurl,
                            "{}/{}".format(
                                _database_for_user(user=fail_account_current.user),
                                "_all_docs",
                            ),
                        ),
                    )
                    if response.status_code != 403:
                        raise ValueError(
                            "Request status_code should have been 403 Forbidden."
                        )

    except requests.exceptions.HTTPError as error:
        print(error)


@task
def delete_accounts(context):
    """
    Delete test accounts.
    """

    #
    # Obtain our connection information and admin credentials
    #
    couchdb_client_config = CouchDBClientConfig.load(
        couchdb_client_config_path=COUCHDB_CLIENT_CONFIG_PATH
    )
    admin_auth = requests.auth.HTTPBasicAuth(
        username=couchdb_client_config.user,
        password=couchdb_client_config.password,
    )

    try:
        # Open a session as admin
        admin_session = requests.Session()
        response = admin_session.post(
            urljoin(couchdb_client_config.baseurl, "_session"),
            json={
                "name": admin_auth.username,
                "password": admin_auth.password,
            },
        )
        response.raise_for_status()

        # Delete the accounts and databases we created
        for account_current in TEST_ACCOUNTS:
            # Delete the database
            response = admin_session.delete(
                urljoin(
                    couchdb_client_config.baseurl,
                    _database_for_user(user=account_current.user),
                )
            )
            response.raise_for_status()

            # Delete the user
            user_doc_id = "org.couchdb.user:{}".format(account_current.user)

            # Obtain the rev from the existing document
            response = admin_session.get(
                urljoin(couchdb_client_config.baseurl, "_users/{}".format(user_doc_id)),
            )
            response.raise_for_status()
            existing_user_doc = response.json()

            # Perform the delete
            response = admin_session.delete(
                urljoin(couchdb_client_config.baseurl, "_users/{}".format(user_doc_id)),
                headers={"If-Match": existing_user_doc["_rev"]},
            )
            response.raise_for_status()

    except requests.exceptions.HTTPError as error:
        print(error)


@task
def get_accounts(context):
    """
    Print which user's account exists in couchdb in the test accounts.
    """

    #
    # Obtain our connection information and admin credentials
    #
    couchdb_client_config = CouchDBClientConfig.load(
        couchdb_client_config_path=COUCHDB_CLIENT_CONFIG_PATH
    )
    admin_auth = requests.auth.HTTPBasicAuth(
        username=couchdb_client_config.user,
        password=couchdb_client_config.password,
    )

    try:
        # Open a session as admin
        admin_session = requests.Session()
        response = admin_session.post(
            urljoin(couchdb_client_config.baseurl, "_session"),
            json={
                "name": admin_auth.username,
                "password": admin_auth.password,
            },
        )
        response.raise_for_status()

        # Create each user and each corresponding database
        for account_current in TEST_ACCOUNTS:
            # Ensure the user is valid
            if not _validate_user(user=account_current.user):
                raise ValueError('Invalid user "{}".'.format(account_current.user))

            # ID of the user document and its content
            user_doc_id = "org.couchdb.user:{}".format(account_current.user)
            user_doc = {
                "type": "user",
                "name": account_current.user,
                "password": account_current.password,
                "roles": [],
            }

            # Check whether the user already exists (e.g., from a previous initialize)
            response = admin_session.get(
                urljoin(couchdb_client_config.baseurl, "_users/{}".format(user_doc_id)),
            )
            if response.status_code != 200:
                # The user does not already exist. Print the user.
                print("User {} Does NOT Exist".format(account_current))
            else:
                print("User {} Does Exist".format(account_current))

    except requests.exceptions.HTTPError as error:
        print(error)


ns = Collection("tests")
ns.add_task(create_accounts, name="create-accounts")
ns.add_task(test_accounts, name="test-accounts")
ns.add_task(delete_accounts, name="delete-accounts")
ns.add_task(get_accounts, name="get-accounts")
