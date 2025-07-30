from ..base_resource import BaseAwsResource

class CloudFrontCore(BaseAwsResource):
    """
    Core CloudFront class with main attributes and authentication logic.
    """
    def __init__(self, name: str):
        super().__init__(name)
        # Core attributes (to be filled in)
        self.distribution_arn = None
        self.distribution_domain = None
        self.distribution_status = None
        self.origins = []
        self.origin_domain = None
        self.origin_type = None
        self.default_behavior = None
        self.custom_domains = []
        self.ssl_certificate_arn = None
        self.ssl_minimum_version = None
        self.price_class_setting = None
        self.http2_enabled = True
        self.ipv6_enabled = True
        self.behaviors = []
        self.compression_enabled = True
        self.security_headers = True
        self.waf_web_acl_id = None
        self.geo_restriction = None
        self.error_pages = []
        self.logging_enabled = False
        self.logging_bucket = None
        self.logging_prefix = 'cloudfront-logs/'
        self.cdn_tags = {}
        self.distribution_created = False
        self.cloudfront_manager = None
        
        # Copy-from functionality attributes
        self._copied_from_distribution_id = None
        self._source_target_origin_id = None
        self._custom_target_origin_id = None

    def _initialize_managers(self):
        """Initialize resource-specific managers"""
        pass

    def _post_authentication_setup(self):
        """Setup after authentication"""
        # Initialize CloudFront client for CDN management
        pass
    
    def create(self):
        """Create/update CloudFront distribution - delegates to lifecycle mixin"""
        # Import here to avoid circular imports
        from .cloudfront_lifecycle import CloudFrontLifecycleMixin
        # Call the lifecycle mixin's create method
        return CloudFrontLifecycleMixin.create(self)

    def destroy(self):
        """Destroy CloudFront distribution - delegates to lifecycle mixin"""
        # Import here to avoid circular imports
        from .cloudfront_lifecycle import CloudFrontLifecycleMixin
        # Call the lifecycle mixin's destroy method
        return CloudFrontLifecycleMixin.destroy(self)

    def preview(self):
        """Preview CloudFront distribution configuration - delegates to lifecycle mixin"""
        # Import here to avoid circular imports
        from .cloudfront_lifecycle import CloudFrontLifecycleMixin
        # Call the lifecycle mixin's preview method
        return CloudFrontLifecycleMixin.preview(self) 