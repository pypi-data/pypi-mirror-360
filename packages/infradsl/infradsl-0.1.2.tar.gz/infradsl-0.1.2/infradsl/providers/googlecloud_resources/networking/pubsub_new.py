"""
GCP PubSub Complete Implementation (Modular Architecture)

Combines all PubSub functionality through multiple inheritance:
- PubSubCore: Core attributes and authentication
- PubSubConfigurationMixin: Chainable configuration methods  
- PubSubLifecycleMixin: Lifecycle operations (create/destroy/preview/publish/consume)
"""

from typing import Dict, Any, List, Optional
from .pubsub_core import PubSubCore
from .pubsub_configuration import PubSubConfigurationMixin
from .pubsub_lifecycle import PubSubLifecycleMixin


class PubSub(PubSubLifecycleMixin, PubSubConfigurationMixin, PubSubCore):
    """
    Complete GCP Pub/Sub implementation for messaging and event streaming.
    
    This class combines:
    - Topic and subscription configuration methods
    - Message publishing and consumption operations
    - Advanced patterns (fan-out, queue, dead letter)
    - Security and compliance features
    - Rails-like method chaining for fluent API
    """
    
    def __init__(self, name: str):
        """Initialize PubSub instance for messaging operations"""
        super().__init__(name)
        
        # Additional attributes specific to the combined class
        self.deployment_ready = False
        self.estimated_monthly_cost = "$0.40/month"
        
        # Cross-Cloud Magic integration
        self._optimization_priority = None
        self._messaging_pattern = None
        self._auto_scaling_enabled = True
        self._high_availability_enabled = True
    
    def validate_configuration(self):
        """Validate the current Pub/Sub configuration"""
        errors = []
        warnings = []
        
        # Validate topic name
        if not self.topic_name:
            errors.append("Topic name is required")
        elif not self._is_valid_topic_name(self.topic_name):
            errors.append(f"Invalid topic name: {self.topic_name}")
        
        # Validate retention
        if not self._is_valid_retention_duration(self.message_retention_duration):
            errors.append(f"Invalid retention duration: {self.message_retention_duration}")
        
        # Validate subscriptions
        for sub_name in self.subscription_names:
            if not self._is_valid_subscription_name(sub_name):
                errors.append(f"Invalid subscription name: {sub_name}")
                
            config = self.subscription_configs.get(sub_name, {})
            
            # Validate ack deadline
            ack_deadline = config.get('ack_deadline_seconds', self.default_ack_deadline_seconds)
            if not self._is_valid_ack_deadline(ack_deadline):
                errors.append(f"Invalid ack deadline for {sub_name}: {ack_deadline}s")
            
            # Validate push configuration
            if config.get('type') == 'push':
                if not config.get('push_endpoint'):
                    errors.append(f"Push subscription {sub_name} missing endpoint")
                elif not config['push_endpoint'].startswith(('http://', 'https://')):
                    errors.append(f"Invalid push endpoint for {sub_name}: {config['push_endpoint']}")
        
        # Performance warnings
        if len(self.subscription_names) > 20:
            warnings.append(f"Large number of subscriptions ({len(self.subscription_names)}) may impact management complexity")
        
        if self.message_ordering_enabled and len(self.subscription_names) > 5:
            warnings.append("Message ordering with many subscriptions may impact throughput")
        
        # Security warnings
        if "allUsers" in self.allowed_publishers:
            warnings.append("Topic allows public publishing - ensure this is intended for security")
        
        if "allUsers" in self.allowed_subscribers:
            warnings.append("Topic allows public subscriptions - review security implications")
        
        # Cost warnings
        retention_days = int(self.message_retention_duration.rstrip('s')) // 86400
        if retention_days > 3:
            warnings.append(f"Long retention ({retention_days} days) is free but may increase storage")
        
        if errors:
            raise ValueError(f"Configuration validation failed: {', '.join(errors)}")
        
        if warnings:
            print(f"⚠️  Configuration warnings:")
            for warning in warnings:
                print(f"   - {warning}")
        
        self.deployment_ready = True
        return True
    
    def get_topic_info(self):
        """Get complete information about the Pub/Sub topic"""
        sub_types = self._get_subscription_types()
        
        return {
            'topic_name': self.topic_name,
            'description': self.topic_description,
            'topic_path': self.topic_path,
            'message_retention_duration': self.message_retention_duration,
            'retention_days': int(self.message_retention_duration.rstrip('s')) // 86400,
            'message_ordering_enabled': self.message_ordering_enabled,
            'kms_key_name': self.kms_key_name,
            'schema_name': self.schema_name,
            'subscription_count': sub_types['total'],
            'pull_subscriptions': sub_types['pull'],
            'push_subscriptions': sub_types['push'],
            'subscription_names': self.subscription_names,
            'subscription_configs': self.subscription_configs,
            'topic_labels_count': len(self.topic_labels),
            'topic_labels': self.topic_labels,
            'allowed_publishers_count': len(self.allowed_publishers),
            'allowed_subscribers_count': len(self.allowed_subscribers),
            'topic_exists': self.topic_exists,
            'deployment_ready': self.deployment_ready,
            'estimated_monthly_cost': self.estimated_monthly_cost,
            'optimization_priority': self._optimization_priority,
            'messaging_pattern': self._messaging_pattern
        }
    
    def clone(self, new_name: str):
        """Create a copy of this Pub/Sub configuration with a new name"""
        cloned_topic = PubSub(new_name)
        cloned_topic.topic_name = new_name
        cloned_topic.topic_description = self.topic_description
        cloned_topic.message_retention_duration = self.message_retention_duration
        cloned_topic.message_ordering_enabled = self.message_ordering_enabled
        cloned_topic.kms_key_name = self.kms_key_name
        cloned_topic.schema_name = self.schema_name
        cloned_topic.subscription_names = self.subscription_names.copy()
        cloned_topic.subscription_configs = self.subscription_configs.copy()
        cloned_topic.topic_labels = self.topic_labels.copy()
        cloned_topic.allowed_publishers = self.allowed_publishers.copy()
        cloned_topic.allowed_subscribers = self.allowed_subscribers.copy()
        return cloned_topic
    
    def export_configuration(self):
        """Export Pub/Sub configuration for backup or migration"""
        return {
            'metadata': {
                'topic_name': self.topic_name,
                'topic_path': self.topic_path,
                'exported_at': 'Mock timestamp'
            },
            'configuration': {
                'topic_name': self.topic_name,
                'description': self.topic_description,
                'message_retention_duration': self.message_retention_duration,
                'message_ordering_enabled': self.message_ordering_enabled,
                'kms_key_name': self.kms_key_name,
                'schema_name': self.schema_name,
                'subscription_names': self.subscription_names,
                'subscription_configs': self.subscription_configs,
                'default_ack_deadline_seconds': self.default_ack_deadline_seconds,
                'default_retain_acked_messages': self.default_retain_acked_messages,
                'default_enable_exactly_once_delivery': self.default_enable_exactly_once_delivery,
                'default_expiration_policy_ttl': self.default_expiration_policy_ttl,
                'allowed_publishers': self.allowed_publishers,
                'allowed_subscribers': self.allowed_subscribers,
                'topic_labels': self.topic_labels,
                'topic_annotations': self.topic_annotations,
                'optimization_priority': self._optimization_priority,
                'messaging_pattern': self._messaging_pattern,
                'auto_scaling_enabled': self._auto_scaling_enabled,
                'high_availability_enabled': self._high_availability_enabled
            }
        }
    
    def import_configuration(self, config_data: dict):
        """Import Pub/Sub configuration from exported data"""
        if 'configuration' in config_data:
            config = config_data['configuration']
            self.topic_name = config.get('topic_name', self.topic_name)
            self.topic_description = config.get('description', f"Pub/Sub topic for {self.topic_name}")
            self.message_retention_duration = config.get('message_retention_duration', '604800s')
            self.message_ordering_enabled = config.get('message_ordering_enabled', False)
            self.kms_key_name = config.get('kms_key_name')
            self.schema_name = config.get('schema_name')
            self.subscription_names = config.get('subscription_names', [])
            self.subscription_configs = config.get('subscription_configs', {})
            self.default_ack_deadline_seconds = config.get('default_ack_deadline_seconds', 10)
            self.default_retain_acked_messages = config.get('default_retain_acked_messages', False)
            self.default_enable_exactly_once_delivery = config.get('default_enable_exactly_once_delivery', False)
            self.default_expiration_policy_ttl = config.get('default_expiration_policy_ttl')
            self.allowed_publishers = config.get('allowed_publishers', [])
            self.allowed_subscribers = config.get('allowed_subscribers', [])
            self.topic_labels = config.get('topic_labels', {})
            self.topic_annotations = config.get('topic_annotations', {})
            self._optimization_priority = config.get('optimization_priority')
            self._messaging_pattern = config.get('messaging_pattern')
            self._auto_scaling_enabled = config.get('auto_scaling_enabled', True)
            self._high_availability_enabled = config.get('high_availability_enabled', True)
        
        return self
    
    def enable_auto_scaling(self, enabled: bool = True):
        """Enable automatic scaling (Pub/Sub scales automatically by default)"""
        self._auto_scaling_enabled = enabled
        if enabled:
            print("📈 Auto-scaling confirmed enabled (Pub/Sub scales automatically)")
            print("   💡 Handles millions of messages per second")
            print("   💡 Global load balancing included")
        return self
    
    def enable_high_availability(self, enabled: bool = True):
        """Enable high availability (Pub/Sub is HA by default)"""
        self._high_availability_enabled = enabled
        if enabled:
            print("🛡️ High availability confirmed enabled (Pub/Sub is globally distributed)")
            print("   💡 Multi-region replication automatic")
            print("   💡 No single point of failure")
            print("   💡 99.95% SLA guaranteed")
        return self
    
    def get_topic_status(self):
        """Get current status of the Pub/Sub topic"""
        status = {
            "overall_status": "healthy",
            "issues": [],
            "recommendations": []
        }
        
        # Check configuration issues
        if not self.topic_name:
            status["issues"].append("No topic name configured")
            status["overall_status"] = "error"
        
        if not self.subscription_names:
            status["recommendations"].append("No subscriptions configured - topic will accumulate messages")
        
        # Check retention
        retention_days = int(self.message_retention_duration.rstrip('s')) // 86400
        if retention_days < 1:
            status["recommendations"].append("Very short retention - consider increasing for reliability")
        
        # Check security
        if "allUsers" in self.allowed_publishers:
            status["recommendations"].append("Public publishing enabled - review security requirements")
        
        # Check patterns
        if self.message_ordering_enabled and not self._messaging_pattern:
            status["recommendations"].append("Message ordering enabled - consider setting messaging pattern")
        
        return status
    
    def apply_best_practices(self):
        """Apply Pub/Sub best practices to the configuration"""
        print("🚀 Applying Pub/Sub best practices")
        
        # Ensure reasonable retention
        retention_days = int(self.message_retention_duration.rstrip('s')) // 86400
        if retention_days < 1:
            print("   💡 Setting retention to 1 day minimum")
            self.retention_days(1)
        
        # Add standard labels
        self.topic_labels.update({
            "managed-by": "infradsl",
            "best-practices": "applied",
            "messaging-platform": "pubsub"
        })
        print("   💡 Added best practice labels")
        
        # Enable exactly-once delivery for new subscriptions by default
        self.default_enable_exactly_once_delivery = True
        print("   💡 Enabled exactly-once delivery default")
        
        # Set reasonable ack deadline
        if self.default_ack_deadline_seconds < 10:
            self.default_ack_deadline_seconds = 10
            print("   💡 Set minimum ack deadline to 10 seconds")
        
        return self
    
    def get_cost_breakdown(self):
        """Get detailed cost breakdown for Pub/Sub usage"""
        # Estimate usage patterns
        monthly_messages = 1_000_000  # 1M messages
        avg_message_size = 1024  # 1KB average
        subscription_count = len(self.subscription_names) or 1
        
        # Calculate costs
        throughput_gb = (monthly_messages * avg_message_size) / (1024**3)
        throughput_tib = throughput_gb / 1024
        
        breakdown = {
            "throughput_cost": throughput_tib * 40,  # $40 per TiB
            "operations_cost": (monthly_messages / 1_000_000) * 0.50,  # $0.50 per million
            "retention_cost": 0,  # Free up to 7 days
            "subscription_cost": 0,  # Subscriptions are free
            "total_messages": monthly_messages,
            "avg_message_size": avg_message_size,
            "throughput_gb": throughput_gb,
            "subscription_count": subscription_count
        }
        
        breakdown["total_cost"] = breakdown["throughput_cost"] + breakdown["operations_cost"]
        
        # Minimum charge
        if breakdown["total_cost"] < 0.40:
            breakdown["total_cost"] = 0.40
        
        return breakdown
    
    def get_security_analysis(self):
        """Analyze Pub/Sub security configuration"""
        analysis = {
            "security_score": 100,
            "issues": [],
            "recommendations": []
        }
        
        # Check public access
        if "allUsers" in self.allowed_publishers:
            analysis["issues"].append("Topic allows public publishing")
            analysis["security_score"] -= 30
        
        if "allUsers" in self.allowed_subscribers:
            analysis["issues"].append("Topic allows public subscriptions")
            analysis["security_score"] -= 20
        
        # Check encryption
        if not self.kms_key_name:
            analysis["recommendations"].append("Consider using customer-managed encryption keys")
            analysis["security_score"] -= 10
        
        # Check authentication on push subscriptions
        push_subs_without_auth = []
        for sub_name, config in self.subscription_configs.items():
            if config.get('type') == 'push':
                if 'push_attributes' not in config or 'x-auth-token' not in config.get('push_attributes', {}):
                    push_subs_without_auth.append(sub_name)
        
        if push_subs_without_auth:
            analysis["recommendations"].append(f"Push subscriptions without auth tokens: {push_subs_without_auth}")
            analysis["security_score"] -= 15
        
        # Check dead letter configuration
        if self.subscription_names and not any(
            'dead_letter_topic' in config for config in self.subscription_configs.values()
        ):
            analysis["recommendations"].append("Consider adding dead letter queues for failed message handling")
            analysis["security_score"] -= 5
        
        return analysis
    
    def get_performance_analysis(self):
        """Analyze Pub/Sub performance configuration"""
        analysis = {
            "performance_score": 100,
            "issues": [],
            "recommendations": []
        }
        
        # Check ordering impact
        if self.message_ordering_enabled:
            analysis["recommendations"].append("Message ordering enabled - may reduce throughput")
            analysis["performance_score"] -= 10
        
        # Check subscription patterns
        sub_types = self._get_subscription_types()
        if sub_types['push'] > sub_types['pull']:
            analysis["recommendations"].append("More push than pull subscriptions - ensure endpoints can handle load")
            analysis["performance_score"] -= 5
        
        # Check ack deadlines
        short_deadlines = []
        for sub_name, config in self.subscription_configs.items():
            ack_deadline = config.get('ack_deadline_seconds', self.default_ack_deadline_seconds)
            if ack_deadline < 10:
                short_deadlines.append((sub_name, ack_deadline))
        
        if short_deadlines:
            analysis["issues"].append(f"Subscriptions with very short ack deadlines: {short_deadlines}")
            analysis["performance_score"] -= 15
        
        # Check retention vs. performance
        retention_days = int(self.message_retention_duration.rstrip('s')) // 86400
        if retention_days > 3 and not any(
            config.get('retain_acked_messages', False) for config in self.subscription_configs.values()
        ):
            analysis["recommendations"].append("Long retention without message replay - consider if needed")
            analysis["performance_score"] -= 5
        
        return analysis


