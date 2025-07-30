"""
Google App Engine Configuration Mixin

Configuration methods for Google App Engine.
Provides Rails-like method chaining for fluent App Engine configuration.
"""

from typing import Dict, Any, List, Optional, Union


class AppEngineConfigurationMixin:
    """
    Mixin for Google App Engine configuration methods.
    
    This mixin provides:
    - Rails-like method chaining for fluent App Engine configuration
    - Runtime and environment configuration
    - Scaling configuration (automatic, basic, manual)
    - Service and version management
    - Routing and handler configuration
    - Environment-specific settings
    """
    
    # Project and Application Configuration
    def project(self, project_id: str):
        """Set Google Cloud project ID"""
        self.project_id = project_id
        self.app_id = project_id
        return self
        
    def location(self, location_id: str):
        """Set App Engine location"""
        if not self._validate_location(location_id):
            raise ValueError(f"Invalid location: {location_id}")
        self.location_id = location_id
        return self
        
    def description(self, description: str):
        """Set application description"""
        self.app_description = description
        return self
    
    # Runtime Configuration Methods
    def runtime(self, runtime: str, version: str = None):
        """Set runtime environment"""
        if not self._validate_runtime(runtime):
            raise ValueError(f"Unsupported runtime: {runtime}")
        self.runtime = runtime
        if version:
            self.runtime_version = version
        return self
        
    def python(self, version: str = "39"):
        """Use Python runtime"""
        return self.runtime(f"python{version}")
        
    def java(self, version: str = "11"):
        """Use Java runtime"""
        return self.runtime(f"java{version}")
        
    def nodejs(self, version: str = "16"):
        """Use Node.js runtime"""
        return self.runtime(f"nodejs{version}")
        
    def go(self, version: str = "116"):
        """Use Go runtime"""
        return self.runtime(f"go{version}")
        
    def php(self, version: str = "74"):
        """Use PHP runtime"""
        return self.runtime(f"php{version}")
        
    def ruby(self, version: str = "27"):
        """Use Ruby runtime"""
        return self.runtime(f"ruby{version}")
        
    def dotnet(self, version: str = "3"):
        """Use .NET runtime"""
        return self.runtime(f"dotnet{version}")
        
    def custom_runtime(self):
        """Use custom runtime with Dockerfile"""
        return self.runtime("custom")
    
    # Instance Class Configuration
    def instance_class(self, instance_class: str):
        """Set instance class"""
        if not self._validate_instance_class(instance_class):
            raise ValueError(f"Invalid instance class: {instance_class}")
        self.instance_class = instance_class
        return self
        
    def micro_instance(self):
        """Use F1 micro instance (shared CPU, 128MB RAM)"""
        return self.instance_class("F1")
        
    def small_instance(self):
        """Use F2 small instance (shared CPU, 256MB RAM)"""
        return self.instance_class("F2")
        
    def medium_instance(self):
        """Use F4 medium instance (shared CPU, 512MB RAM)"""
        return self.instance_class("F4")
        
    def large_instance(self):
        """Use F4_1G large instance (shared CPU, 1GB RAM)"""
        return self.instance_class("F4_1G")
    
    # Scaling Configuration Methods
    def automatic_scaling(self, 
                         min_instances: int = 0, 
                         max_instances: int = 10,
                         target_cpu_utilization: float = 0.6,
                         target_throughput_utilization: float = 0.6):
        """Configure automatic scaling"""
        self.automatic_scaling = True
        self.manual_scaling = False
        self.basic_scaling = False
        self.min_instances = min_instances
        self.max_instances = max_instances
        self.target_cpu_utilization = target_cpu_utilization
        self.target_throughput_utilization = target_throughput_utilization
        return self
        
    def basic_scaling(self, max_instances: int = 5, idle_timeout: str = "15m"):
        """Configure basic scaling"""
        self.basic_scaling = True
        self.automatic_scaling = False
        self.manual_scaling = False
        self.max_instances = max_instances
        self.idle_timeout = idle_timeout
        return self
        
    def manual_scaling(self, instances: int = 1):
        """Configure manual scaling"""
        self.manual_scaling = True
        self.automatic_scaling = False
        self.basic_scaling = False
        self.min_instances = instances
        self.max_instances = instances
        return self
        
    def scale_to_zero(self):
        """Allow scaling to zero instances"""
        return self.automatic_scaling(min_instances=0)
        
    def always_on(self, instances: int = 1):
        """Keep minimum instances always running"""
        return self.automatic_scaling(min_instances=instances)
    
    # Environment Variables and Configuration
    def env_var(self, key: str, value: str):
        """Set environment variable"""
        self.env_vars[key] = value
        return self
        
    def env_vars(self, variables: Dict[str, str]):
        """Set multiple environment variables"""
        self.env_vars.update(variables)
        return self
        
    def database_url(self, url: str):
        """Set database URL environment variable"""
        return self.env_var("DATABASE_URL", url)
        
    def secret_key(self, key: str):
        """Set secret key environment variable"""
        return self.env_var("SECRET_KEY", key)
    
    # Source Code Configuration
    def source_directory(self, directory: str):
        """Set source code directory"""
        self.source_dir = directory
        return self
        
    def source_url(self, url: str):
        """Set source code URL (zip file)"""
        self.source_url = url
        self.deployment_method = "url"
        return self
        
    def dockerfile_deployment(self):
        """Use Dockerfile for deployment"""
        self.deployment_method = "dockerfile"
        return self.custom_runtime()
    
    # Handler and Routing Configuration
    def handler(self, url_pattern: str, script: str, **options):
        """Add URL handler"""
        handler = {
            "url": url_pattern,
            "script": script,
            **options
        }
        self.handlers.append(handler)
        return self
        
    def static_files(self, url_pattern: str, static_dir: str, expiration: str = None):
        """Add static file handler"""
        static_config = {
            "url": url_pattern,
            "static_dir": static_dir,
            "expiration": expiration or self.default_expiration
        }
        self.static_files.append(static_config)
        return self
        
    def default_handler(self, script: str = "main.app"):
        """Set default application handler"""
        return self.handler(".*", script)
    
    # Security Configuration
    def login_required(self):
        """Require login for all requests"""
        self.login = "required"
        return self
        
    def admin_required(self):
        """Require admin login for all requests"""
        self.login = "admin"
        return self
        
    def login_optional(self):
        """Make login optional"""
        self.login = "optional"
        return self
        
    def https_only(self):
        """Require HTTPS for all requests"""
        self.secure = "always"
        return self
        
    def https_optional(self):
        """Allow both HTTP and HTTPS"""
        self.secure = "optional"
        return self
    
    # Service Configuration
    def service(self, service_id: str):
        """Configure as a specific service"""
        self.services.append(service_id)
        self.default_service = (service_id == "default")
        return self
        
    def default_service(self):
        """Configure as the default service"""
        return self.service("default")
        
    def api_service(self, service_name: str = "api"):
        """Configure as API service"""
        return self.service(service_name)
        
    def worker_service(self, service_name: str = "worker"):
        """Configure as background worker service"""
        return self.service(service_name)
    
    # Network Configuration
    def network(self, network: str, subnetwork: str = None):
        """Set VPC network configuration"""
        self.network = network
        if subnetwork:
            self.subnetwork = subnetwork
        return self
        
    def session_affinity(self, enabled: bool = True):
        """Enable session affinity"""
        self.session_affinity = enabled
        return self
    
    # Error Handling
    def error_handler(self, error_code: str, file: str):
        """Add custom error handler"""
        self.error_handlers.append({
            "error_code": error_code,
            "file": file
        })
        return self
        
    def custom_404(self, file: str = "404.html"):
        """Set custom 404 page"""
        return self.error_handler("404", file)
        
    def custom_500(self, file: str = "500.html"):
        """Set custom 500 page"""
        return self.error_handler("500", file)
    
    # High-Level Application Patterns
    def web_application(self):
        """Configure as web application"""
        self.app_labels["purpose"] = "web-app"
        return (self
                .automatic_scaling(min_instances=0, max_instances=10)
                .micro_instance()
                .static_files("/static/*", "static/")
                .static_files("/favicon.ico", "static/favicon.ico")
                .custom_404()
                .custom_500())
                
    def api_application(self):
        """Configure as API application"""
        self.app_labels["purpose"] = "api"
        return (self
                .automatic_scaling(min_instances=1, max_instances=20)
                .small_instance()
                .https_only())
                
    def microservice(self, service_name: str):
        """Configure as microservice"""
        self.app_labels["purpose"] = "microservice"
        self.app_labels["service"] = service_name
        return (self
                .service(service_name)
                .automatic_scaling(min_instances=0, max_instances=5)
                .micro_instance())
                
    def background_worker(self):
        """Configure as background worker"""
        self.app_labels["purpose"] = "worker"
        return (self
                .worker_service()
                .basic_scaling(max_instances=3)
                .small_instance()
                .login_optional())
                
    def static_website(self):
        """Configure as static website"""
        self.app_labels["purpose"] = "static-site"
        return (self
                .automatic_scaling(min_instances=0, max_instances=5)
                .micro_instance()
                .static_files("/*", "public/"))
    
    # Framework-Specific Configurations
    def flask_app(self, main_module: str = "main"):
        """Configure Flask application"""
        self.app_labels["framework"] = "flask"
        return (self
                .python()
                .web_application()
                .default_handler(f"{main_module}.app")
                .env_var("FLASK_ENV", "production"))
                
    def django_app(self, main_module: str = "main"):
        """Configure Django application"""
        self.app_labels["framework"] = "django"
        return (self
                .python()
                .web_application()
                .default_handler(f"{main_module}.application")
                .env_var("DJANGO_SETTINGS_MODULE", f"{main_module}.settings"))
                
    def express_app(self, main_file: str = "app.js"):
        """Configure Express.js application"""
        self.app_labels["framework"] = "express"
        return (self
                .nodejs()
                .web_application()
                .default_handler(main_file))
                
    def spring_boot_app(self, main_class: str = "Application"):
        """Configure Spring Boot application"""
        self.app_labels["framework"] = "spring-boot"
        return (self
                .java()
                .web_application()
                .small_instance()
                .default_handler(main_class))
    
    # Environment-Specific Configurations
    def development(self):
        """Configure for development environment"""
        self.app_labels["environment"] = "development"
        return (self
                .automatic_scaling(min_instances=0, max_instances=2)
                .micro_instance()
                .login_optional()
                .https_optional())
                
    def staging(self):
        """Configure for staging environment"""
        self.app_labels["environment"] = "staging"
        return (self
                .automatic_scaling(min_instances=1, max_instances=5)
                .small_instance()
                .login_required()
                .https_only())
                
    def production(self):
        """Configure for production environment"""
        self.app_labels["environment"] = "production"
        return (self
                .automatic_scaling(min_instances=2, max_instances=20)
                .medium_instance()
                .https_only()
                .session_affinity())
    
    # Label and Metadata Configuration
    def label(self, key: str, value: str):
        """Add label to application"""
        self.app_labels[key] = value
        return self
        
    def labels(self, labels: Dict[str, str]):
        """Add multiple labels"""
        self.app_labels.update(labels)
        return self
        
    def team(self, team_name: str):
        """Set team label"""
        return self.label("team", team_name)
        
    def cost_center(self, cost_center: str):
        """Set cost center label"""
        return self.label("cost-center", cost_center)
        
    def version_label(self, version: str):
        """Set version label"""
        return self.label("version", version)
    
    # Helper Methods
    def get_app_yaml_config(self) -> Dict[str, Any]:
        """Generate app.yaml configuration"""
        config = {
            "runtime": self.runtime
        }
        
        if self.runtime_version:
            config["runtime_config"] = {"python_version": self.runtime_version}
            
        if self.instance_class != "F1":
            config["instance_class"] = self.instance_class
            
        if self.automatic_scaling:
            scaling_config = {}
            if self.min_instances > 0:
                scaling_config["min_instances"] = self.min_instances
            if self.max_instances != 10:
                scaling_config["max_instances"] = self.max_instances
            if scaling_config:
                config["automatic_scaling"] = scaling_config
                
        elif self.basic_scaling:
            config["basic_scaling"] = {
                "max_instances": self.max_instances
            }
            if hasattr(self, 'idle_timeout'):
                config["basic_scaling"]["idle_timeout"] = self.idle_timeout
                
        elif self.manual_scaling:
            config["manual_scaling"] = {
                "instances": self.min_instances
            }
            
        if self.env_vars:
            config["env_variables"] = self.env_vars
            
        if self.handlers:
            config["handlers"] = self.handlers
            
        if self.network:
            config["vpc_access_connector"] = {
                "name": self.network
            }
            
        return config
    
    def has_scaling_configured(self) -> bool:
        """Check if scaling is configured"""
        return self.automatic_scaling or self.basic_scaling or self.manual_scaling
    
    def is_production_ready(self) -> bool:
        """Check if application is production ready"""
        return (
            self.https_only and
            self.has_scaling_configured() and
            len(self.env_vars) > 0 and
            self.instance_class in ["F2", "F4", "F4_1G"]
        )