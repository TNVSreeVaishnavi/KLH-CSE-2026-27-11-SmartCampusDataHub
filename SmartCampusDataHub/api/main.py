from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from api.dependencies.services import get_database_path
from api.routes import academics, attendance, events, facilities, ingestion, lineage, overview, pipeline, quality, students, transportation
from api.schemas.models import HealthResponse
from database.thread_safe_connection import ThreadSafeConnection

app = FastAPI(
    title="Smart Campus Data Hub API",
    version="1.0.0",
    description="REST API over the existing Smart Campus SQLite database and analytics layer.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:4173",
        "http://127.0.0.1:4173",
    ],
    allow_credentials=True,
    allow_methods=["GET", "OPTIONS"],
    allow_headers=["*"],
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(_: Request, exc: RequestValidationError):
    return JSONResponse(status_code=422, content={"detail": exc.errors()})


@app.get("/api/health", response_model=HealthResponse)
def health():
    db = ThreadSafeConnection()
    records = {}
    tables = ["students", "attendance", "academics", "events", "transportation", "facilities"]
    try:
        for table in tables:
            records[table] = db.get_table_count(table)
        return {
            "status": "ok",
            "api": "running",
            "version": app.version,
            "database": "connected",
            "database_path": get_database_path(),
            "records": records,
        }
    except Exception as exc:
        return JSONResponse(
            status_code=503,
            content={
                "status": "degraded",
                "api": "running",
                "version": app.version,
                "database": "unavailable",
                "database_path": get_database_path(),
                "records": records,
                "detail": str(exc),
            },
        )


app.include_router(overview.router, prefix="/api/overview", tags=["Overview"])
app.include_router(students.router, prefix="/api/students", tags=["Students"])
app.include_router(attendance.router, prefix="/api/attendance", tags=["Attendance"])
app.include_router(academics.router, prefix="/api/academics", tags=["Academics"])
app.include_router(events.router, prefix="/api/events", tags=["Events"])
app.include_router(transportation.router, prefix="/api/transportation", tags=["Transportation"])
app.include_router(facilities.router, prefix="/api/facilities", tags=["Facilities"])
app.include_router(quality.router, prefix="/api/data-quality", tags=["Data Quality"])
app.include_router(pipeline.router, prefix="/api/pipeline", tags=["Pipeline"])
app.include_router(ingestion.router, prefix="/api/ingestion", tags=["Ingestion"])
app.include_router(lineage.router, prefix="/api/lineage", tags=["Lineage"])
