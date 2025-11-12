from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from models import db, Author

authors_bp = Blueprint('authors', __name__)

@authors_bp.route('/', methods=['GET'])
@jwt_required()
def list_authors():
    search = request.args.get('search', '', type=str)
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 5, type=int)

    q = Author.query
    if search:
        q = q.filter(Author.name.ilike(f'%{search}%'))
    p = q.order_by(Author.author_id).paginate(page=page, per_page=per_page, error_out=False)
    
    data = [{
        'author_id': a.author_id,
        'name': a.name,
        'email': a.email,
        'birth_date': a.birth_date.isoformat() if a.birth_date else None
    } for a in p.items]
    return jsonify({'authors': data, 'total': p.total, 'page': p.page, 'pages': p.pages})

# get by id
@authors_bp.route('/<int:author_id>', methods=['GET'])
@jwt_required()
def get_author(author_id):
    a = Author.query.get_or_404(author_id)
    return jsonify({
        'author_id': a.author_id,
        'name': a.name,
        'email': a.email,
        'birth_date': a.birth_date.isoformat() if a.birth_date else None,
        'books': [{'book_id': b.book_id, 'title': b.title} for b in a.books]
    })

# create
@authors_bp.route('/', methods=['POST'])
@jwt_required()
def create_author():
    data = request.json or {}
    name = data.get('name')
    if not name:
        return jsonify({'error': 'name required'}), 400
    a = Author(name=name, email=data.get('email'))
    if data.get('birth_date'):
        try:
            from datetime import date
            a.birth_date = date.fromisoformat(data['birth_date'])
        except Exception:
            pass
    db.session.add(a)
    db.session.commit()
    return jsonify({'author_id': a.author_id}), 201

# update
@authors_bp.route('/<int:author_id>', methods=['PUT'])
@jwt_required()
def update_author(author_id):
    a = Author.query.get_or_404(author_id)
    data = request.json or {}
    a.name = data.get('name', a.name)
    a.email = data.get('email', a.email)
    if 'birth_date' in data:
        try:
            from datetime import date
            a.birth_date = date.fromisoformat(data['birth_date']) if data['birth_date'] else None
        except Exception:
            pass
    db.session.commit()
    return jsonify({'message': 'updated'})

# delete
@authors_bp.route('/<int:author_id>', methods=['DELETE'])
@jwt_required()
def delete_author(author_id):
    a = Author.query.get_or_404(author_id)
    db.session.delete(a)
    db.session.commit()
    return jsonify({'message': 'deleted'})
