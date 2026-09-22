import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, BackgroundTasks, Depends, File, Form, HTTPException, UploadFile

from ingestion.upload_service import process_uploaded_batch, store_upload, validate_upload
from monitoring.pipeline_status import PipelineStatusService

router = APIRouter()


@router.post("/upload", status_code=202)
async def upload_csv(
    background_tasks: BackgroundTasks,
    dataset: str = Form(...),
    file: UploadFile = File(...),
    status_service: PipelineStatusService = Depends(PipelineStatusService.from_environment),
):
    batch_id = f"upload-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}-{uuid.uuid4().hex[:8]}"
    try:
        content = await file.read()
        frame = validate_upload(dataset, file.filename or "upload.csv", content)
        raw_path, _ = store_upload(dataset, batch_id, file.filename or "upload.csv", frame)
        status_service.update(dataset=dataset, batch_id=batch_id, current_stage="QUEUED", pipeline_status="QUEUED", records_received=len(frame))
        background_tasks.add_task(process_uploaded_batch, dataset, batch_id, raw_path, len(frame))
        return {"batch_id": batch_id, "dataset": dataset, "filename": file.filename, "status": "QUEUED", "records_received": len(frame)}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"Upload could not be accepted: {exc}") from exc