import pandas as pd
import logging
from typing import Dict

from config.config import get_logger

logger = get_logger(__name__)

class DataTransformer:
    """Transforms and standardizes data for database loading"""
    
    def __init__(self):
        self.transformation_log = {}
    
    def transform_all(self, dataframes: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
        """
        Transform all dataframes
        
        Args:
            dataframes: Dict mapping domain names to DataFrames
            
        Returns:
            Dict of transformed DataFrames
        """
        logger.info("Starting data transformation process...")
        transformed_data = {}
        
        for domain, df in dataframes.items():
            logger.info(f"Transforming {domain}...")
            transformed_df = self.transform_dataframe(df.copy(), domain)
            transformed_data[domain] = transformed_df
        
        logger.info("Data transformation complete.")
        return transformed_data
    
    def transform_dataframe(self, df: pd.DataFrame, domain: str) -> pd.DataFrame:
        """
        Transform a single dataframe for database loading
        
        Args:
            df: DataFrame to transform
            domain: Domain name for specific transformations
            
        Returns:
            Transformed DataFrame
        """
        log_entry = {"domain": domain, "steps": []}
        
        # Step 1: Standardize column names
        df = self._standardize_column_names(df)
        log_entry["steps"].append("Standardized column names")
        
        # Step 2: Convert data types
        df = self._convert_data_types(df, domain)
        log_entry["steps"].append("Converted data types")
        
        # Step 3: Normalize categorical values
        df = self._normalize_categories(df, domain)
        log_entry["steps"].append("Normalized categorical values")
        
        # Step 4: Create derived fields
        df = self._create_derived_fields(df, domain)
        log_entry["steps"].append("Created derived fields")
        
        # Step 5: Reorder columns for consistency
        df = self._reorder_columns(df, domain)
        log_entry["steps"].append("Reordered columns")
        
        log_entry["final_columns"] = list(df.columns)
        log_entry["final_rows"] = len(df)
        
        self.transformation_log[domain] = log_entry
        logger.info(f"Transformed {domain}: {len(df)} rows, {len(df.columns)} columns")
        
        return df
    
    def _standardize_column_names(self, df: pd.DataFrame) -> pd.DataFrame:
        """Standardize column names to snake_case lowercase"""
        df.columns = [col.lower().replace(' ', '_').replace('-', '_') for col in df.columns]
        return df
    
    def _convert_data_types(self, df: pd.DataFrame, domain: str) -> pd.DataFrame:
        """Convert columns to appropriate data types"""

        # Ensure ID columns are string-like object values for compatibility.
        for col in df.columns:
            if 'id' in col.lower() or 'code' in col.lower():
                df[col] = df[col].map(lambda v: str(v) if pd.notna(v) else None).astype(object)

        # Ensure numeric columns are numeric
        for col in df.columns:
            if any(x in col.lower() for x in ['age', 'count', 'capacity', 'percentage', 'gpa', 'score', 'price', 'cost']):
                try:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
                except Exception:
                    pass

        # Ensure date columns are datetime
        for col in df.columns:
            if any(x in col.lower() for x in ['date', 'time']):
                try:
                    df[col] = pd.to_datetime(df[col], errors='coerce')
                except Exception:
                    pass

        return df
    
    def _normalize_categories(self, df: pd.DataFrame, domain: str) -> pd.DataFrame:
        """Normalize categorical values"""
        
        # Convert status columns to lowercase
        for col in df.columns:
            if 'status' in col.lower() and df[col].dtype == 'object':
                df[col] = df[col].str.lower()
        
        # Normalize gender/sex columns
        if 'gender' in df.columns or 'sex' in df.columns:
            gender_col = 'gender' if 'gender' in df.columns else 'sex'
            df[gender_col] = df[gender_col].str.lower().replace({
                'm': 'Male', 'f': 'Female', 'o': 'Other',
                'male': 'Male', 'female': 'Female', 'other': 'Other'
            })
        
        # Normalize department/faculty columns
        for col in df.columns:
            if any(x in col.lower() for x in ['department', 'faculty', 'school']):
                if df[col].dtype == 'object':
                    df[col] = df[col].str.title()
        
        return df
    
    def _create_derived_fields(self, df: pd.DataFrame, domain: str) -> pd.DataFrame:
        """Create useful derived fields"""
        
        if domain == "students":
            # Create age group
            if 'age' in df.columns:
                df['age_group'] = pd.cut(df['age'], bins=[0, 18, 22, 25, 100], 
                                         labels=['<18', '18-22', '22-25', '25+'])
        
        elif domain == "academics":
            # Create performance level based on GPA
            if 'gpa' in df.columns:
                df['performance_level'] = pd.cut(df['gpa'], bins=[0, 2.0, 3.0, 3.5, 4.0],
                                                 labels=['Low', 'Medium', 'High', 'Excellent'])
        
        elif domain == "attendance":
            # Create attendance level based on percentage
            if 'attendance_percentage' in df.columns:
                df['attendance_level'] = pd.cut(df['attendance_percentage'], 
                                               bins=[0, 50, 75, 90, 100],
                                               labels=['Poor', 'Fair', 'Good', 'Excellent'])
        
        # Add ingestion timestamp to all domains
        df['ingestion_timestamp'] = pd.Timestamp.now()
        
        return df
    
    def _reorder_columns(self, df: pd.DataFrame, domain: str) -> pd.DataFrame:
        """Reorder columns for consistency"""
        
        # Define column order preferences
        priority_cols = []
        
        if domain == "students":
            priority_cols = ['student_id', 'name', 'email', 'age', 'gender', 'department', 
                           'status', 'age_group', 'ingestion_timestamp']
        
        elif domain == "attendance":
            priority_cols = ['student_id', 'date', 'status', 'attendance_percentage',
                           'attendance_level', 'ingestion_timestamp']
        
        elif domain == "academics":
            priority_cols = ['student_id', 'course_id', 'course_name', 'grade', 'gpa',
                           'performance_level', 'ingestion_timestamp']
        
        elif domain == "events":
            priority_cols = ['event_id', 'name', 'date', 'location', 'capacity',
                           'organizer', 'ingestion_timestamp']
        
        elif domain == "transportation":
            priority_cols = ['vehicle_id', 'vehicle_type', 'capacity', 'status',
                           'ingestion_timestamp']
        
        elif domain == "facilities":
            priority_cols = ['facility_id', 'name', 'type', 'capacity', 'location',
                           'status', 'ingestion_timestamp']
        
        # Reorder columns: priority first, then alphabetical for remaining
        existing_priority = [col for col in priority_cols if col in df.columns]
        other_cols = sorted([col for col in df.columns if col not in existing_priority])
        
        df = df[existing_priority + other_cols]
        
        return df
    
    def get_report(self) -> Dict:
        """Get the transformation report"""
        return self.transformation_log
    
    def print_report(self):
        """Print the transformation report"""
        logger.info("\n" + "="*60)
        logger.info("TRANSFORMATION REPORT")
        logger.info("="*60)
        
        for domain, report in self.transformation_log.items():
            logger.info(f"\n{domain.upper()}:")
            logger.info(f"  Final Rows: {report['final_rows']}")
            logger.info(f"  Final Columns: {len(report['final_columns'])}")
            logger.info(f"  Transformation Steps:")
            for step in report['steps']:
                logger.info(f"    - {step}")
            logger.info(f"  Column Order: {', '.join(report['final_columns'][:5])}...")
        
        logger.info("="*60 + "\n")


if __name__ == "__main__":
    from ingestion.ingest import DataIngester
    from processing.cleaning import DataCleaner
    from processing.validation import DataValidator
    
    ingester = DataIngester()
    data = ingester.ingest_all()
    
    cleaner = DataCleaner()
    cleaned_data = cleaner.clean_all(data)
    
    validator = DataValidator()
    validated_data, _ = validator.validate_all(cleaned_data)
    
    transformer = DataTransformer()
    transformed_data = transformer.transform_all(validated_data)
    transformer.print_report()
