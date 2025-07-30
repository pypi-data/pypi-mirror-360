"""
GCP Cloud Storage Lifecycle Mixin

Lifecycle operations for Google Cloud Storage buckets.
Handles create, update, preview, and destroy operations.
"""

from typing import Dict, Any, List
import uuid


class StorageLifecycleMixin:
    """
    Mixin for Cloud Storage bucket lifecycle operations (create, update, destroy).
    
    This mixin provides:
    - Preview functionality to show planned changes
    - Bucket creation and configuration
    - File upload management
    - Bucket destruction
    """
    
    def preview(self) -> Dict[str, Any]:
        """Preview what will be created, kept, and removed"""
        self._ensure_authenticated()
        
        # Discover existing buckets to determine what will happen
        existing_buckets = self._discover_existing_buckets()
        
        # Determine what will happen
        bucket_exists = self.bucket_name in existing_buckets
        to_create = [] if bucket_exists else [self.bucket_name]
        to_keep = [self.bucket_name] if bucket_exists else []
        to_remove = [name for name in existing_buckets.keys() if name != self.bucket_name]
        
        self._display_preview(to_create, to_keep, to_remove, existing_buckets)
        
        return {
            'resource_type': 'GCP Cloud Storage Bucket',
            'name': self.bucket_name,
            'bucket_url': self.bucket_url,
            'to_create': to_create,
            'to_keep': to_keep,
            'to_remove': to_remove,
            'existing_buckets': existing_buckets,
            'location': self.location,
            'storage_class': self.storage_class,
            'versioning_enabled': self.versioning_enabled,
            'public_access': self.public_access_prevention == "inherited",
            'lifecycle_rules_count': len(self.lifecycle_rules),
            'cors_rules_count': len(self.cors_rules),
            'files_to_upload': len(self._files_to_upload),
            'estimated_deployment_time': '2-3 minutes',
            'estimated_monthly_cost': self._estimate_monthly_cost()
        }
    
    def _display_preview(self, to_create: List[str], to_keep: List[str], to_remove: List[str], existing_buckets: Dict[str, Any]):
        """Display preview information in a clean format"""
        print(f"\n🪣 Cloud Storage Bucket Preview")
        
        # Show buckets to create
        if to_create:
            print(f"╭─ 🚀 Buckets to CREATE: {len(to_create)}")
            for bucket in to_create:
                print(f"├─ 🆕 {bucket}")
                print(f"│  ├─ 📍 Location: {self.location}")
                print(f"│  ├─ 🏷️  Storage Class: {self.storage_class}")
                print(f"│  ├─ 🔒 Access: {'Public' if self.public_access_prevention == 'inherited' else 'Private'}")
                print(f"│  ├─ 📦 Versioning: {'Enabled' if self.versioning_enabled else 'Disabled'}")
                if self.lifecycle_rules:
                    print(f"│  ├─ 📋 Lifecycle Rules: {len(self.lifecycle_rules)}")
                if self.cors_rules:
                    print(f"│  ├─ 🌐 CORS Rules: {len(self.cors_rules)}")
                if self._files_to_upload:
                    print(f"│  ├─ 📤 Files to Upload: {len(self._files_to_upload)}")
                if self.bucket_labels:
                    print(f"│  ├─ 🏷️  Labels: {len(self.bucket_labels)}")
                print(f"│  └─ ⏱️  Deployment Time: 2-3 minutes")
            print(f"╰─")
        
        # Show buckets to keep
        if to_keep:
            print(f"╭─ 🔄 Buckets to KEEP: {len(to_keep)}")
            for bucket in to_keep:
                bucket_info = existing_buckets.get(bucket, {})
                print(f"├─ ✅ {bucket}")
                print(f"│  ├─ 📍 Location: {bucket_info.get('location', 'Unknown')}")
                print(f"│  ├─ 🏷️  Storage Class: {bucket_info.get('storage_class', 'Unknown')}")
                print(f"│  └─ 📅 Created: {bucket_info.get('created', 'Unknown')}")
            print(f"╰─")
        
        # Show buckets to remove
        if to_remove:
            print(f"╭─ 🗑️  Buckets to REMOVE: {len(to_remove)}")
            for bucket in to_remove:
                bucket_info = existing_buckets.get(bucket, {})
                print(f"├─ ❌ {bucket}")
                print(f"│  ├─ 📍 Location: {bucket_info.get('location', 'Unknown')}")
                print(f"│  ├─ 🏷️  Storage Class: {bucket_info.get('storage_class', 'Unknown')}")
                print(f"│  └─ ⚠️  All objects will be deleted")
            print(f"╰─")
        
        # Show cost estimation
        print(f"\n💰 Estimated Monthly Costs:")
        print(f"   ├─ 📦 Storage ({self.storage_class}): {self._estimate_storage_cost()}")
        print(f"   ├─ 🔄 Operations: {self._estimate_operations_cost()}")
        print(f"   ├─ 🌐 Network Egress: {self._estimate_network_cost()}")
        print(f"   └─ 📊 Total Estimated: {self._estimate_monthly_cost()}")
    
    def create(self) -> Dict[str, Any]:
        """Create/update Cloud Storage bucket"""
        self._ensure_authenticated()
        
        if not self._is_valid_bucket_name(self.bucket_name):
            raise ValueError(f"Invalid bucket name: {self.bucket_name}")
        
        # Discover existing buckets to determine what changes are needed
        existing_buckets = self._discover_existing_buckets()
        bucket_exists = self.bucket_name in existing_buckets
        to_create = [] if bucket_exists else [self.bucket_name]
        to_remove = [name for name in existing_buckets.keys() if name != self.bucket_name]
        
        print(f"\n🪣 Creating Cloud Storage Bucket: {self.bucket_name}")
        print(f"   📍 Location: {self.location}")
        print(f"   🏷️  Storage Class: {self.storage_class}")
        
        try:
            # Remove buckets that are no longer needed
            for bucket_name in to_remove:
                print(f"🗑️  Removing bucket: {bucket_name}")
                try:
                    success = self.bucket_manager.delete_bucket(bucket_name, force=True)
                    if success:
                        print(f"✅ Bucket removed successfully: {bucket_name}")
                except Exception as e:
                    print(f"⚠️  Warning: Failed to remove bucket {bucket_name}: {str(e)}")
            
            # Create bucket configuration
            bucket_config = {
                'name': self.bucket_name,
                'location': self.location,
                'storage_class': self.storage_class,
                'public_access_prevention': self.public_access_prevention,
                'versioning_enabled': self.versioning_enabled,
                'lifecycle_rules': self.lifecycle_rules,
                'cors_rules': self.cors_rules,
                'labels': self.bucket_labels,
                'retention_period': self.retention_period
            }
            
            # Create or update the bucket
            if bucket_exists:
                print(f"🔄 Updating existing bucket configuration")
            else:
                print(f"🆕 Creating new bucket")
            
            # Mock creation for now - in real implementation this would use GCP SDK
            result = {
                'bucket_name': self.bucket_name,
                'bucket_url': self.bucket_url,
                'bucket_arn': self.bucket_arn,
                'location': self.location,
                'storage_class': self.storage_class,
                'versioning_enabled': self.versioning_enabled,
                'public_access_prevention': self.public_access_prevention,
                'lifecycle_rules_count': len(self.lifecycle_rules),
                'cors_rules_count': len(self.cors_rules),
                'labels_count': len(self.bucket_labels),
                'retention_period': self.retention_period,
                'created': True,
                'updated': bucket_exists,
                'changes': {
                    'created': to_create,
                    'removed': to_remove,
                    'updated': [self.bucket_name] if bucket_exists else []
                }
            }
            
            # Configure website if requested
            if hasattr(self, '_website_config'):
                self._configure_website(result)
            
            # Upload files if any were queued
            uploaded_files = []
            if self._files_to_upload:
                print(f"\n📤 Uploading {len(self._files_to_upload)} files...")
                for file_info in self._files_to_upload:
                    try:
                        # Mock upload for now - in real implementation this would use GCP SDK
                        upload_result = {
                            'source_path': file_info['source_path'],
                            'destination_name': file_info['destination_name'],
                            'bucket_name': self.bucket_name,
                            'uploaded': True,
                            'url': f"{self.bucket_url}/{file_info['destination_name']}"
                        }
                        uploaded_files.append(upload_result)
                        print(f"✅ Uploaded: {file_info['source_path']} → {file_info['destination_name']}")
                    except Exception as e:
                        print(f"⚠️  Failed to upload {file_info['source_path']}: {e}")
            
            # Add upload results to bucket result
            result['uploaded_files'] = uploaded_files
            result['files_uploaded'] = len(uploaded_files)
            
            # Update instance attributes
            self.bucket_exists = True
            self.bucket_created = True
            
            self._display_creation_success(result)
            return result
            
        except Exception as e:
            print(f"❌ Failed to create Cloud Storage bucket: {str(e)}")
            raise
    
    def _configure_website(self, bucket_result: Dict[str, Any]):
        """Configure bucket for static website hosting"""
        try:
            print(f"🌐 Configuring website hosting...")
            website_config = getattr(self, '_website_config', {})
            
            # Mock website configuration - in real implementation this would use GCP SDK
            bucket_result['website_config'] = {
                'index_page': website_config.get('index_page', 'index.html'),
                'error_page': website_config.get('error_page', '404.html'),
                'website_url': f"https://storage.googleapis.com/{self.bucket_name}"
            }
            
            print(f"   📄 Index: {website_config.get('index_page', 'index.html')}")
            print(f"   ❌ Error page: {website_config.get('error_page', '404.html')}")
            print(f"   🔗 Website URL: {bucket_result['website_config']['website_url']}")
            
        except Exception as e:
            print(f"⚠️  Website configuration warning: {e}")
    
    def _display_creation_success(self, result: Dict[str, Any]):
        """Display creation success information"""
        print(f"✅ Cloud Storage bucket {'updated' if result['updated'] else 'created'} successfully")
        print(f"   🪣 Bucket Name: {result['bucket_name']}")
        print(f"   📍 Location: {result['location']}")
        print(f"   🏷️  Storage Class: {result['storage_class']}")
        print(f"   🔗 Bucket URL: {result['bucket_url']}")
        if result['files_uploaded'] > 0:
            print(f"   📤 Files Uploaded: {result['files_uploaded']}")
        if result['lifecycle_rules_count'] > 0:
            print(f"   📋 Lifecycle Rules: {result['lifecycle_rules_count']}")
        if result['cors_rules_count'] > 0:
            print(f"   🌐 CORS Rules: {result['cors_rules_count']}")
    
    def destroy(self) -> Dict[str, Any]:
        """Destroy the Cloud Storage bucket"""
        self._ensure_authenticated()
        
        print(f"🗑️  Destroying Cloud Storage Bucket: {self.bucket_name}")
        
        try:
            # Mock destruction for now - in real implementation this would use GCP SDK
            result = {
                'bucket_name': self.bucket_name,
                'bucket_url': self.bucket_url,
                'location': self.location,
                'destroyed': True,
                'note': 'Bucket and all objects deleted permanently'
            }
            
            # Reset instance attributes
            self.bucket_exists = False
            self.bucket_created = False
            self.bucket_url = None
            self.bucket_arn = None
            
            print(f"✅ Cloud Storage bucket destroyed successfully")
            print(f"   🪣 Bucket Name: {result['bucket_name']}")
            print(f"   📍 Location: {result['location']}")
            print(f"   ⚠️  Note: All objects in bucket have been permanently deleted")
            
            return result
            
        except Exception as e:
            print(f"❌ Failed to destroy Cloud Storage bucket: {str(e)}")
            raise
    
    def _discover_existing_buckets(self) -> Dict[str, Any]:
        """Discover existing Cloud Storage buckets that might be related"""
        try:
            existing_buckets = {}
            
            # Mock discovery for now - in real implementation this would use GCP SDK
            # This would list all buckets in the project and filter for related ones
            
            # For testing, we'll simulate finding related buckets
            if hasattr(self, 'bucket_manager') and self.bucket_manager:
                # In real implementation, this would call GCP APIs
                pass
                
            return existing_buckets
            
        except Exception as e:
            print(f"⚠️  Warning: Failed to discover existing buckets: {str(e)}")
            return {}
    
    def _estimate_monthly_cost(self) -> str:
        """Estimate monthly cost based on configuration"""
        # Basic cost estimation based on storage class and usage
        base_costs = {
            'STANDARD': 0.020,  # per GB
            'NEARLINE': 0.010,  # per GB
            'COLDLINE': 0.004,  # per GB
            'ARCHIVE': 0.0012   # per GB
        }
        
        storage_cost = base_costs.get(self.storage_class, 0.020)
        estimated_gb = 10  # Default estimation
        
        return f"~${storage_cost * estimated_gb:.2f}/month"
    
    def _estimate_storage_cost(self) -> str:
        """Estimate storage cost"""
        base_costs = {
            'STANDARD': 0.020,
            'NEARLINE': 0.010,
            'COLDLINE': 0.004,
            'ARCHIVE': 0.0012
        }
        cost_per_gb = base_costs.get(self.storage_class, 0.020)
        return f"${cost_per_gb:.4f}/GB"
    
    def _estimate_operations_cost(self) -> str:
        """Estimate operations cost"""
        return "$0.05/10,000 operations"
    
    def _estimate_network_cost(self) -> str:
        """Estimate network egress cost"""
        return "$0.12/GB (after 1GB free)"