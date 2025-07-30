"""
GCP Cloud Run Complete Implementation (Modular Architecture)

Combines all Cloud Run functionality through multiple inheritance:
- CloudRunCore: Core attributes and authentication
- CloudRunConfigurationMixin: Chainable configuration methods  
- CloudRunLifecycleMixin: Lifecycle operations (create/destroy/preview)
"""

from typing import Dict, Any, List, Optional
from .cloud_run_core import CloudRunCore
from .cloud_run_configuration import CloudRunConfigurationMixin
from .cloud_run_lifecycle import CloudRunLifecycleMixin


class CloudRun(CloudRunLifecycleMixin, CloudRunConfigurationMixin, CloudRunCore):
    """
    Complete GCP Cloud Run implementation for serverless container deployments.
    
    This class combines:
    - Container configuration methods (image, build, resources)
    - Serverless lifecycle management (create, destroy, preview, deploy)
    - Advanced scaling and traffic management
    - Security and access control features
    - Rails-like method chaining for fluent API
    """
    
    def __init__(self, name: str):
        """Initialize CloudRun instance for serverless container deployment"""
        super().__init__(name)
        
        # Additional attributes specific to the combined class
        self.deployment_ready = False
        self.estimated_monthly_cost = "$8.50/month"
        
        # Cross-Cloud Magic integration
        self._optimization_priority = None
        self._service_type = None
        self._auto_scaling_enabled = True
        self._high_availability_enabled = False
    
    def validate_configuration(self):
        """Validate the current Cloud Run configuration"""
        errors = []
        warnings = []
        
        # Validate service name
        if not self.service_name:
            errors.append("Service name is required")
        
        # Validate container configuration
        if not self.image_url and not (self.build_enabled and self.build_source_path):
            errors.append("Either container image URL or build source is required")
        
        if self.image_url and not self._validate_image_url(self.image_url):
            warnings.append(f"Container image URL format may be invalid: {self.image_url}")
        
        # Validate resource limits
        if not self._is_valid_memory_limit(self.memory_limit):
            errors.append(f"Invalid memory limit: {self.memory_limit}")
        
        if not self._is_valid_cpu_limit(self.cpu_limit):
            errors.append(f"Invalid CPU limit: {self.cpu_limit}")
        
        # Validate scaling configuration
        scaling_config = {
            "min_instances": self.min_instances,
            "max_instances": self.max_instances,
            "max_concurrent_requests": self.max_concurrent_requests
        }
        if not self._validate_scaling_config(scaling_config):
            errors.append("Invalid scaling configuration")
        
        if self.min_instances > self.max_instances:
            errors.append(f"Min instances ({self.min_instances}) cannot exceed max instances ({self.max_instances})")
        
        # Validate region
        if not self._is_valid_region(self.region):
            warnings.append(f"Region '{self.region}' may not support Cloud Run")
        
        # Validate port
        if not (1 <= self.container_port <= 65535):
            errors.append(f"Invalid container port: {self.container_port}")
        
        # Performance warnings
        if self.min_instances > 5:
            warnings.append(f"High minimum instances ({self.min_instances}) will increase costs significantly")
        
        if self.memory_limit in ["4Gi", "8Gi", "16Gi", "32Gi"]:
            warnings.append(f"High memory allocation ({self.memory_limit}) will increase costs")
        
        if self.max_instances > 100:
            warnings.append(f"Very high max instances ({self.max_instances}) may hit quotas")
        
        # Security warnings
        if self.allow_unauthenticated:
            warnings.append("Service allows unauthenticated access - ensure this is intended for security")
        
        if not self.service_account_email:
            warnings.append("No custom service account - using default (less secure)")
        
        # Build warnings
        if self.build_enabled and self.build_source_path:
            import os
            if not os.path.exists(self.build_source_path):
                errors.append(f"Build source path does not exist: {self.build_source_path}")
        
        if errors:
            raise ValueError(f"Configuration validation failed: {', '.join(errors)}")
        
        if warnings:
            print(f"⚠️  Configuration warnings:")
            for warning in warnings:
                print(f"   - {warning}")
        
        self.deployment_ready = True
        return True
    
    def get_service_info(self):
        """Get complete information about the Cloud Run service"""
        return {
            'service_name': self.service_name,
            'description': self.service_description,
            'region': self.region,
            'image_url': self.image_url,
            'container_port': self.container_port,
            'memory_limit': self.memory_limit,
            'cpu_limit': self.cpu_limit,
            'timeout_seconds': self.timeout_seconds,
            'execution_environment': self.execution_environment,
            'min_instances': self.min_instances,
            'max_instances': self.max_instances,
            'max_concurrent_requests': self.max_concurrent_requests,
            'allow_unauthenticated': self.allow_unauthenticated,
            'service_account_email': self.service_account_email,
            'vpc_connector': self.vpc_connector,
            'vpc_egress': self.vpc_egress,
            'environment_variables_count': len(self.environment_variables),
            'environment_variables': self.environment_variables,
            'secret_environment_variables_count': len(self.secret_environment_variables),
            'custom_domain': self.custom_domain,
            'auto_ssl': self.auto_ssl,
            'traffic_allocation': self.traffic_allocation,
            'build_enabled': self.build_enabled,
            'build_source_path': self.build_source_path,
            'labels_count': len(self.service_labels),
            'service_exists': self.service_exists,
            'deployment_ready': self.deployment_ready,
            'estimated_monthly_cost': self.estimated_monthly_cost,
            'optimization_priority': self._optimization_priority,
            'service_type': self._service_type
        }
    
    def clone(self, new_name: str):
        """Create a copy of this Cloud Run configuration with a new name"""
        cloned_service = CloudRun(new_name)
        cloned_service.service_name = new_name
        cloned_service.service_description = self.service_description
        cloned_service.region = self.region
        cloned_service.image_url = self.image_url
        cloned_service.container_port = self.container_port
        cloned_service.memory_limit = self.memory_limit
        cloned_service.cpu_limit = self.cpu_limit
        cloned_service.timeout_seconds = self.timeout_seconds
        cloned_service.min_instances = self.min_instances
        cloned_service.max_instances = self.max_instances
        cloned_service.max_concurrent_requests = self.max_concurrent_requests
        cloned_service.allow_unauthenticated = self.allow_unauthenticated
        cloned_service.environment_variables = self.environment_variables.copy()
        cloned_service.secret_environment_variables = self.secret_environment_variables.copy()
        cloned_service.service_labels = self.service_labels.copy()
        cloned_service.custom_domain = self.custom_domain
        cloned_service.build_enabled = self.build_enabled
        cloned_service.build_source_path = self.build_source_path
        return cloned_service
    
    def export_configuration(self):
        """Export Cloud Run configuration for backup or migration"""
        return {
            'metadata': {
                'service_name': self.service_name,
                'region': self.region,
                'image_url': self.image_url,
                'exported_at': 'Mock timestamp'
            },
            'configuration': {
                'service_name': self.service_name,
                'description': self.service_description,
                'region': self.region,
                'image_url': self.image_url,
                'container_port': self.container_port,
                'container_command': self.container_command,
                'container_args': self.container_args,
                'memory_limit': self.memory_limit,
                'cpu_limit': self.cpu_limit,
                'timeout_seconds': self.timeout_seconds,
                'execution_environment': self.execution_environment,
                'min_instances': self.min_instances,
                'max_instances': self.max_instances,
                'max_concurrent_requests': self.max_concurrent_requests,
                'cpu_throttling': self.cpu_throttling,
                'cpu_boost': self.cpu_boost,
                'allow_unauthenticated': self.allow_unauthenticated,
                'service_account_email': self.service_account_email,
                'vpc_connector': self.vpc_connector,
                'vpc_egress': self.vpc_egress,
                'environment_variables': self.environment_variables,
                'secret_environment_variables': self.secret_environment_variables,
                'custom_domain': self.custom_domain,
                'ssl_certificate': self.ssl_certificate,
                'auto_ssl': self.auto_ssl,
                'traffic_allocation': self.traffic_allocation,
                'build_enabled': self.build_enabled,
                'build_source_path': self.build_source_path,
                'build_template': self.build_template,
                'labels': self.service_labels,
                'annotations': self.service_annotations,
                'optimization_priority': self._optimization_priority,
                'service_type': self._service_type,
                'auto_scaling_enabled': self._auto_scaling_enabled,
                'high_availability_enabled': self._high_availability_enabled
            }
        }
    
    def import_configuration(self, config_data: dict):
        """Import Cloud Run configuration from exported data"""
        if 'configuration' in config_data:
            config = config_data['configuration']
            self.service_name = config.get('service_name', self.service_name)
            self.service_description = config.get('description', f"Cloud Run service for {self.service_name}")
            self.region = config.get('region', 'us-central1')
            self.image_url = config.get('image_url')
            self.container_port = config.get('container_port', 8080)
            self.container_command = config.get('container_command')
            self.container_args = config.get('container_args', [])
            self.memory_limit = config.get('memory_limit', '512Mi')
            self.cpu_limit = config.get('cpu_limit', '1000m')
            self.timeout_seconds = config.get('timeout_seconds', 300)
            self.execution_environment = config.get('execution_environment', 'gen2')
            self.min_instances = config.get('min_instances', 0)
            self.max_instances = config.get('max_instances', 100)
            self.max_concurrent_requests = config.get('max_concurrent_requests', 80)
            self.cpu_throttling = config.get('cpu_throttling', True)
            self.cpu_boost = config.get('cpu_boost', False)
            self.allow_unauthenticated = config.get('allow_unauthenticated', False)
            self.service_account_email = config.get('service_account_email')
            self.vpc_connector = config.get('vpc_connector')
            self.vpc_egress = config.get('vpc_egress', 'all-traffic')
            self.environment_variables = config.get('environment_variables', {})
            self.secret_environment_variables = config.get('secret_environment_variables', {})
            self.custom_domain = config.get('custom_domain')
            self.ssl_certificate = config.get('ssl_certificate')
            self.auto_ssl = config.get('auto_ssl', True)
            self.traffic_allocation = config.get('traffic_allocation', {"LATEST": 100})
            self.build_enabled = config.get('build_enabled', True)
            self.build_source_path = config.get('build_source_path')
            self.build_template = config.get('build_template', 'auto')
            self.service_labels = config.get('labels', {})
            self.service_annotations = config.get('annotations', {})
            self._optimization_priority = config.get('optimization_priority')
            self._service_type = config.get('service_type')
            self._auto_scaling_enabled = config.get('auto_scaling_enabled', True)
            self._high_availability_enabled = config.get('high_availability_enabled', False)
        
        return self
    
    def enable_auto_scaling(self, enabled: bool = True):
        """Enable automatic scaling optimizations"""
        self._auto_scaling_enabled = enabled
        if enabled:
            print("📈 Auto-scaling optimizations enabled")
            print("   💡 Dynamic resource adjustment configured")
            print("   💡 Intelligent scaling policies applied")
        return self
    
    def enable_high_availability(self, enabled: bool = True):
        """Enable high availability for the service"""
        self._high_availability_enabled = enabled
        if enabled:
            self.min_instances = max(self.min_instances, 2)  # Ensure multiple instances
            print("🛡️ High availability enabled")
            print("   💡 Minimum 2 instances configured")
            print("   💡 Multi-zone deployment enabled")
        return self
    
    def get_service_status(self):
        """Get current status of the Cloud Run service"""
        status = {
            "overall_status": "healthy",
            "issues": [],
            "recommendations": []
        }
        
        # Check configuration issues
        if not self.image_url and not (self.build_enabled and self.build_source_path):
            status["issues"].append("No container image or build source configured")
            status["overall_status"] = "error"
        
        if self.min_instances == 0:
            status["recommendations"].append("Consider setting min_instances > 0 to avoid cold starts")
        
        if self.allow_unauthenticated:
            status["recommendations"].append("Service is publicly accessible - review security implications")
        
        if not self.health_check_path:
            status["recommendations"].append("Consider adding health check endpoint")
        
        # Check resource allocation
        if self.memory_limit == "128Mi" and self.cpu_limit == "1000m":
            status["recommendations"].append("CPU allocation may be too high for low memory - consider balancing")
        
        # Check scaling configuration
        if self.max_instances == 1:
            status["recommendations"].append("Max instances set to 1 - may limit scalability")
        
        return status
    
    def apply_best_practices(self):
        """Apply Cloud Run best practices to the configuration"""
        print("🚀 Applying Cloud Run best practices")
        
        # Ensure reasonable resource allocation
        if self.memory_limit == "128Mi" and "2000m" in self.cpu_limit:
            print("   💡 Balancing CPU/memory allocation")
            self.memory_limit = "256Mi"
        
        # Add health check if not present
        if not self.health_check_path:
            print("   💡 Adding health check endpoint")
            self.health_check_path = "/health"
        
        # Set reasonable timeout
        if self.timeout_seconds == 300 and self.min_instances == 0:
            print("   💡 Optimizing timeout for scale-to-zero")
            self.timeout_seconds = 60
        
        # Add best practice labels
        self.service_labels.update({
            "managed-by": "infradsl",
            "best-practices": "applied",
            "serverless": "cloud-run"
        })
        print("   💡 Added best practice labels")
        
        # Security recommendations
        if self.allow_unauthenticated and not self.custom_domain:
            print("   💡 Public service detected - consider adding custom domain")
        
        return self
    
    def get_cost_breakdown(self):
        """Get detailed cost breakdown for Cloud Run service"""
        # Parse CPU and memory for cost calculation
        if self.cpu_limit.endswith("m"):
            cpu_cores = int(self.cpu_limit[:-1]) / 1000
        else:
            cpu_cores = float(self.cpu_limit)
            
        if self.memory_limit.endswith("Mi"):
            memory_gb = int(self.memory_limit[:-2]) / 1024
        elif self.memory_limit.endswith("Gi"):
            memory_gb = int(self.memory_limit[:-2])
        else:
            memory_gb = 0.5
            
        # Estimate usage patterns
        requests_per_month = 100000  # 100K requests
        avg_request_duration = 0.5   # 500ms
        cpu_utilization = 0.3        # 30% CPU usage
        
        # Calculate costs
        total_cpu_seconds = requests_per_month * avg_request_duration * cpu_utilization
        total_memory_seconds = requests_per_month * avg_request_duration
        
        breakdown = {
            "cpu_cost": total_cpu_seconds * cpu_cores * 0.000024,
            "memory_cost": total_memory_seconds * memory_gb * 0.0000025,
            "request_cost": (requests_per_month / 1000000) * 0.40,
            "always_on_cost": 0,
            "total_requests": requests_per_month,
            "cpu_cores": cpu_cores,
            "memory_gb": memory_gb
        }
        
        # Add always-on costs for min instances
        if self.min_instances > 0:
            seconds_per_month = 30 * 24 * 3600
            breakdown["always_on_cost"] = (
                self.min_instances * seconds_per_month *
                (cpu_cores * 0.000024 + memory_gb * 0.0000025)
            )
        
        breakdown["total_cost"] = (
            breakdown["cpu_cost"] + 
            breakdown["memory_cost"] + 
            breakdown["request_cost"] + 
            breakdown["always_on_cost"]
        )
        
        return breakdown
    
    def get_security_analysis(self):
        """Analyze Cloud Run security configuration"""
        analysis = {
            "security_score": 100,
            "issues": [],
            "recommendations": []
        }
        
        # Check public access
        if self.allow_unauthenticated:
            analysis["issues"].append("Service allows unauthenticated public access")
            analysis["security_score"] -= 30
        
        # Check service account
        if not self.service_account_email:
            analysis["recommendations"].append("Use custom service account instead of default")
            analysis["security_score"] -= 10
        
        # Check VPC connectivity
        if not self.vpc_connector:
            analysis["recommendations"].append("Consider VPC connector for private resource access")
            analysis["security_score"] -= 5
        
        # Check secrets management
        env_secrets = [k for k in self.environment_variables.keys() 
                      if any(word in k.lower() for word in ['password', 'key', 'secret', 'token'])]
        if env_secrets:
            analysis["issues"].append(f"Potential secrets in environment variables: {env_secrets}")
            analysis["security_score"] -= 20
        
        # Check execution environment
        if self.execution_environment != "gen2":
            analysis["recommendations"].append("Use gen2 execution environment for better security")
            analysis["security_score"] -= 5
        
        return analysis
    
    def get_performance_analysis(self):
        """Analyze Cloud Run performance configuration"""
        analysis = {
            "performance_score": 100,
            "issues": [],
            "recommendations": []
        }
        
        # Check cold start optimization
        if self.min_instances == 0:
            analysis["recommendations"].append("Consider min_instances > 0 to reduce cold starts")
            analysis["performance_score"] -= 10
        
        # Check resource allocation
        cpu_cores = float(self.cpu_limit.rstrip('m')) / 1000 if 'm' in self.cpu_limit else float(self.cpu_limit)
        memory_gb = float(self.memory_limit.rstrip('GiMi')) / (1024 if 'Mi' in self.memory_limit else 1)
        
        if cpu_cores > 2 and memory_gb < 1:
            analysis["issues"].append("High CPU with low memory may cause performance issues")
            analysis["performance_score"] -= 15
        
        # Check concurrency
        if self.max_concurrent_requests > 100:
            analysis["recommendations"].append("High concurrency may impact response times")
            analysis["performance_score"] -= 5
        
        # Check timeout
        if self.timeout_seconds > 900:  # 15 minutes
            analysis["recommendations"].append("Long timeout may indicate performance issues")
            analysis["performance_score"] -= 10
        
        return analysis


