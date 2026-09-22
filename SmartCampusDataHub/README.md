# Smart Campus Data Hub

A comprehensive data engineering platform for centralizing, processing, and analyzing campus-related data from multiple sources.

## 📋 Project Overview

The Smart Campus Data Hub is designed to collect data from six major campus domains, apply rigorous data quality processes, centralize the data in a database, and provide analytics and insights through an interactive dashboard.

### Problem Statement

Universities and campuses manage data across multiple systems and formats:
- Student management systems
- Attendance tracking
- Academic records
- Event management
- Transportation systems
- Facility management

This scattered data prevents insights and makes it difficult to:
- Understand campus-wide patterns
- Make data-driven decisions
- Monitor data quality
- Generate comprehensive reports

### Solution

The Smart Campus Data Hub provides:
1. **Unified Data Ingestion** - Collect from multiple CSV sources
2. **Data Quality Pipeline** - Clean, validate, and standardize data
3. **Centralized Storage** - Single source of truth in a relational database
4. **Analytics Engine** - SQL-based queries for insights
5. **Interactive Dashboard** - Streamlit-based visualization layer

## 🏗️ Architecture

```
Data Sources (CSV Files)
    ↓
┌─────────────────────────┐
│ INGESTION               │ - Read CSV files
└─────────────────────────┘ - Detect missing files
    ↓
┌─────────────────────────┐
│ CLEANING                │ - Remove whitespace
└─────────────────────────┘ - Standardize text
    ↓                       - Handle missing values
┌─────────────────────────┐ - Remove duplicates
│ VALIDATION              │ - Fix invalid values
└─────────────────────────┘
    ↓
┌─────────────────────────┐
│ TRANSFORMATION          │ - Standardize column names
└─────────────────────────┘ - Convert data types
    ↓                       - Normalize categories
┌─────────────────────────┐ - Create derived fields
│ DATABASE LOADING        │
└─────────────────────────┘
    ↓
┌─────────────────────────┐
│ CENTRALIZED DATABASE    │ - SQLite database
└─────────────────────────┘ - 6 main tables
    ↓
┌─────────────────────────┐
│ ANALYTICS               │ - SQL queries
└─────────────────────────┘ - Business intelligence
    ↓
┌─────────────────────────┐
│ STREAMLIT DASHBOARD     │ - Interactive visualizations
└─────────────────────────┘ - KPIs and reports
```

## 📁 Project Structure

```
smart-campus-data-hub/
│
├── data/                          # Data storage
│   ├── raw/                       # Raw CSV input files
│   ├── processed/                 # Processed CSV files after pipeline
│   └── sample/                    # Sample data for testing
│
├── config/
│   └── config.py                  # Configuration and environment setup
│
├── ingestion/
│   ├── __init__.py
│   └── ingest.py                  # Data ingestion module
│
├── processing/
│   ├── __init__.py
│   ├── cleaning.py                # Data cleaning functions
│   ├── validation.py              # Data validation rules
│   └── transformation.py          # Data transformation logic
│
├── database/
│   ├── __init__.py
│   ├── connection.py              # Database connection management
│   ├── schema.sql                 # Database schema
│   └── load_data.py               # Data loading module
│
├── analytics/
│   ├── __init__.py
│   └── queries.py                 # Analytics and reporting queries
│
├── dashboard/
│   └── app.py                     # Streamlit dashboard application
│
├── scripts/
│   ├── run_pipeline.py            # Main pipeline orchestrator
│   └── generate_sample_data.py    # Generate sample data
│
├── tests/
│   └── test_pipeline.py           # Unit tests
│
├── logs/                          # Application logs
│
├── requirements.txt               # Python dependencies
├── .env.example                   # Environment variables template
├── .gitignore                     # Git ignore file
└── README.md                      # This file
```

## 🛢️ Database Schema

### Students Table
- **student_id** (PK): Unique student identifier
- **name**: Student name
- **email**: Student email (unique)
- **age**: Age
- **gender**: Gender
- **department**: Department
- **status**: Active/Inactive/Graduated
- **age_group**: Derived field for age grouping

### Attendance Table
- **attendance_id** (PK): Unique identifier
- **student_id** (FK): Reference to students
- **date**: Attendance date
- **status**: Present/Absent/Late/Excused
- **attendance_percentage**: Calculated percentage
- **attendance_level**: Derived field (Poor/Fair/Good/Excellent)

### Academics Table
- **academic_id** (PK): Unique identifier
- **student_id** (FK): Reference to students
- **course_id**: Course identifier
- **course_name**: Course name
- **grade**: Letter grade (A-F)
- **gpa**: Grade point average
- **performance_level**: Derived field (Low/Medium/High/Excellent)

