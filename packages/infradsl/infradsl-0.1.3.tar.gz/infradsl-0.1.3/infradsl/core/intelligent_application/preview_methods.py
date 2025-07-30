"""
Preview & Utility Methods for IntelligentApplication

Methods for previewing Cross-Cloud Magic optimization results
and providing utility functions.
"""

import logging
from typing import TYPE_CHECKING, Dict, Any, List

from ..cross_cloud_intelligence import cross_cloud_intelligence, ServiceCategory
from ..provider_constraints import constraint_engine

if TYPE_CHECKING:
    from .core import IntelligentApplication

logger = logging.getLogger(__name__)


class PreviewMethodsMixin:
    """Mixin providing preview and utility methods"""
    
    def get_optimization_summary(self: 'IntelligentApplication') -> str:
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
    
    def preview(self: 'IntelligentApplication') -> Dict[str, Any]:
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
            from ...cli.commands import register_preview_resource
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
    
    def _determine_service_category(self: 'IntelligentApplication', service_type: str) -> ServiceCategory:
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
    
    def _get_deployment_regions(self: 'IntelligentApplication') -> List[str]:
        """Get list of deployment regions"""
        
        regions = []
        for service_config in self.services.values():
            if hasattr(service_config.requirements, 'geographic_regions'):
                regions.extend(service_config.requirements.geographic_regions)
        
        return list(set(regions)) or ['us-east-1', 'us-west-2']  # Default regions
    
    def _generate_preview_summary(self: 'IntelligentApplication', services: List[Dict], total_cost: float, savings_percentage: float) -> str:
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
    
    def _display_preview(self: 'IntelligentApplication', preview_data: Dict[str, Any]) -> None:
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
        
        # Show compliance requirements if set
        if hasattr(self, 'compliance_requirements') and self.compliance_requirements:
            print(f"\n📋 Compliance Requirements:")
            for standard in self.compliance_requirements:
                print(f"   • {standard}")
        
        # Show drift detection configuration if set
        if self.services:
            # Check if any service has nexus intelligence configured
            sample_service = next(iter(self.services.values()))
            if 'nexus_intelligence' in sample_service.configuration:
                nexus_config = sample_service.configuration['nexus_intelligence']
                print(f"\n🔍 Drift Detection & Monitoring:")
                print(f"   • Auto-remediation: {nexus_config.get('auto_remediate', 'CONSERVATIVE')}")
                print(f"   • Check interval: {nexus_config.get('check_interval', 'ONE_HOUR')}")
                print(f"   • Webhook alerts: {'Enabled' if nexus_config.get('webhook') else 'Disabled'}")
                print(f"   • Learning mode: {'Enabled' if nexus_config.get('learning_mode', True) else 'Disabled'}")
        
        print(f"\n🧠 Nexus-Engine Intelligence: Enabled")
        print(f"🌐 Cross-Cloud Optimization: Enabled")
        print(f"🚀 Ready to deploy with: .create()")
        print("")