"""
Provider Constraints and User Control System

This module ensures that Cross-Cloud Magic respects user preferences and
organizational constraints while providing intelligent recommendations.

Users have complete control over:
- Which providers they want to use
- Which providers they want to exclude
- Provider preferences and overrides
- Manual provider selection when desired
"""

from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class ProviderPreference(Enum):
    """Provider preference levels"""
    REQUIRED = "required"           # Must use this provider
    PREFERRED = "preferred"         # Prefer this provider when possible
    ALLOWED = "allowed"            # Can use this provider (default)
    AVOID = "avoid"                # Avoid this provider unless necessary
    FORBIDDEN = "forbidden"        # Never use this provider


@dataclass
class ProviderConstraints:
    """User-defined constraints for provider selection"""
    allowed_providers: Optional[Set[str]] = None     # Only use these providers
    forbidden_providers: Optional[Set[str]] = None   # Never use these providers
    provider_preferences: Optional[Dict[str, ProviderPreference]] = None
    service_overrides: Optional[Dict[str, str]] = None  # Force specific service->provider mapping
    compliance_requirements: Optional[List[str]] = None
    geographic_restrictions: Optional[List[str]] = None
    cost_limits: Optional[Dict[str, float]] = None
    
    def __post_init__(self):
        """Initialize default values"""
        if self.allowed_providers is None:
            self.allowed_providers = set()
        if self.forbidden_providers is None:
            self.forbidden_providers = set()
        if self.provider_preferences is None:
            self.provider_preferences = {}
        if self.service_overrides is None:
            self.service_overrides = {}
        if self.compliance_requirements is None:
            self.compliance_requirements = []
        if self.geographic_restrictions is None:
            self.geographic_restrictions = []
        if self.cost_limits is None:
            self.cost_limits = {}


