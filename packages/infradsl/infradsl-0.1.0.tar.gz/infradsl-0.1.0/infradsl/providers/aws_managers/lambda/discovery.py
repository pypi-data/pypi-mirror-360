"""
Lambda Resource Discovery and Monitoring

This module handles Lambda function discovery, infrastructure change detection,
cost estimation, and preview generation.
"""

from typing import Dict, Any, List, Optional
import json


class LambdaDiscoveryManager:
    """
    Lambda Resource Discovery and Monitoring
    
    Handles:
    - Existing function discovery and filtering
    - Infrastructure change detection
    - Cost estimation and analysis
    - Preview generation and formatting
    - Function state monitoring
    """
    
    def __init__(self, aws_client):
        """Initialize the discovery manager with AWS client."""
        self.aws_client = aws_client
    
    def discover_existing_functions(self, name_filter: Optional[str] = None) -> Dict[str, Dict[str, Any]]:
        """
        Discover existing Lambda functions.
        
        Args:
            name_filter: Optional function name filter
            
        Returns:
            Dictionary mapping function names to their information
        """
        try:
            functions = {}
            
            # List all functions
            paginator = self.aws_client.lambda_client.get_paginator('list_functions')
            
            for page in paginator.paginate():
                for func in page.get('Functions', []):
                    func_name = func['FunctionName']
                    
                    # Apply name filter if provided
                    if name_filter and name_filter not in func_name:
                        continue
                    
                    functions[func_name] = {
                        'name': func_name,
                        'arn': func['FunctionArn'],
                        'runtime': func.get('Runtime'),
                        'handler': func.get('Handler'),
                        'memory_size': func.get('MemorySize', 128),
                        'timeout': func.get('Timeout', 3),
                        'package_type': func.get('PackageType', 'Zip'),
                        'last_modified': func.get('LastModified'),
                        'code_size': func.get('CodeSize', 0),
                        'state': func.get('State'),
                        'environment': func.get('Environment', {}).get('Variables', {})
                    }
            
            return functions
            
        except Exception as e:
            print(f"❌ Failed to discover Lambda functions: {str(e)}")
            return {}
    
    def get_function_details(self, function_name: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a specific function.
        
        Args:
            function_name: Name of the function
            
        Returns:
            Function details or None if not found
        """
        try:
            response = self.aws_client.lambda_client.get_function(FunctionName=function_name)
            
            configuration = response['Configuration']
            code = response.get('Code', {})
            
            return {
                'configuration': configuration,
                'code': code,
                'concurrency': response.get('Concurrency', {}),
                'tags': response.get('Tags', {})
            }
            
        except Exception:
            return None
    
    def analyze_infrastructure_changes(
        self,
        function_name: str,
        current_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Analyze what changes will be made to infrastructure.
        
        Args:
            function_name: Name of the function
            current_config: Current function configuration
            
        Returns:
            Analysis of changes to be made
        """
        existing_functions = self.discover_existing_functions(function_name)
        
        function_exists = function_name in existing_functions
        to_create = [] if function_exists else [function_name]
        to_keep = [function_name] if function_exists else []
        to_remove = []  # Lambda typically doesn't remove other functions
        to_update = []
        
        # If function exists, analyze what will be updated
        if function_exists:
            existing = existing_functions[function_name]
            updates = []
            
            if existing.get('runtime') != current_config.get('runtime'):
                updates.append(f"Runtime: {existing.get('runtime')} → {current_config.get('runtime')}")
            
            if existing.get('memory_size') != current_config.get('memory_size'):
                updates.append(f"Memory: {existing.get('memory_size')}MB → {current_config.get('memory_size')}MB")
            
            if existing.get('timeout') != current_config.get('timeout'):
                updates.append(f"Timeout: {existing.get('timeout')}s → {current_config.get('timeout')}s")
            
            if existing.get('handler') != current_config.get('handler'):
                updates.append(f"Handler: {existing.get('handler')} → {current_config.get('handler')}")
            
            if updates:
                to_update = updates
        
        return {
            'function_exists': function_exists,
            'to_create': to_create,
            'to_keep': to_keep,
            'to_remove': to_remove,
            'to_update': to_update,
            'existing_functions': existing_functions
        }
    
    def estimate_monthly_cost(
        self,
        memory_size: int = 128,
        timeout: int = 30,
        monthly_requests: int = 1000000,
        avg_duration_ms: int = 100
    ) -> Dict[str, Any]:
        """
        Estimate monthly cost for Lambda function.
        
        Args:
            memory_size: Memory allocation in MB
            timeout: Function timeout in seconds
            monthly_requests: Estimated monthly requests
            avg_duration_ms: Average execution duration in milliseconds
            
        Returns:
            Cost estimation breakdown
        """
        # AWS Lambda pricing (approximate, varies by region)
        request_cost_per_million = 0.20  # $0.20 per 1M requests
        compute_cost_per_gb_second = 0.0000166667  # Per GB-second
        
        # Calculate compute cost
        gb_memory = memory_size / 1024
        duration_seconds = avg_duration_ms / 1000
        gb_seconds_per_request = gb_memory * duration_seconds
        total_gb_seconds = gb_seconds_per_request * monthly_requests
        
        compute_cost = total_gb_seconds * compute_cost_per_gb_second
        request_cost = (monthly_requests / 1000000) * request_cost_per_million
        
        # Free tier considerations
        free_tier_requests = 1000000  # 1M requests per month
        free_tier_gb_seconds = 400000  # 400K GB-seconds per month
        
        # Apply free tier
        billable_requests = max(0, monthly_requests - free_tier_requests)
        billable_gb_seconds = max(0, total_gb_seconds - free_tier_gb_seconds)
        
        free_tier_request_cost = (billable_requests / 1000000) * request_cost_per_million
        free_tier_compute_cost = billable_gb_seconds * compute_cost_per_gb_second
        
        total_cost = compute_cost + request_cost
        total_cost_with_free_tier = free_tier_compute_cost + free_tier_request_cost
        
        return {
            'memory_size_mb': memory_size,
            'monthly_requests': monthly_requests,
            'avg_duration_ms': avg_duration_ms,
            'compute_cost': compute_cost,
            'request_cost': request_cost,
            'total_cost': total_cost,
            'total_cost_with_free_tier': total_cost_with_free_tier,
            'free_tier_savings': total_cost - total_cost_with_free_tier,
            'gb_seconds_per_month': total_gb_seconds,
            'cost_breakdown': {
                'requests': f"${request_cost:.2f} ({monthly_requests:,} requests)",
                'compute': f"${compute_cost:.2f} ({total_gb_seconds:,.0f} GB-seconds)",
                'free_tier_discount': f"-${total_cost - total_cost_with_free_tier:.2f}"
            }
        }
    
    def generate_preview_output(
        self,
        function_name: str,
        config: Dict[str, Any],
        changes: Dict[str, Any],
        cost_estimate: Dict[str, Any]
    ) -> str:
        """
        Generate formatted preview output.
        
        Args:
            function_name: Name of the function
            config: Function configuration
            changes: Infrastructure changes analysis
            cost_estimate: Cost estimation
            
        Returns:
            Formatted preview string
        """
        output = []
        
        output.append(f"\n🔮 AWS Lambda Function Configuration Preview")
        
        # Show functions to create
        if changes['to_create']:
            output.append(f"╭─ ⚡ Lambda Functions to CREATE: {len(changes['to_create'])}")
            output.append(f"├─ 🆕 {function_name}")
            output.append(f"│  ├─ ⚡ Runtime: {config.get('runtime', 'python3.11')}")
            output.append(f"│  ├─ 📝 Handler: {config.get('handler', 'lambda_function.lambda_handler')}")
            output.append(f"│  ├─ 💾 Memory: {config.get('memory_size', 128)} MB")
            output.append(f"│  ├─ ⏱️  Timeout: {config.get('timeout', 30)} seconds")
            
            if config.get('package_type') == 'Image':
                output.append(f"│  ├─ 🐳 Package: Container Image")
                if config.get('container_image_uri'):
                    output.append(f"│  ├─ 📦 Image: {config['container_image_uri']}")
            else:
                output.append(f"│  ├─ 📦 Package: ZIP")
            
            if config.get('environment_variables'):
                output.append(f"│  ├─ 🔧 Environment Variables: {len(config['environment_variables'])}")
            
            if config.get('api_gateway_integration'):
                output.append(f"│  ├─ 🌐 API Gateway: Enabled")
            
            if config.get('trigger_configurations'):
                output.append(f"│  ├─ 🔗 Triggers: {len(config['trigger_configurations'])}")
            
            output.append(f"│  ├─ 🏷️  Tags: {len(config.get('tags', {}))}")
            output.append(f"│  └─ ⚡ Serverless: Full Lambda API")
        
        # Show functions to update
        if changes['to_update']:
            output.append(f"├─ 🔄 Lambda Functions to UPDATE: 1")
            output.append(f"│  ├─ 📝 {function_name}")
            for update in changes['to_update']:
                output.append(f"│  │  ├─ {update}")
        
        if not changes['to_create'] and not changes['to_update']:
            output.append(f"├─ ✨ No changes needed - infrastructure matches configuration")
        
        output.append(f"╰─")
        
        # Cost estimation
        if changes['to_create'] or changes['to_update']:
            output.append(f"\n💰 Estimated Monthly Costs:")
            output.append(f"   ├─ ⚡ Lambda Requests: ${cost_estimate['request_cost']:.2f}")
            output.append(f"   ├─ 💻 Lambda Compute: ${cost_estimate['compute_cost']:.2f}")
            output.append(f"   ├─ 🎁 Free Tier Savings: -${cost_estimate['free_tier_savings']:.2f}")
            output.append(f"   ├─ 💰 Total (with Free Tier): ${cost_estimate['total_cost_with_free_tier']:.2f}")
            output.append(f"   └─ 🎯 AWS Free Tier: 1M requests + 400K GB-seconds/month")
        
        output.append(f"\n✅ Preview completed - no resources were created.")
        
        return "\n".join(output)
    
    def get_function_status(self, function_name: str) -> Dict[str, Any]:
        """
        Get comprehensive function status.
        
        Args:
            function_name: Name of the function
            
        Returns:
            Function status information
        """
        try:
            response = self.aws_client.lambda_client.get_function(FunctionName=function_name)
            configuration = response['Configuration']
            
            # Get function state
            state = configuration.get('State', 'Unknown')
            state_reason = configuration.get('StateReason', '')
            
            # Get latest version info
            version = configuration.get('Version', '$LATEST')
            
            # Check for any errors
            last_update_status = configuration.get('LastUpdateStatus', 'Unknown')
            last_update_reason = configuration.get('LastUpdateStatusReason', '')
            
            return {
                'exists': True,
                'name': function_name,
                'arn': configuration['FunctionArn'],
                'state': state,
                'state_reason': state_reason,
                'last_update_status': last_update_status,
                'last_update_reason': last_update_reason,
                'version': version,
                'runtime': configuration.get('Runtime'),
                'handler': configuration.get('Handler'),
                'memory_size': configuration.get('MemorySize'),
                'timeout': configuration.get('Timeout'),
                'package_type': configuration.get('PackageType'),
                'last_modified': configuration.get('LastModified'),
                'code_size': configuration.get('CodeSize'),
                'environment_variables': len(configuration.get('Environment', {}).get('Variables', {}))
            }
            
        except Exception as e:
            if 'ResourceNotFoundException' in str(e):
                return {'exists': False, 'name': function_name}
            else:
                return {'exists': False, 'name': function_name, 'error': str(e)}
    
    def get_function_metrics(
        self,
        function_name: str,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get CloudWatch metrics for the function.
        
        Args:
            function_name: Name of the function
            start_time: Start time for metrics
            end_time: End time for metrics
            
        Returns:
            Function metrics data
        """
        try:
            from datetime import datetime, timedelta
            
            # Default time range: last 24 hours
            if not end_time:
                end_time = datetime.utcnow()
            else:
                end_time = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
            
            if not start_time:
                start_time = end_time - timedelta(hours=24)
            else:
                start_time = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
            
            metrics = {}
            
            # Get invocation count
            invocations = self.aws_client.cloudwatch.get_metric_statistics(
                Namespace='AWS/Lambda',
                MetricName='Invocations',
                Dimensions=[{'Name': 'FunctionName', 'Value': function_name}],
                StartTime=start_time,
                EndTime=end_time,
                Period=3600,  # 1-hour intervals
                Statistics=['Sum']
            )
            metrics['invocations'] = invocations.get('Datapoints', [])
            
            # Get duration
            duration = self.aws_client.cloudwatch.get_metric_statistics(
                Namespace='AWS/Lambda',
                MetricName='Duration',
                Dimensions=[{'Name': 'FunctionName', 'Value': function_name}],
                StartTime=start_time,
                EndTime=end_time,
                Period=3600,
                Statistics=['Average', 'Maximum']
            )
            metrics['duration'] = duration.get('Datapoints', [])
            
            # Get errors
            errors = self.aws_client.cloudwatch.get_metric_statistics(
                Namespace='AWS/Lambda',
                MetricName='Errors',
                Dimensions=[{'Name': 'FunctionName', 'Value': function_name}],
                StartTime=start_time,
                EndTime=end_time,
                Period=3600,
                Statistics=['Sum']
            )
            metrics['errors'] = errors.get('Datapoints', [])
            
            return {
                'function_name': function_name,
                'time_range': {
                    'start': start_time.isoformat(),
                    'end': end_time.isoformat()
                },
                'metrics': metrics
            }
            
        except Exception as e:
            print(f"❌ Failed to get function metrics: {str(e)}")
            return {}
    
    def list_function_versions(self, function_name: str) -> List[Dict[str, Any]]:
        """
        List all versions of a function.
        
        Args:
            function_name: Name of the function
            
        Returns:
            List of function versions
        """
        try:
            response = self.aws_client.lambda_client.list_versions_by_function(
                FunctionName=function_name
            )
            
            versions = []
            for version_info in response.get('Versions', []):
                versions.append({
                    'version': version_info['Version'],
                    'last_modified': version_info['LastModified'],
                    'code_size': version_info.get('CodeSize', 0),
                    'state': version_info.get('State'),
                    'description': version_info.get('Description', '')
                })
            
            return versions
            
        except Exception as e:
            print(f"❌ Failed to list function versions: {str(e)}")
            return []