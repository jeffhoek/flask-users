import os
from pymongo import MongoClient, TEXT
from flask import Flask, request, app, jsonify
from flask_users.user import User
from flask_users.password import encrypt_password
from flask_users.tasks import async_get_account_key
from flask_users.exception_handling import handle_exceptions


USERS_DB_NAME = 'flask_users'


from celery import Celery
celery_app = Celery('tasks', broker='redis://redis:6379/0')


app = Flask(__name__)


def get_users_collection(app_config):
    """
    Return a handle to the users collection
    :param app_config: Flask app.config
    :return: pymongo Collection object
    """
    client = MongoClient(app_config['mongo_host'], 27017, serverSelectionTimeoutMS=2)
    return client[app_config['db_name']][app_config['collection_name']]


def initialize_collection(app_reference):
    """
    Initialize mongodb collection and indices
    :param app_reference:
    """
    index_map = dict()
    users = get_users_collection(app_reference.config)
    index_name = users.create_index([('full_name', TEXT), ('email', TEXT), ('metadata', TEXT)])
    index_map[index_name] = 'text'

    index_name = users.create_index('email', unique=True)
    index_map[index_name] = 'email'

    index_name = users.create_index('account_key', unique=True, sparse=True)
    index_map[index_name] = 'account_key'

    app_reference.config['index_map'] = index_map


def get_user_query(request_args):
    """
    Build pymongo user query
    :param request_args: request arguments
    :return: dict
    """
    if request_args.get('query'):
        query = {
            '$text': {
                '$search': request_args.get('query')
            }
        }
    else:
        query = {}

    return query


@app.route('/v1/users', methods=['GET'])
@handle_exceptions(app_config=app.config)
def users_get():
    """
    Handle GET request
    :return: jsonify object
    """
    query = get_user_query(request.args)

    users = get_users_collection(app.config)
    cursor = users.find(query)

    return jsonify(users=[User(doc).to_native() for doc in cursor])


@app.route('/v1/users', methods=['POST'])
@handle_exceptions(app_config=app.config)
def users_post():
    """
    Handle POST request
    :return: jsonify object
    """
    req_json = request.json

    if not req_json:
        return jsonify(errors=['malformed or missing JSON payload']), 422

    if 'password' in req_json:
        salt, encrypt_pswd = encrypt_password(req_json.get('password'))
        req_json['password_salt'] = salt
        req_json['password'] = encrypt_pswd

    # validate the user
    user = User(req_json)
    user.validate()

    users = get_users_collection(app.config)
    result = users.insert_one(req_json)
    if not result.acknowledged:
        return jsonify(errors=['unable to insert new document']), 500
    else:
        # remove the ObjectID from the response
        doc_id = req_json.pop('_id')

        async_response = async_get_account_key.delay(
            req_json['email'],
            str(doc_id),
            app.config['mongo_host'],
            app.config['db_name'],
            app.config['collection_name'])
        app.logger.error(async_response)

        return jsonify(user.to_native()), 201


if __name__ == '__main__':  # pragma: no cover

    app.config['mongo_host'] = 'mongodb'
    app.config['db_name'] = 'flask_users'
    app.config['collection_name'] = 'users'

    initialize_collection(app)

    port = int(os.environ.get('PORT', 5001))
    app.run(debug=True, host='0.0.0.0', port=port)
