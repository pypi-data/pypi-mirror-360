"""Watermark management for data synchronization."""

import sqlite3
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Tuple, Dict, Any
from abc import ABC, abstractmethod

from loguru import logger

from .config import WatermarkStorageConfig, WatermarkStorageType


class BaseWatermarkManager(ABC):
    """Base class for watermark management."""
    
    @abstractmethod
    def get_watermark(self, table_name: str, watermark_column: str) -> Optional[Tuple[str, str]]:
        """Get the watermark value and status for a table.
        
        Returns:
            Tuple of (watermark_value, status) or None if not found
        """
        pass
    
    @abstractmethod
    def update_watermark(self, table_name: str, watermark_column: str, 
                        watermark_value: str, status: str = 'success', 
                        error_message: Optional[str] = None) -> None:
        """Update the watermark value for a table."""
        pass
    
    @abstractmethod
    def close(self) -> None:
        """Close any open connections."""
        pass


class SQLiteWatermarkManager(BaseWatermarkManager):
    """SQLite-based watermark manager for centralized watermark storage."""
    
    def __init__(self, config: WatermarkStorageConfig):
        """Initialize the SQLite watermark manager.
        
        Args:
            config: Watermark storage configuration
        """
        self.config = config
        self.db_path = config.sqlite_path
        self.table_name = config.table_name
        self.connection: Optional[sqlite3.Connection] = None
        
        # Ensure directory exists
        if self.db_path:
            db_dir = Path(self.db_path).parent
            db_dir.mkdir(parents=True, exist_ok=True)
        
        self._connect()
        self._create_watermark_table()
    
    def _connect(self) -> None:
        """Connect to SQLite database."""
        try:
            self.connection = sqlite3.connect(
                self.db_path, 
                check_same_thread=False,
                timeout=30.0
            )
            self.connection.row_factory = sqlite3.Row
            logger.debug(f"Connected to SQLite watermark database: {self.db_path}")
        except sqlite3.Error as e:
            logger.error(f"Error connecting to SQLite watermark database: {str(e)}")
            raise
    
    def _create_watermark_table(self) -> None:
        """Create the watermark table if it doesn't exist."""
        try:
            cursor = self.connection.cursor()
            cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS {self.table_name} (
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
                )
            """)
            self.connection.commit()
            cursor.close()
            logger.debug(f"Watermark table '{self.table_name}' created or already exists")
        except sqlite3.Error as e:
            logger.error(f"Error creating watermark table: {str(e)}")
            raise
    
    def get_watermark(self, table_name: str, watermark_column: str) -> Optional[Tuple[str, str]]:
        """Get the watermark value and status for a table."""
        try:
            cursor = self.connection.cursor()
            cursor.execute(f"""
                SELECT watermark_value, status
                FROM {self.table_name}
                WHERE table_name = ? AND watermark_column = ?
                ORDER BY updated_at DESC
                LIMIT 1
            """, (table_name, watermark_column))
            result = cursor.fetchone()
            cursor.close()
            
            if result:
                logger.debug(f"Retrieved watermark for {table_name}.{watermark_column}: {result['watermark_value']}")
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
        try:
            cursor = self.connection.cursor()
            now = datetime.now(timezone.utc).isoformat()
            
            cursor.execute(f"""
                INSERT INTO {self.table_name} 
                    (table_name, watermark_column, watermark_value, status, error_message, last_sync_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(table_name, watermark_column) DO UPDATE SET 
                    watermark_value = excluded.watermark_value,
                    status = excluded.status,
                    error_message = excluded.error_message,
                    last_sync_at = excluded.last_sync_at,
                    updated_at = excluded.updated_at
            """, (table_name, watermark_column, watermark_value, status, error_message, now, now))
            
            self.connection.commit()
            cursor.close()
            logger.debug(f"Updated watermark for {table_name}.{watermark_column}: {watermark_value}")
        except sqlite3.Error as e:
            logger.error(f"Error updating watermark: {str(e)}")
            raise
    
    def get_all_watermarks(self) -> Dict[str, Dict[str, Any]]:
        """Get all watermarks for monitoring/debugging purposes."""
        try:
            cursor = self.connection.cursor()
            cursor.execute(f"""
                SELECT table_name, watermark_column, watermark_value, status, 
                       error_message, last_sync_at, created_at, updated_at
                FROM {self.table_name}
                ORDER BY updated_at DESC
            """)
            results = cursor.fetchall()
            cursor.close()
            
            watermarks = {}
            for row in results:
                key = f"{row['table_name']}.{row['watermark_column']}"
                watermarks[key] = {
                    'table_name': row['table_name'],
                    'watermark_column': row['watermark_column'],
                    'watermark_value': row['watermark_value'],
                    'status': row['status'],
                    'error_message': row['error_message'],
                    'last_sync_at': row['last_sync_at'],
                    'created_at': row['created_at'],
                    'updated_at': row['updated_at']
                }
            
            return watermarks
        except sqlite3.Error as e:
            logger.error(f"Error getting all watermarks: {str(e)}")
            return {}
    
    def close(self) -> None:
        """Close the SQLite connection."""
        if self.connection:
            self.connection.close()
            self.connection = None
            logger.debug("SQLite watermark database connection closed")


class FileWatermarkManager(BaseWatermarkManager):
    """File-based watermark manager using JSON storage."""
    
    def __init__(self, config: WatermarkStorageConfig):
        """Initialize the file watermark manager.
        
        Args:
            config: Watermark storage configuration
        """
        self.config = config
        self.file_path = Path(config.file_path)
        
        # Ensure directory exists
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize file if it doesn't exist
        if not self.file_path.exists():
            self._save_watermarks({})
    
    def _load_watermarks(self) -> Dict[str, Any]:
        """Load watermarks from JSON file."""
        try:
            with open(self.file_path, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
    
    def _save_watermarks(self, watermarks: Dict[str, Any]) -> None:
        """Save watermarks to JSON file."""
        try:
            with open(self.file_path, 'w') as f:
                json.dump(watermarks, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Error saving watermarks to file: {str(e)}")
            raise
    
    def get_watermark(self, table_name: str, watermark_column: str) -> Optional[Tuple[str, str]]:
        """Get the watermark value and status for a table."""
        watermarks = self._load_watermarks()
        key = f"{table_name}.{watermark_column}"
        
        if key in watermarks:
            entry = watermarks[key]
            return (entry['watermark_value'], entry.get('status', 'success'))
        
        return None
    
    def update_watermark(self, table_name: str, watermark_column: str, 
                        watermark_value: str, status: str = 'success', 
                        error_message: Optional[str] = None) -> None:
        """Update the watermark value for a table."""
        watermarks = self._load_watermarks()
        key = f"{table_name}.{watermark_column}"
        
        watermarks[key] = {
            'table_name': table_name,
            'watermark_column': watermark_column,
            'watermark_value': watermark_value,
            'status': status,
            'error_message': error_message,
            'last_sync_at': datetime.now(timezone.utc).isoformat(),
            'updated_at': datetime.now(timezone.utc).isoformat()
        }
        
        self._save_watermarks(watermarks)
        logger.debug(f"Updated watermark for {table_name}.{watermark_column}: {watermark_value}")
    
    def close(self) -> None:
        """No-op for file-based storage."""
        pass


def create_watermark_manager(config: WatermarkStorageConfig) -> BaseWatermarkManager:
    """Factory function to create appropriate watermark manager.
    
    Args:
        config: Watermark storage configuration
        
    Returns:
        Appropriate watermark manager instance
    """
    if config.type == WatermarkStorageType.SQLITE:
        return SQLiteWatermarkManager(config)
    elif config.type == WatermarkStorageType.FILE:
        return FileWatermarkManager(config)
    else:
        raise ValueError(f"Unsupported watermark storage type: {config.type}")
