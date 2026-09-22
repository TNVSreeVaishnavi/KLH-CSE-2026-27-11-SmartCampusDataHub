import os
from pathlib import Path
import logging

# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent

# Data paths
DATA_RAW_PATH = PROJECT_ROOT / "data" / "raw"
DATA_PROCESSED_PATH = PROJECT_ROOT / "data" / "processed"
DATA_SAMPLE_PATH = PROJECT_ROOT / "data" / "sample"

# Log path
LOG_PATH = PROJECT_ROOT / "logs"

# Create directories if they don't exist
for path in [DATA_RAW_PATH, DATA_PROCESSED_PATH, DATA_SAMPLE_PATH, LOG_PATH]:
    path.mkdir(parents=True, exist_ok=True)

# Database configuration
DB_TYPE = os.getenv("DB_TYPE", "sqlite")
DB_PATH = os.getenv("DB_PATH", str(PROJECT_ROOT / "data" / "smart_campus.db"))
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "smart_campus")

# Logging configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Pipeline configuration
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "1000"))
VALIDATION_STRICT_MODE = os.getenv("VALIDATION_STRICT_MODE", "False").lower() == "true"

# Data source files
RAW_DATA_FILES = {
    "students": "students.csv",
    "attendance": "attendance.csv",
    "academics": "academics.csv",
    "events": "events.csv",
    "transportation": "transportation.csv",
    "facilities": "facilities.csv",
}

def get_logger(name: str) -> logging.Logger:
    """Get a configured logger instance"""
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.FileHandler(LOG_PATH / f"{name}.log")
        formatter = logging.Formatter(LOG_FORMAT)
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        # Also add console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        logger.setLevel(getattr(logging, LOG_LEVEL, logging.INFO))
    
    return logger

if __name__ == "__main__":
    print(f"Project Root: {PROJECT_ROOT}")
    print(f"Raw Data Path: {DATA_RAW_PATH}")
    print(f"Processed Data Path: {DATA_PROCESSED_PATH}")
    print(f"Database Type: {DB_TYPE}")
    print(f"Database Path/Host: {DB_PATH if DB_TYPE == 'sqlite' else DB_HOST}")
