import requests
import requests.auth
from urllib.parse import urljoin

import migraine_shared.config
from tests.test_flask_config import flask_config


def test_flask_reachable(flask_config: migraine_shared.config.FlaskConfig):
    """
    Test Flask is responding at expected baseurl.
    """

    session = requests.session()
    response = session.get(
        urljoin(flask_config.baseurl, ''),
    )
    assert response.ok
