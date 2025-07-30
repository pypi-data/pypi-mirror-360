"""
Base AWS Resource

Abstract base class for all AWS resources, providing common functionality
and enforcing the Rails-like interface pattern.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Union
from .auth_service import AwsAuthenticationService
from ...core.universal_intelligence_mixin import UniversalIntelligenceMixin


class BaseAwsResource(UniversalIntelligenceMixin, ABC):
    """Base class for all AWS resources"""

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
        """Ensure AWS authentication is completed"""
        if not self._auto_authenticated:
            # Use silent mode for subsequent authentication calls to reduce noise
            BaseAwsResource._auth_call_count += 1
            silent = BaseAwsResource._auth_call_count > 1

            AwsAuthenticationService.authenticate(silent=silent)
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

    def get_ec2_client(self, region: Optional[str] = None):
        """Get EC2 client for this resource"""
        return AwsAuthenticationService.get_client('ec2', region)

    def get_ec2_resource(self, region: Optional[str] = None):
        """Get EC2 resource for this resource"""
        return AwsAuthenticationService.get_resource('ec2', region)

    def get_s3_client(self, region: Optional[str] = None):
        """Get S3 client for this resource"""
        return AwsAuthenticationService.get_client('s3', region)

    def get_s3_resource(self, region: Optional[str] = None):
        """Get S3 resource for this resource"""
        return AwsAuthenticationService.get_resource('s3', region)

    def get_rds_client(self, region: Optional[str] = None):
        """Get RDS client for this resource"""
        return AwsAuthenticationService.get_client('rds', region)

    def get_ecs_client(self, region: Optional[str] = None):
        """Get ECS client for this resource"""
        return AwsAuthenticationService.get_client('ecs', region)

    def get_elbv2_client(self, region: Optional[str] = None):
        """Get ELBv2 (ALB) client for this resource"""
        return AwsAuthenticationService.get_client('elbv2', region)

    def get_route53_client(self, region: Optional[str] = None):
        """Get Route53 client for this resource"""
        return AwsAuthenticationService.get_client('route53', region)

    def get_sns_client(self, region: Optional[str] = None):
        """Get SNS client for this resource"""
        return AwsAuthenticationService.get_client('sns', region)

    def get_acm_client(self, region: Optional[str] = None):
        """Get ACM (Certificate Manager) client for this resource"""
        return AwsAuthenticationService.get_client('acm', region)

    def get_current_region(self) -> str:
        """Get the current AWS region"""
        return AwsAuthenticationService.get_region()

    def check_state(self, check_interval: Union[int, 'DriftCheckInterval'] = None,
                   auto_remediate: Union[Dict[str, str], str] = None,
                   webhook: Optional[str] = None,
                   enable_auto_fix: bool = True,
                   learning_mode: bool = False,
                   channel: Optional[str] = None) -> 'BaseAwsResource':
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

    def predict_failures(self, enabled: bool = True) -> 'BaseAwsResource':
        """Enable failure prediction intelligence
        
        Analyzes AWS resource patterns and predicts potential failures:
        - Resource exhaustion prediction (EC2, RDS, Lambda)
        - Storage capacity monitoring (S3, EBS, EFS)
        - Performance degradation trends
        - Service limit approaching alerts
        
        Returns:
            Self for method chaining
        """
        self._failure_prediction_enabled = enabled
        if enabled:
            print("🔮 Failure prediction enabled: Resource exhaustion, storage, performance, and limits analysis")
        return self
    
    def cost_optimization(self, enabled: bool = True) -> 'BaseAwsResource':
        """Enable cost optimization intelligence
        
        Analyzes current AWS configuration and suggests cost savings:
        - Instance type right-sizing (EC2, RDS, ElastiCache)
        - Reserved instance opportunities
        - Storage class optimization (S3, EBS)
        - Regional pricing analysis
        - Unused resource detection
        
        Returns:
            Self for method chaining
        """
        self._cost_optimization_enabled = enabled
        if enabled:
            print("💰 Cost optimization enabled: Instance sizing, reserved instances, storage, and pricing analysis")
        return self
    
    def security_scanning(self, enabled: bool = True) -> 'BaseAwsResource':
        """Enable security scanning intelligence
        
        Scans for AWS security vulnerabilities and compliance issues:
        - Security group rule analysis
        - IAM policy privilege review
        - SSL certificate expiration tracking
        - Encryption status monitoring
        - VPC security assessment
        
        Returns:
            Self for method chaining
        """
        self._security_scanning_enabled = enabled
        if enabled:
            print("🛡️ Security scanning enabled: Security groups, IAM, certificates, encryption, and VPC analysis")
        return self
    
    def performance_insights(self, enabled: bool = True) -> 'BaseAwsResource':
        """Enable performance insights intelligence
        
        Analyzes AWS performance and suggests improvements:
        - Instance performance optimization (EC2, RDS)
        - Network performance tuning (VPC, CloudFront)
        - Database query optimization (RDS, DynamoDB)
        - Auto-scaling recommendations
        - Load balancer optimization
        
        Returns:
            Self for method chaining
        """
        self._performance_insights_enabled = enabled
        if enabled:
            print("⚡ Performance insights enabled: Instance, network, database, auto-scaling, and load balancer optimization")
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
                    provider="aws"
                )
            except ImportError:
                pass
