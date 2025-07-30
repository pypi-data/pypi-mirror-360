"""
AWS VPC Complete Implementation

Combines all VPC functionality through multiple inheritance:
- VPCCore: Core attributes and authentication
- VPCConfigurationMixin: Chainable configuration methods  
- VPCLifecycleMixin: Lifecycle operations (create/destroy/preview)
- VPCDiscoveryMixin: Discovery and management operations
"""

from .vpc_core import VPCCore
from .vpc_configuration import VPCConfigurationMixin
from .vpc_lifecycle import VPCLifecycleMixin
from .vpc_discovery import VPCDiscoveryMixin


class VPC(VPCLifecycleMixin, VPCConfigurationMixin, VPCDiscoveryMixin, VPCCore):
    """
    Complete AWS VPC implementation for virtual private cloud networking.
    
    This class combines:
    - VPC creation and management
    - Subnet, route table, and gateway configuration
    - Internet connectivity and NAT gateways
    - VPC endpoints and peering
    - Rails-like method chaining for fluent API
    """
    
    def __init__(self, name: str):
        """Initialize VPC instance for networking"""
        super().__init__(name)
        
        # Additional attributes specific to the combined class
        self.deployment_ready = False
        self.estimated_monthly_cost = "$0.00/month"  # Base VPC is free
        
        # Cross-Cloud Magic integration
        self._optimization_priority = None
        self._network_performance_tier = "standard"
        self._security_tier = "standard"
    
    @property
    def vpc_name_display(self):
        """Get the VPC name for display purposes"""
        return self._vpc_name or self.name
    
    def validate_configuration(self):
        """Validate the current VPC configuration"""
        errors = []
        warnings = []
        
        # Validate VPC name
        if not self._vpc_name and not self.name:
            errors.append("VPC name is required")
        
        # Validate CIDR block
        if not self.cidr_block:
            warnings.append("No CIDR block specified, will use default 10.0.0.0/16")
        elif self.cidr_block:
            cidr_validation = self.validate_cidr_availability(self.cidr_block)
            if not cidr_validation['available']:
                errors.append(f"Invalid CIDR block: {cidr_validation['error']}")
        
        # Validate instance tenancy
        valid_tenancies = ['default', 'dedicated', 'host']
        if self.instance_tenancy not in valid_tenancies:
            errors.append(f"Invalid instance tenancy: {self.instance_tenancy}")
        
        # Validate subnets
        if self.subnets:
            az_count = len(set(subnet['availability_zone'] for subnet in self.subnets))
            if az_count < 2:
                warnings.append("Consider using multiple availability zones for high availability")
            
            # Check for CIDR conflicts
            cidrs = [subnet['cidr_block'] for subnet in self.subnets]
            if len(cidrs) != len(set(cidrs)):
                errors.append("Duplicate CIDR blocks found in subnets")
        
        # Validate NAT gateways
        if self.nat_gateways:
            public_subnets = [s['name'] for s in self.subnets if s.get('map_public_ip_on_launch')]
            for nat in self.nat_gateways:
                if nat['subnet_name'] not in public_subnets:
                    errors.append(f"NAT gateway {nat['name']} references non-public subnet {nat['subnet_name']}")
        
        # High availability warnings
        public_subnets = [s for s in self.subnets if s.get('map_public_ip_on_launch')]
        if public_subnets and not self.internet_gateway_id:
            warnings.append("Public subnets configured but no Internet Gateway - instances won't have internet access")
        
        if errors:
            raise ValueError(f"Configuration validation failed: {', '.join(errors)}")
        
        if warnings:
            print(f"⚠️  Configuration warnings:")
            for warning in warnings:
                print(f"   - {warning}")
        
        self.deployment_ready = True
        return True
    
    def get_vpc_info(self):
        """Get complete information about the VPC"""
        return {
            'vpc_id': self.vpc_id,
            'vpc_name': self._vpc_name or self.name,
            'cidr_block': self.cidr_block or "10.0.0.0/16",
            'instance_tenancy': self.instance_tenancy,
            'dns_support': self._dns_support,
            'dns_hostnames': self._dns_hostnames,
            'state': self.state,
            'subnets_count': len(self.subnets),
            'route_tables_count': len(self.route_tables),
            'nat_gateways_count': len(self.nat_gateways),
            'vpc_endpoints_count': len(self.endpoints),
            'has_internet_gateway': bool(self.internet_gateway_id),
            'tags_count': len(self.tags),
            'vpc_exists': self.vpc_exists,
            'deployment_ready': self.deployment_ready,
            'estimated_monthly_cost': self.estimated_monthly_cost,
            'optimization_priority': self._optimization_priority,
            'network_performance_tier': self._network_performance_tier,
            'security_tier': self._security_tier
        }
    
    def clone(self, new_name: str):
        """Create a copy of this VPC with a new name"""
        cloned_vpc = VPC(new_name)
        cloned_vpc._vpc_name = new_name
        cloned_vpc.cidr_block = self.cidr_block
        cloned_vpc.instance_tenancy = self.instance_tenancy
        cloned_vpc._dns_support = self._dns_support
        cloned_vpc._dns_hostnames = self._dns_hostnames
        cloned_vpc.subnets = [subnet.copy() for subnet in self.subnets]
        cloned_vpc.route_tables = [rt.copy() for rt in self.route_tables]
        cloned_vpc.nat_gateways = [nat.copy() for nat in self.nat_gateways]
        cloned_vpc.endpoints = [ep.copy() for ep in self.endpoints]
        cloned_vpc.tags = self.tags.copy()
        return cloned_vpc
    
    def export_configuration(self):
        """Export VPC configuration for backup or migration"""
        return {
            'metadata': {
                'vpc_name': self._vpc_name or self.name,
                'cidr_block': self.cidr_block or "10.0.0.0/16",
                'exported_at': 'Mock timestamp'
            },
            'configuration': {
                'instance_tenancy': self.instance_tenancy,
                'dns_support': self._dns_support,
                'dns_hostnames': self._dns_hostnames,
                'subnets': self.subnets,
                'route_tables': self.route_tables,
                'nat_gateways': self.nat_gateways,
                'endpoints': self.endpoints,
                'optimization_priority': self._optimization_priority,
                'network_performance_tier': self._network_performance_tier,
                'security_tier': self._security_tier
            },
            'tags': self.tags
        }
    
    def import_configuration(self, config_data: dict):
        """Import VPC configuration from exported data"""
        if 'configuration' in config_data:
            config = config_data['configuration']
            self.instance_tenancy = config.get('instance_tenancy', 'default')
            self._dns_support = config.get('dns_support', True)
            self._dns_hostnames = config.get('dns_hostnames', True)
            self.subnets = config.get('subnets', [])
            self.route_tables = config.get('route_tables', [])
            self.nat_gateways = config.get('nat_gateways', [])
            self.endpoints = config.get('endpoints', [])
            self._optimization_priority = config.get('optimization_priority')
            self._network_performance_tier = config.get('network_performance_tier', 'standard')
            self._security_tier = config.get('security_tier', 'standard')
        
        if 'tags' in config_data:
            self.tags = config_data['tags']
        
        return self
    
    def optimize_for(self, priority: str):
        """Use Cross-Cloud Magic to optimize for cost/performance/reliability
        
        Args:
            priority: Optimization priority - "cost", "performance", "reliability", "compliance"
            
        Returns:
            Self for method chaining
        """
        valid_priorities = ["cost", "performance", "reliability", "compliance"]
        if priority not in valid_priorities:
            raise ValueError(f"Priority must be one of: {valid_priorities}. Got: {priority}")
        
        self._optimization_priority = priority
        print(f"🎯 Cross-Cloud Magic: Optimizing VPC for {priority}")
        
        # Apply AWS VPC-specific optimizations
        if priority == "cost":
            print("💰 Cost optimization: Configuring cost-effective networking")
            self._apply_cost_optimizations()
        elif priority == "performance":
            print("⚡ Performance optimization: Configuring high-performance networking")
            self._apply_performance_optimizations()
        elif priority == "reliability":
            print("🛡️ Reliability optimization: Configuring reliable networking")
            self._apply_reliability_optimizations()
        elif priority == "compliance":
            print("📋 Compliance optimization: Configuring compliant networking")
            self._apply_compliance_optimizations()
        
        return self
    
    def _apply_cost_optimizations(self):
        """Apply AWS VPC-specific cost optimizations"""
        # Minimize NAT gateways
        if len(self.nat_gateways) > 1:
            print("   💰 Consider consolidating NAT gateways to reduce costs")
        
        # Use VPC endpoints for AWS services
        if not any(ep['service_name'] == 's3' for ep in self.endpoints):
            print("   💰 Consider adding S3 VPC endpoint to reduce data transfer costs")
            self.s3_endpoint()
        
        # Add cost optimization tags
        self.tags.update({
            "cost-optimized": "true",
            "nat-gateway-optimized": "true"
        })
    
    def _apply_performance_optimizations(self):
        """Apply AWS VPC-specific performance optimizations"""
        # Use multiple NAT gateways for performance
        public_subnets = [s for s in self.subnets if s.get('map_public_ip_on_launch')]
        if len(public_subnets) > 1 and len(self.nat_gateways) < len(public_subnets):
            print("   ⚡ Consider adding NAT gateways in each AZ for optimal performance")
        
        # Set performance tier
        self._network_performance_tier = "high"
        
        # Enable enhanced networking features
        print("   ⚡ Consider enabling enhanced networking on instances")
        
        # Add performance tags
        self.tags.update({
            "performance-optimized": "true",
            "network-performance": "high"
        })
    
    def _apply_reliability_optimizations(self):
        """Apply AWS VPC-specific reliability optimizations"""
        # Ensure multi-AZ deployment
        azs = list(set(subnet['availability_zone'] for subnet in self.subnets))
        if len(azs) < 2:
            print("   🛡️ Configure subnets in multiple availability zones for high availability")
        
        # Ensure backup NAT gateways
        if len(self.nat_gateways) < 2:
            print("   🛡️ Consider multiple NAT gateways for redundancy")
        
        # Set reliability tier
        self._security_tier = "high"
        
        # Add reliability tags
        self.tags.update({
            "reliability-optimized": "true",
            "multi-az": "enabled",
            "redundancy": "high"
        })
    
    def _apply_compliance_optimizations(self):
        """Apply AWS VPC-specific compliance optimizations"""
        # Use dedicated tenancy for compliance
        if self.instance_tenancy == 'default':
            print("   📋 Consider dedicated tenancy for compliance requirements")
        
        # Enable VPC Flow Logs
        print("   📋 Enable VPC Flow Logs for audit compliance")
        
        # Ensure private subnets for sensitive workloads
        private_subnets = [s for s in self.subnets if not s.get('map_public_ip_on_launch')]
        if not private_subnets:
            print("   📋 Consider adding private subnets for sensitive workloads")
        
        # Add compliance tags
        self.tags.update({
            "compliance-optimized": "true",
            "audit-logging": "enabled",
            "security-tier": "high"
        })
    
    # Network analysis methods
    def calculate_available_ips(self):
        """Calculate available IP addresses in the VPC"""
        import ipaddress
        
        if not self.cidr_block:
            return 0
        
        try:
            network = ipaddress.IPv4Network(self.cidr_block, strict=False)
            total_ips = network.num_addresses - 2  # Network and broadcast
            
            # Subtract subnet IPs
            used_ips = 0
            for subnet in self.subnets:
                subnet_network = ipaddress.IPv4Network(subnet['cidr_block'], strict=False)
                used_ips += subnet_network.num_addresses - 5  # AWS reserves 5 IPs per subnet
            
            return max(0, total_ips - used_ips)
        except ValueError:
            return 0
    
    def get_network_topology(self):
        """Get a summary of the network topology"""
        public_subnets = [s for s in self.subnets if s.get('map_public_ip_on_launch')]
        private_subnets = [s for s in self.subnets if not s.get('map_public_ip_on_launch')]
        
        return {
            'vpc_cidr': self.cidr_block or "10.0.0.0/16",
            'total_subnets': len(self.subnets),
            'public_subnets': len(public_subnets),
            'private_subnets': len(private_subnets),
            'availability_zones': list(set(s['availability_zone'] for s in self.subnets)),
            'internet_connectivity': bool(self.internet_gateway_id),
            'nat_gateways': len(self.nat_gateways),
            'vpc_endpoints': len(self.endpoints),
            'available_ips': self.calculate_available_ips()
        }


