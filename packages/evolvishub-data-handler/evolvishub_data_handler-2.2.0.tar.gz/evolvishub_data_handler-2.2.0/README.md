# EvolvisHub Data Handler

<div align="center">
  <img src="assets/png/eviesales.png" alt="Evolvis AI Logo" width="200"/>
</div>

[![PyPI version](https://badge.fury.io/py/evolvishub-data-handler.svg)](https://badge.fury.io/py/evolvishub-data-handler)
[![Python Versions](https://img.shields.io/pypi/pyversions/evolvishub-data-handler.svg)](https://pypi.org/project/evolvishub-data-handler/)
[![License: Commercial](https://img.shields.io/badge/License-Commercial-blue.svg)](LICENSE)
[![Downloads](https://pepy.tech/badge/evolvishub-data-handler)](https://pepy.tech/project/evolvishub-data-handler)
[![CI/CD](https://github.com/evolvishub/evolvishub-data-handler/actions/workflows/ci.yml/badge.svg)](https://github.com/evolvishub/evolvishub-data-handler/actions/workflows/ci.yml)
[![Code Coverage](https://codecov.io/gh/evolvishub/evolvishub-data-handler/branch/main/graph/badge.svg)](https://codecov.io/gh/evolvishub/evolvishub-data-handler)

A powerful and flexible data synchronization framework for Change Data Capture (CDC) operations with advanced scheduling, custom queries, and persistent watermark management.

> **Latest Version: 0.1.2** - Now with Oracle support, cron scheduling, SQLite watermarks, and custom queries!

## 🚀 Features

### **Database & Storage Support**
- **Databases**: PostgreSQL, MySQL, SQLite, Oracle (with TNS support), MongoDB, SQL Server
- **Cloud Storage**: AWS S3, Google Cloud Storage, Azure Blob Storage
- **File Formats**: CSV, JSON, Parquet

### **Advanced Sync Modes**
- **One-time Sync**: Run once and exit
- **Continuous Sync**: Real-time synchronization with configurable intervals
- **Cron Scheduling**: Complex scheduling with timezone support and cron expressions

### **Custom Query Support**
- **Custom SQL Queries**: Complex business logic with parameter substitution (`:last_sync`, `:batch_size`)
- **Simple SELECT**: Framework automatically adds WHERE, ORDER BY, LIMIT clauses
- **Database-specific Syntax**: Native SQL features for each database type

### **Persistent Watermark Storage**
- **SQLite Storage**: Independent watermark persistence across restarts
- **File Storage**: JSON-based watermark storage
- **Database Storage**: Traditional database-based watermarks
- **Error Tracking**: Status monitoring and resume from last successful sync

### **Enterprise Features**
- **Configurable**: YAML and INI configuration files with validation
- **CLI Interface**: Comprehensive command-line tools with logging
- **Extensible**: Optional plugin system for custom data sources and transformations
- **Production Ready**: Error handling, retry logic, and monitoring

## Installation

```bash
# Install from PyPI
pip install evolvishub-data-handler

# Install with development dependencies
pip install evolvishub-data-handler[dev]

# Install with documentation dependencies
pip install evolvishub-data-handler[docs]
```

## Quick Start

### Basic Usage (No Plugins Required)

1. Create a simple configuration file (e.g., `config.yaml`):

```yaml
# Basic configuration - no plugins required
source:
  type: postgresql
  host: localhost
  port: 5432
  database: source_db
  username: source_user
  password: source_password
  table: users
  watermark:
    column: updated_at
    type: timestamp
    initial_value: "2024-01-01 00:00:00"

destination:
  type: postgresql
  host: localhost
  port: 5432
  database: dest_db
  username: dest_user
  password: dest_password
  table: users_sync

sync:
  mode: one_time  # Simple one-time sync
  batch_size: 1000
```

2. Use the library in your code:

```python
from evolvishub_data_handler import CDCHandler

# Initialize the handler
handler = CDCHandler("config.yaml")

# Run one-time sync
handler.sync()

# Or run continuous sync
handler.run_continuous()
```

### Advanced Usage with Optional Plugins

For advanced features like data transformation, monitoring, and custom adapters, you can optionally enable the plugin system:

```yaml
# Advanced configuration with optional plugins
source:
  type: postgresql
  host: localhost
  database: source_db
  username: source_user
  password: source_password
  table: users
  watermark:
    column: updated_at
    type: timestamp
    initial_value: "2024-01-01 00:00:00"

destination:
  type: postgresql
  host: localhost
  database: dest_db
  username: dest_user
  password: dest_password
  table: users_sync

sync:
  mode: continuous
  interval_seconds: 30
  batch_size: 1000

# Optional plugins section - remove this entire section for basic usage
plugins:
  # Optional: Data transformations
  transformers:
    transformers:
      - type: field_mapper
        params:
          mapping:
            user_id: customer_id
            full_name: name
      - type: field_filter
        params:
          exclude: [password, ssn]

  # Optional: Monitoring and validation
  middleware:
    middleware:
      - type: logging
        params:
          level: INFO
      - type: validation
        params:
          rules:
            email: {required: true, type: string}

  # Optional: Alerts and notifications
  hooks:
    hooks:
      - type: slack
        params:
          webhook_url: "https://hooks.slack.com/..."
          channel: "#data-sync"
        events: [error]
```

**Important**: The `plugins` section is completely optional. Remove it entirely for basic synchronization without any plugins.

> 📖 **See Examples**:
> - Basic usage (no plugins): [`examples/basic_usage_no_plugins.py`](examples/basic_usage_no_plugins.py)
> - Advanced usage (with plugins): [`examples/plugin_system_example.py`](examples/plugin_system_example.py)
> - Kafka CDC integration: [`examples/kafka_cdc_example.py`](examples/kafka_cdc_example.py)
> - Event bus streaming: [`examples/event_bus_examples.py`](examples/event_bus_examples.py)

3. Run synchronization using the CLI:

```bash
# Basic one-time sync (works with or without plugins)
evolvishub-cdc run -c config.yaml -m one_time

# Continuous sync (works with or without plugins)
evolvishub-cdc run -c config.yaml -m continuous

# Cron-scheduled sync (works with or without plugins)
evolvishub-cdc run -c config.yaml -m cron

# Override cron expression from command line
evolvishub-cdc run -c config.yaml --cron "0 */4 * * *"

# With custom logging
evolvishub-cdc run -c config.yaml -l DEBUG --log-file sync.log

# Legacy commands (still supported)
evolvishub-cdc sync -c config.yaml
evolvishub-cdc continuous-sync -c config.yaml
```

## 🔥 What's New in v2.1

### **Multi-Source Multi-Destination CDC** 🎯
- **Multiple Mappings**: Configure multiple views and tables to different destinations in one file
- **Multiple Destinations**: Each mapping can target different destination databases/types
- **Independent Watermarks**: Each mapping tracks its own incremental state
- **Parallel Execution**: All mappings run simultaneously with configurable workers
- **Custom Transformations**: Column mapping, exclusions, and custom queries per mapping
- **Individual Monitoring**: Track success/failure of each mapping independently

### **Event Bus Integration** 🚀
- **Apache Kafka**: Industry-standard event streaming with producer/consumer support
- **Apache Pulsar**: Next-generation messaging with multi-tenancy and geo-replication
- **Redis Streams**: Lightweight event streaming with consumer groups and persistence
- **RabbitMQ**: Enterprise messaging with complex routing and exchange patterns
- **Real-time CDC**: Stream database changes to event buses for real-time processing

### **Advanced Sync Modes**
- **Cron Scheduling**: Schedule syncs with complex cron expressions and timezone support
- **Enhanced CLI**: New unified `run` command with mode selection and override options
- **Flexible Timing**: One-time, continuous, or scheduled synchronization

### **Custom Query Support**
- **Parameter Substitution**: Use `:last_sync` and `:batch_size` in custom queries
- **Business Logic**: Implement complex data transformations in SQL
- **Database-Specific**: Leverage native SQL features for each database

### **SQLite Watermark Storage**
- **Persistence**: Watermarks survive application restarts and database maintenance
- **Independence**: No dependency on source/destination database availability
- **Error Tracking**: Monitor sync status and resume from failures

### **Oracle Database Support**
- **Complete Implementation**: Full Oracle adapter with TNS name support
- **Enterprise Ready**: Connection pooling, encoding options, and Oracle-specific features
- **Native SQL**: Support for Oracle's TO_TIMESTAMP, FETCH FIRST, MERGE statements

### **Event Bus & Streaming** 🚀
- **Apache Kafka**: Industry-standard event streaming with producer/consumer support
- **Apache Pulsar**: Next-generation messaging with multi-tenancy and geo-replication
- **Redis Streams**: Lightweight event streaming with persistence and consumer groups
- **RabbitMQ**: Enterprise messaging with complex routing and exchange patterns
- **Real-time CDC**: Stream database changes to event buses for real-time processing
- **Event Sourcing**: Immutable event logs for audit trails and system replay

### **Optional Plugin System** 🔌
- **Completely Optional**: Use basic sync without any plugins - just remove the `plugins` section
- **Zero Dependencies**: Core functionality works without any plugin dependencies
- **Extensible**: Add custom adapters, transformations, and monitoring when needed
- **Configuration-Driven**: Enable plugins through simple YAML configuration
- **Graceful Degradation**: System continues working even if plugins fail
- **No Performance Impact**: Plugins only load when configured

## Sync Modes

### One-Time Sync
Run a single synchronization cycle and exit.

```yaml
sync:
  mode: one_time
  batch_size: 1000
```

### Continuous Sync
Run synchronization continuously at specified intervals.

```yaml
sync:
  mode: continuous
  interval_seconds: 60  # Sync every 60 seconds
  batch_size: 1000
```

### Cron-Scheduled Sync
Run synchronization based on cron expressions with timezone support.

```yaml
sync:
  mode: cron
  cron_expression: "0 */2 * * *"  # Every 2 hours
  timezone: "America/New_York"
  batch_size: 1000
```

**Common Cron Expressions:**
- `"0 9 * * 1-5"` - Every weekday at 9 AM
- `"0 */6 * * *"` - Every 6 hours
- `"30 2 * * 0"` - Every Sunday at 2:30 AM
- `"0 0 1 * *"` - First day of every month at midnight
- `"0 8,12,16 * * *"` - At 8 AM, 12 PM, and 4 PM every day

## Custom Queries

### Using Custom SQL Queries
Define complex data extraction logic with custom SQL queries:

```yaml
source:
  type: postgresql
  # ... connection details ...
  query: >
    SELECT
      id, name, email, updated_at,
      CASE
        WHEN deleted_at IS NOT NULL THEN 'delete'
        WHEN updated_at > :last_sync THEN 'update'
        ELSE 'insert'
      END as operation,
      EXTRACT(EPOCH FROM updated_at) as updated_timestamp
    FROM users
    WHERE (updated_at > :last_sync OR :last_sync IS NULL)
      AND status = 'active'
    ORDER BY updated_at
    LIMIT :batch_size
```

**Available Parameters:**
- `:last_sync` - Last synchronization timestamp
- `:batch_size` - Configured batch size

### Using Simple SELECT Statements
For simpler cases, use the `select` field:

```yaml
source:
  type: postgresql
  # ... connection details ...
  select: "SELECT id, name, email, updated_at FROM users"
  watermark:
    column: updated_at
    type: timestamp
```

The framework automatically adds `WHERE`, `ORDER BY`, and `LIMIT` clauses based on watermark configuration.

## Watermark Storage Options

### Database Storage (Default)
Store watermarks in the source or destination database:

```yaml
sync:
  watermark_table: sync_watermark  # Default behavior
```

### SQLite Storage
Store watermarks in a separate SQLite database for persistence across restarts:

```yaml
sync:
  watermark_storage:
    type: sqlite
    sqlite_path: "/var/lib/evolvishub/watermarks.db"
    table_name: "sync_watermark"
```

**Benefits of SQLite Storage:**
- ✅ Persistent across application restarts
- ✅ Independent of source/destination databases
- ✅ Centralized watermark management
- ✅ Error tracking and status monitoring
- ✅ Resume from last successful sync point

### File Storage
Store watermarks in a JSON file:

```yaml
sync:
  watermark_storage:
    type: file
    file_path: "/var/lib/evolvishub/watermarks.json"
```

## Supported Data Sources

### Databases
- **PostgreSQL**: Full support with advanced features
- **MySQL**: Complete implementation with connection pooling
- **SQL Server**: Native SQL Server adapter
- **Oracle**: Enterprise support with TNS names and connection pooling
- **MongoDB**: Document database synchronization
- **SQLite**: Lightweight database support

### Cloud Storage
- AWS S3
- Google Cloud Storage
- Azure Blob Storage

### File Systems
- CSV files
- JSON files
- Parquet files

## 📋 Configuration Examples

### Oracle Database with TNS
```yaml
source:
  type: oracle
  database: "PROD_DB"  # TNS name
  username: readonly_user
  password: secure_password
  table: ORDERS
  watermark:
    column: ORDER_DATE
    type: timestamp
    initial_value: "2024-01-01 00:00:00"
  # Oracle-specific query
  query: >
    SELECT ORDER_ID, CUSTOMER_ID, TOTAL_AMOUNT, ORDER_DATE
    FROM ORDERS
    WHERE ORDER_DATE > TO_TIMESTAMP(:last_sync, 'YYYY-MM-DD HH24:MI:SS')
    ORDER BY ORDER_DATE
    FETCH FIRST :batch_size ROWS ONLY

sync:
  mode: cron
  cron_expression: "0 */6 * * *"  # Every 6 hours
  timezone: "America/New_York"
  watermark_storage:
    type: sqlite
    sqlite_path: "/var/lib/evolvishub/oracle_watermarks.db"
```

### Advanced PostgreSQL with Custom Logic
```yaml
source:
  type: postgresql
  host: postgres-primary.company.com
  database: production
  username: etl_user
  password: secure_password
  query: >
    SELECT
      u.id, u.name, u.email, u.updated_at,
      p.department, p.role,
      CASE
        WHEN u.deleted_at IS NOT NULL THEN 'delete'
        WHEN u.updated_at > :last_sync THEN 'update'
        ELSE 'insert'
      END as operation,
      EXTRACT(EPOCH FROM u.updated_at) as updated_timestamp
    FROM users u
    LEFT JOIN user_profiles p ON u.id = p.user_id
    WHERE u.updated_at > :last_sync OR :last_sync IS NULL
    ORDER BY u.updated_at
    LIMIT :batch_size

sync:
  mode: continuous
  interval_seconds: 30
  watermark_storage:
    type: sqlite
    sqlite_path: "/opt/evolvishub/watermarks.db"
```

### Multi-Database with File Storage
```yaml
source:
  type: mysql
  host: mysql-server.company.com
  database: sales
  username: readonly_user
  password: secure_password
  select: "SELECT id, customer_name, order_total, created_at FROM sales"
  watermark:
    column: created_at
    type: timestamp

destination:
  type: file
  file_path: "/data/exports/sales_export.json"

sync:
  mode: cron
  cron_expression: "0 2 * * *"  # Daily at 2 AM
  watermark_storage:
    type: file
    file_path: "/var/lib/evolvishub/sales_watermarks.json"
```

## Installation

```bash
pip install evolvishub-data-handler
```

### Optional Dependencies

For specific database and event bus support, install additional packages:

```bash
# Database support
pip install oracledb          # Oracle support
pip install psycopg2-binary   # PostgreSQL support
pip install pymysql           # MySQL support
pip install pymongo           # MongoDB support

# Event bus support
pip install kafka-python      # Apache Kafka support
pip install pulsar-client     # Apache Pulsar support
pip install redis             # Redis Streams support
pip install pika              # RabbitMQ support

# MongoDB support
pip install pymongo

# Cloud storage support
pip install boto3 google-cloud-storage azure-storage-blob
```

## 🖥️ CLI Reference

### Main Commands

```bash
# Unified run command (recommended)
evolvishub-cdc run -c config.yaml [OPTIONS]

# Legacy commands (still supported)
evolvishub-cdc sync -c config.yaml
evolvishub-cdc continuous-sync -c config.yaml
```

### Run Command Options

```bash
# Sync modes
evolvishub-cdc run -c config.yaml -m one_time     # One-time sync
evolvishub-cdc run -c config.yaml -m continuous  # Continuous sync
evolvishub-cdc run -c config.yaml -m cron        # Cron-scheduled sync

# Override cron expression
evolvishub-cdc run -c config.yaml --cron "0 */4 * * *"

# Logging options
evolvishub-cdc run -c config.yaml -l DEBUG                    # Set log level
evolvishub-cdc run -c config.yaml --log-file sync.log         # Log to file
evolvishub-cdc run -c config.yaml -l INFO --log-file app.log  # Both

# Help
evolvishub-cdc --help
evolvishub-cdc run --help
```

### Common Cron Expressions

| Expression | Description |
|------------|-------------|
| `"0 */2 * * *"` | Every 2 hours |
| `"0 9 * * 1-5"` | Weekdays at 9 AM |
| `"30 2 * * 0"` | Sundays at 2:30 AM |
| `"0 0 1 * *"` | First day of month |
| `"*/15 * * * *"` | Every 15 minutes |

## Development

### Setup

1. Clone the repository:
```bash
git clone https://github.com/evolvishub/evolvishub-data-handler.git
cd evolvishub-data-handler
```

2. Create a virtual environment:
```bash
make venv
```

3. Install development dependencies:
```bash
make install
```

4. Install pre-commit hooks:
```bash
make install-hooks
```

### Testing

Run the test suite:
```bash
make test
```

### Code Quality

Format code:
```bash
make format
```

Run linters:
```bash
make lint
```

### Building

Build the package:
```bash
make build
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📄 License

This project is licensed under a **Commercial License with Open Source Exception**.

### 🆓 **Free for Open Source**
- **FREE** when used with open source frameworks (Apache Kafka, PostgreSQL, MongoDB, Redis, etc.)
- **FREE** for open source projects with OSI-approved licenses
- **FREE** for educational and research purposes

### 💼 **Commercial License Required**
- For use in proprietary software applications
- For commercial products or services
- For enterprise environments
- For distribution as part of commercial offerings

**Contact**: licensing@evolvis.ai for commercial licensing

See the [LICENSE](LICENSE) file for complete terms and conditions.

## Support

- Documentation: [https://evolvishub.github.io/evolvishub-data-handler](https://evolvishub.github.io/evolvishub-data-handler)
- Issues: [https://github.com/evolvishub/evolvishub-data-handler/issues](https://github.com/evolvishub/evolvishub-data-handler/issues)
- Email: info@evolvishub.com

# EvolvisHub Data Handler Adapter

A powerful and flexible data handling adapter for Evolvis AI's data processing pipeline. This tool provides seamless integration with various database systems and implements Change Data Capture (CDC) functionality.

## 🔌 When to Use Plugins

### **Use Basic Configuration When:**
- ✅ Simple database-to-database synchronization
- ✅ Standard data types and field names
- ✅ No custom business logic required
- ✅ Basic monitoring through logs is sufficient
- ✅ Getting started quickly

### **Add Plugins When You Need:**
- 🔄 **Data Transformation**: Field mapping, type conversion, data cleansing
- 📊 **Advanced Monitoring**: Real-time metrics, Slack alerts, webhooks
- 🔍 **Data Validation**: Quality checks, business rule validation
- 🔗 **Custom Adapters**: Redis, Elasticsearch, APIs, custom databases
- 📈 **Performance Monitoring**: Detailed metrics and performance tracking
- 🚨 **Production Alerting**: Error notifications, status updates

### **Plugin Configuration Examples:**

**Minimal (No Plugins)**:
```yaml
source: {type: postgresql, host: localhost, database: source_db, ...}
destination: {type: postgresql, host: localhost, database: dest_db, ...}
sync: {mode: one_time, batch_size: 1000}
# No plugins section = basic functionality only
```

**With Plugins**:
```yaml
source: {...}
destination: {...}
sync: {...}
plugins:  # Optional section
  transformers: [...]  # Data transformation
  middleware: [...]    # Monitoring and validation
  hooks: [...]         # Alerts and notifications
```

## 🎯 Multi-Source Multi-Destination Configuration

### **Multiple Views to Multiple Destinations**

Perfect for syncing multiple views and tables to different destinations:

```yaml
# Multi-Source Multi-Destination CDC Configuration
name: multi_source_sync
description: Sync multiple views and tables to different destinations

# Global settings (applied to all mappings unless overridden)
global_sync:
  mode: continuous
  interval_seconds: 300
  batch_size: 1000

# Individual source-destination mappings
mappings:
  # View 1: Customer Demographics → PostgreSQL Data Warehouse
  - name: customer_demographics
    source:
      type: postgresql
      host: source-db.company.com
      database: customer_analytics
      table: vw_customer_demographics
    destination:
      type: postgresql
      host: warehouse-db.company.com
      database: data_warehouse
      table: dim_customer_demographics
    watermark:
      column: last_updated
      type: timestamp
    column_mapping:
      customer_id: customer_key
      birth_date: date_of_birth

  # View 2: Purchase Behavior → Kafka Event Stream
  - name: purchase_behavior
    source:
      type: postgresql
      host: source-db.company.com
      database: customer_analytics
      table: vw_customer_purchase_behavior
    destination:
      type: kafka
      host: kafka-cluster.company.com
      port: 9092
      database: events_cluster
      table: purchase_events
    watermark:
      column: analysis_date
      type: timestamp
    custom_query: |
      SELECT customer_id, total_purchases, avg_order_value
      FROM vw_customer_purchase_behavior
      WHERE analysis_date > %(last_sync)s

  # View 3: Geographic Distribution → MongoDB Document Store
  - name: geographic_distribution
    source:
      type: postgresql
      host: source-db.company.com
      database: customer_analytics
      table: vw_customer_geography
    destination:
      type: mongodb
      host: mongo-cluster.company.com
      port: 27017
      database: analytics
      table: customer_geography
    sync:
      interval_seconds: 600  # Less frequent

  # View 4: Engagement Metrics → Redis Streams
  - name: engagement_metrics
    source:
      type: postgresql
      host: source-db.company.com
      database: customer_analytics
      table: vw_customer_engagement
    destination:
      type: redis_streams
      host: redis-cluster.company.com
      port: 6379
      database: 0
      table: engagement_stream
    column_mapping:
      email_opens: email_open_count
      website_visits: web_visit_count

  # View 5: Lifetime Value → S3 Data Lake
  - name: lifetime_value
    source:
      type: postgresql
      host: source-db.company.com
      database: customer_analytics
      table: vw_customer_ltv
    destination:
      type: s3
      host: s3.amazonaws.com
      database: company-data-lake
      table: customer_ltv/year=2024/
    sync:
      interval_seconds: 1800  # Least frequent

# Execution settings
parallel_execution: true
max_workers: 3
stop_on_error: false
```

### **Multi-Source CLI Commands**

```bash
# Run all mappings simultaneously
evolvishub-cdc run-multi -c multi_source_sync.yaml

# Run specific mapping only
evolvishub-cdc run-multi -c multi_source_sync.yaml --mapping customer_demographics

# Monitor all mappings
evolvishub-cdc status -c multi_source_sync.yaml

# Run in sequential mode
evolvishub-cdc run-multi -c multi_source_sync.yaml --sequential
```

### **Independent Watermark Tracking**

Each mapping maintains its own watermark state:

```
./watermarks/
├── customer_demographics.db     # Tracks: last_updated
├── purchase_behavior.db         # Tracks: analysis_date
├── geographic_distribution.db   # Tracks: updated_at
├── engagement_metrics.db        # Tracks: metric_date
└── lifetime_value.db           # Tracks: calculation_date
```

**Benefits:**
- ✅ **Multiple Destinations**: Each mapping can target different destination types
- ✅ **Independent Progress**: Each mapping syncs at its own pace
- ✅ **Parallel Efficiency**: All mappings run simultaneously
- ✅ **Incremental Only**: Only new/changed data per mapping
- ✅ **Error Isolation**: One mapping failure doesn't stop others
- ✅ **Custom Scheduling**: Different intervals per mapping

## 🚀 Event Bus Configuration Examples

### **Apache Kafka Streaming**
```yaml
# Database to Kafka real-time streaming
source:
  type: postgresql
  host: localhost
  database: ecommerce
  table: orders
  watermark:
    column: updated_at
    type: timestamp

destination:
  type: kafka
  host: localhost
  port: 9092
  database: kafka_cluster
  table: order_events
  key_field: order_id
  compression_type: gzip
  security_protocol: SASL_SSL
  sasl_mechanism: PLAIN
  sasl_username: user
  sasl_password: password

sync:
  mode: continuous
  interval_seconds: 10
```

### **Apache Pulsar Messaging**
```yaml
# Kafka to Pulsar bridge
source:
  type: kafka
  host: localhost
  port: 9092
  database: kafka_cluster
  table: order_events
  group_id: pulsar_bridge

destination:
  type: pulsar
  host: localhost
  port: 6650
  database: public/default
  table: persistent://public/default/processed_orders
  subscription_name: cdc_subscription
  compression_type: LZ4
  key_field: order_id

sync:
  mode: continuous
  interval_seconds: 5
```

### **Redis Streams**
```yaml
# Lightweight event streaming
source:
  type: postgresql
  host: localhost
  database: analytics
  table: user_events

destination:
  type: redis_streams
  host: localhost
  port: 6379
  database: 0
  table: user_events_stream
  consumer_group: analytics_group
  max_length: 10000
  key_field: user_id

sync:
  mode: continuous
  interval_seconds: 2
```

### **RabbitMQ Enterprise Messaging**
```yaml
# Complex routing patterns
source:
  type: redis_streams
  host: localhost
  port: 6379
  table: user_events_stream

destination:
  type: rabbitmq
  host: localhost
  port: 5672
  database: /
  table: processed_events
  username: guest
  password: guest
  exchange: events_exchange
  exchange_type: topic
  routing_key: events.processed
  queue_durable: true

sync:
  mode: continuous
  interval_seconds: 1
```

## 🔧 Troubleshooting

### Common Issues

**Oracle Connection Errors**
```bash
# Install Oracle client
pip install oracledb

# For TNS name issues, check tnsnames.ora
export TNS_ADMIN=/path/to/tns/admin
```

**Cron Expression Validation**
```bash
# Test cron expressions online: https://crontab.guru/
# Common mistake: Using 6 fields instead of 5
# Correct: "0 */2 * * *" (every 2 hours)
# Wrong: "0 0 */2 * * *" (6 fields)
```

**Watermark Storage Issues**
```bash
# Check SQLite file permissions
ls -la /var/lib/evolvishub/watermarks.db

# Verify directory exists and is writable
mkdir -p /var/lib/evolvishub
chmod 755 /var/lib/evolvishub
```

**Configuration Validation**
```python
# Test configuration loading
from evolvishub_data_handler.config_loader import load_config
config = load_config("config.yaml")
print("Configuration is valid!")
```

### Getting Help

- 📖 **Documentation**: Check the `examples/` directory for configuration samples
- 🐛 **Issues**: Report bugs on GitHub Issues
- 💬 **Discussions**: Ask questions in GitHub Discussions
- 📧 **Support**: Contact [a.maxhuni@evolvis.ai](mailto:a.maxhuni@evolvis.ai)

## About Evolvis AI

[Evolvis AI](https://evolvis.ai) is a leading provider of AI solutions that helps businesses unlock their data potential. We specialize in:

- Data analysis and decision-making
- Machine learning implementation
- Process optimization
- Predictive maintenance
- Natural language processing
- Custom AI solutions

Our mission is to make artificial intelligence accessible to businesses of all sizes, enabling them to compete in today's data-driven environment. As Forbes highlights: "Organizations that strategically adopt AI will have a significant competitive advantage in today's data-driven market."

## Author

**Alban Maxhuni, PhD**  
Email: [a.maxhuni@evolvis.ai](mailto:a.maxhuni@evolvis.ai)