"""
Firebase Storage Core Implementation

Core attributes and authentication for Firebase Storage.
Provides the foundation for the modular file storage system.
"""

from typing import Dict, Any, List, Optional, Union
from ..base_resource import BaseGcpResource


class FirebaseStorageCore(BaseGcpResource):
    """
    Core class for Firebase Storage functionality.
    
    This class provides:
    - Basic Firebase Storage attributes and configuration
    - Authentication setup
    - Common utilities for file storage operations
    - Validation and state tracking foundations
    """
    
    def __init__(self, name: str):
        """Initialize Firebase Storage core with storage name"""
        super().__init__(name)
        
        # Core storage attributes
        self.storage_name = name
        self.firebase_project_id = None
        self.storage_description = f"Firebase Storage for {name}"
        
        # Bucket configuration
        self.bucket_name = None
        self.location = "us-central1"
        self.storage_class = "STANDARD"  # STANDARD, NEARLINE, COLDLINE, ARCHIVE
        
        # Access configuration
        self.public_access = False
        self.public_read = False
        self.authenticated_read = True
        self.uniform_bucket_level_access = False
        
        # Security configuration
        self.security_rules_file = None
        self.security_rules_content = None
        self.default_security_rules = True
        
        # CORS configuration
        self.cors_enabled = False
        self.cors_origins = ["*"]
        self.cors_methods = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
        self.cors_headers = ["Content-Type", "Authorization"]
        self.cors_max_age = 3600
        
        # Lifecycle configuration
        self.lifecycle_rules = []
        self.retention_policy = None
        self.versioning_enabled = False
        
        # Performance configuration
        self.cdn_enabled = True
        self.cache_control = {}
        self.compression_enabled = True
        
        # Upload configuration
        self.max_upload_size = None  # bytes
        self.allowed_file_types = []
        self.image_transformations = {}
        self.thumbnail_generation = False
        
        # Monitoring configuration
        self.logging_enabled = False
        self.monitoring_enabled = False
        self.notifications = []
        
        # Labels and metadata
        self.storage_labels = {}
        self.storage_annotations = {}
        
        # State tracking
        self.bucket_exists = False
        self.bucket_created = False
        self.bucket_state = None
        self.deployment_status = None
        
        # Client references
        self.storage_client = None
        self.firebase_storage_client = None
        
        # Cost tracking
        self.estimated_monthly_cost = "$5.00/month"
        
    def _initialize_managers(self):
        """Initialize Firebase Storage-specific managers"""
        self.storage_client = None
        self.firebase_storage_client = None
        
    def _post_authentication_setup(self):
        """Setup managers after authentication"""
        try:
            # Firebase Storage uses Firebase project ID rather than GCP project ID
            # Set project context if available
            if not self.firebase_project_id and hasattr(self.gcp_client, 'project_id'):
                self.firebase_project_id = self.gcp_client.project_id
                
        except Exception as e:
            print(f"⚠️  Firebase Storage setup note: {str(e)}")
            
    def _is_valid_project_id(self, project_id: str) -> bool:
        """Check if Firebase project ID is valid"""
        import re
        # Firebase project IDs must contain only lowercase letters, numbers, dashes
        pattern = r'^[a-z][a-z0-9-]*[a-z0-9]$'
        return bool(re.match(pattern, project_id)) and 4 <= len(project_id) <= 30
        
    def _is_valid_bucket_name(self, bucket_name: str) -> bool:
        """Check if bucket name is valid"""
        import re
        # Bucket names must follow Cloud Storage naming rules
        if not bucket_name or len(bucket_name) > 222:
            return False
        # Must not start or end with dot or dash
        if bucket_name.startswith('.') or bucket_name.endswith('.') or bucket_name.startswith('-') or bucket_name.endswith('-'):
            return False
        # Basic pattern check
        pattern = r'^[a-z0-9][a-z0-9._-]*[a-z0-9]$'
        return bool(re.match(pattern, bucket_name))
    
    def _is_valid_location(self, location: str) -> bool:
        """Check if location is valid for Cloud Storage"""
        valid_locations = [
            "us", "eu", "asia",  # Multi-regions
            "us-central1", "us-east1", "us-east4", "us-west1", "us-west2", "us-west3", "us-west4",
            "europe-central2", "europe-west1", "europe-west2", "europe-west3", "europe-west4", "europe-west6",
            "asia-east1", "asia-east2", "asia-northeast1", "asia-northeast2", "asia-northeast3",
            "asia-south1", "asia-southeast1", "asia-southeast2", "australia-southeast1",
            "southamerica-east1"
        ]
        return location in valid_locations
        
    def _is_valid_storage_class(self, storage_class: str) -> bool:
        """Check if storage class is valid"""
        valid_classes = ["STANDARD", "NEARLINE", "COLDLINE", "ARCHIVE"]
        return storage_class in valid_classes
        
    def _validate_storage_config(self, config: Dict[str, Any]) -> bool:
        """Validate storage configuration"""
        required_fields = ["firebase_project_id", "location"]
        
        for field in required_fields:
            if field not in config or not config[field]:
                return False
                
        # Validate project ID format
        if not self._is_valid_project_id(config["firebase_project_id"]):
            return False
            
        # Validate bucket name if provided
        if "bucket_name" in config and config["bucket_name"]:
            if not self._is_valid_bucket_name(config["bucket_name"]):
                return False
            
        # Validate location
        if not self._is_valid_location(config["location"]):
            return False
            
        # Validate storage class if provided
        if "storage_class" in config and not self._is_valid_storage_class(config["storage_class"]):
            return False
                
        return True
        
    def _get_storage_type_from_config(self) -> str:
        """Determine storage type from configuration"""
        labels = self.storage_labels
        
        # Check for purpose-based types
        purpose = labels.get("purpose", "").lower()
        if purpose:
            if "media" in purpose or "images" in purpose:
                return "media_storage"
            elif "documents" in purpose or "files" in purpose:
                return "document_storage"
            elif "backup" in purpose:
                return "backup_storage"
            elif "archive" in purpose:
                return "archive_storage"
            elif "user" in purpose:
                return "user_uploads"
            elif "static" in purpose:
                return "static_assets"
            elif "cache" in purpose:
                return "cache_storage"
        
        # Check environment
        environment = labels.get("environment", "").lower()
        if environment:
            if environment == "development":
                return "development"
            elif environment == "staging":
                return "staging"
            elif environment == "production":
                return "production"
        
        # Check by storage class and configuration
        if self.storage_class == "ARCHIVE":
            return "archive_storage"
        elif self.storage_class == "COLDLINE":
            return "cold_storage"
        elif self.storage_class == "NEARLINE":
            return "nearline_storage"
        elif self.public_access:
            return "public_storage"
        elif len(self.allowed_file_types) > 0:
            if any("image" in ft for ft in self.allowed_file_types):
                return "image_storage"
            elif any("video" in ft for ft in self.allowed_file_types):
                return "video_storage"
            elif any("audio" in ft for ft in self.allowed_file_types):
                return "audio_storage"
            else:
                return "file_storage"
        elif len(self.lifecycle_rules) > 0:
            return "managed_storage"
        else:
            return "general_storage"
            
    def _estimate_firebase_storage_cost(self) -> float:
        """Estimate monthly cost for Firebase Storage usage"""
        # Firebase Storage pricing (simplified)
        
        # Storage cost (first 5GB free)
        estimated_storage_gb = 10  # 10GB estimated
        free_storage_gb = 5
        storage_cost_per_gb = 0.026  # $0.026 per GB/month
        
        if estimated_storage_gb > free_storage_gb:
            storage_cost = (estimated_storage_gb - free_storage_gb) * storage_cost_per_gb
        else:
            storage_cost = 0.0
        
        # Download cost (first 1GB/day free = ~30GB/month)
        estimated_download_gb = 20  # 20GB estimated monthly downloads
        free_download_gb = 30
        download_cost_per_gb = 0.12  # $0.12 per GB
        
        if estimated_download_gb > free_download_gb:
            download_cost = (estimated_download_gb - free_download_gb) * download_cost_per_gb
        else:
            download_cost = 0.0
        
        # Operations cost (first 50K/day free = ~1.5M/month)
        estimated_operations = 100_000  # 100K operations estimated
        free_operations = 1_500_000
        operations_cost_per_10k = 0.05  # $0.05 per 10K operations
        
        if estimated_operations > free_operations:
            billable_operations = estimated_operations - free_operations
            operations_cost = (billable_operations / 10_000) * operations_cost_per_10k
        else:
            operations_cost = 0.0
        
        total_cost = storage_cost + download_cost + operations_cost
        
        # Adjust based on storage class
        if self.storage_class == "NEARLINE":
            total_cost *= 0.5  # Cheaper storage
        elif self.storage_class == "COLDLINE":
            total_cost *= 0.25
        elif self.storage_class == "ARCHIVE":
            total_cost *= 0.1
        
        # Adjust based on configuration complexity
        if len(self.lifecycle_rules) > 3:
            total_cost *= 1.1  # Lifecycle management overhead
        
        if self.public_access:
            total_cost *= 1.2  # Public access might mean more downloads
        
        # Most small apps stay within free tier
        if total_cost < 1.0:
            total_cost = 0.0
            
        return total_cost
        
    def _fetch_current_storage_state(self) -> Dict[str, Any]:
        """Fetch current state of Firebase Storage from Firebase"""
        try:
            import requests
            from google.auth.transport.requests import Request
            
            if not self.firebase_project_id:
                return {
                    "exists": False,
                    "storage_name": self.storage_name,
                    "error": "No Firebase project ID configured"
                }
            
            # Try to use GCP credentials if available
            if hasattr(self, 'gcp_client') and hasattr(self.gcp_client, 'credentials'):
                # Refresh credentials if needed
                if hasattr(self.gcp_client.credentials, 'refresh'):
                    self.gcp_client.credentials.refresh(Request())
                
                # Use Cloud Storage API to get bucket info
                bucket_name = self.bucket_name or f"{self.firebase_project_id}.appspot.com"
                storage_api_url = f"https://storage.googleapis.com/storage/v1/b/{bucket_name}"
                headers = {
                    'Authorization': f'Bearer {self.gcp_client.credentials.token}',
                    'Content-Type': 'application/json'
                }
                
                response = requests.get(storage_api_url, headers=headers)
                
                if response.status_code == 200:
                    bucket_data = response.json()
                    
                    current_state = {
                        "exists": True,
                        "storage_name": self.storage_name,
                        "bucket_name": bucket_name,
                        "firebase_project_id": self.firebase_project_id,
                        "location": bucket_data.get('location', ''),
                        "storage_class": bucket_data.get('storageClass', 'STANDARD'),
                        "creation_time": bucket_data.get('timeCreated', ''),
                        "updated_time": bucket_data.get('updated', ''),
                        "console_url": f"https://console.firebase.google.com/project/{self.firebase_project_id}/storage/"
                    }
                    
                    # Get versioning info
                    versioning = bucket_data.get('versioning', {})
                    current_state['versioning_enabled'] = versioning.get('enabled', False)
                    
                    # Get CORS info
                    cors_config = bucket_data.get('cors', [])
                    current_state['cors_enabled'] = len(cors_config) > 0
                    current_state['cors_config'] = cors_config
                    
                    # Get lifecycle info
                    lifecycle = bucket_data.get('lifecycle', {})
                    lifecycle_rules = lifecycle.get('rule', [])
                    current_state['lifecycle_rules'] = lifecycle_rules
                    current_state['lifecycle_rule_count'] = len(lifecycle_rules)
                    
                    # Try to get IAM policy for public access check
                    try:
                        iam_url = f"https://storage.googleapis.com/storage/v1/b/{bucket_name}/iam"
                        iam_response = requests.get(iam_url, headers=headers)
                        
                        if iam_response.status_code == 200:
                            iam_data = iam_response.json()
                            bindings = iam_data.get('bindings', [])
                            
                            public_access = False
                            for binding in bindings:
                                members = binding.get('members', [])
                                if 'allUsers' in members or 'allAuthenticatedUsers' in members:
                                    public_access = True
                                    break
                            
                            current_state['public_access'] = public_access
                        else:
                            current_state['public_access'] = False
                            
                    except Exception:
                        current_state['public_access'] = False
                    
                    # Try to get object count and size
                    try:
                        objects_url = f"https://storage.googleapis.com/storage/v1/b/{bucket_name}/o"
                        objects_response = requests.get(f"{objects_url}?maxResults=1000", headers=headers)
                        
                        if objects_response.status_code == 200:
                            objects_data = objects_response.json()
                            objects = objects_data.get('items', [])
                            
                            current_state['object_count'] = len(objects)
                            total_size = sum(int(obj.get('size', 0)) for obj in objects)
                            current_state['total_size_bytes'] = total_size
                            current_state['total_size_gb'] = round(total_size / (1024**3), 2)
                        else:
                            current_state['object_count'] = 0
                            current_state['total_size_bytes'] = 0
                            current_state['total_size_gb'] = 0
                            
                    except Exception:
                        current_state['object_count'] = 0
                        current_state['total_size_bytes'] = 0
                        current_state['total_size_gb'] = 0
                    
                    return current_state
                elif response.status_code == 404:
                    return {
                        "exists": False,
                        "storage_name": self.storage_name,
                        "firebase_project_id": self.firebase_project_id,
                        "bucket_name": bucket_name
                    }
            
            # Fallback: check for local config files
            import os
            import json
            
            config_files = ["storage-config.json", "firebase.json"]
            for config_file in config_files:
                if os.path.exists(config_file):
                    try:
                        with open(config_file, 'r') as f:
                            config_data = json.load(f)
                            
                        storage_config = config_data.get("storage", {})
                        if storage_config:
                            return {
                                "exists": True,
                                "storage_name": self.storage_name,
                                "firebase_project_id": self.firebase_project_id,
                                "config_file": config_file,
                                "local_config": storage_config,
                                "status": "local_config",
                                "console_url": f"https://console.firebase.google.com/project/{self.firebase_project_id}/storage/"
                            }
                    except json.JSONDecodeError:
                        continue
            
            return {
                "exists": False,
                "storage_name": self.storage_name,
                "firebase_project_id": self.firebase_project_id
            }
            
        except Exception as e:
            return {
                "exists": False,
                "storage_name": self.storage_name,
                "firebase_project_id": self.firebase_project_id,
                "error": str(e)
            }
            
    def _discover_existing_buckets(self) -> Dict[str, Dict[str, Any]]:
        """Discover all existing Firebase Storage buckets in the project"""
        existing_buckets = {}
        
        if not self.firebase_project_id:
            return existing_buckets
            
        try:
            import requests
            from google.auth.transport.requests import Request
            
            if hasattr(self, 'gcp_client') and hasattr(self.gcp_client, 'credentials'):
                # Refresh credentials if needed
                if hasattr(self.gcp_client.credentials, 'refresh'):
                    self.gcp_client.credentials.refresh(Request())
                
                # Use Cloud Storage API to list buckets
                storage_api_url = f"https://storage.googleapis.com/storage/v1/b"
                headers = {
                    'Authorization': f'Bearer {self.gcp_client.credentials.token}',
                    'Content-Type': 'application/json'
                }
                
                params = {'project': self.firebase_project_id}
                response = requests.get(storage_api_url, headers=headers, params=params)
                
                if response.status_code == 200:
                    data = response.json()
                    buckets = data.get('items', [])
                    
                    for bucket in buckets:
                        bucket_name = bucket.get('name', '')
                        
                        # Check if this is likely a Firebase Storage bucket
                        is_firebase_bucket = (
                            bucket_name.endswith('.appspot.com') or 
                            bucket_name.endswith('.firebaseapp.com') or
                            bucket_name.startswith(self.firebase_project_id)
                        )
                        
                        bucket_info = {
                            'bucket_name': bucket_name,
                            'firebase_project_id': self.firebase_project_id,
                            'location': bucket.get('location', 'unknown'),
                            'storage_class': bucket.get('storageClass', 'STANDARD'),
                            'creation_time': bucket.get('timeCreated', '')[:10] if bucket.get('timeCreated') else 'unknown',
                            'updated_time': bucket.get('updated', '')[:10] if bucket.get('updated') else 'unknown',
                            'is_firebase_bucket': is_firebase_bucket
                        }
                        
                        # Get additional details for each bucket
                        try:
                            # Get versioning
                            versioning = bucket.get('versioning', {})
                            bucket_info['versioning_enabled'] = versioning.get('enabled', False)
                            
                            # Get CORS
                            cors_config = bucket.get('cors', [])
                            bucket_info['cors_enabled'] = len(cors_config) > 0
                            bucket_info['cors_config'] = cors_config
                            
                            # Get lifecycle
                            lifecycle = bucket.get('lifecycle', {})
                            lifecycle_rules = lifecycle.get('rule', [])
                            bucket_info['lifecycle_rules'] = lifecycle_rules
                            bucket_info['lifecycle_rule_count'] = len(lifecycle_rules)
                            
                            # Check public access (simplified)
                            try:
                                iam_url = f"https://storage.googleapis.com/storage/v1/b/{bucket_name}/iam"
                                iam_response = requests.get(iam_url, headers=headers)
                                
                                public_access = False
                                if iam_response.status_code == 200:
                                    iam_data = iam_response.json()
                                    bindings = iam_data.get('bindings', [])
                                    
                                    for binding in bindings:
                                        members = binding.get('members', [])
                                        if 'allUsers' in members:
                                            public_access = True
                                            break
                                
                                bucket_info['public_access'] = public_access
                                
                            except Exception:
                                bucket_info['public_access'] = False
                            
                            # Get object count and size (limited sample)
                            try:
                                objects_url = f"https://storage.googleapis.com/storage/v1/b/{bucket_name}/o"
                                objects_response = requests.get(f"{objects_url}?maxResults=100", headers=headers)
                                
                                if objects_response.status_code == 200:
                                    objects_data = objects_response.json()
                                    objects = objects_data.get('items', [])
                                    
                                    bucket_info['sample_object_count'] = len(objects)
                                    sample_size = sum(int(obj.get('size', 0)) for obj in objects)
                                    bucket_info['sample_size_bytes'] = sample_size
                                    bucket_info['sample_size_gb'] = round(sample_size / (1024**3), 2) if sample_size > 0 else 0
                                else:
                                    bucket_info['sample_object_count'] = 0
                                    bucket_info['sample_size_bytes'] = 0
                                    bucket_info['sample_size_gb'] = 0
                                    
                            except Exception:
                                bucket_info['sample_object_count'] = 0
                                bucket_info['sample_size_bytes'] = 0
                                bucket_info['sample_size_gb'] = 0
                            
                        except Exception as e:
                            bucket_info['error'] = str(e)
                        
                        existing_buckets[bucket_name] = bucket_info
                        
        except Exception as e:
            print(f"⚠️  Failed to discover existing buckets: {str(e)}")
            
        return existing_buckets