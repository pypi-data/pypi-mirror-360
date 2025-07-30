"""
GCP PubSub Configuration Mixin

Chainable configuration methods for Google Cloud Pub/Sub.
Provides Rails-like method chaining for fluent topic and subscription configuration.
"""

from typing import Dict, Any, List, Optional


class PubSubConfigurationMixin:
    """
    Mixin for Pub/Sub configuration methods.
    
    This mixin provides chainable configuration methods for:
    - Topic settings (retention, ordering, encryption)
    - Subscription configuration (pull/push, acknowledgment, dead letter)
    - Message flow patterns (fan-out, queue, event streaming)
    - Security and access controls
    """
    
    def description(self, description: str):
        """Set description for the Pub/Sub topic"""
        self.topic_description = description
        return self
        
    def project(self, project_id: str):
        """Set project ID for Pub/Sub operations - Rails convenience"""
        self.project_id = project_id
        if self.project_id:
            self.topic_path = f"projects/{self.project_id}/topics/{self.topic_name}"
        return self
        
    # Topic configuration
    def retention(self, duration: str):
        """Set message retention duration (e.g., '604800s' for 7 days)"""
        if not self._is_valid_retention_duration(duration):
            print(f"⚠️  Warning: Invalid retention duration '{duration}'. Must be between 10 minutes and 7 days")
        self.message_retention_duration = duration
        return self
        
    def retention_days(self, days: int):
        """Set message retention in days (convenience method)"""
        if not (0.007 <= days <= 7):  # 10 minutes to 7 days
            print(f"⚠️  Warning: Invalid retention days {days}. Must be between 0.007 and 7")
        seconds = int(days * 24 * 60 * 60)
        self.message_retention_duration = f"{seconds}s"
        return self
        
    def ordered_delivery(self, enabled: bool = True):
        """Enable message ordering for FIFO delivery"""
        self.message_ordering_enabled = enabled
        return self
        
    def enable_message_ordering(self, enabled: bool = True):
        """Enable message ordering - alias for ordered_delivery()"""
        return self.ordered_delivery(enabled)
        
    def encryption_key(self, kms_key_name: str):
        """Set KMS encryption key for topic"""
        self.kms_key_name = kms_key_name
        return self
        
    def schema(self, schema_name: str, encoding: str = "JSON"):
        """Set message schema for validation"""
        self.schema_name = schema_name
        self.schema_encoding = encoding
        return self
        
    # Subscription management
    def subscription(self, name: str, **config):
        """Add a subscription with custom configuration"""
        if not self._is_valid_subscription_name(name):
            print(f"⚠️  Warning: Invalid subscription name '{name}'")
            
        self.subscription_names.append(name)
        self.subscription_configs[name] = config
        return self
        
    def pull_subscription(self, name: str, **config):
        """Add a pull subscription"""
        config['type'] = 'pull'
        return self.subscription(name, **config)
        
    def push_subscription(self, name: str, endpoint: str, **config):
        """Add a push subscription with endpoint"""
        config.update({'type': 'push', 'push_endpoint': endpoint})
        return self.subscription(name, **config)
        
    # Subscription configuration methods
    def ack_deadline(self, subscription_name: str, seconds: int):
        """Set acknowledgment deadline for a subscription"""
        if not self._is_valid_ack_deadline(seconds):
            print(f"⚠️  Warning: Invalid ack deadline {seconds}. Must be between 10-600 seconds")
            
        if subscription_name in self.subscription_configs:
            self.subscription_configs[subscription_name]['ack_deadline_seconds'] = seconds
        return self
        
    def retain_acked_messages(self, subscription_name: str, enabled: bool = True):
        """Enable retaining acknowledged messages for replay"""
        if subscription_name in self.subscription_configs:
            self.subscription_configs[subscription_name]['retain_acked_messages'] = enabled
        return self
        
    def exactly_once_delivery(self, subscription_name: str, enabled: bool = True):
        """Enable exactly-once delivery guarantee"""
        if subscription_name in self.subscription_configs:
            self.subscription_configs[subscription_name]['enable_exactly_once_delivery'] = enabled
        return self
        
    def dead_letter_queue(self, subscription_name: str, dlq_topic: str, max_attempts: int = 5):
        """Configure dead letter queue for failed messages"""
        if subscription_name in self.subscription_configs:
            self.subscription_configs[subscription_name].update({
                'dead_letter_topic': f"projects/{self.project_id}/topics/{dlq_topic}",
                'max_delivery_attempts': max_attempts
            })
        return self
        
    def expiration_policy(self, subscription_name: str, ttl: str):
        """Set subscription expiration policy (e.g., '2592000s' for 30 days)"""
        if subscription_name in self.subscription_configs:
            self.subscription_configs[subscription_name]['expiration_policy_ttl'] = ttl
        return self
        
    def retry_policy(self, subscription_name: str, min_backoff: str = "10s", max_backoff: str = "600s"):
        """Configure retry policy for message delivery"""
        if subscription_name in self.subscription_configs:
            self.subscription_configs[subscription_name].update({
                'retry_policy_min_backoff': min_backoff,
                'retry_policy_max_backoff': max_backoff
            })
        return self
        
    def filter(self, subscription_name: str, filter_expression: str):
        """Add message filter to subscription"""
        if subscription_name in self.subscription_configs:
            self.subscription_configs[subscription_name]['filter'] = filter_expression
        return self
        
    # Common subscription patterns
    def fan_out_subscriptions(self, subscription_names: List[str]):
        """Create multiple pull subscriptions for fan-out pattern"""
        for name in subscription_names:
            self.pull_subscription(name)
        return self
        
    def webhook_subscription(self, name: str, webhook_url: str, auth_token: str = None):
        """Create push subscription for webhook delivery"""
        config = {}
        if auth_token:
            config['push_attributes'] = {'x-auth-token': auth_token}
        return self.push_subscription(name, webhook_url, **config)
        
    def queue_subscription(self, name: str, workers: int = 1):
        """Create subscription for work queue pattern"""
        return self.pull_subscription(
            name,
            ack_deadline_seconds=60,  # Longer deadline for processing
            retain_acked_messages=False,
            enable_exactly_once_delivery=True
        )
        
    def event_stream_subscription(self, name: str):
        """Create subscription for event streaming"""
        return self.pull_subscription(
            name,
            ack_deadline_seconds=10,
            retain_acked_messages=True,  # Enable replay
            message_retention_duration="86400s"  # 1 day
        )
        
    # Labels and metadata
    def labels(self, labels: Dict[str, str]):
        """Add labels to topic"""
        self.topic_labels.update(labels)
        return self
        
    def label(self, key: str, value: str):
        """Add individual label - Rails convenience"""
        self.topic_labels[key] = value
        return self
        
    def subscription_labels(self, subscription_name: str, labels: Dict[str, str]):
        """Add labels to subscription"""
        if subscription_name in self.subscription_configs:
            if 'labels' not in self.subscription_configs[subscription_name]:
                self.subscription_configs[subscription_name]['labels'] = {}
            self.subscription_configs[subscription_name]['labels'].update(labels)
        return self
        
    # Access control
    def allow_publishers(self, identities: List[str]):
        """Set allowed publishers for topic"""
        self.allowed_publishers.extend(identities)
        return self
        
    def allow_subscribers(self, identities: List[str]):
        """Set allowed subscribers for topic"""
        self.allowed_subscribers.extend(identities)
        return self
        
    def public_topic(self):
        """Make topic publicly accessible"""
        self.allowed_publishers.append("allUsers")
        self.allowed_subscribers.append("allUsers")
        return self
        
    def private_topic(self):
        """Make topic private (clear public access)"""
        if "allUsers" in self.allowed_publishers:
            self.allowed_publishers.remove("allUsers")
        if "allUsers" in self.allowed_subscribers:
            self.allowed_subscribers.remove("allUsers")
        return self
        
    # Environment configurations
    def development(self):
        """Configure for development environment - Rails convention"""
        return (self.retention_days(1)
                .label("environment", "development")
                .label("cost-optimization", "enabled"))
                
    def staging(self):
        """Configure for staging environment - Rails convention"""
        return (self.retention_days(3)
                .label("environment", "staging")
                .label("testing", "enabled"))
                
    def production(self):
        """Configure for production environment - Rails convention"""
        return (self.retention_days(7)
                .ordered_delivery(True)
                .label("environment", "production")
                .label("reliability", "high"))
                
    # Common messaging patterns
    def event_bus(self):
        """Configure as event bus - Rails convenience"""
        return (self.retention_days(7)
                .ordered_delivery(False)
                .label("pattern", "event-bus")
                .label("architecture", "event-driven"))
                
    def task_queue(self):
        """Configure as task queue - Rails convenience"""
        return (self.retention_days(1)
                .ordered_delivery(False)
                .label("pattern", "task-queue")
                .label("processing", "async"))
                
    def audit_log(self):
        """Configure as audit log - Rails convenience"""
        return (self.retention_days(7)
                .ordered_delivery(True)
                .label("pattern", "audit-log")
                .label("compliance", "enabled"))
                
    def notification_hub(self):
        """Configure as notification hub - Rails convenience"""
        return (self.retention_days(1)
                .ordered_delivery(False)
                .label("pattern", "notification-hub")
                .label("delivery", "best-effort"))
                
    def data_pipeline(self):
        """Configure for data pipeline - Rails convenience"""
        return (self.retention_days(7)
                .ordered_delivery(True)
                .label("pattern", "data-pipeline")
                .label("processing", "batch"))
                
    # Advanced patterns
    def dlq_pattern(self, main_subscription: str, dlq_topic_name: str = None):
        """Set up dead letter queue pattern"""
        if not dlq_topic_name:
            dlq_topic_name = f"{self.topic_name}-dlq"
            
        # Configure main subscription with DLQ
        self.dead_letter_queue(main_subscription, dlq_topic_name, max_attempts=5)
        
        # Add DLQ subscription for monitoring
        self.pull_subscription(f"{main_subscription}-dlq-monitor")
        
        return self
        
    def replay_pattern(self, subscription_name: str):
        """Configure subscription for message replay capability"""
        return (self.retain_acked_messages(subscription_name, True)
                .ack_deadline(subscription_name, 600))  # Longer deadline
                
    def batch_processing_pattern(self, subscription_name: str, batch_size: int = 100):
        """Configure for batch message processing"""
        return self.pull_subscription(
            subscription_name,
            ack_deadline_seconds=300,  # 5 minutes for batch processing
            max_messages=batch_size,
            enable_exactly_once_delivery=True
        )
        
    # Cost optimization
    def cost_optimized(self):
        """Configure for cost optimization"""
        return (self.retention_days(1)  # Minimum retention
                .label("optimization", "cost")
                .label("tier", "basic"))
                
    def performance_optimized(self):
        """Configure for performance optimization"""
        return (self.retention_days(7)
                .ordered_delivery(True)
                .label("optimization", "performance")
                .label("tier", "premium"))
                
    def reliability_optimized(self):
        """Configure for reliability optimization"""
        return (self.retention_days(7)
                .ordered_delivery(True)
                .label("optimization", "reliability")
                .label("tier", "enterprise"))
                
    # Utility methods
    def clear_subscriptions(self):
        """Clear all configured subscriptions"""
        self.subscription_names = []
        self.subscription_configs = {}
        self.subscription_paths = {}
        return self
        
    def remove_subscription(self, name: str):
        """Remove a specific subscription"""
        if name in self.subscription_names:
            self.subscription_names.remove(name)
        if name in self.subscription_configs:
            del self.subscription_configs[name]
        if name in self.subscription_paths:
            del self.subscription_paths[name]
        return self
        
    def get_subscription_config(self, name: str) -> Optional[Dict[str, Any]]:
        """Get configuration for a specific subscription"""
        return self.subscription_configs.get(name)
        
    def list_subscriptions(self) -> List[str]:
        """List all configured subscription names"""
        return self.subscription_names.copy()