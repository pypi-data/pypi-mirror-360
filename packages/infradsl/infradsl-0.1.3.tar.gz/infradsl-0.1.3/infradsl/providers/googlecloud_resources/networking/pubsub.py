"""
Google Cloud Pub/Sub Resource

Rails-like Pub/Sub topic and subscription management with intelligent defaults.
"""

from typing import Dict, Any, List, Optional
from ..base_resource import BaseGcpResource


class PubSub(BaseGcpResource):
    """Google Cloud Pub/Sub Topic Resource with Rails-like API"""

    def __init__(self, name: str):
        super().__init__(name)
        
        # Core configuration
        self.topic_name = name
        self.subscription_names = []
        self.subscription_configs = {}
        
        # Topic settings
        self.message_retention_duration = "604800s"  # 7 days
        self.message_ordering_enabled = False
        
        # Security and access
        self.allowed_publishers = []
        self.allowed_subscribers = []
        self.topic_labels = {}
        
        # State
        self.topic_path = None
        self.subscription_paths = {}
        self.topic_exists = False
        
        # Clients
        self.publisher_client = None
        self.subscriber_client = None

    def _initialize_managers(self):
        self.publisher_client = None
        self.subscriber_client = None

    def _post_authentication_setup(self):
        self.publisher_client = self.get_publisher_client()
        self.subscriber_client = self.get_subscriber_client()
        
        # Generate topic path
        self.topic_path = f"projects/{self.gcp_client.project}/topics/{self.topic_name}"

    def _discover_existing_topics_and_subscriptions(self) -> Dict[str, Dict[str, Any]]:
        """Discover existing Pub/Sub topics and their subscriptions"""
        existing_topics = {}
        
        try:
            from google.cloud import pubsub_v1
            from google.api_core.exceptions import GoogleAPIError
            
            # List all topics in the project
            project_path = f"projects/{self.gcp_client.project}"
            
            for topic in self.publisher_client.list_topics(request={"project": project_path}):
                topic_name = topic.name.split('/')[-1]
                
                try:
                    # Get topic details
                    topic_details = self.publisher_client.get_topic(request={"topic": topic.name})
                    
                    # Get topic metadata
                    labels = dict(topic_details.labels) if topic_details.labels else {}
                    retention_duration = topic_details.message_retention_duration
                    
                    # Check if message ordering is enabled
                    message_ordering_enabled = False
                    if hasattr(topic_details, 'message_storage_policy') and topic_details.message_storage_policy:
                        # Ordering is typically enabled when storage policy is set
                        message_ordering_enabled = bool(topic_details.message_storage_policy.allowed_persistence_regions)
                    
                    # Get subscriptions for this topic
                    subscriptions = []
                    try:
                        for subscription in self.publisher_client.list_topic_subscriptions(request={"topic": topic.name}):
                            sub_name = subscription.split('/')[-1]
                            
                            # Get subscription details
                            try:
                                sub_details = self.subscriber_client.get_subscription(request={"subscription": subscription})
                                
                                sub_info = {
                                    'name': sub_name,
                                    'full_path': subscription,
                                    'ack_deadline_seconds': sub_details.ack_deadline_seconds,
                                    'retain_acked_messages': sub_details.retain_acked_messages,
                                    'message_retention_duration': sub_details.message_retention_duration,
                                    'labels': dict(sub_details.labels) if sub_details.labels else {},
                                    'type': 'push' if sub_details.push_config.push_endpoint else 'pull',
                                    'push_endpoint': sub_details.push_config.push_endpoint if sub_details.push_config.push_endpoint else None,
                                    'dead_letter_enabled': bool(sub_details.dead_letter_policy.dead_letter_topic) if sub_details.dead_letter_policy else False,
                                    'max_delivery_attempts': sub_details.dead_letter_policy.max_delivery_attempts if sub_details.dead_letter_policy else None
                                }
                                subscriptions.append(sub_info)
                                
                            except Exception as e:
                                print(f"⚠️  Failed to get subscription details for {sub_name}: {str(e)}")
                                subscriptions.append({
                                    'name': sub_name,
                                    'error': str(e)
                                })
                                
                    except Exception as e:
                        print(f"⚠️  Failed to list subscriptions for topic {topic_name}: {str(e)}")
                    
                    existing_topics[topic_name] = {
                        'topic_name': topic_name,
                        'full_path': topic.name,
                        'labels': labels,
                        'label_count': len(labels),
                        'message_retention_duration': retention_duration,
                        'message_ordering_enabled': message_ordering_enabled,
                        'subscriptions': subscriptions,
                        'subscription_count': len(subscriptions),
                        'pull_subscriptions': len([s for s in subscriptions if s.get('type') == 'pull']),
                        'push_subscriptions': len([s for s in subscriptions if s.get('type') == 'push']),
                        'dead_letter_subscriptions': len([s for s in subscriptions if s.get('dead_letter_enabled', False)])
                    }
                    
                except Exception as e:
                    print(f"⚠️  Failed to get details for topic {topic_name}: {str(e)}")
                    existing_topics[topic_name] = {
                        'topic_name': topic_name,
                        'error': str(e)
                    }
                    
        except Exception as e:
            print(f"⚠️  Failed to discover existing Pub/Sub topics: {str(e)}")
        
        return existing_topics

    def get_publisher_client(self):
        try:
            from google.cloud import pubsub_v1
            return pubsub_v1.PublisherClient(credentials=self.gcp_client.credentials)
        except Exception as e:
            print(f"⚠️  Failed to create Publisher client: {e}")
            return None

    def get_subscriber_client(self):
        try:
            from google.cloud import pubsub_v1
            return pubsub_v1.SubscriberClient(credentials=self.gcp_client.credentials)
        except Exception as e:
            print(f"⚠️  Failed to create Subscriber client: {e}")
            return None

    def preview(self) -> Dict[str, Any]:
        """Preview what will be created, kept, and removed"""
        self._ensure_authenticated()

        # Discover existing topics and subscriptions
        existing_topics = self._discover_existing_topics_and_subscriptions()
        
        # Categorize topics
        topics_to_create = []
        topics_to_keep = []
        topics_to_remove = []
        
        # Check if our desired topic exists
        desired_topic_name = self.topic_name
        topic_exists = desired_topic_name in existing_topics
        
        if not topic_exists:
            topics_to_create.append({
                'topic_name': desired_topic_name,
                'message_retention_duration': self.message_retention_duration,
                'message_ordering_enabled': self.message_ordering_enabled,
                'subscription_names': self.subscription_names,
                'subscription_configs': self.subscription_configs,
                'subscription_count': len(self.subscription_names),
                'pull_subscriptions': len([s for s in self.subscription_names if self.subscription_configs.get(s, {}).get('type', 'pull') == 'pull']),
                'push_subscriptions': len([s for s in self.subscription_names if self.subscription_configs.get(s, {}).get('type') == 'push']),
                'labels': self.topic_labels,
                'label_count': len(self.topic_labels)
            })
        else:
            topics_to_keep.append(existing_topics[desired_topic_name])

        print(f"\n📡 Google Cloud Pub/Sub Preview")
        
        # Show topics to create
        if topics_to_create:
            print(f"╭─ 📡 Topics to CREATE: {len(topics_to_create)}")
            for topic in topics_to_create:
                print(f"├─ 🆕 {topic['topic_name']}")
                
                # Show retention
                retention_days = int(topic['message_retention_duration'].rstrip('s')) // 86400
                print(f"│  ├─ 📦 Message Retention: {retention_days} days")
                
                print(f"│  ├─ 🔄 Message Ordering: {'✅ Enabled' if topic['message_ordering_enabled'] else '❌ Disabled'}")
                
                # Show subscription summary
                if topic['subscription_count'] > 0:
                    print(f"│  ├─ 📋 Subscriptions: {topic['subscription_count']} total")
                    if topic['pull_subscriptions'] > 0:
                        print(f"│  │  ├─ 📥 Pull: {topic['pull_subscriptions']}")
                    if topic['push_subscriptions'] > 0:
                        print(f"│  │  └─ 📤 Push: {topic['push_subscriptions']}")
                    
                    # Show individual subscriptions
                    print(f"│  ├─ 📋 Subscription Details:")
                    for i, sub_name in enumerate(topic['subscription_names']):
                        config = topic['subscription_configs'].get(sub_name, {})
                        connector = "│  │  ├─" if i < len(topic['subscription_names']) - 1 else "│  │  └─"
                        sub_type = config.get('type', 'pull')
                        
                        print(f"{connector} {sub_name} ({sub_type})")
                        
                        if sub_type == 'push' and config.get('push_endpoint'):
                            print(f"│  │     ├─ 🌐 Endpoint: {config['push_endpoint']}")
                        
                        if config.get('dead_letter_topic'):
                            print(f"│  │     ├─ 💀 Dead Letter: {config['dead_letter_topic']}")
                        
                        ack_deadline = config.get('ack_deadline_seconds', 10)
                        print(f"│  │     └─ ⏰ ACK Deadline: {ack_deadline}s")
                else:
                    print(f"│  ├─ 📋 Subscriptions: None (topic only)")
                
                if topic['label_count'] > 0:
                    print(f"│  ├─ 🏷️  Labels: {topic['label_count']}")
                
                # Show messaging features
                print(f"│  ├─ 🚀 Features:")
                print(f"│  │  ├─ 🌊 At-least-once delivery")
                print(f"│  │  ├─ 📈 Auto-scaling")
                print(f"│  │  ├─ 🔄 Message replay")
                print(f"│  │  └─ 🛡️  Dead letter queues")
                
                print(f"│  └─ ⚡ Throughput: 1M+ messages/second, global distribution")
            print(f"╰─")

        # Show existing topics being kept
        if topics_to_keep:
            print(f"\n╭─ 📡 Existing Topics to KEEP: {len(topics_to_keep)}")
            for topic in topics_to_keep:
                print(f"├─ ✅ {topic['topic_name']}")
                
                # Show retention
                retention_duration = topic.get('message_retention_duration', '604800s')
                if retention_duration:
                    retention_days = int(str(retention_duration).rstrip('s')) // 86400
                    print(f"│  ├─ 📦 Message Retention: {retention_days} days")
                
                print(f"│  ├─ 🔄 Message Ordering: {'✅ Enabled' if topic['message_ordering_enabled'] else '❌ Disabled'}")
                
                # Show subscription summary
                if topic['subscription_count'] > 0:
                    print(f"│  ├─ 📋 Subscriptions: {topic['subscription_count']} total")
                    if topic['pull_subscriptions'] > 0:
                        print(f"│  │  ├─ 📥 Pull: {topic['pull_subscriptions']}")
                    if topic['push_subscriptions'] > 0:
                        print(f"│  │  ├─ 📤 Push: {topic['push_subscriptions']}")
                    if topic['dead_letter_subscriptions'] > 0:
                        print(f"│  │  └─ 💀 Dead Letter: {topic['dead_letter_subscriptions']}")
                    
                    # Show subscription details
                    print(f"│  ├─ 📋 Active Subscriptions:")
                    for i, sub in enumerate(topic['subscriptions'][:3]):  # Show first 3
                        connector = "│  │  ├─" if i < min(len(topic['subscriptions']), 3) - 1 else "│  │  └─"
                        print(f"{connector} {sub['name']} ({sub.get('type', 'unknown')})")
                        if sub.get('push_endpoint'):
                            print(f"│  │     └─ 🌐 {sub['push_endpoint']}")
                    
                    if len(topic['subscriptions']) > 3:
                        print(f"│  │     └─ ... and {len(topic['subscriptions']) - 3} more subscriptions")
                else:
                    print(f"│  ├─ 📋 Subscriptions: None")
                
                if topic['label_count'] > 0:
                    print(f"│  ├─ 🏷️  Labels: {topic['label_count']}")
                
                print(f"│  └─ 🌐 Path: {topic['full_path']}")
            print(f"╰─")

        # Show cost estimation
        print(f"\n💰 Pub/Sub Messaging Costs:")
        if topics_to_create:
            topic = topics_to_create[0]
            
            # Base costs: $40 per TiB throughput, $0.50 per million operations
            print(f"   ├─ 📡 Message throughput: $40/TiB/month")
            print(f"   ├─ 🔄 API operations: $0.50/million requests")
            print(f"   ├─ 📦 Message retention: Free (up to 7 days)")
            
            if topic['subscription_count'] > 0:
                print(f"   ├─ 📋 Subscriptions ({topic['subscription_count']}): Free")
                if topic['push_subscriptions'] > 0:
                    print(f"   ├─ 📤 Push delivery: Included")
            
            print(f"   ├─ 🌍 Global distribution: Included")
            print(f"   └─ 📊 Typical cost: $0.40-$2.00/month (1GB throughput)")
        else:
            print(f"   ├─ 📡 Message throughput: $40/TiB/month")
            print(f"   ├─ 🔄 API operations: $0.50/million requests")
            print(f"   ├─ 📋 Subscriptions: Free")
            print(f"   └─ 📦 Message retention: Free (up to 7 days)")

        return {
            'resource_type': 'gcp_pubsub',
            'name': desired_topic_name,
            'topics_to_create': topics_to_create,
            'topics_to_keep': topics_to_keep,
            'topics_to_remove': topics_to_remove,
            'existing_topics': existing_topics,
            'topic_name': desired_topic_name,
            'subscription_count': len(self.subscription_names),
            'message_ordering_enabled': self.message_ordering_enabled,
            'estimated_cost': "$0.40-$2.00/month"
        }

    def create(self) -> Dict[str, Any]:
        self._ensure_authenticated()
        
        existing_topic = self._find_existing_topic()
        if existing_topic:
            print(f"🔄 Topic '{self.topic_name}' already exists")
            self.topic_exists = True
        else:
            print(f"🚀 Creating Pub/Sub topic: {self.topic_name}")
            self._create_new_topic()
        
        # Create subscriptions
        if self.subscription_names:
            self._create_subscriptions()
        
        return self._get_topic_info()

    def _find_existing_topic(self) -> bool:
        try:
            self.publisher_client.get_topic(request={"topic": self.topic_path})
            return True
        except Exception:
            return False

    def _create_new_topic(self):
        try:
            from google.cloud import pubsub_v1
            
            # Build topic
            topic = pubsub_v1.Topic(
                name=self.topic_path,
                labels=self.topic_labels,
                message_retention_duration=self.message_retention_duration
            )
            
            if self.message_ordering_enabled:
                topic.message_storage_policy = pubsub_v1.MessageStoragePolicy(
                    allowed_persistence_regions=["us-central1", "us-east1"]
                )

            # Create topic
            self.publisher_client.create_topic(request={"name": self.topic_path, "topic": topic})
            self.topic_exists = True
            
            print(f"✅ Pub/Sub topic created!")
            print(f"📍 Topic Path: {self.topic_path}")

        except Exception as e:
            print(f"❌ Failed to create topic: {str(e)}")
            raise

    def _create_subscriptions(self):
        for sub_name in self.subscription_names:
            self._create_subscription(sub_name)

    def _create_subscription(self, sub_name: str):
        try:
            from google.cloud import pubsub_v1
            
            sub_path = f"projects/{self.gcp_client.project}/subscriptions/{sub_name}"
            config = self.subscription_configs.get(sub_name, {})
            
            # Check if subscription exists
            try:
                self.subscriber_client.get_subscription(request={"subscription": sub_path})
                print(f"   📋 Subscription '{sub_name}' already exists")
                self.subscription_paths[sub_name] = sub_path
                return
            except Exception:
                pass  # Subscription doesn't exist, create it
            
            # Build subscription
            subscription = pubsub_v1.Subscription(
                name=sub_path,
                topic=self.topic_path,
                ack_deadline_seconds=config.get('ack_deadline_seconds', 10),
                retain_acked_messages=config.get('retain_acked_messages', False),
                message_retention_duration=config.get('message_retention_duration', "604800s"),
                labels=config.get('labels', {})
            )
            
            # Add push config if specified
            if config.get('type') == 'push' and config.get('push_endpoint'):
                subscription.push_config = pubsub_v1.PushConfig(
                    push_endpoint=config['push_endpoint'],
                    attributes=config.get('push_attributes', {})
                )
            
            # Add dead letter policy if specified
            if config.get('dead_letter_topic'):
                subscription.dead_letter_policy = pubsub_v1.DeadLetterPolicy(
                    dead_letter_topic=config['dead_letter_topic'],
                    max_delivery_attempts=config.get('max_delivery_attempts', 5)
                )
            
            # Create subscription
            self.subscriber_client.create_subscription(request={
                "name": sub_path,
                "subscription": subscription
            })
            
            self.subscription_paths[sub_name] = sub_path
            print(f"   📋 Created subscription: {sub_name}")

        except Exception as e:
            print(f"⚠️  Failed to create subscription {sub_name}: {str(e)}")

    def destroy(self) -> Dict[str, Any]:
        self._ensure_authenticated()
        print(f"🗑️  Destroying Pub/Sub topic: {self.topic_name}")

        try:
            # Delete subscriptions first
            for sub_name, sub_path in self.subscription_paths.items():
                try:
                    self.subscriber_client.delete_subscription(request={"subscription": sub_path})
                    print(f"   🗑️  Deleted subscription: {sub_name}")
                except Exception as e:
                    print(f"⚠️  Failed to delete subscription {sub_name}: {e}")

            # Delete topic
            if self.topic_exists:
                self.publisher_client.delete_topic(request={"topic": self.topic_path})
                print(f"✅ Pub/Sub topic destroyed!")

            return {'success': True, 'topic_name': self.topic_name, 'status': 'deleted'}

        except Exception as e:
            print(f"❌ Failed to destroy topic: {str(e)}")
            return {'success': False, 'error': str(e)}

    def _get_topic_info(self) -> Dict[str, Any]:
        try:
            topic = self.publisher_client.get_topic(request={"topic": self.topic_path})
            
            return {
                'success': True,
                'topic_name': self.topic_name,
                'topic_path': self.topic_path,
                'subscriptions': list(self.subscription_paths.keys()),
                'message_ordering': self.message_ordering_enabled,
                'labels': dict(topic.labels) if topic.labels else {}
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def _estimate_monthly_cost(self) -> str:
        # Rough estimation: $40 per TiB of message throughput, $0.50 per million operations
        monthly_messages = 1_000_000
        avg_message_size = 1024  # 1KB
        
        # Message throughput cost
        throughput_cost = (monthly_messages * avg_message_size / (1024**4)) * 40
        
        # Operations cost
        operations_cost = (monthly_messages / 1_000_000) * 0.50
        
        total_cost = throughput_cost + operations_cost
        return f"~${total_cost:.3f}/month"

    # Rails-like chainable methods
    def subscription(self, name: str, **config) -> 'PubSub':
        """Add a subscription"""
        self.subscription_names.append(name)
        self.subscription_configs[name] = config
        return self

    def pull_subscription(self, name: str, **config) -> 'PubSub':
        """Add a pull subscription"""
        config['type'] = 'pull'
        return self.subscription(name, **config)

    def push_subscription(self, name: str, endpoint: str, **config) -> 'PubSub':
        """Add a push subscription"""
        config.update({'type': 'push', 'push_endpoint': endpoint})
        return self.subscription(name, **config)

    def ordered_delivery(self, enabled: bool = True) -> 'PubSub':
        """Enable message ordering"""
        self.message_ordering_enabled = enabled
        return self

    def retention(self, duration: str) -> 'PubSub':
        """Set message retention duration (e.g., '604800s' for 7 days)"""
        self.message_retention_duration = duration
        return self

    def labels(self, labels: Dict[str, str]) -> 'PubSub':
        """Set topic labels"""
        self.topic_labels.update(labels)
        return self

    def label(self, key: str, value: str) -> 'PubSub':
        """Add a single label"""
        self.topic_labels[key] = value
        return self

    # Topic operations
    def publish_message(self, data: str, attributes: Dict[str, str] = None, ordering_key: str = None) -> str:
        """Publish a message to the topic"""
        if not self.topic_exists:
            raise ValueError("Topic not created. Call .create() first.")

        try:
            # Convert string data to bytes
            data_bytes = data.encode('utf-8')
            
            # Prepare publish kwargs
            kwargs = {'data': data_bytes}
            if attributes:
                kwargs['attributes'] = attributes
            if ordering_key and self.message_ordering_enabled:
                kwargs['ordering_key'] = ordering_key

            # Publish message
            future = self.publisher_client.publish(self.topic_path, **kwargs)
            message_id = future.result()  # Wait for the publish to complete
            
            return message_id

        except Exception as e:
            print(f"❌ Failed to publish message: {e}")
            return None

    def pull_messages(self, subscription_name: str, max_messages: int = 1) -> List[Dict[str, Any]]:
        """Pull messages from a subscription"""
        if subscription_name not in self.subscription_paths:
            raise ValueError(f"Subscription '{subscription_name}' not found")

        try:
            from google.cloud import pubsub_v1
            
            sub_path = self.subscription_paths[subscription_name]
            
            # Pull messages
            response = self.subscriber_client.pull(
                request={
                    "subscription": sub_path,
                    "max_messages": max_messages
                }
            )

            messages = []
            for received_message in response.received_messages:
                msg = received_message.message
                messages.append({
                    'message_id': msg.message_id,
                    'data': msg.data.decode('utf-8'),
                    'attributes': dict(msg.attributes),
                    'publish_time': msg.publish_time,
                    'ack_id': received_message.ack_id
                })

            return messages

        except Exception as e:
            print(f"❌ Failed to pull messages: {e}")
            return []

    def acknowledge_message(self, subscription_name: str, ack_id: str) -> bool:
        """Acknowledge a message"""
        if subscription_name not in self.subscription_paths:
            return False

        try:
            sub_path = self.subscription_paths[subscription_name]
            self.subscriber_client.acknowledge(
                request={
                    "subscription": sub_path,
                    "ack_ids": [ack_id]
                }
            )
            return True

        except Exception as e:
            print(f"❌ Failed to acknowledge message: {e}")
            return False

    def _fetch_current_cloud_state(self) -> Dict[str, Any]:
        """Fetch current state of the Pub/Sub topic from Google Cloud
        
        This method is required by the BaseGcpResource for drift detection.
        
        Returns:
            Dictionary representing current Pub/Sub topic state
        """
        try:
            self._ensure_authenticated()
            
            # Check if topic exists
            try:
                topic = self.publisher_client.get_topic(request={"topic": self.topic_path})
                topic_exists = True
            except Exception:
                topic_exists = False
                
            if not topic_exists:
                return {"exists": False, "topic_name": self.topic_name}
            
            # Get topic details
            current_state = {
                "exists": True,
                "topic_name": self.topic_name,
                "topic_path": self.topic_path,
                "message_retention_duration": self.message_retention_duration,
                "message_ordering_enabled": self.message_ordering_enabled,
                "labels": dict(topic.labels) if topic.labels else {},
                "subscription_count": len(self.subscription_names),
                "subscriptions": []
            }
            
            # Get subscription details
            try:
                for subscription in self.publisher_client.list_topic_subscriptions(request={"topic": self.topic_path}):
                    sub_name = subscription.split('/')[-1]
                    try:
                        sub_details = self.subscriber_client.get_subscription(request={"subscription": subscription})
                        current_state["subscriptions"].append({
                            "name": sub_name,
                            "path": subscription,
                            "ack_deadline_seconds": sub_details.ack_deadline_seconds,
                            "type": "push" if sub_details.push_config.push_endpoint else "pull"
                        })
                    except Exception:
                        pass  # Skip subscriptions we can't access
            except Exception:
                pass  # Topic exists but we can't list subscriptions
                
            return current_state
            
        except Exception as e:
            return {"exists": False, "error": str(e)} 