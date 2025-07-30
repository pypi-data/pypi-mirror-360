"""
Intelligence & Lifecycle Methods for IntelligentApplication

Methods for configuring intelligence, managing application lifecycle,
and orchestrating Cross-Cloud Magic optimization.
"""

import logging
from typing import TYPE_CHECKING, Dict, Any

from ..cross_cloud_intelligence import cross_cloud_intelligence
from ..provider_constraints import constraint_engine

if TYPE_CHECKING:
    from .core import IntelligentApplication

logger = logging.getLogger(__name__)


class LifecycleMethodsMixin:
    """Mixin providing intelligence and lifecycle methods"""
    
    def check_state(self: 'IntelligentApplication',
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
    
    def create(self: 'IntelligentApplication') -> Dict[str, Any]:
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
        logger.info(f"\\n{report}")
        
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