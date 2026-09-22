import pandas as pd
import logging
from typing import Dict, List, Tuple

from config.config import get_logger

logger = get_logger(__name__)

class DataValidator:
    """Validates data quality and business rules"""
    
    def __init__(self):
        self.validation_report = {}
    
    def validate_all(self, dataframes: Dict[str, pd.DataFrame]) -> Tuple[Dict[str, pd.DataFrame], Dict]:
        """
        Validate all dataframes
        
        Args:
            dataframes: Dict mapping domain names to DataFrames
            
        Returns:
            Tuple of (validated_dataframes, validation_report)
        """
        logger.info("Starting data validation process...")
        validated_data = {}
        
        for domain, df in dataframes.items():
            logger.info(f"Validating {domain}...")
            validated_df, validation_result = self.validate_dataframe(df.copy(), domain)
            validated_data[domain] = validated_df
        
        logger.info("Data validation complete.")
        return validated_data, self.validation_report
    
    def validate_dataframe(self, df: pd.DataFrame, domain: str = "unknown") -> Tuple[pd.DataFrame, Dict]:
        """
        Validate a single dataframe
        
        Args:
            df: DataFrame to validate
            domain: Domain name for validation rules
            
        Returns:
            Tuple of (DataFrame, validation_result_dict)
        """
        validation_result = {
            "domain": domain,
            "total_rows": len(df),
            "checks": [],
            "warnings": [],
            "errors": [],
            "rows_with_issues": 0
        }
        
        # Run basic checks
        self._check_required_columns(df, domain, validation_result)
        self._check_data_types(df, domain, validation_result)
        self._check_null_values(df, domain, validation_result)
        self._check_duplicates(df, domain, validation_result)
        self._check_business_rules(df, domain, validation_result)
        
        validation_result["validation_status"] = "PASSED" if not validation_result["errors"] else "FAILED"
        
        self.validation_report[domain] = validation_result
        
        # Log summary
        logger.info(f"Validation for {domain}: {validation_result['validation_status']}")
        if validation_result["warnings"]:
            logger.warning(f"  Warnings: {len(validation_result['warnings'])}")
        if validation_result["errors"]:
            logger.error(f"  Errors: {len(validation_result['errors'])}")
        
        return df, validation_result
    
    def _check_required_columns(self, df: pd.DataFrame, domain: str, result: Dict):
        """Check if required columns are present"""
        required_cols = self._get_required_columns(domain)
        
        if not required_cols:
            result["checks"].append("No specific required columns defined")
            return
        
        missing = [col for col in required_cols if col not in df.columns]
        
        if missing:
            msg = f"Missing required columns: {missing}"
            result["errors"].append(msg)
            logger.error(f"  {msg}")
        else:
            result["checks"].append(f"All {len(required_cols)} required columns present")
    
    def _check_data_types(self, df: pd.DataFrame, domain: str, result: Dict):
        """Check data types are appropriate"""
        type_checks = self._get_expected_types(domain)
        
        if not type_checks:
            result["checks"].append("No specific type checks defined")
            return
        
        issues = []
        for col, expected_type in type_checks.items():
            if col not in df.columns:
                continue
            
            if expected_type == 'numeric' and not pd.api.types.is_numeric_dtype(df[col]):
                issues.append(f"{col} should be numeric")
            elif expected_type == 'date' and not pd.api.types.is_datetime64_any_dtype(df[col]):
                issues.append(f"{col} should be datetime")
            elif expected_type == 'string' and not pd.api.types.is_string_dtype(df[col]):
                issues.append(f"{col} should be string")
        
        if issues:
            for issue in issues:
                result["warnings"].append(issue)
        else:
            result["checks"].append("Data types validated")
    
    def _check_null_values(self, df: pd.DataFrame, domain_or_result, result: Dict = None):
        """Check for null values. Supports the runtime call and the legacy test signature."""
        if result is None and isinstance(domain_or_result, dict):
            result = domain_or_result
            domain = "unknown"
        else:
            domain = domain_or_result

        null_cols = df.columns[df.isna().any()].tolist()

        if null_cols:
            for col in null_cols:
                null_count = df[col].isna().sum()
                pct = (null_count / len(df)) * 100
                if pct > 10:
                    result["warnings"].append(f"{col}: {null_count} nulls ({pct:.1f}%)")
                result["rows_with_issues"] += null_count
        else:
            result["checks"].append("No null values found")

    def _check_duplicates(self, df: pd.DataFrame, domain_or_result, result: Dict = None):
        """Check for duplicate rows. Supports both the runtime and test calling styles."""
        if result is None and isinstance(domain_or_result, dict):
            result = domain_or_result
            domain = "unknown"
        else:
            domain = domain_or_result

        dup_count = df.duplicated().sum()

        if dup_count > 0:
            pct = (dup_count / len(df)) * 100
            result["warnings"].append(f"Found {dup_count} duplicate rows ({pct:.2f}%)")
            result["rows_with_issues"] += dup_count
        else:
            result["checks"].append("No duplicate rows found")
    
    def _check_business_rules(self, df: pd.DataFrame, domain: str, result: Dict):
        """Check domain-specific business rules"""
        
        if domain == "students":
            if 'age' in df.columns:
                invalid_age = len(df[(df['age'] < 15) | (df['age'] > 65)])
                if invalid_age > 0:
                    result["warnings"].append(f"Invalid ages (out of 15-65 range): {invalid_age}")
            
            if 'student_id' in df.columns:
                dup_ids = df['student_id'].duplicated().sum()
                if dup_ids > 0:
                    result["errors"].append(f"Duplicate student_ids: {dup_ids}")
        
        elif domain == "attendance":
            if 'attendance_percentage' in df.columns:
                invalid_pct = len(df[(df['attendance_percentage'] < 0) | (df['attendance_percentage'] > 100)])
                if invalid_pct > 0:
                    result["warnings"].append(f"Invalid attendance percentage: {invalid_pct}")
        
        elif domain == "academics":
            if 'gpa' in df.columns:
                invalid_gpa = len(df[(df['gpa'] < 0) | (df['gpa'] > 4.0)])
                if invalid_gpa > 0:
                    result["warnings"].append(f"Invalid GPA values: {invalid_gpa}")
        
        elif domain == "events":
            if 'capacity' in df.columns:
                invalid_cap = len(df[df['capacity'] <= 0])
                if invalid_cap > 0:
                    result["errors"].append(f"Invalid capacity (must be > 0): {invalid_cap}")
        
        elif domain == "transportation":
            if 'capacity' in df.columns:
                invalid_cap = len(df[df['capacity'] <= 0])
                if invalid_cap > 0:
                    result["errors"].append(f"Invalid capacity (must be > 0): {invalid_cap}")
        
        elif domain == "facilities":
            if 'capacity' in df.columns:
                invalid_cap = len(df[df['capacity'] <= 0])
                if invalid_cap > 0:
                    result["errors"].append(f"Invalid capacity (must be > 0): {invalid_cap}")
        
        if not any([result["warnings"], result["errors"]]):
            result["checks"].append("All business rules passed")
    
    def _get_required_columns(self, domain: str) -> List[str]:
        """Get required columns for each domain"""
        required = {
            "students": ["student_id", "name", "email"],
            "attendance": ["student_id", "date"],
            "academics": ["student_id", "course_id", "grade"],
            "events": ["event_id", "name", "date"],
            "transportation": ["vehicle_id", "capacity"],
            "facilities": ["facility_id", "name", "capacity"],
        }
        return required.get(domain, [])
    
    def _get_expected_types(self, domain: str) -> Dict[str, str]:
        """Get expected data types for each domain"""
        types = {
            "students": {"student_id": "string", "age": "numeric"},
            "attendance": {"date": "date", "attendance_percentage": "numeric"},
            "academics": {"gpa": "numeric"},
            "events": {"date": "date", "capacity": "numeric"},
            "transportation": {"capacity": "numeric"},
            "facilities": {"capacity": "numeric"},
        }
        return types.get(domain, {})
    
    def get_report(self) -> Dict:
        """Get the validation report"""
        return self.validation_report
    
    def print_report(self):
        """Print the validation report"""
        logger.info("\n" + "="*60)
        logger.info("VALIDATION REPORT")
        logger.info("="*60)
        
        for domain, report in self.validation_report.items():
            logger.info(f"\n{domain.upper()}:")
            logger.info(f"  Status: {report['validation_status']}")
            logger.info(f"  Total Rows: {report['total_rows']}")
            logger.info(f"  Rows with Issues: {report['rows_with_issues']}")
            
            if report["checks"]:
                logger.info(f"  Checks Passed:")
                for check in report["checks"]:
                    logger.info(f"    OK: {check}")
            
            if report["warnings"]:
                logger.info(f"  Warnings:")
                for warning in report["warnings"]:
                    logger.info(f"    WARNING: {warning}")
            
            if report["errors"]:
                logger.info(f"  Errors:")
                for error in report["errors"]:
                    logger.info(f"    ERROR: {error}")
        
        logger.info("="*60 + "\n")


if __name__ == "__main__":
    from ingestion.ingest import DataIngester
    from processing.cleaning import DataCleaner
    
    ingester = DataIngester()
    data = ingester.ingest_all()
    
    cleaner = DataCleaner()
    cleaned_data = cleaner.clean_all(data)
    
    validator = DataValidator()
    validated_data, report = validator.validate_all(cleaned_data)
    validator.print_report()
