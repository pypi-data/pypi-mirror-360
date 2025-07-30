"""
Google Cloud CDN Lifecycle Mixin

Lifecycle operations for Google Cloud CDN.
Provides create, destroy, and preview operations with smart state management.
"""

import time
from typing import Dict, Any, List, Optional, Union


class CloudCdnLifecycleMixin:
    """
    Mixin for Google Cloud CDN lifecycle operations.
    
    This mixin provides:
    - preview(): Preview what will be created/updated/deleted
    - create(): Create or update CDN configuration
    - destroy(): Clean up CDN configuration
    - Smart state management and cost estimation
    - Cross-Cloud Magic optimization
    """
    
    def preview(self) -> Dict[str, Any]:
        """Preview what will be created, kept, and removed"""
        # Check authentication first
        try:
            self._ensure_authenticated()
        except Exception:
            print("⚠️  Authentication required for Cloud CDN preview")
            
        # Get current CDN state
        existing_cdns = self._discover_existing_cdns()
        
        # Categorize what will happen
        cdns_to_create = []
        cdns_to_keep = []
        cdns_to_update = []
        
        cdn_config = {
            "cdn_name": self.cdn_name,
            "enabled": self.enabled,
            "cache_mode": self.cache_mode,
            "default_ttl": self.default_ttl,
            "max_ttl": self.max_ttl,
            "compression_mode": self.compression_mode,
            "backend_service": self.backend_service,
            "backend_bucket": self.backend_bucket,
            "negative_caching": self.negative_caching,
            "path_matchers": len(self.path_matchers),
            "cache_key_policy": self.cache_key_policy,
            "labels": self.cdn_labels,
            "estimated_cost": self._estimate_cdn_cost()
        }
        
        if self.cdn_name not in existing_cdns:
            # New CDN configuration
            cdns_to_create.append(cdn_config)
        else:
            # Existing CDN
            existing_cdn = existing_cdns[self.cdn_name]
            cdns_to_keep.append(existing_cdn)
            
        print(f"\\n🌐 Cloud CDN Preview")
        
        # Show CDNs to create
        if cdns_to_create:
            print(f"╭─ 🌐 CDN Configurations to CREATE: {len(cdns_to_create)}")
            for cdn in cdns_to_create:
                print(f"├─ 🆕 {cdn['cdn_name']}")
                print(f"│  ├─ 🔄 Status: {'✅ Enabled' if cdn['enabled'] else '❌ Disabled'}")
                print(f"│  ├─ 💾 Cache Mode: {cdn['cache_mode']}")
                print(f"│  ├─ ⏰ Default TTL: {cdn['default_ttl']}s")
                print(f"│  ├─ ⏰ Max TTL: {cdn['max_ttl']}s")
                print(f"│  ├─ 🗜️ Compression: {cdn['compression_mode']}")
                
                # Backend configuration
                backends = []
                if cdn['backend_service']:
                    backends.append(f"Service: {cdn['backend_service']}")
                if cdn['backend_bucket']:
                    backends.append(f"Bucket: {cdn['backend_bucket']}")
                if backends:
                    print(f"│  ├─ 🔙 Backends: {', '.join(backends)}")
                else:
                    print(f"│  ├─ ⚠️ Backends: None configured")
                    
                print(f"│  ├─ 🚫 Negative Caching: {'✅ Enabled' if cdn['negative_caching'] else '❌ Disabled'}")
                print(f"│  ├─ 🛣️ Path Matchers: {cdn['path_matchers']}")
                
                if cdn['labels']:
                    print(f"│  ├─ 🏷️ Labels: {len(cdn['labels'])}")
                    
                cost = cdn['estimated_cost']
                print(f"│  └─ 💰 Estimated Cost: ${cost:,.2f}/month")
            print(f"╰─")
            
        # Show existing CDNs
        if cdns_to_keep:
            print(f"\\n╭─ ✅ Existing CDN Configurations: {len(cdns_to_keep)}")
            for cdn in cdns_to_keep:
                print(f"├─ ✅ {cdn['cdn_name']}")
                print(f"│  ├─ 🔄 Status: {cdn['status']}")
                print(f"│  ├─ 🛠️ Type: {cdn['type']}")
                print(f"│  └─ 📅 Created: {cdn['create_time']}")
            print(f"╰─")
            
        # Show CDN capabilities
        print(f"\\n🌐 Cloud CDN Features:")
        print(f"   ├─ 🌍 Global edge locations (130+ cities)")
        print(f"   ├─ 🚀 Ultra-low latency content delivery")
        print(f"   ├─ 🛡️ DDoS protection and security")
        print(f"   ├─ 📊 Real-time cache analytics")
        print(f"   ├─ 🗜️ Automatic content compression")
        print(f"   ├─ 🔄 Cache invalidation and purging")
        print(f"   ├─ 🔐 Signed URLs and security policies")
        print(f"   └─ 📈 HTTP/2 and QUIC protocol support")
        
        # Cost information
        print(f"\\n💰 Cloud CDN Pricing:")
        print(f"   ├─ 🌐 Cache egress: $0.04-$0.15/GB (tiered)")
        print(f"   ├─ 📥 Cache fill: $0.085/GB")
        print(f"   ├─ 📊 HTTP requests: $0.0075 per 10,000")
        print(f"   ├─ 🗑️ Cache invalidations: First 1,000 free")
        if cdns_to_create:
            print(f"   └─ 📊 Estimated: ${cdns_to_create[0]['estimated_cost']:,.2f}/month")
        else:
            print(f"   └─ 📊 Varies by traffic volume")
            
        return {
            "resource_type": "cloud_cdn",
            "name": self.cdn_name,
            "cdns_to_create": cdns_to_create,
            "cdns_to_keep": cdns_to_keep,
            "cdns_to_update": cdns_to_update,
            "existing_cdns": existing_cdns,
            "project_id": self.project_id,
            "estimated_cost": f"${self._estimate_cdn_cost():,.2f}/month"
        }
        
    def create(self) -> Dict[str, Any]:
        """Create CDN configuration"""
        if not self.project_id:
            raise ValueError("Project ID is required. Use .project('your-project-id')")
            
        if not (self.backend_service or self.backend_bucket):
            raise ValueError("Backend service or bucket is required. Use .backend_service() or .backend_bucket()")
            
        print(f"🚀 Creating Cloud CDN: {self.cdn_name}")
        
        # Check if CDN exists
        cdn_state = self._fetch_current_cdn_state()
        
        results = {
            "success": True,
            "cdn_created": False,
            "components_created": [],
            "failed": []
        }
        
        if not cdn_state.get("exists"):
            # Create CDN configuration
            try:
                print(f"   🌐 Creating CDN configuration: {self.cdn_name}")
                print(f"      ├─ Cache Mode: {self.cache_mode}")
                print(f"      ├─ Default TTL: {self.default_ttl}s")
                print(f"      ├─ Max TTL: {self.max_ttl}s")
                
                if self.backend_service:
                    print(f"      ├─ Backend Service: {self.backend_service}")
                if self.backend_bucket:
                    print(f"      ├─ Backend Bucket: {self.backend_bucket}")
                    
                cdn_result = self._create_cdn_configuration()
                
                if cdn_result["success"]:
                    print(f"   ✅ CDN configuration created successfully")
                    results["cdn_created"] = True
                    results["components_created"].append("cdn_configuration")
                    
                    # Update state tracking
                    self.cdn_exists = True
                    self.cdn_created = True
                    self.deployment_status = "deployed"
                else:
                    raise Exception(cdn_result.get("error", "CDN creation failed"))
                    
            except Exception as e:
                print(f"   ❌ CDN creation failed: {str(e)}")
                results["failed"].append({
                    "resource": "cdn_configuration",
                    "name": self.cdn_name,
                    "error": str(e)
                })
                results["success"] = False
                return results
        else:
            print(f"   ✅ CDN configuration already exists: {self.cdn_name}")
            
        # Create path matchers if configured
        if self.path_matchers:
            try:
                print(f"   🛣️ Configuring path matchers: {len(self.path_matchers)}")
                
                for matcher in self.path_matchers:
                    matcher_result = self._create_path_matcher(matcher)
                    if matcher_result["success"]:
                        print(f"   ✅ Path matcher created: {matcher['name']}")
                        results["components_created"].append(f"path_matcher_{matcher['name']}")
                    else:
                        print(f"   ⚠️ Path matcher failed: {matcher['name']}")
                        
            except Exception as e:
                print(f"   ⚠️ Path matcher configuration warning: {str(e)}")
                
        # Show summary
        print(f"\\n📊 Creation Summary:")
        print(f"   ├─ 🌐 CDN: {'✅ Created' if results['cdn_created'] else '✅ Exists'}")
        print(f"   ├─ 🧩 Components: {len(results['components_created'])} created")
        print(f"   └─ ❌ Failed: {len(results['failed'])}")
        
        if results["success"]:
            cost = self._estimate_cdn_cost()
            print(f"\\n💰 Estimated Cost: ${cost:,.2f}/month")
            print(f"🌐 Console: https://console.cloud.google.com/net-services/cdn/list?project={self.project_id}")
            
        # Final result
        results.update({
            "cdn_name": self.cdn_name,
            "project_id": self.project_id,
            "cache_mode": self.cache_mode,
            "backend_service": self.backend_service,
            "backend_bucket": self.backend_bucket,
            "estimated_cost": f"${self._estimate_cdn_cost():,.2f}/month",
            "console_url": f"https://console.cloud.google.com/net-services/cdn/list?project={self.project_id}"
        })
        
        return results
        
    def destroy(self) -> Dict[str, Any]:
        """Destroy CDN configuration"""
        print(f"🗑️ Destroying Cloud CDN: {self.cdn_name}")
        
        try:
            # Check if CDN exists
            cdn_state = self._fetch_current_cdn_state()
            
            if not cdn_state.get("exists"):
                print(f"   ℹ️ CDN doesn't exist: {self.cdn_name}")
                return {
                    "success": True,
                    "message": "CDN doesn't exist"
                }
                
            print(f"   🗑️ Deleting CDN configuration: {self.cdn_name}")
            print(f"   ⚠️ This will remove CDN from all backend services")
            
            # Delete CDN configuration
            delete_result = self._delete_cdn_configuration()
            
            if delete_result["success"]:
                print(f"   ✅ CDN configuration deleted successfully")
                
                # Update state tracking
                self.cdn_exists = False
                self.cdn_created = False
                self.deployment_status = "destroyed"
                
                return {
                    "success": True,
                    "cdn_name": self.cdn_name,
                    "project_id": self.project_id,
                    "message": "CDN configuration deleted"
                }
            else:
                raise Exception(delete_result.get("error", "Deletion failed"))
                
        except Exception as e:
            print(f"   ❌ Deletion failed: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
            
    def _create_cdn_configuration(self) -> Dict[str, Any]:
        """Create CDN configuration using API"""
        try:
            # In a real implementation, this would:
            # 1. Update backend service to enable CDN
            # 2. Configure cache policies
            # 3. Set up URL maps if needed
            # 4. Configure SSL certificates
            
            print(f"      ⏳ Configuring CDN (this may take a few minutes)...")
            
            # Simulate CDN configuration
            time.sleep(2)
            
            return {
                "success": True,
                "message": "CDN configuration created (simulated)"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
            
    def _create_path_matcher(self, matcher: Dict[str, Any]) -> Dict[str, Any]:
        """Create path matcher configuration"""
        try:
            # In a real implementation, this would update URL maps
            # with the path matcher configuration
            
            return {
                "success": True,
                "path_matcher": matcher
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
            
    def _delete_cdn_configuration(self) -> Dict[str, Any]:
        """Delete CDN configuration using API"""
        try:
            # In a real implementation, this would:
            # 1. Disable CDN on backend services
            # 2. Clean up cache policies
            # 3. Remove URL map configurations
            
            return {
                "success": True,
                "message": "CDN configuration deleted (simulated)"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
            
    # Cross-Cloud Magic Integration
    def optimize_for(self, optimization_target: str):
        """
        Cross-Cloud Magic: Optimize Cloud CDN configuration for specific targets.
        
        Args:
            optimization_target: Target to optimize for ('cost', 'performance', 'security', 'user_experience')
        """
        if optimization_target.lower() == "cost":
            return self._optimize_for_cost()
        elif optimization_target.lower() == "performance":
            return self._optimize_for_performance()
        elif optimization_target.lower() == "security":
            return self._optimize_for_security()
        elif optimization_target.lower() == "user_experience":
            return self._optimize_for_user_experience()
        else:
            print(f"⚠️ Unknown optimization target: {optimization_target}")
            return self
            
    def _optimize_for_cost(self):
        """Optimize configuration for cost efficiency"""
        print("🏗️ Applying Cross-Cloud Magic: Cost Optimization")
        
        # Longer cache times to reduce origin requests
        self.default_ttl(86400)  # 24 hours
        self.max_ttl(604800)     # 7 days
        self.serve_while_stale(86400)
        
        # Enable compression to reduce bandwidth
        self.auto_compression()
        
        # Enable negative caching
        self.negative_caching(True)
        
        # Add cost optimization labels
        self.labels({
            "optimization": "cost",
            "cache_strategy": "aggressive",
            "compression": "enabled"
        })
        
        print("   ├─ ⏰ Extended cache TTLs")
        print("   ├─ 🗜️ Automatic compression enabled")
        print("   ├─ 🚫 Negative caching enabled")
        print("   └─ 🏷️ Added cost optimization labels")
        
        return self
        
    def _optimize_for_performance(self):
        """Optimize configuration for performance"""
        print("🏗️ Applying Cross-Cloud Magic: Performance Optimization")
        
        # Aggressive caching for performance
        self.force_cache_all()
        self.default_ttl(3600)   # 1 hour
        self.max_ttl(86400)      # 24 hours
        self.serve_while_stale(3600)
        
        # Enable compression
        self.auto_compression()
        
        # Optimize cache key policy
        self.include_query_string(False)  # Reduce cache variations
        
        # Add performance labels
        self.labels({
            "optimization": "performance",
            "cache_strategy": "aggressive",
            "query_handling": "simplified"
        })
        
        print("   ├─ 🚀 Aggressive cache mode")
        print("   ├─ ⏰ Optimized TTL settings")
        print("   ├─ 🗜️ Compression enabled")
        print("   ├─ 🔑 Simplified cache key policy")
        print("   └─ 🏷️ Added performance optimization labels")
        
        return self
        
    def _optimize_for_security(self):
        """Optimize configuration for security"""
        print("🏗️ Applying Cross-Cloud Magic: Security Optimization")
        
        # Conservative caching for security
        self.use_origin_headers()
        self.default_ttl(3600)   # 1 hour
        self.max_ttl(86400)      # 24 hours
        
        # Include more headers in cache key for security
        self.include_headers(["authorization", "user-agent"])
        
        # Enable signed URL support
        self.signed_url_cache_max_age(3600)
        
        # Add security labels
        self.labels({
            "optimization": "security",
            "cache_strategy": "conservative",
            "header_handling": "strict"
        })
        
        print("   ├─ 🔒 Conservative cache mode")
        print("   ├─ 🔑 Enhanced cache key policy")
        print("   ├─ ✍️ Signed URL support")
        print("   └─ 🏷️ Added security optimization labels")
        
        return self
        
    def _optimize_for_user_experience(self):
        """Optimize configuration for user experience"""
        print("🏗️ Applying Cross-Cloud Magic: User Experience Optimization")
        
        # Balanced caching for UX
        self.cache_static_content()
        self.default_ttl(1800)   # 30 minutes
        self.max_ttl(86400)      # 24 hours
        self.serve_while_stale(1800)
        
        # Enable compression for faster loading
        self.auto_compression()
        
        # Enable negative caching to handle errors gracefully
        self.negative_caching(True)
        self.negative_cache_policy(404, 300)  # Cache 404s for 5 minutes
        
        # Add UX labels
        self.labels({
            "optimization": "user_experience",
            "cache_strategy": "balanced",
            "error_handling": "graceful"
        })
        
        print("   ├─ ⚖️ Balanced cache strategy")
        print("   ├─ 🗜️ Compression for faster loading")
        print("   ├─ 🚫 Graceful error caching")
        print("   └─ 🏷️ Added UX optimization labels")
        
        return self