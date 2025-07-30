"""
Firebase Auth Complete Implementation

Complete Firebase Authentication implementation combining core functionality, 
configuration methods, and lifecycle operations into a single modular class.
Rails-like API with Cross-Cloud Magic optimization.
"""

from typing import Dict, Any, List, Optional, Union
from .firebase_auth_core import FirebaseAuthCore
from .firebase_auth_configuration import FirebaseAuthConfigurationMixin
from .firebase_auth_lifecycle import FirebaseAuthLifecycleMixin


class FirebaseAuth(FirebaseAuthCore, FirebaseAuthConfigurationMixin, FirebaseAuthLifecycleMixin):
    """
    Complete Firebase Authentication implementation.
    
    This class combines:
    - FirebaseAuthCore: Basic auth attributes and authentication
    - FirebaseAuthConfigurationMixin: Chainable configuration methods
    - FirebaseAuthLifecycleMixin: Lifecycle operations (create, destroy, preview)
    
    Features:
    - Rails-like method chaining for fluent authentication configuration
    - Smart state management and drift detection
    - Cross-Cloud Magic optimization
    - Complete provider support (email, social, phone, anonymous, custom)
    - Security features (MFA, email verification, password policies)
    - User management and custom claims
    - Enterprise features (audit logs, monitoring, compliance)
    - Common authentication patterns (simple, social, secure, enterprise)
    - Application-specific configurations (mobile, web, gaming, SaaS)
    - Environment-specific settings (development, staging, production)
    
    Example:
        # Simple authentication
        auth = FirebaseAuth("my-app-auth")
        auth.project("my-firebase-project").simple_auth()
        auth.create()
        
        # Social authentication
        auth = FirebaseAuth("social-auth")
        auth.project("my-project").social_auth()
        auth.create()
        
        # Enterprise authentication
        auth = FirebaseAuth("enterprise-auth")
        auth.project("company-project").enterprise_auth()
        auth.authorized_domains(["company.com", "app.company.com"])
        auth.create()
        
        # Custom configuration
        auth = FirebaseAuth("custom-auth")
        auth.project("my-project")
        auth.email_password().google_signin().facebook_signin()
        auth.email_verification().multi_factor_auth()
        auth.password_policy(True, min_length=12, require_uppercase=True)
        auth.custom_claims({"role": "admin", "tier": "premium"})
        auth.create()
        
        # Mobile app authentication
        auth = FirebaseAuth("mobile-auth")
        auth.project("mobile-project").mobile_app_auth()
        auth.create()
        
        # Cross-Cloud Magic optimization
        auth = FirebaseAuth("optimized-auth")
        auth.project("my-project").complete_auth()
        auth.optimize_for("security")
        auth.create()
    """
    
    def __init__(self, name: str):
        """
        Initialize Firebase Auth with auth name.
        
        Args:
            name: Authentication configuration name
        """
        # Initialize all parent classes
        FirebaseAuthCore.__init__(self, name)
        
        # Ensure proper initialization order
        self._initialize_managers()
        
    def __repr__(self) -> str:
        """String representation of Firebase Auth instance"""
        auth_type = self._get_auth_type_from_config()
        provider_count = self.get_provider_count()
        security_level = "high" if self.has_secure_auth() else "medium" if self.has_social_auth() else "basic"
        status = "configured" if provider_count > 0 else "unconfigured"
        
        return (f"FirebaseAuth(name='{self.auth_name}', "
                f"type='{auth_type}', "
                f"providers={provider_count}, "
                f"project='{self.firebase_project_id}', "
                f"security='{security_level}', "
                f"status='{status}')")
    
    def summary(self) -> Dict[str, Any]:
        """
        Get comprehensive summary of Firebase Auth configuration.
        
        Returns:
            Dict containing all configuration details
        """
        # Analyze authentication configuration
        enabled_providers = self.get_enabled_providers()
        social_providers = [p for p in enabled_providers if p in ["google", "facebook", "twitter", "github", "apple", "microsoft", "yahoo"]]
        
        # Categorize by provider types
        provider_categories = []
        if "password" in enabled_providers:
            provider_categories.append("email_password")
        if social_providers:
            provider_categories.append("social_login")
        if "phone" in enabled_providers:
            provider_categories.append("phone_auth")
        if "anonymous" in enabled_providers:
            provider_categories.append("anonymous_auth")
        if "custom" in enabled_providers:
            provider_categories.append("custom_auth")
        
        # Security features analysis
        security_features = []
        if self.email_verification_enabled:
            security_features.append("email_verification")
        if self.multi_factor_auth_enabled:
            security_features.append("multi_factor_auth")
        if self.password_policy_enabled:
            security_features.append("password_policy")
        if self.audit_logs_enabled:
            security_features.append("audit_logs")
        if self.monitoring_enabled:
            security_features.append("monitoring")
        
        # Enterprise features analysis
        enterprise_features = []
        if self.user_management_enabled:
            enterprise_features.append("user_management")
        if self.custom_claims:
            enterprise_features.append("custom_claims")
        if self.authorized_domains:
            enterprise_features.append("domain_restrictions")
        if self.audit_logs_enabled and self.monitoring_enabled:
            enterprise_features.append("compliance_ready")
        
        summary = {
            "auth_name": self.auth_name,
            "firebase_project_id": self.firebase_project_id,
            "auth_description": self.auth_description,
            "auth_type": self._get_auth_type_from_config(),
            "provider_categories": provider_categories,
            
            # Providers
            "enabled_providers": enabled_providers,
            "provider_count": len(enabled_providers),
            "social_providers": social_providers,
            "provider_configs": self.provider_configs,
            
            # Security
            "security_features": security_features,
            "email_verification_enabled": self.email_verification_enabled,
            "multi_factor_auth_enabled": self.multi_factor_auth_enabled,
            "password_policy_enabled": self.password_policy_enabled,
            "has_secure_auth": self.has_secure_auth(),
            
            # User management
            "user_management_enabled": self.user_management_enabled,
            "custom_claims": self.custom_claims,
            "user_metadata_enabled": self.user_metadata_enabled,
            
            # Session and flow
            "sign_in_flow": self.sign_in_flow,
            "session_timeout_minutes": self.session_timeout_minutes,
            "password_reset_enabled": self.password_reset_enabled,
            
            # Domain and security
            "authorized_domains": self.authorized_domains,
            "domain_count": len(self.authorized_domains),
            
            # Enterprise features
            "enterprise_features": enterprise_features,
            "has_enterprise_features": self.has_enterprise_features(),
            "audit_logs_enabled": self.audit_logs_enabled,
            "monitoring_enabled": self.monitoring_enabled,
            
            # Labels and metadata
            "labels": self.auth_labels,
            "label_count": len(self.auth_labels),
            "annotations": self.auth_annotations,
            
            # State
            "state": {
                "exists": self.auth_exists,
                "created": self.auth_created,
                "status": self.auth_status,
                "deployment_status": self.deployment_status
            },
            
            # Cost
            "estimated_monthly_cost": f"${self._estimate_firebase_auth_cost():.2f}",
            "is_free_tier": self._estimate_firebase_auth_cost() == 0.0
        }
        
        return summary
    
    def display_config(self):
        """Display current configuration in human-readable format"""
        print(f"\n🔐 Firebase Authentication Configuration: {self.auth_name}")
        print(f"   📁 Firebase Project: {self.firebase_project_id}")
        print(f"   📝 Description: {self.auth_description}")
        print(f"   🎯 Auth Type: {self._get_auth_type_from_config().replace('_', ' ').title()}")
        
        # Providers
        enabled_providers = self.get_enabled_providers()
        if enabled_providers:
            print(f"\n🔑 Authentication Providers ({len(enabled_providers)}):")
            for provider in enabled_providers:
                provider_icon = self._get_provider_icon(provider)
                print(f"   {provider_icon} {provider.title()}")
                
                # Show provider config if available
                if provider in self.provider_configs:
                    config = self.provider_configs[provider]
                    if isinstance(config, dict):
                        for key, value in config.items():
                            if "secret" not in key.lower() and "password" not in key.lower():
                                print(f"      └─ {key}: {value}")
        else:
            print(f"\n🔑 Authentication Providers: None configured")
        
        # Security features
        print(f"\n🔒 Security Configuration:")
        print(f"   ✉️  Email Verification: {'✅ Enabled' if self.email_verification_enabled else '❌ Disabled'}")
        print(f"   🛡️  Multi-Factor Auth: {'✅ Enabled' if self.multi_factor_auth_enabled else '❌ Disabled'}")
        print(f"   🔐 Password Policy: {'✅ Enabled' if self.password_policy_enabled else '❌ Disabled'}")
        print(f"   🔓 Password Reset: {'✅ Enabled' if self.password_reset_enabled else '❌ Disabled'}")
        
        # Password policy details
        if self.password_policy_enabled and "password_policy" in self.provider_configs:
            policy = self.provider_configs["password_policy"]
            print(f"      ├─ Min Length: {policy.get('min_length', 6)} characters")
            if policy.get('require_uppercase'):
                print(f"      ├─ Requires: Uppercase letters")
            if policy.get('require_numbers'):
                print(f"      ├─ Requires: Numbers")
            if policy.get('require_symbols'):
                print(f"      └─ Requires: Special symbols")
        
        # User management
        print(f"\n👥 User Management:")
        print(f"   🔧 User Management: {'✅ Enabled' if self.user_management_enabled else '❌ Disabled'}")
        print(f"   📊 User Metadata: {'✅ Enabled' if self.user_metadata_enabled else '❌ Disabled'}")
        
        if self.custom_claims:
            print(f"   🏷️  Custom Claims ({len(self.custom_claims)}):")
            for key, value in list(self.custom_claims.items())[:5]:
                print(f"      ├─ {key}: {value}")
            if len(self.custom_claims) > 5:
                print(f"      └─ ... and {len(self.custom_claims) - 5} more")
        
        # Session and flow configuration
        print(f"\n⚙️  Session Configuration:")
        print(f"   🌊 Sign-in Flow: {self.sign_in_flow.title()}")
        print(f"   ⏱️  Session Timeout: {self.session_timeout_minutes} minutes")
        
        # Domain restrictions
        if self.authorized_domains:
            print(f"\n🌐 Authorized Domains ({len(self.authorized_domains)}):")
            for domain in self.authorized_domains[:5]:
                print(f"   🌍 {domain}")
            if len(self.authorized_domains) > 5:
                print(f"   └─ ... and {len(self.authorized_domains) - 5} more")
        
        # Enterprise features
        if self.has_enterprise_features():
            print(f"\n🏢 Enterprise Features:")
            print(f"   📊 Audit Logs: {'✅ Enabled' if self.audit_logs_enabled else '❌ Disabled'}")
            print(f"   📈 Monitoring: {'✅ Enabled' if self.monitoring_enabled else '❌ Disabled'}")
        
        # Labels
        if self.auth_labels:
            print(f"\n🏷️  Labels ({len(self.auth_labels)}):")
            for key, value in list(self.auth_labels.items())[:5]:
                print(f"   • {key}: {value}")
            if len(self.auth_labels) > 5:
                print(f"   • ... and {len(self.auth_labels) - 5} more")
        
        # Cost
        cost = self._estimate_firebase_auth_cost()
        if cost > 0:
            print(f"\n💰 Estimated Cost: ${cost:.2f}/month")
        else:
            print(f"\n💰 Cost: Free tier")
        
        # Console link
        if self.firebase_project_id:
            print(f"\n🌐 Firebase Console:")
            print(f"   🔗 {f'https://console.firebase.google.com/project/{self.firebase_project_id}/authentication/'}")
    
    def analyze_security(self) -> Dict[str, Any]:
        """
        Analyze Firebase Auth security configuration and provide recommendations.
        
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
        
        # Provider security analysis
        enabled_providers = self.get_enabled_providers()
        if "password" in enabled_providers:
            analysis["security_score"] += 20
            analysis["security_features"].append("Email/password authentication")
        
        if self.has_social_auth():
            analysis["security_score"] += 15
            analysis["security_features"].append("Social authentication providers")
        
        if "anonymous" in enabled_providers:
            analysis["risk_factors"].append("Anonymous authentication enabled")
            analysis["recommendations"].append("Monitor anonymous user activity")
        
        # Security features analysis
        if self.email_verification_enabled:
            analysis["security_score"] += 20
            analysis["security_features"].append("Email verification required")
        else:
            analysis["recommendations"].append("Enable email verification")
        
        if self.multi_factor_auth_enabled:
            analysis["security_score"] += 20
            analysis["security_features"].append("Multi-factor authentication")
        else:
            analysis["recommendations"].append("Enable multi-factor authentication")
        
        if self.password_policy_enabled:
            analysis["security_score"] += 15
            analysis["security_features"].append("Password policy enforcement")
            
            # Check password policy strength
            if "password_policy" in self.provider_configs:
                policy = self.provider_configs["password_policy"]
                if policy.get("min_length", 0) >= 12:
                    analysis["security_score"] += 5
                if policy.get("require_uppercase") and policy.get("require_numbers"):
                    analysis["security_score"] += 5
        else:
            analysis["recommendations"].append("Enable password policy with strong requirements")
        
        # Domain security
        if self.authorized_domains:
            analysis["security_score"] += 10
            analysis["security_features"].append("Domain restrictions configured")
        else:
            analysis["recommendations"].append("Configure authorized domains")
        
        # Monitoring and audit
        if self.audit_logs_enabled:
            analysis["security_score"] += 5
            analysis["security_features"].append("Audit logging enabled")
        
        if self.monitoring_enabled:
            analysis["security_score"] += 5
            analysis["security_features"].append("Authentication monitoring")
        
        return analysis
    
    def analyze_user_experience(self) -> Dict[str, Any]:
        """
        Analyze Firebase Auth user experience and provide recommendations.
        
        Returns:
            Dict containing UX analysis and recommendations
        """
        analysis = {
            "ux_score": 0,
            "max_score": 100,
            "recommendations": [],
            "ux_features": [],
            "friction_points": []
        }
        
        # Provider variety analysis
        enabled_providers = self.get_enabled_providers()
        provider_count = len(enabled_providers)
        
        if provider_count >= 3:
            analysis["ux_score"] += 25
            analysis["ux_features"].append("Multiple authentication options")
        elif provider_count >= 2:
            analysis["ux_score"] += 20
            analysis["ux_features"].append("Good authentication variety")
        else:
            analysis["recommendations"].append("Offer multiple authentication options")
        
        # Social auth analysis
        if self.has_social_auth():
            analysis["ux_score"] += 20
            analysis["ux_features"].append("Social login for convenience")
        else:
            analysis["recommendations"].append("Add social login options")
        
        # Anonymous auth for instant access
        if "anonymous" in enabled_providers:
            analysis["ux_score"] += 15
            analysis["ux_features"].append("Anonymous access for instant use")
        else:
            analysis["recommendations"].append("Consider anonymous auth for immediate access")
        
        # Sign-in flow analysis
        if self.sign_in_flow == "popup":
            analysis["ux_score"] += 15
            analysis["ux_features"].append("Popup flow for seamless experience")
        else:
            analysis["recommendations"].append("Consider popup flow for better UX")
        
        # Password reset
        if self.password_reset_enabled:
            analysis["ux_score"] += 10
            analysis["ux_features"].append("Password reset available")
        
        # Email verification friction
        if self.email_verification_enabled:
            analysis["friction_points"].append("Email verification required")
            analysis["recommendations"].append("Consider progressive verification")
        
        # Session timeout analysis
        if self.session_timeout_minutes >= 480:  # 8 hours
            analysis["ux_score"] += 10
            analysis["ux_features"].append("Long session for convenience")
        elif self.session_timeout_minutes <= 30:
            analysis["friction_points"].append("Short session timeout")
        
        # MFA friction
        if self.multi_factor_auth_enabled:
            analysis["friction_points"].append("Multi-factor authentication required")
        
        return analysis
    
    # Utility methods for backwards compatibility
    def _get_provider_icon(self, provider: str) -> str:
        """Get icon for authentication provider"""
        icons = {
            "password": "✉️",
            "google": "🔵",
            "facebook": "🔵", 
            "twitter": "🔵",
            "github": "⚫",
            "apple": "⚫",
            "microsoft": "🔵",
            "yahoo": "🟣",
            "phone": "📞",
            "anonymous": "👤",
            "custom": "🔧"
        }
        return icons.get(provider, "🔑")
    
    def get_status(self) -> Dict[str, Any]:
        """Get authentication status for backwards compatibility"""
        return {
            "auth_name": self.auth_name,
            "firebase_project_id": self.firebase_project_id,
            "auth_type": self._get_auth_type_from_config(),
            "enabled_providers": self.get_enabled_providers(),
            "provider_count": self.get_provider_count(),
            "has_social_auth": self.has_social_auth(),
            "has_secure_auth": self.has_secure_auth(),
            "has_enterprise_features": self.has_enterprise_features(),
            "estimated_cost": f"${self._estimate_firebase_auth_cost():.2f}/month"
        }


# Convenience function for creating Firebase Auth instances
def create_firebase_auth(name: str) -> FirebaseAuth:
    """
    Create a new Firebase Auth instance.
    
    Args:
        name: Authentication configuration name
        
    Returns:
        FirebaseAuth instance
    """
    return FirebaseAuth(name)


# Export the class for easy importing
__all__ = ['FirebaseAuth', 'create_firebase_auth']