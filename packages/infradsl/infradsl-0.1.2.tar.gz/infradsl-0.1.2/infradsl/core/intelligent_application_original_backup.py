"""
IntelligentApplication API - The Revolutionary Developer Experience

This is the magical interface that makes Cross-Cloud Magic possible.
Developers can create applications that automatically select optimal 
providers for each service based on intelligent analysis.

Example:
    app = InfraDSL.Application("my-app")
        .auto_optimize()
        .database("postgresql")      # → Chooses GCP (best price/performance)
        .compute("web-servers")      # → Chooses AWS (best global coverage)
        .cdn("static-assets")        # → Chooses Cloudflare (best edge network)
        .storage("user-uploads")     # → Chooses DigitalOcean (best simplicity)
        .create()

Result: Cost optimization, optimal performance, maximum reliability

File Structure:
    1. Data Classes & Core Setup
    2. Provider Constraint Methods
    3. Service Definition Methods  
    4. Intelligence & Lifecycle Methods
    5. Resource Creation Methods
    6. Preview & Utility Methods
"""

from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass
import logging

from .cross_cloud_intelligence import (
    CrossCloudIntelligence, 
    ServiceRequirements, 
    ServiceCategory,
    OptimizationPriority,
    cross_cloud_intelligence
)
from .provider_constraints import (
    ProviderConstraints,
    ProviderPreference,
    constraint_engine,
    aws_only_constraints,
    aws_gcp_constraints
)
from ..providers.aws import AWS
from ..providers.googlecloud import GoogleCloud
from ..providers.digitalocean import DigitalOcean
from ..providers.cloudflare import Cloudflare

logger = logging.getLogger(__name__)


# ==============================================================================
# 1. DATA CLASSES & CORE SETUP
# ==============================================================================

@dataclass
class OptimizationPreferences:
    """User-defined optimization preferences"""
    cost_weight: float = 0.4           # How much to prioritize cost (0.0-1.0)
    performance_weight: float = 0.3    # How much to prioritize performance
    reliability_weight: float = 0.2    # How much to prioritize reliability  
    compliance_weight: float = 0.1     # How much to prioritize compliance
    
    def normalize(self):
        """Normalize weights to sum to 1.0"""
        total = self.cost_weight + self.performance_weight + self.reliability_weight + self.compliance_weight
        if total > 0:
            self.cost_weight /= total
            self.performance_weight /= total
            self.reliability_weight /= total
            self.compliance_weight /= total


@dataclass
class ServiceConfiguration:
    """Configuration for a specific service"""
    service_name: str
    service_type: str
    service_category: ServiceCategory
    configuration: Dict[str, Any]
    requirements: ServiceRequirements


class IntelligentApplication:
    """
    Revolutionary IntelligentApplication class
    
    Provides the magical developer experience where infrastructure
    automatically selects optimal providers per service.
    
    This is the feature that makes traditional IaC tools obsolete.
    """
    
    def __init__(self, name: str):
        self.name = name
        self.services: Dict[str, ServiceConfiguration] = {}
        self.optimization_preferences = OptimizationPreferences()
        self.cross_cloud_intelligence = cross_cloud_intelligence
        self.auto_optimization_enabled = False
        self.created_resources = {}
        self.provider_constraints = ProviderConstraints()  # User-defined constraints
        
        logger.info(f"🚀 Initializing IntelligentApplication: {name}")
    
    def auto_optimize(self, priorities: Optional[Dict[str, float]] = None) -> 'IntelligentApplication':
        """
        Enable Cross-Cloud Magic auto-optimization
        
        This is the revolutionary feature that automatically selects
        optimal providers for each service.
        
        Args:
            priorities: Optional optimization priorities
                       {'cost': 0.4, 'performance': 0.3, 'reliability': 0.2, 'compliance': 0.1}
        
        Returns:
            Self for method chaining
        """
        
        self.auto_optimization_enabled = True
        
        if priorities:
            self.optimization_preferences.cost_weight = priorities.get('cost', 0.4)
            self.optimization_preferences.performance_weight = priorities.get('performance', 0.3)
            self.optimization_preferences.reliability_weight = priorities.get('reliability', 0.2)
            self.optimization_preferences.compliance_weight = priorities.get('compliance', 0.1)
            
            # Normalize weights
            self.optimization_preferences.normalize()
        
        logger.info(f"🧠 Auto-optimization enabled for {self.name}")
        logger.info(f"   Priorities: Cost={self.optimization_preferences.cost_weight:.1%}, "
                   f"Performance={self.optimization_preferences.performance_weight:.1%}, "
                   f"Reliability={self.optimization_preferences.reliability_weight:.1%}, "
                   f"Compliance={self.optimization_preferences.compliance_weight:.1%}")
        
        return self


