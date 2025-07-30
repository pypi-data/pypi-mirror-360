"""
AWS SQS Complete Implementation

Combines all SQS functionality through multiple inheritance:
- SQSCore: Core attributes and authentication
- SQSConfigurationMixin: Chainable configuration methods
- SQSLifecycleMixin: Lifecycle operations (create/destroy/preview)
"""

from .sqs_core import SQSCore
from .sqs_configuration import SQSConfigurationMixin
from .sqs_lifecycle import SQSLifecycleMixin


class SQS(SQSLifecycleMixin, SQSConfigurationMixin, SQSCore):
    """
    Complete AWS SQS implementation for message queuing.
    
    This class combines:
    - Queue configuration methods (standard/FIFO, timeouts, encryption)
    - Queue lifecycle management (create, destroy, preview)
    - Dead letter queue and retry policies
    - Performance optimization features
    - Rails-like method chaining for fluent API
    """
    
    def __init__(self, name: str):
        """Initialize SQS instance for message queue management"""
        super().__init__(name)
        
        # Additional attributes specific to the combined class
        self.deployment_ready = False
        self.message_count = 0
    
    def validate_configuration(self):
        """Validate the current SQS configuration"""
        errors = []
        warnings = []
        
        # Validate FIFO queue requirements
        if self.fifo_queue:
            if not self.name.endswith('.fifo') and not (self.queue_name and self.queue_name.endswith('.fifo')):
                errors.append("FIFO queue names must end with '.fifo'")
            
            if hasattr(self, 'high_throughput_enabled') and self.content_based_deduplication:
                warnings.append("High throughput FIFO with content-based deduplication may have lower performance")
        
        # Validate timeouts
        if self.visibility_timeout_seconds and self.visibility_timeout_seconds > 43200:
            errors.append("Visibility timeout cannot exceed 43200 seconds (12 hours)")
        
        if self.receive_message_wait_time and self.receive_message_wait_time > 20:
            errors.append("Long polling wait time cannot exceed 20 seconds")
        
        # Validate dead letter queue
        if self.dead_letter_queue_arn and not self.max_receive_count:
            errors.append("Dead letter queue requires max_receive_count to be set")
        
        # Validate message size
        if self.maximum_message_size and self.maximum_message_size > 262144:  # 256KB
            errors.append("Maximum message size cannot exceed 256KB")
        
        if errors:
            raise ValueError(f"Configuration validation failed: {', '.join(errors)}")
        
        if warnings:
            print(f"⚠️  Configuration warnings:")
            for warning in warnings:
                print(f"   - {warning}")
        
        self.deployment_ready = True
        return True
    
    def get_queue_info(self):
        """Get complete information about the SQS queue"""
        return {
            'queue_name': self.queue_name or self.name,
            'queue_url': self.queue_url,
            'queue_arn': self.queue_arn,
            'queue_type': self.queue_type or 'standard',
            'fifo_queue': self.fifo_queue,
            'visibility_timeout': self.visibility_timeout_seconds or 30,
            'message_retention_period': self.message_retention_period or (4 * 24 * 60 * 60),
            'maximum_message_size': self.maximum_message_size or (256 * 1024),
            'delay_seconds': self.delay_seconds or 0,
            'receive_message_wait_time': self.receive_message_wait_time or 0,
            'dead_letter_queue_configured': bool(self.dead_letter_queue_arn),
            'encryption_enabled': hasattr(self, 'kms_master_key_id') and bool(self.kms_master_key_id),
            'tags_count': len(self.tags),
            'queue_exists': self.queue_exists,
            'deployment_ready': self.deployment_ready,
            'estimated_monthly_cost': self._estimate_monthly_cost() if hasattr(self, '_estimate_monthly_cost') else '$0.40'
        }
    
    def clone(self, new_name: str):
        """Create a copy of this queue with a new name"""
        cloned_queue = SQS(new_name)
        cloned_queue.queue_type = self.queue_type
        cloned_queue.fifo_queue = self.fifo_queue
        cloned_queue.visibility_timeout_seconds = self.visibility_timeout_seconds
        cloned_queue.message_retention_period = self.message_retention_period
        cloned_queue.maximum_message_size = self.maximum_message_size
        cloned_queue.delay_seconds = self.delay_seconds
        cloned_queue.receive_message_wait_time = self.receive_message_wait_time
        cloned_queue.content_based_deduplication = self.content_based_deduplication
        cloned_queue.tags = self.tags.copy()
        return cloned_queue
    
    def export_configuration(self):
        """Export queue configuration for backup or migration"""
        return {
            'metadata': {
                'queue_name': self.queue_name or self.name,
                'queue_type': self.queue_type or 'standard',
                'fifo_queue': self.fifo_queue,
                'exported_at': 'Mock timestamp'
            },
            'configuration': {
                'visibility_timeout': self.visibility_timeout_seconds or 30,
                'message_retention_period': self.message_retention_period or (4 * 24 * 60 * 60),
                'maximum_message_size': self.maximum_message_size or (256 * 1024),
                'delay_seconds': self.delay_seconds or 0,
                'receive_message_wait_time': self.receive_message_wait_time or 0,
                'dead_letter_queue_arn': self.dead_letter_queue_arn,
                'max_receive_count': self.max_receive_count,
                'content_based_deduplication': self.content_based_deduplication if self.fifo_queue else None,
                'kms_master_key_id': getattr(self, 'kms_master_key_id', None)
            },
            'tags': self.tags
        }
    
    def import_configuration(self, config_data: dict):
        """Import queue configuration from exported data"""
        if 'configuration' in config_data:
            config = config_data['configuration']
            self.visibility_timeout_seconds = config.get('visibility_timeout')
            self.message_retention_period = config.get('message_retention_period')
            self.maximum_message_size = config.get('maximum_message_size')
            self.delay_seconds = config.get('delay_seconds')
            self.receive_message_wait_time = config.get('receive_message_wait_time')
            self.dead_letter_queue_arn = config.get('dead_letter_queue_arn')
            self.max_receive_count = config.get('max_receive_count')
            self.content_based_deduplication = config.get('content_based_deduplication')
            if config.get('kms_master_key_id'):
                self.kms_master_key_id = config['kms_master_key_id']
        
        if 'tags' in config_data:
            self.tags = config_data['tags']
        
        return self


# Convenience functions for creating SQS instances
def create_queue(name: str, queue_type: str = 'standard') -> SQS:
    """Create a new SQS queue with specified type"""
    queue = SQS(name)
    if queue_type == 'fifo':
        queue.fifo()
    else:
        queue.standard()
    return queue

def create_microservice_queue(name: str) -> SQS:
    """Create a queue optimized for microservice communication"""
    return SQS(name).microservice_queue()

def create_batch_queue(name: str) -> SQS:
    """Create a queue optimized for batch processing"""
    return SQS(name).batch_processing_queue()

def create_fifo_queue(name: str, high_throughput: bool = False) -> SQS:
    """Create a FIFO queue with optional high throughput"""
    queue = SQS(name).fifo()
    if high_throughput:
        queue.high_throughput_fifo()
    else:
        queue.standard_fifo()
    return queue