import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query

from api.dependencies.services import get_monitor, get_pipeline_status
from monitoring.pipeline_monitor import PipelineMonitor
from monitoring.pipeline_status import PipelineStatusService
from ingestion.kafka.producer import publish_dataset
from processing.spark.lake import get_lake_root
from processing.spark.pipeline import process_dataset

router = APIRouter()


def _run_new_pipeline(dataset: str, batch_id: str) -> None:
    status_service = PipelineStatusService.from_environment()
    try:
        status_service.update(dataset=dataset, batch_id=batch_id, current_stage="INGESTION", pipeline_status="RUNNING")
        publish_dataset(dataset, batch_id=batch_id)
        process_dataset(dataset, output_root=str(get_lake_root()), batch_id=batch_id)
    except Exception as exc:
        status_service.update(dataset=dataset, batch_id=batch_id, current_stage="FAILED", pipeline_status="FAILED", completed_at=datetime.now(timezone.utc).isoformat(), error_message=str(exc))


@router.post("/run", status_code=202)
def run_pipeline(
    background_tasks: BackgroundTasks,
    dataset: str = Query(default="students"),
    status_service: PipelineStatusService = Depends(get_pipeline_status),
):
    supported = {"students", "attendance", "academics", "events", "transportation", "facilities"}
    if dataset not in supported:
        raise HTTPException(status_code=400, detail=f"Unsupported dataset '{dataset}'")
    batch_id = f"api-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}-{uuid.uuid4().hex[:8]}"
    try:
        status_service.update(dataset=dataset, batch_id=batch_id, current_stage="QUEUED", pipeline_status="QUEUED")
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"Redis pipeline status is unavailable: {exc}") from exc
    background_tasks.add_task(_run_new_pipeline, dataset, batch_id)
    return {"batch_id": batch_id, "dataset": dataset, "status": "QUEUED", "current_stage": "QUEUED"}


@router.get("/status")
def pipeline_status(status_service: PipelineStatusService = Depends(get_pipeline_status)):
    status = status_service.get_current()
    if not status:
        raise HTTPException(status_code=404, detail="No pipeline status available")
    return status


@router.get("/history")
def pipeline_history(limit: int = Query(default=20, ge=1, le=100), status_service: PipelineStatusService = Depends(get_pipeline_status)):
    return {"history": status_service.get_history(limit)}


@router.get("")
def pipeline(
    execution_id: int | None = Query(default=None, ge=1),
    monitor: PipelineMonitor = Depends(get_monitor),
):
    summary = monitor.get_pipeline_summary()
    selected_id = execution_id
    if selected_id is None and summary.get("last_execution"):
        selected_id = summary["last_execution"].get("execution_id")

    result = {"summary": summary, "execution_id": selected_id}
    if selected_id is not None:
        stages = monitor.get_execution_stage_metrics(selected_id)
        domains = monitor.get_execution_domain_statistics(selected_id)
        if not stages and not domains and selected_id != summary.get("last_execution", {}).get("execution_id"):
            raise HTTPException(status_code=404, detail="Pipeline execution not found")
        result["stages"] = stages
        result["domains"] = domains
    else:
        result["stages"] = []
        result["domains"] = []
    return result
