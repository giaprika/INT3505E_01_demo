import connexion
from typing import Dict
from typing import Tuple
from typing import Union

from openapi_server.models.api_auth_login_post200_response import ApiAuthLoginPost200Response  # noqa: E501
from openapi_server.models.api_auth_register_post_request import ApiAuthRegisterPostRequest  # noqa: E501
from openapi_server import util


def api_auth_login_post(api_auth_register_post_request):  # noqa: E501
    """User login to obtain JWT token

     # noqa: E501

    :param api_auth_register_post_request: 
    :type api_auth_register_post_request: dict | bytes

    :rtype: Union[ApiAuthLoginPost200Response, Tuple[ApiAuthLoginPost200Response, int], Tuple[ApiAuthLoginPost200Response, int, Dict[str, str]]
    """
    if connexion.request.is_json:
        api_auth_register_post_request = ApiAuthRegisterPostRequest.from_dict(connexion.request.get_json())  # noqa: E501
    return 'do some magic!'


def api_auth_refresh_post():  # noqa: E501
    """Refresh JWT token

     # noqa: E501


    :rtype: Union[ApiAuthLoginPost200Response, Tuple[ApiAuthLoginPost200Response, int], Tuple[ApiAuthLoginPost200Response, int, Dict[str, str]]
    """
    return 'do some magic!'


def api_auth_register_post(api_auth_register_post_request):  # noqa: E501
    """Register a new user

     # noqa: E501

    :param api_auth_register_post_request: 
    :type api_auth_register_post_request: dict | bytes

    :rtype: Union[None, Tuple[None, int], Tuple[None, int, Dict[str, str]]
    """
    if connexion.request.is_json:
        api_auth_register_post_request = ApiAuthRegisterPostRequest.from_dict(connexion.request.get_json())  # noqa: E501
    return 'do some magic!'
