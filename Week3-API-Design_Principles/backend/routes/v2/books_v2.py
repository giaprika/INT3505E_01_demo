from flask import Blueprint, request, jsonify
from models import db, Book

books_v2_bp = Blueprint('books_v2', __name__)


@books_v2_bp.route('/', methods=['GET'])
def list_books_v2():
    search = request.args.get('search', '', type=str)
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 5, type=int)

    q = Book.query
    if search:
        like = f'%{search}%'
        q = q.filter((Book.title.ilike(like)) | (Book.genre.ilike(like)))

    p = q.order_by(Book.book_id).paginate(page=page, per_page=per_page, error_out=False)

    books = []
    for b in p.items:
        books.append({
            'id': b.book_id,
            'attributes': {
                'title': b.title,
                'genre': b.genre,
                'published_year': b.published_year,
            },
            'links': {
                'self': f'/api/v2/books/{b.book_id}'
            }
        })

    return jsonify({
        'books': books,
        'meta': {
            'total_items': p.total,
            'page': p.page,
            'per_page': per_page,
            'total_pages': p.pages
        },
        'links': {
            'self': f'/api/v2/books?page={page}&per_page={per_page}'
        }
    })


@books_v2_bp.route('/<int:book_id>', methods=['GET'])
def get_book_v2(book_id):
    b = Book.query.get_or_404(book_id)
    return jsonify({
        'data': {
            'id': b.book_id,
            'type': 'book',
            'attributes': {
                'title': b.title,
                'genre': b.genre,
                'published_year': b.published_year,
            },
            'links': {
                'self': f'/api/v2/books/{b.book_id}'
            }
        }
    })


@books_v2_bp.route('/', methods=['POST'])
def create_book_v2():
    data = request.json or {}
    title = data.get('title')
    if not title:
        return jsonify({'error': 'title required'}), 400

    b = Book(title=title, genre=data.get('genre'), published_year=data.get('published_year'))

    db.session.add(b)
    db.session.commit()

    return jsonify({
        'message': 'Book created successfully',
        'data': {
            'id': b.book_id,
            'title': b.title
        },
        'links': {
            'self': f'/api/v2/books/{b.book_id}'
        }
    }), 201


@books_v2_bp.route('/<int:book_id>', methods=['PUT'])
def update_book_v2(book_id):
    b = Book.query.get_or_404(book_id)
    data = request.json or {}

    b.title = data.get('title', b.title)
    b.genre = data.get('genre', b.genre)
    b.published_year = data.get('published_year', b.published_year)

    db.session.commit()

    return jsonify({
        'message': 'Book updated successfully',
        'data': {'id': b.book_id}
    })


@books_v2_bp.route('/<int:book_id>', methods=['DELETE'])
def delete_book_v2(book_id):
    b = Book.query.get_or_404(book_id)
    db.session.delete(b)
    db.session.commit()
    return jsonify({
        'message': f'Book {book_id} deleted successfully'
    })
