"""
Lambda Configuration and DSL Methods

This module provides Rails-like chainable methods and configuration management
for Lambda functions.
"""

from typing import Dict, Any, List, Optional


class LambdaConfigurationManager:
    """
    Lambda Configuration and DSL Methods
    
    Handles:
    - Rails-like chainable methods
    - Configuration validation and defaults
    - Settings management
    - Convenience methods for common configurations
    """
    
    def __init__(self, lambda_function):
        """Initialize with reference to the Lambda function instance."""
        self.function = lambda_function
    
    # Runtime and basic configuration
    def python(self, version: str = "3.11"):
        """Configure for Python runtime - chainable"""
        self.function.runtime = f"python{version}"
        self.function.handler = "lambda_function.lambda_handler"
        return self.function
    
    def nodejs(self, version: str = "18"):
        """Configure for Node.js runtime - chainable"""
        self.function.runtime = f"nodejs{version}.x"
        self.function.handler = "index.handler"
        return self.function
    
    def java(self, version: str = "11"):
        """Configure for Java runtime - chainable"""
        self.function.runtime = f"java{version}"
        self.function.handler = "example.Handler::handleRequest"
        return self.function
    
    def go(self):
        """Configure for Go runtime - chainable"""
        self.function.runtime = "go1.x"
        self.function.handler = "main"
        return self.function
    
    def dotnet(self, version: str = "6"):
        """Configure for .NET runtime - chainable"""
        self.function.runtime = f"dotnet{version}"
        self.function.handler = "Assembly::Namespace.Class::Method"
        return self.function
    
    def ruby(self, version: str = "3.2"):
        """Configure for Ruby runtime - chainable"""
        self.function.runtime = f"ruby{version}"
        self.function.handler = "lambda_function.lambda_handler"
        return self.function
    
    # Container configuration
    def container(self, image_uri: Optional[str] = None):
        """Configure for container deployment - chainable"""
        self.function.deployment_package_type = "Image"
        if image_uri:
            self.function.container_image_uri = image_uri
        return self.function
    
    def zip_package(self):
        """Configure for ZIP package deployment - chainable"""
        self.function.deployment_package_type = "Zip"
        return self.function
    
    # Memory and performance configuration
    def memory(self, mb: int):
        """Set memory allocation in MB - chainable"""
        if mb < 128 or mb > 10240:
            raise ValueError("Memory must be between 128 and 10240 MB")
        self.function.memory_size = mb
        return self.function
    
    def timeout(self, seconds: int):
        """Set timeout in seconds - chainable"""
        if seconds < 1 or seconds > 900:
            raise ValueError("Timeout must be between 1 and 900 seconds")
        self.function.timeout_seconds = seconds
        return self.function
    
    def handler(self, handler_string: str):
        """Set function handler - chainable"""
        self.function.handler = handler_string
        return self.function
    
    # Size presets
    def nano(self):
        """Nano size: 128MB memory, 30s timeout - chainable"""
        return self.memory(128).timeout(30)
    
    def micro(self):
        """Micro size: 256MB memory, 60s timeout - chainable"""
        return self.memory(256).timeout(60)
    
    def small(self):
        """Small size: 512MB memory, 120s timeout - chainable"""
        return self.memory(512).timeout(120)
    
    def medium(self):
        """Medium size: 1024MB memory, 300s timeout - chainable"""
        return self.memory(1024).timeout(300)
    
    def large(self):
        """Large size: 2048MB memory, 600s timeout - chainable"""
        return self.memory(2048).timeout(600)
    
    def xlarge(self):
        """XLarge size: 4096MB memory, 900s timeout - chainable"""
        return self.memory(4096).timeout(900)
    
    # Environment variables
    def env(self, key: str, value: str):
        """Add environment variable - chainable"""
        self.function.environment_variables[key] = value
        return self.function
    
    def envs(self, env_dict: Dict[str, str]):
        """Add multiple environment variables - chainable"""
        self.function.environment_variables.update(env_dict)
        return self.function
    
    def clear_env(self):
        """Clear all environment variables - chainable"""
        self.function.environment_variables.clear()
        return self.function
    
    # Common workload configurations
    def web_api(self):
        """Configure for web API workload - chainable"""
        return self.medium().env("NODE_ENV", "production")
    
    def data_processing(self):
        """Configure for data processing workload - chainable"""
        return self.large().timeout(900)
    
    def microservice(self):
        """Configure for microservice workload - chainable"""
        return self.small().timeout(60)
    
    def batch_job(self):
        """Configure for batch job workload - chainable"""
        return self.xlarge().timeout(900)
    
    def stream_processing(self):
        """Configure for stream processing workload - chainable"""
        return self.medium().timeout(300)
    
    # Trigger configurations
    def api_gateway(self, cors: bool = True, api_key_required: bool = False):
        """Enable API Gateway integration - chainable"""
        self.function.api_gateway_integration = True
        self.function.api_gateway_cors = cors
        self.function.api_gateway_api_key_required = api_key_required
        return self.function
    
    def s3_trigger(self, bucket_name: str, events: List[str] = None, prefix: str = "", suffix: str = ""):
        """Add S3 bucket trigger - chainable"""
        trigger_config = {
            'type': 's3',
            'bucket_name': bucket_name,
            'events': events or ['s3:ObjectCreated:*'],
            'prefix': prefix,
            'suffix': suffix
        }
        self.function.trigger_configurations.append(trigger_config)
        return self.function
    
    def sqs_trigger(self, queue_arn: str, batch_size: int = 10):
        """Add SQS queue trigger - chainable"""
        trigger_config = {
            'type': 'sqs',
            'queue_arn': queue_arn,
            'batch_size': batch_size
        }
        self.function.trigger_configurations.append(trigger_config)
        return self.function
    
    def schedule(self, expression: str, description: str = ""):
        """Add scheduled trigger - chainable"""
        trigger_config = {
            'type': 'schedule',
            'schedule_expression': expression,
            'description': description or f"Scheduled trigger for {self.function.function_name}"
        }
        self.function.trigger_configurations.append(trigger_config)
        return self.function
    
    def event_pattern(self, pattern: Dict[str, Any], description: str = ""):
        """Add event pattern trigger - chainable"""
        trigger_config = {
            'type': 'event_pattern',
            'event_pattern': pattern,
            'description': description or f"Event pattern trigger for {self.function.function_name}"
        }
        self.function.trigger_configurations.append(trigger_config)
        return self.function
    
    # VPC configuration
    def vpc(self, security_group_ids: List[str], subnet_ids: List[str]):
        """Configure VPC settings - chainable"""
        self.function.security_group_ids = security_group_ids
        self.function.subnet_ids = subnet_ids
        self.function.vpc_config = {
            'SubnetIds': subnet_ids,
            'SecurityGroupIds': security_group_ids
        }
        return self.function
    
    def no_vpc(self):
        """Remove VPC configuration - chainable"""
        self.function.security_group_ids = []
        self.function.subnet_ids = []
        self.function.vpc_config = None
        return self.function
    
    # IAM role configuration
    def execution_role(self, role_arn: str):
        """Set execution role ARN - chainable"""
        self.function.execution_role_arn = role_arn
        return self.function
    
    def auto_role(self):
        """Use auto-generated execution role - chainable"""
        self.function.execution_role_arn = None  # Will be auto-generated
        return self.function
    
    # Code configuration
    def code_from_file(self, file_path: str):
        """Set code from local file - chainable"""
        self.function.code_zip_file = file_path
        self.function.code_s3_bucket = None
        self.function.code_s3_key = None
        return self.function
    
    def code_from_s3(self, bucket: str, key: str):
        """Set code from S3 bucket - chainable"""
        self.function.code_s3_bucket = bucket
        self.function.code_s3_key = key
        self.function.code_zip_file = None
        return self.function
    
    def code_from_string(self, code_string: str, filename: str = "lambda_function.py"):
        """Set code from string - chainable"""
        # Store code string to be packaged later
        self.function._code_string = code_string
        self.function._code_filename = filename
        self.function.code_zip_file = None
        self.function.code_s3_bucket = None
        self.function.code_s3_key = None
        return self.function
    
    # Description and metadata
    def description(self, desc: str):
        """Set function description - chainable"""
        self.function.description = desc
        return self.function
    
    def tag(self, key: str, value: str):
        """Add a tag - chainable"""
        self.function.tags[key] = value
        return self.function
    
    def tags(self, tags_dict: Dict[str, str]):
        """Add multiple tags - chainable"""
        self.function.tags.update(tags_dict)
        return self.function
    
    # Quick setup methods
    def quick_api(self, runtime: str = "python3.11", memory: int = 256):
        """Quick API setup - chainable"""
        if runtime.startswith("python"):
            self.python(runtime.replace("python", ""))
        elif runtime.startswith("nodejs"):
            self.nodejs(runtime.replace("nodejs", "").replace(".x", ""))
        
        return self.memory(memory).timeout(30).api_gateway()
    
    def quick_scheduler(self, schedule_expr: str, runtime: str = "python3.11", memory: int = 128):
        """Quick scheduled function setup - chainable"""
        if runtime.startswith("python"):
            self.python(runtime.replace("python", ""))
        elif runtime.startswith("nodejs"):
            self.nodejs(runtime.replace("nodejs", "").replace(".x", ""))
        
        return self.memory(memory).timeout(300).schedule(schedule_expr)
    
    def quick_processor(self, queue_arn: str, runtime: str = "python3.11", memory: int = 512):
        """Quick SQS processor setup - chainable"""
        if runtime.startswith("python"):
            self.python(runtime.replace("python", ""))
        elif runtime.startswith("nodejs"):
            self.nodejs(runtime.replace("nodejs", "").replace(".x", ""))
        
        return self.memory(memory).timeout(300).sqs_trigger(queue_arn)
    
    # Validation methods
    def validate_configuration(self) -> Dict[str, Any]:
        """Validate the current Lambda configuration."""
        errors = []
        warnings = []
        
        # Required fields
        if not self.function.function_name:
            errors.append("Function name is required")
        
        if self.function.deployment_package_type == "Zip":
            if not self.function.runtime:
                errors.append("Runtime is required for ZIP packages")
            if not self.function.handler:
                errors.append("Handler is required for ZIP packages")
        elif self.function.deployment_package_type == "Image":
            if not self.function.container_image_uri and not hasattr(self.function, 'container_template'):
                errors.append("Container image URI is required for Image packages")
        
        # Memory validation
        if self.function.memory_size < 128 or self.function.memory_size > 10240:
            errors.append("Memory size must be between 128 and 10240 MB")
        
        # Timeout validation
        if self.function.timeout_seconds < 1 or self.function.timeout_seconds > 900:
            errors.append("Timeout must be between 1 and 900 seconds")
        
        # VPC validation
        if self.function.vpc_config:
            if not self.function.security_group_ids:
                errors.append("Security group IDs are required for VPC configuration")
            if not self.function.subnet_ids:
                errors.append("Subnet IDs are required for VPC configuration")
        
        # Code source validation
        code_sources = [
            bool(self.function.code_zip_file),
            bool(self.function.code_s3_bucket and self.function.code_s3_key),
            bool(self.function.container_image_uri),
            bool(hasattr(self.function, '_code_string'))
        ]
        
        if sum(code_sources) == 0:
            errors.append("At least one code source must be specified")
        elif sum(code_sources) > 1:
            warnings.append("Multiple code sources specified, only one will be used")
        
        # Performance warnings
        if self.function.memory_size > 3008 and self.function.timeout_seconds < 300:
            warnings.append("High memory allocation with low timeout may be inefficient")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }
    
    def get_configuration_summary(self) -> Dict[str, Any]:
        """Get a summary of the current configuration."""
        return {
            'function_name': self.function.function_name,
            'runtime': self.function.runtime,
            'handler': self.function.handler,
            'memory_size': f"{self.function.memory_size} MB",
            'timeout': f"{self.function.timeout_seconds} seconds",
            'package_type': self.function.deployment_package_type,
            'environment_variables': len(self.function.environment_variables),
            'vpc_configured': bool(self.function.vpc_config),
            'api_gateway_integration': self.function.api_gateway_integration,
            'triggers': len(self.function.trigger_configurations),
            'execution_role': bool(self.function.execution_role_arn),
            'description': bool(self.function.description),
            'tags': len(self.function.tags)
        }
    
    def get_estimated_cost(self, monthly_requests: int = 1000000, avg_duration_ms: int = 100) -> Dict[str, Any]:
        """Get estimated monthly cost based on current configuration."""
        # AWS Lambda pricing (approximate, varies by region)
        request_cost_per_million = 0.20
        compute_cost_per_gb_second = 0.0000166667
        
        # Calculate costs
        gb_memory = self.function.memory_size / 1024
        duration_seconds = avg_duration_ms / 1000
        gb_seconds_per_request = gb_memory * duration_seconds
        total_gb_seconds = gb_seconds_per_request * monthly_requests
        
        compute_cost = total_gb_seconds * compute_cost_per_gb_second
        request_cost = (monthly_requests / 1000000) * request_cost_per_million
        
        # Free tier
        free_tier_requests = 1000000
        free_tier_gb_seconds = 400000
        
        billable_requests = max(0, monthly_requests - free_tier_requests)
        billable_gb_seconds = max(0, total_gb_seconds - free_tier_gb_seconds)
        
        free_tier_request_cost = (billable_requests / 1000000) * request_cost_per_million
        free_tier_compute_cost = billable_gb_seconds * compute_cost_per_gb_second
        
        return {
            'monthly_requests': monthly_requests,
            'memory_size_mb': self.function.memory_size,
            'avg_duration_ms': avg_duration_ms,
            'total_cost': compute_cost + request_cost,
            'total_cost_with_free_tier': free_tier_compute_cost + free_tier_request_cost,
            'free_tier_savings': (compute_cost + request_cost) - (free_tier_compute_cost + free_tier_request_cost),
            'breakdown': {
                'compute_cost': compute_cost,
                'request_cost': request_cost,
                'gb_seconds_per_month': total_gb_seconds
            }
        }