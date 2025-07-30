"""
Firebase Hosting Configuration Mixin

Configuration methods for Firebase Hosting.
Provides Rails-like method chaining for fluent static site hosting configuration.
"""

from typing import Dict, Any, List, Optional, Union


class FirebaseHostingConfigurationMixin:
    """
    Configuration mixin for Firebase Hosting.
    
    This mixin provides:
    - Chainable configuration methods for hosting setup
    - Domain and SSL management
    - Performance and caching configuration
    - Security headers and policies
    - Common hosting patterns (SPA, static site, documentation, blog)
    - Framework-specific configurations (React, Vue, Angular, Next.js)
    - Environment-specific settings (development, staging, production)
    """
    
    # ========== Project and Site Configuration ==========
    
    def project(self, project_id: str):
        """Set Firebase project ID"""
        self.firebase_project_id = project_id
        self.label("project", project_id)
        return self
    
    def site_id(self, site_id: str):
        """Set Firebase Hosting site ID"""
        if not self._is_valid_site_id(site_id):
            raise ValueError(f"Invalid site ID: {site_id}")
        self.site_id_value = site_id
        self.label("site_id", site_id)
        return self
    
    def description(self, description: str):
        """Set site description"""
        self.site_description = description
        return self
    
    def framework(self, framework_name: str):
        """Set frontend framework"""
        if not self._is_valid_framework(framework_name):
            raise ValueError(f"Unsupported framework: {framework_name}")
        self.framework = framework_name.lower()
        self.label("framework", framework_name.lower())
        return self
    
    # ========== Build and Deploy Configuration ==========
    
    def public_directory(self, directory: str):
        """Set public/build output directory"""
        self.public_directory_path = directory
        self.label("public_dir", directory)
        return self
    
    def build_command(self, command: str):
        """Set build command to run before deployment"""
        self.build_command_value = command
        return self
    
    def build_directory(self, directory: str):
        """Set build working directory"""
        self.build_directory_value = directory
        return self
    
    def build_env(self, key: str, value: str):
        """Add build environment variable"""
        self.build_env_vars[key] = value
        return self
    
    def build_env_vars(self, env_vars: Dict[str, str]):
        """Add multiple build environment variables"""
        self.build_env_vars.update(env_vars)
        return self
    
    # ========== Domain Configuration ==========
    
    def custom_domain(self, domain: str):
        """Add custom domain"""
        if not self._is_valid_domain(domain):
            raise ValueError(f"Invalid domain: {domain}")
        if domain not in self.custom_domains:
            self.custom_domains.append(domain)
        self.label("custom_domains", str(len(self.custom_domains)))
        return self
    
    def custom_domains(self, domains: List[str]):
        """Set multiple custom domains"""
        for domain in domains:
            if not self._is_valid_domain(domain):
                raise ValueError(f"Invalid domain: {domain}")
        self.custom_domains = domains
        self.label("custom_domains", str(len(domains)))
        return self
    
    def primary_domain(self, domain: str):
        """Set primary custom domain (first in list)"""
        if not self._is_valid_domain(domain):
            raise ValueError(f"Invalid domain: {domain}")
        if domain in self.custom_domains:
            self.custom_domains.remove(domain)
        self.custom_domains.insert(0, domain)
        self.label("primary_domain", domain)
        return self
    
    def ssl_certificate(self, domain: str, cert_config: Dict[str, Any]):
        """Configure SSL certificate for domain"""
        self.ssl_certificates[domain] = cert_config
        return self
    
    # ========== App Configuration ==========
    
    def single_page_app(self, enabled: bool = True):
        """Configure as single-page application"""
        self.single_page_app = enabled
        if enabled:
            # Add SPA rewrite rule
            self.rewrites = [{"source": "**", "destination": "/index.html"}]
        else:
            # Remove SPA rewrite rule
            self.rewrites = [r for r in self.rewrites if r.get("destination") != "/index.html"]
        self.label("spa", "true" if enabled else "false")
        return self
    
    def clean_urls(self, enabled: bool = True):
        """Enable clean URLs (remove .html extension)"""
        self.clean_urls = enabled
        self.label("clean_urls", "true" if enabled else "false")
        return self
    
    def trailing_slash(self, enabled: bool = False):
        """Control trailing slash behavior"""
        self.trailing_slash = enabled
        self.label("trailing_slash", "true" if enabled else "false")
        return self
    
    def app_association(self, association_config: Dict[str, Any]):
        """Configure mobile app deep linking"""
        self.app_association = association_config
        return self
    
    # ========== Performance Configuration ==========
    
    def compression(self, enabled: bool = True):
        """Enable/disable compression"""
        self.compression_enabled = enabled
        return self
    
    def cache_control(self, pattern: str, max_age: int, **kwargs):
        """Add cache control rule"""
        cache_rule = {"max_age": max_age}
        cache_rule.update(kwargs)
        self.cache_control[pattern] = cache_rule
        return self
    
    def cache_static_assets(self, max_age: int = 31536000):
        """Cache static assets (CSS, JS, images) for 1 year by default"""
        return self.cache_control("**/*.@(css|js|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)", max_age)
    
    def cache_html(self, max_age: int = 3600):
        """Cache HTML files for 1 hour by default"""
        return self.cache_control("**/*.html", max_age)
    
    def cache_api_responses(self, max_age: int = 300):
        """Cache API responses for 5 minutes by default"""
        return self.cache_control("**/api/**", max_age)
    
    # ========== Headers and Security ==========
    
    def header(self, pattern: str, key: str, value: str):
        """Add custom header rule"""
        header_rule = {"source": pattern, "headers": [{"key": key, "value": value}]}
        
        # Check if pattern already exists
        for i, existing_rule in enumerate(self.custom_headers):
            if existing_rule["source"] == pattern:
                # Add to existing rule
                existing_rule["headers"].append({"key": key, "value": value})
                return self
        
        # Add new rule
        self.custom_headers.append(header_rule)
        return self
    
    def headers(self, header_rules: List[Dict[str, Any]]):
        """Add multiple header rules"""
        self.custom_headers.extend(header_rules)
        return self
    
    def security_headers(self):
        """Add common security headers"""
        self.header("**/*", "X-Frame-Options", "DENY")
        self.header("**/*", "X-Content-Type-Options", "nosniff")
        self.header("**/*", "X-XSS-Protection", "1; mode=block")
        self.header("**/*", "Referrer-Policy", "strict-origin-when-cross-origin")
        self.label("security_headers", "enabled")
        return self
    
    def cors(self, origins: List[str] = None):
        """Configure CORS headers"""
        if origins is None:
            origins = ["*"]
        self.cors_origins = origins
        
        origin_value = ", ".join(origins) if len(origins) > 1 else origins[0]
        self.header("**/*", "Access-Control-Allow-Origin", origin_value)
        self.header("**/*", "Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
        self.header("**/*", "Access-Control-Allow-Headers", "Content-Type, Authorization")
        return self
    
    def content_security_policy(self, policy: str):
        """Set Content Security Policy"""
        self.content_security_policy = policy
        self.header("**/*", "Content-Security-Policy", policy)
        return self
    
    def strict_csp(self):
        """Set strict Content Security Policy"""
        policy = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self' https:; connect-src 'self' https:;"
        return self.content_security_policy(policy)
    
    # ========== Redirects and Rewrites ==========
    
    def redirect(self, source: str, destination: str, status_code: int = 301):
        """Add URL redirect"""
        redirect_rule = {
            "source": source,
            "destination": destination,
            "type": status_code
        }
        self.redirects.append(redirect_rule)
        return self
    
    def redirects(self, redirect_rules: List[Dict[str, Any]]):
        """Add multiple redirects"""
        self.redirects.extend(redirect_rules)
        return self
    
    def rewrite(self, source: str, destination: str):
        """Add URL rewrite rule"""
        rewrite_rule = {
            "source": source,
            "destination": destination
        }
        self.rewrites.append(rewrite_rule)
        return self
    
    def rewrites(self, rewrite_rules: List[Dict[str, Any]]):
        """Add multiple rewrites"""
        self.rewrites.extend(rewrite_rules)
        return self
    
    def api_proxy(self, path: str, function_name: str):
        """Proxy API requests to Firebase Function"""
        return self.rewrite(f"/{path}/**", f"/{function_name}")
    
    # ========== Deployment Configuration ==========
    
    def ignore_files(self, patterns: List[str]):
        """Set file patterns to ignore during deployment"""
        self.ignore_patterns = patterns
        return self
    
    def ignore_pattern(self, pattern: str):
        """Add single ignore pattern"""
        if pattern not in self.ignore_patterns:
            self.ignore_patterns.append(pattern)
        return self
    
    def preview_channels(self, channels: List[str]):
        """Configure preview channels"""
        self.preview_channels = channels
        return self
    
    # ========== CI/CD Configuration ==========
    
    def github_integration(self, enabled: bool = True, branch: str = "main"):
        """Enable GitHub integration"""
        self.github_integration = enabled
        self.auto_deploy_branch = branch
        self.label("ci_cd", "github")
        return self
    
    def auto_deploy(self, branch: str = "main"):
        """Configure auto-deployment from branch"""
        self.auto_deploy_branch = branch
        return self
    
    def managed_by_cicd(self):
        """Mark this resource as managed by CI/CD"""
        self.cicd_managed = True
        self.label("managed_by", "cicd")
        return self
    
    # ========== Monitoring Configuration ==========
    
    def analytics(self, enabled: bool = True):
        """Enable Firebase Analytics"""
        self.analytics_enabled = enabled
        self.label("analytics", "enabled" if enabled else "disabled")
        return self
    
    def performance_monitoring(self, enabled: bool = True):
        """Enable performance monitoring"""
        self.performance_monitoring = enabled
        self.label("performance_monitoring", "enabled" if enabled else "disabled")
        return self
    
    def error_reporting(self, enabled: bool = True):
        """Enable error reporting"""
        self.error_reporting = enabled
        self.label("error_reporting", "enabled" if enabled else "disabled")
        return self
    
    # ========== Framework-Specific Configurations ==========
    
    def react_app(self):
        """Rails convenience: React application"""
        return (self.framework("react")
                .public_directory("build")
                .build_command("npm run build")
                .single_page_app()
                .clean_urls()
                .cache_static_assets()
                .security_headers()
                .label("type", "react_app")
                .label("complexity", "medium"))
    
    def vue_app(self):
        """Rails convenience: Vue.js application"""
        return (self.framework("vue")
                .public_directory("dist")
                .build_command("npm run build")
                .single_page_app()
                .clean_urls()
                .cache_static_assets()
                .security_headers()
                .label("type", "vue_app")
                .label("complexity", "medium"))
    
    def angular_app(self):
        """Rails convenience: Angular application"""
        return (self.framework("angular")
                .public_directory("dist")
                .build_command("ng build --prod")
                .single_page_app()
                .clean_urls()
                .cache_static_assets()
                .security_headers()
                .label("type", "angular_app")
                .label("complexity", "medium"))
    
    def next_app(self):
        """Rails convenience: Next.js application"""
        return (self.framework("next")
                .public_directory("out")
                .build_command("npm run build && npm run export")
                .clean_urls()
                .cache_static_assets()
                .security_headers()
                .label("type", "next_app")
                .label("complexity", "high"))
    
    def nuxt_app(self):
        """Rails convenience: Nuxt.js application"""
        return (self.framework("nuxt")
                .public_directory("dist")
                .build_command("npm run generate")
                .clean_urls()
                .cache_static_assets()
                .security_headers()
                .label("type", "nuxt_app")
                .label("complexity", "high"))
    
    def gatsby_app(self):
        """Rails convenience: Gatsby application"""
        return (self.framework("gatsby")
                .public_directory("public")
                .build_command("gatsby build")
                .clean_urls()
                .cache_static_assets()
                .security_headers()
                .label("type", "gatsby_app")
                .label("complexity", "medium"))
    
    def vite_app(self):
        """Rails convenience: Vite application"""
        return (self.framework("vite")
                .public_directory("dist")
                .build_command("npm run build")
                .single_page_app()
                .clean_urls()
                .cache_static_assets()
                .security_headers()
                .label("type", "vite_app")
                .label("complexity", "medium"))
    
    # ========== Common Patterns ==========
    
    def static_site(self):
        """Rails convenience: Static HTML/CSS/JS site"""
        self.framework = "static"
        self.public_directory_path = "public"
        self.clean_urls = True
        self.trailing_slash = False
        self.label("type", "static_site")
        self.label("complexity", "basic")
        return self
        
    def web_app(self):
        """Rails convenience: Web application (SPA)"""
        self.framework = "react"
        self.public_directory_path = "dist"
        self.single_page_app = True
        self.clean_urls = True
        self.label("type", "web_app")
        self.label("complexity", "medium")
        return self
    
    def documentation_site(self):
        """Rails convenience: Documentation site"""
        return (self.framework("static")
                .public_directory("docs")
                .clean_urls()
                .trailing_slash(True)
                .cache_html(3600)
                .cache_static_assets()
                .security_headers()
                .label("type", "documentation")
                .label("complexity", "basic"))
    
    def blog_site(self):
        """Rails convenience: Blog/content site"""
        return (self.framework("static")
                .public_directory("public")
                .clean_urls()
                .trailing_slash(True)
                .cache_html(7200)  # 2 hours
                .cache_static_assets()
                .security_headers()
                .label("type", "blog")
                .label("complexity", "basic"))
    
    def portfolio_site(self):
        """Rails convenience: Portfolio site"""
        return (self.framework("static")
                .public_directory("dist")
                .clean_urls()
                .cache_static_assets(2592000)  # 30 days for images
                .security_headers()
                .label("type", "portfolio")
                .label("complexity", "basic"))
    
    def landing_page(self):
        """Rails convenience: Marketing landing page"""
        return (self.framework("static")
                .public_directory("dist")
                .clean_urls()
                .cache_html(1800)  # 30 minutes
                .cache_static_assets()
                .security_headers()
                .analytics()
                .performance_monitoring()
                .label("type", "landing_page")
                .label("complexity", "basic"))
    
    def ecommerce_frontend(self):
        """Rails convenience: E-commerce frontend"""
        return (self.react_app()
                .cache_html(300)  # 5 minutes for dynamic content
                .strict_csp()
                .analytics()
                .performance_monitoring()
                .error_reporting()
                .label("type", "ecommerce")
                .label("complexity", "high"))
    
    def dashboard_app(self):
        """Rails convenience: Admin dashboard"""
        return (self.react_app()
                .cache_html(0)  # No caching for dashboards
                .strict_csp()
                .security_headers()
                .cors(["https://api.yourdomain.com"])
                .label("type", "dashboard")
                .label("complexity", "high"))
    
    # ========== Environment-Specific Configurations ==========
    
    def development_site(self):
        """Rails convenience: Development environment"""
        return (self.public_directory("dist")
                .cache_html(0)  # No caching in dev
                .cors(["*"])
                .ignore_pattern("*.log")
                .ignore_pattern(".env*")
                .label("environment", "development")
                .label("caching", "disabled"))
    
    def staging_site(self):
        """Rails convenience: Staging environment"""
        return (self.public_directory("dist")
                .cache_html(300)  # 5 minutes
                .cache_static_assets(86400)  # 1 day
                .security_headers()
                .label("environment", "staging")
                .label("testing", "true"))
    
    def production_site(self):
        """Rails convenience: Production environment"""
        return (self.public_directory("dist")
                .cache_html(3600)  # 1 hour
                .cache_static_assets()  # 1 year
                .security_headers()
                .strict_csp()
                .analytics()
                .performance_monitoring()
                .error_reporting()
                .compression()
                .label("environment", "production")
                .label("optimized", "true"))
    
    # ========== Labels and Metadata ==========
    
    def label(self, key: str, value: str):
        """Add a label to the hosting site"""
        self.hosting_labels[key] = value
        return self
    
    def labels(self, labels_dict: Dict[str, str]):
        """Add multiple labels to the hosting site"""
        self.hosting_labels.update(labels_dict)
        return self
    
    def annotation(self, key: str, value: str):
        """Add an annotation to the hosting site"""
        self.hosting_annotations[key] = value
        return self
    
    def annotations(self, annotations_dict: Dict[str, str]):
        """Add multiple annotations to the hosting site"""
        self.hosting_annotations.update(annotations_dict)
        return self
    
    # ========== Utility Methods ==========
    
    def get_custom_domain_count(self) -> int:
        """Get the number of custom domains"""
        return len(self.custom_domains)
    
    def get_redirect_count(self) -> int:
        """Get the number of redirects"""
        return len(self.redirects)
    
    def get_rewrite_count(self) -> int:
        """Get the number of rewrites"""
        return len(self.rewrites)
    
    def get_header_count(self) -> int:
        """Get the number of custom headers"""
        return len(self.custom_headers)
    
    def has_custom_domains(self) -> bool:
        """Check if custom domains are configured"""
        return len(self.custom_domains) > 0
    
    def has_security_features(self) -> bool:
        """Check if security features are enabled"""
        return (self.content_security_policy is not None or
                any("X-Frame-Options" in str(header) for header in self.custom_headers))
    
    def has_caching_configured(self) -> bool:
        """Check if caching is configured"""
        return len(self.cache_control) > 0
    
    def is_single_page_app(self) -> bool:
        """Check if configured as SPA"""
        return self.single_page_app
    
    def is_production_ready(self) -> bool:
        """Check if site is configured for production"""
        return (self.has_custom_domains() and
                self.has_security_features() and
                self.has_caching_configured() and
                self.compression_enabled)
    
    def get_hosting_type(self) -> str:
        """Get hosting type from configuration"""
        return self._get_hosting_type_from_config()