from flask import request, jsonify, make_response
from db import mongo, serialize_doc
from bson import ObjectId
from datetime import datetime

# Logic xử lý cho V1 

def create_payment():
    data = request.get_json()
    required_fields = ['cardNumber', 'amount']
    if not all(k in data for k in required_fields):
        return jsonify({"error": "Missing fields, requires: cardNumber, amount"}), 400

    payment_record = {
        "cardNumber": data['cardNumber'],
        "amount": int(data['amount']),
        "status": "pending",
        "created_at": datetime.utcnow()
    }

    result = mongo.db.payments_v1.insert_one(payment_record)
    response = jsonify({
        "message": "Payment created",
        "id": str(result.inserted_id)
    })
    add_deprecation_headers(response)
    return response, 201

def get_payments():
    payments = mongo.db.payments_v1.find().limit(10)
    response = jsonify([serialize_doc(doc) for doc in payments])
    add_deprecation_headers(response)
    return response, 200

def get_payment(id):
    try:
        payment = mongo.db.payments_v1.find_one({"_id": ObjectId(id)})
    except:
        return jsonify({"error": "Invalid ID format"}), 400
        
    if payment:
        response = jsonify(serialize_doc(payment))
        add_deprecation_headers(response)
        return response, 200
    return jsonify({"error": "Payment not found"}), 404

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
        response = jsonify({"message": "Updated successfully"})
        add_deprecation_headers(response)
        return response, 200
    return jsonify({"error": "Not found"}), 404

def delete_payment(id):
    try:
        result = mongo.db.payments_v1.delete_one({"_id": ObjectId(id)})
    except:
        return jsonify({"error": "Invalid ID"}), 400

    if result.deleted_count:
        response = jsonify({"message": "Deleted"})
        return response, 200
    return jsonify({"error": "Not found"}), 404

def add_deprecation_headers(response):
    response.headers['Warning'] = '299 - This API v1 is deprecated. Please migrate to v2.'
    response.headers['Deprecation'] = 'true'
    response.headers['Sunset'] = 'Wed, 31 Dec 2025 23:59:59 GMT'
    response.headers['Link'] = '</api/v2/payments>; rel="successor-version"'
    return response