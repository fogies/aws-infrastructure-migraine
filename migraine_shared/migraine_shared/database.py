import hashlib
import re
import requests
from urllib.parse import urljoin

def create_account(
    couchdb_session_admin: requests.Session,
    couchdb_baseurl: str,
    account: str,
    password: str,
) -> requests.Response:
    """
    Use a session_admin to create an account.

    If creation succeeds, return a "shallow" 200 Response.
    If the requested user is forbidden, return a "shallow" 403 Response.
    If the requested account already exists, return a "shallow" 409 Response.
    If an underlying request fails, return that Response.
    """

    # Ensure the requested_user is valid.
    if not validate_user(user=account):
        response = requests.Response()
        response.status_code = 403
        return response

    # ID of the user document and its content.
    user_doc_id = "org.couchdb.user:{}".format(account)
    user_doc = {
        "type": "user",
        "name": account,
        "password": password,
        "roles": [],
    }

    # Name of a corresponding database.
    user_database = database_for_user(user=account)

    # Ensure the user does not already exist.
    response = couchdb_session_admin.get(
        urljoin(couchdb_baseurl, "_users/{}".format(user_doc_id)),
    )
    if response.ok:
        # Get succeeded, so the user already exists.
        response = requests.Response()
        response.status_code = 409
        return response

    # Ensure the database does not already exist.
    response = couchdb_session_admin.head(
        urljoin(couchdb_baseurl, user_database)
    )
    if response.ok:
        # Get succeeded, so the database already exists.
        response = requests.Response()
        response.status_code = 409
        return response

    # Create the requested user.
    response = couchdb_session_admin.put(
        urljoin(couchdb_baseurl, "_users/{}".format(user_doc_id)),
        json=user_doc,
    )
    if not response.ok:
        return response

    # Create the requested database.
    response = couchdb_session_admin.put(
        urljoin(couchdb_baseurl, user_database),
    )
    if not response.ok:
        return response

    # Apply a _security document granting the user access to the database.
    response = couchdb_session_admin.put(
        urljoin(couchdb_baseurl, "{}/_security".format(user_database)),
        json={
            "members": {
                "names": [
                    account,
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
    if not response.ok:
        return response

    response = requests.Response()
    response.status_code = 200
    return response


def delete_account(
    couchdb_session_admin: requests.Session,
    couchdb_baseurl: str,
    account: str,
) -> requests.Response:
    """
    Use a session_admin to delete an account.

    If deletion succeeds, return a "shallow" 204 Response.
    If the account did not exist, return a "shallow" 404 Response.
    If an underlying request fails, return that Response.
    """

    # Name of a corresponding user document and database.
    user_doc_id = "org.couchdb.user:{}".format(account)
    user_database = database_for_user(user=account)

    # Account at least partially existed if either the user or the database existed
    account_existed = False

    # Check if the user exists.
    response = couchdb_session_admin.get(
        urljoin(couchdb_baseurl, "_users/{}".format(user_doc_id)),
    )
    if response.ok:
        # The account at least partially existed
        account_existed = True

        # The user exists, issue a delete including the "_rev" we obtained.
        existing_user_doc = response.json()
        response = couchdb_session_admin.delete(
            urljoin(couchdb_baseurl, "_users/{}".format(user_doc_id)),
            headers={"If-Match": existing_user_doc["_rev"]},
        )
        if not response.ok:
            # Deletion failed, return the underlying failure
            return response

    # Check if the database exists.
    response = couchdb_session_admin.get(
        urljoin(couchdb_baseurl, user_database),
    )
    if response.ok:
        # The account at least partially existed
        account_existed = True

        # The database exists, issue a delete.
        response = couchdb_session_admin.delete(
            urljoin(couchdb_baseurl, user_database)
        )
        if not response.ok:
            # Deletion failed, return the underlying failure
            return response

    response = requests.Response()
    if account_existed:
        # Successful deletion
        response.status_code = 204
    else:
        # No account existed
        response.status_code = 404

    return response


def database_for_user(*, user: str):
    """
    Obtain the name of the database for a specified user.

    CouchDB requirement of database names:
    - Only lowercase characters (a-z), digits (0-9), and any of the characters _$()+-/ are allowed.
    - Must begin with a letter.

    Database names will therefore be 'user_' followed by hex encoding of an MD5 hash of the user name.
    """

    return 'user_{}'.format(hashlib.md5(user.encode('utf-8')).digest().hex())


def validate_user(*, user: str) -> bool:
    """
    Determine whether a provided user name is allowable.

    At least characters :+ are not allowed in CouchDB user names, possibly others.
    Instead of requiring encoding of user names, require that names are alphanumeric with ._ allowed.
    """

    # Forbid user that start with 'user_', as that conflicts with our database encoding
    if user.startswith('user_'):
        return False

    # Limit to 32 characters, just to avoid any issues
    if len(user) > 32:
        return False

    return re.match(pattern='^[a-zA-Z0-9_.]+$', string=user) is not None
