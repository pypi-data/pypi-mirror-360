from typing import Optional, Dict, Any, List, Union
from pydantic import BaseModel, Field, validator, field_validator
from enum import Enum


class DatabaseType(str, Enum):
    POSTGRESQL = "postgresql"
    MYSQL = "mysql"
    SQLITE = "sqlite"
    ORACLE = "oracle"
    SQLSERVER = "sqlserver"
    MONGODB = "mongodb"
    FILE = "file"
    S3 = "s3"
    GCS = "gcs"
    AZURE_BLOB = "azure_blob"
    KAFKA = "kafka"
    PULSAR = "pulsar"
    REDIS_STREAMS = "redis_streams"
    RABBITMQ = "rabbitmq"


class WatermarkType(str, Enum):
    TIMESTAMP = "timestamp"
    INTEGER = "integer"
    STRING = "string"


class CompressionType(str, Enum):
    GZIP = "gzip"
    SNAPPY = "snappy"
    LZ4 = "lz4"
    ZSTD = "zstd"
    NONE = "none"


class SyncMode(str, Enum):
    ONE_TIME = "one_time"
    CONTINUOUS = "continuous"
    CRON = "cron"


class WatermarkStorageType(str, Enum):
    DATABASE = "database"  # Store in source/destination database
    SQLITE = "sqlite"      # Store in separate SQLite file
    FILE = "file"          # Store in JSON file


class WatermarkConfig(BaseModel):
    column: str
    type: WatermarkType
    initial_value: Optional[str] = None
    increment_value: Optional[str] = None


class WatermarkStorageConfig(BaseModel):
    """Configuration for watermark storage."""
    type: WatermarkStorageType = Field(default=WatermarkStorageType.DATABASE)
    sqlite_path: Optional[str] = None  # Path to SQLite file when type is 'sqlite'
    file_path: Optional[str] = None    # Path to JSON file when type is 'file'
    table_name: str = Field(default="sync_watermark")  # Table name for watermark storage

    @field_validator("sqlite_path")
    def validate_sqlite_path(cls, v: Optional[str], info) -> Optional[str]:
        """Validate SQLite path when storage type is SQLite."""
        if info.data.get("type") == WatermarkStorageType.SQLITE and v is None:
            raise ValueError("sqlite_path is required when watermark storage type is 'sqlite'")
        return v

    @field_validator("file_path")
    def validate_file_path(cls, v: Optional[str], info) -> Optional[str]:
        """Validate file path when storage type is file."""
        if info.data.get("type") == WatermarkStorageType.FILE and v is None:
            raise ValueError("file_path is required when watermark storage type is 'file'")
        return v


class CloudStorageConfig(BaseModel):
    region: Optional[str] = None
    endpoint_url: Optional[str] = None
    use_ssl: bool = True
    verify_ssl: bool = True
    max_retries: int = 3
    timeout: int = 30
    chunk_size: int = 8 * 1024 * 1024  # 8MB


class DatabaseConfig(BaseModel):
    """Database configuration."""
    type: DatabaseType
    host: Optional[str] = None
    port: Optional[int] = None
    database: str
    username: Optional[str] = None
    password: Optional[str] = None
    file_path: Optional[str] = None  # For file-based data sources
    table: Optional[str] = None
    watermark: Optional[WatermarkConfig] = None
    query: Optional[str] = None  # Custom SQL query for data extraction
    select: Optional[str] = None  # Simple SELECT statement (alternative to query)
    ssl_mode: Optional[str] = None
    ssl_cert: Optional[str] = None
    ssl_key: Optional[str] = None
    ssl_root_cert: Optional[str] = None
    connection_timeout: int = Field(default=30, gt=0)
    pool_size: int = Field(default=5, gt=0)
    max_overflow: int = Field(default=10, gt=0)
    cloud_storage: Optional[CloudStorageConfig] = None  # For cloud storage services
    additional_params: Dict[str, Any] = Field(default_factory=dict)  # Additional connection parameters

    @field_validator("port")
    def validate_port(cls, v: Optional[int]) -> Optional[int]:
        """Validate port number."""
        if v is not None and not 1 <= v <= 65535:
            raise ValueError("Port must be between 1 and 65535")
        return v

    @field_validator("host", "username", "password")
    def validate_required_fields(cls, v: Optional[str], info) -> Optional[str]:
        """Validate required fields based on database type."""
        if info.data.get("type") != DatabaseType.SQLITE and v is None:
            raise ValueError(f"{info.field_name} is required for {info.data.get('type')} database")
        return v


class SyncConfig(BaseModel):
    mode: SyncMode = Field(default=SyncMode.ONE_TIME)
    batch_size: int = Field(default=1000, gt=0)
    interval_seconds: int = Field(default=60, gt=0)
    cron_expression: Optional[str] = None  # Cron expression for scheduled sync
    timezone: str = Field(default="UTC")  # Timezone for cron scheduling
    watermark_table: str = "sync_watermark"
    watermark_storage: Optional[WatermarkStorageConfig] = None  # Watermark storage configuration
    error_retry_attempts: int = Field(default=3, gt=0)
    error_retry_delay: int = Field(default=5, gt=0)
    compression: Optional[CompressionType] = None
    encryption: Optional[Dict[str, Any]] = None  # Encryption settings

    @field_validator("cron_expression")
    def validate_cron_expression(cls, v: Optional[str], info) -> Optional[str]:
        """Validate cron expression when mode is CRON."""
        if info.data.get("mode") == SyncMode.CRON and v is None:
            raise ValueError("cron_expression is required when mode is 'cron'")
        if v is not None:
            try:
                from croniter import croniter
                croniter(v)  # This will raise ValueError if invalid
            except ImportError:
                # Only warn about missing croniter, don't fail validation
                # The actual runtime will check for croniter when needed
                import warnings
                warnings.warn("croniter package is recommended for cron scheduling validation")
            except ValueError as e:
                raise ValueError(f"Invalid cron expression: {str(e)}")
        return v


