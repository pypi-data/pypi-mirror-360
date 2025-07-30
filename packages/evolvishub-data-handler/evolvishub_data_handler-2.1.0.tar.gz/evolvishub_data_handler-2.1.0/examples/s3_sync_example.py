import os
import yaml
import boto3
import pandas as pd
from datetime import datetime
from evolvishub_data_handler.cdc_handler import CDCHandler
from evolvishub_data_handler.config import CDCConfig

def create_sample_s3_data():
    """Create sample data in S3."""
    # Create sample data
    data = {
        'id': [1, 2, 3, 4, 5],
        'customer_id': [101, 102, 103, 104, 105],
        'product_id': [201, 202, 203, 204, 205],
        'quantity': [2, 1, 3, 4, 2],
        'price': [29.99, 39.99, 19.99, 49.99, 59.99],
        'updated_at': [
            '2024-01-01T10:00:00Z',
            '2024-01-01T11:00:00Z',
            '2024-01-01T12:00:00Z',
            '2024-01-01T13:00:00Z',
            '2024-01-01T14:00:00Z'
        ]
    }
    
    # Create DataFrame
    df = pd.DataFrame(data)
    
    # Initialize S3 client
    s3_client = boto3.client(
        's3',
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
        region_name=os.getenv('AWS_REGION', 'us-west-2')
    )
    
    # Upload to S3
    bucket_name = os.getenv('S3_BUCKET', 'my-bucket')
    key = 'data/orders.parquet'
    
    # Convert to parquet and upload
    buffer = df.to_parquet(index=False)
    s3_client.put_object(
        Bucket=bucket_name,
        Key=key,
        Body=buffer
    )
    print(f"Created sample data in S3: s3://{bucket_name}/{key}")

def main():
    # Create sample data
    create_sample_s3_data()
    
    # Load configuration
    with open("s3_sync_config.yaml", "r") as f:
        config_dict = yaml.safe_load(f)
    
    # Override credentials from environment variables
    if os.getenv('AWS_ACCESS_KEY_ID'):
        config_dict['source']['username'] = os.getenv('AWS_ACCESS_KEY_ID')
    if os.getenv('AWS_SECRET_ACCESS_KEY'):
        config_dict['source']['password'] = os.getenv('AWS_SECRET_ACCESS_KEY')
    if os.getenv('AWS_REGION'):
        config_dict['source']['cloud_storage']['region'] = os.getenv('AWS_REGION')
    if os.getenv('S3_BUCKET'):
        config_dict['source']['file_path'] = f"s3://{os.getenv('S3_BUCKET')}/data/orders.parquet"
    
    config = CDCConfig(**config_dict)
    
    # Initialize CDC handler
    handler = CDCHandler(config)
    
    try:
        # Run one-time sync
        print("Starting one-time sync...")
        handler.sync()
        print("One-time sync completed successfully")
        
        # Run continuous sync
        print("\nStarting continuous sync (press Ctrl+C to stop)...")
        handler.run_continuous()
    except KeyboardInterrupt:
        print("\nStopping continuous sync...")
    except Exception as e:
        print(f"Error during sync: {str(e)}")
    finally:
        # Cleanup
        try:
            s3_client = boto3.client(
                's3',
                aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
                region_name=os.getenv('AWS_REGION', 'us-west-2')
            )
            bucket_name = os.getenv('S3_BUCKET', 'my-bucket')
            key = 'data/orders.parquet'
            s3_client.delete_object(Bucket=bucket_name, Key=key)
            print(f"Cleaned up sample data from S3: s3://{bucket_name}/{key}")
        except Exception as e:
            print(f"Error during cleanup: {str(e)}")

if __name__ == "__main__":
    main() 