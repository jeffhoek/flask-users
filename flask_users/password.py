import hashlib
import uuid


def encrypt_password(password):
    """
    Salt and hash password
    :param password: client supplied password
    :return: tuple of (salt, hashed-salted password)
    """
    salt = uuid.uuid4().hex
    salt_password = salt + password
    hash_salt_pswd = hashlib.md5(salt_password.encode())
    return salt, hash_salt_pswd.hexdigest()


def check_password(password, salt, hash_salt_password):
    """
    Check the password matches the hashed-salted password
    :param password: client password to check
    :param salt: password salt used during creation
    :param hash_salt_password: previously hashed-salted password
    :return: True if passwords match otherwise False
    """
    salt_password = salt + password
    check_hash_salt_pswd = hashlib.md5(salt_password.encode())
    if check_hash_salt_pswd.hexdigest() != hash_salt_password:
        return False
    return True
