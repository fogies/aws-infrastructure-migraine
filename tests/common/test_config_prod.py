"""
Configuration for testing against only production.
"""

import pytest

import migraine_shared.testing
import tests.common.test_config

test_config = migraine_shared.testing.create_test_config(
    configs=tests.common.test_config.PROD_CONFIG
)

couchdb_config = migraine_shared.testing.create_couchdb_config(test_config=test_config)
couchdb_session_admin = migraine_shared.testing.create_couchdb_session_admin(couchdb_config=couchdb_config)
test_couchdb_session_admin = migraine_shared.testing.create_test_couchdb_session_admin(couchdb_config=couchdb_config)

flask_config = migraine_shared.testing.create_flask_config(test_config=test_config)
flask_session_unauthenticated = migraine_shared.testing.create_flask_session_unauthenticated(flask_config=flask_config)
test_flask_session_unauthenticated = migraine_shared.testing.create_test_flask_session_unauthenticated(flask_config=flask_config)
