from ..base_resource import BaseAwsResource

class SQSCore(BaseAwsResource):
    """
    Core SQS class with main attributes and authentication logic.
    """
    def __init__(self, name: str):
        super().__init__(name)
        # Core attributes (to be filled in)
        self.queue_name = None
        self.queue_url = None
        self.queue_arn = None
        self.queue_type = None
        self.visibility_timeout_seconds = None
        self.message_retention_period = None
        self.maximum_message_size = None
        self.delay_seconds = None
        self.receive_message_wait_time = None
        self.dead_letter_queue_arn = None
        self.max_receive_count = None
        self.fifo_queue = False
        self.content_based_deduplication = False
        self.deduplication_scope = None
        self.fifo_throughput_limit = None
        self.tags = {}
        self.queue_exists = False
        self.sqs_manager = None

    def _initialize_managers(self):
        """Initialize resource-specific managers"""
        pass

    def _post_authentication_setup(self):
        """Setup after authentication"""
        # Initialize SQS client for queue management
        self.sqs_client = self.get_sqs_client()
    
    def create(self):
        """Create/update SQS queue - delegates to lifecycle mixin"""
        # Import here to avoid circular imports
        from .sqs_lifecycle import SQSLifecycleMixin
        # Call the lifecycle mixin's create method
        return SQSLifecycleMixin.create(self)

    def destroy(self):
        """Destroy SQS queue - delegates to lifecycle mixin"""
        # Import here to avoid circular imports
        from .sqs_lifecycle import SQSLifecycleMixin
        # Call the lifecycle mixin's destroy method
        return SQSLifecycleMixin.destroy(self)

    def preview(self):
        """Preview SQS queue configuration - delegates to lifecycle mixin"""
        # Import here to avoid circular imports
        from .sqs_lifecycle import SQSLifecycleMixin
        # Call the lifecycle mixin's preview method
        return SQSLifecycleMixin.preview(self)
    
    def get_sqs_client(self, region: str = None):
        """Get SQS client for this resource"""
        return self.get_client('sqs', region)
    
    def get_client(self, service_name: str, region: str = None):
        """Get AWS client for specified service"""
        from ..auth_service import AwsAuthenticationService
        return AwsAuthenticationService.get_client(service_name, region) 