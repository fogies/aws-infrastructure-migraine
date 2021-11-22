from pathlib import Path
from typing import Union

from config.base import Config
import migraine_shared.config


# Path is relative to server_flask
TEMPORARY_FLASK_CONFIG_PATH = "../secrets/configuration/prod_flask.yaml"


class ProductionConfig(Config):
    def __init__(self, *, instance_dir: Union[Path, str]):
        print("loading from:")
        print(instance_dir)
        flask_config = migraine_shared.config.FlaskConfig.load(TEMPORARY_FLASK_CONFIG_PATH)

        Config.__init__(
            self=self,
            secret_key=flask_config.secret_key,
            database_baseurl=flask_config.database_baseurl,
            database_admin_user=flask_config.database_admin_user,
            database_admin_password=flask_config.database_admin_password,
        )
