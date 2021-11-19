import pytest

import migraine_shared.config

DEV_FLASK_CONFIG_PATH = "../secrets/configuration/dev_flask.yaml"
PROD_FLASK_CONFIG_PATH = "../secrets/configuration/prod_flask.yaml"


@pytest.fixture(
    params=[
        DEV_FLASK_CONFIG_PATH,
    ],
)
def flask_config_dev(request) -> migraine_shared.config.FlaskConfig:
    """
    Fixture providing only development Flask configurations.
    """

    return migraine_shared.config.FlaskConfig.load(request.param)


@pytest.fixture(
    params=[
        PROD_FLASK_CONFIG_PATH,
    ],
)
def flask_config_prod(request) -> migraine_shared.config.FlaskConfig:
    """
    Fixture providing only production Flask configurations.
    """

    return migraine_shared.config.FlaskConfig.load(request.param)


@pytest.fixture(
    params=[
        DEV_FLASK_CONFIG_PATH,
        PROD_FLASK_CONFIG_PATH,
    ],
)
def flask_config(request) -> migraine_shared.config.FlaskConfig:
    """
    Fixture providing all Flask configurations.
    """

    return migraine_shared.config.FlaskConfig.load(request.param)
