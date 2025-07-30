"""Oracle database adapter for data synchronization."""

from typing import Any, Dict, List, Optional, Tuple, Union
from datetime import datetime, timezone
import logging

try:
    import oracledb  # type: ignore
except ImportError:
    try:
        import cx_Oracle as oracledb  # type: ignore
    except ImportError:
        oracledb = None

from ..config import DatabaseConfig
from .base import BaseAdapter

OracleError = getattr(oracledb, "Error", Exception)
OracleLOB = getattr(oracledb, "LOB", type(None))

logger = logging.getLogger(__name__)

class OracleAdapter(BaseAdapter):
    """Oracle database adapter for data synchronization."""

    def __init__(self, config: DatabaseConfig):
        """Initialize the Oracle adapter.

        Args:
            config: Database configuration

        Raises:
            ImportError: If oracledb package is not installed
        """
        if oracledb is None:
            raise ImportError(
                "oracledb package is required for Oracle connectivity. "
                "Install it with: pip install oracledb"
            )

        super().__init__(config)
        self.connection = None

    def connect(self) -> None:
        """Connect to the Oracle database."""
        if oracledb is None:
            raise ImportError("oracledb package is required for Oracle connectivity. Install it with: pip install oracledb")
        try:
            # Build connection string
            if self.config.host and self.config.port:
                # Standard connection
                dsn = oracledb.makedsn(
                    host=self.config.host,
                    port=self.config.port,
                    service_name=self.config.database
                )
                self.connection = oracledb.connect(
                    user=self.config.username,
                    password=self.config.password,
                    dsn=dsn,
                    **self.config.additional_params
                )
            else:
                # Connection using TNS name or connection string
                self.connection = oracledb.connect(
                    user=self.config.username,
                    password=self.config.password,
                    dsn=self.config.database,
                    **self.config.additional_params
                )
            self.connection.autocommit = False
            logger.debug(f"Connected to Oracle database: {self.config.database}")
        except OracleError as e:
            logger.error(f"Error connecting to Oracle database: {str(e)}")
            raise

    def disconnect(self) -> None:
        """Close the Oracle connection."""
        if self.connection:
            try:
                self.connection.close()
                self.connection = None
                logger.debug("Oracle database connection closed")
            except OracleError as e:
                logger.error(f"Error closing Oracle connection: {str(e)}")

    def execute_query(self, query: str, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Execute a query and return results.

        Args:
            query: SQL query to execute
            params: Query parameters

        Returns:
            List of dictionaries representing query results
        """
        if self.connection is None:
            raise RuntimeError("Database connection is not established. Call connect() first.")
        try:
            with self.connection.cursor() as cursor:
                # Oracle uses named parameters with :param_name syntax
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)

                # Get column names
                columns = [desc[0].lower() for desc in cursor.description] if cursor.description else []

                # Fetch all results
                rows = cursor.fetchall()

                # Convert to list of dictionaries
                result = []
                for row in rows:
                    row_dict = {}
                    for i, value in enumerate(row):
                        # Handle Oracle-specific data types
                        if isinstance(value, OracleLOB):
                            # Handle CLOB/BLOB
                            value = value.read()
                        elif hasattr(value, 'isoformat'):
                            # Handle datetime objects
                            value = value.isoformat()
                        row_dict[columns[i]] = value
                    result.append(row_dict)

                logger.debug(f"Executed query, returned {len(result)} rows")
                return result

        except OracleError as e:
            logger.error(f"Error executing query: {str(e)}")
            raise

    def insert_data(self, table: str, data: Union[Dict[str, Any], List[Dict[str, Any]]]) -> None:
        """Insert data into the specified table.

        Args:
            table: Target table name
            data: Data to insert (single dict or list of dicts)
        """
        if self.connection is None:
            raise RuntimeError("Database connection is not established. Call connect() first.")
        if not data:
            return

        if isinstance(data, dict):
            data = [data]

        try:
            with self.connection.cursor() as cursor:
                columns = list(data[0].keys())
                placeholders = ", ".join([f":{col}" for col in columns])
                columns_str = ", ".join(columns)

                query = f"INSERT INTO {table} ({columns_str}) VALUES ({placeholders})"

                # Prepare data for Oracle
                oracle_data = []
                for row in data:
                    oracle_row = {}
                    for col in columns:
                        value = row[col]
                        # Handle None values
                        if value is None:
                            oracle_row[col] = None
                        # Handle datetime strings
                        elif isinstance(value, str) and 'T' in value:
                            try:
                                # Try to parse ISO datetime
                                dt = datetime.fromisoformat(value.replace('Z', '+00:00'))
                                oracle_row[col] = dt
                            except ValueError:
                                oracle_row[col] = value
                        else:
                            oracle_row[col] = value
                    oracle_data.append(oracle_row)

                if len(oracle_data) == 1:
                    cursor.execute(query, oracle_data[0])
                else:
                    cursor.executemany(query, oracle_data)

                self.connection.commit()
                logger.debug(f"Inserted {len(oracle_data)} rows into {table}")

        except OracleError as e:
            self.connection.rollback()
            logger.error(f"Error inserting data into {table}: {str(e)}")
            raise

    def update_data(self, table: str, data: Union[Dict[str, Any], List[Dict[str, Any]]],
                   key_columns: Union[str, List[str]]) -> None:
        """Update data in the specified table.

        Args:
            table: Target table name
            data: Data to update (single dict or list of dicts)
            key_columns: Column(s) to use as key for WHERE clause
        """
        if self.connection is None:
            raise RuntimeError("Database connection is not established. Call connect() first.")
        if not data:
            return

        if isinstance(data, dict):
            data = [data]

        if isinstance(key_columns, str):
            key_columns = [key_columns]

        try:
            with self.connection.cursor() as cursor:
                for row in data:
                    # Build SET clause
                    set_columns = [col for col in row.keys() if col not in key_columns]
                    set_clause = ", ".join(f"{col} = :{col}" for col in set_columns)

                    # Build WHERE clause
                    where_clause = " AND ".join(f"{col} = :{col}" for col in key_columns)

                    query = f"UPDATE {table} SET {set_clause} WHERE {where_clause}"

                    # Prepare parameters
                    params = {}
                    for col in set_columns + key_columns:
                        value = row.get(col)
                        if isinstance(value, str) and 'T' in value:
                            try:
                                # Try to parse ISO datetime
                                dt = datetime.fromisoformat(value.replace('Z', '+00:00'))
                                params[col] = dt
                            except ValueError:
                                params[col] = value
                        else:
                            params[col] = value

                    cursor.execute(query, params)

                self.connection.commit()
                logger.debug(f"Updated {len(data)} rows in {table}")

        except OracleError as e:
            self.connection.rollback()
            logger.error(f"Error updating data in {table}: {str(e)}")
            raise

    def delete_data(self, table: str, conditions: Union[str, Dict[str, Any]]) -> None:
        """Delete data from the specified table.

        Args:
            table: Target table name
            conditions: WHERE conditions (string or dict)
        """
        if self.connection is None:
            raise RuntimeError("Database connection is not established. Call connect() first.")
        try:
            with self.connection.cursor() as cursor:
                if isinstance(conditions, str):
                    query = f"DELETE FROM {table} WHERE {conditions}"
                    cursor.execute(query)
                else:
                    where_clause = " AND ".join(f"{col} = :{col}" for col in conditions.keys())
                    query = f"DELETE FROM {table} WHERE {where_clause}"
                    cursor.execute(query, conditions)

                rows_deleted = cursor.rowcount
                self.connection.commit()
                logger.debug(f"Deleted {rows_deleted} rows from {table}")

        except OracleError as e:
            self.connection.rollback()
            logger.error(f"Error deleting data from {table}: {str(e)}")
            raise

    def get_watermark(self, table: str, column: str) -> Optional[str]:
        """Get the watermark value for the specified table and column.

        Args:
            table: Table name
            column: Column name

        Returns:
            Watermark value or None if not found
        """
        if self.connection is None:
            raise RuntimeError("Database connection is not established. Call connect() first.")
        if not table or not column:
            raise ValueError("Table and column must be specified for watermark retrieval.")
        try:
            # Oracle uses ROWNUM instead of LIMIT
            query = f"""
                SELECT {column} FROM (
                    SELECT {column} FROM {table}
                    ORDER BY {column} DESC
                ) WHERE ROWNUM = 1
            """
            result = self.execute_query(query)

            if result and result[0][column.lower()]:
                value = result[0][column.lower()]
                # Convert datetime to string if needed
                if hasattr(value, 'isoformat'):
                    return value.isoformat()
                return str(value)

            return None

        except OracleError as e:
            logger.error(f"Error getting watermark from {table}.{column}: {str(e)}")
            return None

    def update_watermark(self, table_name: str, watermark_column: str,
                        watermark_value: str, status: str = 'success',
                        error_message: Optional[str] = None) -> None:
        """Update the watermark value for a table.

        Args:
            table_name: Name of the table
            watermark_column: Name of the watermark column
            watermark_value: New watermark value
            status: Status of the sync operation
            error_message: Error message if status is 'error'
        """
        if self.connection is None:
            raise RuntimeError("Database connection is not established. Call connect() first.")
        if not table_name or not watermark_column:
            raise ValueError("Table name and watermark column must be specified for updating watermark.")
        try:
            with self.connection.cursor() as cursor:
                # Oracle doesn't have UPSERT like PostgreSQL, so we use MERGE
                merge_query = """
                    MERGE INTO sync_watermark sw
                    USING (
                        SELECT :table_name as table_name,
                               :watermark_column as watermark_column,
                               :watermark_value as watermark_value,
                               :status as status,
                               :error_message as error_message,
                               SYSTIMESTAMP as last_sync_at
                        FROM dual
                    ) src ON (sw.table_name = src.table_name AND sw.watermark_column = src.watermark_column)
                    WHEN MATCHED THEN
                        UPDATE SET
                            watermark_value = src.watermark_value,
                            status = src.status,
                            error_message = src.error_message,
                            last_sync_at = src.last_sync_at,
                            updated_at = SYSTIMESTAMP
                    WHEN NOT MATCHED THEN
                        INSERT (table_name, watermark_column, watermark_value, status, error_message,
                                last_sync_at, created_at, updated_at)
                        VALUES (src.table_name, src.watermark_column, src.watermark_value, src.status,
                                src.error_message, src.last_sync_at, SYSTIMESTAMP, SYSTIMESTAMP)
                """

                cursor.execute(merge_query, {
                    'table_name': table_name,
                    'watermark_column': watermark_column,
                    'watermark_value': watermark_value,
                    'status': status,
                    'error_message': error_message
                })

                self.connection.commit()
                logger.debug(f"Updated watermark for {table_name}.{watermark_column}: {watermark_value}")

        except OracleError as e:
            self.connection.rollback()
            logger.error(f"Error updating watermark: {str(e)}")
            raise

    def get_last_sync_timestamp(self) -> Optional[str]:
        """Get the last synchronization timestamp from the sync_metadata table.

        Returns:
            Last sync timestamp or None if not found
        """
        if not self.config.watermark or not self.config.table:
            return None
        if self.connection is None:
            raise RuntimeError("Database connection is not established. Call connect() first.")
        try:
            # Get watermark from sync_watermark table
            query = """
                SELECT watermark_value FROM (
                    SELECT watermark_value
                    FROM sync_watermark
                    WHERE table_name = :table_name
                      AND watermark_column = :watermark_column
                      AND status = 'success'
                    ORDER BY updated_at DESC
                ) WHERE ROWNUM = 1
            """

            result = self.execute_query(query, {
                'table_name': self.config.table,
                'watermark_column': self.config.watermark.column
            })

            if result:
                return result[0]['watermark_value']

            # If no watermark found, return initial value
            return self.config.watermark.initial_value

        except OracleError as e:
            logger.error(f"Error getting last sync timestamp: {str(e)}")
            return self.config.watermark.initial_value if self.config.watermark else None

    def update_last_sync_timestamp(self, timestamp: str) -> None:
        """Update the last synchronization timestamp in the sync_metadata table.

        Args:
            timestamp: New timestamp value
        """
        if not self.config.watermark or not self.config.table:
            return
        if self.connection is None:
            raise RuntimeError("Database connection is not established. Call connect() first.")
        self.update_watermark(
            self.config.table,
            self.config.watermark.column,
            timestamp
        )

    def create_watermark_table(self) -> None:
        """Create the sync_watermark table if it doesn't exist."""
        if self.connection is None:
            raise RuntimeError("Database connection is not established. Call connect() first.")
        try:
            with self.connection.cursor() as cursor:
                # Check if table exists
                cursor.execute("""
                    SELECT COUNT(*) FROM user_tables
                    WHERE table_name = 'SYNC_WATERMARK'
                """)

                if cursor.fetchone()[0] == 0:
                    # Create the table
                    create_table_sql = """
                        CREATE TABLE sync_watermark (
                            id NUMBER GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
                            table_name VARCHAR2(128) NOT NULL,
                            watermark_column VARCHAR2(128) NOT NULL,
                            watermark_value VARCHAR2(4000) NOT NULL,
                            status VARCHAR2(50) DEFAULT 'success' NOT NULL,
                            error_message CLOB,
                            last_sync_at TIMESTAMP DEFAULT SYSTIMESTAMP,
                            created_at TIMESTAMP DEFAULT SYSTIMESTAMP,
                            updated_at TIMESTAMP DEFAULT SYSTIMESTAMP,
                            CONSTRAINT uk_sync_watermark UNIQUE (table_name, watermark_column)
                        )
                    """
                    cursor.execute(create_table_sql)
                    self.connection.commit()
                    logger.info("Created sync_watermark table")

        except OracleError as e:
            logger.error(f"Error creating watermark table: {str(e)}")
            raise

    def test_connection(self) -> bool:
        """Test the database connection.

        Returns:
            True if connection is successful, False otherwise
        """
        if self.connection is None:
            return False
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("SELECT 1 FROM dual")
                result = cursor.fetchone()
                return result is not None
        except OracleError as e:
            logger.error(f"Connection test failed: {str(e)}")
            return False