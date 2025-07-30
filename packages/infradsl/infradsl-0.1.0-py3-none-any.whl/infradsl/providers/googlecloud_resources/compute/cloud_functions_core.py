"""
GCP Cloud Functions Core Implementation

Core attributes and authentication for Google Cloud Functions.
Provides the foundation for the modular serverless functions system.
"""

from typing import Dict, Any, List, Optional
from ..base_resource import BaseGcpResource


class CloudFunctionsCore(BaseGcpResource):
    """
    Core class for Google Cloud Functions functionality.
    
    This class provides:
    - Basic function attributes and configuration
    - Authentication setup
    - Common utilities for function operations
    """
    
    def __init__(self, name: str):
        """Initialize cloud functions core with function name"""
        super().__init__(name)
        
        # Core function attributes
        self.function_name = name
        self.function_runtime = "python39"  # Default runtime
        self.function_region = "us-central1"  # Default region
        self.function_entry_point = "main"  # Default entry point
        self.source_path = None
        self.function_memory = "256MB"
        self.function_timeout = "60s"
        self.max_instances = 100
        self.min_instances = 0
        
        # Trigger configuration
        self.trigger_type = "http"  # Default to HTTP trigger
        self.trigger_config = {}
        
        # Function settings
        self.environment_variables = {}
        self.service_account = None
        self.function_labels = {}
        self.description = ""
        self.ingress_settings = "ALLOW_ALL"
        self.function_type = None
        
        # Function URLs and ARNs
        self.function_url = None
        self.function_arn = None
        
        # State tracking
        self.function_exists = False
        self.function_created = False
        
    def _initialize_managers(self):
        """Initialize functions-specific managers"""
        # Will be set up after authentication
        self.functions_manager = None
        
    def _post_authentication_setup(self):
        """Setup managers after authentication"""
        # Import here to avoid circular imports
        from ...googlecloud_managers.compute.cloud_functions_manager import CloudFunctionsManager
        self.functions_manager = CloudFunctionsManager(self.gcp_client)
        
        # Set up function URLs
        if self.trigger_type == "http":
            self.function_url = f"https://{self.function_region}-{self.gcp_client.project_id}.cloudfunctions.net/{self.function_name}"
        self.function_arn = f"projects/{self.gcp_client.project_id}/locations/{self.function_region}/functions/{self.function_name}"
        
    def _is_valid_runtime(self, runtime: str) -> bool:
        """Check if runtime is valid for GCP Cloud Functions"""
        valid_runtimes = [
            "python37", "python38", "python39", "python310", "python311",
            "nodejs14", "nodejs16", "nodejs18", "nodejs20",
            "go116", "go119", "go120", "go121",
            "java11", "java17",
            "dotnet3", "dotnet6",
            "ruby27", "ruby30", "ruby32",
            "php74", "php81", "php82"
        ]
        return runtime in valid_runtimes
        
    def _is_valid_region(self, region: str) -> bool:
        """Check if region is valid for GCP Cloud Functions"""
        gcp_regions = [
            'us-central1', 'us-east1', 'us-east4', 'us-west1', 'us-west2', 'us-west3', 'us-west4',
            'europe-north1', 'europe-west1', 'europe-west2', 'europe-west3', 'europe-west4', 'europe-west6',
            'asia-east1', 'asia-east2', 'asia-northeast1', 'asia-northeast2', 'asia-south1', 'asia-southeast1',
            'australia-southeast1', 'northamerica-northeast1', 'southamerica-east1'
        ]
        return region in gcp_regions
        
    def _is_valid_memory(self, memory: str) -> bool:
        """Check if memory allocation is valid"""
        valid_memory = ["128MB", "256MB", "512MB", "1GB", "2GB", "4GB", "8GB"]
        return memory in valid_memory
        
    def _is_valid_timeout(self, timeout: str) -> bool:
        """Check if timeout is valid (1s to 540s for Gen 1, 1s to 3600s for Gen 2)"""
        import re
        
        # Parse timeout string (e.g., "60s", "5m")
        if timeout.endswith('s'):
            try:
                seconds = int(timeout[:-1])
                return 1 <= seconds <= 3600  # Allow up to 1 hour for Gen 2
            except ValueError:
                return False
        elif timeout.endswith('m'):
            try:
                minutes = int(timeout[:-1])
                return 1 <= (minutes * 60) <= 3600
            except ValueError:
                return False
        
        return False
        
    def _is_valid_trigger_type(self, trigger_type: str) -> bool:
        """Check if trigger type is valid"""
        valid_triggers = ["http", "storage", "pubsub", "firestore", "schedule", "firebase"]
        return trigger_type in valid_triggers
        
    def _fetch_current_cloud_state(self) -> Dict[str, Any]:
        """Fetch current state of the function from Google Cloud"""
        self._ensure_authenticated()
        
        try:
            # Get function info if it exists
            if self.functions_manager:
                function_info = self.functions_manager.get_function_info(
                    self.function_name,
                    self.region
                )
                
                if function_info.get("exists", False):
                    return {
                        "exists": True,
                        "function_name": self.function_name,
                        "runtime": function_info.get("runtime"),
                        "status": function_info.get("status"),
                        "region": function_info.get("region", self.region),
                        "memory": function_info.get("available_memory_mb"),
                        "timeout": function_info.get("timeout"),
                        "entry_point": function_info.get("entry_point"),
                        "source_archive_url": function_info.get("source_archive_url"),
                        "https_url": function_info.get("https_url"),
                        "trigger_type": "http" if function_info.get("https_trigger") else "other",
                        "environment_variables": function_info.get("environment_variables", {}),
                        "labels": function_info.get("labels", {}),
                        "update_time": function_info.get("update_time"),
                        "version_id": function_info.get("version_id")
                    }
                else:
                    return {
                        "exists": False,
                        "function_name": self.function_name
                    }
            else:
                return {
                    "exists": False,
                    "function_name": self.function_name,
                    "error": "Functions manager not initialized"
                }
                
        except Exception as e:
            print(f"⚠️  Warning: Failed to fetch function state: {str(e)}")
            return {
                "exists": False,
                "function_name": self.function_name,
                "error": str(e)
            }