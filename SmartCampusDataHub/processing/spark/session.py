import os
import sys
from pathlib import Path

from pyspark.sql import SparkSession


def _ensure_windows_runtime_env() -> None:
    if sys.platform != "win32":
        return

    project_root = Path(__file__).resolve().parents[2]
    hadoop_home = Path(os.getenv("HADOOP_HOME") or str(project_root / "hadoop")).resolve()
    if hadoop_home.exists() and (hadoop_home / "bin").exists():
        os.environ["HADOOP_HOME"] = str(hadoop_home)
        os.environ["hadoop.home.dir"] = str(hadoop_home)
        path_entries = [entry for entry in os.environ.get("PATH", "").split(os.pathsep) if entry]
        bin_dir = str(hadoop_home / "bin")
        if bin_dir not in path_entries:
            os.environ["PATH"] = os.pathsep.join([*path_entries, bin_dir])

    if not os.getenv("JAVA_HOME"):
        candidates = [
            r"C:\Program Files\Java\jdk-21",
            r"C:\Program Files\Java\jdk-17",
            r"C:\Program Files\Java\jdk-11",
        ]
        for candidate in candidates:
            if Path(candidate).exists():
                os.environ["JAVA_HOME"] = candidate
                break

    if not os.getenv("PYSPARK_PYTHON"):
        python_executable = sys.executable or r".venv\Scripts\python.exe"
        os.environ["PYSPARK_PYTHON"] = python_executable
        os.environ["PYSPARK_DRIVER_PYTHON"] = python_executable


def get_spark_session(app_name: str = "smart-campus-spark") -> SparkSession:
    """Create a local Spark session for processing campus datasets."""
    _ensure_windows_runtime_env()
    builder = (
        SparkSession.builder
        .appName(app_name)
        .master("local[*]")
        .config("spark.sql.shuffle.partitions", "4")
        .config("spark.default.parallelism", "4")
        .config("spark.sql.adaptive.enabled", "true")
        .config("spark.hadoop.hadoop.native.lib", "false")
        .config("spark.driver.memory", "1g")
        .config("spark.executor.memory", "1g")
        .config("spark.sql.execution.arrow.pyspark.enabled", "true")
    )
    return builder.getOrCreate()
