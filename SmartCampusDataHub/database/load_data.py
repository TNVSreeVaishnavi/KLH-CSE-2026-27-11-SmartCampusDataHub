import pandas as pd
import logging
from typing import Dict, Tuple
from pathlib import Path

from config.config import get_logger, DATA_PROCESSED_PATH
from database.connection import DatabaseManager

logger = get_logger(__name__)

class DataLoader:
    """Loads processed data into database"""
    
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.load_report = {}
        self.loaded_files = set()
    
    def load_all(self, dataframes: Dict[str, pd.DataFrame]) -> Dict[str, Dict]:
        """
        Load all dataframes into database
        
        Args:
            dataframes: Dict mapping domain names to DataFrames
            
        Returns:
            Dict with load report for each domain
        """
        logger.info("Starting data loading process...")
        
        for domain, df in dataframes.items():
            logger.info(f"Loading {domain}...")
            self.load_dataframe(df, domain)
        
        logger.info("Data loading complete.")
        return self.load_report
    
    def load_dataframe(self, df: pd.DataFrame, domain: str) -> Tuple[int, int]:
        """
        Load a dataframe into the corresponding table
        
        Args:
            df: DataFrame to load
            domain: Domain name (table name)
            
        Returns:
            Tuple of (inserted_rows, failed_rows)
        """
        try:
            df = self._deduplicate_dataframe(df, domain)

            # Ensure table exists
            if not self.db_manager.db.table_exists(domain):
                logger.warning(f"Table {domain} does not exist in database")
                self.load_report[domain] = {
                    "status": "FAILED",
                    "reason": f"Table {domain} does not exist",
                    "rows": 0
                }
                return 0, len(df)

            # If the table already contains data, replace it with the fresh batch.
            # This keeps reruns idempotent and avoids unique-key collisions.
            existing_count = self.db_manager.db.get_table_count(domain)
            if existing_count > 0:
                self.db_manager.db.execute_update(f"DELETE FROM {domain}")
                logger.info(f"Cleared {existing_count} existing rows from {domain} before reload")

            # Insert data
            inserted, failed = self.db_manager.insert_dataframe(df, domain)
            
            self.load_report[domain] = {
                "status": "SUCCESS",
                "rows_inserted": inserted,
                "rows_failed": failed,
                "total_rows": len(df)
            }
            
            logger.info(f"Loaded {domain}: {inserted} rows inserted, {failed} rows failed")
            self.loaded_files.add(domain)
            
            return inserted, failed
        
        except Exception as e:
            logger.error(f"Error loading {domain}: {str(e)}")
            self.load_report[domain] = {
                "status": "FAILED",
                "reason": str(e),
                "rows": 0
            }
            return 0, len(df)
    
    def _deduplicate_dataframe(self, df: pd.DataFrame, domain: str) -> pd.DataFrame:
        """Remove duplicate rows based on the domain's natural unique keys."""
        subset_map = {
            "students": ["email", "student_id"],
            "attendance": ["student_id", "date"],
            "academics": ["student_id", "course_id"],
            "events": ["event_id"],
            "transportation": ["vehicle_id"],
            "facilities": ["facility_id"],
        }
        subset = subset_map.get(domain)
        if subset:
            available = [col for col in subset if col in df.columns]
            if available:
                return df.drop_duplicates(subset=available).copy()
        return df.drop_duplicates().copy()

    def _check_if_loaded(self, domain: str, df: pd.DataFrame) -> bool:
        """
        Check if data has already been loaded to prevent duplicates
        
        Args:
            domain: Domain name
            df: DataFrame to load
            
        Returns:
            True if data appears to be already loaded
        """
        try:
            # Get count in database
            db_count = self.db_manager.db.get_table_count(domain)
            
            # If table is empty, definitely not loaded yet
            if db_count == 0:
                return False
            
            # If incoming data exactly matches table count, might be duplicate
            # (simple heuristic - could be improved with checksums)
            if db_count == len(df):
                logger.warning(f"Database {domain} has same row count as incoming data ({db_count})")
                return False  # Let user decide, don't auto-skip
            
            return False
        
        except Exception as e:
            logger.debug(f"Could not check if loaded: {str(e)}")
            return False
    
    def save_processed_data(self, dataframes: Dict[str, pd.DataFrame]) -> Dict[str, str]:
        """
        Save processed data to CSV files for reference
        
        Args:
            dataframes: Dict mapping domain names to DataFrames
            
        Returns:
            Dict with paths to saved files
        """
        logger.info("Saving processed data to CSV files...")
        saved_files = {}
        
        for domain, df in dataframes.items():
            try:
                file_path = DATA_PROCESSED_PATH / f"{domain}_processed.csv"
                df.to_csv(file_path, index=False)
                saved_files[domain] = str(file_path)
                logger.info(f"Saved {domain} to {file_path}")
            
            except Exception as e:
                logger.error(f"Error saving {domain}: {str(e)}")
        
        return saved_files
    
    def get_report(self) -> Dict:
        """Get the load report"""
        return self.load_report
    
    def print_report(self):
        """Print the load report"""
        logger.info("\n" + "="*60)
        logger.info("DATA LOADING REPORT")
        logger.info("="*60)
        
        total_inserted = 0
        total_failed = 0
        
        for domain, report in self.load_report.items():
            logger.info(f"\n{domain.upper()}:")
            logger.info(f"  Status: {report['status']}")
            
            if 'rows_inserted' in report:
                logger.info(f"  Rows Inserted: {report['rows_inserted']}")
                logger.info(f"  Rows Failed: {report['rows_failed']}")
                logger.info(f"  Total Rows: {report['total_rows']}")
                total_inserted += report['rows_inserted']
                total_failed += report['rows_failed']
            elif 'reason' in report:
                logger.info(f"  Reason: {report['reason']}")
        
        logger.info(f"\nTOTAL:")
        logger.info(f"  Total Inserted: {total_inserted}")
        logger.info(f"  Total Failed: {total_failed}")
        logger.info("="*60 + "\n")
    
    def close(self):
        """Close database connection"""
        self.db_manager.close()


if __name__ == "__main__":
    from ingestion.ingest import DataIngester
    from processing.cleaning import DataCleaner
    from processing.validation import DataValidator
    from processing.transformation import DataTransformer
    
    # Run full pipeline
    ingester = DataIngester()
    data = ingester.ingest_all()
    
    cleaner = DataCleaner()
    cleaned_data = cleaner.clean_all(data)
    
    validator = DataValidator()
    validated_data, _ = validator.validate_all(cleaned_data)
    
    transformer = DataTransformer()
    transformed_data = transformer.transform_all(validated_data)
    
    # Load data
    loader = DataLoader()
    loader.load_all(transformed_data)
    loader.print_report()
    loader.close()
