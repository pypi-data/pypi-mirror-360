from evolvishub_data_handler.config_loader import ConfigLoader
from evolvishub_data_handler.cdc_handler import CDCHandler


def main():
    # Load configuration
    config = ConfigLoader.load_config('config.yaml')
    
    # Create and run CDC handler
    handler = CDCHandler(config)
    
    # Run continuous synchronization
    handler.run_continuous()


if __name__ == '__main__':
    main() 