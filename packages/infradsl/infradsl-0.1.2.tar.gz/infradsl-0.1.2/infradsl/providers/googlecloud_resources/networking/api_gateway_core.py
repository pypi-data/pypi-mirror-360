"""
GCP API Gateway Core Implementation

Core attributes and authentication for Google Cloud API Gateway.
Provides the foundation for the modular API management system.
"""

from typing import Dict, Any, List, Optional, Union
from ..base_resource import BaseGcpResource


class APIGatewayCore(BaseGcpResource):
    """
    Core class for Google Cloud API Gateway functionality.
    
    This class provides:
    - Basic API Gateway attributes and configuration
    - Authentication setup
    - Common utilities for API operations
    - Validation and state tracking foundations
    """
    
    def __init__(self, name: str):
        """Initialize API Gateway core with gateway name"""
        super().__init__(name)
        
        # Core gateway attributes
        self.gateway_name = name
        self.api_id = name
        self.gateway_id = f"{name}-gateway"
        self.config_id = f"{name}-config"
        self.display_name = name
        self.gateway_description = f"API Gateway for {name}"
        
        # Resource names
        self.api_resource_name = None
        self.gateway_resource_name = None
        self.config_resource_name = None
        self.gateway_url = None
        self.managed_service_name = None
        
        # OpenAPI specification
        self.openapi_spec = {
            "swagger": "2.0",
            "info": {
                "title": name,
                "description": self.gateway_description,
                "version": "1.0.0"
            },
            "produces": ["application/json"],
            "schemes": ["https"],
            "paths": {},
            "x-google-backend": {}
        }
        
        # Routes and backends
        self.routes = []
        self.cloud_function_backends = {}
        self.cloud_run_backends = {}
        self.external_backends = {}
        
        # Authentication and security
        self.auth_enabled = False
        self.api_key_required = False
        self.cors_enabled = True
        self.rate_limiting_enabled = False
        self.quota_limit = None
        
        # Configuration
        self.gateway_location = "global"
        self.managed_service = True
        self.gateway_labels = {}
        self.gateway_annotations = {}
        
        # State tracking
        self.gateway_exists = False
        self.gateway_created = False
        self.gateway_status = None
        self.deployment_status = None
        
        # Client reference
        self.api_gateway_client = None
        
        # Estimated costs
        self.estimated_monthly_cost = "$3.00/month"
        
    def _initialize_managers(self):
        """Initialize API Gateway-specific managers"""
        self.api_gateway_client = None
        
    def _post_authentication_setup(self):
        """Setup managers after authentication"""
        try:
            from google.cloud import apigateway_v1
            
            # Initialize client
            self.api_gateway_client = apigateway_v1.ApiGatewayServiceClient(
                credentials=self.gcp_client.credentials
            )
            
            # Set project context
            self.project_id = self.project_id or self.gcp_client.project_id
            
            # Generate resource names
            if self.project_id:
                self.api_resource_name = f"projects/{self.project_id}/locations/{self.gateway_location}/apis/{self.api_id}"
                self.gateway_resource_name = f"projects/{self.project_id}/locations/{self.gateway_location}/gateways/{self.gateway_id}"
                self.config_resource_name = f"projects/{self.project_id}/locations/{self.gateway_location}/gateways/{self.gateway_id}/configs/{self.config_id}"
                
        except Exception as e:
            print(f"⚠️  Failed to initialize API Gateway client: {str(e)}")
            
    def _is_valid_gateway_name(self, name: str) -> bool:
        """Check if gateway name is valid"""
        import re
        # Gateway names must contain only letters, numbers, dashes
        pattern = r'^[a-z][a-z0-9-]*[a-z0-9]$'
        return bool(re.match(pattern, name)) and 1 <= len(name) <= 63
        
    def _is_valid_route_path(self, path: str) -> bool:
        """Check if route path is valid"""
        # Basic path validation
        return path.startswith('/') and len(path) <= 1000
        
    def _is_valid_http_method(self, method: str) -> bool:
        """Check if HTTP method is valid"""
        valid_methods = ["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"]
        return method.upper() in valid_methods
        
    def _validate_gateway_config(self, config: Dict[str, Any]) -> bool:
        """Validate gateway configuration"""
        required_fields = ["gateway_name"]
        
        for field in required_fields:
            if field not in config or not config[field]:
                return False
                
        # Validate gateway name format
        if not self._is_valid_gateway_name(config["gateway_name"]):
            return False
            
        # Validate routes if provided
        routes = config.get("routes", [])
        for route in routes:
            if not route.get("path") or not self._is_valid_route_path(route["path"]):
                return False
            if not route.get("method") or not self._is_valid_http_method(route["method"]):
                return False
            if not route.get("backend_type") or not route.get("backend_name"):
                return False
                
        return True
        
    def _get_gateway_type_from_config(self) -> str:
        """Determine gateway type from configuration"""
        if not self.routes:
            return "empty"
        
        backend_types = set(route.get("backend_type", "") for route in self.routes)
        
        if "cloud_function" in backend_types and len(backend_types) == 1:
            return "functions_only"
        elif "cloud_run" in backend_types and len(backend_types) == 1:
            return "cloud_run_only"
        elif len(backend_types) > 1:
            return "multi_backend"
        elif "external" in backend_types:
            return "external_backend"
        else:
            return "custom"
            
    def _estimate_api_gateway_cost(self) -> float:
        """Estimate monthly cost for API Gateway usage"""
        # API Gateway pricing (simplified)
        
        # Base cost: $3.00 per million API calls
        estimated_monthly_calls = 100000  # 100K calls default
        api_call_cost = (estimated_monthly_calls / 1000000) * 3.00
        
        # Data transfer: $0.09 per GB (first 1GB free)
        estimated_data_gb = 5  # 5GB default
        data_transfer_cost = max(0, (estimated_data_gb - 1) * 0.09)
        
        # Route complexity multiplier
        route_count = len(self.routes)
        if route_count > 50:
            api_call_cost *= 1.1  # Slight increase for complex APIs
        
        # Backend type considerations
        if self.cloud_function_backends:
            # Cloud Functions have their own costs
            pass
        if self.cloud_run_backends:
            # Cloud Run has its own costs
            pass
        
        total_cost = api_call_cost + data_transfer_cost
        
        # Minimum charge
        if total_cost < 0.30:
            total_cost = 0.30
            
        return total_cost
        
    def _fetch_current_cloud_state(self) -> Dict[str, Any]:
        """Fetch current state of API Gateway from Google Cloud"""
        self._ensure_authenticated()
        
        try:
            # Check if gateway exists
            try:
                gateway = self.api_gateway_client.get_gateway(name=self.gateway_resource_name)
                gateway_exists = True
            except Exception:
                gateway_exists = False
                
            if not gateway_exists:
                return {
                    "exists": False,
                    "gateway_name": self.gateway_name,
                    "gateway_resource_name": self.gateway_resource_name
                }
                
            # Get gateway details
            current_state = {
                "exists": True,
                "gateway_name": self.gateway_name,
                "gateway_resource_name": gateway.name,
                "display_name": gateway.display_name,
                "labels": dict(gateway.labels) if gateway.labels else {},
                "create_time": gateway.create_time.isoformat() if hasattr(gateway, 'create_time') else None,
                "update_time": gateway.update_time.isoformat() if hasattr(gateway, 'update_time') else None,
                "state": str(gateway.state).replace('State.', '') if hasattr(gateway, 'state') else 'UNKNOWN',
                "default_hostname": gateway.default_hostname if hasattr(gateway, 'default_hostname') else None,
                "gateway_url": f"https://{gateway.default_hostname}" if hasattr(gateway, 'default_hostname') and gateway.default_hostname else None,
                "api_config": gateway.api_config if hasattr(gateway, 'api_config') else None,
                "routes": [],
                "route_count": 0,
                "backend_count": 0,
                "methods": [],
                "paths": []
            }
            
            # Get API Config details if available
            if current_state["api_config"]:
                try:
                    api_config = self.api_gateway_client.get_api_config(name=current_state["api_config"])
                    
                    # Parse OpenAPI spec if available
                    if hasattr(api_config, 'openapi_documents'):
                        for doc in api_config.openapi_documents:
                            if hasattr(doc, 'document') and hasattr(doc.document, 'contents'):
                                try:
                                    import json
                                    import yaml
                                    
                                    spec_content = doc.document.contents.decode('utf-8')
                                    if spec_content.strip().startswith('{'):
                                        spec = json.loads(spec_content)
                                    else:
                                        spec = yaml.safe_load(spec_content)
                                    
                                    # Extract paths and routes
                                    if 'paths' in spec:
                                        routes = []
                                        methods = set()
                                        paths = set()
                                        
                                        for path, path_methods in spec['paths'].items():
                                            paths.add(path)
                                            for method, operation in path_methods.items():
                                                if isinstance(operation, dict):
                                                    methods.add(method.upper())
                                                    routes.append({
                                                        'method': method.upper(),
                                                        'path': path,
                                                        'operation_id': operation.get('operationId', 'unknown')
                                                    })
                                        
                                        current_state["routes"] = routes
                                        current_state["route_count"] = len(routes)
                                        current_state["methods"] = list(methods)
                                        current_state["paths"] = list(paths)
                                    
                                    # Count backends
                                    if 'x-google-backend' in spec:
                                        current_state["backend_count"] = len(spec['x-google-backend'])
                                    
                                except Exception as e:
                                    print(f"⚠️  Warning: Failed to parse OpenAPI spec: {str(e)}")
                                    
                except Exception as e:
                    print(f"⚠️  Warning: Failed to get API config details: {str(e)}")
            
            return current_state
            
        except Exception as e:
            print(f"⚠️  Warning: Failed to fetch API Gateway state: {str(e)}")
            return {
                "exists": False,
                "gateway_name": self.gateway_name,
                "gateway_resource_name": self.gateway_resource_name,
                "error": str(e)
            }
            
    def _discover_existing_gateways(self) -> Dict[str, Dict[str, Any]]:
        """Discover all existing gateways in the project"""
        existing_gateways = {}
        
        try:
            parent = f"projects/{self.project_id}/locations/{self.gateway_location}"
            
            # List all gateways in the location
            gateways = self.api_gateway_client.list_gateways(parent=parent)
            
            for gateway in gateways:
                gateway_name = gateway.name.split('/')[-1]
                
                try:
                    # Get basic gateway information
                    gateway_info = {
                        "gateway_name": gateway_name,
                        "full_name": gateway.name,
                        "display_name": gateway.display_name,
                        "labels": dict(gateway.labels) if gateway.labels else {},
                        "create_time": gateway.create_time.isoformat() if hasattr(gateway, 'create_time') else None,
                        "state": str(gateway.state).replace('State.', '') if hasattr(gateway, 'state') else 'UNKNOWN',
                        "default_hostname": gateway.default_hostname if hasattr(gateway, 'default_hostname') else None,
                        "gateway_url": f"https://{gateway.default_hostname}" if hasattr(gateway, 'default_hostname') and gateway.default_hostname else None,
                        "api_config": gateway.api_config if hasattr(gateway, 'api_config') else None,
                        "routes": [],
                        "route_count": 0,
                        "backend_count": 0
                    }
                    
                    # Get additional details from API config if available
                    if gateway_info["api_config"]:
                        try:
                            api_config = self.api_gateway_client.get_api_config(name=gateway_info["api_config"])
                            
                            # Basic route counting from OpenAPI spec
                            if hasattr(api_config, 'openapi_documents'):
                                route_count = 0
                                for doc in api_config.openapi_documents:
                                    if hasattr(doc, 'document'):
                                        # Estimate route count (would need full parsing for exact count)
                                        route_count += 10  # Rough estimate
                                gateway_info["route_count"] = route_count
                                
                        except Exception:
                            # Ignore errors in detailed parsing
                            pass
                    
                    existing_gateways[gateway_name] = gateway_info
                    
                except Exception as e:
                    print(f"⚠️  Failed to get details for gateway {gateway_name}: {str(e)}")
                    existing_gateways[gateway_name] = {
                        "gateway_name": gateway_name,
                        "error": str(e)
                    }
                    
        except Exception as e:
            print(f"⚠️  Failed to discover existing gateways: {str(e)}")
            
        return existing_gateways