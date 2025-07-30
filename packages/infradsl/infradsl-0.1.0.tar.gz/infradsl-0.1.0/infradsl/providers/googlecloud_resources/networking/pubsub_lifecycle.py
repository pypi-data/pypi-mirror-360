"""
GCP PubSub Lifecycle Mixin

Lifecycle operations for Google Cloud Pub/Sub messaging service.
Handles create, destroy, and preview operations with smart state management.
"""

from typing import Dict, Any, List, Optional


class PubSubLifecycleMixin:
    """
    Mixin for Pub/Sub lifecycle operations.
    
    This mixin provides:
    - Create operation with smart state management
    - Destroy operation with safety checks
    - Preview operation for infrastructure planning
    - Message publishing and consumption operations
    - State comparison and drift detection
    """
    
    def preview(self) -> Dict[str, Any]:
        """
        Preview what will be created, kept, and removed.
        
        Returns:
            Dict containing preview information and cost estimates
        """
        self._ensure_authenticated()
        
        # Validate configuration
        self._validate_pubsub_configuration()
        
        # Get current cloud state
        current_state = self._fetch_current_cloud_state()
        
        # Discover all existing topics
        existing_topics = self._discover_existing_topics()
        
        # Determine actions needed
        actions = self._determine_pubsub_actions(current_state)
        
        # Display preview
        self._display_pubsub_preview(actions, current_state, existing_topics)
        
        # Return structured data
        return {
            'resource_type': 'gcp_pubsub',
            'name': self.topic_name,
            'current_state': current_state,
            'actions': actions,
            'estimated_cost': self._calculate_pubsub_cost(),
            'configuration': self._get_pubsub_configuration_summary()
        }
        
    def create(self) -> Dict[str, Any]:
        """
        Create or update the Pub/Sub topic and subscriptions.
        
        Returns:
            Dict containing creation results and resource information
        """
        self._ensure_authenticated()
        
        # Validate configuration
        self._validate_pubsub_configuration()
        
        # Get current state
        current_state = self._fetch_current_cloud_state()
        
        # Determine what needs to be done
        actions = self._determine_pubsub_actions(current_state)
        
        # Execute actions
        result = self._execute_pubsub_actions(actions, current_state)
        
        # Update state
        self.topic_exists = True
        self.topic_created = True
        
        return result
        
    def destroy(self) -> Dict[str, Any]:
        """
        Destroy the Pub/Sub topic and all subscriptions.
        
        Returns:
            Dict containing destruction results
        """
        self._ensure_authenticated()
        
        print(f"🗑️  Destroying Pub/Sub topic: {self.topic_name}")
        
        try:
            # Get current state
            current_state = self._fetch_current_cloud_state()
            
            if not current_state.get("exists", False):
                print(f"⚠️  Pub/Sub topic '{self.topic_name}' does not exist")
                return {"success": True, "message": "Topic does not exist", "name": self.topic_name}
            
            # Show what will be destroyed
            self._display_pubsub_destruction_preview(current_state)
            
            # Perform destruction
            destruction_results = []
            
            # 1. Delete subscriptions first
            for subscription in current_state.get("subscriptions", []):
                try:
                    self.subscriber_client.delete_subscription(
                        request={"subscription": subscription["path"]}
                    )
                    destruction_results.append(("subscription", subscription["name"], True))
                    print(f"   🗑️  Deleted subscription: {subscription['name']}")
                except Exception as e:
                    print(f"   ⚠️  Failed to delete subscription {subscription['name']}: {str(e)}")
                    destruction_results.append(("subscription", subscription["name"], False))
            
            # 2. Delete the topic
            try:
                self.publisher_client.delete_topic(request={"topic": self.topic_path})
                destruction_results.append(("topic", self.topic_name, True))
                print(f"   🗑️  Deleted topic: {self.topic_name}")
            except Exception as e:
                print(f"   ⚠️  Failed to delete topic: {str(e)}")
                destruction_results.append(("topic", self.topic_name, False))
            
            # Check overall success
            overall_success = all(result for _, _, result in destruction_results)
            
            if overall_success:
                print(f"✅ Pub/Sub topic '{self.topic_name}' destroyed successfully")
                self.topic_exists = False
                self.topic_created = False
                return {"success": True, "name": self.topic_name, "destroyed_resources": len(destruction_results)}
            else:
                failed_resources = [name for _, name, result in destruction_results if not result]
                print(f"⚠️  Partial failure destroying topic. Failed: {failed_resources}")
                return {"success": False, "name": self.topic_name, "error": f"Failed to destroy: {failed_resources}"}
                
        except Exception as e:
            print(f"❌ Error destroying Pub/Sub topic: {str(e)}")
            return {"success": False, "name": self.topic_name, "error": str(e)}
            
    def publish_message(self, data: str, attributes: Dict[str, str] = None, ordering_key: str = None) -> str:
        """
        Publish a message to the topic.
        
        Args:
            data: Message data as string
            attributes: Optional message attributes
            ordering_key: Optional ordering key for ordered delivery
            
        Returns:
            Message ID if successful, None otherwise
        """
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
            message_id = future.result()  # Wait for publish to complete
            
            return message_id
            
        except Exception as e:
            print(f"❌ Failed to publish message: {str(e)}")
            return None
            
    def publish_batch(self, messages: List[Dict[str, Any]]) -> List[str]:
        """
        Publish multiple messages in batch.
        
        Args:
            messages: List of message dicts with 'data' and optional 'attributes', 'ordering_key'
            
        Returns:
            List of message IDs
        """
        if not self.topic_exists:
            raise ValueError("Topic not created. Call .create() first.")
            
        message_ids = []
        futures = []
        
        try:
            # Publish all messages
            for msg in messages:
                data_bytes = msg['data'].encode('utf-8')
                kwargs = {'data': data_bytes}
                
                if 'attributes' in msg:
                    kwargs['attributes'] = msg['attributes']
                if 'ordering_key' in msg and self.message_ordering_enabled:
                    kwargs['ordering_key'] = msg['ordering_key']
                    
                future = self.publisher_client.publish(self.topic_path, **kwargs)
                futures.append(future)
                
            # Wait for all publishes to complete
            for future in futures:
                message_ids.append(future.result())
                
            return message_ids
            
        except Exception as e:
            print(f"❌ Failed to publish batch: {str(e)}")
            return message_ids
            
    def pull_messages(self, subscription_name: str, max_messages: int = 1) -> List[Dict[str, Any]]:
        """
        Pull messages from a subscription.
        
        Args:
            subscription_name: Name of the subscription
            max_messages: Maximum number of messages to pull
            
        Returns:
            List of message dictionaries
        """
        if subscription_name not in self.subscription_paths:
            raise ValueError(f"Subscription '{subscription_name}' not found")
            
        try:
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
                    'ordering_key': msg.ordering_key if msg.ordering_key else None,
                    'ack_id': received_message.ack_id
                })
                
            return messages
            
        except Exception as e:
            print(f"❌ Failed to pull messages: {str(e)}")
            return []
            
    def acknowledge_messages(self, subscription_name: str, ack_ids: List[str]) -> bool:
        """
        Acknowledge multiple messages.
        
        Args:
            subscription_name: Name of the subscription
            ack_ids: List of acknowledgment IDs
            
        Returns:
            True if successful, False otherwise
        """
        if subscription_name not in self.subscription_paths:
            return False
            
        try:
            sub_path = self.subscription_paths[subscription_name]
            self.subscriber_client.acknowledge(
                request={
                    "subscription": sub_path,
                    "ack_ids": ack_ids
                }
            )
            return True
            
        except Exception as e:
            print(f"❌ Failed to acknowledge messages: {str(e)}")
            return False
            
    def modify_ack_deadline(self, subscription_name: str, ack_ids: List[str], seconds: int) -> bool:
        """
        Modify acknowledgment deadline for messages.
        
        Args:
            subscription_name: Name of the subscription
            ack_ids: List of acknowledgment IDs
            seconds: New deadline in seconds
            
        Returns:
            True if successful, False otherwise
        """
        if subscription_name not in self.subscription_paths:
            return False
            
        try:
            sub_path = self.subscription_paths[subscription_name]
            self.subscriber_client.modify_ack_deadline(
                request={
                    "subscription": sub_path,
                    "ack_ids": ack_ids,
                    "ack_deadline_seconds": seconds
                }
            )
            return True
            
        except Exception as e:
            print(f"❌ Failed to modify ack deadline: {str(e)}")
            return False
            
    def seek_to_time(self, subscription_name: str, time: str) -> bool:
        """
        Seek subscription to a specific time for message replay.
        
        Args:
            subscription_name: Name of the subscription
            time: Time to seek to (ISO 8601 format)
            
        Returns:
            True if successful, False otherwise
        """
        if subscription_name not in self.subscription_paths:
            return False
            
        try:
            from google.protobuf import timestamp_pb2
            
            sub_path = self.subscription_paths[subscription_name]
            
            # Convert time string to timestamp
            timestamp = timestamp_pb2.Timestamp()
            timestamp.FromJsonString(time)
            
            self.subscriber_client.seek(
                request={
                    "subscription": sub_path,
                    "time": timestamp
                }
            )
            return True
            
        except Exception as e:
            print(f"❌ Failed to seek to time: {str(e)}")
            return False
            
    def _validate_pubsub_configuration(self):
        """Validate the Pub/Sub configuration before creation"""
        errors = []
        warnings = []
        
        # Validate topic name
        if not self.topic_name:
            errors.append("Topic name is required")
        elif not self._is_valid_topic_name(self.topic_name):
            errors.append(f"Invalid topic name: {self.topic_name}")
        
        # Validate retention duration
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
                errors.append(f"Invalid ack deadline for {sub_name}: {ack_deadline}")
            
            # Validate push endpoint
            if config.get('type') == 'push' and not config.get('push_endpoint'):
                errors.append(f"Push subscription {sub_name} missing endpoint")
        
        # Performance warnings
        if len(self.subscription_names) > 10:
            warnings.append(f"Large number of subscriptions ({len(self.subscription_names)}) may impact performance")
        
        # Security warnings
        if "allUsers" in self.allowed_publishers:
            warnings.append("Topic allows public publishing - ensure this is intended")
        
        if "allUsers" in self.allowed_subscribers:
            warnings.append("Topic allows public subscriptions - ensure this is intended")
        
        if errors:
            raise ValueError(f"Configuration validation failed: {', '.join(errors)}")
        
        if warnings:
            print(f"⚠️  Configuration warnings:")
            for warning in warnings:
                print(f"   - {warning}")
                
    def _determine_pubsub_actions(self, current_state: Dict[str, Any]) -> Dict[str, Any]:
        """Determine what actions need to be taken based on current state"""
        actions = {
            "create_topic": False,
            "update_topic": False,
            "keep_topic": False,
            "create_subscriptions": [],
            "update_subscriptions": [],
            "delete_subscriptions": [],
            "changes": []
        }
        
        if not current_state.get("exists", False):
            actions["create_topic"] = True
            actions["changes"].append("Create new Pub/Sub topic")
            
            # All subscriptions need to be created
            for sub_name in self.subscription_names:
                actions["create_subscriptions"].append(sub_name)
                actions["changes"].append(f"Create subscription: {sub_name}")
        else:
            # Compare current state with desired state
            topic_changes = self._detect_topic_drift(current_state)
            subscription_changes = self._detect_subscription_drift(current_state)
            
            if topic_changes:
                actions["update_topic"] = True
                actions["changes"].extend(topic_changes)
            
            if subscription_changes["create"]:
                actions["create_subscriptions"] = subscription_changes["create"]
                for sub in subscription_changes["create"]:
                    actions["changes"].append(f"Create subscription: {sub}")
            
            if subscription_changes["update"]:
                actions["update_subscriptions"] = subscription_changes["update"]
                for sub in subscription_changes["update"]:
                    actions["changes"].append(f"Update subscription: {sub}")
            
            if subscription_changes["delete"]:
                actions["delete_subscriptions"] = subscription_changes["delete"]
                for sub in subscription_changes["delete"]:
                    actions["changes"].append(f"Delete subscription: {sub}")
            
            if not actions["changes"]:
                actions["keep_topic"] = True
                actions["changes"].append("No changes needed")
                
        return actions
        
    def _detect_topic_drift(self, current_state: Dict[str, Any]) -> List[str]:
        """Detect differences between current and desired topic configuration"""
        changes = []
        
        # Compare retention duration
        current_retention = current_state.get("message_retention_duration", 604800)
        desired_retention = int(self.message_retention_duration.rstrip('s'))
        if current_retention != desired_retention:
            changes.append(f"Retention: {current_retention}s → {desired_retention}s")
        
        # Compare message ordering
        current_ordering = current_state.get("message_ordering_enabled", False)
        if current_ordering != self.message_ordering_enabled:
            changes.append(f"Message ordering: {current_ordering} → {self.message_ordering_enabled}")
        
        # Compare encryption
        current_kms = current_state.get("kms_key_name")
        if self.kms_key_name != current_kms:
            changes.append(f"Encryption key: {current_kms or 'None'} → {self.kms_key_name or 'None'}")
        
        # Compare schema
        current_schema = current_state.get("schema_name")
        if self.schema_name != current_schema:
            changes.append(f"Schema: {current_schema or 'None'} → {self.schema_name or 'None'}")
        
        return changes
        
    def _detect_subscription_drift(self, current_state: Dict[str, Any]) -> Dict[str, List[str]]:
        """Detect differences in subscription configuration"""
        current_subs = {sub["name"]: sub for sub in current_state.get("subscriptions", [])}
        desired_subs = set(self.subscription_names)
        current_sub_names = set(current_subs.keys())
        
        changes = {
            "create": list(desired_subs - current_sub_names),
            "update": [],
            "delete": list(current_sub_names - desired_subs)
        }
        
        # Check for updates needed
        for sub_name in desired_subs & current_sub_names:
            current_config = current_subs[sub_name]
            desired_config = self.subscription_configs.get(sub_name, {})
            
            # Compare configurations
            if self._subscription_config_differs(current_config, desired_config):
                changes["update"].append(sub_name)
                
        return changes
        
    def _subscription_config_differs(self, current: Dict[str, Any], desired: Dict[str, Any]) -> bool:
        """Check if subscription configuration differs"""
        # Compare type
        current_type = current.get("type", "pull")
        desired_type = desired.get("type", "pull")
        if current_type != desired_type:
            return True
            
        # Compare push endpoint
        if desired_type == "push":
            if current.get("push_endpoint") != desired.get("push_endpoint"):
                return True
                
        # Compare ack deadline
        current_ack = current.get("ack_deadline_seconds", 10)
        desired_ack = desired.get("ack_deadline_seconds", self.default_ack_deadline_seconds)
        if current_ack != desired_ack:
            return True
            
        # Compare other settings
        settings_to_compare = [
            "retain_acked_messages",
            "enable_exactly_once_delivery",
            "dead_letter_enabled"
        ]
        
        for setting in settings_to_compare:
            if current.get(setting, False) != desired.get(setting, False):
                return True
                
        return False
        
    def _execute_pubsub_actions(self, actions: Dict[str, Any], current_state: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the determined actions"""
        if actions["create_topic"]:
            return self._create_pubsub_topic()
        elif actions["update_topic"] or actions["create_subscriptions"] or actions["update_subscriptions"]:
            return self._update_pubsub_resources(current_state, actions)
        else:
            return self._keep_pubsub_topic(current_state)
            
    def _create_pubsub_topic(self) -> Dict[str, Any]:
        """Create a new Pub/Sub topic with subscriptions"""
        print(f"\n🚀 Creating Pub/Sub topic: {self.topic_name}")
        print(f"   📦 Retention: {int(self.message_retention_duration.rstrip('s')) // 86400} days")
        print(f"   🔄 Ordering: {'Enabled' if self.message_ordering_enabled else 'Disabled'}")
        
        if self.subscription_names:
            sub_types = self._get_subscription_types()
            print(f"   📋 Subscriptions: {sub_types['total']} total")
            if sub_types['pull'] > 0:
                print(f"      📥 Pull: {sub_types['pull']}")
            if sub_types['push'] > 0:
                print(f"      📤 Push: {sub_types['push']}")
        
        try:
            from google.cloud import pubsub_v1
            
            # Build topic
            topic = pubsub_v1.Topic(
                name=self.topic_path,
                labels=self.topic_labels,
                message_retention_duration={'seconds': int(self.message_retention_duration.rstrip('s'))}
            )
            
            # Add KMS encryption if specified
            if self.kms_key_name:
                topic.kms_key_name = self.kms_key_name
                
            # Add schema if specified
            if self.schema_name:
                topic.schema_settings = pubsub_v1.SchemaSettings(
                    schema=f"projects/{self.project_id}/schemas/{self.schema_name}",
                    encoding=self.schema_encoding if hasattr(self, 'schema_encoding') else "JSON"
                )
                
            # Enable message ordering if specified
            if self.message_ordering_enabled:
                topic.message_storage_policy = pubsub_v1.MessageStoragePolicy(
                    allowed_persistence_regions=["us-central1", "us-east1"]
                )
                
            # Create topic
            self.publisher_client.create_topic(request={"name": self.topic_path, "topic": topic})
            self.topic_exists = True
            
            print(f"\n✅ Pub/Sub topic created successfully!")
            print(f"   📡 Topic: {self.topic_name}")
            print(f"   🌐 Path: {self.topic_path}")
            
            # Create subscriptions
            if self.subscription_names:
                self._create_subscriptions()
                
            # Set IAM policies if specified
            if self.allowed_publishers or self.allowed_subscribers:
                self._set_iam_policies()
                
            print(f"   💰 Estimated Cost: {self._calculate_pubsub_cost()}")
            
            return {
                "success": True,
                "name": self.topic_name,
                "path": self.topic_path,
                "subscriptions": self.subscription_names,
                "retention_days": int(self.message_retention_duration.rstrip('s')) // 86400,
                "message_ordering": self.message_ordering_enabled,
                "estimated_cost": self._calculate_pubsub_cost(),
                "created": True
            }
                
        except Exception as e:
            print(f"❌ Failed to create Pub/Sub topic: {str(e)}")
            raise
            
    def _update_pubsub_resources(self, current_state: Dict[str, Any], actions: Dict[str, Any]) -> Dict[str, Any]:
        """Update existing Pub/Sub resources"""
        print(f"\n🔄 Updating Pub/Sub resources: {self.topic_name}")
        print(f"   📋 Changes to apply:")
        for change in actions["changes"]:
            print(f"      • {change}")
            
        try:
            results = []
            
            # Update topic if needed
            if actions["update_topic"]:
                # Note: Some topic properties cannot be updated after creation
                print(f"   ⚠️  Note: Some topic properties cannot be updated after creation")
                
            # Create new subscriptions
            for sub_name in actions["create_subscriptions"]:
                result = self._create_subscription(sub_name)
                results.append(("create_subscription", sub_name, result))
                
            # Update existing subscriptions
            for sub_name in actions["update_subscriptions"]:
                result = self._update_subscription(sub_name)
                results.append(("update_subscription", sub_name, result))
                
            # Delete unwanted subscriptions
            for sub_name in actions["delete_subscriptions"]:
                result = self._delete_subscription(sub_name, current_state)
                results.append(("delete_subscription", sub_name, result))
                
            print(f"\n✅ Pub/Sub resources updated successfully!")
            print(f"   📡 Topic: {self.topic_name}")
            print(f"   🔄 Changes Applied: {len(actions['changes'])}")
            
            return {
                "success": True,
                "name": self.topic_name,
                "changes_applied": len(actions["changes"]),
                "results": results,
                "updated": True
            }
                
        except Exception as e:
            print(f"❌ Failed to update Pub/Sub resources: {str(e)}")
            raise
            
    def _keep_pubsub_topic(self, current_state: Dict[str, Any]) -> Dict[str, Any]:
        """Keep existing Pub/Sub topic (no changes needed)"""
        print(f"\n✅ Pub/Sub topic '{self.topic_name}' is up to date")
        print(f"   📡 Topic: {self.topic_name}")
        print(f"   📦 Retention: {current_state.get('message_retention_duration', 604800) // 86400} days")
        print(f"   📋 Subscriptions: {current_state.get('subscription_count', 0)}")
        print(f"   🌐 Path: {current_state.get('topic_path', 'Unknown')}")
        
        return {
            "success": True,
            "name": self.topic_name,
            "path": current_state.get('topic_path'),
            "retention_days": current_state.get('message_retention_duration', 604800) // 86400,
            "subscription_count": current_state.get('subscription_count', 0),
            "unchanged": True
        }
        
    def _create_subscriptions(self):
        """Create all configured subscriptions"""
        for sub_name in self.subscription_names:
            self._create_subscription(sub_name)
            
    def _create_subscription(self, sub_name: str) -> bool:
        """Create a single subscription"""
        try:
            from google.cloud import pubsub_v1
            
            sub_path = f"projects/{self.project_id}/subscriptions/{sub_name}"
            config = self.subscription_configs.get(sub_name, {})
            
            # Build subscription
            subscription = pubsub_v1.Subscription(
                name=sub_path,
                topic=self.topic_path,
                ack_deadline_seconds=config.get('ack_deadline_seconds', self.default_ack_deadline_seconds),
                retain_acked_messages=config.get('retain_acked_messages', self.default_retain_acked_messages),
                message_retention_duration={'seconds': int(config.get('message_retention_duration', self.message_retention_duration).rstrip('s'))},
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
                
            # Add retry policy if specified
            if 'retry_policy_min_backoff' in config:
                subscription.retry_policy = pubsub_v1.RetryPolicy(
                    minimum_backoff={'seconds': int(config['retry_policy_min_backoff'].rstrip('s'))},
                    maximum_backoff={'seconds': int(config.get('retry_policy_max_backoff', '600s').rstrip('s'))}
                )
                
            # Add filter if specified
            if 'filter' in config:
                subscription.filter = config['filter']
                
            # Enable exactly-once delivery if specified
            if config.get('enable_exactly_once_delivery', self.default_enable_exactly_once_delivery):
                subscription.enable_exactly_once_delivery = True
                
            # Create subscription
            self.subscriber_client.create_subscription(request={
                "name": sub_path,
                "subscription": subscription
            })
            
            self.subscription_paths[sub_name] = sub_path
            self.subscriptions_created[sub_name] = True
            
            sub_type = config.get('type', 'pull')
            print(f"   📋 Created {sub_type} subscription: {sub_name}")
            
            return True
            
        except Exception as e:
            print(f"   ⚠️  Failed to create subscription {sub_name}: {str(e)}")
            return False
            
    def _update_subscription(self, sub_name: str) -> bool:
        """Update an existing subscription"""
        # Note: Most subscription properties cannot be updated after creation
        # This is a placeholder for future enhancement
        print(f"   ⚠️  Subscription updates limited - may need to recreate: {sub_name}")
        return True
        
    def _delete_subscription(self, sub_name: str, current_state: Dict[str, Any]) -> bool:
        """Delete a subscription"""
        try:
            # Find subscription path from current state
            for sub in current_state.get("subscriptions", []):
                if sub["name"] == sub_name:
                    self.subscriber_client.delete_subscription(
                        request={"subscription": sub["path"]}
                    )
                    print(f"   🗑️  Deleted subscription: {sub_name}")
                    return True
                    
            return False
            
        except Exception as e:
            print(f"   ⚠️  Failed to delete subscription {sub_name}: {str(e)}")
            return False
            
    def _set_iam_policies(self):
        """Set IAM policies for topic access control"""
        try:
            from google.iam.v1 import iam_policy_pb2, policy_pb2
            
            # Get current policy
            policy = self.publisher_client.get_iam_policy(
                request={"resource": self.topic_path}
            )
            
            # Add publisher bindings
            if self.allowed_publishers:
                publisher_binding = policy_pb2.Binding(
                    role="roles/pubsub.publisher",
                    members=[f"user:{identity}" if "@" in identity else identity 
                            for identity in self.allowed_publishers]
                )
                policy.bindings.append(publisher_binding)
                
            # Add subscriber bindings
            if self.allowed_subscribers:
                subscriber_binding = policy_pb2.Binding(
                    role="roles/pubsub.subscriber",
                    members=[f"user:{identity}" if "@" in identity else identity 
                            for identity in self.allowed_subscribers]
                )
                policy.bindings.append(subscriber_binding)
                
            # Set the updated policy
            self.publisher_client.set_iam_policy(
                request={"resource": self.topic_path, "policy": policy}
            )
            
            print(f"   🔐 IAM policies configured")
            
        except Exception as e:
            print(f"   ⚠️  Failed to set IAM policies: {str(e)}")
            
    def _display_pubsub_preview(self, actions: Dict[str, Any], current_state: Dict[str, Any], existing_topics: Dict[str, Any]):
        """Display preview of actions to be taken"""
        print(f"\n📡 Google Cloud Pub/Sub Preview")
        print(f"   🎯 Topic: {self.topic_name}")
        print(f"   📦 Retention: {int(self.message_retention_duration.rstrip('s')) // 86400} days")
        print(f"   🔄 Ordering: {'Enabled' if self.message_ordering_enabled else 'Disabled'}")
        
        if actions["create_topic"]:
            print(f"\n╭─ 🆕 WILL CREATE")
            print(f"├─ 📡 Topic: {self.topic_name}")
            print(f"├─ 📦 Retention: {int(self.message_retention_duration.rstrip('s')) // 86400} days")
            print(f"├─ 🔄 Message Ordering: {'Enabled' if self.message_ordering_enabled else 'Disabled'}")
            
            if self.kms_key_name:
                print(f"├─ 🔐 Encryption: {self.kms_key_name}")
                
            if self.schema_name:
                print(f"├─ 📋 Schema: {self.schema_name}")
                
            if self.subscription_names:
                sub_types = self._get_subscription_types()
                print(f"├─ 📋 Subscriptions: {sub_types['total']}")
                if sub_types['pull'] > 0:
                    print(f"│  ├─ 📥 Pull: {sub_types['pull']}")
                if sub_types['push'] > 0:
                    print(f"│  └─ 📤 Push: {sub_types['push']}")
                    
            print(f"├─ 🚀 Features:")
            print(f"│  ├─ 🌊 At-least-once delivery")
            print(f"│  ├─ 📈 Auto-scaling to millions of messages")
            print(f"│  ├─ 🔄 Message replay capability")
            print(f"│  └─ 🌍 Global message routing")
            print(f"╰─ 💰 Estimated Cost: {self._calculate_pubsub_cost()}")
            
        elif any([actions["update_topic"], actions["create_subscriptions"], actions["update_subscriptions"], actions["delete_subscriptions"]]):
            print(f"\n╭─ 🔄 WILL UPDATE")
            print(f"├─ 📡 Topic: {self.topic_name}")
            print(f"├─ 📋 Changes:")
            for change in actions["changes"]:
                print(f"│  • {change}")
            print(f"╰─ 💰 Updated Cost: {self._calculate_pubsub_cost()}")
            
        else:
            print(f"\n╭─ ✅ WILL KEEP")
            print(f"├─ 📡 Topic: {self.topic_name}")
            print(f"├─ 📦 Retention: {current_state.get('message_retention_duration', 604800) // 86400} days")
            print(f"├─ 📋 Subscriptions: {current_state.get('subscription_count', 0)}")
            print(f"╰─ 🌐 Path: {current_state.get('topic_path', 'Unknown')}")
            
    def _display_pubsub_destruction_preview(self, current_state: Dict[str, Any]):
        """Display what will be destroyed"""
        print(f"\n⚠️  DESTRUCTION PREVIEW")
        print(f"   🗑️  Topic: {self.topic_name}")
        print(f"   📋 Subscriptions: {current_state.get('subscription_count', 0)}")
        
        if current_state.get("subscriptions"):
            print(f"   📋 Subscriptions to delete:")
            for sub in current_state["subscriptions"]:
                print(f"      • {sub['name']} ({sub.get('type', 'unknown')})")
                
        print(f"   ⚠️  ALL MESSAGES IN TOPIC WILL BE PERMANENTLY LOST")
        print(f"   ⚠️  ALL SUBSCRIPTIONS WILL BE DELETED")
        
    def _calculate_pubsub_cost(self) -> str:
        """Calculate estimated monthly cost"""
        base_cost = self._estimate_pubsub_cost()
        return f"${base_cost:.2f}/month"
        
    def _get_pubsub_configuration_summary(self) -> Dict[str, Any]:
        """Get summary of current Pub/Sub configuration"""
        sub_types = self._get_subscription_types()
        
        return {
            "topic_name": self.topic_name,
            "description": self.topic_description,
            "message_retention_duration": self.message_retention_duration,
            "retention_days": int(self.message_retention_duration.rstrip('s')) // 86400,
            "message_ordering_enabled": self.message_ordering_enabled,
            "kms_key_name": self.kms_key_name,
            "schema_name": self.schema_name,
            "subscription_count": sub_types["total"],
            "pull_subscriptions": sub_types["pull"],
            "push_subscriptions": sub_types["push"],
            "subscription_names": self.subscription_names,
            "topic_labels": self.topic_labels,
            "allowed_publishers": self.allowed_publishers,
            "allowed_subscribers": self.allowed_subscribers
        }
        
    def optimize_for(self, priority: str):
        """
        Use Cross-Cloud Magic to optimize for cost/performance/reliability/compliance
        
        Args:
            priority: Optimization priority - "cost", "performance", "reliability", "compliance"
            
        Returns:
            Self for method chaining
        """
        valid_priorities = ["cost", "performance", "reliability", "compliance"]
        if priority not in valid_priorities:
            raise ValueError(f"Priority must be one of: {valid_priorities}. Got: {priority}")
        
        print(f"🎯 Cross-Cloud Magic: Optimizing Pub/Sub for {priority}")
        
        if priority == "cost":
            print("💰 Cost optimization: Configuring cost-effective messaging")
            # Minimal retention, no ordering
            self.retention_days(1)
            self.ordered_delivery(False)
            self.label("optimization", "cost")
            print("   💡 Configured for minimum retention and basic delivery")
                
        elif priority == "performance":
            print("⚡ Performance optimization: Configuring high-performance messaging")
            # Standard retention, no ordering for speed
            self.retention_days(3)
            self.ordered_delivery(False)
            self.label("optimization", "performance")
            print("   💡 Configured for maximum throughput without ordering")
                
        elif priority == "reliability":
            print("🛡️ Reliability optimization: Configuring reliable messaging")
            # Full retention, ordered delivery
            self.retention_days(7)
            self.ordered_delivery(True)
            self.label("optimization", "reliability")
            print("   💡 Configured for ordered delivery and maximum retention")
                
        elif priority == "compliance":
            print("📋 Compliance optimization: Configuring compliant messaging")
            # Full retention, encryption, audit
            self.retention_days(7)
            self.ordered_delivery(True)
            if hasattr(self, 'project_id') and self.project_id:
                self.encryption_key(f"projects/{self.project_id}/locations/global/keyRings/pubsub/cryptoKeys/topic-key")
            self.label("optimization", "compliance")
            self.label("audit", "enabled")
            self.label("encryption", "kms")
            print("   💡 Configured for compliance with encryption and audit")
            
        return self