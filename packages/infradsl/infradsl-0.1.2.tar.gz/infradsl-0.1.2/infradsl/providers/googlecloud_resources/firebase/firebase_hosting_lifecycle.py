"""
Firebase Hosting Lifecycle Mixin

Lifecycle operations for Firebase Hosting.
Provides create, destroy, and preview operations with smart state management.
"""

import json
import os
import subprocess
from typing import Dict, Any, List, Optional, Union


class FirebaseHostingLifecycleMixin:
    """
    Mixin for Firebase Hosting lifecycle operations.
    
    This mixin provides:
    - preview(): Preview what will be created/updated/deleted
    - create(): Create or update Firebase Hosting configuration
    - destroy(): Clean up Firebase Hosting configuration
    - Smart state management and drift detection
    - Cross-Cloud Magic optimization
    """
    
    def preview(self) -> Dict[str, Any]:
        """Preview what will be created, kept, and removed"""
        # Discover existing sites (ignore auth failures since we use Firebase CLI)
        try:
            existing_sites = self._discover_existing_sites()
        except Exception:
            existing_sites = {}
        
        # Categorize sites
        sites_to_create = []
        sites_to_keep = []
        sites_to_update = []
        
        # Check if our desired site exists
        target_site_id = self.site_id_value or self.site_name
        site_exists = target_site_id in existing_sites
        
        if not site_exists:
            # Determine hosting URLs
            hosting_urls = []
            if self.custom_domains:
                hosting_urls = [f"https://{domain}" for domain in self.custom_domains]
            
            default_url = None
            if self.site_id_value:
                default_url = f"https://{self.site_id_value}.web.app"
            elif self.firebase_project_id:
                default_url = f"https://{self.firebase_project_id}.web.app"
            
            if default_url:
                hosting_urls.insert(0, default_url)
            
            sites_to_create.append({
                'site_name': self.site_name,
                'site_id': target_site_id,
                'firebase_project_id': self.firebase_project_id,
                'hosting_type': self._get_hosting_type_from_config(),
                'framework': self.framework,
                'public_directory': self.public_directory_path,
                'build_command': self.build_command_value,
                'hosting_urls': hosting_urls,
                'default_url': default_url,
                'custom_domains': self.custom_domains,
                'custom_domain_count': len(self.custom_domains),
                'single_page_app': self.single_page_app,
                'clean_urls': self.clean_urls,
                'trailing_slash': self.trailing_slash,
                'security_features': self.has_security_features(),
                'caching_configured': self.has_caching_configured(),
                'compression_enabled': self.compression_enabled,
                'redirect_count': self.get_redirect_count(),
                'rewrite_count': self.get_rewrite_count(),
                'header_count': self.get_header_count(),
                'ignore_pattern_count': len(self.ignore_patterns),
                'analytics_enabled': self.analytics_enabled,
                'performance_monitoring': self.performance_monitoring,
                'github_integration': self.github_integration,
                'auto_deploy_branch': self.auto_deploy_branch,
                'is_production_ready': self.is_production_ready(),
                'labels': self.hosting_labels,
                'label_count': len(self.hosting_labels),
                'estimated_cost': self._estimate_firebase_hosting_cost()
            })
        else:
            existing_site = existing_sites[target_site_id]
            sites_to_keep.append(existing_site)

        print(f"\n🔥 Firebase Hosting Preview")
        
        # Show sites to create
        if sites_to_create:
            print(f"╭─ 🔥 Hosting Sites to CREATE: {len(sites_to_create)}")
            for site in sites_to_create:
                print(f"├─ 🆕 {site['site_name']}")
                if site['site_id'] != site['site_name']:
                    print(f"│  ├─ 🆔 Site ID: {site['site_id']}")
                
                print(f"│  ├─ 📁 Firebase Project: {site['firebase_project_id']}")
                print(f"│  ├─ 🎯 Hosting Type: {site['hosting_type'].replace('_', ' ').title()}")
                
                if site['framework']:
                    print(f"│  ├─ ⚛️  Framework: {site['framework'].title()}")
                
                print(f"│  ├─ 📁 Public Directory: {site['public_directory']}")
                
                if site['build_command']:
                    print(f"│  ├─ 🔨 Build Command: {site['build_command']}")
                else:
                    print(f"│  ├─ 🔨 Build: Manual (no build command)")
                
                # Show hosting URLs
                print(f"│  ├─ 🌐 Hosting URLs:")
                if site['default_url']:
                    print(f"│  │  ├─ 🔵 Default: {site['default_url']}")
                
                if site['custom_domain_count'] > 0:
                    print(f"│  │  ├─ 🌍 Custom Domains ({site['custom_domain_count']}):")
                    for domain in site['custom_domains'][:3]:
                        print(f"│  │  │  ├─ https://{domain}")
                    if len(site['custom_domains']) > 3:
                        print(f"│  │  │  └─ ... and {len(site['custom_domains']) - 3} more")
                else:
                    print(f"│  │  └─ 🌍 Custom Domains: None")
                
                # Show app configuration
                print(f"│  ├─ ⚙️  App Configuration:")
                print(f"│  │  ├─ 🔄 Single Page App: {'✅ Yes' if site['single_page_app'] else '❌ No'}")
                print(f"│  │  ├─ 🧹 Clean URLs: {'✅ Enabled' if site['clean_urls'] else '❌ Disabled'}")
                print(f"│  │  ├─ 📄 Trailing Slash: {'✅ Enabled' if site['trailing_slash'] else '❌ Disabled'}")
                print(f"│  │  └─ 🗜️  Compression: {'✅ Enabled' if site['compression_enabled'] else '❌ Disabled'}")
                
                # Show performance and security
                print(f"│  ├─ 🚀 Performance & Security:")
                print(f"│  │  ├─ 🔒 Security Features: {'✅ Enabled' if site['security_features'] else '❌ None'}")
                print(f"│  │  ├─ 📦 Caching: {'✅ Configured' if site['caching_configured'] else '❌ Not configured'}")
                
                if site['redirect_count'] > 0:
                    print(f"│  │  ├─ ➡️  Redirects: {site['redirect_count']}")
                if site['rewrite_count'] > 0:
                    print(f"│  │  ├─ 🔄 Rewrites: {site['rewrite_count']}")
                if site['header_count'] > 0:
                    print(f"│  │  ├─ 📋 Custom Headers: {site['header_count']}")
                if site['ignore_pattern_count'] > 0:
                    print(f"│  │  └─ 🚫 Ignore Patterns: {site['ignore_pattern_count']}")
                
                # Show monitoring features
                monitoring_features = []
                if site['analytics_enabled']:
                    monitoring_features.append("Analytics")
                if site['performance_monitoring']:
                    monitoring_features.append("Performance Monitoring")
                
                if monitoring_features:
                    print(f"│  ├─ 📊 Monitoring: {', '.join(monitoring_features)}")
                
                # Show CI/CD integration
                if site['github_integration']:
                    print(f"│  ├─ 🔄 CI/CD: GitHub integration")
                    if site['auto_deploy_branch']:
                        print(f"│  │  └─ 🌿 Auto-deploy: {site['auto_deploy_branch']} branch")
                
                # Show Firebase Hosting features
                print(f"│  ├─ 🚀 Firebase Hosting Features:")
                print(f"│  │  ├─ 🔒 Automatic SSL certificates")
                print(f"│  │  ├─ 🌍 Global CDN (Firebase)")
                print(f"│  │  ├─ ⚡ Instant cache invalidation")
                print(f"│  │  ├─ 🔄 Atomic deployments")
                print(f"│  │  ├─ 📈 Real-time analytics")
                print(f"│  │  └─ 🔧 Preview channels support")
                
                # Show production readiness
                production_status = "✅ Production Ready" if site['is_production_ready'] else "⚠️  Needs optimization"
                print(f"│  ├─ 🚀 Status: {production_status}")
                
                # Show labels
                if site['label_count'] > 0:
                    print(f"│  ├─ 🏷️  Labels: {site['label_count']}")
                
                cost = site['estimated_cost']
                if cost > 0:
                    print(f"│  └─ 💰 Estimated Cost: ${cost:.2f}/month")
                else:
                    print(f"│  └─ 💰 Cost: Free tier")
            print(f"╰─")

        # Show existing sites being kept
        if sites_to_keep:
            print(f"\n╭─ 🔥 Existing Hosting Sites to KEEP: {len(sites_to_keep)}")
            for site in sites_to_keep:
                print(f"├─ ✅ {site['site_name']}")
                print(f"│  ├─ 🆔 Site ID: {site['site_id']}")
                print(f"│  ├─ 📁 Firebase Project: {site['firebase_project_id']}")
                print(f"│  ├─ 🌐 Default URL: {site['default_url']}")
                
                if site['custom_domain_count'] > 0:
                    print(f"│  ├─ 🌍 Custom Domains ({site['custom_domain_count']}):")
                    for domain in site['custom_domains'][:3]:
                        status_icon = "✅" if domain['status'] == "CONNECTED" else "🟡" if domain['status'] == "PENDING" else "❌"
                        print(f"│  │  ├─ {status_icon} https://{domain['domain_name']}")
                    if len(site['custom_domains']) > 3:
                        print(f"│  │  └─ ... and {len(site['custom_domains']) - 3} more")
                
                if site.get('has_deployments'):
                    latest = site.get('latest_deployment')
                    if latest:
                        print(f"│  ├─ 📦 Latest Deployment: {latest['release_time']}")
                        print(f"│  │  └─ 👤 By: {latest['release_user']}")
                    else:
                        print(f"│  ├─ 📦 Deployments: Yes")
                else:
                    print(f"│  ├─ 📦 Deployments: None")
                
                print(f"│  └─ 🌐 Access: {site['default_url']}")
            print(f"╰─")

        # Show deployment information
        if sites_to_create:
            print(f"\n🚀 Firebase Hosting Deployment:")
            site = sites_to_create[0]
            print(f"   ├─ 📁 Public Directory: {site['public_directory']}")
            
            if site['build_command']:
                print(f"   ├─ 🔨 Build Command: {site['build_command']}")
            else:
                print(f"   ├─ 🔨 Build: Manual (ensure {site['public_directory']} exists)")
            
            if site['framework']:
                print(f"   ├─ ⚛️  Framework: {site['framework'].title()}")
            
            # Show deployment features
            features = []
            if site['single_page_app']:
                features.append("SPA routing")
            if site['clean_urls']:
                features.append("Clean URLs")
            if site['security_features']:
                features.append("Security headers")
            if site['caching_configured']:
                features.append("Caching rules")
            
            if features:
                print(f"   ├─ 🚀 Features: {', '.join(features)}")
            
            print(f"   └─ 🚀 Deploy: firebase deploy --only hosting")

        # Show cost information
        print(f"\n💰 Firebase Hosting Costs:")
        if sites_to_create:
            site = sites_to_create[0]
            cost = site['estimated_cost']
            
            print(f"   ├─ 🔥 Hosting: Free tier (10GB storage, 10GB/month transfer)")
            print(f"   ├─ 🌍 Global CDN: Included")
            print(f"   ├─ 🔒 SSL certificates: Free (automatic)")
            print(f"   ├─ 🌐 Custom domains: Free (unlimited)")
            print(f"   ├─ 📊 Analytics: Free")
            print(f"   ├─ 💾 Additional storage: $0.026/GB/month")
            print(f"   ├─ 📡 Additional transfer: $0.15/GB")
            
            if cost > 0:
                print(f"   └─ 📊 Estimated: ${cost:.2f}/month")
            else:
                print(f"   └─ 📊 Total: Free tier (typical usage)")
        else:
            print(f"   ├─ 🔥 Free tier: 10GB storage, 10GB/month transfer")
            print(f"   ├─ 🌍 Global CDN: Included")
            print(f"   ├─ 🔒 SSL certificates: Free")
            print(f"   └─ 📊 Additional usage: Pay-as-you-go")

        return {
            'resource_type': 'firebase_hosting',
            'name': self.site_name,
            'sites_to_create': sites_to_create,
            'sites_to_keep': sites_to_keep,
            'sites_to_update': sites_to_update,
            'existing_sites': existing_sites,
            'firebase_project_id': self.firebase_project_id,
            'hosting_type': self._get_hosting_type_from_config(),
            'custom_domain_count': len(self.custom_domains),
            'estimated_cost': f"${self._estimate_firebase_hosting_cost():.2f}/month"
        }

    def create(self) -> Dict[str, Any]:
        """Create or update Firebase Hosting site"""
        if not self.firebase_project_id:
            raise ValueError("Firebase project ID is required. Use .project('your-project-id')")
        
        print(f"🚀 Creating Firebase Hosting Site: {self.site_name}")
        print(f"   🔍 Debug: build_command_value = {getattr(self, 'build_command_value', 'NOT SET')}")
        print(f"   🔍 Debug: public_directory_path = {getattr(self, 'public_directory_path', 'NOT SET')}")
        
        existing_state = self._find_existing_site()
        if existing_state and existing_state.get("exists", False):
            print(f"🔄 Site already exists, updating configuration")
            return self._update_existing_site(existing_state)
        
        print(f"🆕 Creating new site")
        return self._create_new_site()

    def destroy(self) -> Dict[str, Any]:
        """Destroy Firebase Hosting site"""
        print(f"🗑️  Destroying Firebase Hosting Site: {self.site_name}")

        try:
            print(f"⚠️  Firebase Hosting sites cannot be automatically destroyed")
            print(f"🔧 To delete the site:")
            print(f"   1. Go to Firebase Console: https://console.firebase.google.com/project/{self.firebase_project_id}/hosting/")
            if self.site_id_value:
                print(f"   2. Select site: {self.site_id}")
                print(f"   3. Go to site settings")
                print(f"   4. Delete the site manually")
            else:
                print(f"   2. Go to hosting settings")
                print(f"   3. Delete the hosting configuration")
            
            # Remove local config files
            config_files = ["firebase.json", ".firebaserc", ".firebase/"]
            removed_files = []
            
            for config_file in config_files:
                if os.path.exists(config_file):
                    if os.path.isdir(config_file):
                        import shutil
                        shutil.rmtree(config_file)
                    else:
                        os.remove(config_file)
                    removed_files.append(config_file)
            
            if removed_files:
                print(f"   🗑️  Removed local files: {', '.join(removed_files)}")
            
            return {
                'success': True, 
                'site_name': self.site_name, 
                'status': 'manual_action_required',
                'removed_files': removed_files,
                'console_url': f"https://console.firebase.google.com/project/{self.firebase_project_id}/hosting/"
            }

        except Exception as e:
            print(f"❌ Failed to destroy Firebase Hosting site: {str(e)}")
            return {'success': False, 'error': str(e)}

    def optimize_for(self, optimization_target: str):
        """
        Cross-Cloud Magic: Optimize Firebase Hosting configuration for specific targets.
        
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
        
        # Minimize bandwidth usage
        self.compression(True)
        
        # Aggressive caching for static assets
        self.cache_static_assets(31536000)  # 1 year
        self.cache_html(3600)  # 1 hour
        
        # No custom monitoring (uses free Firebase analytics)
        self.analytics(True)
        self.performance_monitoring(False)
        self.error_reporting(False)
        
        # Add cost optimization labels
        self.hosting_labels.update({
            "optimization": "cost",
            "cost_management": "enabled",
            "tier": "free"
        })
        
        print("   ├─ 🗜️  Enabled compression")
        print("   ├─ 📦 Aggressive caching rules")
        print("   ├─ 📊 Using free analytics only")
        print("   └─ 🏷️  Added cost optimization labels")
        
        return self

    def _optimize_for_performance(self):
        """Optimize configuration for performance"""
        print("🏗️  Applying Cross-Cloud Magic: Performance Optimization")
        
        # Enable all performance features
        self.compression(True)
        self.cache_static_assets(31536000)  # 1 year
        self.cache_html(300)  # 5 minutes for dynamic updates
        
        # Performance monitoring
        self.performance_monitoring(True)
        
        # Optimize headers for performance
        self.header("**/*", "Vary", "Accept-Encoding")
        self.header("**/*.@(woff|woff2)", "Cache-Control", "max-age=31536000, immutable")
        
        # Add performance labels
        self.hosting_labels.update({
            "optimization": "performance",
            "caching": "aggressive",
            "compression": "enabled",
            "monitoring": "enabled"
        })
        
        print("   ├─ 🗜️  Enabled compression")
        print("   ├─ 📦 Optimized caching strategy")
        print("   ├─ 📊 Enabled performance monitoring")
        print("   ├─ 📋 Added performance headers")
        print("   └─ 🏷️  Added performance optimization labels")
        
        return self

    def _optimize_for_security(self):
        """Optimize configuration for security"""
        print("🏗️  Applying Cross-Cloud Magic: Security Optimization")
        
        # Enable all security features
        self.security_headers()
        self.strict_csp()
        
        # Additional security headers
        self.header("**/*", "Strict-Transport-Security", "max-age=31536000; includeSubDomains")
        self.header("**/*", "X-Permitted-Cross-Domain-Policies", "none")
        self.header("**/*", "Permissions-Policy", "geolocation=(), microphone=(), camera=()")
        
        # Disable CORS or restrict it
        self.cors([])  # No CORS
        
        # Enable monitoring for security
        self.error_reporting(True)
        
        # Add security labels
        self.hosting_labels.update({
            "optimization": "security",
            "security_level": "maximum",
            "headers": "strict",
            "csp": "enabled"
        })
        
        print("   ├─ 🔒 Enabled security headers")
        print("   ├─ 🛡️  Strict Content Security Policy")
        print("   ├─ 🚫 Disabled CORS")
        print("   ├─ 📊 Enabled error reporting")
        print("   └─ 🏷️  Added security optimization labels")
        
        return self

    def _optimize_for_user_experience(self):
        """Optimize configuration for user experience"""
        print("🏗️  Applying Cross-Cloud Magic: User Experience Optimization")
        
        # UX-focused configuration
        self.clean_urls(True)
        self.compression(True)
        
        # Balanced caching for good UX
        self.cache_static_assets(2592000)  # 30 days
        self.cache_html(1800)  # 30 minutes
        
        # Enable analytics for UX insights
        self.analytics(True)
        self.performance_monitoring(True)
        
        # Progressive enhancement headers
        self.header("**/*", "Accept-CH", "DPR, Width, Viewport-Width")
        
        # Add UX labels
        self.hosting_labels.update({
            "optimization": "user_experience",
            "ux_focused": "true",
            "clean_urls": "enabled",
            "analytics": "enabled"
        })
        
        print("   ├─ 🧹 Enabled clean URLs")
        print("   ├─ 🗜️  Enabled compression")
        print("   ├─ 📦 Balanced caching strategy")
        print("   ├─ 📊 Enabled analytics and monitoring")
        print("   └─ 🏷️  Added UX optimization labels")
        
        return self

    def _find_existing_site(self) -> Optional[Dict[str, Any]]:
        """Find existing Firebase Hosting site"""
        return self._fetch_current_hosting_state()

    def _create_new_site(self) -> Dict[str, Any]:
        """Create new Firebase Hosting site"""
        try:
            print(f"   📋 Project: {self.firebase_project_id}")
            if self.site_id_value:
                print(f"   🆔 Site ID: {self.site_id_value}")
            print(f"   📁 Public Directory: {self.public_directory_path}")
            if self.framework:
                print(f"   ⚛️  Framework: {self.framework.title()}")
            
            # Create Firebase configuration
            firebase_config = self._create_firebase_config()
            
            # Write firebase.json
            with open("firebase.json", 'w') as f:
                json.dump(firebase_config, f, indent=2)
            
            print(f"   📄 Created firebase.json")
            
            # Create .firebaserc
            firebaserc_config = self._create_firebaserc_config()
            
            with open(".firebaserc", 'w') as f:
                json.dump(firebaserc_config, f, indent=2)
            
            print(f"   📄 Created .firebaserc")
            
            # Run build command if specified
            if self.build_command_value:
                print(f"   🔨 Running build: {self.build_command_value}")
                try:
                    build_result = subprocess.run(
                        self.build_command_value, 
                        shell=True, 
                        capture_output=True, 
                        text=True,
                        cwd=self.build_directory_value or os.getcwd()
                    )
                    
                    if build_result.returncode != 0:
                        print(f"   ⚠️  Build warning: {build_result.stderr}")
                        print(f"   💡 Continuing with deployment...")
                    else:
                        print(f"   ✅ Build completed successfully")
                        
                except Exception as e:
                    print(f"   ⚠️  Build failed: {str(e)}")
                    print(f"   💡 Continuing with deployment...")
            
            # Check if public directory exists
            if not os.path.exists(self.public_directory_path):
                print(f"   ⚠️  Warning: Public directory '{self.public_directory_path}' not found")
                print(f"   💡 Creating empty directory for deployment")
                os.makedirs(self.public_directory_path, exist_ok=True)
                
                # Create a simple index.html if none exists
                index_path = os.path.join(self.public_directory_path, "index.html")
                if not os.path.exists(index_path):
                    self._create_default_index_html(index_path)
                    print(f"   📄 Created default index.html")
            
            # Show configured features
            features = []
            if self.single_page_app:
                features.append("SPA routing")
            if self.clean_urls:
                features.append("Clean URLs")
            if self.has_security_features():
                features.append("Security headers")
            if self.has_caching_configured():
                features.append("Caching rules")
            if self.compression_enabled:
                features.append("Compression")
            
            if features:
                print(f"   🚀 Features: {', '.join(features)}")
            
            # Show custom domains
            if self.custom_domains:
                print(f"   🌍 Custom Domains ({len(self.custom_domains)}):")
                for domain in self.custom_domains[:3]:
                    print(f"      • https://{domain}")
                if len(self.custom_domains) > 3:
                    print(f"      • ... and {len(self.custom_domains) - 3} more")
            
            # Deploy to Firebase Hosting using CLI
            deploy_result = self._deploy_to_firebase()
            
            console_url = f"https://console.firebase.google.com/project/{self.firebase_project_id}/hosting/"
            print(f"✅ Firebase Hosting configured successfully!")
            
            if deploy_result.get('success'):
                print(f"🚀 Deployed successfully!")
                if self.custom_domains:
                    for domain in self.custom_domains[:3]:
                        print(f"   🌐 https://{domain}")
                    if len(self.custom_domains) > 3:
                        print(f"   🌐 ... and {len(self.custom_domains) - 3} more")
            else:
                print(f"⚠️  Configuration created, deploy manually with: firebase deploy --only hosting")
            
            print(f"🌐 Console: {console_url}")
            
            return self._get_hosting_info()

        except Exception as e:
            print(f"❌ Failed to create Firebase Hosting site: {str(e)}")
            raise

    def _update_existing_site(self, existing_state: Dict[str, Any]):
        """Update existing Firebase Hosting site"""
        print(f"   🔄 Updating existing configuration")
        # For Firebase Hosting, we typically recreate the config
        return self._create_new_site()

    def _create_firebase_config(self) -> Dict[str, Any]:
        """Create firebase.json configuration"""
        hosting_config = {
            "public": self.public_directory_path,
            "ignore": self.ignore_patterns
        }
        
        # Add site targeting if specified
        if self.site_id_value:
            hosting_config["site"] = self.site_id_value
        
        # Add SPA configuration
        if self.single_page_app:
            hosting_config["rewrites"] = [{"source": "**", "destination": "/index.html"}]
        
        # Add custom rewrites
        if self.rewrites and not self.single_page_app:
            hosting_config["rewrites"] = self.rewrites
        elif self.rewrites and self.single_page_app:
            # Merge custom rewrites with SPA rewrite
            hosting_config["rewrites"] = self.rewrites + [{"source": "**", "destination": "/index.html"}]
        
        # Add redirects
        if self.redirects:
            hosting_config["redirects"] = self.redirects
        
        # Add headers
        if self.custom_headers:
            hosting_config["headers"] = self.custom_headers
        
        # Add clean URLs and trailing slash
        if self.clean_urls:
            hosting_config["cleanUrls"] = True
        
        if self.trailing_slash:
            hosting_config["trailingSlash"] = True
        
        # Add app association for mobile deep linking
        if self.app_association:
            hosting_config["appAssociation"] = self.app_association
        
        return {
            "hosting": hosting_config,
            "emulators": {
                "hosting": {
                    "port": 5000
                },
                "ui": {
                    "enabled": True
                }
            }
        }

    def _create_firebaserc_config(self) -> Dict[str, Any]:
        """Create .firebaserc configuration"""
        config = {
            "projects": {
                "default": self.firebase_project_id
            }
        }
        
        # Add site targeting if specified
        if self.site_id_value:
            config["targets"] = {
                self.firebase_project_id: {
                    "hosting": {
                        self.site_id_value: [self.site_id_value]
                    }
                }
            }
        
        return config

    def _create_default_index_html(self, file_path: str):
        """Create a default index.html file"""
        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{self.site_name}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            padding: 40px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            text-align: center;
        }}
        .container {{
            max-width: 600px;
        }}
        h1 {{
            font-size: 3rem;
            margin-bottom: 1rem;
            font-weight: 300;
        }}
        p {{
            font-size: 1.2rem;
            opacity: 0.9;
            line-height: 1.6;
        }}
        .badge {{
            display: inline-block;
            background: rgba(255,255,255,0.2);
            padding: 8px 16px;
            border-radius: 20px;
            font-size: 0.9rem;
            margin-top: 20px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🔥 {self.site_name}</h1>
        <p>Your Firebase Hosting site is ready!</p>
        <p>Replace this file with your actual content.</p>
        <div class="badge">Powered by Firebase Hosting</div>
    </div>
</body>
</html>"""
        
        with open(file_path, 'w') as f:
            f.write(html_content)

    def _deploy_to_firebase(self) -> Dict[str, Any]:
        """Deploy files to Firebase Hosting"""
        try:
            print(f"   🚀 Deploying to Firebase Hosting...")
            
            # Check if Firebase CLI is available
            firebase_check = subprocess.run(
                ["firebase", "--version"], 
                capture_output=True, 
                text=True
            )
            
            if firebase_check.returncode != 0:
                print(f"   ⚠️  Firebase CLI not found. Install with: npm install -g firebase-tools")
                return {'success': False, 'error': 'Firebase CLI not available'}
            
            # Deploy using Firebase CLI
            if self.site_id_value:
                deploy_cmd = ["firebase", "deploy", "--only", f"hosting:{self.site_id_value}"]
            else:
                deploy_cmd = ["firebase", "deploy", "--only", "hosting"]
            
            print(f"   🔄 Running: {' '.join(deploy_cmd)}")
            
            deploy_result = subprocess.run(
                deploy_cmd,
                capture_output=True,
                text=True,
                cwd=os.getcwd()
            )
            
            if deploy_result.returncode == 0:
                print(f"   ✅ Firebase deployment completed successfully!")
                
                # Parse output for URLs
                output_lines = deploy_result.stdout.split('\n')
                deployed_urls = []
                
                for line in output_lines:
                    if 'Hosting URL:' in line:
                        url = line.split('Hosting URL:')[-1].strip()
                        deployed_urls.append(url)
                    elif 'Project Console:' in line:
                        console_url = line.split('Project Console:')[-1].strip()
                
                return {
                    'success': True,
                    'deployed_urls': deployed_urls,
                    'deployment_output': deploy_result.stdout
                }
            else:
                print(f"   ❌ Firebase deployment failed:")
                print(f"   {deploy_result.stderr}")
                return {
                    'success': False, 
                    'error': deploy_result.stderr,
                    'stdout': deploy_result.stdout
                }
                
        except FileNotFoundError:
            print(f"   ⚠️  Firebase CLI not found. Install with: npm install -g firebase-tools")
            return {'success': False, 'error': 'Firebase CLI not found'}
        except Exception as e:
            print(f"   ❌ Deployment error: {str(e)}")
            return {'success': False, 'error': str(e)}

    def _get_hosting_info(self) -> Dict[str, Any]:
        """Get hosting information"""
        try:
            # Determine URLs
            hosting_urls = []
            if self.custom_domains:
                hosting_urls = [f"https://{domain}" for domain in self.custom_domains]
            
            default_url = None
            if self.site_id_value:
                default_url = f"https://{self.site_id_value}.web.app"
            elif self.firebase_project_id:
                default_url = f"https://{self.firebase_project_id}.web.app"
            
            if default_url:
                hosting_urls.insert(0, default_url)
            
            return {
                'success': True,
                'site_name': self.site_name,
                'site_id': self.site_id,
                'firebase_project_id': self.firebase_project_id,
                'site_description': self.site_description,
                'hosting_type': self._get_hosting_type_from_config(),
                'framework': self.framework,
                'public_directory': self.public_directory_path,
                'build_command': self.build_command_value,
                'hosting_urls': hosting_urls,
                'default_url': default_url,
                'custom_domains': self.custom_domains,
                'custom_domain_count': len(self.custom_domains),
                'single_page_app': self.single_page_app,
                'clean_urls': self.clean_urls,
                'trailing_slash': self.trailing_slash,
                'compression_enabled': self.compression_enabled,
                'has_security_features': self.has_security_features(),
                'has_caching_configured': self.has_caching_configured(),
                'redirect_count': self.get_redirect_count(),
                'rewrite_count': self.get_rewrite_count(),
                'header_count': self.get_header_count(),
                'analytics_enabled': self.analytics_enabled,
                'performance_monitoring': self.performance_monitoring,
                'github_integration': self.github_integration,
                'auto_deploy_branch': self.auto_deploy_branch,
                'is_production_ready': self.is_production_ready(),
                'labels': self.hosting_labels,
                'estimated_monthly_cost': f"${self._estimate_firebase_hosting_cost():.2f}",
                'console_url': f"https://console.firebase.google.com/project/{self.firebase_project_id}/hosting/"
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}