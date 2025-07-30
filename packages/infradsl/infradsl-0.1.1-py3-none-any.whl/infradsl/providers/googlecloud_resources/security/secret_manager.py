"""
Google Cloud Secret Manager Resource

Rails-like secure credential storage with automatic versioning and fine-grained access control.
Supports automatic replication, rotation, and integration with other GCP services.
"""

import json
import base64
from typing import Dict, Any, List, Optional, Union
from ..base_resource import BaseGcpResource


class SecretManager(BaseGcpResource):
    """Google Cloud Secret Manager Resource with Rails-like API"""

    def __init__(self, name: str):
        super().__init__(name)
        
        # Core configuration
        self.secret_name = name
        self.secret_value = None
        self.secret_binary = None
        
        # Replication configuration
        self.replication_policy = "automatic"  # automatic or user_managed
        self.replica_locations = []
        
        # Labels
        self.secret_labels = {}
        
        # Rotation configuration
        self.rotation_period = None
        self.next_rotation_time = None
        
        # State
        self.secret_resource_name = None
        self.secret_version_name = None
        self.secret_id = None

        # Client
        self.secret_manager_client = None

    def _initialize_managers(self):
        self.secret_manager_client = None

    def _post_authentication_setup(self):
        self.secret_manager_client = self.get_secret_manager_client()
        
        # Set resource name
        project_id = self.gcp_client.project
        self.secret_resource_name = f"projects/{project_id}/secrets/{self.secret_name}"

    def _discover_existing_secrets(self) -> Dict[str, Dict[str, Any]]:
        """Discover existing secrets in Secret Manager"""
        existing_secrets = {}
        
        try:
            from google.cloud import secretmanager
            from google.api_core.exceptions import GoogleAPIError
            
            parent = f"projects/{self.gcp_client.project}"
            
            # List all secrets in the project
            page_result = self.secret_manager_client.list_secrets(parent=parent)
            
            for secret in page_result:
                secret_name = secret.name.split('/')[-1]
                
                try:
                    # Get secret details
                    replication_type = "unknown"
                    locations = []
                    
                    if hasattr(secret, 'replication'):
                        if hasattr(secret.replication, 'automatic') and secret.replication.automatic:
                            replication_type = "automatic"
                            locations = ["global"]
                        elif hasattr(secret.replication, 'user_managed') and secret.replication.user_managed:
                            replication_type = "user_managed"
                            replicas = secret.replication.user_managed.replicas
                            locations = [replica.location for replica in replicas]
                    
                    # Get rotation information
                    rotation_enabled = False
                    rotation_period = None
                    next_rotation_time = None
                    
                    if hasattr(secret, 'rotation') and secret.rotation:
                        rotation_enabled = True
                        if hasattr(secret.rotation, 'rotation_period'):
                            rotation_period = secret.rotation.rotation_period.total_seconds()
                        if hasattr(secret.rotation, 'next_rotation_time'):
                            next_rotation_time = secret.rotation.next_rotation_time.isoformat()
                    
                    # Get labels
                    labels = dict(secret.labels) if secret.labels else {}
                    
                    # Get version information
                    versions = []
                    try:
                        versions_request = self.secret_manager_client.list_secret_versions(parent=secret.name)
                        for version in versions_request:
                            version_info = {
                                'name': version.name.split('/')[-1],
                                'state': version.state.name if hasattr(version, 'state') else 'UNKNOWN',
                                'create_time': version.create_time.isoformat() if hasattr(version, 'create_time') else None,
                                'destroy_time': version.destroy_time.isoformat() if hasattr(version, 'destroy_time') else None
                            }
                            versions.append(version_info)
                    except Exception as e:
                        print(f"⚠️  Failed to get versions for secret {secret_name}: {str(e)}")
                    
                    # Determine secret type from labels or name
                    secret_type = "generic"
                    if 'type' in labels:
                        secret_type = labels['type']
                    elif any(keyword in secret_name.lower() for keyword in ['database', 'db', 'sql']):
                        secret_type = "database"
                    elif any(keyword in secret_name.lower() for keyword in ['api', 'key']):
                        secret_type = "api_key"
                    elif any(keyword in secret_name.lower() for keyword in ['jwt', 'token']):
                        secret_type = "jwt"
                    elif any(keyword in secret_name.lower() for keyword in ['oauth', 'auth']):
                        secret_type = "oauth"
                    
                    existing_secrets[secret_name] = {
                        'secret_name': secret_name,
                        'full_name': secret.name,
                        'secret_type': secret_type,
                        'replication_type': replication_type,
                        'locations': locations,
                        'location_count': len(locations),
                        'rotation_enabled': rotation_enabled,
                        'rotation_period': rotation_period,
                        'next_rotation_time': next_rotation_time,
                        'labels': labels,
                        'label_count': len(labels),
                        'versions': versions,
                        'version_count': len(versions),
                        'active_versions': len([v for v in versions if v['state'] == 'ENABLED']),
                        'create_time': secret.create_time.isoformat() if hasattr(secret, 'create_time') else None,
                        'etag': secret.etag if hasattr(secret, 'etag') else None
                    }
                    
                except Exception as e:
                    print(f"⚠️  Failed to get details for secret {secret_name}: {str(e)}")
                    existing_secrets[secret_name] = {
                        'secret_name': secret_name,
                        'error': str(e)
                    }
                    
        except Exception as e:
            print(f"⚠️  Failed to discover existing secrets: {str(e)}")
        
        return existing_secrets

    def get_secret_manager_client(self):
        try:
            from google.cloud import secretmanager
            return secretmanager.SecretManagerServiceClient(credentials=self.gcp_client.credentials)
        except Exception as e:
            print(f"⚠️  Failed to create Secret Manager client: {e}")
            return None

    def preview(self) -> Dict[str, Any]:
        """Preview what will be created, kept, and removed"""
        self._ensure_authenticated()

        # Discover existing secrets
        existing_secrets = self._discover_existing_secrets()
        
        # Categorize secrets
        secrets_to_create = []
        secrets_to_keep = []
        secrets_to_remove = []
        
        # Check if our desired secret exists
        desired_secret_name = self.secret_name
        secret_exists = desired_secret_name in existing_secrets
        
        if not secret_exists:
            secrets_to_create.append({
                'secret_name': desired_secret_name,
                'secret_type': self._get_secret_type(),
                'replication_policy': self.replication_policy,
                'replica_locations': len(self.replica_locations) if self.replica_locations else "Global",
                'rotation_enabled': self.rotation_period is not None,
                'rotation_period': self.rotation_period,
                'labels': self.secret_labels,
                'label_count': len(self.secret_labels)
            })
        else:
            secrets_to_keep.append(existing_secrets[desired_secret_name])

        print(f"\n🔐 Google Cloud Secret Manager Preview")
        
        # Show secrets to create
        if secrets_to_create:
            print(f"╭─ 🔐 Secrets to CREATE: {len(secrets_to_create)}")
            for secret in secrets_to_create:
                print(f"├─ 🆕 {secret['secret_name']}")
                print(f"│  ├─ 🏷️  Type: {secret['secret_type'].replace('_', ' ').title()}")
                print(f"│  ├─ 🌍 Replication: {secret['replication_policy'].replace('_', ' ').title()}")
                
                if secret['replication_policy'] == 'user_managed' and self.replica_locations:
                    print(f"│  ├─ 📍 Locations: {len(self.replica_locations)}")
                    for i, location in enumerate(self.replica_locations[:3]):  # Show first 3 locations
                        connector = "│  │  ├─" if i < min(len(self.replica_locations), 3) - 1 else "│  │  └─"
                        print(f"{connector} {location}")
                    if len(self.replica_locations) > 3:
                        print(f"│  │     └─ ... and {len(self.replica_locations) - 3} more locations")
                elif secret['replication_policy'] == 'automatic':
                    print(f"│  ├─ 📍 Locations: Global (automatic)")
                
                print(f"│  ├─ 🔄 Rotation: {'✅ Enabled' if secret['rotation_enabled'] else '❌ Disabled'}")
                if secret['rotation_enabled'] and secret['rotation_period']:
                    days = secret['rotation_period'] // 86400
                    print(f"│  │  └─ 📅 Period: {days} days")
                
                if secret['label_count'] > 0:
                    print(f"│  ├─ 🏷️  Labels: {secret['label_count']}")
                
                # Show security features
                print(f"│  ├─ 🔒 Security:")
                print(f"│  │  ├─ 🔐 Encryption: AES-256 (Google-managed)")
                print(f"│  │  ├─ 🔑 Access: IAM-controlled")
                print(f"│  │  ├─ 📝 Versioning: Automatic")
                print(f"│  │  └─ 📋 Audit: Cloud Logging")
                
                print(f"│  └─ ⚡ Access: gcloud secrets versions access latest --secret={secret['secret_name']}")
            print(f"╰─")

        # Show existing secrets being kept
        if secrets_to_keep:
            print(f"\n╭─ 🔐 Existing Secrets to KEEP: {len(secrets_to_keep)}")
            for secret in secrets_to_keep:
                print(f"├─ ✅ {secret['secret_name']}")
                print(f"│  ├─ 🏷️  Type: {secret['secret_type'].replace('_', ' ').title()}")
                print(f"│  ├─ 🌍 Replication: {secret['replication_type'].replace('_', ' ').title()}")
                
                if secret['location_count'] > 0 and secret['locations']:
                    if secret['replication_type'] == 'automatic':
                        print(f"│  ├─ 📍 Locations: Global")
                    else:
                        print(f"│  ├─ 📍 Locations: {secret['location_count']}")
                        for i, location in enumerate(secret['locations'][:3]):  # Show first 3 locations
                            connector = "│  │  ├─" if i < min(len(secret['locations']), 3) - 1 else "│  │  └─"
                            print(f"{connector} {location}")
                        if len(secret['locations']) > 3:
                            print(f"│  │     └─ ... and {len(secret['locations']) - 3} more locations")
                
                print(f"│  ├─ 🔄 Rotation: {'✅ Enabled' if secret['rotation_enabled'] else '❌ Disabled'}")
                if secret['rotation_enabled'] and secret['rotation_period']:
                    days = secret['rotation_period'] // 86400
                    print(f"│  │  ├─ 📅 Period: {days} days")
                    if secret['next_rotation_time']:
                        print(f"│  │  └─ ⏰ Next: {secret['next_rotation_time'][:10]}")
                
                print(f"│  ├─ 📦 Versions: {secret['version_count']} total, {secret['active_versions']} active")
                
                if secret['label_count'] > 0:
                    print(f"│  ├─ 🏷️  Labels: {secret['label_count']}")
                
                print(f"│  └─ 📅 Created: {secret.get('create_time', 'Unknown')[:10] if secret.get('create_time') else 'Unknown'}")
            print(f"╰─")

        # Show cost estimation
        print(f"\n💰 Secret Manager Costs:")
        if secrets_to_create:
            secret = secrets_to_create[0]
            # Base cost: $0.06 per 10,000 API calls + $0.03 per active secret version per month
            base_version_cost = 0.03  # per active version per month
            api_cost_per_10k = 0.06
            
            print(f"   ├─ 🔐 Secret storage: ${base_version_cost:.3f}/version/month")
            print(f"   ├─ 📡 API calls: ${api_cost_per_10k:.3f}/10,000 operations")
            
            if secret['replication_policy'] == 'user_managed' and self.replica_locations:
                replica_cost = len(self.replica_locations) * base_version_cost
                print(f"   ├─ 🌍 Replication ({len(self.replica_locations)} regions): ${replica_cost:.3f}/version/month")
            
            print(f"   ├─ 🔄 Rotation: Free (automated)")
            print(f"   └─ 📊 Total (1 version): ~${base_version_cost:.3f}/month")
        else:
            print(f"   ├─ 🔐 Secret storage: $0.03/version/month")
            print(f"   ├─ 📡 API calls: $0.06/10,000 operations")
            print(f"   ├─ 🌍 Multi-region: Additional $0.03/region/version")
            print(f"   └─ 🔄 Automatic rotation: Free")

        return {
            'resource_type': 'gcp_secret_manager',
            'name': desired_secret_name,
            'secrets_to_create': secrets_to_create,
            'secrets_to_keep': secrets_to_keep,
            'secrets_to_remove': secrets_to_remove,
            'existing_secrets': existing_secrets,
            'secret_name': desired_secret_name,
            'secret_type': self._get_secret_type(),
            'replication_policy': self.replication_policy,
            'estimated_cost': "$0.03/month"
        }

    def create(self) -> Dict[str, Any]:
        """Create secret with smart state management"""
        self._ensure_authenticated()
        
        if not self.secret_value and not self.secret_binary:
            raise ValueError("Secret value or binary data is required")
        
        # Discover existing secrets first
        existing_secrets = self._discover_existing_secrets()
        
        # Determine what changes need to be made
        desired_secret_name = self.secret_name
        
        # Check for secrets to remove (not in current configuration)
        secrets_to_remove = []
        for secret_name, secret_info in existing_secrets.items():
            # In a real implementation, this would have more sophisticated logic
            # to determine which secrets should be removed based on configuration
            # For now, we'll focus on creating the desired secret
            pass
        
        # Remove secrets no longer in configuration
        if secrets_to_remove:
            print(f"\n🗑️  Removing secrets no longer in configuration:")
            for secret_info in secrets_to_remove:
                print(f"╭─ 🔄 Removing secret: {secret_info['secret_name']}")
                print(f"├─ 🏷️  Type: {secret_info['secret_type'].replace('_', ' ').title()}")
                print(f"├─ 🌍 Replication: {secret_info['replication_type'].replace('_', ' ').title()}")
                print(f"├─ 📦 Versions: {secret_info['version_count']} total")
                if secret_info['rotation_enabled']:
                    print(f"├─ 🔄 Rotation: Enabled")
                print(f"└─ ⚠️  Secret and all versions will be permanently deleted")
                
                # In real implementation:
                # self.secret_manager_client.delete_secret(name=secret_info['full_name'])

        # Check if our desired secret already exists
        secret_exists = desired_secret_name in existing_secrets
        if secret_exists:
            existing_secret = existing_secrets[desired_secret_name]
            print(f"\n🔄 Secret '{desired_secret_name}' already exists")
            print(f"   🏷️  Type: {existing_secret['secret_type'].replace('_', ' ').title()}")
            print(f"   🌍 Replication: {existing_secret['replication_type'].replace('_', ' ').title()}")
            print(f"   📦 Versions: {existing_secret['version_count']} total, {existing_secret['active_versions']} active")
            
            if existing_secret['rotation_enabled']:
                days = existing_secret['rotation_period'] // 86400 if existing_secret['rotation_period'] else 0
                print(f"   🔄 Rotation: ✅ Enabled ({days} days)")
                if existing_secret['next_rotation_time']:
                    print(f"      └─ ⏰ Next: {existing_secret['next_rotation_time'][:10]}")
            else:
                print(f"   🔄 Rotation: ❌ Disabled")
            
            # Add new version to existing secret
            print(f"   📝 Adding new version to existing secret...")
            self.secret_id = existing_secret['secret_name']
            result = self._add_version_to_existing()
            
            if len(secrets_to_remove) > 0:
                result['changes'] = True
                print(f"   🔄 Infrastructure changes applied")
            
            return result

        print(f"\n🔐 Creating secret: {desired_secret_name}")
        print(f"   🏷️  Type: {self._get_secret_type().replace('_', ' ').title()}")
        print(f"   🌍 Replication: {self.replication_policy.replace('_', ' ').title()}")
        
        if self.replication_policy == 'user_managed' and self.replica_locations:
            print(f"   📍 Locations: {len(self.replica_locations)}")
            for location in self.replica_locations[:3]:
                print(f"      └─ {location}")
            if len(self.replica_locations) > 3:
                print(f"      └─ ... and {len(self.replica_locations) - 3} more locations")
        
        print(f"   🔄 Rotation: {'✅ Enabled' if self.rotation_period else '❌ Disabled'}")
        if self.rotation_period:
            days = self.rotation_period // 86400
            print(f"      └─ 📅 Period: {days} days")

        try:
            result = self._create_new_secret()
            
            print(f"\n✅ Secret created successfully!")
            print(f"   🔐 Name: {result.get('secret_name', desired_secret_name)}")
            print(f"   🏷️  Type: {self._get_secret_type().replace('_', ' ').title()}")
            print(f"   📦 Initial version: Created")
            print(f"   🔒 Security: AES-256 encrypted, IAM-controlled")
            print(f"   📋 Audit logging: Enabled")
            print(f"   ⚡ Access: gcloud secrets versions access latest --secret={desired_secret_name}")
            
            if len(secrets_to_remove) > 0:
                result['changes'] = True
                print(f"   🔄 Infrastructure changes applied")

            return result
        except Exception as e:
            print(f"❌ Failed to create secret: {e}")
            raise

    def _find_existing_secret(self) -> Optional[Any]:
        try:
            secret = self.secret_manager_client.get_secret(name=self.secret_resource_name)
            return secret
        except Exception:
            return None

    def _create_new_secret(self) -> Dict[str, Any]:
        try:
            from google.cloud import secretmanager

            # Create replication policy
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

            # Create secret
            secret = secretmanager.Secret(
                name=self.secret_resource_name,
                replication=replication,
                labels=self.secret_labels
            )

            # Add rotation if configured
            if self.rotation_period:
                secret.rotation = secretmanager.Rotation(
                    rotation_period={"seconds": self.rotation_period}
                )
                if self.next_rotation_time:
                    secret.rotation.next_rotation_time = self.next_rotation_time

            # Create the secret
            created_secret = self.secret_manager_client.create_secret(
                parent=f"projects/{self.gcp_client.project}",
                secret_id=self.secret_name,
                secret=secret
            )

            self.secret_id = created_secret.name.split('/')[-1]
            print(f"✅ Secret created!")
            print(f"📍 Secret: {created_secret.name}")

            # Add the initial version
            return self._add_secret_version()

        except Exception as e:
            print(f"❌ Failed to create secret: {str(e)}")
            raise

    def _add_version_to_existing(self) -> Dict[str, Any]:
        """Add a new version to existing secret"""
        print(f"📝 Adding new version to existing secret")
        return self._add_secret_version()

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
            print(f"✅ Secret version added!")
            print(f"📍 Version: {version.name}")

            return self._get_secret_info()

        except Exception as e:
            print(f"❌ Failed to add secret version: {str(e)}")
            raise

    def update_secret(self, new_value: Union[str, dict, bytes]) -> Dict[str, Any]:
        """Add a new version with updated value"""
        old_value = self.secret_value
        old_binary = self.secret_binary
        
        # Update the value
        if isinstance(new_value, bytes):
            self.secret_binary = new_value
            self.secret_value = None
        else:
            self.secret_value = new_value
            self.secret_binary = None
        
        try:
            result = self._add_secret_version()
            print(f"✅ Secret updated with new version!")
            return result
        except Exception as e:
            # Restore old values on failure
            self.secret_value = old_value
            self.secret_binary = old_binary
            raise

    def get_secret_value(self, version: str = "latest") -> Dict[str, Any]:
        """Retrieve secret value"""
        try:
            version_name = f"{self.secret_resource_name}/versions/{version}"
            
            response = self.secret_manager_client.access_secret_version(name=version_name)
            
            payload = response.payload.data
            
            result = {
                'success': True,
                'secret_name': self.secret_name,
                'version_name': response.name,
                'create_time': response.create_time
            }

            # Try to decode as JSON, then as string
            try:
                decoded_data = payload.decode('utf-8')
                try:
                    result['secret_value'] = json.loads(decoded_data)
                except json.JSONDecodeError:
                    result['secret_value'] = decoded_data
            except UnicodeDecodeError:
                # Binary data
                result['secret_binary'] = payload

            return result

        except Exception as e:
            return {'success': False, 'error': str(e)}

    def list_versions(self) -> Dict[str, Any]:
        """List all versions of the secret"""
        try:
            versions = []
            
            for version in self.secret_manager_client.list_secret_versions(parent=self.secret_resource_name):
                versions.append({
                    'name': version.name,
                    'create_time': version.create_time,
                    'state': version.state.name
                })
            
            return {
                'success': True,
                'secret_name': self.secret_name,
                'versions': versions
            }

        except Exception as e:
            return {'success': False, 'error': str(e)}

    def destroy(self) -> Dict[str, Any]:
        self._ensure_authenticated()
        print(f"🗑️  Destroying Secret: {self.secret_name}")

        try:
            if not self.secret_resource_name:
                return {'success': False, 'error': 'Secret resource name not set'}

            # Delete secret
            self.secret_manager_client.delete_secret(name=self.secret_resource_name)

            print(f"✅ Secret destroyed!")

            return {'success': True, 'secret_name': self.secret_name, 'status': 'deleted'}

        except Exception as e:
            print(f"❌ Failed to destroy secret: {str(e)}")
            return {'success': False, 'error': str(e)}

    def _get_secret_info(self) -> Dict[str, Any]:
        try:
            return {
                'success': True,
                'secret_name': self.secret_name,
                'secret_resource_name': self.secret_resource_name,
                'secret_version_name': self.secret_version_name,
                'replication_policy': self.replication_policy,
                'replica_locations': self.replica_locations
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def _get_secret_type(self) -> str:
        if self.secret_binary:
            return "Binary data"
        elif isinstance(self.secret_value, dict):
            return "JSON object"
        else:
            return "String value"

    def _estimate_monthly_cost(self) -> str:
        # $0.06 per 10,000 access operations + $0.03 per active secret version per month
        base_cost = 0.03  # One active version
        if self.replication_policy == "user_managed":
            base_cost *= len(self.replica_locations) if self.replica_locations else 1
        return f"~${base_cost:.3f}/month + access costs"

    # Rails-like chainable methods
    def value(self, secret_value: Union[str, dict]) -> 'SecretManager':
        """Set secret value"""
        self.secret_value = secret_value
        self.secret_binary = None
        return self

    def binary(self, binary_data: bytes) -> 'SecretManager':
        """Set binary secret data"""
        self.secret_binary = binary_data
        self.secret_value = None
        return self

    def database_credentials(self, host: str, username: str, password: str, 
                           database: str = None, port: int = None, engine: str = "postgres") -> 'SecretManager':
        """Set database credentials"""
        credentials = {
            'host': host,
            'username': username,
            'password': password,
            'engine': engine
        }
        if database:
            credentials['database'] = database
        if port:
            credentials['port'] = port
        
        self.secret_value = credentials
        return self

    def api_key(self, key: str, additional_data: dict = None) -> 'SecretManager':
        """Set API key with optional additional data"""
        secret_data = {'api_key': key}
        if additional_data:
            secret_data.update(additional_data)
        self.secret_value = secret_data
        return self

    def automatic_replication(self) -> 'SecretManager':
        """Use automatic replication (global)"""
        self.replication_policy = "automatic"
        self.replica_locations = []
        return self

    def user_managed_replication(self, locations: List[str]) -> 'SecretManager':
        """Use user-managed replication in specific locations"""
        self.replication_policy = "user_managed"
        self.replica_locations = locations
        return self

    def rotation(self, period_seconds: int, next_rotation_time: str = None) -> 'SecretManager':
        """Enable automatic rotation"""
        self.rotation_period = period_seconds
        if next_rotation_time:
            self.next_rotation_time = next_rotation_time
        return self

    def labels(self, labels: Dict[str, str]) -> 'SecretManager':
        """Set labels"""
        self.secret_labels.update(labels)
        return self

    def label(self, key: str, value: str) -> 'SecretManager':
        """Add single label"""
        self.secret_labels[key] = value
        return self

    # Rails convenience methods
    def mysql_database(self, host: str, username: str, password: str, database: str = None) -> 'SecretManager':
        """Rails convenience: MySQL database credentials"""
        return (self.database_credentials(host, username, password, database, 3306, "mysql")
                .label("type", "database")
                .label("engine", "mysql"))

    def postgresql_database(self, host: str, username: str, password: str, database: str = None) -> 'SecretManager':
        """Rails convenience: PostgreSQL database credentials"""
        return (self.database_credentials(host, username, password, database, 5432, "postgres")
                .label("type", "database") 
                .label("engine", "postgresql"))

    def redis_credentials(self, host: str, password: str, port: int = 6379) -> 'SecretManager':
        """Rails convenience: Redis credentials"""
        return (self.value({
                    'host': host,
                    'password': password,
                    'port': port
                })
                .label("type", "cache")
                .label("engine", "redis"))

    def jwt_secret(self, secret: str, algorithm: str = "HS256") -> 'SecretManager':
        """Rails convenience: JWT signing secret"""
        return (self.value({
                    'secret': secret,
                    'algorithm': algorithm
                })
                .label("type", "jwt"))

    def oauth_credentials(self, client_id: str, client_secret: str, additional_config: dict = None) -> 'SecretManager':
        """Rails convenience: OAuth application credentials"""
        config = {
            'client_id': client_id,
            'client_secret': client_secret
        }
        if additional_config:
            config.update(additional_config)
        return (self.value(config)
                .label("type", "oauth"))

    def stripe_keys(self, public_key: str, secret_key: str, webhook_secret: str = None) -> 'SecretManager':
        """Rails convenience: Stripe API credentials"""
        config = {
            'public_key': public_key,
            'secret_key': secret_key
        }
        if webhook_secret:
            config['webhook_secret'] = webhook_secret
        return (self.value(config)
                .label("type", "payment")
                .label("provider", "stripe"))

    def sendgrid_api_key(self, api_key: str, from_email: str = None) -> 'SecretManager':
        """Rails convenience: SendGrid API credentials"""
        config = {'api_key': api_key}
        if from_email:
            config['from_email'] = from_email
        return (self.value(config)
                .label("type", "email")
                .label("provider", "sendgrid"))

    def gcp_service_account(self, key_json: dict) -> 'SecretManager':
        """Rails convenience: GCP service account key"""
        return (self.value(key_json)
                .label("type", "service-account")
                .label("provider", "gcp"))

    def production_secret(self) -> 'SecretManager':
        """Rails convenience: Production environment configuration"""
        return (self.label("environment", "production")
                .rotation(90 * 24 * 3600))  # 90 days

    def development_secret(self) -> 'SecretManager':
        """Rails convenience: Development environment configuration"""
        return self.label("environment", "development")

    def multi_region_secret(self, regions: List[str]) -> 'SecretManager':
        """Rails convenience: Multi-region replication"""
        return self.user_managed_replication(regions)

    def single_region_secret(self, region: str) -> 'SecretManager':
        """Rails convenience: Single region replication"""
        return self.user_managed_replication([region])

    def _fetch_current_cloud_state(self) -> Dict[str, Any]:
        """Fetch current state of the secret from Google Cloud"""
        self._ensure_authenticated()
        
        try:
            # Try to get the secret
            existing_secret = self._find_existing_secret()
            
            if existing_secret:
                # Get secret metadata
                state = {
                    "exists": True,
                    "secret_name": self.secret_name,
                    "secret_resource_name": existing_secret.name,
                    "replication_policy": "automatic" if existing_secret.replication.automatic else "user_managed",
                    "labels": dict(existing_secret.labels) if existing_secret.labels else {},
                    "create_time": existing_secret.create_time,
                    "etag": existing_secret.etag
                }
                
                # Add replica locations if user-managed
                if not existing_secret.replication.automatic:
                    state["replica_locations"] = [
                        replica.location for replica in existing_secret.replication.user_managed.replicas
                    ]
                
                # Add rotation info if configured
                if hasattr(existing_secret, 'rotation') and existing_secret.rotation:
                    state["rotation_period"] = existing_secret.rotation.rotation_period.seconds if existing_secret.rotation.rotation_period else None
                    state["next_rotation_time"] = existing_secret.rotation.next_rotation_time
                
                return state
            else:
                return {
                    "exists": False,
                    "secret_name": self.secret_name
                }
                
        except Exception as e:
            print(f"⚠️  Warning: Failed to fetch secret state: {str(e)}")
            return {
                "exists": False,
                "secret_name": self.secret_name,
                "error": str(e)
            } 