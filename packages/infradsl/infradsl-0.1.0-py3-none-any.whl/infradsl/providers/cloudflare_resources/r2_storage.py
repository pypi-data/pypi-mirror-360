"""
Cloudflare R2 Storage Resource

Rails-like interface for managing Cloudflare R2 S3-compatible object storage.
Provides chainable methods for easy bucket configuration and management.
"""

from typing import Dict, Any, Optional, List
from .base_resource import BaseCloudflareResource
from ..cloudflare_managers.r2_storage_manager import R2StorageManager


class R2Storage(BaseCloudflareResource):
    """
    Cloudflare R2 Storage resource with Rails-like simplicity.

    Examples:
        # Private bucket
        private = (Cloudflare.R2("private-data")
                   .private_bucket()
                   .create())

        # Public bucket for website assets
        public = (Cloudflare.R2("static-assets")
                  .public_bucket()
                  .website_hosting()
                  .create())

        # Backup bucket with lifecycle
        backup = (Cloudflare.R2("backups")
                  .lifecycle_rule("archive", 30)
                  .create())
    """

    def __init__(self, bucket_name: str):
        """
        Initialize R2 Storage resource for a bucket

        Args:
            bucket_name: The name of the R2 bucket
        """
        super().__init__(bucket_name)
        self.bucket_name = bucket_name
        self._location = "auto"  # Default location
        self._public_access = False
        self._website_hosting = False
        self._index_document = "index.html"
        self._error_document = "error.html"
        self._cors_rules = []
        self._lifecycle_rules = []
        self._event_notifications = []
        self._custom_domain = None

    def _initialize_managers(self):
        """Initialize R2-specific managers"""
        self.r2_manager = None  # Will be initialized after authentication

    def _post_authentication_setup(self):
        """Setup managers after authentication"""
        self.r2_manager = R2StorageManager()

    def location(self, location: str) -> 'R2Storage':
        """
        Set bucket location

        Args:
            location: Bucket location ("auto", "wnam", "enam", "weur", "eeur", "apac")

        Returns:
            R2Storage: Self for method chaining
        """
        valid_locations = ["auto", "wnam", "enam", "weur", "eeur", "apac"]
        if location not in valid_locations:
            raise ValueError(f"Location must be one of: {', '.join(valid_locations)}")
        self._location = location
        return self

    def private_bucket(self) -> 'R2Storage':
        """
        Configure as private bucket (default)

        Returns:
            R2Storage: Self for method chaining
        """
        self._public_access = False
        return self

    def public_bucket(self) -> 'R2Storage':
        """
        Configure as public bucket

        Returns:
            R2Storage: Self for method chaining
        """
        self._public_access = True
        return self

    def website_hosting(self, index_document: str = "index.html", error_document: str = "error.html") -> 'R2Storage':
        """
        Enable static website hosting

        Args:
            index_document: Index document name
            error_document: Error document name

        Returns:
            R2Storage: Self for method chaining
        """
        self._website_hosting = True
        self._index_document = index_document
        self._error_document = error_document
        return self

    def custom_domain(self, domain: str) -> 'R2Storage':
        """
        Set custom domain for the bucket

        Args:
            domain: Custom domain name

        Returns:
            R2Storage: Self for method chaining
        """
        self._custom_domain = domain
        return self

    def cors_rule(self, allowed_origins: List[str], allowed_methods: List[str], 
                  allowed_headers: Optional[List[str]] = None, max_age: int = 3600) -> 'R2Storage':
        """
        Add CORS rule

        Args:
            allowed_origins: List of allowed origins
            allowed_methods: List of allowed HTTP methods
            allowed_headers: List of allowed headers
            max_age: Max age for preflight requests

        Returns:
            R2Storage: Self for method chaining
        """
        self._cors_rules.append({
            "allowed_origins": allowed_origins,
            "allowed_methods": allowed_methods,
            "allowed_headers": allowed_headers or [],
            "max_age": max_age
        })
        return self

    def lifecycle_rule(self, rule_type: str, days: int, prefix: str = "") -> 'R2Storage':
        """
        Add lifecycle rule

        Args:
            rule_type: Rule type ("expire", "archive", "delete")
            days: Number of days after which to apply rule
            prefix: Object prefix to match

        Returns:
            R2Storage: Self for method chaining
        """
        self._lifecycle_rules.append({
            "type": rule_type,
            "days": days,
            "prefix": prefix
        })
        return self

    def event_notification(self, event_type: str, destination: str, prefix: str = "") -> 'R2Storage':
        """
        Add event notification

        Args:
            event_type: Event type ("object_create", "object_delete")
            destination: Notification destination (webhook URL, queue, etc.)
            prefix: Object prefix to match

        Returns:
            R2Storage: Self for method chaining
        """
        self._event_notifications.append({
            "event_type": event_type,
            "destination": destination,
            "prefix": prefix
        })
        return self

    # Rails-like convenience methods
    def cdn_assets(self) -> 'R2Storage':
        """
        Configure bucket for CDN assets

        Returns:
            R2Storage: Self for method chaining
        """
        return (self.public_bucket()
                .cors_rule(["*"], ["GET", "HEAD"])
                .lifecycle_rule("delete", 365, "temp/"))

    def backup_storage(self, retention_days: int = 90) -> 'R2Storage':
        """
        Configure bucket for backup storage

        Args:
            retention_days: Days to retain backups

        Returns:
            R2Storage: Self for method chaining
        """
        return (self.private_bucket()
                .lifecycle_rule("delete", retention_days))

    def log_storage(self, retention_days: int = 30) -> 'R2Storage':
        """
        Configure bucket for log storage

        Args:
            retention_days: Days to retain logs

        Returns:
            R2Storage: Self for method chaining
        """
        return (self.private_bucket()
                .lifecycle_rule("archive", 7)
                .lifecycle_rule("delete", retention_days))

    def media_storage(self) -> 'R2Storage':
        """
        Configure bucket for media file storage

        Returns:
            R2Storage: Self for method chaining
        """
        return (self.public_bucket()
                .cors_rule(["*"], ["GET", "HEAD", "POST", "PUT"])
                .lifecycle_rule("delete", 1095, "uploads/temp/"))  # 3 years

    def data_lake(self) -> 'R2Storage':
        """
        Configure bucket for data lake storage

        Returns:
            R2Storage: Self for method chaining
        """
        return (self.private_bucket()
                .lifecycle_rule("archive", 30)
                .lifecycle_rule("delete", 2555))  # 7 years

    def preview(self) -> Dict[str, Any]:
        """Preview R2 bucket configuration"""
        self._ensure_authenticated()
        
        preview_data = {
            "bucket_name": self.bucket_name,
            "location": self._location,
            "public_access": self._public_access,
            "website_hosting": self._website_hosting
        }

        if self._website_hosting:
            preview_data["index_document"] = self._index_document
            preview_data["error_document"] = self._error_document

        if self._custom_domain:
            preview_data["custom_domain"] = self._custom_domain

        if self._cors_rules:
            preview_data["cors_rules"] = self._cors_rules

        if self._lifecycle_rules:
            preview_data["lifecycle_rules"] = self._lifecycle_rules

        if self._event_notifications:
            preview_data["event_notifications"] = self._event_notifications

        return self._format_response("preview", preview_data)

    def create(self) -> Dict[str, Any]:
        """Create R2 bucket"""
        self._ensure_authenticated()
        
        try:
            result = self.r2_manager.create_bucket(
                bucket_name=self.bucket_name,
                location=self._location,
                public_access=self._public_access,
                website_hosting=self._website_hosting,
                index_document=self._index_document,
                error_document=self._error_document,
                custom_domain=self._custom_domain,
                cors_rules=self._cors_rules,
                lifecycle_rules=self._lifecycle_rules,
                event_notifications=self._event_notifications
            )
            
            return self._format_response("create", result)
        except Exception as e:
            return self._format_error_response("create", str(e))

    def delete(self) -> Dict[str, Any]:
        """Delete R2 bucket"""
        self._ensure_authenticated()
        
        try:
            result = self.r2_manager.delete_bucket(self.bucket_name)
            return self._format_response("delete", result)
        except Exception as e:
            return self._format_error_response("delete", str(e))

    def status(self) -> Dict[str, Any]:
        """Get R2 bucket status"""
        self._ensure_authenticated()
        
        try:
            result = self.r2_manager.get_bucket_status(self.bucket_name)
            return self._format_response("status", result)
        except Exception as e:
            return self._format_error_response("status", str(e))

    def upload_file(self, local_path: str, object_key: str) -> Dict[str, Any]:
        """Upload file to R2 bucket"""
        self._ensure_authenticated()
        
        try:
            result = self.r2_manager.upload_file(self.bucket_name, local_path, object_key)
            return self._format_response("upload", result)
        except Exception as e:
            return self._format_error_response("upload", str(e))

    def list_objects(self, prefix: str = "") -> Dict[str, Any]:
        """List objects in R2 bucket"""
        self._ensure_authenticated()
        
        try:
            result = self.r2_manager.list_objects(self.bucket_name, prefix)
            return self._format_response("list", result)
        except Exception as e:
            return self._format_error_response("list", str(e))

    def help(self) -> str:
        """Return help information for R2Storage resource"""
        return f"""
R2Storage Resource Help
=======================

Bucket: {self.bucket_name}
Provider: Cloudflare

Configuration:
- location(location): Set bucket location
- private_bucket(): Configure as private bucket
- public_bucket(): Configure as public bucket
- website_hosting(index, error): Enable static website hosting
- custom_domain(domain): Set custom domain

Access Control:
- cors_rule(origins, methods, headers, max_age): Add CORS rule

Lifecycle Management:
- lifecycle_rule(type, days, prefix): Add lifecycle rule
- event_notification(event, destination, prefix): Add event notification

Convenience Methods:
- cdn_assets(): Configure for CDN assets
- backup_storage(retention_days): Configure for backup storage
- log_storage(retention_days): Configure for log storage
- media_storage(): Configure for media file storage
- data_lake(): Configure for data lake storage

Methods:
- preview(): Preview bucket configuration
- create(): Create bucket
- delete(): Delete bucket
- status(): Get bucket status
- upload_file(local_path, object_key): Upload file
- list_objects(prefix): List objects in bucket
        """ 