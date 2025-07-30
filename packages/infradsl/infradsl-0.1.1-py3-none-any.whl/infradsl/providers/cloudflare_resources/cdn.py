"""
Cloudflare CDN Resource

Rails-like interface for managing Cloudflare CDN/caching settings.
Provides chainable methods for easy configuration and deployment.
"""

from typing import Dict, Any, Optional, List
from .base_resource import BaseCloudflareResource
from ..cloudflare_managers.cdn_manager import CDNManager


class CDN(BaseCloudflareResource):
    """
    Cloudflare CDN resource with Rails-like simplicity.

    Examples:
        # Basic CDN setup
        cdn = (Cloudflare.CDN("myapp.com")
               .cache_level("aggressive")
               .browser_cache_ttl(86400)
               .create())

        # Advanced CDN with custom rules
        cdn = (Cloudflare.CDN("myapp.com")
               .cache_level("aggressive")
               .browser_cache_ttl(86400)
               .page_rule("*.js", cache_level="cache_everything", edge_cache_ttl=31536000)
               .page_rule("*.css", cache_level="cache_everything", edge_cache_ttl=31536000)
               .page_rule("/api/*", cache_level="bypass")
               .create())

        # CDN with custom cache keys
        cdn = (Cloudflare.CDN("myapp.com")
               .cache_level("aggressive")
               .cache_key_fields(["host", "path", "query_string"])
               .minify_css()
               .minify_js()
               .minify_html()
               .create())
    """

    def __init__(self, domain: str):
        """
        Initialize CDN resource for a domain

        Args:
            domain: The domain name to configure CDN for
        """
        super().__init__(domain)
        self.domain = domain
        self.cache_settings = {}
        self.page_rules = []
        self.minification_settings = {}
        self.cache_key_settings = {}
        self.origin_settings = {}
        self.ssl_settings = {}

    def _initialize_managers(self):
        """Initialize CDN-specific managers"""
        self.cdn_manager = None  # Will be initialized after authentication

    def _post_authentication_setup(self):
        """Setup managers after authentication"""
        self.cdn_manager = CDNManager()

    def cache_level(self, level: str) -> 'CDN':
        """
        Set the cache level

        Args:
            level: Cache level (off, basic, simplified, aggressive, cache_everything)

        Returns:
            CDN: Self for method chaining
        """
        valid_levels = ['off', 'basic', 'simplified', 'aggressive', 'cache_everything']
        if level not in valid_levels:
            raise ValueError(f"Invalid cache level. Must be one of: {valid_levels}")

        self.cache_settings['cache_level'] = level
        return self

    def browser_cache_ttl(self, seconds: int) -> 'CDN':
        """
        Set browser cache TTL

        Args:
            seconds: TTL in seconds (0 = respect origin headers)

        Returns:
            CDN: Self for method chaining
        """
        self.cache_settings['browser_cache_ttl'] = seconds
        return self

    def edge_cache_ttl(self, seconds: int) -> 'CDN':
        """
        Set edge cache TTL

        Args:
            seconds: TTL in seconds

        Returns:
            CDN: Self for method chaining
        """
        self.cache_settings['edge_cache_ttl'] = seconds
        return self

    def development_mode(self, enabled: bool = True) -> 'CDN':
        """
        Enable/disable development mode (bypasses cache)

        Args:
            enabled: Whether to enable development mode

        Returns:
            CDN: Self for method chaining
        """
        self.cache_settings['development_mode'] = enabled
        return self

    def always_online(self, enabled: bool = True) -> 'CDN':
        """
        Enable/disable Always Online feature

        Args:
            enabled: Whether to enable Always Online

        Returns:
            CDN: Self for method chaining
        """
        self.cache_settings['always_online'] = enabled
        return self

    def page_rule(self, url_pattern: str, **settings) -> 'CDN':
        """
        Add a page rule for specific URL patterns

        Args:
            url_pattern: URL pattern to match
            **settings: Page rule settings (cache_level, edge_cache_ttl, etc.)

        Returns:
            CDN: Self for method chaining
        """
        self.page_rules.append({
            'url': url_pattern,
            'settings': settings
        })
        return self

    def minify_css(self, enabled: bool = True) -> 'CDN':
        """
        Enable/disable CSS minification

        Args:
            enabled: Whether to minify CSS

        Returns:
            CDN: Self for method chaining
        """
        self.minification_settings['css'] = enabled
        return self

    def minify_js(self, enabled: bool = True) -> 'CDN':
        """
        Enable/disable JavaScript minification

        Args:
            enabled: Whether to minify JavaScript

        Returns:
            CDN: Self for method chaining
        """
        self.minification_settings['js'] = enabled
        return self

    def minify_html(self, enabled: bool = True) -> 'CDN':
        """
        Enable/disable HTML minification

        Args:
            enabled: Whether to minify HTML

        Returns:
            CDN: Self for method chaining
        """
        self.minification_settings['html'] = enabled
        return self

    def cache_key_fields(self, fields: List[str]) -> 'CDN':
        """
        Set custom cache key fields

        Args:
            fields: List of fields to include in cache key (host, path, query_string, etc.)

        Returns:
            CDN: Self for method chaining
        """
        valid_fields = ['host', 'path', 'query_string', 'user_agent', 'accept_encoding']
        invalid_fields = [f for f in fields if f not in valid_fields]
        if invalid_fields:
            raise ValueError(f"Invalid cache key fields: {invalid_fields}. Valid fields: {valid_fields}")

        self.cache_key_settings['include'] = fields
        return self

    def ignore_query_strings(self, patterns: List[str]) -> 'CDN':
        """
        Ignore specific query string parameters in cache key

        Args:
            patterns: List of query string patterns to ignore

        Returns:
            CDN: Self for method chaining
        """
        self.cache_key_settings['ignore_query_strings'] = patterns
        return self

    def origin_server(self, hostname: str, port: Optional[int] = None) -> 'CDN':
        """
        Set origin server details

        Args:
            hostname: Origin server hostname
            port: Origin server port (optional)

        Returns:
            CDN: Self for method chaining
        """
        self.origin_settings['hostname'] = hostname
        if port:
            self.origin_settings['port'] = port
        return self

    def ssl_mode(self, mode: str) -> 'CDN':
        """
        Set SSL mode

        Args:
            mode: SSL mode (off, flexible, full, strict)

        Returns:
            CDN: Self for method chaining
        """
        valid_modes = ['off', 'flexible', 'full', 'strict']
        if mode not in valid_modes:
            raise ValueError(f"Invalid SSL mode. Must be one of: {valid_modes}")

        self.ssl_settings['mode'] = mode
        return self

    def hsts(self, enabled: bool = True, max_age: int = 31536000, include_subdomains: bool = False) -> 'CDN':
        """
        Configure HTTP Strict Transport Security (HSTS)

        Args:
            enabled: Whether to enable HSTS
            max_age: Max age in seconds
            include_subdomains: Whether to include subdomains

        Returns:
            CDN: Self for method chaining
        """
        self.ssl_settings['hsts'] = {
            'enabled': enabled,
            'max_age': max_age,
            'include_subdomains': include_subdomains
        }
        return self

    # Convenience methods for common configurations
    def static_site(self) -> 'CDN':
        """
        Quick configuration for static sites

        Returns:
            CDN: Self for method chaining
        """
        return (self
                .cache_level("cache_everything")
                .browser_cache_ttl(86400)
                .edge_cache_ttl(86400)
                .minify_css()
                .minify_js()
                .minify_html())

    def api_backend(self) -> 'CDN':
        """
        Quick configuration for API backends

        Returns:
            CDN: Self for method chaining
        """
        return (self
                .cache_level("off")
                .page_rule("/api/*", cache_level="bypass")
                .ssl_mode("strict"))

    def ecommerce_site(self) -> 'CDN':
        """
        Quick configuration for e-commerce sites

        Returns:
            CDN: Self for method chaining
        """
        return (self
                .cache_level("aggressive")
                .browser_cache_ttl(14400)
                .page_rule("*.css", cache_level="cache_everything", edge_cache_ttl=2592000)
                .page_rule("*.js", cache_level="cache_everything", edge_cache_ttl=2592000)
                .page_rule("*.jpg", cache_level="cache_everything", edge_cache_ttl=2592000)
                .page_rule("*.png", cache_level="cache_everything", edge_cache_ttl=2592000)
                .page_rule("/cart/*", cache_level="bypass")
                .page_rule("/checkout/*", cache_level="bypass")
                .page_rule("/account/*", cache_level="bypass")
                .ssl_mode("strict")
                .minify_css()
                .minify_js())

    def media_site(self) -> 'CDN':
        """
        Quick configuration for media-heavy sites

        Returns:
            CDN: Self for method chaining
        """
        return (self
                .cache_level("aggressive")
                .browser_cache_ttl(604800)
                .page_rule("*.jpg", cache_level="cache_everything", edge_cache_ttl=31536000)
                .page_rule("*.png", cache_level="cache_everything", edge_cache_ttl=31536000)
                .page_rule("*.gif", cache_level="cache_everything", edge_cache_ttl=31536000)
                .page_rule("*.mp4", cache_level="cache_everything", edge_cache_ttl=31536000)
                .page_rule("*.webp", cache_level="cache_everything", edge_cache_ttl=31536000))

    def preview(self) -> Dict[str, Any]:
        """Preview the CDN configuration"""
        self._ensure_authenticated()

        return self._format_response("preview", {
            "domain": self.domain,
            "cache_settings": self.cache_settings,
            "page_rules": self.page_rules,
            "minification_settings": self.minification_settings,
            "cache_key_settings": self.cache_key_settings,
            "origin_settings": self.origin_settings,
            "ssl_settings": self.ssl_settings
        })

    def create(self) -> Dict[str, Any]:
        """Apply the CDN configuration"""
        self._ensure_authenticated()

        try:
            results = {}

            # Apply cache settings
            if self.cache_settings:
                results['cache_settings'] = self.cdn_manager.update_cache_settings(
                    self.domain, self.cache_settings
                )

            # Apply page rules
            if self.page_rules:
                results['page_rules'] = []
                for rule in self.page_rules:
                    rule_result = self.cdn_manager.create_page_rule(
                        self.domain, rule['url'], rule['settings']
                    )
                    results['page_rules'].append(rule_result)

            # Apply minification settings
            if self.minification_settings:
                results['minification'] = self.cdn_manager.update_minification_settings(
                    self.domain, self.minification_settings
                )

            # Apply cache key settings
            if self.cache_key_settings:
                results['cache_key'] = self.cdn_manager.update_cache_key_settings(
                    self.domain, self.cache_key_settings
                )

            # Apply SSL settings
            if self.ssl_settings:
                results['ssl'] = self.cdn_manager.update_ssl_settings(
                    self.domain, self.ssl_settings
                )

            return self._format_response("create", {
                "domain": self.domain,
                "applied_settings": results
            })

        except Exception as e:
            return self._format_error_response("create", str(e))

    def delete(self) -> Dict[str, Any]:
        """Reset CDN settings to defaults"""
        self._ensure_authenticated()

        try:
            result = self.cdn_manager.reset_cdn_settings(self.domain)
            return self._format_response("delete", result)
        except Exception as e:
            return self._format_error_response("delete", str(e))

    def status(self) -> Dict[str, Any]:
        """Get current CDN status and settings"""
        self._ensure_authenticated()

        try:
            status = self.cdn_manager.get_cdn_status(self.domain)
            return self._format_response("status", status)
        except Exception as e:
            return self._format_error_response("status", str(e))

    def purge_cache(self, files: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Purge cache for the domain

        Args:
            files: Optional list of specific files to purge (purge all if None)

        Returns:
            Dict containing purge result
        """
        self._ensure_authenticated()

        try:
            result = self.cdn_manager.purge_cache(self.domain, files)
            return self._format_response("purge", result)
        except Exception as e:
            return self._format_error_response("purge", str(e))

    def analytics(self, days: int = 7) -> Dict[str, Any]:
        """
        Get CDN analytics

        Args:
            days: Number of days of analytics data

        Returns:
            Dict containing analytics data
        """
        self._ensure_authenticated()

        try:
            analytics = self.cdn_manager.get_analytics(self.domain, days)
            return self._format_response("analytics", analytics)
        except Exception as e:
            return self._format_error_response("analytics", str(e))
