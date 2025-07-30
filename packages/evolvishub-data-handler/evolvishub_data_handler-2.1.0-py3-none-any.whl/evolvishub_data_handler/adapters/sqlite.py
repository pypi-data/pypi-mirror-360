from typing import Any, Dict, List, Optional, Tuple
import sqlite3  # type: ignore
from datetime import datetime, UTC
import logging
logger = logging.getLogger(__name__)
from ..config import DatabaseConfig, WatermarkConfig
from .base import BaseAdapter

def adapt_datetime(dt: datetime) -> str:
    """Convert datetime to ISO format string for SQLite storage."""
    return dt.isoformat()

def convert_datetime(val: bytes) -> datetime:
    """Convert ISO format string from SQLite to datetime."""
    return datetime.fromisoformat(val.decode())

# Register the adapters
sqlite3.register_adapter(datetime, adapt_datetime)
sqlite3.register_converter("datetime", convert_datetime)

class SQLiteAdapter(BaseAdapter):
    def __init__(self, config: DatabaseConfig):
        """Initialize SQLite adapter.

        Args:
            config: Database configuration
        """
        super().__init__(config)
        self.connection: Optional[sqlite3.Connection] = None
        self.cursor: Optional[sqlite3.Cursor] = None

    def connect(self) -> None:
        """Connect to the SQLite database and ensure watermark table exists."""
        try:
            self.connection = sqlite3.connect(
                self.config.file_path or self.config.database,
                **self.config.additional_params
            )
            self.connection.row_factory = sqlite3.Row
            
            # Create watermark table if it doesn't exist
            self._create_watermark_table()
            
            logger.info(f"Connected to SQLite database: {self.config.database}")
        except sqlite3.Error as e:
            logger.error(f"Error connecting to SQLite database: {str(e)}")
            raise

    def _create_watermark_table(self) -> None:
        """Create the watermark table if it doesn't exist."""
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sync_watermark (
                    table_name TEXT NOT NULL,
                    watermark_column TEXT NOT NULL,
                    watermark_value TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'success',
                    error_message TEXT,
                    last_sync_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (table_name, watermark_column)
                )
            """)
            self.connection.commit()
            cursor.close()
            logger.debug("Watermark table created or already exists")
        except sqlite3.Error as e:
            logger.error(f"Error creating watermark table: {str(e)}")
            raise

    def disconnect(self) -> None:
        """Close the SQLite connection."""
        if self.connection:
            try:
                self.connection.close()
                self.connection = None
                logger.info("Disconnected from SQLite database")
            except sqlite3.Error as e:
                logger.error(f"Error disconnecting from SQLite database: {str(e)}")
                raise

    def execute_query(self, query: str, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Execute a query and return results."""
        if self.connection is None:
            raise RuntimeError("Database connection is not established. Call connect() first.")
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, params or {})
            results = [dict(row) for row in cursor.fetchall()]
            cursor.close()
            return results
        except sqlite3.Error as e:
            logger.error(f"Error executing query: {str(e)}")
            raise

    def insert_data(self, table: str, data: List[Dict[str, Any]]) -> None:
        """Insert data into the specified table."""
        if self.connection is None:
            raise RuntimeError("Database connection is not established. Call connect() first.")
        if not data:
            return
        try:
            columns = list(data[0].keys())
            values = [tuple(row[col] for col in columns) for row in data]
            placeholders = ", ".join(["?"] * len(columns))
            columns_str = ", ".join(columns)
            query = f"INSERT INTO {table} ({columns_str}) VALUES ({placeholders})"
            cursor = self.connection.cursor()
            cursor.executemany(query, values)
            self.connection.commit()
            cursor.close()
            logger.debug(f"Inserted {len(data)} rows into {table}")
        except sqlite3.Error as e:
            logger.error(f"Error inserting data: {str(e)}")
            raise

    def update_data(self, table: str, data: List[Dict[str, Any]], key_columns: List[str]) -> None:
        """Update data in the specified table."""
        if self.connection is None:
            raise RuntimeError("Database connection is not established. Call connect() first.")
        if not data:
            return
        try:
            cursor = self.connection.cursor()
            for row in data:
                set_clause = ", ".join(f"{k} = ?" for k in row.keys() if k not in key_columns)
                where_clause = " AND ".join(f"{k} = ?" for k in key_columns)
                values = [v for k, v in row.items() if k not in key_columns] + [row.get(k) for k in key_columns]
                query = f"UPDATE {table} SET {set_clause} WHERE {where_clause}"
                cursor.execute(query, values)
                self.connection.commit()
                logger.debug(f"Updated row in {table} with keys: {key_columns}")
            cursor.close()
        except sqlite3.Error as e:
            logger.error(f"Error updating data: {str(e)}")
            raise

    def delete_data(self, table: str, conditions: Dict[str, Any]) -> None:
        """Delete data from the specified table."""
        if self.connection is None:
            raise RuntimeError("Database connection is not established. Call connect() first.")
        try:
            where_clause = " AND ".join(f"{k} = ?" for k in conditions.keys())
            values = list(conditions.values())
            query = f"DELETE FROM {table} WHERE {where_clause}"
            cursor = self.connection.cursor()
            cursor.execute(query, values)
            self.connection.commit()
            cursor.close()
            logger.debug(f"Deleted rows from {table} with conditions: {conditions}")
        except sqlite3.Error as e:
            logger.error(f"Error deleting data: {str(e)}")
            raise

    def get_watermark(self, table_name: str, watermark_column: str) -> Optional[Tuple[str, str]]:
        """Get the watermark value and status for a table."""
        if self.connection is None:
            raise RuntimeError("Database connection is not established. Call connect() first.")
        if not table_name or not watermark_column:
            raise ValueError("Table name and watermark column must be specified for watermark retrieval.")
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                SELECT watermark_value, status
                FROM sync_watermark
                WHERE table_name = ? AND watermark_column = ?
            """, (table_name, watermark_column))
            result = cursor.fetchone()
            cursor.close()
            if result:
                logger.debug(f"Retrieved watermark for {table_name}.{watermark_column}")
                return (result['watermark_value'], result['status'])
            logger.debug(f"No watermark found for {table_name}.{watermark_column}")
            return None
        except sqlite3.Error as e:
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
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                INSERT INTO sync_watermark 
                    (table_name, watermark_column, watermark_value, status, error_message, last_sync_at)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(table_name, watermark_column) DO UPDATE SET 
                    watermark_value = excluded.watermark_value,
                    status = excluded.status,
                    error_message = excluded.error_message,
                    last_sync_at = excluded.last_sync_at
            """, (table_name, watermark_column, watermark_value, status, error_message, datetime.now(UTC)))
            self.connection.commit()
            cursor.close()
            logger.debug(f"Updated watermark for {table_name}.{watermark_column}")
        except sqlite3.Error as e:
            logger.error(f"Error updating watermark: {str(e)}")
            raise

    def get_last_sync_timestamp(self) -> Optional[str]:
        """Get the last synchronization timestamp."""
        if not self.config.watermark or not self.config.table:
            return None
        try:
            query = f"""
                SELECT {self.config.watermark.column}
                FROM {self.config.table}
                ORDER BY {self.config.watermark.column} DESC
                LIMIT 1
            """
            result = self.execute_query(query)
            if result:
                logger.debug(f"Retrieved last sync timestamp from {self.config.table}")
                return result[0][self.config.watermark.column]
            logger.debug(f"No sync timestamp found in {self.config.table}")
            return None
        except sqlite3.Error as e:
            logger.error(f"Error getting last sync timestamp: {str(e)}")
            return None

    def update_last_sync_timestamp(self, timestamp: str) -> None:
        """Update the last synchronization timestamp."""
        if not self.config.watermark or not self.config.table:
            return
        try:
            query = f"""
                INSERT INTO {self.config.table} ({self.config.watermark.column})
                VALUES (?)
                ON CONFLICT DO UPDATE SET
                {self.config.watermark.column} = excluded.{self.config.watermark.column}
            """
            cursor = self.connection.cursor()
            cursor.execute(query, (timestamp,))
            self.connection.commit()
            cursor.close()
            logger.debug(f"Updated last sync timestamp in {self.config.table}")
        except sqlite3.Error as e:
            logger.error(f"Error updating last sync timestamp: {str(e)}")
            raise 