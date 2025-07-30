"""
GCP Cloud Functions Stateless Intelligence Implementation

Smart resource fingerprinting and predictive change impact analysis for Cloud Functions.
Extends the GCP intelligence base with Cloud Functions-specific capabilities.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime

from .gcp_intelligence_base import GCPIntelligenceBase, GCPResourceType
from .stateless_intelligence import (
    ChangeImpact,
    ChangeImpactAnalysis,
    ResourceHealth
)


class CloudFunctionsIntelligence(GCPIntelligenceBase):
    """Cloud Functions-specific stateless intelligence implementation"""
    
    def __init__(self):
        super().__init__(GCPResourceType.CLOUD_FUNCTIONS)
        self.functions_client = None
    
    def _initialize_service_client(self):
        """Initialize Cloud Functions client"""
        try:
            from google.cloud import functions_v1
            self.functions_client = functions_v1.CloudFunctionsServiceClient()
        except Exception as e:
            print(f"⚠️  Failed to create Cloud Functions client: {e}")
    
    def _discover_existing_resources(self) -> Dict[str, Dict[str, Any]]:
        """Discover existing Cloud Functions"""
        existing_functions = {}
        
        if not self._get_gcp_client():
            return existing_functions
        
        try:
            # Mock discovery for demonstration
            # In real implementation would use: self.functions_client.list_functions()
            pass
        
        except Exception as e:
            print(f"⚠️  Failed to discover Cloud Functions: {str(e)}")
        
        return existing_functions
    
    def _extract_resource_config(self, cloud_state: Dict[str, Any]) -> Dict[str, Any]:
        """Extract configuration from Cloud Function state"""
        return {
            'name': cloud_state.get('name'),
            'runtime': cloud_state.get('runtime'),
            'entry_point': cloud_state.get('entry_point'),
            'source_archive_url': cloud_state.get('source_archive_url'),
            'source_repository': cloud_state.get('source_repository'),
            'memory': cloud_state.get('available_memory_mb'),
            'timeout': cloud_state.get('timeout'),
            'max_instances': cloud_state.get('max_instances'),
            'min_instances': cloud_state.get('min_instances'),
            'service_account_email': cloud_state.get('service_account_email'),
            'environment_variables': cloud_state.get('environment_variables', {}),
            'vpc_connector': cloud_state.get('vpc_connector'),
            'vpc_connector_egress_settings': cloud_state.get('vpc_connector_egress_settings'),
            'ingress_settings': cloud_state.get('ingress_settings'),
            'labels': cloud_state.get('labels', {}),
            'event_trigger': cloud_state.get('event_trigger', {}),
            'https_trigger': cloud_state.get('https_trigger', {}),
            'build_environment_variables': cloud_state.get('build_environment_variables', {}),
            'kms_key_name': cloud_state.get('kms_key_name'),
            'docker_registry': cloud_state.get('docker_registry')
        }
    
    def _generate_service_specific_fingerprint_data(self, cloud_state: Dict[str, Any]) -> Dict[str, Any]:
        """Generate Cloud Functions-specific fingerprint data"""
        fingerprint_data = {}
        
        # Runtime and language fingerprint
        runtime = cloud_state.get('runtime', '')
        fingerprint_data['runtime_pattern'] = {
            'runtime': runtime,
            'language': self._get_language_from_runtime(runtime),
            'generation': self._get_runtime_generation(runtime),
            'is_python': runtime.startswith('python'),
            'is_nodejs': runtime.startswith('nodejs'),
            'is_go': runtime.startswith('go'),
            'is_java': runtime.startswith('java'),
            'is_dotnet': runtime.startswith('dotnet'),
            'is_ruby': runtime.startswith('ruby'),
            'is_php': runtime.startswith('php')
        }
        
        # Resource allocation fingerprint
        memory_mb = cloud_state.get('available_memory_mb', 256)
        timeout = cloud_state.get('timeout', '60s')
        
        fingerprint_data['resource_pattern'] = {
            'memory_mb': memory_mb,
            'is_memory_optimized': memory_mb >= 1024,
            'is_minimal_memory': memory_mb <= 256,
            'timeout_seconds': self._parse_timeout_to_seconds(timeout),
            'is_long_running': self._parse_timeout_to_seconds(timeout) > 300,
            'max_instances': cloud_state.get('max_instances', 1000),
            'min_instances': cloud_state.get('min_instances', 0),
            'has_min_instances': cloud_state.get('min_instances', 0) > 0
        }
        
        # Source and deployment fingerprint
        fingerprint_data['deployment_pattern'] = {
            'has_source_archive': bool(cloud_state.get('source_archive_url')),
            'has_source_repository': bool(cloud_state.get('source_repository')),
            'deployment_method': self._get_deployment_method(cloud_state),
            'has_build_env_vars': len(cloud_state.get('build_environment_variables', {})) > 0,
            'uses_custom_docker_registry': cloud_state.get('docker_registry') != 'CONTAINER_REGISTRY'
        }
        
        # Trigger and connectivity fingerprint
        event_trigger = cloud_state.get('event_trigger', {})
        https_trigger = cloud_state.get('https_trigger', {})
        
        fingerprint_data['trigger_pattern'] = {
            'has_http_trigger': bool(https_trigger),
            'has_event_trigger': bool(event_trigger),
            'event_type': event_trigger.get('event_type', ''),
            'trigger_resource': event_trigger.get('resource', ''),
            'is_pubsub_trigger': 'pubsub' in event_trigger.get('event_type', '').lower(),
            'is_storage_trigger': 'storage' in event_trigger.get('event_type', '').lower(),
            'is_firestore_trigger': 'firestore' in event_trigger.get('event_type', '').lower(),
            'requires_authentication': https_trigger.get('security_level') == 'SECURE_ALWAYS'
        }
        
        # Network and security fingerprint
        fingerprint_data['security_pattern'] = {
            'has_vpc_connector': bool(cloud_state.get('vpc_connector')),
            'vpc_egress_settings': cloud_state.get('vpc_connector_egress_settings', 'PRIVATE_RANGES_ONLY'),
            'ingress_settings': cloud_state.get('ingress_settings', 'ALLOW_ALL'),
            'allows_all_ingress': cloud_state.get('ingress_settings') == 'ALLOW_ALL',
            'allows_internal_only': cloud_state.get('ingress_settings') == 'ALLOW_INTERNAL_ONLY',
            'has_custom_service_account': bool(cloud_state.get('service_account_email')),
            'has_kms_key': bool(cloud_state.get('kms_key_name')),
            'env_var_count': len(cloud_state.get('environment_variables', {}))
        }
        
        return fingerprint_data
    
    def _get_language_from_runtime(self, runtime: str) -> str:
        """Extract programming language from runtime"""
        if runtime.startswith('python'):
            return 'python'
        elif runtime.startswith('nodejs'):
            return 'javascript'
        elif runtime.startswith('go'):
            return 'go'
        elif runtime.startswith('java'):
            return 'java'
        elif runtime.startswith('dotnet'):
            return 'csharp'
        elif runtime.startswith('ruby'):
            return 'ruby'
        elif runtime.startswith('php'):
            return 'php'
        else:
            return 'unknown'
    
    def _get_runtime_generation(self, runtime: str) -> str:
        """Get runtime generation/version"""
        if 'python' in runtime:
            if '39' in runtime:
                return 'python3.9'
            elif '38' in runtime:
                return 'python3.8'
            elif '37' in runtime:
                return 'python3.7'
        elif 'nodejs' in runtime:
            if '16' in runtime:
                return 'nodejs16'
            elif '14' in runtime:
                return 'nodejs14'
            elif '12' in runtime:
                return 'nodejs12'
        elif 'go' in runtime:
            if '116' in runtime:
                return 'go1.16'
            elif '113' in runtime:
                return 'go1.13'
        
        return runtime
    
    def _parse_timeout_to_seconds(self, timeout: str) -> int:
        """Parse timeout string to seconds"""
        if not timeout:
            return 60
        
        timeout = timeout.lower().strip()
        if timeout.endswith('s'):
            try:
                return int(timeout[:-1])
            except ValueError:
                return 60
        elif timeout.endswith('m'):
            try:
                return int(timeout[:-1]) * 60
            except ValueError:
                return 60
        else:
            try:
                return int(timeout)
            except ValueError:
                return 60
    
    def _get_deployment_method(self, cloud_state: Dict[str, Any]) -> str:
        """Determine deployment method"""
        if cloud_state.get('source_archive_url'):
            return 'zip_upload'
        elif cloud_state.get('source_repository'):
            return 'source_repository'
        else:
            return 'unknown'
    
    def _predict_service_specific_impact(self, current: Dict[str, Any], 
                                       desired: Dict[str, Any]) -> ChangeImpactAnalysis:
        """Predict Cloud Functions-specific change impacts"""
        changes = []
        impact_level = ChangeImpact.LOW
        downtime = 0  # Cloud Functions deployments are generally zero-downtime
        propagation_time = 120  # 2 minutes for function deployment
        cost_impact = 0.0
        affected_resources = []
        recommendations = []
        rollback_complexity = "low"
        
        # 1. Runtime changes
        current_runtime = current.get('runtime', '')
        desired_runtime = desired.get('runtime', '')
        
        if current_runtime != desired_runtime:
            changes.append("runtime_modification")
            impact_level = ChangeImpact.HIGH if impact_level.value < ChangeImpact.HIGH.value else impact_level
            propagation_time = max(propagation_time, 300)
            rollback_complexity = "medium"
            
            recommendations.append("Runtime changes require function redeployment")
            recommendations.append("Test thoroughly as language runtime affects behavior")
            
            # Check for major version changes
            if self._get_language_from_runtime(current_runtime) != self._get_language_from_runtime(desired_runtime):
                impact_level = ChangeImpact.CRITICAL if impact_level.value < ChangeImpact.CRITICAL.value else impact_level
                recommendations.append("CRITICAL: Changing programming language")
                recommendations.append("Requires complete code rewrite")
                rollback_complexity = "high"
        
        # 2. Memory allocation changes
        current_memory = current.get('memory', 256)
        desired_memory = desired.get('memory', 256)
        
        if current_memory != desired_memory:
            changes.append("memory_allocation_modification")
            
            memory_change_percent = ((desired_memory - current_memory) / current_memory) * 100
            cost_impact += memory_change_percent * 0.5  # Memory affects cost linearly
            
            if desired_memory > current_memory:
                recommendations.append(f"Increasing memory from {current_memory}MB to {desired_memory}MB")
                recommendations.append("Higher memory may improve performance but increases cost")
            else:
                recommendations.append(f"Reducing memory from {current_memory}MB to {desired_memory}MB")
                recommendations.append("Lower memory reduces cost but may affect performance")
                
            if desired_memory < 256:
                recommendations.append("WARNING: Very low memory allocation may cause issues")
        
        # 3. Timeout changes
        current_timeout = self._parse_timeout_to_seconds(current.get('timeout', '60s'))
        desired_timeout = self._parse_timeout_to_seconds(desired.get('timeout', '60s'))
        
        if current_timeout != desired_timeout:
            changes.append("timeout_modification")
            
            if desired_timeout > 300:  # 5 minutes
                recommendations.append("Long timeout may indicate function needs optimization")
            elif desired_timeout < 30:
                recommendations.append("Very short timeout may cause premature termination")
        
        # 4. Scaling configuration changes
        current_max = current.get('max_instances', 1000)
        desired_max = desired.get('max_instances', 1000)
        current_min = current.get('min_instances', 0)
        desired_min = desired.get('min_instances', 0)
        
        if current_max != desired_max or current_min != desired_min:
            changes.append("scaling_configuration_modification")
            
            if desired_min > current_min:
                min_cost_increase = (desired_min - current_min) * 24 * 30  # Rough monthly cost
                cost_impact += min_cost_increase
                recommendations.append(f"Setting minimum instances to {desired_min}")
                recommendations.append("Minimum instances reduce cold starts but increase cost")
            
            if desired_max < current_max:
                recommendations.append("Reducing maximum instances may cause throttling under load")
        
        # 5. VPC connector changes
        current_vpc = current.get('vpc_connector')
        desired_vpc = desired.get('vpc_connector')
        
        if current_vpc != desired_vpc:
            changes.append("vpc_connector_modification")
            impact_level = ChangeImpact.MEDIUM if impact_level.value < ChangeImpact.MEDIUM.value else impact_level
            
            if desired_vpc and not current_vpc:
                recommendations.append("Adding VPC connector for private network access")
                recommendations.append("VPC connector may increase latency")
                affected_resources.append("vpc_networks")
            elif not desired_vpc and current_vpc:
                recommendations.append("Removing VPC connector")
                recommendations.append("Function will lose access to private resources")
        
        # 6. Ingress settings changes
        current_ingress = current.get('ingress_settings', 'ALLOW_ALL')
        desired_ingress = desired.get('ingress_settings', 'ALLOW_ALL')
        
        if current_ingress != desired_ingress:
            changes.append("ingress_settings_modification")
            
            if desired_ingress == 'ALLOW_INTERNAL_ONLY':
                impact_level = ChangeImpact.MEDIUM if impact_level.value < ChangeImpact.MEDIUM.value else impact_level
                recommendations.append("Restricting access to internal traffic only")
                recommendations.append("External callers will no longer be able to invoke function")
            elif desired_ingress == 'ALLOW_ALL' and current_ingress != 'ALLOW_ALL':
                recommendations.append("WARNING: Allowing all traffic to function")
                recommendations.append("Consider authentication mechanisms")
        
        # 7. Service account changes
        current_sa = current.get('service_account_email')
        desired_sa = desired.get('service_account_email')
        
        if current_sa != desired_sa:
            changes.append("service_account_modification")
            impact_level = ChangeImpact.MEDIUM if impact_level.value < ChangeImpact.MEDIUM.value else impact_level
            
            recommendations.append("Service account changes affect API permissions")
            recommendations.append("Test function access to GCP services after change")
            affected_resources.append("iam_policies")
        
        # 8. Environment variables changes
        current_env = current.get('environment_variables', {})
        desired_env = desired.get('environment_variables', {})
        
        if current_env != desired_env:
            changes.append("environment_variables_modification")
            
            # Check for sensitive data in environment variables
            sensitive_keys = ['password', 'secret', 'key', 'token', 'api_key']
            for key in desired_env.keys():
                if any(sensitive in key.lower() for sensitive in sensitive_keys):
                    recommendations.append(f"WARNING: Potential sensitive data in env var: {key}")
                    recommendations.append("Consider using Secret Manager instead")
        
        # 9. Trigger changes
        current_event_trigger = current.get('event_trigger', {})
        desired_event_trigger = desired.get('event_trigger', {})
        current_https_trigger = current.get('https_trigger', {})
        desired_https_trigger = desired.get('https_trigger', {})
        
        if current_event_trigger != desired_event_trigger or current_https_trigger != desired_https_trigger:
            changes.append("trigger_modification")
            impact_level = ChangeImpact.HIGH if impact_level.value < ChangeImpact.HIGH.value else impact_level
            
            recommendations.append("Trigger changes affect how function is invoked")
            
            if desired_event_trigger and not current_event_trigger:
                event_type = desired_event_trigger.get('event_type', '')
                affected_resources.append(f"event_source:{event_type}")
                recommendations.append(f"Adding event trigger for {event_type}")
            elif not desired_event_trigger and current_event_trigger:
                recommendations.append("Removing event trigger - function becomes HTTP-only")
        
        # 10. Source code changes
        current_archive = current.get('source_archive_url')
        desired_archive = desired.get('source_archive_url')
        
        if current_archive != desired_archive:
            changes.append("source_code_modification")
            recommendations.append("Source code changes - ensure proper testing")
            
            if not desired_archive:
                recommendations.append("WARNING: No source archive specified")
        
        # Find affected resources
        function_name = current.get('name') or desired.get('name')
        if function_name:
            affected_resources.extend([
                f"cloud_scheduler_jobs:{function_name}",
                f"pubsub_subscriptions:{function_name}",
                f"eventarc_triggers:{function_name}"
            ])
        
        change_type = ", ".join(changes) if changes else "function_configuration_update"
        
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
        """Check Cloud Function health"""
        health_score = 1.0
        issues = []
        metrics = {}
        
        # Function status check
        status = cloud_state.get('status', 'UNKNOWN')
        if status != 'ACTIVE':
            health_score -= 0.3
            issues.append(f"Function status: {status}")
        
        # Runtime version check
        runtime = cloud_state.get('runtime', '')
        if 'python37' in runtime or 'nodejs10' in runtime or 'nodejs8' in runtime:
            health_score -= 0.2
            issues.append("Using deprecated runtime version - consider upgrading")
        
        # Memory allocation check
        memory_mb = cloud_state.get('available_memory_mb', 256)
        if memory_mb < 128:
            health_score -= 0.2
            issues.append("Very low memory allocation (< 128MB)")
        elif memory_mb > 4096:
            issues.append("High memory allocation - ensure it's necessary")
        
        # Timeout check
        timeout_seconds = self._parse_timeout_to_seconds(cloud_state.get('timeout', '60s'))
        if timeout_seconds > 540:  # 9 minutes (max is 540s for HTTP, 60s for event)
            health_score -= 0.1
            issues.append("Very long timeout - consider function optimization")
        elif timeout_seconds < 10:
            health_score -= 0.1
            issues.append("Very short timeout - may cause premature termination")
        
        # Security checks
        ingress_settings = cloud_state.get('ingress_settings', 'ALLOW_ALL')
        if ingress_settings == 'ALLOW_ALL':
            health_score -= 0.1
            issues.append("Function allows all ingress traffic (consider restricting)")
        
        # Service account check
        service_account = cloud_state.get('service_account_email')
        if not service_account:
            health_score -= 0.1
            issues.append("Using default service account (consider custom service account)")
        
        # Environment variables security check
        env_vars = cloud_state.get('environment_variables', {})
        sensitive_keys = ['password', 'secret', 'key', 'token', 'api_key']
        for key in env_vars.keys():
            if any(sensitive in key.lower() for sensitive in sensitive_keys):
                health_score -= 0.2
                issues.append(f"Potential sensitive data in environment variable: {key}")
                break
        
        # VPC connector check
        vpc_connector = cloud_state.get('vpc_connector')
        if vpc_connector:
            metrics['has_vpc_connector'] = True
        else:
            issues.append("No VPC connector (function cannot access private resources)")
            metrics['has_vpc_connector'] = False
        
        # Minimum instances check
        min_instances = cloud_state.get('min_instances', 0)
        if min_instances > 0:
            metrics['has_min_instances'] = True
            issues.append(f"Minimum instances set to {min_instances} (increases cost)")
        else:
            metrics['has_min_instances'] = False
            issues.append("No minimum instances (may experience cold starts)")
        
        # Trigger configuration check
        event_trigger = cloud_state.get('event_trigger', {})
        https_trigger = cloud_state.get('https_trigger', {})
        
        if not event_trigger and not https_trigger:
            health_score -= 0.3
            issues.append("No triggers configured - function cannot be invoked")
        
        # KMS encryption check
        kms_key = cloud_state.get('kms_key_name')
        if kms_key:
            metrics['uses_kms_encryption'] = True
        else:
            issues.append("Not using customer-managed encryption keys")
            metrics['uses_kms_encryption'] = False
        
        # Calculate feature metrics
        metrics['security_features'] = sum([
            ingress_settings != 'ALLOW_ALL',
            bool(service_account),
            bool(kms_key),
            bool(vpc_connector),
            len(env_vars) == 0 or not any(sensitive in key.lower() for key in env_vars.keys() for sensitive in sensitive_keys)
        ])
        
        metrics['performance_features'] = sum([
            memory_mb >= 256,
            timeout_seconds <= 300,
            min_instances > 0,
            'python39' in runtime or 'nodejs16' in runtime or 'go116' in runtime  # Modern runtime
        ])
        
        metrics['reliability_features'] = sum([
            status == 'ACTIVE',
            bool(event_trigger or https_trigger),
            cloud_state.get('max_instances', 1000) > 10  # Reasonable scaling limit
        ])
        
        metrics['memory_mb'] = memory_mb
        metrics['timeout_seconds'] = timeout_seconds
        metrics['min_instances'] = min_instances
        metrics['max_instances'] = cloud_state.get('max_instances', 1000)
        
        return ResourceHealth(
            resource_id=resource_id,
            health_score=max(health_score, 0.0),
            issues=issues,
            performance_metrics=metrics,
            last_check=datetime.now()
        )
    
    def _calculate_service_specific_changes(self, current: Dict[str, Any], 
                                          desired: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate Cloud Functions-specific changes"""
        changes = {}
        
        # Runtime changes
        if current.get('runtime') != desired.get('runtime'):
            changes['runtime'] = {
                'from': current.get('runtime'),
                'to': desired.get('runtime'),
                'requires': 'redeploy'
            }
        
        # Memory changes
        if current.get('memory') != desired.get('memory'):
            changes['memory'] = {
                'from': current.get('memory'),
                'to': desired.get('memory'),
                'requires': 'update'
            }
        
        # Timeout changes
        if current.get('timeout') != desired.get('timeout'):
            changes['timeout'] = {
                'from': current.get('timeout'),
                'to': desired.get('timeout'),
                'requires': 'update'
            }
        
        # Scaling changes
        if (current.get('max_instances') != desired.get('max_instances') or 
            current.get('min_instances') != desired.get('min_instances')):
            changes['scaling'] = {
                'from': {
                    'min': current.get('min_instances'),
                    'max': current.get('max_instances')
                },
                'to': {
                    'min': desired.get('min_instances'),
                    'max': desired.get('max_instances')
                },
                'requires': 'update'
            }
        
        # VPC connector changes
        if current.get('vpc_connector') != desired.get('vpc_connector'):
            changes['vpc_connector'] = {
                'from': current.get('vpc_connector'),
                'to': desired.get('vpc_connector'),
                'requires': 'update'
            }
        
        # Ingress settings changes
        if current.get('ingress_settings') != desired.get('ingress_settings'):
            changes['ingress_settings'] = {
                'from': current.get('ingress_settings'),
                'to': desired.get('ingress_settings'),
                'requires': 'update'
            }
        
        return changes