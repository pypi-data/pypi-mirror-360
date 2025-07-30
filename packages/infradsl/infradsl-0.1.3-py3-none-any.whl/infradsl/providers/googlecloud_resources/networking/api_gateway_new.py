"""
GCP API Gateway Complete Implementation

Complete API Gateway implementation combining core functionality, 
configuration methods, and lifecycle operations into a single modular class.
Rails-like API with Cross-Cloud Magic optimization.
"""

from typing import Dict, Any, List, Optional, Union
from .api_gateway_core import APIGatewayCore
from .api_gateway_configuration import APIGatewayConfigurationMixin
from .api_gateway_lifecycle import APIGatewayLifecycleMixin


class APIGateway(APIGatewayCore, APIGatewayConfigurationMixin, APIGatewayLifecycleMixin):
    """
    Complete Google Cloud API Gateway implementation.
    
    This class combines:
    - APIGatewayCore: Basic gateway attributes and authentication
    - APIGatewayConfigurationMixin: Chainable configuration methods
    - APIGatewayLifecycleMixin: Lifecycle operations (create, destroy, preview)
    
    Features:
    - Rails-like method chaining for fluent API configuration
    - Smart state management and drift detection
    - Cross-Cloud Magic optimization
    - OpenAPI 2.0 specification support
    - Multi-backend support (Cloud Functions, Cloud Run, external APIs)
    - Security features (authentication, API keys, CORS, rate limiting)
    - Common API patterns (REST, GraphQL, microservices, webhooks)
    - Industry-specific configurations (fintech, healthcare, IoT, e-commerce)
    - Environment-specific settings (development, staging, production)
    - Route management and backend integration
    
    Example:
        # Simple function-backed API
        api = APIGateway("my-api")
        api.function_api("my-handler")
        api.create()
        
        # REST API with authentication
        api = APIGateway("rest-api")
        api.rest_api("users", "cloud_function", "users-service")
        api.microservice_api()
        api.create()
        
        # Microservices gateway
        api = APIGateway("microservices-gateway")
        api.microservices_gateway({
            "users": {"type": "cloud_function", "name": "users-service", "prefix": "/api/users"},
            "orders": {"type": "cloud_run", "name": "orders-service", "url": "https://orders.run.app", "prefix": "/api/orders"}
        })
        api.enterprise_grade()
        api.create()
        
        # Industry-specific API
        api = APIGateway("payments-api")
        api.fintech_api("payments-processor")
        api.create()
        
        # Cross-Cloud Magic optimization
        api = APIGateway("optimized-api")
        api.function_api("my-service")
        api.optimize_for("performance")
        api.create()
    """
    
    def __init__(self, name: str):
        """
        Initialize API Gateway with gateway name.
        
        Args:
            name: Gateway name (must be valid GCP gateway name)
        """
        # Initialize all parent classes
        APIGatewayCore.__init__(self, name)
        
        # Ensure proper initialization order
        self._initialize_managers()
        
    def __repr__(self) -> str:
        """String representation of API Gateway instance"""
        backend_count = len(self.cloud_function_backends) + len(self.cloud_run_backends) + len(self.external_backends)
        gateway_type = self._get_gateway_type_from_config()
        status = "configured" if self.routes or backend_count > 0 else "unconfigured"
        
        return (f"APIGateway(name='{self.gateway_name}', "
                f"type='{gateway_type}', "
                f"routes={len(self.routes)}, "
                f"backends={backend_count}, "
                f"location='{self.gateway_location}', "
                f"status='{status}')")
    
    def summary(self) -> Dict[str, Any]:
        """
        Get comprehensive summary of API Gateway configuration.
        
        Returns:
            Dict containing all configuration details
        """
        # Analyze gateway configuration
        gateway_patterns = []
        
        # Detect patterns from routes and backends
        if self.cloud_function_backends:
            gateway_patterns.append("cloud_functions")
        if self.cloud_run_backends:
            gateway_patterns.append("cloud_run")
        if self.external_backends:
            gateway_patterns.append("external_apis")
        
        # Analyze route patterns
        methods = set(route.get('method', 'GET') for route in self.routes)
        paths = set(route.get('path', '/') for route in self.routes)
        
        # Check for API patterns
        if any('/api/' in path for path in paths):
            gateway_patterns.append("rest_api")
        if any('/graphql' in path for path in paths):
            gateway_patterns.append("graphql")
        if any('/webhook' in path for path in paths):
            gateway_patterns.append("webhook")
        
        # Check for common endpoints
        common_endpoints = []
        if any('/health' in path for path in paths):
            common_endpoints.append("health_check")
        if any('/status' in path for path in paths):
            common_endpoints.append("status")
        if any('/docs' in path for path in paths):
            common_endpoints.append("documentation")
        
        summary = {
            "gateway_name": self.gateway_name,
            "api_id": self.api_id,
            "gateway_id": self.gateway_id,
            "display_name": self.display_name,
            "gateway_description": self.gateway_description,
            "gateway_type": self._get_gateway_type_from_config(),
            "gateway_patterns": gateway_patterns,
            
            # Routes and backends
            "routes": self.routes,
            "route_count": len(self.routes),
            "unique_paths": len(paths),
            "http_methods": list(methods),
            "common_endpoints": common_endpoints,
            
            # Backends
            "cloud_function_backends": self.cloud_function_backends,
            "cloud_run_backends": self.cloud_run_backends,
            "external_backends": self.external_backends,
            "backend_count": len(self.cloud_function_backends) + len(self.cloud_run_backends) + len(self.external_backends),
            
            # Security and configuration
            "auth_enabled": self.auth_enabled,
            "api_key_required": self.api_key_required,
            "cors_enabled": self.cors_enabled,
            "rate_limiting_enabled": self.rate_limiting_enabled,
            "quota_limit": self.quota_limit,
            
            # Configuration
            "gateway_location": self.gateway_location,
            "managed_service": self.managed_service,
            "labels": self.gateway_labels,
            "label_count": len(self.gateway_labels),
            "annotations": self.gateway_annotations,
            
            # OpenAPI spec
            "openapi_version": self.openapi_spec.get("swagger", "2.0"),
            "openapi_title": self.openapi_spec.get("info", {}).get("title", self.gateway_name),
            "openapi_version_info": self.openapi_spec.get("info", {}).get("version", "1.0.0"),
            
            # State
            "state": {
                "exists": self.gateway_exists,
                "created": self.gateway_created,
                "resource_name": self.gateway_resource_name,
                "status": self.gateway_status,
                "deployment_status": self.deployment_status,
                "gateway_url": self.gateway_url
            },
            
            # Cost
            "estimated_monthly_cost": f"${self._estimate_api_gateway_cost():.2f}"
        }
        
        return summary
    
    def display_config(self):
        """Display current configuration in human-readable format"""
        print(f"\n🌐 API Gateway Configuration: {self.gateway_name}")
        print(f"   🏷️  Gateway ID: {self.gateway_id}")
        print(f"   📋 API ID: {self.api_id}")
        print(f"   🎯 Display Name: {self.display_name}")
        print(f"   📝 Description: {self.gateway_description}")
        print(f"   📍 Location: {self.gateway_location}")
        print(f"   🏗️  Type: {self._get_gateway_type_from_config().replace('_', ' ').title()}")
        
        # Routes
        if self.routes:
            print(f"\n🛣️  Routes ({len(self.routes)}):")
            methods = set(route.get('method', 'GET') for route in self.routes)
            paths = set(route.get('path', '/') for route in self.routes)
            print(f"   📍 Unique Paths: {len(paths)}")
            print(f"   🔍 HTTP Methods: {', '.join(sorted(methods))}")
            
            # Show route details
            print(f"\n🛣️  Route Details:")
            for i, route in enumerate(self.routes[:10]):  # Show first 10
                method = route.get('method', 'GET')
                path = route.get('path', '/')
                backend = route.get('backend_type', 'function')
                backend_name = route.get('backend_name', 'unknown')
                connector = "├─" if i < min(len(self.routes), 10) - 1 else "└─"
                print(f"   {connector} {method} {path} → {backend}:{backend_name}")
            
            if len(self.routes) > 10:
                print(f"      └─ ... and {len(self.routes) - 10} more routes")
        else:
            print(f"\n🛣️  Routes: None configured")
        
        # Backends
        backend_count = len(self.cloud_function_backends) + len(self.cloud_run_backends) + len(self.external_backends)
        if backend_count > 0:
            print(f"\n⚙️  Backends ({backend_count} total):")
            
            if self.cloud_function_backends:
                print(f"   ⚡ Cloud Functions ({len(self.cloud_function_backends)}):")
                for name, config in list(self.cloud_function_backends.items())[:5]:
                    print(f"      ├─ {name} ({config.get('region', 'us-central1')})")
                if len(self.cloud_function_backends) > 5:
                    print(f"      └─ ... and {len(self.cloud_function_backends) - 5} more")
            
            if self.cloud_run_backends:
                print(f"   🏃 Cloud Run ({len(self.cloud_run_backends)}):")
                for name, config in list(self.cloud_run_backends.items())[:5]:
                    print(f"      ├─ {name} → {config.get('url', 'unknown')}")
                if len(self.cloud_run_backends) > 5:
                    print(f"      └─ ... and {len(self.cloud_run_backends) - 5} more")
            
            if self.external_backends:
                print(f"   🌐 External ({len(self.external_backends)}):")
                for name, config in list(self.external_backends.items())[:5]:
                    print(f"      ├─ {name} → {config.get('url', 'unknown')}")
                if len(self.external_backends) > 5:
                    print(f"      └─ ... and {len(self.external_backends) - 5} more")
        else:
            print(f"\n⚙️  Backends: None configured")
        
        # Security
        print(f"\n🔒 Security Configuration:")
        print(f"   🔐 Authentication: {'✅ Enabled' if self.auth_enabled else '❌ Disabled'}")
        print(f"   🔑 API Key Required: {'✅ Yes' if self.api_key_required else '❌ No'}")
        print(f"   🌍 CORS: {'✅ Enabled' if self.cors_enabled else '❌ Disabled'}")
        print(f"   🚦 Rate Limiting: {'✅ Enabled' if self.rate_limiting_enabled else '❌ Disabled'}")
        if self.quota_limit:
            print(f"   📊 Quota Limit: {self.quota_limit:,} requests")
        
        # Labels
        if self.gateway_labels:
            print(f"\n🏷️  Labels ({len(self.gateway_labels)}):")
            for key, value in list(self.gateway_labels.items())[:5]:
                print(f"   • {key}: {value}")
            if len(self.gateway_labels) > 5:
                print(f"   • ... and {len(self.gateway_labels) - 5} more")
        
        # OpenAPI spec
        print(f"\n📋 OpenAPI Specification:")
        print(f"   📊 Version: {self.openapi_spec.get('swagger', '2.0')}")
        print(f"   🎯 Title: {self.openapi_spec.get('info', {}).get('title', self.gateway_name)}")
        print(f"   🔢 API Version: {self.openapi_spec.get('info', {}).get('version', '1.0.0')}")
        print(f"   📍 Paths: {len(self.openapi_spec.get('paths', {}))}")
        
        # Cost
        print(f"\n💰 Estimated Cost: ${self._estimate_api_gateway_cost():.2f}/month")
        
        # State
        if self.gateway_exists:
            print(f"\n📊 State:")
            print(f"   ✅ Exists: {self.gateway_exists}")
            print(f"   🆔 Resource: {self.gateway_resource_name}")
            if self.gateway_status:
                print(f"   📊 Status: {self.gateway_status}")
            if self.gateway_url:
                print(f"   🌐 URL: {self.gateway_url}")
    
    def analyze_security(self) -> Dict[str, Any]:
        """
        Analyze API Gateway security configuration and provide recommendations.
        
        Returns:
            Dict containing security analysis and recommendations
        """
        analysis = {
            "security_score": 0,
            "max_score": 100,
            "recommendations": [],
            "security_features": [],
            "risk_factors": []
        }
        
        # Authentication analysis
        if self.auth_enabled:
            analysis["security_score"] += 25
            analysis["security_features"].append("Authentication enabled")
        else:
            analysis["risk_factors"].append("No authentication required")
            analysis["recommendations"].append("Enable authentication for better security")
        
        # API key analysis
        if self.api_key_required:
            analysis["security_score"] += 20
            analysis["security_features"].append("API key required")
        else:
            analysis["recommendations"].append("Consider requiring API keys for access control")
        
        # Rate limiting analysis
        if self.rate_limiting_enabled:
            analysis["security_score"] += 20
            analysis["security_features"].append("Rate limiting enabled")
            if self.quota_limit and self.quota_limit < 10000:
                analysis["security_features"].append("Conservative quota limit set")
                analysis["security_score"] += 5
        else:
            analysis["risk_factors"].append("No rate limiting")
            analysis["recommendations"].append("Enable rate limiting to prevent abuse")
        
        # CORS analysis
        if self.cors_enabled:
            analysis["security_score"] += 10
            analysis["security_features"].append("CORS configured")
        else:
            analysis["recommendations"].append("Configure CORS for web client security")
        
        # Backend security analysis
        external_count = len(self.external_backends)
        if external_count == 0:
            analysis["security_score"] += 15
            analysis["security_features"].append("All backends are GCP-native")
        else:
            analysis["risk_factors"].append(f"{external_count} external backends")
            analysis["recommendations"].append("Review external backend security")
        
        # Labels analysis
        security_labels = ["security", "compliance", "audit", "encryption"]
        for label in security_labels:
            if label in self.gateway_labels:
                analysis["security_score"] += 2
                analysis["security_features"].append(f"Security label: {label}")
        
        # Environment analysis
        env_label = self.gateway_labels.get("environment", "").lower()
        if env_label == "production":
            if self.auth_enabled and self.api_key_required:
                analysis["security_score"] += 5
                analysis["security_features"].append("Production environment with security")
            else:
                analysis["risk_factors"].append("Production environment without full security")
        
        return analysis
    
    def analyze_performance(self) -> Dict[str, Any]:
        """
        Analyze API Gateway performance configuration and provide recommendations.
        
        Returns:
            Dict containing performance analysis and recommendations
        """
        analysis = {
            "performance_score": 0,
            "max_score": 100,
            "recommendations": [],
            "performance_factors": [],
            "latency_factors": []
        }
        
        # Location analysis
        if self.gateway_location == "global":
            analysis["performance_score"] += 25
            analysis["performance_factors"].append("Global deployment for worldwide performance")
        else:
            analysis["performance_score"] += 15
            analysis["recommendations"].append("Consider global deployment for better performance")
        
        # Backend type analysis
        cf_count = len(self.cloud_function_backends)
        cr_count = len(self.cloud_run_backends)
        ext_count = len(self.external_backends)
        
        if cf_count > 0:
            analysis["performance_score"] += 20
            analysis["performance_factors"].append(f"Cloud Functions backends ({cf_count}) for serverless scaling")
        
        if cr_count > 0:
            analysis["performance_score"] += 25
            analysis["performance_factors"].append(f"Cloud Run backends ({cr_count}) for containerized performance")
        
        if ext_count > 0:
            analysis["latency_factors"].append(f"External backends ({ext_count}) may add latency")
            analysis["recommendations"].append("Monitor external backend response times")
        
        # Route complexity analysis
        route_count = len(self.routes)
        if route_count <= 50:
            analysis["performance_score"] += 15
        elif route_count <= 200:
            analysis["performance_score"] += 10
            analysis["performance_factors"].append("Moderate route complexity")
        else:
            analysis["performance_score"] += 5
            analysis["latency_factors"].append(f"High route count ({route_count}) may impact routing performance")
        
        # CORS analysis
        if self.cors_enabled:
            analysis["performance_score"] += 10
            analysis["performance_factors"].append("CORS enabled for web client performance")
        
        # Authentication analysis
        if self.auth_enabled or self.api_key_required:
            analysis["performance_score"] += 5
            analysis["latency_factors"].append("Authentication adds small latency overhead")
        
        return analysis
    
    # Utility methods for backwards compatibility
    def get_api_gateway_client(self):
        """Get API Gateway client - backwards compatibility"""
        return self.api_gateway_client
    
    def _estimate_monthly_cost(self) -> str:
        """Get estimated monthly cost for backwards compatibility"""
        return f"${self._estimate_api_gateway_cost():.2f}/month"
    
    def _get_gateway_info(self) -> Dict[str, Any]:
        """Get gateway info for backwards compatibility"""
        return self.summary()


# Convenience function for creating API Gateway instances
def create_api_gateway(name: str) -> APIGateway:
    """
    Create a new API Gateway instance.
    
    Args:
        name: Gateway name
        
    Returns:
        APIGateway instance
    """
    return APIGateway(name)


# Export the class for easy importing
__all__ = ['APIGateway', 'create_api_gateway']