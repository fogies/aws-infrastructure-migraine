class Config:
    SECRET_KEY: str
    """
    SECRET_KEY is required by Flask, used for signing session cookies.
    """

    CLIENT_SECRET_KEY: str
    """
    Used to limit access to the server, required when accessing any endpoints.
    """

    URI_DATABASE: str
    """
    URL of the database.
    """

    DB_USER: str
    """
    Admin user for the database.
    """

    DB_PASSWORD: str
    """
    Admin password for the database.
    """

    def __init__(
        self,
        secret_key: str,
        client_secret_key: str,
        uri_database: str,
        db_user: str,
        db_password: str,
    ):
        """
        Using an explicit constructor so it is clear fields are required.
        """

        self.SECRET_KEY = secret_key
        self.CLIENT_SECRET_KEY = client_secret_key
        self.URI_DATABASE = uri_database
        self.DB_USER = db_user
        self.DB_PASSWORD = db_password
