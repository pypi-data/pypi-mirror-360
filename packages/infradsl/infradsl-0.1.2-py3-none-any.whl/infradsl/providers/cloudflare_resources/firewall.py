"""
Cloudflare Firewall Resource

Rails-like interface for managing Cloudflare Web Application Firewall (WAF).
Provides chainable methods for easy firewall configuration and security rules.
"""

from typing import Dict, Any, Optional, List
from .base_resource import BaseCloudflareResource
from ..cloudflare_managers.firewall_manager import FirewallManager


class Firewall(BaseCloudflareResource):
    """
    Cloudflare Firewall resource with Rails-like simplicity.

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

    def __init__(self, domain: str):
        """
        Initialize Firewall resource for a domain

        Args:
            domain: The domain name to configure firewall for
        """
        super().__init__(domain)
        self.domain = domain
        self._security_level = "medium"  # Default security level
        self._managed_rules = []
        self._custom_rules = []
        self._rate_limit_rules = []
        self._blocked_countries = []
        self._blocked_ips = []
        self._allowed_ips = []
        self._challenge_passage = 3600  # 1 hour default

    def _initialize_managers(self):
        """Initialize Firewall-specific managers"""
        self.firewall_manager = None  # Will be initialized after authentication

    def _post_authentication_setup(self):
        """Setup managers after authentication"""
        self.firewall_manager = FirewallManager()

    def security_level(self, level: str) -> 'Firewall':
        """
        Set security level

        Args:
            level: Security level ("off", "essentially_off", "low", "medium", "high", "under_attack")

        Returns:
            Firewall: Self for method chaining
        """
        valid_levels = ["off", "essentially_off", "low", "medium", "high", "under_attack"]
        if level not in valid_levels:
            raise ValueError(f"Security level must be one of: {', '.join(valid_levels)}")
        self._security_level = level
        return self

    def managed_rule(self, rule_id: str, action: str = "block") -> 'Firewall':
        """
        Add managed rule

        Args:
            rule_id: Managed rule ID
            action: Action to take ("block", "challenge", "log", "allow")

        Returns:
            Firewall: Self for method chaining
        """
        valid_actions = ["block", "challenge", "log", "allow"]
        if action not in valid_actions:
            raise ValueError(f"Action must be one of: {', '.join(valid_actions)}")
        
        self._managed_rules.append({
            "rule_id": rule_id,
            "action": action
        })
        return self

    def custom_rule(self, expression: str, action: str = "block", description: str = "") -> 'Firewall':
        """
        Add custom firewall rule

        Args:
            expression: Firewall rule expression
            action: Action to take ("block", "challenge", "log", "allow", "js_challenge")
            description: Rule description

        Returns:
            Firewall: Self for method chaining
        """
        valid_actions = ["block", "challenge", "log", "allow", "js_challenge"]
        if action not in valid_actions:
            raise ValueError(f"Action must be one of: {', '.join(valid_actions)}")
        
        self._custom_rules.append({
            "expression": expression,
            "action": action,
            "description": description
        })
        return self

    def rate_limit(self, path: str, requests_per_minute: int, action: str = "block") -> 'Firewall':
        """
        Add rate limiting rule

        Args:
            path: Path pattern to rate limit
            requests_per_minute: Maximum requests per minute
            action: Action when limit exceeded ("block", "challenge", "log")

        Returns:
            Firewall: Self for method chaining
        """
        valid_actions = ["block", "challenge", "log"]
        if action not in valid_actions:
            raise ValueError(f"Rate limit action must be one of: {', '.join(valid_actions)}")
        
        self._rate_limit_rules.append({
            "path": path,
            "threshold": requests_per_minute,
            "period": 60,  # 1 minute
            "action": action
        })
        return self

    def block_country(self, countries: List[str]) -> 'Firewall':
        """
        Block traffic from specific countries

        Args:
            countries: List of country codes (ISO 3166-1 alpha-2)

        Returns:
            Firewall: Self for method chaining
        """
        self._blocked_countries.extend(countries)
        return self

    def block_ip(self, ip_addresses: List[str]) -> 'Firewall':
        """
        Block specific IP addresses

        Args:
            ip_addresses: List of IP addresses or CIDR blocks

        Returns:
            Firewall: Self for method chaining
        """
        self._blocked_ips.extend(ip_addresses)
        return self

    def allow_ip(self, ip_addresses: List[str]) -> 'Firewall':
        """
        Allow specific IP addresses (whitelist)

        Args:
            ip_addresses: List of IP addresses or CIDR blocks

        Returns:
            Firewall: Self for method chaining
        """
        self._allowed_ips.extend(ip_addresses)
        return self

    def challenge_passage(self, seconds: int) -> 'Firewall':
        """
        Set challenge passage duration

        Args:
            seconds: Duration in seconds for challenge passage

        Returns:
            Firewall: Self for method chaining
        """
        self._challenge_passage = seconds
        return self

    # Rails-like convenience methods
    def basic_protection(self) -> 'Firewall':
        """
        Configure basic protection for standard websites

        Returns:
            Firewall: Self for method chaining
        """
        return (self.security_level("medium")
                .managed_rule("cloudflare_core_ruleset", "block")
                .rate_limit("/*", 300))

    def ecommerce_protection(self) -> 'Firewall':
        """
        Configure enhanced protection for e-commerce sites

        Returns:
            Firewall: Self for method chaining
        """
        return (self.security_level("high")
                .managed_rule("cloudflare_core_ruleset", "block")
                .managed_rule("cloudflare_owasp_ruleset", "block")
                .rate_limit("/api/*", 100)
                .rate_limit("/checkout/*", 30)
                .rate_limit("/login", 10)
                .custom_rule('(cf.threat_score gt 14)', "challenge", "Block suspicious traffic"))

    def api_protection(self) -> 'Firewall':
        """
        Configure protection for API endpoints

        Returns:
            Firewall: Self for method chaining
        """
        return (self.security_level("high")
                .managed_rule("cloudflare_core_ruleset", "block")
                .rate_limit("/api/*", 200)
                .rate_limit("/auth/*", 20)
                .custom_rule('(http.request.method eq "POST" and http.request.uri.path contains "/api/")', "js_challenge", "Challenge API POST requests"))

    def blog_protection(self) -> 'Firewall':
        """
        Configure protection for blogs and content sites

        Returns:
            Firewall: Self for method chaining
        """
        return (self.security_level("medium")
                .managed_rule("cloudflare_core_ruleset", "block")
                .rate_limit("/wp-admin/*", 20)
                .rate_limit("/*login*", 10)
                .custom_rule('(http.request.uri.path contains "/wp-" and cf.threat_score gt 0)', "challenge", "Challenge WordPress access"))

    def enterprise_protection(self) -> 'Firewall':
        """
        Configure enterprise-grade protection

        Returns:
            Firewall: Self for method chaining
        """
        return (self.security_level("high")
                .managed_rule("cloudflare_core_ruleset", "block")
                .managed_rule("cloudflare_owasp_ruleset", "block")
                .managed_rule("cloudflare_exposed_credentials_check", "block")
                .rate_limit("/api/*", 500)
                .rate_limit("/auth/*", 50)
                .custom_rule('(cf.threat_score gt 10)', "challenge", "Challenge medium threat traffic")
                .custom_rule('(cf.bot_management.score lt 30)', "js_challenge", "Challenge likely bots"))

    def gaming_protection(self) -> 'Firewall':
        """
        Configure protection for gaming applications

        Returns:
            Firewall: Self for method chaining
        """
        return (self.security_level("medium")
                .managed_rule("cloudflare_core_ruleset", "block")
                .rate_limit("/api/game/*", 1000)  # Higher rate limit for gaming
                .rate_limit("/leaderboard/*", 100)
                .custom_rule('(cf.threat_score gt 20)', "challenge", "Challenge high threat gaming traffic"))

    def development_protection(self) -> 'Firewall':
        """
        Configure minimal protection for development environments

        Returns:
            Firewall: Self for method chaining
        """
        return (self.security_level("low")
                .rate_limit("/*", 1000))  # Very permissive for development

    def preview(self) -> Dict[str, Any]:
        """Preview Firewall configuration"""
        self._ensure_authenticated()
        
        preview_data = {
            "domain": self.domain,
            "security_level": self._security_level,
            "challenge_passage_seconds": self._challenge_passage
        }

        if self._managed_rules:
            preview_data["managed_rules"] = self._managed_rules

        if self._custom_rules:
            preview_data["custom_rules"] = self._custom_rules

        if self._rate_limit_rules:
            preview_data["rate_limit_rules"] = self._rate_limit_rules

        if self._blocked_countries:
            preview_data["blocked_countries"] = self._blocked_countries

        if self._blocked_ips:
            preview_data["blocked_ips"] = self._blocked_ips

        if self._allowed_ips:
            preview_data["allowed_ips"] = self._allowed_ips

        return self._format_response("preview", preview_data)

    def create(self) -> Dict[str, Any]:
        """Create Firewall configuration"""
        self._ensure_authenticated()
        
        try:
            result = self.firewall_manager.create_firewall_rules(
                domain=self.domain,
                security_level=self._security_level,
                managed_rules=self._managed_rules,
                custom_rules=self._custom_rules,
                rate_limit_rules=self._rate_limit_rules,
                blocked_countries=self._blocked_countries,
                blocked_ips=self._blocked_ips,
                allowed_ips=self._allowed_ips,
                challenge_passage=self._challenge_passage
            )
            
            return self._format_response("create", result)
        except Exception as e:
            return self._format_error_response("create", str(e))

    def delete(self) -> Dict[str, Any]:
        """Delete Firewall configuration"""
        self._ensure_authenticated()
        
        try:
            result = self.firewall_manager.delete_firewall_rules(self.domain)
            return self._format_response("delete", result)
        except Exception as e:
            return self._format_error_response("delete", str(e))

    def status(self) -> Dict[str, Any]:
        """Get Firewall status"""
        self._ensure_authenticated()
        
        try:
            result = self.firewall_manager.get_firewall_status(self.domain)
            return self._format_response("status", result)
        except Exception as e:
            return self._format_error_response("status", str(e))

    def help(self) -> str:
        """Return help information for Firewall resource"""
        return f"""
Firewall Resource Help
======================

Domain: {self.domain}
Provider: Cloudflare

Security Configuration:
- security_level(level): Set security level (off, low, medium, high, under_attack)
- challenge_passage(seconds): Set challenge passage duration

Rules:
- managed_rule(rule_id, action): Add managed rule
- custom_rule(expression, action, description): Add custom rule
- rate_limit(path, requests_per_minute, action): Add rate limiting

Access Control:
- block_country(countries): Block traffic from countries
- block_ip(ip_addresses): Block specific IP addresses
- allow_ip(ip_addresses): Allow specific IP addresses (whitelist)

Convenience Methods:
- basic_protection(): Basic protection for standard websites
- ecommerce_protection(): Enhanced protection for e-commerce
- api_protection(): Protection for API endpoints
- blog_protection(): Protection for blogs and content sites
- enterprise_protection(): Enterprise-grade protection
- gaming_protection(): Protection for gaming applications
- development_protection(): Minimal protection for development

Methods:
- preview(): Preview Firewall configuration
- create(): Create Firewall configuration
- delete(): Delete Firewall configuration
- status(): Get Firewall status
        """ 