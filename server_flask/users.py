from flask import abort, Blueprint, current_app
from flask import jsonify, request
from flask_json import as_json
import jsonschema
import requests
import requests.auth
import requests.exceptions
from typing import Dict
from urllib.parse import urljoin

import migraine_shared.database

users_blueprint = Blueprint("users_blueprint", __name__)


def _create_session(*, baseurl: str, user: str, password: str) -> requests.Session:
    """
    Obtain a session authenticated by the provided config.
    """

    # Authentication object for our request
    auth = requests.auth.HTTPBasicAuth(
        username=user,
        password=password,
    )

    # Open a session
    session = requests.Session()
    response = session.post(
        urljoin(baseurl, "_session"),
        json={
            "name": auth.username,
            "password": auth.password,
        },
    )
    response.raise_for_status()

    return session


def _validate_request_json_schema(*, instance: Dict, schema: Dict):
    """
    Validate schema_instance against schema.

    Raise 400 on failure.

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


def _validate_secret_key(*, secret_key: str):
    """
    Validate the provided secret key matches are required secret key.

    Raise 403 on failure.
    """
    # Require clients provide a secret
    if secret_key != current_app.config["SECRET_KEY"]:
        abort(403, jsonify(message="Invalid secret key."))  # 403 Forbidden


@users_blueprint.route("/create_account", methods=["POST"])
@as_json
def create_user_account():
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
    _validate_secret_key(secret_key=request.json["secret_key"])

    # Obtain contents of the request
    requested_user = request.json["user_name"]
    requested_password = request.json["user_password"]

    #
    # Connect to the database
    #

    couchdb_baseurl = current_app.config["DATABASE_BASEURL"]
    couchdb_session_admin = _create_session(
        baseurl=couchdb_baseurl,
        user=current_app.config["DATABASE_ADMIN_USER"],
        password=current_app.config["DATABASE_ADMIN_PASSWORD"],
    )

    #
    # Create the user and their database
    #

    response = migraine_shared.database.create_account(
        couchdb_session_admin=couchdb_session_admin,
        couchdb_baseurl=couchdb_baseurl,
        account=requested_user,
        password=requested_password,
    )
    if not response.ok:
        return response

    return {
        "user_name": requested_user,
        "database": migraine_shared.database.database_for_user(user=requested_user),
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
    _validate_secret_key(secret_key=request.json["secret_key"])

    # Obtain contents of the request
    requested_user = request.json["user_name"]

    #
    # Connect to the database
    #

    couchdb_baseurl = current_app.config["DATABASE_BASEURL"]
    couchdb_session_admin = _create_session(
        baseurl=couchdb_baseurl,
        user=current_app.config["DATABASE_ADMIN_USER"],
        password=current_app.config["DATABASE_ADMIN_PASSWORD"],
    )

    #
    # Validate the state of the database
    #

    # ID of the user document and corresponding database
    user_doc_id = "org.couchdb.user:{}".format(requested_user)
    user_database = migraine_shared.database.database_for_user(user=requested_user)

    # Confirm the user exists
    response = couchdb_session_admin.get(
        urljoin(couchdb_baseurl, "_users/{}".format(user_doc_id)),
    )
    if not response.ok:
        abort(404, jsonify(message="User not found."))  # 404 Not Found

    # User exists, confirm database exists
    response = couchdb_session_admin.head(
        urljoin(couchdb_baseurl, user_database),
    )
    if not response.ok:
        abort(404, jsonify(message="Database not found."))  # 404 Not Found

    # Return the profile
    return {"user_name": requested_user, "database": user_database}


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
    _validate_secret_key(secret_key=request.json["secret_key"])

    #
    # Connect to the database
    #

    baseurl = current_app.config["DATABASE_BASEURL"]
    admin_session = _create_session(
        baseurl=baseurl,
        user=current_app.config["DATABASE_ADMIN_USER"],
        password=current_app.config["DATABASE_ADMIN_PASSWORD"],
    )

    # Get all users.
    # https://docs.couchdb.org/en/stable/intro/security.html#authentication-database
    response = admin_session.get(
        urljoin(baseurl, "_users/{}".format("_all_docs")),
    )
    response.raise_for_status()

    # For each element in the list of _user documents, check if 'id' starts with 'org.couchdb.user:""
    #
    # This would be easier to read with a small regex match test, but this is fine for now.
    user_name_prefix = "org.couchdb.user:"
    return [
        user["id"].split(user_name_prefix)[1]
        for user in response.json()["rows"]
        if user_name_prefix in user["id"]
    ]
