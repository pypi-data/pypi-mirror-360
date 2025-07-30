"""
Multi-source, multi-destination CDC handler.
"""

import asyncio
import logging
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any, Optional, Callable
from datetime import datetime
import threading

from .config import MultiCDCConfig, SourceDestinationMapping, CDCConfig, SyncConfig
from .cdc_handler import CDCHandler
from .adapters.factory import AdapterFactory

logger = logging.getLogger(__name__)


class MappingResult:
    """Result of a single mapping execution."""
    
    def __init__(self, mapping_name: str):
        self.mapping_name = mapping_name
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None
        self.success = False
        self.error: Optional[Exception] = None
        self.records_processed = 0
        self.duration_seconds = 0.0
        
    def start(self):
        """Mark the start of mapping execution."""
        self.start_time = datetime.now()
        
    def finish(self, success: bool, error: Optional[Exception] = None, records_processed: int = 0):
        """Mark the end of mapping execution."""
        self.end_time = datetime.now()
        self.success = success
        self.error = error
        self.records_processed = records_processed
        
        if self.start_time and self.end_time:
            self.duration_seconds = (self.end_time - self.start_time).total_seconds()


class MultiCDCHandler:
    """Handler for managing multiple CDC source-destination mappings."""
    
    def __init__(self, config: MultiCDCConfig):
        """Initialize multi-CDC handler.
        
        Args:
            config: Multi-CDC configuration
        """
        self.config = config
        self.mapping_handlers: Dict[str, CDCHandler] = {}
        self.results: List[MappingResult] = []
        self.is_running = False
        self.stop_event = threading.Event()
        
        # Setup logging
        logging.basicConfig(level=getattr(logging, config.log_level.upper()))
        
        # Initialize CDC handlers for each mapping
        self._initialize_handlers()
        
        logger.info(f"Initialized MultiCDCHandler '{config.name}' with {len(config.mappings)} mappings")
    
    def _initialize_handlers(self):
        """Initialize individual CDC handlers for each mapping."""
        for mapping in self.config.mappings:
            if not mapping.enabled:
                logger.info(f"Skipping disabled mapping: {mapping.name}")
                continue
                
            try:
                # Create CDC configuration for this mapping
                cdc_config = self._create_cdc_config(mapping)
                
                # Create CDC handler
                handler = CDCHandler(cdc_config)
                self.mapping_handlers[mapping.name] = handler
                
                logger.info(f"Initialized handler for mapping: {mapping.name}")
                
            except Exception as e:
                logger.error(f"Failed to initialize handler for mapping {mapping.name}: {e}")
                if self.config.stop_on_error:
                    raise
    
    def _create_cdc_config(self, mapping: SourceDestinationMapping) -> CDCConfig:
        """Create a CDC configuration from a mapping."""
        
        # Use mapping-specific sync config or fall back to global
        sync_config = mapping.sync or self.config.global_sync
        
        # Override table names if specified
        source_config = mapping.source.model_copy()
        destination_config = mapping.destination.model_copy()
        
        if mapping.source_table:
            source_config.table = mapping.source_table
        if mapping.destination_table:
            destination_config.table = mapping.destination_table
        
        # Override watermark if specified
        if mapping.watermark:
            source_config.watermark = mapping.watermark
        
        return CDCConfig(
            source=source_config,
            destination=destination_config,
            sync=sync_config,
            plugins=self.config.global_plugins
        )
    
    def execute_mapping(self, mapping_name: str) -> MappingResult:
        """Execute a single mapping.
        
        Args:
            mapping_name: Name of the mapping to execute
            
        Returns:
            Result of the mapping execution
        """
        result = MappingResult(mapping_name)
        result.start()
        
        try:
            if mapping_name not in self.mapping_handlers:
                raise ValueError(f"Mapping '{mapping_name}' not found or not enabled")
            
            handler = self.mapping_handlers[mapping_name]
            mapping = next(m for m in self.config.mappings if m.name == mapping_name)
            
            logger.info(f"Starting execution of mapping: {mapping_name}")
            
            # Apply custom query if specified
            if mapping.custom_query:
                # Execute custom query
                records_processed = self._execute_custom_query(handler, mapping)
            else:
                # Execute standard CDC sync
                records_processed = self._execute_standard_sync(handler, mapping)
            
            result.finish(success=True, records_processed=records_processed)
            logger.info(f"Completed mapping {mapping_name}: {records_processed} records in {result.duration_seconds:.2f}s")
            
        except Exception as e:
            result.finish(success=False, error=e)
            logger.error(f"Failed mapping {mapping_name}: {e}")
            
            if self.config.stop_on_error:
                raise
        
        return result
    
    def _execute_custom_query(self, handler: CDCHandler, mapping: SourceDestinationMapping) -> int:
        """Execute a mapping with custom query."""
        source_adapter = handler.source_adapter
        destination_adapter = handler.destination_adapter
        
        # Execute custom query
        logger.info(f"Executing custom query for mapping {mapping.name}")
        if mapping.custom_query is None:
            raise ValueError(f"custom_query must be provided for mapping {mapping.name}")
        data = source_adapter.execute_query(mapping.custom_query)
        
        # Apply column mapping if specified
        if mapping.column_mapping:
            data = self._apply_column_mapping(data, mapping.column_mapping)
        
        # Exclude columns if specified
        if mapping.exclude_columns:
            data = self._exclude_columns(data, mapping.exclude_columns)
        
        # Insert data to destination
        if data:
            destination_table = mapping.destination_table or mapping.destination.table
            destination_adapter.insert_data(destination_table, data)
        
        return len(data)
    
    def _execute_standard_sync(self, handler: CDCHandler, mapping: SourceDestinationMapping) -> int:
        """Execute standard CDC synchronization."""
        # Use the existing CDC handler sync method
        handler.sync()
        
        # Return approximate record count (this would need to be tracked in CDCHandler)
        return 0  # Placeholder - would need to modify CDCHandler to return count
    
    def _apply_column_mapping(self, data: List[Dict[str, Any]], column_mapping: Dict[str, str]) -> List[Dict[str, Any]]:
        """Apply column name mapping to data."""
        mapped_data = []
        for record in data:
            mapped_record = {}
            for source_col, dest_col in column_mapping.items():
                if source_col in record:
                    mapped_record[dest_col] = record[source_col]
            # Include unmapped columns as-is
            for col, value in record.items():
                if col not in column_mapping:
                    mapped_record[col] = value
            mapped_data.append(mapped_record)
        return mapped_data
    
    def _exclude_columns(self, data: List[Dict[str, Any]], exclude_columns: List[str]) -> List[Dict[str, Any]]:
        """Exclude specified columns from data."""
        filtered_data = []
        for record in data:
            filtered_record = {k: v for k, v in record.items() if k not in exclude_columns}
            filtered_data.append(filtered_record)
        return filtered_data
    
    def execute_all_mappings(self, parallel: Optional[bool] = None) -> List[MappingResult]:
        """Execute all enabled mappings.
        
        Args:
            parallel: Whether to execute in parallel (overrides config setting)
            
        Returns:
            List of mapping results
        """
        use_parallel = parallel if parallel is not None else self.config.parallel_execution
        enabled_mappings = [m.name for m in self.config.mappings if m.enabled]
        
        if not enabled_mappings:
            logger.warning("No enabled mappings to execute")
            return []
        
        logger.info(f"Executing {len(enabled_mappings)} mappings ({'parallel' if use_parallel else 'sequential'})")
        
        if use_parallel:
            return self._execute_parallel(enabled_mappings)
        else:
            return self._execute_sequential(enabled_mappings)
    
    def _execute_sequential(self, mapping_names: List[str]) -> List[MappingResult]:
        """Execute mappings sequentially."""
        results = []
        
        for mapping_name in mapping_names:
            if self.stop_event.is_set():
                logger.info("Stop event set, halting execution")
                break
                
            result = self.execute_mapping(mapping_name)
            results.append(result)
            
            if not result.success and self.config.stop_on_error:
                logger.error(f"Stopping execution due to error in mapping: {mapping_name}")
                break
        
        return results
    
    def _execute_parallel(self, mapping_names: List[str]) -> List[MappingResult]:
        """Execute mappings in parallel."""
        results = []
        
        with ThreadPoolExecutor(max_workers=self.config.max_workers) as executor:
            # Submit all mappings
            future_to_mapping = {
                executor.submit(self.execute_mapping, name): name 
                for name in mapping_names
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_mapping):
                mapping_name = future_to_mapping[future]
                
                try:
                    result = future.result()
                    results.append(result)
                    
                    if not result.success and self.config.stop_on_error:
                        logger.error(f"Cancelling remaining mappings due to error in: {mapping_name}")
                        # Cancel remaining futures
                        for f in future_to_mapping:
                            if not f.done():
                                f.cancel()
                        break
                        
                except Exception as e:
                    # This shouldn't happen as exceptions are caught in execute_mapping
                    logger.error(f"Unexpected error in mapping {mapping_name}: {e}")
                    result = MappingResult(mapping_name)
                    result.finish(success=False, error=e)
                    results.append(result)
        
        return results
    
    def run_continuous(self, interval_seconds: Optional[int] = None):
        """Run continuous synchronization for all mappings.
        
        Args:
            interval_seconds: Override interval from config
        """
        self.is_running = True
        self.stop_event.clear()
        
        sync_interval = interval_seconds or self.config.global_sync.interval_seconds
        
        logger.info(f"Starting continuous sync with {sync_interval}s interval")
        
        try:
            while not self.stop_event.is_set():
                start_time = time.time()
                
                # Execute all mappings
                results = self.execute_all_mappings()
                self.results.extend(results)
                
                # Log summary
                successful = sum(1 for r in results if r.success)
                total = len(results)
                logger.info(f"Sync cycle completed: {successful}/{total} mappings successful")
                
                # Wait for next cycle
                elapsed = time.time() - start_time
                sleep_time = max(0, sync_interval - elapsed)
                
                if sleep_time > 0:
                    logger.debug(f"Sleeping for {sleep_time:.1f}s until next cycle")
                    self.stop_event.wait(sleep_time)
                
        except KeyboardInterrupt:
            logger.info("Received interrupt signal, stopping...")
        finally:
            self.is_running = False
            logger.info("Continuous sync stopped")
    
    def stop(self):
        """Stop continuous execution."""
        logger.info("Stopping multi-CDC handler...")
        self.stop_event.set()
        self.is_running = False
    
    def get_summary(self) -> Dict[str, Any]:
        """Get execution summary."""
        total_executions = len(self.results)
        successful_executions = sum(1 for r in self.results if r.success)
        failed_executions = total_executions - successful_executions
        
        total_records = sum(r.records_processed for r in self.results if r.success)
        avg_duration = sum(r.duration_seconds for r in self.results) / max(1, total_executions)
        
        return {
            "config_name": self.config.name,
            "total_mappings": len(self.config.mappings),
            "enabled_mappings": len([m for m in self.config.mappings if m.enabled]),
            "total_executions": total_executions,
            "successful_executions": successful_executions,
            "failed_executions": failed_executions,
            "total_records_processed": total_records,
            "average_duration_seconds": round(avg_duration, 2),
            "is_running": self.is_running
        }
    
    def get_mapping_status(self) -> List[Dict[str, Any]]:
        """Get status of all mappings."""
        status_list = []
        
        for mapping in self.config.mappings:
            # Get latest result for this mapping
            mapping_results = [r for r in self.results if r.mapping_name == mapping.name]
            latest_result = mapping_results[-1] if mapping_results else None
            
            status = {
                "name": mapping.name,
                "enabled": mapping.enabled,
                "description": mapping.description,
                "source_type": mapping.source.type.value,
                "destination_type": mapping.destination.type.value,
                "source_table": mapping.source_table or mapping.source.table,
                "destination_table": mapping.destination_table or mapping.destination.table,
                "has_custom_query": mapping.custom_query is not None,
                "total_executions": len(mapping_results),
                "last_execution": {
                    "success": latest_result.success if latest_result else None,
                    "timestamp": latest_result.end_time.isoformat() if latest_result and latest_result.end_time else None,
                    "records_processed": latest_result.records_processed if latest_result else 0,
                    "duration_seconds": latest_result.duration_seconds if latest_result else 0,
                    "error": str(latest_result.error) if latest_result and latest_result.error else None
                } if latest_result else None
            }
            status_list.append(status)
        
        return status_list
