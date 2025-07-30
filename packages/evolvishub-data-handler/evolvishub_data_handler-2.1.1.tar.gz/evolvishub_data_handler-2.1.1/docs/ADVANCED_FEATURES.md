# Advanced Features Guide

This guide covers the advanced features of the Evolvishub Data Handler, including custom queries, sync modes, and cron scheduling.

## Table of Contents

1. [Custom Queries](#custom-queries)
2. [Sync Modes](#sync-modes)
3. [Cron Scheduling](#cron-scheduling)
4. [Watermark Storage](#watermark-storage)
5. [Configuration Examples](#configuration-examples)
6. [CLI Usage](#cli-usage)
7. [Best Practices](#best-practices)

## Custom Queries

### Using Custom SQL Queries

You can define complex data extraction logic using custom SQL queries in your source configuration:

```yaml
source:
  type: postgresql
  host: localhost
  port: 5432
  database: source_db
  username: user
  password: password
  watermark:
    column: updated_at
    type: timestamp
    initial_value: "2024-01-01 00:00:00"
  query: >
    SELECT 
      u.id,
      u.name,
      u.email,
      u.updated_at,
      CASE
        WHEN u.deleted_at IS NOT NULL THEN 'delete'
        WHEN u.updated_at > :last_sync THEN 'update'
        ELSE 'insert'
      END as operation,
      EXTRACT(EPOCH FROM u.updated_at) as updated_timestamp,
      p.department
    FROM users u
    LEFT JOIN user_profiles p ON u.id = p.user_id
    WHERE (u.updated_at > :last_sync OR :last_sync IS NULL)
      AND u.status = 'active'
    ORDER BY u.updated_at
    LIMIT :batch_size
```

**Available Parameters:**
- `:last_sync` - The last synchronization timestamp
- `:batch_size` - The configured batch size

### Using Simple SELECT Statements

For simpler cases, use the `select` field. The framework automatically adds WHERE, ORDER BY, and LIMIT clauses:

```yaml
source:
  type: postgresql
  # ... connection details ...
  select: "SELECT id, name, email, updated_at FROM users"
  watermark:
    column: updated_at
    type: timestamp
```

This automatically becomes:
```sql
SELECT id, name, email, updated_at FROM users
WHERE updated_at > :last_sync
ORDER BY updated_at
LIMIT :batch_size
```

## Sync Modes

### One-Time Sync

Run a single synchronization cycle and exit:

```yaml
sync:
  mode: one_time
  batch_size: 1000
```

### Continuous Sync

Run synchronization continuously at specified intervals:

```yaml
sync:
  mode: continuous
  interval_seconds: 60  # Sync every 60 seconds
  batch_size: 1000
```

### Cron-Scheduled Sync

Run synchronization based on cron expressions:

```yaml
sync:
  mode: cron
  cron_expression: "0 */2 * * *"  # Every 2 hours
  timezone: "America/New_York"
  batch_size: 1000
```

## Cron Scheduling

### Cron Expression Examples

| Expression | Description |
|------------|-------------|
| `"0 9 * * 1-5"` | Every weekday at 9 AM |
| `"0 */6 * * *"` | Every 6 hours |
| `"30 2 * * 0"` | Every Sunday at 2:30 AM |
| `"0 0 1 * *"` | First day of every month at midnight |
| `"0 8,12,16 * * *"` | At 8 AM, 12 PM, and 4 PM every day |
| `"*/15 * * * *"` | Every 15 minutes |
| `"0 0 * * 6"` | Every Saturday at midnight |

### Timezone Support

Specify timezone for cron scheduling:

```yaml
sync:
  mode: cron
  cron_expression: "0 9 * * 1-5"
  timezone: "America/New_York"  # Eastern Time
  # Other options: "UTC", "Europe/London", "Asia/Tokyo", etc.
```

## Watermark Storage

The framework supports multiple watermark storage options to persist sync progress across application restarts.

### Database Storage (Default)

By default, watermarks are stored in the source or destination database:

```yaml
sync:
  watermark_table: sync_watermark  # Table name in database
```

### SQLite Storage

Store watermarks in a separate SQLite database for better isolation and persistence:

```yaml
sync:
  watermark_storage:
    type: sqlite
    sqlite_path: "/var/lib/evolvishub/watermarks.db"
    table_name: "sync_watermark"
```

**Benefits of SQLite Storage:**
- **Persistence**: Survives application restarts and database maintenance
- **Independence**: Not tied to source/destination database availability
- **Centralization**: Single location for all watermark data
- **Error Tracking**: Stores sync status and error messages
- **Resume Capability**: Automatically resume from last successful sync point

### File Storage

Store watermarks in a JSON file:

```yaml
sync:
  watermark_storage:
    type: file
    file_path: "/var/lib/evolvishub/watermarks.json"
```

### Watermark Storage Schema

The SQLite watermark storage creates the following schema:

```sql
CREATE TABLE sync_watermark (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    table_name TEXT NOT NULL,
    watermark_column TEXT NOT NULL,
    watermark_value TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'success',
    error_message TEXT,
    last_sync_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(table_name, watermark_column)
);
```

### Resume from Last Watermark

When using SQLite or file storage, the system automatically resumes from the last watermark:

1. **First Run**: Uses `initial_value` from watermark configuration
2. **Subsequent Runs**: Resumes from last successful watermark
3. **After Errors**: Can retry from last known good watermark
4. **Status Tracking**: Monitors sync success/failure status

## Configuration Examples

### Advanced PostgreSQL to PostgreSQL Sync

```yaml
source:
  type: postgresql
  host: source-db.example.com
  port: 5432
  database: production
  username: readonly_user
  password: secure_password
  watermark:
    column: updated_at
    type: timestamp
    initial_value: "2024-01-01 00:00:00"
  query: >
    SELECT 
      o.id,
      o.customer_id,
      o.total_amount,
      o.status,
      o.created_at,
      o.updated_at,
      c.customer_name,
      c.customer_email,
      CASE 
        WHEN o.total_amount > 1000 THEN 'high_value'
        WHEN o.total_amount > 100 THEN 'medium_value'
        ELSE 'low_value'
      END as order_tier
    FROM orders o
    JOIN customers c ON o.customer_id = c.id
    WHERE o.updated_at > :last_sync OR :last_sync IS NULL
    ORDER BY o.updated_at
    LIMIT :batch_size

destination:
  type: postgresql
  host: analytics-db.example.com
  port: 5432
  database: analytics
  username: writer_user
  password: secure_password
  table: enriched_orders

sync:
  mode: cron
  cron_expression: "0 */4 * * *"  # Every 4 hours
  timezone: "UTC"
  batch_size: 5000
  watermark_table: sync_watermark
  error_retry_attempts: 5
  error_retry_delay: 10
```

### Oracle Database Sync

```yaml
source:
  type: oracle
  host: oracle-server.example.com
  port: 1521
  database: ORCL  # Service name
  username: readonly_user
  password: secure_password
  watermark:
    column: LAST_MODIFIED
    type: timestamp
    initial_value: "2024-01-01 00:00:00"
  # Oracle-specific query syntax
  query: >
    SELECT
      ID, NAME, EMAIL, LAST_MODIFIED,
      CASE
        WHEN DELETED_FLAG = 'Y' THEN 'delete'
        WHEN LAST_MODIFIED > TO_TIMESTAMP(:last_sync, 'YYYY-MM-DD HH24:MI:SS') THEN 'update'
        ELSE 'insert'
      END as OPERATION
    FROM USERS
    WHERE LAST_MODIFIED > TO_TIMESTAMP(:last_sync, 'YYYY-MM-DD HH24:MI:SS')
       OR :last_sync IS NULL
    ORDER BY LAST_MODIFIED
    FETCH FIRST :batch_size ROWS ONLY

destination:
  type: oracle
  database: ANALYTICS_TNS  # TNS name
  username: analytics_user
  password: analytics_password
  table: user_analytics

sync:
  mode: cron
  cron_expression: "0 */4 * * *"  # Every 4 hours
  timezone: "UTC"
  batch_size: 1000
  watermark_storage:
    type: sqlite
    sqlite_path: "/var/lib/evolvishub/oracle_watermarks.db"
    table_name: "sync_watermark"

# Oracle-specific connection parameters
additional_params:
  encoding: "UTF-8"
  nencoding: "UTF-8"
  threaded: true
```

### File to Database Sync

```yaml
source:
  type: file
  file_path: "/data/exports/daily_sales.csv"
  watermark:
    column: updated_at
    type: timestamp
    initial_value: "2024-01-01T00:00:00Z"

destination:
  type: postgresql
  host: localhost
  port: 5432
  database: analytics
  username: user
  password: password
  table: daily_sales

sync:
  mode: cron
  cron_expression: "0 6 * * *"  # Daily at 6 AM
  timezone: "America/New_York"
  batch_size: 10000
```

### Multi-Table Sync with SQLite Watermarks

```yaml
source:
  type: postgresql
  host: source-db.example.com
  port: 5432
  database: production
  username: readonly_user
  password: secure_password

destination:
  type: postgresql
  host: analytics-db.example.com
  port: 5432
  database: analytics
  username: writer_user
  password: secure_password

sync:
  mode: cron
  cron_expression: "0 */6 * * *"  # Every 6 hours
  timezone: "UTC"
  batch_size: 5000
  # Centralized SQLite watermark storage
  watermark_storage:
    type: sqlite
    sqlite_path: "/var/lib/evolvishub/watermarks.db"
    table_name: "sync_watermark"
  error_retry_attempts: 5
  error_retry_delay: 10

# Multiple tables with individual watermark tracking
tables:
  - users
  - orders
  - products
  - transactions

# Each table can have its own watermark configuration
# The SQLite storage will track them separately
```

## CLI Usage

### Basic Commands

```bash
# One-time sync
evolvishub-cdc run -c config.yaml -m one_time

# Continuous sync
evolvishub-cdc run -c config.yaml -m continuous

# Cron sync
evolvishub-cdc run -c config.yaml -m cron

# Override cron expression
evolvishub-cdc run -c config.yaml --cron "0 */2 * * *"
```

### Advanced Options

```bash
# Custom logging level
evolvishub-cdc run -c config.yaml -l DEBUG

# Log to file
evolvishub-cdc run -c config.yaml --log-file /var/log/sync.log

# Combine options
evolvishub-cdc run -c config.yaml -m cron --cron "0 9 * * 1-5" -l INFO --log-file sync.log
```

### Legacy Commands

```bash
# Still supported for backward compatibility
evolvishub-cdc sync -c config.yaml
evolvishub-cdc continuous-sync -c config.yaml
```

## Best Practices

### Query Design

1. **Use Indexes**: Ensure your watermark column is indexed for performance
2. **Limit Data**: Always use the `:batch_size` parameter to limit data volume
3. **Filter Early**: Apply WHERE clauses to reduce data transfer
4. **Avoid SELECT ***: Specify only needed columns

### Scheduling

1. **Consider Load**: Schedule heavy syncs during off-peak hours
2. **Use Appropriate Intervals**: Don't sync more frequently than necessary
3. **Monitor Resources**: Watch CPU, memory, and network usage
4. **Plan for Failures**: Use retry settings appropriately

### Configuration

1. **Use Environment Variables**: Store sensitive data like passwords in environment variables
2. **Version Control**: Keep configuration files in version control
3. **Test Configurations**: Validate configurations before production use
4. **Document Changes**: Comment complex queries and scheduling decisions

### Error Handling

```yaml
sync:
  error_retry_attempts: 5
  error_retry_delay: 10  # seconds
  # Exponential backoff: 10s, 20s, 40s, 80s, 160s
```

### Security

1. **Use Read-Only Users**: Source connections should use read-only database users
2. **Network Security**: Use SSL/TLS for database connections
3. **Credential Management**: Use secure credential storage
4. **Access Control**: Limit network access between source and destination

## Troubleshooting

### Common Issues

1. **Invalid Cron Expression**: Use online cron validators to test expressions
2. **Timezone Issues**: Ensure timezone strings are valid (use `pytz.all_timezones`)
3. **Query Syntax**: Test custom queries directly in your database client
4. **Connection Issues**: Verify network connectivity and credentials

### Debugging

```bash
# Enable debug logging
evolvishub-cdc run -c config.yaml -l DEBUG --log-file debug.log

# Check configuration validation
python -c "from evolvishub_data_handler.config_loader import load_config; print(load_config('config.yaml'))"
```
