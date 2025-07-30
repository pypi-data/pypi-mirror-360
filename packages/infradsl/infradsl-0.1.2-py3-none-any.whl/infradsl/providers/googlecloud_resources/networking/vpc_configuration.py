"""
GCP VPC Configuration Mixin

Chainable configuration methods for Google Cloud VPC networks.
Provides Rails-like method chaining for fluent VPC configuration.
"""

from typing import Dict, Any, List, Optional


class VPCConfigurationMixin:
    """
    Mixin for VPC network configuration methods.
    
    This mixin provides chainable configuration methods for:
    - VPC network settings (routing mode, MTU, auto-subnets)
    - Subnet creation and management
    - Firewall rules configuration
    - Static routes and peering
    - DNS and security settings
    """
    
    def description(self, description: str):
        """Set description for the VPC network"""
        self.vpc_description = description
        return self
        
    def routing_mode(self, mode: str):
        """Set routing mode (REGIONAL or GLOBAL)"""
        if not self._is_valid_routing_mode(mode):
            print(f"⚠️  Warning: Invalid routing mode '{mode}'. Valid options: REGIONAL, GLOBAL")
        self.routing_mode = mode.upper()
        return self
        
    def regional_routing(self):
        """Use regional routing mode - Rails convenience"""
        return self.routing_mode("REGIONAL")
        
    def global_routing(self):
        """Use global routing mode - Rails convenience"""
        return self.routing_mode("GLOBAL")
        
    def mtu(self, mtu_size: int):
        """Set Maximum Transmission Unit size (1460-1500)"""
        if not (1460 <= mtu_size <= 1500):
            print(f"⚠️  Warning: MTU should be between 1460 and 1500. Got: {mtu_size}")
        self.mtu = mtu_size
        return self
        
    def auto_subnets(self, enabled: bool = True):
        """Enable/disable automatic subnet creation"""
        self.auto_create_subnetworks = enabled
        if enabled:
            print("⚠️  Warning: Auto-mode VPC will create subnets in all regions automatically")
        return self
        
    def custom_subnets(self):
        """Use custom subnet mode (manual subnet creation) - Rails convenience"""
        return self.auto_subnets(False)
        
    # Subnet configuration methods
    def subnet(self, name: str, cidr: str, region: str, **kwargs):
        """Add a subnet to the VPC"""
        if not self._is_valid_cidr(cidr):
            print(f"⚠️  Warning: Invalid CIDR format '{cidr}'")
            
        if not self._is_valid_region(region):
            print(f"⚠️  Warning: Invalid region '{region}'")
        
        subnet_config = {
            "name": name,
            "cidr": cidr,
            "region": region,
            "description": kwargs.get("description", f"Subnet {name} in {region}"),
            "enable_flow_logs": kwargs.get("enable_flow_logs", False),
            "private_ip_google_access": kwargs.get("private_ip_google_access", False),
            "secondary_ranges": kwargs.get("secondary_ranges", []),
            "purpose": kwargs.get("purpose", "PRIVATE"),
            "role": kwargs.get("role", None),
            "stack_type": kwargs.get("stack_type", "IPV4_ONLY"),
            "ipv6_access_type": kwargs.get("ipv6_access_type", None)
        }
        
        if self._validate_subnet_config(subnet_config):
            self.subnets.append(subnet_config)
        else:
            print(f"⚠️  Warning: Invalid subnet configuration for '{name}'")
            
        return self
        
    def public_subnet(self, name: str, cidr: str, region: str, **kwargs):
        """Add a public subnet with internet access - Rails convenience"""
        kwargs.setdefault("description", f"Public subnet {name} in {region}")
        kwargs.setdefault("purpose", "PRIVATE")
        kwargs.setdefault("private_ip_google_access", True)
        return self.subnet(name, cidr, region, **kwargs)
        
    def private_subnet(self, name: str, cidr: str, region: str, **kwargs):
        """Add a private subnet without direct internet access - Rails convenience"""
        kwargs.setdefault("description", f"Private subnet {name} in {region}")
        kwargs.setdefault("purpose", "PRIVATE")
        kwargs.setdefault("private_ip_google_access", False)
        return self.subnet(name, cidr, region, **kwargs)
        
    def database_subnet(self, name: str, cidr: str, region: str, **kwargs):
        """Add a database subnet optimized for databases - Rails convenience"""
        kwargs.setdefault("description", f"Database subnet {name} in {region}")
        kwargs.setdefault("purpose", "PRIVATE")
        kwargs.setdefault("private_ip_google_access", True)
        kwargs.setdefault("enable_flow_logs", True)
        return self.subnet(name, cidr, region, **kwargs)
        
    def gke_subnet(self, name: str, cidr: str, region: str, pod_cidr: str, service_cidr: str, **kwargs):
        """Add a GKE subnet with secondary ranges - Rails convenience"""
        secondary_ranges = [
            {"rangeName": f"{name}-pods", "ipCidrRange": pod_cidr},
            {"rangeName": f"{name}-services", "ipCidrRange": service_cidr}
        ]
        kwargs.setdefault("description", f"GKE subnet {name} in {region}")
        kwargs.setdefault("secondary_ranges", secondary_ranges)
        kwargs.setdefault("private_ip_google_access", True)
        return self.subnet(name, cidr, region, **kwargs)
        
    # Firewall rules configuration
    def firewall_rule(self, name: str, **kwargs):
        """Add a firewall rule to the VPC"""
        rule_config = {
            "name": name,
            "description": kwargs.get("description", f"Firewall rule {name}"),
            "direction": kwargs.get("direction", "INGRESS").upper(),
            "action": kwargs.get("action", "ALLOW").upper(),
            "priority": kwargs.get("priority", 1000),
            "source_ranges": kwargs.get("source_ranges", []),
            "destination_ranges": kwargs.get("destination_ranges", []),
            "source_tags": kwargs.get("source_tags", []),
            "target_tags": kwargs.get("target_tags", []),
            "source_service_accounts": kwargs.get("source_service_accounts", []),
            "target_service_accounts": kwargs.get("target_service_accounts", []),
            "allowed": kwargs.get("allowed", []),
            "denied": kwargs.get("denied", []),
            "enable_logging": kwargs.get("enable_logging", False)
        }
        
        if self._validate_firewall_rule(rule_config):
            self.firewall_rules.append(rule_config)
        else:
            print(f"⚠️  Warning: Invalid firewall rule configuration for '{name}'")
            
        return self
        
    def allow_ssh(self, source_ranges: List[str] = None, target_tags: List[str] = None):
        """Allow SSH access - Rails convenience"""
        source_ranges = source_ranges or ["0.0.0.0/0"]
        return self.firewall_rule(
            "allow-ssh",
            description="Allow SSH access",
            direction="INGRESS",
            action="ALLOW",
            source_ranges=source_ranges,
            target_tags=target_tags or [],
            allowed=[{"IPProtocol": "tcp", "ports": ["22"]}]
        )
        
    def allow_http(self, source_ranges: List[str] = None, target_tags: List[str] = None):
        """Allow HTTP access - Rails convenience"""
        source_ranges = source_ranges or ["0.0.0.0/0"]
        return self.firewall_rule(
            "allow-http",
            description="Allow HTTP access",
            direction="INGRESS",
            action="ALLOW",
            source_ranges=source_ranges,
            target_tags=target_tags or ["http-server"],
            allowed=[{"IPProtocol": "tcp", "ports": ["80"]}]
        )
        
    def allow_https(self, source_ranges: List[str] = None, target_tags: List[str] = None):
        """Allow HTTPS access - Rails convenience"""
        source_ranges = source_ranges or ["0.0.0.0/0"]
        return self.firewall_rule(
            "allow-https",
            description="Allow HTTPS access",
            direction="INGRESS",
            action="ALLOW",
            source_ranges=source_ranges,
            target_tags=target_tags or ["https-server"],
            allowed=[{"IPProtocol": "tcp", "ports": ["443"]}]
        )
        
    def allow_internal(self, source_ranges: List[str] = None):
        """Allow all internal communication - Rails convenience"""
        source_ranges = source_ranges or ["10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16"]
        return self.firewall_rule(
            "allow-internal",
            description="Allow internal communication",
            direction="INGRESS",
            action="ALLOW",
            source_ranges=source_ranges,
            allowed=[
                {"IPProtocol": "tcp", "ports": ["0-65535"]},
                {"IPProtocol": "udp", "ports": ["0-65535"]},
                {"IPProtocol": "icmp"}
            ]
        )
        
    def deny_all(self, priority: int = 65534):
        """Deny all traffic (lowest priority) - Rails convenience"""
        return self.firewall_rule(
            "deny-all",
            description="Deny all traffic",
            direction="INGRESS",
            action="DENY",
            priority=priority,
            source_ranges=["0.0.0.0/0"],
            denied=[{"IPProtocol": "all"}]
        )
        
    # Static routes configuration
    def static_route(self, name: str, dest_range: str, next_hop_type: str, next_hop: str, **kwargs):
        """Add a static route to the VPC"""
        route_config = {
            "name": name,
            "description": kwargs.get("description", f"Static route {name}"),
            "dest_range": dest_range,
            "next_hop_type": next_hop_type,  # gateway, instance, ip, vpn_tunnel, etc.
            "next_hop": next_hop,
            "priority": kwargs.get("priority", self.route_priority),
            "tags": kwargs.get("tags", [])
        }
        
        if not self._is_valid_cidr(dest_range):
            print(f"⚠️  Warning: Invalid destination CIDR '{dest_range}'")
        
        self.static_routes.append(route_config)
        return self
        
    def default_internet_gateway(self, name: str = "default-route-to-internet"):
        """Add default route to internet gateway - Rails convenience"""
        return self.static_route(
            name,
            "0.0.0.0/0",
            "gateway",
            "default-internet-gateway",
            description="Default route to internet"
        )
        
    # VPC peering configuration
    def peer_with(self, peer_vpc_name: str, peer_project_id: str = None, **kwargs):
        """Set up VPC peering with another VPC"""
        peer_project_id = peer_project_id or self.project_id
        
        peering_config = {
            "name": kwargs.get("name", f"peering-to-{peer_vpc_name}"),
            "peer_vpc_name": peer_vpc_name,
            "peer_project_id": peer_project_id,
            "auto_create_routes": kwargs.get("auto_create_routes", True),
            "import_custom_routes": kwargs.get("import_custom_routes", False),
            "export_custom_routes": kwargs.get("export_custom_routes", False),
            "import_subnet_routes_with_public_ip": kwargs.get("import_subnet_routes_with_public_ip", False),
            "export_subnet_routes_with_public_ip": kwargs.get("export_subnet_routes_with_public_ip", False),
            "state": "ACTIVE"
        }
        
        self.vpc_peerings.append(peering_config)
        return self
        
    # Security and monitoring
    def enable_flow_logs(self, enabled: bool = True, **kwargs):
        """Enable VPC Flow Logs for monitoring"""
        self.enable_flow_logs = enabled
        if enabled:
            self.flow_logs_config.update({
                "aggregation_interval": kwargs.get("aggregation_interval", "INTERVAL_5_SEC"),
                "flow_sampling": kwargs.get("flow_sampling", 0.5),
                "metadata": kwargs.get("metadata", "INCLUDE_ALL_METADATA")
            })
        return self
        
    def flow_logs(self, **kwargs):
        """Enable flow logs - Rails convenience"""
        return self.enable_flow_logs(True, **kwargs)
        
    def no_flow_logs(self):
        """Disable flow logs - Rails convenience"""
        return self.enable_flow_logs(False)
        
    # DNS configuration
    def dns_forwarding(self, enabled: bool = True, forwarding_targets: List[str] = None):
        """Configure DNS forwarding"""
        self.dns_config["enable_inbound_forwarding"] = enabled
        if forwarding_targets:
            self.dns_config["forwarding_targets"] = forwarding_targets
        return self
        
    def dns_logging(self, enabled: bool = True):
        """Enable DNS query logging"""
        self.dns_config["enable_logging"] = enabled
        return self
        
    # Labels and organization
    def labels(self, labels: Dict[str, str]):
        """Add labels for organization and billing"""
        self.vpc_labels.update(labels)
        return self
        
    def label(self, key: str, value: str):
        """Add individual label - Rails convenience"""
        self.vpc_labels[key] = value
        return self
        
    # Rails-like environment configurations
    def development_vpc(self):
        """Configure for development environment - Rails convention"""
        return (self.custom_subnets()
                .regional_routing()
                .mtu(1460)
                .allow_ssh()
                .allow_http()
                .allow_internal()
                .no_flow_logs()
                .label("environment", "development"))
                
    def staging_vpc(self):
        """Configure for staging environment - Rails convention"""
        return (self.custom_subnets()
                .regional_routing()
                .mtu(1460)
                .allow_ssh(["10.0.0.0/8"])  # Restricted SSH
                .allow_http()
                .allow_https()
                .allow_internal()
                .flow_logs()
                .label("environment", "staging"))
                
    def production_vpc(self):
        """Configure for production environment - Rails convention"""
        return (self.custom_subnets()
                .global_routing()
                .mtu(1500)
                .allow_ssh(["10.0.0.0/8"])  # Internal SSH only
                .allow_http()
                .allow_https()
                .allow_internal()
                .flow_logs(flow_sampling=1.0)  # Full sampling
                .dns_logging(True)
                .label("environment", "production"))
                
    def three_tier_architecture(self, cidr_base: str = "10.0", region: str = "us-central1"):
        """Set up common 3-tier architecture - Rails convenience"""
        self.public_subnet("public", f"{cidr_base}.1.0/24", region)
        self.private_subnet("private", f"{cidr_base}.10.0/24", region)
        self.database_subnet("database", f"{cidr_base}.20.0/24", region)
        return self
        
    def microservices_architecture(self, cidr_base: str = "10.0", region: str = "us-central1"):
        """Set up microservices architecture with GKE - Rails convenience"""
        self.gke_subnet("gke-nodes", f"{cidr_base}.0.0/24", region, 
                       f"{cidr_base}.16.0/20", f"{cidr_base}.32.0/20")
        self.private_subnet("services", f"{cidr_base}.64.0/24", region)
        self.database_subnet("data", f"{cidr_base}.80.0/24", region)
        return self
        
    def multi_region_setup(self, regions: List[str], cidr_base: str = "10.0"):
        """Set up subnets across multiple regions - Rails convenience"""
        for i, region in enumerate(regions):
            base_octet = i * 16
            self.public_subnet(f"public-{region}", f"{cidr_base}.{base_octet + 1}.0/24", region)
            self.private_subnet(f"private-{region}", f"{cidr_base}.{base_octet + 8}.0/24", region)
        return self