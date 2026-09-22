import pandas as pd
import numpy as np
import logging
import re
from datetime import datetime
from typing import Dict, List, Tuple

from config.config import get_logger

logger = get_logger(__name__)

class DataCleaner:
    """Cleans and prepares data for processing"""
    
    def __init__(self):
        self.cleaning_log = {}
    
    def clean_all(self, dataframes: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
        """
        Clean all dataframes
        
        Args:
            dataframes: Dict mapping domain names to DataFrames
            
        Returns:
            Dict of cleaned DataFrames
        """
        logger.info("Starting data cleaning process...")
        cleaned_data = {}
        
        for domain, df in dataframes.items():
            logger.info(f"Cleaning {domain}...")
            cleaned_df = self.clean_dataframe(df.copy(), domain)
            cleaned_data[domain] = cleaned_df
        
        logger.info("Data cleaning complete.")
        return cleaned_data
    
    def clean_dataframe(self, df: pd.DataFrame, domain: str = "unknown") -> pd.DataFrame:
        """
        Clean a single dataframe
        
        Args:
            df: DataFrame to clean
            domain: Domain name for logging
            
        Returns:
            Cleaned DataFrame
        """
        log_entry = {"domain": domain, "steps": []}
        initial_rows = len(df)
        
        # Step 1: Remove leading/trailing whitespace
        df = self._remove_whitespace(df)
        log_entry["steps"].append(f"Removed whitespace")
        
        # Step 2: Standardize text
        df = self._standardize_text(df)
        log_entry["steps"].append(f"Standardized text")
        
        # Step 3: Standardize date columns
        df = self._standardize_dates(df)
        log_entry["steps"].append(f"Standardized dates")
        
        # Step 4: Handle missing values
        df = self._handle_missing_values(df, domain)
        log_entry["steps"].append(f"Handled missing values")
        
        # Step 5: Remove duplicates
        df, dup_count = self._remove_duplicates(df)
        log_entry["steps"].append(f"Removed {dup_count} duplicates")
        
        # Step 6: Handle invalid values
        df = self._handle_invalid_values(df, domain)
        log_entry["steps"].append(f"Handled invalid values")
        
        log_entry["initial_rows"] = initial_rows
        log_entry["final_rows"] = len(df)
        log_entry["rows_removed"] = initial_rows - len(df)
        
        self.cleaning_log[domain] = log_entry
        logger.info(f"Cleaned {domain}: {len(df)} rows (removed {log_entry['rows_removed']})")
        
        return df
    
    def _remove_whitespace(self, df: pd.DataFrame) -> pd.DataFrame:
        """Remove leading/trailing whitespace from string columns"""
        for col in df.select_dtypes(include=['object']).columns:
            df[col] = df[col].str.strip()
        return df
    
    def _standardize_text(self, df: pd.DataFrame) -> pd.DataFrame:
        """Standardize text (capitalize first letter, lowercase rest)"""
        for col in df.select_dtypes(include=['object']).columns:
            # Skip columns that look like IDs or emails
            if not any(x in col.lower() for x in ['id', 'email', 'phone', 'code']):
                df[col] = df[col].str.title()
        return df
    
    def _standardize_dates(self, df: pd.DataFrame) -> pd.DataFrame:
        """Standardize date columns to consistent format"""
        for col in df.columns:
            if any(x in col.lower() for x in ['date', 'time']):
                try:
                    df[col] = pd.to_datetime(df[col], errors='coerce')
                    # Keep as datetime type
                except Exception as e:
                    logger.warning(f"Could not parse date column {col}: {e}")
        return df
    
    def _handle_missing_values(self, df: pd.DataFrame, domain: str) -> pd.DataFrame:
        """Handle missing values based on column type and domain"""
        for col in df.columns:
            if df[col].isna().sum() == 0:
                continue

            if pd.api.types.is_numeric_dtype(df[col]):
                df[col] = df[col].fillna(0)
            elif pd.api.types.is_datetime64_any_dtype(df[col]):
                non_null = df[col].dropna()
                if not non_null.empty:
                    df[col] = df[col].fillna(non_null.mode().iloc[0])
                else:
                    df[col] = df[col].fillna(pd.Timestamp("1970-01-01"))
            else:
                df[col] = df[col].fillna('Unknown')

        return df

    def _remove_duplicates(self, df: pd.DataFrame, domain: str = None) -> Tuple[pd.DataFrame, int]:
        """Remove duplicate rows using the most relevant domain key when available."""
        initial_count = len(df)
        subset = None

        if domain:
            subset_map = {
                "students": ["student_id"],
                "attendance": ["student_id", "date"],
                "academics": ["student_id", "course_id"],
                "events": ["event_id"],
                "transportation": ["vehicle_id"],
                "facilities": ["facility_id"],
            }
            subset = subset_map.get(domain)

        if subset is None:
            for candidate in ["student_id", "event_id", "vehicle_id", "facility_id", "course_id", "email"]:
                if candidate in df.columns:
                    subset = [candidate]
                    break

        if subset:
            available = [col for col in subset if col in df.columns]
            if available:
                df = df.drop_duplicates(subset=available)
            else:
                df = df.drop_duplicates()
        else:
            df = df.drop_duplicates()

        dup_count = initial_count - len(df)
        return df, dup_count
    
    def _handle_invalid_values(self, df: pd.DataFrame, domain: str) -> pd.DataFrame:
        """Handle invalid values based on domain rules"""
        
        if domain == "students":
            # Age should be between 15 and 65
            if 'age' in df.columns:
                df.loc[(df['age'] < 15) | (df['age'] > 65), 'age'] = 20
            # Status should be valid
            if 'status' in df.columns:
                valid_status = ['active', 'inactive', 'graduated']
                df.loc[~df['status'].str.lower().isin(valid_status), 'status'] = 'active'
        
        elif domain == "attendance":
            # Attendance percentage should be 0-100
            if 'attendance_percentage' in df.columns:
                df['attendance_percentage'] = df['attendance_percentage'].clip(0, 100)
            # Status should be valid
            if 'status' in df.columns:
                valid_status = ['present', 'absent', 'late', 'excused']
                df.loc[~df['status'].str.lower().isin(valid_status), 'status'] = 'absent'
        
        elif domain == "academics":
            # GPA should be 0-4.0
            if 'gpa' in df.columns:
                df['gpa'] = df['gpa'].clip(0, 4.0)
            # Grade should be valid
            if 'grade' in df.columns:
                valid_grades = ['a', 'b', 'c', 'd', 'f']
                df.loc[~df['grade'].str.lower().isin(valid_grades), 'grade'] = 'c'
        
        elif domain == "events":
            # Capacity should be positive
            if 'capacity' in df.columns:
                df.loc[df['capacity'] <= 0, 'capacity'] = 100
        
        elif domain == "transportation":
            # Capacity should be positive
            if 'capacity' in df.columns:
                df.loc[df['capacity'] <= 0, 'capacity'] = 50
            # Status should be valid
            if 'status' in df.columns:
                valid_status = ['active', 'maintenance', 'inactive']
                df.loc[~df['status'].str.lower().isin(valid_status), 'status'] = 'active'
        
        elif domain == "facilities":
            # Capacity should be positive
            if 'capacity' in df.columns:
                df.loc[df['capacity'] <= 0, 'capacity'] = 100
            # Status should be valid
            if 'status' in df.columns:
                valid_status = ['operational', 'maintenance', 'closed']
                df.loc[~df['status'].str.lower().isin(valid_status), 'status'] = 'operational'
        
        return df
    
    def get_report(self) -> Dict:
        """Get the cleaning report"""
        return self.cleaning_log
    
    def print_report(self):
        """Print the cleaning report"""
        logger.info("\n" + "="*60)
        logger.info("CLEANING REPORT")
        logger.info("="*60)
        for domain, report in self.cleaning_log.items():
            logger.info(f"\n{domain.upper()}:")
            logger.info(f"  Initial Rows: {report['initial_rows']}")
            logger.info(f"  Final Rows: {report['final_rows']}")
            logger.info(f"  Rows Removed: {report['rows_removed']}")
            logger.info(f"  Cleaning Steps:")
            for step in report['steps']:
                logger.info(f"    - {step}")
        logger.info("="*60 + "\n")


if __name__ == "__main__":
    from ingestion.ingest import DataIngester
    
    ingester = DataIngester()
    data = ingester.ingest_all()
    
    cleaner = DataCleaner()
    cleaned_data = cleaner.clean_all(data)
    cleaner.print_report()
