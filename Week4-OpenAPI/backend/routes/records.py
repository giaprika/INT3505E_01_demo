from flask import Blueprint, request, jsonify
from models import db, Record, BookCopy, Reader
from datetime import date
from utils.jwt_protect import protect_blueprint

records_bp = Blueprint('records', __name__)
protect_blueprint(records_bp)

@records_bp.route('/', methods=['GET'])
def list_records():
    search = request.args.get('search', '', type=str)  # search by reader name
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 5, type=int)

    q = Record.query.join(Reader)
    if search:
        q = q.filter(Reader.name.ilike(f'%{search}%'))
    p = q.order_by(Record.record_id.desc()).paginate(page=page, per_page=per_page, error_out=False)

    data = []
    for r in p.items:
        data.append({
            'record_id': r.record_id,
            'book_copy_id': r.book_copy_id,
            'reader_id': r.reader_id,
            'reader': r.reader.name if r.reader else None,
            'borrow_date': r.borrow_date.isoformat() if r.borrow_date else None,
            'return_date': r.return_date.isoformat() if r.return_date else None,
            'status': r.status
        })
    return jsonify({'records': data, 'total': p.total, 'page': p.page, 'pages': p.pages})

@records_bp.route('/<int:record_id>', methods=['GET'])
def get_record(record_id):
    r = Record.query.get_or_404(record_id)
    return jsonify({
        'record_id': r.record_id,
        'book_copy_id': r.book_copy_id,
        'reader_id': r.reader_id,
        'borrow_date': r.borrow_date.isoformat() if r.borrow_date else None,
        'return_date': r.return_date.isoformat() if r.return_date else None,
        'status': r.status
    })

@records_bp.route('/', methods=['POST'])
def create_record():
    """
    Body: { book_copy_id: int, reader_id: int }
    This will mark the copy as unavailable and create a record with borrow_date = today.
    """
    data = request.json or {}
    book_copy_id = data.get('book_copy_id')
    reader_id = data.get('reader_id')
    if not book_copy_id or not reader_id:
        return jsonify({'error': 'book_copy_id and reader_id required'}), 400

    copy = BookCopy.query.get_or_404(book_copy_id)
    if not copy.available:
        return jsonify({'error': 'book copy not available'}), 400
    # create record
    rec = Record(book_copy_id=book_copy_id, reader_id=reader_id, borrow_date=date.today(), status='Borrowed')
    copy.available = False
    db.session.add(rec)
    db.session.commit()
    return jsonify({'record_id': rec.record_id}), 201

@records_bp.route('/<int:record_id>/return', methods=['PUT'])
def return_record(record_id):
    r = Record.query.get_or_404(record_id)
    if r.status == 'Returned':
        return jsonify({'message': 'already returned'})
    r.return_date = date.today()
    r.status = 'Returned'
    copy = BookCopy.query.get(r.book_copy_id)
    if copy:
        copy.available = True
    db.session.commit()
    return jsonify({'message': 'returned'})

@records_bp.route('/<int:record_id>', methods=['PUT'])
def update_record(record_id):
    r = Record.query.get_or_404(record_id)
    data = request.json or {}
    # support updating status/return_date etc.
    if 'status' in data:
        r.status = data['status']
    if 'return_date' in data:
        try:
            from datetime import date
            r.return_date = date.fromisoformat(data['return_date']) if data['return_date'] else None
        except Exception:
            pass
    db.session.commit()
    return jsonify({'message': 'updated'})

@records_bp.route('/<int:record_id>', methods=['DELETE'])
def delete_record(record_id):
    r = Record.query.get_or_404(record_id)
    # optionally mark copy available if record was Borrowed
    copy = BookCopy.query.get(r.book_copy_id)
    if copy and r.status != 'Returned':
        copy.available = True
    db.session.delete(r)
    db.session.commit()
    return jsonify({'message': 'deleted'})
