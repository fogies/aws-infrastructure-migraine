from flask import abort, Blueprint, render_template, current_app
from flask import jsonify, request, make_response, url_for, redirect
from flask_json import as_json

import requests
import re
from database import CouchDBClientConfig

from pathlib import Path
import requests
import requests.auth
import requests.exceptions

from urllib.parse import urljoin
import hashlib

users_blueprint = Blueprint("users_blueprint", __name__)


def _create_session(*, client_config: CouchDBClientConfig) -> requests.Session:
    """
    Obtain a session authenticated by the provided config.
    """

    # Authentication object for our request
    auth = requests.auth.HTTPBasicAuth(
        username=client_config.user,
        password=client_config.password,
    )

    # Open a session as admin
    session = requests.Session()
    response = session.post(
        urljoin(client_config.baseurl, "_session"),
        json={
            "name": auth.username,
            "password": auth.password,
        },
    )
    response.raise_for_status()

    return session


@users_blueprint.route("/create_account", methods=["POST"])
@as_json
def create_user_accounts():
    """
    Create user account.

    Body params:
    {
        "user_name": <>,
        "user_password": <>,
        "secret_key": <>
    }

    Returns:
    {
        "user_name": user_name,
        "database": "database name we create for the user."
    }

    """

    #
    # Validate the contents of the request
    #

    # if "user_name" or "user_password" aren't there in json body raise a http 400.
    if (
        ("user_name" not in request.json)
        or ("user_password" not in request.json)
        or ("secret_key" not in request.json)
    ):
        return "Method not allowed", 400

    user_name = request.json["user_name"]
    user_password = request.json["user_password"]
    secret_key = request.json["secret_key"]
    # current_app holds the flask app context.
    db_config = current_app.config

    # As a simple security measure, check if secret key sent from Yasaman's client matches our secret key.
    if secret_key != db_config["SECRET_KEY"]:
        return "Method not allowed", 400

    # Ensure the user_name is valid
    if not _validate_user(user=user_name):
        return (
            "This user name is not allowed. Please make sure your user name doesn not start with 'user_' and is less than 32 characters long.",
            400,
        )

    #### TODO

    #
    # Connect to the database
    #

    admin_config = CouchDBClientConfig(
        baseurl=current_app.config["URI_DATABASE"],
        user=current_app.config["DB_USER"],
        password=current_app.config["DB_PASSWORD"],
    )

    admin_session = _create_session(client_config=admin_config)

    #
    # Validate the state of the database
    #

    # ID of the user document
    user_doc_id = "org.couchdb.user:{}".format(user_name)

    # Ensure the user does not already exist
    response = admin_session.get(
        urljoin(admin_config.baseurl, "_users/{}".format(user_doc_id)),
    )
    if response.ok:
        # Get succeeded, so the user already exists
        abort(409)  # Conflict

    # Ensure the database does not already exist
    database = _database_for_user(user=user_name)
    response = admin_session.head(
        urljoin(admin_config.baseurl, database),
    )
    if response.ok:
        # Get succeeded, so the database already exists
        abort(409)  # Conflict

    #
    # Create the user and their database
    #

    # Because there are no transactions, it is possible to reach this point in a race condition.
    # In that case, creation of the user document is atomic, so one side of the race will fail.

    # Create the user
    response = admin_session.put(
        urljoin(admin_config.baseurl, "_users/{}".format(user_doc_id)),
        json={
            "type": "user",
            "name": user_name,
            "password": user_password,
            "roles": [],
        },
    )
    response.raise_for_status()

    # Create the database.
    response = admin_session.put(
        urljoin(admin_config.baseurl, database),
    )
    response.raise_for_status()

    # Ensure the database has the desired _security document.
    response = admin_session.put(
        urljoin(admin_config.baseurl, "{}/_security".format(database)),
        json={
            "members": {
                "names": [user_name],
                "roles": ["_admin"],
            },
            "admins": {
                "roles": ["_admin"],
            },
        },
    )
    response.raise_for_status()

    return {
        "user_name": user_name,
        "database": database,
    }


