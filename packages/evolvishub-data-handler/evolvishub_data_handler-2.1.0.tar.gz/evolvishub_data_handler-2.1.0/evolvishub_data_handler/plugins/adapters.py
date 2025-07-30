"""
Adapter plugins for dynamic data source registration.
"""

from typing import Any, Dict, List, Optional, Type
from ..adapters.base import BaseAdapter
from ..config import DatabaseConfig, DatabaseType
from .base import BasePlugin, PluginMetadata, PluginType
from loguru import logger


class AdapterPlugin(BasePlugin):
    """Plugin for registering new adapter types."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.adapter_class: Optional[Type[BaseAdapter]] = None
        self.database_type: Optional[DatabaseType] = None
    
    @property
    def metadata(self) -> PluginMetadata:
        """Return adapter plugin metadata."""
        return PluginMetadata(
            name=self.__class__.__name__,
            version="1.0.0",
            description="Dynamic adapter registration plugin",
            author="Evolvishub",
            plugin_type=PluginType.ADAPTER
        )
    
    def register_adapter(self, database_type: DatabaseType, adapter_class: Type[BaseAdapter]) -> None:
        """Register a new adapter type."""
        if not issubclass(adapter_class, BaseAdapter):
            raise ValueError(f"Adapter must inherit from BaseAdapter: {adapter_class}")
        
        self.adapter_class = adapter_class
        self.database_type = database_type
        
        # Register with the factory
        from ..adapters.factory import AdapterFactory
        AdapterFactory.register_adapter(database_type, adapter_class)
        
        logger.info(f"Registered adapter: {database_type.value} -> {adapter_class.__name__}")
    
    def initialize(self) -> None:
        """Initialize the adapter plugin."""
        if self.config.get('auto_register', True):
            self._auto_register_adapters()
    
    def cleanup(self) -> None:
        """Cleanup adapter plugin."""
        if self.database_type and self.adapter_class:
            from ..adapters.factory import AdapterFactory
            AdapterFactory.unregister_adapter(self.database_type)
    
    def _auto_register_adapters(self) -> None:
        """Auto-register adapters from configuration."""
        adapters_config = self.config.get('adapters', {})
        
        for db_type_str, adapter_config in adapters_config.items():
            try:
                # Convert string to DatabaseType enum
                db_type = DatabaseType(db_type_str)
                
                # Import adapter class
                module_path = adapter_config['module']
                class_name = adapter_config['class']
                
                module = __import__(module_path, fromlist=[class_name])
                adapter_class = getattr(module, class_name)
                
                self.register_adapter(db_type, adapter_class)
                
            except Exception as e:
                logger.error(f"Failed to auto-register adapter {db_type_str}: {e}")


class RedisAdapter(BaseAdapter):
    """Example Redis adapter implementation."""
    
    def __init__(self, config: DatabaseConfig):
        super().__init__(config)
        self.redis_client = None
    
    def connect(self) -> None:
        """Connect to Redis."""
        try:
            import redis
            self.redis_client = redis.Redis(
                host=self.config.host,
                port=self.config.port or 6379,
                password=self.config.password,
                decode_responses=True
            )
            # Test connection
            self.redis_client.ping()
        except ImportError:
            raise ImportError("redis package is required for Redis connectivity. Install it with: pip install redis")
        except Exception as e:
            raise ConnectionError(f"Failed to connect to Redis: {e}")
    
    def disconnect(self) -> None:
        """Disconnect from Redis."""
        if self.redis_client:
            self.redis_client.close()
            self.redis_client = None
    
    def execute_query(self, query: str, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Execute Redis query (scan keys)."""
        if not self.redis_client:
            raise RuntimeError("Redis connection not established")
        
        # Simple key scanning for demonstration
        pattern = params.get('pattern', '*') if params else '*'
        keys = self.redis_client.scan_iter(match=pattern)
        
        results = []
        for key in keys:
            value = self.redis_client.get(key)
            results.append({
                'key': key,
                'value': value,
                'type': self.redis_client.type(key)
            })
        
        return results
    
    def insert_data(self, table: str, data: List[Dict[str, Any]]) -> None:
        """Insert data into Redis."""
        if not self.redis_client:
            raise RuntimeError("Redis connection not established")
        
        for record in data:
            key = record.get('key') or f"{table}:{record.get('id', 'unknown')}"
            value = record.get('value', str(record))
            self.redis_client.set(key, value)
    
    def update_data(self, table: str, data: List[Dict[str, Any]], key_columns: List[str]) -> None:
        """Update data in Redis."""
        # For Redis, update is the same as insert
        self.insert_data(table, data)
    
    def delete_data(self, table: str, conditions: Dict[str, Any]) -> None:
        """Delete data from Redis."""
        if not self.redis_client:
            raise RuntimeError("Redis connection not established")
        
        if 'key' in conditions:
            self.redis_client.delete(conditions['key'])
        elif 'pattern' in conditions:
            keys = list(self.redis_client.scan_iter(match=conditions['pattern']))
            if keys:
                self.redis_client.delete(*keys)
    
    def get_last_sync_timestamp(self) -> Optional[str]:
        """Get last sync timestamp from Redis."""
        if not self.redis_client:
            return None
        
        watermark_key = f"watermark:{self.config.table or 'default'}"
        return self.redis_client.get(watermark_key)
    
    def update_last_sync_timestamp(self, timestamp: str) -> None:
        """Update last sync timestamp in Redis."""
        if not self.redis_client:
            raise RuntimeError("Redis connection not established")
        
        watermark_key = f"watermark:{self.config.table or 'default'}"
        self.redis_client.set(watermark_key, timestamp)


