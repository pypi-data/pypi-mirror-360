"""
GCP Certificate Manager Complete Implementation

Complete Certificate Manager implementation combining core functionality, 
configuration methods, and lifecycle operations into a single modular class.
Rails-like API with Cross-Cloud Magic optimization.
"""

from typing import Dict, Any, List, Optional, Union
from .certificate_manager_core import CertificateManagerCore
from .certificate_manager_configuration import CertificateManagerConfigurationMixin
from .certificate_manager_lifecycle import CertificateManagerLifecycleMixin


class CertificateManager(CertificateManagerCore, CertificateManagerConfigurationMixin, CertificateManagerLifecycleMixin):
    """
    Complete Google Cloud Certificate Manager implementation.
    
    This class combines:
    - CertificateManagerCore: Basic certificate attributes and authentication
    - CertificateManagerConfigurationMixin: Chainable configuration methods
    - CertificateManagerLifecycleMixin: Lifecycle operations (create, destroy, preview)
    
    Features:
    - Rails-like method chaining for fluent SSL certificate configuration
    - Smart state management and drift detection
    - Cross-Cloud Magic optimization
    - Google-managed and self-managed certificate support
    - Domain validation and provisioning monitoring
    - Common certificate patterns (webapp, API, wildcard, etc.)
    - Enterprise and compliance configurations
    - Free Google-managed certificates with automatic renewal
    
    Example:
        # Simple website certificate
        cert = CertificateManager("website-cert")
        cert.webapp_cert("example.com")
        cert.create()
        
        # API certificate with custom domains
        cert = CertificateManager("api-cert")
        cert.domains(["api.example.com", "v1.api.example.com"])
        cert.managed().global_scope()
        cert.create()
        
        # Complete enterprise certificate
        cert = CertificateManager("enterprise-cert")
        cert.complete_website_cert("company.com")
        cert.enterprise_grade()
        cert.create()
        
        # Cross-Cloud Magic optimization
        cert = CertificateManager("optimized-cert")
        cert.single_domain_cert("secure.example.com")
        cert.optimize_for("compliance")
        cert.create()
    """
    
    def __init__(self, name: str):
        """
        Initialize Certificate Manager with certificate name.
        
        Args:
            name: Certificate name (must be valid GCP certificate name)
        """
        # Initialize all parent classes
        CertificateManagerCore.__init__(self, name)
        
        # Ensure proper initialization order
        self._initialize_managers()
        
    def __repr__(self) -> str:
        """String representation of Certificate Manager instance"""
        cert_type = "managed" if self.managed_certificate else "self-managed"
        status = "configured" if self.domain_names or (not self.managed_certificate and self.certificate_pem) else "unconfigured"
        
        return (f"CertificateManager(name='{self.cert_name}', "
                f"type='{cert_type}', "
                f"domains={len(self.domain_names)}, "
                f"location='{self.certificate_location}', "
                f"status='{status}')")
    
    def summary(self) -> Dict[str, Any]:
        """
        Get comprehensive summary of Certificate Manager configuration.
        
        Returns:
            Dict containing all configuration details
        """
        # Analyze certificate configuration
        has_wildcard = any(domain.startswith("*.") for domain in self.domain_names)
        certificate_patterns = []
        
        if has_wildcard:
            certificate_patterns.append("wildcard")
        if any("api." in domain for domain in self.domain_names):
            certificate_patterns.append("api")
        if any("www." in domain for domain in self.domain_names):
            certificate_patterns.append("webapp")
        if any("cdn." in domain for domain in self.domain_names):
            certificate_patterns.append("cdn")
        
        summary = {
            "cert_name": self.cert_name,
            "certificate_description": self.certificate_description,
            "managed_certificate": self.managed_certificate,
            "certificate_type": self._get_certificate_type_from_config(),
            
            # Domains
            "domain_names": self.domain_names,
            "domain_count": len(self.domain_names),
            "has_wildcard": has_wildcard,
            "certificate_patterns": certificate_patterns,
            
            # Configuration
            "certificate_location": self.certificate_location,
            "certificate_scope": self.certificate_scope,
            "validation_method": self.validation_method,
            "renewal_enabled": self.renewal_enabled,
            
            # Labels and metadata
            "labels": self.certificate_labels,
            "label_count": len(self.certificate_labels),
            "annotations": self.certificate_annotations,
            
            # State
            "state": {
                "exists": self.certificate_exists,
                "created": self.certificate_created,
                "resource_name": self.certificate_resource_name,
                "status": self.certificate_status,
                "provisioning_issues": self.provisioning_issues
            },
            
            # Cost
            "estimated_monthly_cost": self._calculate_certificate_cost()
        }
        
        return summary
    
    def display_config(self):
        """Display current configuration in human-readable format"""
        print(f"\n🔐 Certificate Manager Configuration: {self.cert_name}")
        print(f"   🏷️  Type: {'Google-managed' if self.managed_certificate else 'Self-managed'}")
        print(f"   📋 Description: {self.certificate_description}")
        print(f"   📍 Location: {self.certificate_location}")
        print(f"   🎯 Scope: {self.certificate_scope}")
        
        # Domains
        if self.domain_names:
            print(f"\n🌍 Domains ({len(self.domain_names)}):")
            for domain in self.domain_names:
                icon = "🌟" if domain.startswith("*.") else "🌐"
                print(f"   {icon} {domain}")
        else:
            print(f"\n🌍 Domains: None configured")
        
        # Certificate analysis
        if self.domain_names:
            print(f"\n📊 Certificate Analysis:")
            cert_type = self._get_certificate_type_from_config()
            print(f"   🎯 Detected Type: {cert_type.replace('_', ' ').title()}")
            
            if any(domain.startswith("*.") for domain in self.domain_names):
                print(f"   🌟 Wildcard: Yes")
            
            patterns = []
            if any("api." in domain for domain in self.domain_names):
                patterns.append("API")
            if any("www." in domain for domain in self.domain_names):
                patterns.append("Web App")
            if any("cdn." in domain for domain in self.domain_names):
                patterns.append("CDN")
            
            if patterns:
                print(f"   🏗️  Patterns: {', '.join(patterns)}")
        
        # Configuration details
        if self.managed_certificate:
            print(f"\n⚡ Managed Certificate:")
            print(f"   🔄 Auto-renewal: ✅ Enabled")
            print(f"   🔍 Validation: {self.validation_method}")
            print(f"   💰 Cost: Free")
        else:
            print(f"\n📜 Self-managed Certificate:")
            print(f"   🔄 Auto-renewal: ❌ Manual")
            print(f"   📋 PEM Data: {'✅ Provided' if self.certificate_pem else '❌ Missing'}")
            print(f"   🔑 Private Key: {'✅ Provided' if self.private_key_pem else '❌ Missing'}")
        
        # Labels
        if self.certificate_labels:
            print(f"\n🏷️  Labels ({len(self.certificate_labels)}):")
            for key, value in list(self.certificate_labels.items())[:5]:
                print(f"   • {key}: {value}")
            if len(self.certificate_labels) > 5:
                print(f"   • ... and {len(self.certificate_labels) - 5} more")
        
        # Cost
        print(f"\n💰 Estimated Cost: {self._calculate_certificate_cost()}")
        
        # State
        if self.certificate_exists:
            print(f"\n📊 State:")
            print(f"   ✅ Exists: {self.certificate_exists}")
            print(f"   🆔 Resource: {self.certificate_resource_name}")
            if self.certificate_status:
                print(f"   📊 Status: {self.certificate_status}")
    
    def analyze_security(self) -> Dict[str, Any]:
        """
        Analyze certificate security configuration and provide recommendations.
        
        Returns:
            Dict containing security analysis and recommendations
        """
        analysis = {
            "security_score": 0,
            "max_score": 100,
            "recommendations": [],
            "security_features": [],
            "risk_factors": []
        }
        
        # Certificate type analysis
        if self.managed_certificate:
            analysis["security_score"] += 30
            analysis["security_features"].append("Google-managed certificate with automatic renewal")
        else:
            analysis["security_score"] += 15
            analysis["recommendations"].append("Consider using Google-managed certificates for automatic renewal")
        
        # Domain validation analysis
        if self.validation_method == "DNS":
            analysis["security_score"] += 20
            analysis["security_features"].append("DNS validation (more secure)")
        else:
            analysis["security_score"] += 10
            analysis["recommendations"].append("Consider DNS validation for enhanced security")
        
        # Scope analysis
        if self.certificate_scope == "DEFAULT":
            analysis["security_score"] += 15
        elif self.certificate_scope == "EDGE_CACHE":
            analysis["security_score"] += 10
            analysis["recommendations"].append("Edge cache scope may have different security characteristics")
        
        # Domain analysis
        if self.domain_names:
            analysis["security_score"] += 15
            
            # Check for wildcards
            wildcards = [d for d in self.domain_names if d.startswith("*.")]
            if wildcards:
                analysis["security_features"].append(f"Wildcard certificates for {len(wildcards)} domains")
                if len(wildcards) > 2:
                    analysis["recommendations"].append("Consider limiting wildcard certificate scope")
            
            # Check for sensitive subdomains
            sensitive_subdomains = ["admin", "api", "secure", "internal"]
            for domain in self.domain_names:
                for subdomain in sensitive_subdomains:
                    if domain.startswith(f"{subdomain}."):
                        analysis["security_features"].append(f"Secure subdomain protection: {domain}")
        else:
            analysis["risk_factors"].append("No domains configured")
        
        # Labels analysis
        security_labels = ["security", "compliance", "audit", "encryption"]
        for label in security_labels:
            if label in self.certificate_labels:
                analysis["security_score"] += 5
                analysis["security_features"].append(f"Security label: {label}")
        
        # Environment analysis
        env_label = self.certificate_labels.get("environment", "").lower()
        if env_label == "production":
            analysis["security_score"] += 10
            analysis["security_features"].append("Production environment configuration")
        
        return analysis
    
    def analyze_performance(self) -> Dict[str, Any]:
        """
        Analyze certificate performance configuration and provide recommendations.
        
        Returns:
            Dict containing performance analysis and recommendations
        """
        analysis = {
            "performance_score": 0,
            "max_score": 100,
            "recommendations": [],
            "performance_factors": [],
            "latency_factors": []
        }
        
        # Location analysis
        if self.certificate_location == "global":
            analysis["performance_score"] += 30
            analysis["performance_factors"].append("Global scope for worldwide performance")
        else:
            analysis["performance_score"] += 20
            analysis["recommendations"].append("Consider global scope for better worldwide performance")
        
        # Scope analysis
        if self.certificate_scope == "DEFAULT":
            analysis["performance_score"] += 25
        elif self.certificate_scope == "EDGE_CACHE":
            analysis["performance_score"] += 30
            analysis["performance_factors"].append("Edge cache scope for CDN performance")
        
        # Certificate type analysis
        if self.managed_certificate:
            analysis["performance_score"] += 20
            analysis["performance_factors"].append("Google-managed certificates with optimized distribution")
        else:
            analysis["performance_score"] += 10
            analysis["recommendations"].append("Google-managed certificates may provide better performance")
        
        # Domain count analysis
        domain_count = len(self.domain_names)
        if domain_count <= 5:
            analysis["performance_score"] += 15
        elif domain_count <= 20:
            analysis["performance_score"] += 10
        else:
            analysis["performance_score"] += 5
            analysis["latency_factors"].append(f"Large number of domains ({domain_count}) may impact provisioning")
        
        # Validation method analysis
        if self.validation_method == "DNS":
            analysis["performance_score"] += 10
            analysis["performance_factors"].append("DNS validation for faster provisioning")
        
        return analysis
    
    # Utility methods for backwards compatibility
    def description_text(self, desc: str):
        """Set description - backwards compatibility"""
        return self.description(desc)
    
    def _estimate_monthly_cost(self) -> str:
        """Get estimated monthly cost for backwards compatibility"""
        return self._calculate_certificate_cost()
    
    def _get_certificate_info(self) -> Dict[str, Any]:
        """Get certificate info for backwards compatibility"""
        return self.summary()


# Convenience function for creating Certificate Manager instances
def create_certificate_manager(name: str) -> CertificateManager:
    """
    Create a new Certificate Manager instance.
    
    Args:
        name: Certificate name
        
    Returns:
        CertificateManager instance
    """
    return CertificateManager(name)


# Export the class for easy importing
__all__ = ['CertificateManager', 'create_certificate_manager']