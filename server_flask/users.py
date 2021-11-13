from typing import Dict
from flask import abort, Blueprint, current_app
from flask import jsonify, request
from flask_json import as_json
import jsonschema

import requests
import re
from database import CouchDBClientConfig

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

    # Open a session
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


def _database_for_user(*, user: str):
    """
    Obtain the name of the database for a specified user.

    CouchDB requirement of database names:
    - Only lowercase characters (a-z), digits (0-9), and any of the characters _$()+-/ are allowed.
    - Must begin with a letter.

    Database names will therefore be 'user_' followed by hex encoding of an MD5 hash of the user name.
    """

    return "user_{}".format(hashlib.md5(user.encode("utf-8")).digest().hex())


def _validate_request_json_schema(*, instance: Dict, schema: Dict):
    # NOTE - In spirit of James' TODO message - A centralized error handler could do a better job of this
    """Validates schema_instance by comparing it with schema. Raises a 400 if schema_instance in invalid.

    Args:
        instance (Dict): Schema instance which needs to validated
        schema (Dict): Schema against which instance will be validated
    """
    try:
        jsonschema.validate(instance=instance, schema=schema)
    except (jsonschema.SchemaError, jsonschema.ValidationError) as error:
        abort(
            400,
            jsonify(
                message="Invalid contents.", schema=error.schema, error=error.message
            ),
        )


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

    TODO: Before reusing code, check on proper REST verbs.
    """

    #
    # Validate the contents of the request
    #

    schema = {
        "type": "object",
        "properties": {
            "user_name": {"type": "string"},
            "user_password": {"type": "string"},
            "secret_key": {"type": "string"},
        },
        "required": ["user_name", "user_password", "secret_key"],
    }
    _validate_request_json_schema(instance=request.json, schema=schema)

    # Obtain contents of the request
    requested_user = request.json["user_name"]
    requested_password = request.json["user_password"]
    client_secret_key = request.json["secret_key"]

    # Require clients provide a secret
    if client_secret_key != current_app.config["CLIENT_SECRET_KEY"]:
        abort(403, jsonify(message="Invalid secret."))  # 403 Forbidden

    # Ensure the user_name is valid
    if not _validate_user(user=requested_user):
        abort(403, jsonify(message="User not allowed."))  # 403 Forbidden

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
    user_doc_id = "org.couchdb.user:{}".format(requested_user)

    # Ensure the user does not already exist
    response = admin_session.get(
        urljoin(admin_config.baseurl, "_users/{}".format(user_doc_id)),
    )
    if response.ok:
        # Get succeeded, so the user already exists
        abort(409, jsonify(message="User already exists."))  # 409 Conflict

    # Ensure the database does not already exist
    database = _database_for_user(user=requested_user)
    response = admin_session.head(
        urljoin(admin_config.baseurl, database),
    )
    if response.ok:
        # Get succeeded, so the database already exists
        abort(409, jsonify(message="Database already exists."))  # 409 Conflict

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
            "name": requested_user,
            "password": requested_password,
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
                "names": [requested_user],
                "roles": ["_admin"],
            },
            "admins": {
                "roles": ["_admin"],
            },
        },
    )
    response.raise_for_status()

    return {
        "user_name": requested_user,
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

    TODO: Before reusing code, check on proper REST verbs.
    """
    #
    # Validate the contents of the request
    #
    schema = {
        "type": "object",
        "properties": {
            "user_name": {"type": "string"},
            "secret_key": {"type": "string"},
        },
        "required": ["user_name", "secret_key"],
    }
    _validate_request_json_schema(instance=request.json, schema=schema)

    # Obtain contents of the request
    requested_user = request.json["user_name"]
    client_secret_key = request.json["secret_key"]

    # Require clients provide a secret
    if client_secret_key != current_app.config["CLIENT_SECRET_KEY"]:
        abort(403, jsonify(message="Invalid secret."))  # 403 Forbidden

    # Ensure the user_name is valid
    if not _validate_user(user=requested_user):
        abort(403, jsonify(message="User not allowed."))  # 403 Forbidden

    #
    # Connect to the database
    #

    admin_config = CouchDBClientConfig(
        baseurl=current_app.config["URI_DATABASE"],
        user=current_app.config["DB_USER"],
        password=current_app.config["DB_PASSWORD"],
    )

    admin_session = _create_session(client_config=admin_config)

    # ID of the user document and its content
    user_doc_id = "org.couchdb.user:{}".format(requested_user)

    # Check whether the user already exists (e.g., from a previous initialize)
    response = admin_session.get(
        urljoin(admin_config.baseurl, "_users/{}".format(user_doc_id)),
    )
    response.raise_for_status()

    # NOTE: @James: Instead of `response.raise_for_status()`, should we send more usable abort messages if username and/or database doesn't exist? Example provided as comment below.
    """
    if response.status_code != 200:
        # The user does not exist. Return with 404
        abort(404, jsonify(message="The user does not exist."))  # 409 Conflict
    """

    # The user exists, check if database exists.
    database = _database_for_user(user=requested_user)
    response = admin_session.head(
        urljoin(admin_config.baseurl, database),
    )
    response.raise_for_status()

    # Return the database name since it exists.
    return {"user_name": requested_user, "database": database}


@users_blueprint.route("/get_all_users", methods=["POST"])
@as_json
def get_all_users():
    """
    Return the list of all user names.

    Body params:
    {
        "secret_key": <>
    }

    TODO: Before reusing code, check on proper REST verbs.
    """
    #
    # Validate the contents of the request
    #
    schema = {
        "type": "object",
        "properties": {
            "secret_key": {"type": "string"},
        },
        "required": ["secret_key"],
    }
    _validate_request_json_schema(instance=request.json, schema=schema)

    # Obtain contents of the request
    client_secret_key = request.json["secret_key"]

    # Require clients provide a secret
    if client_secret_key != current_app.config["CLIENT_SECRET_KEY"]:
        abort(403, jsonify(message="Invalid secret."))  # 403 Forbidden

    #
    # Connect to the database and create an admin session
    #
    admin_config = CouchDBClientConfig(
        baseurl=current_app.config["URI_DATABASE"],
        user=current_app.config["DB_USER"],
        password=current_app.config["DB_PASSWORD"],
    )
    admin_session = _create_session(client_config=admin_config)

    # Get all users.
    # https://docs.couchdb.org/en/stable/intro/security.html#authentication-database
    response = admin_session.get(
        urljoin(admin_config.baseurl, "_users/{}".format("_all_docs")),
    )
    response.raise_for_status()

    # For each element in the list of _user documents, check if 'id' starts with 'org.couchdb.user:""
    user_name_prefix = "org.couchdb.user:"
    return [
        user["id"].split(user_name_prefix)[1]
        for user in response.json()["rows"]
        if user_name_prefix in user["id"]
    ]
