from fastapi import APIRouter, Depends

from analytics.queries import AnalyticsQueries
from api.dependencies.services import get_analytics

router = APIRouter()


@router.get("")
def data_quality(queries: AnalyticsQueries = Depends(get_analytics)):
    return {
        "metrics": queries.get_comprehensive_quality_metrics(),
        "basic_metrics": queries.get_data_quality_metrics(),
    }
