"""
CloudFront Functions Core Operations

Handles CloudFront Functions CRUD operations, code validation,
and deployment management.
"""

import json
import hashlib
from typing import Dict, Any, List, Optional
from botocore.exceptions import ClientError


class CloudFrontFunctionsCore:
    """
    Core CloudFront Functions operations
    
    Handles the low-level AWS API calls for CloudFront Functions
    including creation, deployment, testing, and management.
    """
    
    def __init__(self, aws_client):
        """Initialize with AWS client"""
        self.aws_client = aws_client
        self.client = None
        
    def _get_client(self):
        """Get CloudFront service client"""
        if not self.client:
            self.client = self.aws_client.get_client('cloudfront')
        return self.client
    
    def validate_function_code(self, code: str) -> bool:
        """
        Basic validation of CloudFront Function JavaScript code
        
        Args:
            code: JavaScript code string
            
        Returns:
            True if code passes basic validation
            
        Raises:
            ValueError: If code fails validation
        """
        if not code or not code.strip():
            raise ValueError("Function code cannot be empty")
        
        # Basic JavaScript syntax checks
        required_patterns = ['function handler(event)', 'return']
        for pattern in required_patterns:
            if pattern not in code:
                raise ValueError(f"Function code must contain: {pattern}")
        
        # Size limits for CloudFront Functions
        code_size = len(code.encode('utf-8'))
        if code_size > 10240:  # 10KB limit for CloudFront Functions
            raise ValueError(f"Function code size ({code_size} bytes) exceeds 10KB limit")
        
        return True
    
    def create_function(self, name: str, code: str, comment: str = None) -> Dict[str, Any]:
        """
        Create a new CloudFront Function
        
        Args:
            name: Function name
            code: JavaScript code
            comment: Optional comment
            
        Returns:
            Dict containing function metadata
        """
        client = self._get_client()
        
        function_config = {
            'Comment': comment or f"CloudFront Function: {name}",
            'Runtime': 'cloudfront-js-1.0'
        }
        
        try:
            response = client.create_function(
                Name=name,
                FunctionConfig=function_config,
                FunctionCode=code.encode('utf-8')
            )
            
            return {
                'function_arn': response['FunctionSummary']['FunctionMetadata']['FunctionARN'],
                'name': response['FunctionSummary']['Name'],
                'status': response['FunctionSummary']['Status'],
                'etag': response['ETag'],
                'location': response['Location']
            }
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'FunctionAlreadyExists':
                # Function exists, return existing function info
                return self.get_function(name, 'DEVELOPMENT')
            else:
                raise Exception(f"Failed to create CloudFront Function: {str(e)}")
    
    def update_function(self, name: str, code: str, if_match: str) -> Dict[str, Any]:
        """
        Update an existing CloudFront Function
        
        Args:
            name: Function name
            code: New JavaScript code
            if_match: ETag for conditional update
            
        Returns:
            Dict containing updated function metadata
        """
        client = self._get_client()
        
        try:
            response = client.update_function(
                Name=name,
                IfMatch=if_match,
                FunctionConfig={
                    'Comment': f"Updated CloudFront Function: {name}",
                    'Runtime': 'cloudfront-js-1.0'
                },
                FunctionCode=code.encode('utf-8')
            )
            
            return {
                'function_arn': response['FunctionSummary']['FunctionMetadata']['FunctionARN'],
                'name': response['FunctionSummary']['Name'],
                'status': response['FunctionSummary']['Status'],
                'etag': response['ETag']
            }
            
        except ClientError as e:
            raise Exception(f"Failed to update CloudFront Function: {str(e)}")
    
    def publish_function(self, function_name: str, if_match: str) -> Dict[str, Any]:
        """
        Publish CloudFront Function to LIVE stage
        
        Args:
            function_name: Name of the function
            if_match: ETag for conditional publish
            
        Returns:
            Dict containing published function metadata
        """
        client = self._get_client()
        
        try:
            response = client.publish_function(
                Name=function_name,
                IfMatch=if_match
            )
            
            return {
                'function_arn': response['FunctionSummary']['FunctionMetadata']['FunctionARN'],
                'name': response['FunctionSummary']['Name'],
                'status': response['FunctionSummary']['Status'],
                'stage': response['FunctionSummary']['FunctionMetadata']['Stage'],
                'etag': response['ETag'],
                'last_modified_time': response['FunctionSummary']['FunctionMetadata']['LastModifiedTime']
            }
            
        except ClientError as e:
            raise Exception(f"Failed to publish CloudFront Function: {str(e)}")
    
    def get_function(self, name: str, stage: str = 'LIVE') -> Dict[str, Any]:
        """
        Get CloudFront Function details
        
        Args:
            name: Function name
            stage: Function stage (DEVELOPMENT or LIVE)
            
        Returns:
            Dict containing function details
        """
        client = self._get_client()
        
        try:
            response = client.get_function(Name=name, Stage=stage)
            
            return {
                'function_arn': response['FunctionSummary']['FunctionMetadata']['FunctionARN'],
                'name': response['FunctionSummary']['Name'],
                'status': response['FunctionSummary']['Status'],
                'stage': response['FunctionSummary']['FunctionMetadata']['Stage'],
                'code': response['FunctionCode'].decode('utf-8'),
                'etag': response['ETag'],
                'content_type': response['ContentType'],
                'last_modified_time': response['FunctionSummary']['FunctionMetadata']['LastModifiedTime']
            }
            
        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchFunction':
                return None
            raise Exception(f"Failed to get CloudFront Function: {str(e)}")
    
    def describe_function(self, name: str, stage: str = 'LIVE') -> Dict[str, Any]:
        """
        Get CloudFront Function description (metadata only)
        
        Args:
            name: Function name
            stage: Function stage
            
        Returns:
            Dict containing function metadata
        """
        client = self._get_client()
        
        try:
            response = client.describe_function(Name=name, Stage=stage)
            return response
            
        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchFunction':
                return None
            raise Exception(f"Failed to describe CloudFront Function: {str(e)}")
    
    def list_functions(self) -> List[Dict[str, Any]]:
        """
        List all CloudFront Functions
        
        Returns:
            List of function summaries
        """
        client = self._get_client()
        
        try:
            paginator = client.get_paginator('list_functions')
            functions = []
            
            for page in paginator.paginate():
                functions.extend(page.get('FunctionList', {}).get('Items', []))
            
            return functions
            
        except ClientError as e:
            raise Exception(f"Failed to list CloudFront Functions: {str(e)}")
    
    def delete_function(self, name: str, if_match: str) -> Dict[str, Any]:
        """
        Delete a CloudFront Function
        
        Args:
            name: Function name
            if_match: ETag for conditional delete
            
        Returns:
            Dict containing deletion result
        """
        client = self._get_client()
        
        try:
            client.delete_function(Name=name, IfMatch=if_match)
            
            return {
                'name': name,
                'status': 'deleted',
                'deleted': True
            }
            
        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchFunction':
                return {'name': name, 'status': 'not_found', 'deleted': False}
            raise Exception(f"Failed to delete CloudFront Function: {str(e)}")
    
    def test_function(self, name: str, stage: str, event_object: Dict[str, Any]) -> Dict[str, Any]:
        """
        Test a CloudFront Function with sample event data
        
        Args:
            name: Function name
            stage: Function stage
            event_object: Sample event data for testing
            
        Returns:
            Dict containing test results
        """
        client = self._get_client()
        
        try:
            response = client.test_function(
                Name=name,
                IfMatch=stage,  # For testing, use stage as ETag
                EventObject=json.dumps(event_object).encode('utf-8')
            )
            
            return {
                'test_result': json.loads(response['TestResult'].decode('utf-8')),
                'compute_utilization': response.get('ComputeUtilization'),
                'function_execution_logs': response.get('FunctionExecutionLogs', []),
                'function_output': response.get('FunctionOutput'),
                'function_summary': response.get('FunctionSummary')
            }
            
        except ClientError as e:
            raise Exception(f"Failed to test CloudFront Function: {str(e)}")
    
    def generate_function_code_hash(self, code: str) -> str:
        """Generate SHA-256 hash of function code for drift detection"""
        return hashlib.sha256(code.encode('utf-8')).hexdigest()
    
    def get_default_viewer_request_code(self) -> str:
        """Get default CloudFront Function code for viewer-request events"""
        return """function handler(event) {
    var request = event.request;
    
    // Add security headers
    request.headers['x-frame-options'] = {value: 'DENY'};
    request.headers['x-content-type-options'] = {value: 'nosniff'};
    request.headers['x-xss-protection'] = {value: '1; mode=block'};
    
    return request;
}"""
    
    def get_default_viewer_response_code(self) -> str:
        """Get default CloudFront Function code for viewer-response events"""
        return """function handler(event) {
    var response = event.response;
    var headers = response.headers;
    
    // Add security headers to response
    headers['strict-transport-security'] = {value: 'max-age=31536000; includeSubDomains'};
    headers['x-frame-options'] = {value: 'DENY'};
    headers['x-content-type-options'] = {value: 'nosniff'};
    headers['x-xss-protection'] = {value: '1; mode=block'};
    headers['referrer-policy'] = {value: 'strict-origin-when-cross-origin'};
    
    return response;
}"""