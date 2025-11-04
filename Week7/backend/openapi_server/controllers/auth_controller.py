import connexion
from typing import Dict
from typing import Tuple
from typing import Union

from openapi_server.models.api_auth_login_post200_response import ApiAuthLoginPost200Response  # noqa: E501
from openapi_server.models.api_auth_register_post_request import ApiAuthRegisterPostRequest  # noqa: E501
from openapi_server import util
from openapi_server.db import get_collection, get_next_sequence

import os
import hashlib
import hmac
import datetime
import jwt

_SECRET = os.getenv('AUTH_SECRET', 'dev-secret')


def _hash_password(password: str) -> str:
    return hmac.new(_SECRET.encode(), password.encode(), hashlib.sha256).hexdigest()


def verify_token(token: str):
    if not token:
        return None
    try:
        payload = jwt.decode(token, _SECRET, algorithms=['HS256'])
        return {'uid': payload.get('uid'), 'username': payload.get('username')}
    except Exception:
        return None


def api_auth_login_post():  # noqa: E501
    """User login to obtain JWT token

     # noqa: E501

    :param api_auth_register_post_request: 
    :type api_auth_register_post_request: dict | bytes

    :rtype: Union[ApiAuthLoginPost200Response, Tuple[ApiAuthLoginPost200Response, int], Tuple[ApiAuthLoginPost200Response, int, Dict[str, str]]
    """
    if connexion.request.is_json:
        api_auth_register_post_request = ApiAuthRegisterPostRequest.from_dict(connexion.request.get_json())  # noqa: E501

    users = get_collection('users')
    username = api_auth_register_post_request.username
    password = api_auth_register_post_request.password
    if not username or not password:
        return {'message': 'username and password required'}, 400

    user = users.find_one({'username': username})
    if not user:
        return {'message': 'invalid credentials'}, 401

    if user.get('password_hash') != _hash_password(password):
        return {'message': 'invalid credentials'}, 401

    payload = {
        'uid': user.get('user_id'),
        'username': username,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=2)
    }
    token = jwt.encode(payload, _SECRET, algorithm='HS256')
    return ApiAuthLoginPost200Response(token=token)


def api_auth_refresh_post():  # noqa: E501
    """Refresh JWT token

     # noqa: E501


    :rtype: Union[ApiAuthLoginPost200Response, Tuple[ApiAuthLoginPost200Response, int], Tuple[ApiAuthLoginPost200Response, int, Dict[str, str]]
    """
    # Read token from Authorization header
    auth = connexion.request.headers.get('Authorization')
    if not auth or not auth.startswith('Bearer '):
        return {'message': 'missing token'}, 401
    token = auth.split(' ', 1)[1]
    info = verify_token(token)
    if not info:
        return {'message': 'invalid token'}, 401

    payload = {
        'uid': info.get('uid'),
        'username': info.get('username'),
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=2)
    }
    new_token = jwt.encode(payload, _SECRET, algorithm='HS256')
    return ApiAuthLoginPost200Response(token=new_token)


def api_auth_register_post():  # noqa: E501
    """Register a new user

     # noqa: E501

    :param api_auth_register_post_request: 
    :type api_auth_register_post_request: dict | bytes

    :rtype: Union[None, Tuple[None, int], Tuple[None, int, Dict[str, str]]
    """
    if connexion.request.is_json:
        api_auth_register_post_request = ApiAuthRegisterPostRequest.from_dict(connexion.request.get_json())  # noqa: E501

    users = get_collection('users')
    username = api_auth_register_post_request.username
    password = api_auth_register_post_request.password
    if not username or not password:
        return {'message': 'username and password required'}, 400

    existing = users.find_one({'username': username})
    if existing:
        return {'message': 'user already exists'}, 400

    user_id = get_next_sequence('userid')
    users.insert_one({
        'user_id': int(user_id),
        'username': username,
        'password_hash': _hash_password(password)
    })
    return '', 201
