"""
Configuration for testing against both development and production.
"""

from pathlib import Path
import pytest
import requests

import migraine_shared.config
import tests.common.test_config


@pytest.fixture(
    params=[
        tests.common.test_config.DEV_COUCHDB_CONFIG_PATH,
        tests.common.test_config.PROD_COUCHDB_CONFIG_PATH,
    ]
)
def couchdb_config(request) -> migraine_shared.config.CouchDBConfig:
    """
    Fixture providing CouchDB configuration.
    """
    return tests.common.test_config.couchdb_config(Path(request.param))


@pytest.fixture
def couchdb_session_admin(couchdb_config: migraine_shared.config.CouchDBConfig) -> requests.Session:
    """
    Fixture providing session authenticated as administrator.
    """
    return tests.common.test_config.couchdb_session_admin(couchdb_config=couchdb_config)


@pytest.fixture(
    params=[
        tests.common.test_config.DEV_FLASK_CONFIG_PATH,
        tests.common.test_config.PROD_FLASK_CONFIG_PATH,
    ]
)
def flask_config(request) -> migraine_shared.config.FlaskConfig:
    """
    Fixture providing Flask configuration.
    """
    return tests.common.test_config.flask_config(Path(request.param))
