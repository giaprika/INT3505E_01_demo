from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from models import db, Reader

readers_bp = Blueprint('readers', __name__)

@readers_bp.route('/', methods=['GET'])
@jwt_required()
def list_readers():
    search = request.args.get('search', '', type=str)
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 5, type=int)

    q = Reader.query
    if search:
        q = q.filter(Reader.name.ilike(f'%{search}%'))
    p = q.order_by(Reader.reader_id).paginate(page=page, per_page=per_page, error_out=False)
    data = [{
        'reader_id': r.reader_id,
        'name': r.name,
        'email': r.email,
        'phone': r.phone,
        'address': r.address,
        'birth_date': r.birth_date.isoformat() if r.birth_date else None,
        'join_date': r.join_date.isoformat() if r.join_date else None
    } for r in p.items]
    return jsonify({'readers': data, 'total': p.total, 'page': p.page, 'pages': p.pages})

@readers_bp.route('/<int:reader_id>', methods=['GET'])
@jwt_required()
def get_reader(reader_id):
    r = Reader.query.get_or_404(reader_id)
    return jsonify({
        'reader_id': r.reader_id,
        'name': r.name,
        'email': r.email,
        'phone': r.phone,
        'address': r.address,
        'birth_date': r.birth_date.isoformat() if r.birth_date else None,
        'join_date': r.join_date.isoformat() if r.join_date else None,
        'records': [{'record_id': rec.record_id, 'book_copy_id': rec.book_copy_id, 'status': rec.status} for rec in r.records]
    })

@readers_bp.route('/', methods=['POST'])
@jwt_required()
def create_reader():
    data = request.json or {}
    name = data.get('name')
    if not name:
        return jsonify({'error': 'name required'}), 400
    r = Reader(
        name=name,
        email=data.get('email'),
        phone=data.get('phone'),
        address=data.get('address')
    )
    if data.get('birth_date'):
        try:
            from datetime import date
            r.birth_date = date.fromisoformat(data['birth_date'])
        except Exception:
            pass
    db.session.add(r)
    db.session.commit()
    return jsonify({'reader_id': r.reader_id}), 201

@readers_bp.route('/<int:reader_id>', methods=['PUT'])
@jwt_required()
def update_reader(reader_id):
    r = Reader.query.get_or_404(reader_id)
    data = request.json or {}
    r.name = data.get('name', r.name)
    r.email = data.get('email', r.email)
    r.phone = data.get('phone', r.phone)
    r.address = data.get('address', r.address)
    if 'birth_date' in data:
        try:
            from datetime import date
            r.birth_date = date.fromisoformat(data['birth_date']) if data['birth_date'] else None
        except Exception:
            pass
    db.session.commit()
    return jsonify({'message': 'updated'})

@readers_bp.route('/<int:reader_id>', methods=['DELETE'])
@jwt_required()
def delete_reader(reader_id):
    r = Reader.query.get_or_404(reader_id)
    db.session.delete(r)
    db.session.commit()
    return jsonify({'message': 'deleted'})
