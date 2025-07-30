"""
Google Cloud CDN Complete Implementation

Complete Google Cloud CDN implementation combining core functionality,
configuration methods, and lifecycle operations into a single modular class.
Rails-like API with Cross-Cloud Magic optimization.
"""

from typing import Dict, Any, List, Optional, Union
from .cloud_cdn_core import CloudCdnCore
from .cloud_cdn_configuration import CloudCdnConfigurationMixin
from .cloud_cdn_lifecycle import CloudCdnLifecycleMixin


class CloudCdn(CloudCdnCore, CloudCdnConfigurationMixin, CloudCdnLifecycleMixin):
    """
    Complete Google Cloud CDN implementation.
    
    This class combines:
    - CloudCdnCore: Basic CDN attributes and authentication
    - CloudCdnConfigurationMixin: Chainable configuration methods
    - CloudCdnLifecycleMixin: Lifecycle operations (create, destroy, preview)
    
    Features:
    - Rails-like method chaining for fluent CDN configuration
    - Smart cache management and cost optimization
    - Cross-Cloud Magic optimization
    - Global content delivery network with 130+ edge locations
    - Ultra-low latency content acceleration
    - DDoS protection and security features
    - Real-time cache analytics and monitoring
    - HTTP/2 and QUIC protocol support
    - Automatic content compression
    - Cache invalidation and purging
    - Signed URLs and security policies
    
    Example:
        # Static website CDN
        static_cdn = CloudCdn("website-cdn")
        static_cdn.project("my-project").static_website()
        static_cdn.backend_bucket("my-static-bucket")
        static_cdn.create()
        
        # API acceleration CDN
        api_cdn = CloudCdn("api-cdn")
        api_cdn.project("my-project").api_acceleration()
        api_cdn.backend_service("api-backend-service")
        api_cdn.create()
        
        # E-commerce CDN with path routing
        ecommerce_cdn = CloudCdn("ecommerce-cdn")
        ecommerce_cdn.project("my-project").e_commerce()
        ecommerce_cdn.backend_service("web-backend")
        ecommerce_cdn.route_api("api-backend")
        ecommerce_cdn.route_static("static-bucket")
        ecommerce_cdn.route_images("image-service")
        ecommerce_cdn.create()
        
        # Media streaming CDN
        media_cdn = CloudCdn("media-cdn")
        media_cdn.project("my-project").media_streaming()
        media_cdn.backend_bucket("media-bucket")
        media_cdn.default_ttl(86400).max_ttl(2592000)
        media_cdn.create()
        
        # High-performance CDN
        perf_cdn = CloudCdn("performance-cdn")
        perf_cdn.project("my-project").high_performance_cdn()
        perf_cdn.backend_service("app-backend")
        perf_cdn.create()
        
        # Development CDN
        dev_cdn = CloudCdn("dev-cdn")
        dev_cdn.project("my-project").development_cdn()
        dev_cdn.backend_service("dev-backend")
        dev_cdn.create()
        
        # Cost-optimized CDN
        cost_cdn = CloudCdn("cost-optimized-cdn")
        cost_cdn.project("my-project").cost_optimized_cdn()
        cost_cdn.backend_bucket("content-bucket")
        cost_cdn.create()
        
        # Cross-Cloud Magic optimization
        optimized_cdn = CloudCdn("optimized-cdn")
        optimized_cdn.project("my-project").backend_service("my-service")
        optimized_cdn.optimize_for("performance")
        optimized_cdn.create()
    """
    
    def __init__(self, name: str):
        """
        Initialize Google Cloud CDN with configuration name.
        
        Args:
            name: CDN configuration name
        """
        # Initialize all parent classes
        CloudCdnCore.__init__(self, name)
        
        # Ensure proper initialization order
        self._initialize_managers()
        
    def __repr__(self) -> str:
        """String representation of Cloud CDN configuration"""
        cdn_type = self._get_cdn_type_from_config()
        backend_info = []
        if self.backend_service:
            backend_info.append(f"service:{self.backend_service}")
        if self.backend_bucket:
            backend_info.append(f"bucket:{self.backend_bucket}")
        backend_str = ",".join(backend_info) if backend_info else "none"
        status = "enabled" if self.enabled else "disabled"
        
        return (f"CloudCdn(name='{self.cdn_name}', "
                f"type='{cdn_type}', "
                f"cache_mode='{self.cache_mode}', "
                f"backends='{backend_str}', "
                f"ttl='{self.default_ttl}s', "
                f"project='{self.project_id}', "
                f"status='{status}')")
    
    def summary(self) -> Dict[str, Any]:
        """
        Get comprehensive summary of Cloud CDN configuration.
        
        Returns:
            Dict containing all configuration details
        """
        # Analyze CDN configuration
        cdn_features = []
        if self.enabled:
            cdn_features.append("enabled")
        if self.negative_caching:
            cdn_features.append("negative_caching")
        if self.compression_mode == "AUTOMATIC":
            cdn_features.append("compression")
        if self.path_matchers:
            cdn_features.append("path_routing")
        if self.cache_key_policy.get("include_query_string"):
            cdn_features.append("query_string_caching")
            
        # Analyze backends
        backend_info = {
            "backend_service": self.backend_service,
            "backend_bucket": self.backend_bucket,
            "url_map": self.url_map,
            "default_service": self.default_service,
            "path_matchers": len(self.path_matchers)
        }
        
        # Analyze cache configuration
        cache_info = self.get_cache_configuration()
        cache_info.update({
            "cache_key_policy": self.cache_key_policy,
            "negative_caching_policies": len(self.negative_caching_policy)
        })
        
        summary = {
            "cdn_name": self.cdn_name,
            "project_id": self.project_id,
            "cdn_description": self.cdn_description,
            "cdn_type": self._get_cdn_type_from_config(),
            
            # CDN configuration
            "enabled": self.enabled,
            "cache_configuration": cache_info,
            
            # Backend configuration
            "backends": backend_info,
            
            # Security configuration
            "security": {
                "signed_url_cache_max_age": self.signed_url_cache_max_age,
                "bypass_cache_headers": self.bypass_cache_on_request_headers
            },
            
            # Features analysis
            "cdn_features": cdn_features,
            "is_production_ready": self.is_production_ready(),
            
            # Labels and metadata
            "labels": self.cdn_labels,
            "label_count": len(self.cdn_labels),
            "annotations": self.cdn_annotations,
            
            # State
            "state": {
                "exists": self.cdn_exists,
                "created": self.cdn_created,
                "cdn_state": self.cdn_state,
                "deployment_status": self.deployment_status
            },
            
            # Cost
            "estimated_monthly_cost": f"${self._estimate_cdn_cost():,.2f}",
            "cost_per_gb": "$0.04-$0.15 (tiered)"
        }
        
        return summary
    
    def display_config(self):
        """Display current configuration in human-readable format"""
        print(f"\\n🌐 Google Cloud CDN Configuration: {self.cdn_name}")
        print(f"   📁 Project: {self.project_id}")
        print(f"   📝 Description: {self.cdn_description}")
        print(f"   🎯 CDN Type: {self._get_cdn_type_from_config().replace('_', ' ').title()}")
        print(f"   🔄 Status: {'✅ Enabled' if self.enabled else '❌ Disabled'}")
        
        # Cache configuration
        print(f"\\n💾 Cache Configuration:")
        print(f"   💾 Cache Mode: {self.cache_mode}")
        print(f"   ⏰ Default TTL: {self.default_ttl}s ({self.default_ttl//3600}h {(self.default_ttl%3600)//60}m)")
        print(f"   ⏰ Max TTL: {self.max_ttl}s ({self.max_ttl//3600}h {(self.max_ttl%3600)//60}m)")
        print(f"   ⏰ Client TTL: {self.client_ttl}s")
        print(f"   🔄 Serve While Stale: {self.serve_while_stale}s")
        print(f"   🗜️ Compression: {self.compression_mode}")
        print(f"   🚫 Negative Caching: {'✅ Enabled' if self.negative_caching else '❌ Disabled'}")
        
        # Backend configuration
        print(f"\\n🔙 Backend Configuration:")
        if self.backend_service:
            print(f"   🖥️ Backend Service: {self.backend_service}")
        if self.backend_bucket:
            print(f"   🪣 Backend Bucket: {self.backend_bucket}")
        if self.url_map:
            print(f"   🗺️ URL Map: {self.url_map}")
        if self.default_service:
            print(f"   🔵 Default Service: {self.default_service}")
        if not (self.backend_service or self.backend_bucket):
            print(f"   ⚠️ No backends configured")
            
        # Path matchers
        if self.path_matchers:
            print(f"\\n🛣️ Path Routing ({len(self.path_matchers)} matchers):")
            for matcher in self.path_matchers[:3]:
                print(f"   • {matcher['name']}")
                for rule in matcher.get('path_rules', [])[:2]:
                    for path in rule.get('paths', [])[:2]:
                        print(f"     └─ {path} → {rule.get('service', 'unknown')}")
            if len(self.path_matchers) > 3:
                print(f"   • ... and {len(self.path_matchers) - 3} more")
                
        # Cache key policy
        print(f"\\n🔑 Cache Key Policy:")
        policy = self.cache_key_policy
        print(f"   🔗 Include Protocol: {'✅ Yes' if policy.get('include_protocol') else '❌ No'}")
        print(f"   🏠 Include Host: {'✅ Yes' if policy.get('include_host') else '❌ No'}")
        print(f"   ❓ Include Query String: {'✅ Yes' if policy.get('include_query_string') else '❌ No'}")
        if policy.get('include_http_headers'):
            print(f"   📄 Headers: {', '.join(policy['include_http_headers'][:3])}")
        if policy.get('include_named_cookies'):
            print(f"   🍪 Cookies: {', '.join(policy['include_named_cookies'][:3])}")
            
        # Security configuration
        print(f"\\n🔒 Security Configuration:")
        print(f"   ✍️ Signed URL Max Age: {self.signed_url_cache_max_age}s")
        if self.bypass_cache_on_request_headers:
            print(f"   🚫 Bypass Cache Headers: {', '.join(self.bypass_cache_on_request_headers[:3])}")
            
        # Labels
        if self.cdn_labels:
            print(f"\\n🏷️ Labels ({len(self.cdn_labels)}):")
            for key, value in list(self.cdn_labels.items())[:5]:
                print(f"   • {key}: {value}")
            if len(self.cdn_labels) > 5:
                print(f"   • ... and {len(self.cdn_labels) - 5} more")
                
        # Production readiness
        production_ready = self.is_production_ready()
        print(f"\\n🚀 Production Readiness: {'✅ Ready' if production_ready else '⚠️ Needs configuration'}")
        if not production_ready:
            issues = []
            if not self.enabled:
                issues.append("CDN disabled")
            if not (self.backend_service or self.backend_bucket):
                issues.append("No backends configured")
            if self.max_ttl <= 0:
                issues.append("Invalid max TTL")
            if not self.negative_caching:
                issues.append("Negative caching disabled")
                
            for issue in issues[:3]:
                print(f"   ⚠️ {issue}")
                
        # Cost estimate
        cost = self._estimate_cdn_cost()
        print(f"\\n💰 Cost Estimate:")
        print(f"   💰 Monthly: ${cost:,.2f}")
        print(f"   🌐 Cache egress: $0.04-$0.15/GB (tiered)")
        print(f"   📥 Cache fill: $0.085/GB")
        
        # Console and URLs
        if self.project_id:
            print(f"\\n🌐 Console:")
            print(f"   🔗 https://console.cloud.google.com/net-services/cdn/list?project={self.project_id}")
            
        # CDN capabilities
        print(f"\\n🌐 Cloud CDN Capabilities:")
        print(f"   ├─ 🌍 130+ global edge locations")
        print(f"   ├─ 🚀 Ultra-low latency delivery")
        print(f"   ├─ 🛡️ DDoS protection and security")
        print(f"   ├─ 📊 Real-time cache analytics")
        print(f"   ├─ 🗜️ Automatic content compression")
        print(f"   └─ 🔄 HTTP/2 and QUIC support")
    
    def get_status(self) -> Dict[str, Any]:
        """Get CDN status for backwards compatibility"""
        return {
            "cdn_name": self.cdn_name,
            "project_id": self.project_id,
            "enabled": self.enabled,
            "cache_mode": self.cache_mode,
            "default_ttl": self.default_ttl,
            "max_ttl": self.max_ttl,
            "compression_mode": self.compression_mode,
            "backend_service": self.backend_service,
            "backend_bucket": self.backend_bucket,
            "path_matchers": len(self.path_matchers),
            "negative_caching": self.negative_caching,
            "is_production_ready": self.is_production_ready(),
            "deployment_status": self.deployment_status,
            "estimated_cost": f"${self._estimate_cdn_cost():,.2f}/month"
        }


