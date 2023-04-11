import functools
import logging
from flask import jsonify
from pymongo.errors import DuplicateKeyError
from schematics.exceptions import DataError


logger = logging.getLogger(__name__)


def handle_duplicate_key_error(error, app_config):
    """
    jsonify pymongo duplicate key errors
    :param error: pymongo DuplicateKeyError
    :param app_config: Flask app.config
    :return: jsonify reseponse
    """
    for index_name in app_config['index_map'].keys():
        if index_name in error.details.get('errmsg'):
            field = app_config['index_map'].get(index_name)
            return jsonify(errors=['{} violated unique constraint'.format(field)]), 422
    logger.error(error)
    return jsonify(errors=['internal server error']), 500


def handle_validation_error(error):
    """
    jsonify Schematics errors
    :param error: Schematics DataError
    :return: jsonify response with error details
    """
    reformat_errors = []
    for field, errs in error.to_primitive().items():
        if isinstance(errs, list):
            reformat_errors.append('{}: {}'.format(field, ' '.join(errs)))
        else:
            reformat_errors.append('{}: {}'.format(field, errs))
    return jsonify(errors=reformat_errors), 422


def handle_exceptions(app_config=None):
    """
    Handle exceptions
    :param app_config: Flask app.config
    :return:
    """
    def handle_exceptions_inner(func):
        """
        Decorator for handling exceptions
        :param func: decorated function
        :return: wrapper func
        """
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except DataError as e:
                return handle_validation_error(e)
            except DuplicateKeyError as e:
                return handle_duplicate_key_error(e, app_config)
            except Exception as e:
                logger.error(e)
                return jsonify(errors=['internal server error']), 500

        return wrapper

    return handle_exceptions_inner
