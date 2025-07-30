from typing import Any, Dict, List, Optional, Tuple, Union
import psycopg2
from psycopg2.extras import RealDictCursor
import logging
from ..config import DatabaseConfig
from .base import BaseAdapter

logger = logging.getLogger(__name__)

class PostgreSQLAdapter(BaseAdapter):
    def connect(self) -> None:
        """Connect to the database."""
        try:
            self.connection = psycopg2.connect(
                host=self.config.host,
                port=self.config.port,
                database=self.config.database,
                user=self.config.username,
                password=self.config.password,
            )
        except psycopg2.Error as e:
            logger.error(f"Error connecting to database: {str(e)}")
            raise

    def disconnect(self) -> None:
        """Close the PostgreSQL connection."""
        if self.connection:
            self.connection.close()
            self.connection = None

    def execute_query(self, query: str, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Execute a query and return results."""
        if self.connection is None:
            raise RuntimeError("Database connection is not established. Call connect() first.")
        with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(query, params or {})
            return [dict(row) for row in cursor.fetchall()]

    def insert_data(self, table: str, data: Union[Dict[str, Any], List[Dict[str, Any]]]) -> None:
        """Insert data into the specified table."""
        if not data:
            return

        if isinstance(data, dict):
            data = [data]

        columns = list(data[0].keys())
        values = [tuple(row[col] for col in columns) for row in data]
        placeholders = ", ".join(["%s"] * len(columns))
        columns_str = ", ".join(columns)

        query = f"INSERT INTO {table} ({columns_str}) VALUES ({placeholders})"
        if self.connection is None:
            raise RuntimeError("Database connection is not established. Call connect() first.")
        with self.connection.cursor() as cursor:
            cursor.executemany(query, values)
            self.connection.commit()

    def update_data(self, table: str, data: Union[Dict[str, Any], List[Dict[str, Any]]], key_columns: Union[str, List[str]]) -> None:
        """Update data in the specified table."""
        if not data:
            return

        if isinstance(data, dict):
            data = [data]

        if isinstance(key_columns, str):
            key_columns = [key_columns]

        if self.connection is None:
            raise RuntimeError("Database connection is not established. Call connect() first.")
        with self.connection.cursor() as cursor:
            for row in data:
                set_clause = ", ".join(f"{k} = %s" for k in row.keys() if k not in key_columns)
                where_clause = " AND ".join(f"{k} = %s" for k in key_columns)
                values = [v for k, v in row.items() if k not in key_columns] + [row.get(k) for k in key_columns]
                query = f"UPDATE {table} SET {set_clause} WHERE {where_clause}"
                cursor.execute(query, values)
            self.connection.commit()

    def delete_data(self, table: str, conditions: Union[str, Dict[str, Any]]) -> None:
        """Delete data from the specified table."""
        if self.connection is None:
            raise RuntimeError("Database connection is not established. Call connect() first.")
        with self.connection.cursor() as cursor:
            if isinstance(conditions, str):
                query = f"DELETE FROM {table} WHERE {conditions}"
                cursor.execute(query)
            else:
                where_clause = " AND ".join(f"{k} = %s" for k in conditions.keys())
                values = list(conditions.values())
                query = f"DELETE FROM {table} WHERE {where_clause}"
                cursor.execute(query, values)
            self.connection.commit()

    def get_watermark(self, table: str, column: str) -> Optional[str]:
        """Get the watermark value for the specified table and column."""
        if not table or not column:
            raise ValueError("Table and column must be specified for watermark retrieval.")
        query = f"SELECT {column} FROM {table} ORDER BY {column} DESC LIMIT 1"
        result = self.execute_query(query)
        return result[0][column] if result else None

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
                ON CONFLICT (table_name, watermark_column)
                DO UPDATE SET 
                    watermark_value = EXCLUDED.watermark_value,
                    status = EXCLUDED.status,
                    error_message = EXCLUDED.error_message,
                    last_sync_at = CURRENT_TIMESTAMP
            """, (table_name, watermark_column, watermark_value, status, error_message))
            self.connection.commit()

    def get_last_sync_timestamp(self) -> Optional[str]:
        """Get the last synchronization timestamp from the sync_metadata table."""
        if not self.config.watermark or not self.config.table:
            return None
        result = self.get_watermark(
            self.config.table,
            self.config.watermark.column
        )
        return result

    def update_last_sync_timestamp(self, timestamp: str) -> None:
        """Update the last synchronization timestamp in the sync_metadata table."""
        if not self.config.watermark or not self.config.table:
            return
        self.update_watermark(
            self.config.table,
            self.config.watermark.column,
            timestamp
        ) 