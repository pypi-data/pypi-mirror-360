"""
Provider Constraint Methods for IntelligentApplication

Methods for constraining and configuring provider preferences 
for Cross-Cloud Magic optimization.
"""

import logging
from typing import TYPE_CHECKING

from ..provider_constraints import ProviderPreference

if TYPE_CHECKING:
    from .core import IntelligentApplication

logger = logging.getLogger(__name__)


class ConstraintMethodsMixin:
    """Mixin providing provider constraint methods"""
    
    def constrain_to_providers(self: 'IntelligentApplication', *providers: str) -> 'IntelligentApplication':
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
    
    def forbid_providers(self: 'IntelligentApplication', *providers: str) -> 'IntelligentApplication':
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
    
    def prefer_providers(self: 'IntelligentApplication', **preferences) -> 'IntelligentApplication':
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
    
    def force_service_provider(self: 'IntelligentApplication', service_type: str, provider: str) -> 'IntelligentApplication':
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
    
    def require_compliance(self: 'IntelligentApplication', *requirements: str) -> 'IntelligentApplication':
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