# ==============================================================================
# 2. PROVIDER CONSTRAINT METHODS  
# ==============================================================================
    
    def constrain_to_providers(self, *providers: str) -> 'IntelligentApplication':
        """
        Constrain Cross-Cloud Magic to only use specific providers
        
        Args:
            *providers: Provider names (aws, gcp, digitalocean, cloudflare)
            
        Returns:
            Self for method chaining
            
        Examples:
            # Company A: AWS only
            app.constrain_to_providers("aws")
            
            # Company B: AWS and GCP only  
            app.constrain_to_providers("aws", "gcp")
            
            # Company C: Multi-cloud but no DigitalOcean
            app.constrain_to_providers("aws", "gcp", "cloudflare")
        """
        
        self.provider_constraints.allowed_providers = set(providers)
        
        logger.info(f"🔒 Provider constraints applied: Only using {', '.join(p.upper() for p in providers)}")
        
        return self
    
    def forbid_providers(self, *providers: str) -> 'IntelligentApplication':
        """
        Forbid Cross-Cloud Magic from using specific providers
        
        Args:
            *providers: Provider names to forbid
            
        Returns:
            Self for method chaining
            
        Examples:
            # Never use DigitalOcean
            app.forbid_providers("digitalocean")
            
            # Avoid AWS and DigitalOcean
            app.forbid_providers("aws", "digitalocean")
        """
        
        self.provider_constraints.forbidden_providers.update(providers)
        
        logger.info(f"❌ Provider restrictions applied: Forbidden {', '.join(p.upper() for p in providers)}")
        
        return self
    
    def prefer_providers(self, **preferences) -> 'IntelligentApplication':
        """
        Set provider preferences for Cross-Cloud Magic
        
        Args:
            **preferences: Provider preferences (required, preferred, allowed, avoid, forbidden)
            
        Returns:
            Self for method chaining
            
        Examples:
            # Prefer AWS, allow GCP, avoid others
            app.prefer_providers(
                aws="preferred",
                gcp="allowed", 
                digitalocean="avoid",
                cloudflare="forbidden"
            )
        """
        
        preference_mapping = {
            "required": ProviderPreference.REQUIRED,
            "preferred": ProviderPreference.PREFERRED,
            "allowed": ProviderPreference.ALLOWED,
            "avoid": ProviderPreference.AVOID,
            "forbidden": ProviderPreference.FORBIDDEN
        }
        
        for provider, preference_str in preferences.items():
            if preference_str in preference_mapping:
                self.provider_constraints.provider_preferences[provider] = preference_mapping[preference_str]
                logger.info(f"✅ Provider preference: {provider.upper()} = {preference_str}")
        
        return self
    
    def force_service_provider(self, service_type: str, provider: str) -> 'IntelligentApplication':
        """
        Force a specific service to use a specific provider
        
        Args:
            service_type: Service type (postgresql, web-servers, etc.)
            provider: Provider to force
            
        Returns:
            Self for method chaining
            
        Examples:
            # Force database to AWS, regardless of optimization
            app.force_service_provider("postgresql", "aws")
            
            # Force CDN to Cloudflare
            app.force_service_provider("static-assets", "cloudflare")
        """
        
        self.provider_constraints.service_overrides[service_type] = provider
        
        logger.info(f"🔒 Service override: {service_type} → {provider.upper()} (forced)")
        
        return self
    
    def require_compliance(self, *requirements: str) -> 'IntelligentApplication':
        """
        Require specific compliance standards
        
        Args:
            *requirements: Compliance requirements (HIPAA, PCI-DSS, SOC2, etc.)
            
        Returns:
            Self for method chaining
            
        Examples:
            # Require HIPAA compliance
            app.require_compliance("HIPAA")
            
            # Require multiple compliance standards
            app.require_compliance("HIPAA", "PCI-DSS", "SOC2")
        """
        
        self.provider_constraints.compliance_requirements.extend(requirements)
        
        logger.info(f"📋 Compliance requirements: {', '.join(requirements)}")
        
        return self


