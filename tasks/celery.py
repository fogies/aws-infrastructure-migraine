"""
Tasks for the Celery worker.
"""

from aws_infrastructure.tasks.collection import compose_collection
from invoke import Collection
from invoke import task
from pathlib import Path

from tasks.terminal import spawn_new_terminal


CELERY_DIR = './server_celery'


@task
def dev_serve(context):
    """
    Start Celery.

    For development purposes, asynchronously starts in a new terminal.
    """

    if spawn_new_terminal(context):
        with context.cd(Path(CELERY_DIR)):
            context.run(
                command=' '.join([
                    'pipenv',
                    'run',
                    'python',
                    'app.py',
                    # '-A app',
                    'worker',
                    '-l info',
                    '--concurrency=1',
                    '--pool=gevent',
                ]),
            )


# Build task collection
ns = Collection('celery')

ns_dev = Collection('dev')
ns_dev.add_task(dev_serve, 'serve')

ns_prod = Collection('prod')

compose_collection(ns, ns_dev, name='dev')
compose_collection(ns, ns_prod, name='prod')
