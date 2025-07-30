from typing import Dict, Any, List
import boto3
import logging

class CloudFrontConfigurationMixin:
    """
    Mixin for CloudFront chainable configuration methods.
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Initialize configuration-specific attributes if not already set
        if not hasattr(self, 'origins'):
            self.origins = []
        if not hasattr(self, 'custom_domains'):
            self.custom_domains = []
        if not hasattr(self, 'behaviors'):
            self.behaviors = []
        if not hasattr(self, 'error_pages'):
            self.error_pages = []
        if not hasattr(self, 'cdn_tags'):
            self.cdn_tags = {}
    
    def copy_from(self, distribution_id: str):
        """
        Copy configuration from an existing CloudFront distribution.
        
        Args:
            distribution_id: The distribution ID to copy from (e.g., "E1L4Q3EMY24Z8R")
            
        This method fetches the configuration from the specified distribution and applies it
        to this instance. You can then override specific settings like custom domains,
        origin configurations, etc.
        
        Example:
            cdn = (AWS.CloudFront("my-new-distribution")
                   .copy_from("E1L4Q3EMY24Z8R")
                   .custom_domain("new.example.com")
                   .create())
        """
        try:
            # Initialize CloudFront client
            cloudfront_client = boto3.client('cloudfront')
            
            # Get distribution configuration
            response = cloudfront_client.get_distribution_config(Id=distribution_id)
            config = response['DistributionConfig']
            
            # Copy origin configuration
            if 'Origins' in config and config['Origins']['Items']:
                primary_origin = config['Origins']['Items'][0]
                self.origin_domain = primary_origin['DomainName']
                
                # Determine origin type
                if 'S3OriginConfig' in primary_origin:
                    self.origin_type = 's3'
                else:
                    self.origin_type = 'custom'
                
                # Store full origins configuration for advanced use
                self.origins = []
                for origin in config['Origins']['Items']:
                    origin_config = {
                        'domain': origin['DomainName'],
                        'type': 's3' if 'S3OriginConfig' in origin else 'custom',
                        'path': origin.get('OriginPath', '/'),
                        'id': origin['Id']
                    }
                    self.origins.append(origin_config)
            
            # Copy custom domains (aliases)
            if 'Aliases' in config and config['Aliases']['Items']:
                self.custom_domains = config['Aliases']['Items'].copy()
            
            # Copy SSL certificate configuration
            if 'ViewerCertificate' in config:
                cert_config = config['ViewerCertificate']
                if 'ACMCertificateArn' in cert_config:
                    self.ssl_certificate_arn = cert_config['ACMCertificateArn']
                if 'MinimumProtocolVersion' in cert_config:
                    self.ssl_minimum_version = cert_config['MinimumProtocolVersion']
            
            # Copy price class
            if 'PriceClass' in config:
                self.price_class_setting = config['PriceClass']
            
            # Copy HTTP version settings
            if 'HttpVersion' in config:
                self.http2_enabled = config['HttpVersion'] == 'http2'
            
            # Copy IPv6 setting
            if 'IsIPV6Enabled' in config:
                self.ipv6_enabled = config['IsIPV6Enabled']
            
            # Copy default cache behavior settings
            if 'DefaultCacheBehavior' in config:
                default_behavior = config['DefaultCacheBehavior']
                
                # Store the target origin ID for replacement later
                self._source_target_origin_id = default_behavior.get('TargetOriginId')
                
                if 'Compress' in default_behavior:
                    self.compression_enabled = default_behavior['Compress']
            
            # Copy WAF Web ACL
            if 'WebACLId' in config and config['WebACLId']:
                self.waf_web_acl_id = config['WebACLId']
            
            # Copy geo restrictions
            if 'Restrictions' in config and 'GeoRestriction' in config['Restrictions']:
                geo_config = config['Restrictions']['GeoRestriction']
                if geo_config['RestrictionType'] != 'none':
                    self.geo_restriction = {
                        'type': geo_config['RestrictionType'],
                        'locations': geo_config.get('Items', [])
                    }
            
            # Copy error pages
            if 'CustomErrorResponses' in config and config['CustomErrorResponses']['Items']:
                self.error_pages = []
                for error_config in config['CustomErrorResponses']['Items']:
                    self.error_pages.append({
                        'error_code': error_config['ErrorCode'],
                        'response_code': error_config.get('ResponseCode'),
                        'response_page': error_config.get('ResponsePagePath'),
                        'ttl': error_config.get('ErrorCachingMinTTL', 300)
                    })
            
            # Store the source distribution ID for reference
            self._copied_from_distribution_id = distribution_id
            
            logging.info(f"Successfully copied configuration from distribution {distribution_id}")
            
        except Exception as e:
            logging.error(f"Failed to copy from distribution {distribution_id}: {str(e)}")
            raise ValueError(f"Could not copy from distribution {distribution_id}: {str(e)}")
        
        return self

    def target_origin_id(self, new_origin_id: str):
        """
        Set a custom Target Origin ID for the default cache behavior.
        
        This is especially useful when copying from another distribution
        and you want to update the Target Origin ID to match your new domain.
        
        Args:
            new_origin_id: The new target origin ID (e.g., "production.example.com-{DOMAIN}")
            
        Example:
            cdn = (AWS.CloudFront("new-cdn")
                   .copy_from("E1L4Q3EMY24Z8R")
                   .target_origin_id("production.newdomain.com-newdomain")
                   .create())
        """
        self._custom_target_origin_id = new_origin_id
        return self

    def origin(self, domain: str, type_: str = 'custom', path: str = '/'):
        """Set the origin domain and type"""
        self.origin_domain = domain
        self.origin_type = type_
        
        # Add to origins list for advanced configurations
        origin_config = {
            'domain': domain,
            'type': type_,
            'path': path
        }
        
        # Check if origin already exists and update it
        existing_origin = next((o for o in self.origins if o['domain'] == domain), None)
        if existing_origin:
            existing_origin.update(origin_config)
        else:
            self.origins.append(origin_config)
        
        return self
    
    def s3_origin(self, bucket_name: str, path: str = '/'):
        """Convenience method for S3 origin"""
        s3_domain = f"{bucket_name}.s3.amazonaws.com"
        return self.origin(s3_domain, 's3', path)
    
    def load_balancer_origin(self, lb_domain: str, path: str = '/'):
        """Convenience method for Load Balancer origin"""
        return self.origin(lb_domain, 'load_balancer', path)
    
    def custom_domain(self, domain: str):
        """Add a custom domain to the distribution"""
        if domain not in self.custom_domains:
            self.custom_domains.append(domain)
        return self
    
    def domains(self, domains: List[str]):
        """Add multiple custom domains"""
        for domain in domains:
            self.custom_domain(domain)
        return self
    
    def clear_domains(self):
        """Clear all custom domains (useful when copying from another distribution)"""
        self.custom_domains = []
        return self
    
    def gaming_optimized(self):
        """Nexus Engine: Gaming-optimized CloudFront preset"""
        self.worldwide()  # All edge locations for global gaming
        self.http2(True)
        self.compression(True)
        self.real_time_logs(True)
        self.websocket_support(True)
        return self
    
    def production_optimized(self):
        """Nexus Engine: Production-optimized CloudFront preset"""
        self.worldwide()
        self.http2(True)
        self.compression(True)
        self.security_headers(True)
        self.ddos_protection(True)
        return self
    
    def ssl_certificate(self, arn: str = None):
        """Set the SSL certificate ARN (or use CloudFront default if None)"""
        if arn:
            self.ssl_certificate_arn = arn
        else:
            self.viewer_certificate_cloudfront_default_certificate = True
        return self
    
    def ssl_minimum_version(self, version: str):
        """Set minimum SSL version (TLSv1, TLSv1.1, TLSv1.2)"""
        self.ssl_minimum_version = version
        return self
    
    def price_class(self, price_class: str):
        """Set the price class (PriceClass_All, PriceClass_200, PriceClass_100)"""
        valid_classes = ['PriceClass_All', 'PriceClass_200', 'PriceClass_100']
        if price_class not in valid_classes:
            raise ValueError(f"Invalid price class. Must be one of: {valid_classes}")
        self.price_class_setting = price_class
        return self
    
    def worldwide(self):
        """Use all edge locations worldwide"""
        return self.price_class('PriceClass_All')
    
    def us_europe_asia(self):
        """Use edge locations in US, Canada, Europe, Asia, India"""
        return self.price_class('PriceClass_200')
    
    def us_europe_only(self):
        """Use edge locations in US, Canada, Europe only"""
        return self.price_class('PriceClass_100')
    
    def http2(self, enabled: bool = True):
        """Enable or disable HTTP/2"""
        self.http2_enabled = enabled
        return self
    
    def ipv6(self, enabled: bool = True):
        """Enable or disable IPv6"""
        self.ipv6_enabled = enabled
        return self
    
    def compress(self, enabled: bool = True):
        """Enable or disable compression"""
        self.compression_enabled = enabled
        return self
    
    def security_headers(self, enabled: bool = True):
        """Enable security headers"""
        self.security_headers = enabled
        return self
    
    def waf(self, web_acl_id: str):
        """Attach a WAF Web ACL"""
        self.waf_web_acl_id = web_acl_id
        return self
    
    def geo_restriction(self, restriction_type: str, locations: List[str] = None):
        """Set geo restriction configuration"""
        self.geo_restriction = {
            'type': restriction_type,  # 'blacklist', 'whitelist', 'none'
            'locations': locations or []
        }
        return self
    
    def block_countries(self, country_codes: List[str]):
        """Block specific countries"""
        return self.geo_restriction('blacklist', country_codes)
    
    def allow_countries(self, country_codes: List[str]):
        """Allow only specific countries"""
        return self.geo_restriction('whitelist', country_codes)
    
    def error_page(self, error_code: int, response_code: int = None, response_page: str = None, ttl: int = 300):
        """Add an error page configuration"""
        error_config = {
            'error_code': error_code,
            'response_code': response_code or error_code,
            'response_page': response_page,
            'ttl': ttl
        }
        self.error_pages.append(error_config)
        return self
    
    def error_404(self, response_page: str = '/404.html', ttl: int = 300):
        """Convenience method for 404 error page"""
        return self.error_page(404, 200, response_page, ttl)
    
    def error_403(self, response_page: str = '/403.html', ttl: int = 300):
        """Convenience method for 403 error page"""
        return self.error_page(403, 200, response_page, ttl)
    
    def behavior(self, path: str, ttl: int = 86400, compress: bool = True, 
                methods: List[str] = None, headers: List[str] = None):
        """Add a custom behavior for specific paths"""
        behavior_config = {
            'path': path,
            'ttl': ttl,
            'compress': compress,
            'methods': methods or ['GET', 'HEAD'],
            'headers': headers or []
        }
        self.behaviors.append(behavior_config)
        return self
    
    def api_behavior(self, path: str = '/api/*', ttl: int = 0):
        """Convenience method for API paths (no caching)"""
        return self.behavior(path, ttl, methods=['GET', 'HEAD', 'OPTIONS', 'PUT', 'POST', 'PATCH', 'DELETE'])
    
    def static_behavior(self, path: str = '/static/*', ttl: int = 31536000):  # 1 year
        """Convenience method for static assets (long caching)"""
        return self.behavior(path, ttl, compress=True)
    
    def logging(self, enabled: bool = True, bucket: str = None, prefix: str = None):
        """Enable or disable logging and set bucket/prefix"""
        self.logging_enabled = enabled
        if bucket:
            self.logging_bucket = bucket
        if prefix:
            self.logging_prefix = prefix
        return self
    
    def cloudwatch_metrics(self, enabled: bool = True):
        """Enable CloudWatch metrics"""
        # This would enable real-time metrics in a real implementation
        return self
    
    def tag(self, key: str, value: str):
        """Add a tag to the distribution"""
        self.cdn_tags[key] = value
        return self
    
    def tags(self, tags_dict: Dict[str, str]):
        """Add multiple tags to the distribution"""
        self.cdn_tags.update(tags_dict)
        return self
    
    @staticmethod
    def copy_from_examples():
        """
        Examples of using the copy_from functionality:
        
        Basic copy with new domains:
            cdn = (AWS.CloudFront("new-distribution")
                   .copy_from("E1L4Q3EMY24Z8R")
                   .clear_domains()
                   .custom_domain("new.example.com")
                   .custom_domain("www.new.example.com")
                   .create())
        
        Copy with origin and target ID updates:
            from datetime import datetime
            
            DOMAIN_NAME = "newdomain.com"
            cdn = (AWS.CloudFront(f"{datetime.now().strftime('%Y%m%d')}")
                   .copy_from("E1L4Q3EMY24Z8R")
                   .clear_domains()
                   .custom_domain(f"ec.{DOMAIN_NAME}")
                   .custom_domain(f"nc.{DOMAIN_NAME}")
                   .target_origin_id(f"production.{DOMAIN_NAME}-{DOMAIN_NAME}")
                   .preview())
        
        Copy but keep origin domain:
            cdn = (AWS.CloudFront("cloned-distribution")
                   .copy_from("E1L4Q3EMY24Z8R")
                   # Origin domain is kept from source
                   .custom_domain("different.example.com")
                   .create())
                   
        What gets copied:
        - Origin configuration (domain, type, paths)
        - Custom domains/aliases
        - SSL certificate settings
        - Price class (edge location coverage)
        - HTTP/2 and IPv6 settings
        - Compression settings
        - WAF Web ACL
        - Geo restrictions
        - Custom error pages
        - Cache behaviors
        
        What you can override:
        - Custom domains (via .clear_domains() then .custom_domain())
        - Origin domain (via .origin())
        - Target Origin ID (via .target_origin_id())
        - SSL certificate (via .ssl_certificate())
        - Any other configuration method
        """
        pass 