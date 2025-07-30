"""
Google App Engine Complete Implementation

Complete Google App Engine implementation combining core functionality,
configuration methods, and lifecycle operations into a single modular class.
Rails-like API with Cross-Cloud Magic optimization.
"""

from typing import Dict, Any, List, Optional, Union
from .app_engine_core import AppEngineCore
from .app_engine_configuration import AppEngineConfigurationMixin
from .app_engine_lifecycle import AppEngineLifecycleMixin


class AppEngine(AppEngineCore, AppEngineConfigurationMixin, AppEngineLifecycleMixin):
    """
    Complete Google App Engine implementation.
    
    This class combines:
    - AppEngineCore: Basic App Engine attributes and authentication
    - AppEngineConfigurationMixin: Chainable configuration methods
    - AppEngineLifecycleMixin: Lifecycle operations (create, destroy, preview)
    
    Features:
    - Rails-like method chaining for fluent App Engine configuration
    - Smart state management and version control
    - Cross-Cloud Magic optimization
    - Platform as a Service (PaaS) deployment
    - Multiple runtime support (Python, Java, Node.js, Go, PHP, Ruby, .NET)
    - Automatic scaling and load balancing
    - Framework-specific configurations (Flask, Django, Express, Spring Boot)
    - Service and version management
    - Environment-specific settings (development, staging, production)
    
    Example:
        # Flask web application
        app = AppEngine("my-web-app")
        app.project("my-project").flask_app()
        app.create()
        
        # Django application with auto-scaling
        django_app = AppEngine("django-site")
        django_app.project("my-project").django_app()
        django_app.automatic_scaling(min_instances=2, max_instances=20)
        django_app.production()
        django_app.create()
        
        # Node.js API service
        api = AppEngine("api-service")
        api.project("my-project").express_app()
        api.api_application().https_only()
        api.create()
        
        # Java Spring Boot microservice
        service = AppEngine("user-service")
        service.project("my-project").spring_boot_app()
        service.microservice("users")
        service.create()
        
        # Background worker
        worker = AppEngine("task-worker")
        worker.project("my-project").python()
        worker.background_worker().manual_scaling(3)
        worker.create()
        
        # Static website
        site = AppEngine("portfolio")
        site.project("my-project").static_website()
        site.static_files("/*", "public/")
        site.create()
        
        # Custom runtime with Dockerfile
        custom = AppEngine("custom-app")
        custom.project("my-project").custom_runtime()
        custom.dockerfile_deployment()
        custom.create()
        
        # Cross-Cloud Magic optimization
        optimized = AppEngine("optimized-app")
        optimized.project("my-project").web_application()
        optimized.optimize_for("performance")
        optimized.create()
    """
    
    def __init__(self, name: str):
        """
        Initialize Google App Engine with application name.
        
        Args:
            name: App Engine application name
        """
        # Initialize all parent classes
        AppEngineCore.__init__(self, name)
        
        # Ensure proper initialization order
        self._initialize_managers()
        
    def __repr__(self) -> str:
        """String representation of App Engine instance"""
        app_type = self._get_app_type_from_config()
        scaling_type = self._get_scaling_type()
        status = "configured" if self.project_id else "unconfigured"
        
        return (f"AppEngine(name='{self.app_name}', "
                f"type='{app_type}', "
                f"runtime='{self.runtime}', "
                f"scaling='{scaling_type}', "
                f"project='{self.project_id}', "
                f"location='{self.location_id}', "
                f"status='{status}')")
    
    def summary(self) -> Dict[str, Any]:
        """
        Get comprehensive summary of App Engine configuration.
        
        Returns:
            Dict containing all configuration details
        """
        # Analyze App Engine configuration
        app_features = []
        if self.https_only:
            app_features.append("https_only")
        if self.login != "optional":
            app_features.append("authentication")
        if self.session_affinity:
            app_features.append("session_affinity")
        if len(self.handlers) > 0:
            app_features.append("custom_handlers")
        if len(self.static_files) > 0:
            app_features.append("static_files")
        if len(self.env_vars) > 0:
            app_features.append("environment_variables")
            
        # Analyze scaling configuration
        scaling_info = {
            "type": self._get_scaling_type(),
            "min_instances": self.min_instances,
            "max_instances": self.max_instances
        }
        
        if self.automatic_scaling:
            scaling_info.update({
                "cpu_utilization": self.target_cpu_utilization,
                "throughput_utilization": self.target_throughput_utilization
            })
            
        # Analyze services
        services_info = {
            "services": self.services or ["default"],
            "service_count": len(self.services) if self.services else 1,
            "default_service": self.default_service
        }
        
        summary = {
            "app_name": self.app_name,
            "project_id": self.project_id,
            "app_id": self.app_id,
            "location_id": self.location_id,
            "app_description": self.app_description,
            "app_type": self._get_app_type_from_config(),
            
            # Runtime configuration
            "runtime": self.runtime,
            "runtime_version": self.runtime_version,
            "instance_class": self.instance_class,
            
            # Scaling configuration
            "scaling": scaling_info,
            
            # Service configuration
            "services": services_info,
            
            # Network configuration
            "network": self.network,
            "subnetwork": self.subnetwork,
            "session_affinity": self.session_affinity,
            
            # Environment and configuration
            "env_vars": self.env_vars,
            "env_var_count": len(self.env_vars),
            
            # Handlers and routing
            "handlers": self.handlers,
            "handler_count": len(self.handlers),
            "static_files": self.static_files,
            "static_file_count": len(self.static_files),
            "error_handlers": self.error_handlers,
            "error_handler_count": len(self.error_handlers),
            
            # Security configuration
            "security": {
                "login": self.login,
                "secure": self.secure,
                "https_only": self.secure == "always",
                "auth_required": self.login in ["required", "admin"],
                "admin_required": self.login == "admin"
            },
            
            # Deployment configuration
            "deployment": {
                "source_dir": self.source_dir,
                "source_url": self.source_url,
                "deployment_method": self.deployment_method,
                "version_id": self.version_id
            },
            
            # Features analysis
            "app_features": app_features,
            "has_scaling_configured": self.has_scaling_configured(),
            "is_production_ready": self.is_production_ready(),
            
            # Labels and metadata
            "labels": self.app_labels,
            "label_count": len(self.app_labels),
            "annotations": self.app_annotations,
            
            # State
            "state": {
                "exists": self.app_exists,
                "created": self.app_created,
                "deployed": self.app_deployed,
                "deployment_status": self.deployment_status
            },
            
            # Cost
            "estimated_monthly_cost": f"${self._estimate_app_engine_cost():.2f}",
            "is_free_tier": self._estimate_app_engine_cost() == 0.0
        }
        
        return summary
    
    def display_config(self):
        """Display current configuration in human-readable format"""
        print(f"\\n🚀 Google App Engine Configuration: {self.app_name}")
        print(f"   📁 Project: {self.project_id}")
        print(f"   📍 Location: {self.location_id}")
        print(f"   📝 Description: {self.app_description}")
        print(f"   🎯 App Type: {self._get_app_type_from_config().replace('_', ' ').title()}")
        
        # Runtime configuration
        print(f"\\n⚙️  Runtime Configuration:")
        print(f"   ⚙️  Runtime: {self.runtime}")
        if self.runtime_version:
            print(f"   📋 Version: {self.runtime_version}")
        print(f"   🖥️  Instance Class: {self.instance_class}")
        
        # Scaling configuration
        print(f"\\n📊 Scaling Configuration:")
        scaling_type = self._get_scaling_type()
        print(f"   📊 Type: {scaling_type.title()}")
        
        if self.automatic_scaling:
            print(f"   📈 Min Instances: {self.min_instances}")
            print(f"   📈 Max Instances: {self.max_instances}")
            print(f"   🎯 CPU Target: {self.target_cpu_utilization * 100:.0f}%")
            print(f"   🎯 Throughput Target: {self.target_throughput_utilization * 100:.0f}%")
        elif self.basic_scaling:
            print(f"   📈 Max Instances: {self.max_instances}")
            if hasattr(self, 'idle_timeout'):
                print(f"   ⏰ Idle Timeout: {self.idle_timeout}")
        elif self.manual_scaling:
            print(f"   📈 Fixed Instances: {self.min_instances}")
            
        # Service configuration
        print(f"\\n🔧 Service Configuration:")
        services = self.services or ["default"]
        print(f"   🔧 Services: {', '.join(services)}")
        print(f"   🔵 Default Service: {'✅ Yes' if self.default_service else '❌ No'}")
        
        # Network configuration
        if self.network or self.session_affinity:
            print(f"\\n🌐 Network Configuration:")
            if self.network:
                print(f"   🌐 VPC Network: {self.network}")
                if self.subnetwork:
                    print(f"   🔗 Subnetwork: {self.subnetwork}")
            print(f"   🔗 Session Affinity: {'✅ Enabled' if self.session_affinity else '❌ Disabled'}")
            
        # Environment variables
        if self.env_vars:
            print(f"\\n🔧 Environment Variables ({len(self.env_vars)}):")
            for key, value in list(self.env_vars.items())[:5]:
                # Mask sensitive values
                display_value = value if len(value) < 20 else f"{value[:10]}..."
                if any(sensitive in key.lower() for sensitive in ['key', 'secret', 'password', 'token']):
                    display_value = "***"
                print(f"   • {key}: {display_value}")
            if len(self.env_vars) > 5:
                print(f"   • ... and {len(self.env_vars) - 5} more")
                
        # Handlers and routing
        if self.handlers:
            print(f"\\n🔗 URL Handlers ({len(self.handlers)}):")
            for handler in self.handlers[:5]:
                print(f"   • {handler['url']} → {handler['script']}")
            if len(self.handlers) > 5:
                print(f"   • ... and {len(self.handlers) - 5} more")
                
        if self.static_files:
            print(f"\\n📄 Static Files ({len(self.static_files)}):")
            for static in self.static_files[:3]:
                print(f"   • {static['url']} → {static['static_dir']}")
            if len(self.static_files) > 3:
                print(f"   • ... and {len(self.static_files) - 3} more")
                
        # Security configuration
        print(f"\\n🔒 Security Configuration:")
        print(f"   🔑 Login: {self.login.title()}")
        print(f"   🔒 HTTPS: {self.secure.title()}")
        print(f"   🛡️  Auth Required: {'✅ Yes' if self.login in ['required', 'admin'] else '❌ No'}")
        
        # Deployment configuration
        print(f"\\n🚀 Deployment Configuration:")
        print(f"   📁 Source Directory: {self.source_dir}")
        print(f"   📦 Method: {self.deployment_method.title()}")
        if self.version_id:
            print(f"   🏷️  Version: {self.version_id}")
            
        # Labels
        if self.app_labels:
            print(f"\\n🏷️  Labels ({len(self.app_labels)}):")
            for key, value in list(self.app_labels.items())[:5]:
                print(f"   • {key}: {value}")
            if len(self.app_labels) > 5:
                print(f"   • ... and {len(self.app_labels) - 5} more")
                
        # Production readiness
        production_ready = self.is_production_ready()
        print(f"\\n🚀 Production Readiness: {'✅ Ready' if production_ready else '⚠️  Needs optimization'}")
        if not production_ready:
            issues = []
            if self.secure != "always":
                issues.append("HTTPS not enforced")
            if not self.has_scaling_configured():
                issues.append("No scaling configured")
            if len(self.env_vars) == 0:
                issues.append("No environment variables")
            if self.instance_class == "F1":
                issues.append("Using micro instances")
                
            for issue in issues[:3]:
                print(f"   ⚠️  {issue}")
                
        # Cost estimate
        cost = self._estimate_app_engine_cost()
        if cost > 0:
            print(f"\\n💰 Estimated Cost: ${cost:.2f}/month")
        else:
            print(f"\\n💰 Cost: Free tier")
            
        # URLs and console
        if self.project_id:
            print(f"\\n🌐 URLs and Console:")
            print(f"   🔗 App URL: https://{self.project_id}.appspot.com")
            print(f"   🌐 Console: https://console.cloud.google.com/appengine?project={self.project_id}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get App Engine status for backwards compatibility"""
        return {
            "app_name": self.app_name,
            "project_id": self.project_id,
            "location": self.location_id,
            "runtime": self.runtime,
            "instance_class": self.instance_class,
            "scaling_type": self._get_scaling_type(),
            "min_instances": self.min_instances,
            "max_instances": self.max_instances,
            "services": self.services or ["default"],
            "env_var_count": len(self.env_vars),
            "handler_count": len(self.handlers),
            "has_scaling_configured": self.has_scaling_configured(),
            "is_production_ready": self.is_production_ready(),
            "deployment_status": self.deployment_status,
            "estimated_cost": f"${self._estimate_app_engine_cost():.2f}/month"
        }


# Convenience function for creating App Engine instances
def create_app_engine(name: str) -> AppEngine:
    """
    Create a new Google App Engine instance.
    
    Args:
        name: App Engine application name
        
    Returns:
        AppEngine instance
    """
    return AppEngine(name)


# Framework-specific convenience functions
def create_flask_app(name: str, project_id: str) -> AppEngine:
    """Create a Flask application"""
    app = AppEngine(name)
    app.project(project_id).flask_app()
    return app


def create_django_app(name: str, project_id: str) -> AppEngine:
    """Create a Django application"""
    app = AppEngine(name)
    app.project(project_id).django_app()
    return app


def create_express_app(name: str, project_id: str) -> AppEngine:
    """Create an Express.js application"""
    app = AppEngine(name)
    app.project(project_id).express_app()
    return app


def create_spring_boot_app(name: str, project_id: str) -> AppEngine:
    """Create a Spring Boot application"""
    app = AppEngine(name)
    app.project(project_id).spring_boot_app()
    return app


# Export the class for easy importing
__all__ = [
    'AppEngine', 
    'create_app_engine',
    'create_flask_app',
    'create_django_app', 
    'create_express_app',
    'create_spring_boot_app'
]