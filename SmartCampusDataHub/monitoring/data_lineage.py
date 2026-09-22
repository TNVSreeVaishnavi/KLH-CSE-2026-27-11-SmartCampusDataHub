#!/usr/bin/env python3
"""
Smart Campus Data Hub - Data Lineage Tracker

Visualizes and tracks data flow through the ETL pipeline stages.
"""

from typing import Dict, List
import logging

from config.config import get_logger

logger = get_logger(__name__)


class DataLineage:
    """Tracks and visualizes data lineage through pipeline stages"""
    
    # Define the pipeline stages and their sequence
    PIPELINE_STAGES = [
        {
            "id": 1,
            "name": "RAW DATA",
            "description": "Raw CSV files from external sources",
            "icon": "📥",
            "domains": ["students", "attendance", "academics", "events", "transportation", "facilities"]
        },
        {
            "id": 2,
            "name": "INGESTION",
            "description": "Load raw data into memory as DataFrames",
            "icon": "📂",
            "output": "Ingested DataFrames"
        },
        {
            "id": 3,
            "name": "CLEANING",
            "description": "Remove duplicates, handle nulls, standardize formats",
            "icon": "🧹",
            "transformations": [
                "Remove whitespace",
                "Handle missing values",
                "Standardize text and dates",
                "Remove duplicates",
                "Handle invalid values"
            ]
        },
        {
            "id": 4,
            "name": "VALIDATION",
            "description": "Verify data quality and business rules",
            "icon": "✓",
            "checks": [
                "Required columns",
                "Data types",
                "Null values",
                "Duplicates",
                "Business rules"
            ]
        },
        {
            "id": 5,
            "name": "TRANSFORMATION",
            "description": "Standardize and prepare for database",
            "icon": "⚙️",
            "operations": [
                "Standardize column names",
                "Convert data types",
                "Normalize categories",
                "Create derived fields",
                "Reorder columns"
            ]
        },
        {
            "id": 6,
            "name": "DATABASE LOAD",
            "description": "Insert transformed data into SQLite",
            "icon": "💾",
            "output": "SQLite tables"
        },
        {
            "id": 7,
            "name": "ANALYTICS",
            "description": "Generate insights and metrics",
            "icon": "📊",
            "queries": [
                "Department distribution",
                "Attendance statistics",
                "Academic performance",
                "Event summaries",
                "Transportation metrics",
                "Facility status"
            ]
        },
        {
            "id": 8,
            "name": "DASHBOARD",
            "description": "Present insights in interactive UI",
            "icon": "📈",
            "sections": [
                "Overview",
                "Students",
                "Attendance",
                "Academics",
                "Events",
                "Transportation",
                "Facilities",
                "Data Quality"
            ]
        }
    ]
    
    @staticmethod
    def get_pipeline_flow() -> str:
        """Get ASCII representation of pipeline flow"""
        return """
╔═══════════════════════════════════════════════════════════════════════════════╗
║                    DATA ENGINEERING PIPELINE FLOW                             ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║                                                                               ║
║   📥 RAW DATA                                                                 ║
║     ↓                                                                         ║
║   📂 INGESTION         → Load CSV files into DataFrames                       ║
║     ↓                                                                         ║
║   🧹 CLEANING          → Remove duplicates, handle nulls, standardize        ║
║     ↓                                                                         ║
║   ✓ VALIDATION         → Verify quality, check business rules                ║
║     ↓                                                                         ║
║   ⚙️  TRANSFORMATION    → Standardize columns, create derived fields          ║
║     ↓                                                                         ║
║   💾 DATABASE LOAD     → Insert into SQLite, create indices                   ║
║     ↓                                                                         ║
║   📊 ANALYTICS         → Generate KPIs and insights                          ║
║     ↓                                                                         ║
║   📈 DASHBOARD         → Interactive visualization and reporting             ║
║                                                                               ║
║ DOMAINS: students, attendance, academics, events, transportation, facilities  ║
║                                                                               ║
╚═══════════════════════════════════════════════════════════════════════════════╝
        """
    
    @staticmethod
    def get_stage_details(stage_id: int) -> Dict:
        """Get detailed information about a specific stage"""
        for stage in DataLineage.PIPELINE_STAGES:
            if stage["id"] == stage_id:
                return stage
        return {}
    
    @staticmethod
    def get_all_stages() -> List[Dict]:
        """Get all pipeline stages"""
        return DataLineage.PIPELINE_STAGES
    
    @staticmethod
    def get_domain_path() -> Dict[str, List[str]]:
        """Get the path that each domain takes through the pipeline"""
        domains = ["students", "attendance", "academics", "events", "transportation", "facilities"]
        
        return {
            "flow": " → ".join([stage["name"] for stage in DataLineage.PIPELINE_STAGES]),
            "domains": domains,
            "total_stages": len(DataLineage.PIPELINE_STAGES),
            "total_domains": len(domains)
        }
    
    @staticmethod
    def print_lineage_summary():
        """Print data lineage summary to console"""
        logger.info(DataLineage.get_pipeline_flow())
        logger.info("\nPIPELINE STAGES:")
        for stage in DataLineage.PIPELINE_STAGES:
            logger.info(f"  {stage['icon']} {stage['name']}: {stage['description']}")
