import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from pyspark.sql import DataFrame, SparkSession
from pyspark.sql import functions as F


LAKE_ROOT_ENV = "SMART_CAMPUS_LAKE_ROOT"
DEFAULT_LAKE_ROOT = Path("data") / "lake"
LAKE_LAYERS = ("raw", "bronze", "silver", "gold")


def get_lake_root(output_root: Optional[str] = None) -> Path:
    """Resolve the lake root from an explicit argument or environment variable."""
    return Path(output_root or os.getenv(LAKE_ROOT_ENV, str(DEFAULT_LAKE_ROOT)))


def ensure_lake_layout(output_root: Optional[str] = None) -> Path:
    root = get_lake_root(output_root)
    for layer in LAKE_LAYERS:
        (root / layer).mkdir(parents=True, exist_ok=True)
    return root


def _with_metadata(df: DataFrame, dataset: str, batch_id: str) -> DataFrame:
    processing_timestamp = datetime.now(timezone.utc).replace(tzinfo=None)
    return (
        df.withColumn("batch_id", F.lit(batch_id))
        .withColumn("processing_timestamp", F.lit(processing_timestamp).cast("timestamp"))
        .withColumn("dataset", F.lit(dataset))
    )


def _write_layer(df: DataFrame, layer: str, dataset: str, batch_id: str, output_root: Optional[str]) -> str:
    root = ensure_lake_layout(output_root)
    target = root / layer
    (
        _with_metadata(df, dataset, batch_id)
        .write.mode("append")
        .partitionBy("dataset", "batch_id")
        .parquet(str(target))
    )
    return str(target)


def write_bronze(df: DataFrame, dataset: str, batch_id: str, output_root: Optional[str] = None) -> str:
    return _write_layer(df, "bronze", dataset, batch_id, output_root)


def write_silver(df: DataFrame, dataset: str, batch_id: str, output_root: Optional[str] = None) -> str:
    return _write_layer(df, "silver", dataset, batch_id, output_root)


def write_gold(df: DataFrame, dataset: str, batch_id: str, output_root: Optional[str] = None) -> str:
    return _write_layer(df, "gold", dataset, batch_id, output_root)


def _read_layer(spark: SparkSession, layer: str, output_root: Optional[str] = None, dataset: Optional[str] = None) -> DataFrame:
    root = get_lake_root(output_root)
    path = root / layer
    if dataset:
        path = path / f"dataset={dataset}"
    return spark.read.parquet(str(path))


def read_bronze(spark: SparkSession, output_root: Optional[str] = None, dataset: Optional[str] = None) -> DataFrame:
    return _read_layer(spark, "bronze", output_root, dataset)


def read_silver(spark: SparkSession, output_root: Optional[str] = None, dataset: Optional[str] = None) -> DataFrame:
    return _read_layer(spark, "silver", output_root, dataset)


def read_gold(spark: SparkSession, output_root: Optional[str] = None, dataset: Optional[str] = None) -> DataFrame:
    return _read_layer(spark, "gold", output_root, dataset)