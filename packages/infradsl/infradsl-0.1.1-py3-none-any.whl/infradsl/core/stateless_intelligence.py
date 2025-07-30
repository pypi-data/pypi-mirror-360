"""
InfraDSL Stateless Intelligence System

Revolutionary stateless infrastructure management with:
- Smart resource fingerprinting beyond traditional tagging
- Predictive change impact analysis
- Resource health monitoring
- Dependency intelligence
- Conflict prevention
"""

import hashlib
import json
import time
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum


class ResourceType(Enum):
    """Supported resource types for fingerprinting"""
    CLOUDFRONT_DISTRIBUTION = "cloudfront_distribution"
    S3_BUCKET = "s3_bucket"
    ROUTE53_RECORD = "route53_record"
    ACM_CERTIFICATE = "acm_certificate"
    EC2_INSTANCE = "ec2_instance"
    RDS_INSTANCE = "rds_instance"
    LAMBDA_FUNCTION = "lambda_function"


class ChangeImpact(Enum):
    """Impact levels for infrastructure changes"""
    LOW = 1           # No downtime, quick propagation
    MEDIUM = 2        # Brief downtime or slow propagation
    HIGH = 3          # Significant downtime or resource recreation
    CRITICAL = 4      # Data loss risk or major service disruption
    
    @property
    def value_name(self):
        """Get string representation of impact level"""
        names = {1: "low", 2: "medium", 3: "high", 4: "critical"}
        return names[self.value]


@dataclass
class ResourceFingerprint:
    """Unique resource identification beyond traditional tags"""
    resource_id: str
    resource_type: ResourceType
    configuration_hash: str
    creation_signature: str
    dependency_fingerprint: str
    ownership_markers: List[str]
    last_seen: datetime
    confidence_score: float  # 0.0 to 1.0


@dataclass
class ChangeImpactAnalysis:
    """Predictive analysis of infrastructure changes"""
    change_type: str
    impact_level: ChangeImpact
    estimated_downtime: int  # seconds
    propagation_time: int    # seconds
    cost_impact: float       # dollars
    affected_resources: List[str]
    recommendations: List[str]
    rollback_complexity: str


@dataclass
class ResourceHealth:
    """Resource health status"""
    resource_id: str
    health_score: float  # 0.0 to 1.0
    issues: List[str]
    performance_metrics: Dict[str, float]
    last_check: datetime


