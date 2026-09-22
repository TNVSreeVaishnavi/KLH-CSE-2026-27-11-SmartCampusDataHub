#!/usr/bin/env python3
"""
Smart Campus Data Hub - Pipeline Monitoring

Tracks pipeline execution metrics, status, and performance.
Provides data lineage and processing statistics.
"""

import sqlite3
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from config.config import get_logger, DB_PATH

logger = get_logger(__name__)


class PipelineMonitor:
    """Monitors and tracks pipeline execution metrics"""
    
    def __init__(self):
        """Initialize pipeline monitor with metrics database"""
        self.metrics_file = Path(DB_PATH).parent / "pipeline_metrics.db"
        self.init_metrics_db()
    
    def init_metrics_db(self):
        """Initialize metrics database schema"""
        try:
            conn = sqlite3.connect(str(self.metrics_file))
            cursor = conn.cursor()
            
            # Pipeline execution log
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS pipeline_executions (
                    execution_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    start_time TIMESTAMP NOT NULL,
                    end_time TIMESTAMP,
                    status VARCHAR(50),
                    duration_seconds REAL,
                    total_input_records INTEGER,
                    total_output_records INTEGER,
                    error_message TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Stage-wise metrics
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS stage_metrics (
                    metric_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    execution_id INTEGER,
                    stage_name VARCHAR(100),
                    input_records INTEGER,
                    output_records INTEGER,
                    records_removed INTEGER,
                    duration_seconds REAL,
                    status VARCHAR(50),
                    error_message TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (execution_id) REFERENCES pipeline_executions(execution_id)
                )
            """)
            
            # Domain-wise statistics
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS domain_statistics (
                    stat_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    execution_id INTEGER,
                    domain VARCHAR(100),
                    raw_records INTEGER,
                    cleaned_records INTEGER,
                    validated_records INTEGER,
                    duplicates_removed INTEGER,
                    nulls_handled INTEGER,
                    invalid_records INTEGER,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (execution_id) REFERENCES pipeline_executions(execution_id)
                )
            """)
            
            conn.commit()
            conn.close()
            logger.info(f"Metrics database initialized: {self.metrics_file}")
        except Exception as e:
            logger.error(f"Failed to initialize metrics database: {str(e)}")
    
    def start_execution(self) -> int:
        """
        Record pipeline execution start.
        
        Returns:
            execution_id for this run
        """
        try:
            conn = sqlite3.connect(str(self.metrics_file))
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            start_time = datetime.now().isoformat()
            cursor.execute(
                "INSERT INTO pipeline_executions (start_time, status) VALUES (?, ?)",
                (start_time, "RUNNING")
            )
            conn.commit()
            execution_id = cursor.lastrowid
            conn.close()
            
            logger.info(f"Pipeline execution started: ID={execution_id}")
            return execution_id
        except Exception as e:
            logger.error(f"Failed to start execution: {str(e)}")
            return -1
    
    def record_stage_metrics(
        self, 
        execution_id: int,
        stage_name: str,
        input_records: int,
        output_records: int,
        records_removed: int,
        duration_seconds: float,
        status: str = "SUCCESS",
        error_message: Optional[str] = None
    ):
        """Record metrics for a pipeline stage"""
        try:
            conn = sqlite3.connect(str(self.metrics_file))
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO stage_metrics 
                (execution_id, stage_name, input_records, output_records, 
                 records_removed, duration_seconds, status, error_message)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (execution_id, stage_name, input_records, output_records,
                  records_removed, duration_seconds, status, error_message))
            
            conn.commit()
            conn.close()
            
            logger.debug(f"Stage {stage_name}: input={input_records}, output={output_records}, removed={records_removed}")
        except Exception as e:
            logger.error(f"Failed to record stage metrics: {str(e)}")
    
    def record_domain_statistics(
        self,
        execution_id: int,
        domain: str,
        raw_records: int,
        cleaned_records: int,
        validated_records: int,
        duplicates_removed: int,
        nulls_handled: int,
        invalid_records: int
    ):
        """Record statistics for a specific domain"""
        try:
            conn = sqlite3.connect(str(self.metrics_file))
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO domain_statistics
                (execution_id, domain, raw_records, cleaned_records, validated_records,
                 duplicates_removed, nulls_handled, invalid_records)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (execution_id, domain, raw_records, cleaned_records, validated_records,
                  duplicates_removed, nulls_handled, invalid_records))
            
            conn.commit()
            conn.close()
            
            logger.debug(f"Domain {domain}: raw={raw_records}, cleaned={cleaned_records}, validated={validated_records}")
        except Exception as e:
            logger.error(f"Failed to record domain statistics: {str(e)}")
    
    def end_execution(
        self,
        execution_id: int,
        status: str = "SUCCESS",
        total_input_records: int = 0,
        total_output_records: int = 0,
        error_message: Optional[str] = None
    ):
        """Record pipeline execution completion"""
        try:
            conn = sqlite3.connect(str(self.metrics_file))
            cursor = conn.cursor()
            
            end_time = datetime.now().isoformat()
            
            # Get start time to calculate duration
            cursor.execute("SELECT start_time FROM pipeline_executions WHERE execution_id = ?", (execution_id,))
            result = cursor.fetchone()
            
            if result:
                start_dt = datetime.fromisoformat(result[0])
                end_dt = datetime.fromisoformat(end_time)
                duration = (end_dt - start_dt).total_seconds()
                
                cursor.execute("""
                    UPDATE pipeline_executions
                    SET end_time = ?, status = ?, duration_seconds = ?,
                        total_input_records = ?, total_output_records = ?, error_message = ?
                    WHERE execution_id = ?
                """, (end_time, status, duration, total_input_records, total_output_records,
                      error_message, execution_id))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Pipeline execution completed: ID={execution_id}, status={status}")
        except Exception as e:
            logger.error(f"Failed to end execution: {str(e)}")
    
    def get_last_execution(self) -> Optional[Dict]:
        """Get metrics from the most recent pipeline execution"""
        try:
            conn = sqlite3.connect(str(self.metrics_file))
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM pipeline_executions
                ORDER BY start_time DESC
                LIMIT 1
            """)
            
            result = cursor.fetchone()
            conn.close()
            
            return dict(result) if result else None
        except Exception as e:
            logger.error(f"Failed to get last execution: {str(e)}")
            return None
    
    def get_execution_stage_metrics(self, execution_id: int) -> List[Dict]:
        """Get stage-wise metrics for an execution"""
        try:
            conn = sqlite3.connect(str(self.metrics_file))
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM stage_metrics
                WHERE execution_id = ?
                ORDER BY metric_id ASC
            """, (execution_id,))
            
            results = cursor.fetchall()
            conn.close()
            
            return [dict(row) for row in results]
        except Exception as e:
            logger.error(f"Failed to get stage metrics: {str(e)}")
            return []
    
    def get_execution_domain_statistics(self, execution_id: int) -> List[Dict]:
        """Get domain-wise statistics for an execution"""
        try:
            conn = sqlite3.connect(str(self.metrics_file))
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM domain_statistics
                WHERE execution_id = ?
                ORDER BY stat_id ASC
            """, (execution_id,))
            
            results = cursor.fetchall()
            conn.close()
            
            return [dict(row) for row in results]
        except Exception as e:
            logger.error(f"Failed to get domain statistics: {str(e)}")
            return []
    
    def get_pipeline_summary(self) -> Dict:
        """Get overall pipeline summary statistics"""
        try:
            conn = sqlite3.connect(str(self.metrics_file))
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Last execution
            cursor.execute("""
                SELECT * FROM pipeline_executions
                ORDER BY start_time DESC
                LIMIT 1
            """)
            last_exec = cursor.fetchone()
            
            # Success rate
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_executions,
                    SUM(CASE WHEN status = 'SUCCESS' THEN 1 ELSE 0 END) as successful_executions,
                    AVG(duration_seconds) as avg_duration
                FROM pipeline_executions
            """)
            stats = cursor.fetchone()
            
            conn.close()
            
            success_rate = 0
            if stats['total_executions'] > 0:
                success_rate = (stats['successful_executions'] / stats['total_executions']) * 100
            
            return {
                'last_execution': dict(last_exec) if last_exec else None,
                'total_executions': stats['total_executions'],
                'successful_executions': stats['successful_executions'],
                'success_rate': round(success_rate, 2),
                'average_duration_seconds': round(stats['avg_duration'], 2) if stats['avg_duration'] else 0
            }
        except Exception as e:
            logger.error(f"Failed to get pipeline summary: {str(e)}")
            return {}
