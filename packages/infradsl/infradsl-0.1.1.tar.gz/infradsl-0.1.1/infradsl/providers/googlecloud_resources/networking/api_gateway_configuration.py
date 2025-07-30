"""
GCP API Gateway Configuration Mixin

Chainable configuration methods for Google Cloud API Gateway.
Provides Rails-like method chaining for fluent API configuration.
"""

from typing import Dict, Any, List, Optional, Union


class APIGatewayConfigurationMixin:
    """
    Mixin for API Gateway configuration methods.
    
    This mixin provides chainable configuration methods for:
    - Route configuration and HTTP methods
    - Backend integration (Cloud Functions, Cloud Run, external)
    - Authentication and security settings
    - CORS and API key management
    - Common API patterns and architectures
    """
    
    def description(self, description: str):
        """Set gateway description"""
        self.gateway_description = description
        self.openapi_spec["info"]["description"] = description
        return self
        
    def display_name(self, name: str):
        """Set display name for the gateway"""
        self.display_name = name
        return self
        
    def project(self, project_id: str):
        """Set project ID for API Gateway operations - Rails convenience"""
        self.project_id = project_id
        if self.project_id:
            self.api_resource_name = f"projects/{self.project_id}/locations/{self.gateway_location}/apis/{self.api_id}"
            self.gateway_resource_name = f"projects/{self.project_id}/locations/{self.gateway_location}/gateways/{self.gateway_id}"
            self.config_resource_name = f"projects/{self.project_id}/locations/{self.gateway_location}/gateways/{self.gateway_id}/configs/{self.config_id}"
        return self
        
    def version(self, version: str):
        """Set API version"""
        self.openapi_spec["info"]["version"] = version
        return self
        
    # Route configuration methods
    def route(self, method: str, path: str, backend_type: str, backend_name: str, **config):
        """Add a route to the API"""
        if not self._is_valid_http_method(method):
            print(f"⚠️  Warning: Invalid HTTP method '{method}'")
        if not self._is_valid_route_path(path):
            print(f"⚠️  Warning: Invalid route path '{path}'")
            
        route_config = {
            'method': method.upper(),
            'path': path,
            'backend_type': backend_type,
            'backend_name': backend_name,
            **config
        }
        self.routes.append(route_config)
        return self
        
    def get(self, path: str, backend_type: str, backend_name: str, **config):
        """Add GET route"""
        return self.route("GET", path, backend_type, backend_name, **config)
        
    def post(self, path: str, backend_type: str, backend_name: str, **config):
        """Add POST route"""
        return self.route("POST", path, backend_type, backend_name, **config)
        
    def put(self, path: str, backend_type: str, backend_name: str, **config):
        """Add PUT route"""
        return self.route("PUT", path, backend_type, backend_name, **config)
        
    def delete_route(self, path: str, backend_type: str, backend_name: str, **config):
        """Add DELETE route"""
        return self.route("DELETE", path, backend_type, backend_name, **config)
        
    def patch(self, path: str, backend_type: str, backend_name: str, **config):
        """Add PATCH route"""
        return self.route("PATCH", path, backend_type, backend_name, **config)
        
    def head(self, path: str, backend_type: str, backend_name: str, **config):
        """Add HEAD route"""
        return self.route("HEAD", path, backend_type, backend_name, **config)
        
    def options(self, path: str, backend_type: str, backend_name: str, **config):
        """Add OPTIONS route"""
        return self.route("OPTIONS", path, backend_type, backend_name, **config)
        
    # Backend configuration methods
    def cloud_function_backend(self, function_name: str, project_id: str = None, region: str = "us-central1"):
        """Add Cloud Function backend"""
        project = project_id or self.project_id or "PROJECT_ID"
        self.cloud_function_backends[function_name] = {
            'function_name': function_name,
            'project_id': project,
            'region': region,
            'url': f"https://{region}-{project}.cloudfunctions.net/{function_name}"
        }
        return self
        
    def cloud_run_backend(self, service_name: str, url: str, region: str = "us-central1"):
        """Add Cloud Run backend"""
        self.cloud_run_backends[service_name] = {
            'service_name': service_name,
            'url': url,
            'region': region
        }
        return self
        
    def external_backend(self, backend_name: str, url: str, **config):
        """Add external backend"""
        self.external_backends[backend_name] = {
            'backend_name': backend_name,
            'url': url,
            **config
        }
        return self
        
    def multiple_backends(self, backends: Dict[str, Dict[str, Any]]):
        """Add multiple backends at once"""
        for backend_name, backend_config in backends.items():
            backend_type = backend_config.get('type', 'external')
            if backend_type == 'cloud_function':
                self.cloud_function_backend(
                    backend_name,
                    backend_config.get('project_id'),
                    backend_config.get('region', 'us-central1')
                )
            elif backend_type == 'cloud_run':
                self.cloud_run_backend(
                    backend_name,
                    backend_config['url'],
                    backend_config.get('region', 'us-central1')
                )
            else:
                self.external_backend(backend_name, backend_config['url'], **backend_config)
        return self
        
    # Security and authentication
    def cors(self, enabled: bool = True):
        """Enable/disable CORS"""
        self.cors_enabled = enabled
        return self
        
    def auth(self, enabled: bool = True):
        """Enable/disable authentication"""
        self.auth_enabled = enabled
        return self
        
    def api_key(self, required: bool = True):
        """Require API key"""
        self.api_key_required = required
        return self
        
    def rate_limiting(self, enabled: bool = True, limit: int = None):
        """Enable rate limiting"""
        self.rate_limiting_enabled = enabled
        if limit:
            self.quota_limit = limit
        return self
        
    def quota(self, limit: int):
        """Set quota limit"""
        self.quota_limit = limit
        return self
        
    # Labels and metadata
    def labels(self, labels: Dict[str, str]):
        """Add labels to the gateway"""
        self.gateway_labels.update(labels)
        return self
        
    def label(self, key: str, value: str):
        """Add individual label - Rails convenience"""
        self.gateway_labels[key] = value
        return self
        
    def annotations(self, annotations: Dict[str, str]):
        """Add annotations to the gateway"""
        self.gateway_annotations.update(annotations)
        return self
        
    def annotation(self, key: str, value: str):
        """Add individual annotation - Rails convenience"""
        self.gateway_annotations[key] = value
        return self
        
    # Common API patterns
    def function_api(self, function_name: str, paths: List[str] = None):
        """Rails convenience: API backed by single Cloud Function"""
        self.cloud_function_backend(function_name)
        
        # Add default routes if none specified
        if not paths:
            paths = ["/", "/{proxy+}"]
        
        for path in paths:
            self.get(path, "cloud_function", function_name)
            self.post(path, "cloud_function", function_name)
            self.put(path, "cloud_function", function_name)
            self.delete_route(path, "cloud_function", function_name)
        
        return self.cors()
        
    def rest_api(self, resource_name: str, backend_type: str, backend_name: str):
        """Rails convenience: Complete REST API for a resource"""
        return (self.get(f"/api/{resource_name}", backend_type, backend_name)
                .post(f"/api/{resource_name}", backend_type, backend_name)
                .get(f"/api/{resource_name}/{{id}}", backend_type, backend_name)
                .put(f"/api/{resource_name}/{{id}}", backend_type, backend_name)
                .patch(f"/api/{resource_name}/{{id}}", backend_type, backend_name)
                .delete_route(f"/api/{resource_name}/{{id}}", backend_type, backend_name)
                .cors())
        
    def crud_api(self, resource_name: str, backend_type: str, backend_name: str):
        """Rails convenience: CRUD API - alias for rest_api"""
        return self.rest_api(resource_name, backend_type, backend_name)
        
    def microservice_api(self):
        """Rails convenience: Microservice API with auth"""
        return (self.cors()
                .auth()
                .api_key()
                .rate_limiting()
                .label("type", "microservice"))
        
    def public_api(self):
        """Rails convenience: Public API without auth"""
        return (self.cors()
                .rate_limiting()
                .label("type", "public"))
        
    def internal_api(self):
        """Rails convenience: Internal API with auth"""
        return (self.auth()
                .api_key()
                .label("type", "internal"))
        
    def webhook_api(self, function_name: str):
        """Rails convenience: Webhook API"""
        return (self.cloud_function_backend(function_name)
                .post("/webhook", "cloud_function", function_name)
                .post("/webhook/{type}", "cloud_function", function_name)
                .label("type", "webhook"))
        
    def graphql_api(self, backend_type: str, backend_name: str):
        """Rails convenience: GraphQL API"""
        return (self.post("/graphql", backend_type, backend_name)
                .get("/graphql", backend_type, backend_name)  # For GraphQL playground
                .cors()
                .label("type", "graphql"))
        
    def proxy_api(self, backend_url: str):
        """Rails convenience: Simple proxy API"""
        return (self.external_backend("proxy", backend_url)
                .get("/{proxy+}", "external", "proxy")
                .post("/{proxy+}", "external", "proxy")
                .put("/{proxy+}", "external", "proxy")
                .delete_route("/{proxy+}", "external", "proxy")
                .cors()
                .label("type", "proxy"))
        
    # Multi-service patterns
    def microservices_gateway(self, services: Dict[str, Dict[str, Any]]):
        """Rails convenience: Gateway for multiple microservices"""
        for service_name, service_config in services.items():
            backend_type = service_config['type']
            backend_name = service_config['name']
            prefix = service_config.get('prefix', f'/{service_name}')
            
            if backend_type == 'cloud_function':
                self.cloud_function_backend(backend_name)
            elif backend_type == 'cloud_run':
                self.cloud_run_backend(backend_name, service_config['url'])
            
            # Add routes for this service
            self.get(f"{prefix}/{{proxy+}}", backend_type, backend_name)
            self.post(f"{prefix}/{{proxy+}}", backend_type, backend_name)
            self.put(f"{prefix}/{{proxy+}}", backend_type, backend_name)
            self.delete_route(f"{prefix}/{{proxy+}}", backend_type, backend_name)
        
        return (self.microservice_api()
                .label("pattern", "microservices_gateway"))
        
    def api_aggregator(self, apis: Dict[str, str]):
        """Rails convenience: API aggregator pattern"""
        for path_prefix, backend_url in apis.items():
            backend_name = f"api_{path_prefix.replace('/', '_')}"
            self.external_backend(backend_name, backend_url)
            self.get(f"{path_prefix}/{{proxy+}}", "external", backend_name)
            self.post(f"{path_prefix}/{{proxy+}}", "external", backend_name)
            self.put(f"{path_prefix}/{{proxy+}}", "external", backend_name)
            self.delete_route(f"{path_prefix}/{{proxy+}}", "external", backend_name)
        
        return (self.cors()
                .auth()
                .rate_limiting()
                .label("pattern", "api_aggregator"))
        
    # Environment-specific configurations
    def development(self):
        """Configure for development environment - Rails convention"""
        return (self.cors()
                .label("environment", "development")
                .label("debug", "enabled"))
                
    def staging(self):
        """Configure for staging environment - Rails convention"""
        return (self.cors()
                .auth()
                .rate_limiting()
                .label("environment", "staging")
                .label("testing", "enabled"))
                
    def production(self):
        """Configure for production environment - Rails convention"""
        return (self.cors()
                .auth()
                .api_key()
                .rate_limiting()
                .label("environment", "production")
                .label("monitoring", "enabled"))
        
    # Security patterns
    def high_security(self):
        """Configure for high security requirements"""
        return (self.auth()
                .api_key()
                .rate_limiting(True, 1000)  # 1000 requests limit
                .label("security", "high")
                .label("compliance", "required"))
        
    def compliance_ready(self):
        """Configure for compliance requirements"""
        return (self.high_security()
                .label("compliance", "sox_pci")
                .label("audit", "required")
                .label("encryption", "required"))
        
    def enterprise_grade(self):
        """Configure for enterprise requirements"""
        return (self.production()
                .high_security()
                .compliance_ready()
                .label("tier", "enterprise"))
        
    # Industry-specific patterns
    def ecommerce_api(self, payment_service: str, inventory_service: str):
        """Rails convenience: E-commerce API gateway"""
        return (self.microservices_gateway({
                    "payments": {"type": "cloud_function", "name": payment_service, "prefix": "/api/payments"},
                    "inventory": {"type": "cloud_function", "name": inventory_service, "prefix": "/api/inventory"},
                    "orders": {"type": "cloud_function", "name": "orders-service", "prefix": "/api/orders"}
                })
                .compliance_ready()
                .label("industry", "ecommerce"))
        
    def fintech_api(self, backend_service: str):
        """Rails convenience: Fintech API gateway"""
        return (self.function_api(backend_service)
                .enterprise_grade()
                .quota(10000)  # Conservative quota for financial services
                .label("industry", "fintech")
                .label("pci_compliant", "true"))
        
    def healthcare_api(self, backend_service: str):
        """Rails convenience: Healthcare API gateway"""
        return (self.function_api(backend_service)
                .enterprise_grade()
                .label("industry", "healthcare")
                .label("hipaa_compliant", "true"))
        
    def iot_api(self, device_service: str, telemetry_service: str):
        """Rails convenience: IoT API gateway"""
        return (self.microservices_gateway({
                    "devices": {"type": "cloud_function", "name": device_service, "prefix": "/api/devices"},
                    "telemetry": {"type": "cloud_function", "name": telemetry_service, "prefix": "/api/telemetry"}
                })
                .api_key()
                .rate_limiting(True, 100000)  # High throughput for IoT
                .label("industry", "iot"))
        
    # Common route patterns
    def health_check(self, backend_type: str = "cloud_function", backend_name: str = "health"):
        """Add health check endpoint"""
        return self.get("/health", backend_type, backend_name)
        
    def status_endpoints(self, backend_type: str = "cloud_function", backend_name: str = "status"):
        """Add common status endpoints"""
        return (self.get("/health", backend_type, backend_name)
                .get("/status", backend_type, backend_name)
                .get("/version", backend_type, backend_name)
                .get("/metrics", backend_type, backend_name))
        
    def api_docs(self, backend_type: str = "cloud_function", backend_name: str = "docs"):
        """Add API documentation endpoints"""
        return (self.get("/docs", backend_type, backend_name)
                .get("/swagger", backend_type, backend_name)
                .get("/openapi.json", backend_type, backend_name))
        
    # Utility methods
    def clear_routes(self):
        """Clear all routes"""
        self.routes = []
        return self
        
    def clear_backends(self):
        """Clear all backends"""
        self.cloud_function_backends = {}
        self.cloud_run_backends = {}
        self.external_backends = {}
        return self
        
    def get_route_count(self) -> int:
        """Get the number of configured routes"""
        return len(self.routes)
        
    def get_backend_count(self) -> int:
        """Get the total number of configured backends"""
        return (len(self.cloud_function_backends) + 
                len(self.cloud_run_backends) + 
                len(self.external_backends))
        
    def get_unique_paths(self) -> List[str]:
        """Get list of unique paths"""
        return list(set(route['path'] for route in self.routes))
        
    def get_methods(self) -> List[str]:
        """Get list of unique HTTP methods"""
        return list(set(route['method'] for route in self.routes))
        
    def has_auth(self) -> bool:
        """Check if authentication is enabled"""
        return self.auth_enabled or self.api_key_required