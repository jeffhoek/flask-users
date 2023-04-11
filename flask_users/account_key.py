import functools
import requests
import time


SERVICE_URL = 'https://bc-account-service.mybluemix.net/v1/accounts'


def retry_request(func, num_retries=5):
    """
    Decorator for retrying request with exponential backoff.
    :param func: decorated function
    :param num_retries: number of retries
    :return: wrapped func
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        response = None
        for attempt in range(num_retries):
            response = func(*args, **kwargs)
            if response.status_code == 500:
                time.sleep(2**attempt)
                continue
            return response

        return response

    return wrapper


@retry_request
def get_account_key(email, user_id):
    """
    Fetch account key from service
    :param email: email
    :param user_id: user ID
    :return: requests Response
    """
    post_json = {
        'email': email,
        'user_id': user_id
    }
    response = requests.post(SERVICE_URL, json=post_json)
    return response
