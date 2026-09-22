"""
Thread-safe SQLite database connection handler for Streamlit.

This module provides thread-safe database access without relying on cached
persistent connections, which causes "SQLite objects created in a thread 
can only be used in that same thread" errors in Streamlit.
"""

import sqlite3
import logging
from pathlib import Path
from contextlib import contextmanager
from typing import Optional, List, Dict, Tuple

from config.config import DB_PATH, get_logger

logger = get_logger(__name__)


class ThreadSafeConnection:
    """
    Provides thread-safe SQLite database access.
    Creates a fresh connection for each operation and closes it immediately.
    """
    
    def __init__(self, db_path: str = DB_PATH):
        """
        Initialize with database path.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = str(db_path)
        # Ensure directory exists
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
    
    @contextmanager
    def get_connection(self):
        """
        Context manager that creates a fresh connection and closes it after use.
        
        Yields:
            SQLite connection object
        """
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            yield conn
        except Exception as e:
            logger.error(f"Database connection error: {str(e)}")
            raise
        finally:
            if conn:
                conn.close()
    
    def execute_query(self, query: str, params: Tuple = None) -> List[Dict]:
        """
        Execute a SELECT query with a fresh connection.
        
        Args:
            query: SQL query string
            params: Query parameters (tuple)
            
        Returns:
            List of result rows as dictionaries
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
                # Convert Row objects to dictionaries
                results = [dict(row) for row in cursor.fetchall()]
                return results
        except Exception as e:
            logger.error(f"Query execution error: {str(e)}")
            return []
    
    def execute_update(self, query: str, params: Tuple = None) -> int:
        """
        Execute an INSERT/UPDATE/DELETE query with a fresh connection.
        
        Args:
            query: SQL query string
            params: Query parameters (tuple)
            
        Returns:
            Number of affected rows
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
                conn.commit()
                return cursor.rowcount
        except Exception as e:
            logger.error(f"Update execution error: {str(e)}")
            return 0
    
    def execute_many(self, query: str, params_list: list) -> int:
        """
        Execute INSERT/UPDATE/DELETE for multiple parameter sets with a fresh connection.
        
        Args:
            query: SQL query string
            params_list: List of parameter tuples
            
        Returns:
            Number of affected rows
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.executemany(query, params_list)
                conn.commit()
                return cursor.rowcount
        except Exception as e:
            logger.error(f"Batch execution error: {str(e)}")
            return 0
    
    def table_exists(self, table_name: str) -> bool:
        """Check if a table exists."""
        try:
            query = "SELECT name FROM sqlite_master WHERE type='table' AND name=?"
            result = self.execute_query(query, (table_name,))
            return len(result) > 0
        except Exception as e:
            logger.error(f"Error checking table existence: {str(e)}")
            return False
    
    def get_table_count(self, table_name: str) -> int:
        """Get row count for a table."""
        try:
            query = f"SELECT COUNT(*) as count FROM {table_name}"
            result = self.execute_query(query)
            return result[0]['count'] if result else 0
        except Exception as e:
            logger.error(f"Error getting table count: {str(e)}")
            return 0
