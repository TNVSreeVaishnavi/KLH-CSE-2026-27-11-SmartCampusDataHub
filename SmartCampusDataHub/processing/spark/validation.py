from functools import reduce

from pyspark.sql import DataFrame
from pyspark.sql import functions as F

from config.config import get_logger

logger = get_logger(__name__)


def get_valid_and_rejected(df: DataFrame, domain: str):
    valid_condition = F.lit(True)

    if domain == "students":
        valid_condition = (
            F.col("student_id").isNotNull() &
            F.col("name").isNotNull() &
            F.col("email").isNotNull() &
            F.col("age").isNotNull() &
            ((F.col("age") >= 15) & (F.col("age") <= 65))
        )

    elif domain == "attendance":
        valid_condition = (
            F.col("student_id").isNotNull() &
            F.col("date").isNotNull() &
            F.col("attendance_percentage").isNotNull() &
            ((F.col("attendance_percentage") >= 0) & (F.col("attendance_percentage") <= 100))
        )

    elif domain == "academics":
        valid_condition = (
            F.col("student_id").isNotNull() &
            F.col("course_id").isNotNull() &
            F.col("grade").isNotNull() &
            F.col("gpa").isNotNull() &
            ((F.col("gpa") >= 0) & (F.col("gpa") <= 4.0))
        )

    elif domain == "events":
        valid_condition = (
            F.col("event_id").isNotNull() &
            F.col("name").isNotNull() &
            F.col("date").isNotNull() &
            F.col("capacity").isNotNull() &
            (F.col("capacity") > 0)
        )

    elif domain == "transportation":
        valid_condition = (
            F.col("vehicle_id").isNotNull() &
            F.col("vehicle_type").isNotNull() &
            F.col("capacity").isNotNull() &
            (F.col("capacity") > 0)
        )

    elif domain == "facilities":
        valid_condition = (
            F.col("facility_id").isNotNull() &
            F.col("name").isNotNull() &
            F.col("capacity").isNotNull() &
            (F.col("capacity") > 0)
        )

    valid_df = df.filter(valid_condition)
    rejected_df = df.filter(~valid_condition)

    metrics = {
        "input_records": df.count(),
        "valid_records": valid_df.count(),
        "rejected_records": rejected_df.count(),
    }

    logger.info("Validation for %s: valid=%s rejected=%s", domain, metrics["valid_records"], metrics["rejected_records"])
    return valid_df, rejected_df, metrics
