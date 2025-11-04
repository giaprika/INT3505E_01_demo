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
from openapi_server.db import get_collection, get_next_sequence
from openapi_server.models.book import Book
from openapi_server.models.book_detail import BookDetail
from openapi_server.models.api_books_get200_response import ApiBooksGet200Response
from openapi_server.models.api_books_post201_response import ApiBooksPost201Response
from openapi_server.models.api_books_book_id_put200_response import ApiBooksBookIdPut200Response
from openapi_server.controllers.auth_controller import verify_token
import math


def api_books_book_id_delete(book_id):  # noqa: E501
    """Delete book

     # noqa: E501

    :param book_id: 
    :type book_id: int

    :rtype: Union[ApiBooksBookIdPut200Response, Tuple[ApiBooksBookIdPut200Response, int], Tuple[ApiBooksBookIdPut200Response, int, Dict[str, str]]
    """
    # auth
    auth = connexion.request.headers.get('Authorization')
    if not auth or not auth.startswith('Bearer '):
        return {'message': 'missing token'}, 401
    token = auth.split(' ', 1)[1]
    info = verify_token(token)
    if not info:
        return {'message': 'invalid token'}, 401

    col = get_collection('books')
    result = col.delete_one({'book_id': int(book_id)})
    if result.deleted_count == 0:
        return {'message': 'Book not found'}, 404
    return ApiBooksBookIdPut200Response(message='deleted')


def api_books_book_id_get(book_id):  # noqa: E501
    """Get book by ID

     # noqa: E501

    :param book_id: 
    :type book_id: int

    :rtype: Union[BookDetail, Tuple[BookDetail, int], Tuple[BookDetail, int, Dict[str, str]]
    """
    auth = connexion.request.headers.get('Authorization')
    if not auth or not auth.startswith('Bearer '):
        return {'message': 'missing token'}, 401
    token = auth.split(' ', 1)[1]
    info = verify_token(token)
    if not info:
        return {'message': 'invalid token'}, 401

    col = get_collection('books')
    doc = col.find_one({'book_id': int(book_id)})
    if not doc:
        return {'message': 'Book not found'}, 404
    # Remove Mongo internal id before mapping
    doc.pop('_id', None)
    return BookDetail.from_dict(doc)


def api_books_book_id_put(book_id, book_update=None):  # noqa: E501
    """Update book

     # noqa: E501

    :param book_id: 
    :type book_id: int
    :param book_update: 
    :type book_update: dict | bytes

    :rtype: Union[ApiBooksBookIdPut200Response, Tuple[ApiBooksBookIdPut200Response, int], Tuple[ApiBooksBookIdPut200Response, int, Dict[str, str]]
    """
    auth = connexion.request.headers.get('Authorization')
    if not auth or not auth.startswith('Bearer '):
        return {'message': 'missing token'}, 401
    token = auth.split(' ', 1)[1]
    info = verify_token(token)
    if not info:
        return {'message': 'invalid token'}, 401

    if connexion.request.is_json:
        book_update = BookUpdate.from_dict(connexion.request.get_json())  # noqa: E501

    col = get_collection('books')
    update_doc = {}
    if book_update.title is not None:
        update_doc['title'] = book_update.title
    if book_update.genre is not None:
        update_doc['genre'] = book_update.genre
    if book_update.published_year is not None:
        update_doc['published_year'] = book_update.published_year
    if book_update.authors is not None:
        update_doc['authors'] = book_update.authors

    # handle copies adjustments
    if book_update.add_copies:
        add = int(book_update.add_copies)
        update_doc['$inc'] = update_doc.get('$inc', {})
        update_doc['$inc']['total_copies'] = add
        update_doc['$inc']['available_copies'] = add

    # Note: remove_copy_ids is simplified to decrement totals
    if book_update.remove_copy_ids:
        rem = len(book_update.remove_copy_ids)
        update_doc['$inc'] = update_doc.get('$inc', {})
        update_doc['$inc']['total_copies'] = update_doc['$inc'].get('total_copies', 0) - rem
        # don't make available negative
        update_doc['$inc']['available_copies'] = update_doc['$inc'].get('available_copies', 0) - rem

    if not update_doc:
        return ApiBooksBookIdPut200Response(message='no changes')

    # If $inc present, separate it from set fields
    inc = update_doc.pop('$inc', None)
    update_ops = {}
    if update_doc:
        update_ops['$set'] = update_doc
    if inc:
        update_ops['$inc'] = inc

    result = col.find_one_and_update({'book_id': int(book_id)}, update_ops)
    if result is None:
        return {'message': 'Book not found'}, 404
    return ApiBooksBookIdPut200Response(message='updated')


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
    auth = connexion.request.headers.get('Authorization')
    if not auth or not auth.startswith('Bearer '):
        return {'message': 'missing token'}, 401
    token = auth.split(' ', 1)[1]
    info = verify_token(token)
    if not info:
        return {'message': 'invalid token'}, 401

    col = get_collection('books')
    page = int(page) if page is not None else 1
    per_page = int(per_page) if per_page is not None else 10

    query = {}
    if search:
        # case-insensitive match on title or genre
        query['$or'] = [
            {'title': {'$regex': search, '$options': 'i'}},
            {'genre': {'$regex': search, '$options': 'i'}}
        ]

    total = col.count_documents(query)
    pages = math.ceil(total / per_page) if per_page else 1
    cursor = col.find(query).skip((page - 1) * per_page).limit(per_page)
    books = []
    for doc in cursor:
        doc.pop('_id', None)
        books.append(Book.from_dict(doc))

    return ApiBooksGet200Response(books=books, total=total, page=page, pages=pages)


def api_books_post():  # noqa: E501
    """Create a new book

     # noqa: E501

    :param book_create: 
    :type book_create: dict | bytes

    :rtype: Union[ApiBooksPost201Response, Tuple[ApiBooksPost201Response, int], Tuple[ApiBooksPost201Response, int, Dict[str, str]]
    """
    auth = connexion.request.headers.get('Authorization')
    if not auth or not auth.startswith('Bearer '):
        return {'message': 'missing token'}, 401
    token = auth.split(' ', 1)[1]
    info = verify_token(token)
    if not info:
        return {'message': 'invalid token'}, 401

    if connexion.request.is_json:
        book_create = BookCreate.from_dict(connexion.request.get_json())  # noqa: E501

    col = get_collection('books')
    # allocate integer book_id
    book_id = get_next_sequence('bookid')

    doc = {
        'book_id': int(book_id),
        'title': book_create.title,
        'genre': book_create.genre,
        'published_year': book_create.published_year,
        'authors': book_create.authors or [],
        'total_copies': int(book_create.copies) if book_create.copies is not None else 0,
        'available_copies': int(book_create.copies) if book_create.copies is not None else 0,
        # 'copies' structure omitted; can be added later
    }

    col.insert_one(doc)
    return ApiBooksPost201Response(book_id=book_id)