### Events Table
- **event_id** (PK): Unique event identifier
- **name**: Event name
- **date**: Event date
- **location**: Event location
- **capacity**: Event capacity
- **organizer**: Organizing entity

### Transportation Table
- **vehicle_id** (PK): Unique vehicle identifier
- **vehicle_type**: Bus/Shuttle/Taxi/Car
- **capacity**: Vehicle capacity
- **status**: Active/Maintenance/Inactive

### Facilities Table
- **facility_id** (PK): Unique facility identifier
- **name**: Facility name
- **type**: Classroom/Lab/Cafeteria/Library
- **capacity**: Facility capacity
- **location**: Building/location
- **status**: Operational/Maintenance/Closed

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- pip (Python package manager)
- Git

### Installation

1. **Clone/Navigate to the project:**
   ```bash
   cd smart-campus-data-hub
   ```

2. **Create a virtual environment (recommended):**
   ```bash
   python -m venv venv
   source venv/Scripts/activate  # On Windows
   # or
   source venv/bin/activate      # On macOS/Linux
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env if you need to change database configuration
   ```

### Generate Sample Data

The project includes a sample data generator that creates realistic data with intentional quality issues:

```bash
python scripts/generate_sample_data.py
```

This generates CSV files in `data/raw/`:
- `students.csv` (100 records)
- `attendance.csv` (200 records)
- `academics.csv` (150 records)
- `events.csv` (50 records)
- `transportation.csv` (30 records)
- `facilities.csv` (40 records)

**Intentional Data Quality Issues:**
- Missing values (NaN)
- Duplicate records
- Inconsistent text capitalization
- Inconsistent whitespace
- Invalid values (negative ages, GPA > 4.0, attendance > 100%)
- Inconsistent date formats
- Null values in required fields

### Run the Pipeline

Execute the complete data pipeline:

```bash
python scripts/run_pipeline.py
```

This will:
1. **Ingest** raw CSV files
2. **Clean** data (remove whitespace, fix formatting, handle missing values)
3. **Validate** data against business rules
4. **Transform** data (standardize columns, convert types, create derived fields)
5. **Load** processed data into SQLite database
6. **Analyze** and generate reports

### Start the Dashboard

Launch the interactive Streamlit dashboard:

```bash
streamlit run dashboard/app.py
```

The dashboard will open in your browser at `http://localhost:8501` with sections for:
- **Overview**: Key KPIs
- **Students**: Student statistics and distribution
- **Attendance**: Attendance metrics and low-attendance alerts
- **Academics**: Grade distribution and top performers
- **Events**: Event statistics by location
- **Transportation**: Vehicle status and types
- **Facilities**: Facility status and types
- **Data Quality**: Quality metrics for each domain

### Run Tests

Execute the unit test suite:

```bash
python tests/test_pipeline.py
```

## 📊 Data Processing Pipeline

### 1. Ingestion
- Reads CSV files from `data/raw/`
- Records file names, row counts, and column information
- Logs any missing files or errors

### 2. Cleaning
Applies data quality fixes:
- **Whitespace Removal**: Strips leading/trailing spaces
- **Text Standardization**: Title-cases text fields
- **Date Standardization**: Converts to consistent datetime format
- **Missing Value Handling**: 
  - Numeric columns → filled with 0
  - String columns → filled with "Unknown"
  - Datetime → filled with mode or minimum value
- **Duplicate Removal**: Removes exact row duplicates
- **Invalid Value Handling**: Domain-specific fixes
  - Students: Age 15-65, valid status values
  - Attendance: Percentage 0-100, valid status
  - Academics: GPA 0-4.0, valid grades
  - Events/Transportation/Facilities: Positive capacity

### 3. Validation
Checks data quality against rules:
- **Required Columns**: Ensures all necessary columns exist
- **Data Types**: Verifies appropriate data types
- **Null Values**: Detects and reports missing data
- **Duplicates**: Identifies duplicate rows
- **Business Rules**: 
  - Age ranges
  - Percentage ranges
  - GPA ranges
  - Unique IDs
  - Referential consistency

Produces validation report with pass/fail status and detailed findings.

### 4. Transformation
Prepares data for storage:
- **Column Name Standardization**: Converts to snake_case
- **Data Type Conversion**: 
  - IDs → strings
  - Numeric fields → numeric types
  - Dates → datetime types
- **Categorical Normalization**: Lowercase status fields, standardize codes
- **Derived Field Creation**:
  - Student: age_group (based on age ranges)
  - Academics: performance_level (based on GPA)
  - Attendance: attendance_level (based on percentage)
- **Ingestion Timestamp**: Adds processing timestamp to all records

### 5. Loading
Loads processed data into database:
- Creates tables if they don't exist
- Inserts transformed dataframes
- Handles potential duplicate loads
- Reports success/failure for each domain
- Saves processed CSV files to `data/processed/`

