from typing import Dict, Iterable, List

from pyspark.sql import DataFrame
from pyspark.sql import functions as F
from pyspark.sql.types import DoubleType, IntegerType, StringType

from config.config import get_logger

logger = get_logger(__name__)


DOMAIN_KEY_COLUMNS = {
    "students": ["student_id"],
    "attendance": ["student_id", "date"],
    "academics": ["student_id", "course_id"],
    "events": ["event_id"],
    "transportation": ["vehicle_id"],
    "facilities": ["facility_id"],
}


def _string_columns(df: DataFrame) -> List[str]:
    return [field.name for field in df.schema.fields if isinstance(field.dataType, StringType)]


def _numeric_columns(df: DataFrame) -> List[str]:
    numeric_types = (DoubleType, IntegerType)
    return [field.name for field in df.schema.fields if isinstance(field.dataType, numeric_types)]


def normalize_whitespace_and_text(df: DataFrame) -> DataFrame:
    for col in _string_columns(df):
        df = df.withColumn(col, F.when(F.col(col).isNull(), F.lit("Unknown")).otherwise(F.trim(F.col(col))))

    for col in [c for c in df.columns if "status" in c.lower()]:
        df = df.withColumn(col, F.lower(F.col(col)))

    for col in [c for c in df.columns if "department" in c.lower() or "location" in c.lower() or "organizer" in c.lower()]:
        df = df.withColumn(col, F.when(F.col(col).isNull(), F.lit("Unknown")).otherwise(F.initcap(F.col(col))))

    return df


def handle_missing_values(df: DataFrame, domain: str) -> DataFrame:
    for col in _numeric_columns(df):
        df = df.withColumn(col, F.when(F.col(col).isNull(), F.lit(0)).otherwise(F.col(col)))

    for col in _string_columns(df):
        df = df.withColumn(col, F.when(F.col(col).isNull(), F.lit("Unknown")).otherwise(F.col(col)))

    for col in [c for c in df.columns if "date" in c.lower() or "time" in c.lower()]:
        df = df.withColumn(col, F.when(F.col(col).isNull(), F.lit("1970-01-01")).otherwise(F.col(col)))

    return df


def normalize_dates(df: DataFrame) -> DataFrame:
    for col in [c for c in df.columns if "date" in c.lower() or "time" in c.lower()]:
        df = df.withColumn(col, F.to_date(F.col(col).cast("string"), "yyyy-MM-dd"))
    return df


def deduplicate_rows(df: DataFrame, domain: str) -> DataFrame:
    subset = DOMAIN_KEY_COLUMNS.get(domain, [])
    available = [c for c in subset if c in df.columns]
    if available:
        logger.info("Dropping duplicates for %s using columns %s", domain, available)
        df = df.dropDuplicates(available)
    else:
        logger.info("Dropping global duplicates for %s", domain)
        df = df.dropDuplicates()
    return df


def clean_dataset(df: DataFrame, domain: str) -> DataFrame:
    logger.info("Starting cleaning for %s", domain)
    df = normalize_whitespace_and_text(df)
    df = handle_missing_values(df, domain)
    df = normalize_dates(df)
    df = deduplicate_rows(df, domain)
    logger.info("Cleaning complete for %s: %s rows", domain, df.count())
    return df
