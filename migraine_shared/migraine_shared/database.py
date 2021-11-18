import hashlib
import re

def database_for_user(*, user: str):
    """
    Obtain the name of the database for a specified user.

    CouchDB requirement of database names:
    - Only lowercase characters (a-z), digits (0-9), and any of the characters _$()+-/ are allowed.
    - Must begin with a letter.

    Database names will therefore be 'user_' followed by hex encoding of an MD5 hash of the user name.
    """

    return 'user_{}'.format(hashlib.md5(user.encode('utf-8')).digest().hex())


def validate_user(*, user: str) -> bool:
    """
    Determine whether a provided user name is allowable.

    At least characters :+ are not allowed in CouchDB user names, possibly others.
    Instead of requiring encoding of user names, require that names are alphanumeric with ._ allowed.
    """

    # Forbid user that start with 'user_', as that conflicts with our database encoding
    if user.startswith('user_'):
        return False

    # Limit to 32 characters, just to avoid any issues
    if len(user) > 32:
        return False

    return re.match(pattern='^[a-zA-Z0-9_.]+$', string=user) is not None
