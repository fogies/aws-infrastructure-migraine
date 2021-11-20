from invoke import Collection
from invoke import task
import requests
import requests.auth
import requests.exceptions
from urllib.parse import urljoin

from migraine_shared.config import CouchDBConfig

# TODO prod/dev
COUCHDB_CLIENT_CONFIG_PATH = './secrets/configuration/dev_couchdb.yaml'


@task
def initialize(context):
    """
    Initialize the database.
    """

    #
    # Obtain our connection information and admin credentials
    #
    couchdb_client_config = CouchDBConfig.load(
        couchdb_config_path=COUCHDB_CLIENT_CONFIG_PATH
    )
    admin_auth = requests.auth.HTTPBasicAuth(
        username=couchdb_client_config.admin_user,
        password=couchdb_client_config.admin_password
    )

    #
    # Ensure the database is initialized
    #
    try:
        # Confirm the database is online
        response = requests.get(
            urljoin(couchdb_client_config.baseurl, ''),
        )
        response.raise_for_status()

        # Check whether the cluster has previously been finished (i.e., in a previous initialize)
        response = requests.get(
            urljoin(couchdb_client_config.baseurl, '_cluster_setup'),
            auth=admin_auth,
        )
        response.raise_for_status()

        # If the cluster was not finished in a previous initialize, do that now
        if response.json()['state'] != 'cluster_finished':
            response = requests.post(
                urljoin(couchdb_client_config.baseurl, '_cluster_setup'),
                json={
                    'action': 'finish_cluster'
                },
                auth=admin_auth,
            )
            response.raise_for_status()
    except requests.exceptions.HTTPError as error:
        print(error)


ns = Collection('database')
ns.add_task(initialize, 'initialize')
