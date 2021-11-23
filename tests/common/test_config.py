from pathlib import Path

import migraine_shared.testing

DEV_CONFIG = [
    migraine_shared.testing.TestingConfig(
        couchdb_config_path=Path("./secrets/configuration/dev_couchdb.yaml"),
        flask_config_path=Path("./secrets/configuration/dev_flask.yaml"),
    )
]

PROD_CONFIG = [
    migraine_shared.testing.TestingConfig(
        couchdb_config_path=Path("./secrets/configuration/prod_couchdb.yaml"),
        flask_config_path=Path("./secrets/configuration/prod_flask.yaml"),
    )
]

ALL_CONFIG = DEV_CONFIG + PROD_CONFIG
