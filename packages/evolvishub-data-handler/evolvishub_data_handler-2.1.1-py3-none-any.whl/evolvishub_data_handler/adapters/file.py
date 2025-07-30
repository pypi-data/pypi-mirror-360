from typing import Any, Dict, List, Optional, Tuple
import json
import csv
import os
from datetime import datetime
from pathlib import Path
import pandas as pd
from ..config import DatabaseConfig
from .base import BaseAdapter


class FileAdapter(BaseAdapter):
    def connect(self) -> None:
        """Initialize file connection."""
        if not self.config.file_path:
            raise ValueError("file_path is required for FileAdapter")
            
        self.file_path = Path(self.config.file_path)
        self.file_type = self.file_path.suffix.lower()
        
        if self.file_type not in ['.csv', '.json']:
            raise ValueError(f"Unsupported file type: {self.file_type}")
            
        # Create directory if it doesn't exist
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Create file if it doesn't exist
        if not self.file_path.exists():
            if self.file_type == '.csv':
                with open(self.file_path, 'w', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow([])  # Empty header
            else:  # json
                with open(self.file_path, 'w') as f:
                    json.dump([], f)

    def disconnect(self) -> None:
        """No-op for file adapter."""
        pass

    def execute_query(self, query: str, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Read data from file with optional filtering."""
        if not hasattr(self, 'file_path') or not self.file_path.exists():
            raise RuntimeError("File connection is not established. Call connect() first.")
        if self.file_type == '.csv':
            df = pd.read_csv(self.file_path)
        else:  # json
            with open(self.file_path, 'r') as f:
                data = json.load(f)
                df = pd.DataFrame(data)
        
        # Apply watermark filtering if specified
        if params and 'last_sync' in params and self.config.watermark:
            df = df[df[self.config.watermark.column] > params['last_sync']]
        
        return df.to_dict('records')

    def insert_data(self, table: str, data: List[Dict[str, Any]]) -> None:
        """Insert data into the specified file."""
        if not hasattr(self, 'file_path') or not self.file_path.exists():
            raise RuntimeError("File connection is not established. Call connect() first.")
        if not data:
            return
        # Only support append for JSON for now
        if self.file_type == '.json':
            with open(self.file_path, 'r+') as f:
                existing = json.load(f)
                existing.extend(data)
                f.seek(0)
                json.dump(existing, f)
                f.truncate()
        elif self.file_type == '.csv':
            df = pd.read_csv(self.file_path)
            new_df = pd.DataFrame(data)
            df = pd.concat([df, new_df], ignore_index=True)
            df.to_csv(self.file_path, index=False)
        else:
            raise ValueError(f"Unsupported file type: {self.file_type}")

    def update_data(self, table: str, data: List[Dict[str, Any]], key_columns: List[str]) -> None:
        """Update data in the specified file."""
        if not hasattr(self, 'file_path') or not self.file_path.exists():
            raise RuntimeError("File connection is not established. Call connect() first.")
        if not data:
            return
        # Only support update for JSON for now
        if self.file_type == '.json':
            with open(self.file_path, 'r+') as f:
                existing = json.load(f)
                for row in data:
                    for i, item in enumerate(existing):
                        if all(item.get(k) == row.get(k) for k in key_columns):
                            existing[i].update(row)
                f.seek(0)
                json.dump(existing, f)
                f.truncate()
        elif self.file_type == '.csv':
            df = pd.read_csv(self.file_path)
            for row in data:
                mask = pd.Series([True] * len(df))
                for k in key_columns:
                    mask &= df[k] == row[k]
                for col, val in row.items():
                    if col not in key_columns:
                        df.loc[mask, col] = val
            df.to_csv(self.file_path, index=False)
        else:
            raise ValueError(f"Unsupported file type: {self.file_type}")

    def delete_data(self, table: str, conditions: Dict[str, Any]) -> None:
        """Delete data from the specified file."""
        if not hasattr(self, 'file_path') or not self.file_path.exists():
            raise RuntimeError("File connection is not established. Call connect() first.")
        # Only support delete for JSON for now
        if self.file_type == '.json':
            with open(self.file_path, 'r+') as f:
                existing = json.load(f)
                filtered = [item for item in existing if not all(item.get(k) == v for k, v in conditions.items())]
                f.seek(0)
                json.dump(filtered, f)
                f.truncate()
        elif self.file_type == '.csv':
            df = pd.read_csv(self.file_path)
            mask = pd.Series([True] * len(df))
            for k, v in conditions.items():
                mask &= df[k] != v
            df = df[mask]
            df.to_csv(self.file_path, index=False)
        else:
            raise ValueError(f"Unsupported file type: {self.file_type}")

    def get_watermark(self, table_name: str, watermark_column: str) -> Optional[Tuple[str, str]]:
        """Get the watermark value and status from watermark file."""
        watermark_file = self.file_path.parent / 'sync_watermark.json'
        
        try:
            if watermark_file.exists():
                with open(watermark_file, 'r') as f:
                    watermark_data = json.load(f)
                    for entry in watermark_data:
                        if entry['table_name'] == table_name and entry['watermark_column'] == watermark_column:
                            return entry['watermark_value'], entry['status']
            return None
        except Exception:
            return None

    def update_watermark(self, table_name: str, watermark_column: str, 
                        watermark_value: str, status: str = 'success', 
                        error_message: Optional[str] = None) -> None:
        """Update the watermark value in watermark file."""
        watermark_file = self.file_path.parent / 'sync_watermark.json'
        
        # Read existing watermark data
        watermark_data = []
        if watermark_file.exists():
            with open(watermark_file, 'r') as f:
                watermark_data = json.load(f)
        
        # Update or add new watermark entry
        entry = {
            'table_name': table_name,
            'watermark_column': watermark_column,
            'watermark_value': watermark_value,
            'status': status,
            'error_message': error_message,
            'last_sync_at': datetime.utcnow().isoformat()
        }
        
        # Find and update existing entry or append new one
        found = False
        for i, existing in enumerate(watermark_data):
            if existing['table_name'] == table_name and existing['watermark_column'] == watermark_column:
                watermark_data[i] = entry
                found = True
                break
        
        if not found:
            watermark_data.append(entry)
        
        # Write back to file
        with open(watermark_file, 'w') as f:
            json.dump(watermark_data, f, indent=2)

    def get_last_sync_timestamp(self) -> Optional[str]:
        """Get the last synchronization timestamp."""
        if not self.config.watermark:
            return None
            
        result = self.get_watermark(
            self.config.table,
            self.config.watermark.column
        )
        return result[0] if result and result[1] == 'success' else None

    def update_last_sync_timestamp(self, timestamp: str) -> None:
        """Update the last synchronization timestamp."""
        if not self.config.watermark:
            return
            
        self.update_watermark(
            self.config.table,
            self.config.watermark.column,
            timestamp
        ) 