class ElasticsearchAdapter(BaseAdapter):
    """Example Elasticsearch adapter implementation."""
    
    def __init__(self, config: DatabaseConfig):
        super().__init__(config)
        self.es_client = None
    
    def connect(self) -> None:
        """Connect to Elasticsearch."""
        try:
            from elasticsearch import Elasticsearch
            
            hosts = [f"{self.config.host}:{self.config.port or 9200}"]
            
            if self.config.username and self.config.password:
                self.es_client = Elasticsearch(
                    hosts,
                    basic_auth=(self.config.username, self.config.password)
                )
            else:
                self.es_client = Elasticsearch(hosts)
            
            # Test connection
            self.es_client.info()
            
        except ImportError:
            raise ImportError("elasticsearch package is required. Install it with: pip install elasticsearch")
        except Exception as e:
            raise ConnectionError(f"Failed to connect to Elasticsearch: {e}")
    
    def disconnect(self) -> None:
        """Disconnect from Elasticsearch."""
        if self.es_client:
            self.es_client.close()
            self.es_client = None
    
    def execute_query(self, query: str, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Execute Elasticsearch query."""
        if not self.es_client:
            raise RuntimeError("Elasticsearch connection not established")
        
        index = self.config.table or self.config.database
        
        # Simple search query
        search_body = {
            "query": {"match_all": {}},
            "size": params.get('batch_size', 1000) if params else 1000
        }
        
        # Add watermark filtering if specified
        if params and 'last_sync' in params and self.config.watermark:
            search_body["query"] = {
                "range": {
                    self.config.watermark.column: {
                        "gt": params['last_sync']
                    }
                }
            }
        
        response = self.es_client.search(index=index, body=search_body)
        
        results = []
        for hit in response['hits']['hits']:
            doc = hit['_source']
            doc['_id'] = hit['_id']
            results.append(doc)
        
        return results
    
    def insert_data(self, table: str, data: List[Dict[str, Any]]) -> None:
        """Insert data into Elasticsearch."""
        if not self.es_client:
            raise RuntimeError("Elasticsearch connection not established")
        
        for record in data:
            doc_id = record.pop('_id', None)
            self.es_client.index(
                index=table,
                id=doc_id,
                document=record
            )
    
    def update_data(self, table: str, data: List[Dict[str, Any]], key_columns: List[str]) -> None:
        """Update data in Elasticsearch."""
        # For Elasticsearch, update is the same as index
        self.insert_data(table, data)
    
    def delete_data(self, table: str, conditions: Dict[str, Any]) -> None:
        """Delete data from Elasticsearch."""
        if not self.es_client:
            raise RuntimeError("Elasticsearch connection not established")
        
        if '_id' in conditions:
            self.es_client.delete(index=table, id=conditions['_id'])
        else:
            # Delete by query
            delete_body = {
                "query": {
                    "bool": {
                        "must": [
                            {"term": {k: v}} for k, v in conditions.items()
                        ]
                    }
                }
            }
            self.es_client.delete_by_query(index=table, body=delete_body)
    
    def get_last_sync_timestamp(self) -> Optional[str]:
        """Get last sync timestamp."""
        # Implementation depends on how you store watermarks in ES
        return None
    
    def update_last_sync_timestamp(self, timestamp: str) -> None:
        """Update last sync timestamp."""
        # Implementation depends on how you store watermarks in ES
        pass
