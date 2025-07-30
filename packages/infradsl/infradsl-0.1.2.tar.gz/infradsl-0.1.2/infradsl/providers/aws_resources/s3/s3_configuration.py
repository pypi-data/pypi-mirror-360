class S3ConfigurationMixin:
    """
    Mixin for S3 chainable configuration methods.
    """
    def bucket(self, name: str):
        """Set bucket name"""
        self.bucket_name = name
        return self

    def region(self, region: str):
        """Set AWS region for the bucket"""
        self.region_name = region
        return self

    def storage(self, storage_class: str):
        """Set storage class"""
        valid_classes = ["STANDARD", "STANDARD_IA", "ONEZONE_IA", "REDUCED_REDUNDANCY", "GLACIER", "DEEP_ARCHIVE"]
        if storage_class not in valid_classes:
            raise ValueError(f"Storage class must be one of: {valid_classes}")
        self.storage_class = storage_class
        return self

    def public(self, enabled: bool = True):
        """Enable or disable public access"""
        self.public_access = enabled
        return self

    def private(self):
        """Ensure bucket is private"""
        self.public_access = False
        return self

    def versioning(self, enabled: bool = True):
        """Enable or disable object versioning"""
        self.versioning_enabled = enabled
        return self

    def encryption(self, enabled: bool = True):
        """Enable or disable server-side encryption"""
        self.encryption_enabled = enabled
        return self

    def website(self, enabled: bool = True):
        """Enable static website hosting"""
        self.website_enabled = enabled
        return self

    def cors(self, enabled: bool = True):
        """Enable CORS for web applications"""
        self.cors_enabled = enabled
        return self

    def upload(self, source_path: str, key: str = None, public: bool = False):
        """Queue file for upload"""
        upload_info = {
            'local_path': source_path,
            'public': public
        }
        if key:
            upload_info['s3_key'] = key
        
        self._files_to_upload.append(upload_info)
        return self

    def upload_directory(self, source_dir: str, prefix: str = "", public: bool = False):
        """Queue directory for upload"""
        upload_info = {
            'local_path': source_dir,
            's3_prefix': prefix,
            'public': public
        }
        self._directories_to_upload.append(upload_info)
        return self

    def lifecycle(self, days: int, action: str = "transition", target_class: str = "GLACIER"):
        """Add lifecycle rule for cost optimization"""
        rule = {
            "ID": f"lifecycle-rule-{len(self.lifecycle_rules) + 1}",
            "Status": "Enabled",
            "Filter": {"Prefix": ""},
            "Transitions": [{
                "Days": days,
                "StorageClass": target_class
            }]
        }
        self.lifecycle_rules.append(rule)
        return self

    def tags(self, tags):
        """Set bucket tags"""
        if isinstance(tags, dict):
            self.bucket_tags.update(tags)
        else:
            raise ValueError("Tags must be a dictionary")
        return self

    def tag(self, key: str, value: str):
        """Add a single tag"""
        self.bucket_tags[key] = value
        return self

    def optimize_for(self, priority: str):
        """Use Cross-Cloud Magic to optimize for cost/performance/reliability
        
        Args:
            priority: Optimization priority - "cost", "performance", "reliability", "compliance"
            
        Returns:
            Self for method chaining
            
        Note:
            This integrates with InfraDSL's revolutionary Cross-Cloud Magic system
            to automatically select the optimal cloud provider and configuration.
        """
        valid_priorities = ["cost", "performance", "reliability", "compliance"]
        if priority not in valid_priorities:
            raise ValueError(f"Priority must be one of: {valid_priorities}. Got: {priority}")
        
        # Store optimization preference
        self._optimization_priority = priority
        
        print(f"🎯 Cross-Cloud Magic: Optimizing for {priority}")
        
        # Integrate with Cross-Cloud Intelligence
        try:
            from ....core.cross_cloud_intelligence import cross_cloud_intelligence, ServiceRequirements, ServiceCategory
            
            # Create service requirements for storage
            requirements = ServiceRequirements(
                service_category=ServiceCategory.STORAGE,
                service_type="user-uploads",  # Default to user uploads
                performance_tier="standard",
                reliability_requirement="high",
                cost_sensitivity=1.0 if priority == "cost" else 0.3,
                performance_sensitivity=1.0 if priority == "performance" else 0.3,
                reliability_sensitivity=1.0 if priority == "reliability" else 0.3,
                compliance_sensitivity=1.0 if priority == "compliance" else 0.3
            )
            
            # Get Cross-Cloud recommendation
            recommendation = cross_cloud_intelligence.select_optimal_provider(requirements)
            
            # Show recommendation to user
            if recommendation.recommended_provider != "aws":
                print(f"💡 Cross-Cloud Magic suggests {recommendation.recommended_provider.upper()} for {priority} optimization")
                print(f"   💰 Potential monthly savings: ${recommendation.estimated_monthly_cost:.2f}")
                print(f"   📊 Confidence: {recommendation.confidence_score:.1%}")
                print(f"   📝 Consider switching providers for optimal {priority}")
            else:
                print(f"✅ AWS S3 is optimal for {priority} optimization")
                
        except ImportError:
            print("⚠️  Cross-Cloud Magic not available - using provider-specific optimizations")
        except Exception as e:
            print(f"⚠️  Cross-Cloud Magic error: {e} - using provider-specific optimizations")
        
        # Apply AWS S3-specific optimizations
        if priority == "cost":
            print("💰 Cost optimization: Configuring cost-effective storage")
            self._apply_cost_optimizations()
        elif priority == "performance":
            print("⚡ Performance optimization: Configuring high-performance storage")
            self._apply_performance_optimizations()
        elif priority == "reliability":
            print("🛡️ Reliability optimization: Configuring reliable storage")
            self._apply_reliability_optimizations()
        elif priority == "compliance":
            print("📋 Compliance optimization: Configuring compliant storage")
            self._apply_compliance_optimizations()
        
        return self
    
    def cdn(self, enabled: bool = True):
        """Enable CloudFront CDN for the bucket
        
        Args:
            enabled: Whether to enable CDN distribution
            
        Returns:
            Self for method chaining
            
        Note:
            This automatically creates a CloudFront distribution for the bucket
            to improve global content delivery performance.
        """
        self._cdn_enabled = enabled
        if enabled:
            print("🌐 CDN enabled: CloudFront distribution will be created")
            # Store CDN configuration for later creation
            if not hasattr(self, '_cdn_config'):
                self._cdn_config = {
                    "price_class": "PriceClass_100",  # Use only North America and Europe
                    "compress": True,
                    "cache_behaviors": {
                        "static_assets": {
                            "path_pattern": "*.{js,css,png,jpg,jpeg,gif,ico,svg,woff,woff2}",
                            "ttl": 86400  # 24 hours
                        }
                    }
                }
        else:
            print("🚫 CDN disabled")
        return self
    
    def backup_retention(self, days: int):
        """Set backup retention policy using versioning and lifecycle
        
        Args:
            days: Number of days to retain old versions
            
        Returns:
            Self for method chaining
        """
        if days < 1:
            raise ValueError("Backup retention must be at least 1 day")
        
        # Enable versioning for backups
        self.versioning(True)
        
        # Configure lifecycle to clean up old versions
        self._backup_retention_days = days
        print(f"💾 Backup retention: {days} days (versioning + lifecycle)")
        
        return self
    
    def lifecycle_rule(self, name: str, **kwargs):
        """Add advanced lifecycle rule
        
        Args:
            name: Rule name
            **kwargs: Rule configuration (transition_days, storage_class, delete_after, etc.)
            
        Returns:
            Self for method chaining
        """
        if not hasattr(self, '_lifecycle_rules'):
            self._lifecycle_rules = []
        
        rule = {"name": name, **kwargs}
        self._lifecycle_rules.append(rule)
        
        print(f"⏰ Added lifecycle rule: {name}")
        return self
    
    def delete_after(self, days: int):
        """Configure automatic deletion after specified days
        
        Args:
            days: Number of days after which objects are deleted
            
        Returns:
            Self for method chaining
        """
        return self.lifecycle_rule("auto-delete", delete_after=days)
    
    def cors_config(self, allowed_origins=None, allowed_methods=None, allowed_headers=None):
        """Configure detailed CORS settings
        
        Args:
            allowed_origins: List of allowed origins (default: ["*"])
            allowed_methods: List of allowed methods (default: ["GET", "POST", "PUT", "DELETE"])
            allowed_headers: List of allowed headers (default: ["*"])
            
        Returns:
            Self for method chaining
        """
        if allowed_origins is None:
            allowed_origins = ["*"]
        if allowed_methods is None:
            allowed_methods = ["GET", "POST", "PUT", "DELETE"]
        if allowed_headers is None:
            allowed_headers = ["*"]
        
        self._cors_config = {
            "allowed_origins": allowed_origins,
            "allowed_methods": allowed_methods,
            "allowed_headers": allowed_headers,
            "max_age": 3600
        }
        
        print(f"🌐 CORS configured: {len(allowed_origins)} origins, {len(allowed_methods)} methods")
        return self
    
    def static_website(self, index_document="index.html", error_document="error.html"):
        """Configure as static website hosting
        
        Args:
            index_document: Default index document (default: "index.html")
            error_document: Error document (default: "error.html")
            
        Returns:
            Self for method chaining
        """
        self.website(True)
        self.public(True)  # Static websites need to be public
        
        self._website_config = {
            "index_document": index_document,
            "error_document": error_document
        }
        
        print(f"🌐 Static website configured: {index_document}")
        return self
    
    def _apply_cost_optimizations(self):
        """Apply AWS S3-specific cost optimizations"""
        # Use Standard-IA for cost savings on infrequently accessed data
        self.storage_class("STANDARD_IA")
        print("   💰 Using Standard-IA storage class for cost savings")
        
        # Add lifecycle rule to transition to Glacier
        self.lifecycle_rule("cost-optimization", 
                          transition_days=30, 
                          storage_class="GLACIER")
        print("   💰 Added lifecycle rule: transition to Glacier after 30 days")
        
        # Add cost optimization tags
        self.tag("cost-optimized", "true")
        self.tag("lifecycle-enabled", "true")
    
    def _apply_performance_optimizations(self):
        """Apply AWS S3-specific performance optimizations"""
        # Use Transfer Acceleration for better performance
        print("   ⚡ Performance: Transfer Acceleration recommended")
        
        # Enable CDN for better global performance
        self.cdn(True)
        print("   ⚡ Performance: CloudFront CDN enabled")
        
        # Add performance tags
        self.tag("performance-optimized", "true")
        self.tag("cdn-enabled", "true")
    
    def _apply_reliability_optimizations(self):
        """Apply AWS S3-specific reliability optimizations"""
        # Enable versioning for data protection
        self.versioning(True)
        print("   🛡️ Reliability: Object versioning enabled")
        
        # Enable server-side encryption
        self.encryption(True)
        print("   🛡️ Reliability: Server-side encryption enabled")
        
        # Configure backup retention
        self.backup_retention(30)
        print("   🛡️ Reliability: 30-day backup retention configured")
        
        # Add reliability tags
        self.tag("reliability-optimized", "true")
        self.tag("versioning-enabled", "true")
        self.tag("encryption-enabled", "true")
    
    def _apply_compliance_optimizations(self):
        """Apply AWS S3-specific compliance optimizations"""
        # Enable encryption for compliance
        self.encryption(True)
        print("   📋 Compliance: Server-side encryption enabled")
        
        # Enable versioning for audit trail
        self.versioning(True)
        print("   📋 Compliance: Object versioning for audit trail")
        
        # Make bucket private for compliance
        self.private()
        print("   📋 Compliance: Bucket access restricted to private")
        
        # Add compliance tags
        self.tag("compliance-optimized", "true")
        self.tag("audit-enabled", "true")
        self.tag("encryption-required", "true") 