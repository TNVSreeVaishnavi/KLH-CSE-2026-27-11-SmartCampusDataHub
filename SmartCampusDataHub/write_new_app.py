#!/usr/bin/env python3
"""Script to write the new professional dashboard app"""

new_app_content = '''#!/usr/bin/env python3
"""
Smart Campus Data Hub - Professional Streamlit Dashboard

Interactive dashboard for campus data analytics and reporting with:
- Thread-safe SQLite database access
- Professional modern UI design
- Comprehensive data visualization
- Pipeline monitoring and data lineage
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from analytics.queries import AnalyticsQueries
from monitoring.pipeline_monitor import PipelineMonitor
from monitoring.data_lineage import DataLineage
from database.thread_safe_connection import ThreadSafeConnection

# ==================== PAGE CONFIGURATION ====================

st.set_page_config(
    page_title="Smart Campus Data Hub",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== PROFESSIONAL DESIGN SYSTEM ====================

# Custom CSS for professional modern design
st.markdown("""
<style>
    /* Root variables */
    :root {
        --primary-blue: #1e3a8a;
        --light-blue: #dbeafe;
        --sidebar-bg: #0f172a;
        --card-bg: #ffffff;
        --border-color: #e5e7eb;
        --text-primary: #1f2937;
        --text-secondary: #6b7280;
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background-color: #0f172a !important;
    }
    
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] {
        color: #ffffff !important;
    }
    
    /* Main content area */
    .main {
        background-color: #f9fafb;
    }
    
    /* Professional metric cards */
    .metric-card {
        background: linear-gradient(135deg, #ffffff 0%, #f3f4f6 100%);
        padding: 24px;
        border-radius: 12px;
        border: 1px solid #e5e7eb;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        margin: 8px 0;
        transition: all 0.3s ease;
    }
    
    .metric-card:hover {
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        border-color: #1e3a8a;
    }
    
    .metric-label {
        font-size: 14px;
        font-weight: 600;
        color: #6b7280;
        margin-bottom: 8px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .metric-value {
        font-size: 32px;
        font-weight: 700;
        color: #1e3a8a;
        margin: 8px 0;
    }
    
    .metric-subtext {
        font-size: 12px;
        color: #9ca3af;
    }
    
    /* Professional headers */
    .page-header {
        padding: 24px 0;
        border-bottom: 2px solid #e5e7eb;
        margin-bottom: 32px;
    }
    
    .page-title {
        font-size: 28px;
        font-weight: 700;
        color: #1f2937;
        margin-bottom: 8px;
    }
    
    .page-subtitle {
        font-size: 14px;
        color: #6b7280;
        font-weight: 500;
    }
    
    /* Cards and containers */
    .info-card {
        background: #ffffff;
        padding: 20px;
        border-radius: 10px;
        border-left: 4px solid #1e3a8a;
        margin: 12px 0;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
    }
    
    /* Status badges */
    .status-success {
        background-color: #dcfce7;
        color: #166534;
        padding: 4px 8px;
        border-radius: 4px;
        font-weight: 600;
        font-size: 12px;
    }
    
    .status-warning {
        background-color: #fef3c7;
        color: #92400e;
        padding: 4px 8px;
        border-radius: 4px;
        font-weight: 600;
        font-size: 12px;
    }
    
    .status-error {
        background-color: #fee2e2;
        color: #991b1b;
        padding: 4px 8px;
        border-radius: 4px;
        font-weight: 600;
        font-size: 12px;
    }
    
    /* Tables */
    .dataframe {
        border-collapse: collapse;
        width: 100%;
    }
    
    .dataframe th {
        background-color: #f3f4f6;
        padding: 12px;
        text-align: left;
        font-weight: 600;
        color: #1f2937;
        border-bottom: 2px solid #e5e7eb;
    }
    
    .dataframe td {
        padding: 12px;
        border-bottom: 1px solid #f3f4f6;
    }
    
    /* System status card */
    .system-status-card {
        background: linear-gradient(135deg, #1e3a8a 0%, #1e40af 100%);
        padding: 16px;
        border-radius: 10px;
        color: white;
        margin-top: 24px;
        font-size: 12px;
    }
    
    .system-status-item {
        display: flex;
        justify-content: space-between;
        padding: 8px 0;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .system-status-label {
        font-weight: 600;
    }
    
    .system-status-value {
        color: #dbeafe;
    }
</style>
""", unsafe_allow_html=True)

# ==================== HELPER FUNCTIONS ====================

def get_analytics_queries():
    """Get AnalyticsQueries instance - NOT cached, new instance per call"""
    return AnalyticsQueries()

def get_pipeline_monitor():
    """Get PipelineMonitor instance"""
    return PipelineMonitor()

def get_database_connection():
    """Get ThreadSafeConnection instance - NOT cached"""
    return ThreadSafeConnection()

def format_large_number(num):
    """Format large numbers for display"""
    if num >= 1000000:
        return f"{num / 1000000:.1f}M"
    elif num >= 1000:
        return f"{num / 1000:.1f}K"
    return str(int(num))

def render_metric_card(col, label, value, icon="", subtitle="", color="blue"):
    """Render a professional metric card"""
    with col:
        st.markdown(f"""
        <div class="metric-card">
            <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                <div>
                    <div class="metric-label">{icon} {label}</div>
                    <div class="metric-value">{value}</div>
                    {f'<div class="metric-subtext">{subtitle}</div>' if subtitle else ''}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

def render_system_status():
    """Render system status card in sidebar"""
    st.sidebar.markdown("---")
    
    try:
        db = get_database_connection()
        monitor = get_pipeline_monitor()
        
        # Get system info
        students_count = db.get_table_count("students")
        db_connected = students_count > 0
        
        # Get last execution
        last_exec = monitor.get_last_execution()
        last_run_time = last_exec.get("end_time", "Never") if last_exec else "Never"
        pipeline_status = last_exec.get("status", "Unknown") if last_exec else "Unknown"
        
        st.sidebar.markdown("""
        <div class="system-status-card">
            <div style="font-size: 14px; font-weight: 700; margin-bottom: 12px;">System Status</div>
            <div class="system-status-item">
                <span class="system-status-label">Status:</span>
                <span class="system-status-value">Operational</span>
            </div>
            <div class="system-status-item">
                <span class="system-status-label">Database:</span>
                <span class="system-status-value">Connected</span>
            </div>
            <div class="system-status-item">
                <span class="system-status-label">Records:</span>
                <span class="system-status-value">""" + str(students_count) + """ students</span>
            </div>
            <div class="system-status-item">
                <span class="system-status-label">Pipeline:</span>
                <span class="system-status-value">""" + str(pipeline_status) + """</span>
            </div>
            <div class="system-status-item">
                <span class="system-status-label">Last Run:</span>
                <span class="system-status-value">""" + str(last_run_time)[:10] + """</span>
            </div>
            <div class="system-status-item" style="border-bottom: none;">
                <span class="system-status-label">Version:</span>
                <span class="system-status-value">1.2.0</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    except Exception as e:
        st.sidebar.warning(f"Could not load system status: {e}")

# ==================== SIDEBAR NAVIGATION ====================

def sidebar_navigation():
    """Render professional sidebar navigation"""
    with st.sidebar:
        # Logo and title
        st.markdown("""
        <div style="text-align: center; padding: 20px 0; border-bottom: 1px solid rgba(255,255,255,0.1);">
            <div style="font-size: 28px; margin-bottom: 8px;">🎓</div>
            <div style="font-size: 18px; font-weight: 700; color: white;">Smart Campus</div>
            <div style="font-size: 12px; color: #cbd5e1;">Data Hub</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("")
        
        # Navigation
        page = st.radio(
            "Navigation",
            [
                "Overview",
                "Students",
                "Attendance",
                "Academics",
                "Events",
                "Transportation",
                "Facilities",
                "Data Quality",
                "Pipeline Monitor",
                "Data Lineage"
            ],
            label_visibility="collapsed"
        )
        
        # System status
        render_system_status()
    
    return page

# ==================== PAGE: OVERVIEW ====================

def page_overview():
    """Professional overview dashboard"""
    # Header
    st.markdown("""
    <div class="page-header">
        <div class="page-title">📊 Overview Dashboard</div>
        <div class="page-subtitle">Real-time insights from Smart Campus Data Hub</div>
    </div>
    """, unsafe_allow_html=True)
    
    try:
        queries = get_analytics_queries()
        
        # KPI Section
        st.subheader("Key Metrics")
        col1, col2, col3, col4, col5, col6 = st.columns(6)
        
        with col1:
            total_students = queries.get_total_students()
            render_metric_card(col1, "Students", format_large_number(total_students), "👥")
        
        with col2:
            att_stats = queries.get_attendance_statistics()
            avg_att = att_stats.get('avg_attendance', 0)
            render_metric_card(col2, "Attendance", f"{avg_att:.1f}%", "📋")
        
        with col3:
            acad_stats = queries.get_academic_statistics()
            avg_gpa = acad_stats.get('avg_gpa', 0)
            render_metric_card(col3, "Avg GPA", f"{avg_gpa:.2f}", "🎓")
        
        with col4:
            event_stats = queries.get_event_statistics()
            total_events = event_stats.get('total_events', 0)
            render_metric_card(col4, "Events", format_large_number(total_events), "🎪")
        
        with col5:
            trans_stats = queries.get_vehicle_health()
            vehicle_count = trans_stats.get('total_vehicles', 0)
            render_metric_card(col5, "Vehicles", format_large_number(vehicle_count), "🚌")
        
        with col6:
            fac_stats = queries.get_facilities_maintenance_status()
            fac_count = fac_stats.get('total_facilities', 0)
            render_metric_card(col6, "Facilities", format_large_number(fac_count), "🏢")
        
        st.markdown("---")
        
        # Analytics Section
        st.subheader("Data Analytics")
        col1, col2 = st.columns(2)
        
        # Students by Department
        with col1:
            st.markdown("<div style='padding: 16px; background: white; border-radius: 10px; border: 1px solid #e5e7eb;'>", unsafe_allow_html=True)
            st.markdown("**Students by Department**")
            depts = queries.get_students_by_department()
            if depts:
                dept_df = pd.DataFrame(depts)
                fig = px.pie(dept_df, values='count', names='department',
                           title="Distribution", hole=0.4)
                fig.update_traces(textposition='inside', textinfo='percent+label')
                st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
            st.markdown("</div>", unsafe_allow_html=True)
        
        # Attendance Trend
        with col2:
            st.markdown("<div style='padding: 16px; background: white; border-radius: 10px; border: 1px solid #e5e7eb;'>", unsafe_allow_html=True)
            st.markdown("**Attendance by Department**")
            att_by_dept = queries.get_attendance_by_department()
            if att_by_dept:
                att_df = pd.DataFrame(att_by_dept)
                fig = px.bar(att_df, x='department', y='avg_attendance',
                           title="Average Attendance %", color='avg_attendance',
                           color_continuous_scale='Blues')
                st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
            st.markdown("</div>", unsafe_allow_html=True)
        
        # Bottom analytics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("<div style='padding: 16px; background: white; border-radius: 10px; border: 1px solid #e5e7eb;'>", unsafe_allow_html=True)
            st.markdown("**Recent Events**")
            events = queries.get_events_by_location_detailed()
            if events:
                events_df = pd.DataFrame(events)
                st.dataframe(events_df[['location', 'event_count', 'total_capacity']], 
                            use_container_width=True, hide_index=True)
            else:
                st.info("No events data available")
            st.markdown("</div>", unsafe_allow_html=True)
        
        with col2:
            st.markdown("<div style='padding: 16px; background: white; border-radius: 10px; border: 1px solid #e5e7eb;'>", unsafe_allow_html=True)
            st.markdown("**Top Students**")
            top_students = queries.get_top_performers(limit=5)
            if top_students:
                top_df = pd.DataFrame(top_students)
                st.dataframe(top_df[['name', 'avg_gpa', 'courses']], 
                            use_container_width=True, hide_index=True)
            else:
                st.info("No academic data available")
            st.markdown("</div>", unsafe_allow_html=True)
        
        with col3:
            st.markdown("<div style='padding: 16px; background: white; border-radius: 10px; border: 1px solid #e5e7eb;'>", unsafe_allow_html=True)
            st.markdown("**Transportation**")
            vehicles = queries.get_vehicle_utilization()
            if vehicles:
                vehicles_df = pd.DataFrame(vehicles)
                st.dataframe(vehicles_df[['vehicle_type', 'total_vehicles', 'active_vehicles']], 
                            use_container_width=True, hide_index=True)
            else:
                st.info("No vehicle data available")
            st.markdown("</div>", unsafe_allow_html=True)
    
    except Exception as e:
        st.error(f"Error loading overview: {str(e)}")

# ==================== PAGE: STUDENTS ====================

def page_students():
    """Professional students page"""
    st.markdown("""
    <div class="page-header">
        <div class="page-title">👥 Students</div>
        <div class="page-subtitle">Student demographics and academic standing</div>
    </div>
    """, unsafe_allow_html=True)
    
    try:
        queries = get_analytics_queries()
        
        # KPI Row
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            total = queries.get_total_students()
            render_metric_card(col1, "Total", format_large_number(total), "👥")
        with col2:
            depts = queries.get_students_by_department()
            render_metric_card(col2, "Departments", len(depts), "🏛️")
        with col3:
            status_dist = queries.get_student_status_distribution()
            active = sum(1 for s in status_dist if s.get('status', '').lower() == 'active')
            render_metric_card(col3, "Active", active, "✓")
        with col4:
            st.markdown("")
            st.markdown("")
            st.markdown("")
        
        st.markdown("---")
        
        # Analytics
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("<div style='padding: 16px; background: white; border-radius: 10px; border: 1px solid #e5e7eb;'>", unsafe_allow_html=True)
            st.markdown("**Distribution by Department**")
            depts = queries.get_students_by_department()
            if depts:
                dept_df = pd.DataFrame(depts)
                fig = px.bar(dept_df, x='department', y='count', color='count',
                           color_continuous_scale='Blues')
                st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
            st.markdown("</div>", unsafe_allow_html=True)
        
        with col2:
            st.markdown("<div style='padding: 16px; background: white; border-radius: 10px; border: 1px solid #e5e7eb;'>", unsafe_allow_html=True)
            st.markdown("**Student Status**")
            status_dist = queries.get_student_status_distribution()
            if status_dist:
                status_df = pd.DataFrame(status_dist)
                fig = px.pie(status_df, values='count', names='status', hole=0.4)
                st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
            st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("---")
        st.subheader("Student Records")
        students = queries.get_student_details(limit=50)
        if students:
            student_df = pd.DataFrame(students)
            st.dataframe(student_df, use_container_width=True, hide_index=True)
        else:
            st.info("No student records available")
    
    except Exception as e:
        st.error(f"Error loading students page: {str(e)}")

# ==================== PAGE: ATTENDANCE ====================

def page_attendance():
    """Professional attendance page"""
    st.markdown("""
    <div class="page-header">
        <div class="page-title">📋 Attendance</div>
        <div class="page-subtitle">Student attendance patterns and trends</div>
    </div>
    """, unsafe_allow_html=True)
    
    try:
        queries = get_analytics_queries()
        
        # KPI Row
        att_stats = queries.get_attendance_statistics()
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            render_metric_card(col1, "Avg Attendance", 
                             f"{att_stats.get('avg_attendance', 0):.1f}%", "📊")
        with col2:
            render_metric_card(col2, "Min", 
                             f"{att_stats.get('min_attendance', 0):.1f}%", "📉")
        with col3:
            render_metric_card(col3, "Max", 
                             f"{att_stats.get('max_attendance', 0):.1f}%", "📈")
        with col4:
            low_att = queries.get_low_attendance_students(75)
            render_metric_card(col4, "At Risk", len(low_att), "⚠️")
        
        st.markdown("---")
        
        # Analytics
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("<div style='padding: 16px; background: white; border-radius: 10px; border: 1px solid #e5e7eb;'>", unsafe_allow_html=True)
            st.markdown("**Attendance by Department**")
            att_dept = queries.get_attendance_by_department()
            if att_dept:
                att_df = pd.DataFrame(att_dept)
                fig = px.bar(att_df, x='department', y='avg_attendance',
                           color='avg_attendance', color_continuous_scale='Greens')
                st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
            st.markdown("</div>", unsafe_allow_html=True)
        
        with col2:
            st.markdown("<div style='padding: 16px; background: white; border-radius: 10px; border: 1px solid #e5e7eb;'>", unsafe_allow_html=True)
            st.markdown("**Status Breakdown**")
            att_status = queries.get_attendance_by_status()
            if att_status:
                status_df = pd.DataFrame(att_status)
                fig = px.pie(status_df, values='count', names='status', hole=0.4)
                st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
            st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("---")
        st.subheader("Low Attendance Alert")
        low_att = queries.get_low_attendance_students(75)
        if low_att:
            low_df = pd.DataFrame(low_att)
            st.warning(f"⚠️ {len(low_df)} students have attendance below 75%")
            st.dataframe(low_df, use_container_width=True, hide_index=True)
        else:
            st.success("✓ All students have good attendance!")
    
    except Exception as e:
        st.error(f"Error loading attendance page: {str(e)}")

# ==================== PAGE: ACADEMICS ====================

def page_academics():
    """Professional academics page"""
    st.markdown("""
    <div class="page-header">
        <div class="page-title">🎓 Academics</div>
        <div class="page-subtitle">Academic performance and course analytics</div>
    </div>
    """, unsafe_allow_html=True)
    
    try:
        queries = get_analytics_queries()
        
        # KPI Row
        acad_stats = queries.get_academic_statistics()
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            render_metric_card(col1, "Avg GPA", 
                             f"{acad_stats.get('avg_gpa', 0):.2f}", "📊")
        with col2:
            render_metric_card(col2, "Min GPA", 
                             f"{acad_stats.get('min_gpa', 0):.2f}", "📉")
        with col3:
            render_metric_card(col3, "Max GPA", 
                             f"{acad_stats.get('max_gpa', 0):.2f}", "📈")
        with col4:
            struggling = queries.get_struggling_students(2.0)
            render_metric_card(col4, "At Risk", len(struggling), "⚠️")
        
        st.markdown("---")
        
        # Analytics
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("<div style='padding: 16px; background: white; border-radius: 10px; border: 1px solid #e5e7eb;'>", unsafe_allow_html=True)
            st.markdown("**GPA by Department**")
            acad_dept = queries.get_academics_by_department()
            if acad_dept:
                acad_df = pd.DataFrame(acad_dept)
                fig = px.bar(acad_df, x='department', y='avg_gpa',
                           color='avg_gpa', color_continuous_scale='Blues')
                st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
            st.markdown("</div>", unsafe_allow_html=True)
        
        with col2:
            st.markdown("<div style='padding: 16px; background: white; border-radius: 10px; border: 1px solid #e5e7eb;'>", unsafe_allow_html=True)
            st.markdown("**Grade Distribution**")
            grades = queries.get_grade_distribution()
            if grades:
                grade_df = pd.DataFrame(grades)
                fig = px.pie(grade_df, values='count', names='grade')
                st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
            st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Top Performers")
            top = queries.get_top_performers(10)
            if top:
                top_df = pd.DataFrame(top)
                st.dataframe(top_df, use_container_width=True, hide_index=True)
            else:
                st.info("No academic data available")
        
        with col2:
            st.subheader("At-Risk Students")
            struggling = queries.get_struggling_students(2.0)
            if struggling:
                struggle_df = pd.DataFrame(struggling)
                st.dataframe(struggle_df, use_container_width=True, hide_index=True)
            else:
                st.success("No at-risk students detected!")
    
    except Exception as e:
        st.error(f"Error loading academics page: {str(e)}")

# ==================== PAGE: EVENTS ====================

def page_events():
    """Professional events page"""
    st.markdown("""
    <div class="page-header">
        <div class="page-title">🎪 Events</div>
        <div class="page-subtitle">Campus events and venue management</div>
    </div>
    """, unsafe_allow_html=True)
    
    try:
        queries = get_analytics_queries()
        
        # KPI Row
        event_stats = queries.get_event_statistics()
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            render_metric_card(col1, "Total Events", 
                             format_large_number(event_stats.get('total_events', 0)), "🎪")
        with col2:
            render_metric_card(col2, "Capacity", 
                             format_large_number(event_stats.get('total_capacity', 0)), "👥")
        with col3:
            render_metric_card(col3, "Avg Size", 
                             format_large_number(event_stats.get('avg_capacity', 0)), "📊")
        with col4:
            st.markdown("")
            st.markdown("")
            st.markdown("")
        
        st.markdown("---")
        
        st.subheader("Events by Location")
        events_loc = queries.get_events_by_location_detailed()
        if events_loc:
            events_df = pd.DataFrame(events_loc)
            fig = px.bar(events_df, x='location', y='event_count',
                       color='event_count', color_continuous_scale='Purples')
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
            
            st.markdown("---")
            st.subheader("Detailed Events")
            st.dataframe(events_df, use_container_width=True, hide_index=True)
        else:
            st.info("No events data available")
    
    except Exception as e:
        st.error(f"Error loading events page: {str(e)}")

# ==================== PAGE: TRANSPORTATION ====================

def page_transportation():
    """Professional transportation page"""
    st.markdown("""
    <div class="page-header">
        <div class="page-title">🚌 Transportation</div>
        <div class="page-subtitle">Fleet management and vehicle analytics</div>
    </div>
    """, unsafe_allow_html=True)
    
    try:
        queries = get_analytics_queries()
        
        # KPI Row
        health = queries.get_vehicle_health()
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            render_metric_card(col1, "Total Vehicles", 
                             format_large_number(health.get('total_vehicles', 0)), "🚌")
        with col2:
            render_metric_card(col2, "Active", 
                             format_large_number(health.get('active_count', 0)), "✓")
        with col3:
            render_metric_card(col3, "Fleet Health", 
                             f"{health.get('health_percentage', 0):.1f}%", "📊")
        with col4:
            st.markdown("")
            st.markdown("")
            st.markdown("")
        
        st.markdown("---")
        
        st.subheader("Vehicles by Type")
        vehicles = queries.get_vehicle_utilization()
        if vehicles:
            vehicles_df = pd.DataFrame(vehicles)
            fig = px.bar(vehicles_df, x='vehicle_type', y='total_vehicles',
                       color='active_vehicles', color_continuous_scale='Greens')
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
            
            st.markdown("---")
            st.subheader("Utilization Details")
            st.dataframe(vehicles_df, use_container_width=True, hide_index=True)
        else:
            st.info("No vehicle data available")
    
    except Exception as e:
        st.error(f"Error loading transportation page: {str(e)}")

# ==================== PAGE: FACILITIES ====================

def page_facilities():
    """Professional facilities page"""
    st.markdown("""
    <div class="page-header">
        <div class="page-title">🏢 Facilities</div>
        <div class="page-subtitle">Campus facilities and maintenance</div>
    </div>
    """, unsafe_allow_html=True)
    
    try:
        queries = get_analytics_queries()
        
        # KPI Row
        fac_maint = queries.get_facilities_maintenance_status()
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            render_metric_card(col1, "Total Facilities", 
                             format_large_number(fac_maint.get('total_facilities', 0)), "🏢")
        with col2:
            render_metric_card(col2, "Operational", 
                             format_large_number(fac_maint.get('operational_count', 0)), "✓")
        with col3:
            render_metric_card(col3, "Uptime", 
                             f"{fac_maint.get('operational_percentage', 0):.1f}%", "📊")
        with col4:
            st.markdown("")
            st.markdown("")
            st.markdown("")
        
        st.markdown("---")
        
        st.subheader("Facilities by Type")
        facilities = queries.get_facilities_overview()
        if facilities:
            facilities_df = pd.DataFrame(facilities)
            fig = px.bar(facilities_df, x='type', y='total_facilities',
                       color='operational', color_continuous_scale='Teal')
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
            
            st.markdown("---")
            st.subheader("By Location")
            fac_loc = queries.get_facilities_by_location()
            if fac_loc:
                loc_df = pd.DataFrame(fac_loc)
                st.dataframe(loc_df, use_container_width=True, hide_index=True)
        else:
            st.info("No facilities data available")
    
    except Exception as e:
        st.error(f"Error loading facilities page: {str(e)}")

# ==================== PAGE: DATA QUALITY ====================

def page_data_quality():
    """Professional data quality page"""
    st.markdown("""
    <div class="page-header">
        <div class="page-title">✓ Data Quality</div>
        <div class="page-subtitle">Comprehensive data quality metrics and analysis</div>
    </div>
    """, unsafe_allow_html=True)
    
    try:
        queries = get_analytics_queries()
        
        # Get quality metrics
        metrics = queries.get_comprehensive_quality_metrics()
        
        st.subheader("Domain Quality Scores")
        col1, col2, col3, col4, col5, col6 = st.columns(6)
        
        columns = [col1, col2, col3, col4, col5, col6]
        domains = ['students', 'attendance', 'academics', 'events', 'transportation', 'facilities']
        icons = ['👥', '📋', '🎓', '🎪', '🚌', '🏢']
        
        for i, (domain, icon) in enumerate(zip(domains, icons)):
            if domain in metrics:
                quality = metrics[domain].get('quality_score', 0)
                render_metric_card(columns[i], domain.title(), 
                                 f"{quality:.1f}%", icon)
        
        st.markdown("---")
        
        # Quality charts
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("<div style='padding: 16px; background: white; border-radius: 10px; border: 1px solid #e5e7eb;'>", unsafe_allow_html=True)
            st.markdown("**Quality Scores by Domain**")
            quality_data = []
            for domain in domains:
                if domain in metrics:
                    quality_data.append({
                        'domain': domain.title(),
                        'score': metrics[domain].get('quality_score', 0)
                    })
            if quality_data:
                quality_df = pd.DataFrame(quality_data)
                fig = px.bar(quality_df, x='domain', y='score',
                           color='score', color_continuous_scale='Greens',
                           range_y=[0, 100])
                st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
            st.markdown("</div>", unsafe_allow_html=True)
        
        with col2:
            st.markdown("<div style='padding: 16px; background: white; border-radius: 10px; border: 1px solid #e5e7eb;'>", unsafe_allow_html=True)
            st.markdown("**Record Counts**")
            record_data = []
            for domain in domains:
                if domain in metrics:
                    record_data.append({
                        'domain': domain.title(),
                        'records': metrics[domain].get('total_records', 0)
                    })
            if record_data:
                record_df = pd.DataFrame(record_data)
                fig = px.bar(record_df, x='domain', y='records',
                           color='records', color_continuous_scale='Blues')
                st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
            st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("---")
        st.subheader("Detailed Metrics")
        
        for domain in domains:
            if domain in metrics:
                with st.expander(f"{domain.upper()} - {metrics[domain].get('quality_score', 0):.1f}% Quality"):
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Total Records", metrics[domain].get('total_records', 0))
                    with col2:
                        st.metric("Null Values", metrics[domain].get('null_count', 0))
                    with col3:
                        st.metric("Invalid Records", metrics[domain].get('invalid_count', 0))
                    with col4:
                        st.metric("Quality Score", f"{metrics[domain].get('quality_score', 0):.1f}%")
    
    except Exception as e:
        st.error(f"Error loading data quality page: {str(e)}")

# ==================== PAGE: PIPELINE MONITOR ====================

def page_pipeline_monitor():
    """Professional pipeline monitoring page"""
    st.markdown("""
    <div class="page-header">
        <div class="page-title">⚙️ Pipeline Monitor</div>
        <div class="page-subtitle">ETL pipeline execution history and performance</div>
    </div>
    """, unsafe_allow_html=True)
    
    try:
        monitor = get_pipeline_monitor()
        
        # Last execution
        last_exec = monitor.get_last_execution()
        if last_exec:
            col1, col2, col3, col4, col5, col6 = st.columns(6)
            
            with col1:
                render_metric_card(col1, "Status", last_exec.get('status', 'Unknown'), "✓")
            with col2:
                duration = last_exec.get('duration', 0)
                render_metric_card(col2, "Duration", f"{duration:.2f}s", "⏱️")
            with col3:
                render_metric_card(col3, "Input", 
                                 format_large_number(last_exec.get('input_records', 0)), "📥")
            with col4:
                render_metric_card(col4, "Output", 
                                 format_large_number(last_exec.get('output_records', 0)), "📤")
            with col5:
                removed = last_exec.get('input_records', 0) - last_exec.get('output_records', 0)
                render_metric_card(col5, "Removed", format_large_number(removed), "🗑️")
            with col6:
                st.markdown("")
                st.markdown("")
                st.markdown("")
            
            st.markdown("---")
            st.subheader("Stage Performance")
            
            # Get stage metrics
            exec_id = last_exec.get('execution_id')
            if exec_id:
                stage_metrics = monitor.get_execution_stage_metrics(exec_id)
                if stage_metrics:
                    stages_df = pd.DataFrame(stage_metrics)
                    
                    # Visualization
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        fig = px.bar(stages_df, x='stage_name', y=['input_records', 'output_records'],
                                   title="Input vs Output by Stage",
                                   barmode='group')
                        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
                    
                    with col2:
                        fig = px.bar(stages_df, x='stage_name', y='duration_seconds',
                                   title="Duration by Stage", color='duration_seconds',
                                   color_continuous_scale='Reds')
                        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
                    
                    st.markdown("---")
                    st.subheader("Detailed Stage Metrics")
                    st.dataframe(stages_df, use_container_width=True, hide_index=True)
        
        else:
            st.info("No pipeline executions recorded yet")
    
    except Exception as e:
        st.error(f"Error loading pipeline monitor: {str(e)}")

# ==================== PAGE: DATA LINEAGE ====================

def page_data_lineage():
    """Professional data lineage page"""
    st.markdown("""
    <div class="page-header">
        <div class="page-title">🔄 Data Lineage</div>
        <div class="page-subtitle">Data flow through the ETL pipeline</div>
    </div>
    """, unsafe_allow_html=True)
    
    try:
        lineage = DataLineage()
        
        # Pipeline flow
        st.subheader("Pipeline Architecture")
        st.markdown(lineage.get_pipeline_flow())
        
        st.markdown("---")
        st.subheader("Stage Details")
        
        # All stages
        stages = lineage.get_all_stages()
        for stage in stages:
            with st.expander(f"🔹 {stage['name']} - {stage['description']}"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**Transformations:**")
                    for trans in stage.get('transformations', []):
                        st.markdown(f"• {trans}")
                    
                    st.markdown("**Validation Checks:**")
                    for check in stage.get('checks', []):
                        st.markdown(f"• {check}")
                
                with col2:
                    st.markdown("**Operations:**")
                    for op in stage.get('operations', []):
                        st.markdown(f"• {op}")
                    
                    st.markdown("**Dashboard Sections:**")
                    for section in stage.get('sections', []):
                        st.markdown(f"• {section}")
        
        st.markdown("---")
        st.subheader("Domain Tracking")
        
        # Domain flow
        domains = ['Students', 'Attendance', 'Academics', 'Events', 'Transportation', 'Facilities']
        for domain in domains:
            with st.expander(f"📊 {domain} Flow"):
                flow = lineage.get_domain_path(domain.lower())
                if flow:
                    st.markdown(flow.get('description', 'No description'))
                    st.markdown(f"**Transformations:** {flow.get('transformations', 'None')}")
    
    except Exception as e:
        st.error(f"Error loading data lineage: {str(e)}")

# ==================== MAIN APP ====================

def main():
    """Main application entry point"""
    # Sidebar navigation
    page = sidebar_navigation()
    
    # Page routing
    if page == "Overview":
        page_overview()
    elif page == "Students":
        page_students()
    elif page == "Attendance":
        page_attendance()
    elif page == "Academics":
        page_academics()
    elif page == "Events":
        page_events()
    elif page == "Transportation":
        page_transportation()
    elif page == "Facilities":
        page_facilities()
    elif page == "Data Quality":
        page_data_quality()
    elif page == "Pipeline Monitor":
        page_pipeline_monitor()
    elif page == "Data Lineage":
        page_data_lineage()

if __name__ == "__main__":
    main()
'''

# Write the new app.py
with open('dashboard/app.py', 'w') as f:
    f.write(new_app_content)

print("✓ Professional dashboard written successfully!")
print(f"File size: {len(new_app_content)} bytes")
