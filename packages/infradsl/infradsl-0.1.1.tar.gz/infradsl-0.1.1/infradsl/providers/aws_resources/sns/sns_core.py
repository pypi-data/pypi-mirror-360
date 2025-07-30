from ..base_resource import BaseAwsResource

class SNSCore(BaseAwsResource):
    """
    Core SNS class with main attributes and authentication logic.
    """
    def __init__(self, name: str):
        super().__init__(name)
        # Core attributes (to be filled in)
        self.topic_name = None
        self.topic_arn = None
        self.display_name = None
        self.fifo_topic = False
        self.content_based_deduplication = False
        self.delivery_policy = None
        self.tags = {}
        self.topic_exists = False
        self.sns_manager = None

    def _initialize_managers(self):
        """Initialize resource-specific managers"""
        pass

    def _post_authentication_setup(self):
        """Setup after authentication"""
        # Initialize SNS client
        self.sns_client = self.get_sns_client()
    
    def get_sns_client(self, region: str = None):
        """Get SNS client for this resource"""
        return self.get_client('sns', region)
    
    def get_client(self, service_name: str, region: str = None):
        """Get AWS client for specified service"""
        from ..auth_service import AwsAuthenticationService
        return AwsAuthenticationService.get_client(service_name, region)
    
    def create(self):
        """Create/update SNS topic - delegates to lifecycle mixin"""
        # Import here to avoid circular imports
        from .sns_lifecycle import SNSLifecycleMixin
        # Call the lifecycle mixin's create method
        return SNSLifecycleMixin.create(self)

    def destroy(self):
        """Destroy SNS topic - delegates to lifecycle mixin"""
        # Import here to avoid circular imports
        from .sns_lifecycle import SNSLifecycleMixin
        # Call the lifecycle mixin's destroy method
        return SNSLifecycleMixin.destroy(self)

    def preview(self):
        """Preview SNS topic configuration"""
        return {
            "resource_type": "AWS SNS Topic",
            "topic_name": self.topic_name or self.name,
            "topic_arn": self.topic_arn,
            "fifo_topic": self.fifo_topic,
            "content_based_deduplication": self.content_based_deduplication,
            "tags_count": len(self.tags),
            "estimated_monthly_cost": self._estimate_monthly_cost()
        }

    def _estimate_monthly_cost(self) -> str:
        """Estimate monthly cost for SNS topic"""
        # SNS pricing: $0.50 per 1M requests + delivery costs
        # Simplified calculation
        base_cost = 0.50  # Estimated for 1M requests
        
        total_cost = base_cost
        return f"${total_cost:.2f}" 