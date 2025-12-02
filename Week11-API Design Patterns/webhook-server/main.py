from flask import Flask, request, jsonify, abort
import pika, json, os, hmac, hashlib

app = Flask(__name__)

RABBIT_URL = os.environ.get("RABBIT_URL")
WEBHOOK_SECRET = os.environ.get("WEBHOOK_SECRET")


def verify_signature(payload_body, signature):
    """Verify HMAC SHA256 signature"""
    computed_sig = hmac.new(
        WEBHOOK_SECRET.encode(),
        msg=payload_body,
        digestmod=hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(computed_sig, signature)


@app.route("/webhooks/events", methods=["POST"])
def handle_webhook():
    payload_body = request.data  # raw body
    signature = request.headers.get("X-Signature")

    if not signature or not verify_signature(payload_body, signature):
        abort(401, description="Invalid signature")

    payload = json.loads(payload_body)

    params = pika.URLParameters(RABBIT_URL)
    params.heartbeat = 600
    params.blocked_connection_timeout = 300
    connection = pika.BlockingConnection(params)
    channel = connection.channel()
    channel.queue_declare(queue='notifications', durable=True)

    channel.basic_publish(
        exchange='',
        routing_key='notifications',
        body=json.dumps(payload),
        properties=pika.BasicProperties(delivery_mode=2)
    )
    connection.close()

    return jsonify({"status": "queued"}), 200


@app.route("/")
def health():
    return "Webhook server OK", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
