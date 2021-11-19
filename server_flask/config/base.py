class Config:
    SECRET_KEY: str
    """
    SECRET_KEY is required by Flask, used for signing session cookies.
    
    We also use it to limit access to the server, require it when accessing any endpoint. 
    """

    DATABASE_BASEURL: str
    """
    URL of the database.
    """

    DATABASE_ADMIN_USER: str
    """
    Admin user for the database.
    """

    DATABASE_ADMIN_PASSWORD: str
    """
    Admin password for the database.
    """

    def __init__(
        self,
        secret_key: str,
        database_baseurl: str,
        database_admin_user: str,
        database_admin_password: str,
    ):
        """
        Using an explicit constructor so it is clear fields are required.
        """

        self.SECRET_KEY = secret_key
        self.DATABASE_BASEURL = database_baseurl
        self.DATABASE_ADMIN_USER = database_admin_user
        self.DATABASE_ADMIN_PASSWORD = database_admin_password
