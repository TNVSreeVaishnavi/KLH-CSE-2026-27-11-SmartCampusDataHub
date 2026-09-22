#!/usr/bin/env python3
"""
Generate realistic sample data with intentional data quality issues
"""

import pandas as pd
import numpy as np
from pathlib import Path
import random
from datetime import datetime, timedelta

# Set random seed for reproducibility
np.random.seed(42)
random.seed(42)

OUTPUT_PATH = Path(__file__).parent.parent / "data" / "raw"
OUTPUT_PATH.mkdir(parents=True, exist_ok=True)

def generate_students_data(n_records=100):
    """Generate sample students data with quality issues"""
    
    departments = ["Computer Science", "Engineering", "Business", "Arts", "Science", "Medicine"]
    statuses = ["Active", "ACTIVE", "active", "Inactive", "INACTIVE", "Graduated", "On Leave"]
    genders = ["Male", "Female", "Other", "M", "F", None]
    
    data = {
        'student_id': [f"STU{str(i).zfill(5)}" for i in range(1, n_records + 1)],
        'name': [f"Student {i}" for i in range(1, n_records + 1)],
        'email': [f"student{i}@campus.edu" if i % 10 != 0 else None for i in range(1, n_records + 1)],
        'age': [random.randint(15, 65) if i % 15 != 0 else random.randint(-5, 100) for i in range(n_records)],
        'gender': [random.choice(genders) for _ in range(n_records)],
        'department': [random.choice(departments) for _ in range(n_records)],
        'status': [random.choice(statuses) for _ in range(n_records)]
    }
    
    df = pd.DataFrame(data)
    
    # Introduce quality issues
    # Add whitespace
    df.loc[5:10, 'name'] = '  ' + df.loc[5:10, 'name'] + '  '
    df.loc[15:20, 'department'] = df.loc[15:20, 'department'].str.lower()
    
    # Add duplicates
    df = pd.concat([df, df.iloc[0:5]], ignore_index=True)
    
    # Add more missing values
    df.loc[25:30, 'email'] = None
    df.loc[35:40, 'gender'] = None
    
    return df

def generate_attendance_data(n_records=200):
    """Generate sample attendance data with quality issues"""
    
    student_ids = [f"STU{str(i).zfill(5)}" for i in range(1, 101)]
    statuses = ["Present", "PRESENT", "present", "Absent", "ABSENT", "Late", "LATE", "Excused", "EXCUSED"]
    base_date = datetime(2024, 1, 1)
    
    data = {
        'student_id': [random.choice(student_ids) for _ in range(n_records)],
        'date': [base_date + timedelta(days=random.randint(0, 30)) for _ in range(n_records)],
        'status': [random.choice(statuses) for _ in range(n_records)],
        'attendance_percentage': [random.choice([random.randint(0, 100), -10, 150, None]) for _ in range(n_records)]
    }
    
    df = pd.DataFrame(data)
    
    # Introduce quality issues
    # Add whitespace
    df.loc[10:20, 'status'] = '  ' + df.loc[10:20, 'status'] + '  '
    
    # Add duplicates
    df = pd.concat([df, df.iloc[0:10]], ignore_index=True)
    
    # Add inconsistent date formats (will cause issues)
    df.loc[30:35, 'date'] = df.loc[30:35, 'date'].astype(str)
    
    return df

def generate_academics_data(n_records=150):
    """Generate sample academics data with quality issues"""
    
    student_ids = [f"STU{str(i).zfill(5)}" for i in range(1, 101)]
    courses = ["CS101", "CS102", "MATH201", "PHYS101", "CHEM101", "ENG101"]
    course_names = ["Programming", "Data Structures", "Calculus", "Physics", "Chemistry", "English"]
    grades = ["A", "B", "C", "D", "F", "a", "b", "c", None]
    
    data = {
        'student_id': [random.choice(student_ids) for _ in range(n_records)],
        'course_id': [random.choice(courses) for _ in range(n_records)],
        'course_name': [random.choice(course_names) for _ in range(n_records)],
        'grade': [random.choice(grades) for _ in range(n_records)],
        'gpa': [random.choice([random.uniform(0, 4.0), -1, 5.5, None]) for _ in range(n_records)]
    }
    
    df = pd.DataFrame(data)
    
    # Introduce quality issues
    # Add duplicates
    df = pd.concat([df, df.iloc[0:15]], ignore_index=True)
    
    return df

