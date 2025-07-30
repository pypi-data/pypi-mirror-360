from typing import Dict, Any, Union

class SQSConfigurationMixin:
    """
    Mixin for SQS chainable configuration methods.
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Initialize configuration-specific attributes if not already set
        if not hasattr(self, 'tags'):
            self.tags = {}
    
    def queue_name(self, name: str):
        """Set the queue name"""
        self.queue_name = name
        return self

    def standard(self):
        """Configure as standard queue (default)"""
        self.queue_type = 'standard'
        self.fifo_queue = False
        return self

    def fifo(self, content_based_deduplication: bool = True):
        """Configure as FIFO queue"""
        self.queue_type = 'fifo'
        self.fifo_queue = True
        self.content_based_deduplication = content_based_deduplication
        # FIFO queues must end with .fifo
        if not self.name.endswith('.fifo'):
            self.queue_name = f"{self.name}.fifo"
        return self

    def visibility_timeout(self, seconds: int):
        """Set the visibility timeout in seconds (0-43200, default: 30)"""
        if not 0 <= seconds <= 43200:
            raise ValueError("Visibility timeout must be between 0 and 43200 seconds")
        self.visibility_timeout_seconds = seconds
        return self

    def message_retention(self, days: int):
        """Set the message retention period in days (1-14, default: 4)"""
        if not 1 <= days <= 14:
            raise ValueError("Message retention must be between 1 and 14 days")
        self.message_retention_period = days * 24 * 60 * 60  # Convert to seconds
        return self

    def maximum_message_size(self, size_kb: int):
        """Set the maximum message size in KB (1-256, default: 256)"""
        if not 1 <= size_kb <= 256:
            raise ValueError("Maximum message size must be between 1 and 256 KB")
        self.maximum_message_size = size_kb * 1024  # Convert to bytes
        return self

    def delay_seconds(self, seconds: int):
        """Set the delay seconds (0-900, default: 0)"""
        if not 0 <= seconds <= 900:
            raise ValueError("Delay seconds must be between 0 and 900")
        self.delay_seconds = seconds
        return self

    def long_polling(self, seconds: int):
        """Set the long polling wait time in seconds (0-20, default: 0)"""
        if not 0 <= seconds <= 20:
            raise ValueError("Long polling wait time must be between 0 and 20 seconds")
        self.receive_message_wait_time = seconds
        return self

    def dead_letter_queue(self, dlq_arn: str, max_receive_count: int = 3):
        """Configure dead letter queue"""
        if not 1 <= max_receive_count <= 1000:
            raise ValueError("Max receive count must be between 1 and 1000")
        self.dead_letter_queue_arn = dlq_arn
        self.max_receive_count = max_receive_count
        return self

    def high_throughput_fifo(self):
        """Enable high throughput for FIFO queues"""
        if not self.fifo_queue:
            raise ValueError("High throughput can only be enabled for FIFO queues")
        self.fifo_throughput_limit = 'perMessageGroupId'
        self.deduplication_scope = 'messageGroup'
        return self

    def standard_fifo(self):
        """Use standard FIFO settings (lower throughput, strict ordering)"""
        if not self.fifo_queue:
            raise ValueError("Standard FIFO can only be set for FIFO queues")
        self.fifo_throughput_limit = 'perQueue'
        self.deduplication_scope = 'queue'
        return self

    # Preset configurations
    def microservice_queue(self):
        """Standard configuration for microservice communication"""
        return self.standard().visibility_timeout(30).message_retention(4).long_polling(20)

    def batch_processing_queue(self):
        """Configuration optimized for batch processing"""
        return self.standard().visibility_timeout(300).message_retention(14).maximum_message_size(256)

    def dlq_setup(self, main_queue_arn: str):
        """Configure as a dead letter queue"""
        return self.standard().message_retention(14).visibility_timeout(60)

    def event_queue(self):
        """Configuration for event-driven architectures"""
        return self.standard().delay_seconds(0).long_polling(20).visibility_timeout(60)

    def fifo_transactional(self):
        """FIFO queue for transactional processing"""
        return self.fifo().standard_fifo().visibility_timeout(120).message_retention(7)

    def fifo_high_volume(self):
        """FIFO queue for high volume processing"""
        return self.fifo().high_throughput_fifo().visibility_timeout(30).message_retention(4)

    # Security and access control
    def encrypt_in_transit(self):
        """Enable encryption in transit (HTTPS)"""
        # This is automatically enabled for SQS
        return self

    def encrypt_at_rest(self, kms_key_id: str = None):
        """Enable encryption at rest with optional KMS key"""
        self.kms_master_key_id = kms_key_id or 'alias/aws/sqs'
        return self

    def tag(self, key: str, value: str):
        """Add a tag to the queue"""
        self.tags[key] = value
        return self

    def tags_dict(self, tags_dict: Dict[str, str]):
        """Add multiple tags to the queue"""
        self.tags.update(tags_dict)
        return self

    # Monitoring and alerting
    def enable_cloudwatch_metrics(self):
        """Enable detailed CloudWatch metrics"""
        # This would be handled in the actual AWS implementation
        return self

    def redrive_policy(self, source_queue_arn: str, max_receive_count: int = 3):
        """Set up redrive policy for dead letter queue handling"""
        return self.dead_letter_queue(source_queue_arn, max_receive_count)