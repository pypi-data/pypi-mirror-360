"""
External Resource Handler for InfraDSL
Comprehensive system for managing resources NOT created by InfraDSL
"""

import json
import hashlib
from typing import Dict, Any, List, Optional, Tuple, Set
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from enum import Enum
import logging
from pathlib import Path

from .stateless_intelligence import StatelessIntelligence, ResourceFingerprint, ResourceType
from .universal_resource_discovery import (
    UniversalResourceDiscovery, 
    ExternalResource, 
    AdoptionPolicy, 
    AdoptionResult
)


class ImportStrategy(Enum):
    """Strategies for importing external resources"""
    SAFE_MODE = "safe_mode"              # Read-only analysis, no modifications
    ADOPT_ONLY = "adopt_only"            # Add tags, no config changes
    STANDARDIZE = "standardize"          # Adopt + standardize configuration
    FULL_MIGRATION = "full_migration"    # Complete migration to InfraDSL patterns


class ConflictResolution(Enum):
    """How to handle resource conflicts"""
    MANUAL_REVIEW = "manual_review"      # Stop and require manual intervention
    SKIP_CONFLICTED = "skip_conflicted"  # Skip conflicted resources
    AUTO_RESOLVE = "auto_resolve"        # Attempt automatic resolution
    FORCE_ADOPT = "force_adopt"          # Force adoption with warnings


class OwnershipTransition(Enum):
    """Types of ownership transitions"""
    TERRAFORM_TO_INFRADSL = "terraform_to_infradsl"
    MANUAL_TO_INFRADSL = "manual_to_infradsl"
    CLOUDFORMATION_TO_INFRADSL = "cloudformation_to_infradsl"
    UNKNOWN_TO_INFRADSL = "unknown_to_infradsl"


@dataclass
class ExternalResourceAnalysis:
    """Comprehensive analysis of an external resource"""
    resource_id: str
    provider: str
    resource_type: str
    current_owner: str
    ownership_confidence: float
    dependencies: List[str]
    dependents: List[str]
    configuration_drift: Dict[str, Any]
    security_posture: Dict[str, Any]
    compliance_status: Dict[str, str]
    cost_optimization_opportunities: List[str]
    adoption_complexity: str  # low, medium, high, very_high
    estimated_adoption_time: int  # minutes
    rollback_feasibility: str  # easy, moderate, difficult, impossible
    business_impact: str  # low, medium, high, critical


@dataclass
class ImportSession:
    """Session for tracking external resource imports"""
    session_id: str
    provider: str
    import_strategy: ImportStrategy
    conflict_resolution: ConflictResolution
    started_at: datetime
    completed_at: Optional[datetime] = None
    resources_analyzed: int = 0
    resources_adopted: int = 0
    resources_skipped: int = 0
    resources_failed: int = 0
    conflicts_detected: int = 0
    total_cost_savings_estimated: float = 0.0
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    rollback_plan: Optional[Dict[str, Any]] = None


@dataclass
class OwnershipTransitionPlan:
    """Plan for transitioning resource ownership"""
    resource_id: str
    current_owner: str
    target_owner: str
    transition_type: OwnershipTransition
    prerequisites: List[str]
    steps: List[Dict[str, Any]]
    estimated_downtime: int  # seconds
    rollback_steps: List[Dict[str, Any]]
    validation_checks: List[str]
    risk_mitigation: List[str]


