class CouchDBClientConfig:
    """
    Configuration for connection to a CouchDB instance.
    """

    _baseurl: str
    _password: str
    _user: str

    def __init__(self, *, baseurl: str, user: str, password: str):
        self._baseurl = baseurl
        self._user = user
        self._password = password

    @property
    def baseurl(self) -> str:
        return self._baseurl

    @property
    def password(self) -> str:
        return self._password

    @property
    def user(self) -> str:
        return self._user
