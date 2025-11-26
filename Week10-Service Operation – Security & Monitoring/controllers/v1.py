from flask import request, jsonify, make_response
from db import mongo, serialize_doc
from bson import ObjectId
from datetime import datetime
from utils.logger import logger

def create_payment():
    logger.info({
        "event": "payment_v1_create_request",
        "body": request.get_json(silent=True)
    })

    data = request.get_json()
    required_fields = ['cardNumber', 'amount']
    
    if not all(k in data for k in required_fields):
        logger.warning({
            "event": "payment_v1_create_missing_fields",
            "required": required_fields,
            "received": data
        })
        return jsonify({"error": "Missing fields, requires: cardNumber, amount"}), 400

    payment_record = {
        "cardNumber": data['cardNumber'],
        "amount": int(data['amount']),
        "status": "pending",
        "created_at": datetime.utcnow()
    }

    result = mongo.db.payments_v1.insert_one(payment_record)

    logger.info({
        "event": "payment_v1_created",
        "payment_id": str(result.inserted_id),
        "record": payment_record
    })

    response = jsonify({
        "message": "Payment created",
        "id": str(result.inserted_id)
    })

    add_deprecation_headers(response)
    return response, 201


def get_payments():
    logger.info({
        "event": "payment_v1_list_request",
        "query_params": request.args.to_dict()
    })

    payments = mongo.db.payments_v1.find().limit(10)
    items = [serialize_doc(doc) for doc in payments]

    logger.info({
        "event": "payment_v1_list_response",
        "count": len(items)
    })

    response = jsonify(items)
    add_deprecation_headers(response)
    return response, 200


def get_payment(id):
    logger.info({
        "event": "payment_v1_get_request",
        "payment_id": id
    })

    try:
        payment = mongo.db.payments_v1.find_one({"_id": ObjectId(id)})
    except Exception as e:
        logger.error({
            "event": "payment_v1_get_invalid_id",
            "payment_id": id,
            "error": str(e)
        })
        return jsonify({"error": "Invalid ID format"}), 400

    if payment:
        logger.info({
            "event": "payment_v1_get_success",
            "payment_id": id
        })
        response = jsonify(serialize_doc(payment))
        add_deprecation_headers(response)
        return response, 200

    logger.warning({
        "event": "payment_v1_get_not_found",
        "payment_id": id
    })
    return jsonify({"error": "Payment not found"}), 404


def update_payment(id):
    logger.info({
        "event": "payment_v1_update_request",
        "payment_id": id,
        "body": request.get_json(silent=True)
    })

    data = request.get_json()
    update_data = {}
    if 'amount' in data: update_data['amount'] = data['amount']
    if 'status' in data: update_data['status'] = data['status']

    try:
        result = mongo.db.payments_v1.update_one(
            {"_id": ObjectId(id)},
            {"$set": update_data}
        )
    except Exception as e:
        logger.error({
            "event": "payment_v1_update_invalid_id",
            "payment_id": id,
            "error": str(e)
        })
        return jsonify({"error": "Invalid ID"}), 400

    if result.matched_count:
        logger.info({
            "event": "payment_v1_update_success",
            "payment_id": id,
            "updated_fields": update_data
        })
        response = jsonify({"message": "Updated successfully"})
        add_deprecation_headers(response)
        return response, 200

    logger.warning({
        "event": "payment_v1_update_not_found",
        "payment_id": id
    })
    return jsonify({"error": "Not found"}), 404


def delete_payment(id):
    logger.info({
        "event": "payment_v1_delete_request",
        "payment_id": id
    })

    try:
        result = mongo.db.payments_v1.delete_one({"_id": ObjectId(id)})
    except Exception as e:
        logger.error({
            "event": "payment_v1_delete_invalid_id",
            "payment_id": id,
            "error": str(e)
        })
        return jsonify({"error": "Invalid ID"}), 400

    if result.deleted_count:
        logger.info({
            "event": "payment_v1_delete_success",
            "payment_id": id
        })
        response = jsonify({"message": "Deleted"})
        return response, 200

    logger.warning({
        "event": "payment_v1_delete_not_found",
        "payment_id": id
    })
    return jsonify({"error": "Not found"}), 404

def add_deprecation_headers(response):
    response.headers['Warning'] = '299 - This API v1 is deprecated. Please migrate to v2.'
    response.headers['Deprecation'] = 'true'
    response.headers['Sunset'] = 'Wed, 31 Dec 2025 23:59:59 GMT'
    response.headers['Link'] = '</api/v2/payments>; rel="successor-version"'
    logger.warning({
        "event": "payment_v1_deprecation_header_added",
        "path": request.path
    })
    return response
