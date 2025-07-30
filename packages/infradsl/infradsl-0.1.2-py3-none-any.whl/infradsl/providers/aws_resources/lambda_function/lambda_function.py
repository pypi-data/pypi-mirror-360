"""
AWS Lambda Complete Implementation

Combines all Lambda functionality through multiple inheritance:
- LambdaCore: Core attributes and authentication
- LambdaFunctionConfigurationMixin: Chainable configuration methods  
- LambdaFunctionLifecycleMixin: Lifecycle operations (create/destroy/preview)
"""

from .lambda_function_core import LambdaCore
from .lambda_function_configuration import LambdaFunctionConfigurationMixin
from .lambda_function_lifecycle import LambdaFunctionLifecycleMixin


class Lambda(LambdaFunctionLifecycleMixin, LambdaFunctionConfigurationMixin, LambdaCore):
    """
    Complete AWS Lambda implementation for serverless functions.
    
    This class combines:
    - Function configuration methods (runtime, memory, timeout, triggers)
    - Function lifecycle management (create, destroy, preview)
    - Container and API Gateway integration
    - Environment variables and VPC configuration
    - Rails-like method chaining for fluent API
    """
    
    def __init__(self, name: str):
        """Initialize Lambda instance for function management"""
        super().__init__(name)
        
        # Additional attributes specific to the combined class
        self.deployment_ready = False
        self.estimated_monthly_cost = "$0.20/month"
        
        # Cross-Cloud Magic integration
        self._optimization_priority = None
        self._auto_scaling_enabled = False
        
    def validate_configuration(self):
        """Validate the current Lambda configuration"""
        errors = []
        warnings = []
        
        # Validate function name
        if not self.function_name:
            errors.append("Function name is required")
        elif not self._is_valid_function_name(self.function_name):
            errors.append("Invalid function name format")
        
        # Validate runtime
        valid_runtimes = [
            "python3.8", "python3.9", "python3.10", "python3.11", "python3.12",
            "nodejs18.x", "nodejs20.x", "java8", "java11", "java17", "java21",
            "dotnet6", "dotnet8", "go1.x", "ruby3.2", "provided.al2"
        ]
        if self.runtime not in valid_runtimes:
            warnings.append(f"Unusual runtime: {self.runtime}")
        
        # Validate memory size
        if not (128 <= self.memory_size <= 10240):
            errors.append("Memory size must be between 128 MB and 10,240 MB")
        
        # Validate timeout
        if not (1 <= self.timeout_seconds <= 900):
            errors.append("Timeout must be between 1 and 900 seconds")
        
        # Validate handler
        if self.deployment_package_type == "Zip" and not self.handler:
            errors.append("Handler is required for Zip deployment packages")
        
        # Validate code source
        if self.deployment_package_type == "Zip":
            if not (self.code_zip_file or (self.code_s3_bucket and self.code_s3_key)):
                errors.append("Code source required: either zip file or S3 location")
        elif self.deployment_package_type == "Image":
            if not self.container_image_uri and not self.container_template:
                errors.append("Container image URI or template required for Image deployment")
        
        # Validate VPC configuration
        if self.vpc_config:
            if not self.subnet_ids:
                errors.append("Subnet IDs required when VPC config is specified")
            if not self.security_group_ids:
                warnings.append("No security groups specified for VPC Lambda")
        
        if errors:
            raise ValueError(f"Configuration validation failed: {', '.join(errors)}")
        
        if warnings:
            print(f"⚠️  Configuration warnings:")
            for warning in warnings:
                print(f"   - {warning}")
        
        self.deployment_ready = True
        return True
    
    def get_function_info(self):
        """Get complete information about the Lambda function"""
        return {
            'function_name': self.function_name,
            'runtime': self.runtime,
            'handler': self.handler,
            'memory_size': self.memory_size,
            'timeout_seconds': self.timeout_seconds,
            'deployment_package_type': self.deployment_package_type,
            'function_arn': self.function_arn,
            'function_url': self.function_url,
            'api_gateway_url': self.api_gateway_url,
            'api_gateway_integration': self.api_gateway_integration,
            'container_image_uri': self.container_image_uri,
            'container_template': self.container_template,
            'container_port': self.container_port,
            'environment_variables_count': len(self.environment_variables),
            'trigger_configurations_count': len(self.trigger_configurations),
            'vpc_configured': self.vpc_config is not None,
            'subnet_ids_count': len(self.subnet_ids),
            'security_group_ids_count': len(self.security_group_ids),
            'tags_count': len(self.tags),
            'state': self.state,
            'last_modified': self.last_modified,
            'deployment_ready': self.deployment_ready,
            'estimated_monthly_cost': self.estimated_monthly_cost,
            'optimization_priority': self._optimization_priority,
            'auto_scaling_enabled': self._auto_scaling_enabled
        }
    
    def clone(self, new_name: str):
        """Create a copy of this function with a new name"""
        cloned_function = Lambda(new_name)
        cloned_function.function_name = new_name
        cloned_function.runtime = self.runtime
        cloned_function.handler = self.handler
        cloned_function.memory_size = self.memory_size
        cloned_function.timeout_seconds = self.timeout_seconds
        cloned_function.environment_variables = self.environment_variables.copy()
        cloned_function.description = self.description
        cloned_function.deployment_package_type = self.deployment_package_type
        cloned_function.container_image_uri = self.container_image_uri
        cloned_function.container_template = self.container_template
        cloned_function.container_port = self.container_port
        cloned_function.api_gateway_integration = self.api_gateway_integration
        cloned_function.api_gateway_cors = self.api_gateway_cors
        cloned_function.trigger_configurations = self.trigger_configurations.copy()
        cloned_function.execution_role_arn = self.execution_role_arn
        cloned_function.vpc_config = self.vpc_config
        cloned_function.security_group_ids = self.security_group_ids.copy()
        cloned_function.subnet_ids = self.subnet_ids.copy()
        cloned_function.tags = self.tags.copy()
        return cloned_function
    
    def export_configuration(self):
        """Export function configuration for backup or migration"""
        return {
            'metadata': {
                'function_name': self.function_name,
                'runtime': self.runtime,
                'deployment_package_type': self.deployment_package_type,
                'exported_at': 'Mock timestamp'
            },
            'configuration': {
                'handler': self.handler,
                'memory_size': self.memory_size,
                'timeout_seconds': self.timeout_seconds,
                'environment_variables': self.environment_variables,
                'description': self.description,
                'api_gateway_integration': self.api_gateway_integration,
                'api_gateway_cors': self.api_gateway_cors,
                'container_image_uri': self.container_image_uri,
                'container_template': self.container_template,
                'container_port': self.container_port,
                'execution_role_arn': self.execution_role_arn,
                'vpc_config': self.vpc_config,
                'security_group_ids': self.security_group_ids,
                'subnet_ids': self.subnet_ids,
                'optimization_priority': self._optimization_priority,
                'auto_scaling_enabled': self._auto_scaling_enabled
            },
            'triggers': self.trigger_configurations,
            'tags': self.tags
        }
    
    def import_configuration(self, config_data: dict):
        """Import function configuration from exported data"""
        if 'configuration' in config_data:
            config = config_data['configuration']
            self.handler = config.get('handler', 'lambda_function.lambda_handler')
            self.memory_size = config.get('memory_size', 128)
            self.timeout_seconds = config.get('timeout_seconds', 30)
            self.environment_variables = config.get('environment_variables', {})
            self.description = config.get('description', '')
            self.api_gateway_integration = config.get('api_gateway_integration', False)
            self.api_gateway_cors = config.get('api_gateway_cors', True)
            self.container_image_uri = config.get('container_image_uri')
            self.container_template = config.get('container_template')
            self.container_port = config.get('container_port', 8080)
            self.execution_role_arn = config.get('execution_role_arn')
            self.vpc_config = config.get('vpc_config')
            self.security_group_ids = config.get('security_group_ids', [])
            self.subnet_ids = config.get('subnet_ids', [])
            self._optimization_priority = config.get('optimization_priority')
            self._auto_scaling_enabled = config.get('auto_scaling_enabled', False)
        
        if 'triggers' in config_data:
            self.trigger_configurations = config_data['triggers']
        
        if 'tags' in config_data:
            self.tags = config_data['tags']
        
        return self
    
    def _is_valid_function_name(self, function_name: str) -> bool:
        """Validate Lambda function name according to AWS rules"""
        import re
        
        # Function name can be 1-64 characters
        if len(function_name) < 1 or len(function_name) > 64:
            return False
        
        # Must contain only letters, numbers, hyphens, and underscores
        if not re.match(r'^[a-zA-Z0-9-_]+$', function_name):
            return False
        
        return True
    
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
        print(f"🎯 Cross-Cloud Magic: Optimizing Lambda for {priority}")
        
        # Apply AWS Lambda-specific optimizations
        if priority == "cost":
            print("💰 Cost optimization: Configuring cost-effective function")
            self._apply_cost_optimizations()
        elif priority == "performance":
            print("⚡ Performance optimization: Configuring high-performance function")
            self._apply_performance_optimizations()
        elif priority == "reliability":
            print("🛡️ Reliability optimization: Configuring reliable function")
            self._apply_reliability_optimizations()
        elif priority == "compliance":
            print("📋 Compliance optimization: Configuring compliant function")
            self._apply_compliance_optimizations()
        
        return self
    
    def _apply_cost_optimizations(self):
        """Apply AWS Lambda-specific cost optimizations"""
        # Use minimum memory for cost savings
        if self.memory_size > 256:
            print(f"   💰 Reducing memory from {self.memory_size}MB to 256MB for cost savings")
            self.memory_size = 256
        
        # Optimize timeout
        if self.timeout_seconds > 60:
            print(f"   💰 Reducing timeout from {self.timeout_seconds}s to 60s for cost savings")
            self.timeout_seconds = 60
        
        # Add cost optimization tags
        self.tags.update({
            "cost-optimized": "true",
            "memory-optimized": "true"
        })
    
    def _apply_performance_optimizations(self):
        """Apply AWS Lambda-specific performance optimizations"""
        # Increase memory for better performance
        if self.memory_size < 512:
            print(f"   ⚡ Increasing memory from {self.memory_size}MB to 512MB for performance")
            self.memory_size = 512
        
        # Enable provisioned concurrency consideration
        print("   ⚡ Performance: Consider enabling provisioned concurrency")
        
        # Add performance tags
        self.tags.update({
            "performance-optimized": "true",
            "memory-optimized-perf": "true"
        })
    
    def _apply_reliability_optimizations(self):
        """Apply AWS Lambda-specific reliability optimizations"""
        # Configure dead letter queue
        print("   🛡️ Reliability: Configure dead letter queue for failed invocations")
        
        # Enable X-Ray tracing
        print("   🛡️ Reliability: Enable X-Ray tracing for monitoring")
        
        # Add reliability tags
        self.tags.update({
            "reliability-optimized": "true",
            "monitoring-enabled": "true"
        })
    
    def _apply_compliance_optimizations(self):
        """Apply AWS Lambda-specific compliance optimizations"""
        # Configure VPC if not already configured
        if not self.vpc_config:
            print("   📋 Compliance: Consider VPC configuration for network isolation")
        
        # Add compliance tags
        self.tags.update({
            "compliance-optimized": "true",
            "audit-enabled": "true"
        })


# Convenience functions for creating Lambda instances
def create_function(name: str, runtime: str = "python3.11", handler: str = "lambda_function.lambda_handler") -> Lambda:
    """Create a new Lambda function with basic configuration"""
    function = Lambda(name)
    function.python_runtime(runtime).set_handler(handler)
    return function

def create_api_function(name: str, runtime: str = "python3.11") -> Lambda:
    """Create a Lambda function configured for API Gateway"""
    function = Lambda(name)
    function.python_runtime(runtime).trigger("api-gateway").memory(512).timeout(30)
    return function

def create_container_function(name: str, template_path: str, port: int = 8080) -> Lambda:
    """Create a Lambda function using container deployment"""
    function = Lambda(name)
    function.container("lambda-container", template_path, port)
    return function

def create_scheduled_function(name: str, runtime: str = "python3.11", schedule: str = "rate(1 hour)") -> Lambda:
    """Create a Lambda function with CloudWatch Events trigger"""
    function = Lambda(name)
    function.python_runtime(runtime).trigger("cloudwatch", schedule_expression=schedule)
    return function