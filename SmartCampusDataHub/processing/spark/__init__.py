"""PySpark-based processing pipeline for the Smart Campus Data Hub."""

from .pipeline import process_dataset, process_all_datasets

__all__ = ["process_dataset", "process_all_datasets"]
