import unittest

from flask import json

from openapi_server.models.api_auth_login_post200_response import ApiAuthLoginPost200Response  # noqa: E501
from openapi_server.models.api_auth_register_post_request import ApiAuthRegisterPostRequest  # noqa: E501
from openapi_server.test import BaseTestCase


class TestAuthController(BaseTestCase):
    """AuthController integration test stubs"""

    def test_api_auth_login_post(self):
        """Test case for api_auth_login_post

        User login to obtain JWT token
        """
        api_auth_register_post_request = openapi_server.ApiAuthRegisterPostRequest()
        headers = { 
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': 'Bearer special-key',
        }
        response = self.client.open(
            '/api/auth/login',
            method='POST',
            headers=headers,
            data=json.dumps(api_auth_register_post_request),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_api_auth_refresh_post(self):
        """Test case for api_auth_refresh_post

        Refresh JWT token
        """
        headers = { 
            'Accept': 'application/json',
            'Authorization': 'Bearer special-key',
        }
        response = self.client.open(
            '/api/auth/refresh',
            method='POST',
            headers=headers)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_api_auth_register_post(self):
        """Test case for api_auth_register_post

        Register a new user
        """
        api_auth_register_post_request = openapi_server.ApiAuthRegisterPostRequest()
        headers = { 
            'Content-Type': 'application/json',
            'Authorization': 'Bearer special-key',
        }
        response = self.client.open(
            '/api/auth/register',
            method='POST',
            headers=headers,
            data=json.dumps(api_auth_register_post_request),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    unittest.main()
