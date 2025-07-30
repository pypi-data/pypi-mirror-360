"""
Firebase Hosting Resource for InfraDSL
Production-ready web hosting with automatic SSL and global CDN

Features:
- Static site hosting
- Custom domains with automatic SSL
- Global CDN
- CI/CD integration
"""

import os
import json
import subprocess
from typing import Dict, List, Optional, Any
from ..base_resource import BaseGcpResource


class FirebaseHosting(BaseGcpResource):
    """
    Firebase Hosting for static websites and SPAs
    
    Example:
        docs_site = (FirebaseHosting("infradsl-docs")
                   .project("my-project")
                   .site_id("infradsl-docs")
                   .public_directory("dist")
                   .custom_domain("docs.infradsl.dev")
                   .single_page_app(True)
                   .ignore_files([
                       "firebase.json",
                       "**/.*",
                       "**/node_modules/**"
                   ])
                   .redirects([
                       {"source": "/old-path", "destination": "/new-path", "type": 301}
                   ])
                   .headers([
                       {"source": "**/*.@(js|css)", "headers": [{"key": "Cache-Control", "value": "max-age=31536000"}]}
                   ]))
    """
    
    def __init__(self, name: str):
        super().__init__(name)
        self.config = {
            "hosting": {
                "public": "dist",
                "ignore": [
                    "firebase.json",
                    "**/.*",
                    "**/node_modules/**"
                ],
                "rewrites": []
            }
        }
        self._project_id = None
        self._site_id = None
        self._custom_domains = []
        self._build_command = None
        self._public_dir = "dist"
        self._region = None
        
    def _initialize_managers(self):
        """Initialize Firebase-specific managers"""
        # Firebase hosting doesn't require additional managers
        pass
        
    def _post_authentication_setup(self):
        """Setup after authentication"""
        # Firebase hosting doesn't require post-auth setup
        pass

    def _discover_existing_sites(self) -> Dict[str, Dict[str, Any]]:
        """Discover existing Firebase Hosting sites"""
        existing_sites = {}
        
        try:
            import requests
            from google.auth.transport.requests import Request
            
            if not self.gcp_client or not hasattr(self.gcp_client, 'credentials'):
                print(f"⚠️  No GCP credentials available for Firebase API discovery")
                return existing_sites
            
            # Refresh credentials if needed
            if hasattr(self.gcp_client.credentials, 'refresh'):
                self.gcp_client.credentials.refresh(Request())
            
            # Firebase Hosting API requires project ID
            project_id = self._project_id or self.gcp_client.project_id
            if not project_id:
                print(f"⚠️  Project ID required for Firebase Hosting discovery")
                return existing_sites
            
            # List Firebase Hosting sites
            hosting_api_url = f"https://firebase.googleapis.com/v1beta1/projects/{project_id}/sites"
            headers = {
                'Authorization': f'Bearer {self.gcp_client.credentials.token}',
                'Content-Type': 'application/json'
            }
            
            response = requests.get(hosting_api_url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                sites = data.get('sites', [])
                
                for site in sites:
                    site_name = site.get('name', '').split('/')[-1]
                    site_id = site.get('siteId', site_name)
                    
                    # Get site configuration details
                    site_config = {
                        'site_name': site_name,
                        'site_id': site_id,
                        'display_name': site.get('displayName', site_name),
                        'default_domain': site.get('defaultUrl', ''),
                        'app_id': site.get('appId', ''),
                        'type': site.get('type', 'DEFAULT_SITE'),
                        'state': 'ACTIVE',  # Firebase sites are typically active when listed
                        'project_id': project_id
                    }
                    
                    # Get custom domains if available
                    try:
                        domains_url = f"https://firebase.googleapis.com/v1beta1/projects/{project_id}/sites/{site_id}/domains"
                        domains_response = requests.get(domains_url, headers=headers)
                        
                        if domains_response.status_code == 200:
                            domains_data = domains_response.json()
                            domains = domains_data.get('domains', [])
                            
                            custom_domains = []
                            for domain in domains:
                                domain_info = {
                                    'domain_name': domain.get('domainName', ''),
                                    'status': domain.get('status', 'UNKNOWN'),
                                    'provisioning': domain.get('provisioning', {}),
                                    'update_time': domain.get('updateTime', '')
                                }
                                custom_domains.append(domain_info)
                            
                            site_config['custom_domains'] = custom_domains
                            site_config['custom_domain_count'] = len(custom_domains)
                        else:
                            site_config['custom_domains'] = []
                            site_config['custom_domain_count'] = 0
                            
                    except Exception as e:
                        print(f"⚠️  Failed to get domains for site {site_id}: {str(e)}")
                        site_config['custom_domains'] = []
                        site_config['custom_domain_count'] = 0
                    
                    # Try to get recent releases/deployments
                    try:
                        releases_url = f"https://firebase.googleapis.com/v1beta1/projects/{project_id}/sites/{site_id}/releases"
                        releases_response = requests.get(f"{releases_url}?pageSize=5", headers=headers)
                        
                        if releases_response.status_code == 200:
                            releases_data = releases_response.json()
                            releases = releases_data.get('releases', [])
                            
                            if releases:
                                latest_release = releases[0]
                                site_config['latest_release'] = {
                                    'name': latest_release.get('name', ''),
                                    'release_time': latest_release.get('releaseTime', ''),
                                    'release_user': latest_release.get('releaseUser', {}).get('email', 'unknown'),
                                    'version': latest_release.get('version', {}).get('name', '').split('/')[-1] if latest_release.get('version') else 'unknown'
                                }
                                site_config['total_releases'] = len(releases)
                            else:
                                site_config['latest_release'] = None
                                site_config['total_releases'] = 0
                        else:
                            site_config['latest_release'] = None
                            site_config['total_releases'] = 0
                            
                    except Exception as e:
                        print(f"⚠️  Failed to get releases for site {site_id}: {str(e)}")
                        site_config['latest_release'] = None
                        site_config['total_releases'] = 0
                    
                    existing_sites[site_id] = site_config
                    
            elif response.status_code == 403:
                print(f"⚠️  Firebase Hosting API access denied. Enable Firebase Hosting API in the console.")
            elif response.status_code == 404:
                print(f"⚠️  Firebase project not found or Firebase not enabled for project {project_id}")
            else:
                print(f"⚠️  Failed to list Firebase Hosting sites: HTTP {response.status_code}")
                
        except ImportError:
            print(f"⚠️  'requests' library required for Firebase API discovery. Install with: pip install requests")
        except Exception as e:
            print(f"⚠️  Failed to discover existing Firebase Hosting sites: {str(e)}")
        
        return existing_sites
        
    def project(self, project_id: str):
        """Set Firebase project ID"""
        self._project_id = project_id
        return self
        
    def site_id(self, site_id: str):
        """Set Firebase Hosting site ID"""
        self._site_id = site_id
        return self
        
    def public_directory(self, directory: str):
        """Set the public directory containing built assets"""
        self._public_dir = directory
        self.config["hosting"]["public"] = directory
        return self
        
    def custom_domain(self, domain: str):
        """Add custom domain"""
        self._custom_domains.append(domain)
        return self
        
    def single_page_app(self, enabled: bool = True):
        """Configure as single-page application (React, Vue, etc.)"""
        if enabled:
            self.config["hosting"]["rewrites"] = [
                {
                    "source": "**",
                    "destination": "/index.html"
                }
            ]
        else:
            self.config["hosting"]["rewrites"] = []
        return self
        
    def ignore_files(self, patterns: List[str]):
        """Set file patterns to ignore during deployment"""
        self.config["hosting"]["ignore"] = patterns
        return self
        
    def redirects(self, redirects: List[Dict[str, Any]]):
        """Add URL redirects"""
        self.config["hosting"]["redirects"] = redirects
        return self
        
    def headers(self, headers: List[Dict[str, Any]]):
        """Add custom headers"""
        self.config["hosting"]["headers"] = headers
        return self
        
    def build_command(self, command: str):
        """Set build command to run before deployment"""
        self._build_command = command
        return self
        
    def clean_urls(self, enabled: bool = True):
        """Enable clean URLs (remove .html extension)"""
        self.config["hosting"]["cleanUrls"] = enabled
        return self
        
    def trailing_slash(self, enabled: bool = False):
        """Control trailing slash behavior"""
        self.config["hosting"]["trailingSlash"] = enabled
        return self
        
    def location(self, region: str):
        """Set the deployment region"""
        self._region = region
        return self

    def preview(self) -> Dict[str, Any]:
        """Preview what will be created, kept, and removed"""
        try:
            self._ensure_authenticated()
        except:
            # Firebase Hosting can work without full GCP authentication in some cases
            pass

        # Discover existing sites
        existing_sites = self._discover_existing_sites()
        
        # Categorize sites
        sites_to_create = []
        sites_to_keep = []
        sites_to_remove = []
        
        # Check if our desired site exists
        desired_site_id = self._site_id or self.name
        site_exists = desired_site_id in existing_sites
        
        if not site_exists:
            # Determine hosting URL
            hosting_url = None
            if self._custom_domains:
                hosting_url = f"https://{self._custom_domains[0]}"
            elif self._site_id:
                hosting_url = f"https://{self._site_id}.web.app"
            elif self._project_id:
                hosting_url = f"https://{self._project_id}.web.app"
            else:
                hosting_url = "https://<project>.web.app"
            
            sites_to_create.append({
                'site_name': self.name,
                'site_id': desired_site_id,
                'project_id': self._project_id,
                'public_directory': self._public_dir,
                'hosting_url': hosting_url,
                'custom_domains': self._custom_domains,
                'custom_domain_count': len(self._custom_domains),
                'single_page_app': bool(self.config["hosting"].get("rewrites")),
                'build_command': self._build_command,
                'clean_urls': self.config["hosting"].get("cleanUrls", False),
                'trailing_slash': self.config["hosting"].get("trailingSlash", False),
                'ignore_patterns': len(self.config["hosting"].get("ignore", [])),
                'redirects': len(self.config["hosting"].get("redirects", [])),
                'headers': len(self.config["hosting"].get("headers", [])),
                'region': self._region
            })
        else:
            sites_to_keep.append(existing_sites[desired_site_id])

        print(f"\n🔥 Firebase Hosting Preview")
        
        # Show sites to create
        if sites_to_create:
            print(f"╭─ 🔥 Hosting Sites to CREATE: {len(sites_to_create)}")
            for site in sites_to_create:
                print(f"├─ 🆕 {site['site_name']}")
                if site['site_id'] != site['site_name']:
                    print(f"│  ├─ 🆔 Site ID: {site['site_id']}")
                
                if site['project_id']:
                    print(f"│  ├─ 📋 Project: {site['project_id']}")
                
                print(f"│  ├─ 📁 Public Directory: {site['public_directory']}")
                print(f"│  ├─ 🌐 Hosting URL: {site['hosting_url']}")
                
                # Show custom domains
                if site['custom_domain_count'] > 0:
                    print(f"│  ├─ 🌍 Custom Domains: {site['custom_domain_count']}")
                    for domain in site['custom_domains'][:3]:  # Show first 3
                        print(f"│  │  ├─ https://{domain}")
                    if len(site['custom_domains']) > 3:
                        print(f"│  │  └─ ... and {len(site['custom_domains']) - 3} more domains")
                else:
                    print(f"│  ├─ 🌍 Custom Domains: None")
                
                # Show app configuration
                print(f"│  ├─ ⚛️  Single Page App: {'✅ Yes' if site['single_page_app'] else '❌ No'}")
                print(f"│  ├─ 🧹 Clean URLs: {'✅ Enabled' if site['clean_urls'] else '❌ Disabled'}")
                print(f"│  ├─ 📄 Trailing Slash: {'✅ Enabled' if site['trailing_slash'] else '❌ Disabled'}")
                
                # Show build configuration
                if site['build_command']:
                    print(f"│  ├─ 🔨 Build Command: {site['build_command']}")
                else:
                    print(f"│  ├─ 🔨 Build Command: None (manual build)")
                
                # Show deployment configuration
                if site['ignore_patterns'] > 0:
                    print(f"│  ├─ 🚫 Ignore Patterns: {site['ignore_patterns']}")
                
                if site['redirects'] > 0:
                    print(f"│  ├─ ➡️  Redirects: {site['redirects']}")
                
                if site['headers'] > 0:
                    print(f"│  ├─ 📋 Custom Headers: {site['headers']}")
                
                if site['region']:
                    print(f"│  ├─ 📍 Region: {site['region']}")
                
                # Show Firebase features
                print(f"│  ├─ 🚀 Features:")
                print(f"│  │  ├─ 🔒 Automatic SSL certificates")
                print(f"│  │  ├─ 🌍 Global CDN")
                print(f"│  │  ├─ ⚡ Fast deployments")
                print(f"│  │  └─ 📊 Built-in analytics")
                
                print(f"│  └─ 🚀 Deploy: firebase deploy --only hosting")
            print(f"╰─")

        # Show existing sites being kept
        if sites_to_keep:
            print(f"\n╭─ 🔥 Existing Hosting Sites to KEEP: {len(sites_to_keep)}")
            for site in sites_to_keep:
                print(f"├─ ✅ {site['site_name']}")
                print(f"│  ├─ 🆔 Site ID: {site['site_id']}")
                print(f"│  ├─ 📋 Project: {site['project_id']}")
                print(f"│  ├─ 🌐 Default URL: {site['default_domain']}")
                
                if site['custom_domain_count'] > 0:
                    print(f"│  ├─ 🌍 Custom Domains: {site['custom_domain_count']}")
                    for domain in site['custom_domains'][:3]:
                        status_icon = "✅" if domain['status'] == "CONNECTED" else "🟡" if domain['status'] == "PENDING" else "❌"
                        print(f"│  │  ├─ {status_icon} https://{domain['domain_name']}")
                    if len(site['custom_domains']) > 3:
                        print(f"│  │  └─ ... and {len(site['custom_domains']) - 3} more domains")
                
                if site['latest_release']:
                    release = site['latest_release']
                    release_time = release['release_time'][:10] if release['release_time'] else 'unknown'
                    print(f"│  ├─ 📦 Latest Release: {release_time}")
                    print(f"│  │  ├─ 👤 By: {release['release_user']}")
                    print(f"│  │  └─ 📝 Version: {release['version']}")
                else:
                    print(f"│  ├─ 📦 Latest Release: None")
                
                if site['total_releases'] > 0:
                    print(f"│  ├─ 📊 Total Releases: {site['total_releases']}")
                
                print(f"│  └─ 🌐 Access: {site['default_domain']}")
            print(f"╰─")

        # Show cost information
        print(f"\n💰 Firebase Hosting Costs:")
        if sites_to_create:
            site = sites_to_create[0]
            print(f"   ├─ 🔥 Hosting: Free tier (10GB storage, 10GB/month transfer)")
            print(f"   ├─ 🌍 Global CDN: Included")
            print(f"   ├─ 🔒 SSL certificates: Free")
            
            if site['custom_domain_count'] > 0:
                print(f"   ├─ 🌐 Custom domains ({site['custom_domain_count']}): Free")
            
            print(f"   ├─ 📊 Additional storage: $0.026/GB/month")
            print(f"   ├─ 📡 Additional transfer: $0.15/GB")
            print(f"   └─ 📊 Typical cost: Free for most projects")
        else:
            print(f"   ├─ 🔥 Hosting: Free tier (10GB storage, 10GB/month transfer)")
            print(f"   ├─ 🌍 Global CDN: Included")
            print(f"   ├─ 🔒 SSL certificates: Free")
            print(f"   └─ 📊 Additional usage: $0.026/GB storage, $0.15/GB transfer")

        return {
            'resource_type': 'firebase_hosting',
            'name': self.name,
            'sites_to_create': sites_to_create,
            'sites_to_keep': sites_to_keep,
            'sites_to_remove': sites_to_remove,
            'existing_sites': existing_sites,
            'site_id': desired_site_id,
            'project_id': self._project_id,
            'custom_domain_count': len(self._custom_domains),
            'single_page_app': bool(self.config["hosting"].get("rewrites")),
            'estimated_cost': "Free (within limits)"
        }

    def create(self) -> Dict[str, Any]:
        """Deploy to Firebase Hosting"""
        try:
            # Validate required parameters
            if not self._project_id:
                raise ValueError("Firebase project ID is required. Use .project('your-project-id')")
                
            # Create firebase.json configuration
            config_path = os.path.join(os.getcwd(), "firebase.json")
            with open(config_path, 'w') as f:
                json.dump(self.config, f, indent=2)
                
            # Create .firebaserc project configuration
            firebaserc_path = os.path.join(os.getcwd(), ".firebaserc")
            firebaserc_config = {
                "projects": {
                    "default": self._project_id
                }
            }
            
            # Add site targeting if site_id is specified
            if self._site_id:
                firebaserc_config["targets"] = {
                    self._project_id: {
                        "hosting": {
                            self._site_id: [self._site_id]
                        }
                    }
                }
                # Update hosting config to target specific site
                self.config["hosting"]["site"] = self._site_id
                with open(config_path, 'w') as f:
                    json.dump(self.config, f, indent=2)
                    
            with open(firebaserc_path, 'w') as f:
                json.dump(firebaserc_config, f, indent=2)
                
            print(f"✅ Created Firebase configuration files")
            
            # Run build command if specified
            if self._build_command:
                print(f"🔨 Running build command: {self._build_command}")
                result = subprocess.run(self._build_command, shell=True, capture_output=True, text=True)
                if result.returncode != 0:
                    raise Exception(f"Build command failed: {result.stderr}")
                print(f"✅ Build completed successfully")
                
            # Check if public directory exists
            if not os.path.exists(self._public_dir):
                print(f"⚠️  Warning: Public directory '{self._public_dir}' does not exist")
                print(f"💡 Make sure to run your build command first")
                
            # Deploy to Firebase
            deploy_cmd = ["firebase", "deploy", "--only", "hosting"]
            if self._site_id:
                deploy_cmd.extend(["--only", f"hosting:{self._site_id}"])
                
            print(f"🚀 Deploying to Firebase Hosting...")
            result = subprocess.run(deploy_cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                raise Exception(f"Firebase deployment failed: {result.stderr}")
                
            # Parse deployment output for URLs
            output_lines = result.stdout.split('\n')
            hosting_url = None
            
            for line in output_lines:
                if "Hosting URL:" in line:
                    hosting_url = line.split("Hosting URL:")[-1].strip()
                    break
                    
            deployment_result = {
                "status": "deployed",
                "project_id": self._project_id,
                "site_id": self._site_id,
                "hosting_url": hosting_url or f"https://{self._project_id}.web.app",
                "public_directory": self._public_dir,
                "custom_domains": self._custom_domains,
                "firebase_config": self.config
            }
            
            print(f"✅ Deployment successful!")
            print(f"🌐 Site URL: {deployment_result['hosting_url']}")
            
            # Add custom domains programmatically
            if self._custom_domains:
                print(f"\n🌐 Setting up custom domains...")
                domain_results = []
                
                for domain in self._custom_domains:
                    try:
                        print(f"   📝 Adding domain: {domain}")
                        
                        # Attempt to add custom domain using Firebase CLI
                        domain_cmd = ["firebase", "hosting:domains:add", domain]
                        if self._site_id:
                            domain_cmd.extend(["--site", self._site_id])
                            
                        domain_result = subprocess.run(domain_cmd, capture_output=True, text=True)
                        
                        if domain_result.returncode == 0:
                            print(f"   ✅ Domain {domain} added successfully")
                            domain_results.append({"domain": domain, "status": "added", "message": "Successfully added"})
                        else:
                            # Domain might already exist or need verification
                            error_output = domain_result.stderr.lower()
                            if "already exists" in error_output or "already added" in error_output:
                                print(f"   ℹ️  Domain {domain} already exists")
                                domain_results.append({"domain": domain, "status": "exists", "message": "Domain already exists"})
                            else:
                                print(f"   ⚠️  Could not add domain {domain}: {domain_result.stderr}")
                                domain_results.append({"domain": domain, "status": "failed", "message": domain_result.stderr})
                                
                    except Exception as e:
                        print(f"   ❌ Error adding domain {domain}: {str(e)}")
                        domain_results.append({"domain": domain, "status": "error", "message": str(e)})
                
                # Check domain status and provide verification instructions
                print(f"\n📋 Domain Status & Next Steps:")
                for domain_info in domain_results:
                    domain = domain_info["domain"]
                    status = domain_info["status"]
                    
                    if status in ["added", "exists"]:
                        try:
                            # Get domain verification status
                            status_cmd = ["firebase", "hosting:domains:list"]
                            if self._site_id:
                                status_cmd.extend(["--site", self._site_id])
                                
                            status_result = subprocess.run(status_cmd, capture_output=True, text=True)
                            if status_result.returncode == 0:
                                print(f"   🔍 {domain}: Check status in Firebase Console")
                            else:
                                print(f"   📋 {domain}: Manual verification required")
                        except:
                            print(f"   📋 {domain}: Manual verification required")
                    else:
                        print(f"   ❌ {domain}: {domain_info['message']}")
                
                # Always provide manual backup instructions
                print(f"\n📖 Manual Setup Instructions (if needed):")
                print(f"   1. Go to Firebase Console: https://console.firebase.google.com/project/{self._project_id}/hosting/")
                if self._site_id:
                    print(f"   2. Select site: {self._site_id}")
                    print(f"   3. Click 'Add custom domain'")
                else:
                    print(f"   2. Click 'Add custom domain'")
                    
                for domain in self._custom_domains:
                    print(f"   4. Add domain: {domain}")
                    print(f"   5. Complete domain verification")
                    print(f"   6. Update DNS CNAME: {domain} → {deployment_result['hosting_url'].replace('https://', '')}")
                
                # Add domain results to deployment result
                deployment_result["domain_setup"] = domain_results
                
            return deployment_result
            
        except subprocess.CalledProcessError as e:
            raise Exception(f"Firebase command failed: {e}")
        except FileNotFoundError:
            raise Exception("Firebase CLI not found. Install with: npm install -g firebase-tools")
        except Exception as e:
            raise Exception(f"Firebase Hosting deployment failed: {str(e)}")

    def destroy(self) -> Dict[str, Any]:
        """Remove Firebase Hosting deployment"""
        try:
            # Firebase doesn't have a direct "destroy" command
            # We can disable hosting or delete the site
            print(f"⚠️  Firebase Hosting sites cannot be automatically destroyed via CLI")
            print(f"🔧 To remove the site:")
            print(f"   1. Go to Firebase Console: https://console.firebase.google.com/project/{self._project_id}/hosting/")
            print(f"   2. Delete the hosting site manually")
            print(f"   3. Or disable hosting with: firebase hosting:disable")
            
            return {
                "status": "manual_action_required",
                "message": "Visit Firebase Console to delete hosting site"
            }
            
        except Exception as e:
            raise Exception(f"Firebase Hosting destroy failed: {str(e)}")

    def update(self) -> Dict[str, Any]:
        """Update Firebase Hosting deployment"""
        # For Firebase Hosting, update is the same as create/deploy
        return self.create() 