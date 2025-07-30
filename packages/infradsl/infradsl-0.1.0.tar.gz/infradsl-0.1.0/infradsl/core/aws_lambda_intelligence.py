"""
Lambda Stateless Intelligence Implementation

Smart resource fingerprinting and predictive change impact analysis for Lambda functions.
Extends the AWS intelligence base with Lambda-specific capabilities.
"""

import boto3
from typing import Dict, Any, List, Optional
from botocore.exceptions import ClientError, NoCredentialsError
from datetime import datetime

from .aws_intelligence_base import AWSIntelligenceBase
from .stateless_intelligence import (
    ResourceType,
    ChangeImpact,
    ChangeImpactAnalysis,
    ResourceHealth
)


class LambdaIntelligence(AWSIntelligenceBase):
    """Lambda-specific stateless intelligence implementation"""
    
    def __init__(self):
        super().__init__(ResourceType.LAMBDA_FUNCTION)
        self.lambda_client = None
    
    def _get_lambda_client(self):
        """Get Lambda client with error handling"""
        if not self.lambda_client:
            try:
                self.lambda_client = boto3.client('lambda')
            except (NoCredentialsError, Exception) as e:
                print(f"⚠️  Failed to create Lambda client: {e}")
                return None
        return self.lambda_client
    
    def _discover_existing_resources(self) -> Dict[str, Dict[str, Any]]:
        """Discover existing Lambda functions"""
        existing_functions = {}
        
        client = self._get_lambda_client()
        if not client:
            return existing_functions
        
        try:
            # Get all Lambda functions
            paginator = client.get_paginator('list_functions')
            
            for page in paginator.paginate():
                for function in page.get('Functions', []):
                    function_name = function['FunctionName']
                    
                    try:
                        # Get detailed function information
                        function_data = self._get_function_details(function_name)
                        existing_functions[function_name] = function_data
                        
                    except Exception as e:
                        print(f"⚠️  Failed to get details for Lambda function {function_name}: {str(e)}")
                        existing_functions[function_name] = {
                            'function_name': function_name,
                            'runtime': function.get('Runtime'),
                            'state': function.get('State', 'unknown'),
                            'error': str(e)
                        }
        
        except Exception as e:
            print(f"⚠️  Failed to discover Lambda functions: {str(e)}")
        
        return existing_functions
    
    def _get_function_details(self, function_name: str) -> Dict[str, Any]:
        """Get comprehensive function details"""
        client = self._get_lambda_client()
        
        # Get function configuration
        function_config = client.get_function(FunctionName=function_name)
        function_data = function_config['Configuration']
        
        # Get function tags
        try:
            tags_response = client.list_tags(Resource=function_data['FunctionArn'])
            tags = tags_response.get('Tags', {})
        except Exception:
            tags = {}
        
        # Get function concurrency
        try:
            concurrency_response = client.get_provisioned_concurrency_config(
                FunctionName=function_name,
                Qualifier='$LATEST'
            )
            provisioned_concurrency = concurrency_response.get('AllocatedConcurrency', 0)
        except ClientError:
            provisioned_concurrency = 0
        
        # Get function event source mappings
        try:
            event_sources = client.list_event_source_mappings(FunctionName=function_name)
            event_source_mappings = event_sources.get('EventSourceMappings', [])
        except Exception:
            event_source_mappings = []
        
        # Get function policy
        try:
            policy_response = client.get_policy(FunctionName=function_name)
            policy = policy_response.get('Policy')
        except ClientError:
            policy = None
        
        return {
            'function_name': function_data['FunctionName'],
            'function_arn': function_data['FunctionArn'],
            'runtime': function_data['Runtime'],
            'role': function_data['Role'],
            'handler': function_data['Handler'],
            'code_size': function_data['CodeSize'],
            'description': function_data.get('Description', ''),
            'timeout': function_data['Timeout'],
            'memory_size': function_data['MemorySize'],
            'last_modified': function_data['LastModified'],
            'code_sha256': function_data['CodeSha256'],
            'version': function_data['Version'],
            'vpc_config': function_data.get('VpcConfig', {}),
            'environment': function_data.get('Environment', {}),
            'dead_letter_config': function_data.get('DeadLetterConfig', {}),
            'kms_key_arn': function_data.get('KMSKeyArn'),
            'tracing_config': function_data.get('TracingConfig', {}),
            'master_arn': function_data.get('MasterArn'),
            'revision_id': function_data['RevisionId'],
            'layers': function_data.get('Layers', []),
            'state': function_data.get('State'),
            'state_reason': function_data.get('StateReason'),
            'state_reason_code': function_data.get('StateReasonCode'),
            'last_update_status': function_data.get('LastUpdateStatus'),
            'file_system_configs': function_data.get('FileSystemConfigs', []),
            'package_type': function_data.get('PackageType', 'Zip'),
            'image_config': function_data.get('ImageConfig', {}),
            'signing_profile_version_arn': function_data.get('SigningProfileVersionArn'),
            'signing_job_arn': function_data.get('SigningJobArn'),
            'architectures': function_data.get('Architectures', ['x86_64']),
            'ephemeral_storage': function_data.get('EphemeralStorage', {}),
            'tags': tags,
            'provisioned_concurrency': provisioned_concurrency,
            'event_source_mappings': event_source_mappings,
            'resource_policy': policy
        }
    
    def _extract_resource_config(self, cloud_state: Dict[str, Any]) -> Dict[str, Any]:
        """Extract configuration from Lambda function state"""
        return {
            'function_name': cloud_state.get('function_name'),
            'runtime': cloud_state.get('runtime'),
            'handler': cloud_state.get('handler'),
            'role': cloud_state.get('role'),
            'memory_size': cloud_state.get('memory_size'),
            'timeout': cloud_state.get('timeout'),
            'package_type': cloud_state.get('package_type', 'Zip'),
            'architectures': cloud_state.get('architectures', ['x86_64']),
            'vpc_config': cloud_state.get('vpc_config', {}),
            'environment_variables': cloud_state.get('environment', {}).get('Variables', {}),
            'dead_letter_config': cloud_state.get('dead_letter_config', {}),
            'tracing_config': cloud_state.get('tracing_config', {}),
            'layers': cloud_state.get('layers', []),
            'ephemeral_storage_size': cloud_state.get('ephemeral_storage', {}).get('Size', 512),
            'tags': cloud_state.get('tags', {})
        }
    
    def _generate_service_specific_fingerprint_data(self, cloud_state: Dict[str, Any]) -> Dict[str, Any]:
        """Generate Lambda-specific fingerprint data"""
        fingerprint_data = {}
        
        # Runtime fingerprint
        runtime = cloud_state.get('runtime', '')
        fingerprint_data['runtime_pattern'] = {
            'language_family': self._get_language_family(runtime),
            'runtime_version': runtime,
            'is_python': runtime.startswith('python'),
            'is_node': runtime.startswith('nodejs'),
            'is_java': runtime.startswith('java'),
            'is_dotnet': runtime.startswith('dotnet'),
            'is_go': runtime.startswith('go'),
            'is_ruby': runtime.startswith('ruby'),
            'is_custom': runtime == 'provided' or runtime.startswith('provided')
        }
        
        # Resource configuration fingerprint
        fingerprint_data['resource_pattern'] = {
            'memory_category': self._categorize_memory(cloud_state.get('memory_size', 128)),
            'timeout_category': self._categorize_timeout(cloud_state.get('timeout', 3)),
            'ephemeral_storage_size': cloud_state.get('ephemeral_storage', {}).get('Size', 512),
            'architecture': cloud_state.get('architectures', ['x86_64'])[0],
            'package_type': cloud_state.get('package_type', 'Zip')
        }
        
        # Integration fingerprint
        fingerprint_data['integration_pattern'] = {
            'in_vpc': bool(cloud_state.get('vpc_config', {}).get('VpcId')),
            'has_layers': len(cloud_state.get('layers', [])) > 0,
            'layer_count': len(cloud_state.get('layers', [])),
            'has_environment_vars': len(cloud_state.get('environment', {}).get('Variables', {})) > 0,
            'env_var_count': len(cloud_state.get('environment', {}).get('Variables', {})),
            'has_dead_letter_queue': bool(cloud_state.get('dead_letter_config', {}).get('TargetArn')),
            'tracing_enabled': cloud_state.get('tracing_config', {}).get('Mode') == 'Active',
            'has_event_sources': len(cloud_state.get('event_source_mappings', [])) > 0,
            'event_source_count': len(cloud_state.get('event_source_mappings', []))
        }
        
        # Security fingerprint
        fingerprint_data['security_pattern'] = {
            'has_kms_key': bool(cloud_state.get('kms_key_arn')),
            'has_resource_policy': bool(cloud_state.get('resource_policy')),
            'has_signing_config': bool(cloud_state.get('signing_profile_version_arn')),
            'provisioned_concurrency': cloud_state.get('provisioned_concurrency', 0)
        }
        
        return fingerprint_data
    
    def _get_language_family(self, runtime: str) -> str:
        """Get programming language family from runtime"""
        if runtime.startswith('python'):
            return 'python'
        elif runtime.startswith('nodejs'):
            return 'javascript'
        elif runtime.startswith('java'):
            return 'java'
        elif runtime.startswith('dotnet'):
            return 'dotnet'
        elif runtime.startswith('go'):
            return 'go'
        elif runtime.startswith('ruby'):
            return 'ruby'
        elif runtime == 'provided' or runtime.startswith('provided'):
            return 'custom'
        else:
            return 'other'
    
    def _categorize_memory(self, memory_mb: int) -> str:
        """Categorize memory allocation"""
        if memory_mb <= 128:
            return 'minimal'
        elif memory_mb <= 512:
            return 'small'
        elif memory_mb <= 1024:
            return 'medium'
        elif memory_mb <= 3008:
            return 'large'
        else:
            return 'maximum'
    
    def _categorize_timeout(self, timeout_seconds: int) -> str:
        """Categorize timeout duration"""
        if timeout_seconds <= 30:
            return 'short'
        elif timeout_seconds <= 300:
            return 'medium'
        elif timeout_seconds <= 600:
            return 'long'
        else:
            return 'maximum'
    
    def _predict_service_specific_impact(self, current: Dict[str, Any], 
                                       desired: Dict[str, Any]) -> ChangeImpactAnalysis:
        """Predict Lambda-specific change impacts"""
        changes = []
        impact_level = ChangeImpact.LOW
        downtime = 0  # Lambda updates are zero-downtime
        propagation_time = 60  # 1 minute for deployment
        cost_impact = 0.0
        affected_resources = []
        recommendations = []
        rollback_complexity = "low"
        
        # 1. Runtime changes
        if current.get('runtime') != desired.get('runtime'):
            changes.append("runtime_modification")
            impact_level = ChangeImpact.HIGH if impact_level.value < ChangeImpact.HIGH.value else impact_level
            propagation_time = max(propagation_time, 300)  # 5 minutes for testing
            rollback_complexity = "medium"
            
            recommendations.append("Runtime change requires thorough testing")
            recommendations.append("Verify all dependencies are compatible")
            recommendations.append("Consider gradual rollout with aliases")
        
        # 2. Memory size changes
        current_memory = current.get('memory_size', 128)
        desired_memory = desired.get('memory_size', 128)
        
        if current_memory != desired_memory:
            changes.append("memory_modification")
            
            memory_change_pct = ((desired_memory - current_memory) / current_memory) * 100
            cost_impact += memory_change_pct  # Memory directly affects cost
            
            if desired_memory > current_memory:
                recommendations.append("Memory increase may improve performance")
                if memory_change_pct > 100:
                    recommendations.append(f"WARNING: Significant cost increase (~{memory_change_pct:.0f}%)")
            else:
                recommendations.append("Memory reduction may affect performance")
                recommendations.append("Monitor for memory-related errors")
        
        # 3. Timeout changes
        current_timeout = current.get('timeout', 3)
        desired_timeout = desired.get('timeout', 3)
        
        if current_timeout != desired_timeout:
            changes.append("timeout_modification")
            
            if desired_timeout > current_timeout:
                recommendations.append("Timeout increase allows longer execution")
                if desired_timeout > 300:
                    recommendations.append("Long timeouts may indicate architectural issues")
            else:
                impact_level = ChangeImpact.MEDIUM if impact_level.value < ChangeImpact.MEDIUM.value else impact_level
                recommendations.append("WARNING: Timeout reduction may cause failures")
                recommendations.append("Verify function execution time before deployment")
        
        # 4. VPC configuration changes
        current_vpc = current.get('vpc_config', {})
        desired_vpc = desired.get('vpc_config', {})
        
        if current_vpc != desired_vpc:
            changes.append("vpc_configuration_modification")
            impact_level = ChangeImpact.MEDIUM if impact_level.value < ChangeImpact.MEDIUM.value else impact_level
            propagation_time = max(propagation_time, 180)  # 3 minutes for VPC changes
            
            current_in_vpc = bool(current_vpc.get('VpcId'))
            desired_in_vpc = bool(desired_vpc.get('VpcId'))
            
            if not current_in_vpc and desired_in_vpc:
                recommendations.append("Adding VPC configuration increases cold start time")
                recommendations.append("Ensure proper security group and subnet configuration")
                affected_resources.extend(['security_groups', 'subnets'])
            elif current_in_vpc and not desired_in_vpc:
                recommendations.append("Removing VPC configuration improves cold start time")
                recommendations.append("Verify external connectivity requirements")
            else:
                recommendations.append("VPC configuration changes affect network access")
        
        # 5. Environment variables changes
        current_env = current.get('environment', {}).get('Variables', {})
        desired_env = desired.get('environment_variables', {})
        
        if current_env != desired_env:
            changes.append("environment_variables_modification")
            
            # Check for sensitive data
            sensitive_keys = ['password', 'secret', 'key', 'token', 'api_key']
            for key in desired_env.keys():
                if any(sensitive in key.lower() for sensitive in sensitive_keys):
                    recommendations.append(f"Consider using AWS Secrets Manager for {key}")
        
        # 6. Dead letter queue changes
        current_dlq = current.get('dead_letter_config', {})
        desired_dlq = desired.get('dead_letter_config', {})
        
        if current_dlq != desired_dlq:
            changes.append("dead_letter_queue_modification")
            
            if desired_dlq.get('TargetArn') and not current_dlq.get('TargetArn'):
                recommendations.append("Adding DLQ improves error handling")
                affected_resources.append('sqs_queue')
            elif not desired_dlq.get('TargetArn') and current_dlq.get('TargetArn'):
                recommendations.append("Removing DLQ reduces error visibility")
        
        # 7. Layer changes
        current_layers = [layer.get('Arn', '') for layer in current.get('layers', [])]
        desired_layers = desired.get('layers', [])
        
        if current_layers != desired_layers:
            changes.append("layers_modification")
            propagation_time = max(propagation_time, 120)  # 2 minutes for layer updates
            
            if len(desired_layers) > len(current_layers):
                recommendations.append("Adding layers may increase cold start time")
            
            recommendations.append("Verify layer compatibility with runtime")
            affected_resources.extend([f"lambda_layer:{layer}" for layer in desired_layers])
        
        # 8. Architecture changes
        current_arch = current.get('architectures', ['x86_64'])[0]
        desired_arch = desired.get('architectures', ['x86_64'])[0]
        
        if current_arch != desired_arch:
            changes.append("architecture_modification")
            impact_level = ChangeImpact.HIGH if impact_level.value < ChangeImpact.HIGH.value else impact_level
            rollback_complexity = "medium"
            
            if desired_arch == 'arm64':
                recommendations.append("ARM64 architecture may provide better price-performance")
                cost_impact -= 10  # ARM64 is typically cheaper
            else:
                recommendations.append("x86_64 architecture has broader library compatibility")
            
            recommendations.append("Verify all dependencies support target architecture")
        
        # 9. Package type changes
        if current.get('package_type') != desired.get('package_type'):
            changes.append("package_type_modification")
            impact_level = ChangeImpact.CRITICAL if impact_level.value < ChangeImpact.CRITICAL.value else impact_level
            rollback_complexity = "high"
            
            recommendations.append("CRITICAL: Package type change requires complete redeploy")
            recommendations.append("Zip vs Container deployment methods are incompatible")
        
        # Calculate invocation cost impact
        if current_memory != desired_memory:
            # Memory affects both compute cost and potentially duration
            execution_cost_impact = memory_change_pct * 0.5  # Rough estimate
            cost_impact += execution_cost_impact
        
        # Find affected resources
        function_name = current.get('function_name') or desired.get('function_name')
        if function_name:
            affected_resources.extend([
                f"api_gateway_integrations_{function_name}",
                f"cloudwatch_events_{function_name}",
                f"cloudwatch_logs_{function_name}",
                f"iam_roles_{function_name}"
            ])
        
        change_type = ", ".join(changes) if changes else "function_update"
        
        return ChangeImpactAnalysis(
            change_type=change_type,
            impact_level=impact_level,
            estimated_downtime=downtime,
            propagation_time=propagation_time,
            cost_impact=cost_impact,
            affected_resources=affected_resources,
            recommendations=recommendations,
            rollback_complexity=rollback_complexity
        )
    
    def _check_service_specific_health(self, resource_id: str, 
                                     cloud_state: Dict[str, Any]) -> ResourceHealth:
        """Check Lambda function health"""
        health_score = 1.0
        issues = []
        metrics = {}
        
        # State check
        state = cloud_state.get('state', 'Active')
        if state != 'Active':
            health_score -= 0.4
            issues.append(f"Function state: {state}")
        
        last_update_status = cloud_state.get('last_update_status', 'Successful')
        if last_update_status != 'Successful':
            health_score -= 0.3
            issues.append(f"Last update status: {last_update_status}")
        
        # Configuration checks
        memory_size = cloud_state.get('memory_size', 128)
        if memory_size < 512:
            issues.append("Low memory allocation may affect performance")
        elif memory_size == 128:
            issues.append("Minimum memory allocation (consider increasing for better performance)")
        
        timeout = cloud_state.get('timeout', 3)
        if timeout >= 900:  # 15 minutes
            issues.append("Maximum timeout configured (consider architectural review)")
        elif timeout <= 3:
            issues.append("Very short timeout (may cause failures for longer operations)")
        
        # VPC configuration check
        vpc_config = cloud_state.get('vpc_config', {})
        if vpc_config.get('VpcId'):
            metrics['in_vpc'] = True
            if not vpc_config.get('SecurityGroupIds'):
                health_score -= 0.2
                issues.append("VPC function without security groups")
        else:
            metrics['in_vpc'] = False
        
        # Environment variables check
        env_vars = cloud_state.get('environment', {}).get('Variables', {})
        metrics['environment_variables_count'] = len(env_vars)
        
        # Check for potentially sensitive data in env vars
        sensitive_patterns = ['password', 'secret', 'key', 'token', 'api_key']
        for key in env_vars.keys():
            if any(pattern in key.lower() for pattern in sensitive_patterns):
                health_score -= 0.1
                issues.append(f"Potentially sensitive data in environment variable: {key}")
        
        # Dead letter queue check
        dlq_config = cloud_state.get('dead_letter_config', {})
        if not dlq_config.get('TargetArn'):
            issues.append("No dead letter queue configured (recommended for error handling)")
        else:
            metrics['has_dead_letter_queue'] = True
        
        # Tracing check
        tracing_mode = cloud_state.get('tracing_config', {}).get('Mode', 'PassThrough')
        if tracing_mode != 'Active':
            issues.append("X-Ray tracing not enabled (recommended for debugging)")
        else:
            metrics['tracing_enabled'] = True
        
        # Layers check
        layers = cloud_state.get('layers', [])
        metrics['layer_count'] = len(layers)
        if len(layers) > 5:
            issues.append("Many layers may increase cold start time")
        
        # Event source mappings check
        event_sources = cloud_state.get('event_source_mappings', [])
        metrics['event_source_count'] = len(event_sources)
        
        # Code size check
        code_size = cloud_state.get('code_size', 0)
        metrics['code_size_mb'] = code_size / (1024 * 1024)
        
        if code_size > 50 * 1024 * 1024:  # 50MB
            health_score -= 0.1
            issues.append("Large deployment package may increase cold start time")
        
        # Runtime check
        runtime = cloud_state.get('runtime', '')
        if runtime:
            # Check for deprecated runtimes (simplified)
            deprecated_runtimes = ['python2.7', 'nodejs8.10', 'nodejs10.x', 'dotnetcore2.1']
            if runtime in deprecated_runtimes:
                health_score -= 0.2
                issues.append(f"Deprecated runtime: {runtime}")
        
        # Calculate feature scores
        metrics['performance_features'] = sum([
            memory_size >= 512,
            timeout <= 300,
            bool(dlq_config.get('TargetArn')),
            tracing_mode == 'Active'
        ])
        
        metrics['security_features'] = sum([
            bool(cloud_state.get('kms_key_arn')),
            bool(vpc_config.get('VpcId')),
            len([k for k in env_vars.keys() if not any(p in k.lower() for p in sensitive_patterns)]) == len(env_vars),
            bool(cloud_state.get('signing_profile_version_arn'))
        ])
        
        return ResourceHealth(
            resource_id=resource_id,
            health_score=max(health_score, 0.0),
            issues=issues,
            performance_metrics=metrics,
            last_check=datetime.now()
        )
    
    def _calculate_service_specific_changes(self, current: Dict[str, Any], 
                                          desired: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate Lambda-specific changes"""
        changes = {}
        
        # Runtime changes
        if current.get('runtime') != desired.get('runtime'):
            changes['runtime'] = {
                'from': current.get('runtime'),
                'to': desired.get('runtime'),
                'requires': 'update'
            }
        
        # Memory changes
        if current.get('memory_size') != desired.get('memory_size'):
            changes['memory_size'] = {
                'from': current.get('memory_size'),
                'to': desired.get('memory_size'),
                'requires': 'update'
            }
        
        # Timeout changes
        if current.get('timeout') != desired.get('timeout'):
            changes['timeout'] = {
                'from': current.get('timeout'),
                'to': desired.get('timeout'),
                'requires': 'update'
            }
        
        # VPC configuration changes
        if current.get('vpc_config') != desired.get('vpc_config'):
            changes['vpc_config'] = {
                'from': current.get('vpc_config'),
                'to': desired.get('vpc_config'),
                'requires': 'update'
            }
        
        # Environment variables changes
        current_env = current.get('environment', {}).get('Variables', {})
        desired_env = desired.get('environment_variables', {})
        
        if current_env != desired_env:
            changes['environment_variables'] = {
                'from': current_env,
                'to': desired_env,
                'requires': 'update'
            }
        
        # Layers changes
        current_layers = [layer.get('Arn', '') for layer in current.get('layers', [])]
        desired_layers = desired.get('layers', [])
        
        if current_layers != desired_layers:
            changes['layers'] = {
                'from': current_layers,
                'to': desired_layers,
                'requires': 'update'
            }
        
        return changes