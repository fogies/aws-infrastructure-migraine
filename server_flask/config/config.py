class Config:
    SECRET_KEY: str
    """
    SECRET_KEY is required by Flask, used for signing session cookies.
    """

    CLIENT_SECRET_KEY: str
    """
    Used to limit access to the server, required when accessing any endpoints.
    """

    DB_BASEURL: str
    """
    URL of the database.
    """

    DB_ADMIN_USER: str
    """
    Admin user for the database.
    """

    DB_ADMIN_PASSWORD: str
    """
    Admin password for the database.
    """

    def __init__(
        self,
        secret_key: str,
        client_secret_key: str,
        db_baseurl: str,
        db_admin_user: str,
        db_admin_password: str,
    ):
        """
        Using an explicit constructor so it is clear fields are required.
        """

        self.SECRET_KEY = secret_key
        self.CLIENT_SECRET_KEY = client_secret_key
        self.DB_BASEURL = DB_BASEURL
        self.DB_ADMIN_USER = db_admin_user
        self.DB_ADMIN_PASSWORD = db_admin_password