# Convenience function for creating Cloud CDN
def create_cloud_cdn(name: str) -> CloudCdn:
    """
    Create a new Cloud CDN configuration.
    
    Args:
        name: CDN configuration name
        
    Returns:
        CloudCdn instance
    """
    return CloudCdn(name)


# Pattern-specific convenience functions
def create_static_website_cdn(name: str, project_id: str, bucket_name: str) -> CloudCdn:
    """Create a CDN for static website hosting"""
    cdn = CloudCdn(name)
    cdn.project(project_id).static_website()
    cdn.backend_bucket(bucket_name)
    return cdn


def create_api_cdn(name: str, project_id: str, backend_service: str) -> CloudCdn:
    """Create a CDN for API acceleration"""
    cdn = CloudCdn(name)
    cdn.project(project_id).api_acceleration()
    cdn.backend_service(backend_service)
    return cdn


def create_media_cdn(name: str, project_id: str, media_bucket: str) -> CloudCdn:
    """Create a CDN for media streaming"""
    cdn = CloudCdn(name)
    cdn.project(project_id).media_streaming()
    cdn.backend_bucket(media_bucket)
    return cdn


def create_ecommerce_cdn(name: str, project_id: str, web_backend: str) -> CloudCdn:
    """Create a CDN for e-commerce applications"""
    cdn = CloudCdn(name)
    cdn.project(project_id).e_commerce()
    cdn.backend_service(web_backend)
    return cdn


def create_development_cdn(name: str, project_id: str, backend_service: str) -> CloudCdn:
    """Create a CDN for development environment"""
    cdn = CloudCdn(name)
    cdn.project(project_id).development_cdn()
    cdn.backend_service(backend_service)
    return cdn


# Export the class for easy importing
__all__ = [
    'CloudCdn',
    'create_cloud_cdn',
    'create_static_website_cdn',
    'create_api_cdn',
    'create_media_cdn',
    'create_ecommerce_cdn',
    'create_development_cdn'
]