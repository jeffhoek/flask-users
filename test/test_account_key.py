from unittest.mock import patch
from flask_users.account_key import get_account_key
from httmock import HTTMock, all_requests, response


def test_get_account_key_200():
    @all_requests
    def callback_mock(*args, **kwargs):
        return response(200)

    with HTTMock(callback_mock):
        result = get_account_key('janedoe@example.com', 'abc123')
        assert type(result) == int


@patch('time.sleep', return_value=None)
def test_exceeds_num_retries(patched_sleep):
    @all_requests
    def callback_mock(*args, **kwargs):
        return response(500)

    with HTTMock(callback_mock):
        result = get_account_key('janedoe@example.com', 'abc123')
        assert result <= 100
