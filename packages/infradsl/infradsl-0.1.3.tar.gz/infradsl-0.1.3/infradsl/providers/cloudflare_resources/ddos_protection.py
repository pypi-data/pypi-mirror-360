"""
Cloudflare DDoS Protection Resource

Rails-like interface for managing Cloudflare DDoS Protection.
Provides chainable methods for easy DDoS protection configuration.
"""

from typing import Dict, Any, Optional, List
from .base_resource import BaseCloudflareResource
from ..cloudflare_managers.ddos_protection_manager import DDOSProtectionManager


class DDOSProtection(BaseCloudflareResource):
    """
    Cloudflare DDoS Protection resource with Rails-like simplicity.

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

    def __init__(self, domain: str):
        """
        Initialize DDoS Protection resource for a domain

        Args:
            domain: The domain name to configure DDoS protection for
        """
        super().__init__(domain)
        self.domain = domain
        self._protection_mode = "standard"  # Default protection mode
        self._sensitivity = "medium"  # Default sensitivity
        self._attack_threshold = "auto"
        self._mitigation_timeout = 300  # 5 minutes default
        self._custom_rules = []
        self._rate_limiting_rules = []
        self._bypass_rules = []

    def _initialize_managers(self):
        """Initialize DDoS Protection-specific managers"""
        self.ddos_manager = None  # Will be initialized after authentication

    def _post_authentication_setup(self):
        """Setup managers after authentication"""
        self.ddos_manager = DDOSProtectionManager()

    def protection_mode(self, mode: str) -> 'DDOSProtection':
        """
        Set DDoS protection mode

        Args:
            mode: Protection mode ("off", "standard", "advanced", "maximum")

        Returns:
            DDOSProtection: Self for method chaining
        """
        valid_modes = ["off", "standard", "advanced", "maximum"]
        if mode not in valid_modes:
            raise ValueError(f"Protection mode must be one of: {', '.join(valid_modes)}")
        self._protection_mode = mode
        return self

    def sensitivity(self, level: str) -> 'DDOSProtection':
        """
        Set DDoS detection sensitivity

        Args:
            level: Sensitivity level ("low", "medium", "high")

        Returns:
            DDOSProtection: Self for method chaining
        """
        valid_levels = ["low", "medium", "high"]
        if level not in valid_levels:
            raise ValueError(f"Sensitivity must be one of: {', '.join(valid_levels)}")
        self._sensitivity = level
        return self

    def attack_threshold(self, threshold: str) -> 'DDOSProtection':
        """
        Set attack detection threshold

        Args:
            threshold: Threshold ("auto", "low", "medium", "high", "very_high")

        Returns:
            DDOSProtection: Self for method chaining
        """
        valid_thresholds = ["auto", "low", "medium", "high", "very_high"]
        if threshold not in valid_thresholds:
            raise ValueError(f"Threshold must be one of: {', '.join(valid_thresholds)}")
        self._attack_threshold = threshold
        return self

    def mitigation_timeout(self, seconds: int) -> 'DDOSProtection':
        """
        Set mitigation timeout duration

        Args:
            seconds: Timeout in seconds (60-3600)

        Returns:
            DDOSProtection: Self for method chaining
        """
        if seconds < 60 or seconds > 3600:
            raise ValueError("Mitigation timeout must be between 60 and 3600 seconds")
        self._mitigation_timeout = seconds
        return self

    def custom_rule(self, expression: str, action: str, description: str = "") -> 'DDOSProtection':
        """
        Add custom DDoS protection rule

        Args:
            expression: Rule expression
            action: Action to take ("block", "challenge", "rate_limit")
            description: Rule description

        Returns:
            DDOSProtection: Self for method chaining
        """
        valid_actions = ["block", "challenge", "rate_limit"]
        if action not in valid_actions:
            raise ValueError(f"Action must be one of: {', '.join(valid_actions)}")
        
        self._custom_rules.append({
            "expression": expression,
            "action": action,
            "description": description
        })
        return self

    def rate_limiting_rule(self, path_pattern: str, requests_per_second: int, burst_size: int = None) -> 'DDOSProtection':
        """
        Add rate limiting rule for DDoS protection

        Args:
            path_pattern: Path pattern to rate limit
            requests_per_second: Maximum requests per second
            burst_size: Burst size (defaults to 2x requests_per_second)

        Returns:
            DDOSProtection: Self for method chaining
        """
        self._rate_limiting_rules.append({
            "path_pattern": path_pattern,
            "requests_per_second": requests_per_second,
            "burst_size": burst_size or (requests_per_second * 2)
        })
        return self

    def bypass_rule(self, expression: str, description: str = "") -> 'DDOSProtection':
        """
        Add bypass rule to allow legitimate traffic

        Args:
            expression: Bypass rule expression
            description: Rule description

        Returns:
            DDOSProtection: Self for method chaining
        """
        self._bypass_rules.append({
            "expression": expression,
            "description": description
        })
        return self

    # Rails-like convenience methods
    def standard_protection(self) -> 'DDOSProtection':
        """
        Configure standard DDoS protection for typical websites

        Returns:
            DDOSProtection: Self for method chaining
        """
        return (self.protection_mode("standard")
                .sensitivity("medium")
                .attack_threshold("auto")
                .mitigation_timeout(300))

    def advanced_protection(self) -> 'DDOSProtection':
        """
        Configure advanced DDoS protection for high-traffic sites

        Returns:
            DDOSProtection: Self for method chaining
        """
        return (self.protection_mode("advanced")
                .sensitivity("high")
                .attack_threshold("medium")
                .mitigation_timeout(600)
                .rate_limiting_rule("/*", 1000)
                .rate_limiting_rule("/api/*", 500))

    def gaming_protection(self) -> 'DDOSProtection':
        """
        Configure DDoS protection optimized for gaming applications

        Returns:
            DDOSProtection: Self for method chaining
        """
        return (self.protection_mode("advanced")
                .sensitivity("medium")  # Lower sensitivity for gaming traffic
                .attack_threshold("high")  # Higher threshold for gaming
                .mitigation_timeout(180)  # Shorter timeout for gaming
                .rate_limiting_rule("/api/game/*", 5000)  # High rate limit for game API
                .bypass_rule('(cf.edge.server_port eq 80 or cf.edge.server_port eq 443)', "Allow standard web traffic"))

    def streaming_protection(self) -> 'DDOSProtection':
        """
        Configure DDoS protection for streaming applications

        Returns:
            DDOSProtection: Self for method chaining
        """
        return (self.protection_mode("advanced")
                .sensitivity("medium")
                .attack_threshold("high")
                .mitigation_timeout(240)
                .rate_limiting_rule("/stream/*", 2000)
                .rate_limiting_rule("/api/stream/*", 1000))

    def api_protection(self) -> 'DDOSProtection':
        """
        Configure DDoS protection for API services

        Returns:
            DDOSProtection: Self for method chaining
        """
        return (self.protection_mode("advanced")
                .sensitivity("high")
                .attack_threshold("medium")
                .mitigation_timeout(600)
                .rate_limiting_rule("/api/*", 1000)
                .rate_limiting_rule("/v1/*", 800)
                .custom_rule('(http.request.method eq "POST" and rate(10s) > 100)', "rate_limit", "Limit POST requests"))

    def ecommerce_protection(self) -> 'DDOSProtection':
        """
        Configure DDoS protection for e-commerce sites

        Returns:
            DDOSProtection: Self for method chaining
        """
        return (self.protection_mode("advanced")
                .sensitivity("high")
                .attack_threshold("medium")
                .mitigation_timeout(900)  # Longer timeout for e-commerce
                .rate_limiting_rule("/checkout/*", 100)
                .rate_limiting_rule("/payment/*", 50)
                .rate_limiting_rule("/api/cart/*", 200)
                .bypass_rule('(cf.verified_bot_category eq "Search Engine")', "Allow search engine bots"))

    def enterprise_protection(self) -> 'DDOSProtection':
        """
        Configure enterprise-grade DDoS protection

        Returns:
            DDOSProtection: Self for method chaining
        """
        return (self.protection_mode("maximum")
                .sensitivity("high")
                .attack_threshold("low")  # Very sensitive for enterprise
                .mitigation_timeout(1200)  # Long timeout for enterprise
                .rate_limiting_rule("/*", 5000)
                .rate_limiting_rule("/api/*", 2000)
                .custom_rule('(cf.threat_score gt 10)', "challenge", "Challenge suspicious traffic")
                .bypass_rule('(ip.src in {192.168.0.0/16 10.0.0.0/8 172.16.0.0/12})', "Allow internal networks"))

    def development_protection(self) -> 'DDOSProtection':
        """
        Configure minimal DDoS protection for development environments

        Returns:
            DDOSProtection: Self for method chaining
        """
        return (self.protection_mode("standard")
                .sensitivity("low")
                .attack_threshold("very_high")
                .mitigation_timeout(120))  # Short timeout for development

    def preview(self) -> Dict[str, Any]:
        """Preview DDoS Protection configuration"""
        self._ensure_authenticated()
        
        preview_data = {
            "domain": self.domain,
            "protection_mode": self._protection_mode,
            "sensitivity": self._sensitivity,
            "attack_threshold": self._attack_threshold,
            "mitigation_timeout_seconds": self._mitigation_timeout
        }

        if self._custom_rules:
            preview_data["custom_rules"] = self._custom_rules

        if self._rate_limiting_rules:
            preview_data["rate_limiting_rules"] = self._rate_limiting_rules

        if self._bypass_rules:
            preview_data["bypass_rules"] = self._bypass_rules

        return self._format_response("preview", preview_data)

    def create(self) -> Dict[str, Any]:
        """Create DDoS Protection configuration"""
        self._ensure_authenticated()
        
        try:
            result = self.ddos_manager.create_ddos_protection(
                domain=self.domain,
                protection_mode=self._protection_mode,
                sensitivity=self._sensitivity,
                attack_threshold=self._attack_threshold,
                mitigation_timeout=self._mitigation_timeout,
                custom_rules=self._custom_rules,
                rate_limiting_rules=self._rate_limiting_rules,
                bypass_rules=self._bypass_rules
            )
            
            return self._format_response("create", result)
        except Exception as e:
            return self._format_error_response("create", str(e))

    def delete(self) -> Dict[str, Any]:
        """Delete DDoS Protection configuration"""
        self._ensure_authenticated()
        
        try:
            result = self.ddos_manager.delete_ddos_protection(self.domain)
            return self._format_response("delete", result)
        except Exception as e:
            return self._format_error_response("delete", str(e))

    def status(self) -> Dict[str, Any]:
        """Get DDoS Protection status"""
        self._ensure_authenticated()
        
        try:
            result = self.ddos_manager.get_ddos_status(self.domain)
            return self._format_response("status", result)
        except Exception as e:
            return self._format_error_response("status", str(e))

    def help(self) -> str:
        """Return help information for DDOSProtection resource"""
        return f"""
DDOSProtection Resource Help
============================

Domain: {self.domain}
Provider: Cloudflare

Protection Configuration:
- protection_mode(mode): Set protection mode (off, standard, advanced, maximum)
- sensitivity(level): Set detection sensitivity (low, medium, high)
- attack_threshold(threshold): Set attack threshold (auto, low, medium, high, very_high)
- mitigation_timeout(seconds): Set mitigation timeout duration

Rules:
- custom_rule(expression, action, description): Add custom protection rule
- rate_limiting_rule(path, rps, burst): Add rate limiting rule
- bypass_rule(expression, description): Add bypass rule for legitimate traffic

Convenience Methods:
- standard_protection(): Standard protection for typical websites
- advanced_protection(): Advanced protection for high-traffic sites
- gaming_protection(): Optimized protection for gaming applications
- streaming_protection(): Protection for streaming applications
- api_protection(): Protection for API services
- ecommerce_protection(): Protection for e-commerce sites
- enterprise_protection(): Enterprise-grade protection
- development_protection(): Minimal protection for development

Methods:
- preview(): Preview DDoS Protection configuration
- create(): Create DDoS Protection configuration
- delete(): Delete DDoS Protection configuration
- status(): Get DDoS Protection status
        """ 