from flask import Blueprint, request, jsonify
from db import mongo, serialize_doc
from bson import ObjectId
from datetime import datetime

bp = Blueprint('v1', __name__)

# API V1: Chỉ hỗ trợ thẻ, tiền tệ mặc định là VND

@bp.route('/', methods=['POST'])
def create_payment():
    data = request.get_json()
    
    required_fields = ['cardNumber', 'amount']
    if not all(k in data for k in required_fields):
        return jsonify({"error": "Missing fields, requires: cardNumber, amount"}), 400

    payment_record = {
        "cardNumber": data['cardNumber'],
        "amount": int(data['amount']),
        "status": "pending",
        "created_at": datetime.utcnow(),
    }

    result = mongo.db.payments_v1.insert_one(payment_record)
    
    return jsonify({
        "message": "Payment created",
        "id": str(result.inserted_id)
    }), 201


@bp.route('/', methods=['GET'])
def get_payments():
    payments = mongo.db.payments_v1.find().limit(10)
    return jsonify([serialize_doc(doc) for doc in payments]), 200


@bp.route('/<id>', methods=['GET'])
def get_payment(id):
    try:
        payment = mongo.db.payments_v1.find_one({"_id": ObjectId(id)})
    except:
        return jsonify({"error": "Invalid ID format"}), 400
        
    if payment:
        response = jsonify(serialize_doc(payment))
        response.headers['Warning'] = '299 - This API v1 is deprecated. Please migrate to v2.'
        return response
    return jsonify({"error": "Payment not found"}), 404


@bp.route('/<id>', methods=['PUT'])
def update_payment(id):
    data = request.get_json()
    update_data = {}
    if 'amount' in data: update_data['amount'] = data['amount']
    if 'status' in data: update_data['status'] = data['status']

    try:
        result = mongo.db.payments_v1.update_one(
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
        result = mongo.db.payments_v1.delete_one({"_id": ObjectId(id)})
    except:
        return jsonify({"error": "Invalid ID"}), 400

    if result.deleted_count:
        return jsonify({"message": "Deleted"}), 200
    return jsonify({"error": "Not found"}), 404