"""
Unit tests for Smart Campus Data Hub
"""

import unittest
import sqlite3
import pandas as pd
import numpy as np
import sys
from pathlib import Path

from database.connection import DatabaseConnection, DatabaseManager

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from processing.cleaning import DataCleaner
from processing.validation import DataValidator
from processing.transformation import DataTransformer

class TestDataCleaner(unittest.TestCase):
    """Test data cleaning functions"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.cleaner = DataCleaner()
    
    def test_remove_whitespace(self):
        """Test whitespace removal"""
        df = pd.DataFrame({
            'name': ['  John  ', 'Jane  ', '  Bob']
        })
        
        cleaned = self.cleaner._remove_whitespace(df)
        self.assertEqual(cleaned['name'][0], 'John')
        self.assertEqual(cleaned['name'][1], 'Jane')
        self.assertEqual(cleaned['name'][2], 'Bob')
    
    def test_remove_duplicates(self):
        """Test duplicate removal"""
        df = pd.DataFrame({
            'id': [1, 2, 2, 3],
            'name': ['a', 'b', 'b', 'c']
        })
        
        cleaned, dup_count = self.cleaner._remove_duplicates(df)
        self.assertEqual(len(cleaned), 3)
        self.assertEqual(dup_count, 1)
    
    def test_handle_missing_values_numeric(self):
        """Test missing value handling for numeric columns"""
        df = pd.DataFrame({
            'age': [20, np.nan, 25],
            'score': [80, 90, np.nan]
        })
        
        cleaned = self.cleaner._handle_missing_values(df, 'test')
        self.assertEqual(cleaned['age'].isna().sum(), 0)
        self.assertEqual(cleaned['score'].isna().sum(), 0)
        # Numeric columns should be filled with 0
        self.assertEqual(cleaned['age'][1], 0)
        self.assertEqual(cleaned['score'][2], 0)
    
    def test_handle_missing_values_string(self):
        """Test missing value handling for string columns"""
        df = pd.DataFrame({
            'name': ['John', None, 'Jane'],
            'city': ['NYC', 'LA', None]
        })
        
        cleaned = self.cleaner._handle_missing_values(df, 'test')
        self.assertEqual(cleaned['name'].isna().sum(), 0)
        self.assertEqual(cleaned['city'].isna().sum(), 0)
        # String columns should be filled with 'Unknown'
        self.assertEqual(cleaned['name'][1], 'Unknown')
        self.assertEqual(cleaned['city'][2], 'Unknown')
    
    def test_standardize_dates(self):
        """Test date standardization"""
        df = pd.DataFrame({
            'date': ['2024-01-01', '01/01/2024', '2024-01-01']
        })
        
        cleaned = self.cleaner._standardize_dates(df)
        self.assertTrue(pd.api.types.is_datetime64_any_dtype(cleaned['date']))
    
    def test_handle_invalid_values_students(self):
        """Test invalid value handling for students domain"""
        df = pd.DataFrame({
            'age': [15, 100, 25],
            'status': ['active', 'invalid_status', 'inactive']
        })
        
        cleaned = self.cleaner._handle_invalid_values(df, 'students')
        # Age outside range should be replaced
        self.assertGreaterEqual(cleaned['age'][1], 15)
        self.assertLessEqual(cleaned['age'][1], 65)
        # Invalid status should be replaced with 'active'
        self.assertEqual(cleaned['status'][1], 'active')


    def test_init_schema_migrates_legacy_events_table(self):
        """Test schema init adds missing columns to an older SQLite table."""
        db_path = Path(__file__).parent / "test_legacy_schema.db"
        if db_path.exists():
            db_path.unlink()

        conn = sqlite3.connect(db_path)
        conn.execute(
            """
            CREATE TABLE events (
                event_id TEXT PRIMARY KEY,
                name TEXT,
                date TEXT,
                location TEXT,
                capacity INTEGER,
                organizer TEXT
            )
            """
        )
        conn.close()

        db = DatabaseConnection()
        db.connection = sqlite3.connect(db_path)
        db.connection.row_factory = sqlite3.Row

        schema_path = Path(__file__).parent.parent / "database" / "schema.sql"
        self.assertTrue(db.init_schema(schema_path))

        columns = db.execute_query("PRAGMA table_info(events)")
        names = {row["name"] for row in columns}
        self.assertIn("event_type", names)
        db.connection.close()
        db_path.unlink(missing_ok=True)


class TestDataValidator(unittest.TestCase):
    """Test data validation functions"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.validator = DataValidator()
    
    def test_check_null_values(self):
        """Test null value checking"""
        df = pd.DataFrame({
            'id': [1, 2, None],
            'name': ['a', None, 'c']
        })
        
        result = {'checks': [], 'warnings': [], 'errors': [], 'rows_with_issues': 0}
        self.validator._check_null_values(df, result)
        
        # Should have warnings about null values
        self.assertGreater(len(result['warnings']), 0)
        self.assertGreater(result['rows_with_issues'], 0)
    
    def test_check_duplicates(self):
        """Test duplicate checking"""
        df = pd.DataFrame({
            'id': [1, 2, 1],
            'name': ['a', 'b', 'a']
        })
        
        result = {'checks': [], 'warnings': [], 'errors': [], 'rows_with_issues': 0}
        self.validator._check_duplicates(df, result)
        
        # Should have warnings about duplicates
        self.assertGreater(len(result['warnings']), 0)
    
    def test_check_business_rules_students(self):
        """Test business rules for students"""
        df = pd.DataFrame({
            'age': [15, 100, 25],
            'student_id': ['1', '2', '2']
        })
        
        result = {'checks': [], 'warnings': [], 'errors': [], 'rows_with_issues': 0}
        self.validator._check_business_rules(df, 'students', result)
        
        # Should have warnings about invalid ages
        has_age_warning = any('age' in w.lower() for w in result['warnings'])
        self.assertTrue(has_age_warning)
    
    def test_validate_attendance_percentage(self):
        """Test attendance percentage validation"""
        df = pd.DataFrame({
            'attendance_percentage': [50, 150, -10, 100]
        })
        
        result = {'checks': [], 'warnings': [], 'errors': [], 'rows_with_issues': 0}
        self.validator._check_business_rules(df, 'attendance', result)
        
        # Should have warnings about invalid percentages
        self.assertGreater(len(result['warnings']), 0)


