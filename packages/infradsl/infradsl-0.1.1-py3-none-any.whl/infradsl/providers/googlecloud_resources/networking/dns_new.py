"""
GCP Cloud DNS Complete Implementation

Combines all Cloud DNS functionality through multiple inheritance:
- DNSCore: Core attributes and authentication
- DNSConfigurationMixin: Chainable configuration methods  
- DNSLifecycleMixin: Lifecycle operations (create/destroy/preview)
"""

from typing import Dict, Any, List, Optional
from .dns_core import DNSCore, DNSRecord
from .dns_configuration import DNSConfigurationMixin
from .dns_lifecycle import DNSLifecycleMixin


class CloudDNS(DNSLifecycleMixin, DNSConfigurationMixin, DNSCore):
    """
    Complete GCP Cloud DNS implementation for domain name resolution.
    
    This class combines:
    - DNS zone configuration methods (domain, visibility, DNSSEC, records)
    - DNS lifecycle management (create, destroy, preview)
    - Multiple DNS record types (A, AAAA, CNAME, MX, TXT, SRV, etc.)
    - Advanced features (private zones, DNSSEC, logging)
    - Rails-like method chaining for fluent API
    """
    
    def __init__(self, name: str):
        """Initialize CloudDNS instance for domain name resolution"""
        super().__init__(name)
        
        # Additional attributes specific to the combined class
        self.deployment_ready = False
        self.estimated_monthly_cost = "$0.90/month"
        
        # Cross-Cloud Magic integration
        self._optimization_priority = None
        self._dns_type = None
        self._monitoring_enabled = True
        self._auto_scaling_enabled = False
    
    def validate_configuration(self):
        """Validate the current Cloud DNS configuration"""
        errors = []
        warnings = []
        
        # Validate zone name
        if not self.zone_name:
            errors.append("Zone name is required")
        elif not self._is_valid_zone_name(self.zone_name):
            errors.append(f"Invalid zone name format: {self.zone_name}")
        
        # Validate DNS name
        if not self.dns_name:
            errors.append("Domain name is required")
        elif not self._is_valid_dns_name(self.dns_name):
            errors.append(f"Invalid domain name format: {self.dns_name}")
        
        # Validate visibility
        if not self._is_valid_visibility(self.dns_visibility):
            errors.append(f"Invalid visibility: {self.dns_visibility}")
        
        # Validate VPC networks for private zones
        if self.dns_visibility == "private" and not self.vpc_networks:
            warnings.append("Private DNS zone without VPC networks - zone will not be accessible")
        
        # Validate DNSSEC state
        if not self._is_valid_dnssec_state(self.dnssec_state):
            errors.append(f"Invalid DNSSEC state: {self.dnssec_state}")
        
        # Validate DNS records
        for i, record in enumerate(self.dns_records):
            if not self._is_valid_record_type(record.record_type):
                errors.append(f"Invalid record type at index {i}: {record.record_type}")
            
            for value in record.values:
                if not self._validate_record_value(record.record_type, value):
                    warnings.append(f"Potentially invalid {record.record_type} record value: {value}")
        
        # Validate TTL values
        if self.default_ttl < 1 or self.default_ttl > 86400:
            warnings.append("Default TTL should be between 1 and 86400 seconds")
        
        if self.soa_ttl < 1 or self.soa_ttl > 2147483647:
            errors.append("SOA TTL must be between 1 and 2147483647 seconds")
        
        # Security warnings
        if self.dns_visibility == "public" and not self.dnssec_enabled:
            warnings.append("Public DNS zone without DNSSEC - consider enabling for security")
        
        if not self.logging_enabled:
            warnings.append("DNS query logging disabled - consider enabling for monitoring")
        
        # Record type warnings
        has_root_a = any(r.name == self.dns_name and r.record_type == "A" for r in self.dns_records)
        has_www_record = any("www." in r.name for r in self.dns_records)
        
        if not has_root_a and self.dns_visibility == "public":
            warnings.append("No root A record found - visitors may not be able to reach your domain")
        
        if not has_www_record and self.dns_visibility == "public":
            warnings.append("No www subdomain record found - consider adding www.yourdomain.com")
        
        # Check for conflicting CNAME records
        cname_names = {r.name for r in self.dns_records if r.record_type == "CNAME"}
        other_names = {r.name for r in self.dns_records if r.record_type != "CNAME"}
        conflicts = cname_names.intersection(other_names)
        
        if conflicts:
            errors.append(f"CNAME records conflict with other records for: {', '.join(conflicts)}")
        
        if errors:
            raise ValueError(f"Configuration validation failed: {', '.join(errors)}")
        
        if warnings:
            print(f"⚠️  Configuration warnings:")
            for warning in warnings:
                print(f"   - {warning}")
        
        self.deployment_ready = True
        return True
    
    def get_dns_info(self):
        """Get complete information about the Cloud DNS zone"""
        return {
            'zone_name': self.zone_name,
            'dns_name': self.dns_name,
            'description': self.dns_description,
            'visibility': self.dns_visibility,
            'region': self.dns_region,
            'dnssec_enabled': self.dnssec_enabled,
            'dnssec_state': self.dnssec_state,
            'vpc_networks': self.vpc_networks,
            'vpc_networks_count': len(self.vpc_networks),
            'labels_count': len(self.dns_labels),
            'logging_enabled': self.logging_enabled,
            'default_ttl': self.default_ttl,
            'soa_ttl': self.soa_ttl,
            'ns_ttl': self.ns_ttl,
            'records_count': len(self.dns_records),
            'records_by_type': self._get_records_by_type(),
            'name_servers': self.name_servers,
            'zone_exists': self.zone_exists,
            'deployment_ready': self.deployment_ready,
            'estimated_monthly_cost': self.estimated_monthly_cost,
            'optimization_priority': self._optimization_priority,
            'dns_type': self._dns_type
        }
    
    def _get_records_by_type(self):
        """Get count of records by type"""
        record_counts = {}
        for record in self.dns_records:
            record_type = record.record_type
            record_counts[record_type] = record_counts.get(record_type, 0) + 1
        return record_counts
    
    def clone(self, new_name: str):
        """Create a copy of this DNS zone with a new name"""
        cloned_dns = CloudDNS(new_name)
        cloned_dns.zone_name = new_name
        cloned_dns.dns_name = self.dns_name
        cloned_dns.dns_description = self.dns_description
        cloned_dns.dns_visibility = self.dns_visibility
        cloned_dns.dns_region = self.dns_region
        cloned_dns.dnssec_enabled = self.dnssec_enabled
        cloned_dns.dnssec_state = self.dnssec_state
        cloned_dns.vpc_networks = self.vpc_networks.copy()
        cloned_dns.dns_labels = self.dns_labels.copy()
        cloned_dns.logging_enabled = self.logging_enabled
        cloned_dns.logging_config = self.logging_config.copy()
        cloned_dns.default_ttl = self.default_ttl
        cloned_dns.soa_ttl = self.soa_ttl
        cloned_dns.ns_ttl = self.ns_ttl
        # Clone records
        cloned_dns.dns_records = []
        for record in self.dns_records:
            new_record = DNSRecord(record.name, record.record_type, record.ttl)
            new_record.values = record.values.copy()
            cloned_dns.dns_records.append(new_record)
        return cloned_dns
    
    def export_configuration(self):
        """Export DNS configuration for backup or migration"""
        return {
            'metadata': {
                'zone_name': self.zone_name,
                'dns_name': self.dns_name,
                'visibility': self.dns_visibility,
                'region': self.dns_region,
                'exported_at': 'Mock timestamp'
            },
            'configuration': {
                'zone_name': self.zone_name,
                'dns_name': self.dns_name,
                'description': self.dns_description,
                'visibility': self.dns_visibility,
                'dnssec_enabled': self.dnssec_enabled,
                'dnssec_state': self.dnssec_state,
                'vpc_networks': self.vpc_networks,
                'labels': self.dns_labels,
                'logging_enabled': self.logging_enabled,
                'logging_config': self.logging_config,
                'default_ttl': self.default_ttl,
                'soa_ttl': self.soa_ttl,
                'ns_ttl': self.ns_ttl,
                'records': [record.to_dict() for record in self.dns_records],
                'optimization_priority': self._optimization_priority,
                'dns_type': self._dns_type,
                'monitoring_enabled': self._monitoring_enabled,
                'auto_scaling_enabled': self._auto_scaling_enabled
            }
        }
    
    def import_configuration(self, config_data: dict):
        """Import DNS configuration from exported data"""
        if 'configuration' in config_data:
            config = config_data['configuration']
            self.zone_name = config.get('zone_name', self.zone_name)
            self.dns_name = config.get('dns_name')
            self.dns_description = config.get('description', f"DNS zone for {self.zone_name}")
            self.dns_visibility = config.get('visibility', 'public')
            self.dnssec_enabled = config.get('dnssec_enabled', False)
            self.dnssec_state = config.get('dnssec_state', 'off')
            self.vpc_networks = config.get('vpc_networks', [])
            self.dns_labels = config.get('labels', {})
            self.logging_enabled = config.get('logging_enabled', False)
            self.logging_config = config.get('logging_config', {})
            self.default_ttl = config.get('default_ttl', 300)
            self.soa_ttl = config.get('soa_ttl', 21600)
            self.ns_ttl = config.get('ns_ttl', 21600)
            self._optimization_priority = config.get('optimization_priority')
            self._dns_type = config.get('dns_type')
            self._monitoring_enabled = config.get('monitoring_enabled', True)
            self._auto_scaling_enabled = config.get('auto_scaling_enabled', False)
            
            # Import records
            records_data = config.get('records', [])
            self.dns_records = []
            for record_data in records_data:
                record = DNSRecord(record_data['name'], record_data['type'], record_data.get('ttl', 300))
                record.values = record_data.get('rrdatas', [])
                self.dns_records.append(record)
        
        return self
    
    def enable_monitoring(self, enabled: bool = True):
        """Enable comprehensive monitoring and alerting"""
        self._monitoring_enabled = enabled
        if enabled:
            self.logging_enabled = True
            print("📊 Comprehensive monitoring enabled")
            print("   💡 DNS query logging activated")
            print("   💡 Performance monitoring configured")
        return self
    
    def enable_auto_scaling(self, enabled: bool = True):
        """Enable automatic DNS scaling (note: DNS is inherently scalable)"""
        self._auto_scaling_enabled = enabled
        if enabled:
            print("📈 Auto-scaling enabled for DNS")
            print("   💡 DNS queries will be handled automatically")
        return self
    
    def get_zone_statistics(self):
        """Get statistics about the DNS zone"""
        if not self.dns_manager:
            return {"error": "DNS manager not available"}
        
        try:
            stats = self.dns_manager.get_zone_statistics(self.zone_name)
            return {
                "zone_name": self.zone_name,
                "records_count": len(self.dns_records),
                "records_by_type": self._get_records_by_type(),
                "queries_per_day": stats.get("queries_per_day", 0),
                "query_types": stats.get("query_types", {}),
                "response_codes": stats.get("response_codes", {}),
                "geographic_distribution": stats.get("geographic_distribution", {}),
                "period": stats.get("period", "24h")
            }
        except Exception as e:
            return {"error": str(e)}
    
    def get_record_by_name(self, name: str, record_type: str = None):
        """Get DNS record(s) by name and optionally type"""
        formatted_name = self._format_record_name(name)
        
        matching_records = []
        for record in self.dns_records:
            if record.name == formatted_name:
                if record_type is None or record.record_type == record_type.upper():
                    matching_records.append(record)
        
        return matching_records
    
    def remove_record(self, name: str, record_type: str = None):
        """Remove DNS record(s) by name and optionally type"""
        formatted_name = self._format_record_name(name)
        
        records_to_remove = []
        for record in self.dns_records:
            if record.name == formatted_name:
                if record_type is None or record.record_type == record_type.upper():
                    records_to_remove.append(record)
        
        for record in records_to_remove:
            self.dns_records.remove(record)
        
        print(f"🗑️  Removed {len(records_to_remove)} DNS record(s) for '{name}'")
        return self
    
    def update_record_ttl(self, name: str, new_ttl: int, record_type: str = None):
        """Update TTL for DNS record(s)"""
        formatted_name = self._format_record_name(name)
        
        updated_count = 0
        for record in self.dns_records:
            if record.name == formatted_name:
                if record_type is None or record.record_type == record_type.upper():
                    record.ttl = new_ttl
                    updated_count += 1
        
        print(f"⏱️  Updated TTL to {new_ttl}s for {updated_count} record(s)")
        return self
    
    def get_nameservers(self):
        """Get the name servers for this DNS zone"""
        if self.name_servers:
            return self.name_servers
        
        # Try to fetch from cloud state
        current_state = self._fetch_current_cloud_state()
        if current_state.get("exists") and current_state.get("name_servers"):
            self.name_servers = current_state["name_servers"]
            return self.name_servers
        
        return []
    
    def validate_delegation(self):
        """Validate that domain delegation is configured correctly"""
        nameservers = self.get_nameservers()
        
        if not nameservers:
            return {
                "status": "unknown",
                "message": "Cannot validate - nameservers not available"
            }
        
        # In a real implementation, this would check the parent zone
        return {
            "status": "pending",
            "message": f"Configure these nameservers with your domain registrar: {', '.join(nameservers[:2])}...",
            "nameservers": nameservers
        }


