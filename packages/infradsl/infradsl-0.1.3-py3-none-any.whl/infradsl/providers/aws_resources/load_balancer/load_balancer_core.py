from ..base_resource import BaseAwsResource

class LoadBalancerCore(BaseAwsResource):
    """
    Core LoadBalancer class with main attributes and authentication logic.
    """
    def __init__(self, name: str):
        super().__init__(name)
        # Core attributes (to be filled in)
        self.load_balancer_arn = None
        self.load_balancer_name = None
        self.load_balancer_type = None
        self.lb_scheme = None
        self.ip_address_type = None
        self.vpc_id = None
        self.subnets = []
        self.security_groups = []
        self.target_groups = []
        self.listeners = []
        self.health_checks = []
        self.tags = {}
        self.load_balancer_exists = False
        self.dns_name = None
        self.canonical_hosted_zone_id = None
        self.state = None
        self.load_balancer_manager = None

    def _initialize_managers(self):
        """Initialize resource-specific managers"""
        pass

    def _post_authentication_setup(self):
        """Setup after authentication"""
        # Initialize ELBv2 client for Application Load Balancer
        self.elbv2_client = self.get_elbv2_client()

    def create(self):
        """Create/update load balancer - delegates to lifecycle mixin"""
        # Import here to avoid circular imports
        from .load_balancer_lifecycle import LoadBalancerLifecycleMixin
        # Call the lifecycle mixin's create method
        return LoadBalancerLifecycleMixin.create(self)

    def destroy(self):
        """Destroy load balancer - delegates to lifecycle mixin"""
        # Import here to avoid circular imports
        from .load_balancer_lifecycle import LoadBalancerLifecycleMixin
        # Call the lifecycle mixin's destroy method
        return LoadBalancerLifecycleMixin.destroy(self)

    def preview(self):
        """Preview load balancer configuration"""
        return {
            "resource_type": "AWS Application Load Balancer",
            "load_balancer_name": self.load_balancer_name or self.name,
            "load_balancer_type": self.load_balancer_type or "application",
            "scheme": self.lb_scheme or "internet-facing",
            "ip_address_type": self.ip_address_type or "ipv4",
            "subnets_count": len(self.subnets),
            "security_groups_count": len(self.security_groups),
            "target_groups_count": len(self.target_groups),
            "listeners_count": len(self.listeners),
            "health_checks_count": len(self.health_checks),
            "tags_count": len(self.tags),
            "estimated_monthly_cost": self._estimate_monthly_cost()
        }

    def _estimate_monthly_cost(self) -> str:
        """Estimate monthly cost for load balancer"""
        # ALB pricing: $0.0225 per hour + $0.008 per LCU-hour
        # Simplified calculation
        base_hourly_cost = 0.0225  # Base ALB cost per hour
        monthly_hours = 24 * 30
        base_monthly_cost = base_hourly_cost * monthly_hours
        
        # Estimate LCU cost (depends on traffic, simplified to 10 LCUs average)
        estimated_lcus = 10
        lcu_hourly_cost = 0.008 * estimated_lcus
        lcu_monthly_cost = lcu_hourly_cost * monthly_hours
        
        total_cost = base_monthly_cost + lcu_monthly_cost
        return f"${total_cost:.2f}"
    
    def get_elbv2_client(self, region: str = None):
        """Get ELBv2 client for this resource"""
        return self.get_client('elbv2', region)
    
    def get_client(self, service_name: str, region: str = None):
        """Get AWS client for specified service"""
        from ..auth_service import AwsAuthenticationService
        return AwsAuthenticationService.get_client(service_name, region) 