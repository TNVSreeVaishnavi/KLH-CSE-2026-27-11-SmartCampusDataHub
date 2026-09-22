from fastapi import APIRouter, Depends

from analytics.queries import AnalyticsQueries
from api.dependencies.services import get_analytics

router = APIRouter()


@router.get("")
def facilities(queries: AnalyticsQueries = Depends(get_analytics)):
    return {
        "status": queries.get_facilities_status(),
        "by_type": queries.get_facilities_by_type(),
        "overview": queries.get_facilities_overview(),
        "maintenance": queries.get_facilities_maintenance_status(),
        "by_location": queries.get_facilities_by_location(),
    }
