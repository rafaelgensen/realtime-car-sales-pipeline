import json
import time
from google.cloud import pubsub_v1
import os

# lê project id salvo num txt
with open(r"./tests/credentials/account.txt") as f:
    PROJECT_ID = f.read().strip()

TOPIC_ID = f"cars-sales-{PROJECT_ID}-prod-events"

serviceAccount = r"./tests/credentials/credentials.json"
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = serviceAccount

publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path(PROJECT_ID, TOPIC_ID)

messages = [
    {
        "type": "purchase",
        "order_id": "A001",
        "customer_id": "C101",
        "car_model": "SUV",
        "amount": 45000.00,
        "timestamp": "2025-11-01T19:32:00Z"
    },
    {
        "type": "purchase",
        "order_id": "A002",
        "customer_id": "C102",
        "car_model": "Sedan",
        "amount": 32000.50,
        "timestamp": "2025-11-01T19:32:05Z"
    },
    {
        "type": "cancellation",
        "order_id": "A003",
        "customer_id": "C103",
        "car_model": "Hatch",
        "reason": "payment_failed",
        "timestamp": "2025-11-01T19:32:10Z"
    },
    {
        "type": "purchase",
        "order_id": "A004",
        "customer_id": "C104",
        "car_model": "Pickup",
        "amount": 78000.00,
        "timestamp": "2025-11-01T19:32:15Z"
    },
    {
        "type": "cancellation",
        "order_id": "A005",
        "customer_id": "C105",
        "car_model": "SUV",
        "reason": "customer_changed_mind",
        "timestamp": "2025-11-01T19:32:20Z"
    }
]

for msg in messages:
    data = json.dumps(msg).encode("utf-8")
    future = publisher.publish(topic_path, data=data)
    print(f"sent: {msg['order_id']} -> {msg['type']} | msg_id={future.result()}")
    time.sleep(5)