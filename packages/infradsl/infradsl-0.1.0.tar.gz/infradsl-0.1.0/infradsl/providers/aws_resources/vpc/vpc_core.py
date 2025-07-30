from ..base_resource import BaseAwsResource

class VPCCore(BaseAwsResource):
    """
    Core VPC class with main attributes and authentication logic.
    """
    def __init__(self, name: str):
        super().__init__(name)
        # Core VPC attributes
        self.vpc_id = None
        self._vpc_name = None  # Use underscore to avoid method conflicts
        self.cidr_block = None
        self.ipv6_cidr_block = None
        self.instance_tenancy = 'default'  # default, dedicated, host
        self._dns_support = True
        self._dns_hostnames = True
        self.amazon_provided_ipv6_cidr_block = False
        
        # VPC components
        self.subnets = []
        self.route_tables = []
        self.internet_gateway_id = None
        self.nat_gateways = []
        self.vpn_gateways = []
        self.peering_connections = []
        self.endpoints = []
        
        # Resource state
        self.state = None
        self.tags = {}
        self.vpc_exists = False
        self.availability_zones = []
        
        # Manager
        self.vpc_manager = None

    def _initialize_managers(self):
        """Initialize resource-specific managers"""
        # VPC manager will be initialized after authentication
        self.vpc_manager = None

    def _post_authentication_setup(self):
        """Setup after authentication"""
        # Initialize EC2 client for VPC operations
        self.ec2_client = self.get_ec2_client()
    
    def get_ec2_client(self, region: str = None):
        """Get EC2 client for this resource"""
        return self.get_client('ec2', region)
    
    def get_client(self, service_name: str, region: str = None):
        """Get AWS client for specified service"""
        from ..auth_service import AwsAuthenticationService
        return AwsAuthenticationService.get_client(service_name, region)
    
    def create(self):
        """Create/update VPC - delegates to lifecycle mixin"""
        # Import here to avoid circular imports
        from .vpc_lifecycle import VPCLifecycleMixin
        # Call the lifecycle mixin's create method
        return VPCLifecycleMixin.create(self)

    def destroy(self):
        """Destroy VPC - delegates to lifecycle mixin"""
        # Import here to avoid circular imports
        from .vpc_lifecycle import VPCLifecycleMixin
        # Call the lifecycle mixin's destroy method
        return VPCLifecycleMixin.destroy(self)

    def preview(self):
        """Preview VPC configuration"""
        return {
            "resource_type": "AWS VPC",
            "vpc_name": self._vpc_name or self.name,
            "cidr_block": self.cidr_block or "10.0.0.0/16",
            "instance_tenancy": self.instance_tenancy,
            "dns_support": self._dns_support,
            "dns_hostnames": self._dns_hostnames,
            "subnets_count": len(self.subnets),
            "route_tables_count": len(self.route_tables),
            "has_internet_gateway": bool(self.internet_gateway_id),
            "nat_gateways_count": len(self.nat_gateways),
            "tags_count": len(self.tags),
            "estimated_monthly_cost": self._estimate_monthly_cost()
        }

    def _estimate_monthly_cost(self) -> str:
        """Estimate monthly cost for VPC"""
        # VPC itself is free, but components have costs
        base_cost = 0.00  # VPC is free
        
        # NAT Gateway costs (~$45/month each)
        nat_cost = len(self.nat_gateways) * 45.0
        
        # VPN Gateway costs (~$36/month each)
        vpn_cost = len(self.vpn_gateways) * 36.0
        
        # VPC Endpoints costs (varies, estimate $7/month each)
        endpoint_cost = len(self.endpoints) * 7.0
        
        total_cost = base_cost + nat_cost + vpn_cost + endpoint_cost
        return f"${total_cost:.2f}"