# Convenience functions for creating CloudRun instances
def create_web_app_service(project_id: str, app_name: str, source_path: str = None) -> CloudRun:
    """Create Cloud Run service for web application"""
    service = CloudRun(app_name)
    service.project(project_id).web_app().public()
    if source_path:
        service.build_from_source(source_path)
    return service

def create_api_service(project_id: str, api_name: str, source_path: str = None) -> CloudRun:
    """Create Cloud Run service for API"""
    service = CloudRun(api_name)
    service.project(project_id).api_service().private()
    if source_path:
        service.build_from_source(source_path)
    return service

def create_microservice(project_id: str, service_name: str, source_path: str = None) -> CloudRun:
    """Create Cloud Run microservice"""
    service = CloudRun(service_name)
    service.project(project_id).microservice().private()
    if source_path:
        service.build_from_source(source_path)
    return service

def create_background_worker(project_id: str, worker_name: str, source_path: str = None) -> CloudRun:
    """Create Cloud Run background worker"""
    service = CloudRun(worker_name)
    service.project(project_id).background_worker()
    if source_path:
        service.build_from_source(source_path)
    return service

def create_static_site(project_id: str, site_name: str, source_path: str = None) -> CloudRun:
    """Create Cloud Run static site"""
    service = CloudRun(site_name)
    service.project(project_id).static_site()
    if source_path:
        service.build_from_source(source_path)
    return service

# Aliases for backward compatibility
GCPCloudRun = CloudRun