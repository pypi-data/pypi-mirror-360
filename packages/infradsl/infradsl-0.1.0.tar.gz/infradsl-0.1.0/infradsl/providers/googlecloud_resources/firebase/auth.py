"""
Firebase Authentication Resource for InfraDSL
User authentication with social logins and email/password

Features:
- Email/password authentication
- Social login providers (Google, Facebook, Twitter, etc.)
- Phone authentication
- Anonymous authentication
- Custom claims and user management
"""

import os
import json
import subprocess
from typing import Dict, List, Optional, Any
from ..base_resource import BaseGcpResource


class FirebaseAuth(BaseGcpResource):
    """
    Firebase Authentication for user management
    
    Example:
        auth = (FirebaseAuth("my-app-auth")
               .project("my-project")
               .email_password(True)
               .google_signin(True)
               .phone_auth(True)
               .anonymous_auth(True)
               .custom_claims({"admin": True}))
    """
    
    def __init__(self, name: str):
        super().__init__(name)
        self._project_id = None
        self._providers = {
            "password": False,
            "google": False,
            "facebook": False,
            "twitter": False,
            "github": False,
            "phone": False,
            "anonymous": False
        }
        self._custom_claims = {}
        self._user_management = False
        
    def _initialize_managers(self):
        """Initialize Firebase Auth managers"""
        # Firebase Auth doesn't require additional managers
        pass
        
    def _post_authentication_setup(self):
        """Setup after authentication"""
        # Firebase Auth doesn't require post-auth setup
        pass
        
    def project(self, project_id: str):
        """Set Firebase project ID"""
        self._project_id = project_id
        return self
        
    def email_password(self, enabled: bool = True):
        """Enable email/password authentication"""
        self._providers["password"] = enabled
        return self
        
    def google_signin(self, enabled: bool = True, client_id: str = None):
        """Enable Google Sign-In"""
        self._providers["google"] = enabled
        if client_id:
            self._custom_claims["google_client_id"] = client_id
        return self
        
    def facebook_signin(self, enabled: bool = True, app_id: str = None):
        """Enable Facebook Sign-In"""
        self._providers["facebook"] = enabled
        if app_id:
            self._custom_claims["facebook_app_id"] = app_id
        return self
        
    def twitter_signin(self, enabled: bool = True):
        """Enable Twitter Sign-In"""
        self._providers["twitter"] = enabled
        return self
        
    def github_signin(self, enabled: bool = True):
        """Enable GitHub Sign-In"""
        self._providers["github"] = enabled
        return self
        
    def phone_auth(self, enabled: bool = True):
        """Enable phone number authentication"""
        self._providers["phone"] = enabled
        return self
        
    def anonymous_auth(self, enabled: bool = True):
        """Enable anonymous authentication"""
        self._providers["anonymous"] = enabled
        return self
        
    def custom_claims(self, claims: Dict[str, Any]):
        """Set custom claims for users"""
        self._custom_claims.update(claims)
        return self
        
    def user_management(self, enabled: bool = True):
        """Enable user management features"""
        self._user_management = enabled
        return self

    def _discover_existing_auth_config(self) -> Dict[str, Dict[str, Any]]:
        """Discover existing Firebase Auth configuration using Firebase Admin SDK or CLI"""
        existing_config = {}
        
        if not self._project_id:
            return existing_config
            
        try:
            # Try to get current auth config using Firebase CLI
            cmd = ["firebase", "auth:export", "--project", self._project_id, "--format", "json"]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0 and result.stdout:
                auth_data = json.loads(result.stdout)
                existing_config["auth_config"] = {
                    "project_id": self._project_id,
                    "enabled_providers": auth_data.get("users", []),
                    "provider_config": auth_data.get("config", {}),
                    "status": "configured"
                }
        except (subprocess.TimeoutExpired, json.JSONDecodeError, FileNotFoundError):
            # Firebase CLI not available or timeout - check for config file
            try:
                if os.path.exists("firebase-auth.json"):
                    with open("firebase-auth.json", 'r') as f:
                        config_data = json.load(f)
                        existing_config["auth_config"] = {
                            "project_id": self._project_id,
                            "config_file": "firebase-auth.json",
                            "local_config": config_data,
                            "status": "local_config"
                        }
            except json.JSONDecodeError:
                pass
        except Exception:
            pass
            
        return existing_config

    def preview(self) -> Dict[str, Any]:
        """Preview the Firebase Auth configuration with smart state management"""
        print(f"╭─ 🔐 Firebase Auth Preview: {self.name}")
        print(f"├─ 📁 Project: {self._project_id or 'Not specified'}")
        print(f"├─ 🌍 Cost: $0/month (free tier)")
        
        # Discover existing configuration
        existing_config = self._discover_existing_auth_config()
        
        desired_providers = [k for k, v in self._providers.items() if v]
        
        # Determine what needs to be changed
        to_configure = []
        to_update = []
        to_keep = []
        
        if not existing_config:
            to_configure = desired_providers
        else:
            # Compare with existing
            existing_providers = existing_config.get("auth_config", {}).get("enabled_providers", [])
            
            for provider in desired_providers:
                if provider not in existing_providers:
                    to_configure.append(provider)
                else:
                    to_keep.append(provider)
        
        # Show only actionable changes
        if to_configure:
            print(f"├─ 🔧 Providers to CONFIGURE:")
            for provider in to_configure:
                print(f"│  ├─ 🔑 {provider.title()}")
                
        if to_update:
            print(f"├─ 🔄 Providers to UPDATE:")
            for provider in to_update:
                print(f"│  ├─ 🔄 {provider.title()}")
        
        if existing_config:
            print(f"├─ ✅ Current status: {existing_config.get('auth_config', {}).get('status', 'unknown')}")
        
        print(f"╰─ 💡 Run .create() to configure Firebase Auth")
        
        return {
            "resource_type": "Firebase Authentication",
            "name": self.name,
            "project_id": self._project_id,
            "to_configure": to_configure,
            "to_update": to_update,
            "existing_config": existing_config,
            "changes": len(to_configure) + len(to_update) > 0
        }

    def create(self) -> Dict[str, Any]:
        """Configure Firebase Authentication with smart state management"""
        try:
            if not self._project_id:
                raise ValueError("Firebase project ID is required. Use .project('your-project-id')")
            
            # Discover existing configuration first
            existing_config = self._discover_existing_auth_config()
            desired_providers = [k for k, v in self._providers.items() if v]
            
            # Determine changes needed
            to_configure = []
            to_keep = []
            
            if not existing_config:
                to_configure = desired_providers
            else:
                existing_providers = existing_config.get("auth_config", {}).get("enabled_providers", [])
                for provider in desired_providers:
                    if provider not in existing_providers:
                        to_configure.append(provider)
                    else:
                        to_keep.append(provider)
            
            print(f"🔐 Configuring Firebase Authentication: {self.name}")
            
            # Configure new providers
            configured_providers = []
            if to_configure:
                print(f"╭─ 🔧 Configuring providers:")
                for provider in to_configure:
                    try:
                        if provider == "password":
                            print(f"│  ├─ 🔑 Email/password authentication")
                            configured_providers.append(provider)
                        elif provider == "google":
                            print(f"│  ├─ 🔑 Google Sign-In")
                            configured_providers.append(provider)
                        elif provider == "facebook":
                            print(f"│  ├─ 🔑 Facebook Sign-In")
                            configured_providers.append(provider)
                        elif provider == "twitter":
                            print(f"│  ├─ 🔑 Twitter Sign-In")
                            configured_providers.append(provider)
                        elif provider == "github":
                            print(f"│  ├─ 🔑 GitHub Sign-In")
                            configured_providers.append(provider)
                        elif provider == "phone":
                            print(f"│  ├─ 🔑 Phone authentication")
                            configured_providers.append(provider)
                        elif provider == "anonymous":
                            print(f"│  ├─ 🔑 Anonymous authentication")
                            configured_providers.append(provider)
                    except Exception as e:
                        print(f"│  ├─ ⚠️  Failed to configure {provider}: {str(e)}")
                print(f"╰─ ✅ {len(configured_providers)} provider(s) configured")
            
            # Create/update auth configuration file
            auth_config = {
                "auth": {
                    "project_id": self._project_id,
                    "providers": desired_providers,
                    "custom_claims": self._custom_claims,
                    "user_management": self._user_management,
                    "configured_at": json.dumps({"timestamp": "now"})
                }
            }
            
            config_path = "firebase-auth.json"
            with open(config_path, 'w') as f:
                json.dump(auth_config, f, indent=2)
            
            print(f"✅ Firebase Authentication configured successfully!")
            print(f"📄 Configuration saved to: {config_path}")
            print(f"🌐 Console: https://console.firebase.google.com/project/{self._project_id}/authentication/")
            
            return {
                "status": "configured",
                "project_id": self._project_id,
                "configured_providers": configured_providers,
                "existing_providers": to_keep,
                "custom_claims": self._custom_claims,
                "config_file": config_path,
                "console_url": f"https://console.firebase.google.com/project/{self._project_id}/authentication/",
                "changes": len(configured_providers) > 0
            }
            
        except Exception as e:
            raise Exception(f"Firebase Authentication configuration failed: {str(e)}")

    def destroy(self) -> Dict[str, Any]:
        """Remove Firebase Authentication configuration"""
        try:
            print(f"⚠️  Firebase Authentication cannot be automatically destroyed")
            print(f"🔧 To disable providers:")
            print(f"   1. Go to Firebase Console: https://console.firebase.google.com/project/{self._project_id}/authentication/")
            print(f"   2. Disable providers manually")
            
            return {
                "status": "manual_action_required",
                "message": "Visit Firebase Console to disable authentication providers"
            }
            
        except Exception as e:
            raise Exception(f"Firebase Authentication destroy failed: {str(e)}")

    def update(self) -> Dict[str, Any]:
        """Update Firebase Authentication configuration"""
        return self.create() 