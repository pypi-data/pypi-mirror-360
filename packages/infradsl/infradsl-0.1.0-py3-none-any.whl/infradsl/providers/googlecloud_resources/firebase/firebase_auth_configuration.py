"""
Firebase Auth Configuration Mixin

Chainable configuration methods for Firebase Authentication.
Provides Rails-like method chaining for fluent authentication configuration.
"""

from typing import Dict, Any, List, Optional, Union


class FirebaseAuthConfigurationMixin:
    """
    Mixin for Firebase Auth configuration methods.
    
    This mixin provides chainable configuration methods for:
    - Authentication providers (email, social, phone, anonymous)
    - Security settings (MFA, email verification, password policies)
    - User management and custom claims
    - Sign-in flow configuration
    - Domain and session management
    - Common authentication patterns
    """
    
    def project(self, project_id: str):
        """Set Firebase project ID - Rails convenience"""
        if not self._is_valid_project_id(project_id):
            print(f"⚠️  Warning: Invalid Firebase project ID '{project_id}'")
        self.firebase_project_id = project_id
        return self
        
    def description(self, description: str):
        """Set authentication description"""
        self.auth_description = description
        return self
    
    # Core authentication providers
    def email_password(self, enabled: bool = True):
        """Enable/disable email and password authentication - chainable"""
        self.providers["password"] = enabled
        return self
        
    def email_auth(self, enabled: bool = True):
        """Alias for email_password - Rails convenience"""
        return self.email_password(enabled)
        
    def anonymous_auth(self, enabled: bool = True):
        """Enable/disable anonymous authentication - chainable"""
        self.providers["anonymous"] = enabled
        return self
        
    def phone_auth(self, enabled: bool = True):
        """Enable/disable phone number authentication - chainable"""
        self.providers["phone"] = enabled
        return self
        
    def custom_auth(self, enabled: bool = True):
        """Enable/disable custom authentication - chainable"""
        self.providers["custom"] = enabled
        return self
    
    # Social authentication providers
    def google_signin(self, enabled: bool = True, client_id: str = None, client_secret: str = None):
        """Enable Google Sign-In - chainable"""
        self.providers["google"] = enabled
        if enabled and (client_id or client_secret):
            self.provider_configs["google"] = {
                "client_id": client_id,
                "client_secret": client_secret
            }
        return self
        
    def facebook_signin(self, enabled: bool = True, app_id: str = None, app_secret: str = None):
        """Enable Facebook Sign-In - chainable"""
        self.providers["facebook"] = enabled
        if enabled and (app_id or app_secret):
            self.provider_configs["facebook"] = {
                "app_id": app_id,
                "app_secret": app_secret
            }
        return self
        
    def twitter_signin(self, enabled: bool = True, api_key: str = None, api_secret: str = None):
        """Enable Twitter Sign-In - chainable"""
        self.providers["twitter"] = enabled
        if enabled and (api_key or api_secret):
            self.provider_configs["twitter"] = {
                "api_key": api_key,
                "api_secret": api_secret
            }
        return self
        
    def github_signin(self, enabled: bool = True, client_id: str = None, client_secret: str = None):
        """Enable GitHub Sign-In - chainable"""
        self.providers["github"] = enabled
        if enabled and (client_id or client_secret):
            self.provider_configs["github"] = {
                "client_id": client_id,
                "client_secret": client_secret
            }
        return self
        
    def apple_signin(self, enabled: bool = True, service_id: str = None, key_id: str = None):
        """Enable Apple Sign-In - chainable"""
        self.providers["apple"] = enabled
        if enabled and (service_id or key_id):
            self.provider_configs["apple"] = {
                "service_id": service_id,
                "key_id": key_id
            }
        return self
        
    def microsoft_signin(self, enabled: bool = True, client_id: str = None, client_secret: str = None):
        """Enable Microsoft Sign-In - chainable"""
        self.providers["microsoft"] = enabled
        if enabled and (client_id or client_secret):
            self.provider_configs["microsoft"] = {
                "client_id": client_id,
                "client_secret": client_secret
            }
        return self
        
    def yahoo_signin(self, enabled: bool = True, client_id: str = None, client_secret: str = None):
        """Enable Yahoo Sign-In - chainable"""
        self.providers["yahoo"] = enabled
        if enabled and (client_id or client_secret):
            self.provider_configs["yahoo"] = {
                "client_id": client_id,
                "client_secret": client_secret
            }
        return self
    
    # Security configuration
    def email_verification(self, enabled: bool = True):
        """Enable/disable email verification - chainable"""
        self.email_verification_enabled = enabled
        return self
        
    def password_policy(self, enabled: bool = True, min_length: int = 6, require_uppercase: bool = False, 
                       require_lowercase: bool = False, require_numbers: bool = False, 
                       require_symbols: bool = False):
        """Configure password policy - chainable"""
        self.password_policy_enabled = enabled
        if enabled:
            self.provider_configs["password_policy"] = {
                "min_length": min_length,
                "require_uppercase": require_uppercase,
                "require_lowercase": require_lowercase,
                "require_numbers": require_numbers,
                "require_symbols": require_symbols
            }
        return self
        
    def multi_factor_auth(self, enabled: bool = True):
        """Enable/disable multi-factor authentication - chainable"""
        self.multi_factor_auth_enabled = enabled
        return self
        
    def mfa(self, enabled: bool = True):
        """Alias for multi_factor_auth - Rails convenience"""
        return self.multi_factor_auth(enabled)
    
    # User management
    def user_management(self, enabled: bool = True):
        """Enable/disable user management features - chainable"""
        self.user_management_enabled = enabled
        return self
        
    def custom_claims(self, claims: Dict[str, Any]):
        """Set custom claims for users - chainable"""
        self.custom_claims.update(claims)
        return self
        
    def custom_claim(self, key: str, value: Any):
        """Add individual custom claim - Rails convenience"""
        self.custom_claims[key] = value
        return self
        
    def user_metadata(self, enabled: bool = True):
        """Enable/disable user metadata collection - chainable"""
        self.user_metadata_enabled = enabled
        return self
    
    # Sign-in configuration
    def sign_in_flow(self, flow: str = "popup"):
        """Set sign-in flow (popup or redirect) - chainable"""
        valid_flows = ["popup", "redirect"]
        if flow not in valid_flows:
            print(f"⚠️  Warning: Invalid sign-in flow '{flow}'. Valid: {valid_flows}")
        self.sign_in_flow = flow
        return self
        
    def popup_signin(self):
        """Use popup sign-in flow - Rails convenience"""
        return self.sign_in_flow("popup")
        
    def redirect_signin(self):
        """Use redirect sign-in flow - Rails convenience"""
        return self.sign_in_flow("redirect")
        
    def session_timeout(self, minutes: int = 60):
        """Set session timeout in minutes - chainable"""
        self.session_timeout_minutes = minutes
        return self
        
    def password_reset(self, enabled: bool = True):
        """Enable/disable password reset functionality - chainable"""
        self.password_reset_enabled = enabled
        return self
    
    # Domain and security configuration
    def authorized_domains(self, domains: List[str]):
        """Set authorized domains for authentication - chainable"""
        self.authorized_domains = domains
        return self
        
    def authorized_domain(self, domain: str):
        """Add individual authorized domain - Rails convenience"""
        if domain not in self.authorized_domains:
            self.authorized_domains.append(domain)
        return self
        
    def audit_logs(self, enabled: bool = True):
        """Enable/disable audit logging - chainable"""
        self.audit_logs_enabled = enabled
        return self
        
    def monitoring(self, enabled: bool = True):
        """Enable/disable authentication monitoring - chainable"""
        self.monitoring_enabled = enabled
        return self
    
    # Labels and metadata
    def labels(self, labels: Dict[str, str]):
        """Add labels to the authentication config"""
        self.auth_labels.update(labels)
        return self
        
    def label(self, key: str, value: str):
        """Add individual label - Rails convenience"""
        self.auth_labels[key] = value
        return self
        
    def annotations(self, annotations: Dict[str, str]):
        """Add annotations to the authentication config"""
        self.auth_annotations.update(annotations)
        return self
        
    def annotation(self, key: str, value: str):
        """Add individual annotation - Rails convenience"""
        self.auth_annotations[key] = value
        return self
    
    # Common authentication patterns
    def simple_auth(self):
        """Rails convenience: Simple email/password authentication"""
        return (self.email_password(True)
                .email_verification(True)
                .password_reset(True)
                .label("type", "simple")
                .label("complexity", "basic"))
                
    def social_auth(self):
        """Rails convenience: Social authentication only"""
        return (self.google_signin(True)
                .facebook_signin(True)
                .anonymous_auth(True)
                .label("type", "social")
                .label("complexity", "medium"))
                
    def complete_auth(self):
        """Rails convenience: Complete authentication with all providers"""
        return (self.email_password(True)
                .google_signin(True)
                .facebook_signin(True)
                .phone_auth(True)
                .anonymous_auth(True)
                .email_verification(True)
                .password_reset(True)
                .label("type", "complete")
                .label("complexity", "full"))
                
    def secure_auth(self):
        """Rails convenience: High-security authentication"""
        return (self.email_password(True)
                .email_verification(True)
                .multi_factor_auth(True)
                .password_policy(True, min_length=8, require_uppercase=True, 
                               require_numbers=True, require_symbols=True)
                .audit_logs(True)
                .monitoring(True)
                .label("type", "secure")
                .label("security", "high"))
                
    def enterprise_auth(self):
        """Rails convenience: Enterprise authentication"""
        return (self.complete_auth()
                .secure_auth()
                .user_management(True)
                .custom_claims({"enterprise": True})
                .label("tier", "enterprise"))
    
    # Application-specific patterns
    def mobile_app_auth(self):
        """Rails convenience: Mobile app authentication"""
        return (self.email_password(True)
                .google_signin(True)
                .apple_signin(True)
                .phone_auth(True)
                .anonymous_auth(True)
                .popup_signin()
                .label("platform", "mobile"))
                
    def web_app_auth(self):
        """Rails convenience: Web application authentication"""
        return (self.email_password(True)
                .google_signin(True)
                .facebook_signin(True)
                .redirect_signin()
                .email_verification(True)
                .label("platform", "web"))
                
    def game_auth(self):
        """Rails convenience: Gaming application authentication"""
        return (self.anonymous_auth(True)
                .google_signin(True)
                .apple_signin(True)
                .custom_claims({"player": True})
                .label("industry", "gaming"))
                
    def saas_auth(self):
        """Rails convenience: SaaS application authentication"""
        return (self.enterprise_auth()
                .authorized_domains(["company.com"])
                .session_timeout(480)  # 8 hours
                .label("industry", "saas"))
    
    # Environment-specific configurations
    def development(self):
        """Configure for development environment - Rails convention"""
        return (self.email_password(True)
                .anonymous_auth(True)
                .email_verification(False)
                .password_policy(False)
                .label("environment", "development"))
                
    def staging(self):
        """Configure for staging environment - Rails convention"""
        return (self.simple_auth()
                .google_signin(True)
                .label("environment", "staging"))
                
    def production(self):
        """Configure for production environment - Rails convention"""
        return (self.secure_auth()
                .social_auth()
                .user_management(True)
                .audit_logs(True)
                .monitoring(True)
                .label("environment", "production"))
    
    # Utility methods
    def clear_providers(self):
        """Clear all authentication providers"""
        for provider in self.providers:
            self.providers[provider] = False
        self.provider_configs = {}
        return self
        
    def clear_labels(self):
        """Clear all labels"""
        self.auth_labels = {}
        return self
        
    def get_enabled_providers(self) -> List[str]:
        """Get list of enabled authentication providers"""
        return [provider for provider, enabled in self.providers.items() if enabled]
        
    def get_provider_count(self) -> int:
        """Get the number of enabled providers"""
        return len(self.get_enabled_providers())
        
    def has_social_auth(self) -> bool:
        """Check if any social authentication providers are enabled"""
        social_providers = ["google", "facebook", "twitter", "github", "apple", "microsoft", "yahoo"]
        return any(self.providers.get(provider, False) for provider in social_providers)
        
    def has_secure_auth(self) -> bool:
        """Check if secure authentication features are enabled"""
        return (self.email_verification_enabled and 
                self.password_policy_enabled and 
                self.multi_factor_auth_enabled)
    
    def has_enterprise_features(self) -> bool:
        """Check if enterprise features are enabled"""
        return (self.user_management_enabled and 
                self.audit_logs_enabled and 
                self.monitoring_enabled and 
                bool(self.custom_claims))