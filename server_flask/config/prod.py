import os


class Config:
    # TODO: Secret key will need to be shared across instances
    SECRET_KEY = os.urandom(16)

    # TODO Production Config
