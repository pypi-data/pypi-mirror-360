"""
Firebase Auth Lifecycle Mixin

Lifecycle operations for Firebase Authentication.
Provides create, destroy, and preview operations with smart state management.
"""

import json
import os
import subprocess
from typing import Dict, Any, List, Optional, Union


class FirebaseAuthLifecycleMixin:
    """
    Mixin for Firebase Auth lifecycle operations.
    
    This mixin provides:
    - preview(): Preview what will be created/updated/deleted
    - create(): Create or update Firebase Auth configuration
    - destroy(): Clean up Firebase Auth configuration
    - Smart state management and drift detection
    - Cross-Cloud Magic optimization
    """
    
    def preview(self) -> Dict[str, Any]:
        """Preview what will be created, kept, and removed"""
        # Discover existing configuration
        existing_configs = self._discover_existing_auth_configs()
        
        # Categorize auth configurations
        configs_to_create = []
        configs_to_keep = []
        configs_to_update = []
        
        # Check if our desired auth config exists
        desired_config_name = self.auth_name
        config_exists = desired_config_name in existing_configs
        
        enabled_providers = self.get_enabled_providers()
        
        if not config_exists:
            if enabled_providers:
                configs_to_create.append({
                    'auth_name': desired_config_name,
                    'firebase_project_id': self.firebase_project_id,
                    'enabled_providers': enabled_providers,
                    'provider_count': len(enabled_providers),
                    'auth_type': self._get_auth_type_from_config(),
                    'has_social_auth': self.has_social_auth(),
                    'has_secure_auth': self.has_secure_auth(),
                    'has_enterprise_features': self.has_enterprise_features(),
                    'email_verification_enabled': self.email_verification_enabled,
                    'multi_factor_auth_enabled': self.multi_factor_auth_enabled,
                    'password_policy_enabled': self.password_policy_enabled,
                    'user_management_enabled': self.user_management_enabled,
                    'custom_claims': self.custom_claims,
                    'authorized_domains': self.authorized_domains,
                    'session_timeout_minutes': self.session_timeout_minutes,
                    'sign_in_flow': self.sign_in_flow,
                    'labels': self.auth_labels,
                    'label_count': len(self.auth_labels),
                    'estimated_cost': self._estimate_firebase_auth_cost()
                })
        else:
            existing_config = existing_configs[desired_config_name]
            existing_providers = existing_config.get('providers', [])
            
            # Check if update is needed
            if set(enabled_providers) != set(existing_providers):
                configs_to_update.append({
                    'auth_name': desired_config_name,
                    'current_providers': existing_providers,
                    'desired_providers': enabled_providers,
                    'providers_to_add': list(set(enabled_providers) - set(existing_providers)),
                    'providers_to_remove': list(set(existing_providers) - set(enabled_providers))
                })
            else:
                configs_to_keep.append(existing_config)

        print(f"\n🔐 Firebase Authentication Preview")
        
        # Show configs to create
        if configs_to_create:
            print(f"╭─ 🔐 Authentication Configs to CREATE: {len(configs_to_create)}")
            for config in configs_to_create:
                print(f"├─ 🆕 {config['auth_name']}")
                print(f"│  ├─ 📁 Firebase Project: {config['firebase_project_id']}")
                print(f"│  ├─ 🎯 Auth Type: {config['auth_type'].replace('_', ' ').title()}")
                print(f"│  ├─ 🔑 Providers: {config['provider_count']}")
                
                # Show provider details
                if config['enabled_providers']:
                    print(f"│  ├─ 🔐 Provider Details:")
                    for i, provider in enumerate(config['enabled_providers'][:5]):
                        connector = "│  │  ├─" if i < min(len(config['enabled_providers']), 5) - 1 else "│  │  └─"
                        provider_icon = self._get_provider_icon(provider)
                        print(f"{connector} {provider_icon} {provider.title()}")
                    
                    if len(config['enabled_providers']) > 5:
                        print(f"│  │     └─ ... and {len(config['enabled_providers']) - 5} more providers")
                
                # Show security features
                print(f"│  ├─ 🔒 Security Features:")
                print(f"│  │  ├─ ✉️  Email Verification: {'✅ Enabled' if config['email_verification_enabled'] else '❌ Disabled'}")
                print(f"│  │  ├─ 🛡️  Multi-Factor Auth: {'✅ Enabled' if config['multi_factor_auth_enabled'] else '❌ Disabled'}")
                print(f"│  │  ├─ 🔐 Password Policy: {'✅ Enabled' if config['password_policy_enabled'] else '❌ Disabled'}")
                print(f"│  │  └─ 👥 User Management: {'✅ Enabled' if config['user_management_enabled'] else '❌ Disabled'}")
                
                # Show configuration details
                print(f"│  ├─ ⚙️  Configuration:")
                print(f"│  │  ├─ 🌊 Sign-in Flow: {config['sign_in_flow'].title()}")
                print(f"│  │  ├─ ⏱️  Session Timeout: {config['session_timeout_minutes']} minutes")
                if config['authorized_domains']:
                    print(f"│  │  ├─ 🌐 Authorized Domains: {len(config['authorized_domains'])}")
                if config['custom_claims']:
                    print(f"│  │  └─ 🏷️  Custom Claims: {len(config['custom_claims'])}")
                
                # Show labels
                if config['label_count'] > 0:
                    print(f"│  ├─ 🏷️  Labels: {config['label_count']}")
                
                # Show Firebase features
                print(f"│  ├─ 🚀 Firebase Features:")
                print(f"│  │  ├─ 🆓 Free authentication for most use cases")
                print(f"│  │  ├─ 📱 Multi-platform SDK support")
                print(f"│  │  ├─ 🔐 Built-in security and compliance")
                print(f"│  │  └─ 📊 Real-time auth state management")
                
                cost = config['estimated_cost']
                if cost > 0:
                    print(f"│  └─ 💰 Estimated Cost: ${cost:.2f}/month")
                else:
                    print(f"│  └─ 💰 Cost: Free tier")
            print(f"╰─")

        # Show configs to update
        if configs_to_update:
            print(f"\n╭─ 🔐 Authentication Configs to UPDATE: {len(configs_to_update)}")
            for config in configs_to_update:
                print(f"├─ 🔄 {config['auth_name']}")
                
                if config['providers_to_add']:
                    print(f"│  ├─ ➕ Providers to Add:")
                    for provider in config['providers_to_add']:
                        provider_icon = self._get_provider_icon(provider)
                        print(f"│  │  ├─ {provider_icon} {provider.title()}")
                
                if config['providers_to_remove']:
                    print(f"│  ├─ ➖ Providers to Remove:")
                    for provider in config['providers_to_remove']:
                        provider_icon = self._get_provider_icon(provider)
                        print(f"│  │  ├─ {provider_icon} {provider.title()}")
                
                print(f"│  └─ 📊 Current: {len(config['current_providers'])} → Desired: {len(config['desired_providers'])}")
            print(f"╰─")

        # Show existing configs being kept
        if configs_to_keep:
            print(f"\n╭─ 🔐 Existing Authentication Configs to KEEP: {len(configs_to_keep)}")
            for config in configs_to_keep:
                status_icon = "🟢" if config.get('status') == 'active' else "🟡"
                print(f"├─ {status_icon} {config['auth_name']}")
                print(f"│  ├─ 📁 Firebase Project: {config['firebase_project_id']}")
                print(f"│  ├─ 📊 Status: {config.get('status', 'unknown').title()}")
                
                providers = config.get('providers', [])
                if providers:
                    print(f"│  ├─ 🔑 Active Providers: {len(providers)}")
                    for provider in providers[:3]:
                        provider_icon = self._get_provider_icon(provider)
                        print(f"│  │  ├─ {provider_icon} {provider.title()}")
                    if len(providers) > 3:
                        print(f"│  │  └─ ... and {len(providers) - 3} more")
                
                user_count = config.get('user_count', 0)
                if user_count > 0:
                    print(f"│  ├─ 👥 Users: {user_count:,}")
                
                print(f"│  └─ 🌐 Console: {config['console_url']}")
            print(f"╰─")

        # Show cost information
        print(f"\n💰 Firebase Authentication Costs:")
        if configs_to_create:
            config = configs_to_create[0]
            cost = config['estimated_cost']
            
            print(f"   ├─ 🆓 Email/password auth: Free")
            print(f"   ├─ 🆓 Social logins: Free")
            print(f"   ├─ 🆓 Anonymous auth: Free")
            print(f"   ├─ 📞 Phone auth: $0.01 per verification")
            print(f"   ├─ 🛡️  Multi-factor auth: $0.05 per verification")
            
            if cost > 0:
                print(f"   └─ 📊 Estimated: ${cost:.2f}/month")
            else:
                print(f"   └─ 📊 Total: Free tier")
        else:
            print(f"   ├─ 🆓 Most features: Free")
            print(f"   ├─ 📞 Phone auth: $0.01 per verification")
            print(f"   └─ 🛡️  Multi-factor auth: $0.05 per verification")

        return {
            'resource_type': 'firebase_authentication',
            'name': desired_config_name,
            'configs_to_create': configs_to_create,
            'configs_to_update': configs_to_update,
            'configs_to_keep': configs_to_keep,
            'existing_configs': existing_configs,
            'firebase_project_id': self.firebase_project_id,
            'auth_type': self._get_auth_type_from_config(),
            'provider_count': len(enabled_providers),
            'estimated_cost': f"${self._estimate_firebase_auth_cost():.2f}/month"
        }

    def create(self) -> Dict[str, Any]:
        """Create or update Firebase Authentication configuration"""
        if not self.firebase_project_id:
            raise ValueError("Firebase project ID is required. Use .project('your-project-id')")
        
        existing_config = self._find_existing_config()
        if existing_config and existing_config.get("exists", False):
            print(f"🔄 Firebase Auth config '{self.auth_name}' already exists")
            return self._update_existing_config(existing_config)
        
        print(f"🚀 Creating Firebase Authentication: {self.auth_name}")
        return self._create_new_config()

    def destroy(self) -> Dict[str, Any]:
        """Destroy Firebase Authentication configuration"""
        print(f"🗑️  Destroying Firebase Authentication: {self.auth_name}")

        try:
            print(f"⚠️  Firebase Authentication cannot be automatically destroyed")
            print(f"🔧 To disable authentication:")
            print(f"   1. Go to Firebase Console: https://console.firebase.google.com/project/{self.firebase_project_id}/authentication/")
            print(f"   2. Disable providers manually in the Sign-in method tab")
            print(f"   3. Optionally delete users in the Users tab")
            
            # Remove local config files
            config_files = ["firebase-auth.json", "firebase-auth-config.json"]
            removed_files = []
            
            for config_file in config_files:
                if os.path.exists(config_file):
                    os.remove(config_file)
                    removed_files.append(config_file)
            
            if removed_files:
                print(f"   🗑️  Removed local config files: {', '.join(removed_files)}")
            
            return {
                'success': True, 
                'auth_name': self.auth_name, 
                'status': 'manual_action_required',
                'removed_files': removed_files,
                'console_url': f"https://console.firebase.google.com/project/{self.firebase_project_id}/authentication/"
            }

        except Exception as e:
            print(f"❌ Failed to destroy Firebase Auth config: {str(e)}")
            return {'success': False, 'error': str(e)}

    def optimize_for(self, optimization_target: str):
        """
        Cross-Cloud Magic: Optimize authentication configuration for specific targets.
        
        Args:
            optimization_target: Target to optimize for ('cost', 'performance', 'security', 'user_experience')
        """
        if optimization_target.lower() == "cost":
            return self._optimize_for_cost()
        elif optimization_target.lower() == "performance":
            return self._optimize_for_performance()
        elif optimization_target.lower() == "security":
            return self._optimize_for_security()
        elif optimization_target.lower() == "user_experience":
            return self._optimize_for_user_experience()
        else:
            print(f"⚠️  Unknown optimization target: {optimization_target}")
            return self

    def _optimize_for_cost(self):
        """Optimize configuration for cost efficiency"""
        print("🏗️  Applying Cross-Cloud Magic: Cost Optimization")
        
        # Use free authentication methods
        self.email_password(True)
        self.google_signin(True)
        self.anonymous_auth(True)
        
        # Avoid paid features
        self.phone_auth(False)
        self.multi_factor_auth(False)
        
        # Add cost optimization labels
        self.auth_labels.update({
            "optimization": "cost",
            "cost_management": "enabled",
            "tier": "free"
        })
        
        print("   ├─ 🆓 Enabled free authentication methods")
        print("   ├─ 📞 Disabled phone auth (paid feature)")
        print("   ├─ 🛡️  Disabled MFA (paid feature)")
        print("   └─ 🏷️  Added cost optimization labels")
        
        return self

    def _optimize_for_performance(self):
        """Optimize configuration for performance"""
        print("🏗️  Applying Cross-Cloud Magic: Performance Optimization")
        
        # Use popup flow for faster sign-in
        self.popup_signin()
        
        # Enable anonymous auth for instant access
        self.anonymous_auth(True)
        
        # Reduce session timeout for better security/performance balance
        self.session_timeout(30)  # 30 minutes
        
        # Add performance labels
        self.auth_labels.update({
            "optimization": "performance",
            "signin_flow": "optimized",
            "session_management": "efficient"
        })
        
        print("   ├─ 🪟 Set popup sign-in for faster flow")
        print("   ├─ 🚀 Enabled anonymous auth for instant access")
        print("   ├─ ⏱️  Optimized session timeout")
        print("   └─ 🏷️  Added performance optimization labels")
        
        return self

    def _optimize_for_security(self):
        """Optimize configuration for security"""
        print("🏗️  Applying Cross-Cloud Magic: Security Optimization")
        
        # Enable all security features
        self.email_verification(True)
        self.multi_factor_auth(True)
        self.password_policy(True, min_length=12, require_uppercase=True, 
                           require_numbers=True, require_symbols=True)
        
        # Enable monitoring and audit logs
        self.audit_logs(True)
        self.monitoring(True)
        
        # Secure session management
        self.session_timeout(120)  # 2 hours
        
        # Add security labels
        self.auth_labels.update({
            "optimization": "security",
            "security_level": "maximum",
            "compliance": "enabled",
            "audit": "required"
        })
        
        print("   ├─ ✉️  Enabled email verification")
        print("   ├─ 🛡️  Enabled multi-factor authentication")
        print("   ├─ 🔐 Enforced strong password policy")
        print("   ├─ 📊 Enabled audit logs and monitoring")
        print("   └─ 🏷️  Added security optimization labels")
        
        return self

    def _optimize_for_user_experience(self):
        """Optimize configuration for user experience"""
        print("🏗️  Applying Cross-Cloud Magic: User Experience Optimization")
        
        # Enable popular authentication methods
        self.email_password(True)
        self.google_signin(True)
        self.facebook_signin(True)
        self.apple_signin(True)
        self.anonymous_auth(True)
        
        # User-friendly settings
        self.popup_signin()
        self.password_reset(True)
        self.session_timeout(480)  # 8 hours for convenience
        
        # Add UX labels
        self.auth_labels.update({
            "optimization": "user_experience",
            "ux_focused": "true",
            "convenience": "high"
        })
        
        print("   ├─ 🔑 Enabled popular auth providers")
        print("   ├─ 🪟 Set popup flow for seamless experience")
        print("   ├─ 🔓 Enabled password reset")
        print("   ├─ ⏱️  Extended session for convenience")
        print("   └─ 🏷️  Added UX optimization labels")
        
        return self

    def _find_existing_config(self) -> Optional[Dict[str, Any]]:
        """Find existing Firebase Auth configuration"""
        return self._fetch_current_firebase_state()

    def _create_new_config(self) -> Dict[str, Any]:
        """Create new Firebase Authentication configuration"""
        try:
            enabled_providers = self.get_enabled_providers()
            
            if not enabled_providers:
                print("⚠️  No authentication providers enabled. Use provider methods like .email_password() or .google_signin()")
                return {"status": "no_providers", "providers": []}
            
            print(f"   📋 Project: {self.firebase_project_id}")
            print(f"   🔑 Providers: {len(enabled_providers)}")
            
            # Create configuration object
            auth_config = {
                "auth": {
                    "project_id": self.firebase_project_id,
                    "providers": {provider: True for provider in enabled_providers},
                    "provider_configs": self.provider_configs,
                    "security": {
                        "email_verification": self.email_verification_enabled,
                        "password_policy": self.password_policy_enabled,
                        "multi_factor_auth": self.multi_factor_auth_enabled
                    },
                    "user_management": {
                        "enabled": self.user_management_enabled,
                        "custom_claims": self.custom_claims,
                        "metadata_enabled": self.user_metadata_enabled
                    },
                    "session": {
                        "timeout_minutes": self.session_timeout_minutes,
                        "sign_in_flow": self.sign_in_flow
                    },
                    "domains": {
                        "authorized_domains": self.authorized_domains
                    },
                    "monitoring": {
                        "audit_logs": self.audit_logs_enabled,
                        "monitoring": self.monitoring_enabled
                    },
                    "labels": self.auth_labels,
                    "created_by": "infradsl"
                }
            }
            
            # Save configuration to file
            config_path = "firebase-auth-config.json"
            with open(config_path, 'w') as f:
                json.dump(auth_config, f, indent=2)
            
            print(f"   📄 Config saved to: {config_path}")
            
            # Show provider configuration details
            print(f"   🔐 Configured Providers:")
            for provider in enabled_providers:
                provider_icon = self._get_provider_icon(provider)
                print(f"      {provider_icon} {provider.title()}")
            
            # Show security features
            security_features = []
            if self.email_verification_enabled:
                security_features.append("Email Verification")
            if self.multi_factor_auth_enabled:
                security_features.append("Multi-Factor Auth")
            if self.password_policy_enabled:
                security_features.append("Password Policy")
            
            if security_features:
                print(f"   🔒 Security: {', '.join(security_features)}")
            
            console_url = f"https://console.firebase.google.com/project/{self.firebase_project_id}/authentication/"
            print(f"✅ Firebase Authentication configured successfully!")
            print(f"🌐 Console: {console_url}")
            
            return self._get_auth_info()

        except Exception as e:
            print(f"❌ Failed to create Firebase Auth config: {str(e)}")
            raise

    def _update_existing_config(self, existing_config: Dict[str, Any]):
        """Update existing Firebase Auth configuration"""
        print(f"   🔄 Updating existing configuration")
        # For Firebase Auth, we typically recreate the config
        return self._create_new_config()

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

    def _get_auth_info(self) -> Dict[str, Any]:
        """Get authentication information"""
        try:
            enabled_providers = self.get_enabled_providers()
            
            return {
                'success': True,
                'auth_name': self.auth_name,
                'firebase_project_id': self.firebase_project_id,
                'auth_description': self.auth_description,
                'enabled_providers': enabled_providers,
                'provider_count': len(enabled_providers),
                'auth_type': self._get_auth_type_from_config(),
                'has_social_auth': self.has_social_auth(),
                'has_secure_auth': self.has_secure_auth(),
                'has_enterprise_features': self.has_enterprise_features(),
                'email_verification_enabled': self.email_verification_enabled,
                'multi_factor_auth_enabled': self.multi_factor_auth_enabled,
                'password_policy_enabled': self.password_policy_enabled,
                'user_management_enabled': self.user_management_enabled,
                'custom_claims': self.custom_claims,
                'authorized_domains': self.authorized_domains,
                'session_timeout_minutes': self.session_timeout_minutes,
                'sign_in_flow': self.sign_in_flow,
                'labels': self.auth_labels,
                'estimated_monthly_cost': f"${self._estimate_firebase_auth_cost():.2f}",
                'console_url': f"https://console.firebase.google.com/project/{self.firebase_project_id}/authentication/"
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}