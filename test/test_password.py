from flask_users.password import encrypt_password, check_password
import nose.tools


def test_encrypt_password():
    """
    Test password salt+hash and comparisons
    """
    test_password = 'pass123*'
    salt, encrypt_pswd = encrypt_password(test_password)

    nose.tools.assert_true(check_password(test_password, salt, encrypt_pswd))

    nose.tools.assert_false(check_password('pass123#', salt, encrypt_pswd))
