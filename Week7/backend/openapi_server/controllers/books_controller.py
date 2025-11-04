import connexion
from typing import Dict
from typing import Tuple
from typing import Union

from openapi_server.models.api_books_book_id_put200_response import ApiBooksBookIdPut200Response  # noqa: E501
from openapi_server.models.api_books_get200_response import ApiBooksGet200Response  # noqa: E501
from openapi_server.models.api_books_post201_response import ApiBooksPost201Response  # noqa: E501
from openapi_server.models.book_create import BookCreate  # noqa: E501
from openapi_server.models.book_detail import BookDetail  # noqa: E501
from openapi_server.models.book_update import BookUpdate  # noqa: E501
from openapi_server import util


def api_books_book_id_delete(book_id):  # noqa: E501
    """Delete book

     # noqa: E501

    :param book_id: 
    :type book_id: int

    :rtype: Union[ApiBooksBookIdPut200Response, Tuple[ApiBooksBookIdPut200Response, int], Tuple[ApiBooksBookIdPut200Response, int, Dict[str, str]]
    """
    return 'do some magic!'


def api_books_book_id_get(book_id):  # noqa: E501
    """Get book by ID

     # noqa: E501

    :param book_id: 
    :type book_id: int

    :rtype: Union[BookDetail, Tuple[BookDetail, int], Tuple[BookDetail, int, Dict[str, str]]
    """
    return 'do some magic!'


def api_books_book_id_put(book_id, book_update=None):  # noqa: E501
    """Update book

     # noqa: E501

    :param book_id: 
    :type book_id: int
    :param book_update: 
    :type book_update: dict | bytes

    :rtype: Union[ApiBooksBookIdPut200Response, Tuple[ApiBooksBookIdPut200Response, int], Tuple[ApiBooksBookIdPut200Response, int, Dict[str, str]]
    """
    if connexion.request.is_json:
        book_update = BookUpdate.from_dict(connexion.request.get_json())  # noqa: E501
    return 'do some magic!'


def api_books_get(search=None, page=None, per_page=None):  # noqa: E501
    """List all books with pagination and search

     # noqa: E501

    :param search: Search by title or genre
    :type search: str
    :param page: 
    :type page: int
    :param per_page: 
    :type per_page: int

    :rtype: Union[ApiBooksGet200Response, Tuple[ApiBooksGet200Response, int], Tuple[ApiBooksGet200Response, int, Dict[str, str]]
    """
    return 'do some magic!'


def api_books_post(book_create):  # noqa: E501
    """Create a new book

     # noqa: E501

    :param book_create: 
    :type book_create: dict | bytes

    :rtype: Union[ApiBooksPost201Response, Tuple[ApiBooksPost201Response, int], Tuple[ApiBooksPost201Response, int, Dict[str, str]]
    """
    if connexion.request.is_json:
        book_create = BookCreate.from_dict(connexion.request.get_json())  # noqa: E501
    return 'do some magic!'
