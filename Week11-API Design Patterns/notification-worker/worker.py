import pika, json, time, os
from pika.exceptions import AMQPConnectionError

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

channel.queue_declare(queue='notifications', durable=True)

print(" [*] Notification worker started. Waiting for messages.")

def callback(ch, method, properties, body):
    event = json.loads(body)
    print(f" [x] Received event: {event}")
    
    # Giả lập gửi thông báo
    time.sleep(1)
    print(f" [✓] Notification sent for event_id={event.get('id')}")

    ch.basic_ack(delivery_tag=method.delivery_tag)

channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue='notifications', on_message_callback=callback)

channel.start_consuming()
