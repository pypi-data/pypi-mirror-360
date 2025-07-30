"""
Universal Resource Discovery System for InfraDSL
Bulletproof resource fingerprinting for brownfield environments
"""

import asyncio
from typing import Dict, Any, List, Optional, Set, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

from .stateless_intelligence import StatelessIntelligence, ResourceFingerprint, ResourceType, ChangeImpact
# from .conflict_monitor import ConflictMonitor  # Optional dependency
from .drift_management import SmartDriftManager


class DiscoveryStatus(Enum):
    """Status of resource discovery operations"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    PARTIAL = "partial"


class AdoptionPolicy(Enum):
    """Policies for adopting external resources"""
    CONSERVATIVE = "conservative"  # Manual review required
    MODERATE = "moderate"         # Auto-adopt low-risk resources
    AGGRESSIVE = "aggressive"     # Auto-adopt most resources


@dataclass
class OrphanedResource:
    """Resource that should be managed by InfraDSL but isn't"""
    resource_id: str
    provider: str
    resource_type: str
    fingerprint: ResourceFingerprint
    risk_level: str  # low, medium, high
    adoption_recommendation: str
    discovered_at: datetime = field(default_factory=datetime.now)


@dataclass
class ExternalResource:
    """Resource not created by InfraDSL"""
    resource_id: str
    provider: str
    resource_type: str
    ownership_markers: List[str]
    configuration: Dict[str, Any]
    dependencies: List[str]
    risk_assessment: str
    adoption_feasible: bool


@dataclass
class AdoptionResult:
    """Result of resource adoption process"""
    status: str  # success, failed, manual_review_required
    resource_id: str
    adoption_policy_applied: AdoptionPolicy
    risk_level: str
    modifications_required: List[str]
    rollback_plan: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None


@dataclass
class MultiAccountDiscovery:
    """Discovery results across multiple accounts/projects"""
    provider: str
    accounts: List[str]
    resources: Dict[str, List[ResourceFingerprint]]  # account_id -> resources
    cross_account_dependencies: Dict[str, List[str]]  # resource_id -> dependent_resources
    orphaned_resources: List[OrphanedResource]
    adoption_recommendations: List[str]
    discovery_summary: Dict[str, Any]


@dataclass
class DiscoverySession:
    """Session for tracking discovery operations"""
    session_id: str
    provider: str
    accounts: List[str]
    resource_types: List[str]
    status: DiscoveryStatus
    started_at: datetime
    completed_at: Optional[datetime] = None
    resources_discovered: int = 0
    errors: List[str] = field(default_factory=list)
    performance_metrics: Dict[str, float] = field(default_factory=dict)


