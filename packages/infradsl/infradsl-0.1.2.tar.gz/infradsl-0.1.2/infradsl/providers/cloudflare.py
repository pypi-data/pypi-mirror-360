"""
Cloudflare Provider

Rails-like interface for Cloudflare services.
Makes Cloudflare as easy to use as Rails for web apps.
"""

from .cloudflare_resources.dns import DNS
from .cloudflare_resources.workers import Workers
from .cloudflare_resources.cdn import CDN
from .cloudflare_resources.ssl import SSL
from .cloudflare_resources.pages import Pages
from .cloudflare_resources.r2_storage import R2Storage
from .cloudflare_resources.kv_storage import KVStorage
from .cloudflare_resources.firewall import Firewall
from .cloudflare_resources.ddos_protection import DDOSProtection


class Cloudflare:
    """
    Cloudflare provider with Rails-like simplicity.

    Makes Cloudflare services as easy to use as Rails for web apps.
    """

    @staticmethod
    def DNS(domain: str) -> DNS:
        """
        Create DNS configuration with Rails-like simplicity.

        Args:
            domain: Domain name to manage DNS for

        Returns:
            DNS: A configured DNS instance ready for chaining

        Examples:
            # Simple domain setup
            dns = (Cloudflare.DNS("myapp.com")
                   .a_record("@", "192.168.1.1")
                   .a_record("www", "192.168.1.1")
                   .create())

            # Complete domain with email
            domain = (Cloudflare.DNS("myapp.com")
                      .web_app("192.168.1.1")
                      .google_workspace()
                      .create())

            # API subdomain
            api = (Cloudflare.DNS("myapp.com")
                   .cname_record("api", "api.herokuapp.com")
                   .create())
        """
        return DNS(domain)

    @staticmethod
    def Workers(name: str) -> Workers:
        """
        Create Workers (edge functions) with Rails-like simplicity.

        Args:
            name: Name of the worker

        Returns:
            Workers: A configured Workers instance ready for chaining

        Examples:
            # Simple API endpoint
            worker = (Cloudflare.Workers("api-endpoint")
                      .script("./worker.js")
                      .route("api.myapp.com/*")
                      .create())

            # Authentication middleware
            auth = (Cloudflare.Workers("auth-service")
                    .auth_middleware("app.myapp.com", "./auth.js", "jwt-secret")
                    .create())

            # Scheduled worker
            cron = (Cloudflare.Workers("daily-cleanup")
                    .scheduled_worker("./cleanup.js", "0 2 * * *")
                    .create())
        """
        return Workers(name)

    @staticmethod
    def CDN(domain: str) -> CDN:
        """
        Create CDN configuration with Rails-like simplicity.

        Args:
            domain: Domain name to configure CDN for

        Returns:
            CDN: A configured CDN instance ready for chaining

        Examples:
            # Static site CDN
            cdn = (Cloudflare.CDN("myapp.com")
                   .static_site()
                   .create())

            # E-commerce site with custom rules
            shop = (Cloudflare.CDN("shop.myapp.com")
                    .ecommerce_site()
                    .create())

            # API backend (no caching)
            api = (Cloudflare.CDN("api.myapp.com")
                   .api_backend()
                   .create())
        """
        return CDN(domain)

    @staticmethod
    def Worker(name: str) -> Workers:
        """
        Alias for Workers (common usage pattern).

        Args:
            name: Name of the worker

        Returns:
            Workers: A configured Workers instance ready for chaining
        """
        return Cloudflare.Workers(name)

    @staticmethod
    def Zone(domain: str) -> DNS:
        """
        Alias for DNS (Cloudflare terminology).

        Args:
            domain: Domain name to manage

        Returns:
            DNS: A configured DNS instance ready for chaining
        """
        return Cloudflare.DNS(domain)

    @staticmethod
    def SSL(domain: str) -> SSL:
        """
        Create SSL/TLS certificate configuration with Rails-like simplicity.

        Args:
            domain: Domain name to configure SSL for

        Returns:
            SSL: A configured SSL instance ready for chaining

        Examples:
            # Universal SSL (free)
            ssl = (Cloudflare.SSL("myapp.com")
                   .universal_ssl()
                   .create())

            # Advanced certificate with custom settings
            advanced = (Cloudflare.SSL("myapp.com")
                        .advanced_certificate()
                        .min_tls_version("1.2")
                        .cipher_suites(["ECDHE-RSA-AES128-GCM-SHA256"])
                        .create())

            # Origin certificate for backend
            origin = (Cloudflare.SSL("myapp.com")
                      .origin_certificate()
                      .hostnames(["myapp.com", "*.myapp.com"])
                      .create())
        """
        return SSL(domain)

    @staticmethod
    def Pages(project_name: str) -> Pages:
        """
        Create Pages (static site hosting) with Rails-like simplicity.

        Args:
            project_name: Name of the Pages project

        Returns:
            Pages: A configured Pages instance ready for chaining

        Examples:
            # GitHub integration
            site = (Cloudflare.Pages("my-website")
                    .github_repo("myorg/website")
                    .build_command("npm run build")
                    .output_dir("dist")
                    .create())

            # Direct upload
            upload = (Cloudflare.Pages("portfolio")
                      .upload_directory("./build")
                      .custom_domain("portfolio.myapp.com")
                      .create())

            # Framework-specific deployment
            nextjs = (Cloudflare.Pages("nextjs-app")
                      .nextjs_app("myorg/nextjs-app")
                      .create())
        """
        return Pages(project_name)

    @staticmethod
    def R2(bucket_name: str) -> R2Storage:
        """
        Create R2 Storage (S3-compatible) with Rails-like simplicity.

        Args:
            bucket_name: Name of the R2 bucket

        Returns:
            R2Storage: A configured R2Storage instance ready for chaining

        Examples:
            # Private bucket
            private = (Cloudflare.R2("private-data")
                       .private_bucket()
                       .create())

            # Public bucket for website assets
            public = (Cloudflare.R2("static-assets")
                      .public_bucket()
                      .website_hosting()
                      .create())

            # Backup bucket with lifecycle
            backup = (Cloudflare.R2("backups")
                      .lifecycle_rule("archive", 30)
                      .create())
        """
        return R2Storage(bucket_name)

    @staticmethod
    def R2Storage(bucket_name: str) -> R2Storage:
        """
        Alias for R2 (full name).

        Args:
            bucket_name: Name of the R2 bucket

        Returns:
            R2Storage: A configured R2Storage instance ready for chaining
        """
        return Cloudflare.R2(bucket_name)

    @staticmethod
    def KV(namespace: str) -> KVStorage:
        """
        Create KV Storage (edge key-value store) with Rails-like simplicity.

        Args:
            namespace: Name of the KV namespace

        Returns:
            KVStorage: A configured KVStorage instance ready for chaining

        Examples:
            # Session storage
            sessions = (Cloudflare.KV("user-sessions")
                        .session_store()
                        .create())

            # Configuration cache
            config = (Cloudflare.KV("app-config")
                      .configuration_cache()
                      .create())

            # Feature flags
            flags = (Cloudflare.KV("feature-flags")
                     .feature_flags()
                     .create())
        """
        return KVStorage(namespace)

    @staticmethod
    def KVStorage(namespace: str) -> KVStorage:
        """
        Alias for KV (full name).

        Args:
            namespace: Name of the KV namespace

        Returns:
            KVStorage: A configured KVStorage instance ready for chaining
        """
        return Cloudflare.KV(namespace)

    @staticmethod
    def Firewall(domain: str) -> Firewall:
        """
        Create Web Application Firewall with Rails-like simplicity.

        Args:
            domain: Domain name to configure firewall for

        Returns:
            Firewall: A configured Firewall instance ready for chaining

        Examples:
            # Basic protection
            basic = (Cloudflare.Firewall("myapp.com")
                     .basic_protection()
                     .create())

            # E-commerce protection
            ecommerce = (Cloudflare.Firewall("shop.myapp.com")
                         .ecommerce_protection()
                         .create())

            # Custom rules
            custom = (Cloudflare.Firewall("api.myapp.com")
                      .rate_limit("/api", 100)
                      .block_country(["CN", "RU"])
                      .create())
        """
        return Firewall(domain)

    @staticmethod
    def WAF(domain: str) -> Firewall:
        """
        Alias for Firewall (Web Application Firewall).

        Args:
            domain: Domain name to configure firewall for

        Returns:
            Firewall: A configured Firewall instance ready for chaining
        """
        return Cloudflare.Firewall(domain)

    @staticmethod
    def DDoSProtection(domain: str) -> DDOSProtection:
        """
        Create DDoS Protection with Rails-like simplicity.

        Args:
            domain: Domain name to configure DDoS protection for

        Returns:
            DDOSProtection: A configured DDOSProtection instance ready for chaining

        Examples:
            # Standard protection
            standard = (Cloudflare.DDoSProtection("myapp.com")
                        .standard_protection()
                        .create())

            # Advanced protection for high-traffic sites
            advanced = (Cloudflare.DDoSProtection("enterprise.myapp.com")
                        .advanced_protection()
                        .sensitivity("high")
                        .create())

            # Gaming/streaming protection
            gaming = (Cloudflare.DDoSProtection("game.myapp.com")
                      .gaming_protection()
                      .create())
        """
        return DDOSProtection(domain)

    @staticmethod
    def DDoS(domain: str) -> DDOSProtection:
        """
        Alias for DDoSProtection (shorter name).

        Args:
            domain: Domain name to configure DDoS protection for

        Returns:
            DDOSProtection: A configured DDOSProtection instance ready for chaining
        """
        return Cloudflare.DDoSProtection(domain)

    @staticmethod
    def authenticate():
        """
        Test Cloudflare authentication.

        This method will attempt to authenticate with Cloudflare using
        environment variables and return the authentication status.

        Environment Variables Required:
            Either:
            - CLOUDFLARE_API_TOKEN (recommended)
            Or:
            - CLOUDFLARE_API_KEY and CLOUDFLARE_EMAIL

        Optional:
            - CLOUDFLARE_ZONE_ID (for faster operations)

        Returns:
            Dict containing authentication result

        Examples:
            # Test authentication
            result = Cloudflare.authenticate()
            if result['authenticated']:
                print("✅ Cloudflare authentication successful!")
            else:
                print(f"❌ Authentication failed: {result['error']}")
        """
        from .cloudflare_resources.auth_service import CloudflareAuthenticationService

        try:
            success = CloudflareAuthenticationService.authenticate(silent=False)
            if success:
                return {
                    'provider': 'cloudflare',
                    'authenticated': True,
                    'message': 'Cloudflare authentication successful'
                }
            else:
                return {
                    'provider': 'cloudflare',
                    'authenticated': False,
                    'error': 'Authentication failed - check your credentials'
                }
        except Exception as e:
            return {
                'provider': 'cloudflare',
                'authenticated': False,
                'error': str(e)
            }

    @staticmethod
    def version() -> str:
        """Get the Cloudflare provider version."""
        return "1.0.0"

    @staticmethod
    def help() -> str:
        """
        Get help information for Cloudflare provider.

        Returns:
            str: Comprehensive help text
        """
        return """
Cloudflare Provider Help
========================

The Cloudflare provider brings Rails-like simplicity to Cloudflare services.

🌐 Available Services:
---------------------
• DNS              - Lightning-fast domain management
• Workers          - Edge computing functions
• CDN              - Global edge caching and optimization
• SSL/TLS          - Universal SSL certificates
• Pages            - Static site hosting
• R2 Storage       - S3-compatible object storage
• KV Storage       - Edge key-value store
• Firewall (WAF)   - Web application firewall
• DDoS Protection  - Advanced threat protection

🔐 Authentication:
-----------------
Set one of these environment variable combinations:

Option 1 (Recommended):
  CLOUDFLARE_API_TOKEN=your_api_token

Option 2 (Legacy):
  CLOUDFLARE_API_KEY=your_api_key
  CLOUDFLARE_EMAIL=your_email

Optional:
  CLOUDFLARE_ZONE_ID=your_zone_id  # For faster operations

🚀 Quick Examples:
-----------------

# DNS Management
dns = (Cloudflare.DNS("myapp.com")
       .web_app("192.168.1.1")
       .google_workspace()
       .create())

# Edge Workers
worker = (Cloudflare.Workers("api")
          .script("./api-worker.js")
          .route("api.myapp.com/*")
          .create())

# CDN Configuration
cdn = (Cloudflare.CDN("myapp.com")
       .static_site()
       .create())

# SSL Certificates
ssl = (Cloudflare.SSL("myapp.com")
       .universal_ssl()
       .create())

# Static Site Hosting
site = (Cloudflare.Pages("my-website")
        .github_repo("myorg/website")
        .build_command("npm run build")
        .create())

# Object Storage
storage = (Cloudflare.R2("static-assets")
           .public_bucket()
           .website_hosting()
           .create())

# Edge Key-Value Store
cache = (Cloudflare.KV("app-config")
         .configuration_cache()
         .create())

# Web Application Firewall
firewall = (Cloudflare.Firewall("myapp.com")
            .basic_protection()
            .create())

# DDoS Protection
ddos = (Cloudflare.DDoSProtection("myapp.com")
        .standard_protection()
        .create())

📚 Method Chaining:
------------------
All resources support Rails-like method chaining:
• .preview()  - Preview changes before applying
• .create()   - Create/deploy the resource
• .delete()   - Remove the resource
• .status()   - Get current status
• .help()     - Get resource-specific help

🔧 Authentication Test:
----------------------
result = Cloudflare.authenticate()

For more detailed help on specific resources, use:
• Cloudflare.DNS("example.com").help()
• Cloudflare.Workers("worker-name").help()
• Cloudflare.CDN("example.com").help()
• Cloudflare.SSL("example.com").help()
• Cloudflare.Pages("project-name").help()
• Cloudflare.R2("bucket-name").help()
• Cloudflare.KV("namespace").help()
• Cloudflare.Firewall("example.com").help()
• Cloudflare.DDoSProtection("example.com").help()
        """

    @staticmethod
    def status() -> dict:
        """
        Get overall Cloudflare provider status.

        Returns:
            Dict containing provider status information
        """
        from .cloudflare_resources.auth_service import CloudflareAuthenticationService

        return {
            'provider': 'cloudflare',
            'version': Cloudflare.version(),
            'authenticated': CloudflareAuthenticationService.is_authenticated(),
            'available_services': [
                'DNS', 'Workers', 'CDN', 'SSL', 'Pages', 
                'R2Storage', 'KVStorage', 'Firewall', 'DDOSProtection'
            ],
            'service_count': 9
        }
