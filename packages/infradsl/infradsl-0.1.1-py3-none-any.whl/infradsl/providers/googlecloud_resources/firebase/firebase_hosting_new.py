"""
Firebase Hosting Complete Implementation

Complete Firebase Hosting implementation combining core functionality, 
configuration methods, and lifecycle operations into a single modular class.
Rails-like API with Cross-Cloud Magic optimization.
"""

from typing import Dict, Any, List, Optional, Union
from .firebase_hosting_core import FirebaseHostingCore
from .firebase_hosting_configuration import FirebaseHostingConfigurationMixin
from .firebase_hosting_lifecycle import FirebaseHostingLifecycleMixin


class FirebaseHosting(FirebaseHostingCore, FirebaseHostingConfigurationMixin, FirebaseHostingLifecycleMixin):
    """
    Complete Firebase Hosting implementation.
    
    This class combines:
    - FirebaseHostingCore: Basic hosting attributes and authentication
    - FirebaseHostingConfigurationMixin: Chainable configuration methods
    - FirebaseHostingLifecycleMixin: Lifecycle operations (create, destroy, preview)
    
    Features:
    - Rails-like method chaining for fluent hosting configuration
    - Smart state management and drift detection
    - Cross-Cloud Magic optimization
    - Complete static site hosting (SPAs, static sites, documentation)
    - Framework support (React, Vue, Angular, Next.js, Nuxt, Gatsby)
    - Custom domains with automatic SSL
    - Performance optimization (caching, compression, CDN)
    - Security features (headers, CSP, CORS)
    - Common hosting patterns (documentation, blog, portfolio, landing pages)
    - Environment-specific settings (development, staging, production)
    
    Example:
        # React application
        app = FirebaseHosting("my-react-app")
        app.project("my-firebase-project").react_app()
        app.create()
        
        # Documentation site
        docs = FirebaseHosting("docs-site")
        docs.project("my-project").documentation_site()
        docs.custom_domain("docs.mydomain.com")
        docs.create()
        
        # Portfolio site
        portfolio = FirebaseHosting("portfolio")
        portfolio.project("my-project").portfolio_site()
        portfolio.custom_domain("portfolio.dev")
        portfolio.create()
        
        # Landing page
        landing = FirebaseHosting("landing")
        landing.project("marketing-project").landing_page()
        landing.custom_domains(["landing.com", "www.landing.com"])
        landing.create()
        
        # Custom configuration
        site = FirebaseHosting("custom-site")
        site.project("my-project").framework("vue")
        site.public_directory("dist").build_command("npm run build")
        site.single_page_app().clean_urls().security_headers()
        site.custom_domain("app.mydomain.com")
        site.cache_static_assets().compression()
        site.create()
        
        # Next.js application
        nextjs = FirebaseHosting("nextjs-app")
        nextjs.project("my-project").next_app()
        nextjs.custom_domain("app.example.com")
        nextjs.create()
        
        # Production-ready site
        prod = FirebaseHosting("production-site")
        prod.project("prod-project").react_app()
        prod.production_site()
        prod.custom_domains(["app.com", "www.app.com"])
        prod.create()
        
        # Cross-Cloud Magic optimization
        optimized = FirebaseHosting("optimized-site")
        optimized.project("my-project").vue_app()
        optimized.optimize_for("performance")
        optimized.create()
    """
    
    def __init__(self, name: str):
        """
        Initialize Firebase Hosting with site name.
        
        Args:
            name: Hosting site name
        """
        # Initialize all parent classes
        FirebaseHostingCore.__init__(self, name)
        
        # Ensure proper initialization order
        self._initialize_managers()
        
    def __repr__(self) -> str:
        """String representation of Firebase Hosting instance"""
        hosting_type = self._get_hosting_type_from_config()
        domain_info = f"{len(self.custom_domains)} domains" if self.custom_domains else "default domain"
        framework_info = f"{self.framework}" if self.framework else "static"
        status = "configured" if self.firebase_project_id else "unconfigured"
        
        return (f"FirebaseHosting(name='{self.site_name}', "
                f"type='{hosting_type}', "
                f"framework='{framework_info}', "
                f"domains='{domain_info}', "
                f"project='{self.firebase_project_id}', "
                f"status='{status}')")
    
    def summary(self) -> Dict[str, Any]:
        """
        Get comprehensive summary of Firebase Hosting configuration.
        
        Returns:
            Dict containing all configuration details
        """
        # Analyze hosting configuration
        hosting_features = []
        if self.single_page_app:
            hosting_features.append("single_page_app")
        if self.clean_urls:
            hosting_features.append("clean_urls")
        if self.compression_enabled:
            hosting_features.append("compression")
        if self.has_security_features():
            hosting_features.append("security_headers")
        if self.has_caching_configured():
            hosting_features.append("caching_rules")
        
        # Categorize by hosting purpose
        hosting_categories = []
        if self.framework in ["react", "vue", "angular", "svelte"]:
            hosting_categories.append("spa_framework")
        elif self.framework in ["next", "nuxt", "gatsby"]:
            hosting_categories.append("static_generator")
        elif self.framework == "static":
            hosting_categories.append("static_site")
        
        # Analyze performance features
        performance_features = []
        if self.compression_enabled:
            performance_features.append("compression")
        if self.has_caching_configured():
            performance_features.append("caching")
        if len(self.custom_domains) > 0:
            performance_features.append("custom_domains")
        if self.analytics_enabled:
            performance_features.append("analytics")
        
        # Security analysis
        security_features = []
        if self.has_security_features():
            security_features.append("security_headers")
        if self.content_security_policy:
            security_features.append("content_security_policy")
        if len(self.cors_origins) > 0:
            security_features.append("cors_configured")
        
        summary = {
            "site_name": self.site_name,
            "site_id": self.site_id,
            "firebase_project_id": self.firebase_project_id,
            "site_description": self.site_description,
            "hosting_type": self._get_hosting_type_from_config(),
            "hosting_categories": hosting_categories,
            
            # Framework and build
            "framework": self.framework,
            "public_directory": self.public_directory,
            "build_command": self.build_command,
            "build_directory": self.build_directory,
            "build_env_vars": self.build_env_vars,
            
            # Domains and URLs
            "custom_domains": self.custom_domains,
            "custom_domain_count": len(self.custom_domains),
            "domain_configs": self.domain_configs,
            "ssl_certificates": self.ssl_certificates,
            
            # App configuration
            "single_page_app": self.single_page_app,
            "clean_urls": self.clean_urls,
            "trailing_slash": self.trailing_slash,
            "app_association": self.app_association,
            
            # Performance
            "performance_features": performance_features,
            "compression_enabled": self.compression_enabled,
            "cache_control": self.cache_control,
            "cache_rule_count": len(self.cache_control),
            
            # Headers and routing
            "custom_headers": self.custom_headers,
            "header_count": len(self.custom_headers),
            "redirects": self.redirects,
            "redirect_count": len(self.redirects),
            "rewrites": self.rewrites,
            "rewrite_count": len(self.rewrites),
            
            # Security
            "security_features": security_features,
            "has_security_features": self.has_security_features(),
            "content_security_policy": self.content_security_policy,
            "cors_origins": self.cors_origins,
            
            # Deployment
            "ignore_patterns": self.ignore_patterns,
            "ignore_pattern_count": len(self.ignore_patterns),
            "preview_channels": self.preview_channels,
            
            # CI/CD
            "github_integration": self.github_integration,
            "auto_deploy_branch": self.auto_deploy_branch,
            
            # Monitoring
            "analytics_enabled": self.analytics_enabled,
            "performance_monitoring": self.performance_monitoring,
            "error_reporting": self.error_reporting,
            
            # Features analysis
            "hosting_features": hosting_features,
            "has_custom_domains": self.has_custom_domains(),
            "has_caching_configured": self.has_caching_configured(),
            "is_production_ready": self.is_production_ready(),
            
            # Labels and metadata
            "labels": self.hosting_labels,
            "label_count": len(self.hosting_labels),
            "annotations": self.hosting_annotations,
            
            # State
            "state": {
                "exists": self.site_exists,
                "deployed": self.site_deployed,
                "deployment_status": self.deployment_status,
                "last_deployment": self.last_deployment,
                "deployment_count": self.deployment_count
            },
            
            # Cost
            "estimated_monthly_cost": f"${self._estimate_firebase_hosting_cost():.2f}",
            "is_free_tier": self._estimate_firebase_hosting_cost() == 0.0
        }
        
        return summary
    
    def display_config(self):
        """Display current configuration in human-readable format"""
        print(f"\n🔥 Firebase Hosting Configuration: {self.site_name}")
        print(f"   📁 Firebase Project: {self.firebase_project_id}")
        if self.site_id:
            print(f"   🆔 Site ID: {self.site_id}")
        print(f"   📝 Description: {self.site_description}")
        print(f"   🎯 Hosting Type: {self._get_hosting_type_from_config().replace('_', ' ').title()}")
        
        # Framework and build
        if self.framework:
            print(f"   ⚛️  Framework: {self.framework.title()}")
        print(f"   📁 Public Directory: {self.public_directory}")
        if self.build_command:
            print(f"   🔨 Build Command: {self.build_command}")
        if self.build_directory:
            print(f"   📁 Build Directory: {self.build_directory}")
        
        # URLs and domains
        print(f"\n🌐 Hosting URLs:")
        if self.site_id:
            print(f"   🔵 Default: https://{self.site_id}.web.app")
        elif self.firebase_project_id:
            print(f"   🔵 Default: https://{self.firebase_project_id}.web.app")
        
        if self.custom_domains:
            print(f"   🌍 Custom Domains ({len(self.custom_domains)}):")
            for domain in self.custom_domains:
                print(f"      • https://{domain}")
        else:
            print(f"   🌍 Custom Domains: None")
        
        # App configuration
        print(f"\n⚙️  App Configuration:")
        print(f"   🔄 Single Page App: {'✅ Yes' if self.single_page_app else '❌ No'}")
        print(f"   🧹 Clean URLs: {'✅ Enabled' if self.clean_urls else '❌ Disabled'}")
        print(f"   📄 Trailing Slash: {'✅ Enabled' if self.trailing_slash else '❌ Disabled'}")
        print(f"   🗜️  Compression: {'✅ Enabled' if self.compression_enabled else '❌ Disabled'}")
        
        # Performance and caching
        print(f"\n🚀 Performance Configuration:")
        cache_rules = len(self.cache_control)
        print(f"   📦 Cache Rules: {cache_rules}")
        if cache_rules > 0:
            for pattern, rule in list(self.cache_control.items())[:3]:
                max_age_hours = rule['max_age'] // 3600 if rule['max_age'] >= 3600 else 0
                if max_age_hours > 0:
                    print(f"      • {pattern}: {max_age_hours}h")
                else:
                    print(f"      • {pattern}: {rule['max_age']}s")
            if cache_rules > 3:
                print(f"      • ... and {cache_rules - 3} more rules")
        
        # Headers and routing
        if self.custom_headers:
            print(f"\n📋 Custom Headers ({len(self.custom_headers)}):")
            for header_rule in self.custom_headers[:3]:
                pattern = header_rule.get('source', 'unknown')
                header_count = len(header_rule.get('headers', []))
                print(f"   • {pattern}: {header_count} headers")
            if len(self.custom_headers) > 3:
                print(f"   • ... and {len(self.custom_headers) - 3} more rules")
        
        if self.redirects:
            print(f"\n➡️  Redirects ({len(self.redirects)}):")
            for redirect in self.redirects[:3]:
                source = redirect.get('source', 'unknown')
                destination = redirect.get('destination', 'unknown')
                status = redirect.get('type', 301)
                print(f"   • {source} → {destination} ({status})")
            if len(self.redirects) > 3:
                print(f"   • ... and {len(self.redirects) - 3} more")
        
        if self.rewrites:
            print(f"\n🔄 Rewrites ({len(self.rewrites)}):")
            for rewrite in self.rewrites[:3]:
                source = rewrite.get('source', 'unknown')
                destination = rewrite.get('destination', 'unknown')
                print(f"   • {source} → {destination}")
            if len(self.rewrites) > 3:
                print(f"   • ... and {len(self.rewrites) - 3} more")
        
        # Security
        print(f"\n🔒 Security Configuration:")
        print(f"   🛡️  Security Headers: {'✅ Enabled' if self.has_security_features() else '❌ None'}")
        if self.content_security_policy:
            print(f"   📜 Content Security Policy: ✅ Configured")
        if self.cors_origins:
            if self.cors_origins == ["*"]:
                print(f"   🌍 CORS: ✅ Allow all origins")
            else:
                print(f"   🌍 CORS: ✅ {len(self.cors_origins)} origins")
        
        # Deployment configuration
        if self.ignore_patterns:
            print(f"\n🚫 Ignore Patterns ({len(self.ignore_patterns)}):")
            for pattern in self.ignore_patterns[:5]:
                print(f"   • {pattern}")
            if len(self.ignore_patterns) > 5:
                print(f"   • ... and {len(self.ignore_patterns) - 5} more")
        
        # CI/CD
        if self.github_integration:
            print(f"\n🔄 CI/CD Integration:")
            print(f"   📱 GitHub: ✅ Enabled")
            if self.auto_deploy_branch:
                print(f"   🌿 Auto-deploy: {self.auto_deploy_branch} branch")
        
        # Monitoring
        monitoring_features = []
        if self.analytics_enabled:
            monitoring_features.append("Analytics")
        if self.performance_monitoring:
            monitoring_features.append("Performance Monitoring")
        if self.error_reporting:
            monitoring_features.append("Error Reporting")
        
        if monitoring_features:
            print(f"\n📊 Monitoring: {', '.join(monitoring_features)}")
        
        # Labels
        if self.hosting_labels:
            print(f"\n🏷️  Labels ({len(self.hosting_labels)}):")
            for key, value in list(self.hosting_labels.items())[:5]:
                print(f"   • {key}: {value}")
            if len(self.hosting_labels) > 5:
                print(f"   • ... and {len(self.hosting_labels) - 5} more")
        
        # Production readiness
        production_ready = self.is_production_ready()
        print(f"\n🚀 Production Readiness: {'✅ Ready' if production_ready else '⚠️  Needs optimization'}")
        if not production_ready:
            issues = []
            if not self.has_custom_domains():
                issues.append("No custom domains")
            if not self.has_security_features():
                issues.append("No security headers")
            if not self.has_caching_configured():
                issues.append("No caching rules")
            if not self.compression_enabled:
                issues.append("Compression disabled")
            
            for issue in issues[:3]:
                print(f"   ⚠️  {issue}")
        
        # Cost
        cost = self._estimate_firebase_hosting_cost()
        if cost > 0:
            print(f"\n💰 Estimated Cost: ${cost:.2f}/month")
        else:
            print(f"\n💰 Cost: Free tier")
        
        # Console link
        if self.firebase_project_id:
            print(f"\n🌐 Firebase Console:")
            print(f"   🔗 https://console.firebase.google.com/project/{self.firebase_project_id}/hosting/")
    
    def analyze_performance(self) -> Dict[str, Any]:
        """
        Analyze Firebase Hosting performance configuration and provide recommendations.
        
        Returns:
            Dict containing performance analysis and recommendations
        """
        analysis = {
            "performance_score": 0,
            "max_score": 100,
            "recommendations": [],
            "performance_features": [],
            "bottlenecks": []
        }
        
        # Compression analysis
        if self.compression_enabled:
            analysis["performance_score"] += 20
            analysis["performance_features"].append("Compression enabled")
        else:
            analysis["bottlenecks"].append("Compression disabled")
            analysis["recommendations"].append("Enable compression for faster loading")
        
        # Caching analysis
        if self.has_caching_configured():
            analysis["performance_score"] += 25
            analysis["performance_features"].append("Caching rules configured")
            
            # Check for static asset caching
            has_static_caching = any("css" in pattern or "js" in pattern for pattern in self.cache_control.keys())
            if has_static_caching:
                analysis["performance_score"] += 15
                analysis["performance_features"].append("Static asset caching")
        else:
            analysis["bottlenecks"].append("No caching rules")
            analysis["recommendations"].append("Configure caching for static assets")
        
        # CDN analysis (Firebase Hosting has built-in CDN)
        analysis["performance_score"] += 20
        analysis["performance_features"].append("Global CDN (Firebase)")
        
        # Domain analysis
        if self.has_custom_domains():
            analysis["performance_score"] += 10
            analysis["performance_features"].append("Custom domains configured")
        
        # Clean URLs
        if self.clean_urls:
            analysis["performance_score"] += 5
            analysis["performance_features"].append("Clean URLs enabled")
        
        # Framework-specific optimizations
        if self.framework in ["next", "nuxt", "gatsby"]:
            analysis["performance_score"] += 5
            analysis["performance_features"].append("Static site generator")
        
        return analysis
    
    def analyze_security(self) -> Dict[str, Any]:
        """
        Analyze Firebase Hosting security configuration and provide recommendations.
        
        Returns:
            Dict containing security analysis and recommendations
        """
        analysis = {
            "security_score": 0,
            "max_score": 100,
            "recommendations": [],
            "security_features": [],
            "vulnerabilities": []
        }
        
        # Security headers analysis
        if self.has_security_features():
            analysis["security_score"] += 30
            analysis["security_features"].append("Security headers configured")
        else:
            analysis["vulnerabilities"].append("No security headers")
            analysis["recommendations"].append("Enable security headers")
        
        # Content Security Policy
        if self.content_security_policy:
            analysis["security_score"] += 25
            analysis["security_features"].append("Content Security Policy")
        else:
            analysis["recommendations"].append("Configure Content Security Policy")
        
        # HTTPS (Firebase Hosting enforces HTTPS)
        analysis["security_score"] += 20
        analysis["security_features"].append("HTTPS enforced (Firebase)")
        
        # Custom domains with SSL
        if self.has_custom_domains():
            analysis["security_score"] += 15
            analysis["security_features"].append("Custom domains with SSL")
        
        # CORS configuration
        if self.cors_origins and self.cors_origins != ["*"]:
            analysis["security_score"] += 10
            analysis["security_features"].append("CORS properly configured")
        elif self.cors_origins == ["*"]:
            analysis["vulnerabilities"].append("CORS allows all origins")
            analysis["recommendations"].append("Restrict CORS origins")
        
        return analysis
    
    # Utility methods for backwards compatibility
    def get_status(self) -> Dict[str, Any]:
        """Get hosting status for backwards compatibility"""
        return {
            "site_name": self.site_name,
            "site_id": self.site_id,
            "firebase_project_id": self.firebase_project_id,
            "hosting_type": self._get_hosting_type_from_config(),
            "framework": self.framework,
            "public_directory": self.public_directory,
            "custom_domains": self.custom_domains,
            "custom_domain_count": len(self.custom_domains),
            "single_page_app": self.single_page_app,
            "has_custom_domains": self.has_custom_domains(),
            "has_security_features": self.has_security_features(),
            "has_caching_configured": self.has_caching_configured(),
            "is_production_ready": self.is_production_ready(),
            "estimated_cost": f"${self._estimate_firebase_hosting_cost():.2f}/month"
        }

    # Required abstract methods implementation
    def create(self) -> Dict[str, Any]:
        """Create Firebase Hosting site"""
        # Call the real lifecycle create method that handles build and deploy
        return FirebaseHostingLifecycleMixin.create(self)
        
    def destroy(self) -> Dict[str, Any]:
        """Destroy Firebase Hosting site"""
        # Call the real lifecycle destroy method
        return FirebaseHostingLifecycleMixin.destroy(self)
        
    def preview(self) -> Dict[str, Any]:
        """Preview Firebase Hosting configuration"""
        # Call the real lifecycle preview method  
        return FirebaseHostingLifecycleMixin.preview(self)
        
    def _fetch_current_cloud_state(self) -> Dict[str, Any]:
        """Fetch current Firebase Hosting state"""
        # Simulate fetching current state
        return {
            "exists": False,  # Simplified for now
            "site_name": self.site_name,
            "site_id": self.site_id,
            "firebase_project_id": self.firebase_project_id
        }


# Convenience function for creating Firebase Hosting instances
def create_firebase_hosting(name: str) -> FirebaseHosting:
    """
    Create a new Firebase Hosting instance.
    
    Args:
        name: Hosting site name
        
    Returns:
        FirebaseHosting instance
    """
    return FirebaseHosting(name)


# Export the class for easy importing
__all__ = ['FirebaseHosting', 'create_firebase_hosting']