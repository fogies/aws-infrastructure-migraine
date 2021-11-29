from pathlib import Path
from typing import Union

from config.base import Config
import migraine_shared.config


class ProductionConfig(Config):
    def __init__(self, *, instance_dir: Union[Path, str]):
        flask_config_path = Path(instance_dir, "flask_config.yaml")
        flask_config = migraine_shared.config.FlaskConfig.load(flask_config_path=flask_config_path)

        Config.__init__(
            self=self,
            secret_key=flask_config.secret_key,
            database_baseurl=flask_config.database_baseurl,
            database_admin_user=flask_config.database_admin_user,
            database_admin_password=flask_config.database_admin_password,
        )
