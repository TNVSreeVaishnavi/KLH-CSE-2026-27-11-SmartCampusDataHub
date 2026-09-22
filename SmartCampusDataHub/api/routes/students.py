from fastapi import APIRouter, Depends, Query

from analytics.queries import AnalyticsQueries
from api.dependencies.services import get_analytics
from api.routes.common import collection, run_query

router = APIRouter()


@router.get("")
def students(
    department: str | None = Query(default=None),
    year: int | None = Query(default=None, ge=1, le=4),
    limit: int = Query(default=100, ge=1, le=1000),
    queries: AnalyticsQueries = Depends(get_analytics),
):
    if hasattr(queries, "get_student_records"):
        records = queries.get_student_records(department=department, year=year, limit=limit)
        return collection(records)

    filters = []
    params: list[object] = []
    if department:
        filters.append("department = ?")
        params.append(department)
    if year:
        filters.append(
            "CASE WHEN age BETWEEN 18 AND 19 THEN 1 "
            "WHEN age BETWEEN 20 AND 21 THEN 2 "
            "WHEN age BETWEEN 22 AND 23 THEN 3 ELSE 4 END = ?"
        )
        params.append(year)
    where = f"WHERE {' AND '.join(filters)}" if filters else ""
    params.append(limit)
    records = run_query(
        queries.db,
        f"""
        SELECT s.student_id, s.name, s.email, s.age, s.gender, s.department,
               s.status, s.age_group,
               CASE WHEN s.age BETWEEN 18 AND 19 THEN 'Year 1'
                    WHEN s.age BETWEEN 20 AND 21 THEN 'Year 2'
                    WHEN s.age BETWEEN 22 AND 23 THEN 'Year 3'
                    ELSE 'Year 4' END AS year,
               ROUND(AVG(a.gpa), 2) AS avg_gpa
        FROM students s
        LEFT JOIN academics a ON s.student_id = a.student_id
        {where}
        GROUP BY s.student_id, s.name, s.email, s.age, s.gender,
                 s.department, s.status, s.age_group
        ORDER BY s.student_id LIMIT ?
        """,
        tuple(params),
    )
    return collection(records)
