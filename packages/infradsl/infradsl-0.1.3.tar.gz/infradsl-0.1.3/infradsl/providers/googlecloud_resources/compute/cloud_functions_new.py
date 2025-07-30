"""
GCP Cloud Functions Complete Implementation

Combines all Cloud Functions functionality through multiple inheritance:
- CloudFunctionsCore: Core attributes and authentication
- CloudFunctionsConfigurationMixin: Chainable configuration methods  
- CloudFunctionsLifecycleMixin: Lifecycle operations (create/destroy/preview)
"""

from typing import Dict, Any
from .cloud_functions_core import CloudFunctionsCore
from .cloud_functions_configuration import CloudFunctionsConfigurationMixin
from .cloud_functions_lifecycle import CloudFunctionsLifecycleMixin


class CloudFunctions(CloudFunctionsLifecycleMixin, CloudFunctionsConfigurationMixin, CloudFunctionsCore):
    """
    Complete GCP Cloud Functions implementation for serverless computing.
    
    This class combines:
    - Function configuration methods (runtime, memory, triggers, scaling)
    - Function lifecycle management (create, destroy, preview)
    - Trigger setup and event handling
    - Security and access control
    - Rails-like method chaining for fluent API
    """
    
    def __init__(self, name: str):
        """Initialize CloudFunctions instance for serverless function management"""
        super().__init__(name)
        
        # Additional attributes specific to the combined class
        self.deployment_ready = False
        self.estimated_monthly_cost = "$2.50/month"
        
        # Cross-Cloud Magic integration
        self._optimization_priority = None
        self._cdn_enabled = False
        self._auto_scaling_enabled = True
        self._monitoring_enabled = False
    
    # Properties for backward compatibility and easier access
    @property
    def runtime(self):
        """Get runtime"""
        return self.function_runtime
    
    @property
    def region(self):
        """Get region"""
        return self.function_region
        
    @property
    def entry_point(self):
        """Get entry point"""
        return self.function_entry_point
        
    @property
    def memory(self):
        """Get memory"""
        return self.function_memory
        
    @property
    def timeout(self):
        """Get timeout"""
        return self.function_timeout
        
    def validate_configuration(self):
        """Validate the current Cloud Functions configuration"""
        errors = []
        warnings = []
        
        # Validate function name
        if not self.function_name:
            errors.append("Function name is required")
        
        # Validate runtime
        if not self._is_valid_runtime(self.runtime):
            errors.append(f"Invalid runtime: {self.runtime}")
        
        # Validate region
        if not self._is_valid_region(self.region):
            warnings.append(f"Unusual region: {self.region}")
        
        # Validate memory
        if not self._is_valid_memory(self.memory):
            errors.append(f"Invalid memory allocation: {self.memory}")
        
        # Validate timeout
        if not self._is_valid_timeout(self.timeout):
            errors.append(f"Invalid timeout: {self.timeout}")
        
        # Validate scaling configuration
        if self.min_instances > self.max_instances:
            errors.append("Min instances cannot be greater than max instances")
        
        # Validate trigger configuration
        if not self._is_valid_trigger_type(self.trigger_type):
            errors.append(f"Invalid trigger type: {self.trigger_type}")
        
        # Validate source path for deployment
        if self.source_path and not self.source_path.strip():
            warnings.append("Source path is empty - function will use inline code")
        
        if errors:
            raise ValueError(f"Configuration validation failed: {', '.join(errors)}")
        
        if warnings:
            print(f"⚠️  Configuration warnings:")
            for warning in warnings:
                print(f"   - {warning}")
        
        self.deployment_ready = True
        return True
    
    def get_function_info(self):
        """Get complete information about the Cloud Function"""
        return {
            'function_name': self.function_name,
            'runtime': self.runtime,
            'region': self.region,
            'function_url': self.function_url,
            'function_arn': self.function_arn,
            'entry_point': self.entry_point,
            'source_path': self.source_path,
            'memory': self.memory,
            'timeout': self.timeout,
            'max_instances': self.max_instances,
            'min_instances': self.min_instances,
            'trigger_type': self.trigger_type,
            'trigger_config': self.trigger_config,
            'environment_variables': len(self.environment_variables),
            'service_account': self.service_account,
            'labels_count': len(self.function_labels),
            'description': self.description,
            'ingress_settings': self.ingress_settings,
            'function_type': self.function_type,
            'function_exists': self.function_exists,
            'deployment_ready': self.deployment_ready,
            'estimated_monthly_cost': self.estimated_monthly_cost,
            'optimization_priority': self._optimization_priority,
            'auto_scaling_enabled': self._auto_scaling_enabled
        }
    
    def clone(self, new_name: str):
        """Create a copy of this function with a new name"""
        cloned_function = CloudFunctions(new_name)
        cloned_function.function_name = new_name
        cloned_function.runtime = self.runtime
        cloned_function.region = self.region
        cloned_function.entry_point = self.entry_point
        cloned_function.source_path = self.source_path
        cloned_function.memory = self.memory
        cloned_function.timeout = self.timeout
        cloned_function.max_instances = self.max_instances
        cloned_function.min_instances = self.min_instances
        cloned_function.trigger_type = self.trigger_type
        cloned_function.trigger_config = self.trigger_config.copy()
        cloned_function.environment_variables = self.environment_variables.copy()
        cloned_function.service_account = self.service_account
        cloned_function.function_labels = self.function_labels.copy()
        cloned_function.description = self.description
        cloned_function.ingress_settings = self.ingress_settings
        cloned_function.function_type = self.function_type
        return cloned_function
    
    def export_configuration(self):
        """Export function configuration for backup or migration"""
        return {
            'metadata': {
                'function_name': self.function_name,
                'runtime': self.runtime,
                'region': self.region,
                'exported_at': 'Mock timestamp'
            },
            'configuration': {
                'entry_point': self.entry_point,
                'source_path': self.source_path,
                'memory': self.memory,
                'timeout': self.timeout,
                'max_instances': self.max_instances,
                'min_instances': self.min_instances,
                'trigger_type': self.trigger_type,
                'trigger_config': self.trigger_config,
                'environment_variables': self.environment_variables,
                'service_account': self.service_account,
                'labels': self.function_labels,
                'description': self.description,
                'ingress_settings': self.ingress_settings,
                'function_type': self.function_type,
                'optimization_priority': self._optimization_priority,
                'auto_scaling_enabled': self._auto_scaling_enabled,
                'monitoring_enabled': self._monitoring_enabled
            }
        }
    
    def import_configuration(self, config_data: dict):
        """Import function configuration from exported data"""
        if 'configuration' in config_data:
            config = config_data['configuration']
            self.entry_point = config.get('entry_point', 'main')
            self.source_path = config.get('source_path')
            self.memory = config.get('memory', '256MB')
            self.timeout = config.get('timeout', '60s')
            self.max_instances = config.get('max_instances', 100)
            self.min_instances = config.get('min_instances', 0)
            self.trigger_type = config.get('trigger_type', 'http')
            self.trigger_config = config.get('trigger_config', {})
            self.environment_variables = config.get('environment_variables', {})
            self.service_account = config.get('service_account')
            self.function_labels = config.get('labels', {})
            self.description = config.get('description', '')
            self.ingress_settings = config.get('ingress_settings', 'ALLOW_ALL')
            self.function_type = config.get('function_type')
            self._optimization_priority = config.get('optimization_priority')
            self._auto_scaling_enabled = config.get('auto_scaling_enabled', True)
            self._monitoring_enabled = config.get('monitoring_enabled', False)
        
        return self
    
    def optimize_for(self, priority: str):
        """Use Cross-Cloud Magic to optimize for cost/performance/reliability
        
        Args:
            priority: Optimization priority - "cost", "performance", "reliability", "compliance"
            
        Returns:
            Self for method chaining
        """
        valid_priorities = ["cost", "performance", "reliability", "compliance"]
        if priority not in valid_priorities:
            raise ValueError(f"Priority must be one of: {valid_priorities}. Got: {priority}")
        
        self._optimization_priority = priority
        
        print(f"🎯 Cross-Cloud Magic: Optimizing Cloud Functions for {priority}")
        
        # Apply GCP-specific optimizations
        if priority == "cost":
            print("💰 Cost optimization: Configuring cost-effective function")
            # Scale to zero when not in use
            if self.min_instances > 0:
                print("   💡 Setting min instances to 0 for cost savings")
                self.min_instances = 0
            # Use smaller memory if not processor function
            if self.function_type != "processor" and self.memory in ["1GB", "2GB", "4GB", "8GB"]:
                print("   💡 Reducing memory allocation for cost savings")
                self.memory = "512MB"
            print("   💡 Function will scale to zero when not in use")
            
        elif priority == "performance":
            print("⚡ Performance optimization: Configuring high-performance function")
            # Keep at least one instance warm
            if self.min_instances == 0:
                print("   💡 Setting min instances to 1 for faster cold starts")
                self.min_instances = 1
            # Increase memory for better performance
            if self.memory in ["128MB", "256MB"]:
                print("   💡 Increasing memory for better performance")
                self.memory = "512MB"
            print("   💡 Instance will stay warm for faster response times")
            
        elif priority == "reliability":
            print("🛡️ Reliability optimization: Configuring reliable function")
            # Keep multiple instances for high availability
            if self.min_instances < 2:
                print("   💡 Setting min instances to 2 for high availability")
                self.min_instances = 2
            # Increase timeout for reliability
            if self.timeout in ["30s", "60s"]:
                print("   💡 Increasing timeout for reliability")
                self.timeout = "180s"
            print("   💡 Multiple instances for high availability")
            
        elif priority == "compliance":
            print("📋 Compliance optimization: Configuring compliant function")
            # Ensure internal-only access
            if self.ingress_settings == "ALLOW_ALL":
                print("   💡 Setting to internal-only access for compliance")
                self.ingress_settings = "ALLOW_INTERNAL_ONLY"
            # Add compliance labels
            self.function_labels.update({
                "compliance": "enabled",
                "access": "internal-only"
            })
            print("   💡 Function configured for internal-only access")
        
        return self
    
    def enable_monitoring(self, enabled: bool = True):
        """Enable monitoring and logging for the function"""
        self._monitoring_enabled = enabled
        if enabled:
            print("📊 Monitoring and logging enabled")
            self.function_labels.update({
                "monitoring": "enabled",
                "logging": "enabled"
            })
        return self
    
    def with_secrets(self, secrets: Dict[str, str]):
        """Add secret manager integration"""
        for key, secret_name in secrets.items():
            self.environment_variables[key] = f"projects/{self.gcp_client.project_id if hasattr(self, 'gcp_client') and self.gcp_client else 'PROJECT'}/secrets/{secret_name}/versions/latest"
        
        print(f"🔐 Added {len(secrets)} secret references")
        return self
    
    def with_vpc_connector(self, connector_name: str):
        """Configure VPC connector for private network access"""
        self.function_labels["vpc_connector"] = connector_name
        print(f"🌐 VPC connector configured: {connector_name}")
        return self
    
    def with_custom_domain(self, domain: str):
        """Configure custom domain mapping"""
        if self.trigger_type != "http":
            raise ValueError("Custom domain only available for HTTP functions")
        
        self.function_labels["custom_domain"] = domain
        print(f"🌍 Custom domain configured: {domain}")
        return self


