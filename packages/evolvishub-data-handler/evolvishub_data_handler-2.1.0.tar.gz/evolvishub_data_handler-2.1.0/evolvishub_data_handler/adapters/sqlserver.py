from typing import Any, Dict, List, Optional, Tuple
import pymssql
from ..config import DatabaseConfig
from .base import BaseAdapter
import logging

logger = logging.getLogger(__name__)


class SQLServerAdapter(BaseAdapter):
    def connect(self) -> None:
        """Establish connection to SQL Server database."""
        self.connection = pymssql.connect(
            server=self.config.host,
            port=self.config.port,
            database=self.config.database,
            user=self.config.username,
            password=self.config.password,
            **self.config.additional_params
        )

    def disconnect(self) -> None:
        """Close the SQL Server connection."""
        if self.connection:
            self.connection.close()
            self.connection = None

    def execute_query(self, query: str, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Execute a query and return results."""
        if self.connection is None:
            raise RuntimeError("Database connection is not established. Call connect() first.")
        with self.connection.cursor(as_dict=True) as cursor:
            cursor.execute(query, params or {})
            return cursor.fetchall()

    def insert_data(self, table: str, data: List[Dict[str, Any]]) -> None:
        """Insert data into the specified table."""
        if self.connection is None:
            raise RuntimeError("Database connection is not established. Call connect() first.")
        if not data:
            return
        columns = list(data[0].keys())
        placeholders = ', '.join(['%s'] * len(columns))
        query = f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({placeholders})"
        values = [tuple(row[col] for col in columns) for row in data]
        with self.connection.cursor() as cursor:
            cursor.executemany(query, values)
            self.connection.commit()

    def update_data(self, table: str, data: List[Dict[str, Any]], key_columns: List[str]) -> None:
        """Update data in the specified table."""
        if self.connection is None:
            raise RuntimeError("Database connection is not established. Call connect() first.")
        if not data:
            return
        for row in data:
            set_clause = ", ".join(f"{k} = %s" for k in row.keys() if k not in key_columns)
            where_clause = " AND ".join(f"{k} = %s" for k in key_columns)
            set_values = [row[k] for k in row.keys() if k not in key_columns]
            where_values = [row[k] for k in key_columns]
            query = f"UPDATE {table} SET {set_clause} WHERE {where_clause}"
            with self.connection.cursor() as cursor:
                cursor.execute(query, set_values + where_values)
                self.connection.commit()

    def delete_data(self, table: str, conditions: Dict[str, Any]) -> None:
        """Delete data from the specified table."""
        if self.connection is None:
            raise RuntimeError("Database connection is not established. Call connect() first.")
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
        except pymssql.Error as e:
            logger.error(f"Error getting watermark: {str(e)}")
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
                MERGE sync_watermark AS target
                USING (SELECT %s AS table_name, %s AS watermark_column) AS source
                ON (target.table_name = source.table_name AND target.watermark_column = source.watermark_column)
                WHEN MATCHED THEN
                    UPDATE SET 
                        watermark_value = %s,
                        status = %s,
                        error_message = %s,
                        last_sync_at = GETDATE()
                WHEN NOT MATCHED THEN
                    INSERT (table_name, watermark_column, watermark_value, status, error_message)
                    VALUES (%s, %s, %s, %s, %s);
            """, (table_name, watermark_column, watermark_value, status, error_message,
                  table_name, watermark_column, watermark_value, status, error_message))
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