# Convenience functions for creating VPC instances
def create_vpc(name: str, cidr: str = "10.0.0.0/16") -> VPC:
    """Create a new VPC with basic configuration"""
    vpc = VPC(name)
    vpc.vpc_name(name).cidr(cidr)
    return vpc

def create_simple_vpc(name: str, cidr_base: str = "10.0") -> VPC:
    """Create a VPC with simple architecture (public + private subnet)"""
    vpc = VPC(name)
    vpc.vpc_name(name).cidr(f"{cidr_base}.0.0/16")
    vpc.simple_architecture(cidr_base)
    return vpc

def create_three_tier_vpc(name: str, cidr_base: str = "10.0") -> VPC:
    """Create a VPC with three-tier architecture"""
    vpc = VPC(name)
    vpc.vpc_name(name).cidr(f"{cidr_base}.0.0/16")
    vpc.three_tier_architecture(cidr_base)
    return vpc

def create_highly_available_vpc(name: str, cidr_base: str = "10.0") -> VPC:
    """Create a highly available VPC across multiple AZs"""
    vpc = VPC(name)
    vpc.vpc_name(name).cidr(f"{cidr_base}.0.0/16")
    vpc.three_tier_architecture(cidr_base)
    vpc.optimize_for("reliability")
    return vpc