class ProviderConstraintEngine:
    """
    Engine that applies user constraints to Cross-Cloud Magic recommendations
    
    This ensures users maintain complete control over their infrastructure
    while benefiting from intelligent optimization within their constraints.
    """
    
    def __init__(self):
        self.default_constraints = ProviderConstraints()
    
    def apply_constraints(self, 
                         recommendations: Dict[str, Any],
                         constraints: ProviderConstraints) -> Dict[str, Any]:
        """
        Apply user constraints to Cross-Cloud Magic recommendations
        
        Args:
            recommendations: Original Cross-Cloud Magic recommendations
            constraints: User-defined provider constraints
            
        Returns:
            Modified recommendations respecting user constraints
        """
        
        logger.info("🎯 Applying provider constraints to recommendations")
        
        constrained_recommendations = {}
        
        for service_name, recommendation in recommendations.items():
            # Apply constraints to each service recommendation
            constrained_rec = self._apply_service_constraints(
                service_name, 
                recommendation, 
                constraints
            )
            constrained_recommendations[service_name] = constrained_rec
        
        return constrained_recommendations
    
    def _apply_service_constraints(self,
                                 service_name: str,
                                 recommendation: Any,
                                 constraints: ProviderConstraints) -> Any:
        """Apply constraints to a single service recommendation"""
        
        service_type = getattr(recommendation, 'service_type', '')
        original_provider = getattr(recommendation, 'recommended_provider', '')
        
        # 1. Check for service-specific overrides (highest priority)
        if service_type in constraints.service_overrides:
            forced_provider = constraints.service_overrides[service_type]
            logger.info(f"🔒 Service override: {service_type} forced to {forced_provider.upper()}")
            return self._create_override_recommendation(
                recommendation, forced_provider, "Service override"
            )
        
        # 2. Check forbidden providers
        if original_provider in constraints.forbidden_providers:
            logger.info(f"❌ Provider {original_provider.upper()} forbidden, finding alternative")
            alternative = self._find_allowed_alternative(
                recommendation, constraints
            )
            return alternative
        
        # 3. Check allowed providers constraint
        if constraints.allowed_providers and original_provider not in constraints.allowed_providers:
            logger.info(f"⚠️ Provider {original_provider.upper()} not in allowed list, finding alternative")
            alternative = self._find_allowed_alternative(
                recommendation, constraints
            )
            return alternative
        
        # 4. Apply provider preferences
        # 4a. Check for REQUIRED providers first (highest priority among preferences)
        required_providers = [p for p, pref in constraints.provider_preferences.items() 
                            if pref == ProviderPreference.REQUIRED]
        
        if required_providers and original_provider not in required_providers:
            # Find the best required provider for this specific service
            best_required_provider = self._find_best_required_provider(
                required_providers, recommendation
            )
            
            if best_required_provider:
                logger.info(f"🔒 REQUIRED provider constraint: optimally selecting {best_required_provider.upper()} for {getattr(recommendation, 'service_type', '')}")
                return self._create_override_recommendation(
                    recommendation, best_required_provider, f"Best required provider: {best_required_provider}"
                )
            
            logger.warning(f"⚠️ Required providers {required_providers} don't support service type {getattr(recommendation, 'service_type', '')}")
        
        # 4b. Handle AVOID preferences
        if original_provider in constraints.provider_preferences:
            preference = constraints.provider_preferences[original_provider]
            
            if preference == ProviderPreference.AVOID:
                logger.info(f"⚠️ Provider {original_provider.upper()} marked as 'avoid', finding better option")
                alternative = self._find_preferred_alternative(
                    recommendation, constraints
                )
                if alternative:
                    return alternative
        
        # 5. Check compliance requirements
        if not self._meets_compliance_requirements(recommendation, constraints):
            logger.info(f"📋 Provider {original_provider.upper()} doesn't meet compliance, finding compliant option")
            alternative = self._find_compliant_alternative(
                recommendation, constraints
            )
            return alternative
        
        # Original recommendation passes all constraints
        logger.info(f"✅ Provider {original_provider.upper()} for {service_type} meets all constraints")
        return recommendation
    
    def _find_allowed_alternative(self,
                                original_recommendation: Any,
                                constraints: ProviderConstraints) -> Any:
        """Find an alternative provider that meets user constraints"""
        
        alternatives = getattr(original_recommendation, 'alternatives', [])
        
        for provider, score in alternatives:
            # Check if provider is allowed
            if constraints.allowed_providers and provider not in constraints.allowed_providers:
                continue
            
            # Check if provider is forbidden
            if provider in constraints.forbidden_providers:
                continue
            
            # Check provider preferences
            if provider in constraints.provider_preferences:
                preference = constraints.provider_preferences[provider]
                if preference == ProviderPreference.FORBIDDEN:
                    continue
            
            logger.info(f"✅ Found allowed alternative: {provider.upper()} (score: {score:.1%})")
            return self._create_override_recommendation(
                original_recommendation, provider, "User constraint compliance"
            )
        
        # No allowed alternative found - use the least bad option
        logger.warning("⚠️ No fully compliant alternative found, using best available option")
        if alternatives:
            fallback_provider = alternatives[0][0]
            return self._create_override_recommendation(
                original_recommendation, fallback_provider, "Best available option"
            )
        
        return original_recommendation
    
    def _find_preferred_alternative(self,
                                  original_recommendation: Any,
                                  constraints: ProviderConstraints) -> Any:
        """Find a preferred alternative if available"""
        
        alternatives = getattr(original_recommendation, 'alternatives', [])
        
        # Look for preferred providers first
        for provider, score in alternatives:
            if provider in constraints.provider_preferences:
                preference = constraints.provider_preferences[provider]
                if preference == ProviderPreference.PREFERRED:
                    logger.info(f"✨ Found preferred alternative: {provider.upper()}")
                    return self._create_override_recommendation(
                        original_recommendation, provider, "User preference"
                    )
        
        return None  # No preferred alternative found
    
    def _find_compliant_alternative(self,
                                  original_recommendation: Any,
                                  constraints: ProviderConstraints) -> Any:
        """Find an alternative that meets compliance requirements"""
        
        alternatives = getattr(original_recommendation, 'alternatives', [])
        
        for provider, score in alternatives:
            if self._provider_meets_compliance(provider, constraints.compliance_requirements):
                logger.info(f"📋 Found compliant alternative: {provider.upper()}")
                return self._create_override_recommendation(
                    original_recommendation, provider, "Compliance requirement"
                )
        
        logger.warning("⚠️ No compliant alternative found")
        return original_recommendation
    
    def _meets_compliance_requirements(self,
                                     recommendation: Any,
                                     constraints: ProviderConstraints) -> bool:
        """Check if recommendation meets compliance requirements"""
        
        if not constraints.compliance_requirements:
            return True
        
        provider = getattr(recommendation, 'recommended_provider', '')
        return self._provider_meets_compliance(provider, constraints.compliance_requirements)
    
    def _provider_meets_compliance(self,
                                 provider: str,
                                 requirements: List[str]) -> bool:
        """Check if provider meets specific compliance requirements"""
        
        # Provider compliance matrix
        compliance_matrix = {
            "aws": ["SOC2", "ISO27001", "HIPAA", "PCI-DSS", "FedRAMP"],
            "gcp": ["SOC2", "ISO27001", "HIPAA", "PCI-DSS"],
            "digitalocean": ["SOC2", "ISO27001"],
            "cloudflare": ["SOC2", "ISO27001"]
        }
        
        provider_compliance = compliance_matrix.get(provider, [])
        
        for requirement in requirements:
            if requirement not in provider_compliance:
                return False
        
        return True
    
    def _provider_supports_service(self, provider: str, recommendation: Any) -> bool:
        """Check if a provider supports the service type in the recommendation"""
        service_type = getattr(recommendation, 'service_type', '')
        
        # Import here to avoid circular imports
        try:
            from .cross_cloud_intelligence import cross_cloud_intelligence
            available_providers = cross_cloud_intelligence._get_available_providers(service_type)
            return provider in available_providers
        except Exception:
            # Fallback: assume basic service support
            basic_services = ["postgresql", "web-servers", "static-assets", "user-uploads", "full-stack"]
            return service_type in basic_services
    
    def _find_best_required_provider(self, required_providers: List[str], recommendation: Any) -> Optional[str]:
        """Find the best required provider for a specific service type"""
        service_type = getattr(recommendation, 'service_type', '')
        
        # Get alternatives from the original recommendation (includes all provider scores)
        alternatives = getattr(recommendation, 'alternatives', [])
        
        # Create a combined list of all providers with scores
        all_providers = [(recommendation.recommended_provider, recommendation.confidence_score)]
        if alternatives:
            all_providers.extend(alternatives)
        
        # Filter to only required providers that support this service
        valid_required_providers = []
        for provider, score in all_providers:
            if provider in required_providers and self._provider_supports_service(provider, recommendation):
                valid_required_providers.append((provider, score))
        
        # If no valid required providers found, fall back to first required provider that supports the service
        if not valid_required_providers:
            logger.warning(f"⚠️ No valid required providers found for {service_type}, falling back")
            for provider in required_providers:
                if self._provider_supports_service(provider, recommendation):
                    return provider
            return None
        
        # If scores are tied at 1.0, use service-specific intelligence for CDN
        if service_type == "static-assets" and len(valid_required_providers) > 1:
            # For CDN services, prefer Cloudflare if it's available
            for provider, score in valid_required_providers:
                if provider == "cloudflare":
                    return "cloudflare"
        
        # Return the required provider with the highest score
        best_provider, best_score = max(valid_required_providers, key=lambda x: x[1])
        return best_provider
    
    def _create_override_recommendation(self,
                                      original_recommendation: Any,
                                      new_provider: str,
                                      reason: str) -> Any:
        """Create a new recommendation with overridden provider"""
        
        # Create a copy of the original recommendation with new provider
        override_rec = original_recommendation
        override_rec.recommended_provider = new_provider
        override_rec.reasoning.insert(0, f"Provider override: {reason}")
        
        return override_rec