class ExternalResourceHandler:
    """
    Comprehensive handler for external resources
    
    Capabilities:
    - Deep analysis of external resources
    - Safe adoption with multiple strategies
    - Conflict detection and resolution
    - Ownership transition planning
    - Rollback and recovery procedures
    """
    
    def __init__(self):
        self.discovery = UniversalResourceDiscovery()
        self.stateless_intelligence = StatelessIntelligence()
        self.logger = logging.getLogger(__name__)
        
        # Configuration
        self.analysis_cache: Dict[str, Tuple[datetime, ExternalResourceAnalysis]] = {}
        self.cache_ttl = timedelta(hours=1)
        
        # Import tracking
        self.import_sessions: Dict[str, ImportSession] = {}
        self.adoption_history: List[Dict[str, Any]] = []
        
        # Provider-specific handlers
        self.provider_handlers = {
            "aws": self._get_aws_handler,
            "gcp": self._get_gcp_handler,
            "digitalocean": self._get_do_handler
        }
    
    def analyze_external_resource(self, resource_id: str, provider: str, 
                                deep_analysis: bool = True) -> ExternalResourceAnalysis:
        """
        Perform comprehensive analysis of an external resource
        
        Args:
            resource_id: Resource identifier
            provider: Cloud provider
            deep_analysis: Whether to perform deep security/compliance analysis
            
        Returns:
            ExternalResourceAnalysis with comprehensive insights
        """
        
        cache_key = f"{provider}_{resource_id}"
        
        # Check cache first
        if cache_key in self.analysis_cache:
            cached_time, cached_analysis = self.analysis_cache[cache_key]
            if datetime.now() - cached_time < self.cache_ttl:
                self.logger.info(f"Returning cached analysis for {resource_id}")
                return cached_analysis
        
        self.logger.info(f"Starting analysis of external resource {resource_id} on {provider}")
        
        try:
            # Get provider-specific handler
            handler = self.provider_handlers[provider]()
            
            # Fetch resource details
            resource_details = handler.fetch_resource_details(resource_id)
            if not resource_details:
                raise ValueError(f"Resource {resource_id} not found")
            
            # Analyze ownership
            ownership_analysis = self._analyze_ownership(resource_details)
            
            # Analyze dependencies
            dependencies = self._analyze_dependencies(resource_details, provider)
            dependents = self._analyze_dependents(resource_id, provider)
            
            # Configuration analysis
            config_drift = self._analyze_configuration_drift(resource_details)
            
            # Security analysis
            security_posture = {}
            compliance_status = {}
            if deep_analysis:
                security_posture = self._analyze_security_posture(resource_details, provider)
                compliance_status = self._analyze_compliance_status(resource_details, provider)
            
            # Cost optimization
            cost_opportunities = self._identify_cost_optimizations(resource_details, provider)
            
            # Adoption complexity assessment
            adoption_complexity = self._assess_adoption_complexity(
                resource_details, ownership_analysis, dependencies
            )
            
            # Time estimation
            estimated_time = self._estimate_adoption_time(adoption_complexity, resource_details)
            
            # Rollback feasibility
            rollback_feasibility = self._assess_rollback_feasibility(resource_details, provider)
            
            # Business impact assessment
            business_impact = self._assess_business_impact(resource_details, dependents)
            
            analysis = ExternalResourceAnalysis(
                resource_id=resource_id,
                provider=provider,
                resource_type=resource_details.get("type", "unknown"),
                current_owner=ownership_analysis["primary_owner"],
                ownership_confidence=ownership_analysis["confidence"],
                dependencies=dependencies,
                dependents=dependents,
                configuration_drift=config_drift,
                security_posture=security_posture,
                compliance_status=compliance_status,
                cost_optimization_opportunities=cost_opportunities,
                adoption_complexity=adoption_complexity,
                estimated_adoption_time=estimated_time,
                rollback_feasibility=rollback_feasibility,
                business_impact=business_impact
            )
            
            # Cache the analysis
            self.analysis_cache[cache_key] = (datetime.now(), analysis)
            
            self.logger.info(f"Analysis completed for {resource_id}: {adoption_complexity} complexity")
            return analysis
            
        except Exception as e:
            self.logger.error(f"Failed to analyze resource {resource_id}: {str(e)}")
            raise
    
    def create_ownership_transition_plan(self, resource_id: str, provider: str, 
                                       target_owner: str = "infradsl") -> OwnershipTransitionPlan:
        """
        Create a detailed plan for transitioning resource ownership
        
        Args:
            resource_id: Resource to transition
            provider: Cloud provider
            target_owner: Target ownership system
            
        Returns:
            OwnershipTransitionPlan with detailed steps
        """
        
        # Analyze the resource first
        analysis = self.analyze_external_resource(resource_id, provider)
        
        # Determine transition type
        current_owner = analysis.current_owner.lower()
        if "terraform" in current_owner:
            transition_type = OwnershipTransition.TERRAFORM_TO_INFRADSL
        elif "cloudformation" in current_owner:
            transition_type = OwnershipTransition.CLOUDFORMATION_TO_INFRADSL
        elif "manual" in current_owner:
            transition_type = OwnershipTransition.MANUAL_TO_INFRADSL
        else:
            transition_type = OwnershipTransition.UNKNOWN_TO_INFRADSL
        
        # Generate transition steps based on type
        steps = self._generate_transition_steps(transition_type, analysis)
        
        # Generate prerequisites
        prerequisites = self._generate_prerequisites(transition_type, analysis)
        
        # Generate rollback steps
        rollback_steps = self._generate_rollback_steps(transition_type, analysis)
        
        # Validation checks
        validation_checks = self._generate_validation_checks(analysis)
        
        # Risk mitigation strategies
        risk_mitigation = self._generate_risk_mitigation(analysis)
        
        # Estimate downtime
        estimated_downtime = self._estimate_transition_downtime(transition_type, analysis)
        
        return OwnershipTransitionPlan(
            resource_id=resource_id,
            current_owner=analysis.current_owner,
            target_owner=target_owner,
            transition_type=transition_type,
            prerequisites=prerequisites,
            steps=steps,
            estimated_downtime=estimated_downtime,
            rollback_steps=rollback_steps,
            validation_checks=validation_checks,
            risk_mitigation=risk_mitigation
        )
    
    def import_external_resources(self, provider: str, resource_filters: Dict[str, Any],
                                import_strategy: ImportStrategy = ImportStrategy.SAFE_MODE,
                                conflict_resolution: ConflictResolution = ConflictResolution.MANUAL_REVIEW,
                                batch_size: int = 10) -> ImportSession:
        """
        Import multiple external resources with specified strategy
        
        Args:
            provider: Cloud provider
            resource_filters: Filters for selecting resources
            import_strategy: Strategy for import process
            conflict_resolution: How to handle conflicts
            batch_size: Number of resources to process in parallel
            
        Returns:
            ImportSession with detailed results
        """
        
        session_id = f"import_{provider}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        session = ImportSession(
            session_id=session_id,
            provider=provider,
            import_strategy=import_strategy,
            conflict_resolution=conflict_resolution,
            started_at=datetime.now()
        )
        
        self.import_sessions[session_id] = session
        
        try:
            self.logger.info(f"Starting import session {session_id} with strategy {import_strategy.value}")
            
            # Discover external resources based on filters
            resource_types = resource_filters.get("resource_types", self._get_all_resource_types(provider))
            discovered_resources = self.discovery.discover_resources(
                provider=provider,
                resource_types=resource_types,
                filters=resource_filters
            )
            
            session.resources_analyzed = len(discovered_resources)
            
            # Process resources in batches
            for i in range(0, len(discovered_resources), batch_size):
                batch = discovered_resources[i:i + batch_size]
                batch_results = self._process_resource_batch(batch, session)
                
                # Update session statistics
                for result in batch_results:
                    if result["status"] == "adopted":
                        session.resources_adopted += 1
                        session.total_cost_savings_estimated += result.get("cost_savings", 0.0)
                    elif result["status"] == "skipped":
                        session.resources_skipped += 1
                    elif result["status"] == "failed":
                        session.resources_failed += 1
                        session.errors.append(result.get("error", "Unknown error"))
                    
                    if result.get("conflicts"):
                        session.conflicts_detected += len(result["conflicts"])
            
            # Generate rollback plan
            session.rollback_plan = self._generate_session_rollback_plan(session)
            
            session.completed_at = datetime.now()
            
            self.logger.info(f"Import session {session_id} completed: "
                           f"{session.resources_adopted} adopted, "
                           f"{session.resources_skipped} skipped, "
                           f"{session.resources_failed} failed")
            
            return session
            
        except Exception as e:
            session.errors.append(str(e))
            self.logger.error(f"Import session {session_id} failed: {str(e)}")
            raise
    
    def validate_adoption_safety(self, resource_id: str, provider: str) -> Dict[str, Any]:
        """
        Validate that adopting a resource is safe and won't cause issues
        
        Args:
            resource_id: Resource to validate
            provider: Cloud provider
            
        Returns:
            Dictionary with safety validation results
        """
        
        analysis = self.analyze_external_resource(resource_id, provider, deep_analysis=True)
        
        safety_checks = {
            "overall_safety": "unknown",
            "checks_passed": 0,
            "checks_failed": 0,
            "warnings": [],
            "blockers": [],
            "recommendations": []
        }
        
        # Check 1: Ownership clarity
        if analysis.ownership_confidence >= 0.8:
            safety_checks["checks_passed"] += 1
        else:
            safety_checks["checks_failed"] += 1
            safety_checks["blockers"].append(f"Unclear ownership (confidence: {analysis.ownership_confidence:.2f})")
        
        # Check 2: No critical dependencies
        critical_deps = [dep for dep in analysis.dependencies if "critical" in dep.lower()]
        if not critical_deps:
            safety_checks["checks_passed"] += 1
        else:
            safety_checks["checks_failed"] += 1
            safety_checks["blockers"].append(f"Critical dependencies detected: {critical_deps}")
        
        # Check 3: Rollback feasibility
        if analysis.rollback_feasibility in ["easy", "moderate"]:
            safety_checks["checks_passed"] += 1
        else:
            safety_checks["warnings"].append(f"Rollback is {analysis.rollback_feasibility}")
        
        # Check 4: Business impact
        if analysis.business_impact in ["low", "medium"]:
            safety_checks["checks_passed"] += 1
        else:
            safety_checks["warnings"].append(f"High business impact: {analysis.business_impact}")
        
        # Check 5: Security posture
        security_issues = analysis.security_posture.get("issues", [])
        if len(security_issues) <= 2:
            safety_checks["checks_passed"] += 1
        else:
            safety_checks["warnings"].append(f"Multiple security issues: {security_issues}")
        
        # Check 6: Compliance status
        compliance_failures = [k for k, v in analysis.compliance_status.items() if v == "failed"]
        if not compliance_failures:
            safety_checks["checks_passed"] += 1
        else:
            safety_checks["blockers"].append(f"Compliance failures: {compliance_failures}")
        
        # Generate recommendations
        if analysis.cost_optimization_opportunities:
            safety_checks["recommendations"].extend([
                f"Cost optimization: {opp}" for opp in analysis.cost_optimization_opportunities[:3]
            ])
        
        if analysis.adoption_complexity == "low":
            safety_checks["recommendations"].append("Low complexity - good candidate for automatic adoption")
        
        # Determine overall safety
        if safety_checks["checks_failed"] == 0:
            if len(safety_checks["warnings"]) <= 1:
                safety_checks["overall_safety"] = "safe"
            else:
                safety_checks["overall_safety"] = "caution"
        else:
            safety_checks["overall_safety"] = "unsafe"
        
        return safety_checks
    
    def _analyze_ownership(self, resource_details: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze resource ownership patterns"""
        
        ownership_indicators = {
            "terraform": 0,
            "cloudformation": 0,
            "manual": 0,
            "infradsl": 0,
            "unknown": 0
        }
        
        # Check tags
        tags = resource_details.get("tags", {})
        for key, value in tags.items():
            key_lower = key.lower()
            value_lower = str(value).lower()
            
            if "terraform" in key_lower or "terraform" in value_lower:
                ownership_indicators["terraform"] += 2
            elif "cloudformation" in key_lower or "cloudformation" in value_lower:
                ownership_indicators["cloudformation"] += 2
            elif "infradsl" in key_lower or "infradsl" in value_lower:
                ownership_indicators["infradsl"] += 2
            elif "manual" in value_lower or "created" in key_lower:
                ownership_indicators["manual"] += 1
        
        # Check resource name patterns
        name = resource_details.get("name", "")
        if "terraform" in name.lower():
            ownership_indicators["terraform"] += 1
        elif "infradsl" in name.lower():
            ownership_indicators["infradsl"] += 1
        
        # Determine primary owner
        max_score = max(ownership_indicators.values())
        if max_score == 0:
            primary_owner = "unknown"
            confidence = 0.0
        else:
            primary_owner = max(ownership_indicators.keys(), key=ownership_indicators.get)
            confidence = min(max_score / 5.0, 1.0)  # Normalize to 0-1
        
        return {
            "primary_owner": primary_owner,
            "confidence": confidence,
            "indicators": ownership_indicators
        }
    
    def _analyze_dependencies(self, resource_details: Dict[str, Any], provider: str) -> List[str]:
        """Analyze resource dependencies"""
        
        dependencies = []
        
        # VPC dependencies
        if "vpc_id" in resource_details:
            dependencies.append(f"vpc:{resource_details['vpc_id']}")
        
        # Subnet dependencies
        if "subnet_id" in resource_details:
            dependencies.append(f"subnet:{resource_details['subnet_id']}")
        
        # Security group dependencies
        security_groups = resource_details.get("security_groups", [])
        for sg in security_groups:
            dependencies.append(f"security_group:{sg}")
        
        # IAM role dependencies
        if "iam_role" in resource_details:
            dependencies.append(f"iam_role:{resource_details['iam_role']}")
        
        # Storage dependencies
        if "storage" in resource_details:
            storage_info = resource_details["storage"]
            if isinstance(storage_info, dict):
                if "bucket" in storage_info:
                    dependencies.append(f"s3_bucket:{storage_info['bucket']}")
        
        return dependencies
    
    def _analyze_dependents(self, resource_id: str, provider: str) -> List[str]:
        """Analyze what depends on this resource"""
        
        # This would typically query the provider's APIs to find dependents
        # For now, return mock data
        return []
    
    def _analyze_configuration_drift(self, resource_details: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze configuration drift from standards"""
        
        drift = {}
        
        # Check for missing required tags
        required_tags = ["Environment", "Owner", "Project"]
        tags = resource_details.get("tags", {})
        missing_tags = [tag for tag in required_tags if tag not in tags]
        if missing_tags:
            drift["missing_tags"] = missing_tags
        
        # Check for non-standard naming
        name = resource_details.get("name", "")
        if not self._follows_naming_convention(name):
            drift["naming_convention"] = "Non-standard naming pattern"
        
        # Check for missing monitoring
        if not resource_details.get("monitoring_enabled", False):
            drift["monitoring"] = "Monitoring not enabled"
        
        # Check for missing backups
        if resource_details.get("type") in ["rds_instance", "ec2_instance"]:
            if not resource_details.get("backup_enabled", False):
                drift["backup"] = "Backup not enabled"
        
        return drift
    
    def _analyze_security_posture(self, resource_details: Dict[str, Any], provider: str) -> Dict[str, Any]:
        """Analyze security posture of the resource"""
        
        security = {
            "score": 8.0,  # Default score out of 10
            "issues": [],
            "recommendations": []
        }
        
        # Check encryption
        if not resource_details.get("encryption_enabled", True):
            security["issues"].append("Encryption not enabled")
            security["score"] -= 2.0
            security["recommendations"].append("Enable encryption at rest")
        
        # Check public access
        if resource_details.get("public_access", False):
            security["issues"].append("Public access enabled")
            security["score"] -= 1.5
            security["recommendations"].append("Review public access necessity")
        
        # Check security groups (if applicable)
        security_groups = resource_details.get("security_groups", [])
        for sg in security_groups:
            if "0.0.0.0/0" in str(sg):
                security["issues"].append("Overly permissive security group")
                security["score"] -= 1.0
                security["recommendations"].append("Restrict security group rules")
                break
        
        return security
    
    def _analyze_compliance_status(self, resource_details: Dict[str, Any], provider: str) -> Dict[str, str]:
        """Analyze compliance status against common frameworks"""
        
        compliance = {}
        
        # GDPR compliance (for EU resources)
        if resource_details.get("region", "").startswith("eu-"):
            if resource_details.get("encryption_enabled", False):
                compliance["GDPR"] = "passed"
            else:
                compliance["GDPR"] = "failed"
        
        # SOC2 compliance
        monitoring = resource_details.get("monitoring_enabled", False)
        logging = resource_details.get("logging_enabled", False)
        if monitoring and logging:
            compliance["SOC2"] = "passed"
        else:
            compliance["SOC2"] = "failed"
        
        # HIPAA compliance (if healthcare tags present)
        tags = resource_details.get("tags", {})
        if any("health" in str(v).lower() or "hipaa" in str(v).lower() for v in tags.values()):
            encryption = resource_details.get("encryption_enabled", False)
            access_logging = resource_details.get("access_logging", False)
            if encryption and access_logging:
                compliance["HIPAA"] = "passed"
            else:
                compliance["HIPAA"] = "failed"
        
        return compliance
    
    def _identify_cost_optimizations(self, resource_details: Dict[str, Any], provider: str) -> List[str]:
        """Identify cost optimization opportunities"""
        
        opportunities = []
        
        # Right-sizing opportunities
        if resource_details.get("type") == "ec2_instance":
            cpu_utilization = resource_details.get("cpu_utilization", 50)
            if cpu_utilization < 20:
                opportunities.append("Consider downsizing instance - low CPU utilization")
        
        # Storage optimization
        if resource_details.get("type") == "s3_bucket":
            lifecycle_policy = resource_details.get("lifecycle_policy")
            if not lifecycle_policy:
                opportunities.append("Add lifecycle policy to transition to cheaper storage classes")
        
        # Reserved instance opportunities
        if resource_details.get("type") in ["ec2_instance", "rds_instance"]:
            instance_age_days = resource_details.get("age_days", 0)
            if instance_age_days > 30:
                opportunities.append("Consider reserved instances for long-running resources")
        
        return opportunities
    
    def _assess_adoption_complexity(self, resource_details: Dict[str, Any], 
                                  ownership_analysis: Dict[str, Any], 
                                  dependencies: List[str]) -> str:
        """Assess complexity of adopting the resource"""
        
        complexity_score = 0
        
        # Ownership clarity
        if ownership_analysis["confidence"] < 0.5:
            complexity_score += 2
        elif ownership_analysis["confidence"] < 0.8:
            complexity_score += 1
        
        # Number of dependencies
        if len(dependencies) > 5:
            complexity_score += 2
        elif len(dependencies) > 2:
            complexity_score += 1
        
        # Resource type complexity
        complex_types = ["cloudfront_distribution", "rds_cluster", "eks_cluster"]
        if resource_details.get("type") in complex_types:
            complexity_score += 1
        
        # Configuration drift
        config_drift = self._analyze_configuration_drift(resource_details)
        if len(config_drift) > 3:
            complexity_score += 2
        elif len(config_drift) > 1:
            complexity_score += 1
        
        # Map score to complexity level
        if complexity_score >= 6:
            return "very_high"
        elif complexity_score >= 4:
            return "high"
        elif complexity_score >= 2:
            return "medium"
        else:
            return "low"
    
    def _estimate_adoption_time(self, complexity: str, resource_details: Dict[str, Any]) -> int:
        """Estimate time to adopt resource in minutes"""
        
        base_times = {
            "low": 10,
            "medium": 30,
            "high": 60,
            "very_high": 120
        }
        
        base_time = base_times.get(complexity, 30)
        
        # Adjust for resource type
        complex_types = ["cloudfront_distribution", "rds_cluster", "eks_cluster"]
        if resource_details.get("type") in complex_types:
            base_time *= 1.5
        
        return int(base_time)
    
    def _assess_rollback_feasibility(self, resource_details: Dict[str, Any], provider: str) -> str:
        """Assess how easy it would be to rollback adoption"""
        
        # Stateful resources are harder to rollback
        stateful_types = ["rds_instance", "s3_bucket_with_data", "persistent_disk"]
        if resource_details.get("type") in stateful_types:
            return "difficult"
        
        # Resources with many dependencies are harder to rollback
        dependencies_count = len(self._analyze_dependencies(resource_details, provider))
        if dependencies_count > 5:
            return "moderate"
        elif dependencies_count > 2:
            return "easy"
        
        return "easy"
    
    def _assess_business_impact(self, resource_details: Dict[str, Any], dependents: List[str]) -> str:
        """Assess business impact of adopting the resource"""
        
        # Check for production tags
        tags = resource_details.get("tags", {})
        for tag_value in tags.values():
            if "prod" in str(tag_value).lower() or "production" in str(tag_value).lower():
                return "high"
        
        # Check number of dependents
        if len(dependents) > 10:
            return "critical"
        elif len(dependents) > 5:
            return "high"
        elif len(dependents) > 0:
            return "medium"
        
        return "low"
    
    def _generate_transition_steps(self, transition_type: OwnershipTransition, 
                                 analysis: ExternalResourceAnalysis) -> List[Dict[str, Any]]:
        """Generate detailed transition steps"""
        
        steps = []
        
        if transition_type == OwnershipTransition.TERRAFORM_TO_INFRADSL:
            steps.extend([
                {
                    "step": 1,
                    "action": "backup_terraform_state",
                    "description": "Create backup of current Terraform state",
                    "estimated_time": 2,
                    "risk": "low"
                },
                {
                    "step": 2,
                    "action": "import_to_infradsl",
                    "description": "Import resource into InfraDSL workspace",
                    "estimated_time": 5,
                    "risk": "medium"
                },
                {
                    "step": 3,
                    "action": "remove_from_terraform",
                    "description": "Remove resource from Terraform configuration",
                    "estimated_time": 3,
                    "risk": "medium"
                },
                {
                    "step": 4,
                    "action": "validate_infradsl_control",
                    "description": "Validate InfraDSL can manage the resource",
                    "estimated_time": 5,
                    "risk": "low"
                }
            ])
        
        elif transition_type == OwnershipTransition.MANUAL_TO_INFRADSL:
            steps.extend([
                {
                    "step": 1,
                    "action": "document_current_config",
                    "description": "Document current manual configuration",
                    "estimated_time": 10,
                    "risk": "low"
                },
                {
                    "step": 2,
                    "action": "add_management_tags",
                    "description": "Add InfraDSL management tags",
                    "estimated_time": 2,
                    "risk": "low"
                },
                {
                    "step": 3,
                    "action": "create_infradsl_config",
                    "description": "Create InfraDSL configuration matching current state",
                    "estimated_time": 15,
                    "risk": "medium"
                },
                {
                    "step": 4,
                    "action": "validate_control",
                    "description": "Validate InfraDSL can manage the resource",
                    "estimated_time": 5,
                    "risk": "low"
                }
            ])
        
        return steps
    
    def _generate_prerequisites(self, transition_type: OwnershipTransition, 
                              analysis: ExternalResourceAnalysis) -> List[str]:
        """Generate prerequisites for transition"""
        
        prerequisites = [
            "Backup current resource configuration",
            "Verify resource is not in critical production use during transition window",
            "Ensure InfraDSL has necessary permissions to manage the resource"
        ]
        
        if transition_type == OwnershipTransition.TERRAFORM_TO_INFRADSL:
            prerequisites.extend([
                "Backup Terraform state file",
                "Coordinate with team managing Terraform configuration",
                "Plan Terraform state removal procedure"
            ])
        
        if analysis.business_impact in ["high", "critical"]:
            prerequisites.extend([
                "Schedule maintenance window",
                "Notify stakeholders of ownership transition",
                "Prepare rapid rollback procedure"
            ])
        
        return prerequisites
    
    def _generate_rollback_steps(self, transition_type: OwnershipTransition, 
                               analysis: ExternalResourceAnalysis) -> List[Dict[str, Any]]:
        """Generate rollback steps"""
        
        rollback_steps = [
            {
                "step": 1,
                "action": "remove_infradsl_tags",
                "description": "Remove InfraDSL management tags",
                "estimated_time": 2
            },
            {
                "step": 2,
                "action": "restore_original_config",
                "description": "Restore original resource configuration",
                "estimated_time": 5
            }
        ]
        
        if transition_type == OwnershipTransition.TERRAFORM_TO_INFRADSL:
            rollback_steps.extend([
                {
                    "step": 3,
                    "action": "restore_terraform_state",
                    "description": "Restore resource to Terraform state",
                    "estimated_time": 10
                },
                {
                    "step": 4,
                    "action": "validate_terraform_control",
                    "description": "Validate Terraform can manage the resource again",
                    "estimated_time": 5
                }
            ])
        
        return rollback_steps
    
    def _generate_validation_checks(self, analysis: ExternalResourceAnalysis) -> List[str]:
        """Generate validation checks for transition"""
        
        checks = [
            "Resource responds to InfraDSL preview commands",
            "Resource configuration matches expected state",
            "All dependencies are accessible",
            "No configuration drift detected"
        ]
        
        if analysis.business_impact in ["high", "critical"]:
            checks.extend([
                "Application functionality verified",
                "Performance metrics within normal ranges",
                "All dependent services functioning normally"
            ])
        
        return checks
    
    def _generate_risk_mitigation(self, analysis: ExternalResourceAnalysis) -> List[str]:
        """Generate risk mitigation strategies"""
        
        mitigation = [
            "Perform transition during low-traffic period",
            "Have rollback procedure ready and tested",
            "Monitor resource closely during transition"
        ]
        
        if analysis.adoption_complexity in ["high", "very_high"]:
            mitigation.extend([
                "Consider staged transition approach",
                "Perform dry-run in non-production environment first",
                "Have expert support available during transition"
            ])
        
        return mitigation
    
    def _estimate_transition_downtime(self, transition_type: OwnershipTransition, 
                                    analysis: ExternalResourceAnalysis) -> int:
        """Estimate downtime in seconds"""
        
        # Most transitions should have zero downtime
        if analysis.business_impact == "critical":
            return 0  # Must be zero-downtime
        
        if transition_type == OwnershipTransition.TERRAFORM_TO_INFRADSL:
            return 30  # Brief downtime during state transition
        
        return 0  # Zero downtime for other transitions
    
    def _process_resource_batch(self, resources: List[ResourceFingerprint], 
                              session: ImportSession) -> List[Dict[str, Any]]:
        """Process a batch of resources for import"""
        
        results = []
        
        for resource in resources:
            try:
                # Analyze the resource
                analysis = self.analyze_external_resource(resource.resource_id, session.provider)
                
                # Check if adoption is safe
                safety_check = self.validate_adoption_safety(resource.resource_id, session.provider)
                
                result = {
                    "resource_id": resource.resource_id,
                    "status": "unknown",
                    "analysis": analysis,
                    "safety_check": safety_check
                }
                
                # Determine action based on strategy and safety
                if session.import_strategy == ImportStrategy.SAFE_MODE:
                    result["status"] = "analyzed_only"
                    result["action_taken"] = "Analysis performed, no modifications made"
                
                elif safety_check["overall_safety"] == "unsafe":
                    if session.conflict_resolution == ConflictResolution.SKIP_CONFLICTED:
                        result["status"] = "skipped"
                        result["reason"] = "Safety check failed"
                    else:
                        result["status"] = "manual_review_required"
                
                elif safety_check["overall_safety"] in ["safe", "caution"]:
                    # Attempt adoption
                    adoption_result = self.discovery.adopt_external_resource(
                        resource.resource_id, 
                        session.provider, 
                        AdoptionPolicy.MODERATE
                    )
                    
                    if adoption_result.status == "success":
                        result["status"] = "adopted"
                        result["cost_savings"] = self._estimate_cost_savings(analysis)
                    else:
                        result["status"] = "failed"
                        result["error"] = adoption_result.error_message
                
                results.append(result)
                
            except Exception as e:
                results.append({
                    "resource_id": resource.resource_id,
                    "status": "failed",
                    "error": str(e)
                })
        
        return results
    
    def _generate_session_rollback_plan(self, session: ImportSession) -> Dict[str, Any]:
        """Generate rollback plan for entire import session"""
        
        return {
            "session_id": session.session_id,
            "rollback_steps": [
                "Identify all resources modified during session",
                "Remove InfraDSL management tags from adopted resources",
                "Restore original ownership markers",
                "Validate original management tools can control resources again"
            ],
            "estimated_rollback_time": session.resources_adopted * 5,  # 5 minutes per resource
            "rollback_complexity": "medium" if session.resources_adopted > 10 else "low"
        }
    
    def _estimate_cost_savings(self, analysis: ExternalResourceAnalysis) -> float:
        """Estimate cost savings from adoption"""
        
        # Rough estimation based on optimization opportunities
        opportunities = len(analysis.cost_optimization_opportunities)
        if opportunities >= 3:
            return 100.0  # $100/month estimated savings
        elif opportunities >= 2:
            return 50.0
        elif opportunities >= 1:
            return 25.0
        return 0.0
    
    def _follows_naming_convention(self, name: str) -> bool:
        """Check if name follows organizational conventions"""
        # Simple check - would be more sophisticated in practice
        return len(name) > 3 and not name.startswith("temp-")
    
    def _get_all_resource_types(self, provider: str) -> List[str]:
        """Get all resource types for a provider"""
        types = {
            "aws": ["ec2_instance", "rds_instance", "s3_bucket", "lambda_function"],
            "gcp": ["vm", "cloud_sql", "cloud_storage", "cloud_functions"],
            "digitalocean": ["droplet", "database", "spaces"]
        }
        return types.get(provider, [])
    
    def _get_aws_handler(self):
        """Get AWS-specific handler"""
        class MockAWSHandler:
            def fetch_resource_details(self, resource_id):
                return {"id": resource_id, "type": "ec2_instance", "tags": {}}
        return MockAWSHandler()
    
    def _get_gcp_handler(self):
        """Get GCP-specific handler"""
        class MockGCPHandler:
            def fetch_resource_details(self, resource_id):
                return {"id": resource_id, "type": "vm", "labels": {}}
        return MockGCPHandler()
    
    def _get_do_handler(self):
        """Get DigitalOcean-specific handler"""
        class MockDOHandler:
            def fetch_resource_details(self, resource_id):
                return {"id": resource_id, "type": "droplet", "tags": []}
        return MockDOHandler()