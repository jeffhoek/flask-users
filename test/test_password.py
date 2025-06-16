from flask_users.password import encrypt_password, check_password


def test_encrypt_password():
    """
    Test password salt+hash and comparisons
    """
    test_password = 'pass123*'
    salt, encrypt_pswd = encrypt_password(test_password)

    assert check_password(test_password, salt, encrypt_pswd) is True

    assert check_password('pass123#', salt, encrypt_pswd) is False
