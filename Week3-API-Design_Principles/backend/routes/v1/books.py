from flask import Blueprint, request, jsonify
from models import db, Book

books_bp = Blueprint('books', __name__)

@books_bp.route('/', methods=['GET'])
def list_books():
    search = request.args.get('search', '', type=str)
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 5, type=int)

    q = Book.query
    if search:
        like = f'%{search}%'
        q = q.filter((Book.title.ilike(like)) | (Book.genre.ilike(like)))
    p = q.order_by(Book.book_id).paginate(page=page, per_page=per_page, error_out=False)

    data = []
    for b in p.items:
        data.append({
            'book_id': b.book_id,
            'title': b.title,
            'genre': b.genre,
            'published_year': b.published_year,
        })
    return jsonify({'books': data, 'total': p.total, 'page': p.page, 'pages': p.pages})

@books_bp.route('/<int:book_id>', methods=['GET'])
def get_book(book_id):
    b = Book.query.get_or_404(book_id)
    return jsonify({
        'book_id': b.book_id,
        'title': b.title,
        'genre': b.genre,
        'published_year': b.published_year,
    })

@books_bp.route('/', methods=['POST'])
def create_book():
    data = request.json or {}
    title = data.get('title')
    if not title:
        return jsonify({'error': 'title required'}), 400
    b = Book(title=title, genre=data.get('genre'), published_year=data.get('published_year'))
    db.session.add(b)
    db.session.commit()
    return jsonify({'book_id': b.book_id}), 201

@books_bp.route('/<int:book_id>', methods=['PUT'])
def update_book(book_id):
    b = Book.query.get_or_404(book_id)
    data = request.json or {}
    b.title = data.get('title', b.title)
    b.genre = data.get('genre', b.genre)
    b.published_year = data.get('published_year', b.published_year)
    db.session.commit()
    return jsonify({'message': 'updated'})

@books_bp.route('/<int:book_id>', methods=['DELETE'])
def delete_book(book_id):
    b = Book.query.get_or_404(book_id)
    db.session.delete(b)
    db.session.commit()
    return jsonify({'message': 'deleted'})
