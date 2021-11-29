"""
Configuration for testing against both development and production.
"""

import migraine_shared.testing
import tests.common.test_config

test_config = migraine_shared.testing.create_test_config(
    configs=tests.common.test_config.ALL_CONFIG
)

couchdb_config = migraine_shared.testing.create_couchdb_config(test_config=test_config)
couchdb_session_admin = migraine_shared.testing.create_couchdb_session_admin(couchdb_config=couchdb_config)
# Tested in test_config_dev and test_config_prod
# test_couchdb_session_admin = migraine_shared.testing.create_test_couchdb_session_admin(couchdb_config=couchdb_config)

flask_config = migraine_shared.testing.create_flask_config(test_config=test_config)
flask_session_unauthenticated = migraine_shared.testing.create_flask_session_unauthenticated(flask_config=flask_config)
# Tested in test_config_dev and test_config_prod
# test_flask_session_unauthenticated = migraine_shared.testing.create_test_flask_session_unauthenticated(flask_config=flask_config)
