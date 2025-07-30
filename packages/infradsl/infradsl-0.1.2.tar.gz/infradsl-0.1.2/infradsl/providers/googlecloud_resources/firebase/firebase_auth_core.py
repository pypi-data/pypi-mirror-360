"""
Firebase Auth Core Implementation

Core attributes and authentication for Firebase Authentication.
Provides the foundation for the modular authentication system.
"""

from typing import Dict, Any, List, Optional, Union
from ..base_resource import BaseGcpResource


class FirebaseAuthCore(BaseGcpResource):
    """
    Core class for Firebase Authentication functionality.
    
    This class provides:
    - Basic Firebase Auth attributes and configuration
    - Authentication setup
    - Common utilities for auth operations
    - Validation and state tracking foundations
    """
    
    def __init__(self, name: str):
        """Initialize Firebase Auth core with auth name"""
        super().__init__(name)
        
        # Core auth attributes
        self.auth_name = name
        self.firebase_project_id = None
        self.auth_description = f"Firebase Authentication for {name}"
        
        # Authentication providers configuration
        self.providers = {
            "password": False,
            "google": False,
            "facebook": False,
            "twitter": False,
            "github": False,
            "apple": False,
            "microsoft": False,
            "yahoo": False,
            "phone": False,
            "anonymous": False,
            "custom": False
        }
        
        # Provider configurations
        self.provider_configs = {}
        
        # User management configuration
        self.user_management_enabled = False
        self.custom_claims = {}
        self.user_metadata_enabled = True
        
        # Security configuration
        self.email_verification_enabled = True
        self.password_policy_enabled = True
        self.multi_factor_auth_enabled = False
        self.authorized_domains = []
        
        # Sign-in configuration
        self.sign_in_flow = "popup"  # popup or redirect
        self.session_timeout_minutes = 60
        self.password_reset_enabled = True
        
        # Audit and monitoring
        self.audit_logs_enabled = False
        self.monitoring_enabled = False
        
        # Labels and metadata
        self.auth_labels = {}
        self.auth_annotations = {}
        
        # State tracking
        self.auth_exists = False
        self.auth_created = False
        self.auth_status = None
        self.deployment_status = None
        
        # Client references
        self.firebase_client = None
        self.firebase_admin = None
        
        # Estimated costs
        self.estimated_monthly_cost = "$0.00/month"  # Firebase Auth is free
        
    def _initialize_managers(self):
        """Initialize Firebase Auth-specific managers"""
        self.firebase_client = None
        self.firebase_admin = None
        
    def _post_authentication_setup(self):
        """Setup managers after authentication"""
        try:
            # Firebase Auth doesn't require GCP authentication
            # It uses Firebase project ID and config
            
            # Set project context if available
            if not self.firebase_project_id and hasattr(self.gcp_client, 'project_id'):
                self.firebase_project_id = self.gcp_client.project_id
                
        except Exception as e:
            print(f"⚠️  Firebase Auth setup note: {str(e)}")
            
    def _is_valid_project_id(self, project_id: str) -> bool:
        """Check if Firebase project ID is valid"""
        import re
        # Firebase project IDs must contain only lowercase letters, numbers, dashes
        pattern = r'^[a-z][a-z0-9-]*[a-z0-9]$'
        return bool(re.match(pattern, project_id)) and 4 <= len(project_id) <= 30
        
    def _is_valid_provider(self, provider: str) -> bool:
        """Check if auth provider is valid"""
        return provider in self.providers
        
    def _is_valid_email(self, email: str) -> bool:
        """Check if email format is valid"""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
        
    def _validate_auth_config(self, config: Dict[str, Any]) -> bool:
        """Validate authentication configuration"""
        required_fields = ["firebase_project_id"]
        
        for field in required_fields:
            if field not in config or not config[field]:
                return False
                
        # Validate project ID format
        if not self._is_valid_project_id(config["firebase_project_id"]):
            return False
            
        # Validate providers
        providers = config.get("providers", {})
        for provider in providers:
            if not self._is_valid_provider(provider):
                return False
                
        return True
        
    def _get_auth_type_from_config(self) -> str:
        """Determine auth type from configuration"""
        enabled_providers = [p for p, enabled in self.providers.items() if enabled]
        
        if not enabled_providers:
            return "no_auth"
        elif len(enabled_providers) == 1:
            if "password" in enabled_providers:
                return "email_password_only"
            elif "anonymous" in enabled_providers:
                return "anonymous_only"
            elif "google" in enabled_providers:
                return "google_only"
            else:
                return f"{enabled_providers[0]}_only"
        elif "password" in enabled_providers and "google" in enabled_providers:
            return "email_google_auth"
        elif "anonymous" in enabled_providers and len(enabled_providers) > 1:
            return "multi_auth_with_anonymous"
        else:
            return "multi_provider_auth"
            
    def _estimate_firebase_auth_cost(self) -> float:
        """Estimate monthly cost for Firebase Auth usage"""
        # Firebase Authentication is free for most use cases
        # Only charged for phone auth and advanced features
        
        cost = 0.0
        
        # Phone authentication: $0.01 per verification
        if self.providers.get("phone", False):
            # Estimate 1000 phone verifications per month
            estimated_phone_verifications = 1000
            cost += estimated_phone_verifications * 0.01
        
        # Multi-factor auth: $0.05 per verification
        if self.multi_factor_auth_enabled:
            # Estimate 500 MFA verifications per month
            estimated_mfa_verifications = 500
            cost += estimated_mfa_verifications * 0.05
        
        return cost
        
    def _fetch_current_firebase_state(self) -> Dict[str, Any]:
        """Fetch current state of Firebase Auth from Firebase Console"""
        try:
            import subprocess
            import json
            import os
            
            if not self.firebase_project_id:
                return {
                    "exists": False,
                    "auth_name": self.auth_name,
                    "error": "No Firebase project ID configured"
                }
            
            # Try to get current auth config using Firebase CLI
            try:
                cmd = ["firebase", "auth:export", "--project", self.firebase_project_id, "--format", "json"]
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
                
                if result.returncode == 0 and result.stdout:
                    auth_data = json.loads(result.stdout)
                    
                    current_state = {
                        "exists": True,
                        "auth_name": self.auth_name,
                        "firebase_project_id": self.firebase_project_id,
                        "providers": self._extract_enabled_providers(auth_data),
                        "user_count": len(auth_data.get("users", [])),
                        "config": auth_data.get("config", {}),
                        "status": "active",
                        "console_url": f"https://console.firebase.google.com/project/{self.firebase_project_id}/authentication/"
                    }
                    
                    return current_state
                    
            except (subprocess.TimeoutExpired, json.JSONDecodeError, FileNotFoundError):
                # Firebase CLI not available - check for local config
                pass
            
            # Check for local Firebase config file
            config_files = ["firebase-auth.json", "firebase.json", ".firebaserc"]
            for config_file in config_files:
                if os.path.exists(config_file):
                    try:
                        with open(config_file, 'r') as f:
                            config_data = json.load(f)
                            
                        return {
                            "exists": True,
                            "auth_name": self.auth_name,
                            "firebase_project_id": self.firebase_project_id,
                            "config_file": config_file,
                            "local_config": config_data,
                            "status": "local_config",
                            "console_url": f"https://console.firebase.google.com/project/{self.firebase_project_id}/authentication/"
                        }
                    except json.JSONDecodeError:
                        continue
            
            return {
                "exists": False,
                "auth_name": self.auth_name,
                "firebase_project_id": self.firebase_project_id
            }
            
        except Exception as e:
            return {
                "exists": False,
                "auth_name": self.auth_name,
                "firebase_project_id": self.firebase_project_id,
                "error": str(e)
            }
            
    def _extract_enabled_providers(self, auth_data: Dict[str, Any]) -> List[str]:
        """Extract enabled providers from Firebase auth data"""
        enabled_providers = []
        
        # Extract from config if available
        config = auth_data.get("config", {})
        if "signIn" in config:
            sign_in_config = config["signIn"]
            if sign_in_config.get("email", {}).get("enabled", False):
                enabled_providers.append("password")
            if sign_in_config.get("anonymous", {}).get("enabled", False):
                enabled_providers.append("anonymous")
            if sign_in_config.get("phone", {}).get("enabled", False):
                enabled_providers.append("phone")
                
            # Check OAuth providers
            oauth_providers = sign_in_config.get("oauth", [])
            for provider in oauth_providers:
                provider_id = provider.get("providerId", "")
                if "google" in provider_id:
                    enabled_providers.append("google")
                elif "facebook" in provider_id:
                    enabled_providers.append("facebook")
                elif "twitter" in provider_id:
                    enabled_providers.append("twitter")
                elif "github" in provider_id:
                    enabled_providers.append("github")
        
        return enabled_providers
        
    def _discover_existing_auth_configs(self) -> Dict[str, Dict[str, Any]]:
        """Discover all existing Firebase Auth configurations"""
        existing_configs = {}
        
        if not self.firebase_project_id:
            return existing_configs
            
        try:
            current_state = self._fetch_current_firebase_state()
            if current_state.get("exists", False):
                existing_configs[self.auth_name] = current_state
                
        except Exception as e:
            print(f"⚠️  Failed to discover existing auth configs: {str(e)}")
            
        return existing_configs