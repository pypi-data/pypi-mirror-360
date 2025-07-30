"""
Firebase Hosting Core Implementation

Core attributes and authentication for Firebase Hosting.
Provides the foundation for the modular web hosting system.
"""

from typing import Dict, Any, List, Optional, Union
from ..base_resource import BaseGcpResource


class FirebaseHostingCore(BaseGcpResource):
    """
    Core class for Firebase Hosting functionality.
    
    This class provides:
    - Basic Firebase Hosting attributes and configuration
    - Authentication setup
    - Common utilities for static site hosting
    - Validation and state tracking foundations
    """
    
    def __init__(self, name: str):
        """Initialize Firebase Hosting core with site name"""
        super().__init__(name)
        
        # Core site attributes
        self.site_name = name
        self.firebase_project_id = None
        self.site_id_value = None
        self.site_description = f"Firebase Hosting site for {name}"
        
        # Hosting configuration
        self.public_directory_path = "dist"
        self.build_command_value = None
        self.build_directory_value = None
        self.framework = None  # react, vue, angular, next, nuxt, etc.
        
        # Domain configuration
        self.custom_domains = []
        self.domain_configs = {}
        self.ssl_certificates = {}
        
        # Site configuration
        self.single_page_app = False
        self.clean_urls = False
        self.trailing_slash = False
        self.app_association = None  # For mobile app deep linking
        
        # Performance configuration
        self.compression_enabled = True
        self.cache_control = {}
        self.custom_headers = []
        self.redirects = []
        self.rewrites = []
        
        # Security configuration
        self.security_headers = {}
        self.cors_origins = []
        self.content_security_policy = None
        
        # Deployment configuration
        self.ignore_patterns = [
            "firebase.json",
            "**/.*",
            "**/node_modules/**",
            "**/*.log"
        ]
        self.deploy_hooks = {}
        self.preview_channels = []
        
        # CI/CD configuration
        self.github_integration = False
        self.auto_deploy_branch = None
        self.build_env_vars = {}
        
        # Monitoring configuration
        self.analytics_enabled = False
        self.performance_monitoring = False
        self.error_reporting = False
        
        # Labels and metadata
        self.hosting_labels = {}
        self.hosting_annotations = {}
        
        # State tracking
        self.site_exists = False
        self.site_deployed = False
        self.deployment_status = None
        self.last_deployment = None
        self.deployment_count = 0
        
        # Client references
        self.hosting_client = None
        self.firebase_client = None
        
        # Cost tracking
        self.estimated_monthly_cost = "$0.00/month"
        
    def _initialize_managers(self):
        """Initialize Firebase Hosting-specific managers"""
        self.hosting_client = None
        self.firebase_client = None
        
    def _post_authentication_setup(self):
        """Setup managers after authentication"""
        try:
            # Firebase Hosting uses Firebase project ID rather than GCP project ID
            # Set project context if available
            if not self.firebase_project_id and hasattr(self.gcp_client, 'project_id'):
                self.firebase_project_id = self.gcp_client.project_id
                
        except Exception as e:
            print(f"⚠️  Firebase Hosting setup note: {str(e)}")
            
    def _is_valid_project_id(self, project_id: str) -> bool:
        """Check if Firebase project ID is valid"""
        import re
        # Firebase project IDs must contain only lowercase letters, numbers, dashes
        pattern = r'^[a-z][a-z0-9-]*[a-z0-9]$'
        return bool(re.match(pattern, project_id)) and 4 <= len(project_id) <= 30
        
    def _is_valid_site_id(self, site_id: str) -> bool:
        """Check if site ID is valid"""
        import re
        # Site IDs must be valid domain-like strings
        if not site_id or len(site_id) > 63:
            return False
        # Must start with letter or number, contain only letters, numbers, hyphens
        pattern = r'^[a-zA-Z0-9][a-zA-Z0-9-]*[a-zA-Z0-9]$'
        return bool(re.match(pattern, site_id))
    
    def _is_valid_domain(self, domain: str) -> bool:
        """Check if domain name is valid"""
        import re
        # Basic domain validation
        if not domain or len(domain) > 253:
            return False
        # Must not start or end with dot or hyphen
        if domain.startswith('.') or domain.endswith('.') or domain.startswith('-') or domain.endswith('-'):
            return False
        # Basic pattern check
        pattern = r'^[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$'
        return bool(re.match(pattern, domain))
        
    def _is_valid_framework(self, framework: str) -> bool:
        """Check if framework is supported"""
        supported_frameworks = [
            "react", "vue", "angular", "svelte", "preact",
            "next", "nuxt", "gatsby", "vite", "webpack",
            "static", "html", "jekyll", "hugo", "eleventy"
        ]
        return framework.lower() in supported_frameworks
        
    def _validate_hosting_config(self, config: Dict[str, Any]) -> bool:
        """Validate hosting configuration"""
        required_fields = ["firebase_project_id", "public_directory"]
        
        for field in required_fields:
            if field not in config or not config[field]:
                return False
                
        # Validate project ID format
        if not self._is_valid_project_id(config["firebase_project_id"]):
            return False
            
        # Validate site ID if provided
        if "site_id" in config and config["site_id"]:
            if not self._is_valid_site_id(config["site_id"]):
                return False
            
        # Validate domains if provided
        domains = config.get("custom_domains", [])
        for domain in domains:
            if not self._is_valid_domain(domain):
                return False
                
        return True
        
    def _get_hosting_type_from_config(self) -> str:
        """Determine hosting type from configuration"""
        labels = self.hosting_labels
        
        # Check for explicit framework type
        if self.framework:
            return f"{self.framework}_app"
        
        # Check for purpose-based types
        purpose = labels.get("purpose", "").lower()
        if purpose:
            if "documentation" in purpose or "docs" in purpose:
                return "documentation_site"
            elif "blog" in purpose:
                return "blog_site"
            elif "portfolio" in purpose:
                return "portfolio_site"
            elif "landing" in purpose:
                return "landing_page"
            elif "marketing" in purpose:
                return "marketing_site"
            elif "ecommerce" in purpose:
                return "ecommerce_site"
            elif "dashboard" in purpose:
                return "dashboard_app"
        
        # Check environment
        environment = labels.get("environment", "").lower()
        if environment:
            if environment == "development":
                return "development"
            elif environment == "staging":
                return "staging"
            elif environment == "production":
                return "production"
        
        # Check by configuration patterns
        if self.single_page_app:
            if len(self.custom_domains) > 0:
                return "spa_production"
            else:
                return "spa_development"
        elif len(self.custom_domains) > 1:
            return "multi_domain_site"
        elif len(self.custom_domains) == 1:
            return "custom_domain_site"
        elif self.clean_urls or self.redirects:
            return "static_website"
        else:
            return "simple_site"
            
    def _estimate_firebase_hosting_cost(self) -> float:
        """Estimate monthly cost for Firebase Hosting usage"""
        # Firebase Hosting pricing (simplified)
        
        # Storage cost (first 10GB free)
        estimated_storage_gb = 2  # 2GB estimated
        free_storage_gb = 10
        storage_cost_per_gb = 0.026  # $0.026 per GB/month
        
        if estimated_storage_gb > free_storage_gb:
            storage_cost = (estimated_storage_gb - free_storage_gb) * storage_cost_per_gb
        else:
            storage_cost = 0.0
        
        # Data transfer cost (first 10GB free)
        estimated_transfer_gb = 5  # 5GB estimated monthly transfer
        free_transfer_gb = 10
        transfer_cost_per_gb = 0.15  # $0.15 per GB
        
        if estimated_transfer_gb > free_transfer_gb:
            transfer_cost = (estimated_transfer_gb - free_transfer_gb) * transfer_cost_per_gb
        else:
            transfer_cost = 0.0
        
        # Custom domains are free
        domain_cost = 0.0
        
        # SSL certificates are free
        ssl_cost = 0.0
        
        total_cost = storage_cost + transfer_cost + domain_cost + ssl_cost
        
        # Adjust based on site complexity
        if len(self.custom_domains) > 2:
            total_cost *= 1.2  # More domains might mean more traffic
        
        if self.single_page_app and len(self.redirects) > 10:
            total_cost *= 1.1  # Complex routing might mean more usage
        
        # Most sites stay within free tier
        if total_cost < 1.0:
            total_cost = 0.0
            
        return total_cost
        
    def _fetch_current_hosting_state(self) -> Dict[str, Any]:
        """Fetch current state of Firebase Hosting from Firebase"""
        try:
            import requests
            from google.auth.transport.requests import Request
            
            if not self.firebase_project_id:
                return {
                    "exists": False,
                    "site_name": self.site_name,
                    "error": "No Firebase project ID configured"
                }
            
            # Try to use GCP credentials if available
            if hasattr(self, 'gcp_client') and hasattr(self.gcp_client, 'credentials'):
                # Refresh credentials if needed
                if hasattr(self.gcp_client.credentials, 'refresh'):
                    self.gcp_client.credentials.refresh(Request())
                
                # Use Firebase Hosting API to get site info
                site_api_url = f"https://firebase.googleapis.com/v1beta1/projects/{self.firebase_project_id}/sites"
                headers = {
                    'Authorization': f'Bearer {self.gcp_client.credentials.token}',
                    'Content-Type': 'application/json'
                }
                
                response = requests.get(site_api_url, headers=headers)
                
                if response.status_code == 200:
                    sites_data = response.json()
                    sites = sites_data.get('sites', [])
                    
                    # Look for our specific site
                    target_site_id = self.site_id or self.site_name
                    current_site = None
                    
                    for site in sites:
                        site_id = site.get('siteId', '')
                        if site_id == target_site_id:
                            current_site = site
                            break
                    
                    if current_site:
                        current_state = {
                            "exists": True,
                            "site_name": self.site_name,
                            "site_id": current_site.get('siteId', ''),
                            "firebase_project_id": self.firebase_project_id,
                            "display_name": current_site.get('displayName', ''),
                            "default_url": current_site.get('defaultUrl', ''),
                            "app_id": current_site.get('appId', ''),
                            "type": current_site.get('type', 'DEFAULT_SITE'),
                            "console_url": f"https://console.firebase.google.com/project/{self.firebase_project_id}/hosting/"
                        }
                        
                        # Try to get custom domains
                        try:
                            domains_url = f"https://firebase.googleapis.com/v1beta1/projects/{self.firebase_project_id}/sites/{current_site.get('siteId')}/domains"
                            domains_response = requests.get(domains_url, headers=headers)
                            
                            domains = []
                            if domains_response.status_code == 200:
                                domains_data = domains_response.json()
                                domain_list = domains_data.get('domains', [])
                                
                                for domain in domain_list:
                                    domains.append({
                                        'domain_name': domain.get('domainName', ''),
                                        'status': domain.get('status', 'UNKNOWN'),
                                        'update_time': domain.get('updateTime', '')
                                    })
                            
                            current_state['custom_domains'] = domains
                            current_state['custom_domain_count'] = len(domains)
                            
                        except Exception:
                            current_state['custom_domains'] = []
                            current_state['custom_domain_count'] = 0
                        
                        # Try to get recent releases
                        try:
                            releases_url = f"https://firebase.googleapis.com/v1beta1/projects/{self.firebase_project_id}/sites/{current_site.get('siteId')}/releases"
                            releases_response = requests.get(f"{releases_url}?pageSize=5", headers=headers)
                            
                            releases = []
                            if releases_response.status_code == 200:
                                releases_data = releases_response.json()
                                release_list = releases_data.get('releases', [])
                                
                                for release in release_list:
                                    releases.append({
                                        'name': release.get('name', ''),
                                        'release_time': release.get('releaseTime', ''),
                                        'release_user': release.get('releaseUser', {}).get('email', 'unknown'),
                                        'version': release.get('version', {}).get('name', '').split('/')[-1] if release.get('version') else 'unknown'
                                    })
                            
                            current_state['releases'] = releases
                            current_state['release_count'] = len(releases)
                            current_state['latest_release'] = releases[0] if releases else None
                            
                        except Exception:
                            current_state['releases'] = []
                            current_state['release_count'] = 0
                            current_state['latest_release'] = None
                        
                        return current_state
                    else:
                        return {
                            "exists": False,
                            "site_name": self.site_name,
                            "firebase_project_id": self.firebase_project_id,
                            "target_site_id": target_site_id
                        }
                elif response.status_code == 404:
                    return {
                        "exists": False,
                        "site_name": self.site_name,
                        "firebase_project_id": self.firebase_project_id
                    }
            
            # Fallback: check for local config files
            import os
            import json
            
            config_files = ["firebase.json", ".firebaserc"]
            for config_file in config_files:
                if os.path.exists(config_file):
                    try:
                        with open(config_file, 'r') as f:
                            config_data = json.load(f)
                            
                        if config_file == "firebase.json":
                            hosting_config = config_data.get("hosting", {})
                            if hosting_config:
                                return {
                                    "exists": True,
                                    "site_name": self.site_name,
                                    "firebase_project_id": self.firebase_project_id,
                                    "config_file": config_file,
                                    "local_config": hosting_config,
                                    "status": "local_config",
                                    "console_url": f"https://console.firebase.google.com/project/{self.firebase_project_id}/hosting/"
                                }
                        elif config_file == ".firebaserc":
                            projects = config_data.get("projects", {})
                            if projects:
                                return {
                                    "exists": True,
                                    "site_name": self.site_name,
                                    "firebase_project_id": projects.get("default", self.firebase_project_id),
                                    "config_file": config_file,
                                    "local_config": config_data,
                                    "status": "local_config",
                                    "console_url": f"https://console.firebase.google.com/project/{self.firebase_project_id}/hosting/"
                                }
                    except json.JSONDecodeError:
                        continue
            
            return {
                "exists": False,
                "site_name": self.site_name,
                "firebase_project_id": self.firebase_project_id
            }
            
        except Exception as e:
            # Silently fail for auth issues since we use Firebase CLI
            if "authenticate" not in str(e).lower():
                return {
                    "exists": False,
                    "site_name": self.site_name,
                    "firebase_project_id": self.firebase_project_id,
                    "error": str(e)
                }
            else:
                return {
                    "exists": False,
                    "site_name": self.site_name,
                    "firebase_project_id": self.firebase_project_id
                }
            
    def _discover_existing_sites(self) -> Dict[str, Dict[str, Any]]:
        """Discover all existing Firebase Hosting sites in the project"""
        existing_sites = {}
        
        if not self.firebase_project_id:
            return existing_sites
            
        try:
            import requests
            from google.auth.transport.requests import Request
            
            if hasattr(self, 'gcp_client') and hasattr(self.gcp_client, 'credentials'):
                # Refresh credentials if needed
                if hasattr(self.gcp_client.credentials, 'refresh'):
                    self.gcp_client.credentials.refresh(Request())
                
                # Use Firebase Hosting API to list sites
                sites_api_url = f"https://firebase.googleapis.com/v1beta1/projects/{self.firebase_project_id}/sites"
                headers = {
                    'Authorization': f'Bearer {self.gcp_client.credentials.token}',
                    'Content-Type': 'application/json'
                }
                
                response = requests.get(sites_api_url, headers=headers)
                
                if response.status_code == 200:
                    data = response.json()
                    sites = data.get('sites', [])
                    
                    for site in sites:
                        site_id = site.get('siteId', '')
                        
                        site_info = {
                            'site_id': site_id,
                            'site_name': site.get('name', '').split('/')[-1],
                            'display_name': site.get('displayName', site_id),
                            'default_url': site.get('defaultUrl', ''),
                            'app_id': site.get('appId', ''),
                            'type': site.get('type', 'DEFAULT_SITE'),
                            'firebase_project_id': self.firebase_project_id
                        }
                        
                        # Get additional info for each site
                        try:
                            # Get custom domains
                            domains_url = f"https://firebase.googleapis.com/v1beta1/projects/{self.firebase_project_id}/sites/{site_id}/domains"
                            domains_response = requests.get(domains_url, headers=headers)
                            
                            domains = []
                            if domains_response.status_code == 200:
                                domains_data = domains_response.json()
                                domain_list = domains_data.get('domains', [])
                                
                                for domain in domain_list:
                                    domains.append({
                                        'domain_name': domain.get('domainName', ''),
                                        'status': domain.get('status', 'UNKNOWN'),
                                        'update_time': domain.get('updateTime', '')[:10] if domain.get('updateTime') else 'unknown'
                                    })
                            
                            site_info['custom_domains'] = domains
                            site_info['custom_domain_count'] = len(domains)
                            
                        except Exception:
                            site_info['custom_domains'] = []
                            site_info['custom_domain_count'] = 0
                        
                        # Get release count
                        try:
                            releases_url = f"https://firebase.googleapis.com/v1beta1/projects/{self.firebase_project_id}/sites/{site_id}/releases"
                            releases_response = requests.get(f"{releases_url}?pageSize=1", headers=headers)
                            
                            if releases_response.status_code == 200:
                                releases_data = releases_response.json()
                                releases = releases_data.get('releases', [])
                                site_info['has_deployments'] = len(releases) > 0
                                
                                if releases:
                                    latest_release = releases[0]
                                    site_info['latest_deployment'] = {
                                        'release_time': latest_release.get('releaseTime', '')[:10] if latest_release.get('releaseTime') else 'unknown',
                                        'release_user': latest_release.get('releaseUser', {}).get('email', 'unknown')
                                    }
                                else:
                                    site_info['latest_deployment'] = None
                            else:
                                site_info['has_deployments'] = False
                                site_info['latest_deployment'] = None
                                
                        except Exception:
                            site_info['has_deployments'] = False
                            site_info['latest_deployment'] = None
                        
                        existing_sites[site_id] = site_info
                        
        except Exception as e:
            # Silently fail for auth issues since we use Firebase CLI
            if "authenticate" not in str(e).lower():
                print(f"⚠️  Failed to discover existing sites: {str(e)}")
            
        return existing_sites