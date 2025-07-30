from typing import Any, Dict, List, Optional, Tuple, Union
import mysql.connector  # type: ignore
from mysql.connector.cursor import MySQLCursorDict  # type: ignore
import logging
from ..config import DatabaseConfig
from .base import BaseAdapter

logger = logging.getLogger(__name__)

class MySQLAdapter(BaseAdapter):
    def connect(self) -> None:
        """Connect to the MySQL database."""
        try:
            self.connection = mysql.connector.connect(
                host=self.config.host,
                port=self.config.port,
                database=self.config.database,
                user=self.config.username,
                password=self.config.password,
                **self.config.additional_params
            )
        except mysql.connector.Error as e:
            logger.error(f"Error connecting to MySQL database: {str(e)}")
            raise

    def disconnect(self) -> None:
        """Close the MySQL connection."""
        if self.connection:
            self.connection.close()
            self.connection = None

    def execute_query(self, query: str, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Execute a query and return results."""
        if self.connection is None:
            raise RuntimeError("Database connection is not established. Call connect() first.")
        with self.connection.cursor(cursor_class=MySQLCursorDict) as cursor:
            cursor.execute(query, params or {})
            return cursor.fetchall()

    def insert_data(self, table: str, data: Union[Dict[str, Any], List[Dict[str, Any]]]) -> None:
        """Insert data into the specified table."""
        if self.connection is None:
            raise RuntimeError("Database connection is not established. Call connect() first.")
        if not data:
            return
        if isinstance(data, dict):
            data = [data]
        columns = list(data[0].keys())
        values = [tuple(row[col] for col in columns) for row in data]
        placeholders = ", ".join(["%s"] * len(columns))
        columns_str = ", ".join(columns)
        query = f"INSERT INTO {table} ({columns_str}) VALUES ({placeholders})"
        with self.connection.cursor() as cursor:
            cursor.executemany(query, values)
            self.connection.commit()

    def update_data(self, table: str, data: Union[Dict[str, Any], List[Dict[str, Any]]], key_columns: Union[str, List[str]]) -> None:
        """Update data in the specified table."""
        if self.connection is None:
            raise RuntimeError("Database connection is not established. Call connect() first.")
        if not data:
            return
        if isinstance(data, dict):
            data = [data]
        if isinstance(key_columns, str):
            key_columns = [key_columns]
        for row in data:
            set_clause = ", ".join(f"{k} = %s" for k in row.keys() if k not in key_columns)
            where_clause = " AND ".join(f"{k} = %s" for k in key_columns)
            values = [v for k, v in row.items() if k not in key_columns] + [row.get(k) for k in key_columns]
            query = f"UPDATE {table} SET {set_clause} WHERE {where_clause}"
            with self.connection.cursor() as cursor:
                cursor.execute(query, values)
                self.connection.commit()

    def delete_data(self, table: str, conditions: Union[str, Dict[str, Any]]) -> None:
        """Delete data from the specified table."""
        if self.connection is None:
            raise RuntimeError("Database connection is not established. Call connect() first.")
        if isinstance(conditions, str):
            query = f"DELETE FROM {table} WHERE {conditions}"
            with self.connection.cursor() as cursor:
                cursor.execute(query)
                self.connection.commit()
        else:
            where_clause = " AND ".join(f"{k} = %s" for k in conditions.keys())
            values = list(conditions.values())
            query = f"DELETE FROM {table} WHERE {where_clause}"
            with self.connection.cursor() as cursor:
                cursor.execute(query, values)
                self.connection.commit()

    def get_watermark(self, table_name: str, watermark_column: str) -> Optional[Tuple[str, str]]:
        """Get the watermark value and status for a table."""
        if self.connection is None:
            raise RuntimeError("Database connection is not established. Call connect() first.")
        if not table_name or not watermark_column:
            raise ValueError("Table name and watermark column must be specified for watermark retrieval.")
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("""
                    SELECT watermark_value, status
                    FROM sync_watermark
                    WHERE table_name = %s AND watermark_column = %s
                """, (table_name, watermark_column))
                result = cursor.fetchone()
                return result if result else None
        except mysql.connector.Error:
            return None

    def update_watermark(self, table_name: str, watermark_column: str, 
                        watermark_value: str, status: str = 'success', 
                        error_message: Optional[str] = None) -> None:
        """Update the watermark value for a table."""
        if self.connection is None:
            raise RuntimeError("Database connection is not established. Call connect() first.")
        if not table_name or not watermark_column:
            raise ValueError("Table name and watermark column must be specified for updating watermark.")
        with self.connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO sync_watermark 
                    (table_name, watermark_column, watermark_value, status, error_message)
                VALUES (%s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE 
                    watermark_value = VALUES(watermark_value),
                    status = VALUES(status),
                    error_message = VALUES(error_message),
                    last_sync_at = CURRENT_TIMESTAMP
            """, (table_name, watermark_column, watermark_value, status, error_message))
            self.connection.commit()

    def get_last_sync_timestamp(self) -> Optional[str]:
        """Get the last synchronization timestamp."""
        if not self.config.watermark or not self.config.table:
            return None
        result = self.get_watermark(
            self.config.table,
            self.config.watermark.column
        )
        return result[0] if result and result[1] == 'success' else None

    def update_last_sync_timestamp(self, timestamp: str) -> None:
        """Update the last synchronization timestamp."""
        if not self.config.watermark or not self.config.table:
            return
        self.update_watermark(
            self.config.table,
            self.config.watermark.column,
            timestamp
        ) 