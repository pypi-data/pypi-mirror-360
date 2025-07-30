from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime
import pymongo
from bson import ObjectId
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database
import logging
logger = logging.getLogger(__name__)
from ..config import DatabaseConfig
from .base import BaseAdapter


class MongoDBAdapter(BaseAdapter):
    def connect(self) -> None:
        """Connect to the MongoDB database."""
        try:
            connection_string = self._build_connection_string()
            self.connection = MongoClient(connection_string, **self.config.additional_params)
            self.db: Database = self.connection[self.config.database]
        except Exception as e:
            logger.error(f"Error connecting to MongoDB: {str(e)}")
            raise

    def _build_connection_string(self) -> str:
        """Build MongoDB connection string."""
        auth = ""
        if self.config.username and self.config.password:
            auth = f"{self.config.username}:{self.config.password}@"
        
        host = self.config.host or "localhost"
        port = self.config.port or 27017
        
        return f"mongodb://{auth}{host}:{port}"

    def disconnect(self) -> None:
        """Close the MongoDB connection."""
        if self.connection:
            self.connection.close()
            self.connection = None
            self.db = None

    def execute_query(self, query: str, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Execute a MongoDB query and return results."""
        if not hasattr(self, 'db') or self.db is None:
            raise RuntimeError("Database connection is not established. Call connect() first.")
        collection: Collection = self.db[self.config.table]
        return list(collection.find(params or {}))

    def insert_data(self, table: str, data: List[Dict[str, Any]]) -> None:
        """Insert data into the specified collection."""
        if not hasattr(self, 'db') or self.db is None:
            raise RuntimeError("Database connection is not established. Call connect() first.")
        if not data:
            return
        collection: Collection = self.db[table]
        collection.insert_many(data)

    def update_data(self, table: str, data: List[Dict[str, Any]], key_columns: List[str]) -> None:
        """Update data in the specified collection."""
        if not hasattr(self, 'db') or self.db is None:
            raise RuntimeError("Database connection is not established. Call connect() first.")
        if not data:
            return
        collection: Collection = self.db[table]
        for row in data:
            filter_doc = {k: row[k] for k in key_columns}
            update_doc = {"$set": {k: v for k, v in row.items() if k not in key_columns}}
            collection.update_one(filter_doc, update_doc, upsert=True)

    def delete_data(self, table: str, conditions: Dict[str, Any]) -> None:
        """Delete data from the specified collection."""
        if not hasattr(self, 'db') or self.db is None:
            raise RuntimeError("Database connection is not established. Call connect() first.")
        collection: Collection = self.db[table]
        collection.delete_many(conditions)

    def get_watermark(self, table_name: str, watermark_column: str) -> Optional[Tuple[str, str]]:
        """Get the watermark value and status for a collection."""
        if not hasattr(self, 'db') or self.db is None:
            raise RuntimeError("Database connection is not established. Call connect() first.")
        if not table_name or not watermark_column:
            raise ValueError("Table name and watermark column must be specified for watermark retrieval.")
        try:
            collection = self.connection['sync_watermark']
            result = collection.find_one({
                'table_name': table_name,
                'watermark_column': watermark_column
            })
            return (result['watermark_value'], result['status']) if result else None
        except Exception as e:
            logger.error(f"Error getting watermark: {str(e)}")
            return None

    def update_watermark(self, table_name: str, watermark_column: str, 
                        watermark_value: str, status: str = 'success', 
                        error_message: Optional[str] = None) -> None:
        """Update the watermark value for a collection."""
        if not hasattr(self, 'db') or self.db is None:
            raise RuntimeError("Database connection is not established. Call connect() first.")
        if not table_name or not watermark_column:
            raise ValueError("Table name and watermark column must be specified for updating watermark.")
        collection = self.connection['sync_watermark']
        collection.update_one(
            {
                'table_name': table_name,
                'watermark_column': watermark_column
            },
            {
                '$set': {
                    'watermark_value': watermark_value,
                    'status': status,
                    'error_message': error_message,
                    'last_sync_at': datetime.utcnow()
                }
            },
            upsert=True
        )

    def get_last_sync_timestamp(self) -> Optional[str]:
        """Get the last synchronization timestamp."""
        if not self.config.watermark or not self.config.table:
            return None
        if not hasattr(self, 'db') or self.db is None:
            raise RuntimeError("Database connection is not established. Call connect() first.")
        collection: Collection = self.db[self.config.table]
        result = collection.find_one(
            sort=[(self.config.watermark.column, -1)]
        )
        return result[self.config.watermark.column] if result else None

    def update_last_sync_timestamp(self, timestamp: str) -> None:
        """Update the last synchronization timestamp."""
        if not self.config.watermark or not self.config.table:
            return
        if not hasattr(self, 'db') or self.db is None:
            raise RuntimeError("Database connection is not established. Call connect() first.")
        collection: Collection = self.db[self.config.table]
        collection.update_one(
            {"_id": "sync_timestamp"},
            {"$set": {self.config.watermark.column: timestamp}},
            upsert=True
        ) 