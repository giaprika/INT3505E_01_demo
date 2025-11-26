from flask import request, jsonify
from db import mongo, serialize_doc
from bson import ObjectId
from datetime import datetime
from utils.logger import logger


def create_payment():
    logger.info({
        "event": "payment_v2_create_request",
        "body": request.get_json(silent=True)
    })

    data = request.get_json()
    if 'method' not in data or 'amount' not in data:
        logger.warning({
            "event": "payment_v2_create_missing_fields",
            "required": ["method", "amount"],
            "received": data
        })
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

    logger.info({
        "event": "payment_v2_created",
        "payment_id": str(result.inserted_id),
        "method": payment_record["method"],
        "currency": payment_record["amount"]["currency"]
    })

    return jsonify({
        "message": "Payment created successfully",
        "id": str(result.inserted_id),
        "data": serialize_doc(payment_record)
    }), 201


def get_payments():
    logger.info({
        "event": "payment_v2_list_request",
        "query_params": request.args.to_dict()
    })

    currency = request.args.get('currency')
    query = {}

    if currency:
        query['amount.currency'] = currency

    payments = mongo.db.payments_v2.find(query).limit(20)
    count = mongo.db.payments_v2.count_documents(query)
    items = [serialize_doc(doc) for doc in payments]

    logger.info({
        "event": "payment_v2_list_response",
        "count": count
    })

    return jsonify({
        "count": count,
        "items": items
    }), 200


def get_payment(id):
    logger.info({
        "event": "payment_v2_get_request",
        "payment_id": id
    })

    try:
        payment = mongo.db.payments_v2.find_one({"_id": ObjectId(id)})
    except Exception as e:
        logger.error({
            "event": "payment_v2_get_invalid_id",
            "payment_id": id,
            "error": str(e)
        })
        return jsonify({"error": "Invalid ID format"}), 400

    if payment:
        logger.info({
            "event": "payment_v2_get_success",
            "payment_id": id
        })
        return jsonify(serialize_doc(payment)), 200

    logger.warning({
        "event": "payment_v2_get_not_found",
        "payment_id": id
    })
    return jsonify({"error": "Payment not found"}), 404


def update_payment(id):
    logger.info({
        "event": "payment_v2_update_request",
        "payment_id": id,
        "body": request.get_json(silent=True)
    })

    data = request.get_json()

    if 'amount' in data:
        logger.warning({
            "event": "payment_v2_update_forbidden_field",
            "payment_id": id,
            "field": "amount"
        })
        return jsonify({"error": "Cannot modify amount in V2."}), 403

    update_data = {}
    if 'status' in data: update_data['status'] = data['status']
    if 'details' in data: update_data['details'] = data['details']

    try:
        result = mongo.db.payments_v2.update_one(
            {"_id": ObjectId(id)},
            {"$set": update_data}
        )
    except Exception as e:
        logger.error({
            "event": "payment_v2_update_invalid_id",
            "payment_id": id,
            "error": str(e)
        })
        return jsonify({"error": "Invalid ID"}), 400

    if result.matched_count:
        logger.info({
            "event": "payment_v2_update_success",
            "payment_id": id,
            "updated_fields": update_data
        })
        return jsonify({"message": "Updated successfully"}), 200

    logger.warning({
        "event": "payment_v2_update_not_found",
        "payment_id": id
    })
    return jsonify({"error": "Not found"}), 404


def delete_payment(id):
    logger.info({
        "event": "payment_v2_delete_request",
        "payment_id": id
    })

    try:
        result = mongo.db.payments_v2.update_one(
            {"_id": ObjectId(id)},
            {"$set": {"status": "archived", "deleted_at": datetime.utcnow()}}
        )
    except Exception as e:
        logger.error({
            "event": "payment_v2_delete_invalid_id",
            "payment_id": id,
            "error": str(e)
        })
        return jsonify({"error": "Invalid ID"}), 400

    if result.matched_count:
        logger.info({
            "event": "payment_v2_deleted",
            "payment_id": id
        })
        return jsonify({"message": "Payment archived (Soft Delete)"}), 200

    logger.warning({
        "event": "payment_v2_delete_not_found",
        "payment_id": id
    })
    return jsonify({"error": "Not found"}), 404