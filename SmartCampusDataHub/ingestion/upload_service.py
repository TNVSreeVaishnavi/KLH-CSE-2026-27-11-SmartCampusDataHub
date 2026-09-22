import re
from io import BytesIO
from pathlib import Path
from typing import Any, Dict, Tuple

import pandas as pd

from ingestion.kafka.producer import publish_records
from monitoring.pipeline_status import PipelineStatusService
from processing.spark.pipeline import process_dataset
from processing.spark.lake import get_lake_root


REQUIRED_COLUMNS = {
    "students": {"student_id", "name", "email", "age", "gender", "department", "status"},
    "attendance": {"student_id", "date", "status", "attendance_percentage"},
    "academics": {"student_id", "course_id", "course_name", "grade", "gpa"},
    "events": {"event_id", "name", "date", "location", "capacity", "organizer"},
    "transportation": {"vehicle_id", "vehicle_type", "capacity", "status"},
    "facilities": {"facility_id", "name", "type", "capacity", "location", "status"},
}


def validate_upload(dataset: str, filename: str, content: bytes) -> pd.DataFrame:
    if dataset not in REQUIRED_COLUMNS:
        raise ValueError(f"Unsupported dataset '{dataset}'")
    if not filename.lower().endswith(".csv"):
        raise ValueError("Only CSV uploads are supported")
    if not content:
        raise ValueError("Uploaded file is empty")
    if len(content) > 25 * 1024 * 1024:
        raise ValueError("Uploaded file exceeds the 25 MB limit")

    try:
        frame = pd.read_csv(BytesIO(content))
    except Exception as exc:
        raise ValueError(f"Invalid CSV file: {exc}") from exc
    missing = REQUIRED_COLUMNS[dataset] - set(frame.columns)
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(sorted(missing))}")
    if frame.empty:
        raise ValueError("Uploaded CSV contains no records")
    return frame


def store_upload(dataset: str, batch_id: str, filename: str, frame: pd.DataFrame) -> Tuple[str, str]:
    root = get_lake_root()
    safe_filename = re.sub(r"[^A-Za-z0-9_.-]", "_", Path(filename).name)
    raw_dir = root / "raw" / f"dataset={dataset}" / f"batch_id={batch_id}"
    bronze_dir = root / "bronze" / f"dataset={dataset}" / f"batch_id={batch_id}"
    raw_dir.mkdir(parents=True, exist_ok=True)
    bronze_dir.mkdir(parents=True, exist_ok=True)
    raw_path = raw_dir / safe_filename
    bronze_path = bronze_dir / "part-00000.parquet"
    frame.to_csv(raw_path, index=False)
    bronze = frame.copy()
    bronze["processing_timestamp"] = pd.Timestamp.utcnow()
    bronze.to_parquet(bronze_path, index=False)
    return str(raw_path), str(bronze_path)


def process_uploaded_batch(dataset: str, batch_id: str, raw_path: str, records_received: int) -> None:
    status = PipelineStatusService.from_environment()
    try:
        status.update(dataset=dataset, batch_id=batch_id, current_stage="INGESTION", records_received=records_received)
        publish_records(dataset, pd.read_csv(raw_path).to_dict(orient="records"), batch_id)
        process_dataset(dataset, output_root=str(get_lake_root()), source_path=raw_path, batch_id=batch_id)
    except Exception as exc:
        status.update(dataset=dataset, batch_id=batch_id, current_stage="FAILED", pipeline_status="FAILED", records_received=records_received, completed_at=pd.Timestamp.utcnow().isoformat(), error_message=str(exc))
