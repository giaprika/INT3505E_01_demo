import unittest

from flask import json

from openapi_server.models.api_books_book_id_put200_response import ApiBooksBookIdPut200Response  # noqa: E501
from openapi_server.models.api_books_get200_response import ApiBooksGet200Response  # noqa: E501
from openapi_server.models.api_books_post201_response import ApiBooksPost201Response  # noqa: E501
from openapi_server.models.book_create import BookCreate  # noqa: E501
from openapi_server.models.book_detail import BookDetail  # noqa: E501
from openapi_server.models.book_update import BookUpdate  # noqa: E501
from openapi_server.test import BaseTestCase


class TestBooksController(BaseTestCase):
    """BooksController integration test stubs"""

    def test_api_books_book_id_delete(self):
        """Test case for api_books_book_id_delete

        Delete book
        """
        headers = { 
            'Accept': 'application/json',
            'Authorization': 'Bearer special-key',
        }
        response = self.client.open(
            '/api/books/{book_id}'.format(book_id=56),
            method='DELETE',
            headers=headers)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_api_books_book_id_get(self):
        """Test case for api_books_book_id_get

        Get book by ID
        """
        headers = { 
            'Accept': 'application/json',
            'Authorization': 'Bearer special-key',
        }
        response = self.client.open(
            '/api/books/{book_id}'.format(book_id=56),
            method='GET',
            headers=headers)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_api_books_book_id_put(self):
        """Test case for api_books_book_id_put

        Update book
        """
        book_update = {"add_copies":6,"published_year":0,"remove_copy_ids":[1,1],"genre":"genre","title":"title","authors":["authors","authors"]}
        headers = { 
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': 'Bearer special-key',
        }
        response = self.client.open(
            '/api/books/{book_id}'.format(book_id=56),
            method='PUT',
            headers=headers,
            data=json.dumps(book_update),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_api_books_get(self):
        """Test case for api_books_get

        List all books with pagination and search
        """
        query_string = [('search', 'search_example'),
                        ('page', 1),
                        ('per_page', 5)]
        headers = { 
            'Accept': 'application/json',
            'Authorization': 'Bearer special-key',
        }
        response = self.client.open(
            '/api/books',
            method='GET',
            headers=headers,
            query_string=query_string)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_api_books_post(self):
        """Test case for api_books_post

        Create a new book
        """
        book_create = {"copies":6,"published_year":0,"genre":"genre","title":"title","authors":["authors","authors"]}
        headers = { 
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': 'Bearer special-key',
        }
        response = self.client.open(
            '/api/books',
            method='POST',
            headers=headers,
            data=json.dumps(book_create),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    unittest.main()
