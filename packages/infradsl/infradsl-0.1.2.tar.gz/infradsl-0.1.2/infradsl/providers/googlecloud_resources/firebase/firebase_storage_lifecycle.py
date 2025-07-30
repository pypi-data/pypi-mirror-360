"""
Firebase Storage Lifecycle Mixin

Lifecycle operations for Firebase Storage.
Provides create, destroy, and preview operations with smart state management.
"""

import json
import os
import subprocess
from typing import Dict, Any, List, Optional, Union


class FirebaseStorageLifecycleMixin:
    """
    Mixin for Firebase Storage lifecycle operations.
    
    This mixin provides:
    - preview(): Preview what will be created/updated/deleted
    - create(): Create or update Firebase Storage configuration
    - destroy(): Clean up Firebase Storage configuration
    - Smart state management and drift detection
    - Cross-Cloud Magic optimization
    """
    
    def preview(self) -> Dict[str, Any]:
        """Preview what will be created, kept, and removed"""
        # Discover existing buckets
        existing_buckets = self._discover_existing_buckets()
        
        # Categorize buckets
        buckets_to_create = []
        buckets_to_keep = []
        buckets_to_update = []
        
        # Check if our desired bucket exists
        target_bucket_name = self.get_bucket_name()
        bucket_exists = target_bucket_name in existing_buckets
        
        if not bucket_exists:
            buckets_to_create.append({
                'bucket_name': target_bucket_name,
                'storage_name': self.storage_name,
                'firebase_project_id': self.firebase_project_id,
                'storage_type': self._get_storage_type_from_config(),
                'location': self.location,
                'storage_class': self.storage_class,
                'public_access': self.public_access,
                'public_read': self.public_read,
                'authenticated_read': self.authenticated_read,
                'uniform_bucket_level_access': self.uniform_bucket_level_access,
                'security_rules_configured': self.has_security_rules(),
                'default_security_rules': self.default_security_rules,
                'cors_enabled': self.cors_enabled,
                'cors_origins': self.cors_origins,
                'lifecycle_rule_count': len(self.lifecycle_rules),
                'versioning_enabled': self.versioning_enabled,
                'retention_policy': self.retention_policy,
                'cdn_enabled': self.cdn_enabled,
                'compression_enabled': self.compression_enabled,
                'max_upload_size': self.max_upload_size,
                'allowed_file_types': self.allowed_file_types,
                'thumbnail_generation': self.thumbnail_generation,
                'caching_configured': self.has_caching_configured(),
                'monitoring_enabled': self.has_monitoring_enabled(),
                'logging_enabled': self.logging_enabled,
                'notification_count': len(self.notifications),
                'labels': self.storage_labels,
                'label_count': len(self.storage_labels),
                'estimated_cost': self._estimate_firebase_storage_cost()
            })
        else:
            existing_bucket = existing_buckets[target_bucket_name]
            buckets_to_keep.append(existing_bucket)

        print(f"\\n🔥 Firebase Storage Preview")
        
        # Show buckets to create
        if buckets_to_create:
            print(f"╭─ 📁 Storage Buckets to CREATE: {len(buckets_to_create)}")
            for bucket in buckets_to_create:
                print(f"├─ 🆕 {bucket['bucket_name']}")
                print(f"│  ├─ 📁 Storage Name: {bucket['storage_name']}")
                
                if bucket['firebase_project_id']:
                    print(f"│  ├─ 📋 Firebase Project: {bucket['firebase_project_id']}")
                
                print(f"│  ├─ 🎯 Storage Type: {bucket['storage_type'].replace('_', ' ').title()}")
                print(f"│  ├─ 📍 Location: {bucket['location']}")
                print(f"│  ├─ 💾 Storage Class: {bucket['storage_class']}")
                
                # Show access configuration
                print(f"│  ├─ 🔒 Access Configuration:")
                print(f"│  │  ├─ 🌐 Public Access: {'✅ Enabled' if bucket['public_access'] else '❌ Disabled'}")
                print(f"│  │  ├─ 👁️  Public Read: {'✅ Enabled' if bucket['public_read'] else '❌ Disabled'}")
                print(f"│  │  ├─ 🔐 Authenticated Read: {'✅ Enabled' if bucket['authenticated_read'] else '❌ Disabled'}")
                print(f"│  │  └─ 🛡️  Uniform Access: {'✅ Enabled' if bucket['uniform_bucket_level_access'] else '❌ Disabled'}")
                
                # Show security configuration
                print(f"│  ├─ 🔒 Security Configuration:")
                if bucket['security_rules_configured']:
                    if self.security_rules_file:
                        print(f"│  │  ├─ 📄 Rules File: {self.security_rules_file}")
                    else:
                        print(f"│  │  ├─ 📝 Custom Rules: Configured")
                else:
                    print(f"│  │  ├─ 📝 Security Rules: {'✅ Default (auth required)' if bucket['default_security_rules'] else '❌ None'}")
                
                # Show CORS configuration
                if bucket['cors_enabled']:
                    origins = bucket['cors_origins']
                    print(f"│  │  ├─ 🌍 CORS: ✅ Enabled")
                    if origins == ["*"]:
                        print(f"│  │  │  └─ 🌐 Origins: All (*)") 
                    else:
                        print(f"│  │  │  └─ 🌐 Origins: {len(origins)} configured")
                else:
                    print(f"│  │  └─ 🌍 CORS: ❌ Disabled")
                
                # Show lifecycle configuration
                print(f"│  ├─ ⏰ Lifecycle Configuration:")
                if bucket['lifecycle_rule_count'] > 0:
                    print(f"│  │  ├─ 📋 Rules: {bucket['lifecycle_rule_count']}")
                    for i, rule in enumerate(self.lifecycle_rules[:3]):  # Show first 3
                        action = rule.get('action', 'unknown')
                        condition = rule.get('condition', {})
                        connector = "│  │  │  ├─" if i < min(len(self.lifecycle_rules), 3) - 1 else "│  │  │  └─"
                        
                        if 'age' in condition:
                            print(f"{connector} {action} after {condition['age']} days")
                        elif 'storageClass' in condition:
                            print(f"{connector} Move to {condition['storageClass']}")
                        else:
                            print(f"{connector} {action}")
                    
                    if len(self.lifecycle_rules) > 3:
                        print(f"│  │  │     └─ ... and {len(self.lifecycle_rules) - 3} more rules")
                else:
                    print(f"│  │  ├─ 📋 Rules: None")
                
                print(f"│  │  ├─ 🔄 Versioning: {'✅ Enabled' if bucket['versioning_enabled'] else '❌ Disabled'}")
                
                if bucket['retention_policy']:
                    retention_days = int(bucket['retention_policy']['retentionPeriod']) // 86400
                    print(f"│  │  └─ 🔒 Retention: {retention_days} days")
                else:
                    print(f"│  │  └─ 🔒 Retention: None")
                
                # Show performance configuration
                print(f"│  ├─ 🚀 Performance Configuration:")
                print(f"│  │  ├─ 🌍 CDN: {'✅ Enabled' if bucket['cdn_enabled'] else '❌ Disabled'}")
                print(f"│  │  ├─ 🗜️  Compression: {'✅ Enabled' if bucket['compression_enabled'] else '❌ Disabled'}")
                print(f"│  │  └─ 📦 Caching: {'✅ Configured' if bucket['caching_configured'] else '❌ Not configured'}")
                
                # Show upload configuration
                print(f"│  ├─ 📤 Upload Configuration:")
                if bucket['max_upload_size']:
                    size_mb = bucket['max_upload_size'] // (1024 * 1024)
                    print(f"│  │  ├─ 📏 Max Size: {size_mb} MB")
                else:
                    print(f"│  │  ├─ 📏 Max Size: Unlimited")
                
                if bucket['allowed_file_types']:
                    file_type_count = len(bucket['allowed_file_types'])
                    print(f"│  │  ├─ 📄 File Types: {file_type_count} allowed")
                    for file_type in bucket['allowed_file_types'][:3]:
                        print(f"│  │  │  ├─ {file_type}")
                    if len(bucket['allowed_file_types']) > 3:
                        print(f"│  │  │  └─ ... and {len(bucket['allowed_file_types']) - 3} more")
                else:
                    print(f"│  │  ├─ 📄 File Types: All allowed")
                
                print(f"│  │  └─ 🖼️  Thumbnails: {'✅ Enabled' if bucket['thumbnail_generation'] else '❌ Disabled'}")
                
                # Show monitoring configuration
                print(f"│  ├─ 📊 Monitoring Configuration:")
                print(f"│  │  ├─ 📋 Logging: {'✅ Enabled' if bucket['logging_enabled'] else '❌ Disabled'}")
                print(f"│  │  ├─ 📈 Monitoring: {'✅ Enabled' if bucket['monitoring_enabled'] else '❌ Disabled'}")
                print(f"│  │  └─ 🔔 Notifications: {bucket['notification_count']}")
                
                # Show Firebase Storage features
                print(f"│  ├─ 🔥 Firebase Storage Features:")
                print(f"│  │  ├─ 📱 Mobile SDK integration")
                print(f"│  │  ├─ 🔒 Security Rules integration")
                print(f"│  │  ├─ 🌍 Global CDN (Firebase)")
                print(f"│  │  ├─ 🔄 Real-time upload progress")
                print(f"│  │  ├─ 🖼️  Image transformations")
                print(f"│  │  └─ ⚡ Instant file sharing")
                
                # Show labels
                if bucket['label_count'] > 0:
                    print(f"│  ├─ 🏷️  Labels ({bucket['label_count']}):")
                    for key, value in list(bucket['labels'].items())[:3]:
                        print(f"│  │  ├─ {key}: {value}")
                    if len(bucket['labels']) > 3:
                        print(f"│  │  └─ ... and {len(bucket['labels']) - 3} more")
                
                cost = bucket['estimated_cost']
                if cost > 0:
                    print(f"│  └─ 💰 Estimated Cost: ${cost:.2f}/month")
                else:
                    print(f"│  └─ 💰 Cost: Free tier")
            print(f"╰─")

        # Show existing buckets being kept
        if buckets_to_keep:
            print(f"\\n╭─ 📁 Existing Storage Buckets to KEEP: {len(buckets_to_keep)}")
            for bucket in buckets_to_keep:
                print(f"├─ ✅ {bucket['bucket_name']}")
                print(f"│  ├─ 📋 Firebase Project: {bucket['firebase_project_id']}")
                print(f"│  ├─ 📍 Location: {bucket['location']}")
                print(f"│  ├─ 💾 Storage Class: {bucket['storage_class']}")
                print(f"│  ├─ 🌐 Public Access: {'✅ Enabled' if bucket.get('public_access', False) else '❌ Disabled'}")
                
                # Show current usage
                if bucket.get('sample_object_count', 0) > 0:
                    print(f"│  ├─ 📊 Objects: {bucket['sample_object_count']:,} (sample)")
                    if bucket.get('sample_size_gb', 0) > 0:
                        if bucket['sample_size_gb'] < 1:
                            print(f"│  ├─ 💾 Size: {bucket['sample_size_bytes']:,} bytes (sample)")
                        else:
                            print(f"│  ├─ 💾 Size: {bucket['sample_size_gb']} GB (sample)")
                else:
                    print(f"│  ├─ 📊 Objects: Empty or no access")
                
                # Show configuration
                print(f"│  ├─ 🔄 Versioning: {'✅ Enabled' if bucket.get('versioning_enabled', False) else '❌ Disabled'}")
                print(f"│  ├─ 🌍 CORS: {'✅ Enabled' if bucket.get('cors_enabled', False) else '❌ Disabled'}")
                
                if bucket.get('lifecycle_rule_count', 0) > 0:
                    print(f"│  ├─ ⏰ Lifecycle Rules: {bucket['lifecycle_rule_count']}")
                
                print(f"│  ├─ 📅 Created: {bucket.get('creation_time', 'unknown')}")
                print(f"│  └─ 🌐 Access: gs://{bucket['bucket_name']}")
            print(f"╰─")

        # Show deployment information
        if buckets_to_create:
            print(f"\\n🚀 Firebase Storage Deployment:")
            bucket = buckets_to_create[0]
            print(f"   ├─ 📁 Bucket: gs://{bucket['bucket_name']}")
            print(f"   ├─ 📍 Location: {bucket['location']}")
            print(f"   ├─ 💾 Storage Class: {bucket['storage_class']}")
            
            if bucket['firebase_project_id']:
                print(f"   ├─ 📋 Firebase Project: {bucket['firebase_project_id']}")
            
            # Show deployment features
            features = []
            if bucket['security_rules_configured']:
                features.append("Security rules")
            if bucket['cors_enabled']:
                features.append("CORS")
            if bucket['lifecycle_rule_count'] > 0:
                features.append("Lifecycle rules")
            if bucket['versioning_enabled']:
                features.append("Versioning")
            if bucket['cdn_enabled']:
                features.append("CDN")
            
            if features:
                print(f"   ├─ 🚀 Features: {', '.join(features)}")
            
            print(f"   └─ 🚀 Deploy: firebase deploy --only storage")

        # Show cost information
        print(f"\\n💰 Firebase Storage Costs:")
        if buckets_to_create:
            bucket = buckets_to_create[0]
            cost = bucket['estimated_cost']
            
            print(f"   ├─ 📁 Storage: Free tier (5GB), then $0.026/GB/month")
            print(f"   ├─ 📡 Downloads: Free tier (1GB/day), then $0.12/GB")
            print(f"   ├─ 🔄 Operations: Free tier (50K/day), then $0.05/10K operations")
            print(f"   ├─ 🌍 Global CDN: Included")
            print(f"   ├─ 🔒 Security Rules: Free")
            print(f"   ├─ 📱 Mobile SDKs: Free")
            
            if cost > 0:
                print(f"   └─ 📊 Estimated: ${cost:.2f}/month")
            else:
                print(f"   └─ 📊 Total: Free tier (typical usage)")
        else:
            print(f"   ├─ 📁 Free tier: 5GB storage")
            print(f"   ├─ 📡 Free tier: 1GB/day downloads")
            print(f"   ├─ 🔄 Free tier: 50K/day operations")
            print(f"   ├─ 🌍 Global CDN: Included")
            print(f"   └─ 📊 Additional usage: Pay-as-you-go")

        return {
            'resource_type': 'firebase_storage',
            'name': self.storage_name,
            'buckets_to_create': buckets_to_create,
            'buckets_to_keep': buckets_to_keep,
            'buckets_to_update': buckets_to_update,
            'existing_buckets': existing_buckets,
            'bucket_name': target_bucket_name,
            'firebase_project_id': self.firebase_project_id,
            'storage_type': self._get_storage_type_from_config(),
            'location': self.location,
            'storage_class': self.storage_class,
            'estimated_cost': f"${self._estimate_firebase_storage_cost():.2f}/month"
        }

    def create(self) -> Dict[str, Any]:
        """Create or update Firebase Storage bucket"""
        if not self.firebase_project_id:
            raise ValueError("Firebase project ID is required. Use .project('your-project-id')")
        
        existing_state = self._fetch_current_storage_state()
        if existing_state and existing_state.get("exists", False):
            print(f"🔄 Firebase Storage bucket already exists: {self.get_bucket_name()}")
            return self._update_existing_bucket(existing_state)
        
        print(f"🚀 Creating Firebase Storage: {self.storage_name}")
        return self._create_new_bucket()

    def destroy(self) -> Dict[str, Any]:
        """Destroy Firebase Storage bucket"""
        print(f"🗑️  Destroying Firebase Storage: {self.storage_name}")
        
        bucket_name = self.get_bucket_name()

        try:
            print(f"⚠️  Firebase Storage buckets should be deleted carefully")
            print(f"🔧 To delete the bucket:")
            print(f"   1. Go to Firebase Console: https://console.firebase.google.com/project/{self.firebase_project_id}/storage/")
            print(f"   2. Select bucket: {bucket_name}")
            print(f"   3. Delete all objects first")
            print(f"   4. Delete the bucket manually")
            print(f"   5. Or use: gsutil rm -r gs://{bucket_name}")
            
            # Remove local config files
            config_files = ["storage.rules", "firebase.json"]
            removed_files = []
            
            for config_file in config_files:
                if os.path.exists(config_file):
                    try:
                        # Check if firebase.json contains storage config
                        if config_file == "firebase.json":
                            with open(config_file, 'r') as f:
                                config_data = json.load(f)
                            
                            if "storage" in config_data:
                                # Remove storage section
                                del config_data["storage"]
                                
                                # If firebase.json is now empty, delete it
                                if not config_data or config_data == {}:
                                    os.remove(config_file)
                                    removed_files.append(config_file)
                                else:
                                    # Update firebase.json without storage
                                    with open(config_file, 'w') as f:
                                        json.dump(config_data, f, indent=2)
                                    print(f"   📄 Removed storage config from {config_file}")
                        else:
                            os.remove(config_file)
                            removed_files.append(config_file)
                    except Exception:
                        pass  # Ignore errors removing config files
            
            if removed_files:
                print(f"   🗑️  Removed local files: {', '.join(removed_files)}")
            
            return {
                'success': True,
                'storage_name': self.storage_name,
                'bucket_name': bucket_name,
                'status': 'manual_action_required',
                'removed_files': removed_files,
                'console_url': f"https://console.firebase.google.com/project/{self.firebase_project_id}/storage/"
            }

        except Exception as e:
            print(f"❌ Failed to destroy Firebase Storage: {str(e)}")
            return {'success': False, 'error': str(e)}

    def optimize_for(self, optimization_target: str):
        """
        Cross-Cloud Magic: Optimize Firebase Storage configuration for specific targets.
        
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
            print(f"⚠️  Unknown optimization target: {optimization_target}")
            return self

    def _optimize_for_cost(self):
        """Optimize configuration for cost efficiency"""
        print("🏗️  Applying Cross-Cloud Magic: Cost Optimization")
        
        # Use cheaper storage class for infrequent access
        self.storage_class("NEARLINE")
        
        # Aggressive lifecycle management
        self.delete_after_days(90)
        self.archive_after_days(30)
        
        # Minimal features to reduce operations
        self.compression(False)  # Save on CPU costs
        self.thumbnail_generation(False)
        self.monitoring(False)
        self.logging(False)
        
        # Restrict uploads to reduce storage
        self.max_upload_size_mb(10)
        
        # Add cost optimization labels
        self.labels({
            "optimization": "cost",
            "cost_management": "enabled",
            "storage_class": "nearline"
        })
        
        print("   ├─ 💾 Set storage class to NEARLINE")
        print("   ├─ ⏰ Aggressive lifecycle rules")
        print("   ├─ 📉 Disabled expensive features")
        print("   ├─ 📏 Limited upload size")
        print("   └─ 🏷️  Added cost optimization labels")
        
        return self

    def _optimize_for_performance(self):
        """Optimize configuration for performance"""
        print("🏗️  Applying Cross-Cloud Magic: Performance Optimization")
        
        # Use standard storage class for best performance
        self.storage_class("STANDARD")
        
        # Enable all performance features
        self.cdn(True)
        self.compression(True)
        self.cache_images(86400)      # 1 day
        self.cache_static_assets()    # 1 year
        self.cache_videos(604800)     # 1 week
        
        # Image optimizations
        self.thumbnail_generation(True)
        self.image_optimization(True)
        
        # Enable monitoring for performance insights
        self.monitoring(True)
        
        # Add performance labels
        self.labels({
            "optimization": "performance",
            "caching": "aggressive",
            "cdn": "enabled",
            "compression": "enabled"
        })
        
        print("   ├─ 💾 Set storage class to STANDARD")
        print("   ├─ 🌍 Enabled CDN")
        print("   ├─ 🗜️  Enabled compression")
        print("   ├─ 📦 Configured caching rules")
        print("   ├─ 🖼️  Enabled image optimizations")
        print("   ├─ 📊 Enabled monitoring")
        print("   └─ 🏷️  Added performance optimization labels")
        
        return self

    def _optimize_for_security(self):
        """Optimize configuration for security"""
        print("🏗️  Applying Cross-Cloud Magic: Security Optimization")
        
        # Apply strict security configuration
        self.strict_security_rules()
        self.authenticated_read(True)
        self.public_access(False)
        self.public_read(False)
        self.uniform_bucket_level_access(True)
        
        # Disable CORS for maximum security
        self.cors_disable()
        
        # Enable versioning for recovery
        self.versioning(True)
        
        # Enable comprehensive monitoring
        self.monitoring(True)
        self.logging(True)
        
        # Restrict file types
        self.allowed_file_types(["image/*", "application/pdf"])
        self.max_upload_size_mb(50)
        
        # Add security labels
        self.labels({
            "optimization": "security",
            "security_level": "maximum",
            "access_control": "strict",
            "monitoring": "enabled"
        })
        
        print("   ├─ 🔒 Applied strict security rules")
        print("   ├─ 🚫 Disabled public access")
        print("   ├─ 🛡️  Enabled uniform bucket-level access")
        print("   ├─ 🌍 Disabled CORS")
        print("   ├─ 🔄 Enabled versioning")
        print("   ├─ 📊 Enabled comprehensive monitoring")
        print("   ├─ 📄 Restricted file types")
        print("   └─ 🏷️  Added security optimization labels")
        
        return self

    def _optimize_for_user_experience(self):
        """Optimize configuration for user experience"""
        print("🏗️  Applying Cross-Cloud Magic: User Experience Optimization")
        
        # Balance between performance and features
        self.storage_class("STANDARD")
        self.cdn(True)
        self.compression(True)
        
        # UX-friendly configurations
        self.cache_images(3600)       # 1 hour for faster updates
        self.cache_static_assets(86400)  # 1 day
        
        # Enable user-friendly features
        self.thumbnail_generation(True)
        self.image_optimization(True)
        self.cors_allow_all()  # For web apps
        
        # Generous upload limits
        self.max_upload_size_mb(100)
        self.allow_images()
        self.allow_videos()
        self.allow_documents()
        
        # Enable monitoring for UX insights
        self.monitoring(True)
        
        # Add UX labels
        self.labels({
            "optimization": "user_experience",
            "ux_focused": "true",
            "features": "full",
            "cors": "enabled"
        })
        
        print("   ├─ 💾 Set storage class to STANDARD")
        print("   ├─ 🌍 Enabled CDN")
        print("   ├─ 🗜️  Enabled compression")
        print("   ├─ 📦 Balanced caching strategy")
        print("   ├─ 🖼️  Enabled image features")
        print("   ├─ 🌍 Enabled CORS for web apps")
        print("   ├─ 📤 Generous upload limits")
        print("   ├─ 📊 Enabled monitoring")
        print("   └─ 🏷️  Added UX optimization labels")
        
        return self

    def _create_new_bucket(self) -> Dict[str, Any]:
        """Create new Firebase Storage bucket"""
        try:
            bucket_name = self.get_bucket_name()
            
            print(f"   📁 Bucket: gs://{bucket_name}")
            print(f"   📋 Firebase Project: {self.firebase_project_id}")
            print(f"   📍 Location: {self.location}")
            print(f"   💾 Storage Class: {self.storage_class}")
            
            # Create Firebase Storage configuration
            storage_config = self._create_storage_config()
            
            # Write storage rules if configured
            if self.has_security_rules():
                rules_content = self._get_security_rules_content()
                with open("storage.rules", 'w') as f:
                    f.write(rules_content)
                print(f"   📄 Created storage.rules")
            
            # Update or create firebase.json
            firebase_config = self._create_firebase_config()
            
            # Read existing firebase.json if it exists
            existing_config = {}
            if os.path.exists("firebase.json"):
                try:
                    with open("firebase.json", 'r') as f:
                        existing_config = json.load(f)
                except json.JSONDecodeError:
                    existing_config = {}
            
            # Merge storage config with existing config
            existing_config.update(firebase_config)
            
            with open("firebase.json", 'w') as f:
                json.dump(existing_config, f, indent=2)
            
            print(f"   📄 Updated firebase.json")
            
            # Show configured features
            features = []
            if self.has_security_rules():
                features.append("Security rules")
            if self.cors_enabled:
                features.append("CORS")
            if self.has_lifecycle_rules():
                features.append("Lifecycle rules")
            if self.versioning_enabled:
                features.append("Versioning")
            if self.cdn_enabled:
                features.append("CDN")
            if self.compression_enabled:
                features.append("Compression")
            
            if features:
                print(f"   🚀 Features: {', '.join(features)}")
            
            console_url = f"https://console.firebase.google.com/project/{self.firebase_project_id}/storage/"
            print(f"✅ Firebase Storage configured successfully!")
            print(f"🚀 Deploy with: firebase deploy --only storage")
            print(f"🌐 Console: {console_url}")
            
            return self._get_storage_info()

        except Exception as e:
            print(f"❌ Failed to create Firebase Storage: {str(e)}")
            raise

    def _update_existing_bucket(self, existing_state: Dict[str, Any]):
        """Update existing Firebase Storage bucket"""
        print(f"   🔄 Updating existing configuration")
        # For Firebase Storage, we typically recreate the config
        return self._create_new_bucket()

    def _create_storage_config(self) -> Dict[str, Any]:
        """Create storage configuration for firebase.json"""
        storage_config = {}
        
        # Add security rules if configured
        if self.has_security_rules():
            storage_config["rules"] = "storage.rules"
        
        return storage_config

    def _create_firebase_config(self) -> Dict[str, Any]:
        """Create firebase.json configuration for storage"""
        config = {}
        
        storage_config = self._create_storage_config()
        if storage_config:
            config["storage"] = storage_config
        
        return config

    def _get_security_rules_content(self) -> str:
        """Get security rules content"""
        if self.security_rules_content:
            return self.security_rules_content
        elif self.security_rules_file and os.path.exists(self.security_rules_file):
            with open(self.security_rules_file, 'r') as f:
                return f.read()
        else:
            # Default security rules
            return """rules_version = '2';
