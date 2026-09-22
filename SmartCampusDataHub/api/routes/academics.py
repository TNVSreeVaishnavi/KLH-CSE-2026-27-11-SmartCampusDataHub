from fastapi import APIRouter, Depends, Query

from analytics.queries import AnalyticsQueries
from api.dependencies.services import get_analytics
from api.routes.common import collection, run_query

router = APIRouter()


@router.get("")
def academics(
    department: str | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=1000),
    queries: AnalyticsQueries = Depends(get_analytics),
):
    if department and hasattr(queries, "get_department_top_performers"):
        records = queries.get_department_top_performers(department=department, limit=limit)
    elif department:
        records = run_query(
            queries.db,
            """
            SELECT s.student_id, s.name, s.department,
                   ROUND(AVG(a.gpa), 2) AS avg_gpa,
                   COUNT(a.course_id) AS courses,
                   COUNT(CASE WHEN a.grade IN ('D', 'F') THEN 1 END) AS failing_grades
            FROM students s JOIN academics a ON s.student_id = a.student_id
            WHERE s.department = ?
            GROUP BY s.student_id, s.name, s.department
            ORDER BY avg_gpa DESC LIMIT ?
            """,
            (department, limit),
        )
    else:
        records = queries.get_top_performers(limit=limit)

    return {
        "statistics": queries.get_academic_statistics(),
        "grades": queries.get_grade_distribution(),
        "by_department": queries.get_academics_by_department(),
        "top_performers": collection(records),
        "struggling_students": collection(queries.get_struggling_students()),
        "grade_statistics": queries.get_grade_statistics(),
        "top_courses": queries.get_top_courses(limit=min(limit, 100)),
    }
