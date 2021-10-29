import os


class Config:
    # TODO: Secret key will need to be shared across instances
    SECRET_KEY = os.urandom(16)

    # Database is in service `scope-database-svc-couchdb` on port 5984
    URI_DATABASE = ''