@users_blueprint.route("/get_profile", methods=["POST"])
@as_json
def get_user_profile():
    """
    Get user profile given a user name.

    Body params:
    {
        "user_name": <>,
        "secret_key": <>
    }

    Returns:
    {
        "user_name": user_name,
        "database": "existing database for the user."
    }

    """
    # if "user_name" or "user_password" aren't there in json body raise a http 400.
    if ("user_name" not in request.json) or ("secret_key" not in request.json):
        return "Method not allowed", 400

    user_name = request.json["user_name"]
    secret_key = request.json["secret_key"]
    # current_app holds the flask app context.
    db_config = current_app.config

    # As a simple security measure, check if secret key sent from Yasaman's client matches our secret key.
    if secret_key != db_config["SECRET_KEY"]:
        return "Method not allowed", 400

    # Load the couchdb class.
    couchdb_client_config = CouchDBClientConfig.load(
        db_config["URI_DATABASE"], db_config["DB_USER"], db_config["DB_PASSWORD"]
    )

    #
    # Obtain our connection information and admin credentials
    #
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

        # Ensure the user_name is valid
        if not _validate_user(user=user_name):
            return (
                "This user name is not allowed. Please make sure your user name doesn not start with 'user_' and is less than 32 characters long.",
                400,
            )

        # ID of the user document and its content
        user_doc_id = "org.couchdb.user:{}".format(user_name)

        # Check whether the user already exists (e.g., from a previous initialize)
        response = admin_session.get(
            urljoin(couchdb_client_config.baseurl, "_users/{}".format(user_doc_id)),
        )
        if response.status_code != 200:
            # The user does not already exist. Return with 400
            return "The user does not exist", 400
        else:

            # The user exists, check if database exists.
            database = _database_for_user(user=user_name)
            response = admin_session.head(
                urljoin(
                    couchdb_client_config.baseurl, _database_for_user(user=user_name)
                ),
            )
            if response.status_code != 200:
                # The database does not exist. Something is weird. Raise 500.
                return (
                    "Uh oh, this shouldn't happen. Database doesn't exist for this user. Please get in touch with the administrator.",
                    500,
                )

            else:
                # Return the database name since it exists.
                return {"user_name": user_name, "database": database}

    except requests.exceptions.HTTPError:
        return (
            "Uh oh, something went down. Please get in touch with the administrator.",
            500,
        )


@users_blueprint.route("/get_all_users", methods=["POST"])
@as_json
def get_all_users():
    """
    Return the list of all user names.

    Body params:
    {
        "secret_key": <>
    }
    """
    # if "user_name" or "user_password" aren't there in json body raise a http 400.
    if "secret_key" not in request.json:
        return "Method not allowed", 400

    secret_key = request.json["secret_key"]
    # current_app holds the flask app context.
    db_config = current_app.config

    # As a simple security measure, check if secret key sent from Yasaman's client matches our secret key.
    if secret_key != db_config["SECRET_KEY"]:
        return "Method not allowed", 400

    # Load the couchdb class.
    couchdb_client_config = CouchDBClientConfig.load(
        db_config["URI_DATABASE"], db_config["DB_USER"], db_config["DB_PASSWORD"]
    )

    #
    # Obtain our connection information and admin credentials
    #
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

        # Get all users.
        # https://docs.couchdb.org/en/stable/intro/security.html#authentication-database
        response = admin_session.get(
            urljoin(couchdb_client_config.baseurl, "_users/{}".format("_all_docs")),
        )
        if response.status_code != 200:
            # The _users database is empty?
            return "There are no users.", 400
        else:
            # For each element in the list of _user documents, check if 'id' starts with 'org.couchdb.user:""
            user_name_prefix = "org.couchdb.user:"
            return [
                user["id"].split(user_name_prefix)[1]
                for user in response.json()["rows"]
                if user_name_prefix in user["id"]
            ]

    except requests.exceptions.HTTPError:
        return (
            "Uh oh, something went down. Please get in touch with the administrator.",
            500,
        )


def _database_for_user(*, user: str):
    """
    Obtain the name of the database for a specified user.

    CouchDB requirement of database names:
    - Only lowercase characters (a-z), digits (0-9), and any of the characters _$()+-/ are allowed.
    - Must begin with a letter.

    Database names will therefore be 'user_' followed by hex encoding of an MD5 hash of the user name.
    """

    return "user_{}".format(hashlib.md5(user.encode("utf-8")).digest().hex())


def _validate_user(*, user: str) -> bool:
    """
    Determine whether a provided user name is allowable.

    At least characters :+ are not allowed in CouchDB user names, possibly others.
    Instead of requiring encoding of user names, require that names are alphanumeric with ._ allowed.
    """

    # Forbid user that start with 'user_', as that conflicts with our database encoding
    if user.startswith("user_"):
        return False

    # Limit to 32 characters, just to avoid any issues
    if len(user) > 32:
        return False

    return re.match(pattern="^[a-zA-Z0-9_.]+$", string=user) is not None
