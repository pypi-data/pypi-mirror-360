"""
AWS Stateless Intelligence Base Class

Provides a unified interface for integrating stateless intelligence
with all AWS resources. This base class ensures consistent patterns
for resource fingerprinting, change impact analysis, and health monitoring
across all AWS services.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime

from .stateless_intelligence import (
    StatelessIntelligence,
    ResourceType,
    ResourceFingerprint,
    ChangeImpactAnalysis,
    ResourceHealth
)


class AWSIntelligenceBase(ABC):
    """
    Base class for AWS resource intelligence integration
    
    Provides standardized methods for:
    - Smart resource fingerprinting
    - Predictive change impact analysis  
    - Resource health monitoring
    - Conflict detection
    - State discovery and management
    """
    
    def __init__(self, resource_type: ResourceType):
        self.resource_type = resource_type
        self.intelligence = StatelessIntelligence()
    
    # Abstract methods that must be implemented by each AWS service
    
    @abstractmethod
    def _discover_existing_resources(self) -> Dict[str, Dict[str, Any]]:
        """
        Discover existing resources of this type in AWS
        Returns: {resource_id: resource_data}
        """
        pass
    
    @abstractmethod
    def _extract_resource_config(self, cloud_state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract configuration from AWS resource state
        Used for fingerprinting and comparison
        """
        pass
    
    @abstractmethod
    def _generate_service_specific_fingerprint_data(self, 
                                                   cloud_state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate service-specific data for fingerprinting
        Examples: S3 bucket policies, EC2 security groups, etc.
        """
        pass
    
    @abstractmethod
    def _predict_service_specific_impact(self, 
                                       current: Dict[str, Any], 
                                       desired: Dict[str, Any]) -> ChangeImpactAnalysis:
        """
        Predict impact of changes specific to this service
        """
        pass
    
    @abstractmethod
    def _check_service_specific_health(self, 
                                     resource_id: str,
                                     cloud_state: Dict[str, Any]) -> ResourceHealth:
        """
        Check health specific to this service
        """
        pass
    
    # Concrete methods providing standard functionality
    
    def discover_with_intelligence(self, resource_config: Dict[str, Any] = None) -> Dict[str, Dict[str, Any]]:
        """
        Enhanced resource discovery with intelligence
        """
        existing_resources = self._discover_existing_resources()
        
        if not resource_config:
            return existing_resources
        
        enhanced_resources = {}
        
        for resource_id, resource_data in existing_resources.items():
            try:
                # Extract configuration for fingerprinting
                extracted_config = self._extract_resource_config(resource_data)
                
                # Generate resource fingerprint
                fingerprint = self.intelligence.generate_resource_fingerprint(
                    resource_config=resource_config,
                    cloud_state=resource_data,
                    resource_type=self.resource_type
                )
                
                # Check resource health
                health = self._check_service_specific_health(resource_id, resource_data)
                
                # Generate optimization recommendations
                recommendations = self.intelligence.generate_optimization_recommendations(
                    resource_config=resource_config,
                    cloud_state=resource_data,
                    resource_type=self.resource_type
                )
                
                # Enhance resource data
                enhanced_resources[resource_id] = {
                    **resource_data,
                    'fingerprint': fingerprint,
                    'health': health,
                    'recommendations': recommendations,
                    'confidence_score': fingerprint.confidence_score,
                    'extracted_config': extracted_config
                }
                
            except Exception as e:
                print(f"⚠️  Failed to enhance {self.resource_type.value} {resource_id}: {str(e)}")
                enhanced_resources[resource_id] = resource_data
        
        return enhanced_resources
    
    def find_matching_resource(self, resource_config: Dict[str, Any]) -> Optional[Tuple[str, Dict[str, Any], float]]:
        """
        Find existing resource that matches desired configuration
        Returns: (resource_id, resource_data, confidence_score)
        """
        enhanced_resources = self.discover_with_intelligence(resource_config)
        
        best_match = None
        highest_confidence = 0.0
        
        for resource_id, resource_data in enhanced_resources.items():
            confidence = resource_data.get('confidence_score', 0.0)
            
            if confidence > highest_confidence and confidence >= 0.7:  # 70% confidence threshold
                highest_confidence = confidence
                best_match = (resource_id, resource_data, confidence)
        
        return best_match
    
    def predict_change_impact(self, current_state: Dict[str, Any], 
                            desired_config: Dict[str, Any]) -> ChangeImpactAnalysis:
        """
        Predict impact of proposed changes
        """
        return self._predict_service_specific_impact(current_state, desired_config)
    
    def detect_conflicts(self, desired_config: Dict[str, Any]) -> List[str]:
        """
        Detect potential conflicts with existing resources
        """
        existing = self._discover_existing_resources()
        return self.intelligence.detect_resource_conflicts(desired_config, existing)
    
    def _discover_current_state(self, resource_name: str) -> Dict[str, Any]:
        """
        Discover current state using standardized pattern
        """
        existing_resources = self._discover_existing_resources()
        
        # Find resource by InfraDSL markers
        for resource_id, resource_data in existing_resources.items():
            if self._is_managed_resource(resource_data, resource_name):
                return {
                    'exists': True,
                    'resource_id': resource_id,
                    **resource_data
                }
        
        return {'exists': False}
    
    def _is_managed_resource(self, resource_data: Dict[str, Any], resource_name: str) -> bool:
        """
        Check if resource is managed by InfraDSL
        """
        # Check tags for InfraDSL markers
        tags = resource_data.get('tags', {})
        
        # Look for InfraDSL management tags
        if tags.get('infradsl:managed') == 'true':
            if tags.get('infradsl:resource-name') == resource_name:
                return True
        
        # Check comments or descriptions
        comment = resource_data.get('comment', '') or resource_data.get('description', '')
        if resource_name in comment or f"infradsl:{resource_name}" in comment:
            return True
        
        # Check name patterns
        name = resource_data.get('name', '') or resource_data.get('Name', '')
        if name == resource_name:
            return True
        
        return False
    
    def _build_desired_state(self, resource_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Build desired state with InfraDSL management tags
        """
        desired_state = {
            'exists': True,
            **resource_config
        }
        
        # Add standard InfraDSL tags
        if 'tags' not in desired_state:
            desired_state['tags'] = {}
        
        desired_state['tags'].update({
            'infradsl:managed': 'true',
            'infradsl:resource-type': self.resource_type.value,
            'infradsl:created-by': 'infradsl',
            'infradsl:resource-name': resource_config.get('name', ''),
            'infradsl:config-hash': self._generate_config_hash(resource_config)
        })
        
        return desired_state
    
    def _generate_config_hash(self, config: Dict[str, Any]) -> str:
        """
        Generate configuration hash for resource versioning
        """
        return self.intelligence._generate_configuration_hash(config)
    
    def _calculate_diff(self, current: Dict[str, Any], desired: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate differences between current and desired state
        """
        if not current['exists'] and desired['exists']:
            return {'action': 'create', 'resource': desired}
        
        if current['exists'] and not desired['exists']:
            return {'action': 'delete', 'resource': current}
        
        # Calculate specific changes
        changes = {}
        
        # Compare tags
        current_tags = current.get('tags', {})
        desired_tags = desired.get('tags', {})
        
        if current_tags != desired_tags:
            changes['tags'] = {
                'from': current_tags,
                'to': desired_tags,
                'requires': 'update'
            }
        
        # Service-specific comparisons should be implemented in subclasses
        service_changes = self._calculate_service_specific_changes(current, desired)
        changes.update(service_changes)
        
        return {'action': 'update', 'changes': changes} if changes else {'action': 'no_change'}
    
    def _calculate_service_specific_changes(self, current: Dict[str, Any], 
                                          desired: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate service-specific changes (implemented by subclasses)
        """
        return {}
    
    def preview_changes(self, resource_name: str, resource_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Preview changes with intelligence integration
        """
        current_state = self._discover_current_state(resource_name)
        desired_state = self._build_desired_state(resource_config)
        diff = self._calculate_diff(current_state, desired_state)
        
        result = {
            'resource_name': resource_name,
            'resource_type': self.resource_type.value,
            'current_state': current_state,
            'desired_state': desired_state,
            'diff': diff
        }
        
        # Add predictive impact analysis
        if diff['action'] in ['create', 'update']:
            impact_analysis = self.predict_change_impact(current_state, desired_state)
            result['impact_analysis'] = {
                'change_type': impact_analysis.change_type,
                'impact_level': impact_analysis.impact_level.value_name,
                'estimated_downtime': impact_analysis.estimated_downtime,
                'propagation_time': impact_analysis.propagation_time,
                'cost_impact': impact_analysis.cost_impact,
                'affected_resources': impact_analysis.affected_resources,
                'recommendations': impact_analysis.recommendations,
                'rollback_complexity': impact_analysis.rollback_complexity
            }
        
        # Add conflict detection
        conflicts = self.detect_conflicts(desired_state)
        if conflicts:
            result['conflicts'] = conflicts
        
        # Add health information if resource exists
        if current_state['exists']:
            health = self._check_service_specific_health(
                current_state['resource_id'], 
                current_state
            )
            result['health'] = {
                'health_score': health.health_score,
                'issues': health.issues,
                'performance_metrics': health.performance_metrics
            }
        
        return result


class AWSServiceIntelligence:
    """
    Factory class for creating service-specific intelligence implementations
    """
    
    @staticmethod
    def create_s3_intelligence():
        """Create S3-specific intelligence implementation"""
        from .aws_s3_intelligence import S3Intelligence
        return S3Intelligence()
    
    @staticmethod
    def create_ec2_intelligence():
        """Create EC2-specific intelligence implementation"""
        from .aws_ec2_intelligence import EC2Intelligence
        return EC2Intelligence()
    
    @staticmethod
    def create_route53_intelligence():
        """Create Route53-specific intelligence implementation"""
        from .aws_route53_intelligence import Route53Intelligence
        return Route53Intelligence()
    
    @staticmethod
    def create_rds_intelligence():
        """Create RDS-specific intelligence implementation"""
        from .aws_rds_intelligence import RDSIntelligence
        return RDSIntelligence()
    
    @staticmethod
    def create_lambda_intelligence():
        """Create Lambda-specific intelligence implementation"""
        from .aws_lambda_intelligence import LambdaIntelligence
        return LambdaIntelligence()
    
    @staticmethod
    def create_cloudfront_intelligence():
        """Create CloudFront-specific intelligence implementation"""
        from ..providers.aws_managers.cloudfront.distributions import CloudFrontDistributions
        # CloudFront intelligence is integrated into the distributions manager
        return CloudFrontDistributions(None)
    
    @staticmethod
    def get_all_services():
        """Get list of all supported AWS services"""
        return [
            'cloudfront',
            's3', 
            'ec2',
            'route53',
            'rds',
            'lambda'
        ]
    
    @staticmethod
    def create_intelligence_for_service(service_name: str):
        """Create intelligence implementation for any supported service"""
        intelligence_map = {
            's3': AWSServiceIntelligence.create_s3_intelligence,
            'ec2': AWSServiceIntelligence.create_ec2_intelligence,
            'route53': AWSServiceIntelligence.create_route53_intelligence,
            'rds': AWSServiceIntelligence.create_rds_intelligence,
            'lambda': AWSServiceIntelligence.create_lambda_intelligence,
            'cloudfront': AWSServiceIntelligence.create_cloudfront_intelligence
        }
        
        if service_name not in intelligence_map:
            raise ValueError(f"Unsupported service: {service_name}")
        
        return intelligence_map[service_name]()


def enhance_aws_resource_with_intelligence(resource_class, intelligence_class):
    """
    Decorator to enhance existing AWS resource classes with intelligence
    """
    def decorator(cls):
        # Add intelligence as a mixin
        class EnhancedResource(intelligence_class, cls):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                # Initialize intelligence if not already present
                if not hasattr(self, 'intelligence'):
                    self.intelligence = intelligence_class()
        
        return EnhancedResource
    
    return decorator