# ==============================================================================
# 3. SERVICE DEFINITION METHODS
# ==============================================================================
    
    def database(self, 
                db_type: str, 
                **kwargs) -> 'IntelligentApplication':
        """
        Add intelligent database service
        
        Args:
            db_type: Database type (postgresql, mysql, mongodb, etc.)
            **kwargs: Additional configuration options
                     performance: basic, standard, high, ultra
                     reliability: basic, high, mission_critical
                     compliance: List of compliance requirements
                     regions: List of geographic regions
        
        Returns:
            Self for method chaining
        """
        
        service_name = f"{self.name}-database"
        
        # Create service requirements
        requirements = ServiceRequirements(
            service_category=ServiceCategory.DATABASE,
            service_type=db_type,
            performance_tier=kwargs.get('performance', 'standard'),
            reliability_requirement=kwargs.get('reliability', 'high'),
            compliance_requirements=kwargs.get('compliance', []),
            geographic_regions=kwargs.get('regions', ['us-east-1']),
            cost_sensitivity=self.optimization_preferences.cost_weight,
            performance_sensitivity=self.optimization_preferences.performance_weight,
            reliability_sensitivity=self.optimization_preferences.reliability_weight,
            compliance_sensitivity=self.optimization_preferences.compliance_weight
        )
        
        # Store service configuration
        self.services[service_name] = ServiceConfiguration(
            service_name=service_name,
            service_type=db_type,
            service_category=ServiceCategory.DATABASE,
            configuration=kwargs,
            requirements=requirements
        )
        
        logger.info(f"📊 Added database service: {db_type}")
        
        return self
    
    def compute(self, 
               compute_type: str,
               **kwargs) -> 'IntelligentApplication':
        """
        Add intelligent compute service
        
        Args:
            compute_type: Compute type (web-servers, api-servers, workers, etc.)
            **kwargs: Additional configuration options
                     scaling: minimal, moderate, aggressive
                     performance: basic, standard, high, ultra
                     global_distribution: bool
        
        Returns:
            Self for method chaining
        """
        
        service_name = f"{self.name}-compute"
        
        # Determine performance tier based on scaling requirements
        scaling = kwargs.get('scaling', 'moderate')
        if scaling == 'aggressive':
            performance_tier = 'high'
        elif scaling == 'minimal':
            performance_tier = 'basic'
        else:
            performance_tier = kwargs.get('performance', 'standard')
        
        # Create service requirements
        requirements = ServiceRequirements(
            service_category=ServiceCategory.COMPUTE,
            service_type=compute_type,
            performance_tier=performance_tier,
            reliability_requirement=kwargs.get('reliability', 'high'),
            compliance_requirements=kwargs.get('compliance', []),
            geographic_regions=kwargs.get('regions', ['us-east-1', 'eu-west-1'] if kwargs.get('global_distribution') else ['us-east-1']),
            cost_sensitivity=self.optimization_preferences.cost_weight,
            performance_sensitivity=self.optimization_preferences.performance_weight,
            reliability_sensitivity=self.optimization_preferences.reliability_weight,
            compliance_sensitivity=self.optimization_preferences.compliance_weight
        )
        
        # Store service configuration
        self.services[service_name] = ServiceConfiguration(
            service_name=service_name,
            service_type=compute_type,
            service_category=ServiceCategory.COMPUTE,
            configuration=kwargs,
            requirements=requirements
        )
        
        logger.info(f"🖥️ Added compute service: {compute_type}")
        
        return self
    
    def cdn(self, 
           content_type: str,
           **kwargs) -> 'IntelligentApplication':
        """
        Add intelligent CDN service
        
        Args:
            content_type: Content type (static-assets, api-cache, media, etc.)
            **kwargs: Additional configuration options
                     performance: basic, standard, high, ultra
                     edge_optimization: bool
                     global_distribution: bool
        
        Returns:
            Self for method chaining
        """
        
        service_name = f"{self.name}-cdn"
        
        # CDN services typically need global distribution
        regions = ['global'] if kwargs.get('global_distribution', True) else ['us-east-1']
        
        # Create service requirements
        requirements = ServiceRequirements(
            service_category=ServiceCategory.CDN,
            service_type=content_type,
            performance_tier=kwargs.get('performance', 'high'),  # CDN typically needs high performance
            reliability_requirement=kwargs.get('reliability', 'high'),
            compliance_requirements=kwargs.get('compliance', []),
            geographic_regions=regions,
            cost_sensitivity=self.optimization_preferences.cost_weight,
            performance_sensitivity=self.optimization_preferences.performance_weight * 1.2,  # CDN is performance-critical
            reliability_sensitivity=self.optimization_preferences.reliability_weight,
            compliance_sensitivity=self.optimization_preferences.compliance_weight
        )
        
        # Store service configuration
        self.services[service_name] = ServiceConfiguration(
            service_name=service_name,
            service_type=content_type,
            service_category=ServiceCategory.CDN,
            configuration=kwargs,
            requirements=requirements
        )
        
        logger.info(f"🌐 Added CDN service: {content_type}")
        
        return self
    
    def storage(self, 
               storage_type: str,
               **kwargs) -> 'IntelligentApplication':
        """
        Add intelligent storage service
        
        Args:
            storage_type: Storage type (user-uploads, backups, data-lake, etc.)
            **kwargs: Additional configuration options
                     access_pattern: frequent, infrequent, archive
                     backup_requirements: none, basic, automated
                     compliance: List of compliance requirements
        
        Returns:
            Self for method chaining
        """
        
        service_name = f"{self.name}-storage"
        
        # Adjust performance requirements based on access pattern
        access_pattern = kwargs.get('access_pattern', 'frequent')
        if access_pattern == 'archive':
            performance_tier = 'basic'
        elif access_pattern == 'infrequent':
            performance_tier = 'standard'
        else:
            performance_tier = kwargs.get('performance', 'standard')
        
        # Create service requirements
        requirements = ServiceRequirements(
            service_category=ServiceCategory.STORAGE,
            service_type=storage_type,
            performance_tier=performance_tier,
            reliability_requirement=kwargs.get('reliability', 'high'),
            compliance_requirements=kwargs.get('compliance', []),
            geographic_regions=kwargs.get('regions', ['us-east-1']),
            cost_sensitivity=self.optimization_preferences.cost_weight * 1.2,  # Storage is often cost-sensitive
            performance_sensitivity=self.optimization_preferences.performance_weight,
            reliability_sensitivity=self.optimization_preferences.reliability_weight,
            compliance_sensitivity=self.optimization_preferences.compliance_weight
        )
        
        # Store service configuration
        self.services[service_name] = ServiceConfiguration(
            service_name=service_name,
            service_type=storage_type,
            service_category=ServiceCategory.STORAGE,
            configuration=kwargs,
            requirements=requirements
        )
        
        logger.info(f"💾 Added storage service: {storage_type}")
        
        return self
    
    def monitoring(self, 
                  monitoring_type: str,
                  **kwargs) -> 'IntelligentApplication':
        """
        Add intelligent monitoring service
        
        Args:
            monitoring_type: Monitoring type (full-stack, metrics-only, logs-only, etc.)
            **kwargs: Additional configuration options
        
        Returns:
            Self for method chaining
        """
        
        service_name = f"{self.name}-monitoring"
        
        # Create service requirements
        requirements = ServiceRequirements(
            service_category=ServiceCategory.MONITORING,
            service_type=monitoring_type,
            performance_tier=kwargs.get('performance', 'standard'),
            reliability_requirement=kwargs.get('reliability', 'high'),
            compliance_requirements=kwargs.get('compliance', []),
            geographic_regions=kwargs.get('regions', ['us-east-1']),
            cost_sensitivity=self.optimization_preferences.cost_weight,
            performance_sensitivity=self.optimization_preferences.performance_weight,
            reliability_sensitivity=self.optimization_preferences.reliability_weight,
            compliance_sensitivity=self.optimization_preferences.compliance_weight
        )
        
        # Store service configuration
        self.services[service_name] = ServiceConfiguration(
            service_name=service_name,
            service_type=monitoring_type,
            service_category=ServiceCategory.MONITORING,
            configuration=kwargs,
            requirements=requirements
        )
        
        logger.info(f"📈 Added monitoring service: {monitoring_type}")
        
        return self
    
    def function(self, 
                function_name: str,
                **kwargs) -> 'IntelligentApplication':
        """
        Add intelligent serverless function
        
        Args:
            function_name: Function identifier
            **kwargs: Additional configuration options
                     runtime: python, nodejs, go, etc.
                     memory: Memory allocation in MB
                     timeout: Function timeout in seconds
                     triggers: List of trigger types
        
        Returns:
            Self for method chaining
        """
        
        service_name = f"{self.name}-function"
        
        # Create service requirements
        requirements = ServiceRequirements(
            service_category=ServiceCategory.FUNCTIONS,
            service_type=function_name,
            performance_tier=kwargs.get('performance', 'standard'),
            reliability_requirement=kwargs.get('reliability', 'high'),
            compliance_requirements=kwargs.get('compliance', []),
            geographic_regions=kwargs.get('regions', ['us-east-1']),
            cost_sensitivity=self.optimization_preferences.cost_weight * 1.1,  # Functions are cost-sensitive
            performance_sensitivity=self.optimization_preferences.performance_weight,
            reliability_sensitivity=self.optimization_preferences.reliability_weight,
            compliance_sensitivity=self.optimization_preferences.compliance_weight
        )
        
        # Store service configuration
        self.services[service_name] = ServiceConfiguration(
            service_name=service_name,
            service_type=function_name,
            service_category=ServiceCategory.FUNCTIONS,
            configuration=kwargs,
            requirements=requirements
        )
        
        logger.info(f"⚡ Added serverless function: {function_name}")
        
        return self
    
    def container(self, 
                 container_name: str,
                 **kwargs) -> 'IntelligentApplication':
        """
        Add intelligent containerized service
        
        Args:
            container_name: Container service identifier
            **kwargs: Additional configuration options
                     image: Container image
                     cpu: CPU allocation
                     memory: Memory allocation
                     scaling: Scaling configuration
        
        Returns:
            Self for method chaining
        """
        
        service_name = f"{self.name}-container"
        
        # Create service requirements
        requirements = ServiceRequirements(
            service_category=ServiceCategory.CONTAINERS,
            service_type=container_name,
            performance_tier=kwargs.get('performance', 'standard'),
            reliability_requirement=kwargs.get('reliability', 'high'),
            compliance_requirements=kwargs.get('compliance', []),
            geographic_regions=kwargs.get('regions', ['us-east-1']),
            cost_sensitivity=self.optimization_preferences.cost_weight,
            performance_sensitivity=self.optimization_preferences.performance_weight,
            reliability_sensitivity=self.optimization_preferences.reliability_weight,
            compliance_sensitivity=self.optimization_preferences.compliance_weight
        )
        
        # Store service configuration
        self.services[service_name] = ServiceConfiguration(
            service_name=service_name,
            service_type=container_name,
            service_category=ServiceCategory.CONTAINERS,
            configuration=kwargs,
            requirements=requirements
        )
        
        logger.info(f"🐳 Added container service: {container_name}")
        
        return self
    
    def kubernetes(self,
                  cluster_name: str,
                  **kwargs) -> 'IntelligentApplication':
        """
        Add intelligent Kubernetes cluster
        
        Args:
            cluster_name: Kubernetes cluster identifier
            **kwargs: Additional configuration options
                     node_count: Number of nodes
                     node_type: Node instance type
                     auto_scaling: Enable auto-scaling
        
        Returns:
            Self for method chaining
        """
        
        service_name = f"{self.name}-kubernetes"
        
        # Create service requirements
        requirements = ServiceRequirements(
            service_category=ServiceCategory.KUBERNETES,
            service_type="kubernetes",
            performance_tier=kwargs.get('performance', 'high'),  # K8s typically needs good performance
            reliability_requirement=kwargs.get('reliability', 'high'),
            compliance_requirements=kwargs.get('compliance', []),
            geographic_regions=kwargs.get('regions', ['us-east-1']),
            cost_sensitivity=self.optimization_preferences.cost_weight,
            performance_sensitivity=self.optimization_preferences.performance_weight * 1.1,  # K8s is performance-critical
            reliability_sensitivity=self.optimization_preferences.reliability_weight,
            compliance_sensitivity=self.optimization_preferences.compliance_weight
        )
        
        # Store service configuration
        self.services[service_name] = ServiceConfiguration(
            service_name=service_name,
            service_type="kubernetes",
            service_category=ServiceCategory.KUBERNETES,
            configuration=kwargs,
            requirements=requirements
        )
        
        logger.info(f"☸️ Added Kubernetes cluster: {cluster_name}")
        
        return self
    
    def load_balancer(self,
                     lb_name: str,
                     **kwargs) -> 'IntelligentApplication':
        """
        Add intelligent load balancer
        
        Args:
            lb_name: Load balancer identifier
            **kwargs: Additional configuration options
                     type: application, network, classic
                     ssl_termination: Enable SSL termination
                     health_checks: Health check configuration
        
        Returns:
            Self for method chaining
        """
        
        service_name = f"{self.name}-load-balancer"
        
        # Create service requirements
        requirements = ServiceRequirements(
            service_category=ServiceCategory.LOAD_BALANCER,
            service_type="load-balancer",
            performance_tier=kwargs.get('performance', 'high'),  # LB needs good performance
            reliability_requirement=kwargs.get('reliability', 'high'),
            compliance_requirements=kwargs.get('compliance', []),
            geographic_regions=kwargs.get('regions', ['us-east-1']),
            cost_sensitivity=self.optimization_preferences.cost_weight,
            performance_sensitivity=self.optimization_preferences.performance_weight * 1.2,  # LB is performance-critical
            reliability_sensitivity=self.optimization_preferences.reliability_weight * 1.1,  # LB is reliability-critical
            compliance_sensitivity=self.optimization_preferences.compliance_weight
        )
        
        # Store service configuration
        self.services[service_name] = ServiceConfiguration(
            service_name=service_name,
            service_type="load-balancer",
            service_category=ServiceCategory.LOAD_BALANCER,
            configuration=kwargs,
            requirements=requirements
        )
        
        logger.info(f"⚖️ Added load balancer: {lb_name}")
        
        return self
    
    def compliance(self, standards: List[str]) -> 'IntelligentApplication':
        """
        Add compliance requirements to the application
        
        Args:
            standards: List of compliance standards (e.g., ["SOC2", "HIPAA", "PCI-DSS"])
            
        Returns:
            Self for method chaining
        """
        
        # Store compliance requirements globally for the application
        self.compliance_requirements = standards
        
        # Apply compliance requirements to all existing services
        for service_name, service_config in self.services.items():
            service_config.requirements.compliance_requirements = standards
            
            # Update compliance sensitivity based on standards
            if standards:
                service_config.requirements.compliance_sensitivity = 1.0
            
        logger.info(f"📋 Added compliance requirements: {', '.join(standards)}")
        
        return self


