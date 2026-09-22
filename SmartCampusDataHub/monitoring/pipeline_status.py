import json
import os
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from redis import Redis
from redis.exceptions import ConnectionError as RedisConnectionError, TimeoutError as RedisTimeoutError


PIPELINE_STAGES = (
    "QUEUED",
    "INGESTION",
    "CLEANING",
    "VALIDATION",
    "TRANSFORMATION",
    "STORAGE",
    "ANALYTICS",
    "COMPLETED",
    "FAILED",
)
STATUS_FIELDS = (
    "pipeline_status",
    "current_stage",
    "dataset",
    "batch_id",
    "started_at",
    "completed_at",
    "records_received",
    "records_cleaned",
    "records_validated",
    "records_rejected",
    "records_written",
    "error_message",
)


class PipelineStatusService:
    """Redis-backed status and bounded history for pipeline metadata only."""

    def __init__(self, redis_client: Redis, status_key: Optional[str] = None, history_key: Optional[str] = None, history_limit: int = 100):
        self.redis = redis_client
        self.status_key = status_key or os.getenv("REDIS_PIPELINE_KEY", "campus:pipeline:status")
        self.history_key = history_key or f"{self.status_key}:history"
        self.history_limit = history_limit

    @staticmethod
    def build_client() -> Redis:
        url = os.getenv("REDIS_URL", "redis://:campusredispass@localhost:6379/0")
        return Redis.from_url(
            url,
            decode_responses=True,
            socket_connect_timeout=3,
            socket_timeout=3,
            health_check_interval=30,
            retry_on_timeout=True,
        )

    @classmethod
    def from_environment(cls) -> "PipelineStatusService":
        client = cls.build_client()
        try:
            client.ping()
        except (RedisConnectionError, RedisTimeoutError, OSError) as exc:
            raise RuntimeError(f"Redis is not reachable at {os.getenv('REDIS_URL', 'redis://:campusredispass@localhost:6379/0')}: {exc}") from exc
        return cls(client)

    def update(self, *, dataset: str, batch_id: str, current_stage: str, pipeline_status: str = "RUNNING", started_at: Optional[str] = None, completed_at: Optional[str] = None, records_received: int = 0, records_cleaned: int = 0, records_validated: int = 0, records_rejected: int = 0, records_written: int = 0, error_message: str = "") -> Dict[str, str]:
        if current_stage not in PIPELINE_STAGES:
            raise ValueError(f"Unsupported pipeline stage: {current_stage}")

        now = datetime.now(timezone.utc).isoformat()
        existing = self.redis.hgetall(self.status_key)
        is_new_batch = existing.get("batch_id") != batch_id
        payload = {
            "pipeline_status": pipeline_status,
            "current_stage": current_stage,
            "dataset": dataset,
            "batch_id": batch_id,
            "started_at": started_at or (existing.get("started_at") if not is_new_batch else None) or now,
            "completed_at": completed_at or (existing.get("completed_at", "") if not is_new_batch else ""),
            "records_received": str(records_received),
            "records_cleaned": str(records_cleaned),
            "records_validated": str(records_validated),
            "records_rejected": str(records_rejected),
            "records_written": str(records_written),
            "error_message": error_message,
        }
        with self.redis.pipeline(transaction=True) as pipe:
            pipe.hset(self.status_key, mapping=payload)
            pipe.rpush(self.history_key, json.dumps(payload))
            pipe.ltrim(self.history_key, -self.history_limit, -1)
            pipe.execute()
        return payload

    def get_current(self) -> Dict[str, str]:
        return self.redis.hgetall(self.status_key)

    def get_history(self, limit: int = 20) -> List[Dict[str, Any]]:
        limit = max(1, min(limit, self.history_limit))
        entries = self.redis.lrange(self.history_key, -limit, -1)
        return [json.loads(entry) for entry in reversed(entries)]