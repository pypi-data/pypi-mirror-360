"""
AWS CloudFront Configuration

Handles CloudFront distribution configuration including SSL certificates,
logging, geo restrictions, and complete distribution config assembly.
"""

import time
from typing import Dict, Any, List, Optional


class CloudFrontConfiguration:
    """Manages CloudFront distribution configurations"""

    def __init__(self, aws_client):
        self.aws_client = aws_client

    def build_complete_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Build complete CloudFront distribution configuration"""
        
        # Generate caller reference (unique identifier)
        caller_reference = f"infradsl-{config['name']}-{int(time.time())}"
        
        # Build the distribution config
        distribution_config = {
            'CallerReference': caller_reference,
            'Comment': f"Managed by InfraDSL: {config['name']}",
            'Enabled': True,
            'Origins': {
                'Quantity': len(config['origins']),
                'Items': config['origins']
            },
            'DefaultCacheBehavior': config['default_behavior'],
            'PriceClass': config.get('price_class', 'PriceClass_All'),
            'HttpVersion': 'http2' if config.get('http2_enabled', True) else 'http1.1',
            'IsIPV6Enabled': config.get('ipv6_enabled', True),
            'WebACLId': config.get('waf_web_acl_id', '')
        }
        
        # Add optional configurations
        aliases = config.get('custom_domains', [])
        if aliases:
            distribution_config['Aliases'] = {'Quantity': len(aliases), 'Items': aliases}
        else:
            distribution_config['Aliases'] = {'Quantity': 0}
            
        cache_behaviors = config.get('cache_behaviors', [])
        if cache_behaviors:
            distribution_config['CacheBehaviors'] = {
                'Quantity': len(cache_behaviors),
                'Items': cache_behaviors
            }
        else:
            distribution_config['CacheBehaviors'] = {'Quantity': 0}
            
        # SSL/TLS configuration
        if config.get('ssl_certificate_arn') and aliases:
            distribution_config['ViewerCertificate'] = self.build_ssl_config({
                'certificate_arn': config['ssl_certificate_arn'],
                'ssl_minimum_version': config.get('ssl_minimum_version', 'TLSv1.2_2021')
            })
        else:
            distribution_config['ViewerCertificate'] = {
                'CloudFrontDefaultCertificate': True,
                'MinimumProtocolVersion': 'TLSv1',
                'CertificateSource': 'cloudfront'
            }
            
        # Logging configuration
        if config.get('logging_enabled'):
            distribution_config['Logging'] = self.build_logging_config({
                'enabled': True,
                'bucket': config.get('logging_bucket'),
                'prefix': config.get('logging_prefix', 'cloudfront-logs/')
            })
        else:
            distribution_config['Logging'] = {
                'Enabled': False,
                'IncludeCookies': False,
                'Bucket': '',
                'Prefix': ''
            }
            
        # Geo restrictions
        if config.get('geo_restriction'):
            distribution_config['Restrictions'] = self.build_geo_restrictions(config['geo_restriction'])
        else:
            distribution_config['Restrictions'] = {
                'GeoRestriction': {
                    'RestrictionType': 'none',
                    'Quantity': 0
                }
            }
            
        # Error pages
        error_pages = config.get('error_pages', [])
        if error_pages:
            distribution_config['CustomErrorResponses'] = {
                'Quantity': len(error_pages),
                'Items': [
                    {
                        'ErrorCode': error['error_code'],
                        'ResponsePagePath': error['response_page_path'],
                        'ResponseCode': str(error['response_code']),
                        'ErrorCachingMinTTL': error.get('error_caching_min_ttl', 300)
                    }
                    for error in error_pages
                ]
            }
        else:
            distribution_config['CustomErrorResponses'] = {'Quantity': 0}
        
        return distribution_config

    def build_ssl_config(self, ssl_config: Dict[str, Any]) -> Dict[str, Any]:
        """Build viewer certificate configuration"""
        return {
            'ACMCertificateArn': ssl_config['certificate_arn'],
            'SSLSupportMethod': 'sni-only',
            'MinimumProtocolVersion': ssl_config.get('ssl_minimum_version', 'TLSv1.2_2021'),
            'CertificateSource': 'acm'
        }

    def build_logging_config(self, logging_config: Dict[str, Any]) -> Dict[str, Any]:
        """Build logging configuration"""
        if logging_config.get('enabled') and logging_config.get('bucket'):
            return {
                'Enabled': True,
                'IncludeCookies': logging_config.get('include_cookies', False),
                'Bucket': logging_config['bucket'],
                'Prefix': logging_config.get('prefix', 'cloudfront-logs/')
            }
        else:
            return {
                'Enabled': False,
                'IncludeCookies': False,
                'Bucket': '',
                'Prefix': ''
            }

    def build_geo_restrictions(self, geo_config: Dict[str, Any]) -> Dict[str, Any]:
        """Build geo restrictions"""
        if geo_config:
            return {
                'GeoRestriction': {
                    'RestrictionType': geo_config['type'],  # 'whitelist' or 'blacklist'
                    'Quantity': len(geo_config['countries']),
                    'Items': geo_config['countries']
                }
            }
        else:
            return {
                'GeoRestriction': {
                    'RestrictionType': 'none',
                    'Quantity': 0
                }
            }

    def build_static_site_config(
        self,
        name: str,
        origin_domain: str,
        custom_domains: List[str] = None,
        ssl_certificate_arn: str = None
    ) -> Dict[str, Any]:
        """Build optimized config for static sites"""
        from .origins import CloudFrontOrigins
        from .behaviors import CloudFrontBehaviors
        
        origins_manager = CloudFrontOrigins(self.aws_client)
        behaviors_manager = CloudFrontBehaviors(self.aws_client)
        
        # Create S3 origin
        origins = [origins_manager.create_s3_origin('default-origin', origin_domain)]
        
        # Create static site behavior
        default_behavior = behaviors_manager.create_static_site_behavior()
        
        config = {
            'name': name,
            'origins': origins_manager.build_origins_config(origins),
            'default_behavior': behaviors_manager.build_default_behavior(default_behavior),
            'custom_domains': custom_domains or [],
            'ssl_certificate_arn': ssl_certificate_arn,
            'price_class': 'PriceClass_100',  # Cheaper for static sites
            'http2_enabled': True,
            'ipv6_enabled': True,
            'compression_enabled': True,
            'error_pages': [
                {'error_code': 404, 'response_page_path': '/404.html', 'response_code': 404},
                {'error_code': 403, 'response_page_path': '/404.html', 'response_code': 404}
            ]
        }
        
        return self.build_complete_config(config)

    def build_api_config(
        self,
        name: str,
        api_domain: str,
        custom_domains: List[str] = None,
        ssl_certificate_arn: str = None
    ) -> Dict[str, Any]:
        """Build optimized config for API acceleration"""
        from .origins import CloudFrontOrigins
        from .behaviors import CloudFrontBehaviors
        
        origins_manager = CloudFrontOrigins(self.aws_client)
        behaviors_manager = CloudFrontBehaviors(self.aws_client)
        
        # Create API origin
        origins = [origins_manager.create_custom_origin('default-origin', api_domain)]
        
        # Create API behavior
        default_behavior = behaviors_manager.create_api_behavior()
        
        config = {
            'name': name,
            'origins': origins_manager.build_origins_config(origins),
            'default_behavior': behaviors_manager.build_default_behavior(default_behavior),
            'custom_domains': custom_domains or [],
            'ssl_certificate_arn': ssl_certificate_arn,
            'price_class': 'PriceClass_All',  # Global for APIs
            'http2_enabled': True,
            'ipv6_enabled': True,
            'compression_enabled': True
        }
        
        return self.build_complete_config(config)

    def build_spa_config(
        self,
        name: str,
        origin_domain: str,
        custom_domains: List[str] = None,
        ssl_certificate_arn: str = None
    ) -> Dict[str, Any]:
        """Build optimized config for Single Page Applications"""
        from .origins import CloudFrontOrigins
        from .behaviors import CloudFrontBehaviors
        
        origins_manager = CloudFrontOrigins(self.aws_client)
        behaviors_manager = CloudFrontBehaviors(self.aws_client)
        
        # Create S3 origin
        origins = [origins_manager.create_s3_origin('default-origin', origin_domain)]
        
        # Create SPA behavior
        default_behavior = behaviors_manager.create_spa_behavior()
        
        config = {
            'name': name,
            'origins': origins_manager.build_origins_config(origins),
            'default_behavior': behaviors_manager.build_default_behavior(default_behavior),
            'custom_domains': custom_domains or [],
            'ssl_certificate_arn': ssl_certificate_arn,
            'price_class': 'PriceClass_100',
            'http2_enabled': True,
            'ipv6_enabled': True,
            'compression_enabled': True,
            'error_pages': [
                {'error_code': 404, 'response_page_path': '/index.html', 'response_code': 200},
                {'error_code': 403, 'response_page_path': '/index.html', 'response_code': 200}
            ]
        }
        
        return self.build_complete_config(config)

    def build_assets_config(
        self,
        name: str,
        origin_domain: str,
        path: str = 'assets',
        custom_domains: List[str] = None,
        ssl_certificate_arn: str = None
    ) -> Dict[str, Any]:
        """Build optimized config for static assets delivery"""
        from .origins import CloudFrontOrigins
        from .behaviors import CloudFrontBehaviors
        
        origins_manager = CloudFrontOrigins(self.aws_client)
        behaviors_manager = CloudFrontBehaviors(self.aws_client)
        
        # Create S3 origin with path
        origins = [origins_manager.create_s3_origin('default-origin', origin_domain, path)]
        
        # Create assets behavior
        default_behavior = behaviors_manager.create_assets_behavior()
        
        config = {
            'name': name,
            'origins': origins_manager.build_origins_config(origins),
            'default_behavior': behaviors_manager.build_default_behavior(default_behavior),
            'custom_domains': custom_domains or [],
            'ssl_certificate_arn': ssl_certificate_arn,
            'price_class': 'PriceClass_200',  # Good global coverage for assets
            'http2_enabled': True,
            'ipv6_enabled': True,
            'compression_enabled': True
        }
        
        return self.build_complete_config(config)

    def validate_config(self, config: Dict[str, Any]) -> List[str]:
        """Validate distribution configuration and return any errors"""
        errors = []
        
        # Required fields
        if not config.get('name'):
            errors.append("name is required")
        
        if not config.get('origins'):
            errors.append("at least one origin is required")
        
        if not config.get('default_behavior'):
            errors.append("default_behavior is required")
        
        # SSL validation
        custom_domains = config.get('custom_domains', [])
        ssl_certificate_arn = config.get('ssl_certificate_arn')
        
        if custom_domains and not ssl_certificate_arn:
            errors.append("ssl_certificate_arn is required when using custom domains")
        
        # Price class validation
        price_class = config.get('price_class', 'PriceClass_All')
        valid_price_classes = ['PriceClass_100', 'PriceClass_200', 'PriceClass_All']
        if price_class not in valid_price_classes:
            errors.append(f"price_class must be one of {valid_price_classes}")
        
        # Geo restriction validation
        geo_restriction = config.get('geo_restriction')
        if geo_restriction:
            restriction_type = geo_restriction.get('type')
            if restriction_type not in ['whitelist', 'blacklist']:
                errors.append("geo_restriction type must be 'whitelist' or 'blacklist'")
            
            countries = geo_restriction.get('countries', [])
            if not countries:
                errors.append("geo_restriction countries list cannot be empty")
        
        return errors

    def get_ssl_minimum_versions(self) -> List[str]:
        """Get available SSL minimum protocol versions"""
        return [
            'SSLv3',
            'TLSv1',
            'TLSv1_2016',
            'TLSv1.1_2016',
            'TLSv1.2_2018',
            'TLSv1.2_2019',
            'TLSv1.2_2021'
        ]

    def get_price_class_descriptions(self) -> Dict[str, str]:
        """Get price class descriptions"""
        return {
            'PriceClass_100': 'Use only the least expensive edge locations (US, Canada, Europe)',
            'PriceClass_200': 'Use most edge locations (excludes Asia Pacific)',
            'PriceClass_All': 'Use all edge locations worldwide'
        }

    def estimate_monthly_cost(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Estimate monthly costs based on configuration"""
        price_class = config.get('price_class', 'PriceClass_All')
        custom_domains = config.get('custom_domains', [])
        ssl_enabled = bool(config.get('ssl_certificate_arn'))
        logging_enabled = config.get('logging_enabled', False)
        
        cost_estimate = {
            'data_transfer': 'Variable based on usage',
            'http_requests': '$0.0075 per 10,000 requests',
            'https_requests': '$0.0100 per 10,000 requests',
            'ssl_certificate': 'Free (AWS Certificate Manager)' if ssl_enabled else 'N/A',
            'price_class_impact': 'Higher costs' if price_class == 'PriceClass_All' else 'Lower costs',
            'access_logs': 'S3 storage costs apply' if logging_enabled else 'Disabled'
        }
        
        return cost_estimate 