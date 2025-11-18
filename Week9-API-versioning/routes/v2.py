from flask import Blueprint, request, jsonify
from db import mongo, serialize_doc
from bson import ObjectId
from datetime import datetime

bp = Blueprint('v2', __name__)

# API V2: Hỗ trợ đa tiền tệ, đa phương thức

@bp.route('/', methods=['POST'])
def create_payment():
    data = request.get_json()
    
    if 'method' not in data or 'amount' not in data:
        return jsonify({"error": "Missing method or amount object"}), 400
    
    payment_record = {
        "method": data['method'],
        "amount": {
            "value": data['amount'].get('value'),
            "currency": data['amount'].get('currency', 'VND') 
        },
        "details": data.get('details', {}), 
        "status": "processing", 
        "created_at": datetime.utcnow(),
    }

    result = mongo.db.payments_v2.insert_one(payment_record)
    
    return jsonify({
        "message": "Payment created successfully (V2)",
        "id": str(result.inserted_id),
        "data": serialize_doc(payment_record)
    }), 201


@bp.route('/', methods=['GET'])
def get_payments():
    currency = request.args.get('currency')
    query = {}
    if currency:
        query['amount.currency'] = currency
        
    payments = mongo.db.payments_v2.find(query).limit(20)
    return jsonify({
        "count": mongo.db.payments_v2.count_documents(query),
        "items": [serialize_doc(doc) for doc in payments]
    }), 200


@bp.route('/<id>', methods=['GET'])
def get_payment(id):
    try:
        payment = mongo.db.payments_v2.find_one({"_id": ObjectId(id)})
    except:
        return jsonify({"error": "Invalid ID format"}), 400
        
    if payment:
        return jsonify(serialize_doc(payment))
    return jsonify({"error": "Payment not found"}), 404


@bp.route('/<id>', methods=['PUT'])
def update_payment(id):
    data = request.get_json()
    
    if 'amount' in data:
        return jsonify({"error": "Cannot modify amount .Please create new payment."}), 403

    update_data = {}
    if 'status' in data: update_data['status'] = data['status']
    if 'details' in data: update_data['details'] = data['details']

    try:
        result = mongo.db.payments_v2.update_one(
            {"_id": ObjectId(id)}, 
            {"$set": update_data}
        )
    except:
        return jsonify({"error": "Invalid ID"}), 400

    if result.matched_count:
        return jsonify({"message": "Updated successfully"}), 200
    return jsonify({"error": "Not found"}), 404


@bp.route('/<id>', methods=['DELETE'])
def delete_payment(id):
    try:
        result = mongo.db.payments_v2.update_one(
            {"_id": ObjectId(id)},
            {"$set": {"status": "archived", "deleted_at": datetime.utcnow()}}
        )
    except:
        return jsonify({"error": "Invalid ID"}), 400
    
    if result.matched_count:
        return jsonify({"message": "Payment archived (Soft Delete)"}), 200
    return jsonify({"error": "Not found"}), 404