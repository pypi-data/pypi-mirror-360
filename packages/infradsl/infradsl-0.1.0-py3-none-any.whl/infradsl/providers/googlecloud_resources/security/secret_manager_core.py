"""
GCP Secret Manager Core Implementation

Core attributes and authentication for Google Cloud Secret Manager.
Provides the foundation for the modular secrets management system.
"""

from typing import Dict, Any, List, Optional, Union
from ..base_resource import BaseGcpResource


class SecretManagerCore(BaseGcpResource):
    """
    Core class for Google Cloud Secret Manager functionality.
    
    This class provides:
    - Basic secret attributes and configuration
    - Authentication setup
    - Common utilities for secret operations
    - Validation and state tracking foundations
    """
    
    def __init__(self, name: str):
        """Initialize Secret Manager core with secret name"""
        super().__init__(name)
        
        # Core secret attributes
        self.secret_name = name
        self.secret_description = f"Secret for {name}"
        self.secret_resource_name = None
        self.secret_version_name = None
        self.secret_id = None
        
        # Secret data
        self.secret_value = None
        self.secret_binary = None
        self.secret_type = "generic"  # generic, database, api_key, jwt, oauth, certificate
        
        # Replication configuration
        self.replication_policy = "automatic"  # automatic or user_managed
        self.replica_locations = []
        
        # Rotation configuration
        self.rotation_enabled = False
        self.rotation_period = None  # seconds
        self.next_rotation_time = None
        self.rotation_topic = None  # Pub/Sub topic for rotation notifications
        
        # Access and security
        self.kms_key_name = None  # Customer-managed encryption key
        self.allowed_access_identities = []
        self.secret_labels = {}
        self.secret_annotations = {}
        
        # Version management
        self.version_aliases = {}  # aliases like "prod", "staging"
        self.max_versions = None  # automatic cleanup after N versions
        self.version_destroy_ttl = None  # TTL for destroyed versions
        
        # State tracking
        self.secret_exists = False
        self.secret_created = False
        self.current_version = None
        self.total_versions = 0
        
        # Client reference
        self.secret_manager_client = None
        
        # Estimated costs
        self.estimated_monthly_cost = "$0.03/month"
        
    def _initialize_managers(self):
        """Initialize Secret Manager-specific managers"""
        self.secret_manager_client = None
        
    def _post_authentication_setup(self):
        """Setup managers after authentication"""
        try:
            from google.cloud import secretmanager
            
            # Initialize client
            self.secret_manager_client = secretmanager.SecretManagerServiceClient(
                credentials=self.gcp_client.credentials
            )
            
            # Set project context
            self.project_id = self.project_id or self.gcp_client.project_id
            
            # Generate resource names
            if self.project_id:
                self.secret_resource_name = f"projects/{self.project_id}/secrets/{self.secret_name}"
                
        except Exception as e:
            print(f"⚠️  Failed to initialize Secret Manager client: {str(e)}")
            
    def _is_valid_secret_name(self, name: str) -> bool:
        """Check if secret name is valid"""
        import re
        # Secret names must contain only letters, numbers, dashes, underscores
        pattern = r'^[a-zA-Z][a-zA-Z0-9_-]*$'
        return bool(re.match(pattern, name)) and 1 <= len(name) <= 255
        
    def _is_valid_location(self, location: str) -> bool:
        """Check if replication location is valid"""
        valid_locations = [
            "us-central1", "us-east1", "us-east4", "us-west1", "us-west2", "us-west3", "us-west4",
            "europe-north1", "europe-west1", "europe-west2", "europe-west3", "europe-west4", "europe-west6",
            "asia-east1", "asia-east2", "asia-northeast1", "asia-northeast2", "asia-northeast3",
            "asia-south1", "asia-southeast1", "asia-southeast2", "australia-southeast1"
        ]
        return location in valid_locations
        
    def _is_valid_rotation_period(self, seconds: int) -> bool:
        """Check if rotation period is valid"""
        # Must be at least 1 day and at most 1 year
        return 86400 <= seconds <= 31536000
        
    def _validate_secret_config(self, config: Dict[str, Any]) -> bool:
        """Validate secret configuration"""
        required_fields = ["secret_name"]
        
        for field in required_fields:
            if field not in config or not config[field]:
                return False
                
        # Validate secret name format
        if not self._is_valid_secret_name(config["secret_name"]):
            return False
            
        # Validate replication locations if user-managed
        if config.get("replication_policy") == "user_managed":
            locations = config.get("replica_locations", [])
            if not locations:
                return False
            for location in locations:
                if not self._is_valid_location(location):
                    return False
                    
        # Validate rotation period if specified
        if config.get("rotation_period"):
            if not self._is_valid_rotation_period(config["rotation_period"]):
                return False
                
        return True
        
    def _get_secret_type_from_value(self) -> str:
        """Determine secret type from value"""
        if self.secret_binary:
            return "binary"
        elif isinstance(self.secret_value, dict):
            # Check for common patterns
            if "password" in self.secret_value and "username" in self.secret_value:
                return "database"
            elif "api_key" in self.secret_value or "access_token" in self.secret_value:
                return "api_key"
            elif "client_id" in self.secret_value and "client_secret" in self.secret_value:
                return "oauth"
            elif "secret" in self.secret_value and "algorithm" in self.secret_value:
                return "jwt"
            elif "private_key" in self.secret_value or "certificate" in self.secret_value:
                return "certificate"
            else:
                return "json"
        else:
            # String value - try to infer from name or content
            if any(keyword in self.secret_name.lower() for keyword in ['db', 'database', 'sql']):
                return "database"
            elif any(keyword in self.secret_name.lower() for keyword in ['api', 'key']):
                return "api_key"
            elif any(keyword in self.secret_name.lower() for keyword in ['jwt', 'token']):
                return "jwt"
            elif any(keyword in self.secret_name.lower() for keyword in ['oauth', 'auth']):
                return "oauth"
            elif any(keyword in self.secret_name.lower() for keyword in ['cert', 'ssl', 'tls']):
                return "certificate"
            else:
                return "string"
                
    def _estimate_secret_manager_cost(self) -> float:
        """Estimate monthly cost for Secret Manager usage"""
        # Secret Manager pricing (simplified)
        
        # Base cost per active secret version per month
        base_cost_per_version = 0.03
        
        # Estimate active versions (usually 1-3)
        active_versions = 1
        if self.max_versions:
            active_versions = min(self.max_versions, 3)
        
        # Replication multiplier
        replication_multiplier = 1
        if self.replication_policy == "user_managed" and self.replica_locations:
            replication_multiplier = len(self.replica_locations)
            
        # Version cost
        version_cost = base_cost_per_version * active_versions * replication_multiplier
        
        # API operations cost (estimated usage)
        monthly_operations = 1000  # Moderate usage
        operations_cost = (monthly_operations / 10000) * 0.06  # $0.06 per 10K operations
        
        total_cost = version_cost + operations_cost
        
        # Minimum charge
        if total_cost < 0.03:
            total_cost = 0.03
            
        return total_cost
        
    def _fetch_current_cloud_state(self) -> Dict[str, Any]:
        """Fetch current state of Secret Manager secret from Google Cloud"""
        self._ensure_authenticated()
        
        try:
            # Check if secret exists
            try:
                secret = self.secret_manager_client.get_secret(name=self.secret_resource_name)
                secret_exists = True
            except Exception:
                secret_exists = False
                
            if not secret_exists:
                return {
                    "exists": False,
                    "secret_name": self.secret_name,
                    "secret_resource_name": self.secret_resource_name
                }
                
            # Get secret details
            current_state = {
                "exists": True,
                "secret_name": self.secret_name,
                "secret_resource_name": secret.name,
                "labels": dict(secret.labels) if secret.labels else {},
                "create_time": secret.create_time.isoformat() if hasattr(secret, 'create_time') else None,
                "etag": secret.etag if hasattr(secret, 'etag') else None,
                "replication_policy": "automatic" if secret.replication.automatic else "user_managed",
                "replica_locations": [],
                "rotation_enabled": False,
                "rotation_period": None,
                "next_rotation_time": None,
                "versions": [],
                "version_count": 0,
                "active_versions": 0
            }
            
            # Add replication details
            if not secret.replication.automatic:
                current_state["replica_locations"] = [
                    replica.location for replica in secret.replication.user_managed.replicas
                ]
                
            # Add rotation details if configured
            if hasattr(secret, 'rotation') and secret.rotation:
                current_state["rotation_enabled"] = True
                if hasattr(secret.rotation, 'rotation_period') and secret.rotation.rotation_period:
                    current_state["rotation_period"] = secret.rotation.rotation_period.seconds
                if hasattr(secret.rotation, 'next_rotation_time') and secret.rotation.next_rotation_time:
                    current_state["next_rotation_time"] = secret.rotation.next_rotation_time.isoformat()
                    
            # Get version information
            try:
                versions = []
                active_count = 0
                
                for version in self.secret_manager_client.list_secret_versions(parent=secret.name):
                    version_info = {
                        "name": version.name.split('/')[-1],
                        "state": version.state.name if hasattr(version, 'state') else 'UNKNOWN',
                        "create_time": version.create_time.isoformat() if hasattr(version, 'create_time') else None,
                        "destroy_time": version.destroy_time.isoformat() if hasattr(version, 'destroy_time') else None
                    }
                    versions.append(version_info)
                    
                    if version_info["state"] == "ENABLED":
                        active_count += 1
                        
                current_state["versions"] = versions
                current_state["version_count"] = len(versions)
                current_state["active_versions"] = active_count
                
            except Exception as e:
                print(f"⚠️  Warning: Failed to get version information: {str(e)}")
                
            return current_state
            
        except Exception as e:
            print(f"⚠️  Warning: Failed to fetch Secret Manager state: {str(e)}")
            return {
                "exists": False,
                "secret_name": self.secret_name,
                "secret_resource_name": self.secret_resource_name,
                "error": str(e)
            }
            
    def _discover_existing_secrets(self) -> Dict[str, Dict[str, Any]]:
        """Discover all existing secrets in the project"""
        existing_secrets = {}
        
        try:
            parent = f"projects/{self.project_id}"
            
            for secret in self.secret_manager_client.list_secrets(parent=parent):
                secret_name = secret.name.split('/')[-1]
                
                try:
                    # Get basic secret information
                    secret_info = {
                        "secret_name": secret_name,
                        "full_name": secret.name,
                        "labels": dict(secret.labels) if secret.labels else {},
                        "create_time": secret.create_time.isoformat() if hasattr(secret, 'create_time') else None,
                        "replication_policy": "automatic" if secret.replication.automatic else "user_managed",
                        "replica_locations": [],
                        "rotation_enabled": False
                    }
                    
                    # Add replication details
                    if not secret.replication.automatic:
                        secret_info["replica_locations"] = [
                            replica.location for replica in secret.replication.user_managed.replicas
                        ]
                        
                    # Add rotation details
                    if hasattr(secret, 'rotation') and secret.rotation:
                        secret_info["rotation_enabled"] = True
                        if hasattr(secret.rotation, 'rotation_period') and secret.rotation.rotation_period:
                            secret_info["rotation_period"] = secret.rotation.rotation_period.seconds
                            
                    # Get version count
                    try:
                        versions = list(self.secret_manager_client.list_secret_versions(parent=secret.name))
                        secret_info["version_count"] = len(versions)
                        secret_info["active_versions"] = len([v for v in versions if v.state.name == "ENABLED"])
                    except Exception:
                        secret_info["version_count"] = 0
                        secret_info["active_versions"] = 0
                        
                    existing_secrets[secret_name] = secret_info
                    
                except Exception as e:
                    print(f"⚠️  Failed to get details for secret {secret_name}: {str(e)}")
                    existing_secrets[secret_name] = {
                        "secret_name": secret_name,
                        "error": str(e)
                    }
                    
        except Exception as e:
            print(f"⚠️  Failed to discover existing secrets: {str(e)}")
            
        return existing_secrets