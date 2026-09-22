import argparse
import json
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List

from confluent_kafka import Producer
from redis.exceptions import RedisError

from config.config import DATA_RAW_PATH, RAW_DATA_FILES, get_logger
from ingestion.kafka.config import KAFKA_BOOTSTRAP_SERVERS, REDIS_URL, REDIS_PIPELINE_KEY, get_kafka_config, TOPIC_MAP
from ingestion.kafka.topics import get_topic_for_dataset
from monitoring.pipeline_status import PipelineStatusService

logger = get_logger(__name__)


def _ensure_kafka_reachable() -> None:
    """Validate Kafka connectivity before producing messages."""
    try:
        producer = Producer(get_kafka_config())
        producer.list_topics(timeout=5)
        logger.info("Kafka connectivity check passed.")
    except Exception as exc:  # pragma: no cover - runtime check
        raise RuntimeError(f"Kafka is not reachable at {KAFKA_BOOTSTRAP_SERVERS}: {exc}") from exc


def _ensure_redis_reachable() -> PipelineStatusService:
    """Validate Redis connectivity and return a client instance."""
    try:
        service = PipelineStatusService.from_environment()
        logger.info("Redis connectivity check passed.")
        return service
    except RedisError as exc:  # pragma: no cover - runtime check
        raise RuntimeError(f"Redis is not reachable at {REDIS_URL}: {exc}") from exc


def _read_csv_dataset(dataset: str) -> List[Dict[str, Any]]:
    filename = RAW_DATA_FILES.get(dataset)
    if not filename:
        raise ValueError(f"Unsupported dataset '{dataset}'")

    file_path = Path(DATA_RAW_PATH) / filename
    if not file_path.exists():
        raise FileNotFoundError(f"Raw dataset not found: {file_path}")

    import pandas as pd
    df = pd.read_csv(file_path)
    records = df.to_dict(orient="records")
    logger.info("Loaded %s records from %s", len(records), file_path)
    return records


def _build_message(record: Dict[str, Any], dataset: str, batch_id: str) -> Dict[str, Any]:
    message = dict(record)
    message["event_id"] = str(uuid.uuid4())
    message["dataset"] = dataset
    message["batch_id"] = batch_id
    message["ingestion_timestamp"] = datetime.now(timezone.utc).isoformat()
    return message


def _publish_dataset(dataset: str, producer: Producer, status_service: PipelineStatusService, batch_id: str) -> int:
    topic = get_topic_for_dataset(dataset)
    records = _read_csv_dataset(dataset)

    if not records:
        logger.warning("No records found for dataset %s; nothing to send.", dataset)
        status_service.update(dataset=dataset, batch_id=batch_id, current_stage="COMPLETED", pipeline_status="COMPLETED")
        return 0

    status_service.update(dataset=dataset, batch_id=batch_id, current_stage="INGESTION", records_received=len(records))
    sent = 0

    for record in records:
        payload = json.dumps(_build_message(record, dataset, batch_id), default=str)
        producer.produce(topic=topic, value=payload.encode("utf-8"))
        producer.flush()
        sent += 1

    status_service.update(dataset=dataset, batch_id=batch_id, current_stage="COMPLETED", pipeline_status="COMPLETED", records_received=len(records), records_written=sent, completed_at=datetime.now(timezone.utc).isoformat())
    logger.info("Published %s messages to Kafka topic %s", sent, topic)
    return sent


def publish_records(dataset: str, records: List[Dict[str, Any]], batch_id: str) -> int:
    """Publish validated records to Kafka without storing campus data in Redis."""
    _ensure_kafka_reachable()
    status_service = _ensure_redis_reachable()
    producer = Producer(get_kafka_config())
    topic = get_topic_for_dataset(dataset)
    status_service.update(dataset=dataset, batch_id=batch_id, current_stage="INGESTION", records_received=len(records))
    for record in records:
        payload = json.dumps(_build_message(record, dataset, batch_id), default=str)
        producer.produce(topic=topic, value=payload.encode("utf-8"))
    producer.flush()
    status_service.update(dataset=dataset, batch_id=batch_id, current_stage="INGESTION", records_received=len(records), records_written=len(records))
    return len(records)


def publish_dataset(dataset: str, batch_id: str | None = None) -> Dict[str, Any]:
    """Publish a single dataset to its Kafka topic."""
    batch_id = batch_id or f"batch-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}-{uuid.uuid4().hex[:8]}"
    _ensure_kafka_reachable()
    status_service = _ensure_redis_reachable()

    producer = Producer(get_kafka_config())
    sent_count = _publish_dataset(dataset, producer, status_service, batch_id)
    return {
        "dataset": dataset,
        "topic": get_topic_for_dataset(dataset),
        "batch_id": batch_id,
        "records_sent": sent_count,
        "status": "COMPLETED",
    }


def publish_all_datasets() -> List[Dict[str, Any]]:
    """Publish all datasets to their Kafka topics."""
    results = []
    for dataset in ["students", "attendance", "academics", "events", "transportation", "facilities"]:
        results.append(publish_dataset(dataset))
    return results


def main() -> int:
    parser = argparse.ArgumentParser(description="Publish campus datasets to Kafka topics.")
    parser.add_argument("--dataset", choices=["all", *sorted(TOPIC_MAP.keys())], required=True, help="Dataset to publish")
    args = parser.parse_args()

    try:
        if args.dataset == "all":
            results = publish_all_datasets()
            print(json.dumps(results, indent=2, default=str))
            return 0

        result = publish_dataset(args.dataset)
        print(json.dumps(result, indent=2, default=str))
        return 0
    except Exception as exc:
        logger.exception("Kafka producer failed")
        if "REDIS" in str(exc) or "Kafka is not reachable" in str(exc):
            print(f"ERROR: {exc}", file=sys.stderr)
        else:
            print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
