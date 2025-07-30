"""
Base Cloudflare Resource

Abstract base class for all Cloudflare resources, providing common functionality
and enforcing the Rails-like interface pattern.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Union
from .auth_service import CloudflareAuthenticationService
from ...core.universal_intelligence_mixin import UniversalIntelligenceMixin


class BaseCloudflareResource(UniversalIntelligenceMixin, ABC):
    """Base class for all Cloudflare resources"""

    # Class-level counter to track authentication calls
    _auth_call_count = 0

    def __init__(self, name: str):
        self.name = name
        self._auto_authenticated = False
        # Initialize Universal Intelligence Mixin
        super().__init__()
        self._initialize_managers()

    @abstractmethod
    def _initialize_managers(self):
        """Initialize resource-specific managers"""
        pass

    def _ensure_authenticated(self):
        """Ensure Cloudflare authentication is completed"""
        if not self._auto_authenticated:
            # Use silent mode for subsequent authentication calls to reduce noise
            BaseCloudflareResource._auth_call_count += 1
            silent = BaseCloudflareResource._auth_call_count > 1

            CloudflareAuthenticationService.authenticate(silent=silent)
            self._post_authentication_setup()
            self._auto_authenticated = True

    @abstractmethod
    def _post_authentication_setup(self):
        """Setup managers after authentication"""
        pass

    @abstractmethod
    def preview(self) -> Dict[str, Any]:
        """Preview what will be created"""
        pass

    @abstractmethod
    def create(self) -> Dict[str, Any]:
        """Create the resource"""
        pass

    @abstractmethod
    def delete(self) -> Dict[str, Any]:
        """Delete the resource"""
        pass

    @abstractmethod
    def status(self) -> Dict[str, Any]:
        """Get the current status of the resource"""
        pass

    def _format_response(self, action: str, details: Dict[str, Any]) -> Dict[str, Any]:
        """Format a standardized response"""
        return {
            "resource_type": self.__class__.__name__,
            "resource_name": self.name,
            "action": action,
            "status": "success",
            "details": details,
            "provider": "cloudflare"
        }

    def _format_error_response(self, action: str, error: str) -> Dict[str, Any]:
        """Format a standardized error response"""
        return {
            "resource_type": self.__class__.__name__,
            "resource_name": self.name,
            "action": action,
            "status": "error",
            "error": error,
            "provider": "cloudflare"
        }

    def help(self) -> str:
        """Return help information for this resource"""
        return f"""
{self.__class__.__name__} Resource Help
{'=' * 50}

Resource: {self.name}
Provider: Cloudflare

Common Methods:
- preview(): Preview what will be created
- create(): Create the resource
- delete(): Delete the resource
- status(): Get current status

