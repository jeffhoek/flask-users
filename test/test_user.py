from flask_users.user import User
from schematics.exceptions import DataError
from nose.tools import raises
import nose.tools


def test_user():
    u = User({
        'email': 'janedoe@example.com',
        'full_name': 'my full name',
        'account_key': 'abc123',
        'password': 'pass123*'
    })
    u.validate()


@raises(DataError)
def test_user_required():
    try:
        u = User({
            'full_name': 'my full name',
            'account_key': 'abc123'
        })
        u.validate()
    except DataError as e:
        error_dict = e.to_primitive()
        nose.tools.assert_in('email', error_dict)
        nose.tools.assert_in('field is required', error_dict.get('email')[0])
        nose.tools.assert_in('password', error_dict)
        nose.tools.assert_in('field is required', error_dict.get('password')[0])
        raise


@raises(DataError)
def test_user_rogue():
    try:
        u = User({
            'rogue': 'field',
            'email': 'janedoe@example.com',
            'full_name': 'my full name',
            'account_key': 'abc123'
        })
        u.validate()
    except DataError as e:
        error_dict = e.to_primitive()
        nose.tools.assert_in('Rogue field', error_dict.get('rogue'))
        raise


@raises(DataError)
def test_user_exceeds_max_length():
    try:
        u = User({
            'email': 'x'*300,
            'full_name': 'my full name',
            'account_key': 'abc123',
            'password': 'pass456*'
        })
        u.validate()
    except DataError as e:
        error_dict = e.to_primitive()
        nose.tools.assert_in('email', error_dict.keys())
        nose.tools.assert_in('String value is too long.', error_dict.get('email'))
        nose.tools.assert_in('Not a well-formed email address.', error_dict.get('email'))
        raise


def test_user_blacklist_fields():
    u = User({
        'email': 'janedoe@example.com',
        'account_key': 'abc123',
        '_id': '1234567890'
    })
    serialized = u.to_native()
    nose.tools.assert_not_in('_id', list(serialized.keys()))
    pass