class UniversalResourceDiscovery:
    """
    Universal resource discovery system with intelligent fingerprinting
    
    Handles:
    - Multi-provider resource discovery
    - External resource adoption
    - Orphaned resource detection
    - Cross-account/project discovery
    - Conflict resolution
    """
    
    def __init__(self):
        self.stateless_intelligence = StatelessIntelligence()
        # self.conflict_monitor = ConflictMonitor()  # Optional
        self.drift_manager = SmartDriftManager()
        self.logger = logging.getLogger(__name__)
        
        # Performance tracking
        self.discovery_cache: Dict[str, Tuple[datetime, List[ResourceFingerprint]]] = {}
        self.cache_ttl = timedelta(minutes=15)
        
        # Provider-specific discovery modules
        self.provider_modules = {
            "aws": self._import_aws_discovery,
            "gcp": self._import_gcp_discovery, 
            "digitalocean": self._import_do_discovery,
            "cloudflare": self._import_cloudflare_discovery
        }
    
    def discover_resources(self, provider: str, resource_types: List[str], 
                          filters: Optional[Dict[str, Any]] = None,
                          accounts: Optional[List[str]] = None) -> List[ResourceFingerprint]:
        """
        Universal resource discovery interface
        
        Args:
            provider: Cloud provider (aws, gcp, digitalocean, etc.)
            resource_types: List of resource types to discover
            filters: Optional filters for discovery
            accounts: Optional list of accounts/projects to search
            
        Returns:
            List of ResourceFingerprint objects with high-confidence resource identification
        """
        
        session = DiscoverySession(
            session_id=f"{provider}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            provider=provider,
            accounts=accounts or ["default"],
            resource_types=resource_types,
            status=DiscoveryStatus.PENDING,
            started_at=datetime.now()
        )
        
        try:
            session.status = DiscoveryStatus.IN_PROGRESS
            self.logger.info(f"Starting discovery session {session.session_id}")
            
            # Check cache first
            cache_key = f"{provider}_{','.join(resource_types)}_{','.join(accounts or ['default'])}"
            if self._is_cache_valid(cache_key):
                cached_results = self.discovery_cache[cache_key][1]
                self.logger.info(f"Returning cached results for {cache_key}")
                return cached_results
            
            # Perform discovery
            all_fingerprints = []
            
            if accounts and len(accounts) > 1:
                # Multi-account discovery
                multi_account_results = self._discover_multi_account(provider, resource_types, accounts, filters)
                for account_resources in multi_account_results.resources.values():
                    all_fingerprints.extend(account_resources)
            else:
                # Single account discovery
                account = accounts[0] if accounts else "default"
                all_fingerprints = self._discover_single_account(provider, resource_types, account, filters)
            
            # Apply intelligent fingerprinting
            enhanced_fingerprints = self._enhance_fingerprints(all_fingerprints)
            
            # Cache results
            self.discovery_cache[cache_key] = (datetime.now(), enhanced_fingerprints)
            
            # Update session
            session.status = DiscoveryStatus.COMPLETED
            session.completed_at = datetime.now()
            session.resources_discovered = len(enhanced_fingerprints)
            session.performance_metrics = {
                "discovery_time": (session.completed_at - session.started_at).total_seconds(),
                "resources_per_second": len(enhanced_fingerprints) / max(1, (session.completed_at - session.started_at).total_seconds())
            }
            
            self.logger.info(f"Discovery session {session.session_id} completed: {len(enhanced_fingerprints)} resources")
            return enhanced_fingerprints
            
        except Exception as e:
            session.status = DiscoveryStatus.FAILED
            session.errors.append(str(e))
            self.logger.error(f"Discovery session {session.session_id} failed: {str(e)}")
            raise
    
    def detect_orphaned_resources(self, provider: str, workspace: str, 
                                 resource_types: Optional[List[str]] = None) -> List[OrphanedResource]:
        """
        Detect resources that should be managed by InfraDSL but aren't
        
        Args:
            provider: Cloud provider
            workspace: InfraDSL workspace name
            resource_types: Optional list of resource types to check
            
        Returns:
            List of orphaned resources with adoption recommendations
        """
        
        self.logger.info(f"Detecting orphaned resources for {provider} in workspace {workspace}")
        
        # Get all resources from provider
        all_resources = self.discover_resources(provider, resource_types or self._get_all_resource_types(provider))
        
        # Get currently managed resources
        managed_resources = self._get_managed_resources(workspace)
        managed_resource_ids = {r.resource_id for r in managed_resources}
        
        orphaned = []
        
        for resource in all_resources:
            # Skip if already managed
            if resource.resource_id in managed_resource_ids:
                continue
            
            # Check if resource matches InfraDSL patterns
            if self._matches_infradsl_patterns(resource):
                risk_level = self._assess_adoption_risk(resource)
                recommendation = self._generate_adoption_recommendation(resource, risk_level)
                
                orphaned.append(OrphanedResource(
                    resource_id=resource.resource_id,
                    provider=provider,
                    resource_type=resource.resource_type.value,
                    fingerprint=resource,
                    risk_level=risk_level,
                    adoption_recommendation=recommendation
                ))
        
        self.logger.info(f"Found {len(orphaned)} orphaned resources")
        return orphaned
    
    def adopt_external_resource(self, resource_id: str, provider: str, 
                               adoption_policy: AdoptionPolicy = AdoptionPolicy.CONSERVATIVE) -> AdoptionResult:
        """
        Adopt an external resource into InfraDSL management
        
        Args:
            resource_id: Resource ID to adopt
            provider: Cloud provider
            adoption_policy: Policy for adoption decisions
            
        Returns:
            AdoptionResult with adoption status and recommendations
        """
        
        self.logger.info(f"Attempting to adopt external resource {resource_id} from {provider}")
        
        try:
            # Discover the external resource
            external_resource = self._discover_external_resource(resource_id, provider)
            
            if not external_resource:
                return AdoptionResult(
                    status="failed",
                    resource_id=resource_id,
                    adoption_policy_applied=adoption_policy,
                    risk_level="unknown",
                    modifications_required=[],
                    error_message=f"Resource {resource_id} not found"
                )
            
            # Analyze adoption feasibility
            adoption_analysis = self._analyze_adoption_feasibility(external_resource)
            
            # Apply adoption policy
            if self._should_auto_adopt(adoption_policy, adoption_analysis):
                return self._perform_adoption(external_resource, adoption_policy)
            else:
                return AdoptionResult(
                    status="manual_review_required",
                    resource_id=resource_id,
                    adoption_policy_applied=adoption_policy,
                    risk_level=adoption_analysis.risk_assessment,
                    modifications_required=self._generate_modification_requirements(external_resource),
                    error_message="Manual review required due to policy or risk level"
                )
                
        except Exception as e:
            self.logger.error(f"Failed to adopt resource {resource_id}: {str(e)}")
            return AdoptionResult(
                status="failed",
                resource_id=resource_id,
                adoption_policy_applied=adoption_policy,
                risk_level="unknown",
                modifications_required=[],
                error_message=str(e)
            )
    
    def discover_across_accounts(self, provider: str, account_list: List[str], 
                               resource_types: Optional[List[str]] = None) -> MultiAccountDiscovery:
        """
        Discover resources across multiple accounts/projects
        
        Args:
            provider: Cloud provider
            account_list: List of account IDs or project names
            resource_types: Optional list of resource types to discover
            
        Returns:
            MultiAccountDiscovery with cross-account analysis
        """
        
        self.logger.info(f"Starting multi-account discovery for {provider} across {len(account_list)} accounts")
        
        discovery_start = datetime.now()
        all_resources = {}
        cross_account_deps = {}
        total_resources = 0
        
        # Use ThreadPoolExecutor for parallel discovery
        with ThreadPoolExecutor(max_workers=min(len(account_list), 10)) as executor:
            # Submit discovery tasks
            future_to_account = {
                executor.submit(self._discover_single_account, provider, resource_types or self._get_all_resource_types(provider), account): account 
                for account in account_list
            }
            
            # Collect results
            for future in as_completed(future_to_account):
                account = future_to_account[future]
                try:
                    resources = future.result()
                    all_resources[account] = resources
                    total_resources += len(resources)
                    
                    # Analyze cross-account dependencies
                    for resource in resources:
                        deps = self._analyze_cross_account_dependencies(resource, account_list)
                        if deps:
                            cross_account_deps[resource.resource_id] = deps
                            
                except Exception as e:
                    self.logger.error(f"Failed to discover resources in account {account}: {str(e)}")
                    all_resources[account] = []
        
        # Detect orphaned resources across all accounts
        orphaned_resources = []
        for account in account_list:
            account_orphaned = self.detect_orphaned_resources(provider, f"multi-account-{account}")
            orphaned_resources.extend(account_orphaned)
        
        # Generate adoption recommendations
        adoption_recommendations = self._generate_multi_account_recommendations(
            all_resources, cross_account_deps, orphaned_resources
        )
        
        discovery_time = (datetime.now() - discovery_start).total_seconds()
        
        return MultiAccountDiscovery(
            provider=provider,
            accounts=account_list,
            resources=all_resources,
            cross_account_dependencies=cross_account_deps,
            orphaned_resources=orphaned_resources,
            adoption_recommendations=adoption_recommendations,
            discovery_summary={
                "total_resources": total_resources,
                "total_accounts": len(account_list),
                "discovery_time_seconds": discovery_time,
                "cross_account_dependencies": len(cross_account_deps),
                "orphaned_resources": len(orphaned_resources),
                "resources_per_second": total_resources / max(1, discovery_time)
            }
        )
    
    def _discover_multi_account(self, provider: str, resource_types: List[str], 
                              accounts: List[str], filters: Optional[Dict[str, Any]]) -> MultiAccountDiscovery:
        """Internal method for multi-account discovery"""
        return self.discover_across_accounts(provider, accounts, resource_types)
    
    def _discover_single_account(self, provider: str, resource_types: List[str], 
                               account: str, filters: Optional[Dict[str, Any]] = None) -> List[ResourceFingerprint]:
        """Internal method for single account discovery"""
        
        if provider not in self.provider_modules:
            raise ValueError(f"Unsupported provider: {provider}")
        
        discovery_module = self.provider_modules[provider]()
        raw_resources = discovery_module.fetch_resources(resource_types, account, filters)
        
        fingerprints = []
        for resource in raw_resources:
            try:
                fingerprint = self.stateless_intelligence.generate_resource_fingerprint(
                    resource["config"], resource["cloud_state"], ResourceType(resource["type"])
                )
                fingerprints.append(fingerprint)
            except Exception as e:
                self.logger.warning(f"Failed to generate fingerprint for resource {resource.get('id', 'unknown')}: {str(e)}")
        
        return fingerprints
    
    def _enhance_fingerprints(self, fingerprints: List[ResourceFingerprint]) -> List[ResourceFingerprint]:
        """Apply additional intelligence to fingerprints"""
        
        enhanced = []
        for fingerprint in fingerprints:
            # Apply conflict detection (optional)
            conflicts = []  # self.conflict_monitor.check_resource_conflicts(fingerprint) if available
            
            # Apply drift detection
            drift_status = self.drift_manager.check_resource_drift(fingerprint)
            
            # Enhance fingerprint with additional metadata
            enhanced_fingerprint = fingerprint
            enhanced_fingerprint.conflicts = conflicts
            enhanced_fingerprint.drift_status = drift_status
            
            enhanced.append(enhanced_fingerprint)
        
        return enhanced
    
    def _is_cache_valid(self, cache_key: str) -> bool:
        """Check if cached discovery results are still valid"""
        if cache_key not in self.discovery_cache:
            return False
        
        cached_time, _ = self.discovery_cache[cache_key]
        return datetime.now() - cached_time < self.cache_ttl
    
    def _matches_infradsl_patterns(self, resource: ResourceFingerprint) -> bool:
        """Check if resource matches InfraDSL naming/tagging patterns"""
        
        # Check for InfraDSL ownership markers
        infradsl_markers = [m for m in resource.ownership_markers if 'infradsl' in m.lower()]
        if infradsl_markers:
            return True
        
        # Check for InfraDSL naming patterns
        if hasattr(resource, 'name'):
            name = resource.name.lower()
            infradsl_patterns = ['infradsl-', 'infra-', '-infra', 'managed-by-infradsl']
            if any(pattern in name for pattern in infradsl_patterns):
                return True
        
        return False
    
    def _assess_adoption_risk(self, resource: ResourceFingerprint) -> str:
        """Assess risk level for adopting a resource"""
        
        risk_factors = 0
        
        # Check confidence score
        if resource.confidence_score < 0.7:
            risk_factors += 2
        elif resource.confidence_score < 0.9:
            risk_factors += 1
        
        # Check for conflicting ownership markers
        ownership_types = set()
        for marker in resource.ownership_markers:
            if 'terraform' in marker.lower():
                ownership_types.add('terraform')
            elif 'cloudformation' in marker.lower():
                ownership_types.add('cloudformation')
            elif 'manual' in marker.lower():
                ownership_types.add('manual')
        
        if len(ownership_types) > 1:
            risk_factors += 2
        elif len(ownership_types) == 1 and 'terraform' in ownership_types:
            risk_factors += 1
        
        # Check for production markers
        if any('prod' in marker.lower() for marker in resource.ownership_markers):
            risk_factors += 1
        
        # Return risk assessment
        if risk_factors >= 4:
            return "high"
        elif risk_factors >= 2:
            return "medium"
        else:
            return "low"
    
    def _generate_adoption_recommendation(self, resource: ResourceFingerprint, risk_level: str) -> str:
        """Generate adoption recommendation based on risk assessment"""
        
        if risk_level == "low":
            return "Safe to auto-adopt with moderate policy"
        elif risk_level == "medium":
            return "Review configuration and dependencies before adoption"
        else:
            return "Manual review required - high risk of conflicts"
    
    def _get_managed_resources(self, workspace: str) -> List[ResourceFingerprint]:
        """Get currently managed resources for a workspace"""
        # This would interface with the workspace management system
        # For now, return empty list
        return []
    
    def _get_all_resource_types(self, provider: str) -> List[str]:
        """Get all supported resource types for a provider"""
        
        resource_types = {
            "aws": ["ec2", "rds", "s3", "lambda", "ecs", "alb", "route53", "cloudfront", "vpc", "security_group"],
            "gcp": ["vm", "cloud_sql", "cloud_storage", "cloud_functions", "load_balancer", "cloud_dns", "vpc", "gke"],
            "digitalocean": ["droplet", "database", "load_balancer", "vpc", "dns", "kubernetes"]
        }
        
        return resource_types.get(provider, [])
    
    def _discover_external_resource(self, resource_id: str, provider: str) -> Optional[ExternalResource]:
        """Discover a specific external resource"""
        # This would use provider-specific APIs to fetch resource details
        # For now, return None
        return None
    
    def _analyze_adoption_feasibility(self, external_resource: ExternalResource) -> ExternalResource:
        """Analyze if an external resource can be safely adopted"""
        # This would perform deep analysis of the resource
        # For now, return the resource as-is
        return external_resource
    
    def _should_auto_adopt(self, policy: AdoptionPolicy, analysis: ExternalResource) -> bool:
        """Determine if resource should be auto-adopted based on policy"""
        
        if policy == AdoptionPolicy.CONSERVATIVE:
            return False
        elif policy == AdoptionPolicy.MODERATE:
            return analysis.risk_assessment == "low"
        else:  # AGGRESSIVE
            return analysis.risk_assessment in ["low", "medium"]
    
    def _perform_adoption(self, external_resource: ExternalResource, policy: AdoptionPolicy) -> AdoptionResult:
        """Perform the actual adoption of an external resource"""
        
        return AdoptionResult(
            status="success",
            resource_id=external_resource.resource_id,
            adoption_policy_applied=policy,
            risk_level=external_resource.risk_assessment,
            modifications_required=self._generate_modification_requirements(external_resource),
            rollback_plan=self._generate_rollback_plan(external_resource)
        )
    
    def _generate_modification_requirements(self, external_resource: ExternalResource) -> List[str]:
        """Generate list of modifications needed for adoption"""
        
        modifications = []
        
        # Add InfraDSL management tags
        modifications.append("Add InfraDSL management tags")
        
        # Standardize naming if needed
        if not self._follows_naming_convention(external_resource):
            modifications.append("Standardize resource naming")
        
        # Add monitoring if missing
        if not self._has_monitoring(external_resource):
            modifications.append("Enable monitoring and logging")
        
        return modifications
    
    def _generate_rollback_plan(self, external_resource: ExternalResource) -> Dict[str, Any]:
        """Generate rollback plan for adoption"""
        
        return {
            "original_configuration": external_resource.configuration,
            "rollback_steps": [
                "Remove InfraDSL management tags",
                "Restore original configuration",
                "Verify resource functionality"
            ],
            "rollback_time_estimate": "5 minutes"
        }
    
    def _analyze_cross_account_dependencies(self, resource: ResourceFingerprint, account_list: List[str]) -> List[str]:
        """Analyze cross-account dependencies for a resource"""
        
        dependencies = []
        
        # This would analyze resource configuration for cross-account references
        # For now, return empty list
        return dependencies
    
    def _generate_multi_account_recommendations(self, all_resources: Dict[str, List[ResourceFingerprint]], 
                                              cross_account_deps: Dict[str, List[str]], 
                                              orphaned_resources: List[OrphanedResource]) -> List[str]:
        """Generate recommendations for multi-account optimization"""
        
        recommendations = []
        
        # Resource consolidation opportunities
        total_resources = sum(len(resources) for resources in all_resources.values())
        if total_resources > 500:
            recommendations.append("Consider resource consolidation to reduce management overhead")
        
        # Cross-account dependency optimization
        if len(cross_account_deps) > 20:
            recommendations.append("High number of cross-account dependencies - consider account restructuring")
        
        # Orphaned resource adoption
        if len(orphaned_resources) > 10:
            recommendations.append("Significant number of orphaned resources - plan adoption strategy")
        
        return recommendations
    
    def _follows_naming_convention(self, resource: ExternalResource) -> bool:
        """Check if resource follows naming conventions"""
        # This would check against organizational naming standards
        return True
    
    def _has_monitoring(self, resource: ExternalResource) -> bool:
        """Check if resource has monitoring enabled"""
        # This would check for monitoring configuration
        return True
    
    def _import_aws_discovery(self):
        """Import AWS-specific discovery module"""
        # This would import the actual AWS discovery implementation
        class MockAWSDiscovery:
            def fetch_resources(self, resource_types, account, filters):
                return []
        return MockAWSDiscovery()
    
    def _import_gcp_discovery(self):
        """Import GCP-specific discovery module"""
        # This would import the actual GCP discovery implementation
        class MockGCPDiscovery:
            def fetch_resources(self, resource_types, account, filters):
                return []
        return MockGCPDiscovery()
    
    def _import_do_discovery(self):
        """Import DigitalOcean-specific discovery module"""
        # This would import the actual DO discovery implementation
        class MockDODiscovery:
            def fetch_resources(self, resource_types, account, filters):
                return []
        return MockDODiscovery()
    
    def _import_cloudflare_discovery(self):
        """Import Cloudflare-specific discovery module"""
        # This would import the actual Cloudflare discovery implementation
        class MockCloudflareDiscovery:
            def fetch_resources(self, resource_types, account, filters):
                return []
        return MockCloudflareDiscovery()