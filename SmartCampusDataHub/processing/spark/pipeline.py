import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List
from uuid import uuid4

from pyspark.sql import DataFrame
from redis.exceptions import RedisError

from config.config import DATA_RAW_PATH, RAW_DATA_FILES, get_logger
from processing.spark.cleaning import clean_dataset
from processing.spark.lake import ensure_lake_layout, write_bronze, write_gold, write_silver
from processing.spark.session import get_spark_session
from processing.spark.transformation import transform_dataset
from processing.spark.validation import get_valid_and_rejected
from monitoring.pipeline_status import PipelineStatusService

logger = get_logger(__name__)

def _status_service() -> PipelineStatusService | None:
    try:
        return PipelineStatusService.from_environment()
    except (RedisError, RuntimeError) as exc:
        logger.warning("Redis unavailable; continuing Spark processing without pipeline status updates: %s", exc)
        return None


def _update_status(status_service: PipelineStatusService | None, **kwargs: object) -> None:
    if status_service is None:
        return
    try:
        status_service.update(**kwargs)
    except RedisError as exc:
        logger.warning("Redis status update failed; continuing pipeline processing: %s", exc)


def _load_raw_dataset(dataset: str, spark, source_path: str | None = None) -> DataFrame:
    filename = RAW_DATA_FILES[dataset]
    file_path = Path(source_path) if source_path else DATA_RAW_PATH / filename
    if not file_path.exists():
        raise FileNotFoundError(f"Raw dataset not found: {file_path}")

    raw_df = spark.read.csv(str(file_path), header=True, inferSchema=True)
    return raw_df


def process_dataset(dataset: str, output_root: str | None = None, source_path: str | None = None, batch_id: str | None = None) -> Dict[str, object]:
    spark = get_spark_session(app_name=f"smart-campus-{dataset}")
    status_service = _status_service()
    batch_id = batch_id or f"spark-batch-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}-{uuid4().hex[:8]}"
    start_time = time.time()
    records_received = records_cleaned = records_validated = records_rejected = records_written = 0

    try:
        lake_root = ensure_lake_layout(output_root)
        _update_status(status_service, dataset=dataset, batch_id=batch_id, current_stage="QUEUED", pipeline_status="QUEUED")
        _update_status(status_service, dataset=dataset, batch_id=batch_id, current_stage="INGESTION", records_received=0)
        raw_df = _load_raw_dataset(dataset, spark, source_path=source_path)
        input_count = raw_df.count()
        records_received = input_count
        bronze_path = write_bronze(raw_df, dataset, batch_id, str(lake_root))
        _update_status(status_service, dataset=dataset, batch_id=batch_id, current_stage="INGESTION", records_received=input_count)

        _update_status(status_service, dataset=dataset, batch_id=batch_id, current_stage="CLEANING", records_received=input_count)
        cleaned_df = clean_dataset(raw_df, dataset)
        cleaned_count = cleaned_df.count()
        records_cleaned = cleaned_count

        _update_status(status_service, dataset=dataset, batch_id=batch_id, current_stage="VALIDATION", records_received=input_count, records_cleaned=cleaned_count)
        valid_df, rejected_df, validation_metrics = get_valid_and_rejected(cleaned_df, dataset)
        rejected_count = validation_metrics["rejected_records"]
        records_validated = validation_metrics["valid_records"]
        records_rejected = rejected_count
        silver_path = write_silver(valid_df, dataset, batch_id, str(lake_root))

        _update_status(status_service, dataset=dataset, batch_id=batch_id, current_stage="TRANSFORMATION", records_received=input_count, records_cleaned=cleaned_count, records_validated=records_validated, records_rejected=rejected_count)
        transformed_df = transform_dataset(valid_df, dataset)
        output_count = transformed_df.count()
        records_written = output_count

        _update_status(status_service, dataset=dataset, batch_id=batch_id, current_stage="STORAGE", records_received=input_count, records_cleaned=cleaned_count, records_validated=records_validated, records_rejected=rejected_count, records_written=output_count)
        gold_path = write_gold(transformed_df, dataset, batch_id, str(lake_root))

        rejected_path = lake_root / "silver" / "rejected" / f"dataset={dataset}" / f"batch_id={batch_id}"
        rejected_path.mkdir(parents=True, exist_ok=True)
        rejected_df.write.mode("append").parquet(str(rejected_path))

        processing_duration = round(time.time() - start_time, 4)
        _update_status(status_service, dataset=dataset, batch_id=batch_id, current_stage="ANALYTICS", records_received=input_count, records_cleaned=cleaned_count, records_validated=records_validated, records_rejected=rejected_count, records_written=output_count)
        _update_status(status_service, dataset=dataset, batch_id=batch_id, current_stage="COMPLETED", pipeline_status="COMPLETED", records_received=input_count, records_cleaned=cleaned_count, records_validated=records_validated, records_rejected=rejected_count, records_written=output_count, completed_at=datetime.now(timezone.utc).isoformat())

        result = {
            "dataset": dataset,
            "batch_id": batch_id,
            "input_records": input_count,
            "cleaned_records": cleaned_count,
            "valid_records": validation_metrics["valid_records"],
            "rejected_records": rejected_count,
            "output_records": output_count,
            "processing_duration": processing_duration,
            "lake_root": str(lake_root),
            "bronze_path": bronze_path,
            "silver_path": silver_path,
            "gold_path": gold_path,
            "rejected_path": str(rejected_path),
            "current_stage": "COMPLETED",
            "pipeline_status": "COMPLETED",
        }
        logger.info("Spark pipeline completed for %s with %s output rows", dataset, output_count)
        return result

    except Exception as exc:
        logger.exception("Spark pipeline failed for %s", dataset)
        _update_status(status_service, dataset=dataset, batch_id=batch_id, current_stage="FAILED", pipeline_status="FAILED", records_received=records_received, records_cleaned=records_cleaned, records_validated=records_validated, records_rejected=records_rejected, records_written=records_written, completed_at=datetime.now(timezone.utc).isoformat(), error_message=str(exc))
        raise RuntimeError(f"Spark pipeline failed for {dataset}: {exc}") from exc
    finally:
        spark.stop()


def process_all_datasets(output_root: str | None = None) -> List[Dict[str, object]]:
    datasets = ["students", "attendance", "academics", "events", "transportation", "facilities"]
    results = []
    for dataset in datasets:
        results.append(process_dataset(dataset, output_root=output_root))
    return results
