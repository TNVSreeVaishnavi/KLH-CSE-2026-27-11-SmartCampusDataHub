import pandas as pd
import logging
from pathlib import Path
from typing import Dict, Tuple

from config.config import (
    DATA_RAW_PATH, 
    DATA_PROCESSED_PATH, 
    RAW_DATA_FILES, 
    get_logger
)

logger = get_logger(__name__)

class DataIngester:
    """Ingests raw data from CSV files"""
    
    def __init__(self, raw_data_path: Path = DATA_RAW_PATH):
        self.raw_data_path = Path(raw_data_path)
        self.ingestion_report = {}
    
    def ingest_all(self) -> Dict[str, pd.DataFrame]:
        """
        Ingest all raw CSV files
        
        Returns:
            Dict mapping domain names to DataFrames
        """
        logger.info("Starting data ingestion process...")
        ingested_data = {}
        
        for domain, filename in RAW_DATA_FILES.items():
            file_path = self.raw_data_path / filename
            
            if not file_path.exists():
                logger.warning(f"File not found: {file_path}")
                self.ingestion_report[domain] = {
                    "status": "FAILED",
                    "file": filename,
                    "reason": "File not found"
                }
                continue
            
            try:
                df = pd.read_csv(file_path)
                ingested_data[domain] = df
                
                self.ingestion_report[domain] = {
                    "status": "SUCCESS",
                    "file": filename,
                    "rows": len(df),
                    "columns": list(df.columns)
                }
                logger.info(f"Ingested {domain}: {len(df)} rows, {len(df.columns)} columns")
                
            except Exception as e:
                logger.error(f"Error ingesting {domain}: {str(e)}")
                self.ingestion_report[domain] = {
                    "status": "FAILED",
                    "file": filename,
                    "reason": str(e)
                }
        
        logger.info(f"Ingestion complete. {len(ingested_data)} domains successfully ingested.")
        return ingested_data
    
    def ingest_single(self, domain: str) -> Tuple[pd.DataFrame, dict]:
        """
        Ingest a single domain
        
        Args:
            domain: Domain name (e.g., 'students', 'attendance')
            
        Returns:
            Tuple of (DataFrame, status_dict)
        """
        if domain not in RAW_DATA_FILES:
            raise ValueError(f"Unknown domain: {domain}")
        
        filename = RAW_DATA_FILES[domain]
        file_path = self.raw_data_path / filename
        
        if not file_path.exists():
            logger.warning(f"File not found: {file_path}")
            return None, {"status": "FAILED", "reason": "File not found"}
        
        try:
            df = pd.read_csv(file_path)
            logger.info(f"Ingested {domain}: {len(df)} rows")
            return df, {"status": "SUCCESS", "rows": len(df), "columns": len(df.columns)}
        except Exception as e:
            logger.error(f"Error ingesting {domain}: {str(e)}")
            return None, {"status": "FAILED", "reason": str(e)}
    
    def get_report(self) -> Dict:
        """Get the ingestion report"""
        return self.ingestion_report
    
    def print_report(self):
        """Print the ingestion report"""
        logger.info("\n" + "="*60)
        logger.info("INGESTION REPORT")
        logger.info("="*60)
        for domain, status in self.ingestion_report.items():
            logger.info(f"\n{domain.upper()}:")
            for key, value in status.items():
                logger.info(f"  {key}: {value}")
        logger.info("="*60 + "\n")


if __name__ == "__main__":
    ingester = DataIngester()
    data = ingester.ingest_all()
    ingester.print_report()
