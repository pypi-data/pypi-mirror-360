"""
GCP Stateless Intelligence Base Class

Provides a unified interface for integrating stateless intelligence
with all Google Cloud Platform resources. This base class ensures consistent patterns
for resource fingerprinting, change impact analysis, and health monitoring
across all GCP services including Firebase.
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


# Add GCP Resource Types
class GCPResourceType:
    """GCP-specific resource types for fingerprinting"""
    COMPUTE_ENGINE = "compute_engine"
    CLOUD_STORAGE = "cloud_storage"
    CLOUD_SQL = "cloud_sql"
    CLOUD_FUNCTIONS = "cloud_functions"
    CLOUD_DNS = "cloud_dns"
    CLOUD_CDN = "cloud_cdn"
    CLOUD_RUN = "cloud_run"
    GKE_CLUSTER = "gke_cluster"
    FIREBASE_HOSTING = "firebase_hosting"
    FIREBASE_AUTH = "firebase_auth"
    FIRESTORE = "firestore"
    FIREBASE_FUNCTIONS = "firebase_functions"
    FIREBASE_STORAGE = "firebase_storage"
    CLOUD_LOAD_BALANCER = "cloud_load_balancer"
    SECRET_MANAGER = "secret_manager"
    PUBSUB = "pubsub"
    BIGQUERY = "bigquery"


class GCPIntelligenceBase(ABC):
    """
    Base class for GCP resource intelligence integration
    
    Provides standardized methods for:
    - Smart resource fingerprinting across all GCP services
    - Predictive change impact analysis including Firebase
    - Resource health monitoring with GCP-specific metrics
    - Cross-service conflict detection
    - State discovery and management
    """
    
    def __init__(self, resource_type: str):
        self.resource_type = resource_type
        self.intelligence = StatelessIntelligence()
        self.gcp_client = None
    
    # Abstract methods that must be implemented by each GCP service
    
    @abstractmethod
    def _discover_existing_resources(self) -> Dict[str, Dict[str, Any]]:
        """
        Discover existing resources of this type in GCP
        Returns: {resource_id: resource_data}
        """
        pass
    
    @abstractmethod
    def _extract_resource_config(self, cloud_state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract configuration from GCP resource state
        Used for fingerprinting and comparison
        """
        pass
    
    @abstractmethod
    def _generate_service_specific_fingerprint_data(self, 
                                                   cloud_state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate service-specific data for fingerprinting
        Examples: Compute Engine machine types, Cloud Storage bucket policies, Firebase configs
        """
        pass
    
    @abstractmethod
    def _predict_service_specific_impact(self, 
                                       current: Dict[str, Any], 
                                       desired: Dict[str, Any]) -> ChangeImpactAnalysis:
        """
        Predict impact of changes specific to this GCP service
        """
        pass
    
    @abstractmethod
    def _check_service_specific_health(self, 
                                     resource_id: str,
                                     cloud_state: Dict[str, Any]) -> ResourceHealth:
        """
        Check health specific to this GCP service
        """
        pass
    
    # Concrete methods providing standard GCP functionality
    
    def _get_gcp_client(self):
        """Get authenticated GCP client with error handling"""
        if not self.gcp_client:
            try:
                from google.cloud import resource_manager
                # Initialize based on service
                self._initialize_service_client()
            except Exception as e:
                print(f"⚠️  Failed to create GCP client: {e}")
                return None
        return self.gcp_client
    
    @abstractmethod
    def _initialize_service_client(self):
        """Initialize service-specific GCP client"""
        pass
    
    def discover_with_intelligence(self, resource_config: Dict[str, Any] = None) -> Dict[str, Dict[str, Any]]:
        """
        Enhanced resource discovery with GCP intelligence
        """
        existing_resources = self._discover_existing_resources()
        
        if not resource_config:
            return existing_resources
        
        enhanced_resources = {}
        
        for resource_id, resource_data in existing_resources.items():
            try:
                # Extract configuration for fingerprinting
                extracted_config = self._extract_resource_config(resource_data)
                
                # Generate resource fingerprint using generic ResourceType for now
                # (can be enhanced with GCP-specific types)
                fingerprint = self.intelligence.generate_resource_fingerprint(
                    resource_config=resource_config,
                    cloud_state=resource_data,
                    resource_type=ResourceType.EC2_INSTANCE  # Generic for now
                )
                
                # Check resource health
                health = self._check_service_specific_health(resource_id, resource_data)
                
                # Generate optimization recommendations
                recommendations = self._generate_gcp_optimization_recommendations(
                    resource_config=resource_config,
                    cloud_state=resource_data
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
                print(f"⚠️  Failed to enhance {self.resource_type} {resource_id}: {str(e)}")
                enhanced_resources[resource_id] = resource_data
        
        return enhanced_resources
    
    def _generate_gcp_optimization_recommendations(self, 
                                                 resource_config: Dict[str, Any],
                                                 cloud_state: Dict[str, Any]) -> List[str]:
        """Generate GCP-specific optimization recommendations"""
        recommendations = []
        
        # GCP-specific optimization patterns
        if 'machine_type' in cloud_state:
            # Compute Engine optimizations
            machine_type = cloud_state.get('machine_type', '')
            if 'n1-' in machine_type:
                recommendations.append("Consider upgrading to E2 or N2 machine types for better price-performance")
            
            if machine_type.endswith('-1'):
                recommendations.append("Single vCPU instance may be underutilized - consider scaling up")
        
        # GCP-specific labels (equivalent to AWS tags)
        labels = cloud_state.get('labels', {})
        if not labels:
            recommendations.append("Add resource labels for better cost tracking and management")
        
        # Regional vs Zonal resources
        if 'zone' in cloud_state and not cloud_state.get('region'):
            recommendations.append("Consider regional resources for higher availability")
        
        # Sustained use discounts
        if 'uptime' in cloud_state and cloud_state.get('uptime', 0) > 86400 * 25:  # 25 days
            recommendations.append("Long-running instance qualifies for sustained use discounts")
        
        return recommendations
    
    def find_matching_resource(self, resource_config: Dict[str, Any]) -> Optional[Tuple[str, Dict[str, Any], float]]:
        """
        Find existing GCP resource that matches desired configuration
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
        Predict impact of proposed changes with GCP-specific considerations
        """
        return self._predict_service_specific_impact(current_state, desired_config)
    
    def detect_conflicts(self, desired_config: Dict[str, Any]) -> List[str]:
        """
        Detect potential conflicts with existing GCP resources
        """
        existing = self._discover_existing_resources()
        return self._detect_gcp_specific_conflicts(desired_config, existing)
    
    def _detect_gcp_specific_conflicts(self, desired_config: Dict[str, Any], 
                                     existing_resources: Dict[str, Any]) -> List[str]:
        """Detect GCP-specific resource conflicts"""
        conflicts = []
        
        # Name conflicts (GCP resources often have global uniqueness requirements)
        desired_name = desired_config.get('name', '')
        if desired_name:
            for resource_id, resource_data in existing_resources.items():
                existing_name = resource_data.get('name', '')
                if existing_name == desired_name:
                    conflicts.append(f"Resource name conflict: {desired_name} already exists")
        
        # Project-level conflicts
        project_id = desired_config.get('project_id', '')
        if project_id:
            # Check for project-level resource limits or conflicts
            pass
        
        # Zone/region conflicts
        zone = desired_config.get('zone', '')
        region = desired_config.get('region', '')
        if zone and region:
            # Validate zone is in specified region
            if not zone.startswith(region.rstrip('1234567890')):
                conflicts.append(f"Zone {zone} is not in region {region}")
        
        return conflicts
    
    def _discover_current_state(self, resource_name: str) -> Dict[str, Any]:
        """
        Discover current state using GCP-specific patterns
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
        Check if GCP resource is managed by InfraDSL
        """
        # Check labels for InfraDSL markers (GCP equivalent of AWS tags)
        labels = resource_data.get('labels', {})
        
        # Look for InfraDSL management labels
        if labels.get('infradsl-managed') == 'true':
            if labels.get('infradsl-resource-name') == resource_name:
                return True
        
        # Check descriptions
        description = resource_data.get('description', '')
        if resource_name in description or f"infradsl:{resource_name}" in description:
            return True
        
        # Check name patterns
        name = resource_data.get('name', '')
        if name == resource_name:
            return True
        
        return False
    
    def _build_desired_state(self, resource_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Build desired state with InfraDSL management labels
        """
        desired_state = {
            'exists': True,
            **resource_config
        }
        
        # Add standard InfraDSL labels (GCP uses labels instead of tags)
        if 'labels' not in desired_state:
            desired_state['labels'] = {}
        
        desired_state['labels'].update({
            'infradsl-managed': 'true',
            'infradsl-resource-type': self.resource_type,
            'infradsl-created-by': 'infradsl',
            'infradsl-resource-name': resource_config.get('name', ''),
            'infradsl-config-hash': self._generate_config_hash(resource_config)
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
        
        # Compare labels (GCP equivalent of AWS tags)
        current_labels = current.get('labels', {})
        desired_labels = desired.get('labels', {})
        
        if current_labels != desired_labels:
            changes['labels'] = {
                'from': current_labels,
                'to': desired_labels,
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
        Preview changes with GCP intelligence integration
        """
        current_state = self._discover_current_state(resource_name)
        desired_state = self._build_desired_state(resource_config)
        diff = self._calculate_diff(current_state, desired_state)
        
        result = {
            'resource_name': resource_name,
            'resource_type': self.resource_type,
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


class GCPServiceIntelligence:
    """
    Factory class for creating GCP service-specific intelligence implementations
    """
    
    @staticmethod
    def create_compute_engine_intelligence():
        """Create Compute Engine-specific intelligence implementation"""
        from .gcp_compute_engine_intelligence import ComputeEngineIntelligence
        return ComputeEngineIntelligence()
    
    @staticmethod
    def create_cloud_storage_intelligence():
        """Create Cloud Storage-specific intelligence implementation"""
        from .gcp_cloud_storage_intelligence import CloudStorageIntelligence
        return CloudStorageIntelligence()
    
    @staticmethod
    def create_cloud_sql_intelligence():
        """Create Cloud SQL-specific intelligence implementation"""
        from .gcp_cloud_sql_intelligence import CloudSQLIntelligence
        return CloudSQLIntelligence()
    
    @staticmethod
    def create_cloud_functions_intelligence():
        """Create Cloud Functions-specific intelligence implementation"""
        from .gcp_cloud_functions_intelligence import CloudFunctionsIntelligence
        return CloudFunctionsIntelligence()
    
    @staticmethod
    def create_cloud_dns_intelligence():
        """Create Cloud DNS-specific intelligence implementation"""
        from .gcp_cloud_dns_intelligence import CloudDNSIntelligence
        return CloudDNSIntelligence()
    
    @staticmethod
    def create_firebase_intelligence():
        """Create Firebase-specific intelligence implementation"""
        from .gcp_firebase_intelligence import FirebaseIntelligence
        return FirebaseIntelligence()
    
    @staticmethod
    def get_all_services():
        """Get list of all supported GCP services"""
        return [
            'compute_engine',
            'cloud_storage', 
            'cloud_sql',
            'cloud_functions',
            'cloud_dns',
            'firebase'
        ]
    
    @staticmethod
    def create_intelligence_for_service(service_name: str):
        """Create intelligence implementation for any supported GCP service"""
        intelligence_map = {
            'compute_engine': GCPServiceIntelligence.create_compute_engine_intelligence,
            'cloud_storage': GCPServiceIntelligence.create_cloud_storage_intelligence,
            'cloud_sql': GCPServiceIntelligence.create_cloud_sql_intelligence,
            'cloud_functions': GCPServiceIntelligence.create_cloud_functions_intelligence,
            'cloud_dns': GCPServiceIntelligence.create_cloud_dns_intelligence,
            'firebase': GCPServiceIntelligence.create_firebase_intelligence
        }
        
        if service_name not in intelligence_map:
            raise ValueError(f"Unsupported GCP service: {service_name}")
        
        return intelligence_map[service_name]()


def enhance_gcp_resource_with_intelligence(resource_class, intelligence_class):
    """
    Decorator to enhance existing GCP resource classes with intelligence
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