For specific method help, check the class documentation.
        """

    def check_state(self, check_interval: Union[int, 'DriftCheckInterval'] = None,
                   auto_remediate: Union[Dict[str, str], str] = None,
                   webhook: Optional[str] = None,
                   enable_auto_fix: bool = True,
                   learning_mode: bool = False,
                   channel: Optional[str] = None) -> 'BaseCloudflareResource':
        """Enable drift detection with configurable interval and auto-remediation
        
        Args:
            check_interval: How often to check for drift (default: 6 hours)
            auto_remediate: Auto-remediation policy (CONSERVATIVE, AGGRESSIVE, or custom dict)
            webhook: Webhook URL for drift notifications
            enable_auto_fix: Whether to enable automatic fixing of drift
            learning_mode: Enable 30-day learning mode before auto-remediation
            channel: Slack/Discord channel for notifications
            
        Returns:
            Self for method chaining
        """
        self._drift_enabled = True
        self._drift_check_interval = check_interval
        self._enable_auto_fix = enable_auto_fix
        self._notification_channel = channel
        
        # Lazy import drift management
        try:
            from ...core.drift_management import DriftCheckInterval, AutoRemediationPolicy
            
            if check_interval is None:
                check_interval = DriftCheckInterval.SIX_HOURS
                
            # Handle auto-remediation policy
            if auto_remediate is None:
                self._remediation_policy = AutoRemediationPolicy.CONSERVATIVE
            elif isinstance(auto_remediate, str):
                if auto_remediate.upper() == "CONSERVATIVE":
                    self._remediation_policy = AutoRemediationPolicy.CONSERVATIVE
                elif auto_remediate.upper() == "AGGRESSIVE":
                    self._remediation_policy = AutoRemediationPolicy.AGGRESSIVE
                elif auto_remediate.upper() == "DISABLED":
                    self._remediation_policy = AutoRemediationPolicy.DISABLED
                else:
                    raise ValueError("auto_remediate must be 'CONSERVATIVE', 'AGGRESSIVE', 'DISABLED', or a custom dict")
            else:
                self._remediation_policy = auto_remediate
        except ImportError:
            print("⚠️  Drift management not available")
            return self
        
        # Enable learning mode if requested
        if learning_mode:
            try:
                from ...core.drift_management import get_drift_manager
                drift_manager = get_drift_manager()
                drift_manager.enable_learning_mode(self.name)
            except ImportError:
                print("⚠️  Drift management not available for learning mode")
        
        # Store webhook if provided
        if webhook:
            try:
                from ...core.drift_management import get_drift_manager
                drift_manager = get_drift_manager()
                drift_manager.add_webhook(webhook)
            except ImportError:
                print("⚠️  Drift management not available for webhooks")
        
        return self

    def predict_failures(self, enabled: bool = True) -> 'BaseCloudflareResource':
        """Enable failure prediction intelligence
        
        Analyzes Cloudflare edge network patterns and predicts potential failures:
        - CDN cache hit ratio degradation and origin overload
        - DNS query response time increases and resolution failures
        - DDoS protection capacity and attack pattern analysis
        - Worker script execution limits and performance degradation
        - SSL certificate expiration and validation issues
        
        Returns:
            Self for method chaining
        """
        self._failure_prediction_enabled = enabled
        if enabled:
            print("🔮 Failure prediction enabled: CDN performance, DNS resolution, DDoS capacity, Worker limits, and SSL analysis")
        return self
    
    def cost_optimization(self, enabled: bool = True) -> 'BaseCloudflareResource':
        """Enable cost optimization intelligence
        
        Analyzes current Cloudflare configuration and suggests cost savings:
        - Bandwidth optimization and caching strategy improvements
        - Worker execution optimization and pricing tier analysis
        - DNS query optimization and plan recommendations
        - R2 storage class optimization and lifecycle management
        - Zone configuration and feature usage analysis
        
        Returns:
            Self for method chaining
        """
        self._cost_optimization_enabled = enabled
        if enabled:
            print("💰 Cost optimization enabled: Bandwidth optimization, Worker efficiency, DNS optimization, and storage management")
        return self
    
    def security_scanning(self, enabled: bool = True) -> 'BaseCloudflareResource':
        """Enable security scanning intelligence
        
        Scans for Cloudflare security vulnerabilities and configuration issues:
        - Firewall rule effectiveness and security gaps
        - SSL/TLS configuration and certificate validation
        - DDoS protection configuration and threat analysis
        - Access control and authentication settings review
        - Worker script security and permission analysis
        
        Returns:
            Self for method chaining
        """
        self._security_scanning_enabled = enabled
        if enabled:
            print("🛡️ Security scanning enabled: Firewall rules, SSL/TLS config, DDoS protection, access controls, and Worker security")
        return self
    
    def performance_insights(self, enabled: bool = True) -> 'BaseCloudflareResource':
        """Enable performance insights intelligence
        
        Analyzes Cloudflare edge performance and suggests improvements:
        - CDN cache optimization and edge location performance
        - DNS response time optimization and routing improvements
        - Worker script performance tuning and optimization
        - Page Rules and Transform Rules optimization
        - Origin server performance and connection optimization
        
        Returns:
            Self for method chaining
        """
        self._performance_insights_enabled = enabled
        if enabled:
            print("⚡ Performance insights enabled: CDN optimization, DNS performance, Worker tuning, rule optimization, and origin connectivity")
        return self

    def _cache_resource_state(self, resource_config: Dict[str, Any], current_state: Dict[str, Any]):
        """Cache the resource state after creation/update"""
        if hasattr(self, '_drift_enabled') and self._drift_enabled:
            try:
                from ...core.drift_management import get_drift_manager
                drift_manager = get_drift_manager()
                drift_manager.cache_resource_state(
                    self.name,
                    resource_config,
                    current_state,
                    provider="cloudflare"
                )
            except ImportError:
                pass
