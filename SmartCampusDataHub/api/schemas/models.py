from typing import Any

from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str
    api: str
    version: str
    database: str
    database_path: str
    records: dict[str, int]


class ErrorResponse(BaseModel):
    detail: str


class CollectionResponse(BaseModel):
    records: list[dict[str, Any]]
    total: int
