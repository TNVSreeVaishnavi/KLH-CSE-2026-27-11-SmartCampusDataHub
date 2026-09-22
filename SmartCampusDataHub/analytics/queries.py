import logging
from typing import Dict, List

from config.config import get_logger
from database.thread_safe_connection import ThreadSafeConnection

logger = get_logger(__name__)

class AnalyticsQueries:
    """Provides analytics queries for the campus data using thread-safe connections"""
    
    def __init__(self):
        """Initialize with thread-safe database connection factory"""
        self.db = ThreadSafeConnection()

    def close(self) -> None:
        """Keep the pipeline cleanup contract; connections are per-query."""
        return None
    
    def get_total_students(self) -> int:
        """Get total number of students"""
        query = "SELECT COUNT(*) as count FROM students"
        result = self.db.execute_query(query)
        return result[0]['count'] if result else 0
    
    def get_students_by_department(self) -> List[Dict]:
        """Get student count by department"""
        query = """
            SELECT department, COUNT(*) as count
            FROM students
            WHERE department != 'Unknown'
            GROUP BY department
            ORDER BY count DESC
        """
        return self.db.execute_query(query)
    
    def get_student_details(self, limit: int = 10) -> List[Dict]:
        """Get sample student details"""
        query = f"""
            SELECT student_id, name, email, age, gender, department, status
            FROM students
            LIMIT {limit}
        """
        return self.db.execute_query(query)
    
    def get_attendance_statistics(self) -> Dict:
        """Get overall attendance statistics"""
        query = """
            SELECT 
                COUNT(DISTINCT student_id) as total_students,
                AVG(attendance_percentage) as avg_attendance,
                MIN(attendance_percentage) as min_attendance,
                MAX(attendance_percentage) as max_attendance
            FROM attendance
        """
        result = self.db.execute_query(query)
        if result:
            row = result[0]
            return {
                'total_students': row['total_students'],
                'avg_attendance': round(row['avg_attendance'], 2) if row['avg_attendance'] else 0,
                'min_attendance': row['min_attendance'],
                'max_attendance': row['max_attendance']
            }
        return {}
    
    def get_low_attendance_students(self, threshold: float = 75.0) -> List[Dict]:
        """Get students with low attendance"""
        query = f"""
            SELECT DISTINCT 
                s.student_id, 
                s.name, 
                s.email,
                AVG(a.attendance_percentage) as avg_attendance
            FROM students s
            JOIN attendance a ON s.student_id = a.student_id
            GROUP BY s.student_id, s.name, s.email
            HAVING AVG(a.attendance_percentage) < {threshold}
            ORDER BY avg_attendance ASC
        """
        return self.db.execute_query(query)
    
    def get_attendance_by_status(self) -> List[Dict]:
        """Get attendance breakdown by status"""
        query = """
            SELECT status, COUNT(*) as count, 
                   ROUND(AVG(attendance_percentage), 2) as avg_attendance
            FROM attendance
            GROUP BY status
            ORDER BY count DESC
        """
        return self.db.execute_query(query)
    
    def get_academic_statistics(self) -> Dict:
        """Get overall academic statistics"""
        query = """
            SELECT 
                COUNT(DISTINCT student_id) as total_students,
                AVG(gpa) as avg_gpa,
                MIN(gpa) as min_gpa,
                MAX(gpa) as max_gpa
            FROM academics
        """
        result = self.db.execute_query(query)
        if result:
            row = result[0]
            return {
                'total_students': row['total_students'],
                'avg_gpa': round(row['avg_gpa'], 2) if row['avg_gpa'] else 0,
                'min_gpa': row['min_gpa'],
                'max_gpa': row['max_gpa']
            }
        return {}
    
    def get_grade_distribution(self) -> List[Dict]:
        """Get distribution of grades"""
        query = """
            SELECT grade, COUNT(*) as count
            FROM academics
            WHERE grade IS NOT NULL
            GROUP BY grade
            ORDER BY grade
        """
        return self.db.execute_query(query)
    
    def get_top_performers(self, limit: int = 10) -> List[Dict]:
        """Get top academic performers"""
        query = f"""
            SELECT 
                s.student_id,
                s.name,
                s.email,
                AVG(a.gpa) as avg_gpa,
                COUNT(a.course_id) as courses
            FROM students s
            JOIN academics a ON s.student_id = a.student_id
            GROUP BY s.student_id, s.name, s.email
            ORDER BY avg_gpa DESC
            LIMIT {limit}
        """
        return self.db.execute_query(query)
    
    def get_event_statistics(self) -> Dict:
        """Get event statistics"""
        query = """
            SELECT 
                COUNT(*) as total_events,
                SUM(capacity) as total_capacity,
                AVG(capacity) as avg_capacity
            FROM events
        """
        result = self.db.execute_query(query)
        if result:
            row = result[0]
            return {
                'total_events': row['total_events'],
                'total_capacity': row['total_capacity'],
                'avg_capacity': round(row['avg_capacity'], 0) if row['avg_capacity'] else 0
            }
        return {}
    
    def get_events_by_location(self) -> List[Dict]:
        """Get events by location"""
        query = """
            SELECT location, COUNT(*) as count, SUM(capacity) as total_capacity
            FROM events
            WHERE location != 'Unknown'
            GROUP BY location
            ORDER BY count DESC
        """
        return self.db.execute_query(query)
    
    def get_transportation_status(self) -> List[Dict]:
        """Get transportation vehicle status"""
        query = """
            SELECT status, COUNT(*) as count, 
                   ROUND(AVG(capacity), 0) as avg_capacity
            FROM transportation
            GROUP BY status
            ORDER BY count DESC
        """
        return self.db.execute_query(query)
    
    def get_vehicle_by_type(self) -> List[Dict]:
        """Get vehicles by type"""
        query = """
            SELECT vehicle_type, COUNT(*) as count, 
                   SUM(capacity) as total_capacity
            FROM transportation
            WHERE vehicle_type != 'Unknown'
            GROUP BY vehicle_type
            ORDER BY count DESC
        """
        return self.db.execute_query(query)
    
    def get_facilities_status(self) -> List[Dict]:
        """Get facility status"""
        query = """
            SELECT status, COUNT(*) as count,
                   ROUND(AVG(capacity), 0) as avg_capacity
            FROM facilities
            GROUP BY status
            ORDER BY count DESC
        """
        return self.db.execute_query(query)
    
    def get_facilities_by_type(self) -> List[Dict]:
        """Get facilities by type"""
        query = """
            SELECT type, COUNT(*) as count,
                   SUM(capacity) as total_capacity,
                   GROUP_CONCAT(DISTINCT location) as locations
            FROM facilities
            WHERE type != 'Unknown'
            GROUP BY type
            ORDER BY count DESC
        """
        return self.db.execute_query(query)
    
    def get_data_quality_metrics(self) -> Dict:
        """Get data quality metrics"""
        metrics = {
            'students': {
                'total_records': 0,
                'null_emails': 0,
                'null_names': 0
            },
            'attendance': {
                'total_records': 0,
                'invalid_percentages': 0
            },
            'academics': {
                'total_records': 0,
                'invalid_gpa': 0
            }
        }
        
        try:
            # Students quality
            query = "SELECT COUNT(*) as count FROM students"
            result = self.db.execute_query(query)
            if result:
                metrics['students']['total_records'] = result[0]['count']
            
            query = "SELECT COUNT(*) as count FROM students WHERE email IS NULL or email = 'Unknown'"
            result = self.db.execute_query(query)
            if result:
                metrics['students']['null_emails'] = result[0]['count']
            
            # Attendance quality
            query = "SELECT COUNT(*) as count FROM attendance"
            result = self.db.execute_query(query)
            if result:
                metrics['attendance']['total_records'] = result[0]['count']
            
            query = "SELECT COUNT(*) as count FROM attendance WHERE attendance_percentage < 0 OR attendance_percentage > 100"
            result = self.db.execute_query(query)
            if result:
                metrics['attendance']['invalid_percentages'] = result[0]['count']
            
            # Academics quality
            query = "SELECT COUNT(*) as count FROM academics"
            result = self.db.execute_query(query)
            if result:
                metrics['academics']['total_records'] = result[0]['count']
            
            query = "SELECT COUNT(*) as count FROM academics WHERE gpa < 0 OR gpa > 4.0"
            result = self.db.execute_query(query)
            if result:
                metrics['academics']['invalid_gpa'] = result[0]['count']
        
        except Exception as e:
            logger.warning(f"Could not calculate all quality metrics: {e}")
        
        return metrics
    
    # ==================== ENHANCED ANALYTICS QUERIES ====================
    
    # STUDENTS ANALYTICS
    
    def get_students_by_year(self) -> List[Dict]:
        """Get student distribution by academic year (if available)"""
        query = """
            SELECT 
                CASE 
                    WHEN age BETWEEN 18 AND 19 THEN 'Freshman'
                    WHEN age BETWEEN 20 AND 21 THEN 'Sophomore'
                    WHEN age BETWEEN 22 AND 23 THEN 'Junior'
                    ELSE 'Senior'
                END as year,
                COUNT(*) as count
            FROM students
            GROUP BY year
            ORDER BY year
        """
        return self.db.execute_query(query)
    
    def get_students_by_gender(self) -> List[Dict]:
        """Get student distribution by gender"""
        query = """
            SELECT gender, COUNT(*) as count
            FROM students
            WHERE gender IS NOT NULL AND gender != 'Unknown'
            GROUP BY gender
            ORDER BY count DESC
        """
        return self.db.execute_query(query)
    
    def get_student_status_distribution(self) -> List[Dict]:
        """Get distribution of student status"""
        query = """
            SELECT status, COUNT(*) as count
            FROM students
            WHERE status IS NOT NULL
            GROUP BY status
            ORDER BY count DESC
        """
        return self.db.execute_query(query)
    
    def get_students_count_by_age_group(self) -> List[Dict]:
        """Get student count by age group"""
        query = """
            SELECT age_group, COUNT(*) as count
            FROM students
            WHERE age_group IS NOT NULL AND age_group != 'Unknown'
            GROUP BY age_group
            ORDER BY age_group
        """
        return self.db.execute_query(query)
    
    # ATTENDANCE ANALYTICS
    
    def get_attendance_by_department(self) -> List[Dict]:
        """Get average attendance by department"""
        query = """
            SELECT 
                s.department,
                COUNT(DISTINCT s.student_id) as students,
                ROUND(AVG(a.attendance_percentage), 2) as avg_attendance,
                COUNT(DISTINCT a.date) as total_sessions
            FROM students s
            LEFT JOIN attendance a ON s.student_id = a.student_id
            WHERE s.department IS NOT NULL AND s.department != 'Unknown'
            GROUP BY s.department
            ORDER BY avg_attendance DESC
        """
        return self.db.execute_query(query)
    
    def get_attendance_trends(self, limit: int = 30) -> List[Dict]:
        """Get attendance trends over time"""
        query = f"""
            SELECT 
                date,
                COUNT(DISTINCT student_id) as students_present,
                ROUND(AVG(attendance_percentage), 2) as avg_attendance,
                SUM(CASE WHEN status = 'Present' THEN 1 ELSE 0 END) as present_count,
                SUM(CASE WHEN status = 'Absent' THEN 1 ELSE 0 END) as absent_count
            FROM attendance
            GROUP BY date
            ORDER BY date DESC
            LIMIT {limit}
        """
        return self.db.execute_query(query)
    
    def get_chronic_absentees(self, threshold: float = 50.0) -> List[Dict]:
        """Get students with chronic absenteeism"""
        query = f"""
            SELECT 
                s.student_id,
                s.name,
                s.department,
                ROUND(AVG(a.attendance_percentage), 2) as avg_attendance,
                COUNT(DISTINCT a.date) as sessions_tracked
            FROM students s
            JOIN attendance a ON s.student_id = a.student_id
            GROUP BY s.student_id, s.name, s.department
            HAVING AVG(a.attendance_percentage) < {threshold}
            ORDER BY avg_attendance ASC
        """
        return self.db.execute_query(query)
    
    # ACADEMICS ANALYTICS
    
    def get_academics_by_department(self) -> List[Dict]:
        """Get average GPA and performance by department"""
        query = """
            SELECT 
                s.department,
                COUNT(DISTINCT s.student_id) as students,
                ROUND(AVG(a.gpa), 2) as avg_gpa,
                ROUND(MIN(a.gpa), 2) as min_gpa,
                ROUND(MAX(a.gpa), 2) as max_gpa,
                COUNT(a.course_id) as total_courses
            FROM students s
            LEFT JOIN academics a ON s.student_id = a.student_id
            WHERE s.department IS NOT NULL AND s.department != 'Unknown'
            GROUP BY s.department
            ORDER BY avg_gpa DESC
        """
        return self.db.execute_query(query)
    
    def get_struggling_students(self, gpa_threshold: float = 2.0) -> List[Dict]:
        """Get students below academic threshold (at-risk students)"""
        query = f"""
            SELECT 
                s.student_id,
                s.name,
                s.department,
                ROUND(AVG(a.gpa), 2) as avg_gpa,
                COUNT(a.course_id) as courses,
                COUNT(CASE WHEN a.grade IN ('D', 'F') THEN 1 END) as failing_grades
            FROM students s
            JOIN academics a ON s.student_id = a.student_id
            GROUP BY s.student_id, s.name, s.department
            HAVING AVG(a.gpa) < {gpa_threshold}
            ORDER BY avg_gpa ASC
        """
        return self.db.execute_query(query)
    
    def get_grade_statistics(self) -> Dict:
        """Get overall grade statistics"""
        query = """
            SELECT 
                COUNT(*) as total_grades,
                ROUND(AVG(gpa), 2) as avg_gpa,
                ROUND(MIN(gpa), 2) as min_gpa,
                ROUND(MAX(gpa), 2) as max_gpa,
                COUNT(CASE WHEN gpa >= 3.5 THEN 1 END) as excellent_count,
                COUNT(CASE WHEN gpa >= 3.0 AND gpa < 3.5 THEN 1 END) as good_count,
                COUNT(CASE WHEN gpa >= 2.0 AND gpa < 3.0 THEN 1 END) as average_count,
                COUNT(CASE WHEN gpa < 2.0 THEN 1 END) as below_average_count
            FROM academics
            WHERE gpa IS NOT NULL
        """
        result = self.db.execute_query(query)
        return dict(result[0]) if result else {}
    
    def get_top_courses(self, limit: int = 10) -> List[Dict]:
        """Get most popular courses by enrollment"""
        query = f"""
            SELECT 
                course_id,
                course_name,
                COUNT(DISTINCT student_id) as enrollment,
                ROUND(AVG(gpa), 2) as avg_gpa,
                COUNT(CASE WHEN grade IN ('A', 'A+') THEN 1 END) as excellent_students
            FROM academics
            WHERE course_name IS NOT NULL
            GROUP BY course_id, course_name
            ORDER BY enrollment DESC
            LIMIT {limit}
        """
        return self.db.execute_query(query)
    
    # EVENTS ANALYTICS
    
    def get_events_by_type(self) -> List[Dict]:
        """Get event distribution (if event type is tracked)"""
        query = """
            SELECT 
                COUNT(*) as total_events,
                SUM(capacity) as total_capacity
            FROM events
        """
        return self.db.execute_query(query)
    
    def get_events_by_location_detailed(self) -> List[Dict]:
        """Get events by location with capacity details"""
        query = """
            SELECT 
                location,
                COUNT(*) as event_count,
                SUM(capacity) as total_capacity,
                ROUND(AVG(capacity), 0) as avg_capacity,
                MIN(date) as earliest_date,
                MAX(date) as latest_date
            FROM events
            WHERE location IS NOT NULL AND location != 'Unknown'
            GROUP BY location
            ORDER BY event_count DESC
        """
        return self.db.execute_query(query)
    
    # TRANSPORTATION ANALYTICS
    
    def get_vehicle_utilization(self) -> List[Dict]:
        """Get vehicle utilization statistics"""
        query = """
            SELECT 
                vehicle_type,
                COUNT(*) as total_vehicles,
                SUM(capacity) as total_capacity,
                ROUND(AVG(capacity), 0) as avg_capacity,
                SUM(CASE WHEN status = 'Active' THEN 1 ELSE 0 END) as active_vehicles,
                SUM(CASE WHEN status = 'Maintenance' THEN 1 ELSE 0 END) as maintenance_vehicles
            FROM transportation
            WHERE vehicle_type IS NOT NULL
            GROUP BY vehicle_type
            ORDER BY total_vehicles DESC
        """
        return self.db.execute_query(query)
    
    def get_vehicle_health(self) -> Dict:
        """Get overall vehicle fleet health"""
        query = """
            SELECT 
                COUNT(*) as total_vehicles,
                SUM(capacity) as total_capacity,
                COUNT(CASE WHEN status = 'Active' THEN 1 END) as active_count,
                COUNT(CASE WHEN status = 'Maintenance' THEN 1 END) as maintenance_count,
                COUNT(CASE WHEN status = 'Inactive' THEN 1 END) as inactive_count,
                ROUND(100.0 * COUNT(CASE WHEN status = 'Active' THEN 1 END) / COUNT(*), 2) as health_percentage
            FROM transportation
        """
        result = self.db.execute_query(query)
        return dict(result[0]) if result else {}
    
    # FACILITIES ANALYTICS
    
    def get_facilities_overview(self) -> List[Dict]:
        """Get comprehensive facility statistics"""
        query = """
            SELECT 
                type,
                COUNT(*) as total_facilities,
                SUM(capacity) as total_capacity,
                ROUND(AVG(capacity), 0) as avg_capacity,
                COUNT(CASE WHEN status = 'Operational' THEN 1 END) as operational,
                COUNT(CASE WHEN status = 'Under Maintenance' THEN 1 END) as maintenance,
                COUNT(DISTINCT location) as unique_locations
            FROM facilities
            WHERE type IS NOT NULL AND type != 'Unknown'
            GROUP BY type
            ORDER BY total_facilities DESC
        """
        return self.db.execute_query(query)
    
    def get_facilities_maintenance_status(self) -> Dict:
        """Get facility maintenance status summary"""
        query = """
            SELECT 
                COUNT(*) as total_facilities,
                SUM(capacity) as total_capacity,
                COUNT(CASE WHEN status = 'Operational' THEN 1 END) as operational_count,
                COUNT(CASE WHEN status = 'Under Maintenance' THEN 1 END) as maintenance_count,
                ROUND(100.0 * COUNT(CASE WHEN status = 'Operational' THEN 1 END) / COUNT(*), 2) as operational_percentage
            FROM facilities
        """
        result = self.db.execute_query(query)
        return dict(result[0]) if result else {}
    
    def get_facilities_by_location(self) -> List[Dict]:
        """Get facilities aggregated by location"""
        query = """
            SELECT 
                location,
                COUNT(*) as facility_count,
                SUM(capacity) as total_capacity,
                GROUP_CONCAT(DISTINCT type) as types,
                COUNT(CASE WHEN status = 'Operational' THEN 1 END) as operational
            FROM facilities
            WHERE location IS NOT NULL AND location != 'Unknown'
            GROUP BY location
            ORDER BY facility_count DESC
        """
        return self.db.execute_query(query)
    
    # OVERALL DATA QUALITY METRICS
    
    def get_comprehensive_quality_metrics(self) -> Dict:
        """Get comprehensive data quality metrics for all domains"""
        metrics = {}
        
        try:
            domains = ['students', 'attendance', 'academics', 'events', 'transportation', 'facilities']
            
            for domain in domains:
                query = f"SELECT COUNT(*) as count FROM {domain}"
                result = self.db.execute_query(query)
                total_records = result[0]['count'] if result else 0
                
                metrics[domain] = {
                    'total_records': total_records,
                    'null_count': 0,
                    'invalid_count': 0,
                    'quality_score': 0
                }
                
                # Domain-specific quality checks
                if domain == 'students':
                    query = "SELECT COUNT(*) as count FROM students WHERE email IS NULL OR email = 'Unknown'"
                    result = self.db.execute_query(query)
                    metrics[domain]['null_count'] = result[0]['count'] if result else 0
                
                elif domain == 'attendance':
                    query = "SELECT COUNT(*) as count FROM attendance WHERE attendance_percentage < 0 OR attendance_percentage > 100"
                    result = self.db.execute_query(query)
                    metrics[domain]['invalid_count'] = result[0]['count'] if result else 0
                
                elif domain == 'academics':
                    query = "SELECT COUNT(*) as count FROM academics WHERE gpa < 0 OR gpa > 4.0"
                    result = self.db.execute_query(query)
                    metrics[domain]['invalid_count'] = result[0]['count'] if result else 0
                
                # Calculate quality score (0-100)
                if total_records > 0:
                    issues = metrics[domain]['null_count'] + metrics[domain]['invalid_count']
                    quality_score = max(0, 100 - (issues / total_records * 100))
                    metrics[domain]['quality_score'] = round(quality_score, 2)
        
        except Exception as e:
            logger.warning(f"Could not calculate comprehensive quality metrics: {e}")
        
        return metrics
    
    def print_analytics_report(self):
        """Print a comprehensive analytics report"""
        logger.info("\n" + "="*60)
        logger.info("ANALYTICS REPORT")
        logger.info("="*60)
        
        # Students
        logger.info(f"\nSTUDENTS:")
        logger.info(f"  Total Students: {self.get_total_students()}")
        
        depts = self.get_students_by_department()
        if depts:
            logger.info(f"  By Department:")
            for dept in depts:
                logger.info(f"    {dept['department']}: {dept['count']}")
        
        # Attendance
        logger.info(f"\nATTENDANCE:")
        att_stats = self.get_attendance_statistics()
        for key, value in att_stats.items():
            logger.info(f"  {key.replace('_', ' ').title()}: {value}")
        
        low_att = self.get_low_attendance_students()
        logger.info(f"  Students with <75% attendance: {len(low_att)}")
        
        # Academics
        logger.info(f"\nACADEMICS:")
        acad_stats = self.get_academic_statistics()
        for key, value in acad_stats.items():
            logger.info(f"  {key.replace('_', ' ').title()}: {value}")
        
        grades = self.get_grade_distribution()
        if grades:
            logger.info(f"  Grade Distribution:")
            for grade in grades:
                logger.info(f"    {grade['grade']}: {grade['count']}")
        
        # Events
        logger.info(f"\nEVENTS:")
        event_stats = self.get_event_statistics()
        for key, value in event_stats.items():
            logger.info(f"  {key.replace('_', ' ').title()}: {value}")
        
        # Transportation
        logger.info(f"\nTRANSPORTATION:")
        trans = self.get_transportation_status()
        if trans:
            logger.info(f"  By Status:")
            for t in trans:
                logger.info(f"    {t['status']}: {t['count']}")
        
        # Facilities
        logger.info(f"\nFACILITIES:")
        fac = self.get_facilities_status()
        if fac:
            logger.info(f"  By Status:")
            for f in fac:
                logger.info(f"    {f['status']}: {f['count']}")
        
        # Data Quality
        logger.info(f"\nDATA QUALITY METRICS:")
        dq = self.get_data_quality_metrics()
        for domain, metrics in dq.items():
            logger.info(f"  {domain.upper()}:")
            for metric, value in metrics.items():
                logger.info(f"    {metric}: {value}")
        
        logger.info("="*60 + "\n")


if __name__ == "__main__":
    queries = AnalyticsQueries()
    queries.print_analytics_report()
    queries.close()