# Convenience functions for creating CloudDNS instances
def create_public_dns_zone(name: str, domain: str) -> CloudDNS:
    """Create a public DNS zone"""
    dns = CloudDNS(name)
    dns.domain(domain).public().production_dns()
    return dns

def create_private_dns_zone(name: str, domain: str, vpc_networks: List[str] = None) -> CloudDNS:
    """Create a private DNS zone for VPC networks"""
    dns = CloudDNS(name)
    dns.domain(domain).private(vpc_networks).internal_dns(vpc_networks)
    return dns

def create_development_dns_zone(name: str, domain: str) -> CloudDNS:
    """Create a DNS zone for development environments"""
    dns = CloudDNS(name)
    dns.domain(domain).development_dns().optimize_for("cost")
    return dns

def create_production_dns_zone(name: str, domain: str) -> CloudDNS:
    """Create a DNS zone for production environments"""
    dns = CloudDNS(name)
    dns.domain(domain).production_dns().optimize_for("reliability")
    return dns

def create_staging_dns_zone(name: str, domain: str) -> CloudDNS:
    """Create a DNS zone for staging environments"""
    dns = CloudDNS(name)
    dns.domain(domain).staging_dns().optimize_for("performance")
    return dns

# Alias for backward compatibility
DNS = CloudDNS