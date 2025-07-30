from abc import ABC, abstractmethod
from typing import Dict, Any, Union, Callable, Optional
from ..googlecloud_managers.gcp_client import GcpClient
from .auth_service import GcpAuthenticationService
from ...core.universal_intelligence_mixin import UniversalIntelligenceMixin
# Lazy imports to avoid circular dependencies
# from ...core.drift_management import (
#     get_drift_manager, 
#     DriftCheckInterval, 
#     AutoRemediationPolicy,
#     DriftResult
# )


class BaseGcpResource(UniversalIntelligenceMixin, ABC):
    """Base class for all Google Cloud resources"""
    
    # Class-level counter to track authentication calls
    _auth_call_count = 0

    def __init__(self, name: str):
        self.name = name
        self.gcp_client = GcpClient()
        self._auto_authenticated = False
        # Initialize Universal Intelligence Mixin
        super().__init__()
        self._initialize_managers()

    @abstractmethod
    def _initialize_managers(self):
        """Initialize resource-specific managers"""
        pass

    def _ensure_authenticated(self):
        """Ensure the GCP client is authenticated"""
        if not self._auto_authenticated:
            # Use silent mode for subsequent authentication calls to reduce noise
            BaseGcpResource._auth_call_count += 1
            silent = BaseGcpResource._auth_call_count > 1
            
            GcpAuthenticationService.authenticate_client(self.gcp_client, silent=silent)
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
    def destroy(self) -> Dict[str, Any]:
        """Destroy the resource"""
        pass

    def _print_resource_header(self, resource_type: str, action: str):
        """Print a consistent header for resource operations"""
        print(f"\n🔍 {resource_type} {action}")
        print("=" * 40)

    def _print_resource_footer(self, action: str):
        """Print a consistent footer for resource operations"""
        print("=" * 40)
        print(f"💡 Run .create() to {action.lower()} this resource")
    
    def check_state(self, check_interval: Union[int, 'DriftCheckInterval'] = None,
                   auto_remediate: Union[Dict[str, str], str] = None,
                   webhook: Optional[str] = None,
                   enable_auto_fix: bool = True,
                   learning_mode: bool = False) -> 'BaseGcpResource':
        """Enable drift detection with configurable interval and auto-remediation
        
        Args:
            check_interval: How often to check for drift (default: 6 hours)
            auto_remediate: Auto-remediation policy (CONSERVATIVE, AGGRESSIVE, or custom dict)
            webhook: Webhook URL for drift notifications
            enable_auto_fix: Whether to enable automatic fixing of drift
            learning_mode: Enable 30-day learning mode before auto-remediation
            
        Returns:
            Self for method chaining
        """
        self._drift_enabled = True
        self._drift_check_interval = check_interval
        self._enable_auto_fix = enable_auto_fix
        
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
    
    def _cache_resource_state(self, resource_config: Dict[str, Any], current_state: Dict[str, Any]):
        """Cache the resource state after creation/update"""
        try:
            from ...core.drift_management import get_drift_manager
            drift_manager = get_drift_manager()
            drift_manager.cache_resource_state(
                resource_name=self.name,
                resource_type=self.__class__.__name__.lower(),
                provider="googlecloud",
                config=resource_config,
                current_state=current_state
            )
        except ImportError:
            print("⚠️  Drift management not available for caching state")
    
    def _check_drift_if_enabled(self) -> Optional['DriftResult']:
        """Check for drift if drift detection is enabled"""
        if not hasattr(self, '_drift_enabled') or not self._drift_enabled:
            return None
        
        try:
            from ...core.drift_management import get_drift_manager, AutoRemediationPolicy
            
            drift_manager = get_drift_manager()
            
            def fetch_current_state():
                """Fetch current state from Google Cloud - to be implemented by subclasses"""
                return self._fetch_current_cloud_state()
            
            drift_result = drift_manager.check_resource_drift(
                resource_name=self.name,
                provider="googlecloud",
                check_interval=self._drift_check_interval,
                current_state_fetcher=fetch_current_state,
                remediation_policy=getattr(self, '_remediation_policy', AutoRemediationPolicy.CONSERVATIVE)
            )
            
            # Perform auto-remediation if drift is detected and auto-fix is enabled
            if (drift_result and drift_result.has_drift and 
                getattr(self, '_enable_auto_fix', True) and
                self._remediation_policy != AutoRemediationPolicy.DISABLED):
                
                drift_result = drift_manager.auto_remediate_drift(
                    drift_result=drift_result,
                    resource_instance=self,
                    policy=self._remediation_policy
                )
            
            return drift_result
        except ImportError:
            print("⚠️  Drift management not available for drift checking")
            return None
    
    def _apply_configuration_update(self, field_name: str, new_value: Any):
        """Apply a configuration update to the resource
        
        This method is called during auto-remediation to update specific fields.
        Subclasses should override this to implement provider-specific update logic.
        
        Args:
            field_name: Name of the field to update
            new_value: New value to set
        """
        # Default implementation - just update the local attribute
        # Subclasses should override to also update the cloud resource
        setattr(self, field_name, new_value)
        print(f"   📝 Updated {field_name} = {new_value} (local only - override _apply_configuration_update for cloud updates)")

    def predict_failures(self, enabled: bool = True) -> 'BaseGcpResource':
        """Enable failure prediction intelligence
        
        Analyzes Google Cloud resource patterns and predicts potential failures:
        - Compute instance capacity exhaustion (CPU, memory, disk)
        - Database connection pool limits and performance degradation
        - Storage quota approaching and I/O bottlenecks
        - Network traffic spikes and bandwidth limitations
        - GKE cluster resource starvation
        
        Returns:
            Self for method chaining
        """
        self._failure_prediction_enabled = enabled
        if enabled:
            print("🔮 Failure prediction enabled: Compute capacity, database limits, storage quotas, and network analysis")
        return self
    
    def cost_optimization(self, enabled: bool = True) -> 'BaseGcpResource':
        """Enable cost optimization intelligence
        
        Analyzes current Google Cloud configuration and suggests cost savings:
        - Machine type right-sizing recommendations (Compute Engine, GKE)
        - Committed use discounts and sustained use analysis
        - Storage class optimization (Standard, Nearline, Coldline, Archive)
        - Regional vs multi-regional pricing analysis
        - Idle resource detection and cleanup suggestions
        
        Returns:
            Self for method chaining
        """
        self._cost_optimization_enabled = enabled
        if enabled:
            print("💰 Cost optimization enabled: Machine sizing, committed use discounts, storage classes, and idle resource detection")
        return self
    
    def security_scanning(self, enabled: bool = True) -> 'BaseGcpResource':
        """Enable security scanning intelligence
        
        Scans for Google Cloud security vulnerabilities and compliance issues:
        - IAM policy and role privilege analysis
        - Firewall rule security assessment
        - SSL certificate expiration monitoring
        - VPC security configuration review
        - Data encryption status verification
        
        Returns:
            Self for method chaining
        """
        self._security_scanning_enabled = enabled
        if enabled:
            print("🛡️ Security scanning enabled: IAM policies, firewall rules, certificates, VPC security, and encryption analysis")
        return self
    
    def performance_insights(self, enabled: bool = True) -> 'BaseGcpResource':
        """Enable performance insights intelligence
        
        Analyzes Google Cloud performance and suggests improvements:
        - Compute Engine instance performance optimization
        - Database query performance tuning (Cloud SQL, BigQuery)
        - Load balancer and CDN optimization recommendations
        - GKE cluster performance and auto-scaling tuning
        - Network latency and throughput improvements
        
        Returns:
            Self for method chaining
        """
        self._performance_insights_enabled = enabled
        if enabled:
            print("⚡ Performance insights enabled: Compute optimization, database tuning, load balancing, GKE scaling, and network performance")
        return self
    
    @abstractmethod
    def _fetch_current_cloud_state(self) -> Dict[str, Any]:
        """Fetch current state of the resource from Google Cloud
        
        This method should be implemented by each resource type to return
        the current state as it exists in Google Cloud.
        
        Returns:
            Dictionary representing current state in Google Cloud
        """
        pass
