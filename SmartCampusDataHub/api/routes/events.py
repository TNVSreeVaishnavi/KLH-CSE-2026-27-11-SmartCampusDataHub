from fastapi import APIRouter, Depends, Query

from analytics.queries import AnalyticsQueries
from api.dependencies.services import get_analytics
from api.routes.common import collection, event_status, run_query

router = APIRouter()


@router.get("")
def events(
    status: str | None = Query(default=None),
    location: str | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=1000),
    queries: AnalyticsQueries = Depends(get_analytics),
):
    if hasattr(queries, "get_recent_events"):
        records = queries.get_recent_events(limit=limit, status=status, location=location)
        for record in records:
            record["event_type"] = None
            record["status"] = event_status(record.get("date", ""))
        return {
            "statistics": queries.get_event_statistics(),
            "by_location": queries.get_events_by_location(),
            "records": records,
            "total": len(records),
        }

    filters = []
    params: list[object] = []
    if location:
        filters.append("location = ?")
        params.append(location)
    if status:
        normalized_status = status.strip().lower()
        if normalized_status == "upcoming":
            filters.append("date > date('now')")
        elif normalized_status == "ongoing":
            filters.append("date = date('now')")
        elif normalized_status == "completed":
            filters.append("date < date('now')")
        else:
            return {"statistics": queries.get_event_statistics(), "records": [], "total": 0}
    params.append(limit)
    where = f"WHERE {' AND '.join(filters)}" if filters else ""
    records = run_query(
        queries.db,
        f"SELECT event_id, name, date, location, capacity, organizer "
        f"FROM events {where} ORDER BY date DESC LIMIT ?",
        tuple(params),
    )
    for record in records:
        record["event_type"] = None
        record["status"] = event_status(record.get("date", ""))

    return {
        "statistics": queries.get_event_statistics(),
        "by_location": queries.get_events_by_location(),
        "records": records,
        "total": len(records),
    }
