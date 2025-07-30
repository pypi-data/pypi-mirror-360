"""
Firebase Functions Core Implementation

Core attributes and authentication for Firebase Functions.
Provides the foundation for the modular serverless functions system.
"""

from typing import Dict, Any, List, Optional, Union
from ..base_resource import BaseGcpResource


class FirebaseFunctionsCore(BaseGcpResource):
    """
    Core class for Firebase Functions functionality.
    
    This class provides:
    - Basic Firebase Functions attributes and configuration
    - Authentication setup
    - Common utilities for serverless operations
    - Validation and state tracking foundations
    """
    
    def __init__(self, name: str):
        """Initialize Firebase Functions core with project name"""
        super().__init__(name)
        
        # Core project attributes
        self.functions_name = name
        self.firebase_project_id = None
        self.functions_description = f"Firebase Functions for {name}"
        
        # Runtime configuration
        self.runtime = "nodejs18"  # nodejs18, python311, go119, java11, etc.
        self.region = "us-central1"
        self.source_directory = "functions"
        self.entry_point = "index.js"
        
        # Function configurations
        self.functions = []
        self.function_configs = {}
        
        # Resource allocation defaults
        self.default_memory = "256MB"  # 128MB, 256MB, 512MB, 1GB, 2GB, 4GB, 8GB
        self.default_timeout = 60  # seconds (max 540s for HTTP, 9min)
        self.default_max_instances = 1000
        self.default_min_instances = 0
        
        # Environment and configuration
        self.environment_variables = {}
        self.secrets = {}
        self.vpc_connector = None
        self.ingress_settings = "ALLOW_ALL"  # ALLOW_ALL, ALLOW_INTERNAL_ONLY, ALLOW_INTERNAL_AND_GCLB
        self.egress_settings = "PRIVATE_RANGES_ONLY"  # PRIVATE_RANGES_ONLY, ALL
        
        # Dependencies and build configuration
        self.dependencies = {}
        self.dev_dependencies = {}
        self.build_env_vars = {}
        self.ignore_files = [".git", "node_modules", ".env*"]
        
        # Security configuration
        self.require_auth = False
        self.cors_enabled = True
        self.cors_origins = ["*"]
        self.invoker_permissions = []  # List of service accounts/users that can invoke
        
        # Monitoring and logging
        self.logging_config = {
            "log_level": "INFO",
            "error_reporting": True,
            "cloud_trace": False,
            "cloud_profiler": False
        }
        
        # Performance configuration
        self.concurrency = 1  # Requests per instance
        self.cpu = 1  # CPU allocation
        self.execution_environment = "gen2"  # gen1 or gen2
        
        # Labels and metadata
        self.functions_labels = {}
        self.functions_annotations = {}
        
        # State tracking
        self.functions_deployed = False
        self.deployment_status = None
        self.deployment_time = None
        self.last_updated = None
        
        # Cost tracking
        self.estimated_monthly_cost = "$5.00/month"
        
        # Client references
        self.functions_client = None
        self.cloud_functions_client = None
        
    def _initialize_managers(self):
        """Initialize Firebase Functions-specific managers"""
        self.functions_client = None
        self.cloud_functions_client = None
        
    def _post_authentication_setup(self):
        """Setup managers after authentication"""
        try:
            # Firebase Functions uses Firebase project ID rather than GCP project ID
            # Set project context if available
            if not self.firebase_project_id and hasattr(self.gcp_client, 'project_id'):
                self.firebase_project_id = self.gcp_client.project_id
                
        except Exception as e:
            print(f"⚠️  Firebase Functions setup note: {str(e)}")
            
    def _is_valid_project_id(self, project_id: str) -> bool:
        """Check if Firebase project ID is valid"""
        import re
        # Firebase project IDs must contain only lowercase letters, numbers, dashes
        pattern = r'^[a-z][a-z0-9-]*[a-z0-9]$'
        return bool(re.match(pattern, project_id)) and 4 <= len(project_id) <= 30
        
    def _is_valid_function_name(self, name: str) -> bool:
        """Check if function name is valid"""
        import re
        # Function names must be valid JavaScript identifiers
        if not name or len(name) > 63:
            return False
        # Must start with letter, contain only letters, numbers, underscores, hyphens
        pattern = r'^[a-zA-Z][a-zA-Z0-9_-]*$'
        return bool(re.match(pattern, name))
    
    def _is_valid_runtime(self, runtime: str) -> bool:
        """Check if runtime is valid"""
        valid_runtimes = [
            "nodejs18", "nodejs16", "nodejs14",
            "python311", "python39", "python38",
            "go119", "go118", "go116",
            "java17", "java11",
            "dotnet6", "dotnet3",
            "ruby30", "ruby27"
        ]
        return runtime in valid_runtimes
        
    def _is_valid_region(self, region: str) -> bool:
        """Check if region is valid for Cloud Functions"""
        valid_regions = [
            "us-central1", "us-east1", "us-east4", "us-west1", "us-west2", "us-west3", "us-west4",
            "europe-central2", "europe-west1", "europe-west2", "europe-west3", "europe-west6",
            "asia-east1", "asia-east2", "asia-northeast1", "asia-northeast2", "asia-northeast3",
            "asia-south1", "asia-southeast1", "asia-southeast2", "australia-southeast1",
            "southamerica-east1"
        ]
        return region in valid_regions
        
    def _is_valid_memory(self, memory: str) -> bool:
        """Check if memory allocation is valid"""
        valid_memory = ["128MB", "256MB", "512MB", "1GB", "2GB", "4GB", "8GB", "16GB", "32GB"]
        return memory in valid_memory
        
    def _validate_function_config(self, config: Dict[str, Any]) -> bool:
        """Validate function configuration"""
        required_fields = ["name", "type"]
        
        for field in required_fields:
            if field not in config or not config[field]:
                return False
                
        # Validate function name
        if not self._is_valid_function_name(config["name"]):
            return False
            
        # Validate function type
        valid_types = ["http", "callable", "firestore", "storage", "scheduled", "pubsub", "auth", "analytics"]
        if config["type"] not in valid_types:
            return False
            
        # Validate memory if provided
        if "memory" in config and not self._is_valid_memory(config["memory"]):
            return False
            
        # Validate timeout if provided
        if "timeout" in config:
            timeout = config["timeout"]
            if not isinstance(timeout, int) or timeout < 1 or timeout > 540:
                return False
                
        return True
        
    def _get_functions_type_from_config(self) -> str:
        """Determine functions type from configuration"""
        labels = self.functions_labels
        
        # Check for purpose-based types
        purpose = labels.get("purpose", "").lower()
        if purpose:
            if "api" in purpose:
                return "api_backend"
            elif "webhook" in purpose:
                return "webhook_handler"
            elif "trigger" in purpose:
                return "event_processor"
            elif "scheduled" in purpose:
                return "scheduled_tasks"
            elif "analytics" in purpose:
                return "analytics_processor"
            elif "auth" in purpose:
                return "auth_handler"
        
        # Check environment
        environment = labels.get("environment", "").lower()
        if environment:
            if environment == "development":
                return "development"
            elif environment == "staging":
                return "staging"
            elif environment == "production":
                return "production"
        
        # Check by function types
        function_types = set()
        for func in self.functions:
            function_types.add(func.get("type", "unknown"))
        
        if "http" in function_types and len(function_types) == 1:
            return "api_only"
        elif "callable" in function_types and len(function_types) == 1:
            return "callable_only"
        elif "firestore" in function_types or "storage" in function_types:
            return "trigger_based"
        elif "scheduled" in function_types:
            return "scheduled_tasks"
        elif len(function_types) > 3:
            return "microservices"
        elif len(self.functions) == 0:
            return "empty_project"
        elif len(self.functions) <= 3:
            return "simple_backend"
        elif len(self.functions) <= 10:
            return "complex_backend"
        else:
            return "enterprise_backend"
            
    def _estimate_firebase_functions_cost(self) -> float:
        """Estimate monthly cost for Firebase Functions usage"""
        # Firebase Functions pricing (simplified)
        
        # Base pricing (first 2M invocations free)
        invocations_per_month = 100_000  # 100K invocations estimate
        compute_gb_seconds_per_month = 50_000  # 50K GB-seconds estimate
        outbound_gb_per_month = 1  # 1GB outbound data estimate
        
        # Free tier limits
        free_invocations = 2_000_000  # 2M free invocations
        free_compute_gb_seconds = 400_000  # 400K GB-seconds free
        free_outbound_gb = 5  # 5GB free outbound
        
        # Pricing rates
        invocation_cost_per_million = 0.40  # $0.40 per million invocations
        compute_cost_per_gb_second = 0.0000025  # $0.0000025 per GB-second
        outbound_cost_per_gb = 0.12  # $0.12 per GB
        
        # Calculate costs
        total_cost = 0.0
        
        # Invocation costs
        if invocations_per_month > free_invocations:
            billable_invocations = invocations_per_month - free_invocations
            total_cost += (billable_invocations / 1_000_000) * invocation_cost_per_million
        
        # Compute costs
        if compute_gb_seconds_per_month > free_compute_gb_seconds:
            billable_compute = compute_gb_seconds_per_month - free_compute_gb_seconds
            total_cost += billable_compute * compute_cost_per_gb_second
        
        # Outbound data costs
        if outbound_gb_per_month > free_outbound_gb:
            billable_outbound = outbound_gb_per_month - free_outbound_gb
            total_cost += billable_outbound * outbound_cost_per_gb
        
        # Adjust based on number of functions (complexity)
        function_count = len(self.functions)
        if function_count > 5:
            total_cost *= 1.5  # More functions typically mean more usage
        elif function_count > 10:
            total_cost *= 2.0
        
        # Adjust based on memory allocation
        if self.default_memory in ["1GB", "2GB", "4GB", "8GB"]:
            total_cost *= 1.5  # Higher memory means higher costs
        
        # Most small apps stay within free tier
        if total_cost < 0.50:
            total_cost = 0.0
            
        return total_cost
        
    def _fetch_current_functions_state(self) -> Dict[str, Any]:
        """Fetch current state of Firebase Functions from Firebase"""
        try:
            import requests
            from google.auth.transport.requests import Request
            
            if not self.firebase_project_id:
                return {
                    "exists": False,
                    "functions_name": self.functions_name,
                    "error": "No Firebase project ID configured"
                }
            
            # Try to use GCP credentials if available
            if hasattr(self, 'gcp_client') and hasattr(self.gcp_client, 'credentials'):
                # Refresh credentials if needed
                if hasattr(self.gcp_client.credentials, 'refresh'):
                    self.gcp_client.credentials.refresh(Request())
                
                # Use Cloud Functions API to get functions info
                functions_api_url = f"https://cloudfunctions.googleapis.com/v1/projects/{self.firebase_project_id}/locations/{self.region}/functions"
                headers = {
                    'Authorization': f'Bearer {self.gcp_client.credentials.token}',
                    'Content-Type': 'application/json'
                }
                
                response = requests.get(functions_api_url, headers=headers)
                
                if response.status_code == 200:
                    functions_data = response.json()
                    functions_list = functions_data.get('functions', [])
                    
                    # Filter for Firebase Functions (they have specific labels)
                    firebase_functions = []
                    for func in functions_list:
                        labels = func.get('labels', {})
                        if ('firebase-functions-hash' in labels or 
                            'deployment-tool' in labels and labels.get('deployment-tool') == 'firebase-tools'):
                            firebase_functions.append(func)
                    
                    current_state = {
                        "exists": True,
                        "functions_name": self.functions_name,
                        "firebase_project_id": self.firebase_project_id,
                        "region": self.region,
                        "function_count": len(firebase_functions),
                        "functions": firebase_functions,
                        "console_url": f"https://console.firebase.google.com/project/{self.firebase_project_id}/functions/"
                    }
                    
                    # Analyze function types
                    function_types = {}
                    total_memory = 0
                    runtimes = set()
                    
                    for func in firebase_functions:
                        # Determine function type from trigger
                        func_type = "unknown"
                        if 'httpsTrigger' in func:
                            func_type = "http"
                        elif 'eventTrigger' in func:
                            event_trigger = func['eventTrigger']
                            event_type = event_trigger.get('eventType', '')
                            if 'firestore' in event_type.lower():
                                func_type = "firestore"
                            elif 'storage' in event_type.lower():
                                func_type = "storage"
                            elif 'pubsub' in event_type.lower():
                                func_type = "pubsub"
                            elif 'auth' in event_type.lower():
                                func_type = "auth"
                            else:
                                func_type = "event"
                        
                        function_types[func_type] = function_types.get(func_type, 0) + 1
                        
                        # Aggregate memory and runtime info
                        memory_mb = func.get('availableMemoryMb', 256)
                        total_memory += memory_mb
                        
                        runtime = func.get('runtime', 'unknown')
                        runtimes.add(runtime)
                    
                    current_state['function_types'] = function_types
                    current_state['total_memory_mb'] = total_memory
                    current_state['average_memory_mb'] = total_memory // max(len(firebase_functions), 1)
                    current_state['runtimes'] = list(runtimes)
                    
                    return current_state
                elif response.status_code == 404:
                    return {
                        "exists": False,
                        "functions_name": self.functions_name,
                        "firebase_project_id": self.firebase_project_id
                    }
            
            # Fallback: check for local config files
            import os
            import json
            
            config_files = ["firebase.json", "functions/package.json"]
            for config_file in config_files:
                if os.path.exists(config_file):
                    try:
                        with open(config_file, 'r') as f:
                            config_data = json.load(f)
                            
                        functions_config = config_data.get("functions", {})
                        if functions_config or config_file.endswith("package.json"):
                            return {
                                "exists": True,
                                "functions_name": self.functions_name,
                                "firebase_project_id": self.firebase_project_id,
                                "config_file": config_file,
                                "local_config": functions_config if functions_config else config_data,
                                "status": "local_config",
                                "console_url": f"https://console.firebase.google.com/project/{self.firebase_project_id}/functions/"
                            }
                    except json.JSONDecodeError:
                        continue
            
            return {
                "exists": False,
                "functions_name": self.functions_name,
                "firebase_project_id": self.firebase_project_id
            }
            
        except Exception as e:
            return {
                "exists": False,
                "functions_name": self.functions_name,
                "firebase_project_id": self.firebase_project_id,
                "error": str(e)
            }
            
    def _discover_existing_functions(self) -> Dict[str, Dict[str, Any]]:
        """Discover all existing Firebase Functions in the project"""
        existing_functions = {}
        
        if not self.firebase_project_id:
            return existing_functions
            
        try:
            import requests
            from google.auth.transport.requests import Request
            
            if hasattr(self, 'gcp_client') and hasattr(self.gcp_client, 'credentials'):
                # Refresh credentials if needed
                if hasattr(self.gcp_client.credentials, 'refresh'):
                    self.gcp_client.credentials.refresh(Request())
                
                # Use Cloud Functions API to list functions
                functions_api_url = f"https://cloudfunctions.googleapis.com/v1/projects/{self.firebase_project_id}/locations/{self.region}/functions"
                headers = {
                    'Authorization': f'Bearer {self.gcp_client.credentials.token}',
                    'Content-Type': 'application/json'
                }
                
                response = requests.get(functions_api_url, headers=headers)
                
                if response.status_code == 200:
                    data = response.json()
                    functions = data.get('functions', [])
                    
                    for function in functions:
                        function_name = function.get('name', '').split('/')[-1]
                        
                        # Check if this is a Firebase function
                        labels = function.get('labels', {})
                        is_firebase_function = (
                            'firebase-functions-hash' in labels or
                            'deployment-tool' in labels and labels.get('deployment-tool') == 'firebase-tools'
                        )
                        
                        # Determine trigger type
                        trigger_type = "unknown"
                        trigger_config = {}
                        
                        if 'httpsTrigger' in function:
                            trigger_type = "http"
                            trigger_config = {
                                'url': function['httpsTrigger'].get('url', ''),
                                'security_level': function['httpsTrigger'].get('securityLevel', 'SECURE_ALWAYS')
                            }
                        elif 'eventTrigger' in function:
                            event_trigger = function['eventTrigger']
                            event_type = event_trigger.get('eventType', '')
                            
                            if 'firestore' in event_type.lower():
                                trigger_type = "firestore"
                            elif 'storage' in event_type.lower():
                                trigger_type = "storage"
                            elif 'pubsub' in event_type.lower():
                                trigger_type = "pubsub"
                            elif 'auth' in event_type.lower():
                                trigger_type = "auth"
                            else:
                                trigger_type = "event"
                            
                            trigger_config = {
                                'event_type': event_type,
                                'resource': event_trigger.get('resource', ''),
                                'service': event_trigger.get('service', '')
                            }
                        
                        function_info = {
                            'function_name': function_name,
                            'full_name': function['name'],
                            'runtime': function.get('runtime', 'unknown'),
                            'trigger_type': trigger_type,
                            'trigger_config': trigger_config,
                            'available_memory_mb': function.get('availableMemoryMb', 256),
                            'timeout': function.get('timeout', '60s'),
                            'status': function.get('status', 'UNKNOWN'),
                            'update_time': function.get('updateTime', '')[:10] if function.get('updateTime') else 'unknown',
                            'version_id': function.get('versionId', ''),
                            'source_archive_url': function.get('sourceArchiveUrl', ''),
                            'entry_point': function.get('entryPoint', 'main'),
                            'environment_variables': function.get('environmentVariables', {}),
                            'labels': labels,
                            'is_firebase_function': is_firebase_function,
                            'firebase_project_id': self.firebase_project_id,
                            'region': self.region
                        }
                        
                        existing_functions[function_name] = function_info
                        
        except Exception as e:
            print(f"⚠️  Failed to discover existing functions: {str(e)}")
            
        return existing_functions