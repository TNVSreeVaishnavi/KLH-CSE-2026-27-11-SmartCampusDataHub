import os

KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
KAFKA_TOPIC_PREFIX = os.getenv("KAFKA_TOPIC_PREFIX", "campus")
REDIS_URL = os.getenv("REDIS_URL", "redis://:campusredispass@localhost:6379/0")
REDIS_PIPELINE_KEY = os.getenv("REDIS_PIPELINE_KEY", "campus:pipeline:status")

TOPIC_MAP = {
    "students": f"{KAFKA_TOPIC_PREFIX}.students",
    "attendance": f"{KAFKA_TOPIC_PREFIX}.attendance",
    "academics": f"{KAFKA_TOPIC_PREFIX}.academics",
    "events": f"{KAFKA_TOPIC_PREFIX}.events",
    "transportation": f"{KAFKA_TOPIC_PREFIX}.transportation",
    "facilities": f"{KAFKA_TOPIC_PREFIX}.facilities",
}

DATASET_ORDER = [
    "students",
    "attendance",
    "academics",
    "events",
    "transportation",
    "facilities",
]


def get_kafka_config() -> dict:
    return {
        "bootstrap.servers": KAFKA_BOOTSTRAP_SERVERS,
        "client.id": "smart-campus-producer",
        "acks": "all",
        "enable.idempotence": True,
        "linger.ms": 10,
        "retries": 5,
        "socket.timeout.ms": 5000,
        "message.timeout.ms": 10000,
        "request.timeout.ms": 15000,
    }
