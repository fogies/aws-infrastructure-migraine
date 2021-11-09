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

    @property
    def admin_password(self) -> str:
        return self._admin_password

    @property
    def admin_user(self) -> str:
        return self._admin_user

    @property
    def baseurl(self) -> str:
        return self._baseurl
