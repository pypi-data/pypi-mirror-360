"""
AWS CloudFront Behaviors

Handles CloudFront cache behaviors including default behavior, path-based behaviors,
and caching policies.
"""

from typing import Dict, Any, List


class CloudFrontBehaviors:
    """Manages CloudFront cache behaviors"""

    def __init__(self, aws_client):
        self.aws_client = aws_client

    def build_default_behavior(self, behavior_config: Dict[str, Any]) -> Dict[str, Any]:
        """Build default cache behavior"""
        allowed_methods = behavior_config.get('allowed_methods', ['GET', 'HEAD'])
        cached_methods = behavior_config.get('cached_methods', ['GET', 'HEAD'])
        
        behavior = {
            'TargetOriginId': behavior_config.get('target_origin_id', 'default-origin'),
            'ViewerProtocolPolicy': behavior_config.get('viewer_protocol_policy', 'redirect-to-https'),
            'TrustedSigners': {'Enabled': False, 'Quantity': 0},
            'ForwardedValues': {
                'QueryString': behavior_config.get('query_string', False),
                'Cookies': {'Forward': behavior_config.get('cookies', 'none')},
                'Headers': {'Quantity': 0}
            },
            'MinTTL': behavior_config.get('ttl_min', 0),
            'DefaultTTL': behavior_config.get('ttl_default', 86400),
            'MaxTTL': behavior_config.get('ttl_max', 31536000),
            'Compress': behavior_config.get('compress', True),
            'AllowedMethods': {
                'Quantity': len(allowed_methods),
                'Items': allowed_methods,
                'CachedMethods': {
                    'Quantity': len(cached_methods),
                    'Items': cached_methods
                }
            }
        }
        
        # Add cache policy if specified
        if behavior_config.get('cache_policy_id'):
            behavior['CachePolicyId'] = behavior_config['cache_policy_id']
            # Remove legacy ForwardedValues when using cache policies
            del behavior['ForwardedValues']
            del behavior['MinTTL']
            del behavior['DefaultTTL']
            del behavior['MaxTTL']
        
        # Add origin request policy if specified
        if behavior_config.get('origin_request_policy_id'):
            behavior['OriginRequestPolicyId'] = behavior_config['origin_request_policy_id']
        
        return behavior

    def build_behaviors_list(self, behaviors_config: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Build cache behaviors list"""
        cache_behaviors = []
        
        for behavior in behaviors_config:
            cache_behaviors.append(self._build_single_behavior(behavior))
            
        return cache_behaviors

    def _build_single_behavior(self, behavior: Dict[str, Any]) -> Dict[str, Any]:
        """Build single cache behavior"""
        allowed_methods = behavior.get('allowed_methods', ['GET', 'HEAD'])
        cached_methods = behavior.get('cached_methods', ['GET', 'HEAD'])
        
        cache_behavior = {
            'PathPattern': behavior['path_pattern'],
            'TargetOriginId': behavior.get('target_origin_id', 'default-origin'),
            'ViewerProtocolPolicy': behavior.get('viewer_protocol_policy', 'redirect-to-https'),
            'TrustedSigners': {'Enabled': False, 'Quantity': 0},
            'ForwardedValues': {
                'QueryString': behavior.get('query_string', False),
                'Cookies': {'Forward': behavior.get('cookies', 'none')},
                'Headers': {'Quantity': 0}
            },
            'MinTTL': behavior.get('ttl_min', 0),
            'DefaultTTL': behavior.get('ttl_default', 86400),
            'MaxTTL': behavior.get('ttl_max', 31536000),
            'Compress': behavior.get('compress', True),
            'AllowedMethods': {
                'Quantity': len(allowed_methods),
                'Items': allowed_methods,
                'CachedMethods': {
                    'Quantity': len(cached_methods),
                    'Items': cached_methods
                }
            }
        }
        
        # Add cache policy if specified
        if behavior.get('cache_policy_id'):
            cache_behavior['CachePolicyId'] = behavior['cache_policy_id']
            # Remove legacy ForwardedValues when using cache policies
            del cache_behavior['ForwardedValues']
            del cache_behavior['MinTTL']
            del cache_behavior['DefaultTTL']
            del cache_behavior['MaxTTL']
        
        # Add origin request policy if specified
        if behavior.get('origin_request_policy_id'):
            cache_behavior['OriginRequestPolicyId'] = behavior['origin_request_policy_id']
        
        return cache_behavior

    def create_static_site_behavior(self, target_origin_id: str = 'default-origin') -> Dict[str, Any]:
        """Create behavior optimized for static sites"""
        return {
            'target_origin_id': target_origin_id,
            'viewer_protocol_policy': 'redirect-to-https',
            'allowed_methods': ['GET', 'HEAD'],
            'cached_methods': ['GET', 'HEAD'],
            'compress': True,
            'ttl_min': 0,
            'ttl_default': 3600,  # 1 hour for HTML/CSS/JS
            'ttl_max': 86400,     # 1 day max
            'query_string': False,
            'cookies': 'none'
        }

    def create_api_behavior(self, target_origin_id: str = 'default-origin') -> Dict[str, Any]:
        """Create behavior optimized for API acceleration"""
        return {
            'target_origin_id': target_origin_id,
            'viewer_protocol_policy': 'redirect-to-https',
            'allowed_methods': ['GET', 'HEAD', 'OPTIONS', 'PUT', 'POST', 'PATCH', 'DELETE'],
            'cached_methods': ['GET', 'HEAD', 'OPTIONS'],
            'compress': True,
            'ttl_min': 0,
            'ttl_default': 0,     # No caching by default for APIs
            'ttl_max': 3600,      # Max 1 hour
            'query_string': True,
            'cookies': 'all'
        }

    def create_assets_behavior(self, target_origin_id: str = 'default-origin') -> Dict[str, Any]:
        """Create behavior optimized for static assets (CSS, JS, images)"""
        return {
            'target_origin_id': target_origin_id,
            'viewer_protocol_policy': 'redirect-to-https',
            'allowed_methods': ['GET', 'HEAD'],
            'cached_methods': ['GET', 'HEAD'],
            'compress': True,
            'ttl_min': 86400,     # 1 day minimum
            'ttl_default': 86400, # 1 day default
            'ttl_max': 31536000,  # 1 year max for versioned assets
            'query_string': False,
            'cookies': 'none'
        }

    def create_spa_behavior(self, target_origin_id: str = 'default-origin') -> Dict[str, Any]:
        """Create behavior optimized for Single Page Applications"""
        return {
            'target_origin_id': target_origin_id,
            'viewer_protocol_policy': 'redirect-to-https',
            'allowed_methods': ['GET', 'HEAD'],
            'cached_methods': ['GET', 'HEAD'],
            'compress': True,
            'ttl_min': 0,
            'ttl_default': 300,   # 5 minutes for HTML
            'ttl_max': 3600,      # 1 hour max
            'query_string': False,
            'cookies': 'none'
        }

    def create_path_behavior(
        self, 
        path_pattern: str, 
        cache_policy: str = 'default',
        target_origin_id: str = 'default-origin'
    ) -> Dict[str, Any]:
        """Create path-based behavior with predefined cache policies"""
        
        # Predefined cache policies
        cache_policies = {
            'no-cache': {
                'ttl_min': 0,
                'ttl_default': 0,
                'ttl_max': 0,
                'query_string': True,
                'cookies': 'all'
            },
            'short': {
                'ttl_min': 0,
                'ttl_default': 300,   # 5 minutes
                'ttl_max': 3600,      # 1 hour
                'query_string': False,
                'cookies': 'none'
            },
            'medium': {
                'ttl_min': 0,
                'ttl_default': 3600,  # 1 hour
                'ttl_max': 86400,     # 1 day
                'query_string': False,
                'cookies': 'none'
            },
            'long': {
                'ttl_min': 86400,     # 1 day
                'ttl_default': 86400, # 1 day
                'ttl_max': 31536000,  # 1 year
                'query_string': False,
                'cookies': 'none'
            },
            'default': {
                'ttl_min': 0,
                'ttl_default': 86400, # 1 day
                'ttl_max': 31536000,  # 1 year
                'query_string': False,
                'cookies': 'none'
            }
        }
        
        policy = cache_policies.get(cache_policy, cache_policies['default'])
        
        return {
            'path_pattern': path_pattern,
            'target_origin_id': target_origin_id,
            'viewer_protocol_policy': 'redirect-to-https',
            'allowed_methods': ['GET', 'HEAD'],
            'cached_methods': ['GET', 'HEAD'],
            'compress': True,
            **policy
        }

    def get_managed_cache_policy_ids(self) -> Dict[str, str]:
        """Get AWS managed cache policy IDs"""
        return {
            'caching_optimized': '658327ea-f89d-4fab-a63d-7e88639e58f6',
            'caching_disabled': '4135ea2d-6df8-44a3-9df3-4b5a84be39ad',
            'caching_optimized_for_uncompressed_objects': 'b2884449-e4de-46a7-ac36-70bc7f1ddd6d',
            'elemental_media_package': '08627262-05a9-4f76-9ded-b50ca2e3a84f'
        }

    def get_managed_origin_request_policy_ids(self) -> Dict[str, str]:
        """Get AWS managed origin request policy IDs"""
        return {
            'cors_s3_origin': '88a5eaf4-2fd4-4709-b370-b4c650ea3fcf',
            'cors_custom_origin': 'acba4595-bd28-49b8-b9fe-13317c0390fa',
            'user_agent_referer_headers': 'acba4595-bd28-49b8-b9fe-13317c0390fa',
            'all_viewer': '216adef6-5c7f-47e4-b989-5492eafa07d3'
        }

    def validate_behavior_config(self, behavior: Dict[str, Any]) -> List[str]:
        """Validate behavior configuration and return any errors"""
        errors = []
        
        # Required fields
        if not behavior.get('target_origin_id'):
            errors.append("target_origin_id is required")
        
        # Path pattern validation for non-default behaviors
        if 'path_pattern' in behavior:
            pattern = behavior['path_pattern']
            if not pattern or pattern == '/':
                errors.append("path_pattern must be a valid path pattern (not empty or '/')")
        
        # TTL validation
        ttl_min = behavior.get('ttl_min', 0)
        ttl_default = behavior.get('ttl_default', 86400)
        ttl_max = behavior.get('ttl_max', 31536000)
        
        if ttl_min > ttl_default:
            errors.append("ttl_min cannot be greater than ttl_default")
        if ttl_default > ttl_max:
            errors.append("ttl_default cannot be greater than ttl_max")
        
        # Method validation
        allowed_methods = behavior.get('allowed_methods', ['GET', 'HEAD'])
        cached_methods = behavior.get('cached_methods', ['GET', 'HEAD'])
        
        for method in cached_methods:
            if method not in allowed_methods:
                errors.append(f"cached method '{method}' must be in allowed_methods")
        
        return errors 