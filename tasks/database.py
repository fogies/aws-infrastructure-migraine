from aws_infrastructure.tasks.collection import compose_collection
import migraine_shared.config
from invoke import Collection
from invoke import task
import requests
import requests.auth
import requests.exceptions
from urllib.parse import urljoin

from migraine_shared.config import CouchDBConfig

DEV_COUCHDB_CONFIG_PATH = "./secrets/configuration/dev_couchdb.yaml"
PROD_COUCHDB_CONFIG_PATH = "./secrets/configuration/prod_couchdb.yaml"


def _initialize(couchdb_config: migraine_shared.config.CouchDBConfig):
    """
    Helper to initialize a database.
    """
    # Confirm the database is online
    response = requests.get(
        urljoin(couchdb_config.baseurl, ''),
    )
    response.raise_for_status()

    # Create basic authentication credentials as the administrator
    admin_auth = requests.auth.HTTPBasicAuth(
        username=couchdb_config.admin_user,
        password=couchdb_config.admin_password
    )

    # Check whether the cluster has previously been finished (i.e., in a previous initialize)
    response = requests.get(
        urljoin(couchdb_config.baseurl, '_cluster_setup'),
        auth=admin_auth,
    )
    response.raise_for_status()

    # If the cluster was not finished in a previous initialize, do that now
    if response.json()['state'] != 'cluster_finished':
        response = requests.post(
            urljoin(couchdb_config.baseurl, '_cluster_setup'),
            json={
                'action': 'finish_cluster'
            },
            auth=admin_auth,
        )
        response.raise_for_status()


@task
def dev_initialize(context):
    """
    Initialize the database.
    """
    couchdb_config = CouchDBConfig.load(
        couchdb_config_path=DEV_COUCHDB_CONFIG_PATH
    )
    _initialize(couchdb_config=couchdb_config)


@task
def prod_initialize(context):
    """
    Initialize the database.
    """
    couchdb_config = CouchDBConfig.load(
        couchdb_config_path=PROD_COUCHDB_CONFIG_PATH
    )
    _initialize(couchdb_config=couchdb_config)


# Build task collection
ns = Collection('database')

ns_dev = Collection('dev')
ns_dev.add_task(dev_initialize, 'initialize')

ns_prod = Collection('prod')
ns_prod.add_task(prod_initialize, 'initialize')

compose_collection(ns, ns_dev, name='dev')
compose_collection(ns, ns_prod, name='prod')
