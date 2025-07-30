# 🔄 Multi-Source Multi-Destination CDC

This document explains how to configure and use the multi-source, multi-destination CDC functionality in the Evolvishub Data Handler.

## 🎯 Overview

The multi-CDC feature allows you to:
- **Configure multiple source-destination pairs** in a single configuration file
- **Sync 5+ views to different destination tables** as requested
- **Execute mappings in parallel or sequential mode**
- **Apply custom transformations** per mapping (column mapping, exclusions, custom queries)
- **Monitor and manage** each mapping independently
- **Stream to multiple event buses** simultaneously

## 📋 Configuration Structure

### Basic Multi-CDC Configuration

```yaml
name: customer_analytics_sync
description: Sync customer analytics views to data warehouse

# Global settings (applied to all mappings unless overridden)
global_sync:
  mode: continuous
  interval_seconds: 300
  batch_size: 1000

# Individual source-destination mappings
mappings:
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

  - name: purchase_behavior
    source:
      type: postgresql
      host: source-db.company.com
      database: customer_analytics
      table: vw_customer_purchase_behavior
    destination:
      type: postgresql
      host: warehouse-db.company.com
      database: data_warehouse
      table: fact_customer_behavior
    custom_query: |
      SELECT customer_id, total_purchases, avg_order_value
      FROM vw_customer_purchase_behavior 
      WHERE analysis_date > %(last_sync)s

# Execution settings
parallel_execution: true
max_workers: 3
stop_on_error: false
```

## 🔧 Advanced Features

### 1. Column Mapping

Transform column names between source and destination:

```yaml
mappings:
  - name: customer_demographics
    source: {...}
    destination: {...}
    column_mapping:
      customer_id: customer_key
      birth_date: date_of_birth
      registration_date: customer_since
```

### 2. Column Exclusion

Exclude sensitive or unnecessary columns:

```yaml
mappings:
  - name: customer_data
    source: {...}
    destination: {...}
    exclude_columns:
      - internal_notes
      - temp_field
      - ssn
```

### 3. Custom Queries

Use complex SQL for data extraction:

```yaml
mappings:
  - name: customer_ltv
    source: {...}
    destination: {...}
    custom_query: |
      SELECT 
        customer_id,
        current_ltv,
        predicted_ltv,
        calculation_date
      FROM vw_customer_ltv 
      WHERE calculation_date > %(last_sync)s
        AND model_version = 'v2.1'
      ORDER BY calculation_date
```

### 4. Per-Mapping Sync Settings

Override global settings for specific mappings:

```yaml
mappings:
  - name: high_frequency_data
    source: {...}
    destination: {...}
    sync:
      mode: continuous
      interval_seconds: 60  # More frequent than global
      batch_size: 500

  - name: low_frequency_data
    source: {...}
    destination: {...}
    sync:
      mode: continuous
      interval_seconds: 1800  # Less frequent
      batch_size: 200
```

## 🚀 Usage Examples

### Customer Views Scenario (Your Use Case)

```yaml
name: customer_analytics_sync
description: Sync 5 customer views to different destination tables

mappings:
  # View 1: Customer Demographics
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

  # View 2: Purchase Behavior
  - name: purchase_behavior
    source:
      type: postgresql
      host: source-db.company.com
      database: customer_analytics
      table: vw_customer_purchase_behavior
    destination:
      type: postgresql
      host: warehouse-db.company.com
      database: data_warehouse
      table: fact_customer_behavior

  # View 3: Geographic Distribution
  - name: geographic_distribution
    source:
      type: postgresql
      host: source-db.company.com
      database: customer_analytics
      table: vw_customer_geography
    destination:
      type: postgresql
      host: warehouse-db.company.com
      database: data_warehouse
      table: dim_customer_geography

  # View 4: Engagement Metrics
  - name: engagement_metrics
    source:
      type: postgresql
      host: source-db.company.com
      database: customer_analytics
      table: vw_customer_engagement
    destination:
      type: postgresql
      host: warehouse-db.company.com
      database: data_warehouse
      table: fact_customer_engagement

  # View 5: Lifetime Value
  - name: lifetime_value
    source:
      type: postgresql
      host: source-db.company.com
      database: customer_analytics
      table: vw_customer_ltv
    destination:
      type: postgresql
      host: warehouse-db.company.com
      database: data_warehouse
      table: fact_customer_ltv

parallel_execution: true
max_workers: 3
```

### Event Bus Multi-Destination

```yaml
name: ecommerce_event_streaming
description: Stream to multiple event buses

mappings:
  # Orders to Kafka
  - name: orders_to_kafka
    source:
      type: postgresql
      host: localhost
      database: ecommerce
      table: orders
    destination:
      type: kafka
      host: localhost
      port: 9092
      database: kafka_cluster
      table: order_events

  # Customers to Pulsar
  - name: customers_to_pulsar
    source:
      type: postgresql
      host: localhost
      database: ecommerce
      table: customers
    destination:
      type: pulsar
      host: localhost
      port: 6650
      database: public/default
      table: persistent://public/default/customer_events

  # Products to Redis Streams
  - name: products_to_redis
    source:
      type: postgresql
      host: localhost
      database: ecommerce
      table: products
    destination:
      type: redis_streams
      host: localhost
      port: 6379
      database: 0
      table: product_updates
```

