"""
GCP PubSub Core Implementation

Core attributes and authentication for Google Cloud Pub/Sub messaging service.
Provides the foundation for the modular PubSub system.
"""

from typing import Dict, Any, List, Optional
from ..base_resource import BaseGcpResource


class PubSubCore(BaseGcpResource):
    """
    Core class for Google Cloud Pub/Sub functionality.
    
    This class provides:
    - Basic topic and subscription attributes
    - Authentication setup
    - Common utilities for messaging operations
    - State tracking and validation foundations
    """
    
    def __init__(self, name: str):
        """Initialize PubSub core with topic name"""
        super().__init__(name)
        
        # Core topic attributes
        self.topic_name = name
        self.topic_description = f"Pub/Sub topic for {name}"
        self.topic_path = None
        
        # Topic configuration
        self.message_retention_duration = "604800s"  # 7 days default
        self.message_ordering_enabled = False
        self.kms_key_name = None  # Encryption key
        self.schema_name = None  # Message schema
        
        # Subscription storage
        self.subscription_names = []
        self.subscription_configs = {}
        self.subscription_paths = {}
        
        # Default subscription settings
        self.default_ack_deadline_seconds = 10
        self.default_retain_acked_messages = False
        self.default_enable_exactly_once_delivery = False
        self.default_expiration_policy_ttl = None  # Never expire by default
        
        # Security and access
        self.allowed_publishers = []
        self.allowed_subscribers = []
        self.topic_labels = {}
        self.topic_annotations = {}
        
        # State tracking
        self.topic_exists = False
        self.topic_created = False
        self.subscriptions_created = {}
        
        # Client references
        self.publisher_client = None
        self.subscriber_client = None
        self.schema_client = None
        
        # Estimated costs
        self.estimated_monthly_cost = "$0.40/month"
        
    def _initialize_managers(self):
        """Initialize Pub/Sub-specific managers"""
        self.publisher_client = None
        self.subscriber_client = None
        self.schema_client = None
        
    def _post_authentication_setup(self):
        """Setup managers after authentication"""
        try:
            from google.cloud import pubsub_v1
            
            # Initialize clients
            self.publisher_client = pubsub_v1.PublisherClient(credentials=self.gcp_client.credentials)
            self.subscriber_client = pubsub_v1.SubscriberClient(credentials=self.gcp_client.credentials)
            
            # Generate topic path
            self.project_id = self.project_id or self.gcp_client.project_id
            self.topic_path = f"projects/{self.project_id}/topics/{self.topic_name}"
            
        except Exception as e:
            print(f"⚠️  Failed to initialize Pub/Sub clients: {str(e)}")
            
    def _is_valid_topic_name(self, name: str) -> bool:
        """Check if topic name is valid"""
        import re
        # Topic names must contain only letters, numbers, dashes, underscores
        pattern = r'^[a-zA-Z][a-zA-Z0-9_-]*$'
        return bool(re.match(pattern, name)) and len(name) <= 255
        
    def _is_valid_subscription_name(self, name: str) -> bool:
        """Check if subscription name is valid"""
        import re
        # Subscription names must contain only letters, numbers, dashes, underscores
        pattern = r'^[a-zA-Z][a-zA-Z0-9_-]*$'
        return bool(re.match(pattern, name)) and len(name) <= 255
        
    def _is_valid_retention_duration(self, duration: str) -> bool:
        """Check if message retention duration is valid"""
        if not duration.endswith('s'):
            return False
            
        try:
            seconds = int(duration[:-1])
            # Must be between 10 minutes and 7 days
            return 600 <= seconds <= 604800
        except ValueError:
            return False
            
    def _is_valid_ack_deadline(self, seconds: int) -> bool:
        """Check if acknowledgment deadline is valid"""
        # Must be between 10 and 600 seconds
        return 10 <= seconds <= 600
        
    def _validate_topic_config(self, config: Dict[str, Any]) -> bool:
        """Validate topic configuration"""
        required_fields = ["topic_name"]
        
        for field in required_fields:
            if field not in config or not config[field]:
                return False
                
        # Validate topic name format
        if not self._is_valid_topic_name(config["topic_name"]):
            return False
            
        # Validate retention duration if specified
        if "message_retention_duration" in config:
            if not self._is_valid_retention_duration(config["message_retention_duration"]):
                return False
                
        return True
        
    def _validate_subscription_config(self, sub_config: Dict[str, Any]) -> bool:
        """Validate subscription configuration"""
        required_fields = ["name"]
        
        for field in required_fields:
            if field not in sub_config:
                return False
                
        # Validate subscription name
        if not self._is_valid_subscription_name(sub_config["name"]):
            return False
            
        # Validate ack deadline if specified
        if "ack_deadline_seconds" in sub_config:
            if not self._is_valid_ack_deadline(sub_config["ack_deadline_seconds"]):
                return False
                
        # Validate push endpoint if push subscription
        if sub_config.get("type") == "push":
            if not sub_config.get("push_endpoint"):
                return False
                
        return True
        
    def _get_subscription_types(self) -> Dict[str, int]:
        """Get count of subscription types"""
        pull_count = 0
        push_count = 0
        
        for config in self.subscription_configs.values():
            if config.get("type") == "push":
                push_count += 1
            else:
                pull_count += 1
                
        return {
            "pull": pull_count,
            "push": push_count,
            "total": pull_count + push_count
        }
        
    def _estimate_pubsub_cost(self) -> float:
        """Estimate monthly cost for Pub/Sub usage"""
        # Pub/Sub pricing (simplified)
        
        # Assume moderate usage
        monthly_messages = 1_000_000  # 1M messages
        avg_message_size = 1024  # 1KB average
        
        # Message throughput cost: $40 per TiB
        throughput_gb = (monthly_messages * avg_message_size) / (1024**3)
        throughput_cost = (throughput_gb / 1024) * 40
        
        # Operations cost: $0.50 per million
        operations_cost = (monthly_messages / 1_000_000) * 0.50
        
        # Subscriptions are free
        # Message retention up to 7 days is free
        
        total_cost = throughput_cost + operations_cost
        
        # Minimum charge
        if total_cost < 0.40:
            total_cost = 0.40
            
        return total_cost
        
    def _fetch_current_cloud_state(self) -> Dict[str, Any]:
        """Fetch current state of Pub/Sub topic from Google Cloud"""
        self._ensure_authenticated()
        
        try:
            # Check if topic exists
            try:
                topic = self.publisher_client.get_topic(request={"topic": self.topic_path})
                topic_exists = True
            except Exception:
                topic_exists = False
                
            if not topic_exists:
                return {
                    "exists": False,
                    "topic_name": self.topic_name,
                    "topic_path": self.topic_path
                }
                
            # Get topic details
            current_state = {
                "exists": True,
                "topic_name": self.topic_name,
                "topic_path": self.topic_path,
                "message_retention_duration": topic.message_retention_duration.seconds if topic.message_retention_duration else 604800,
                "kms_key_name": topic.kms_key_name if hasattr(topic, 'kms_key_name') else None,
                "schema_name": topic.schema_settings.schema if hasattr(topic, 'schema_settings') and topic.schema_settings else None,
                "labels": dict(topic.labels) if topic.labels else {},
                "message_ordering_enabled": False,
                "subscriptions": []
            }
            
            # Check if message ordering is enabled (inferred from storage policy)
            if hasattr(topic, 'message_storage_policy') and topic.message_storage_policy:
                if topic.message_storage_policy.allowed_persistence_regions:
                    current_state["message_ordering_enabled"] = True
                    
            # Get subscription information
            try:
                subscription_list = []
                for subscription in self.publisher_client.list_topic_subscriptions(request={"topic": self.topic_path}):
                    sub_name = subscription.split('/')[-1]
                    
                    # Get subscription details
                    try:
                        sub_details = self.subscriber_client.get_subscription(request={"subscription": subscription})
                        
                        sub_info = {
                            "name": sub_name,
                            "path": subscription,
                            "ack_deadline_seconds": sub_details.ack_deadline_seconds,
                            "retain_acked_messages": sub_details.retain_acked_messages,
                            "message_retention_duration": sub_details.message_retention_duration.seconds if sub_details.message_retention_duration else 604800,
                            "enable_exactly_once_delivery": sub_details.enable_exactly_once_delivery if hasattr(sub_details, 'enable_exactly_once_delivery') else False,
                            "type": "push" if sub_details.push_config.push_endpoint else "pull",
                            "push_endpoint": sub_details.push_config.push_endpoint if sub_details.push_config.push_endpoint else None,
                            "labels": dict(sub_details.labels) if sub_details.labels else {},
                            "dead_letter_enabled": bool(sub_details.dead_letter_policy.dead_letter_topic) if sub_details.dead_letter_policy else False,
                            "max_delivery_attempts": sub_details.dead_letter_policy.max_delivery_attempts if sub_details.dead_letter_policy else None
                        }
                        subscription_list.append(sub_info)
                        
                    except Exception as e:
                        print(f"⚠️  Warning: Failed to get subscription details for {sub_name}: {str(e)}")
                        
                current_state["subscriptions"] = subscription_list
                current_state["subscription_count"] = len(subscription_list)
                
            except Exception as e:
                print(f"⚠️  Warning: Failed to list topic subscriptions: {str(e)}")
                current_state["subscription_count"] = 0
                
            return current_state
            
        except Exception as e:
            print(f"⚠️  Warning: Failed to fetch Pub/Sub state: {str(e)}")
            return {
                "exists": False,
                "topic_name": self.topic_name,
                "topic_path": self.topic_path,
                "error": str(e)
            }
            
    def _discover_existing_topics(self) -> Dict[str, Dict[str, Any]]:
        """Discover all existing Pub/Sub topics in the project"""
        existing_topics = {}
        
        try:
            # List all topics in the project
            project_path = f"projects/{self.project_id}"
            
            for topic in self.publisher_client.list_topics(request={"project": project_path}):
                topic_name = topic.name.split('/')[-1]
                
                try:
                    # Get topic details
                    topic_details = self.publisher_client.get_topic(request={"topic": topic.name})
                    
                    existing_topics[topic_name] = {
                        "topic_name": topic_name,
                        "full_path": topic.name,
                        "labels": dict(topic_details.labels) if topic_details.labels else {},
                        "message_retention_duration": topic_details.message_retention_duration.seconds if topic_details.message_retention_duration else 604800,
                        "kms_key_name": topic_details.kms_key_name if hasattr(topic_details, 'kms_key_name') else None,
                        "schema_name": topic_details.schema_settings.schema if hasattr(topic_details, 'schema_settings') and topic_details.schema_settings else None
                    }
                    
                except Exception as e:
                    print(f"⚠️  Failed to get details for topic {topic_name}: {str(e)}")
                    existing_topics[topic_name] = {
                        "topic_name": topic_name,
                        "error": str(e)
                    }
                    
        except Exception as e:
            print(f"⚠️  Failed to discover existing Pub/Sub topics: {str(e)}")
            
        return existing_topics