service firebase.storage {
  match /b/{bucket}/o {
    match /{allPaths=**} {
      allow read, write: if request.auth != null;
    }
  }
}"""

    def _get_storage_info(self) -> Dict[str, Any]:
        """Get storage information"""
        try:
            bucket_name = self.get_bucket_name()
            
            return {
                'success': True,
                'storage_name': self.storage_name,
                'bucket_name': bucket_name,
                'firebase_project_id': self.firebase_project_id,
                'storage_description': self.storage_description,
                'storage_type': self._get_storage_type_from_config(),
                'location': self.location,
                'storage_class': self.storage_class,
                'public_access': self.public_access,
                'public_read': self.public_read,
                'authenticated_read': self.authenticated_read,
                'has_security_rules': self.has_security_rules(),
                'cors_enabled': self.cors_enabled,
                'cors_origins': self.cors_origins,
                'lifecycle_rule_count': len(self.lifecycle_rules),
                'versioning_enabled': self.versioning_enabled,
                'cdn_enabled': self.cdn_enabled,
                'compression_enabled': self.compression_enabled,
                'max_upload_size': self.max_upload_size,
                'allowed_file_types': self.allowed_file_types,
                'thumbnail_generation': self.thumbnail_generation,
                'has_caching_configured': self.has_caching_configured(),
                'has_monitoring_enabled': self.has_monitoring_enabled(),
                'notification_count': len(self.notifications),
                'labels': self.storage_labels,
                'estimated_monthly_cost': f"${self._estimate_firebase_storage_cost():.2f}",
                'bucket_url': f"gs://{bucket_name}",
                'console_url': f"https://console.firebase.google.com/project/{self.firebase_project_id}/storage/"
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}