from fastapi import APIRouter, Depends

from analytics.queries import AnalyticsQueries
from api.dependencies.services import get_analytics, get_pipeline_status
from api.routes.common import run_query
from monitoring.pipeline_status import PipelineStatusService

router = APIRouter()


@router.get("")
def overview(
    queries: AnalyticsQueries = Depends(get_analytics),
    status_service: PipelineStatusService = Depends(get_pipeline_status),
):
    attendance = queries.get_attendance_statistics()
    academics = queries.get_academic_statistics()
    events = queries.get_event_statistics()
    facilities = queries.get_facilities_status()
    transportation = queries.get_transportation_status()
    if hasattr(queries, "get_recent_events"):
        recent_events = queries.get_recent_events(limit=5)
    else:
        recent_events = run_query(
            queries.db,
            "SELECT event_id, name, date, location, capacity, organizer "
            "FROM events ORDER BY date DESC LIMIT ?",
            (5,),
        )
    for event in recent_events:
        event["event_type"] = None

    active_facilities = sum(
        item.get("count", 0)
        for item in facilities
        if str(item.get("status", "")).lower() in {"operational", "active", "available"}
    )
    history = status_service.get_history(limit=100)
    batches = {entry.get("batch_id"): entry for entry in history if entry.get("batch_id")}
    completed = [entry for entry in batches.values() if entry.get("pipeline_status") == "COMPLETED"]
    durations = []
    for entry in completed:
        if entry.get("started_at") and entry.get("completed_at"):
            from datetime import datetime
            durations.append((datetime.fromisoformat(entry["completed_at"]) - datetime.fromisoformat(entry["started_at"])).total_seconds())
    current = status_service.get_current()
    last_execution = {
        "execution_id": None,
        "start_time": current.get("started_at"),
        "end_time": current.get("completed_at"),
        "status": "SUCCESS" if current.get("pipeline_status") == "COMPLETED" else current.get("pipeline_status", "UNKNOWN"),
        "duration_seconds": durations[0] if durations else None,
        "total_input_records": int(current.get("records_received", 0)),
        "total_output_records": int(current.get("records_written", 0)),
    } if current else None
    return {
        "kpis": {
            "total_students": queries.get_total_students(),
            "average_attendance": attendance.get("avg_attendance", 0),
            "average_gpa": academics.get("avg_gpa", 0),
            "total_events": events.get("total_events", 0),
            "transportation_vehicles": sum(item.get("count", 0) for item in transportation),
            "active_facilities": active_facilities,
        },
        "students_by_department": queries.get_students_by_department(),
        "attendance_by_status": queries.get_attendance_by_status(),
        "recent_events": recent_events,
        "pipeline": {
            "last_execution": last_execution,
            "total_executions": len(batches),
            "successful_executions": len(completed),
            "success_rate": round((len(completed) / len(batches)) * 100, 2) if batches else 0,
            "average_duration_seconds": round(sum(durations) / len(durations), 2) if durations else 0,
        },
    }
