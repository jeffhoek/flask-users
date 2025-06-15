import pytest
from unittest.mock import patch

from pymongo import MongoClient
from pymongo.results import InsertOneResult
from pymongo.errors import DuplicateKeyError
from httmock import HTTMock, all_requests

from flask_users.app import app, initialize_collection, USERS_DB_NAME
from flask_users.tasks import celery_app


USERS_API_BASE = 'http://localhost:5001/v1/users'

MONGO_HOST = 'localhost'
TEST_COLLECTION = 'users_test'


def setup_module():
    celery_app.conf.update(task_always_eager=True)


def teardown_function():
    client = MongoClient(MONGO_HOST, 27017)
    client[USERS_DB_NAME][TEST_COLLECTION].drop()


@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['mongo_host'] = MONGO_HOST
    app.config['db_name'] = USERS_DB_NAME
    app.config['collection_name'] = TEST_COLLECTION

    initialize_collection(app)

    client = app.test_client()

    yield client


def test_internal_server_error(client):
    """
    Test internal server error
    :param client: Flask test client
    """
    def my_side_effect(dummy_arg):
        raise Exception

    with patch('flask_users.app.get_user_query', side_effect=my_side_effect):
        response = client.get(USERS_API_BASE)
        assert response.status_code == 500


def test_backend_server_error(client):
    """
    Test internal server error from pymongo
    :param client: Flask test client
    """
    def my_side_effect(dummy_arg):
        result = InsertOneResult(None, False)
        return result

    with patch('pymongo.collection.Collection.insert_one', side_effect=my_side_effect):
        user = {
            'full_name': 'Jane Doe',
            'email': 'janedoe@example.com',
            'metadata': 'age 30, hobbies sewing skiing',
            'password': 'pass123#'
        }
        response = client.post(USERS_API_BASE, json=user)
        assert response.status_code == 500


def test_get_users(client):
    """
    Test GET /v1/users
    :param client: Flask test client
    """
    response = client.get(USERS_API_BASE)
    assert response.status_code == 200


def test_post_missing_json(client):
    response = client.post(USERS_API_BASE)
    assert response.status_code == 422


def test_get_post(client):
    """
    Test POST /v1/users
    :param client: Flask test client
    """
    @all_requests
    def callback_mock(*args, **kwargs):
        return response(status_code=200, content={'account_key': '1234567890'})

    with HTTMock(callback_mock):

        user = {
            'full_name': 'Jane Doe',
            'email': 'janedoe@example.com',
            'metadata': 'age 30, hobbies sewing skiing',
            'password': 'pass123#'
        }
        response = client.post(USERS_API_BASE, json=user)
        assert response.status_code == 201

        response = client.get(USERS_API_BASE)
        assert response.status_code == 200
        users = response.json.get('users')
        assert len(users) == 1

        response = client.get(USERS_API_BASE + '?query=miss')
        assert response.status_code == 200

        response = client.get(USERS_API_BASE + '?query=sewing')
        assert response.status_code == 200
        users = response.json.get('users')
        assert len(users) == 1
        assert 'sewing' in users[0].get('metadata')

        user = {
            'junk': 'Unprocessable entity'
        }
        response = client.post(USERS_API_BASE, json=user)
        assert response.status_code == 422

        user = {
            'full_name': 'John Doe',
            'email': 'johndoe@example.com',
            'metadata': 'age 25, hobbies computers cards coins',
            'password': 'pass123#'
        }
        response = client.post(USERS_API_BASE, json=user)
        assert 201 == response.status_code

        response = client.get(USERS_API_BASE + '?query=doe')
        assert 200 == response.status_code
        users = response.json.get('users')
        assert 2 == len(users)


def test_unique_email_constraint(client):
    """
    Test unique email constraint
    :param client: Flask test app
    """
    @all_requests
    def callback_mock(*args, **kwargs):
        return response(status_code=200, content={'account_key': '1234567890'})

    with HTTMock(callback_mock):
        user = {
            'full_name': 'Jane Doe',
            'email': 'janedoe@example.com',
            'metadata': 'age 30, hobbies sewing skiing',
            'password': 'pass123#'
        }
        response = client.post(USERS_API_BASE, json=user)
        assert 201 == response.status_code

        response = client.post(USERS_API_BASE, json=user)
        assert 422 == response.status_code

        user['email'] = 'janedoe123@example.com'
        response = client.post(USERS_API_BASE, json=user)
        assert 201 == response.status_code


def test_field_constraints(client):
    """
    Test model constraints validations
    :param client: Flask test app
    """
    user = {
        'full_name': 'x'*201,
        'email': 'janedoe@example.com',
        'metadata': 'age 30, hobbies sewing skiing',
        'password': 'pass123#'
    }
    response = client.post(USERS_API_BASE, json=user)
    assert 422 == response.status_code

    user['email'] = 'y'*201 + '@example.com'
    response = client.post(USERS_API_BASE, json=user)
    assert 422 == response.status_code

    user['metadata'] = 'm'*2001
    user['password'] = 'p'*101
    response = client.post(USERS_API_BASE, json=user)
    assert 422 == response.status_code
    errors = response.json.get('errors')
    assert 3 == len(errors)
    for err in errors:
        assert 'too long' in err


def test_duplicate_key_missing(client):
    """
    Test unique key handlers
    :param client: Flask test app
    """
    def my_side_effect(dummy_arg):
        dke = DuplicateKeyError('duplicate key error',
                                code=11000,
                                details={'errmsg': 'E11000 duplicate key ... missing_key ...'})
        raise dke

    user = {
        'email': 'janedoe@example.com',
        'password': 'pass123#'
    }
    response = client.post(USERS_API_BASE, json=user)
    assert 201 == response.status_code

    with patch('pymongo.collection.Collection.insert_one', side_effect=my_side_effect):
        response = client.post(USERS_API_BASE, json=user)
        assert 500 == response.status_code


def test_rogue_fields(client):
    """
    Test model validation with unexpected rogue fields
    :param client: Flask test app
    """
    user = {
        'abracadabra': 'john doe',
        'email': 'janedoe@example.com',
        'metadata': 'age 30, hobbies sewing skiing',
        'password': 'pass123#'
    }
    response = client.post(USERS_API_BASE, json=user)
    assert 422 == response.status_code
    errors = response.json.get('errors')
    assert 1 == len(errors)
    assert 'Rogue' in errors[0]