class StatelessIntelligence:
    """Core stateless intelligence engine"""
    
    def __init__(self):
        self.fingerprint_cache: Dict[str, ResourceFingerprint] = {}
        self.health_cache: Dict[str, ResourceHealth] = {}
        self.dependency_graph: Dict[str, List[str]] = {}
    
    def generate_resource_fingerprint(self, 
                                    resource_config: Dict[str, Any],
                                    cloud_state: Dict[str, Any],
                                    resource_type: ResourceType) -> ResourceFingerprint:
        """
        Generate unique resource fingerprint based on immutable characteristics
        Goes beyond tags to create resilient resource identification
        """
        
        # 1. Configuration DNA - Hash of normalized configuration
        config_dna = self._generate_configuration_hash(resource_config)
        
        # 2. Creation Signature - Pattern of resource creation
        creation_sig = self._generate_creation_signature(cloud_state, resource_type)
        
        # 3. Dependency Fingerprint - Relationships with other resources
        dep_fingerprint = self._generate_dependency_fingerprint(resource_config, cloud_state)
        
        # 4. Ownership Markers - Multiple identification methods
        ownership_markers = self._extract_ownership_markers(resource_config, cloud_state)
        
        # 5. Confidence Score - How confident are we in this identification
        confidence = self._calculate_confidence_score(cloud_state, ownership_markers)
        
        return ResourceFingerprint(
            resource_id=cloud_state.get('id', ''),
            resource_type=resource_type,
            configuration_hash=config_dna,
            creation_signature=creation_sig,
            dependency_fingerprint=dep_fingerprint,
            ownership_markers=ownership_markers,
            last_seen=datetime.now(),
            confidence_score=confidence
        )
    
    def _generate_configuration_hash(self, config: Dict[str, Any]) -> str:
        """Generate SHA256 hash of normalized configuration"""
        # Normalize config by sorting keys and handling None values
        normalized = self._normalize_config(config)
        config_str = json.dumps(normalized, sort_keys=True)
        return hashlib.sha256(config_str.encode()).hexdigest()[:16]
    
    def _normalize_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize configuration for consistent hashing"""
        normalized = {}
        
        for key, value in config.items():
            if value is None:
                continue
            elif isinstance(value, dict):
                normalized[key] = self._normalize_config(value)
            elif isinstance(value, list):
                # Sort lists for consistent ordering
                if value and isinstance(value[0], dict):
                    normalized[key] = sorted([self._normalize_config(item) for item in value],
                                           key=lambda x: json.dumps(x, sort_keys=True))
                else:
                    normalized[key] = sorted(value) if value else []
            else:
                normalized[key] = value
        
        return normalized
    
    def _generate_creation_signature(self, cloud_state: Dict[str, Any], 
                                   resource_type: ResourceType) -> str:
        """Generate signature based on resource creation patterns"""
        
        signature_elements = []
        
        if resource_type == ResourceType.CLOUDFRONT_DISTRIBUTION:
            # CloudFront-specific creation patterns
            signature_elements.extend([
                cloud_state.get('domain_name', '')[:8],  # First 8 chars of domain
                str(len(cloud_state.get('origins', []))),  # Number of origins
                cloud_state.get('price_class', ''),
                str(cloud_state.get('enabled', False))
            ])
        
        # Add timestamp-based elements for uniqueness
        created_date = cloud_state.get('created_date') or cloud_state.get('last_modified')
        if created_date:
            if hasattr(created_date, 'strftime'):
                signature_elements.append(created_date.strftime('%Y%m%d'))
            else:
                signature_elements.append(str(created_date)[:10])
        
        signature = '_'.join(filter(None, signature_elements))
        return hashlib.md5(signature.encode()).hexdigest()[:12]
    
    def _generate_dependency_fingerprint(self, config: Dict[str, Any], 
                                       cloud_state: Dict[str, Any]) -> str:
        """Generate fingerprint based on resource dependencies"""
        
        dependencies = []
        
        # Extract S3 bucket dependencies
        if 'origins' in cloud_state:
            for origin in cloud_state['origins']:
                if 's3' in origin.get('domain_name', '').lower():
                    dependencies.append(f"s3:{origin['domain_name']}")
        
        # Extract custom domain dependencies
        if 'aliases' in cloud_state:
            for alias in cloud_state['aliases']:
                dependencies.append(f"domain:{alias}")
        
        # Extract certificate dependencies
        viewer_cert = cloud_state.get('viewer_certificate', {})
        if viewer_cert.get('acm_certificate_arn'):
            cert_id = viewer_cert['acm_certificate_arn'].split('/')[-1]
            dependencies.append(f"cert:{cert_id}")
        
        # Sort for consistent fingerprint
        dependencies.sort()
        dep_string = ','.join(dependencies)
        
        return hashlib.md5(dep_string.encode()).hexdigest()[:10]
    
    def _extract_ownership_markers(self, config: Dict[str, Any], 
                                 cloud_state: Dict[str, Any]) -> List[str]:
        """Extract multiple ownership identification markers"""
        
        markers = []
        
        # 1. InfraDSL comment signature
        comment = cloud_state.get('comment', '')
        if 'infradsl' in comment.lower():
            markers.append(f"infradsl_comment:{comment}")
        
        # 2. Naming pattern analysis
        resource_name = config.get('name', '')
        if resource_name:
            markers.append(f"name_pattern:{resource_name}")
        
        # 3. Configuration pattern markers
        if 'origins' in cloud_state:
            origin_patterns = []
            for origin in cloud_state['origins']:
                if origin.get('id'):
                    origin_patterns.append(origin['id'])
            if origin_patterns:
                markers.append(f"origin_pattern:{'_'.join(sorted(origin_patterns))}")
        
        # 4. Domain pattern markers
        if 'aliases' in cloud_state:
            domain_patterns = sorted(cloud_state['aliases'])
            if domain_patterns:
                markers.append(f"domain_pattern:{'_'.join(domain_patterns)}")
        
        return markers
    
    def _calculate_confidence_score(self, cloud_state: Dict[str, Any], 
                                  ownership_markers: List[str]) -> float:
        """Calculate confidence score for resource identification"""
        
        score = 0.0
        
        # Base score for having the resource
        score += 0.2
        
        # Score for InfraDSL markers
        infradsl_markers = [m for m in ownership_markers if 'infradsl' in m.lower()]
        score += len(infradsl_markers) * 0.3
        
        # Score for naming patterns
        name_markers = [m for m in ownership_markers if 'name_pattern' in m]
        score += len(name_markers) * 0.2
        
        # Score for configuration complexity (more complex = more unique)
        if 'origins' in cloud_state:
            score += min(len(cloud_state['origins']) * 0.1, 0.2)
        
        if 'aliases' in cloud_state:
            score += min(len(cloud_state['aliases']) * 0.1, 0.2)
        
        # Cap at 1.0
        return min(score, 1.0)
    
    def predict_change_impact(self, 
                            current_state: Dict[str, Any],
                            desired_state: Dict[str, Any],
                            resource_type: ResourceType) -> ChangeImpactAnalysis:
        """
        Predict the impact of infrastructure changes
        Revolutionary feature for preventing deployment issues
        """
        
        if resource_type == ResourceType.CLOUDFRONT_DISTRIBUTION:
            return self._predict_cloudfront_impact(current_state, desired_state)
        
        # Default impact analysis
        return ChangeImpactAnalysis(
            change_type="unknown",
            impact_level=ChangeImpact.MEDIUM,
            estimated_downtime=0,
            propagation_time=300,
            cost_impact=0.0,
            affected_resources=[],
            recommendations=["Review changes manually"],
            rollback_complexity="medium"
        )
    
    def _predict_cloudfront_impact(self, 
                                 current: Dict[str, Any],
                                 desired: Dict[str, Any]) -> ChangeImpactAnalysis:
        """Predict CloudFront-specific change impacts"""
        
        changes = []
        impact_level = ChangeImpact.LOW
        downtime = 0
        propagation_time = 900  # 15 minutes default
        cost_impact = 0.0
        affected_resources = []
        recommendations = []
        rollback_complexity = "low"
        
        # Analyze specific changes
        
        # 1. Origin changes
        if current.get('origins') != desired.get('origins'):
            changes.append("origin_modification")
            impact_level = ChangeImpact.MEDIUM if impact_level.value < ChangeImpact.MEDIUM.value else impact_level
            propagation_time = max(propagation_time, 1200)  # 20 minutes
            recommendations.append("Test origin accessibility before deployment")
            recommendations.append("Consider gradual traffic shifting")
        
        # 2. Domain/alias changes
        current_aliases = set(current.get('aliases', []))
        desired_aliases = set(desired.get('aliases', []))
        
        if current_aliases != desired_aliases:
            changes.append("domain_modification")
            impact_level = ChangeImpact.HIGH if impact_level.value < ChangeImpact.HIGH.value else impact_level
            propagation_time = max(propagation_time, 1800)  # 30 minutes
            
            # Detect if removing domains (higher impact)
            if current_aliases - desired_aliases:
                recommendations.append("WARNING: Removing domains may break existing traffic")
                rollback_complexity = "high"
            
            recommendations.append("Update DNS records accordingly")
            recommendations.append("Test domain resolution after deployment")
        
        # 3. SSL certificate changes
        current_cert = current.get('viewer_certificate', {}).get('acm_certificate_arn')
        desired_cert = desired.get('viewer_certificate', {}).get('acm_certificate_arn')
        
        if current_cert != desired_cert:
            changes.append("ssl_certificate_change")
            impact_level = ChangeImpact.HIGH if impact_level.value < ChangeImpact.HIGH.value else impact_level
            recommendations.append("Verify certificate covers all domains")
            recommendations.append("Test HTTPS connectivity after deployment")
        
        # 4. Behavior changes
        current_behaviors = current.get('default_cache_behavior', {})
        desired_behaviors = desired.get('default_cache_behavior', {})
        
        if current_behaviors != desired_behaviors:
            changes.append("cache_behavior_modification")
            impact_level = ChangeImpact.MEDIUM if impact_level.value < ChangeImpact.MEDIUM.value else impact_level
            recommendations.append("Monitor cache hit rates after deployment")
            recommendations.append("Consider cache invalidation if needed")
        
        # 5. Enabled/disabled state
        if current.get('enabled') != desired.get('enabled'):
            if not desired.get('enabled'):
                changes.append("distribution_disable")
                impact_level = ChangeImpact.CRITICAL
                downtime = 60  # 1 minute
                recommendations.append("CRITICAL: This will disable the distribution")
                recommendations.append("Ensure this is intentional")
            else:
                changes.append("distribution_enable")
                impact_level = ChangeImpact.MEDIUM if impact_level.value < ChangeImpact.MEDIUM.value else impact_level
        
        # Calculate cost impact
        price_class_change = current.get('price_class') != desired.get('price_class')
        if price_class_change:
            # Rough cost impact estimation
            cost_impact = self._estimate_cloudfront_cost_impact(
                current.get('price_class'), 
                desired.get('price_class')
            )
        
        # Determine affected resources
        affected_resources = self._find_affected_resources(current, desired)
        
        change_type = ", ".join(changes) if changes else "configuration_update"
        
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
    
    def _estimate_cloudfront_cost_impact(self, current_price_class: str, 
                                       desired_price_class: str) -> float:
        """Estimate cost impact of price class changes"""
        
        price_class_costs = {
            'PriceClass_100': 1.0,    # US, Canada, Europe
            'PriceClass_200': 1.5,    # + Asia Pacific
            'PriceClass_All': 2.0     # All edge locations
        }
        
        current_cost = price_class_costs.get(current_price_class, 1.5)
        desired_cost = price_class_costs.get(desired_price_class, 1.5)
        
        # Return percentage change
        return (desired_cost - current_cost) / current_cost * 100
    
    def _find_affected_resources(self, current: Dict[str, Any], 
                               desired: Dict[str, Any]) -> List[str]:
        """Find resources affected by CloudFront changes"""
        
        affected = []
        
        # DNS records for domain changes
        current_aliases = set(current.get('aliases', []))
        desired_aliases = set(desired.get('aliases', []))
        
        for alias in current_aliases.union(desired_aliases):
            affected.append(f"route53_record:{alias}")
        
        # S3 buckets for origin changes
        all_origins = current.get('origins', []) + desired.get('origins', [])
        for origin in all_origins:
            domain = origin.get('domain_name', '')
            if 's3' in domain.lower():
                affected.append(f"s3_bucket:{domain}")
        
        return list(set(affected))  # Remove duplicates
    
    def check_resource_health(self, resource_id: str, 
                            cloud_state: Dict[str, Any],
                            resource_type: ResourceType) -> ResourceHealth:
        """Check resource health status"""
        
        if resource_type == ResourceType.CLOUDFRONT_DISTRIBUTION:
            return self._check_cloudfront_health(resource_id, cloud_state)
        
        # Default health check
        return ResourceHealth(
            resource_id=resource_id,
            health_score=0.8,
            issues=[],
            performance_metrics={},
            last_check=datetime.now()
        )
    
    def _check_cloudfront_health(self, resource_id: str, 
                               cloud_state: Dict[str, Any]) -> ResourceHealth:
        """Check CloudFront distribution health"""
        
        health_score = 1.0
        issues = []
        metrics = {}
        
        # Check distribution status
        status = cloud_state.get('status', '')
        if status != 'Deployed':
            health_score -= 0.3
            issues.append(f"Distribution status: {status}")
        
        # Check if enabled
        if not cloud_state.get('enabled', True):
            health_score -= 0.2
            issues.append("Distribution is disabled")
        
        # Check origins
        origins = cloud_state.get('origins', [])
        if not origins:
            health_score -= 0.4
            issues.append("No origins configured")
        else:
            metrics['origin_count'] = len(origins)
        
        # Check aliases
        aliases = cloud_state.get('aliases', [])
        metrics['alias_count'] = len(aliases)
        
        # Check SSL certificate
        viewer_cert = cloud_state.get('viewer_certificate', {})
        if not viewer_cert.get('acm_certificate_arn') and aliases:
            health_score -= 0.3
            issues.append("Custom domains without SSL certificate")
        
        # Price class efficiency
        price_class = cloud_state.get('price_class', 'PriceClass_All')
        if len(aliases) < 3 and price_class == 'PriceClass_All':
            issues.append("Consider PriceClass_100 for cost optimization")
        
        return ResourceHealth(
            resource_id=resource_id,
            health_score=max(health_score, 0.0),
            issues=issues,
            performance_metrics=metrics,
            last_check=datetime.now()
        )
    
    def detect_resource_conflicts(self, desired_config: Dict[str, Any],
                                existing_resources: Dict[str, Any]) -> List[str]:
        """Detect potential conflicts with existing resources"""
        
        conflicts = []
        
        # Domain conflicts
        desired_aliases = set(desired_config.get('aliases', []))
        
        for resource_id, resource_data in existing_resources.items():
            existing_aliases = set(resource_data.get('aliases', []))
            
            # Check for domain conflicts
            conflicting_domains = desired_aliases.intersection(existing_aliases)
            if conflicting_domains:
                conflicts.append(
                    f"Domain conflict with {resource_id}: {', '.join(conflicting_domains)}"
                )
        
        return conflicts
    
    def generate_optimization_recommendations(self, 
                                            resource_config: Dict[str, Any],
                                            cloud_state: Dict[str, Any],
                                            resource_type: ResourceType) -> List[str]:
        """Generate optimization recommendations"""
        
        recommendations = []
        
        if resource_type == ResourceType.CLOUDFRONT_DISTRIBUTION:
            # Cost optimization
            price_class = cloud_state.get('price_class', 'PriceClass_All')
            aliases = cloud_state.get('aliases', [])
            
            if len(aliases) <= 2 and price_class == 'PriceClass_All':
                recommendations.append(
                    "Consider PriceClass_100 for cost savings with limited geographic reach"
                )
            
            # Performance optimization
            origins = cloud_state.get('origins', [])
            if len(origins) > 1:
                recommendations.append(
                    "Consider implementing origin failover for high availability"
                )
            
            # Security optimization
            viewer_cert = cloud_state.get('viewer_certificate', {})
            if not viewer_cert.get('acm_certificate_arn') and aliases:
                recommendations.append(
                    "Add SSL certificate for secure HTTPS connections"
                )
        
        return recommendations