# Convenience functions for creating PubSub instances
def create_event_bus(project_id: str, topic_name: str) -> PubSub:
    """Create Pub/Sub topic for event bus pattern"""
    topic = PubSub(topic_name)
    topic.project(project_id).event_bus()
    return topic

def create_task_queue(project_id: str, topic_name: str, worker_subscription: str = None) -> PubSub:
    """Create Pub/Sub topic for task queue pattern"""
    topic = PubSub(topic_name)
    topic.project(project_id).task_queue()
    if worker_subscription:
        topic.queue_subscription(worker_subscription)
    return topic

def create_notification_hub(project_id: str, topic_name: str) -> PubSub:
    """Create Pub/Sub topic for notification hub pattern"""
    topic = PubSub(topic_name)
    topic.project(project_id).notification_hub()
    return topic

def create_audit_log(project_id: str, topic_name: str) -> PubSub:
    """Create Pub/Sub topic for audit logging"""
    topic = PubSub(topic_name)
    topic.project(project_id).audit_log()
    return topic

def create_data_pipeline(project_id: str, topic_name: str) -> PubSub:
    """Create Pub/Sub topic for data pipeline"""
    topic = PubSub(topic_name)
    topic.project(project_id).data_pipeline()
    return topic

def create_fanout_topic(project_id: str, topic_name: str, subscriber_names: List[str]) -> PubSub:
    """Create Pub/Sub topic with fan-out pattern"""
    topic = PubSub(topic_name)
    topic.project(project_id).fan_out_subscriptions(subscriber_names)
    return topic

# Aliases for backward compatibility
GCPPubSub = PubSub
GooglePubSub = PubSub