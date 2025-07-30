"""
Cloudflare SSL Resource

Rails-like interface for managing Cloudflare SSL/TLS certificates.
Provides chainable methods for easy SSL configuration and deployment.
"""

from typing import Dict, Any, Optional, List
from .base_resource import BaseCloudflareResource
from ..cloudflare_managers.ssl_manager import SSLManager


class SSL(BaseCloudflareResource):
    """
    Cloudflare SSL resource with Rails-like simplicity.

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

    def __init__(self, domain: str):
        """
        Initialize SSL resource for a domain

        Args:
            domain: The domain name to configure SSL for
        """
        super().__init__(domain)
        self.domain = domain
        self._certificate_type = "universal"  # Default to Universal SSL
        self._min_tls_version = "1.0"
        self._cipher_suites = []
        self._hostnames = []
        self._validity_days = 365
        self._custom_hostnames = []

    def _initialize_managers(self):
        """Initialize SSL-specific managers"""
        self.ssl_manager = None  # Will be initialized after authentication

    def _post_authentication_setup(self):
        """Setup managers after authentication"""
        self.ssl_manager = SSLManager()

    def universal_ssl(self) -> 'SSL':
        """
        Enable Universal SSL (free SSL certificate from Cloudflare)

        Returns:
            SSL: Self for method chaining
        """
        self._certificate_type = "universal"
        return self

    def advanced_certificate(self) -> 'SSL':
        """
        Use Advanced Certificate Manager for custom SSL settings

        Returns:
            SSL: Self for method chaining
        """
        self._certificate_type = "advanced"
        return self

    def origin_certificate(self) -> 'SSL':
        """
        Create an Origin Certificate for secure backend connections

        Returns:
            SSL: Self for method chaining
        """
        self._certificate_type = "origin"
        return self

    def dedicated_certificate(self) -> 'SSL':
        """
        Use Dedicated SSL Certificate for enhanced security

        Returns:
            SSL: Self for method chaining
        """
        self._certificate_type = "dedicated"
        return self

    def min_tls_version(self, version: str) -> 'SSL':
        """
        Set minimum TLS version

        Args:
            version: Minimum TLS version ("1.0", "1.1", "1.2", "1.3")

        Returns:
            SSL: Self for method chaining
        """
        if version not in ["1.0", "1.1", "1.2", "1.3"]:
            raise ValueError("TLS version must be one of: 1.0, 1.1, 1.2, 1.3")
        self._min_tls_version = version
        return self

    def cipher_suites(self, suites: List[str]) -> 'SSL':
        """
        Set custom cipher suites

        Args:
            suites: List of cipher suite names

        Returns:
            SSL: Self for method chaining
        """
        self._cipher_suites = suites
        return self

    def hostnames(self, hostnames: List[str]) -> 'SSL':
        """
        Set hostnames for the certificate

        Args:
            hostnames: List of hostnames to include in certificate

        Returns:
            SSL: Self for method chaining
        """
        self._hostnames = hostnames
        return self

    def validity_days(self, days: int) -> 'SSL':
        """
        Set certificate validity period

        Args:
            days: Number of days certificate should be valid

        Returns:
            SSL: Self for method chaining
        """
        self._validity_days = days
        return self

    def custom_hostname(self, hostname: str) -> 'SSL':
        """
        Add a custom hostname to the certificate

        Args:
            hostname: Custom hostname to add

        Returns:
            SSL: Self for method chaining
        """
        self._custom_hostnames.append(hostname)
        return self

    def ssl_mode(self, mode: str) -> 'SSL':
        """
        Set SSL mode for the domain

        Args:
            mode: SSL mode ("off", "flexible", "full", "strict")

        Returns:
            SSL: Self for method chaining
        """
        if mode not in ["off", "flexible", "full", "strict"]:
            raise ValueError("SSL mode must be one of: off, flexible, full, strict")
        self._ssl_mode = mode
        return self

    def full_strict(self) -> 'SSL':
        """
        Enable Full (Strict) SSL mode for maximum security

        Returns:
            SSL: Self for method chaining
        """
        return self.ssl_mode("strict")

    def full_ssl(self) -> 'SSL':
        """
        Enable Full SSL mode

        Returns:
            SSL: Self for method chaining
        """
        return self.ssl_mode("full")

    def flexible_ssl(self) -> 'SSL':
        """
        Enable Flexible SSL mode

        Returns:
            SSL: Self for method chaining
        """
        return self.ssl_mode("flexible")

    def always_use_https(self, enabled: bool = True) -> 'SSL':
        """
        Force HTTPS redirects

        Args:
            enabled: Whether to force HTTPS

        Returns:
            SSL: Self for method chaining
        """
        self._always_use_https = enabled
        return self

    def hsts(self, max_age: int = 31536000, include_subdomains: bool = True) -> 'SSL':
        """
        Enable HTTP Strict Transport Security

        Args:
            max_age: HSTS max age in seconds
            include_subdomains: Whether to include subdomains

        Returns:
            SSL: Self for method chaining
        """
        self._hsts_enabled = True
        self._hsts_max_age = max_age
        self._hsts_include_subdomains = include_subdomains
        return self

    def edge_certificates(self) -> 'SSL':
        """
        Configure edge certificates for performance

        Returns:
            SSL: Self for method chaining
        """
        self._edge_certificates = True
        return self

    # Rails-like convenience methods
    def ecommerce_ssl(self) -> 'SSL':
        """
        Configure SSL for e-commerce sites with maximum security

        Returns:
            SSL: Self for method chaining
        """
        return (self.advanced_certificate()
                .min_tls_version("1.2")
                .full_strict()
                .always_use_https()
                .hsts())

    def api_ssl(self) -> 'SSL':
        """
        Configure SSL for API endpoints

        Returns:
            SSL: Self for method chaining
        """
        return (self.advanced_certificate()
                .min_tls_version("1.2")
                .full_strict())

    def website_ssl(self) -> 'SSL':
        """
        Configure SSL for regular websites

        Returns:
            SSL: Self for method chaining
        """
        return (self.universal_ssl()
                .full_ssl()
                .always_use_https())

    def preview(self) -> Dict[str, Any]:
        """Preview SSL configuration"""
        self._ensure_authenticated()
        
        preview_data = {
            "domain": self.domain,
            "certificate_type": self._certificate_type,
            "min_tls_version": self._min_tls_version,
            "ssl_mode": getattr(self, '_ssl_mode', 'full'),
            "always_use_https": getattr(self, '_always_use_https', False),
            "hsts_enabled": getattr(self, '_hsts_enabled', False)
        }

        if self._hostnames:
            preview_data["hostnames"] = self._hostnames
        if self._cipher_suites:
            preview_data["cipher_suites"] = self._cipher_suites
        if self._custom_hostnames:
            preview_data["custom_hostnames"] = self._custom_hostnames

        return self._format_response("preview", preview_data)

    def create(self) -> Dict[str, Any]:
        """Create SSL configuration"""
        self._ensure_authenticated()
        
        try:
            result = self.ssl_manager.create_ssl_configuration(
                domain=self.domain,
                certificate_type=self._certificate_type,
                min_tls_version=self._min_tls_version,
                cipher_suites=self._cipher_suites,
                hostnames=self._hostnames,
                ssl_mode=getattr(self, '_ssl_mode', 'full'),
                always_use_https=getattr(self, '_always_use_https', False),
                hsts_enabled=getattr(self, '_hsts_enabled', False),
                hsts_max_age=getattr(self, '_hsts_max_age', 31536000),
                hsts_include_subdomains=getattr(self, '_hsts_include_subdomains', True)
            )
            
            return self._format_response("create", result)
        except Exception as e:
            return self._format_error_response("create", str(e))

    def delete(self) -> Dict[str, Any]:
        """Delete SSL configuration"""
        self._ensure_authenticated()
        
        try:
            result = self.ssl_manager.delete_ssl_configuration(self.domain)
            return self._format_response("delete", result)
        except Exception as e:
            return self._format_error_response("delete", str(e))

    def status(self) -> Dict[str, Any]:
        """Get SSL status"""
        self._ensure_authenticated()
        
        try:
            result = self.ssl_manager.get_ssl_status(self.domain)
            return self._format_response("status", result)
        except Exception as e:
            return self._format_error_response("status", str(e))

    def renew(self) -> Dict[str, Any]:
        """Renew SSL certificate"""
        self._ensure_authenticated()
        
        try:
            result = self.ssl_manager.renew_certificate(self.domain)
            return self._format_response("renew", result)
        except Exception as e:
            return self._format_error_response("renew", str(e))

    def help(self) -> str:
        """Return help information for SSL resource"""
        return f"""
SSL Resource Help
=================

Domain: {self.domain}
Provider: Cloudflare

Certificate Types:
- universal_ssl(): Free SSL certificate from Cloudflare
- advanced_certificate(): Advanced Certificate Manager
- origin_certificate(): Origin Certificate for backend
- dedicated_certificate(): Dedicated SSL Certificate

SSL Modes:
- flexible_ssl(): Flexible SSL mode
- full_ssl(): Full SSL mode
- full_strict(): Full (Strict) SSL mode

Security Settings:
- min_tls_version(version): Set minimum TLS version
- cipher_suites(suites): Set custom cipher suites
- always_use_https(): Force HTTPS redirects
- hsts(): Enable HTTP Strict Transport Security

Convenience Methods:
- ecommerce_ssl(): SSL for e-commerce sites
- api_ssl(): SSL for API endpoints
- website_ssl(): SSL for regular websites

Methods:
- preview(): Preview SSL configuration
- create(): Create SSL configuration
- delete(): Delete SSL configuration
- status(): Get SSL status
- renew(): Renew SSL certificate
        """ 