class SourceDestinationMapping(BaseModel):
    """Configuration for mapping a source to a destination."""
    name: str = Field(..., description="Unique name for this mapping")
    source: DatabaseConfig = Field(..., description="Source database configuration")
    destination: DatabaseConfig = Field(..., description="Destination database configuration")
    sync: Optional[SyncConfig] = Field(default=None, description="Override sync settings for this mapping")
    enabled: bool = Field(default=True, description="Whether this mapping is enabled")
    description: Optional[str] = Field(default=None, description="Description of this mapping")

    # Table/view specific settings
    source_table: Optional[str] = Field(default=None, description="Override source table name")
    destination_table: Optional[str] = Field(default=None, description="Override destination table name")

    # Custom query for complex data extraction
    custom_query: Optional[str] = Field(default=None, description="Custom SQL query for data extraction")

    # Transformation settings
    column_mapping: Optional[Dict[str, str]] = Field(default=None, description="Map source columns to destination columns")
    exclude_columns: List[str] = Field(default_factory=list, description="Columns to exclude from sync")

    # Watermark override
    watermark: Optional[WatermarkConfig] = Field(default=None, description="Override watermark settings")


class CDCConfig(BaseModel):
    """Single source, single destination CDC configuration (backward compatible)."""
    source: DatabaseConfig
    destination: DatabaseConfig
    sync: SyncConfig = Field(default_factory=SyncConfig)
    tables: List[str] = Field(default_factory=list)
    exclude_tables: List[str] = Field(default_factory=list)
    include_schemas: List[str] = Field(default_factory=list)
    exclude_schemas: List[str] = Field(default_factory=list)
    plugins: Optional[Dict[str, Any]] = None  # Plugin configuration


class MultiCDCConfig(BaseModel):
    """Multi-source, multi-destination CDC configuration."""
    name: str = Field(..., description="Name of this CDC configuration")
    description: Optional[str] = Field(default=None, description="Description of this CDC setup")

    # Global settings that apply to all mappings (can be overridden per mapping)
    global_sync: SyncConfig = Field(default_factory=SyncConfig, description="Default sync settings")
    global_plugins: Optional[Dict[str, Any]] = Field(default=None, description="Global plugin configuration")

    # Source-destination mappings
    mappings: List[SourceDestinationMapping] = Field(..., description="List of source-destination mappings")

    # Execution settings
    parallel_execution: bool = Field(default=True, description="Execute mappings in parallel")
    max_workers: int = Field(default=5, description="Maximum number of parallel workers")
    stop_on_error: bool = Field(default=False, description="Stop all mappings if one fails")

    # Monitoring and logging
    enable_monitoring: bool = Field(default=True, description="Enable monitoring and metrics")
    log_level: str = Field(default="INFO", description="Logging level")

    @field_validator('mappings')
    @classmethod
    def validate_mappings(cls, v):
        if not v:
            raise ValueError("At least one mapping must be defined")

        # Check for duplicate mapping names
        names = [mapping.name for mapping in v]
        if len(names) != len(set(names)):
            raise ValueError("Mapping names must be unique")

        return v

    @field_validator('max_workers')
    @classmethod
    def validate_max_workers(cls, v):
        if v < 1:
            raise ValueError("max_workers must be at least 1")
        if v > 20:
            raise ValueError("max_workers should not exceed 20 for performance reasons")
        return v


class FlexibleCDCConfig(BaseModel):
    """Flexible CDC configuration that supports both single and multi-source scenarios."""

    # Single source/destination (backward compatible)
    source: Optional[DatabaseConfig] = Field(default=None)
    destination: Optional[DatabaseConfig] = Field(default=None)
    sync: Optional[SyncConfig] = Field(default=None)

    # Multi-source/destination
    multi: Optional[MultiCDCConfig] = Field(default=None)

    # Common settings
    tables: List[str] = Field(default_factory=list)
    exclude_tables: List[str] = Field(default_factory=list)
    include_schemas: List[str] = Field(default_factory=list)
    exclude_schemas: List[str] = Field(default_factory=list)
    plugins: Optional[Dict[str, Any]] = None

    def model_post_init(self, __context):
        """Post-initialization validation."""
        # Check that either single or multi configuration is provided, not both
        if self.multi is not None and self.source is not None:
            raise ValueError("Cannot specify both single source and multi configuration")
        elif self.source is None and self.multi is None:
            raise ValueError("Must specify either single source/destination or multi configuration")

    def is_multi_config(self) -> bool:
        """Check if this is a multi-source/destination configuration."""
        return self.multi is not None

    def get_single_config(self) -> CDCConfig:
        """Convert to single CDC configuration (for backward compatibility)."""
        if self.is_multi_config():
            raise ValueError("Cannot convert multi-configuration to single configuration")

        return CDCConfig(
            source=self.source,
            destination=self.destination,
            sync=self.sync or SyncConfig(),
            tables=self.tables,
            exclude_tables=self.exclude_tables,
            include_schemas=self.include_schemas,
            exclude_schemas=self.exclude_schemas,
            plugins=self.plugins
        )