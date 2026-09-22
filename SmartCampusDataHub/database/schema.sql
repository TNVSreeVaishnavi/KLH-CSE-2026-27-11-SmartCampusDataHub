-- Smart Campus Data Hub - Database Schema
-- This schema defines the relational structure for all domains

-- Students Table
CREATE TABLE IF NOT EXISTS students (
    student_id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    age INTEGER,
    gender VARCHAR(50),
    department VARCHAR(255),
    status VARCHAR(50) DEFAULT 'active',
    age_group VARCHAR(50),
    ingestion_timestamp TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create index for email lookups
CREATE INDEX IF NOT EXISTS idx_students_email ON students(email);
CREATE INDEX IF NOT EXISTS idx_students_department ON students(department);
CREATE INDEX IF NOT EXISTS idx_students_status ON students(status);

-- Attendance Table
CREATE TABLE IF NOT EXISTS attendance (
    attendance_id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id VARCHAR(50) NOT NULL,
    date DATE NOT NULL,
    status VARCHAR(50),
    attendance_percentage REAL,
    attendance_level VARCHAR(50),
    ingestion_timestamp TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE,
    UNIQUE(student_id, date)
);

-- Create indexes for attendance queries
CREATE INDEX IF NOT EXISTS idx_attendance_student_id ON attendance(student_id);
CREATE INDEX IF NOT EXISTS idx_attendance_date ON attendance(date);
CREATE INDEX IF NOT EXISTS idx_attendance_status ON attendance(status);

-- Academics Table
CREATE TABLE IF NOT EXISTS academics (
    academic_id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id VARCHAR(50) NOT NULL,
    course_id VARCHAR(50) NOT NULL,
    course_name VARCHAR(255),
    grade VARCHAR(2),
    gpa REAL,
    performance_level VARCHAR(50),
    ingestion_timestamp TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE,
    UNIQUE(student_id, course_id)
);

-- Create indexes for academic queries
CREATE INDEX IF NOT EXISTS idx_academics_student_id ON academics(student_id);
CREATE INDEX IF NOT EXISTS idx_academics_course_id ON academics(course_id);
CREATE INDEX IF NOT EXISTS idx_academics_grade ON academics(grade);

-- Events Table
CREATE TABLE IF NOT EXISTS events (
    event_id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    date DATE NOT NULL,
    event_type VARCHAR(100),
    location VARCHAR(255),
    capacity INTEGER,
    organizer VARCHAR(255),
    ingestion_timestamp TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for event queries
CREATE INDEX IF NOT EXISTS idx_events_date ON events(date);
CREATE INDEX IF NOT EXISTS idx_events_location ON events(location);
CREATE INDEX IF NOT EXISTS idx_events_type ON events(event_type);

-- Transportation Table
CREATE TABLE IF NOT EXISTS transportation (
    vehicle_id VARCHAR(50) PRIMARY KEY,
    vehicle_type VARCHAR(100),
    capacity INTEGER,
    status VARCHAR(50),
    ingestion_timestamp TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for transportation queries
CREATE INDEX IF NOT EXISTS idx_transportation_status ON transportation(status);
CREATE INDEX IF NOT EXISTS idx_transportation_type ON transportation(vehicle_type);

-- Facilities Table
CREATE TABLE IF NOT EXISTS facilities (
    facility_id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    type VARCHAR(100),
    capacity INTEGER,
    location VARCHAR(255),
    status VARCHAR(50),
    ingestion_timestamp TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for facility queries
CREATE INDEX IF NOT EXISTS idx_facilities_type ON facilities(type);
CREATE INDEX IF NOT EXISTS idx_facilities_status ON facilities(status);
CREATE INDEX IF NOT EXISTS idx_facilities_location ON facilities(location);

-- Data Quality Log Table (for tracking data issues)
CREATE TABLE IF NOT EXISTS data_quality_log (
    log_id INTEGER PRIMARY KEY AUTOINCREMENT,
    domain VARCHAR(50),
    issue_type VARCHAR(100),
    description TEXT,
    severity VARCHAR(20),
    log_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_quality_log_domain ON data_quality_log(domain);
CREATE INDEX IF NOT EXISTS idx_quality_log_timestamp ON data_quality_log(log_timestamp);
