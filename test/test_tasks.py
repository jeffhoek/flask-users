from unittest.mock import patch
import nose.tools
from flask_users.tasks import async_get_account_key
from flask_users.tasks import celery_app
from httmock import HTTMock, all_requests, response
from pymongo import MongoClient

from flask_users.app import USERS_DB_NAME


MONGO_HOST = 'localhost'
TEST_COLLECTION = 'users_test'


def setup_module():
    celery_app.conf.update(task_always_eager=True)


def teardown_function():
    client = MongoClient(MONGO_HOST, 27017)
    client[USERS_DB_NAME][TEST_COLLECTION].drop()


def test_async_get_account_key_200():
    user = {
        'full_name': 'Jane Doe',
        'email': 'janedoe@example.com',
        'metadata': 'age 30, hobbies sewing skiing',
        'password': 'pass123#'
    }
    client = MongoClient(MONGO_HOST, 27017)
    users = client[USERS_DB_NAME][TEST_COLLECTION]
    result = users.insert_one(user)
    nose.tools.assert_true(result.acknowledged)

    test_id = user.pop('_id')
    test_account_key = '1234567890'

    @all_requests
    def callback_mock(*args, **kwargs):
        return response(status_code=200, content={'account_key': test_account_key})

    with HTTMock(callback_mock):
        async_result = async_get_account_key.delay(
            'abc@example.com', test_id, 'localhost', USERS_DB_NAME, TEST_COLLECTION)

        # ensure the account_key was added and matches our test ID
        result = users.find_one({'_id': test_id})
        nose.tools.assert_equal(test_account_key, result.get('account_key'))


@patch('time.sleep', return_value=None)
def test_async_get_account_key_500(patched_sleep):
    @all_requests
    def callback_mock(*args, **kwargs):
        return response(status_code=500)

    with HTTMock(callback_mock):
        async_result = async_get_account_key.delay(
            'abc@example.com', '12345678900', 'localhost', USERS_DB_NAME, TEST_COLLECTION)


def test_async_get_account_key_missing():
    @all_requests
    def callback_mock(*args, **kwargs):
        return response(status_code=200, content={})

    with HTTMock(callback_mock):
        async_result = async_get_account_key.delay(
            'abc@example.com', '12345678900', 'localhost', USERS_DB_NAME, TEST_COLLECTION)
