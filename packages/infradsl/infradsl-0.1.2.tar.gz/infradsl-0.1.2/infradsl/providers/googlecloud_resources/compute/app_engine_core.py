"""
Google App Engine Core Implementation

Core attributes and authentication for Google App Engine.
Provides the foundation for the modular App Engine platform as a service.
"""

from typing import Dict, Any, List, Optional, Union
from ..base_resource import BaseGcpResource


class AppEngineCore(BaseGcpResource):
    """
    Core class for Google App Engine functionality.
    
    This class provides:
    - Basic App Engine attributes and configuration
    - Authentication setup
    - Common utilities for App Engine operations
    - Validation and state tracking foundations
    """
    
    def __init__(self, name: str):
        """
        Initialize App Engine core with application name.
        
        Args:
            name: App Engine application name
        """
        super().__init__(name)
        
        # Core App Engine attributes
        self.app_name = name
        self.app_description = f"Google App Engine application: {name}"
        self.app_type = "appengine_application"
        
        # Application configuration
        self.app_id = None
        self.project_id = None
        self.location_id = "us-central"
        self.serving_status = "SERVING"
        self.database_type = "CLOUD_DATASTORE_COMPATIBILITY"
        
        # Runtime configuration
        self.runtime = "python39"
        self.runtime_version = None
        self.instance_class = "F1"
        self.automatic_scaling = True
        self.manual_scaling = False
        self.basic_scaling = False
        
        # Scaling configuration
        self.min_instances = 0
        self.max_instances = 10
        self.target_cpu_utilization = 0.6
        self.target_throughput_utilization = 0.6
        self.min_pending_latency = "30ms"
        self.max_pending_latency = "30s"
        
        # Network configuration
        self.network = None
        self.subnetwork = None
        self.session_affinity = False
        
        # Environment variables
        self.env_vars = {}
        
        # Handlers and routing
        self.handlers = []
        self.default_expiration = "1h"
        
        # Deployment configuration
        self.source_url = None
        self.source_dir = "./app"
        self.deployment_method = "source"
        self.version_id = None
        self.traffic_allocation = {}
        
        # Service configuration
        self.services = []
        self.default_service = True
        
        # Security configuration
        self.login = "optional"  # optional, required, admin
        self.secure = "optional"  # always, never, optional
        self.auth_fail_action = "redirect"
        
        # Features
        self.static_files = []
        self.libraries = []
        self.skip_files = []
        self.error_handlers = []
        
        # State tracking
        self.app_exists = False
        self.app_created = False
        self.app_deployed = False
        self.deployment_status = None
        
        # Labels and metadata
        self.app_labels = {}
        self.app_annotations = {}
        
        # Cost tracking
        self.estimated_monthly_cost = "$0.00/month"
        
    def _initialize_managers(self):
        """Initialize App Engine specific managers"""
        self.app_engine_admin = None
        
    def _post_authentication_setup(self):
        """Setup managers after authentication"""
        try:
            from google.cloud import appengine_admin_v1
            
            self.app_engine_admin = appengine_admin_v1.ApplicationsClient()
            
            # Set project ID from GCP client if available
            if hasattr(self.gcp_client, 'project'):
                self.project_id = self.gcp_client.project
                self.app_id = self.gcp_client.project
                
        except Exception as e:
            print(f"⚠️  App Engine setup note: {str(e)}")
            
    def _validate_runtime(self, runtime: str) -> bool:
        """Validate if runtime is supported by App Engine"""
        supported_runtimes = [
            "python39", "python38", "python37",
            "java11", "java8",
            "nodejs16", "nodejs14", "nodejs12",
            "go116", "go115", "go114",
            "php74", "php73",
            "ruby27", "ruby26",
            "dotnet3",
            "custom"
        ]
        return runtime in supported_runtimes
        
    def _validate_location(self, location: str) -> bool:
        """Validate if location is valid for App Engine"""
        valid_locations = [
            "us-central", "us-west2", "us-east1", "us-east4",
            "europe-west", "europe-west2", "europe-west3",
            "asia-northeast1", "asia-south1", "australia-southeast1",
            "southamerica-east1"
        ]
        return location in valid_locations
        
    def _validate_instance_class(self, instance_class: str) -> bool:
        """Validate if instance class is valid"""
        valid_classes = [
            "F1", "F2", "F4", "F4_1G",  # Automatic scaling
            "B1", "B2", "B4", "B4_1G", "B8",  # Basic and manual scaling
        ]
        return instance_class in valid_classes
        
    def _get_app_type_from_config(self) -> str:
        """Determine application type from configuration"""
        # Check by runtime
        if self.runtime.startswith("python"):
            return "python_app"
        elif self.runtime.startswith("java"):
            return "java_app"
        elif self.runtime.startswith("nodejs"):
            return "nodejs_app"
        elif self.runtime.startswith("go"):
            return "go_app"
        elif self.runtime.startswith("php"):
            return "php_app"
        elif self.runtime.startswith("ruby"):
            return "ruby_app"
        elif self.runtime.startswith("dotnet"):
            return "dotnet_app"
        elif self.runtime == "custom":
            return "custom_app"
            
        # Check by service patterns
        if len(self.services) > 1:
            return "microservices_app"
        elif self.default_service:
            return "web_app"
        else:
            return "service_app"
            
    def _estimate_app_engine_cost(self) -> float:
        """Estimate monthly cost for App Engine"""
        # App Engine pricing (simplified)
        
        # Standard environment pricing
        if self.instance_class.startswith("F"):
            # Frontend instances - based on instance hours
            instance_hours_per_month = 730  # Assuming always running for estimation
            
            instance_costs = {
                "F1": 0.05,   # $0.05/hour
                "F2": 0.10,   # $0.10/hour 
                "F4": 0.30,   # $0.30/hour
                "F4_1G": 0.30
            }
            
            hourly_cost = instance_costs.get(self.instance_class, 0.05)
            instance_cost = hourly_cost * instance_hours_per_month
            
        else:
            # Basic/Manual scaling instances
            instance_costs = {
                "B1": 0.05,
                "B2": 0.10,
                "B4": 0.20,
                "B4_1G": 0.20,
                "B8": 0.40
            }
            
            hourly_cost = instance_costs.get(self.instance_class, 0.05)
            # Assume 50% utilization for basic scaling
            instance_cost = hourly_cost * instance_hours_per_month * 0.5
            
        # Outbound data transfer (first 1GB free per day = ~30GB/month)
        estimated_outbound_gb = 10  # 10GB estimated
        free_outbound_gb = 30
        outbound_cost_per_gb = 0.12
        
        if estimated_outbound_gb > free_outbound_gb:
            outbound_cost = (estimated_outbound_gb - free_outbound_gb) * outbound_cost_per_gb
        else:
            outbound_cost = 0.0
            
        # Cloud Datastore operations (if using)
        if self.database_type == "CLOUD_DATASTORE_COMPATIBILITY":
            # Assume moderate usage - 100K entity reads, 10K writes per month
            entity_reads = 100_000
            entity_writes = 10_000
            
            # First 50K reads and 20K writes are free per day (~1.5M reads, 600K writes per month)
            free_reads_monthly = 1_500_000
            free_writes_monthly = 600_000
            
            read_cost = max(0, entity_reads - free_reads_monthly) * 0.036 / 100_000
            write_cost = max(0, entity_writes - free_writes_monthly) * 0.180 / 100_000
            
            datastore_cost = read_cost + write_cost
        else:
            datastore_cost = 0.0
            
        total_cost = instance_cost + outbound_cost + datastore_cost
        
        # Most apps with light usage stay in free tier
        if total_cost < 2.0:
            total_cost = 0.0
            
        return total_cost
        
    def _fetch_current_app_state(self) -> Dict[str, Any]:
        """Fetch current state of App Engine application"""
        try:
            if not self.app_engine_admin or not self.project_id:
                return {
                    "exists": False,
                    "app_name": self.app_name,
                    "error": "App Engine admin client not initialized or no project ID"
                }
                
            # Get application info
            from google.cloud import appengine_admin_v1
            
            try:
                request = appengine_admin_v1.GetApplicationRequest(
                    name=f"apps/{self.project_id}"
                )
                
                application = self.app_engine_admin.get_application(request=request)
                
                return {
                    "exists": True,
                    "app_name": self.app_name,
                    "app_id": application.id,
                    "name": application.name,
                    "location_id": application.location_id,
                    "serving_status": application.serving_status.name,
                    "database_type": application.database_type.name,
                    "dispatch_rules": len(application.dispatch_rules),
                    "default_hostname": application.default_hostname,
                    "default_bucket": application.default_bucket,
                    "iap": bool(application.iap)
                }
                
            except Exception as e:
                if "does not contain an App Engine application" in str(e):
                    return {
                        "exists": False,
                        "app_name": self.app_name,
                        "project_id": self.project_id,
                        "reason": "No App Engine application found in project"
                    }
                else:
                    return {
                        "exists": False,
                        "app_name": self.app_name,
                        "error": str(e)
                    }
                    
        except Exception as e:
            return {
                "exists": False,
                "app_name": self.app_name,
                "error": str(e)
            }
            
    def _discover_existing_services(self) -> Dict[str, Dict[str, Any]]:
        """Discover existing App Engine services"""
        existing_services = {}
        
        try:
            if not self.app_engine_admin or not self.project_id:
                return existing_services
                
            from google.cloud import appengine_admin_v1
            
            # List services
            request = appengine_admin_v1.ListServicesRequest(
                parent=f"apps/{self.project_id}"
            )
            
            services = self.app_engine_admin.list_services(request=request)
            
            for service in services:
                service_info = {
                    "service_id": service.id,
                    "service_name": service.name,
                    "split": dict(service.split.allocations) if service.split else {},
                    "network_settings": {
                        "ingress_traffic_allowed": service.network_settings.ingress_traffic_allowed.name if service.network_settings else "INGRESS_TRAFFIC_ALLOWED_ALL"
                    }
                }
                
                # Get versions for this service
                try:
                    versions_request = appengine_admin_v1.ListVersionsRequest(
                        parent=f"apps/{self.project_id}/services/{service.id}"
                    )
                    
                    versions = self.app_engine_admin.list_versions(request=versions_request)
                    version_list = []
                    
                    for version in versions:
                        version_info = {
                            "version_id": version.id,
                            "serving_status": version.serving_status.name,
                            "runtime": version.runtime,
                            "env": version.env,
                            "instance_class": version.instance_class,
                            "automatic_scaling": bool(version.automatic_scaling),
                            "basic_scaling": bool(version.basic_scaling),
                            "manual_scaling": bool(version.manual_scaling),
                            "created_by": version.created_by,
                            "create_time": version.create_time,
                            "disk_usage_bytes": version.disk_usage_bytes
                        }
                        version_list.append(version_info)
                        
                    service_info["versions"] = version_list
                    service_info["version_count"] = len(version_list)
                    
                except Exception as ve:
                    service_info["versions"] = []
                    service_info["version_error"] = str(ve)
                    
                existing_services[service.id] = service_info
                
        except Exception as e:
            print(f"⚠️  Failed to discover existing services: {str(e)}")
            
        return existing_services