import os
from typing import Dict, Any, Optional, List, Union
from ..base_resource import BaseGcpResource
from ...googlecloud_managers.storage.bucket_manager import BucketManager, BucketConfig
from ...googlecloud_managers.status_reporter import GcpStatusReporter


class Storage(BaseGcpResource):
    """Rails-like Cloud Storage bucket orchestrator - file storage made simple"""

    def __init__(self, bucket_name: str):
        self.config = BucketConfig(name=bucket_name)
        self.status_reporter = GcpStatusReporter()
        self._files_to_upload = []
        super().__init__(bucket_name)

    def _initialize_managers(self):
        """Initialize Storage specific managers"""
        self.bucket_manager = None

    def _post_authentication_setup(self):
        """Setup managers after authentication"""
        self.bucket_manager = BucketManager(self.gcp_client)

    def location(self, location: str) -> 'Storage':
        """Set bucket location (e.g., 'US', 'EU', 'us-central1')"""
        self.config.location = location
        return self

    def storage_class(self, storage_class: str) -> 'Storage':
        """Set storage class ('STANDARD', 'NEARLINE', 'COLDLINE', 'ARCHIVE')"""
        self.config.storage_class = storage_class
        return self

    def public(self, enabled: bool = True) -> 'Storage':
        """Configure public access (Rails convention: secure by default)"""
        if enabled:
            self.config.public_access_prevention = "inherited"
            print("⚠️  Enabling public access - objects can be made publicly readable")
        else:
            self.config.public_access_prevention = "enforced"
        return self

    def versioning(self, enabled: bool = True) -> 'Storage':
        """Enable/disable object versioning"""
        self.config.versioning_enabled = enabled
        return self

    def lifecycle(self, bucket_type: str = "general") -> 'Storage':
        """
        Apply smart lifecycle rules based on bucket type.

        Types: 'general', 'logs', 'backup', 'temp'
        """
        if not self.bucket_manager:
            # Store for later application
            self._lifecycle_type = bucket_type
        else:
            rules = self.bucket_manager.get_smart_lifecycle_rules(bucket_type)
            self.config.lifecycle_rules = rules
            print(f"📋 Applied {bucket_type} lifecycle rules ({len(rules)} rules)")
        return self

    def cors(self, cors_type: str = "web") -> 'Storage':
        """
        Apply smart CORS rules based on use case.

        Types: 'web', 'api', 'cdn'
        """
        if not self.bucket_manager:
            # Store for later application
            self._cors_type = cors_type
        else:
            rules = self.bucket_manager.get_smart_cors_rules(cors_type)
            self.config.cors_rules = rules
            print(f"🌐 Applied {cors_type} CORS rules ({len(rules)} rules)")
        return self

    def labels(self, labels: Dict[str, str]) -> 'Storage':
        """Add labels for organization and billing"""
        self.config.labels = labels
        return self

    def retention(self, days: int) -> 'Storage':
        """Set retention policy (objects cannot be deleted for specified days)"""
        self.config.retention_period = days * 24 * 60 * 60  # Convert to seconds
        return self

    def upload(self, source_path: str, destination_name: str = None, **kwargs) -> 'Storage':
        """
        Queue file for upload (Rails-like chaining).

        Args:
            source_path: Local file path
            destination_name: Name in bucket (defaults to filename)
            **kwargs: Additional options (content_type, metadata, etc.)
        """
        self._files_to_upload.append({
            'source_path': source_path,
            'destination_name': destination_name,
            'options': kwargs
        })
        return self

    def upload_directory(self, source_dir: str, prefix: str = "", **kwargs) -> 'Storage':
        """
        Queue entire directory for upload (Rails convenience).

        Args:
            source_dir: Local directory path
            prefix: Prefix for objects in bucket
            **kwargs: Additional options
        """
        if not os.path.exists(source_dir):
            raise FileNotFoundError(f"Source directory not found: {source_dir}")

        for root, dirs, files in os.walk(source_dir):
            for file in files:
                local_path = os.path.join(root, file)
                # Create relative path from source directory
                rel_path = os.path.relpath(local_path, source_dir)
                # Combine with prefix
                bucket_path = os.path.join(prefix, rel_path).replace('\\', '/') if prefix else rel_path.replace('\\', '/')

                self._files_to_upload.append({
                    'source_path': local_path,
                    'destination_name': bucket_path,
                    'options': kwargs
                })

        print(f"📁 Queued directory for upload: {source_dir} ({len([f for f in self._files_to_upload if f['source_path'].startswith(source_dir)])} files)")
        return self

    def website(self, index_page: str = "index.html", error_page: str = "404.html") -> 'Storage':
        """
        Configure bucket for static website hosting.

        Args:
            index_page: Main index document
            error_page: Error page for 404s
        """
        # Enable public access for website
        self.public(True)

        # Store website config for later application
        self._website_config = {
            'index_page': index_page,
            'error_page': error_page
        }
        print(f"🌐 Configured for static website hosting")
        print(f"   📄 Index: {index_page}")
        print(f"   ❌ Error page: {error_page}")
        return self

    def backup_bucket(self) -> 'Storage':
        """Configure bucket optimized for backups (Rails convention)"""
        return (self.storage_class("COLDLINE")
                .lifecycle("backup")
                .versioning(True)
                .public(False))

    def temp_bucket(self) -> 'Storage':
        """Configure bucket for temporary files (Rails convention)"""
        return (self.storage_class("STANDARD")
                .lifecycle("temp")
                .public(False))

    def logs_bucket(self) -> 'Storage':
        """Configure bucket optimized for logs (Rails convention)"""
        return (self.storage_class("STANDARD")
                .lifecycle("logs")
                .public(False))

    def cdn_bucket(self) -> 'Storage':
        """Configure bucket for CDN usage (Rails convention)"""
        return (self.storage_class("STANDARD")
                .cors("cdn")
                .public(True))

    def preview(self) -> Dict[str, Any]:
        """Preview what will be created, updated, or removed"""
        self._ensure_authenticated()

        # Discover existing buckets to determine what will happen
        existing_buckets = self._discover_existing_buckets()
        
        # Determine what will happen
        bucket_exists = self.config.name in existing_buckets
        to_create = [] if bucket_exists else [self.config.name]
        to_keep = [self.config.name] if bucket_exists else []
        to_remove = [name for name in existing_buckets.keys() if name != self.config.name]

        # Print simple header without formatting
        print(f"🔍 Cloud Storage Bucket Preview")

        # Show infrastructure changes (only actionable changes)
        changes_needed = to_create or to_remove
        
        if changes_needed:
            print(f"📋 Infrastructure Changes:")
            
            if to_create:
                print(f"🆕 BUCKETS to CREATE:  {', '.join(to_create)}")
                # Show details about bucket being created
                print(f"   ╭─ 🪣 {self.config.name}")
                print(f"   ├─ 📍 Location: {self.config.location}")
                print(f"   ├─ 🏷️  Class: {self.config.storage_class}")
                print(f"   ├─ 🔒 Access: {'Public' if self.config.public_access_prevention == 'inherited' else 'Private'}")
                print(f"   ├─ 📦 Versioning: {'Enabled' if self.config.versioning_enabled else 'Disabled'}")
                if self.config.lifecycle_rules:
                    print(f"   ├─ 📋 Lifecycle: {len(self.config.lifecycle_rules)} rules")
                if self.config.cors_rules:
                    print(f"   ├─ 🌐 CORS: {len(self.config.cors_rules)} rules")
                if self._files_to_upload:
                    print(f"   ├─ 📤 Files: {len(self._files_to_upload)} to upload")
                print(f"   ╰─ 🏷️  Labels: {len(self.config.labels or {})}")
                print()
                
            if to_remove:
                print(f"🗑️  BUCKETS to REMOVE:")
                # Show details about buckets being removed
                for bucket_name in to_remove:
                    bucket_info = existing_buckets.get(bucket_name)
                    if bucket_info:
                        location = bucket_info.get('location', 'unknown')
                        storage_class = bucket_info.get('storage_class', 'unknown')
                        created = bucket_info.get('created', 'unknown')
                        
                        # Pretty format with box drawing
                        print(f"   ╭─ 🪣 {bucket_name}")
                        print(f"   ├─ 📍 Location: {location}")
                        print(f"   ├─ 🏷️  Class: {storage_class}")
                        print(f"   ├─ 📅 Created: {created}")
                        print(f"   ╰─ ⚠️  Will delete all objects in bucket")
                        print()
        else:
            print(f"✨ No changes needed - infrastructure matches configuration")

        # Show unchanged buckets summary
        if to_keep:
            print(f"📋 Unchanged: {len(to_keep)} bucket(s) remain the same")

        return {
            "name": self.config.name,
            "location": self.config.location,
            "to_create": to_create,
            "to_keep": to_keep,
            "to_remove": to_remove,
            "existing_buckets": existing_buckets,
            "storage_class": self.config.storage_class,
            "versioning_enabled": self.config.versioning_enabled,
            "public_access_prevention": self.config.public_access_prevention,
            "lifecycle_rules": len(self.config.lifecycle_rules),
            "cors_rules": len(self.config.cors_rules),
            "labels": self.config.labels,
            "files_to_upload": len(self._files_to_upload)
        }

    def create(self) -> Dict[str, Any]:
        """Create/update Cloud Storage bucket and remove any that are no longer needed"""
        self._ensure_authenticated()

        # Discover existing buckets to determine what changes are needed
        existing_buckets = self._discover_existing_buckets()
        bucket_exists = self.config.name in existing_buckets
        to_create = [] if bucket_exists else [self.config.name]
        to_remove = [name for name in existing_buckets.keys() if name != self.config.name]

        # Show infrastructure changes
        print(f"\n🔍 Cloud Storage Bucket")

        changes_needed = to_create or to_remove
        if changes_needed:
            print(f"📋 Infrastructure Changes:")
            
            if to_create:
                print(f"🆕 BUCKETS to CREATE:  {', '.join(to_create)}")
                
            if to_remove:
                print(f"🗑️  BUCKETS to REMOVE:")
                # Show details about buckets being removed
                for bucket_name in to_remove:
                    bucket_info = existing_buckets.get(bucket_name)
                    if bucket_info:
                        location = bucket_info.get('location', 'unknown')
                        storage_class = bucket_info.get('storage_class', 'unknown')
                        created = bucket_info.get('created', 'unknown')
                        
                        # Pretty format with box drawing
                        print(f"   ╭─ 🪣 {bucket_name}")
                        print(f"   ├─ 📍 Location: {location}")
                        print(f"   ├─ 🏷️  Class: {storage_class}")
                        print(f"   ├─ 📅 Created: {created}")
                        print(f"   ╰─ ⚠️  Will delete all objects in bucket")
                        print()
        else:
            print(f"✨ No changes needed - infrastructure matches configuration")

        # Apply deferred configurations
        if hasattr(self, '_lifecycle_type'):
            rules = self.bucket_manager.get_smart_lifecycle_rules(self._lifecycle_type)
            self.config.lifecycle_rules = rules

        if hasattr(self, '_cors_type'):
            rules = self.bucket_manager.get_smart_cors_rules(self._cors_type)
            self.config.cors_rules = rules

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

            # Create/update the bucket that is in the configuration
            if bucket_exists:
                print(f"🔄 Updating bucket: {self.config.name}")
            else:
                print(f"🆕 Creating bucket: {self.config.name}")

            # Create the bucket
            bucket_result = self.bucket_manager.create_bucket(self.config)
            print(f"✅ Bucket ready: {bucket_result['name']}")

            # Configure website if requested
            if hasattr(self, '_website_config'):
                self._configure_website(bucket_result['name'])

            # Upload files if any were queued
            uploaded_files = []
            if self._files_to_upload:
                print(f"\n📤 Uploading {len(self._files_to_upload)} files...")
                for file_info in self._files_to_upload:
                    try:
                        upload_result = self.bucket_manager.upload_file(
                            bucket_result['name'],
                            file_info['source_path'],
                            file_info['destination_name'],
                            **file_info['options']
                        )
                        uploaded_files.append(upload_result)
                    except Exception as e:
                        print(f"⚠️  Failed to upload {file_info['source_path']}: {e}")

            # Add upload results to bucket result
            bucket_result['uploaded_files'] = uploaded_files
            bucket_result['files_uploaded'] = len(uploaded_files)

            # Add change tracking to result
            bucket_result["changes"] = {
                "created": to_create,
                "removed": to_remove,
                "updated": [self.config.name] if bucket_exists else []
            }

            return bucket_result

        except Exception as e:
            print(f"❌ Failed to manage Cloud Storage bucket: {str(e)}")
            raise

    def _discover_existing_buckets(self) -> Dict[str, Any]:
        """Discover existing Cloud Storage buckets that might be related to this configuration"""
        try:
            existing_buckets = {}
            
            # Get the storage client through bucket manager
            client = self.bucket_manager.storage_client
            
            # List all buckets in the current project
            buckets = client.list_buckets()
            
            # Filter buckets that might be related to this configuration
            # We look for buckets that either:
            # 1. Have the exact same name as our bucket
            # 2. Match our naming pattern (same base name with different suffixes)
            # 3. Have InfraDSL-related labels
            
            base_name = self.name.lower().replace('_', '-')
            
            for bucket in buckets:
                bucket_name = bucket.name
                
                # Check if this bucket might be related
                is_related = False
                
                # 1. Exact match
                if bucket_name == self.config.name:
                    is_related = True
                
                # 2. Naming pattern match (same base name)
                elif base_name in bucket_name.lower():
                    is_related = True
                
                # 3. Check labels for InfraDSL managed buckets
                try:
                    labels = bucket.labels or {}
                    if any(label_key.lower() in ['infradsl', 'managedby'] for label_key in labels.keys()):
                        is_related = True
                except Exception:
                    # Skip buckets we can't get labels for
                    pass
                
                if is_related:
                    # Parse creation date
                    created = 'unknown'
                    if bucket.time_created:
                        try:
                            created = bucket.time_created.strftime('%Y-%m-%d %H:%M')
                        except Exception:
                            pass
                    
                    existing_buckets[bucket_name] = {
                        'bucket_name': bucket_name,
                        'location': bucket.location or 'unknown',
                        'storage_class': bucket.storage_class or 'unknown',
                        'created': created,
                        'versioning_enabled': getattr(bucket, 'versioning_enabled', False),
                        'public_access_prevention': getattr(bucket.iam_configuration, 'public_access_prevention', 'unknown'),
                        'labels': dict(bucket.labels) if bucket.labels else {}
                    }
            
            return existing_buckets
            
        except Exception as e:
            print(f"   ⚠️  Warning: Failed to discover existing Cloud Storage buckets: {str(e)}")
            return {}

    def destroy(self) -> Dict[str, Any]:
        """Destroy the bucket and all its contents"""
        self._ensure_authenticated()

        print(f"\n🗑️  DESTROY OPERATION")
        print("=" * 50)
        print(f"📋 Resources to be destroyed:")
        print(f"   🪣 Bucket: {self.config.name}")
        print(f"   📍 Location: {self.config.location}")
        print("=" * 50)
        print("⚠️  WARNING: This will permanently delete the bucket and ALL its contents!")
        print("=" * 50)

        try:
            # Delete bucket with force=True to delete all objects
            success = self.bucket_manager.delete_bucket(self.config.name, force=True)

            result = {
                "bucket_name": self.config.name,
                "destroyed": success
            }

            if success:
                print(f"✅ Bucket destroyed: {self.config.name}")
            else:
                print(f"⚠️  Failed to destroy bucket: {self.config.name}")

            return result

        except Exception as e:
            print(f"❌ Failed to destroy bucket: {str(e)}")
            return {"bucket_name": self.config.name, "destroyed": False, "error": str(e)}

    def _configure_website(self, bucket_name: str):
        """Configure bucket for static website hosting"""
        try:
            # This would typically involve setting up website configuration
            # For now, we'll just make the bucket public and suggest next steps
            print(f"🌐 Configuring website hosting...")
            print(f"   💡 Next steps:")
            print(f"   1. Make your index and error pages public")
            print(f"   2. Configure custom domain (if needed)")
            print(f"   3. Set up CDN for better performance")
        except Exception as e:
            print(f"⚠️  Website configuration warning: {e}")

    # Utility methods for direct operations (Rails-like convenience)
    def upload_file_direct(self, source_path: str, destination_name: str = None, **kwargs) -> Dict[str, Any]:
        """Upload a file directly (without chaining)"""
        self._ensure_authenticated()
        return self.bucket_manager.upload_file(self.config.name, source_path, destination_name, **kwargs)

    def download_file_direct(self, object_name: str, destination_path: str) -> Dict[str, Any]:
        """Download a file directly (without chaining)"""
        self._ensure_authenticated()
        return self.bucket_manager.download_file(self.config.name, object_name, destination_path)

    def list_files(self, prefix: str = None) -> List[Dict[str, Any]]:
        """List files in bucket"""
        self._ensure_authenticated()
        return self.bucket_manager.list_objects(self.config.name, prefix)

    def make_file_public(self, object_name: str) -> Dict[str, Any]:
        """Make a specific file publicly accessible"""
        self._ensure_authenticated()
        return self.bucket_manager.make_public(self.config.name, object_name)

    def make_bucket_public(self) -> Dict[str, Any]:
        """Make entire bucket publicly accessible"""
        self._ensure_authenticated()
        return self.bucket_manager.make_public(self.config.name)

    def get_info(self) -> Dict[str, Any]:
        """Get bucket information"""
        self._ensure_authenticated()
        return self.bucket_manager.get_bucket_info(self.config.name)

    def _fetch_current_cloud_state(self) -> Dict[str, Any]:
        """Fetch current state of the bucket from Google Cloud"""
        self._ensure_authenticated()
        
        try:
            # Get bucket info if it exists
            bucket_info = self.bucket_manager.get_bucket_info(self.config.name)
            
            if bucket_info.get("exists", False):
                return {
                    "exists": True,
                    "bucket_name": self.config.name,
                    "location": bucket_info.get("location"),
                    "storage_class": bucket_info.get("storage_class"),
                    "versioning_enabled": bucket_info.get("versioning_enabled", False),
                    "public_access_prevention": bucket_info.get("public_access_prevention"),
                    "labels": bucket_info.get("labels", {}),
                    "creation_time": bucket_info.get("creation_time"),
                    "lifecycle_rules": bucket_info.get("lifecycle_rules", []),
                    "cors_rules": bucket_info.get("cors_rules", [])
                }
            else:
                return {
                    "exists": False,
                    "bucket_name": self.config.name
                }
                
        except Exception as e:
            print(f"⚠️  Warning: Failed to fetch bucket state: {str(e)}")
            return {
                "exists": False,
                "bucket_name": self.config.name,
                "error": str(e)
            }
