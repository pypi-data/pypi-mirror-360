from typing import Any, Dict, List, Optional, Tuple
import boto3
import json
import csv
import io
from datetime import datetime
from pathlib import Path
import pandas as pd
from ..config import DatabaseConfig
from .base import BaseAdapter
import logging

logger = logging.getLogger(__name__)


class S3Adapter(BaseAdapter):
    
    def connect(self) -> None:
        """Initialize S3 connection."""
        if not self.config.file_path:
            raise ValueError("file_path is required for S3Adapter")
            
        # Parse S3 path (s3://bucket-name/path/to/file)
        s3_path = self.config.file_path.replace('s3://', '')
        self.bucket_name, *path_parts = s3_path.split('/')
        self.key = '/'.join(path_parts)
        self.file_type = Path(self.key).suffix.lower()
        
        if self.file_type not in ['.csv', '.json', '.parquet']:
            raise ValueError(f"Unsupported file type: {self.file_type}")
        
        # Initialize S3 client
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=self.config.username,
            aws_secret_access_key=self.config.password,
            region_name=self.config.region
        )

    def disconnect(self) -> None:
        """No-op for S3 adapter."""
        pass

    def execute_query(self, query: str, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Read data from S3 with optional filtering."""
        if not hasattr(self, 's3_client') or not hasattr(self, 'bucket_name') or not hasattr(self, 'key'):
            raise RuntimeError("S3 connection is not established. Call connect() first.")
        try:
            response = self.s3_client.get_object(
                Bucket=self.bucket_name,
                Key=self.key
            )
            if self.file_type == '.csv':
                df = pd.read_csv(response['Body'])
            elif self.file_type == '.json':
                df = pd.read_json(response['Body'])
            else:  # parquet
                df = pd.read_parquet(response['Body'])
            if params and 'last_sync' in params and self.config.watermark:
                df = df[df[self.config.watermark.column] > params['last_sync']]
            return df.to_dict('records')
        except Exception as e:
            logger.error(f"Error reading from S3: {str(e)}")
            raise Exception(f"Error reading from S3: {str(e)}")

    def insert_data(self, table: str, data: List[Dict[str, Any]]) -> None:
        """Append data to S3 file."""
        if not data:
            return

        try:
            # Read existing data
            existing_data = []
            try:
                response = self.s3_client.get_object(
                    Bucket=self.bucket_name,
                    Key=self.key
                )
                
                if self.file_type == '.csv':
                    existing_data = pd.read_csv(response['Body']).to_dict('records')
                elif self.file_type == '.json':
                    existing_data = json.load(response['Body'])
                else:  # parquet
                    existing_data = pd.read_parquet(response['Body']).to_dict('records')
            except self.s3_client.exceptions.NoSuchKey:
                pass
            
            # Append new data
            existing_data.extend(data)
            
            # Convert to appropriate format and upload
            if self.file_type == '.csv':
                df = pd.DataFrame(existing_data)
                buffer = io.StringIO()
                df.to_csv(buffer, index=False)
                self.s3_client.put_object(
                    Bucket=self.bucket_name,
                    Key=self.key,
                    Body=buffer.getvalue()
                )
            elif self.file_type == '.json':
                self.s3_client.put_object(
                    Bucket=self.bucket_name,
                    Key=self.key,
                    Body=json.dumps(existing_data, indent=2)
                )
            else:  # parquet
                df = pd.DataFrame(existing_data)
                buffer = io.BytesIO()
                df.to_parquet(buffer, index=False)
                self.s3_client.put_object(
                    Bucket=self.bucket_name,
                    Key=self.key,
                    Body=buffer.getvalue()
                )
        except Exception as e:
            raise Exception(f"Error writing to S3: {str(e)}")

    def update_data(self, table: str, data: List[Dict[str, Any]], key_columns: List[str]) -> None:
        """Update data in S3 file."""
        if not data:
            return

        try:
            # Read existing data
            response = self.s3_client.get_object(
                Bucket=self.bucket_name,
                Key=self.key
            )
            
            if self.file_type == '.csv':
                df = pd.read_csv(response['Body'])
            elif self.file_type == '.json':
                df = pd.DataFrame(json.load(response['Body']))
            else:  # parquet
                df = pd.read_parquet(response['Body'])
            
            # Update records
            for row in data:
                mask = True
                for key in key_columns:
                    mask &= (df[key] == row[key])
                df.loc[mask] = row
            
            # Write back to S3
            if self.file_type == '.csv':
                buffer = io.StringIO()
                df.to_csv(buffer, index=False)
                self.s3_client.put_object(
                    Bucket=self.bucket_name,
                    Key=self.key,
                    Body=buffer.getvalue()
                )
            elif self.file_type == '.json':
                self.s3_client.put_object(
                    Bucket=self.bucket_name,
                    Key=self.key,
                    Body=json.dumps(df.to_dict('records'), indent=2)
                )
            else:  # parquet
                buffer = io.BytesIO()
                df.to_parquet(buffer, index=False)
                self.s3_client.put_object(
                    Bucket=self.bucket_name,
                    Key=self.key,
                    Body=buffer.getvalue()
                )
        except Exception as e:
            raise Exception(f"Error updating S3 data: {str(e)}")

    def delete_data(self, table: str, conditions: Dict[str, Any]) -> None:
        """Delete data from S3 file."""
        try:
            # Read existing data
            response = self.s3_client.get_object(
                Bucket=self.bucket_name,
                Key=self.key
            )
            
            if self.file_type == '.csv':
                df = pd.read_csv(response['Body'])
            elif self.file_type == '.json':
                df = pd.DataFrame(json.load(response['Body']))
            else:  # parquet
                df = pd.read_parquet(response['Body'])
            
            # Create mask for deletion
            mask = True
            for key, value in conditions.items():
                mask &= (df[key] == value)
            
            # Remove matching rows
            df = df[~mask]
            
            # Write back to S3
            if self.file_type == '.csv':
                buffer = io.StringIO()
                df.to_csv(buffer, index=False)
                self.s3_client.put_object(
                    Bucket=self.bucket_name,
                    Key=self.key,
                    Body=buffer.getvalue()
                )
            elif self.file_type == '.json':
                self.s3_client.put_object(
                    Bucket=self.bucket_name,
                    Key=self.key,
                    Body=json.dumps(df.to_dict('records'), indent=2)
                )
            else:  # parquet
                buffer = io.BytesIO()
                df.to_parquet(buffer, index=False)
                self.s3_client.put_object(
                    Bucket=self.bucket_name,
                    Key=self.key,
                    Body=buffer.getvalue()
                )
        except Exception as e:
            raise Exception(f"Error deleting from S3: {str(e)}")

    def get_watermark(self, table_name: str, watermark_column: str) -> Optional[Tuple[str, str]]:
        """Get the watermark value and status from S3 watermark file."""
        watermark_key = f"{Path(self.key).parent}/sync_watermark.json"
        
        try:
            response = self.s3_client.get_object(
                Bucket=self.bucket_name,
                Key=watermark_key
            )
            watermark_data = json.load(response['Body'])
            for entry in watermark_data:
                if entry['table_name'] == table_name and entry['watermark_column'] == watermark_column:
                    return entry['watermark_value'], entry['status']
            return None
        except Exception:
            return None

    def update_watermark(self, table_name: str, watermark_column: str, 
                        watermark_value: str, status: str = 'success', 
                        error_message: Optional[str] = None) -> None:
        """Update the watermark value in S3 watermark file."""
        watermark_key = f"{Path(self.key).parent}/sync_watermark.json"
        
        try:
            # Read existing watermark data
            watermark_data = []
            try:
                response = self.s3_client.get_object(
                    Bucket=self.bucket_name,
                    Key=watermark_key
                )
                watermark_data = json.load(response['Body'])
            except self.s3_client.exceptions.NoSuchKey:
                pass
            
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
            
            # Write back to S3
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=watermark_key,
                Body=json.dumps(watermark_data, indent=2)
            )
        except Exception as e:
            raise Exception(f"Error updating S3 watermark: {str(e)}")

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