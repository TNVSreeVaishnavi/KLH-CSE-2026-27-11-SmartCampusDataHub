from pyspark.sql.types import (
    DoubleType,
    IntegerType,
    StringType,
    StructField,
    StructType,
)

DOMAIN_SCHEMAS = {
    "students": StructType([
        StructField("student_id", StringType(), True),
        StructField("name", StringType(), True),
        StructField("email", StringType(), True),
        StructField("age", IntegerType(), True),
        StructField("gender", StringType(), True),
        StructField("department", StringType(), True),
        StructField("status", StringType(), True),
    ]),
    "attendance": StructType([
        StructField("student_id", StringType(), True),
        StructField("date", StringType(), True),
        StructField("status", StringType(), True),
        StructField("attendance_percentage", DoubleType(), True),
    ]),
    "academics": StructType([
        StructField("student_id", StringType(), True),
        StructField("course_id", StringType(), True),
        StructField("course_name", StringType(), True),
        StructField("grade", StringType(), True),
        StructField("gpa", DoubleType(), True),
    ]),
    "events": StructType([
        StructField("event_id", StringType(), True),
        StructField("name", StringType(), True),
        StructField("date", StringType(), True),
        StructField("location", StringType(), True),
        StructField("capacity", IntegerType(), True),
        StructField("organizer", StringType(), True),
    ]),
    "transportation": StructType([
        StructField("vehicle_id", StringType(), True),
        StructField("vehicle_type", StringType(), True),
        StructField("capacity", IntegerType(), True),
        StructField("status", StringType(), True),
    ]),
    "facilities": StructType([
        StructField("facility_id", StringType(), True),
        StructField("name", StringType(), True),
        StructField("type", StringType(), True),
        StructField("capacity", IntegerType(), True),
        StructField("location", StringType(), True),
        StructField("status", StringType(), True),
    ]),
}


def get_domain_schema(domain: str):
    if domain not in DOMAIN_SCHEMAS:
        raise ValueError(f"Unsupported dataset '{domain}'")
    return DOMAIN_SCHEMAS[domain]