class TestDataTransformer(unittest.TestCase):
    """Test data transformation functions"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.transformer = DataTransformer()
    
    def test_standardize_column_names(self):
        """Test column name standardization"""
        df = pd.DataFrame({
            'Student ID': [1, 2],
            'First Name': ['John', 'Jane'],
            'Date-Of-Birth': ['2000-01-01', '2001-01-01']
        })
        
        transformed = self.transformer._standardize_column_names(df)
        
        # Column names should be lowercase with underscores
        self.assertIn('student_id', transformed.columns)
        self.assertIn('first_name', transformed.columns)
        self.assertIn('date_of_birth', transformed.columns)
    
    def test_convert_data_types(self):
        """Test data type conversion"""
        df = pd.DataFrame({
            'student_id': ['1', '2', '3'],
            'age': ['20', '21', '22'],
            'gpa': ['3.5', '3.8', '3.2'],
            'date': ['2024-01-01', '2024-01-02', '2024-01-03']
        })
        
        transformed = self.transformer._convert_data_types(df, 'students')
        
        # IDs should be strings
        self.assertEqual(transformed['student_id'].dtype, object)
        # Numeric columns should be numeric
        self.assertTrue(pd.api.types.is_numeric_dtype(transformed['age']))
        self.assertTrue(pd.api.types.is_numeric_dtype(transformed['gpa']))
        # Dates should be datetime
        self.assertTrue(pd.api.types.is_datetime64_any_dtype(transformed['date']))
    
    def test_reorder_columns(self):
        """Test column reordering"""
        df = pd.DataFrame({
            'other_col': [1, 2],
            'student_id': ['1', '2'],
            'name': ['John', 'Jane'],
            'email': ['john@test.com', 'jane@test.com'],
            'age': [20, 21]
        })
        
        transformed = self.transformer._reorder_columns(df, 'students')
        
        # Priority columns should come first
        first_cols = transformed.columns[:3]
        self.assertIn('student_id', first_cols)
        self.assertIn('name', first_cols)
        self.assertIn('email', first_cols)
    
    def test_add_ingestion_timestamp(self):
        """Test ingestion timestamp addition"""
        df = pd.DataFrame({
            'id': [1, 2],
            'name': ['a', 'b']
        })
        
        transformed = self.transformer._create_derived_fields(df, 'students')
        
        # Should have ingestion_timestamp column
        self.assertIn('ingestion_timestamp', transformed.columns)
        self.assertTrue(pd.api.types.is_datetime64_any_dtype(transformed['ingestion_timestamp']))


class TestDatabaseInserts(unittest.TestCase):
    """Database integration checks"""

    def test_insert_dataframe_handles_timestamps(self):
        """SQLite insert should accept pandas timestamps by converting them to strings"""
        schema_path = Path(__file__).parent.parent / "database" / "schema.sql"
        manager = DatabaseManager()
        manager.initialize(schema_path)

        try:
            df = pd.DataFrame({
                'student_id': ['DB001', 'DB002'],
                'name': ['Alice Example', 'Bob Example'],
                'email': ['alice@example.com', 'bob@example.com'],
                'age': [20, 21],
                'gender': ['Female', 'Male'],
                'department': ['Computer Science', 'Engineering'],
                'status': ['active', 'active'],
                'age_group': ['18-22', '18-22'],
                'ingestion_timestamp': [pd.Timestamp.now(), pd.Timestamp.now()],
            })

            inserted, failed = manager.insert_dataframe(df, 'students')
            self.assertEqual(inserted, 2)
            self.assertEqual(failed, 0)
        finally:
            manager.close()


class TestPipelineIntegration(unittest.TestCase):
    """Integration tests for the pipeline"""

    def test_validation_report_uses_ascii_only_log_messages(self):
        """Validation logs should avoid Unicode symbols that break Windows cp1252 consoles."""
        validator = DataValidator()
        df = pd.DataFrame({
            'student_id': ['S1', 'S2'],
            'name': ['Alice', 'Bob'],
            'email': ['alice@example.com', 'bob@example.com'],
            'age': [20, 70],
        })

        validator.validate_dataframe(df, 'students')
        report_lines = []

        for domain, report in validator.get_report().items():
            report_lines.append(f"{domain}: {report['validation_status']}")
            for warning in report['warnings']:
                report_lines.append(warning)
            for error in report['errors']:
                report_lines.append(error)

        joined = "\n".join(report_lines)
        self.assertNotIn('⚠', joined)
        self.assertNotIn('✗', joined)
        self.assertNotIn('✓', joined)

    def test_cleaning_validation_transformation_pipeline(self):
        """Test the cleaning -> validation -> transformation pipeline"""
        
        # Create sample data with quality issues
        df = pd.DataFrame({
            'student_id': ['STU001', 'STU002', 'STU002'],  # Duplicate
            'name': ['  John Doe  ', 'jane SMITH', 'jane SMITH'],  # Whitespace and case
            'email': ['john@test.com', None, None],  # Missing values
            'age': [20, 150, 22],  # Invalid value
            'status': ['active', 'ACTIVE', 'active']  # Inconsistent case
        })
        
        # Cleaning
        cleaner = DataCleaner()
        cleaned = cleaner._remove_whitespace(df.copy())
        cleaned = cleaner._standardize_text(cleaned)
        cleaned = cleaner._handle_missing_values(cleaned, 'students')
        cleaned, _ = cleaner._remove_duplicates(cleaned)
        cleaned = cleaner._handle_invalid_values(cleaned, 'students')
        
        # After cleaning
        self.assertEqual(len(cleaned), 2)  # One duplicate removed
        self.assertEqual(cleaned['name'][0], 'John Doe')  # Whitespace removed
        self.assertNotEqual(cleaned['email'][1], None)  # Missing value handled
        
        # Validation
        validator = DataValidator()
        validated, validation_report = validator.validate_dataframe(cleaned, 'students')
        
        # Transformation
        transformer = DataTransformer()
        transformed = transformer.transform_dataframe(validated, 'students')
        
        # After transformation
        self.assertIn('student_id', transformed.columns)
        self.assertTrue(pd.api.types.is_datetime64_any_dtype(transformed['ingestion_timestamp']))


def run_tests():
    """Run all tests"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestDataCleaner))
    suite.addTests(loader.loadTestsFromTestCase(TestDataValidator))
    suite.addTests(loader.loadTestsFromTestCase(TestDataTransformer))
    suite.addTests(loader.loadTestsFromTestCase(TestPipelineIntegration))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
