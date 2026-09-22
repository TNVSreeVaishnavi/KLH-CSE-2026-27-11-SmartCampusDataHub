import sqlite3
import logging
import os
from pathlib import Path
from typing import Optional, Tuple

import pandas as pd

from config.config import (
    DB_TYPE, 
    DB_PATH, 
    DB_HOST, 
    DB_PORT, 
    DB_USER, 
    DB_PASSWORD, 
    DB_NAME,
    get_logger
)

logger = get_logger(__name__)

class DatabaseConnection:
    """Manages database connections"""
    
    def __init__(self):
        self.connection = None
        self.db_type = DB_TYPE
    
    def connect(self) -> sqlite3.Connection:
        """
        Establish database connection
        
        Returns:
            Database connection object
        """
        try:
            if self.db_type == "sqlite":
                db_path = Path(DB_PATH)
                db_path.parent.mkdir(parents=True, exist_ok=True)
                
                self.connection = sqlite3.connect(str(db_path))
                self.connection.row_factory = sqlite3.Row  # Return rows as dictionaries
                logger.info(f"Connected to SQLite database: {DB_PATH}")
            
            else:
                raise NotImplementedError(f"Database type '{self.db_type}' not yet implemented")
            
            return self.connection
        
        except Exception as e:
            logger.error(f"Failed to connect to database: {str(e)}")
            raise
    
    def disconnect(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            logger.info("Database connection closed")
    
    def execute_query(self, query: str, params: Tuple = None) -> Optional[list]:
        """
        Execute a SELECT query
        
        Args:
            query: SQL query string
            params: Query parameters (tuple)
            
        Returns:
            List of result rows
        """
        try:
            cursor = self.connection.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            return cursor.fetchall()
        except Exception as e:
            logger.error(f"Query execution error: {str(e)}")
            raise
    
    def execute_update(self, query: str, params: Tuple = None) -> int:
        """
        Execute an INSERT/UPDATE/DELETE query
        
        Args:
            query: SQL query string
            params: Query parameters (tuple)
            
        Returns:
            Number of affected rows
        """
        try:
            cursor = self.connection.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            self.connection.commit()
            logger.debug(f"Executed update: {query[:50]}... (affected {cursor.rowcount} rows)")
            return cursor.rowcount
        except Exception as e:
            self.connection.rollback()
            logger.error(f"Update execution error: {str(e)}")
            raise
    
    def execute_many(self, query: str, params_list: list) -> int:
        """
        Execute INSERT/UPDATE/DELETE for multiple parameter sets
        
        Args:
            query: SQL query string
            params_list: List of parameter tuples
            
        Returns:
            Number of affected rows
        """
        try:
            cursor = self.connection.cursor()
            cursor.executemany(query, params_list)
            self.connection.commit()
            logger.debug(f"Executed batch: {len(params_list)} rows (affected {cursor.rowcount} total)")
            return cursor.rowcount
        except Exception as e:
            self.connection.rollback()
            logger.error(f"Batch execution error: {str(e)}")
            raise
    
    def init_schema(self, schema_file: Path) -> bool:
        """
        Initialize database schema from SQL file, including migration for
        legacy SQLite databases that already exist but are missing newer columns.
        
        Args:
            schema_file: Path to SQL schema file
            
        Returns:
            True if successful
        """
        try:
            if not schema_file.exists():
                logger.error(f"Schema file not found: {schema_file}")
                return False
            
            with open(schema_file, 'r') as f:
                schema_sql = f.read()
            
            cursor = self.connection.cursor()
            index_statements = []

            # Execute all table statements first, then migrate any legacy tables, and only
            # create indexes after the required columns exist. Older SQLite databases may
            # already contain tables without the newer columns, so index creation must wait.
            for statement in schema_sql.split(';'):
                statement = statement.strip()
                if not statement:
                    continue

                statement_upper = statement.upper()
                if statement_upper.startswith('CREATE INDEX') or statement_upper.startswith('CREATE UNIQUE INDEX'):
                    index_statements.append(statement)
                    continue

                try:
                    cursor.execute(statement)
                except sqlite3.OperationalError as exc:
                    msg = str(exc).lower()
                    if 'duplicate column name' in msg or 'duplicate' in msg or 'already exists' in msg:
                        logger.warning(f"Ignoring duplicate schema statement: {statement[:80]}... ({exc})")
                        continue
                    raise

            self._migrate_missing_columns(schema_sql)

            for statement in index_statements:
                try:
                    cursor.execute(statement)
                except sqlite3.OperationalError as exc:
                    msg = str(exc).lower()
                    if 'duplicate' in msg or 'already exists' in msg or 'no such column' in msg:
                        logger.warning(f"Skipping schema index statement: {statement[:80]}... ({exc})")
                        continue
                    raise

            self.connection.commit()
            logger.info(f"Database schema initialized from {schema_file}")
            return True
        
        except Exception as e:
            logger.error(f"Schema initialization error: {str(e)}")
            return False

    def _migrate_missing_columns(self, schema_sql: str):
        """Add any missing columns required by the current schema for existing tables."""
        for statement in schema_sql.split(';'):
            statement = statement.strip()
            if not statement or not statement.upper().startswith('CREATE TABLE'):
                continue

            body = self._extract_table_body(statement)
            if not body:
                continue

            table_name = self._extract_table_name(statement)
            if not table_name:
                continue

            expected_columns = {}
            for raw_part in self._split_top_level_parts(body):
                part = raw_part.strip()
                if not part:
                    continue
                upper_part = part.upper()
                if upper_part.startswith(('PRIMARY', 'FOREIGN', 'UNIQUE', 'CHECK', 'CONSTRAINT')):
                    continue

                cols = part.split(None, 1)
                if len(cols) < 2:
                    continue

                column_name = cols[0].strip('"`[]')
                definition = cols[1].strip()
                if column_name and definition:
                    expected_columns[column_name] = definition

            if not expected_columns:
                continue

            table_info = self.execute_query(f"PRAGMA table_info({table_name})")
            existing_columns = {row['name'] for row in table_info}

            for column_name, definition in expected_columns.items():
                if column_name in existing_columns:
                    continue

                alter_sql = f"ALTER TABLE {table_name} ADD COLUMN {column_name} {definition}"
                logger.info(f"Migrating {table_name} by adding missing column: {column_name}")
                self.execute_update(alter_sql)

    @staticmethod
    def _extract_table_name(statement: str) -> Optional[str]:
        """Extract the table name from a CREATE TABLE statement."""
        match = statement.upper().find('CREATE TABLE')
        if match == -1:
            return None

        remainder = statement[match + len('CREATE TABLE'):].lstrip()
        if remainder.upper().startswith('IF NOT EXISTS'):
            remainder = remainder[len('IF NOT EXISTS'):].lstrip()

        name = remainder.split('(')[0].strip().strip('"`[]')
        return name or None

    @staticmethod
    def _extract_table_body(statement: str) -> Optional[str]:
        """Return the body between the opening and closing parentheses of a CREATE TABLE."""
        start = statement.find('(')
        if start == -1:
            return None

        depth = 0
        for index in range(start, len(statement)):
            ch = statement[index]
            if ch == '(':
                depth += 1
            elif ch == ')':
                depth -= 1
                if depth == 0:
                    return statement[start + 1:index]
        return None

    @staticmethod
    def _split_top_level_parts(body: str):
        """Split the table body only on commas at the top level, not inside type definitions."""
        parts = []
        current = []
        depth = 0
        for ch in body:
            if ch == '(':
                depth += 1
            elif ch == ')':
                depth = max(0, depth - 1)

            if ch == ',' and depth == 0:
                part = ''.join(current).strip()
                if part:
                    parts.append(part)
                current = []
                continue

            current.append(ch)

        tail = ''.join(current).strip()
        if tail:
            parts.append(tail)
        return parts
    
    def table_exists(self, table_name: str) -> bool:
        """Check if a table exists"""
        try:
            if self.db_type == "sqlite":
                query = "SELECT name FROM sqlite_master WHERE type='table' AND name=?"
                result = self.execute_query(query, (table_name,))
                return len(result) > 0
        except Exception as e:
            logger.error(f"Error checking table existence: {str(e)}")
            return False
    
    def get_table_count(self, table_name: str) -> int:
        """Get row count for a table"""
        try:
            query = f"SELECT COUNT(*) as count FROM {table_name}"
            result = self.execute_query(query)
            return result[0]['count'] if result else 0
        except Exception as e:
            logger.error(f"Error getting table count: {str(e)}")
            return 0


class DatabaseManager:
    """High-level database management"""
    
    def __init__(self):
        self.db = DatabaseConnection()
        self.db.connect()
    
    def initialize(self, schema_file: Path) -> bool:
        """Initialize database with schema"""
        return self.db.init_schema(schema_file)
    
    def close(self):
        """Close database connection"""
        self.db.disconnect()
    
    def insert_dataframe(self, df, table_name: str, if_exists: str = 'append') -> Tuple[int, int]:
        """
        Insert a pandas DataFrame into database
        
        Args:
            df: Pandas DataFrame
            table_name: Target table name
            if_exists: 'append' (default) or 'replace'
            
        Returns:
            Tuple of (inserted_rows, failed_rows)
        """
        try:
            # Convert DataFrame to list of tuples for insertion.
            # SQLite does not support pandas Timestamp objects directly.
            df_for_insert = df.copy()
            for col in df_for_insert.columns:
                if pd.api.types.is_datetime64_any_dtype(df_for_insert[col]):
                    df_for_insert[col] = df_for_insert[col].dt.strftime('%Y-%m-%d %H:%M:%S')
                elif hasattr(df_for_insert[col].dtype, 'kind') and df_for_insert[col].dtype.kind == 'M':
                    df_for_insert[col] = df_for_insert[col].map(
                        lambda value: value.strftime('%Y-%m-%d %H:%M:%S') if pd.notna(value) else None
                    )

            columns = list(df_for_insert.columns)
            rows = [tuple(row) for row in df_for_insert.values]
            
            # Use OR REPLACE so reruns safely update existing rows instead of failing
            # when the database already contains the same natural key values.
            placeholders = ','.join(['?' for _ in columns])
            col_list = ','.join(columns)
            query = f"INSERT OR REPLACE INTO {table_name} ({col_list}) VALUES ({placeholders})"

            # Insert rows
            affected = self.db.execute_many(query, rows)
            
            logger.info(f"Inserted {affected} rows into {table_name}")
            return affected, 0
        
        except Exception as e:
            logger.error(f"Error inserting into {table_name}: {str(e)}")
            return 0, len(df)
    
    def get_table_stats(self, table_name: str) -> dict:
        """Get statistics for a table"""
        try:
            count = self.db.get_table_count(table_name)
            return {
                "table": table_name,
                "row_count": count,
                "exists": self.db.table_exists(table_name)
            }
        except Exception as e:
            logger.error(f"Error getting table stats: {str(e)}")
            return {}


if __name__ == "__main__":
    from pathlib import Path
    
    manager = DatabaseManager()
    schema_path = Path(__file__).parent / "schema.sql"
    
    if manager.initialize(schema_path):
        logger.info("Database initialized successfully")
        
        # Print table stats
        for table in ['students', 'attendance', 'academics', 'events', 'transportation', 'facilities']:
            stats = manager.get_table_stats(table)
            logger.info(f"Table {table}: {stats}")
    
    manager.close()
