"""
GCP Secret Manager Lifecycle Mixin

Lifecycle operations for Google Cloud Secret Manager.
Handles create, destroy, and preview operations with smart state management.
"""

from typing import Dict, Any, List, Optional, Union
import json


class SecretManagerLifecycleMixin:
    """
    Mixin for Secret Manager lifecycle operations.
    
    This mixin provides:
    - Create operation with smart state management
    - Destroy operation with safety checks
    - Preview operation for infrastructure planning
    - Secret value access and versioning operations
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
        self._validate_secret_manager_configuration()
        
        # Get current cloud state
        current_state = self._fetch_current_cloud_state()
        
        # Discover all existing secrets
        existing_secrets = self._discover_existing_secrets()
        
        # Determine actions needed
        actions = self._determine_secret_manager_actions(current_state)
        
        # Display preview
        self._display_secret_manager_preview(actions, current_state, existing_secrets)
        
        # Return structured data
        return {
            'resource_type': 'gcp_secret_manager',
            'name': self.secret_name,
            'current_state': current_state,
            'actions': actions,
            'estimated_cost': self._calculate_secret_manager_cost(),
            'configuration': self._get_secret_manager_configuration_summary()
        }
        
    def create(self) -> Dict[str, Any]:
        """
        Create or update the Secret Manager secret with versions.
        
        Returns:
            Dict containing creation results and resource information
        """
        self._ensure_authenticated()
        
        # Validate configuration and value
        self._validate_secret_manager_configuration()
        
        if not self.secret_value and not self.secret_binary:
            raise ValueError("Secret value or binary data is required")
        
        # Get current state
        current_state = self._fetch_current_cloud_state()
        
        # Determine what needs to be done
        actions = self._determine_secret_manager_actions(current_state)
        
        # Execute actions
        result = self._execute_secret_manager_actions(actions, current_state)
        
        # Update state
        self.secret_exists = True
        self.secret_created = True
        
        return result
        
    def destroy(self) -> Dict[str, Any]:
        """
        Destroy the Secret Manager secret and all versions.
        
        Returns:
            Dict containing destruction results
        """
        self._ensure_authenticated()
        
        print(f"🗑️  Destroying Secret Manager secret: {self.secret_name}")
        
        try:
            # Get current state
            current_state = self._fetch_current_cloud_state()
            
            if not current_state.get("exists", False):
                print(f"⚠️  Secret '{self.secret_name}' does not exist")
                return {"success": True, "message": "Secret does not exist", "name": self.secret_name}
            
            # Show what will be destroyed
            self._display_secret_manager_destruction_preview(current_state)
            
            # Perform destruction
            try:
                self.secret_manager_client.delete_secret(name=self.secret_resource_name)
                print(f"✅ Secret '{self.secret_name}' destroyed successfully")
                
                self.secret_exists = False
                self.secret_created = False
                
                return {
                    "success": True, 
                    "name": self.secret_name,
                    "versions_destroyed": current_state.get("version_count", 0)
                }
                
            except Exception as e:
                print(f"❌ Failed to destroy secret: {str(e)}")
                return {"success": False, "name": self.secret_name, "error": str(e)}
                
        except Exception as e:
            print(f"❌ Error destroying Secret Manager secret: {str(e)}")
            return {"success": False, "name": self.secret_name, "error": str(e)}
            
    def add_version(self, value: Union[str, dict, bytes]) -> Dict[str, Any]:
        """
        Add a new version to the secret.
        
        Args:
            value: New secret value
            
        Returns:
            Dict containing version creation results
        """
        if not self.secret_exists:
            raise ValueError("Secret not created. Call .create() first.")
            
        # Store current value
        old_value = self.secret_value
        old_binary = self.secret_binary
        
        # Update with new value
        if isinstance(value, bytes):
            self.secret_binary = value
            self.secret_value = None
        else:
            self.secret_value = value
            self.secret_binary = None
            
        try:
            result = self._add_secret_version()
            print(f"✅ New secret version added successfully")
            return result
        except Exception as e:
            # Restore old values on failure
            self.secret_value = old_value
            self.secret_binary = old_binary
            raise
            
    def get_secret_value(self, version: str = "latest") -> Dict[str, Any]:
        """
        Retrieve secret value from specific version.
        
        Args:
            version: Version identifier ("latest", "1", "2", etc.)
            
        Returns:
            Dict containing secret value and metadata
        """
        if not self.secret_exists:
            raise ValueError("Secret not created. Call .create() first.")
            
        try:
            version_name = f"{self.secret_resource_name}/versions/{version}"
            
            response = self.secret_manager_client.access_secret_version(name=version_name)
            payload = response.payload.data
            
            result = {
                'success': True,
                'secret_name': self.secret_name,
                'version_name': response.name.split('/')[-1],
                'create_time': response.create_time.isoformat() if hasattr(response, 'create_time') else None
            }
            
            # Try to decode the payload
            try:
                decoded_data = payload.decode('utf-8')
                try:
                    # Try to parse as JSON
                    result['secret_value'] = json.loads(decoded_data)
                    result['value_type'] = 'json'
                except json.JSONDecodeError:
                    # Plain string
                    result['secret_value'] = decoded_data
                    result['value_type'] = 'string'
            except UnicodeDecodeError:
                # Binary data
                result['secret_binary'] = payload
                result['value_type'] = 'binary'
                
            return result
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
            
    def list_versions(self) -> Dict[str, Any]:
        """
        List all versions of the secret.
        
        Returns:
            Dict containing version information
        """
        if not self.secret_exists:
            raise ValueError("Secret not created. Call .create() first.")
            
        try:
            versions = []
            active_count = 0
            
            for version in self.secret_manager_client.list_secret_versions(parent=self.secret_resource_name):
                version_info = {
                    'name': version.name.split('/')[-1],
                    'state': version.state.name if hasattr(version, 'state') else 'UNKNOWN',
                    'create_time': version.create_time.isoformat() if hasattr(version, 'create_time') else None,
                    'destroy_time': version.destroy_time.isoformat() if hasattr(version, 'destroy_time') else None
                }
                versions.append(version_info)
                
                if version_info['state'] == 'ENABLED':
                    active_count += 1
                    
            return {
                'success': True,
                'secret_name': self.secret_name,
                'versions': versions,
                'total_versions': len(versions),
                'active_versions': active_count
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
            
    def destroy_version(self, version: str) -> Dict[str, Any]:
        """
        Destroy a specific version of the secret.
        
        Args:
            version: Version identifier
            
        Returns:
            Dict containing destruction results
        """
        if not self.secret_exists:
            raise ValueError("Secret not created. Call .create() first.")
            
        try:
            version_name = f"{self.secret_resource_name}/versions/{version}"
            
            self.secret_manager_client.destroy_secret_version(name=version_name)
            print(f"✅ Secret version {version} destroyed successfully")
            
            return {
                'success': True,
                'secret_name': self.secret_name,
                'version': version,
                'destroyed': True
            }
            
        except Exception as e:
            print(f"❌ Failed to destroy version {version}: {str(e)}")
            return {'success': False, 'error': str(e)}
            
    def disable_version(self, version: str) -> Dict[str, Any]:
        """
        Disable a specific version of the secret.
        
        Args:
            version: Version identifier
            
        Returns:
            Dict containing disable results
        """
        if not self.secret_exists:
            raise ValueError("Secret not created. Call .create() first.")
            
        try:
            version_name = f"{self.secret_resource_name}/versions/{version}"
            
            self.secret_manager_client.disable_secret_version(name=version_name)
            print(f"✅ Secret version {version} disabled successfully")
            
            return {
                'success': True,
                'secret_name': self.secret_name,
                'version': version,
                'disabled': True
            }
            
        except Exception as e:
            print(f"❌ Failed to disable version {version}: {str(e)}")
            return {'success': False, 'error': str(e)}
            
    def enable_version(self, version: str) -> Dict[str, Any]:
        """
        Enable a specific version of the secret.
        
        Args:
            version: Version identifier
            
        Returns:
            Dict containing enable results
        """
        if not self.secret_exists:
            raise ValueError("Secret not created. Call .create() first.")
            
        try:
            version_name = f"{self.secret_resource_name}/versions/{version}"
            
            self.secret_manager_client.enable_secret_version(name=version_name)
            print(f"✅ Secret version {version} enabled successfully")
            
            return {
                'success': True,
                'secret_name': self.secret_name,
                'version': version,
                'enabled': True
            }
            
        except Exception as e:
            print(f"❌ Failed to enable version {version}: {str(e)}")
            return {'success': False, 'error': str(e)}
            
    def _validate_secret_manager_configuration(self):
        """Validate the Secret Manager configuration before creation"""
        errors = []
        warnings = []
        
        # Validate secret name
        if not self.secret_name:
            errors.append("Secret name is required")
        elif not self._is_valid_secret_name(self.secret_name):
            errors.append(f"Invalid secret name: {self.secret_name}")
        
        # Validate replication configuration
        if self.replication_policy == "user_managed":
            if not self.replica_locations:
                errors.append("User-managed replication requires replica locations")
            else:
                for location in self.replica_locations:
                    if not self._is_valid_location(location):
                        errors.append(f"Invalid replica location: {location}")
        
        # Validate rotation configuration
        if self.rotation_enabled:
            if not self.rotation_period:
                errors.append("Rotation enabled but no period specified")
            elif not self._is_valid_rotation_period(self.rotation_period):
                errors.append(f"Invalid rotation period: {self.rotation_period}")
        
        # Performance warnings
        if self.replication_policy == "user_managed" and len(self.replica_locations) > 5:
            warnings.append(f"Large number of replica locations ({len(self.replica_locations)}) will increase costs")
        
        # Security warnings
        if not self.allowed_access_identities:
            warnings.append("No access identities specified - only project admins can access")
        
        if self.rotation_enabled and self.rotation_period and self.rotation_period < 86400:
            warnings.append("Very short rotation period may cause operational issues")
        
        # Cost warnings
        if self.max_versions and self.max_versions > 10:
            warnings.append(f"High max versions ({self.max_versions}) will increase storage costs")
        
        if errors:
            raise ValueError(f"Configuration validation failed: {', '.join(errors)}")
        
        if warnings:
            print(f"⚠️  Configuration warnings:")
            for warning in warnings:
                print(f"   - {warning}")
                
    def _determine_secret_manager_actions(self, current_state: Dict[str, Any]) -> Dict[str, Any]:
        """Determine what actions need to be taken based on current state"""
        actions = {
            "create_secret": False,
            "update_secret": False,
            "keep_secret": False,
            "add_version": False,
            "update_metadata": False,
            "changes": []
        }
        
        if not current_state.get("exists", False):
            actions["create_secret"] = True
            actions["changes"].append("Create new secret")
            actions["changes"].append("Add initial version")
        else:
            # Compare current state with desired state
            metadata_changes = self._detect_secret_metadata_drift(current_state)
            
            if metadata_changes:
                actions["update_metadata"] = True
                actions["changes"].extend(metadata_changes)
            
            # Always add new version if value is provided
            if self.secret_value is not None or self.secret_binary is not None:
                actions["add_version"] = True
                actions["changes"].append("Add new secret version")
            
            if not actions["changes"]:
                actions["keep_secret"] = True
                actions["changes"].append("No changes needed")
                
        return actions
        
    def _detect_secret_metadata_drift(self, current_state: Dict[str, Any]) -> List[str]:
        """Detect differences between current and desired secret metadata"""
        changes = []
        
        # Compare replication policy
        current_replication = current_state.get("replication_policy", "automatic")
        if current_replication != self.replication_policy:
            changes.append(f"Replication: {current_replication} → {self.replication_policy}")
        
        # Compare replica locations for user-managed
        if self.replication_policy == "user_managed":
            current_locations = set(current_state.get("replica_locations", []))
            desired_locations = set(self.replica_locations)
            if current_locations != desired_locations:
                changes.append(f"Replica locations: {current_locations} → {desired_locations}")
        
        # Compare rotation settings
        current_rotation = current_state.get("rotation_enabled", False)
        if current_rotation != self.rotation_enabled:
            changes.append(f"Rotation: {current_rotation} → {self.rotation_enabled}")
            
        if self.rotation_enabled:
            current_period = current_state.get("rotation_period")
            if current_period != self.rotation_period:
                current_days = current_period // 86400 if current_period else 0
                desired_days = self.rotation_period // 86400 if self.rotation_period else 0
                changes.append(f"Rotation period: {current_days} days → {desired_days} days")
        
        # Note: Some metadata like replication policy cannot be changed after creation
        # These would require recreation of the secret
        
        return changes
        
    def _execute_secret_manager_actions(self, actions: Dict[str, Any], current_state: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the determined actions"""
        if actions["create_secret"]:
            return self._create_secret_manager_secret()
        elif actions["add_version"] or actions["update_metadata"]:
            return self._update_secret_manager_secret(current_state, actions)
        else:
            return self._keep_secret_manager_secret(current_state)
            
    def _create_secret_manager_secret(self) -> Dict[str, Any]:
        """Create a new Secret Manager secret"""
        print(f"\n🔐 Creating Secret Manager secret: {self.secret_name}")
        print(f"   🏷️  Type: {self.secret_type}")
        print(f"   🌍 Replication: {self.replication_policy}")
        
        if self.replication_policy == "user_managed":
            print(f"   📍 Locations: {len(self.replica_locations)}")
            for location in self.replica_locations[:3]:
                print(f"      • {location}")
            if len(self.replica_locations) > 3:
                print(f"      • ... and {len(self.replica_locations) - 3} more")
        
        print(f"   🔄 Rotation: {'Enabled' if self.rotation_enabled else 'Disabled'}")
        if self.rotation_enabled and self.rotation_period:
            days = self.rotation_period // 86400
            print(f"      📅 Period: {days} days")
        
        try:
            from google.cloud import secretmanager
            
            # Build replication policy
            if self.replication_policy == "automatic":
                replication = secretmanager.Replication(
                    automatic=secretmanager.Replication.Automatic()
                )
            else:
                # User-managed replication
                replicas = []
                for location in self.replica_locations:
                    replicas.append(
                        secretmanager.Replication.UserManaged.Replica(location=location)
                    )
                replication = secretmanager.Replication(
                    user_managed=secretmanager.Replication.UserManaged(replicas=replicas)
                )
            
            # Build secret
            secret = secretmanager.Secret(
                name=self.secret_resource_name,
                replication=replication,
                labels=self.secret_labels
            )
            
            # Add rotation if configured
            if self.rotation_enabled and self.rotation_period:
                secret.rotation = secretmanager.Rotation(
                    rotation_period={'seconds': self.rotation_period}
                )
                if self.next_rotation_time:
                    secret.rotation.next_rotation_time = self.next_rotation_time
                if self.rotation_topic:
                    secret.rotation.rotation_topic = self.rotation_topic
            
            # Create the secret
            created_secret = self.secret_manager_client.create_secret(
                parent=f"projects/{self.project_id}",
                secret_id=self.secret_name,
                secret=secret
            )
            
            self.secret_id = created_secret.name.split('/')[-1]
            
            print(f"\n✅ Secret Manager secret created successfully!")
            print(f"   🔐 Secret: {self.secret_name}")
            print(f"   🌐 Resource: {created_secret.name}")
            
            # Add the initial version
            version_result = self._add_secret_version()
            
            # Set IAM policies if specified
            if self.allowed_access_identities:
                self._set_secret_iam_policies()
            
            print(f"   💰 Estimated Cost: {self._calculate_secret_manager_cost()}")
            
            return {
                "success": True,
                "name": self.secret_name,
                "resource_name": created_secret.name,
                "secret_type": self.secret_type,
                "replication_policy": self.replication_policy,
                "rotation_enabled": self.rotation_enabled,
                "initial_version": version_result.get("version_name"),
                "estimated_cost": self._calculate_secret_manager_cost(),
                "created": True
            }
            
        except Exception as e:
            print(f"❌ Failed to create Secret Manager secret: {str(e)}")
            raise
            
    def _update_secret_manager_secret(self, current_state: Dict[str, Any], actions: Dict[str, Any]) -> Dict[str, Any]:
        """Update existing Secret Manager secret"""
        print(f"\n🔄 Updating Secret Manager secret: {self.secret_name}")
        print(f"   📋 Changes to apply:")
        for change in actions["changes"]:
            print(f"      • {change}")
            
        try:
            results = []
            
            # Add new version if needed
            if actions["add_version"]:
                version_result = self._add_secret_version()
                results.append(("add_version", version_result))
                
            # Update metadata if needed (limited updates possible)
            if actions["update_metadata"]:
                print(f"   ⚠️  Note: Some secret properties cannot be updated after creation")
                
            # Update IAM policies if specified
            if self.allowed_access_identities:
                self._set_secret_iam_policies()
                results.append(("update_iam", True))
                
            print(f"\n✅ Secret Manager secret updated successfully!")
            print(f"   🔐 Secret: {self.secret_name}")
            print(f"   🔄 Changes Applied: {len(actions['changes'])}")
            
            return {
                "success": True,
                "name": self.secret_name,
                "changes_applied": len(actions["changes"]),
                "results": results,
                "updated": True
            }
            
        except Exception as e:
            print(f"❌ Failed to update Secret Manager secret: {str(e)}")
            raise
            
    def _keep_secret_manager_secret(self, current_state: Dict[str, Any]) -> Dict[str, Any]:
        """Keep existing Secret Manager secret (no changes needed)"""
        print(f"\n✅ Secret Manager secret '{self.secret_name}' is up to date")
        print(f"   🔐 Secret: {self.secret_name}")
        print(f"   🏷️  Type: {current_state.get('secret_type', 'Unknown')}")
        print(f"   📦 Versions: {current_state.get('version_count', 0)} total, {current_state.get('active_versions', 0)} active")
        print(f"   🌍 Replication: {current_state.get('replication_policy', 'Unknown')}")
        print(f"   🔄 Rotation: {'Enabled' if current_state.get('rotation_enabled', False) else 'Disabled'}")
        
        return {
            "success": True,
            "name": self.secret_name,
            "resource_name": current_state.get('secret_resource_name'),
            "version_count": current_state.get('version_count', 0),
            "active_versions": current_state.get('active_versions', 0),
            "replication_policy": current_state.get('replication_policy'),
            "rotation_enabled": current_state.get('rotation_enabled', False),
            "unchanged": True
        }
        
    def _add_secret_version(self) -> Dict[str, Any]:
        """Add a version with the secret value"""
        try:
            from google.cloud import secretmanager
            
            # Prepare payload
            if self.secret_binary:
                payload = secretmanager.SecretPayload(data=self.secret_binary)
            else:
                if isinstance(self.secret_value, dict):
                    data = json.dumps(self.secret_value).encode('utf-8')
                else:
                    data = str(self.secret_value).encode('utf-8')
                payload = secretmanager.SecretPayload(data=data)
            
            # Add version
            version = self.secret_manager_client.add_secret_version(
                parent=self.secret_resource_name,
                payload=payload
            )
            
            self.secret_version_name = version.name
            version_number = version.name.split('/')[-1]
            
            print(f"   📦 Added version: {version_number}")
            
            return {
                "success": True,
                "version_name": version_number,
                "full_version_name": version.name,
                "create_time": version.create_time.isoformat() if hasattr(version, 'create_time') else None
            }
            
        except Exception as e:
            print(f"❌ Failed to add secret version: {str(e)}")
            raise
            
    def _set_secret_iam_policies(self):
        """Set IAM policies for secret access control"""
        try:
            from google.iam.v1 import iam_policy_pb2, policy_pb2
            
            # Get current policy
            policy = self.secret_manager_client.get_iam_policy(
                request={"resource": self.secret_resource_name}
            )
            
            # Add accessor bindings
            if self.allowed_access_identities:
                accessor_binding = policy_pb2.Binding(
                    role="roles/secretmanager.secretAccessor",
                    members=self.allowed_access_identities
                )
                policy.bindings.append(accessor_binding)
                
            # Set the updated policy
            self.secret_manager_client.set_iam_policy(
                request={"resource": self.secret_resource_name, "policy": policy}
            )
            
            print(f"   🔐 IAM policies configured for {len(self.allowed_access_identities)} identities")
            
        except Exception as e:
            print(f"   ⚠️  Failed to set IAM policies: {str(e)}")
            
    def _display_secret_manager_preview(self, actions: Dict[str, Any], current_state: Dict[str, Any], existing_secrets: Dict[str, Any]):
        """Display preview of actions to be taken"""
        print(f"\n🔐 Google Cloud Secret Manager Preview")
        print(f"   🎯 Secret: {self.secret_name}")
        print(f"   🏷️  Type: {self.secret_type}")
        print(f"   🌍 Replication: {self.replication_policy}")
        
        if actions["create_secret"]:
            print(f"\n╭─ 🆕 WILL CREATE")
            print(f"├─ 🔐 Secret: {self.secret_name}")
            print(f"├─ 🏷️  Type: {self.secret_type}")
            print(f"├─ 🌍 Replication: {self.replication_policy}")
            
            if self.replication_policy == "user_managed":
                print(f"├─ 📍 Locations: {len(self.replica_locations)}")
                for location in self.replica_locations[:3]:
                    print(f"│  • {location}")
                if len(self.replica_locations) > 3:
                    print(f"│  • ... and {len(self.replica_locations) - 3} more")
                    
            print(f"├─ 🔄 Rotation: {'Enabled' if self.rotation_enabled else 'Disabled'}")
            if self.rotation_enabled and self.rotation_period:
                days = self.rotation_period // 86400
                print(f"│  └─ 📅 Period: {days} days")
                
            if self.kms_key_name:
                print(f"├─ 🔐 Encryption: Customer-managed key")
                
            print(f"├─ 🚀 Features:")
            print(f"│  ├─ 🔒 AES-256 encryption")
            print(f"│  ├─ 📝 Automatic versioning")
            print(f"│  ├─ 🔐 IAM access control")
            print(f"│  └─ 📋 Audit logging")
            print(f"╰─ 💰 Estimated Cost: {self._calculate_secret_manager_cost()}")
            
        elif any([actions["add_version"], actions["update_metadata"]]):
            print(f"\n╭─ 🔄 WILL UPDATE")
            print(f"├─ 🔐 Secret: {self.secret_name}")
            print(f"├─ 📋 Changes:")
            for change in actions["changes"]:
                print(f"│  • {change}")
            print(f"╰─ 💰 Updated Cost: {self._calculate_secret_manager_cost()}")
            
        else:
            print(f"\n╭─ ✅ WILL KEEP")
            print(f"├─ 🔐 Secret: {self.secret_name}")
            print(f"├─ 📦 Versions: {current_state.get('version_count', 0)} total, {current_state.get('active_versions', 0)} active")
            print(f"├─ 🌍 Replication: {current_state.get('replication_policy', 'Unknown')}")
            print(f"╰─ 🔄 Rotation: {'Enabled' if current_state.get('rotation_enabled', False) else 'Disabled'}")
            
    def _display_secret_manager_destruction_preview(self, current_state: Dict[str, Any]):
        """Display what will be destroyed"""
        print(f"\n⚠️  DESTRUCTION PREVIEW")
        print(f"   🗑️  Secret: {self.secret_name}")
        print(f"   📦 Versions: {current_state.get('version_count', 0)}")
        print(f"   🌍 Replication: {current_state.get('replication_policy', 'Unknown')}")
        if current_state.get("replica_locations"):
            print(f"   📍 Replicated in: {len(current_state['replica_locations'])} locations")
        print(f"   ⚠️  ALL SECRET VERSIONS WILL BE PERMANENTLY DELETED")
        print(f"   ⚠️  THIS ACTION CANNOT BE UNDONE")
        
    def _calculate_secret_manager_cost(self) -> str:
        """Calculate estimated monthly cost"""
        base_cost = self._estimate_secret_manager_cost()
        return f"${base_cost:.3f}/month"
        
    def _get_secret_manager_configuration_summary(self) -> Dict[str, Any]:
        """Get summary of current Secret Manager configuration"""
        return {
            "secret_name": self.secret_name,
            "description": self.secret_description,
            "secret_type": self.secret_type,
            "replication_policy": self.replication_policy,
            "replica_locations": self.replica_locations,
            "replica_count": len(self.replica_locations) if self.replica_locations else 0,
            "rotation_enabled": self.rotation_enabled,
            "rotation_period_days": self.rotation_period // 86400 if self.rotation_period else None,
            "kms_key_name": self.kms_key_name,
            "max_versions": self.max_versions,
            "secret_labels": self.secret_labels,
            "allowed_access_count": len(self.allowed_access_identities),
            "has_value": self.secret_value is not None or self.secret_binary is not None
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
        
        print(f"🎯 Cross-Cloud Magic: Optimizing Secret Manager for {priority}")
        
        if priority == "cost":
            print("💰 Cost optimization: Configuring cost-effective secret storage")
            # Minimal configuration
            self.automatic_replication()
            self.no_rotation()
            self.max_versions(2)
            self.label("optimization", "cost")
            print("   💡 Configured for automatic replication and minimal versions")
                
        elif priority == "performance":
            print("⚡ Performance optimization: Configuring high-performance secret access")
            # Global replication for fast access
            self.automatic_replication()
            self.max_versions(5)
            self.label("optimization", "performance")
            print("   💡 Configured for global availability and fast access")
                
        elif priority == "reliability":
            print("🛡️ Reliability optimization: Configuring reliable secret storage")
            # Multi-region with rotation
            self.automatic_replication()
            self.quarterly_rotation()
            self.max_versions(10)
            self.label("optimization", "reliability")
            print("   💡 Configured for high availability and automatic rotation")
                
        elif priority == "compliance":
            print("📋 Compliance optimization: Configuring compliant secret storage")
            # Enhanced security and audit
            self.monthly_rotation()
            self.max_versions(12)  # Keep 1 year of versions
            if hasattr(self, 'project_id') and self.project_id:
                self.encryption_key(f"projects/{self.project_id}/locations/global/keyRings/secrets/cryptoKeys/secret-key")
            self.label("optimization", "compliance")
            self.label("audit", "enabled")
            self.label("retention", "1year")
            print("   💡 Configured for compliance with encryption and audit")
            
        return self