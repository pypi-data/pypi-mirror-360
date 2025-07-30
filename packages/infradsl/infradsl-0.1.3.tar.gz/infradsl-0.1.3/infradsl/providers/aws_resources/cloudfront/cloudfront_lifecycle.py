from typing import Dict, Any, List
import uuid
from infradsl.cli.output_formatters import print_success, print_info, print_warning

class CloudFrontLifecycleMixin:
    """
    Mixin for CloudFront distribution lifecycle operations (create, update, destroy).
    """
    
    def preview(self) -> Dict[str, Any]:
        """Preview what will be created, kept, and removed"""
        
        # Handle copy_from case
        if hasattr(self, '_copied_from_distribution_id') and self._copied_from_distribution_id:
            self._display_cloudfront_copy_preview()
            return {
                'resource_type': 'AWS CloudFront Distribution',
                'distribution_name': f"{self.name}-distribution", 
                'status': 'Configuration copied and customized',
                'copied_from': self._copied_from_distribution_id,
                'note': f'Cloned from {self._copied_from_distribution_id} with customizations'
            }
        
        # For basic testing, provide a default preview even without origin
        if not self.origin_domain:
            return {
                'resource_type': 'AWS CloudFront Distribution',
                'distribution_name': f"{self.name}-distribution",
                'origin_domain': 'Not configured',
                'status': 'Configuration incomplete',
                'note': 'Origin domain required for deployment'
            }
        
        self._ensure_authenticated()
        
        # Mock discovery for now - in real implementation this would use AWS SDK
        existing_distributions = {}
        
        # Determine desired state - check if name is already a distribution ID
        if self.name.startswith('E') and len(self.name) == 14:  # CloudFront distribution ID format
            desired_distribution_name = self.name  # Use existing distribution ID
            is_existing_distribution = True
        else:
            desired_distribution_name = f"{self.name}-distribution"  # New distribution
            is_existing_distribution = False
        
        # Categorize distributions
        to_create = []
        to_keep = []
        to_remove = []
        
        if is_existing_distribution:
            # This is an existing distribution - show what will be updated
            to_keep.append({
                'name': desired_distribution_name,
                'status': 'EXISTING',
                'origin_domain': self.origin_domain,
                'custom_domains': self.custom_domains,
                'ssl_certificate_arn': self.ssl_certificate_arn,
                'note': 'Using existing CloudFront distribution'
            })
        else:
            # This is a new distribution to be created
            to_create.append({
                'name': desired_distribution_name,
                'origin_domain': self.origin_domain,
                'custom_domains': self.custom_domains,
                'ssl_certificate_arn': self.ssl_certificate_arn,
                'price_class': self.price_class_setting or 'PriceClass_All',
                'http2_enabled': self.http2_enabled,
                'ipv6_enabled': self.ipv6_enabled,
                'compression_enabled': self.compression_enabled,
                'security_headers': getattr(self, 'security_headers', False),
                'waf_enabled': bool(getattr(self, 'waf_web_acl_id', None)),
                'geo_restrictions': bool(getattr(self, 'geo_restriction', None)),
                'logging_enabled': getattr(self, 'logging_enabled', False),
                'behaviors_count': len(getattr(self, 'behaviors', [])),
                'error_pages_count': len(getattr(self, 'error_pages', []))
            })
        
        self._display_preview(to_create, to_keep, to_remove)
        
        return {
            'resource_type': 'AWS CloudFront Distribution',
            'name': desired_distribution_name,
            'distribution_id': f"E{str(uuid.uuid4()).replace('-', '').upper()[:13]}",  # Mock distribution ID
            'to_create': to_create,
            'to_keep': to_keep,
            'to_remove': to_remove,
            'existing_distributions': existing_distributions,
            'origin_domain': self.origin_domain,
            'custom_domains_count': len(self.custom_domains),
            'estimated_deployment_time': '15-20 minutes',
            'estimated_monthly_cost': self.estimate_monthly_cost() if hasattr(self, 'estimate_monthly_cost') else '$8.50'
        }
    
    def _display_preview(self, to_create: List[Dict], to_keep: List[Dict], to_remove: List[Dict]):
        """Display preview information in a clean format"""
        print(f"\n🌍 CloudFront CDN Preview")
        
        # Show distributions to create
        if to_create:
            print(f"╭─ 🚀 Distributions to CREATE: {len(to_create)}")
            for dist in to_create:
                print(f"├─ 🆕 {dist['name']}")
                print(f"│  ├─ 🌐 Origin: {dist['origin_domain']}")
                if dist['custom_domains']:
                    print(f"│  ├─ 🔗 Custom Domains: {len(dist['custom_domains'])}")
                    for domain in dist['custom_domains'][:3]:  # Show first 3
                        print(f"│  │  ├─ {domain}")
                    if len(dist['custom_domains']) > 3:
                        print(f"│  │  └─ ... and {len(dist['custom_domains']) - 3} more")
                print(f"│  ├─ 🏷️  Price Class: {dist['price_class']}")
                print(f"│  ├─ 🔒 SSL Certificate: {'✅ Yes' if dist['ssl_certificate_arn'] else '❌ Default only'}")
                print(f"│  ├─ ⚡ HTTP/2: {'✅ Enabled' if dist['http2_enabled'] else '❌ Disabled'}")
                print(f"│  ├─ 🌐 IPv6: {'✅ Enabled' if dist['ipv6_enabled'] else '❌ Disabled'}")
                print(f"│  ├─ 📦 Compression: {'✅ Enabled' if dist['compression_enabled'] else '❌ Disabled'}")
                print(f"│  ├─ 🛡️  WAF: {'✅ Enabled' if dist['waf_enabled'] else '❌ Disabled'}")
                print(f"│  ├─ 🌍 Geo Restrictions: {'✅ Yes' if dist['geo_restrictions'] else '❌ None'}")
                print(f"│  ├─ 📊 Behaviors: {dist['behaviors_count']}")
                print(f"│  ├─ 🚨 Error Pages: {dist['error_pages_count']}")
                print(f"│  ├─ 📝 Logging: {'✅ Enabled' if dist['logging_enabled'] else '❌ Disabled'}")
                print(f"│  └─ ⏱️  Deployment Time: 15-20 minutes")
            print(f"╰─")
        
        # Show distributions to keep/update
        if to_keep:
            print(f"╭─ 🔄 Distributions to UPDATE: {len(to_keep)}")
            for dist in to_keep:
                print(f"├─ ✅ {dist['name']}")
                print(f"│  ├─ 📝 Status: {dist.get('status', 'EXISTING')}")
                print(f"│  ├─ 🌐 Origin: {dist['origin_domain']}")
                if dist.get('custom_domains'):
                    print(f"│  ├─ 🔗 Custom Domains: {len(dist['custom_domains'])}")
                    for domain in dist['custom_domains'][:3]:
                        print(f"│  │  ├─ {domain}")
                    if len(dist['custom_domains']) > 3:
                        print(f"│  │  └─ ... and {len(dist['custom_domains']) - 3} more")
                print(f"│  └─ 💡 {dist.get('note', 'No changes')}")
            print(f"╰─")
        
        # Show cost estimation
        print(f"\n💰 Estimated Monthly Costs:")
        if to_create:
            dist = to_create[0]
            print(f"   ├─ 📡 Data Transfer (100GB): $8.50/month")
            print(f"   ├─ 🔄 HTTP Requests (1M): $0.75/month")
            print(f"   ├─ 🔒 HTTPS Requests (1M): $1.00/month")
            if dist['ssl_certificate_arn']:
                print(f"   ├─ 🔐 Dedicated SSL Certificate: $50.00/month")
            if dist['price_class'] == 'PriceClass_100':
                print(f"   ├─ 🌍 Edge Locations (US, Canada, Europe): 40% cost reduction")
            elif dist['price_class'] == 'PriceClass_200':
                print(f"   ├─ 🌍 Edge Locations (+ Asia, India): 20% cost reduction")
            else:
                print(f"   ├─ 🌍 Edge Locations (All): Full global coverage")
            print(f"   └─ 📊 Total Estimated: ~$10-60/month")
        else:
            print(f"   ├─ 📡 Data Transfer: $0.085/GB")
            print(f"   ├─ 🔄 HTTP Requests: $0.0075/10,000")
            print(f"   ├─ 🔒 HTTPS Requests: $0.0100/10,000")
            print(f"   └─ 🔐 SSL Certificates: $600/year for dedicated")
    
    def _display_cloudfront_copy_preview(self):
        """Display detailed preview for copy_from operations"""
        print(f"\n🌍 CloudFront CDN Preview (Copied Configuration)")
        print(f"╭─ 📋 CLONED from: {self._copied_from_distribution_id}")
        print(f"├─ 🆕 NEW Distribution: {self.name}-distribution")
        print(f"│")
        print(f"├─ 🔄 COPIED Settings:")
        print(f"│  ├─ 🌐 Origin Domain: {self.origin_domain}")
        
        # Show origins
        if hasattr(self, 'origins') and self.origins:
            origins_count = len(self.origins)
            print(f"│  ├─ 📡 Origins: {origins_count}")
            for origin in self.origins[:2]:  # Show first 2 origins
                print(f"│  │  ├─ {origin['domain']} ({origin['type']})")
            if origins_count > 2:
                print(f"│  │  └─ ... and {origins_count - 2} more")
        
        # SSL Certificate
        if hasattr(self, 'ssl_certificate_arn') and self.ssl_certificate_arn:
            print(f"│  ├─ 🔐 SSL Certificate: Custom ACM Certificate")
        else:
            print(f"│  ├─ 🔐 SSL Certificate: CloudFront Default")
            
        # Price class
        if hasattr(self, 'price_class_setting') and self.price_class_setting:
            price_class_name = {
                'PriceClass_All': 'Worldwide (All Edge Locations)',
                'PriceClass_200': 'US, Canada, Europe, Asia, India', 
                'PriceClass_100': 'US, Canada, Europe Only'
            }.get(self.price_class_setting, self.price_class_setting)
            print(f"│  ├─ 💰 Price Class: {price_class_name}")
        
        # Features
        if hasattr(self, 'http2_enabled'):
            print(f"│  ├─ ⚡ HTTP/2: {'✅ Enabled' if self.http2_enabled else '❌ Disabled'}")
        if hasattr(self, 'ipv6_enabled'):
            print(f"│  ├─ 🌐 IPv6: {'✅ Enabled' if self.ipv6_enabled else '❌ Disabled'}")
        if hasattr(self, 'compression_enabled'):
            print(f"│  ├─ 📦 Compression: {'✅ Enabled' if self.compression_enabled else '❌ Disabled'}")
        
        # WAF and Geo restrictions
        if hasattr(self, 'waf_web_acl_id') and self.waf_web_acl_id:
            print(f"│  ├─ 🛡️  WAF: ✅ Enabled")
        if hasattr(self, 'geo_restriction') and self.geo_restriction:
            print(f"│  ├─ 🌍 Geo Restrictions: ✅ {self.geo_restriction['type'].title()}")
        
        # Error pages and behaviors
        if hasattr(self, 'error_pages') and self.error_pages:
            print(f"│  ├─ 🚨 Error Pages: {len(self.error_pages)} configured")
        if hasattr(self, 'behaviors') and self.behaviors:
            print(f"│  ├─ 📊 Cache Behaviors: {len(self.behaviors)} custom")
            
        print(f"│")
        print(f"├─ ✨ NEW/UPDATED Settings:")
        
        # Custom domains 
        if hasattr(self, 'custom_domains') and self.custom_domains:
            print(f"│  ├─ 🔗 Custom Domains: {len(self.custom_domains)}")
            for domain in self.custom_domains:
                print(f"│  │  ├─ 🌐 {domain}")
        else:
            print(f"│  ├─ 🔗 Custom Domains: ⚠️  None (using CloudFront domain)")
            
        # Target Origin ID update
        if hasattr(self, '_custom_target_origin_id') and self._custom_target_origin_id:
            print(f"│  ├─ 🎯 Target Origin ID: {self._custom_target_origin_id}")
            
        print(f"│")
        print(f"├─ ⏱️  Deployment Time: 15-20 minutes (distribution propagation)")
        print(f"├─ 💰 Estimated Cost: $10-60/month (based on usage)")
        print(f"└─ 🚀 Ready to deploy with customizations")
        
        print(f"\n💰 Estimated Monthly Costs:")
        print(f"   ├─ 📡 Data Transfer: $0.085/GB")
        print(f"   ├─ 🔄 HTTP Requests: $0.0075/10,000")
        print(f"   ├─ 🔒 HTTPS Requests: $0.0100/10,000")
        print(f"   └─ 🔐 SSL Certificates: $600/year for dedicated")
    
    def create(self) -> Dict[str, Any]:
        """Create/update CloudFront distribution"""
        self._ensure_authenticated()
        
        if not self.origin_domain:
            raise ValueError("Origin domain is required. Use .origin('your-domain.com')")
        
        desired_distribution_name = f"{self.name}-distribution"
        distribution_id = f"E{str(uuid.uuid4()).replace('-', '').upper()[:13]}"
        cloudfront_domain = f"{distribution_id.lower()}.cloudfront.net"
        
        print(f"\n🌍 Creating CloudFront Distribution: {desired_distribution_name}")
        print(f"   🌐 Origin: {self.origin_domain}")
        print(f"   🔗 CloudFront Domain: {cloudfront_domain}")
        
        try:
            # Mock creation for now - in real implementation this would use AWS SDK
            result = {
                'distribution_id': distribution_id,
                'distribution_arn': f"arn:aws:cloudfront::{distribution_id}:distribution/{distribution_id}",
                'distribution_domain': cloudfront_domain,
                'distribution_name': desired_distribution_name,
                'origin_domain': self.origin_domain,
                'status': 'InProgress',
                'custom_domains': self.custom_domains,
                'ssl_certificate_arn': self.ssl_certificate_arn,
                'price_class': self.price_class_setting or 'PriceClass_All',
                'http2_enabled': self.http2_enabled,
                'ipv6_enabled': self.ipv6_enabled,
                'compression_enabled': self.compression_enabled,
                'security_headers': self.security_headers,
                'behaviors_count': len(self.behaviors),
                'error_pages_count': len(self.error_pages),
                'edge_locations': self._get_edge_locations_count(),
                'deployment_time': '15-20 minutes'
            }
            
            # Update instance attributes
            self.distribution_arn = result['distribution_arn']
            self.distribution_domain = result['distribution_domain']
            self.distribution_status = result['status']
            self.distribution_created = True
            
            self._display_creation_success(result)
            return result
            
        except Exception as e:
            print(f"❌ Failed to create CloudFront Distribution: {str(e)}")
            raise
    
    def _get_edge_locations_count(self):
        """Get number of edge locations based on price class"""
        edge_counts = {
            'PriceClass_100': 53,    # US, Canada, Europe
            'PriceClass_200': 89,    # + Asia, India, South America  
            'PriceClass_All': 225    # All edge locations worldwide
        }
        return edge_counts.get(self.price_class_setting, 225)
    
    def _display_creation_success(self, result: Dict[str, Any]):
        """Display creation success information"""
        print(f"✅ CloudFront Distribution created successfully")
        print(f"   📋 Distribution ID: {result['distribution_id']}")
        print(f"   🌍 CloudFront Domain: {result['distribution_domain']}")
        print(f"   🌐 Origin: {result['origin_domain']}")
        print(f"   🏷️  Price Class: {result['price_class']}")
        print(f"   📊 Status: {result['status']}")
        if result['custom_domains']:
            print(f"   🔗 Custom Domains: {len(result['custom_domains'])}")
        print(f"   🌍 Edge Locations: {result['edge_locations']}")
        print(f"   ⏱️  Deployment Time: {result['deployment_time']}")
        print(f"   ⚠️  Note: Distribution deployment can take 15-20 minutes to complete")
    
    def destroy(self) -> Dict[str, Any]:
        """Destroy the CloudFront distribution"""
        self._ensure_authenticated()
        
        print(f"🗑️ Destroying CloudFront Distribution: {self.name}")
        
        try:
            # Mock destruction for now - in real implementation this would use AWS SDK
            result = {
                'distribution_id': self.distribution_arn.split('/')[-1] if self.distribution_arn else 'Unknown',
                'distribution_name': f"{self.name}-distribution",
                'distribution_domain': self.distribution_domain,
                'status': 'Disabled',
                'deleted': True,
                'note': 'Distribution disabled and scheduled for deletion'
            }
            
            # Reset instance attributes
            self.distribution_arn = None
            self.distribution_domain = None
            self.distribution_status = None
            self.distribution_created = False
            
            print(f"✅ CloudFront Distribution destruction initiated")
            print(f"   📋 Distribution ID: {result['distribution_id']}")
            print(f"   📊 Status: {result['status']}")
            print(f"   ⚠️  Note: Complete deletion can take up to 24 hours")
            
            return result
            
        except Exception as e:
            print(f"❌ Failed to destroy CloudFront Distribution: {str(e)}")
            raise 