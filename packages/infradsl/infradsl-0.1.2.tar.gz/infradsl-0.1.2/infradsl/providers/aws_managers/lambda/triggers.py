"""
Lambda Triggers and Integration Management

This module handles Lambda function triggers, event source mappings,
and integrations with other AWS services.
"""

from typing import Dict, Any, List, Optional
import json


class LambdaTriggersManager:
    """
    Lambda Triggers and Integration Management
    
    Handles:
    - API Gateway integration and configuration
    - Event source mappings (S3, SQS, EventBridge, CloudWatch)
    - Trigger configuration and management
    - Permission setup for various trigger types
    """
    
    def __init__(self, aws_client):
        """Initialize the triggers manager with AWS client."""
        self.aws_client = aws_client
    
    def create_api_gateway_integration(
        self,
        function_name: str,
        api_name: Optional[str] = None,
        stage_name: str = "prod",
        cors_enabled: bool = True,
        api_key_required: bool = False
    ) -> Dict[str, Any]:
        """
        Create API Gateway integration for Lambda function.
        
        Args:
            function_name: Name of the Lambda function
            api_name: Name of the API (defaults to function name + '-api')
            stage_name: Stage name for deployment
            cors_enabled: Whether to enable CORS
            api_key_required: Whether API key is required
            
        Returns:
            API Gateway integration result
        """
        try:
            if not api_name:
                api_name = f"{function_name}-api"
            
            print(f"🌐 Creating API Gateway integration for: {function_name}")
            
            # Create REST API
            api_response = self.aws_client.apigateway.create_rest_api(
                name=api_name,
                description=f"API for Lambda function {function_name}",
                endpointConfiguration={'types': ['REGIONAL']}
            )
            
            api_id = api_response['id']
            
            # Get root resource
            resources_response = self.aws_client.apigateway.get_resources(restApiId=api_id)
            root_resource_id = None
            
            for resource in resources_response['items']:
                if resource['path'] == '/':
                    root_resource_id = resource['id']
                    break
            
            if not root_resource_id:
                raise Exception("Could not find root resource")
            
            # Create proxy resource
            proxy_resource = self.aws_client.apigateway.create_resource(
                restApiId=api_id,
                parentId=root_resource_id,
                pathPart='{proxy+}'
            )
            
            proxy_resource_id = proxy_resource['id']
            
            # Create ANY method for proxy resource
            self._create_api_method(
                api_id, proxy_resource_id, 'ANY', function_name,
                cors_enabled, api_key_required
            )
            
            # Create ANY method for root resource (for requests to /)
            self._create_api_method(
                api_id, root_resource_id, 'ANY', function_name,
                cors_enabled, api_key_required
            )
            
            # Deploy API
            deployment = self.aws_client.apigateway.create_deployment(
                restApiId=api_id,
                stageName=stage_name
            )
            
            # Add permission for API Gateway to invoke Lambda
            from .security import LambdaSecurityManager
            security_manager = LambdaSecurityManager(self.aws_client)
            
            source_arn = f"arn:aws:execute-api:{self.aws_client.region_name}:{self.aws_client.account_id}:{api_id}/*/*"
            
            security_manager.create_resource_based_policy(
                function_name=function_name,
                principal="apigateway.amazonaws.com",
                source_arn=source_arn,
                statement_id="allow-api-gateway"
            )
            
            api_url = f"https://{api_id}.execute-api.{self.aws_client.region_name}.amazonaws.com/{stage_name}"
            
            print(f"✅ API Gateway integration created: {api_url}")
            
            return {
                'api_id': api_id,
                'api_name': api_name,
                'api_url': api_url,
                'stage_name': stage_name,
                'deployment_id': deployment['id']
            }
            
        except Exception as e:
            print(f"❌ Failed to create API Gateway integration: {str(e)}")
            raise
    
    def _create_api_method(
        self,
        api_id: str,
        resource_id: str,
        http_method: str,
        function_name: str,
        cors_enabled: bool,
        api_key_required: bool
    ):
        """Create API Gateway method with Lambda integration."""
        # Create method
        self.aws_client.apigateway.put_method(
            restApiId=api_id,
            resourceId=resource_id,
            httpMethod=http_method,
            authorizationType='NONE',
            apiKeyRequired=api_key_required
        )
        
        # Get Lambda function ARN
        function_response = self.aws_client.lambda_client.get_function(FunctionName=function_name)
        function_arn = function_response['Configuration']['FunctionArn']
        
        # Create integration
        integration_uri = f"arn:aws:apigateway:{self.aws_client.region_name}:lambda:path/2015-03-31/functions/{function_arn}/invocations"
        
        self.aws_client.apigateway.put_integration(
            restApiId=api_id,
            resourceId=resource_id,
            httpMethod=http_method,
            type='AWS_PROXY',
            integrationHttpMethod='POST',
            uri=integration_uri
        )
        
        # Add CORS headers if enabled
        if cors_enabled:
            self._add_cors_headers(api_id, resource_id, http_method)
    
    def _add_cors_headers(self, api_id: str, resource_id: str, http_method: str):
        """Add CORS headers to API Gateway method."""
        # Add CORS response headers
        self.aws_client.apigateway.put_method_response(
            restApiId=api_id,
            resourceId=resource_id,
            httpMethod=http_method,
            statusCode='200',
            responseParameters={
                'method.response.header.Access-Control-Allow-Origin': False,
                'method.response.header.Access-Control-Allow-Headers': False,
                'method.response.header.Access-Control-Allow-Methods': False
            }
        )
        
        # Add integration response with CORS headers
        self.aws_client.apigateway.put_integration_response(
            restApiId=api_id,
            resourceId=resource_id,
            httpMethod=http_method,
            statusCode='200',
            responseParameters={
                'method.response.header.Access-Control-Allow-Origin': "'*'",
                'method.response.header.Access-Control-Allow-Headers': "'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'",
                'method.response.header.Access-Control-Allow-Methods': "'GET,POST,PUT,DELETE,OPTIONS'"
            }
        )
    
    def create_s3_trigger(
        self,
        function_name: str,
        bucket_name: str,
        events: List[str] = None,
        prefix: str = "",
        suffix: str = ""
    ) -> Dict[str, Any]:
        """
        Create S3 bucket notification trigger for Lambda function.
        
        Args:
            function_name: Name of the Lambda function
            bucket_name: S3 bucket name
            events: List of S3 events (defaults to ['s3:ObjectCreated:*'])
            prefix: Object key prefix filter
            suffix: Object key suffix filter
            
        Returns:
            S3 trigger configuration result
        """
        try:
            if not events:
                events = ['s3:ObjectCreated:*']
            
            print(f"🪣 Creating S3 trigger for bucket: {bucket_name}")
            
            # Get function ARN
            function_response = self.aws_client.lambda_client.get_function(FunctionName=function_name)
            function_arn = function_response['Configuration']['FunctionArn']
            
            # Add permission for S3 to invoke Lambda
            from .security import LambdaSecurityManager
            security_manager = LambdaSecurityManager(self.aws_client)
            
            source_arn = f"arn:aws:s3:::{bucket_name}"
            
            security_manager.create_resource_based_policy(
                function_name=function_name,
                principal="s3.amazonaws.com",
                source_arn=source_arn,
                statement_id=f"allow-s3-{bucket_name}"
            )
            
            # Configure bucket notification
            notification_config = {
                'LambdaConfigurations': [
                    {
                        'Id': f"{function_name}-trigger",
                        'LambdaFunctionArn': function_arn,
                        'Events': events
                    }
                ]
            }
            
            # Add filter if specified
            if prefix or suffix:
                filter_rules = []
                if prefix:
                    filter_rules.append({'Name': 'prefix', 'Value': prefix})
                if suffix:
                    filter_rules.append({'Name': 'suffix', 'Value': suffix})
                
                notification_config['LambdaConfigurations'][0]['Filter'] = {
                    'Key': {'FilterRules': filter_rules}
                }
            
            self.aws_client.s3.put_bucket_notification_configuration(
                Bucket=bucket_name,
                NotificationConfiguration=notification_config
            )
            
            print(f"✅ S3 trigger created for bucket: {bucket_name}")
            
            return {
                'bucket_name': bucket_name,
                'events': events,
                'prefix': prefix,
                'suffix': suffix,
                'function_arn': function_arn
            }
            
        except Exception as e:
            print(f"❌ Failed to create S3 trigger: {str(e)}")
            raise
    
    def create_sqs_trigger(
        self,
        function_name: str,
        queue_arn: str,
        batch_size: int = 10,
        maximum_batching_window: int = 0
    ) -> Dict[str, Any]:
        """
        Create SQS queue trigger for Lambda function.
        
        Args:
            function_name: Name of the Lambda function
            queue_arn: SQS queue ARN
            batch_size: Batch size for processing
            maximum_batching_window: Maximum batching window in seconds
            
        Returns:
            SQS trigger configuration result
        """
        try:
            print(f"📬 Creating SQS trigger for queue: {queue_arn}")
            
            # Create event source mapping
            mapping_config = {
                'EventSourceArn': queue_arn,
                'FunctionName': function_name,
                'BatchSize': batch_size,
                'MaximumBatchingWindowInSeconds': maximum_batching_window
            }
            
            response = self.aws_client.lambda_client.create_event_source_mapping(**mapping_config)
            
            print(f"✅ SQS trigger created with UUID: {response['UUID']}")
            
            return {
                'uuid': response['UUID'],
                'queue_arn': queue_arn,
                'batch_size': batch_size,
                'state': response.get('State'),
                'function_arn': response.get('FunctionArn')
            }
            
        except Exception as e:
            print(f"❌ Failed to create SQS trigger: {str(e)}")
            raise
    
    def create_eventbridge_trigger(
        self,
        function_name: str,
        rule_name: str,
        schedule_expression: Optional[str] = None,
        event_pattern: Optional[Dict[str, Any]] = None,
        description: str = ""
    ) -> Dict[str, Any]:
        """
        Create EventBridge (CloudWatch Events) trigger for Lambda function.
        
        Args:
            function_name: Name of the Lambda function
            rule_name: EventBridge rule name
            schedule_expression: Schedule expression (for scheduled events)
            event_pattern: Event pattern (for event-driven triggers)
            description: Rule description
            
        Returns:
            EventBridge trigger configuration result
        """
        try:
            print(f"📅 Creating EventBridge trigger: {rule_name}")
            
            # Create EventBridge rule
            rule_config = {
                'Name': rule_name,
                'State': 'ENABLED'
            }
            
            if description:
                rule_config['Description'] = description
            
            if schedule_expression:
                rule_config['ScheduleExpression'] = schedule_expression
            elif event_pattern:
                rule_config['EventPattern'] = json.dumps(event_pattern)
            else:
                raise ValueError("Either schedule_expression or event_pattern must be provided")
            
            rule_response = self.aws_client.events.put_rule(**rule_config)
            rule_arn = rule_response['RuleArn']
            
            # Get function ARN
            function_response = self.aws_client.lambda_client.get_function(FunctionName=function_name)
            function_arn = function_response['Configuration']['FunctionArn']
            
            # Add Lambda as target
            self.aws_client.events.put_targets(
                Rule=rule_name,
                Targets=[
                    {
                        'Id': '1',
                        'Arn': function_arn
                    }
                ]
            )
            
            # Add permission for EventBridge to invoke Lambda
            from .security import LambdaSecurityManager
            security_manager = LambdaSecurityManager(self.aws_client)
            
            security_manager.create_resource_based_policy(
                function_name=function_name,
                principal="events.amazonaws.com",
                source_arn=rule_arn,
                statement_id=f"allow-eventbridge-{rule_name}"
            )
            
            print(f"✅ EventBridge trigger created: {rule_name}")
            
            return {
                'rule_name': rule_name,
                'rule_arn': rule_arn,
                'function_arn': function_arn,
                'schedule_expression': schedule_expression,
                'event_pattern': event_pattern
            }
            
        except Exception as e:
            print(f"❌ Failed to create EventBridge trigger: {str(e)}")
            raise
    
    def create_cloudwatch_logs_trigger(
        self,
        function_name: str,
        log_group_name: str,
        filter_name: str,
        filter_pattern: str = ""
    ) -> Dict[str, Any]:
        """
        Create CloudWatch Logs trigger for Lambda function.
        
        Args:
            function_name: Name of the Lambda function
            log_group_name: CloudWatch log group name
            filter_name: Log filter name
            filter_pattern: Log filter pattern
            
        Returns:
            CloudWatch Logs trigger configuration result
        """
        try:
            print(f"📝 Creating CloudWatch Logs trigger for: {log_group_name}")
            
            # Get function ARN
            function_response = self.aws_client.lambda_client.get_function(FunctionName=function_name)
            function_arn = function_response['Configuration']['FunctionArn']
            
            # Add permission for CloudWatch Logs to invoke Lambda
            from .security import LambdaSecurityManager
            security_manager = LambdaSecurityManager(self.aws_client)
            
            source_arn = f"arn:aws:logs:{self.aws_client.region_name}:{self.aws_client.account_id}:log-group:{log_group_name}:*"
            
            security_manager.create_resource_based_policy(
                function_name=function_name,
                principal="logs.amazonaws.com",
                source_arn=source_arn,
                statement_id=f"allow-cloudwatch-logs-{filter_name}"
            )
            
            # Create subscription filter
            self.aws_client.logs.put_subscription_filter(
                logGroupName=log_group_name,
                filterName=filter_name,
                filterPattern=filter_pattern,
                destinationArn=function_arn
            )
            
            print(f"✅ CloudWatch Logs trigger created: {filter_name}")
            
            return {
                'log_group_name': log_group_name,
                'filter_name': filter_name,
                'filter_pattern': filter_pattern,
                'function_arn': function_arn
            }
            
        except Exception as e:
            print(f"❌ Failed to create CloudWatch Logs trigger: {str(e)}")
            raise
    
    def delete_api_gateway_integration(self, api_id: str) -> Dict[str, Any]:
        """
        Delete API Gateway integration.
        
        Args:
            api_id: API Gateway REST API ID
            
        Returns:
            Deletion result
        """
        try:
            print(f"🗑️  Deleting API Gateway: {api_id}")
            
            self.aws_client.apigateway.delete_rest_api(restApiId=api_id)
            
            print(f"✅ API Gateway deleted: {api_id}")
            
            return {'deleted': True, 'api_id': api_id}
            
        except Exception as e:
            if 'NotFoundException' in str(e):
                print(f"⚠️  API Gateway not found: {api_id}")
                return {'deleted': False, 'reason': 'API not found'}
            else:
                print(f"❌ Failed to delete API Gateway: {str(e)}")
                raise
    
    def delete_event_source_mapping(self, uuid: str) -> Dict[str, Any]:
        """
        Delete event source mapping.
        
        Args:
            uuid: Event source mapping UUID
            
        Returns:
            Deletion result
        """
        try:
            print(f"🗑️  Deleting event source mapping: {uuid}")
            
            response = self.aws_client.lambda_client.delete_event_source_mapping(UUID=uuid)
            
            print(f"✅ Event source mapping deleted: {uuid}")
            
            return {
                'deleted': True,
                'uuid': uuid,
                'state': response.get('State')
            }
            
        except Exception as e:
            if 'ResourceNotFoundException' in str(e):
                print(f"⚠️  Event source mapping not found: {uuid}")
                return {'deleted': False, 'reason': 'Mapping not found'}
            else:
                print(f"❌ Failed to delete event source mapping: {str(e)}")
                raise
    
    def list_function_triggers(self, function_name: str) -> Dict[str, Any]:
        """
        List all triggers configured for a function.
        
        Args:
            function_name: Name of the Lambda function
            
        Returns:
            List of configured triggers
        """
        try:
            triggers = {
                'api_gateway': [],
                'event_source_mappings': [],
                'eventbridge_rules': [],
                'resource_policies': []
            }
            
            # Get function ARN
            function_response = self.aws_client.lambda_client.get_function(FunctionName=function_name)
            function_arn = function_response['Configuration']['FunctionArn']
            
            # Get event source mappings
            mappings_response = self.aws_client.lambda_client.list_event_source_mappings(
                FunctionName=function_name
            )
            triggers['event_source_mappings'] = mappings_response.get('EventSourceMappings', [])
            
            # Get resource-based policies
            from .security import LambdaSecurityManager
            security_manager = LambdaSecurityManager(self.aws_client)
            
            permissions = security_manager.get_function_permissions(function_name)
            if permissions['has_permissions']:
                triggers['resource_policies'] = permissions['permissions']
            
            return triggers
            
        except Exception as e:
            print(f"❌ Failed to list function triggers: {str(e)}")
            return {}