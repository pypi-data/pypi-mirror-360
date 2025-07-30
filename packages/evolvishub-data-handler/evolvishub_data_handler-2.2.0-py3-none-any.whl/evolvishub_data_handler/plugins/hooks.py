"""
Event hooks and callbacks for extensible processing.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Callable
from enum import Enum
from .base import BasePlugin, PluginMetadata, PluginType
from loguru import logger


class EventType(str, Enum):
    """Types of events that can trigger hooks."""
    SYNC_START = "sync_start"
    SYNC_END = "sync_end"
    READ_START = "read_start"
    READ_END = "read_end"
    WRITE_START = "write_start"
    WRITE_END = "write_end"
    ERROR = "error"
    BATCH_PROCESSED = "batch_processed"
    WATERMARK_UPDATED = "watermark_updated"


class EventHook(ABC):
    """Base class for event hooks."""
    
    @abstractmethod
    def handle(self, event_type: EventType, data: Dict[str, Any]) -> None:
        """Handle an event."""
        pass
    
    @abstractmethod
    def get_name(self) -> str:
        """Get hook name."""
        pass
    
    def get_supported_events(self) -> List[EventType]:
        """Get list of supported event types."""
        return list(EventType)


class HookPlugin(BasePlugin):
    """Plugin for event hooks and callbacks."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.hooks: Dict[EventType, List[EventHook]] = {}
        self.global_hooks: List[EventHook] = []
    
    @property
    def metadata(self) -> PluginMetadata:
        """Return hook plugin metadata."""
        return PluginMetadata(
            name="HookPlugin",
            version="1.0.0",
            description="Event hooks and callbacks plugin",
            author="Evolvishub",
            plugin_type=PluginType.HOOK
        )
    
    def initialize(self) -> None:
        """Initialize hooks."""
        hooks_config = self.config.get('hooks', [])
        
        for hook_config in hooks_config:
            hook_type = hook_config.get('type')
            hook_params = hook_config.get('params', {})
            events = hook_config.get('events', [])
            
            hook = self._create_hook(hook_type, hook_params)
            if hook:
                if events:
                    # Register for specific events
                    for event_str in events:
                        try:
                            event_type = EventType(event_str)
                            self.register_hook(event_type, hook)
                        except ValueError:
                            logger.warning(f"Unknown event type: {event_str}")
                else:
                    # Register as global hook
                    self.register_global_hook(hook)
                
                logger.info(f"Added hook: {hook.get_name()}")
    
    def cleanup(self) -> None:
        """Cleanup hook resources."""
        self.hooks.clear()
        self.global_hooks.clear()
    
    def register_hook(self, event_type: EventType, hook: EventHook) -> None:
        """Register a hook for specific event type."""
        if event_type not in self.hooks:
            self.hooks[event_type] = []
        self.hooks[event_type].append(hook)
    
    def register_global_hook(self, hook: EventHook) -> None:
        """Register a global hook for all events."""
        self.global_hooks.append(hook)
    
    def trigger_event(self, event_type: EventType, data: Dict[str, Any]) -> None:
        """Trigger an event and call all registered hooks."""
        # Call specific hooks
        if event_type in self.hooks:
            for hook in self.hooks[event_type]:
                try:
                    hook.handle(event_type, data)
                except Exception as e:
                    logger.error(f"Hook {hook.get_name()} failed for event {event_type}: {e}")
        
        # Call global hooks
        for hook in self.global_hooks:
            try:
                if event_type in hook.get_supported_events():
                    hook.handle(event_type, data)
            except Exception as e:
                logger.error(f"Global hook {hook.get_name()} failed for event {event_type}: {e}")
    
    def _create_hook(self, hook_type: str, params: Dict[str, Any]) -> Optional[EventHook]:
        """Create hook instance based on type."""
        hook_map = {
            'webhook': WebhookHook,
            'email': EmailHook,
            'slack': SlackHook,
            'file_logger': FileLoggerHook,
            'metrics_collector': MetricsCollectorHook,
            'custom_function': CustomFunctionHook,
        }
        
        hook_class = hook_map.get(hook_type)
        if hook_class:
            return hook_class(params)
        
        logger.warning(f"Unknown hook type: {hook_type}")
        return None


class WebhookHook(EventHook):
    """Hook that sends HTTP webhooks."""
    
    def __init__(self, params: Dict[str, Any]):
        self.webhook_url = params.get('url')
        self.headers = params.get('headers', {})
        self.timeout = params.get('timeout', 30)
    
    def handle(self, event_type: EventType, data: Dict[str, Any]) -> None:
        """Send webhook."""
        if not self.webhook_url:
            return
        
        try:
            import requests
            
            payload = {
                'event_type': event_type.value,
                'timestamp': data.get('timestamp'),
                'data': data
            }
            
            response = requests.post(
                self.webhook_url,
                json=payload,
                headers=self.headers,
                timeout=self.timeout
            )
            response.raise_for_status()
            
            logger.debug(f"Webhook sent for event {event_type}")
            
        except ImportError:
            logger.error("requests package required for webhook hook")
        except Exception as e:
            logger.error(f"Webhook failed: {e}")
    
    def get_name(self) -> str:
        return "WebhookHook"


