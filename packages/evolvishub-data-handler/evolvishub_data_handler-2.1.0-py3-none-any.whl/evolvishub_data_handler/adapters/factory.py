from typing import Dict, Type
from ..config import DatabaseConfig, DatabaseType
from .base import BaseAdapter
# Import adapters with graceful fallback for optional dependencies
try:
    from .postgresql import PostgreSQLAdapter
except ImportError:
    PostgreSQLAdapter = None

try:
    from .mysql import MySQLAdapter
except ImportError:
    MySQLAdapter = None

try:
    from .sqlite import SQLiteAdapter
except ImportError:
    SQLiteAdapter = None

try:
    from .oracle import OracleAdapter
except ImportError:
    OracleAdapter = None

try:
    from .mongodb import MongoDBAdapter
except ImportError:
    MongoDBAdapter = None

try:
    from .file import FileAdapter
except ImportError:
    FileAdapter = None

try:
    from .s3 import S3Adapter
except ImportError:
    S3Adapter = None

try:
    from .kafka import KafkaAdapter
except ImportError:
    KafkaAdapter = None

try:
    from .pulsar import PulsarAdapter
except ImportError:
    PulsarAdapter = None

try:
    from .redis_streams import RedisStreamsAdapter
except ImportError:
    RedisStreamsAdapter = None

try:
    from .rabbitmq import RabbitMQAdapter
except ImportError:
    RabbitMQAdapter = None


class AdapterFactory:
    """Factory class for creating database adapters."""

    # Initialize adapters dict with only available adapters
    _adapters: Dict[DatabaseType, Type[BaseAdapter]] = {}

    @classmethod
    def _initialize_adapters(cls):
        """Initialize available adapters."""
        if cls._adapters:  # Already initialized
            return

        # Add adapters that are available
        if PostgreSQLAdapter:
            cls._adapters[DatabaseType.POSTGRESQL] = PostgreSQLAdapter
        if MySQLAdapter:
            cls._adapters[DatabaseType.MYSQL] = MySQLAdapter
        if SQLiteAdapter:
            cls._adapters[DatabaseType.SQLITE] = SQLiteAdapter
        if OracleAdapter:
            cls._adapters[DatabaseType.ORACLE] = OracleAdapter
        if MongoDBAdapter:
            cls._adapters[DatabaseType.MONGODB] = MongoDBAdapter
        if FileAdapter:
            cls._adapters[DatabaseType.FILE] = FileAdapter
        if S3Adapter:
            cls._adapters[DatabaseType.S3] = S3Adapter
        if KafkaAdapter:
            cls._adapters[DatabaseType.KAFKA] = KafkaAdapter
        if PulsarAdapter:
            cls._adapters[DatabaseType.PULSAR] = PulsarAdapter
        if RedisStreamsAdapter:
            cls._adapters[DatabaseType.REDIS_STREAMS] = RedisStreamsAdapter
        if RabbitMQAdapter:
            cls._adapters[DatabaseType.RABBITMQ] = RabbitMQAdapter

    @classmethod
    def create(cls, config: DatabaseConfig) -> BaseAdapter:
        """Create a database adapter based on the configuration.

        Args:
            config: Database configuration object.

        Returns:
            An instance of the appropriate database adapter.

        Raises:
            ValueError: If the database type is not supported.
        """
        cls._initialize_adapters()  # Ensure adapters are initialized

        adapter_class = cls._adapters.get(config.type)
        if not adapter_class:
            available_types = list(cls._adapters.keys())
            raise ValueError(f"Unsupported database type: {config.type}. Available types: {available_types}")

        return adapter_class(config)

    @classmethod
    def register_adapter(cls, database_type: DatabaseType, adapter_class: Type[BaseAdapter]) -> None:
        """Register a new adapter type dynamically.

        Args:
            database_type: The database type enum value
            adapter_class: The adapter class to register
        """
        if not issubclass(adapter_class, BaseAdapter):
            raise ValueError(f"Adapter must inherit from BaseAdapter: {adapter_class}")

        cls._initialize_adapters()  # Ensure adapters are initialized
        cls._adapters[database_type] = adapter_class

    @classmethod
    def unregister_adapter(cls, database_type: DatabaseType) -> None:
        """Unregister an adapter type.

        Args:
            database_type: The database type to unregister
        """
        if database_type in cls._adapters:
            del cls._adapters[database_type]

    @classmethod
    def list_adapters(cls) -> Dict[DatabaseType, Type[BaseAdapter]]:
        """List all registered adapters.

        Returns:
            Dictionary of database types to adapter classes
        """
        cls._initialize_adapters()  # Ensure adapters are initialized
        return cls._adapters.copy()