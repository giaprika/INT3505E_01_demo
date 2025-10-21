from flask import Blueprint, request, jsonify
from models import db, Reader

readers_v2_bp = Blueprint('readers_v2', __name__)

@readers_v2_bp.route('/', methods=['GET'])
def list_readers_v2():
    search = request.args.get('search', '', type=str)
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 5, type=int)

    q = Reader.query
    if search:
        like = f'%{search}%'
        q = q.filter(Reader.name.ilike(like))

    p = q.order_by(Reader.reader_id).paginate(page=page, per_page=per_page, error_out=False)

    readers = []
    for r in p.items:
        readers.append({
            'id': r.reader_id,
            'type': 'reader',
            'attributes': {
                'name': r.name,
                'email': r.email,
                'phone': r.phone,
                'address': r.address,
                'birth_date': r.birth_date.isoformat() if r.birth_date else None,
                'join_date': r.join_date.isoformat() if r.join_date else None
            },
            'links': {
                'self': f'/api/v2/readers/{r.reader_id}'
            }
        })

    return jsonify({
        'data': readers,
        'meta': {
            'total_items': p.total,
            'page': p.page,
            'per_page': per_page,
            'total_pages': p.pages
        },
        'links': {
            'self': f'/api/v2/readers?page={page}&per_page={per_page}'
        }
    })


@readers_v2_bp.route('/<int:reader_id>', methods=['GET'])
def get_reader_v2(reader_id):
    r = Reader.query.get_or_404(reader_id)
    return jsonify({
        'data': {
            'id': r.reader_id,
            'type': 'reader',
            'attributes': {
                'name': r.name,
                'email': r.email,
                'phone': r.phone,
                'address': r.address,
                'birth_date': r.birth_date.isoformat() if r.birth_date else None,
                'join_date': r.join_date.isoformat() if r.join_date else None
            },
            'links': {
                'self': f'/api/v2/readers/{r.reader_id}'
            }
        }
    })


@readers_v2_bp.route('/', methods=['POST'])
def create_reader_v2():
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

    return jsonify({
        'message': 'Reader created successfully',
        'data': {
            'id': r.reader_id,
            'type': 'reader',
            'attributes': {
                'name': r.name,
                'email': r.email,
                'phone': r.phone,
                'address': r.address
            },
            'links': {
                'self': f'/api/v2/readers/{r.reader_id}'
            }
        }
    }), 201


@readers_v2_bp.route('/<int:reader_id>', methods=['PUT'])
def update_reader_v2(reader_id):
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

    return jsonify({
        'message': 'Reader updated successfully',
        'data': {'id': r.reader_id},
        'links': {
            'self': f'/api/v2/readers/{r.reader_id}'
        }
    })


@readers_v2_bp.route('/<int:reader_id>', methods=['DELETE'])
def delete_reader_v2(reader_id):
    r = Reader.query.get_or_404(reader_id)
    db.session.delete(r)
    db.session.commit()

    return jsonify({
        'message': f'Reader {reader_id} deleted successfully'
    })
