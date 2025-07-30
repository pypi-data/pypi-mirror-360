"""
Google Cloud CDN Configuration Mixin

Configuration methods for Google Cloud CDN.
Provides Rails-like method chaining for fluent CDN configuration.
"""

from typing import Dict, Any, List, Optional, Union


class CloudCdnConfigurationMixin:
    """
    Mixin for Google Cloud CDN configuration methods.
    
    This mixin provides:
    - Rails-like method chaining for fluent CDN configuration
    - Cache behavior configuration
    - Origin and backend configuration
    - Security and performance settings
    - Path-based routing configuration
    """
    
    # Project and CDN Configuration
    def project(self, project_id: str):
        """Set Google Cloud project ID"""
        self.project_id = project_id
        return self
        
    def enabled(self, enabled: bool = True):
        """Enable or disable CDN"""
        self.enabled = enabled
        return self
        
    def description(self, description: str):
        """Set CDN description"""
        self.cdn_description = description
        return self
    
    # Cache Configuration Methods
    def cache_mode(self, mode: str):
        """Set cache mode"""
        if not self._validate_cache_mode(mode):
            raise ValueError(f"Invalid cache mode: {mode}")
        self.cache_mode = mode
        return self
        
    def use_origin_headers(self):
        """Use origin headers for caching decisions"""
        return self.cache_mode("USE_ORIGIN_HEADERS")
        
    def force_cache_all(self):
        """Force cache all content regardless of headers"""
        return self.cache_mode("FORCE_CACHE_ALL")
        
    def cache_static_content(self):
        """Cache all static content (default)"""
        return self.cache_mode("CACHE_ALL_STATIC")
        
    def default_ttl(self, ttl_seconds: int):
        """Set default TTL for cached content"""
        if not self._validate_ttl(ttl_seconds):
            raise ValueError(f"Invalid TTL: {ttl_seconds}")
        self.default_ttl = ttl_seconds
        return self
        
    def max_ttl(self, ttl_seconds: int):
        """Set maximum TTL for cached content"""
        if not self._validate_ttl(ttl_seconds):
            raise ValueError(f"Invalid max TTL: {ttl_seconds}")
        self.max_ttl = ttl_seconds
        return self
        
    def client_ttl(self, ttl_seconds: int):
        """Set client TTL"""
        if not self._validate_ttl(ttl_seconds):
            raise ValueError(f"Invalid client TTL: {ttl_seconds}")
        self.client_ttl = ttl_seconds
        return self
        
    def serve_while_stale(self, ttl_seconds: int):
        """Set serve while stale TTL"""
        if not self._validate_ttl(ttl_seconds):
            raise ValueError(f"Invalid serve while stale TTL: {ttl_seconds}")
        self.serve_while_stale = ttl_seconds
        return self
    
    # Compression Configuration
    def compression(self, mode: str = "AUTOMATIC"):
        """Set compression mode"""
        if not self._validate_compression_mode(mode):
            raise ValueError(f"Invalid compression mode: {mode}")
        self.compression_mode = mode
        return self
        
    def auto_compression(self):
        """Enable automatic compression"""
        return self.compression("AUTOMATIC")
        
    def disable_compression(self):
        """Disable compression"""
        return self.compression("DISABLED")
    
    # Backend Configuration Methods
    def backend_service(self, service_name: str):
        """Set backend service"""
        self.backend_service = service_name
        return self
        
    def backend_bucket(self, bucket_name: str):
        """Set backend bucket for static content"""
        self.backend_bucket = bucket_name
        return self
        
    def url_map(self, url_map_name: str):
        """Set URL map for routing"""
        self.url_map = url_map_name
        return self
        
    def default_service(self, service_name: str):
        """Set default backend service"""
        self.default_service = service_name
        return self
    
    # Cache Key Policy Configuration
    def include_protocol(self, include: bool = True):
        """Include protocol in cache key"""
        self.cache_key_policy["include_protocol"] = include
        return self
        
    def include_host(self, include: bool = True):
        """Include host in cache key"""
        self.cache_key_policy["include_host"] = include
        return self
        
    def include_query_string(self, include: bool = True):
        """Include query string in cache key"""
        self.cache_key_policy["include_query_string"] = include
        return self
        
    def query_string_whitelist(self, parameters: List[str]):
        """Set query string parameters to include"""
        self.cache_key_policy["query_string_whitelist"] = parameters
        return self
        
    def query_string_blacklist(self, parameters: List[str]):
        """Set query string parameters to exclude"""
        self.cache_key_policy["query_string_blacklist"] = parameters
        return self
        
    def include_headers(self, headers: List[str]):
        """Include specific headers in cache key"""
        self.cache_key_policy["include_http_headers"] = headers
        return self
        
    def include_cookies(self, cookies: List[str]):
        """Include specific cookies in cache key"""
        self.cache_key_policy["include_named_cookies"] = cookies
        return self
    
    # Negative Caching Configuration
    def negative_caching(self, enabled: bool = True):
        """Enable negative caching"""
        self.negative_caching = enabled
        return self
        
    def negative_cache_policy(self, code: int, ttl: int):
        """Add negative caching policy for specific HTTP code"""
        policy = {"code": code, "ttl": ttl}
        self.negative_caching_policy.append(policy)
        return self
    
    # Security Configuration
    def signed_url_cache_max_age(self, max_age: int):
        """Set signed URL cache max age"""
        self.signed_url_cache_max_age = max_age
        return self
        
    def bypass_cache_headers(self, headers: List[str]):
        """Set headers that bypass cache"""
        self.bypass_cache_on_request_headers = headers
        return self
    
    # High-Level Configuration Patterns
    def static_website(self):
        """Configure for static website hosting"""
        self.cdn_labels["use_case"] = "static_website"
        return (self
                .cache_static_content()
                .auto_compression()
                .default_ttl(86400)  # 24 hours
                .max_ttl(604800)     # 7 days
                .negative_caching())
                
    def api_acceleration(self):
        """Configure for API acceleration"""
        self.cdn_labels["use_case"] = "api_acceleration"
        return (self
                .use_origin_headers()
                .auto_compression()
                .default_ttl(300)    # 5 minutes
                .max_ttl(3600)       # 1 hour
                .include_query_string(True))
                
    def media_streaming(self):
        """Configure for media streaming"""
        self.cdn_labels["use_case"] = "media_streaming"
        return (self
                .force_cache_all()
                .disable_compression()  # Media is already compressed
                .default_ttl(86400)     # 24 hours
                .max_ttl(2592000)       # 30 days
                .serve_while_stale(604800))  # 7 days
                
    def e_commerce(self):
        """Configure for e-commerce site"""
        self.cdn_labels["use_case"] = "e_commerce"
        return (self
                .cache_static_content()
                .auto_compression()
                .default_ttl(3600)      # 1 hour
                .max_ttl(86400)         # 24 hours
                .include_cookies(["session_id"])
                .negative_caching())
                
    def development_cdn(self):
        """Configure for development environment"""
        self.cdn_labels["environment"] = "development"
        return (self
                .use_origin_headers()
                .auto_compression()
                .default_ttl(60)        # 1 minute
                .max_ttl(300)           # 5 minutes
                .negative_caching(False))
                
    def production_cdn(self):
        """Configure for production environment"""
        self.cdn_labels["environment"] = "production"
        return (self
                .cache_static_content()
                .auto_compression()
                .default_ttl(3600)      # 1 hour
                .max_ttl(86400)         # 24 hours
                .serve_while_stale(604800)  # 7 days
                .negative_caching())
                
    def high_performance_cdn(self):
        """Configure for high performance"""
        self.cdn_labels["optimization"] = "high_performance"
        return (self
                .force_cache_all()
                .auto_compression()
                .default_ttl(86400)     # 24 hours
                .max_ttl(2592000)       # 30 days
                .serve_while_stale(86400))
                
    def cost_optimized_cdn(self):
        """Configure for cost optimization"""
        self.cdn_labels["optimization"] = "cost_optimized"
        return (self
                .use_origin_headers()
                .auto_compression()
                .default_ttl(86400)     # 24 hours - longer cache
                .max_ttl(604800)        # 7 days
                .negative_caching())
    
    # Path-based Configuration
    def add_path_matcher(self, path_pattern: str, service: str, **options):
        """Add path matcher for routing"""
        matcher = {
            "name": f"matcher-{len(self.path_matchers)}",
            "path_rules": [{
                "paths": [path_pattern],
                "service": service
            }]
        }
        matcher.update(options)
        self.path_matchers.append(matcher)
        return self
        
    def route_path(self, path: str, service: str):
        """Route specific path to service"""
        return self.add_path_matcher(path, service)
        
    def route_api(self, api_service: str):
        """Route /api/* to API service"""
        return self.route_path("/api/*", api_service)
        
    def route_static(self, static_bucket: str):
        """Route /static/* to storage bucket"""
        return self.route_path("/static/*", static_bucket)
        
    def route_images(self, image_service: str):
        """Route /images/* to image service"""
        return self.route_path("/images/*", image_service)
    
    # Label and Metadata Configuration
    def label(self, key: str, value: str):
        """Add label to CDN"""
        self.cdn_labels[key] = value
        return self
        
    def labels(self, labels: Dict[str, str]):
        """Add multiple labels"""
        self.cdn_labels.update(labels)
        return self
        
    def team(self, team_name: str):
        """Set team label"""
        return self.label("team", team_name)
        
    def cost_center(self, cost_center: str):
        """Set cost center label"""
        return self.label("cost-center", cost_center)
        
    def application(self, app_name: str):
        """Set application label"""
        return self.label("application", app_name)
        
    def version(self, version: str):
        """Set version label"""
        return self.label("version", version)
    
    # Helper Methods
    def get_cache_configuration(self) -> Dict[str, Any]:
        """Get cache configuration"""
        return {
            "cache_mode": self.cache_mode,
            "default_ttl": self.default_ttl,
            "max_ttl": self.max_ttl,
            "client_ttl": self.client_ttl,
            "serve_while_stale": self.serve_while_stale,
            "negative_caching": self.negative_caching,
            "compression_mode": self.compression_mode
        }
        
    def get_backend_configuration(self) -> Dict[str, Any]:
        """Get backend configuration"""
        return {
            "backend_service": self.backend_service,
            "backend_bucket": self.backend_bucket,
            "url_map": self.url_map,
            "default_service": self.default_service,
            "path_matchers": self.path_matchers
        }
        
    def is_production_ready(self) -> bool:
        """Check if CDN is production ready"""
        return (
            self.enabled and
            (self.backend_service or self.backend_bucket) and
            self.max_ttl > 0 and
            self.negative_caching
        )