def generate_events_data(n_records=50):
    """Generate sample events data with quality issues"""
    
    event_types = ["Seminar", "SEMINAR", "seminar", "Conference", "Workshop", "Social"]
    locations = ["Auditorium", "AUDITORIUM", "auditorium", "Cafeteria", "Gym", "Library", None]
    organizers = ["Student Council", "Administration", "Department", "Club"]
    base_date = datetime(2024, 1, 1)
    
    data = {
        'event_id': [f"EVT{str(i).zfill(4)}" for i in range(1, n_records + 1)],
        'name': [f"Event {i}" for i in range(1, n_records + 1)],
        'date': [base_date + timedelta(days=random.randint(0, 365)) for _ in range(n_records)],
        'location': [random.choice(locations) for _ in range(n_records)],
        'capacity': [random.choice([random.randint(1, 500), -50, 0, None]) for _ in range(n_records)],
        'organizer': [random.choice(organizers) for _ in range(n_records)]
    }
    
    df = pd.DataFrame(data)
    
    # Introduce quality issues
    # Add whitespace
    df.loc[5:10, 'location'] = '  ' + df.loc[5:10, 'location'] + '  '
    
    # Add duplicates
    df = pd.concat([df, df.iloc[0:5]], ignore_index=True)
    
    return df

def generate_transportation_data(n_records=30):
    """Generate sample transportation data with quality issues"""
    
    vehicle_types = ["Bus", "BUS", "bus", "Shuttle", "SHUTTLE", "Taxi", "Car"]
    statuses = ["Active", "ACTIVE", "active", "Maintenance", "MAINTENANCE", "Inactive"]
    
    data = {
        'vehicle_id': [f"VEH{str(i).zfill(4)}" for i in range(1, n_records + 1)],
        'vehicle_type': [random.choice(vehicle_types) for _ in range(n_records)],
        'capacity': [random.choice([random.randint(1, 100), -10, 0, None]) for _ in range(n_records)],
        'status': [random.choice(statuses) for _ in range(n_records)]
    }
    
    df = pd.DataFrame(data)
    
    # Introduce quality issues
    # Add whitespace
    df.loc[3:8, 'vehicle_type'] = '  ' + df.loc[3:8, 'vehicle_type'] + '  '
    
    # Add duplicates
    df = pd.concat([df, df.iloc[0:3]], ignore_index=True)
    
    return df

def generate_facilities_data(n_records=40):
    """Generate sample facilities data with quality issues"""
    
    facility_types = ["Classroom", "CLASSROOM", "classroom", "Lab", "LAB", "Lab", "Cafeteria", "Library"]
    statuses = ["Operational", "OPERATIONAL", "operational", "Maintenance", "MAINTENANCE", "Closed"]
    locations = ["Building A", "BUILDING A", "building a", "Building B", "Building C", None]
    
    data = {
        'facility_id': [f"FAC{str(i).zfill(4)}" for i in range(1, n_records + 1)],
        'name': [f"Facility {i}" for i in range(1, n_records + 1)],
        'type': [random.choice(facility_types) for _ in range(n_records)],
        'capacity': [random.choice([random.randint(1, 500), -50, 0, None]) for _ in range(n_records)],
        'location': [random.choice(locations) for _ in range(n_records)],
        'status': [random.choice(statuses) for _ in range(n_records)]
    }
    
    df = pd.DataFrame(data)
    
    # Introduce quality issues
    # Add whitespace
    df.loc[5:10, 'type'] = '  ' + df.loc[5:10, 'type'] + '  '
    
    # Add duplicates
    df = pd.concat([df, df.iloc[0:5]], ignore_index=True)
    
    return df

def main():
    """Generate all sample datasets"""
    
    print("Generating sample data with quality issues...")
    
    datasets = {
        'students': generate_students_data(100),
        'attendance': generate_attendance_data(200),
        'academics': generate_academics_data(150),
        'events': generate_events_data(50),
        'transportation': generate_transportation_data(30),
        'facilities': generate_facilities_data(40)
    }
    
    # Save all datasets
    for name, df in datasets.items():
        filepath = OUTPUT_PATH / f"{name}.csv"
        df.to_csv(filepath, index=False)
        print(f"Generated {name}.csv ({len(df)} rows)")
    
    print(f"\nSample data saved to: {OUTPUT_PATH}")
    print("\nData Quality Issues Introduced:")
    print("  - Missing values (NaN)")
    print("  - Duplicate records")
    print("  - Inconsistent text capitalization (Upper, lower, Title case)")
    print("  - Inconsistent whitespace (leading/trailing spaces)")
    print("  - Invalid values (negative ages, GPA > 4.0, attendance > 100%)")
    print("  - Inconsistent date formats")
    print("  - Null values in required fields")
    
    return True

if __name__ == "__main__":
    main()
