"""
GCP Cloud Storage Configuration Mixin

Chainable configuration methods for Google Cloud Storage buckets.
Provides Rails-like method chaining for fluent bucket configuration.
"""

from typing import Dict, Any, List, Optional
import os


class StorageConfigurationMixin:
    """
    Mixin for Cloud Storage bucket configuration methods.
    
    This mixin provides chainable configuration methods for:
    - Bucket location and storage class
    - Access control and security settings
    - Versioning and lifecycle management
    - CORS and website configuration
    - File upload queueing
    """
    
    def bucket(self, name: str):
        """Set bucket name (Rails-like method chaining)"""
        self.bucket_name = name
        self.bucket_url = f"gs://{name}"
        return self
        
    def region(self, location: str):
        """Set bucket location (e.g., 'US', 'EU', 'us-central1')"""
        if not self._is_valid_location(location):
            print(f"⚠️  Warning: Unusual location '{location}' - verify this is correct")
        self.location = location
        return self
        
    def storage(self, storage_class: str):
        """Set storage class ('STANDARD', 'NEARLINE', 'COLDLINE', 'ARCHIVE')"""
        if not self._is_valid_storage_class(storage_class):
            raise ValueError(f"Invalid storage class: {storage_class}")
        self.storage_class = storage_class
        return self
        
    def public(self, enabled: bool = True):
        """Configure public access (Rails convention: secure by default)"""
        if enabled:
            self.public_access_prevention = "inherited"
            print("⚠️  Enabling public access - objects can be made publicly readable")
        else:
            self.public_access_prevention = "enforced"
        return self
        
    def private(self):
        """Ensure bucket is private (Rails convention)"""
        return self.public(False)
        
    def versioning(self, enabled: bool = True):
        """Enable/disable object versioning"""
        self.versioning_enabled = enabled
        return self
        
    def lifecycle(self, days: int, action: str = "delete", target_class: str = None):
        """Add lifecycle rule for automated storage management
        
        Args:
            days: Number of days after which to apply the action
            action: Action to take ('delete', 'transition')
            target_class: Target storage class for transition
        """
        rule = {
            "id": f"rule-{len(self.lifecycle_rules) + 1}",
            "status": "Enabled",
            "filter": {},
            "transitions": [],
            "expiration": None
        }
        
        if action == "delete":
            rule["expiration"] = {"days": days}
        elif action == "transition" and target_class:
            rule["transitions"].append({
                "days": days,
                "storage_class": target_class
            })
        
        self.lifecycle_rules.append(rule)
        return self
        
    def cors(self, origins: List[str] = None, methods: List[str] = None, headers: List[str] = None):
        """Configure CORS rules for web access"""
        if origins is None:
            origins = ["*"]
        if methods is None:
            methods = ["GET", "POST", "PUT", "DELETE", "HEAD"]
        if headers is None:
            headers = ["*"]
            
        cors_rule = {
            "origin": origins,
            "method": methods,
            "responseHeader": headers,
            "maxAgeSeconds": 3600
        }
        
        self.cors_rules.append(cors_rule)
        return self
        
    def labels(self, labels: Dict[str, str]):
        """Add labels for organization and billing"""
        self.bucket_labels.update(labels)
        return self
        
    def retention(self, days: int):
        """Set retention policy (objects cannot be deleted for specified days)"""
        self.retention_period = days * 24 * 60 * 60  # Convert to seconds
        return self
        
    def upload_file(self, source_path: str, destination_name: str = None, **kwargs):
        """Queue file for upload (Rails-like chaining)"""
        if not os.path.exists(source_path):
            raise FileNotFoundError(f"Source file not found: {source_path}")
            
        if destination_name is None:
            destination_name = os.path.basename(source_path)
            
        self._files_to_upload.append({
            'source_path': source_path,
            'destination_name': destination_name,
            'options': kwargs
        })
        return self
        
    def upload_directory(self, source_dir: str, prefix: str = "", **kwargs):
        """Queue entire directory for upload (Rails convenience)"""
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
        
    def static_website(self, index_page: str = "index.html", error_page: str = "404.html"):
        """Configure bucket for static website hosting"""
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
        
    def cdn(self, enabled: bool = True):
        """Enable CDN integration (for Cross-Cloud Magic)"""
        self._cdn_enabled = enabled
        if enabled:
            print("🚀 CDN integration enabled")
        return self
        
    def backup_retention(self, days: int):
        """Set backup retention period (Cross-Cloud Magic)"""
        self._backup_retention_days = days
        return self.retention(days)
        
    # Rails-like convenience methods
    def web_bucket(self):
        """Configure bucket for web applications (Rails convention)"""
        return (self.storage("STANDARD")
                .cors()
                .public(True)
                .versioning(False))
        
    def backup_bucket(self):
        """Configure bucket optimized for backups (Rails convention)"""
        return (self.storage("COLDLINE")
                .lifecycle(30, "transition", "ARCHIVE")
                .versioning(True)
                .private())
        
    def temp_bucket(self):
        """Configure bucket for temporary files (Rails convention)"""
        return (self.storage("STANDARD")
                .lifecycle(7, "delete")
                .private())
        
    def logs_bucket(self):
        """Configure bucket optimized for logs (Rails convention)"""
        return (self.storage("STANDARD")
                .lifecycle(90, "transition", "NEARLINE")
                .lifecycle(365, "transition", "ARCHIVE")
                .private())
        
    def cdn_bucket(self):
        """Configure bucket for CDN usage (Rails convention)"""
        return (self.storage("STANDARD")
                .cors()
                .public(True)
                .cdn(True))