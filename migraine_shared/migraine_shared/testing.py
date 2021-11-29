"""
Utilities for configuring testing.
"""

from dataclasses import dataclass
from pathlib import Path
import pytest
import requests
from typing import List
from urllib.parse import urljoin

import migraine_shared.config


@dataclass(frozen=True)
class TestingConfig:
    couchdb_config_path: Path
    flask_config_path: Path


def create_test_config(*, configs: List[TestingConfig]):
    """
    Create a fixture to provide test configuration.
    """
    @pytest.fixture(params=configs)
    def test_config(request) -> TestingConfig:
        return request.param

    return test_config

def create_couchdb_config(*, test_config):
    """
    Create a fixture to provide CouchDB configuration.
    """
    assert test_config

    @pytest.fixture
    def couchdb_config(test_config: TestingConfig) -> migraine_shared.config.CouchDBConfig:
        """
        Fixture to provide CouchDB configuration.
        """
        return migraine_shared.config.CouchDBConfig.load(
            couchdb_config_path=test_config.couchdb_config_path
        )

    return couchdb_config

def _couchdb_session_admin(couchdb_config: migraine_shared.config.CouchDBConfig) -> requests.Session:
    """
    Helper for creating couchdb_session_admin.
    """
    # Obtain a session
    session = requests.Session()

    # Confirm the database is reachable
    session = requests.session()
    response = session.get(
        urljoin(couchdb_config.baseurl, ''),
    )
    assert response.ok

    # Authenticate the session
    response = session.post(
        urljoin(couchdb_config.baseurl, "_session"),
        json={
            "name": couchdb_config.admin_user,
            "password": couchdb_config.admin_password,
        },
    )
    assert response.ok

    # Only an administrator can access the _users database
    response = session.get(
        urljoin(couchdb_config.baseurl, "_users"),
    )
    assert response.ok

    return session

def create_couchdb_session_admin(*, couchdb_config):
    """
    Create a fixture to provide a session authenticated as administrator.
    """
    assert couchdb_config

    @pytest.fixture
    def couchdb_session_admin(couchdb_config: migraine_shared.config.CouchDBConfig) -> requests.Session:
        """
        Fixture providing a session authenticated as administrator.

        This will xfail if _couchdb_session_admin fails, so all tests based on it will xfail.
        """
        try:
            session = _couchdb_session_admin(couchdb_config=couchdb_config)
        except AssertionError:
            pytest.xfail("Failed to create couchdb_session_admin")

        return session

    return couchdb_session_admin

def create_test_couchdb_session_admin(*, couchdb_config):
    """
    Create a test for creation of couchdb_session_admin.
    """
    assert couchdb_config

    def test_couchdb_session_admin(couchdb_config: migraine_shared.config.CouchDBConfig):
        """
        Test creation of couchdb_session_admin.

        Because couchdb_session_admin will xfail if this fails,
        this test provides an indication of why couchdb_session_admin is failing.
        """
        _couchdb_session_admin(couchdb_config=couchdb_config)

    return test_couchdb_session_admin

def create_flask_config(*, test_config):
    """
    Create a fixture to provide Flask configuration.
    """
    assert test_config

    @pytest.fixture
    def flask_config(test_config: TestingConfig) -> migraine_shared.config.FlaskConfig:
        """
        Fixture to provide Flask configuration.
        """
        return migraine_shared.config.FlaskConfig.load(
            flask_config_path=test_config.flask_config_path
        )

    return flask_config

def _flask_session_unauthenticated(flask_config: migraine_shared.config.FlaskConfig) -> requests.Session:
    """
    Helper for creating flask_session_unauthenticated.
    """
    # Obtain a session
    session = requests.Session()

    # Confirm Flask is reachable
    session = requests.session()
    response = session.get(
        urljoin(flask_config.baseurl, ''),
    )
    assert response.ok

    return session

def create_flask_session_unauthenticated(*, flask_config):
    """
    Create a fixture to provide a session that is not authenticated.
    """
    assert flask_config

    @pytest.fixture
    def flask_session_unauthenticated(flask_config: migraine_shared.config.FlaskConfig) -> requests.Session:
        """
        Fixture providing a session that is not authenticated.

        This will xfail if _flask_session_unauthenticated fails, so all tests based on it will xfail.
        """
        try:
            session = _flask_session_unauthenticated(flask_config=flask_config)
        except AssertionError:
            pytest.xfail("Failed to create flask_session_unauthenticated")

        return session

    return flask_session_unauthenticated

def create_test_flask_session_unauthenticated(*, flask_config):
    """
    Create a test for creation of flask_session_unauthenticated.
    """
    assert flask_config

    def test_flask_session_unauthenticated(flask_config: migraine_shared.config.FlaskConfig):
        """
        Test creation of flask_session_unauthenticated.

        Because flask_session_unauthenticated will xfail if this fails,
        this test provides an indication of why flask_session_unauthenticated is failing.
        """
        _flask_session_unauthenticated(flask_config=flask_config)

    return test_flask_session_unauthenticated