class EmailHook(EventHook):
    """Hook that sends email notifications."""
    
    def __init__(self, params: Dict[str, Any]):
        self.smtp_server = params.get('smtp_server')
        self.smtp_port = params.get('smtp_port', 587)
        self.username = params.get('username')
        self.password = params.get('password')
        self.from_email = params.get('from_email')
        self.to_emails = params.get('to_emails', [])
        self.subject_template = params.get('subject_template', 'CDC Event: {event_type}')
    
    def handle(self, event_type: EventType, data: Dict[str, Any]) -> None:
        """Send email notification."""
        if not all([self.smtp_server, self.username, self.password, self.from_email, self.to_emails]):
            logger.warning("Email hook not properly configured")
            return
        
        try:
            import smtplib
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart
            
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.from_email
            msg['To'] = ', '.join(self.to_emails)
            msg['Subject'] = self.subject_template.format(event_type=event_type.value)
            
            # Create body
            body = f"""
            Event: {event_type.value}
            Timestamp: {data.get('timestamp')}
            
            Details:
            {data}
            """
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Send email
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.username, self.password)
            server.send_message(msg)
            server.quit()
            
            logger.debug(f"Email sent for event {event_type}")
            
        except Exception as e:
            logger.error(f"Email hook failed: {e}")
    
    def get_name(self) -> str:
        return "EmailHook"


class SlackHook(EventHook):
    """Hook that sends Slack notifications."""
    
    def __init__(self, params: Dict[str, Any]):
        self.webhook_url = params.get('webhook_url')
        self.channel = params.get('channel')
        self.username = params.get('username', 'CDC Bot')
    
    def handle(self, event_type: EventType, data: Dict[str, Any]) -> None:
        """Send Slack notification."""
        if not self.webhook_url:
            return
        
        try:
            import requests
            
            # Create Slack message
            message = {
                'channel': self.channel,
                'username': self.username,
                'text': f"CDC Event: {event_type.value}",
                'attachments': [
                    {
                        'color': 'good' if event_type != EventType.ERROR else 'danger',
                        'fields': [
                            {
                                'title': 'Event Type',
                                'value': event_type.value,
                                'short': True
                            },
                            {
                                'title': 'Timestamp',
                                'value': data.get('timestamp'),
                                'short': True
                            }
                        ]
                    }
                ]
            }
            
            response = requests.post(self.webhook_url, json=message)
            response.raise_for_status()
            
            logger.debug(f"Slack notification sent for event {event_type}")
            
        except ImportError:
            logger.error("requests package required for Slack hook")
        except Exception as e:
            logger.error(f"Slack hook failed: {e}")
    
    def get_name(self) -> str:
        return "SlackHook"


class FileLoggerHook(EventHook):
    """Hook that logs events to a file."""
    
    def __init__(self, params: Dict[str, Any]):
        self.log_file = params.get('log_file', 'cdc_events.log')
        self.log_format = params.get('format', '{timestamp} - {event_type} - {data}')
    
    def handle(self, event_type: EventType, data: Dict[str, Any]) -> None:
        """Log event to file."""
        try:
            from datetime import datetime
            
            timestamp = datetime.now().isoformat()
            log_entry = self.log_format.format(
                timestamp=timestamp,
                event_type=event_type.value,
                data=data
            )
            
            with open(self.log_file, 'a') as f:
                f.write(log_entry + '\n')
                
        except Exception as e:
            logger.error(f"File logger hook failed: {e}")
    
    def get_name(self) -> str:
        return "FileLoggerHook"


class MetricsCollectorHook(EventHook):
    """Hook that collects metrics."""
    
    def __init__(self, params: Dict[str, Any]):
        self.metrics_file = params.get('metrics_file', 'cdc_metrics.json')
        self.metrics = {}
    
    def handle(self, event_type: EventType, data: Dict[str, Any]) -> None:
        """Collect metrics."""
        try:
            import json
            from datetime import datetime
            
            # Update metrics
            if event_type.value not in self.metrics:
                self.metrics[event_type.value] = {
                    'count': 0,
                    'last_occurrence': None
                }
            
            self.metrics[event_type.value]['count'] += 1
            self.metrics[event_type.value]['last_occurrence'] = datetime.now().isoformat()
            
            # Add specific metrics based on event type
            if event_type == EventType.BATCH_PROCESSED:
                records_count = data.get('records_count', 0)
                if 'total_records_processed' not in self.metrics:
                    self.metrics['total_records_processed'] = 0
                self.metrics['total_records_processed'] += records_count
            
            # Save metrics to file
            with open(self.metrics_file, 'w') as f:
                json.dump(self.metrics, f, indent=2)
                
        except Exception as e:
            logger.error(f"Metrics collector hook failed: {e}")
    
    def get_name(self) -> str:
        return "MetricsCollectorHook"


class CustomFunctionHook(EventHook):
    """Hook that executes custom Python function."""
    
    def __init__(self, params: Dict[str, Any]):
        self.function_code = params.get('function')
        self.function: Optional[Callable] = None
        
        if self.function_code:
            try:
                # Create function from code string
                local_vars = {}
                exec(f"def custom_hook(event_type, data):\n{self.function_code}", globals(), local_vars)
                self.function = local_vars['custom_hook']
            except Exception as e:
                logger.error(f"Failed to create custom hook function: {e}")
    
    def handle(self, event_type: EventType, data: Dict[str, Any]) -> None:
        """Execute custom function."""
        if not self.function:
            return
        
        try:
            self.function(event_type, data)
        except Exception as e:
            logger.error(f"Custom hook function failed: {e}")
    
    def get_name(self) -> str:
        return "CustomFunctionHook"
