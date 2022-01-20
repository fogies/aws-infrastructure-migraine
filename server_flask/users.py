from flask import abort, Blueprint, current_app, Response
from flask import jsonify, request
from flask_json import as_json
import jsonschema
import requests
import requests.auth
import requests.exceptions
from typing import Dict
from urllib.parse import urljoin
from functools import wraps
import re
import json

import migraine_shared.database

from timeit import default_timer as timer


users_blueprint = Blueprint("users_blueprint", __name__)


ADMIN_SESSION = None
ADMIN_SESSION_CREATED_TIME = -10000


def _admin_session() -> requests.Session:
    """
    Obtain a session authenticated by the provided config.
    """

    global ADMIN_SESSION
    global ADMIN_SESSION_CREATED_TIME

    time_current = timer()
    if (time_current - ADMIN_SESSION_CREATED_TIME) > 120:  # 120 seconds
        # Authentication object for our request
        auth = requests.auth.HTTPBasicAuth(
            username=current_app.config["DATABASE_ADMIN_USER"],
            password=current_app.config["DATABASE_ADMIN_PASSWORD"],
        )

        # Open a session
        session = requests.Session()
        response = session.post(
            urljoin(current_app.config["DATABASE_BASEURL"], "_session"),
            json={
                "name": auth.username,
                "password": auth.password,
            },
        )
        response.raise_for_status()

        ADMIN_SESSION = session
        ADMIN_SESSION_CREATED_TIME = time_current

    return ADMIN_SESSION


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


def secure(f):
    """
    Decorator function to validate the Bearer token in authorization header.

    Raise 403 on secret key mismatch or if secret key is missing in authorization header.
    """

    @wraps(f)
    def check_authorization_bearer(*args, **kwargs):
        try:
            # Check if request headers have 'Authorization: Bearer <secret_key>'
            assert (
                re.match("Bearer\s(.*)", request.headers.get("Authorization")).group(1)
                == current_app.config["SECRET_KEY"]
            )
        except:
            abort(403, jsonify(message="Invalid secret key."))  # 403 Forbidden

        return f(*args, **kwargs)

    return check_authorization_bearer


@users_blueprint.route("/", methods=["GET"])
@as_json
@secure
def get_users():
    """
    GET all users

    Returns:
        {"users": [list of users]}
    """
    #
    # Connect to the database
    #

    baseurl = current_app.config["DATABASE_BASEURL"]
    admin_session = _admin_session()

    # Get all users.
    # https://docs.couchdb.org/en/stable/intro/security.html#authentication-database
    response = admin_session.get(
        urljoin(baseurl, "_users/{}".format("_all_docs")),
    )
    response.raise_for_status()

    # For each element in the list of _user documents, check if 'id' starts with 'org.couchdb.user:'
    regex_match_string = "org.couchdb.user:(.*)"
    return {
        "users": [
            re.match(regex_match_string, user["id"]).group(1)
            for user in response.json()["rows"]
            if re.match(regex_match_string, user["id"])
        ]
    }


@users_blueprint.route("/<string:user_name>", methods=["GET"])
@as_json
@secure
def get_user(user_name):
    """
    GET user_name from couchdb

    Args:
        user_name ([string]): [User name]

    Returns:
    {
        "user_name": user_name,
        "database": "existing database for the user."
    }
    """
    #
    # Connect to the database
    #
    baseurl = current_app.config["DATABASE_BASEURL"]
    admin_session = _admin_session()

    #
    # Validate the state of the database
    #

    # ID of the user document and corresponding database
    user_doc_id = "org.couchdb.user:{}".format(user_name)
    user_database = migraine_shared.database.database_for_user(user=user_name)

    # Confirm the user exists
    response = admin_session.get(
        urljoin(baseurl, "_users/{}".format(user_doc_id)),
    )
    if not response.ok:
        abort(404, jsonify(message="User not found."))  # 404 Not Found

    # User exists, confirm database exists
    response = admin_session.head(
        urljoin(baseurl, user_database),
    )
    if not response.ok:
        abort(404, jsonify(message="Database not found."))  # 404 Not Found

    # Return the profile
    return {"user_name": user_name, "database": user_database}


# Create a user in couchdb
@users_blueprint.route("/", methods=["POST"])
@as_json
@secure
def create_user():
    """
    Create user account.

    Body params:
    {
        "user_name": <>,
        "user_password": <>,
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

    schema = {
        "type": "object",
        "properties": {
            "user_name": {"type": "string"},
            "user_password": {"type": "string"},
        },
        "required": ["user_name", "user_password"],
    }
    _validate_request_json_schema(instance=request.json, schema=schema)

    # Obtain contents of the request
    requested_user = request.json["user_name"]
    requested_password = request.json["user_password"]

    #
    # Connect to the database
    #

    baseurl = current_app.config["DATABASE_BASEURL"]
    admin_session = _admin_session()

    #
    # Create the user and their database
    #

    response = migraine_shared.database.create_account(
        couchdb_session_admin=admin_session,
        couchdb_baseurl=baseurl,
        account=requested_user,
        password=requested_password,
    )

    if not response.ok:
        # Flask can return an object of type flask.wrappers.Response.
        return Response(
            response=json.dumps(response.reason),
            status=response.status_code,
            headers=dict(response.headers),
            mimetype="application/json",
        )

    return {
        "user_name": requested_user,
        "database": migraine_shared.database.database_for_user(user=requested_user),
    }
