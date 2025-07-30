class VPCConfigurationMixin:
    """
    Mixin for VPC chainable configuration methods.
    """
    def vpc_name(self, name: str):
        """Set the VPC name"""
        self._vpc_name = name
        return self
    
    def cidr(self, cidr_block: str):
        """Set the CIDR block for the VPC"""
        self.cidr_block = cidr_block
        return self
    
    def ipv6_cidr(self, cidr_block: str = None):
        """Enable IPv6 with optional custom CIDR block"""
        if cidr_block:
            self.ipv6_cidr_block = cidr_block
        else:
            self.amazon_provided_ipv6_cidr_block = True
        return self
    
    def tenancy(self, tenancy: str):
        """Set instance tenancy (default, dedicated, host)"""
        valid_tenancies = ['default', 'dedicated', 'host']
        if tenancy not in valid_tenancies:
            raise ValueError(f"Invalid tenancy: {tenancy}. Must be one of: {valid_tenancies}")
        self.instance_tenancy = tenancy
        return self
    
    def dedicated_tenancy(self):
        """Use dedicated tenancy"""
        self.instance_tenancy = 'dedicated'
        return self
    
    def dns_support(self, enabled: bool = True):
        """Enable or disable DNS support"""
        self._dns_support = enabled
        return self
    
    def dns_hostnames(self, enabled: bool = True):
        """Enable or disable DNS hostnames"""
        self._dns_hostnames = enabled
        return self
    
    def subnet(self, name: str, cidr: str, availability_zone: str, public: bool = False):
        """Add a subnet to the VPC"""
        subnet = {
            'name': name,
            'cidr_block': cidr,
            'availability_zone': availability_zone,
            'map_public_ip_on_launch': public,
            'type': 'public' if public else 'private'
        }
        self.subnets.append(subnet)
        return self
    
    def public_subnet(self, name: str, cidr: str, availability_zone: str):
        """Add a public subnet"""
        return self.subnet(name, cidr, availability_zone, public=True)
    
    def private_subnet(self, name: str, cidr: str, availability_zone: str):
        """Add a private subnet"""
        return self.subnet(name, cidr, availability_zone, public=False)
    
    def internet_gateway(self):
        """Add an internet gateway to the VPC"""
        self.internet_gateway_id = f"igw-{self.name}-generated"
        return self
    
    def nat_gateway(self, name: str, subnet_name: str, allocation_id: str = None):
        """Add a NAT gateway"""
        nat_gateway = {
            'name': name,
            'subnet_name': subnet_name,
            'allocation_id': allocation_id or f"eip-{name}-generated"
        }
        self.nat_gateways.append(nat_gateway)
        return self
    
    def vpn_gateway(self, name: str, type: str = 'ipsec.1'):
        """Add a VPN gateway"""
        vpn_gateway = {
            'name': name,
            'type': type
        }
        self.vpn_gateways.append(vpn_gateway)
        return self
    
    def vpc_endpoint(self, service_name: str, endpoint_type: str = 'Gateway'):
        """Add a VPC endpoint"""
        endpoint = {
            'service_name': service_name,
            'vpc_endpoint_type': endpoint_type
        }
        self.endpoints.append(endpoint)
        return self
    
    def s3_endpoint(self):
        """Add S3 VPC endpoint"""
        return self.vpc_endpoint('s3', 'Gateway')
    
    def dynamodb_endpoint(self):
        """Add DynamoDB VPC endpoint"""
        return self.vpc_endpoint('dynamodb', 'Gateway')
    
    def route_table(self, name: str, routes: list = None):
        """Add a route table"""
        route_table = {
            'name': name,
            'routes': routes or []
        }
        self.route_tables.append(route_table)
        return self
    
    def availability_zone(self, az: str):
        """Add an availability zone to the list"""
        if az not in self.availability_zones:
            self.availability_zones.append(az)
        return self
    
    def multi_az(self, zones: list):
        """Configure multiple availability zones"""
        self.availability_zones.extend(zones)
        return self
    
    def tag(self, key: str, value: str):
        """Add a tag to the VPC"""
        self.tags[key] = value
        return self
    
    # Convenience methods for common patterns
    def three_tier_architecture(self, cidr_base: str = "10.0"):
        """Set up common 3-tier architecture (public, private, database subnets)"""
        # Public subnets for load balancers
        self.public_subnet("public-1a", f"{cidr_base}.1.0/24", "us-east-1a")
        self.public_subnet("public-1b", f"{cidr_base}.2.0/24", "us-east-1b")
        
        # Private subnets for application servers
        self.private_subnet("private-1a", f"{cidr_base}.10.0/24", "us-east-1a")
        self.private_subnet("private-1b", f"{cidr_base}.11.0/24", "us-east-1b")
        
        # Database subnets
        self.private_subnet("database-1a", f"{cidr_base}.20.0/24", "us-east-1a")
        self.private_subnet("database-1b", f"{cidr_base}.21.0/24", "us-east-1b")
        
        # Add internet gateway and NAT gateways
        self.internet_gateway()
        self.nat_gateway("nat-1a", "public-1a")
        self.nat_gateway("nat-1b", "public-1b")
        
        return self
    
    def simple_architecture(self, cidr_base: str = "10.0"):
        """Set up simple architecture (public and private subnets)"""
        # Public subnet
        self.public_subnet("public-1a", f"{cidr_base}.1.0/24", "us-east-1a")
        
        # Private subnet
        self.private_subnet("private-1a", f"{cidr_base}.10.0/24", "us-east-1a")
        
        # Add internet gateway and NAT gateway
        self.internet_gateway()
        self.nat_gateway("nat-1a", "public-1a")
        
        return self