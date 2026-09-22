from pyspark.sql import DataFrame
from pyspark.sql import functions as F

from config.config import get_logger

logger = get_logger(__name__)


def transform_dataset(df: DataFrame, domain: str) -> DataFrame:
    logger.info("Starting transformation for %s", domain)

    df = df.toDF(*[c.lower().replace(" ", "_").replace("-", "_") for c in df.columns])

    if domain == "students":
        df = df.withColumn("age_group", F.when(F.col("age") < 18, "<18").when(F.col("age") <= 22, "18-22").when(F.col("age") <= 25, "22-25").otherwise("25+"))

    elif domain == "academics":
        df = df.withColumn("performance_level", F.when(F.col("gpa") < 2.0, "Low").when(F.col("gpa") < 3.0, "Medium").when(F.col("gpa") < 3.5, "High").otherwise("Excellent"))

    elif domain == "attendance":
        df = df.withColumn("attendance_level", F.when(F.col("attendance_percentage") < 50, "Poor").when(F.col("attendance_percentage") < 75, "Fair").when(F.col("attendance_percentage") < 90, "Good").otherwise("Excellent"))

    df = df.withColumn("ingestion_timestamp", F.current_timestamp())

    # Keep the existing pipeline field naming conventions and add derived fields where already supported.
    logger.info("Transformation complete for %s: %s rows", domain, df.count())
    return df
