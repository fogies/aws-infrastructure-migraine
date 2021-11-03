import requests
import requests.auth
import requests.exceptions
from urllib.parse import urljoin


class CouchDBClientConfig:
    """
    Configuration for connection to a CouchDB instance.
    """

    _baseurl: str
    _admin_password: str
    _admin_user: str

    def __init__(self, *, baseurl: str, admin_user: str, admin_password: str):
        self._baseurl = baseurl
        self._admin_user = admin_user
        self._admin_password = admin_password

    @staticmethod
    def load(baseurl: str, admin_user: str, admin_password: str):

        return CouchDBClientConfig(
            baseurl=baseurl,
            admin_user=admin_user,
            admin_password=admin_password,
        )

    @staticmethod
    def initialize(self):
        """
        Initialize the database. Picked this method from tasks.database. Not being used in flask at the moment. Might want to move to aws-infrastructure code at some point. 
        """
        #
        # Obtain our connection information and admin credentials
        #
        admin_auth = requests.auth.HTTPBasicAuth(
            username=self._admin_user,
            password=self._admin_password
        )

        #
        # Ensure the database is initialized
        #
        try:
            # Confirm the database is online
            response = requests.get(
                urljoin(self._baseurl, ''),
            )
            response.raise_for_status()

            # Check whether the cluster has previously been finished (i.e., in a previous initialize)
            response = requests.get(
                urljoin(self._baseurl, '_cluster_setup'),
                auth=admin_auth,
            )
            response.raise_for_status()

            # If the cluster was not finished in a previous initialize, do that now
            if response.json()['state'] != 'cluster_finished':
                response = requests.post(
                    urljoin(self._baseurl, '_cluster_setup'),
                    json={
                        'action': 'finish_cluster'
                    },
                    auth=admin_auth,
                )
                response.raise_for_status()
        except requests.exceptions.HTTPError as error:
            print(error)

    @property
    def admin_password(self) -> str:
        return self._admin_password

    @property
    def admin_user(self) -> str:
        return self._admin_user

    @property
    def baseurl(self) -> str:
        return self._baseurl
