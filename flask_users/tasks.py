import json
import logging
from pymongo import MongoClient
from celery import Celery
from bson import ObjectId
from flask_users.account_key import get_account_key
from flask_users.exception_handling import handle_exceptions


logger = logging.getLogger(__name__)


celery_app = Celery('tasks', broker='redis://redis:6379/0')


@handle_exceptions(None)
def update_document(users, user_id, account_key):
    result = users.find_one_and_update(
        {'_id': ObjectId(user_id)},
        update={'$set': {'account_key': account_key}}
    )
    logger.debug(result)
    return result


@celery_app.task
def async_get_account_key(user_email, user_id, host, db_name, collection_name):
    account_key = get_account_key(user_email, str(user_id))
    if not account_key:
        logger.warning('Could not get account key')
        return None

    client = MongoClient(host, 27017, serverSelectionTimeoutMS=2)
    users = client[db_name][collection_name]
    update_document(users, user_id, str(account_key))


# TODO implement an additional periodic (every few minutes) celery task to check for
# users with no account_key and retry hitting the service
