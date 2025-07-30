"""Configuration loader module."""
import os
import yaml
import configparser
from typing import Union, Dict, Any
from pathlib import Path
from .config import CDCConfig, DatabaseConfig, SyncConfig


class ConfigLoader:
    @staticmethod
    def load_yaml(file_path: Union[str, Path]) -> CDCConfig:
        """Load configuration from YAML file."""
        with open(file_path, 'r') as f:
            config_dict = yaml.safe_load(f)
        return CDCConfig(**config_dict)

    @staticmethod
    def load_ini(file_path: Union[str, Path]) -> CDCConfig:
        """Load configuration from INI file."""
        config = configparser.ConfigParser()
        config.read(file_path)

        def parse_database_section(section: str) -> Dict[str, Any]:
            db_config = dict(config[section])
            if 'additional_params' in db_config:
                db_config['additional_params'] = yaml.safe_load(db_config['additional_params'])
            return db_config

        source_config = parse_database_section('source')
        dest_config = parse_database_section('destination')
        sync_config = dict(config['sync'])

        return CDCConfig(
            source=DatabaseConfig(**source_config),
            destination=DatabaseConfig(**dest_config),
            sync=SyncConfig(**sync_config)
        )

    @staticmethod
    def load_config(file_path: Union[str, Path]) -> CDCConfig:
        """Load configuration from file (supports both YAML and INI)."""
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {file_path}")

        if file_path.suffix.lower() in ['.yaml', '.yml']:
            return ConfigLoader.load_yaml(file_path)
        elif file_path.suffix.lower() == '.ini':
            return ConfigLoader.load_ini(file_path)
        else:
            raise ValueError(f"Unsupported configuration file format: {file_path.suffix}")


def load_config(config_path: str) -> CDCConfig:
    """Load configuration from YAML file.

    Args:
        config_path: Path to the configuration file

    Returns:
        CDCConfig: Loaded configuration

    Raises:
        FileNotFoundError: If the configuration file does not exist
        yaml.YAMLError: If the configuration file is invalid
        ValueError: If the configuration is invalid
    """
    try:
        config_file = Path(config_path)
        if not config_file.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")

        with open(config_file, 'r') as f:
            config_dict = yaml.safe_load(f)

        return CDCConfig(**config_dict)
    except yaml.YAMLError as e:
        raise ValueError(f"Invalid YAML configuration: {str(e)}")
    except Exception as e:
        raise ValueError(f"Error loading configuration: {str(e)}") 