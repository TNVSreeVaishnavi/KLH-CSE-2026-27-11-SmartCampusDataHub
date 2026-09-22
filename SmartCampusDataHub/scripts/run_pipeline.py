#!/usr/bin/env python3
"""
Smart Campus Data Hub - Main Pipeline Script

This script orchestrates the complete data engineering pipeline:
Ingestion → Cleaning → Validation → Transformation → Loading → Analytics
Includes pipeline monitoring and execution metrics tracking.
"""

import sys
import logging
from pathlib import Path
import time

# Add project root to path so the package can be imported when run as a script
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from config.config import get_logger, DATA_RAW_PATH
from ingestion.ingest import DataIngester
from processing.cleaning import DataCleaner
from processing.validation import DataValidator
from processing.transformation import DataTransformer
from database.load_data import DataLoader
from analytics.queries import AnalyticsQueries
from monitoring.pipeline_monitor import PipelineMonitor
from monitoring.data_lineage import DataLineage

logger = get_logger(__name__)

def run_pipeline():
    """Execute the complete data pipeline"""
    
    # Initialize pipeline monitor
    monitor = PipelineMonitor()
    execution_id = monitor.start_execution()
    
    logger.info("\n" + "="*70)
    logger.info("SMART CAMPUS DATA HUB - DATA PIPELINE")
    logger.info("="*70 + "\n")
    
    # Print data lineage
    DataLineage.print_lineage_summary()
    
    start_time = time.time()
    
    try:
        # Step 1: Data Ingestion
        logger.info("STEP 1: DATA INGESTION")
        logger.info("-" * 70)
        
        step_start = time.time()
        ingester = DataIngester()
        raw_data = ingester.ingest_all()
        ingester.print_report()
        
        if not raw_data:
            logger.error("No data was ingested. Aborting pipeline.")
            monitor.end_execution(execution_id, "FAILED", error_message="No data ingested")
            return False
        
        step_time = time.time() - step_start
        ingest_total = sum(len(df) for df in raw_data.values())
        monitor.record_stage_metrics(execution_id, "INGESTION", 0, ingest_total, 0, step_time)
        
        # Step 2: Data Cleaning
        logger.info("\nSTEP 2: DATA CLEANING")
        logger.info("-" * 70)
        
        step_start = time.time()
        cleaner = DataCleaner()
        cleaned_data = cleaner.clean_all(raw_data)
        cleaner.print_report()
        
        step_time = time.time() - step_start
        cleaned_total = sum(len(df) for df in cleaned_data.values())
        removed_during_cleaning = ingest_total - cleaned_total
        monitor.record_stage_metrics(execution_id, "CLEANING", ingest_total, cleaned_total, removed_during_cleaning, step_time)
        
        # Step 3: Data Validation
        logger.info("\nSTEP 3: DATA VALIDATION")
        logger.info("-" * 70)
        
        step_start = time.time()
        validator = DataValidator()
        validated_data, validation_report = validator.validate_all(cleaned_data)
        validator.print_report()
        
        step_time = time.time() - step_start
        validated_total = sum(len(df) for df in validated_data.values())
        monitor.record_stage_metrics(execution_id, "VALIDATION", cleaned_total, validated_total, 0, step_time)
        
        # Check if validation passed
        failed_domains = [d for d, r in validation_report.items() if r.get('validation_status') == 'FAILED']
        if failed_domains:
            logger.warning(f"Validation failed for: {failed_domains}")
            logger.info("Continuing with warnings...")
        
        # Step 4: Data Transformation
        logger.info("\nSTEP 4: DATA TRANSFORMATION")
        logger.info("-" * 70)
        
        step_start = time.time()
        transformer = DataTransformer()
        transformed_data = transformer.transform_all(validated_data)
        transformer.print_report()
        
        step_time = time.time() - step_start
        transformed_total = sum(len(df) for df in transformed_data.values())
        monitor.record_stage_metrics(execution_id, "TRANSFORMATION", validated_total, transformed_total, 0, step_time)
        
        # Step 5: Data Loading
        logger.info("\nSTEP 5: DATA LOADING INTO DATABASE")
        logger.info("-" * 70)
        
        step_start = time.time()
        loader = DataLoader()
        
        # Initialize database schema
        schema_path = Path(__file__).parent.parent / "database" / "schema.sql"
        if schema_path.exists():
            logger.info("Initializing database schema...")
            loader.db_manager.initialize(schema_path)
        else:
            logger.warning(f"Schema file not found: {schema_path}")
        
        loader.load_all(transformed_data)
        loader.save_processed_data(transformed_data)
        loader.print_report()
        loader.close()
        
        step_time = time.time() - step_start
        loaded_total = sum(len(df) for df in transformed_data.values())
        monitor.record_stage_metrics(execution_id, "DATABASE_LOAD", transformed_total, loaded_total, 0, step_time)
        
        # Step 6: Analytics
        logger.info("\nSTEP 6: ANALYTICS & REPORTING")
        logger.info("-" * 70)
        
        queries = AnalyticsQueries()
        queries.print_analytics_report()
        queries.close()
        
        # Pipeline Summary
        elapsed_time = time.time() - start_time
        
        logger.info("="*70)
        logger.info("PIPELINE EXECUTION SUMMARY")
        logger.info("="*70)
        logger.info(f"Total Execution Time: {elapsed_time:.2f} seconds")
        logger.info(f"Domains Processed: {len(raw_data)}")
        logger.info(f"Input Records: {ingest_total}")
        logger.info(f"Output Records: {loaded_total}")
        logger.info("Pipeline Status: OK COMPLETED")
        logger.info("="*70 + "\n")
        
        # Record successful completion
        monitor.end_execution(execution_id, "SUCCESS", ingest_total, loaded_total)
        
        return True
    
    except Exception as e:
        logger.error(f"Pipeline execution failed: {str(e)}")
        monitor.end_execution(execution_id, "FAILED", error_message=str(e))
        return False


def verify_raw_data():
    """Verify that raw data files exist"""
    if not DATA_RAW_PATH.exists():
        logger.error(f"Raw data path does not exist: {DATA_RAW_PATH}")
        logger.info("Please create the data/raw directory and add CSV files.")
        return False
    
    csv_files = list(DATA_RAW_PATH.glob("*.csv"))
    if not csv_files:
        logger.warning(f"No CSV files found in {DATA_RAW_PATH}")
        logger.info("Pipeline will continue but may not ingest any data.")
    
    return True


def main():
    """Main entry point"""
    
    try:
        # Verify prerequisites
        if not verify_raw_data():
            logger.warning("Proceeding without raw data files...")
        
        # Run pipeline
        success = run_pipeline()
        
        if success:
            logger.info("Pipeline completed successfully!")
            sys.exit(0)
        else:
            logger.error("Pipeline failed!")
            sys.exit(1)
    
    except Exception as e:
        logger.error(f"Pipeline error: {str(e)}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
