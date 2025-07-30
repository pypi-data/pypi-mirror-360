"""
Base Resource for DigitalOcean Resources

Provides common functionality and authentication management for all DigitalOcean resources.
"""

from typing import Dict, Any, Optional, Union
from abc import ABC, abstractmethod
from ...core.universal_intelligence_mixin import UniversalIntelligenceMixin


class BaseDigitalOceanResource(UniversalIntelligenceMixin, ABC):
    """Base class for all DigitalOcean resources"""

    def __init__(self, name: str):
        self.name = name
        self.resource_type = self.__class__.__name__.lower()
        self.do_client = None
        self._authenticated = False
        
        # Initialize Universal Intelligence Mixin
        super().__init__()
        
        # Initialize managers
        self._initialize_managers()

    @abstractmethod
    def _initialize_managers(self):
        """Initialize resource-specific managers"""
        pass

    def _ensure_authenticated(self):
        """Ensure the resource is authenticated"""
        if not self._authenticated:
            # Import here to avoid circular imports
            from ..digitalocean_managers.do_client import DoClient
            if not self.do_client:
                self.do_client = DoClient()
            
            if not self.do_client.is_authenticated():
                self.do_client.authenticate()
            
            self._authenticated = True
            self._post_authentication_setup()

    def _post_authentication_setup(self):
        """Setup that happens after authentication"""
        pass

    def _print_resource_header(self, resource_type: str, action: str):
        """Print formatted resource header"""
        print(f"\n🚀 {action}: {resource_type} ({self.name})")
        print("=" * 50)

    def check_state(self, check_interval: Union[int, 'DriftCheckInterval'] = None,
                   auto_remediate: Union[Dict[str, str], str] = None,
                   webhook: Optional[str] = None,
                   enable_auto_fix: bool = True,
                   learning_mode: bool = False,
                   channel: Optional[str] = None) -> 'BaseDigitalOceanResource':
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

    def predict_failures(self, enabled: bool = True) -> 'BaseDigitalOceanResource':
        """Enable failure prediction intelligence
        
        Analyzes DigitalOcean resource patterns and predicts potential failures:
        - Droplet resource exhaustion (CPU, memory, disk space)
        - Database connection limits and performance degradation
        - Load balancer capacity and health check failures
        - Volume storage quota and I/O bottlenecks
        - Kubernetes cluster resource starvation
        
        Returns:
            Self for method chaining
        """
        self._failure_prediction_enabled = enabled
        if enabled:
            print("🔮 Failure prediction enabled: Droplet capacity, database limits, load balancer health, and volume analysis")
        return self
    
    def cost_optimization(self, enabled: bool = True) -> 'BaseDigitalOceanResource':
        """Enable cost optimization intelligence
        
        Analyzes current DigitalOcean configuration and suggests cost savings:
        - Droplet right-sizing recommendations
        - Reserved instance pricing analysis
        - Volume storage optimization and snapshots
        - Load balancer and networking cost analysis
        - Idle resource detection and cleanup
        
        Returns:
            Self for method chaining
        """
        self._cost_optimization_enabled = enabled
        if enabled:
            print("💰 Cost optimization enabled: Droplet sizing, reserved pricing, volume optimization, and idle resource detection")
        return self
    
    def security_scanning(self, enabled: bool = True) -> 'BaseDigitalOceanResource':
        """Enable security scanning intelligence
        
        Scans for DigitalOcean security vulnerabilities and compliance issues:
        - Firewall rule security assessment
        - SSH key and access control analysis
        - SSL certificate expiration monitoring
        - VPC security configuration review
        - Database encryption and access controls
        
        Returns:
            Self for method chaining
        """
        self._security_scanning_enabled = enabled
        if enabled:
            print("🛡️ Security scanning enabled: Firewall rules, SSH access, certificates, VPC security, and database encryption")
        return self
    
    def performance_insights(self, enabled: bool = True) -> 'BaseDigitalOceanResource':
        """Enable performance insights intelligence
        
        Analyzes DigitalOcean performance and suggests improvements:
        - Droplet performance optimization and scaling
        - Database query performance tuning
        - Load balancer distribution and health optimization
        - Volume I/O performance improvements
        - Kubernetes cluster performance tuning
        
        Returns:
            Self for method chaining
        """
        self._performance_insights_enabled = enabled
        if enabled:
            print("⚡ Performance insights enabled: Droplet optimization, database tuning, load balancing, volume I/O, and K8s performance")
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
                    provider="digitalocean"
                )
            except ImportError:
                pass

    def _print_resource_footer(self, action: str):
        """Print formatted resource footer"""
        print("=" * 50)
        print(f"✅ Ready to {action}")
        print()

    @abstractmethod
    def preview(self) -> Dict[str, Any]:
        """Preview what will be created/changed"""
        pass

    @abstractmethod
    def create(self) -> Dict[str, Any]:
        """Create or update the resource"""
        pass

    def apply(self) -> Dict[str, Any]:
        """Alias for create() - Rails-like convention"""
        return self.create()

    def destroy(self) -> Dict[str, Any]:
        """Destroy the resource"""
        raise NotImplementedError("Destroy method must be implemented by subclasses") 