# Factory functions for common constraint patterns
def aws_only_constraints() -> ProviderConstraints:
    """Company A: AWS-only constraint"""
    return ProviderConstraints(
        allowed_providers={"aws"},
        provider_preferences={"aws": ProviderPreference.REQUIRED}
    )


def aws_gcp_constraints() -> ProviderConstraints:
    """Company B: AWS and GCP only"""
    return ProviderConstraints(
        allowed_providers={"aws", "gcp"},
        provider_preferences={
            "aws": ProviderPreference.PREFERRED,
            "gcp": ProviderPreference.PREFERRED
        }
    )


def multi_cloud_with_preferences() -> ProviderConstraints:
    """Company C: Multi-cloud with specific preferences"""
    return ProviderConstraints(
        provider_preferences={
            "aws": ProviderPreference.PREFERRED,      # Prefer AWS
            "gcp": ProviderPreference.ALLOWED,        # Allow GCP
            "digitalocean": ProviderPreference.AVOID, # Avoid DO unless very cost-effective
            "cloudflare": ProviderPreference.PREFERRED # Prefer Cloudflare for edge
        }
    )


def compliance_heavy_constraints() -> ProviderConstraints:
    """Company D: Compliance-heavy requirements"""
    return ProviderConstraints(
        compliance_requirements=["HIPAA", "PCI-DSS", "SOC2"],
        provider_preferences={
            "aws": ProviderPreference.PREFERRED,  # AWS has best compliance
            "gcp": ProviderPreference.ALLOWED,
            "digitalocean": ProviderPreference.FORBIDDEN,  # Doesn't meet HIPAA
            "cloudflare": ProviderPreference.AVOID
        }
    )


def cost_conscious_constraints() -> ProviderConstraints:
    """Company E: Cost-conscious with specific limits"""
    return ProviderConstraints(
        cost_limits={
            "database": 100.0,     # Max $100/month for database
            "compute": 200.0,      # Max $200/month for compute
            "total": 500.0         # Max $500/month total
        },
        provider_preferences={
            "digitalocean": ProviderPreference.PREFERRED,  # Prefer cost-effective DO
            "aws": ProviderPreference.AVOID,               # Avoid expensive AWS
            "cloudflare": ProviderPreference.PREFERRED     # Prefer cost-effective edge
        }
    )


# Global constraint engine instance
constraint_engine = ProviderConstraintEngine()