"""
GCP Cloud Storage Core Implementation

Core attributes and authentication for Google Cloud Storage buckets.
Provides the foundation for the modular storage system.
"""

from typing import Dict, Any, List, Optional
from ..base_resource import BaseGcpResource


class StorageCore(BaseGcpResource):
    """
    Core class for Google Cloud Storage bucket functionality.
    
    This class provides:
    - Basic bucket attributes and configuration
    - Authentication setup
    - Common utilities for bucket operations
    """
    
    def __init__(self, name: str):
        """Initialize storage core with bucket name"""
        super().__init__(name)
        
        # Core bucket attributes
        self.bucket_name = name
        self.location = "US"  # Default location
        self.storage_class = "STANDARD"  # Default storage class
        self.public_access_prevention = "enforced"  # Secure by default
        self.versioning_enabled = False
        self.lifecycle_rules = []
        self.cors_rules = []
        self.bucket_labels = {}
        self.retention_period = None
        
        # Storage URLs and ARNs
        self.bucket_url = None
        self.bucket_arn = None
        self.website_url = None
        
        # Upload queues
        self._files_to_upload = []
        self._directories_to_upload = []
        
        # State tracking
        self.bucket_exists = False
        self.bucket_created = False
        
    def _initialize_managers(self):
        """Initialize storage-specific managers"""
        # Will be set up after authentication
        self.bucket_manager = None
        
    def _post_authentication_setup(self):
        """Setup managers after authentication"""
        # Import here to avoid circular imports
        from ...googlecloud_managers.storage.bucket_manager import BucketManager
        self.bucket_manager = BucketManager(self.gcp_client)
        
        # Set up bucket URLs
        self.bucket_url = f"gs://{self.bucket_name}"
        self.bucket_arn = f"projects/{self.gcp_client.project_id}/buckets/{self.bucket_name}"
        if self.public_access_prevention == "inherited":
            self.website_url = f"https://storage.googleapis.com/{self.bucket_name}"
        
    def _is_valid_bucket_name(self, bucket_name: str) -> bool:
        """Validate GCP bucket name according to Google Cloud rules"""
        import re
        
        # Basic validation rules
        if len(bucket_name) < 3 or len(bucket_name) > 63:
            return False
            
        # Must be lowercase letters, numbers, hyphens, and underscores
        if not re.match(r'^[a-z0-9._-]+$', bucket_name):
            return False
            
        # Cannot start or end with period or hyphen
        if bucket_name.startswith('.') or bucket_name.startswith('-'):
            return False
        if bucket_name.endswith('.') or bucket_name.endswith('-'):
            return False
            
        # Cannot contain consecutive periods
        if '..' in bucket_name:
            return False
            
        # Cannot look like an IP address
        if re.match(r'^(\d{1,3}\.){3}\d{1,3}$', bucket_name):
            return False
            
        return True
        
    def _is_valid_location(self, location: str) -> bool:
        """Check if location is a valid GCP location"""
        gcp_locations = [
            'US', 'EU', 'ASIA',  # Multi-region
            'us-central1', 'us-east1', 'us-east4', 'us-west1', 'us-west2', 'us-west3', 'us-west4',
            'europe-north1', 'europe-west1', 'europe-west2', 'europe-west3', 'europe-west4', 'europe-west6',
            'asia-east1', 'asia-east2', 'asia-northeast1', 'asia-northeast2', 'asia-south1', 'asia-southeast1',
            'australia-southeast1', 'northamerica-northeast1', 'southamerica-east1'
        ]
        return location in gcp_locations
        
    def _is_valid_storage_class(self, storage_class: str) -> bool:
        """Check if storage class is valid for GCP"""
        valid_classes = ["STANDARD", "NEARLINE", "COLDLINE", "ARCHIVE"]
        return storage_class in valid_classes
        
    def _fetch_current_cloud_state(self) -> Dict[str, Any]:
        """Fetch current state of the bucket from Google Cloud"""
        self._ensure_authenticated()
        
        try:
            # Get bucket info if it exists
            bucket_info = self.bucket_manager.get_bucket_info(self.bucket_name)
            
            if bucket_info.get("exists", False):
                return {
                    "exists": True,
                    "bucket_name": self.bucket_name,
                    "location": bucket_info.get("location"),
                    "storage_class": bucket_info.get("storage_class"),
                    "versioning_enabled": bucket_info.get("versioning_enabled", False),
                    "public_access_prevention": bucket_info.get("public_access_prevention"),
                    "labels": bucket_info.get("labels", {}),
                    "creation_time": bucket_info.get("creation_time"),
                    "lifecycle_rules": bucket_info.get("lifecycle_rules", []),
                    "cors_rules": bucket_info.get("cors_rules", [])
                }
            else:
                return {
                    "exists": False,
                    "bucket_name": self.bucket_name
                }
                
        except Exception as e:
            print(f"⚠️  Warning: Failed to fetch bucket state: {str(e)}")
            return {
                "exists": False,
                "bucket_name": self.bucket_name,
                "error": str(e)
            }