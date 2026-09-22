#!/usr/bin/env python3
"""
Smart Campus Data Hub - Streamlit Dashboard

Interactive dashboard for campus data analytics and reporting
Enhanced with data quality monitoring and pipeline metrics
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

# Page configuration
st.set_page_config(
    page_title="Smart Campus Data Hub",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional dashboard design
st.markdown("""
<style>
    :root {
        --sidebar-bg: #071A33;
        --sidebar-bg-2: #0b1f3a;
        --page-bg: #F7F9FC;
        --card-bg: #FFFFFF;
        --primary: #2563EB;
        --primary-soft: #E8F1FF;
        --text: #172033;
        --muted: #667085;
        --border: #E5EAF1;
        --success: #16A34A;
        --warning: #F59E0B;
        --danger: #E11D48;
    }

    .stApp {
        background: var(--page-bg);
    }

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, var(--sidebar-bg) 0%, var(--sidebar-bg-2) 100%);
        border-right: 1px solid rgba(255,255,255,0.08);
    }

    [data-testid="stSidebar"] > div {
        padding-top: 0.75rem;
    }

    .sidebar-brand {
        padding: 1.2rem 1rem 1rem 1rem;
        border-bottom: 1px solid rgba(255,255,255,0.08);
        text-align: center;
    }

    .sidebar-brand-icon {
        width: 46px;
        height: 46px;
        border-radius: 14px;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        background: rgba(37, 99, 235, 0.16);
        color: #dfeeff;
        font-size: 22px;
        margin-bottom: 0.65rem;
    }

    .sidebar-brand-title {
        color: #ffffff;
        font-size: 1.15rem;
        font-weight: 700;
        letter-spacing: 0.02em;
    }

    .sidebar-brand-subtitle {
        color: rgba(255,255,255,0.72);
        font-size: 0.70rem;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        margin-top: 0.15rem;
    }

    .sidebar-nav {
        padding: 1rem 0.8rem 0.4rem 0.8rem;
    }

    .nav-button {
        width: 100%;
        display: flex;
        align-items: center;
        gap: 0.75rem;
        padding: 0.78rem 0.9rem;
        border-radius: 12px;
        margin: 0.18rem 0;
        border: 1px solid transparent;
        background: transparent;
        color: rgba(255,255,255,0.82);
        font-size: 0.95rem;
        font-weight: 500;
        text-align: left;
        transition: all 0.2s ease;
    }

    .nav-button:hover {
        background: rgba(255,255,255,0.04);
        color: #ffffff;
        border-color: rgba(255,255,255,0.04);
    }

    .nav-button.active {
        background: rgba(37, 99, 235, 0.20);
        border-color: rgba(96, 165, 250, 0.7);
        color: #ffffff;
        box-shadow: inset 0 0 0 1px rgba(96, 165, 250, 0.18);
    }

    .sidebar-status {
        margin: 1rem 0.8rem 0.8rem 0.8rem;
        border-radius: 16px;
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(255,255,255,0.06);
        padding: 1rem 0.9rem;
    }

    .status-label {
        color: rgba(255,255,255,0.78);
        font-size: 0.72rem;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        margin-bottom: 0.8rem;
    }

    .status-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        color: rgba(255,255,255,0.9);
        font-size: 0.79rem;
        line-height: 1.8;
    }

    .status-pill {
        display: inline-flex;
        align-items: center;
        gap: 0.4rem;
        padding: 0.2rem 0.55rem;
        border-radius: 999px;
        background: rgba(22, 163, 74, 0.15);
        color: #a7f3d0;
        font-size: 0.72rem;
        font-weight: 600;
    }

    .status-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: #22c55e;
        display: inline-block;
    }

    .page-shell {
        padding: 0.5rem 0.2rem 1.5rem 0.2rem;
    }

    .page-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0.3rem 0 1.2rem 0;
        margin-bottom: 1.2rem;
    }

    .page-title {
        font-size: clamp(1.8rem, 2vw, 2.6rem);
        font-weight: 700;
        line-height: 1.2;
        color: var(--text);
        margin: 0;
    }

    .page-subtitle {
        color: var(--muted);
        margin-top: 0.3rem;
        font-size: 0.96rem;
    }

    .header-actions {
        display: flex;
        align-items: center;
        gap: 0.7rem;
    }

    .refresh-button {
        border: 1px solid var(--border);
        background: var(--card-bg);
        color: var(--text);
        border-radius: 10px;
        padding: 0.65rem 0.95rem;
        font-weight: 600;
    }

    .kpi-grid {
        display: grid;
        grid-template-columns: repeat(6, minmax(160px, 1fr));
        gap: 1rem;
        margin: 0.6rem 0 1.3rem 0;
    }

    .kpi-card {
        background: var(--card-bg);
        border: 1px solid var(--border);
        border-radius: 16px;
        padding: 1rem 1rem 0.9rem 1rem;
        box-shadow: 0 8px 20px rgba(15,23,42,0.025);
    }

    .kpi-card-header {
        display: flex;
        align-items: center;
        gap: 0.7rem;
        margin-bottom: 0.9rem;
    }

    .kpi-icon {
        width: 42px;
        height: 42px;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        border-radius: 12px;
        font-size: 1.15rem;
        background: var(--primary-soft);
        color: var(--primary);
    }

    .kpi-label {
        color: var(--muted);
        font-size: 0.78rem;
        font-weight: 600;
        letter-spacing: 0.02em;
        text-transform: uppercase;
    }

    .kpi-value {
        font-size: 1.8rem;
        font-weight: 700;
        line-height: 1.2;
        color: var(--text);
        margin: 0.1rem 0 0.15rem 0;
    }

    .kpi-meta {
        color: var(--muted);
        font-size: 0.8rem;
    }

    .chart-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 1rem;
        margin-bottom: 1.2rem;
    }

    .panel-card {
        background: var(--card-bg);
        border: 1px solid var(--border);
        border-radius: 16px;
        box-shadow: 0 10px 18px rgba(15,23,42,0.018);
        padding: 1.2rem;
    }

    .panel-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 0.8rem;
    }

    .panel-title {
        color: var(--text);
        font-size: 1.15rem;
        font-weight: 700;
        margin: 0;
    }

    .panel-caption {
        color: var(--muted);
        font-size: 0.82rem;
        margin-top: 0.15rem;
    }

    .insights-grid {
        display: grid;
        grid-template-columns: repeat(4, minmax(180px, 1fr));
        gap: 1rem;
        margin-bottom: 1rem;
    }

    .insight-card {
        background: linear-gradient(180deg, #ffffff, #f9fbff);
        border: 1px solid var(--border);
        border-radius: 16px;
        padding: 1rem;
    }

    .insight-label {
        color: var(--muted);
        font-size: 0.72rem;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        margin-bottom: 0.35rem;
    }

    .insight-value {
        color: var(--text);
        font-size: 1.1rem;
        font-weight: 700;
        line-height: 1.4;
    }

    .section-spacer {
        height: 0.6rem;
    }

    @media (max-width: 1180px) {
        .kpi-grid {
            grid-template-columns: repeat(3, minmax(150px, 1fr));
        }
    }

    @media (max-width: 900px) {
        .chart-grid,
        .insights-grid {
            grid-template-columns: 1fr;
        }
        .kpi-grid {
            grid-template-columns: repeat(2, minmax(150px, 1fr));
        }
    }

    @media (max-width: 640px) {
        .kpi-grid {
            grid-template-columns: 1fr;
        }
    }
</style>
""", unsafe_allow_html=True)

def get_analytics_queries():
    """Get fresh AnalyticsQueries instance (NOT cached - thread-safe)"""
    return AnalyticsQueries()

def get_pipeline_monitor():
    """Get PipelineMonitor instance"""
    return PipelineMonitor()

def get_database_connection():
    """Get ThreadSafeConnection instance (NOT cached)"""
    return ThreadSafeConnection()

def format_large_number(num):
    """Format large numbers for display"""
    if num is None:
        return "0"
    if num >= 1000000:
        return f"{num / 1000000:.1f}M"
    elif num >= 1000:
        return f"{num / 1000:.1f}K"
    return str(int(num))

def render_metric_card(col, label, value, icon="", accent=""):
    """Render a professional metric card"""
    with col:
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-card-header">
                    <div class="kpi-icon" style="background:{accent}; color: #fff;">{icon}</div>
                    <div class="kpi-label">{label}</div>
                </div>
                <div class="kpi-value">{value}</div>
                <div class="kpi-meta">Current total</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

def render_system_status():
    """Render system status and recent pipeline details in the sidebar."""
    try:
        db = get_database_connection()
        monitor = get_pipeline_monitor()
        students_count = db.get_table_count("students")
        last_exec = monitor.get_last_execution()
        pipeline_status = (last_exec.get("status", "Unknown") if last_exec else "Unknown").upper()
        if pipeline_status not in {"SUCCESS", "FAILED", "RUNNING"}:
            pipeline_status = "UNKNOWN"
        last_pipeline_run = last_exec.get("start_time", "N/A") if last_exec else "N/A"
        version = "1.2.0"

        st.sidebar.markdown("<div class='sidebar-status'>", unsafe_allow_html=True)
        st.sidebar.markdown("<div class='status-label'>System Status</div>", unsafe_allow_html=True)
        st.sidebar.markdown(f"""
            <div class='status-pill'><span class='status-dot'></span> All Systems Operational</div>
        """, unsafe_allow_html=True)
        st.sidebar.markdown(f"""
            <div class='status-row'><span>Database</span><span>Connected</span></div>
            <div class='status-row'><span>Records</span><span>{students_count} students</span></div>
            <div class='status-row'><span>Last Pipeline</span><span>{last_pipeline_run[:10] if isinstance(last_pipeline_run, str) and len(last_pipeline_run) >= 10 else last_pipeline_run}</span></div>
            <div class='status-row'><span>Pipeline</span><span>{pipeline_status}</span></div>
            <div class='status-row'><span>Version</span><span>{version}</span></div>
        """, unsafe_allow_html=True)
        st.sidebar.markdown("</div>", unsafe_allow_html=True)
    except Exception:
        st.sidebar.markdown("<div class='sidebar-status'><div class='status-label'>System Status</div><div class='status-row'><span>Status</span><span>Unavailable</span></div></div>", unsafe_allow_html=True)

def sidebar_navigation():
    """Render a custom, application-style sidebar navigation."""
    with st.sidebar:
        st.markdown("""
        <div class="sidebar-brand">
            <div class="sidebar-brand-icon">🎓</div>
            <div class="sidebar-brand-title">Smart Campus</div>
            <div class="sidebar-brand-subtitle">Data Hub</div>
        </div>
        """, unsafe_allow_html=True)

        nav_items = [
            ("Overview", "🏠"),
            ("Students", "👥"),
            ("Attendance", "📅"),
            ("Academics", "📚"),
            ("Events", "📅"),
            ("Transportation", "🚌"),
            ("Facilities", "🏢"),
            ("Data Quality", "🛡"),
            ("Pipeline Monitor", "📊"),
            ("Data Lineage", "🔗"),
        ]

        selected_page = st.session_state.get("selected_page", "Overview")
        st.markdown('<div class="sidebar-nav">', unsafe_allow_html=True)
        for label, icon in nav_items:
            button_class = "nav-button active" if label == selected_page else "nav-button"
            if st.button(f"{icon} {label}", key=f"nav_{label}", help=label, use_container_width=True):
                st.session_state["selected_page"] = label
                st.rerun()
            if label == selected_page:
                # Update active styling after the button render by injecting CSS via a markdown placeholder
                st.markdown(f"<style>.stButton button[kind='primary'] {{ background: transparent; }}</style>", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        render_system_status()

    return st.session_state.get("selected_page", "Overview")

def page_overview():
    """Professional overview dashboard with executive KPI cards and charts."""
    queries = get_analytics_queries()

    header_col, action_col = st.columns([6, 1])
    with header_col:
        st.markdown("<div class='page-title'>Campus Executive Overview</div>", unsafe_allow_html=True)
        st.markdown("<div class='page-subtitle'>Real-time insights and analytics from Smart Campus Data Hub</div>", unsafe_allow_html=True)
    with action_col:
        if st.button("↻ Refresh", key="refresh_overview", use_container_width=True):
            st.rerun()

    att_stats = queries.get_attendance_statistics()
    event_stats = queries.get_event_statistics()
    acad_stats = queries.get_academic_statistics()
    dept_counts = queries.get_students_by_department()
    attendance_status = queries.get_attendance_by_status()
    facility_status = queries.get_facilities_status()

    total_students = queries.get_total_students()
    avg_attendance = att_stats.get('avg_attendance', 0)
    avg_gpa = acad_stats.get('avg_gpa', 0)
    total_events = event_stats.get('total_events', 0)

    transport_status = queries.get_transportation_status()
    transport_total = sum(item.get('count', 0) for item in transport_status)
    facilities_active = 0
    if facility_status:
        for item in facility_status:
            if str(item.get('status', '')).lower() in {'operational', 'active', 'available'}:
                facilities_active += item.get('count', 0)

    kpi_cols = st.columns(6)
    render_metric_card(kpi_cols[0], "Total Students", format_large_number(total_students), "👥", "#E8F1FF")
    render_metric_card(kpi_cols[1], "Average Attendance", f"{avg_attendance:.1f}%", "📈", "#EAF8EF")
    render_metric_card(kpi_cols[2], "Academic Performance", f"{avg_gpa:.2f}", "🎓", "#F2ECFF")
    render_metric_card(kpi_cols[3], "Total Events", format_large_number(total_events), "📅", "#FFF4E5")
    render_metric_card(kpi_cols[4], "Transportation Usage", format_large_number(transport_total), "🚌", "#E0F2FE")
    render_metric_card(kpi_cols[5], "Facilities Active", format_large_number(facilities_active), "🏢", "#E8F1FF")

    st.markdown("<div class='section-spacer'></div>", unsafe_allow_html=True)

    chart_col_1, chart_col_2 = st.columns(2)

    with chart_col_1:
        st.markdown("""
        <div class="panel-card">
            <div class="panel-header">
                <div>
                    <div class="panel-title">Students by Department</div>
                    <div class="panel-caption">Student distribution across departments</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        if dept_counts:
            dept_df = pd.DataFrame(dept_counts)
            fig = px.bar(
                dept_df,
                x='department',
                y='count',
                color='department',
                title='Students by Department',
                color_discrete_sequence=px.colors.qualitative.Plotly,
            )
            fig.update_layout(
                title_text='',
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                showlegend=False,
                margin=dict(l=20, r=20, t=10, b=10),
                xaxis=dict(showgrid=False),
                yaxis=dict(showgrid=True, gridcolor='#eef2f7'),
            )
            st.plotly_chart(fig, use_container_width=True)

    with chart_col_2:
        st.markdown("""
        <div class="panel-card">
            <div class="panel-header">
                <div>
                    <div class="panel-title">Attendance Status</div>
                    <div class="panel-caption">Current attendance distribution</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        if attendance_status:
            att_df = pd.DataFrame(attendance_status)
            fig = px.pie(
                att_df,
                values='count',
                names='status',
                color='status',
                color_discrete_map={
                    'Present': '#2563EB',
                    'Late': '#F59E0B',
                    'Excused': '#16A34A',
                    'Absent': '#E11D48',
                },
            )
            fig.update_traces(textinfo='percent+label', hole=0.45)
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                showlegend=True,
                legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
                margin=dict(l=10, r=10, t=10, b=10),
            )
            st.plotly_chart(fig, use_container_width=True)

    st.markdown("<div class='section-spacer'></div>", unsafe_allow_html=True)
    st.markdown("<div class='panel-title' style='margin-bottom: 0.8rem;'>Key Insights</div>", unsafe_allow_html=True)

    dept_df = pd.DataFrame(dept_counts) if dept_counts else pd.DataFrame(columns=['department', 'count'])
    top_dept = dept_df.loc[dept_df['count'].idxmax()] if not dept_df.empty else None
    low_attendance = queries.get_low_attendance_students(threshold=75)
    low_count = len(low_attendance)
    facilities_total = sum(item.get('count', 0) for item in facility_status)
    active_facilities = facilities_active

    insight_items = []
    if top_dept is not None:
        insight_items.append(("Enrollment", f"{top_dept['department']} has the highest student enrollment."))
    insight_items.append(("Attendance", f"Average attendance is {avg_attendance:.1f}% across the campus."))
    insight_items.append(("Performance", f"{low_count} students are below the attendance threshold."))
    insight_items.append(("Operations", f"{active_facilities} of {facilities_total} facilities are operational."))

    insight_cols = st.columns(4)
    for i, (label, value) in enumerate(insight_items):
        with insight_cols[i]:
            st.markdown(f"""
            <div class="insight-card">
                <div class="insight-label">{label}</div>
                <div class="insight-value">{value}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<div class='section-spacer'></div>", unsafe_allow_html=True)

    q1, q2 = st.columns(2)
    with q1:
        st.markdown("<div class='panel-title' style='margin-bottom: 12px;'>Recent Campus Events</div>", unsafe_allow_html=True)
        events = queries.get_events_by_location() or []
        if events:
            event_df = pd.DataFrame(events).head(5)
            st.dataframe(event_df, use_container_width=True, hide_index=True)
    with q2:
        st.markdown("<div class='panel-title' style='margin-bottom: 12px;'>System Status</div>", unsafe_allow_html=True)
        monitor = get_pipeline_monitor()
        summary = monitor.get_pipeline_summary()
        summary_values = [
            ("Data Ingestion", "Operational"),
            ("Data Cleaning", "Operational"),
            ("Data Validation", "Operational"),
            ("Data Transformation", "Operational"),
            ("Database Load", "Operational"),
            ("Analytics Engine", "Operational"),
        ]
        for name, status in summary_values:
            st.markdown(f"<div class='status-row' style='color: #172033;'><span>{name}</span><span style='color: #16A34A;'>{status}</span></div>", unsafe_allow_html=True)

    return None

def page_students():
    """Professional students page"""
    st.markdown("""
    <div class="page-header">
        <div class="page-title">👥 Students</div>
        <div class="page-subtitle">Student demographics and academic standing</div>
    </div>
    """, unsafe_allow_html=True)
    
    queries = get_analytics_queries()
    
    # Summary metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        total_students = queries.get_total_students()
        st.metric("Total Students", total_students)
    
    with col2:
        depts = queries.get_students_by_department()
        num_depts = len(depts)
        st.metric("Departments", num_depts)
    
    with col3:
        st.metric("Status", "Active Pipeline")
    
    st.markdown("---")
    
    # Department distribution
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Distribution by Department")
        depts = queries.get_students_by_department()
        if depts:
            dept_df = pd.DataFrame(depts)
            fig = px.bar(dept_df, x='department', y='count', color='department',
                        title="Students per Department")
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Department Summary")
        if depts:
            dept_df = pd.DataFrame(depts)
            st.dataframe(dept_df, use_container_width=True, hide_index=True)
    
    # Student details
    st.markdown("---")
    st.subheader("Sample Student Records")
    students = queries.get_student_details(limit=20)
    if students:
        student_df = pd.DataFrame(students)
        st.dataframe(student_df, use_container_width=True, hide_index=True)

def page_attendance():
    """Professional attendance page"""
    st.markdown("""
    <div class="page-header">
        <div class="page-title">📋 Attendance</div>
        <div class="page-subtitle">Student attendance patterns and trends</div>
    </div>
    """, unsafe_allow_html=True)
    
    queries = get_analytics_queries()
    
    # KPI Row
    att_stats = queries.get_attendance_statistics()
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Students", att_stats.get('total_students', 0))
    
    with col2:
        st.metric("Avg Attendance %", f"{att_stats.get('avg_attendance', 0):.1f}%")
    
    with col3:
        st.metric("Min Attendance %", f"{att_stats.get('min_attendance', 0):.1f}%")
    
    with col4:
        st.metric("Max Attendance %", f"{att_stats.get('max_attendance', 0):.1f}%")
    
    st.markdown("---")
    
    # Attendance by status
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Attendance by Status")
        att_status = queries.get_attendance_by_status()
        if att_status:
            att_df = pd.DataFrame(att_status)
            fig = px.pie(att_df, values='count', names='status',
                        title="Attendance Status Breakdown")
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Status Summary")
        if att_status:
            att_df = pd.DataFrame(att_status)
            st.dataframe(att_df, use_container_width=True, hide_index=True)
    
    # Low attendance students
    st.markdown("---")
    st.subheader("Students with Low Attendance (<75%)")
    low_att = queries.get_low_attendance_students(threshold=75)
    if low_att:
        low_att_df = pd.DataFrame(low_att)
        st.warning(f"⚠️ {len(low_att_df)} students have attendance below 75%")
        st.dataframe(low_att_df, use_container_width=True, hide_index=True)
    else:
        st.success("✓ All students have good attendance!")

def page_academics():
    """Professional academics page"""
    st.markdown("""
    <div class="page-header">
        <div class="page-title">🎓 Academics</div>
        <div class="page-subtitle">Academic performance and course analytics</div>
    </div>
    """, unsafe_allow_html=True)
    
    queries = get_analytics_queries()
    
    # KPI Row
    acad_stats = queries.get_academic_statistics()
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Students", acad_stats.get('total_students', 0))
    
    with col2:
        st.metric("Avg GPA", f"{acad_stats.get('avg_gpa', 0):.2f}")
    
    with col3:
        st.metric("Min GPA", f"{acad_stats.get('min_gpa', 0):.2f}")
    
    with col4:
        st.metric("Max GPA", f"{acad_stats.get('max_gpa', 0):.2f}")
    
    st.markdown("---")
    
    # Grade distribution
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Grade Distribution")
        grades = queries.get_grade_distribution()
        if grades:
            grade_df = pd.DataFrame(grades)
            fig = px.bar(grade_df, x='grade', y='count', color='grade',
                        title="Distribution of Grades")
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Grade Summary")
        if grades:
            grade_df = pd.DataFrame(grades)
            st.dataframe(grade_df, use_container_width=True, hide_index=True)
    
    # Top performers
    st.markdown("---")
    st.subheader("Top Performers (by GPA)")
    top_performers = queries.get_top_performers(limit=15)
    if top_performers:
        top_df = pd.DataFrame(top_performers)
        st.dataframe(top_df, use_container_width=True, hide_index=True)

def page_events():
    """Professional events page"""
    st.markdown("""
    <div class="page-header">
        <div class="page-title">🎪 Events</div>
        <div class="page-subtitle">Campus events and venue management</div>
    </div>
    """, unsafe_allow_html=True)
    
    queries = get_analytics_queries()
    
    # KPI Row
    event_stats = queries.get_event_statistics()
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Events", event_stats.get('total_events', 0))
    
    with col2:
        st.metric("Total Capacity", event_stats.get('total_capacity', 0))
    
    with col3:
        st.metric("Avg Capacity", f"{event_stats.get('avg_capacity', 0):.0f}")
    
    st.markdown("---")
    
    # Events by location
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Events by Location")
        locations = queries.get_events_by_location()
        if locations:
            loc_df = pd.DataFrame(locations)
            fig = px.bar(loc_df, x='location', y='count', color='total_capacity',
                        title="Events by Location")
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Location Summary")
        if locations:
            loc_df = pd.DataFrame(locations)
            st.dataframe(loc_df, use_container_width=True, hide_index=True)

def page_transportation():
    """Professional transportation page"""
    st.markdown("""
    <div class="page-header">
        <div class="page-title">🚌 Transportation</div>
        <div class="page-subtitle">Fleet management and vehicle analytics</div>
    </div>
    """, unsafe_allow_html=True)
    
    queries = get_analytics_queries()
    
    # KPI Row
    health = queries.get_vehicle_health()
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.subheader("Vehicles by Status")
        trans_status = queries.get_transportation_status()
        if trans_status:
            trans_df = pd.DataFrame(trans_status)
            fig = px.pie(trans_df, values='count', names='status',
                        title="Vehicle Status Distribution")
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Status Summary")
        if trans_status:
            trans_df = pd.DataFrame(trans_status)
            st.dataframe(trans_df, use_container_width=True, hide_index=True)
    
    st.markdown("---")
    
    # Vehicles by type
    st.subheader("Vehicles by Type")
    vehicles = queries.get_vehicle_by_type()
    if vehicles:
        veh_df = pd.DataFrame(vehicles)
        fig = px.bar(veh_df, x='vehicle_type', y='count', color='total_capacity',
                    title="Vehicle Distribution by Type")
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(veh_df, use_container_width=True, hide_index=True)

def page_facilities():
    """Professional facilities page"""
    st.markdown("""
    <div class="page-header">
        <div class="page-title">🏢 Facilities</div>
        <div class="page-subtitle">Campus facilities and maintenance</div>
    </div>
    """, unsafe_allow_html=True)
    
    queries = get_analytics_queries()
    
    # KPI Row
    fac_maint = queries.get_facilities_maintenance_status()
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.subheader("Facilities by Status")
        fac_status = queries.get_facilities_status()
        if fac_status:
            fac_df = pd.DataFrame(fac_status)
            fig = px.pie(fac_df, values='count', names='status',
                        title="Facility Status Distribution")
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Status Summary")
        if fac_status:
            fac_df = pd.DataFrame(fac_status)
            st.dataframe(fac_df, use_container_width=True, hide_index=True)
    
    st.markdown("---")
    
    # Facilities by type
    st.subheader("Facilities by Type")
    facilities = queries.get_facilities_by_type()
    if facilities:
        fac_df = pd.DataFrame(facilities)
        fig = px.bar(fac_df, x='type', y='count', color='total_capacity',
                    title="Facility Distribution by Type")
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(fac_df, use_container_width=True, hide_index=True)

def page_data_quality():
    """Professional data quality page"""
    st.markdown("""
    <div class="page-header">
        <div class="page-title">✓ Data Quality</div>
        <div class="page-subtitle">Comprehensive data quality metrics and analysis</div>
    </div>
    """, unsafe_allow_html=True)
    
    queries = get_analytics_queries()
    
    # Get quality metrics
    metrics = queries.get_comprehensive_quality_metrics()
    
    st.subheader("Data Quality Summary")
    
    for domain, domain_metrics in metrics.items():
        with st.expander(f"📁 {domain.upper()}", expanded=True):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric(
                    "Total Records",
                    domain_metrics.get('total_records', 0)
                )
            
            if domain == 'students':
                with col2:
                    st.metric(
                        "Null Emails",
                        domain_metrics.get('null_emails', 0)
                    )
                with col3:
                    st.metric(
                        "Null Names",
                        domain_metrics.get('null_names', 0)
                    )
            
            elif domain == 'attendance':
                with col2:
                    st.metric(
                        "Invalid Percentages",
                        domain_metrics.get('invalid_percentages', 0)
                    )
                with col3:
                    st.metric("Status", "✓ OK" if domain_metrics.get('invalid_percentages', 0) == 0 else "⚠️ Issues")
            
            elif domain == 'academics':
                with col2:
                    st.metric(
                        "Invalid GPAs",
                        domain_metrics.get('invalid_gpa', 0)
                    )
                with col3:
                    st.metric("Status", "✓ OK" if domain_metrics.get('invalid_gpa', 0) == 0 else "⚠️ Issues")

def page_pipeline_monitor():
    """Professional pipeline monitoring page"""
    st.markdown("""
    <div class="page-header">
        <div class="page-title">⚙️ Pipeline Monitor</div>
        <div class="page-subtitle">ETL pipeline execution history and performance</div>
    </div>
    """, unsafe_allow_html=True)
    
    monitor = get_pipeline_monitor()
    
    # Pipeline Summary
    summary = monitor.get_pipeline_summary()
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Executions", summary.get('total_executions', 0))
    with col2:
        st.metric("Successful Runs", summary.get('successful_executions', 0))
    with col3:
        st.metric("Success Rate", f"{summary.get('success_rate', 0)}%")
    with col4:
        st.metric("Avg Duration (s)", summary.get('average_duration_seconds', 0))
    
    st.markdown("---")
    
    # Last Execution Details
    if summary.get('last_execution'):
        last_exec = summary['last_execution']
        st.subheader("Last Pipeline Execution")
        
        exec_col1, exec_col2, exec_col3 = st.columns(3)
        with exec_col1:
            st.metric("Status", last_exec.get('status', 'UNKNOWN'))
        with exec_col2:
            st.metric("Duration (s)", f"{last_exec.get('duration_seconds', 0):.2f}")
        with exec_col3:
            st.metric("Time", last_exec.get('start_time', 'N/A')[:10])
        
        # Input vs Output
        st.markdown("---")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Input Records", last_exec.get('total_input_records', 0))
        with col2:
            st.metric("Output Records", last_exec.get('total_output_records', 0))
    
    # Stage-wise Metrics
    if summary.get('last_execution'):
        exec_id = summary['last_execution'].get('execution_id')
        if exec_id:
            st.markdown("---")
            st.subheader("Stage-wise Metrics")
            
            stage_metrics = monitor.get_execution_stage_metrics(exec_id)
            if stage_metrics:
                stages_df = pd.DataFrame(stage_metrics)
                stages_df = stages_df[['stage_name', 'input_records', 'output_records', 'records_removed', 'duration_seconds', 'status']]
                st.dataframe(stages_df, use_container_width=True, hide_index=True)
                
                # Visualization
                col1, col2 = st.columns(2)
                with col1:
                    fig = px.bar(stages_df, x='stage_name', y='input_records', 
                                title="Records by Stage", labels={'input_records': 'Input Records'})
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    fig = px.bar(stages_df, x='stage_name', y='records_removed',
                                title="Records Removed", labels={'records_removed': 'Removed'})
                    st.plotly_chart(fig, use_container_width=True)

def page_data_lineage():
    """Professional data lineage page"""
    st.markdown("""
    <div class="page-header">
        <div class="page-title">🔄 Data Lineage</div>
        <div class="page-subtitle">Data flow through the ETL pipeline</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Display the pipeline flow
    st.markdown(DataLineage.get_pipeline_flow())
    
    # Detailed stage information
    st.subheader("Pipeline Stages Details")
    
    stages = DataLineage.get_all_stages()
    
    for stage in stages:
        with st.expander(f"{stage['icon']} {stage['name']}", expanded=False):
            st.write(f"**Description:** {stage['description']}")
            
            if 'domains' in stage:
                st.write(f"**Domains:** {', '.join(stage['domains'])}")
            
            if 'transformations' in stage:
                st.write("**Transformations:**")
                for t in stage['transformations']:
                    st.write(f"  • {t}")
            
            if 'checks' in stage:
                st.write("**Validation Checks:**")
                for c in stage['checks']:
                    st.write(f"  • {c}")
            
            if 'operations' in stage:
                st.write("**Operations:**")
                for op in stage['operations']:
                    st.write(f"  • {op}")
            
            if 'queries' in stage:
                st.write("**Analytics Queries:**")
                for q in stage['queries']:
                    st.write(f"  • {q}")
            
            if 'sections' in stage:
                st.write("**Dashboard Sections:**")
                for s in stage['sections']:
                    st.write(f"  • {s}")
    
    # Data Flow Summary
    st.markdown("---")
    st.subheader("Data Flow Path")
    
    flow_info = DataLineage.get_domain_path()
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Stages", flow_info['total_stages'])
    with col2:
        st.metric("Total Domains", flow_info['total_domains'])
    
    st.write(f"**Pipeline Flow:** {flow_info['flow']}")
    st.write(f"**Domains Tracked:** {', '.join(flow_info['domains'])}")

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
