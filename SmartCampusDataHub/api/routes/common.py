from datetime import date
from typing import Any

from fastapi import HTTPException

from database.thread_safe_connection import ThreadSafeConnection


def run_query(db: ThreadSafeConnection, query: str, params: tuple[Any, ...] = ()) -> list[dict]:
    try:
        return db.execute_query(query, params)
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"Database query failed: {exc}") from exc


def collection(records: list[dict]) -> dict[str, Any]:
    return {"records": records, "total": len(records)}


def event_status(event_date: str) -> str:
    try:
        parsed = date.fromisoformat(event_date[:10])
    except (TypeError, ValueError):
        return "Unknown"
    if parsed > date.today():
        return "Upcoming"
    if parsed == date.today():
        return "Ongoing"
    return "Completed"
