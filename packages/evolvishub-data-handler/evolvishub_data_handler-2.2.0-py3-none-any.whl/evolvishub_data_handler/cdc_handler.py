"""CDC handler implementation."""
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
import threading

from loguru import logger

from .adapters.base import BaseAdapter
from .config import DatabaseConfig, DatabaseType, CDCConfig, SyncMode, WatermarkStorageType
from .adapters.factory import AdapterFactory
from .watermark_manager import create_watermark_manager, BaseWatermarkManager
from .plugins.manager import PluginManager
from .plugins.hooks import EventType


class CDCHandler:
    """Change Data Capture handler for data synchronization."""

    def __init__(self, config: CDCConfig):
        """Initialize the CDC handler.

        Args:
            config: CDC configuration object.
        """
        self.config = config
        self.source_adapter: BaseAdapter = AdapterFactory.create(config.source)
        self.destination_adapter: BaseAdapter = AdapterFactory.create(config.destination)
        self._stop_event = threading.Event()
        self._scheduler_thread: Optional[threading.Thread] = None

        # Initialize watermark manager if configured
        self.watermark_manager: Optional[BaseWatermarkManager] = None

        # Initialize plugin manager (optional)
        self.plugin_manager: Optional[PluginManager] = None
        if hasattr(config, 'plugins') and config.plugins:
            try:
                self.plugin_manager = PluginManager(config.plugins)
                self.plugin_manager.initialize()
                logger.info("Plugin system initialized")
            except Exception as e:
                logger.warning(f"Plugin system initialization failed, continuing without plugins: {e}")
                self.plugin_manager = None
        if config.sync.watermark_storage and config.sync.watermark_storage.type != WatermarkStorageType.DATABASE:
            self.watermark_manager = create_watermark_manager(config.sync.watermark_storage)

        self._setup_logging()

    def _setup_logging(self) -> None:
        """Set up logging configuration."""
        logger.add(
            "logs/cdc.log",
            rotation="10 MB",
            retention="10 days",
            level="INFO",
        )

    def _create_adapter(self, config: DatabaseConfig) -> BaseAdapter:
        """Create a database adapter based on configuration.

        Args:
            config: Database configuration

        Returns:
            BaseAdapter: Configured database adapter

        Raises:
            ValueError: If database type is not supported
        """
        if config.type == DatabaseType.POSTGRESQL:
            from .adapters.postgresql import PostgreSQLAdapter
            return PostgreSQLAdapter(config)
        elif config.type == DatabaseType.MYSQL:
            from .adapters.mysql import MySQLAdapter
            return MySQLAdapter(config)
        elif config.type == DatabaseType.SQLITE:
            from .adapters.sqlite import SQLiteAdapter
            return SQLiteAdapter(config)
        elif config.type == DatabaseType.ORACLE:
            from .adapters.oracle import OracleAdapter
            return OracleAdapter(config)
        elif config.type == DatabaseType.SQLSERVER:
            from .adapters.sqlserver import SQLServerAdapter
            return SQLServerAdapter(config)
        elif config.type == DatabaseType.MONGODB:
            from .adapters.mongodb import MongoDBAdapter
            return MongoDBAdapter(config)
        else:
            raise ValueError(f"Unsupported database type: {config.type}")

    def _create_adapters(self) -> Tuple[BaseAdapter, BaseAdapter]:
        """Create source and destination adapters.

        Returns:
            Tuple[BaseAdapter, BaseAdapter]: Source and destination adapters
        """
        source_adapter = self._create_adapter(self.config.source)
        dest_adapter = self._create_adapter(self.config.destination)
        return source_adapter, dest_adapter

    def _process_batch(self, changes: List[Dict[str, Any]]) -> None:
        """Process a batch of changes.

        Args:
            changes: List of changes to process.
        """
        for change in changes:
            try:
                operation = change.get("operation", "INSERT")
                if operation == "INSERT":
                    self.destination_adapter.insert_data(self.config.destination.table, [change])
                elif operation == "UPDATE":
                    self.destination_adapter.update_data(
                        self.config.destination.table,
                        [change],
                        ["id"]  # Assuming 'id' is the primary key
                    )
                elif operation == "DELETE":
                    self.destination_adapter.delete_data(
                        self.config.destination.table,
                        {"id": change["id"]}
                    )
            except Exception as e:
                logger.error(f"Error processing change: {str(e)}")
                raise

    def _get_watermark_value(
        self, watermark_type: str, current_value: str, new_value: str
    ) -> str:
        """Get the appropriate watermark value based on type.

        Args:
            watermark_type: Type of watermark (timestamp, integer, string)
            current_value: Current watermark value
            new_value: New watermark value

        Returns:
            str: Selected watermark value
        """
        if watermark_type == "timestamp":
            return max(current_value, new_value)
        elif watermark_type == "integer":
            return str(max(int(current_value), int(new_value)))
        else:  # string
            return max(current_value, new_value)

    def _get_current_watermark(self) -> Optional[str]:
        """Get the current watermark value using the appropriate method."""
        if self.watermark_manager and self.config.source.watermark:
            # Use centralized watermark manager
            table_name = self.config.source.table or "default"
            watermark_column = self.config.source.watermark.column

            result = self.watermark_manager.get_watermark(table_name, watermark_column)
            if result:
                watermark_value, status = result
                if status == 'success':
                    return watermark_value
                else:
                    logger.warning(f"Last sync had status '{status}', using initial value")

            # Return initial value if no watermark found
            return self.config.source.watermark.initial_value
        else:
            # Use adapter's built-in watermark functionality
            return self.source_adapter.get_last_sync_timestamp()

    def _update_current_watermark(self, watermark_value: str, status: str = 'success',
                                 error_message: Optional[str] = None) -> None:
        """Update the watermark value using the appropriate method."""
        if self.watermark_manager and self.config.source.watermark:
            # Use centralized watermark manager
            table_name = self.config.source.table or "default"
            watermark_column = self.config.source.watermark.column

            self.watermark_manager.update_watermark(
                table_name, watermark_column, watermark_value, status, error_message
            )
        else:
            # Use adapter's built-in watermark functionality
            self.source_adapter.update_last_sync_timestamp(watermark_value)

    def _build_query(self, watermark: Optional[str]) -> Tuple[str, Dict[str, Any]]:
        """Build the query for data extraction.

        Args:
            watermark: The last sync timestamp

        Returns:
            Tuple of (query_string, parameters)
        """
        params = {
            "last_sync": watermark,
            "batch_size": self.config.sync.batch_size
        }

        # Use custom query if provided
        if self.config.source.query:
            query = self.config.source.query
            # Replace named parameters
            for param_name, param_value in params.items():
                query = query.replace(f":{param_name}", f"%({param_name})s")
            return query, params

        # Use simple select if provided
        elif self.config.source.select:
            base_query = self.config.source.select
            if self.config.source.watermark and watermark:
                query = f"""
                    {base_query}
                    WHERE {self.config.source.watermark.column} > %(last_sync)s
                    ORDER BY {self.config.source.watermark.column}
                    LIMIT %(batch_size)s
                """
            else:
                query = f"{base_query} LIMIT %(batch_size)s"
            return query, params

        # Default query
        else:
            if self.config.source.watermark and watermark:
                query = f"""
                    SELECT * FROM {self.config.source.table}
                    WHERE {self.config.source.watermark.column} > %(last_sync)s
                    ORDER BY {self.config.source.watermark.column}
                    LIMIT %(batch_size)s
                """
            else:
                query = f"SELECT * FROM {self.config.source.table} LIMIT %(batch_size)s"
            return query, params

    def sync(self) -> None:
        """Perform a single synchronization cycle."""
        try:
            # Trigger sync start event (optional)
            if self.plugin_manager:
                try:
                    self.plugin_manager.trigger_event(EventType.SYNC_START, {
                        'timestamp': datetime.now().isoformat(),
                        'source_type': self.config.source.type.value,
                        'destination_type': self.config.destination.type.value
                    })
                except Exception as e:
                    logger.warning(f"Plugin event failed, continuing: {e}")

            # Connect to databases
            self.source_adapter.connect()
            self.destination_adapter.connect()

            # Get the current watermark value
            watermark = self._get_current_watermark()

            # Build and execute query
            query, params = self._build_query(watermark)
            changes = self.source_adapter.execute_query(query, params)

            if changes:
                # Trigger read end event (optional)
                if self.plugin_manager:
                    try:
                        self.plugin_manager.trigger_event(EventType.READ_END, {
                            'timestamp': datetime.now().isoformat(),
                            'records_count': len(changes)
                        })
                    except Exception as e:
                        logger.warning(f"Plugin event failed, continuing: {e}")

                self._process_batch(changes)
                # Update watermark if we have watermark configuration
                if self.config.source.watermark and changes:
                    last_record = changes[-1]
                    new_watermark = last_record.get(self.config.source.watermark.column)
                    if new_watermark:
                        self._update_current_watermark(str(new_watermark), 'success')

        except Exception as e:
            logger.error(f"Error during sync: {str(e)}")
            # Update watermark with error status if we have watermark configuration
            if self.config.source.watermark:
                watermark = self._get_current_watermark()
                if watermark:
                    self._update_current_watermark(watermark, 'error', str(e))
            raise
        finally:
            # Trigger sync end event (optional)
            if self.plugin_manager:
                try:
                    self.plugin_manager.trigger_event(EventType.SYNC_END, {
                        'timestamp': datetime.now().isoformat()
                    })
                except Exception as e:
                    logger.warning(f"Plugin event failed, continuing: {e}")

            # Disconnect from databases
            self.source_adapter.disconnect()
            self.destination_adapter.disconnect()

    def _process_batch(self, data: List[Dict[str, Any]]) -> None:
        """Process a batch of data with optional plugin integration."""
        try:
            # Apply middleware after read processing (optional)
            if self.plugin_manager:
                try:
                    data = self.plugin_manager.process_middleware_after_read(data)
                except Exception as e:
                    logger.warning(f"Middleware after read failed, continuing: {e}")

            # Apply data transformations (optional)
            if self.plugin_manager:
                try:
                    data = self.plugin_manager.transform_data(data)
                except Exception as e:
                    logger.warning(f"Data transformation failed, continuing: {e}")

            # Apply middleware before write processing (optional)
            if self.plugin_manager:
                try:
                    data = self.plugin_manager.process_middleware_before_write(data)
                except Exception as e:
                    logger.warning(f"Middleware before write failed, continuing: {e}")

            # Trigger write start event (optional)
            if self.plugin_manager:
                try:
                    self.plugin_manager.trigger_event(EventType.WRITE_START, {
                        'timestamp': datetime.now().isoformat(),
                        'records_count': len(data)
                    })
                except Exception as e:
                    logger.warning(f"Plugin event failed, continuing: {e}")

            # Write data to destination (core functionality)
            if data:
                self.destination_adapter.insert_data(self.config.destination.table, data)
                logger.info(f"Successfully processed {len(data)} records")

                # Trigger batch processed event (optional)
                if self.plugin_manager:
                    try:
                        self.plugin_manager.trigger_event(EventType.BATCH_PROCESSED, {
                            'timestamp': datetime.now().isoformat(),
                            'records_count': len(data)
                        })
                    except Exception as e:
                        logger.warning(f"Plugin event failed, continuing: {e}")

            # Apply middleware after write processing (optional)
            if self.plugin_manager:
                try:
                    self.plugin_manager.process_middleware_after_write(data, None)
                except Exception as e:
                    logger.warning(f"Middleware after write failed, continuing: {e}")

            # Trigger write end event (optional)
            if self.plugin_manager:
                try:
                    self.plugin_manager.trigger_event(EventType.WRITE_END, {
                        'timestamp': datetime.now().isoformat(),
                        'records_count': len(data)
                    })
                except Exception as e:
                    logger.warning(f"Plugin event failed, continuing: {e}")

        except Exception as e:
            # Trigger error event (optional)
            if self.plugin_manager:
                try:
                    self.plugin_manager.trigger_event(EventType.ERROR, {
                        'timestamp': datetime.now().isoformat(),
                        'error': str(e),
                        'records_count': len(data) if data else 0
                    })
                except Exception as plugin_error:
                    logger.warning(f"Plugin error event failed: {plugin_error}")
            raise

    def run_continuous(self) -> None:
        """Run continuous synchronization."""
        try:
            logger.info("Starting continuous sync...")
            while not self._stop_event.is_set():
                self.sync()
                if self._stop_event.wait(self.config.sync.interval_seconds):
                    break
        except KeyboardInterrupt:
            logger.info("Continuous sync stopped by user")
        except Exception as e:
            logger.error(f"Error in continuous sync: {str(e)}")
            raise

    def run_cron(self) -> None:
        """Run synchronization based on cron schedule."""
        if not self.config.sync.cron_expression:
            raise ValueError("Cron expression is required for cron mode")

        try:
            from croniter import croniter
            import pytz
        except ImportError:
            raise ImportError("croniter and pytz packages are required for cron scheduling")

        # Set up timezone
        tz = pytz.timezone(self.config.sync.timezone)

        logger.info(f"Starting cron sync with expression: {self.config.sync.cron_expression}")

        try:
            cron = croniter(self.config.sync.cron_expression, datetime.now(tz))

            while not self._stop_event.is_set():
                next_run = cron.get_next(datetime)
                now = datetime.now(tz)

                # Calculate sleep time until next run
                sleep_time = (next_run - now).total_seconds()

                if sleep_time > 0:
                    logger.info(f"Next sync scheduled at: {next_run}")
                    if self._stop_event.wait(sleep_time):
                        break

                # Run sync if not stopped
                if not self._stop_event.is_set():
                    logger.info("Running scheduled sync...")
                    self.sync()

        except KeyboardInterrupt:
            logger.info("Cron sync stopped by user")
        except Exception as e:
            logger.error(f"Error in cron sync: {str(e)}")
            raise

    def run(self) -> None:
        """Run synchronization based on configured mode."""
        mode = self.config.sync.mode

        if mode == SyncMode.ONE_TIME:
            logger.info("Running one-time sync...")
            self.sync()
        elif mode == SyncMode.CONTINUOUS:
            self.run_continuous()
        elif mode == SyncMode.CRON:
            self.run_cron()
        else:
            raise ValueError(f"Unsupported sync mode: {mode}")

    def stop(self) -> None:
        """Stop the synchronization process."""
        logger.info("Stopping sync process...")
        self._stop_event.set()

        if self._scheduler_thread and self._scheduler_thread.is_alive():
            self._scheduler_thread.join(timeout=5)

        # Close watermark manager if it exists
        if self.watermark_manager:
            self.watermark_manager.close()

        # Cleanup plugin manager if it exists (optional)
        if self.plugin_manager:
            try:
                self.plugin_manager.cleanup()
                logger.info("Plugin system cleaned up")
            except Exception as e:
                logger.warning(f"Plugin cleanup failed: {e}")