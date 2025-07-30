"""
AWS CloudFront Complete Implementation

Combines all CloudFront functionality through multiple inheritance:
- CloudFrontCore: Core attributes and authentication
- CloudFrontConfigurationMixin: Chainable configuration methods
- CloudFrontLifecycleMixin: Lifecycle operations (create/destroy/preview)
"""

from .cloudfront_core import CloudFrontCore
from .cloudfront_configuration import CloudFrontConfigurationMixin
from .cloudfront_lifecycle import CloudFrontLifecycleMixin


class CloudFront(CloudFrontLifecycleMixin, CloudFrontConfigurationMixin, CloudFrontCore):
    """
    Complete AWS CloudFront implementation for CDN and content delivery.
    
    This class combines:
    - CDN configuration methods (origins, behaviors, caching rules)
    - Distribution lifecycle management (create, destroy, preview)
    - SSL certificates and custom domains
    - Performance and security optimizations
    - Rails-like method chaining for fluent API
    """
    
    def __init__(self, name: str):
        """Initialize CloudFront instance for CDN management"""
        super().__init__(name)
        
        # Additional attributes specific to the combined class
        self.deployment_ready = False
        self.edge_locations_count = 0
    
    def validate_configuration(self):
        """Validate the current CloudFront configuration"""
        errors = []
        
        # Validate origin
        if not self.origin_domain:
            errors.append("Origin domain is required")
        
        # Validate custom domains have SSL certificate
        if self.custom_domains and not self.ssl_certificate_arn:
            errors.append("SSL certificate is required when using custom domains")
        
        # Validate price class
        valid_price_classes = ['PriceClass_All', 'PriceClass_200', 'PriceClass_100']
        if self.price_class_setting and self.price_class_setting not in valid_price_classes:
            errors.append(f"Invalid price class. Must be one of: {valid_price_classes}")
        
        if errors:
            raise ValueError(f"Configuration validation failed: {', '.join(errors)}")
        
        self.deployment_ready = True
        return True
    
    def get_distribution_info(self):
        """Get complete information about the CloudFront distribution"""
        return {
            'distribution_arn': self.distribution_arn,
            'distribution_domain': self.distribution_domain,
            'distribution_status': self.distribution_status,
            'origin_domain': self.origin_domain,
            'custom_domains_count': len(self.custom_domains),
            'behaviors_count': len(self.behaviors),
            'ssl_enabled': bool(self.ssl_certificate_arn),
            'http2_enabled': self.http2_enabled,
            'ipv6_enabled': self.ipv6_enabled,
            'compression_enabled': self.compression_enabled,
            'waf_enabled': bool(self.waf_web_acl_id),
            'geo_restrictions': bool(self.geo_restriction),
            'logging_enabled': self.logging_enabled,
            'price_class': self.price_class_setting or 'PriceClass_All',
            'tags_count': len(self.cdn_tags),
            'deployment_ready': self.deployment_ready
        }
    
    def estimate_monthly_cost(self):
        """Estimate monthly costs for the CloudFront distribution"""
        # Base pricing estimates (simplified)
        base_cost = 0.00
        
        # Data transfer costs (per GB)
        data_transfer_cost = 0.085  # $0.085/GB for first 10TB
        estimated_monthly_gb = 100  # Conservative estimate
        
        # Request costs
        http_requests = 1000000  # 1M requests
        https_requests = 1000000  # 1M requests
        request_cost = (http_requests * 0.0075 / 10000) + (https_requests * 0.0100 / 10000)
        
        # SSL certificate cost (if using custom domains)
        ssl_cost = 600 if self.custom_domains else 0  # $600/year for dedicated SSL
        
        # Edge locations factor
        price_class_multiplier = {
            'PriceClass_100': 0.6,    # US, Canada, Europe
            'PriceClass_200': 0.8,    # + Asia, India, South America
            'PriceClass_All': 1.0     # All edge locations
        }.get(self.price_class_setting, 1.0)
        
        monthly_cost = (
            (data_transfer_cost * estimated_monthly_gb * price_class_multiplier) +
            request_cost +
            (ssl_cost / 12)  # Annual SSL cost divided by 12
        )
        
        return f"${monthly_cost:.2f}"


# Convenience function for creating CloudFront instances
def create_cdn(name: str, origin_domain: str) -> CloudFront:
    """Create a new CloudFront CDN distribution"""
    return CloudFront(name).origin(origin_domain)