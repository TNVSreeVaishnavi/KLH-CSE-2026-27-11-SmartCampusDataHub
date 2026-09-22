from fastapi import APIRouter, Depends

from analytics.queries import AnalyticsQueries
from api.dependencies.services import get_analytics

router = APIRouter()


@router.get("")
def transportation(queries: AnalyticsQueries = Depends(get_analytics)):
    return {
        "status": queries.get_transportation_status(),
        "by_type": queries.get_vehicle_by_type(),
        "utilization": queries.get_vehicle_utilization(),
        "health": queries.get_vehicle_health(),
    }