# ==============================================================================
# 4. INTELLIGENCE & LIFECYCLE METHODS
# ==============================================================================
    
    def check_state(self,
                   **kwargs) -> 'IntelligentApplication':
        """
        Add Nexus-Engine intelligence configuration to ALL services
        
        This integrates Cross-Cloud Magic with Nexus-Engine intelligence
        for failure prediction, cost optimization, security scanning, etc.
        
        Args:
            **kwargs: Nexus-Engine configuration options
                     auto_remediate: CONSERVATIVE, AGGRESSIVE, DISABLED
                     webhook: Discord/Slack webhook URL
                     learning_mode: Enable 30-day learning period
                     check_interval: Drift check frequency
        
        Returns:
            Self for method chaining
        """
        
        # Apply Nexus-Engine intelligence to all services
        for service_name, service_config in self.services.items():
            service_config.configuration.update({
                'nexus_intelligence': {
                    'failure_prediction': True,
                    'cost_optimization': True,
                    'security_scanning': True,
                    'performance_insights': True,
                    'auto_remediate': kwargs.get('auto_remediate', 'CONSERVATIVE'),
                    'webhook': kwargs.get('webhook'),
                    'learning_mode': kwargs.get('learning_mode', True),
                    'check_interval': kwargs.get('check_interval', 'ONE_HOUR')
                }
            })
        
        logger.info(f"🧠 Nexus-Engine intelligence enabled for all services")
        logger.info(f"   Auto-remediation: {kwargs.get('auto_remediate', 'CONSERVATIVE')}")
        logger.info(f"   Learning mode: {kwargs.get('learning_mode', True)}")
        logger.info(f"   Webhook alerts: {'Enabled' if kwargs.get('webhook') else 'Disabled'}")
        
        return self
    
    def preview(self) -> Dict[str, Any]:
        """
        Preview the optimized cross-cloud application deployment
        
        This shows what resources will be created across which cloud providers
        without actually creating anything.
        
        Returns:
            Dictionary of preview information with optimization details
        """
        
        if not self.auto_optimization_enabled:
            raise ValueError("Auto-optimization must be enabled to use Cross-Cloud Magic. Call .auto_optimize() first.")
        
        if not self.services:
            raise ValueError("No services defined. Add services with .database(), .compute(), etc.")
        
        print(f"\n🔍 Cross-Cloud Magic Preview: {self.name}")
        print("=" * 50)
        
        # Get optimization recommendations
        service_requirements = {name: config.requirements for name, config in self.services.items()}
        optimization = self.cross_cloud_intelligence.optimize_application(service_requirements)
        
        # Apply user constraints to recommendations
        constrained_recommendations = constraint_engine.apply_constraints(
            optimization.service_recommendations, 
            self.provider_constraints
        )
        
        # Update optimization with constrained recommendations
        optimization.service_recommendations = constrained_recommendations
        
        print(f"📋 Infrastructure Changes:")
        print()
        
        # Preview resources with optimal providers
        preview_resources = {}
        total_resources = len(optimization.service_recommendations)
        
        for service_name, recommendation in optimization.service_recommendations.items():
            provider = recommendation.recommended_provider
            service_config = self.services[service_name]
            
            print(f"🆕 SERVICE to CREATE: {service_name}")
            print(f"   ╭─ 🏷️  Service Type: {service_config.service_type}")
            print(f"   ├─ ☁️  Provider: {provider.upper()}")
            print(f"   ├─ 💰 Est. Cost: ${recommendation.estimated_monthly_cost:.2f}/month")
            print(f"   ├─ 🎯 Confidence: {recommendation.confidence_score:.1%}")
            print(f"   ├─ ⚡ Performance: +{recommendation.estimated_performance_gain:.1f}%")
            print(f"   ├─ 🛡️  Reliability: +{recommendation.estimated_reliability_improvement:.2f}%")
            print(f"   ╰─ 💡 Reason: {recommendation.reasoning}")
            print()
            
            # Register for global preview summary
            try:
                from ..cli.commands import register_preview_resource
                register_preview_resource(
                    provider=provider,
                    resource_type=service_config.service_type,
                    name=service_name,
                    details=[
                        f"Cost: ${recommendation.estimated_monthly_cost:.2f}/month",
                        f"Confidence: {recommendation.confidence_score:.1%}",
                        f"Performance: +{recommendation.estimated_performance_gain:.1f}%"
                    ]
                )
            except ImportError:
                pass  # CLI module not available
            
            preview_resources[service_name] = {
                'provider': provider,
                'service_type': service_config.service_type,
                'recommendation': recommendation,
                'estimated_cost': recommendation.estimated_monthly_cost
            }
        
        # Show optimization summary
        print("💰 Cross-Cloud Magic Optimization Summary:")
        print(f"   Total Monthly Cost: ${optimization.total_estimated_cost:.2f}")
        print(f"   Monthly Savings: ${optimization.total_cost_savings:.2f} ({optimization.cost_savings_percentage:.1f}%)")
        print(f"   Performance Improvement: {optimization.performance_improvement:.1f}%")
        print(f"   Reliability Improvement: +{optimization.reliability_improvement:.2f}% uptime")
        print()
        
        print(f"📊 Deployment Statistics:")
        print(f"   Total Resources: {total_resources}")
        print(f"   Providers Used: {len(set(r.recommended_provider for r in optimization.service_recommendations.values()))}")
        print(f"   Est. Deployment Time: 5-15 minutes")
        print()
        
        # Show provider breakdown
        provider_breakdown = {}
        for recommendation in optimization.service_recommendations.values():
            provider = recommendation.recommended_provider
            if provider not in provider_breakdown:
                provider_breakdown[provider] = []
            provider_breakdown[provider].append(recommendation)
        
        print("🌐 Provider Breakdown:")
        for provider, recommendations in provider_breakdown.items():
            provider_cost = sum(r.estimated_monthly_cost for r in recommendations)
            print(f"   {provider.upper()}: {len(recommendations)} service(s), ${provider_cost:.2f}/month")
        print()
        
        print("💡 Run .create() to deploy this optimized cross-cloud infrastructure")
        
        result = {
            'application_name': self.name,
            'preview_mode': True,
            'optimization': optimization,
            'preview_resources': preview_resources,
            'total_monthly_cost': optimization.total_estimated_cost,
            'monthly_savings': optimization.total_cost_savings,
            'savings_percentage': optimization.cost_savings_percentage,
            'total_resources': total_resources,
            'providers_used': list(provider_breakdown.keys()),
            'estimated_deployment_time': '5-15 minutes'
        }
        
        return result

    def create(self) -> Dict[str, Any]:
        """
        Create the optimized cross-cloud application
        
        This is where the magic happens - automatic provider selection
        and resource creation across multiple clouds.
        
        Returns:
            Dictionary of created resources with optimization details
        """
        
        if not self.auto_optimization_enabled:
            raise ValueError("Auto-optimization must be enabled to use Cross-Cloud Magic. Call .auto_optimize() first.")
        
        if not self.services:
            raise ValueError("No services defined. Add services with .database(), .compute(), etc.")
        
        logger.info(f"🚀 Creating cross-cloud optimized application: {self.name}")
        
        # Get optimization recommendations
        service_requirements = {name: config.requirements for name, config in self.services.items()}
        optimization = self.cross_cloud_intelligence.optimize_application(service_requirements)
        
        # Apply user constraints to recommendations
        logger.info("🎯 Applying user constraints to Cross-Cloud Magic recommendations")
        constrained_recommendations = constraint_engine.apply_constraints(
            optimization.service_recommendations, 
            self.provider_constraints
        )
        
        # Update optimization with constrained recommendations
        optimization.service_recommendations = constrained_recommendations
        
        # Log optimization results
        logger.info(f"💰 Optimization Results:")
        logger.info(f"   Total Cost: ${optimization.total_estimated_cost:.2f}/month")
        logger.info(f"   Cost Savings: ${optimization.total_cost_savings:.2f}/month ({optimization.cost_savings_percentage:.1f}%)")
        logger.info(f"   Performance Gain: {optimization.performance_improvement:.1f}%")
        logger.info(f"   Reliability Improvement: +{optimization.reliability_improvement:.2f}% uptime")
        
        # Create resources with optimal providers
        created_resources = {}
        
        for service_name, recommendation in optimization.service_recommendations.items():
            provider = recommendation.recommended_provider
            service_config = self.services[service_name]
            
            logger.info(f"🔨 Creating {service_name} on {provider.upper()}")
            
            # Create resource with optimal provider
            resource = self._create_resource_with_provider(
                provider, 
                service_config, 
                recommendation
            )
            
            created_resources[service_name] = {
                'resource': resource,
                'provider': provider,
                'recommendation': recommendation,
                'estimated_cost': recommendation.estimated_monthly_cost
            }
        
        # Store created resources
        self.created_resources = created_resources
        
        # Generate and display optimization report
        report = self.cross_cloud_intelligence.generate_cross_cloud_report(optimization)
        logger.info(f"\n{report}")
        
        result = {
            'application_name': self.name,
            'optimization': optimization,
            'resources': created_resources,
            'total_monthly_cost': optimization.total_estimated_cost,
            'monthly_savings': optimization.total_cost_savings,
            'savings_percentage': optimization.cost_savings_percentage
        }
        
        logger.info(f"✅ Cross-Cloud Magic deployment complete!")
        
        return result
    
    def _create_resource_with_provider(self, 
                                     provider: str, 
                                     service_config: ServiceConfiguration,
                                     recommendation) -> Any:
        """Create resource with the optimal provider"""
        
        service_type = service_config.service_type
        config = service_config.configuration
        service_name = service_config.service_name
        
        # Map service types to provider-specific resources
        if provider == "aws":
            return self._create_aws_resource(service_type, service_name, config)
        elif provider == "gcp":
            return self._create_gcp_resource(service_type, service_name, config)
        elif provider == "digitalocean":
            return self._create_digitalocean_resource(service_type, service_name, config)
        elif provider == "cloudflare":
            return self._create_cloudflare_resource(service_type, service_name, config)
        else:
            raise ValueError(f"Unknown provider: {provider}")


