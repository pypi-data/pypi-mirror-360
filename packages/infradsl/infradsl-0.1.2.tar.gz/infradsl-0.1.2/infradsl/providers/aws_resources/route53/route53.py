"""
AWS Route53 Complete Implementation

Combines all Route53 functionality through multiple inheritance:
- Route53Core: Core attributes and authentication
- Route53ConfigurationMixin: Chainable configuration methods
- Route53LifecycleMixin: Lifecycle operations (create/destroy/preview)
"""

from .route53_core import Route53Core
from .route53_configuration import Route53ConfigurationMixin
from .route53_lifecycle import Route53LifecycleMixin


class Route53(Route53LifecycleMixin, Route53ConfigurationMixin, Route53Core):
    """
    Complete AWS Route53 implementation with hosted zone and DNS record management.
    
    This class combines:
    - DNS record configuration methods (A, CNAME, MX, TXT, etc.)
    - Hosted zone lifecycle management (create, destroy, preview)
    - Health checks and VPC associations
    - Rails-like method chaining for fluent API
    """
    
    def __init__(self, name: str):
        """Initialize Route53 instance for DNS management"""
        super().__init__(name)
        
        # Additional attributes specific to the combined class
        self.deployment_ready = False
    
    def validate_configuration(self):
        """Validate the current Route53 configuration"""
        errors = []
        
        # Validate domain name
        if not self.domain_name and not self.name:
            errors.append("Domain name is required")
        
        # Validate private zone VPC associations
        if self.zone_type == 'private' and not self.vpc_associations:
            errors.append("Private zones require at least one VPC association")
        
        # Validate record types
        for record in self.records:
            if record['type'] not in ['A', 'AAAA', 'CNAME', 'MX', 'TXT', 'SRV', 'NS', 'PTR']:
                errors.append(f"Invalid record type: {record['type']}")
        
        if errors:
            raise ValueError(f"Configuration validation failed: {', '.join(errors)}")
        
        self.deployment_ready = True
        return True
    
    def get_name_servers(self):
        """Get the name servers for the hosted zone"""
        if not self.hosted_zone_id:
            return None
        
        # In real implementation, this would query AWS
        return [
            'ns-1234.awsdns-12.com',
            'ns-567.awsdns-34.net',
            'ns-890.awsdns-56.org',
            'ns-123.awsdns-78.co.uk'
        ]
    
    def get_zone_info(self):
        """Get complete information about the hosted zone"""
        return {
            'zone_id': self.hosted_zone_id,
            'domain_name': self.domain_name or self.name,
            'zone_type': self.zone_type,
            'records_count': len(self.records),
            'health_checks_count': len(self.health_checks),
            'vpc_associations_count': len(self.vpc_associations),
            'tags_count': len(self.tags),
            'zone_exists': self.zone_exists,
            'deployment_ready': self.deployment_ready
        }


# Convenience function for creating Route53 instances
def create_dns_zone(domain_name: str) -> Route53:
    """Create a new Route53 DNS zone"""
    return Route53(domain_name).zone(domain_name)