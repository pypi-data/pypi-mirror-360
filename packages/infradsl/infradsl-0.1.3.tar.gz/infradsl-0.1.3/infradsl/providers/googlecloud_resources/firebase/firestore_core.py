"""
Firestore Core Implementation

Core attributes and authentication for Firebase Firestore.
Provides the foundation for the modular NoSQL database system.
"""

from typing import Dict, Any, List, Optional, Union
from ..base_resource import BaseGcpResource


class FirestoreCore(BaseGcpResource):
    """
    Core class for Firebase Firestore functionality.
    
    This class provides:
    - Basic Firestore database attributes and configuration
    - Authentication setup
    - Common utilities for database operations
    - Validation and state tracking foundations
    """
    
    def __init__(self, name: str):
        """Initialize Firestore core with database name"""
        super().__init__(name)
        
        # Core database attributes
        self.database_name = name
        self.database_id = "(default)"  # Default database ID for Firestore
        self.firebase_project_id = None
        self.database_description = f"Firestore database for {name}"
        
        # Database configuration
        self.location_id = "us-central1"
        self.database_mode = "FIRESTORE_NATIVE"  # FIRESTORE_NATIVE or DATASTORE_MODE
        self.concurrency_mode = "OPTIMISTIC"  # OPTIMISTIC, PESSIMISTIC
        self.app_engine_integration_mode = "DISABLED"  # ENABLED, DISABLED
        
        # Collections configuration
        self.collections = []
        self.collection_configs = {}
        
        # Security configuration
        self.security_rules_file = None
        self.security_rules_content = None
        self.default_security_rules = True
        
        # Indexing configuration
        self.composite_indexes = []
        self.single_field_indexes = []
        self.field_overrides = []
        self.ttl_policies = []
        
        # Backup and recovery configuration
        self.backup_enabled = False
        self.backup_schedule = None
        self.point_in_time_recovery = False
        self.delete_protection = False
        
        # Performance configuration
        self.read_time_consistency = "STRONG"  # STRONG, EVENTUAL
        self.transaction_options = {}
        
        # Labels and metadata
        self.database_labels = {}
        self.database_annotations = {}
        
        # State tracking
        self.database_exists = False
        self.database_created = False
        self.database_state = None
        self.deployment_status = None
        
        # Client references
        self.firestore_client = None
        self.firestore_admin_client = None
        
        # Estimated costs
        self.estimated_monthly_cost = "$25.00/month"
        
    def _initialize_managers(self):
        """Initialize Firestore-specific managers"""
        self.firestore_client = None
        self.firestore_admin_client = None
        
    def _post_authentication_setup(self):
        """Setup managers after authentication"""
        try:
            # Firestore uses Firebase project ID rather than GCP project ID
            # Set project context if available
            if not self.firebase_project_id and hasattr(self.gcp_client, 'project_id'):
                self.firebase_project_id = self.gcp_client.project_id
                
        except Exception as e:
            print(f"⚠️  Firestore setup note: {str(e)}")
            
    def _is_valid_project_id(self, project_id: str) -> bool:
        """Check if Firebase project ID is valid"""
        import re
        # Firebase project IDs must contain only lowercase letters, numbers, dashes
        pattern = r'^[a-z][a-z0-9-]*[a-z0-9]$'
        return bool(re.match(pattern, project_id)) and 4 <= len(project_id) <= 30
        
    def _is_valid_location(self, location: str) -> bool:
        """Check if location is valid for Firestore"""
        valid_locations = [
            "us-central1", "us-east1", "us-east4", "us-west1", "us-west2", "us-west3", "us-west4",
            "europe-central2", "europe-west1", "europe-west2", "europe-west3", "europe-west6",
            "asia-east1", "asia-east2", "asia-northeast1", "asia-northeast2", "asia-northeast3",
            "asia-south1", "asia-southeast1", "asia-southeast2", "australia-southeast1",
            "southamerica-east1"
        ]
        return location in valid_locations
        
    def _is_valid_collection_name(self, name: str) -> bool:
        """Check if collection name is valid"""
        import re
        # Collection names must not contain certain characters
        if not name or len(name) > 1500:
            return False
        # Must not start or end with a dot, or contain consecutive dots
        if name.startswith('.') or name.endswith('.') or '..' in name:
            return False
        # Must not match reserved names
        reserved_names = ["__.*__"]
        for pattern in reserved_names:
            if re.match(pattern, name):
                return False
        return True
        
    def _validate_database_config(self, config: Dict[str, Any]) -> bool:
        """Validate database configuration"""
        required_fields = ["firebase_project_id", "location_id"]
        
        for field in required_fields:
            if field not in config or not config[field]:
                return False
                
        # Validate project ID format
        if not self._is_valid_project_id(config["firebase_project_id"]):
            return False
            
        # Validate location
        if not self._is_valid_location(config["location_id"]):
            return False
            
        # Validate collections if provided
        collections = config.get("collections", [])
        for collection in collections:
            if not self._is_valid_collection_name(collection):
                return False
                
        return True
        
    def _get_database_type_from_config(self) -> str:
        """Determine database type from configuration"""
        labels = self.database_labels
        
        # Check for purpose-based types
        purpose = labels.get("purpose", "").lower()
        if purpose:
            if "realtime" in purpose:
                return "realtime_database"
            elif "analytics" in purpose:
                return "analytics_database"
            elif "content" in purpose:
                return "content_management"
            elif "user" in purpose:
                return "user_data"
            elif "chat" in purpose:
                return "chat_messaging"
            elif "ecommerce" in purpose:
                return "ecommerce_database"
        
        # Check environment
        environment = labels.get("environment", "").lower()
        if environment:
            if environment == "development":
                return "development"
            elif environment == "staging":
                return "staging"
            elif environment == "production":
                return "production"
        
        # Check by mode and collections
        if self.database_mode == "DATASTORE_MODE":
            return "datastore_compatibility"
        elif len(self.collections) == 0:
            return "empty_database"
        elif len(self.collections) <= 5:
            return "simple_app"
        elif len(self.collections) <= 20:
            return "complex_app"
        else:
            return "enterprise_app"
            
    def _estimate_firestore_cost(self) -> float:
        """Estimate monthly cost for Firestore usage"""
        # Firestore pricing (simplified)
        
        # Document operations (reads, writes, deletes)
        # Rough estimates for a medium-sized app
        estimated_reads_per_month = 1_000_000  # 1M reads
        estimated_writes_per_month = 200_000   # 200K writes
        estimated_deletes_per_month = 10_000   # 10K deletes
        
        # Pricing per operation (in dollars)
        read_cost = estimated_reads_per_month * 0.000036  # $0.036 per 100K reads
        write_cost = estimated_writes_per_month * 0.00018  # $0.18 per 100K writes
        delete_cost = estimated_deletes_per_month * 0.000002  # $0.002 per 100K deletes
        
        # Storage cost
        estimated_storage_gb = 5  # 5GB of data
        storage_cost = estimated_storage_gb * 0.18  # $0.18 per GB/month
        
        # Network egress (minimal for most apps)
        network_cost = 1.0  # $1 estimated
        
        total_cost = read_cost + write_cost + delete_cost + storage_cost + network_cost
        
        # Adjust based on number of collections (complexity)
        collection_count = len(self.collections)
        if collection_count > 10:
            total_cost *= 1.5  # More complex apps use more resources
        elif collection_count > 20:
            total_cost *= 2.0
        
        # Minimum cost
        if total_cost < 1.0:
            total_cost = 1.0
            
        return total_cost
        
    def _fetch_current_firestore_state(self) -> Dict[str, Any]:
        """Fetch current state of Firestore database from Firebase"""
        try:
            import requests
            from google.auth.transport.requests import Request
            
            if not self.firebase_project_id:
                return {
                    "exists": False,
                    "database_name": self.database_name,
                    "error": "No Firebase project ID configured"
                }
            
            # Try to use GCP credentials if available
            if hasattr(self, 'gcp_client') and hasattr(self.gcp_client, 'credentials'):
                # Refresh credentials if needed
                if hasattr(self.gcp_client.credentials, 'refresh'):
                    self.gcp_client.credentials.refresh(Request())
                
                # Use Firestore Admin API to get database info
                firestore_api_url = f"https://firestore.googleapis.com/v1/projects/{self.firebase_project_id}/databases/{self.database_id}"
                headers = {
                    'Authorization': f'Bearer {self.gcp_client.credentials.token}',
                    'Content-Type': 'application/json'
                }
                
                response = requests.get(firestore_api_url, headers=headers)
                
                if response.status_code == 200:
                    database_data = response.json()
                    
                    current_state = {
                        "exists": True,
                        "database_name": self.database_name,
                        "database_id": self.database_id,
                        "firebase_project_id": self.firebase_project_id,
                        "full_name": database_data.get("name", ""),
                        "location_id": database_data.get("locationId", ""),
                        "database_type": database_data.get("type", ""),
                        "concurrency_mode": database_data.get("concurrencyMode", ""),
                        "app_engine_integration_mode": database_data.get("appEngineIntegrationMode", ""),
                        "state": database_data.get("state", ""),
                        "create_time": database_data.get("createTime", ""),
                        "etag": database_data.get("etag", ""),
                        "console_url": f"https://console.firebase.google.com/project/{self.firebase_project_id}/firestore/"
                    }
                    
                    # Try to get collections information
                    try:
                        collections_url = f"https://firestore.googleapis.com/v1/projects/{self.firebase_project_id}/databases/{self.database_id}/documents"
                        collections_response = requests.get(collections_url, headers=headers)
                        
                        collections = []
                        document_count = 0
                        
                        if collections_response.status_code == 200:
                            collections_data = collections_response.json()
                            documents = collections_data.get('documents', [])
                            
                            # Extract collection names from document paths
                            collection_names = set()
                            for doc in documents:
                                doc_name = doc.get('name', '')
                                if '/documents/' in doc_name:
                                    doc_path = doc_name.split('/documents/')[-1]
                                    if '/' in doc_path:
                                        collection_name = doc_path.split('/')[0]
                                        collection_names.add(collection_name)
                            
                            collections = list(collection_names)
                            document_count = len(documents)
                        
                        current_state['collections'] = collections
                        current_state['collection_count'] = len(collections)
                        current_state['document_count'] = document_count
                        
                    except Exception:
                        current_state['collections'] = []
                        current_state['collection_count'] = 0
                        current_state['document_count'] = 0
                    
                    return current_state
                elif response.status_code == 404:
                    return {
                        "exists": False,
                        "database_name": self.database_name,
                        "firebase_project_id": self.firebase_project_id
                    }
            
            # Fallback: check for local config files
            import os
            import json
            
            config_files = ["firestore-config.json", "firebase.json"]
            for config_file in config_files:
                if os.path.exists(config_file):
                    try:
                        with open(config_file, 'r') as f:
                            config_data = json.load(f)
                            
                        firestore_config = config_data.get("firestore", {})
                        if firestore_config:
                            return {
                                "exists": True,
                                "database_name": self.database_name,
                                "firebase_project_id": self.firebase_project_id,
                                "config_file": config_file,
                                "local_config": firestore_config,
                                "status": "local_config",
                                "console_url": f"https://console.firebase.google.com/project/{self.firebase_project_id}/firestore/"
                            }
                    except json.JSONDecodeError:
                        continue
            
            return {
                "exists": False,
                "database_name": self.database_name,
                "firebase_project_id": self.firebase_project_id
            }
            
        except Exception as e:
            return {
                "exists": False,
                "database_name": self.database_name,
                "firebase_project_id": self.firebase_project_id,
                "error": str(e)
            }
            
    def _discover_existing_databases(self) -> Dict[str, Dict[str, Any]]:
        """Discover all existing Firestore databases in the project"""
        existing_databases = {}
        
        if not self.firebase_project_id:
            return existing_databases
            
        try:
            import requests
            from google.auth.transport.requests import Request
            
            if hasattr(self, 'gcp_client') and hasattr(self.gcp_client, 'credentials'):
                # Refresh credentials if needed
                if hasattr(self.gcp_client.credentials, 'refresh'):
                    self.gcp_client.credentials.refresh(Request())
                
                # Use Firestore Admin API to list databases
                firestore_api_url = f"https://firestore.googleapis.com/v1/projects/{self.firebase_project_id}/databases"
                headers = {
                    'Authorization': f'Bearer {self.gcp_client.credentials.token}',
                    'Content-Type': 'application/json'
                }
                
                response = requests.get(firestore_api_url, headers=headers)
                
                if response.status_code == 200:
                    data = response.json()
                    databases = data.get('databases', [])
                    
                    for database in databases:
                        database_id = database.get('name', '').split('/')[-1]
                        
                        database_info = {
                            'database_id': database_id,
                            'full_name': database['name'],
                            'location_id': database.get('locationId', 'unknown'),
                            'database_type': database.get('type', 'FIRESTORE_NATIVE'),
                            'concurrency_mode': database.get('concurrencyMode', 'OPTIMISTIC'),
                            'app_engine_integration_mode': database.get('appEngineIntegrationMode', 'DISABLED'),
                            'state': database.get('state', 'UNKNOWN'),
                            'create_time': database.get('createTime', '')[:10] if database.get('createTime') else 'unknown',
                            'etag': database.get('etag', ''),
                            'firebase_project_id': self.firebase_project_id
                        }
                        
                        # Get additional info for each database
                        try:
                            # Get collections count (simplified)
                            collections_url = f"https://firestore.googleapis.com/v1/projects/{self.firebase_project_id}/databases/{database_id}/documents"
                            collections_response = requests.get(collections_url, headers=headers)
                            
                            collection_count = 0
                            document_count = 0
                            
                            if collections_response.status_code == 200:
                                collections_data = collections_response.json()
                                documents = collections_data.get('documents', [])
                                
                                collection_names = set()
                                for doc in documents:
                                    doc_name = doc.get('name', '')
                                    if '/documents/' in doc_name:
                                        doc_path = doc_name.split('/documents/')[-1]
                                        if '/' in doc_path:
                                            collection_name = doc_path.split('/')[0]
                                            collection_names.add(collection_name)
                                
                                collection_count = len(collection_names)
                                document_count = len(documents)
                            
                            database_info['collection_count'] = collection_count
                            database_info['document_count'] = document_count
                            
                        except Exception:
                            database_info['collection_count'] = 0
                            database_info['document_count'] = 0
                        
                        existing_databases[database_id] = database_info
                        
        except Exception as e:
            print(f"⚠️  Failed to discover existing databases: {str(e)}")
            
        return existing_databases