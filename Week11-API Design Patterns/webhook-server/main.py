from flask import Flask, request, jsonify
import pika, json, os
import time
from pika.exceptions import AMQPConnectionError

app = Flask(__name__)

RABBIT_URL = os.environ.get("RABBIT_URL")

def connect_rabbitmq(url, retries=10, delay=5):
    for i in range(retries):
        try:
            params = pika.URLParameters(url)
            connection = pika.BlockingConnection(params)
            print("Connected to RabbitMQ")
            return connection
        except AMQPConnectionError as e:
            print(f"RabbitMQ not ready yet... retrying {i+1}/{retries}")
            time.sleep(delay)
    raise Exception("Could not connect to RabbitMQ after many retries")

connection = connect_rabbitmq(RABBIT_URL)
channel = connection.channel()

@app.route("/webhooks/events", methods=["POST"])
def handle_webhook():
    payload = request.get_json()

    # Publish vào queue
    channel.basic_publish(
        exchange='',
        routing_key='notifications',
        body=json.dumps(payload),
        properties=pika.BasicProperties(delivery_mode=2) # persistent
    )

    return jsonify({"status": "queued"}), 200


@app.route("/")
def health():
    return "Webhook server OK", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
