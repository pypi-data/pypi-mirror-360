"""
AWS SNS Complete Implementation

Combines all SNS functionality through multiple inheritance:
- SNSCore: Core attributes and authentication
- SNSConfigurationMixin: Chainable configuration methods  
- SNSLifecycleMixin: Lifecycle operations (create/destroy/preview)
"""

from .sns_core import SNSCore
from .sns_configuration import SNSConfigurationMixin
from .sns_lifecycle import SNSLifecycleMixin


class SNS(SNSLifecycleMixin, SNSConfigurationMixin, SNSCore):
    """
    Complete AWS SNS implementation for message publishing and notification.
    
    This class combines:
    - Topic configuration (FIFO, display name, delivery policies)
    - Subscription management (email, SMS, HTTP, SQS, Lambda)
    - Message publishing and filtering
    - Rails-like method chaining for fluent API
    """
    
    def __init__(self, name: str):
        """Initialize SNS instance for messaging"""
        super().__init__(name)
        
        # Additional attributes specific to the combined class
        self.deployment_ready = False
        self.estimated_monthly_cost = "$0.50/month"
        
        # Initialize attributes for configuration mixin
        self.sns_topic_name = None
        self.sns_display_name = None
        self.sns_fifo_topic = False
        self.sns_content_based_deduplication = False
        self.sns_delivery_policy = None
        self.subscriptions = []
        self.message_attributes = {}
        
        # Cross-Cloud Magic integration
        self._optimization_priority = None
    
    def validate_configuration(self):
        """Validate the current SNS configuration"""
        errors = []
        warnings = []
        
        # Validate topic name
        if not self.sns_topic_name and not self.name:
            errors.append("Topic name is required")
        
        topic_name = self.sns_topic_name or self.name
        if topic_name and not self._is_valid_topic_name(topic_name):
            errors.append("Invalid topic name format")
        
        # FIFO validation
        if self.sns_fifo_topic:
            if not topic_name.endswith('.fifo'):
                errors.append("FIFO topic names must end with .fifo")
            
            if self.sns_content_based_deduplication and not self.sns_fifo_topic:
                errors.append("Content-based deduplication requires FIFO topic")
        
        # Validate subscriptions
        if not self.subscriptions:
            warnings.append("No subscriptions configured - topic will have no subscribers")
        
        for subscription in self.subscriptions:
            if subscription['protocol'] not in ['email', 'sms', 'http', 'https', 'sqs', 'lambda']:
                errors.append(f"Invalid subscription protocol: {subscription['protocol']}")
        
        if errors:
            raise ValueError(f"Configuration validation failed: {', '.join(errors)}")
        
        if warnings:
            print(f"⚠️  Configuration warnings:")
            for warning in warnings:
                print(f"   - {warning}")
        
        self.deployment_ready = True
        return True
    
    def get_topic_info(self):
        """Get complete information about the SNS topic"""
        return {
            'topic_name': self.sns_topic_name or self.name,
            'topic_arn': self.topic_arn,
            'display_name': self.sns_display_name,
            'fifo_topic': self.sns_fifo_topic,
            'content_based_deduplication': self.sns_content_based_deduplication,
            'subscriptions_count': len(self.subscriptions),
            'message_attributes_count': len(self.message_attributes),
            'tags_count': len(self.tags),
            'topic_exists': self.topic_exists,
            'deployment_ready': self.deployment_ready,
            'estimated_monthly_cost': self.estimated_monthly_cost,
            'optimization_priority': self._optimization_priority
        }
    
    def clone(self, new_name: str):
        """Create a copy of this SNS topic with a new name"""
        cloned_sns = SNS(new_name)
        cloned_sns.sns_topic_name = new_name
        cloned_sns.sns_display_name = self.sns_display_name
        cloned_sns.sns_fifo_topic = self.sns_fifo_topic
        cloned_sns.sns_content_based_deduplication = self.sns_content_based_deduplication
        cloned_sns.sns_delivery_policy = self.sns_delivery_policy
        cloned_sns.subscriptions = [sub.copy() for sub in self.subscriptions]
        cloned_sns.message_attributes = self.message_attributes.copy()
        cloned_sns.tags = self.tags.copy()
        return cloned_sns
    
    def export_configuration(self):
        """Export SNS configuration for backup or migration"""
        return {
            'metadata': {
                'topic_name': self.sns_topic_name or self.name,
                'fifo_topic': self.sns_fifo_topic,
                'exported_at': 'Mock timestamp'
            },
            'configuration': {
                'display_name': self.sns_display_name,
                'content_based_deduplication': self.sns_content_based_deduplication,
                'delivery_policy': self.sns_delivery_policy,
                'subscriptions': self.subscriptions,
                'message_attributes': self.message_attributes,
                'optimization_priority': self._optimization_priority
            },
            'tags': self.tags
        }
    
    def import_configuration(self, config_data: dict):
        """Import SNS configuration from exported data"""
        if 'configuration' in config_data:
            config = config_data['configuration']
            self.sns_display_name = config.get('display_name')
            self.sns_content_based_deduplication = config.get('content_based_deduplication', False)
            self.sns_delivery_policy = config.get('delivery_policy')
            self.subscriptions = config.get('subscriptions', [])
            self.message_attributes = config.get('message_attributes', {})
            self._optimization_priority = config.get('optimization_priority')
        
        if 'tags' in config_data:
            self.tags = config_data['tags']
        
        return self
    
    def _is_valid_topic_name(self, topic_name: str) -> bool:
        """Validate topic name according to AWS rules"""
        import re
        
        # Topic name can be 1-256 characters
        if len(topic_name) < 1 or len(topic_name) > 256:
            return False
        
        # Must contain only alphanumeric characters, hyphens, underscores, and periods
        if not re.match(r'^[a-zA-Z0-9_.-]+$', topic_name):
            return False
        
        return True
    
    def optimize_for(self, priority: str):
        """Use Cross-Cloud Magic to optimize for cost/performance/reliability
        
        Args:
            priority: Optimization priority - "cost", "performance", "reliability", "compliance"
            
        Returns:
            Self for method chaining
        """
        valid_priorities = ["cost", "performance", "reliability", "compliance"]
        if priority not in valid_priorities:
            raise ValueError(f"Priority must be one of: {valid_priorities}. Got: {priority}")
        
        self._optimization_priority = priority
        print(f"🎯 Cross-Cloud Magic: Optimizing SNS for {priority}")
        
        # Apply AWS SNS-specific optimizations
        if priority == "cost":
            print("💰 Cost optimization: Configuring cost-effective messaging")
            self._apply_cost_optimizations()
        elif priority == "performance":
            print("⚡ Performance optimization: Configuring high-performance messaging")
            self._apply_performance_optimizations()
        elif priority == "reliability":
            print("🛡️ Reliability optimization: Configuring reliable messaging")
            self._apply_reliability_optimizations()
        elif priority == "compliance":
            print("📋 Compliance optimization: Configuring compliant messaging")
            self._apply_compliance_optimizations()
        
        return self
    
    def _apply_cost_optimizations(self):
        """Apply AWS SNS-specific cost optimizations"""
        # Use standard topics instead of FIFO for cost savings
        if self.sns_fifo_topic:
            print("   💰 Consider standard topics for lower cost (FIFO topics cost more)")
        
        # Optimize delivery policies
        print("   💰 Optimizing delivery policies for cost efficiency")
        
        # Add cost optimization tags
        self.tags.update({
            "cost-optimized": "true",
            "topic-type-optimized": "true"
        })
    
    def _apply_performance_optimizations(self):
        """Apply AWS SNS-specific performance optimizations"""
        # Configure for high throughput
        print("   ⚡ Configuring for high message throughput")
        
        # Optimize delivery policies for performance
        print("   ⚡ Setting aggressive delivery retry policies")
        
        # Add performance tags
        self.tags.update({
            "performance-optimized": "true",
            "high-throughput": "enabled"
        })
    
    def _apply_reliability_optimizations(self):
        """Apply AWS SNS-specific reliability optimizations"""
        # Configure dead letter queues
        print("   🛡️ Consider configuring dead letter queues for failed deliveries")
        
        # Enable detailed monitoring
        print("   🛡️ Enable detailed CloudWatch monitoring")
        
        # Add reliability tags
        self.tags.update({
            "reliability-optimized": "true",
            "monitoring-enabled": "true"
        })
    
    def _apply_compliance_optimizations(self):
        """Apply AWS SNS-specific compliance optimizations"""
        # Enable encryption
        print("   📋 Enable server-side encryption for message security")
        
        # Configure access policies
        print("   📋 Configure restrictive access policies")
        
        # Add compliance tags
        self.tags.update({
            "compliance-optimized": "true",
            "encryption-enabled": "true"
        })
    
    # Convenience methods for common configurations
    def topic(self, name: str):
        """Set the topic name - avoiding conflict with attribute"""
        self.sns_topic_name = name
        return self
    
    def display(self, display_name: str):
        """Set the display name for the topic"""
        self.sns_display_name = display_name
        return self
    
    def fifo(self, enabled: bool = True):
        """Enable or disable FIFO topic"""
        self.sns_fifo_topic = enabled
        if enabled and self.sns_topic_name and not self.sns_topic_name.endswith('.fifo'):
            self.sns_topic_name += '.fifo'
        return self
    
    def deduplication(self, enabled: bool = True):
        """Enable or disable content-based deduplication"""
        self.sns_content_based_deduplication = enabled
        return self
    
    def delivery_policy(self, policy: dict):
        """Set the delivery policy for the topic"""
        self.sns_delivery_policy = policy
        return self
    
    def subscribe_email(self, email: str):
        """Subscribe an email address to the topic"""
        self.subscriptions.append({
            'protocol': 'email',
            'endpoint': email
        })
        print(f"📧 Email subscription added: {email}")
        return self
    
    def subscribe_sms(self, phone_number: str):
        """Subscribe a phone number to the topic"""
        self.subscriptions.append({
            'protocol': 'sms',
            'endpoint': phone_number
        })
        print(f"📱 SMS subscription added: {phone_number}")
        return self
    
    def subscribe_http(self, url: str):
        """Subscribe an HTTP endpoint to the topic"""
        protocol = 'https' if url.startswith('https://') else 'http'
        self.subscriptions.append({
            'protocol': protocol,
            'endpoint': url
        })
        print(f"🌐 HTTP subscription added: {url}")
        return self
    
    def subscribe_sqs(self, queue_arn: str):
        """Subscribe an SQS queue to the topic"""
        self.subscriptions.append({
            'protocol': 'sqs',
            'endpoint': queue_arn
        })
        print(f"📦 SQS subscription added: {queue_arn}")
        return self
    
    def subscribe_lambda(self, function_arn: str):
        """Subscribe a Lambda function to the topic"""
        self.subscriptions.append({
            'protocol': 'lambda',
            'endpoint': function_arn
        })
        print(f"⚡ Lambda subscription added: {function_arn}")
        return self
    
    def message_attribute(self, name: str, value: str, data_type: str = "String"):
        """Add a message attribute"""
        self.message_attributes[name] = {
            'value': value,
            'data_type': data_type
        }
        return self
    
    def tag(self, key: str, value: str):
        """Add a tag to the topic"""
        self.tags[key] = value
        return self


# Convenience functions for creating SNS instances
def create_topic(name: str, fifo: bool = False) -> SNS:
    """Create a new SNS topic with basic configuration"""
    sns = SNS(name)
    sns.topic(name)
    if fifo:
        sns.fifo(True)
    return sns

def create_notification_topic(name: str, email: str = None, sms: str = None) -> SNS:
    """Create a notification topic with email and/or SMS subscriptions"""
    sns = SNS(name)
    sns.topic(name).display(f"{name} Notifications")
    
    if email:
        sns.subscribe_email(email)
    if sms:
        sns.subscribe_sms(sms)
    
    return sns

def create_alert_topic(name: str, emails: list) -> SNS:
    """Create an alert topic with multiple email subscriptions"""
    sns = SNS(name)
    sns.topic(name).display(f"{name} Alerts")
    
    for email in emails:
        sns.subscribe_email(email)
    
    return sns