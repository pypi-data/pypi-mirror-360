from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from ..config import DatabaseConfig


class BaseAdapter(ABC):
    def __init__(self, config: DatabaseConfig):
        self.config = config
        self.connection = None

    @abstractmethod
    def connect(self) -> None:
        """Establish connection to the database."""
        pass

    @abstractmethod
    def disconnect(self) -> None:
        """Close the database connection."""
        pass

    @abstractmethod
    def execute_query(self, query: str, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Execute a query and return results."""
        pass

    @abstractmethod
    def insert_data(self, table: str, data: List[Dict[str, Any]]) -> None:
        """Insert data into the specified table."""
        pass

    @abstractmethod
    def update_data(self, table: str, data: List[Dict[str, Any]], key_columns: List[str]) -> None:
        """Update data in the specified table."""
        pass

    @abstractmethod
    def delete_data(self, table: str, conditions: Dict[str, Any]) -> None:
        """Delete data from the specified table."""
        pass

    @abstractmethod
    def get_last_sync_timestamp(self) -> Optional[str]:
        """Get the last synchronization timestamp."""
        pass

    @abstractmethod
    def update_last_sync_timestamp(self, timestamp: str) -> None:
        """Update the last synchronization timestamp."""
        pass

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect() 