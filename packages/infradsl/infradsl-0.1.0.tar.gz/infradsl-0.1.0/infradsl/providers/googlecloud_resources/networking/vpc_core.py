"""
GCP VPC Core Implementation

Core attributes and authentication for Google Cloud Virtual Private Cloud.
Provides the foundation for the modular VPC networking system.
"""

from typing import Dict, Any, List, Optional
from ..base_resource import BaseGcpResource


class VPCCore(BaseGcpResource):
    """
    Core class for Google Cloud VPC functionality.
    
    This class provides:
    - Basic VPC attributes and configuration
    - Authentication setup
    - Common utilities for VPC operations
    - Subnet and firewall management foundations
    """
    
    def __init__(self, name: str):
        """Initialize VPC core with network name"""
        super().__init__(name)
        
        # Core VPC attributes
        self.vpc_name = name
        self.vpc_description = f"VPC network for {name}"
        self.vpc_region = "global"  # VPC networks are global in GCP
        self.routing_mode = "REGIONAL"  # REGIONAL or GLOBAL
        
        # Network configuration
        self.auto_create_subnetworks = False  # Custom mode by default
        self.mtu = 1460  # Default MTU for GCP VPC
        self.enable_ula_internal_ipv6 = False
        self.internal_ipv6_range = None
        
        # Subnets configuration
        self.subnets = []
        self.secondary_ranges = {}
        
        # Firewall rules
        self.firewall_rules = []
        self.default_firewall_action = "DENY"
        
        # Routes configuration  
        self.static_routes = []
        self.route_priority = 1000
        
        # Peering configuration
        self.vpc_peerings = []
        self.peering_routes_config = {
            "import_custom_routes": False,
            "export_custom_routes": False,
            "import_subnet_routes_with_public_ip": False,
            "export_subnet_routes_with_public_ip": False
        }
        
        # DNS configuration
        self.dns_config = {
            "enable_inbound_forwarding": False,
            "enable_logging": False,
            "private_visibility": []
        }
        
        # Network security
        self.enable_flow_logs = False
        self.flow_logs_config = {
            "aggregation_interval": "INTERVAL_5_SEC",
            "flow_sampling": 0.5,
            "metadata": "INCLUDE_ALL_METADATA"
        }
        
        # Labels and organization
        self.vpc_labels = {}
        
        # State tracking
        self.vpc_exists = False
        self.vpc_created = False
        self.vpc_url = None
        
    def _initialize_managers(self):
        """Initialize VPC-specific managers"""
        # Will be set up after authentication
        self.vpc_manager = None
        self.subnet_manager = None
        self.firewall_manager = None
        
    def _post_authentication_setup(self):
        """Setup managers after authentication"""
        # Import here to avoid circular imports
        from ...googlecloud_managers.networking.vpc_manager import VPCManager
        from ...googlecloud_managers.networking.subnet_manager import SubnetManager  
        from ...googlecloud_managers.networking.firewall_manager import FirewallManager
        
        self.vpc_manager = VPCManager(self.gcp_client)
        self.subnet_manager = SubnetManager(self.gcp_client)
        self.firewall_manager = FirewallManager(self.gcp_client)
        
        # Set up VPC URL
        self.project_id = self.gcp_client.project_id
        self.vpc_url = f"projects/{self.project_id}/global/networks/{self.vpc_name}"
        
    def _is_valid_cidr(self, cidr: str) -> bool:
        """Check if CIDR notation is valid"""
        import ipaddress
        try:
            ipaddress.ip_network(cidr, strict=False)
            return True
        except ValueError:
            return False
            
    def _is_valid_routing_mode(self, mode: str) -> bool:
        """Check if routing mode is valid"""
        valid_modes = ["REGIONAL", "GLOBAL"]
        return mode.upper() in valid_modes
        
    def _is_valid_region(self, region: str) -> bool:
        """Check if region is valid for GCP"""
        gcp_regions = [
            'us-central1', 'us-east1', 'us-east4', 'us-west1', 'us-west2', 'us-west3', 'us-west4',
            'europe-north1', 'europe-west1', 'europe-west2', 'europe-west3', 'europe-west4', 'europe-west6',
            'asia-east1', 'asia-east2', 'asia-northeast1', 'asia-northeast2', 'asia-south1', 'asia-southeast1',
            'australia-southeast1', 'northamerica-northeast1', 'southamerica-east1'
        ]
        return region in gcp_regions
        
    def _is_valid_zone(self, zone: str) -> bool:
        """Check if zone is valid for GCP"""
        # Zone format: region-zone (e.g., us-central1-a)
        if '-' not in zone:
            return False
        
        region = '-'.join(zone.split('-')[:-1])
        zone_letter = zone.split('-')[-1]
        
        return self._is_valid_region(region) and zone_letter.isalpha()
        
    def _validate_subnet_config(self, subnet_config: Dict[str, Any]) -> bool:
        """Validate subnet configuration"""
        required_fields = ["name", "cidr", "region"]
        
        for field in required_fields:
            if field not in subnet_config:
                return False
                
        # Validate CIDR
        if not self._is_valid_cidr(subnet_config["cidr"]):
            return False
            
        # Validate region
        if not self._is_valid_region(subnet_config["region"]):
            return False
            
        return True
        
    def _validate_firewall_rule(self, rule_config: Dict[str, Any]) -> bool:
        """Validate firewall rule configuration"""
        required_fields = ["name", "direction"]
        
        for field in required_fields:
            if field not in rule_config:
                return False
                
        # Validate direction
        valid_directions = ["INGRESS", "EGRESS"]
        if rule_config["direction"].upper() not in valid_directions:
            return False
            
        # Validate action
        valid_actions = ["ALLOW", "DENY"]
        action = rule_config.get("action", "ALLOW").upper()
        if action not in valid_actions:
            return False
            
        return True
        
    def _is_overlapping_cidr(self, cidr1: str, cidr2: str) -> bool:
        """Check if two CIDR blocks overlap"""
        import ipaddress
        try:
            network1 = ipaddress.ip_network(cidr1, strict=False)
            network2 = ipaddress.ip_network(cidr2, strict=False)
            return network1.overlaps(network2)
        except ValueError:
            return False
            
    def _check_subnet_overlaps(self) -> List[str]:
        """Check for overlapping subnet CIDR blocks"""
        overlaps = []
        
        for i, subnet1 in enumerate(self.subnets):
            for j, subnet2 in enumerate(self.subnets[i+1:], i+1):
                if self._is_overlapping_cidr(subnet1["cidr"], subnet2["cidr"]):
                    overlaps.append(f"Subnets '{subnet1['name']}' and '{subnet2['name']}' have overlapping CIDR blocks")
                    
        return overlaps
        
    def _estimate_vpc_cost(self) -> float:
        """Estimate monthly cost for VPC"""
        # GCP VPC pricing (simplified)
        base_cost = 0.0  # VPC networks are free
        
        # Firewall rules cost
        firewall_cost = len(self.firewall_rules) * 0.10  # $0.10 per rule per month (simplified)
        
        # Static routes cost
        routes_cost = len(self.static_routes) * 0.05  # $0.05 per route per month (simplified)
        
        # VPC peering cost (simplified)
        peering_cost = len(self.vpc_peerings) * 1.0  # $1.00 per peering per month
        
        # Flow logs cost (if enabled)
        flow_logs_cost = 0.0
        if self.enable_flow_logs:
            flow_logs_cost = 5.0  # $5.00 per month (simplified estimate)
            
        return base_cost + firewall_cost + routes_cost + peering_cost + flow_logs_cost
        
    def _get_vpc_type_display(self) -> str:
        """Get display name for VPC type"""
        if self.auto_create_subnetworks:
            return "Auto Mode VPC (automatic subnets)"
        else:
            return "Custom Mode VPC (manual subnets)"
            
    def _fetch_current_cloud_state(self) -> Dict[str, Any]:
        """Fetch current state of the VPC from Google Cloud"""
        self._ensure_authenticated()
        
        try:
            # Get VPC info if it exists
            if self.vpc_manager:
                vpc_info = self.vpc_manager.get_vpc_info(self.vpc_name)
                
                if vpc_info.get("exists", False):
                    # Get subnets info
                    subnets_info = []
                    if self.subnet_manager:
                        subnets_info = self.subnet_manager.list_subnets(self.vpc_name)
                    
                    # Get firewall rules info
                    firewall_info = []
                    if self.firewall_manager:
                        firewall_info = self.firewall_manager.list_firewall_rules(self.vpc_name)
                    
                    return {
                        "exists": True,
                        "vpc_name": self.vpc_name,
                        "description": vpc_info.get("description"),
                        "routing_mode": vpc_info.get("routing_mode"),
                        "auto_create_subnetworks": vpc_info.get("auto_create_subnetworks", False),
                        "mtu": vpc_info.get("mtu", 1460),
                        "creation_timestamp": vpc_info.get("creation_timestamp"),
                        "vpc_url": vpc_info.get("self_link"),
                        "subnets": subnets_info,
                        "subnets_count": len(subnets_info),
                        "firewall_rules": firewall_info,
                        "firewall_rules_count": len(firewall_info),
                        "peerings": vpc_info.get("peerings", []),
                        "peerings_count": len(vpc_info.get("peerings", [])),
                        "labels": vpc_info.get("labels", {}),
                        "enable_flow_logs": vpc_info.get("enable_flow_logs", False),
                        "status": vpc_info.get("status", "UNKNOWN")
                    }
                else:
                    return {
                        "exists": False,
                        "vpc_name": self.vpc_name
                    }
            else:
                return {
                    "exists": False,
                    "vpc_name": self.vpc_name,
                    "error": "VPC manager not initialized"
                }
                
        except Exception as e:
            print(f"⚠️  Warning: Failed to fetch VPC state: {str(e)}")
            return {
                "exists": False,
                "vpc_name": self.vpc_name,
                "error": str(e)
            }