"""
GCP Cloud DNS Core Implementation

Core attributes and authentication for Google Cloud DNS zones.
Provides the foundation for the modular DNS system.
"""

from typing import Dict, Any, List, Optional
from ..base_resource import BaseGcpResource


class DNSRecord:
    """Represents a DNS record for Cloud DNS"""
    
    def __init__(self, name: str, record_type: str, ttl: int = 300):
        self.name = name
        self.record_type = record_type.upper()
        self.ttl = ttl
        self.values = []
        
    def add_value(self, value: str):
        """Add a value to this DNS record"""
        self.values.append(value)
        return self
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert to API format"""
        return {
            'name': self.name,
            'type': self.record_type,
            'ttl': self.ttl,
            'rrdatas': self.values
        }


class DNSCore(BaseGcpResource):
    """
    Core class for Google Cloud DNS functionality.
    
    This class provides:
    - Basic DNS zone attributes and configuration
    - Authentication setup
    - Common utilities for DNS operations
    """
    
    def __init__(self, name: str):
        """Initialize DNS core with zone name"""
        super().__init__(name)
        
        # Core DNS zone attributes
        self.zone_name = name
        self.dns_name = None  # Domain name (e.g., example.com.)
        self.dns_description = f"DNS zone for {name}"
        self.dns_visibility = "public"  # public or private
        self.dns_region = "global"  # DNS is global in GCP
        
        # DNS configuration
        self.dnssec_enabled = False
        self.vpc_networks = []
        self.forwarding_targets = []
        self.dns_labels = {}
        
        # DNS records
        self.dns_records = []
        
        # Zone configuration
        self.reverse_lookup = False
        self.logging_enabled = False
        self.logging_config = {}
        
        # DNSSEC configuration
        self.dnssec_state = "off"  # off, on, transfer
        self.key_signing_key_algorithm = "rsasha256"
        self.zone_signing_key_algorithm = "rsasha256"
        
        # Performance settings
        self.default_ttl = 300
        self.soa_ttl = 21600  # SOA record TTL
        self.ns_ttl = 21600   # NS record TTL
        
        # State tracking
        self.zone_exists = False
        self.zone_created = False
        self.name_servers = []
        
    def _initialize_managers(self):
        """Initialize DNS-specific managers"""
        # Will be set up after authentication
        self.dns_manager = None
        
    def _post_authentication_setup(self):
        """Setup managers after authentication"""
        # Import here to avoid circular imports
        from ...googlecloud_managers.dns.dns_manager import DNSManager
        self.dns_manager = DNSManager(self.gcp_client)
        
        # Set up project-specific configurations
        self.project_id = self.gcp_client.project_id
        
    def _is_valid_zone_name(self, zone_name: str) -> bool:
        """Check if zone name is valid for GCP Cloud DNS"""
        # Zone names must be lowercase, contain only letters, numbers, and hyphens
        import re
        pattern = r'^[a-z0-9][a-z0-9-]*[a-z0-9]$'
        return bool(re.match(pattern, zone_name)) and len(zone_name) <= 63
        
    def _is_valid_dns_name(self, dns_name: str) -> bool:
        """Check if DNS domain name is valid"""
        if not dns_name:
            return False
        
        # Must end with a dot for fully qualified domain name
        if not dns_name.endswith('.'):
            return False
            
        # Remove trailing dot for validation
        domain = dns_name[:-1]
        
        # Basic domain validation
        import re
        pattern = r'^[a-zA-Z0-9]([a-zA-Z0-9-]*[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9-]*[a-zA-Z0-9])?)*$'
        return bool(re.match(pattern, domain)) and len(domain) <= 253
        
    def _is_valid_record_type(self, record_type: str) -> bool:
        """Check if DNS record type is valid"""
        valid_types = [
            "A", "AAAA", "CAA", "CNAME", "DNSKEY", "DS", "IPSECKEY", 
            "MX", "NAPTR", "NS", "PTR", "SOA", "SPF", "SRV", "SSHFP", 
            "TLSA", "TXT"
        ]
        return record_type.upper() in valid_types
        
    def _is_valid_visibility(self, visibility: str) -> bool:
        """Check if DNS zone visibility is valid"""
        valid_visibilities = ["public", "private"]
        return visibility.lower() in valid_visibilities
        
    def _is_valid_dnssec_state(self, state: str) -> bool:
        """Check if DNSSEC state is valid"""
        valid_states = ["off", "on", "transfer"]
        return state.lower() in valid_states
        
    def _format_record_name(self, name: str) -> str:
        """Format record name with proper domain suffix"""
        if name == '@':
            # Root domain
            return self.dns_name or f"{self.zone_name}."
        elif name.endswith('.'):
            # Already fully qualified
            return name
        else:
            # Add domain suffix
            domain = self.dns_name or f"{self.zone_name}."
            return f"{name}.{domain}"
            
    def _validate_record_value(self, record_type: str, value: str) -> bool:
        """Validate DNS record value based on type"""
        import re
        
        if record_type == "A":
            # IPv4 address validation
            pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
            if not re.match(pattern, value):
                return False
            # Check each octet is 0-255
            octets = value.split('.')
            return all(0 <= int(octet) <= 255 for octet in octets)
            
        elif record_type == "AAAA":
            # IPv6 address validation (simplified)
            pattern = r'^[0-9a-fA-F:]+$'
            return bool(re.match(pattern, value)) and '::' in value or value.count(':') == 7
            
        elif record_type == "CNAME":
            # CNAME should be a valid domain name
            return self._is_valid_dns_name(value) or value.endswith('.')
            
        elif record_type == "MX":
            # MX format: "priority mailserver"
            parts = value.split(' ', 1)
            if len(parts) != 2:
                return False
            try:
                priority = int(parts[0])
                return 0 <= priority <= 65535 and self._is_valid_dns_name(parts[1] + '.')
            except ValueError:
                return False
                
        elif record_type == "TXT":
            # TXT records can contain any text, but should be quoted
            return len(value) <= 255
            
        elif record_type == "SRV":
            # SRV format: "priority weight port target"
            parts = value.split()
            if len(parts) != 4:
                return False
            try:
                priority, weight, port = map(int, parts[:3])
                target = parts[3]
                return (0 <= priority <= 65535 and 
                       0 <= weight <= 65535 and 
                       0 <= port <= 65535 and 
                       self._is_valid_dns_name(target + '.'))
            except ValueError:
                return False
                
        # For other record types, basic validation
        return len(value) > 0 and len(value) <= 65535
        
    def _get_record_type_description(self, record_type: str) -> str:
        """Get description for DNS record type"""
        descriptions = {
            "A": "IPv4 Address",
            "AAAA": "IPv6 Address", 
            "CNAME": "Canonical Name",
            "MX": "Mail Exchange",
            "TXT": "Text Record",
            "NS": "Name Server",
            "SRV": "Service Record",
            "PTR": "Pointer Record",
            "SOA": "Start of Authority",
            "CAA": "Certificate Authority Authorization"
        }
        return descriptions.get(record_type.upper(), record_type.upper())
        
    def _estimate_dns_cost(self) -> float:
        """Estimate monthly cost for DNS zone"""
        # GCP Cloud DNS pricing (simplified)
        base_cost = 0.50  # $0.50/month per hosted zone
        
        # Query cost (estimated)
        estimated_queries = 100000  # 100K queries per month
        query_cost = (estimated_queries / 1000000) * 0.40  # $0.40 per million queries
        
        return base_cost + query_cost
        
    def _fetch_current_cloud_state(self) -> Dict[str, Any]:
        """Fetch current state of the DNS zone from Google Cloud"""
        self._ensure_authenticated()
        
        try:
            # Get DNS zone info if it exists
            if self.dns_manager:
                zone_info = self.dns_manager.get_zone_info(self.zone_name)
                
                if zone_info.get("exists", False):
                    return {
                        "exists": True,
                        "zone_name": self.zone_name,
                        "dns_name": zone_info.get("dns_name"),
                        "description": zone_info.get("description"),
                        "visibility": zone_info.get("visibility"),
                        "dnssec_enabled": zone_info.get("dnssec_enabled", False),
                        "creation_time": zone_info.get("creation_time"),
                        "name_servers": zone_info.get("name_servers", []),
                        "records_count": zone_info.get("records_count", 0),
                        "records": zone_info.get("records", []),
                        "vpc_networks": zone_info.get("vpc_networks", []),
                        "labels": zone_info.get("labels", {}),
                        "logging_enabled": zone_info.get("logging_enabled", False),
                        "status": zone_info.get("status", "UNKNOWN")
                    }
                else:
                    return {
                        "exists": False,
                        "zone_name": self.zone_name
                    }
            else:
                return {
                    "exists": False,
                    "zone_name": self.zone_name,
                    "error": "DNS manager not initialized"
                }
                
        except Exception as e:
            print(f"⚠️  Warning: Failed to fetch DNS zone state: {str(e)}")
            return {
                "exists": False,
                "zone_name": self.zone_name,
                "error": str(e)
            }