## 💻 CLI Usage

### Run Multi-CDC Configuration

```bash
# Run all mappings
evolvishub-cdc run-multi -c multi_customer_views.yaml

# Run specific mapping only
evolvishub-cdc run-multi -c multi_customer_views.yaml --mapping customer_demographics

# Run in sequential mode (override config)
evolvishub-cdc run-multi -c multi_customer_views.yaml --sequential

# Run with custom worker count
evolvishub-cdc run-multi -c multi_customer_views.yaml --workers 5
```

### Monitor Status

```bash
# Show status in table format
evolvishub-cdc status -c multi_customer_views.yaml

# Show status in JSON format
evolvishub-cdc status -c multi_customer_views.yaml --format json

# Show status in YAML format
evolvishub-cdc status -c multi_customer_views.yaml --format yaml
```

### Run Individual Mapping

```bash
# Run a single mapping
evolvishub-cdc run-mapping -c multi_customer_views.yaml --mapping customer_demographics
```

## 🔍 Monitoring & Management

### Execution Summary

```python
from evolvishub_data_handler.multi_cdc_handler import MultiCDCHandler
from evolvishub_data_handler.config import MultiCDCConfig

# Load configuration
with open('multi_customer_views.yaml') as f:
    config_dict = yaml.safe_load(f)
config = MultiCDCConfig(**config_dict)

# Create handler
handler = MultiCDCHandler(config)

# Get execution summary
summary = handler.get_summary()
print(f"Total mappings: {summary['total_mappings']}")
print(f"Successful executions: {summary['successful_executions']}")
print(f"Failed executions: {summary['failed_executions']}")
print(f"Records processed: {summary['total_records_processed']}")
```

### Mapping Status

```python
# Get detailed status for each mapping
status_list = handler.get_mapping_status()

for mapping_status in status_list:
    print(f"Mapping: {mapping_status['name']}")
    print(f"  Enabled: {mapping_status['enabled']}")
    print(f"  Executions: {mapping_status['total_executions']}")
    
    if mapping_status['last_execution']:
        last = mapping_status['last_execution']
        print(f"  Last run: {last['success']} - {last['records_processed']} records")
```

## ⚡ Performance & Scalability

### Parallel Execution

- **Enabled by default**: `parallel_execution: true`
- **Configurable workers**: `max_workers: 3` (adjust based on resources)
- **Independent execution**: Each mapping runs independently
- **Resource isolation**: Separate connections per mapping

### Error Handling

- **Continue on error**: `stop_on_error: false` (default)
- **Stop on error**: `stop_on_error: true` (halt all if one fails)
- **Individual tracking**: Each mapping's success/failure tracked separately
- **Retry logic**: Built-in retry mechanisms per adapter

### Optimization Tips

1. **Batch sizes**: Adjust per mapping based on data volume
2. **Sync intervals**: More frequent for critical data, less for historical
3. **Worker count**: Balance between parallelism and resource usage
4. **Custom queries**: Use efficient SQL with proper indexing
5. **Watermarks**: Ensure proper indexing on watermark columns

## 🎯 Benefits

### For Your Customer Views Use Case

✅ **Single Configuration**: All 5 views in one YAML file  
✅ **Independent Scheduling**: Different sync frequencies per view  
✅ **Parallel Processing**: All views sync simultaneously  
✅ **Custom Transformations**: Column mapping and filtering per view  
✅ **Monitoring**: Track each view's sync status independently  
✅ **Error Isolation**: One view failure doesn't stop others  
✅ **Scalable**: Easy to add more views or change destinations  

### Production Ready

✅ **Comprehensive Logging**: Detailed logs per mapping  
✅ **Metrics & Monitoring**: Built-in performance tracking  
✅ **Error Recovery**: Automatic retry and error handling  
✅ **Resource Management**: Configurable parallelism and batching  
✅ **Flexible Deployment**: CLI, programmatic, or scheduled execution  

## 🔄 Migration from Single CDC

Existing single CDC configurations remain fully compatible. To migrate:

1. **Wrap existing config** in a mapping:
   ```yaml
   # Old single config
   source: {...}
   destination: {...}
   
   # New multi config
   mappings:
     - name: existing_sync
       source: {...}
       destination: {...}
   ```

2. **Add more mappings** as needed
3. **Configure execution settings**
4. **Update CLI commands** to use `run-multi`

The multi-CDC system is designed to handle your exact use case of syncing multiple customer views to different destination tables efficiently and reliably! 🚀
