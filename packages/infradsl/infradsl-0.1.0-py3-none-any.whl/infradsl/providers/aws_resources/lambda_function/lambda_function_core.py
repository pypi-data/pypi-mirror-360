from typing import Dict, Any, List, Optional
from pathlib import Path
import json
import time
from ..base_resource import BaseAwsResource


class LambdaCore(BaseAwsResource):
    def __init__(self, name: str):
        super().__init__(name)

        self.function_name = name
        self.runtime = "python3.11"
        self.handler = "lambda_function.lambda_handler"
        self.memory_size = 128
        self.timeout_seconds = 30
        self.environment_variables = {}
        self.description = ""

        self.container_image_uri = None
        self.container_template = None
        self.container_port = 8080
        self.container_workdir = None

        self.api_gateway_integration = False
        self.api_gateway_cors = True
        self.trigger_configurations = []

        self.execution_role_arn = None
        self.vpc_config = None
        self.security_group_ids = []
        self.subnet_ids = []

        self.deployment_package_type = "Zip"
        self.code_zip_file = None
        self.code_s3_bucket = None
        self.code_s3_key = None

        self.function_arn = None
        self.function_url = None
        self.api_gateway_url = None
        self.last_modified = None
        self.state = None
        self.tags = {}

    def _initialize_managers(self):
        self.lambda_client = None
        self.apigateway_client = None
        self.iam_client = None
        self.container_manager = None

    def _post_authentication_setup(self):
        self.region = self.get_current_region()
        
        self.lambda_client = self.get_lambda_client()
        self.apigateway_client = self.get_apigateway_client()
        self.iam_client = self.get_iam_client()

        if self.container_template:
            from ...container_engines import UniversalContainerManager
            self.container_manager = UniversalContainerManager()

    def get_lambda_client(self):
        try:
            import boto3
            return boto3.client('lambda', region_name=self.region)
        except Exception as e:
            print(f"⚠️  Failed to create Lambda client: {e}")
            return None

    def get_apigateway_client(self):
        try:
            import boto3
            return boto3.client('apigateway', region_name=self.region)
        except Exception as e:
            print(f"⚠️  Failed to create API Gateway client: {e}")
            return None

    def get_iam_client(self):
        try:
            import boto3
            return boto3.client('iam', region_name=self.region)
        except Exception as e:
            print(f"⚠️  Failed to create IAM client: {e}")
            return None
    
    def get_client(self, service_name: str, region: str = None):
        """Get AWS client for specified service"""
        from ..auth_service import AwsAuthenticationService
        return AwsAuthenticationService.get_client(service_name, region or self.region)

    def _get_all_tags(self) -> Dict[str, str]:
        tags = {
            "Name": self.function_name,
            "InfraDSL": "true",
            "ResourceType": "lambda-function"
        }
        tags.update(self.tags)
        return tags

    def _estimate_monthly_cost(self) -> str:
        requests_per_month = 1000000
        avg_duration_ms = 100
        
        request_cost = requests_per_month * 0.0000002
        compute_cost = (requests_per_month * avg_duration_ms / 1000) * (self.memory_size / 1024) * 0.0000166667
        
        total_cost = request_cost + compute_cost
        return f"${total_cost:.2f}"

    def create(self):
        """Create/update Lambda function - delegates to lifecycle mixin"""
        # Import here to avoid circular imports
        from .lambda_function_lifecycle import LambdaFunctionLifecycleMixin
        # Call the lifecycle mixin's create method
        return LambdaFunctionLifecycleMixin.create(self)

    def destroy(self):
        """Destroy Lambda function - delegates to lifecycle mixin"""
        # Import here to avoid circular imports
        from .lambda_function_lifecycle import LambdaFunctionLifecycleMixin
        # Call the lifecycle mixin's destroy method
        return LambdaFunctionLifecycleMixin.destroy(self)

    def preview(self):
        """Preview Lambda function configuration"""
        return {
            "resource_type": "AWS Lambda Function",
            "function_name": self.function_name,
            "runtime": self.runtime,
            "handler": self.handler,
            "memory_size": self.memory_size,
            "timeout_seconds": self.timeout_seconds,
            "environment_variables": self.environment_variables,
            "description": self.description,
            "deployment_package_type": self.deployment_package_type,
            "container_image_uri": self.container_image_uri,
            "api_gateway_integration": self.api_gateway_integration,
            "estimated_monthly_cost": self._estimate_monthly_cost(),
            "triggers_count": len(self.trigger_configurations)
        }
