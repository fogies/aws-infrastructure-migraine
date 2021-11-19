"""
Tasks for executing tests within appropriate environments.
"""

from aws_infrastructure.tasks import compose_collection
import aws_infrastructure.tasks.library.tests
from invoke import Collection


CONFIG_KEY = 'test'
TESTS = {
    'all': aws_infrastructure.tasks.library.tests.Test(
        pipenv_pytest_dirs=[
            '.',
            './server_celery',
            './server_flask',
        ],
    ),
    'celery': aws_infrastructure.tasks.library.tests.Test(
        pipenv_pytest_dirs=[
            './server_celery',
        ],
    ),
    'flask': aws_infrastructure.tasks.library.tests.Test(
        pipenv_pytest_dirs=[
            './server_flask',
        ],
    ),
    'root': aws_infrastructure.tasks.library.tests.Test(
        pipenv_pytest_dirs=[
            '.',
        ],
    ),
}

ns = Collection('tests')

ns_dependencies = aws_infrastructure.tasks.library.tests.create_tasks(
    config_key=CONFIG_KEY,
    tests=TESTS,
)

compose_collection(
    ns,
    ns_dependencies,
    sub=False,
)
