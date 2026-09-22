import os

from analytics.parquet_queries import ParquetAnalytics
from analytics.queries import AnalyticsQueries
from config.config import DB_PATH
from database.thread_safe_connection import ThreadSafeConnection
from monitoring.data_lineage import DataLineage
from monitoring.pipeline_monitor import PipelineMonitor
from monitoring.pipeline_status import PipelineStatusService


def get_analytics() -> AnalyticsQueries | ParquetAnalytics:
    if os.getenv("ANALYTICS_BACKEND", "parquet").lower() == "sqlite":
        return AnalyticsQueries()
    return ParquetAnalytics()


def get_database() -> ThreadSafeConnection:
    return ThreadSafeConnection()


def get_monitor() -> PipelineMonitor:
    return PipelineMonitor()


def get_lineage() -> type[DataLineage]:
    return DataLineage


def get_database_path() -> str:
    return str(DB_PATH)


def get_pipeline_status() -> PipelineStatusService:
    return PipelineStatusService.from_environment()
