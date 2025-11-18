from flask import request, jsonify
from db import mongo, serialize_doc
from bson import ObjectId
from datetime import datetime

# --- Logic xử lý cho V2 ---

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
        "api_version": "v2"
    }

    result = mongo.db.payments_v2.insert_one(payment_record)
    return jsonify({
        "message": "Payment created successfully",
        "id": str(result.inserted_id),
        "data": serialize_doc(payment_record)
    }), 201

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

def get_payment(id):
    try:
        payment = mongo.db.payments_v2.find_one({"_id": ObjectId(id)})
    except:
        return jsonify({"error": "Invalid ID format"}), 400
        
    if payment:
        return jsonify(serialize_doc(payment)), 200
    return jsonify({"error": "Payment not found"}), 404

def update_payment(id):
    data = request.get_json()
    if 'amount' in data:
        return jsonify({"error": "Cannot modify amount in V2."}), 403

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