# ==============================================================================
# 5. RESOURCE CREATION METHODS
# ==============================================================================
    
    def _create_aws_resource(self, service_type: str, service_name: str, config: Dict[str, Any]) -> Any:
        """Create AWS resource based on service type"""
        
        if service_type == "postgresql":
            return (AWS.RDS(service_name)
                   .postgres()
                   .instance_class(config.get('instance_class', 'db.t3.micro'))
                   .storage(config.get('storage', 20))
                   .backup_retention(config.get('backup_retention', 7))
                   .tags([self.name, "cross-cloud-optimized", "nexus-intelligent"])
                   .create())
        
        elif service_type == "web-servers":
            return (AWS.EC2(service_name)
                   .t3_medium()
                   .auto_scale(
                       min_size=config.get('min_size', 2),
                       max_size=config.get('max_size', 10)
                   )
                   .load_balancer()
                   .tags([self.name, "cross-cloud-optimized", "nexus-intelligent"])
                   .create())
        
        elif service_type == "user-uploads":
            return (AWS.S3(service_name)
                   .private()
                   .versioning()
                   .backup()
                   .tags([self.name, "cross-cloud-optimized"])
                   .create())
        
        elif service_type == "static-assets":
            return (AWS.CloudFront(service_name)
                   .price_class("PriceClass_100")
                   .cache_behavior("optimized")
                   .tags([self.name, "cross-cloud-optimized"])
                   .create())
        
        elif service_type in ["my-function", "function"]:
            return (AWS.Lambda(service_name)
                   .python()
                   .memory(config.get('memory', 512))
                   .timeout(config.get('timeout', 30))
                   .trigger(config.get('trigger', 'http'))
                   .nexus_intelligence()
                   .tags([self.name, "cross-cloud-optimized", "nexus-intelligent"])
                   .create())
        
        elif service_type in ["my-container", "container"]:
            return (AWS.ECS(service_name)
                   .fargate()
                   .cpu(config.get('cpu', 512))
                   .memory(config.get('memory', 1024))
                   .auto_scale(
                       min_size=config.get('min_size', 1),
                       max_size=config.get('max_size', 10)
                   )
                   .nexus_intelligence()
                   .tags([self.name, "cross-cloud-optimized", "nexus-intelligent"])
                   .create())
        
        elif service_type == "full-stack":
            # AWS CloudWatch + X-Ray monitoring
            return f"AWS CloudWatch monitoring for {service_name}"
        
        elif service_type == "kubernetes":
            return f"AWS EKS cluster for {service_name}"
        
        elif service_type == "load-balancer":
            return (AWS.LoadBalancer(service_name)
                   .application()
                   .health_checks()
                   .ssl_termination()
                   .tags([self.name, "cross-cloud-optimized"])
                   .create())
        
        else:
            raise ValueError(f"Unsupported AWS service type: {service_type}")
    
    def _create_gcp_resource(self, service_type: str, service_name: str, config: Dict[str, Any]) -> Any:
        """Create GCP resource based on service type"""
        
        if service_type == "postgresql":
            return (GoogleCloud.CloudSQL(service_name)
                   .postgres()
                   .tier(config.get('tier', 'db-f1-micro'))
                   .storage_size(config.get('storage', 20))
                   .backup_enabled()
                   .tags([self.name, "cross-cloud-optimized", "nexus-intelligent"])
                   .create())
        
        elif service_type == "web-servers":
            return (GoogleCloud.Vm(service_name)
                   .machine_type(config.get('machine_type', 'e2-medium'))
                   .disk_size(config.get('disk_size', 20))
                   .auto_scaling(
                       min_replicas=config.get('min_size', 2),
                       max_replicas=config.get('max_size', 10)
                   )
                   .tags([self.name, "cross-cloud-optimized", "nexus-intelligent"])
                   .create())
        
        elif service_type in ["my-function", "function"]:
            return (GoogleCloud.CloudFunctions(service_name)
                   .python()
                   .memory(config.get('memory', '512MB'))
                   .timeout(config.get('timeout', 60))
                   .trigger(config.get('trigger', 'http'))
                   .nexus_intelligence()
                   .tags([self.name, "cross-cloud-optimized", "nexus-intelligent"])
                   .create())
        
        elif service_type in ["my-container", "container"]:
            return (GoogleCloud.CloudRun(service_name)
                   .cpu(config.get('cpu', 1))
                   .memory(config.get('memory', '1Gi'))
                   .min_instances(config.get('min_size', 0))
                   .max_instances(config.get('max_size', 10))
                   .nexus_intelligence()
                   .tags([self.name, "cross-cloud-optimized", "nexus-intelligent"])
                   .create())
        
        elif service_type == "full-stack":
            # GCP Cloud Monitoring + Logging
            return f"GCP Cloud Monitoring for {service_name}"
        
        elif service_type == "kubernetes":
            return (GoogleCloud.GKE(service_name)
                   .autopilot()
                   .region(config.get('region', 'us-central1'))
                   .nexus_intelligence()
                   .tags([self.name, "cross-cloud-optimized", "nexus-intelligent"])
                   .create())
        
        elif service_type == "load-balancer":
            return (GoogleCloud.LoadBalancer(service_name)
                   .global_load_balancer()
                   .health_checks()
                   .ssl_certificates()
                   .tags([self.name, "cross-cloud-optimized"])
                   .create())
        
        else:
            raise ValueError(f"Unsupported GCP service type: {service_type}")
    
    def _create_digitalocean_resource(self, service_type: str, service_name: str, config: Dict[str, Any]) -> Any:
        """Create DigitalOcean resource based on service type"""
        
        if service_type == "web-servers":
            return (DigitalOcean.Droplet(service_name)
                   .size(config.get('size', 's-2vcpu-2gb'))
                   .region(config.get('region', 'nyc1'))
                   .tags([self.name, "cross-cloud-optimized", "nexus-intelligent"])
                   .create())
        
        elif service_type == "user-uploads":
            return (DigitalOcean.Space(service_name)
                   .region(config.get('region', 'nyc3'))
                   .cdn_enabled(config.get('cdn', True))
                   .tags([self.name, "cross-cloud-optimized"])
                   .create())
        
        elif service_type == "postgresql":
            return (DigitalOcean.Database(service_name)
                   .postgres()
                   .size(config.get('size', 'db-s-1vcpu-1gb'))
                   .region(config.get('region', 'nyc1'))
                   .tags([self.name, "cross-cloud-optimized", "nexus-intelligent"])
                   .create())
        
        elif service_type in ["my-function", "function"]:
            return (DigitalOcean.Function(service_name)
                   .python()
                   .memory(config.get('memory', 512))
                   .timeout(config.get('timeout', 30))
                   .trigger(config.get('trigger', 'http'))
                   .nexus_intelligence()
                   .tags([self.name, "cross-cloud-optimized", "nexus-intelligent"])
                   .create())
        
        elif service_type in ["my-container", "container"]:
            return (DigitalOcean.AppPlatform(service_name)
                   .container()
                   .size(config.get('size', 'basic'))
                   .auto_deploy()
                   .nexus_intelligence()
                   .tags([self.name, "cross-cloud-optimized", "nexus-intelligent"])
                   .create())
        
        elif service_type == "full-stack":
            # DigitalOcean basic monitoring
            return f"DigitalOcean monitoring for {service_name}"
        
        elif service_type == "kubernetes":
            return (DigitalOcean.Kubernetes(service_name)
                   .node_pool(
                       size=config.get('node_size', 's-2vcpu-2gb'),
                       count=config.get('node_count', 3)
                   )
                   .region(config.get('region', 'nyc1'))
                   .nexus_intelligence()
                   .tags([self.name, "cross-cloud-optimized", "nexus-intelligent"])
                   .create())
        
        elif service_type == "load-balancer":
            return (DigitalOcean.LoadBalancer(service_name)
                   .health_checks()
                   .sticky_sessions()
                   .region(config.get('region', 'nyc1'))
                   .tags([self.name, "cross-cloud-optimized"])
                   .create())
        
        else:
            raise ValueError(f"Unsupported DigitalOcean service type: {service_type}")
    
    def _create_cloudflare_resource(self, service_type: str, service_name: str, config: Dict[str, Any]) -> Any:
        """Create Cloudflare resource based on service type"""
        
        if service_type == "static-assets":
            domain = config.get('domain', f"{self.name}.example.com")
            return (Cloudflare.DNS(domain)
                   .cdn_enabled()
                   .ssl_full()
                   .firewall("strict")
                   .tags([self.name, "cross-cloud-optimized"])
                   .create())
        
        elif service_type == "dns":
            domain = config.get('domain', f"{self.name}.example.com")
            return (Cloudflare.DNS(domain)
                   .proxy_enabled()
                   .tags([self.name, "cross-cloud-optimized"])
                   .create())
        
        elif service_type in ["my-function", "function"]:
            return (Cloudflare.Worker(service_name)
                   .script(config.get('script', 'worker.js'))
                   .route(config.get('route', f"api.{self.name}.com/*"))
                   .kv_namespace(config.get('kv_namespace'))
                   .tags([self.name, "cross-cloud-optimized"])
                   .create())
        
        elif service_type == "load-balancer":
            return (Cloudflare.LoadBalancer(service_name)
                   .geo_routing()
                   .health_checks()
                   .failover_pools()
                   .tags([self.name, "cross-cloud-optimized"])
                   .create())
        
        else:
            raise ValueError(f"Unsupported Cloudflare service type: {service_type}")


