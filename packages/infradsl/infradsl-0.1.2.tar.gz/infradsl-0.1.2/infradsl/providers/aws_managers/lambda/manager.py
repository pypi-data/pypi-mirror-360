"""
Lambda Manager - Main Orchestrator

This module coordinates all Lambda operations by delegating to specialized managers.
"""

from typing import Dict, Any, List, Optional
from .discovery import LambdaDiscoveryManager
from .security import LambdaSecurityManager
from .deployment import LambdaDeploymentManager
from .triggers import LambdaTriggersManager
from .configuration import LambdaConfigurationManager


class LambdaManager:
    """
    Lambda Manager - Main Orchestrator
    
    Coordinates all Lambda operations by delegating to specialized managers:
    - DiscoveryManager: Resource discovery and monitoring
    - SecurityManager: IAM roles and permissions
    - DeploymentManager: Function deployment and code management
    - TriggersManager: Triggers and integrations
    - ConfigurationManager: DSL methods and configuration
    """
    
    def __init__(self, aws_client, lambda_function):
        """
        Initialize Lambda manager with AWS client and function instance.
        
        Args:
            aws_client: Authenticated AWS client
            lambda_function: Reference to the Lambda function instance
        """
        self.aws_client = aws_client
        self.function = lambda_function
        
        # Initialize specialized managers
        self.discovery_manager = LambdaDiscoveryManager(aws_client)
        self.security_manager = LambdaSecurityManager(aws_client)
        self.deployment_manager = LambdaDeploymentManager(aws_client)
        self.triggers_manager = LambdaTriggersManager(aws_client)
        self.configuration_manager = LambdaConfigurationManager(lambda_function)
    
    def preview(self) -> Dict[str, Any]:
        """Preview what will be created, updated, or removed."""
        # Get current function configuration
        current_config = {
            'runtime': self.function.runtime,
            'handler': self.function.handler,
            'memory_size': self.function.memory_size,
            'timeout': self.function.timeout_seconds,
            'package_type': self.function.deployment_package_type,
            'environment_variables': self.function.environment_variables,
            'api_gateway_integration': self.function.api_gateway_integration,
            'trigger_configurations': self.function.trigger_configurations,
            'tags': self.function.tags
        }
        
        # Analyze infrastructure changes
        changes = self.discovery_manager.analyze_infrastructure_changes(
            self.function.function_name,
            current_config
        )
        
        # Estimate costs
        cost_estimate = self.discovery_manager.estimate_monthly_cost(
            memory_size=self.function.memory_size,
            timeout=self.function.timeout_seconds
        )
        
        # Generate preview output
        preview_output = self.discovery_manager.generate_preview_output(
            self.function.function_name,
            current_config,
            changes,
            cost_estimate
        )
        
        print(preview_output)
        
        return {
            'resource_type': 'aws_lambda_function',
            'function_name': self.function.function_name,
            'changes': changes,
            'cost_estimate': cost_estimate,
            'configuration': self.configuration_manager.get_configuration_summary()
        }
    
    def create(self) -> Dict[str, Any]:
        """Create or update Lambda function and all related resources."""
        print(f"\n⚡ Creating/updating Lambda function: {self.function.function_name}")
        
        try:
            # Validate configuration
            validation = self.configuration_manager.validate_configuration()
            if not validation['valid']:
                raise ValueError(f"Configuration validation failed: {', '.join(validation['errors'])}")
            
            # Step 1: Setup execution role
            execution_role_arn = self._setup_execution_role()
            
            # Step 2: Prepare code package
            code_config = self._prepare_code_package()
            
            # Step 3: Check if function exists
            existing_function = self.discovery_manager.get_function_details(self.function.function_name)
            
            if existing_function:
                # Update existing function
                result = self._update_existing_function(code_config, execution_role_arn)
            else:
                # Create new function
                result = self._create_new_function(code_config, execution_role_arn)
            
            # Step 4: Configure triggers
            trigger_results = self._configure_triggers()
            
            print(f"\n✅ Lambda function deployment completed successfully!")
            print(f"   ├─ Function ARN: {result['function_arn']}")
            print(f"   ├─ Runtime: {self.function.runtime}")
            print(f"   ├─ Memory: {self.function.memory_size} MB")
            print(f"   ├─ Timeout: {self.function.timeout_seconds}s")
            
            if trigger_results:
                print(f"   ├─ Triggers: {len(trigger_results)} configured")
                for trigger in trigger_results:
                    if trigger.get('api_url'):
                        print(f"   │  └─ API URL: {trigger['api_url']}")
            
            print(f"   └─ Status: {result.get('state', 'Active')}")
            
            # Update function state
            self.function.function_arn = result['function_arn']
            self.function.last_modified = result.get('last_modified')
            self.function.state = result.get('state')
            
            return {
                'success': True,
                'function_arn': result['function_arn'],
                'function_name': self.function.function_name,
                'state': result.get('state'),
                'version': result.get('version'),
                'triggers': trigger_results,
                'api_urls': [t.get('api_url') for t in trigger_results if t.get('api_url')]
            }
            
        except Exception as e:
            print(f"❌ Failed to create Lambda function: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def destroy(self) -> Dict[str, Any]:
        """Destroy Lambda function and clean up related resources."""
        print(f"\n🗑️  Destroying Lambda function: {self.function.function_name}")
        
        try:
            results = {'deleted_resources': []}
            
            # Step 1: Get function details to know what to clean up
            function_details = self.discovery_manager.get_function_details(self.function.function_name)
            
            if not function_details:
                print(f"⚠️  Function not found: {self.function.function_name}")
                return {'success': True, 'deleted_resources': []}
            
            # Step 2: Clean up triggers
            triggers = self.triggers_manager.list_function_triggers(self.function.function_name)
            
            # Delete event source mappings
            for mapping in triggers.get('event_source_mappings', []):
                try:
                    self.triggers_manager.delete_event_source_mapping(mapping['UUID'])
                    results['deleted_resources'].append(f"Event source mapping: {mapping['UUID']}")
                except Exception as e:
                    print(f"⚠️  Failed to delete event source mapping: {str(e)}")
            
            # Step 3: Delete the function
            try:
                delete_result = self.deployment_manager.delete_function(self.function.function_name)
                if delete_result['deleted']:
                    results['deleted_resources'].append(f"Function: {self.function.function_name}")
            except Exception as e:
                print(f"⚠️  Function deletion failed: {str(e)}")
            
            # Step 4: Optionally clean up execution role (if auto-generated)
            if not self.function.execution_role_arn:  # Was auto-generated
                role_name = self.security_manager.get_default_execution_role_name(self.function.function_name)
                try:
                    role_result = self.security_manager.delete_execution_role(role_name)
                    if role_result['deleted']:
                        results['deleted_resources'].append(f"Execution role: {role_name}")
                except Exception as e:
                    print(f"⚠️  Execution role cleanup failed: {str(e)}")
            
            print(f"\n✅ Lambda function destruction completed!")
            if results['deleted_resources']:
                print(f"   └─ Deleted: {', '.join(results['deleted_resources'])}")
            
            return {'success': True, **results}
            
        except Exception as e:
            print(f"❌ Failed to destroy Lambda function: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def status(self) -> Dict[str, Any]:
        """Get comprehensive status of the Lambda function."""
        return self.discovery_manager.get_function_status(self.function.function_name)
    
    def logs(self, start_time: Optional[str] = None, end_time: Optional[str] = None, limit: int = 100):
        """Get recent logs from CloudWatch for the function."""
        log_group_name = f"/aws/lambda/{self.function.function_name}"
        
        try:
            # Use CloudWatch logs client to get recent logs
            import boto3
            logs_client = boto3.client('logs', region_name=self.aws_client.region_name)
            
            kwargs = {
                'logGroupName': log_group_name,
                'limit': limit,
                'startFromHead': False
            }
            
            if start_time:
                from datetime import datetime
                start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
                kwargs['startTime'] = int(start_dt.timestamp() * 1000)
            
            if end_time:
                from datetime import datetime
                end_dt = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
                kwargs['endTime'] = int(end_dt.timestamp() * 1000)
            
            response = logs_client.filter_log_events(**kwargs)
            
            logs = []
            for event in response.get('events', []):
                from datetime import datetime
                logs.append({
                    'timestamp': datetime.fromtimestamp(event['timestamp'] / 1000).isoformat(),
                    'message': event['message'].strip(),
                    'log_stream': event['logStreamName']
                })
            
            return logs
            
        except Exception as e:
            print(f"❌ Failed to get function logs: {str(e)}")
            return []
    
    def invoke(self, payload: Optional[Dict[str, Any]] = None, invocation_type: str = "RequestResponse") -> Dict[str, Any]:
        """
        Invoke the Lambda function.
        
        Args:
            payload: JSON payload to send to the function
            invocation_type: Synchronous (RequestResponse) or asynchronous (Event)
            
        Returns:
            Invocation result
        """
        try:
            import json
            
            invoke_params = {
                'FunctionName': self.function.function_name,
                'InvocationType': invocation_type
            }
            
            if payload:
                invoke_params['Payload'] = json.dumps(payload)
            
            response = self.aws_client.lambda_client.invoke(**invoke_params)
            
            result = {
                'status_code': response['StatusCode'],
                'executed_version': response.get('ExecutedVersion'),
                'log_result': response.get('LogResult')
            }
            
            if 'Payload' in response:
                payload_data = response['Payload'].read()
                if payload_data:
                    result['payload'] = json.loads(payload_data.decode('utf-8'))
            
            return result
            
        except Exception as e:
            print(f"❌ Failed to invoke function: {str(e)}")
            return {'error': str(e)}
    
    def _setup_execution_role(self) -> str:
        """Setup or validate execution role."""
        if self.function.execution_role_arn:
            # Validate existing role
            validation = self.security_manager.validate_execution_role(self.function.execution_role_arn)
            if not validation['valid']:
                raise Exception(f"Invalid execution role: {validation.get('error')}")
            return self.function.execution_role_arn
        
        # Create auto-generated role
        role_name = self.security_manager.get_default_execution_role_name(self.function.function_name)
        
        # Determine additional policies based on configuration
        additional_policies = []
        if self.function.vpc_config:
            additional_policies.append('arn:aws:iam::aws:policy/service-role/AWSLambdaVPCAccessExecutionRole')
        
        role_result = self.security_manager.create_execution_role(
            role_name=role_name,
            additional_policies=additional_policies,
            tags=self._get_all_tags()
        )
        
        return role_result['role_arn']
    
    def _prepare_code_package(self) -> Dict[str, Any]:
        """Prepare code package for deployment."""
        if self.function.deployment_package_type == "Image":
            if self.function.container_image_uri:
                return {'ImageUri': self.function.container_image_uri}
            else:
                raise ValueError("Container image URI is required for Image package type")
        
        # ZIP package
        if hasattr(self.function, '_code_string'):
            # Code from string
            zip_bytes = self.deployment_manager.prepare_code_from_string(
                self.function._code_string,
                self.function._code_filename
            )
            return {'ZipFile': zip_bytes}
        
        elif self.function.code_zip_file:
            # Code from file/directory
            zip_bytes = self.deployment_manager.prepare_zip_package(self.function.code_zip_file)
            return {'ZipFile': zip_bytes}
        
        elif self.function.code_s3_bucket and self.function.code_s3_key:
            # Code from S3
            return {
                'S3Bucket': self.function.code_s3_bucket,
                'S3Key': self.function.code_s3_key
            }
        
        else:
            raise ValueError("No code source specified")
    
    def _create_new_function(self, code_config: Dict[str, Any], execution_role_arn: str) -> Dict[str, Any]:
        """Create a new Lambda function."""
        return self.deployment_manager.create_function(
            function_name=self.function.function_name,
            runtime=self.function.runtime,
            handler=self.function.handler,
            execution_role_arn=execution_role_arn,
            code=code_config,
            memory_size=self.function.memory_size,
            timeout=self.function.timeout_seconds,
            environment_variables=self.function.environment_variables,
            vpc_config=self.function.vpc_config,
            package_type=self.function.deployment_package_type,
            description=self.function.description,
            tags=self._get_all_tags()
        )
    
    def _update_existing_function(self, code_config: Dict[str, Any], execution_role_arn: str) -> Dict[str, Any]:
        """Update an existing Lambda function."""
        print(f"🔄 Updating existing function...")
        
        # Update code first
        code_result = self.deployment_manager.update_function_code(
            function_name=self.function.function_name,
            code=code_config
        )
        
        # Update configuration
        config_result = self.deployment_manager.update_function_configuration(
            function_name=self.function.function_name,
            runtime=self.function.runtime if self.function.deployment_package_type == "Zip" else None,
            handler=self.function.handler if self.function.deployment_package_type == "Zip" else None,
            memory_size=self.function.memory_size,
            timeout=self.function.timeout_seconds,
            environment_variables=self.function.environment_variables,
            vpc_config=self.function.vpc_config,
            description=self.function.description
        )
        
        return {
            'function_arn': config_result['function_arn'],
            'version': code_result.get('version'),
            'last_modified': config_result.get('last_modified'),
            'state': config_result.get('state')
        }
    
    def _configure_triggers(self) -> List[Dict[str, Any]]:
        """Configure all triggers for the function."""
        trigger_results = []
        
        # API Gateway integration
        if self.function.api_gateway_integration:
            try:
                api_result = self.triggers_manager.create_api_gateway_integration(
                    function_name=self.function.function_name,
                    cors_enabled=getattr(self.function, 'api_gateway_cors', True)
                )
                trigger_results.append(api_result)
                self.function.api_gateway_url = api_result['api_url']
            except Exception as e:
                print(f"⚠️  Failed to create API Gateway integration: {str(e)}")
        
        # Other triggers
        for trigger_config in self.function.trigger_configurations:
            try:
                if trigger_config['type'] == 's3':
                    result = self.triggers_manager.create_s3_trigger(
                        function_name=self.function.function_name,
                        bucket_name=trigger_config['bucket_name'],
                        events=trigger_config['events'],
                        prefix=trigger_config['prefix'],
                        suffix=trigger_config['suffix']
                    )
                    trigger_results.append(result)
                
                elif trigger_config['type'] == 'sqs':
                    result = self.triggers_manager.create_sqs_trigger(
                        function_name=self.function.function_name,
                        queue_arn=trigger_config['queue_arn'],
                        batch_size=trigger_config['batch_size']
                    )
                    trigger_results.append(result)
                
                elif trigger_config['type'] == 'schedule':
                    result = self.triggers_manager.create_eventbridge_trigger(
                        function_name=self.function.function_name,
                        rule_name=f"{self.function.function_name}-schedule",
                        schedule_expression=trigger_config['schedule_expression'],
                        description=trigger_config['description']
                    )
                    trigger_results.append(result)
                
                elif trigger_config['type'] == 'event_pattern':
                    result = self.triggers_manager.create_eventbridge_trigger(
                        function_name=self.function.function_name,
                        rule_name=f"{self.function.function_name}-events",
                        event_pattern=trigger_config['event_pattern'],
                        description=trigger_config['description']
                    )
                    trigger_results.append(result)
                
            except Exception as e:
                print(f"⚠️  Failed to create trigger {trigger_config['type']}: {str(e)}")
        
        return trigger_results
    
    def _get_all_tags(self) -> Dict[str, str]:
        """Get all tags including function tags and defaults."""
        tags = {
            'ManagedBy': 'InfraDSL',
            'Function': self.function.function_name
        }
        tags.update(self.function.tags)
        return tags