# Convenience functions for creating CloudFunctions instances
def create_api_function(name: str, runtime: str = "python39") -> CloudFunctions:
    """Create a function optimized for API workloads"""
    function = CloudFunctions(name)
    function.function(name).runtime(runtime).http().optimize_for("performance")
    return function

def create_webhook_function(name: str, runtime: str = "python39") -> CloudFunctions:
    """Create a function optimized for webhooks"""
    function = CloudFunctions(name)
    function.function(name).runtime(runtime).webhook().optimize_for("performance")
    return function

def create_processor_function(name: str, runtime: str = "python39") -> CloudFunctions:
    """Create a function optimized for data processing"""
    function = CloudFunctions(name)
    function.function(name).runtime(runtime).processor().optimize_for("reliability")
    return function

def create_scheduled_function(name: str, schedule: str = "0 2 * * *", runtime: str = "python39") -> CloudFunctions:
    """Create a function for scheduled tasks"""
    function = CloudFunctions(name)
    function.function(name).runtime(runtime).scheduled(schedule).optimize_for("cost")
    return function

def create_microservice(name: str, runtime: str = "python39") -> CloudFunctions:
    """Create a microservice function"""
    function = CloudFunctions(name)
    function.function(name).runtime(runtime).microservice().optimize_for("performance")
    return function