### 6. Analytics
Runs SQL queries to generate insights:
- Student statistics (total, by department)
- Attendance metrics (average, by status, low attendance alerts)
- Academic performance (GPA stats, grade distribution, top performers)
- Event statistics (total, by location, capacity)
- Transportation status (by status, by vehicle type)
- Facility status (by status, by type, by location)
- Data quality metrics (null counts, invalid values)

## 📈 Analytics Queries

The system provides numerous analytics queries:

### Students
- Total student count
- Students by department
- Student demographics

### Attendance
- Average attendance percentage
- Attendance by status
- Students with low attendance (<75%)
- Attendance trends

### Academics
- Average GPA
- Grade distribution
- Top academic performers
- Performance by course

### Events
- Total events
- Events by location
- Event capacity analysis

### Transportation
- Vehicle status
- Vehicles by type
- Fleet capacity

### Facilities
- Facility status
- Facilities by type
- Facility distribution

### Data Quality
- Record counts by domain
- Null value counts
- Invalid value counts
- Data completeness metrics

## 🧪 Testing

Unit tests verify:
- **Whitespace removal**
- **Duplicate detection and removal**
- **Missing value handling**
- **Date standardization**
- **Invalid value correction**
- **Column name standardization**
- **Data type conversion**
- **Column reordering**
- **Validation rules**
- **Full pipeline integration**

Run tests:
```bash
python tests/test_pipeline.py
```

## 📝 Logging

The system logs all activities:
- Ingestion status and row counts
- Cleaning operations and rows removed
- Validation warnings and errors
- Transformation steps and column changes
- Database loading results
- Analytics query results

Log files are stored in `logs/` directory.

Enable debug logging by setting `LOG_LEVEL=DEBUG` in `.env`.

## ⚙️ Configuration

Configure the system via `.env` file:

```env
# Database Configuration
DB_TYPE=sqlite
DB_PATH=./data/smart_campus.db

# For PostgreSQL (when DB_TYPE=postgresql):
# DB_HOST=localhost
# DB_PORT=5432
# DB_USER=postgres
# DB_PASSWORD=your_password
# DB_NAME=smart_campus

# Logging
LOG_LEVEL=INFO

# Pipeline
CHUNK_SIZE=1000
VALIDATION_STRICT_MODE=False
```

## 🔒 Security

- No hardcoded passwords (use .env file)
- Database connections properly handled
- Input validation on all data
- Logging of all pipeline operations
- No sensitive data in version control

## 🚨 Error Handling

The system includes robust error handling:
- Graceful handling of missing input files
- Detailed error messages in logs
- Continues pipeline despite warnings
- Prevents accidental duplicate data loads
- Transaction rollback on database errors
- Comprehensive exception logging

## 📊 Data Quality Demonstrations

The sample data demonstrates real quality issues:

**Before Pipeline:**
- Duplicate records
- Inconsistent capitalization
- Missing values
- Invalid data types
- Whitespace problems
- Out-of-range values

**After Pipeline:**
- Clean, deduplicated data
- Consistent formatting
- Null values handled appropriately
- Correct data types
- No whitespace issues
- Valid value ranges

## 🔄 Reproducibility

The pipeline is fully reproducible:
1. Generate sample data: `python scripts/generate_sample_data.py`
2. Run pipeline: `python scripts/run_pipeline.py`
3. View results in dashboard: `streamlit run dashboard/app.py`

Same inputs always produce the same outputs due to:
- Fixed random seeds in sample generation
- Deterministic cleaning rules
- Consistent transformation logic
- Proper transaction handling in database

## 📚 Technologies Used

- **Python 3.8+**: Core language
- **Pandas**: Data manipulation and processing
- **NumPy**: Numerical computations
- **SQLite**: Relational database
- **Streamlit**: Web dashboard framework
- **Plotly**: Interactive visualizations
- **Python-dotenv**: Environment variable management
- **SQLAlchemy**: Database ORM (optional)

## 🎯 Future Enhancements

Potential improvements:
- Support for additional data sources (APIs, databases)
- Real-time data streaming
- Advanced data profiling and anomaly detection
- Machine learning models for predictions
- Data export to various formats (Excel, Parquet)
- Role-based access control for dashboard
- Data lineage and audit trails
- Incremental data loading
- Automated data quality monitoring
- Integration with data warehouse (Snowflake, BigQuery)
- Advanced visualization options
- Custom report generation

## 📞 Support

For issues or questions:
1. Check the logs in `logs/` directory
2. Review README and documentation
3. Check data in `data/processed/` for debugging
4. Run tests to verify components

## 📄 License

[Add your license information here]

## 👥 Authors

Smart Campus Data Hub Development Team

---

**Last Updated**: 2024
**Version**: 1.0.0
