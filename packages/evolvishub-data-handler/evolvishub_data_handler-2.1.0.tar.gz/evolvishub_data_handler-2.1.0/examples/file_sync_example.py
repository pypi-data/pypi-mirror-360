import os
import yaml
from datetime import datetime
import pandas as pd
from evolvishub_data_handler.cdc_handler import CDCHandler
from evolvishub_data_handler.config import CDCConfig

def create_sample_csv():
    """Create a sample CSV file with test data."""
    # Create directory if it doesn't exist
    os.makedirs("data/source", exist_ok=True)
    
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
    
    # Create DataFrame and save to CSV
    df = pd.DataFrame(data)
    df.to_csv("data/source/orders.csv", index=False)
    print("Created sample CSV file at data/source/orders.csv")

def main():
    # Create sample data
    create_sample_csv()
    
    # Load configuration
    with open("file_sync_config.yaml", "r") as f:
        config_dict = yaml.safe_load(f)
    
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
        if os.path.exists("data/source/orders.csv"):
            os.remove("data/source/orders.csv")
            print("Cleaned up sample CSV file")

if __name__ == "__main__":
    main() 