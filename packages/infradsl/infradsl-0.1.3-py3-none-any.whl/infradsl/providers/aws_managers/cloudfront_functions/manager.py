"""
CloudFront Functions Manager

Coordinates CloudFront Functions operations including creation, deployment,
and association with distributions.
"""

from typing import Dict, Any, List, Optional
from .functions import CloudFrontFunctionsCore
from .associations import CloudFrontFunctionAssociations


class CloudFrontFunctionsManager:
    """
    Main coordinator for CloudFront Functions operations
    
    Manages the lifecycle of CloudFront Functions including:
    - Function creation and deployment
    - Association with distributions
    - Code management and validation
    """
    
    def __init__(self, aws_client):
        """Initialize the CloudFront Functions manager"""
        self.aws_client = aws_client
        self.functions_core = CloudFrontFunctionsCore(aws_client)
        self.associations = CloudFrontFunctionAssociations(aws_client)
        
    def create_function(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new CloudFront Function
        
        Args:
            config: Function configuration including name, code, event_type
            
        Returns:
            Dict containing function ARN, name, and status
        """
        # Validate function code
        self.functions_core.validate_function_code(config['code'])
        
        # Create the function
        function_result = self.functions_core.create_function(
            name=config['name'],
            code=config['code'],
            comment=config.get('comment', f"Managed by InfraDSL: {config['name']}")
        )
        
        # Publish the function to LIVE stage
        publish_result = self.functions_core.publish_function(
            function_name=config['name'],
            if_match=function_result['etag']
        )
        
        return {
            'function_arn': function_result['function_arn'],
            'function_name': config['name'],
            'status': publish_result['status'],
            'stage': 'LIVE',
            'etag': publish_result['etag'],
            'last_modified_time': publish_result['last_modified_time']
        }
    
    def update_function(self, name: str, code: str, if_match: str) -> Dict[str, Any]:
        """Update an existing CloudFront Function"""
        # Validate new code
        self.functions_core.validate_function_code(code)
        
        # Update the function
        update_result = self.functions_core.update_function(name, code, if_match)
        
        # Publish updated function
        publish_result = self.functions_core.publish_function(name, update_result['etag'])
        
        return publish_result
    
    def delete_function(self, name: str, if_match: str) -> Dict[str, Any]:
        """Delete a CloudFront Function"""
        return self.functions_core.delete_function(name, if_match)
    
    def get_function(self, name: str, stage: str = 'LIVE') -> Dict[str, Any]:
        """Get CloudFront Function details"""
        return self.functions_core.get_function(name, stage)
    
    def list_functions(self) -> List[Dict[str, Any]]:
        """List all CloudFront Functions"""
        return self.functions_core.list_functions()
    
    def describe_function(self, name: str, stage: str = 'LIVE') -> Dict[str, Any]:
        """Get detailed information about a CloudFront Function"""
        return self.functions_core.describe_function(name, stage)
    
    def test_function(self, name: str, stage: str, event_object: Dict[str, Any]) -> Dict[str, Any]:
        """Test a CloudFront Function with sample event data"""
        return self.functions_core.test_function(name, stage, event_object)
    
    def associate_with_distribution(self, distribution_id: str, function_associations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Associate CloudFront Functions with a distribution"""
        return self.associations.associate_functions(distribution_id, function_associations)
    
    def discover_existing_functions(self) -> Dict[str, Dict[str, Any]]:
        """Discover existing CloudFront Functions for drift detection"""
        functions = self.list_functions()
        function_map = {}
        
        for func in functions:
            function_name = func['Name']
            # Get detailed information
            details = self.describe_function(function_name, 'LIVE')
            function_map[function_name] = {
                'name': function_name,
                'arn': func['FunctionMetadata']['FunctionARN'],
                'stage': func['FunctionMetadata']['Stage'],
                'status': func['Status'],
                'comment': details.get('FunctionConfig', {}).get('Comment', ''),
                'last_modified': func['FunctionMetadata']['LastModifiedTime'],
                'runtime': details.get('FunctionConfig', {}).get('Runtime', 'cloudfront-js-1.0')
            }
        
        return function_map