# ==============================================================================
# 6. PREVIEW & UTILITY METHODS
# ==============================================================================
    
    def get_optimization_summary(self) -> str:
        """Get human-readable optimization summary"""
        
        if not self.created_resources:
            return "No optimization performed yet. Call .create() first."
        
        lines = [
            f"🌐 Cross-Cloud Magic Summary for {self.name}",
            "=" * 50,
            ""
        ]
        
        total_cost = 0
        for service_name, resource_info in self.created_resources.items():
            provider = resource_info['provider']
            cost = resource_info['estimated_cost']
            total_cost += cost
            
            lines.append(f"🔨 {service_name}:")
            lines.append(f"   Provider: {provider.upper()}")
            lines.append(f"   Cost: ${cost:.2f}/month")
            lines.append("")
        
        lines.extend([
            f"💰 Total Monthly Cost: ${total_cost:.2f}",
            f"🚀 Deployment Status: Complete",
            f"🧠 Intelligence: Nexus-Engine enabled on all resources"
        ])
        
        return "\n".join(lines)
    
    def preview(self) -> Dict[str, Any]:
        """
        Preview what the Cross-Cloud Magic optimization will create without actually deploying
        
        Returns:
            Dict containing preview information for CLI display
        """
        
        if not self.auto_optimization_enabled:
            return {
                "error": "Auto-optimization not enabled. Call .auto_optimize() first.",
                "services": []
            }
        
        if not self.services:
            return {
                "error": "No services defined. Add services like .database(), .compute(), etc.",
                "services": []
            }
        
        logger.info("🔍 Analyzing Cross-Cloud Magic optimization...")
        
        # Convert services to requirements for Cross-Cloud Intelligence
        service_requirements = {}
        for service_name, service_config in self.services.items():
            service_requirements[service_name] = service_config.requirements
        
        # Run Cross-Cloud Intelligence optimization
        optimization_result = cross_cloud_intelligence.optimize_application(service_requirements)
        
        # Apply any user constraints
        final_selections = constraint_engine.apply_constraints(
            optimization_result.service_recommendations,
            self.provider_constraints
        )
        
        # Build preview information using CONSTRAINED recommendations
        preview_services = []
        total_estimated_cost = optimization_result.total_estimated_cost
        
        for service_name, recommendation in final_selections.items():
            service_config = self.services[service_name]
            
            # Get reasoning as string
            reasoning_text = "; ".join(recommendation.reasoning) if recommendation.reasoning else "Optimal choice based on analysis"
            
            preview_services.append({
                "name": service_name,
                "type": service_config.service_type,
                "provider": recommendation.recommended_provider,
                "reasoning": reasoning_text,
                "estimated_cost_monthly": recommendation.estimated_monthly_cost,
                "confidence_score": int(recommendation.confidence_score * 100),
                "performance_score": recommendation.performance_score,
                "reliability_score": recommendation.reliability_score
            })
        
        # Provider breakdown
        provider_counts = {}
        for service in preview_services:
            provider = service['provider']
            provider_counts[provider] = provider_counts.get(provider, 0) + 1
        
        # Use savings from optimization result
        estimated_savings = optimization_result.total_cost_savings
        savings_percentage = optimization_result.cost_savings_percentage
        
        preview_data = {
            "application_name": self.name,
            "optimization_enabled": True,
            "services": preview_services,
            "total_services": len(preview_services),
            "estimated_monthly_cost": total_estimated_cost,
            "estimated_savings": estimated_savings,
            "savings_percentage": savings_percentage,
            "provider_breakdown": provider_counts,
            "cross_cloud_magic": True,
            "nexus_intelligence": True,
            "deployment_regions": self._get_deployment_regions(),
            "summary": self._generate_preview_summary(preview_services, total_estimated_cost, savings_percentage)
        }
        
        # Register individual services with CLI preview system instead of dumping raw data
        try:
            from ..cli.commands import register_preview_resource
            for service in preview_services:
                register_preview_resource(
                    provider=service['provider'],
                    resource_type=service['type'], 
                    name=service['name'],
                    details=[
                        f"Monthly Cost: ${service['estimated_cost_monthly']:.2f}",
                        f"Confidence: {service['confidence_score']}%",
                        f"Reasoning: {service['reasoning'][:50]}..." if len(service['reasoning']) > 50 else f"Reasoning: {service['reasoning']}"
                    ]
                )
        except ImportError:
            pass  # CLI not available, continue normally
        
        # Display preview in CLI format
        self._display_preview(preview_data)
        
        return preview_data
    
    def _determine_service_category(self, service_type: str) -> ServiceCategory:
        """Determine service category for Cross-Cloud Intelligence"""
        
        if service_type in ['postgresql', 'mysql', 'mongodb', 'redis']:
            return ServiceCategory.DATABASE
        elif service_type in ['web-servers', 'api-servers', 'worker-nodes']:
            return ServiceCategory.COMPUTE
        elif service_type in ['user-uploads', 'data-lake', 'backups']:
            return ServiceCategory.STORAGE
        elif service_type in ['static-assets', 'media-delivery']:
            return ServiceCategory.CDN
        elif service_type in ['functions', 'lambdas', 'serverless']:
            return ServiceCategory.SERVERLESS
        else:
            return ServiceCategory.COMPUTE  # Default fallback
    
    def _get_deployment_regions(self) -> List[str]:
        """Get list of deployment regions"""
        
        regions = []
        for service_config in self.services.values():
            if hasattr(service_config.requirements, 'geographic_regions'):
                regions.extend(service_config.requirements.geographic_regions)
        
        return list(set(regions)) or ['us-east-1', 'us-west-2']  # Default regions
    
    def _generate_preview_summary(self, services: List[Dict], total_cost: float, savings_percentage: float) -> str:
        """Generate human-readable preview summary"""
        
        provider_counts = {}
        for service in services:
            provider = service['provider']
            provider_counts[provider] = provider_counts.get(provider, 0) + 1
        
        lines = [
            f"🌐 Cross-Cloud Magic will deploy {len(services)} services:",
            "",
        ]
        
        for service in services:
            lines.append(f"  • {service['name']} ({service['type']}) → {service['provider'].upper()}")
            lines.append(f"    Reason: {service['reasoning']}")
            lines.append(f"    Cost: ${service['estimated_cost_monthly']:.2f}/month")
            lines.append("")
        
        lines.extend([
            f"💰 Total estimated cost: ${total_cost:.2f}/month",
            f"💵 Estimated savings: {savings_percentage:.1f}% vs single-cloud",
            "",
            "🏢 Provider distribution:",
        ])
        
        for provider, count in provider_counts.items():
            lines.append(f"  • {provider.upper()}: {count} service{'s' if count != 1 else ''}")
        
        return "\n".join(lines)
    
    def _display_preview(self, preview_data: Dict[str, Any]) -> None:
        """Display preview information in CLI-friendly format"""
        
        print("\n🔍 Cross-Cloud Magic Preview")
        print("=" * 50)
        print(f"Application: {preview_data['application_name']}")
        print(f"Services: {preview_data['total_services']}")
        print(f"Estimated Monthly Cost: ${preview_data['estimated_monthly_cost']:.2f}")
        print(f"Estimated Savings: {preview_data['savings_percentage']:.1f}%")
        print("\n📋 Service Details:")
        print("-" * 30)
        
        for service in preview_data['services']:
            print(f"\n🔨 {service['name']} ({service['type']})")
            print(f"   Provider: {service['provider'].upper()}")
            print(f"   Reasoning: {service['reasoning']}")
            print(f"   Monthly Cost: ${service['estimated_cost_monthly']:.2f}")
            print(f"   Confidence: {service['confidence_score']}%")
        
        print(f"\n🏢 Provider Breakdown:")
        for provider, count in preview_data['provider_breakdown'].items():
            print(f"   • {provider.upper()}: {count} service{'s' if count != 1 else ''}")
        
        print(f"\n🧠 Nexus-Engine Intelligence: Enabled")
        print(f"🌐 Cross-Cloud Optimization: Enabled")
        print(f"🚀 Ready to deploy with: .create()")
        print("")