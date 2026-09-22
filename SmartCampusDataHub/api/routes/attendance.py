from fastapi import APIRouter, Depends, Query

from analytics.queries import AnalyticsQueries
from api.dependencies.services import get_analytics
from api.routes.common import collection, run_query

router = APIRouter()


@router.get("")
def attendance(
    department: str | None = Query(default=None),
    threshold: float = Query(default=75.0, ge=0, le=100),
    limit: int = Query(default=100, ge=1, le=1000),
    queries: AnalyticsQueries = Depends(get_analytics),
):
    if department and hasattr(queries, "get_department_low_attendance"):
        records = queries.get_department_low_attendance(department=department, limit=limit)
    elif department:
        records = run_query(
            queries.db,
            """
            SELECT s.student_id, s.name, s.department,
                   ROUND(AVG(a.attendance_percentage), 2) AS avg_attendance,
                     COUNT(DISTINCT a.date) AS sessions_tracked,
                       COUNT(DISTINCT a.date) - SUM(CASE WHEN lower(a.status) = 'present' THEN 1 ELSE 0 END) AS missed_sessions
            FROM students s JOIN attendance a ON s.student_id = a.student_id
            WHERE s.department = ?
            GROUP BY s.student_id, s.name, s.department
            ORDER BY avg_attendance ASC LIMIT ?
            """,
            (department, limit),
        )
    else:
        records = queries.get_low_attendance_students(threshold=threshold)[:limit]

    return {
        "statistics": queries.get_attendance_statistics(),
        "by_status": queries.get_attendance_by_status(),
        "by_department": queries.get_attendance_by_department(),
        "low_attendance": collection(records),
        "trends": queries.get_attendance_trends(limit=min(limit, 100)),
    }
